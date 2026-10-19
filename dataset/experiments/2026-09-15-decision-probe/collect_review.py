"""Collect the decision-probe review exports and count what the reviewer confirmed.

    python collect_review.py            # copy newest exports, then report
    python collect_review.py --dry-run  # report only

For every sheets_review/<meeting>.L.csv, the newest ~/Downloads/<meeting>.B.csv (or
"<meeting>.B (1).csv", ...) written after it is copied to sheets_review/<meeting>.B.csv.
The report counts, over the **sampled candidate rows only** (llm_kind set in the L
sheet), how many are confirmed and what they became, plus how that splits by Qwen's
p_decision. Neighbour rows are context and are not counted.

Counts only, never utterance text.
"""

from __future__ import annotations

import csv
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHEETS = HERE / "sheets_review"
DOWNLOADS = Path.home() / "Downloads"
KINDS = ("commitment", "decision", "open_question", "concern", "ambiguous", "none")


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def bucket(p: float) -> str:
    return "0.1-0.3" if p < 0.3 else "0.3-0.5" if p < 0.5 else "0.5-0.9" if p < 0.9 else ">=0.9"


def main() -> None:
    dry = "--dry-run" in sys.argv
    kinds_total: Counter = Counter()
    by_bucket: dict[str, Counter] = {}
    confirmed_total = sampled_total = 0
    missing = []
    for l_path in sorted(SHEETS.glob("*.L.csv")):
        meeting = l_path.name.removesuffix(".L.csv")
        pattern = re.compile(rf"^{re.escape(meeting)}\.B(?: \(\d+\))?\.csv$")
        exports = [p for p in DOWNLOADS.iterdir() if pattern.match(p.name) and p.stat().st_mtime > l_path.stat().st_mtime]
        b_path = SHEETS / f"{meeting}.B.csv"
        if exports and not dry:
            shutil.copy2(max(exports, key=lambda p: p.stat().st_mtime), b_path)
        sampled = {r["row"]: float(r.get("p_decision") or 0) for r in read(l_path) if r.get("llm_kind")}
        sampled_total += len(sampled)
        if not b_path.exists():
            missing.append(meeting)
            continue
        for r in read(b_path):
            if r["row"] not in sampled or not (r.get("reviewed", "").strip() and r.get("kind", "").strip()):
                continue
            kind = r["kind"].strip()
            confirmed_total += 1
            kinds_total[kind] += 1
            by_bucket.setdefault(bucket(sampled[r["row"]]), Counter())[kind] += 1

    print(f"sampled candidates {sampled_total}; confirmed {confirmed_total}; meetings without export {len(missing)}")
    print("confirmed kinds:", " ".join(f"{k} {kinds_total[k]}" for k in KINDS))
    for b in ("0.1-0.3", "0.3-0.5", "0.5-0.9", ">=0.9"):
        c = by_bucket.get(b, Counter())
        n = sum(c.values())
        if n:
            print(f"  p_decision {b:<8} decision {c['decision']}/{n} ({c['decision'] / n:.0%})")
    if missing:
        print("no export yet:", missing)
    if dry:
        print("(dry run: nothing copied)")


if __name__ == "__main__":
    main()
