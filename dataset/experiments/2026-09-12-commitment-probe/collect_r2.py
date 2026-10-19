"""Collect round-2 review exports from Downloads into sheets_r2/ and check them.

    python collect_r2.py            # copy newest exports, then report
    python collect_r2.py --dry-run  # report what would be copied, copy nothing

For every sheets_r2/<meeting>.L.csv, the newest ~/Downloads/<meeting>.R.csv or
browser duplicate (<meeting>.R (1).csv, ...) written after the L sheet is copied
to sheets_r2/<meeting>.R.csv. Then, per meeting, over the *candidate* rows (the
ones carrying llm_kind), it counts what was confirmed and how often the confirmed
label is still the LLM pre-fill. A meeting whose confirmed candidates are almost
all unchanged is flagged: that is what an unreviewed export looks like.

Counts and row numbers only, never utterance text.
"""

from __future__ import annotations

import csv
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHEETS = HERE / "sheets_r2"
DOWNLOADS = Path.home() / "Downloads"
UNCHANGED_FLAG = 0.99


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def newest_export(meeting: str, after: float) -> Path | None:
    pattern = re.compile(rf"^{re.escape(meeting)}\.R(?: \(\d+\))?\.csv$")
    found = [p for p in DOWNLOADS.iterdir() if pattern.match(p.name) and p.stat().st_mtime > after]
    return max(found, key=lambda p: p.stat().st_mtime) if found else None


def main() -> None:
    dry = "--dry-run" in sys.argv
    totals = dict(candidates=0, confirmed=0, bulk=0, unchanged=0, changed=0)
    missing: list[str] = []
    flagged: list[str] = []

    print(f"{'meeting':<15} {'cand':>4} {'conf':>4} {'bulk':>4} {'same':>4} {'chg':>4}  source")
    for l_path in sorted(SHEETS.glob("*.L.csv")):
        meeting = l_path.name.removesuffix(".L.csv")
        r_path = SHEETS / f"{meeting}.R.csv"
        src = newest_export(meeting, after=l_path.stat().st_mtime)
        if src is not None and not dry and (not r_path.exists() or src.stat().st_mtime > r_path.stat().st_mtime):
            shutil.copy2(src, r_path)
        use = r_path if r_path.exists() else src
        if use is None:
            missing.append(meeting)
            continue

        prefill = {r["row"]: r.get("llm_kind", "") for r in read(l_path) if r.get("llm_kind")}
        reviewed = {r["row"]: r for r in read(use)}
        cand = len(prefill)
        conf = bulk = same = chg = 0
        for row, llm_kind in prefill.items():
            r = reviewed.get(row)
            if r is None or not r.get("reviewed"):
                continue
            if r["reviewed"] == "bulk":
                bulk += 1
                continue
            conf += 1
            if r.get("kind", "") == llm_kind:
                same += 1
            else:
                chg += 1
        note = src.name if src is not None else "(sheets_r2, no newer export)"
        print(f"{meeting:<15} {cand:>4} {conf:>4} {bulk:>4} {same:>4} {chg:>4}  {note}")
        for k, v in zip(totals, (cand, conf, bulk, same, chg), strict=True):
            totals[k] += v
        if conf and same / conf >= UNCHANGED_FLAG and conf >= 5:
            flagged.append(meeting)

    print(f"{'TOTAL':<15} {totals['candidates']:>4} {totals['confirmed']:>4} {totals['bulk']:>4} "
          f"{totals['unchanged']:>4} {totals['changed']:>4}")
    unconfirmed = totals["candidates"] - totals["confirmed"] - totals["bulk"]
    print(f"candidates not yet confirmed: {unconfirmed} (from exported meetings)")
    print(f"meetings with no export: {len(missing)} {missing}")
    if flagged:
        print(f"CHECK: >= {UNCHANGED_FLAG:.0%} of confirmed candidates unchanged from the LLM pre-fill in {flagged}")
    if dry:
        print("(dry run: nothing copied)")


if __name__ == "__main__":
    main()
