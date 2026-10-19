"""clean30 / rough30 with two utterances of context either side (#323).

    python build_ctx_split.py --name clean30 [--context 2]
    python build_ctx_split.py --name rough30 [--context 2]

Same shape as 2026-09-17-ensemble-context-llm/build_ctx_split.py: same rows,
same labels, same validation as the named split -- only the input changes, so
a difference from the no-context run is the context and nothing else. Each
row gains `before` and `after`: lists of {"same": speaker matches, "text": ...}.

Extends that script's neighbour sources with one more: `dummy:MEETING:ROW`,
which clean30/rough30 add on top of v2's `syn:`/`probe:`/AMI ids and the
earlier script never had to resolve. Neighbours for a dummy row come from
`team_dummy/<MEETING>.C.csv`, the same file build_split.py read to build the
split in the first place.

Local files only. Prints counts only.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATASET = HERE.parents[1]
DUMMY = DATASET / "team_dummy"
sys.path.insert(0, str(DATASET / "experiments" / "2026-09-10-none-context"))
sys.path.insert(0, str(DATASET / "experiments" / "2026-09-17-ensemble-context-llm"))
import exp_ctx_none as exp  # noqa: E402
from meetings import full_rows  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="clean30, rough30, ...")
    ap.add_argument("--context", type=int, default=2)
    args = ap.parse_args()
    c = args.context

    split = HERE / "splits" / args.name
    if not split.exists():
        raise SystemExit(f"no such split: {split} (run build_split.py first)")

    ami_rows, _ = exp.build_rows(DATASET / "ami_public_manual_1.6.2")
    by_meeting: dict[str, list[dict]] = defaultdict(list)
    for r in ami_rows:
        by_meeting[r["meeting"]].append(r)
    ami_neigh = {}
    for acts in by_meeting.values():
        acts.sort(key=lambda r: (r["start"], r["speaker"], r["id"]))
        for i, r in enumerate(acts):
            ami_neigh[r["id"]] = (r["speaker"], acts[max(0, i - c) : i], acts[i + 1 : i + 1 + c])

    sheet_cache: dict[str, list[dict]] = {}

    def syn_or_probe_rows(kind: str, meeting: str) -> list[dict]:
        key = f"{kind}:{meeting}"
        if key not in sheet_cache:
            if kind == "syn":
                syn_dir = DATASET / "experiments" / "2026-09-12-synthetic-meetings" / "sheets_v4"
                with open(syn_dir / f"{meeting}.G.csv", encoding="utf-8-sig", newline="") as fh:
                    rows = sorted(csv.DictReader(fh), key=lambda r: int(r["row"]))
            else:
                rows = list(full_rows(meeting) or [])
            sheet_cache[key] = rows
        return sheet_cache[key]

    def dummy_rows(meeting: str) -> list[dict]:
        key = f"dummy:{meeting}"
        if key not in sheet_cache:
            with open(DUMMY / f"{meeting}.C.csv", encoding="utf-8-sig", newline="") as fh:
                rows = sorted(csv.DictReader(fh), key=lambda r: int(r["row"]))
            sheet_cache[key] = rows
        return sheet_cache[key]

    out_dir = HERE / "splits" / f"{args.name}_ctx{c}"
    out_dir.mkdir(parents=True, exist_ok=True)
    stats: Counter = Counter()
    for name in ("train", "validation"):
        with open(split / f"{name}.jsonl", encoding="utf-8") as src, open(
            out_dir / f"{name}.jsonl", "w", encoding="utf-8"
        ) as dst:
            for line in src:
                row = json.loads(line)
                uid = row["utterance_id"]
                if uid.startswith("dummy:"):
                    _, meeting, rownum = uid.split(":")
                    rows = dummy_rows(meeting)
                    pos = {r["row"]: i for i, r in enumerate(rows)}
                    if rownum not in pos:
                        stats["dummy row missing from source"] += 1
                        before, after, speaker = [], [], None
                    else:
                        i = pos[rownum]
                        speaker = rows[i]["speaker"]
                        before, after = rows[max(0, i - c) : i], rows[i + 1 : i + 1 + c]
                        stats["dummy ok"] += 1
                elif uid.startswith(("syn:", "probe:")):
                    kind, meeting, rownum = uid.split(":")
                    rows = syn_or_probe_rows(kind, meeting)
                    pos = {r["row"]: i for i, r in enumerate(rows)}
                    if rownum not in pos:
                        stats[f"{kind} row missing from source"] += 1
                        before, after, speaker = [], [], None
                    else:
                        i = pos[rownum]
                        speaker = rows[i]["speaker"]
                        before, after = rows[max(0, i - c) : i], rows[i + 1 : i + 1 + c]
                        stats[f"{kind} ok"] += 1
                else:
                    speaker, before, after = ami_neigh[uid]
                    stats["ami ok"] += 1
                row["before"] = [{"same": b["speaker"] == speaker, "text": b["text"]} for b in before]
                row["after"] = [{"same": a["speaker"] == speaker, "text": a["text"]} for a in after]
                stats[f"{name} rows"] += 1
                dst.write(json.dumps(row, ensure_ascii=False) + "\n")
    for k, v in sorted(stats.items()):
        print(f"{k}: {v}")
    print(f"\nwrote {out_dir}")


if __name__ == "__main__":
    main()
