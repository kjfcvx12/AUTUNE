"""v2's training split (syn_none_probe) with two utterances of context either side.

    python build_ctx_split.py [--context 2]

Same rows, same labels, same validation as v2 -- only the input changes -- so a
difference from v2 is the context and nothing else. Each row gains `before` and
`after`: lists of {"same": speaker matches, "text": ...}.

  AMI       neighbours from the corpus, ordered as exp_ctx_none.Encoder orders them
  synthetic neighbours from the generated sheet (whole meetings)
  probe     neighbours from the AI Hub source file (the sheets are gapped)

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
sys.path.insert(0, str(DATASET / "experiments" / "2026-09-10-none-context"))
sys.path.insert(0, str(HERE))
import exp_ctx_none as exp  # noqa: E402
from meetings import full_rows  # noqa: E402

SPLIT = DATASET / "experiments" / "2026-09-15-korean-v1" / "splits" / "syn_none_probe"
SYN = DATASET / "experiments" / "2026-09-12-synthetic-meetings" / "sheets_v4"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--context", type=int, default=2)
    args = ap.parse_args()
    c = args.context

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

    def meeting_rows(kind: str, meeting: str) -> list[dict]:
        key = f"{kind}:{meeting}"
        if key not in sheet_cache:
            if kind == "syn":
                with open(SYN / f"{meeting}.G.csv", encoding="utf-8-sig", newline="") as fh:
                    rows = sorted(csv.DictReader(fh), key=lambda r: int(r["row"]))
            else:
                rows = list(full_rows(meeting) or [])
            sheet_cache[key] = rows
        return sheet_cache[key]

    out_dir = HERE / "splits" / f"ctx{c}"
    out_dir.mkdir(parents=True, exist_ok=True)
    stats: Counter = Counter()
    for name in ("train", "validation"):
        with open(SPLIT / f"{name}.jsonl", encoding="utf-8") as src, open(out_dir / f"{name}.jsonl", "w", encoding="utf-8") as dst:
            for line in src:
                row = json.loads(line)
                uid = row["utterance_id"]
                if uid.startswith(("syn:", "probe:")):
                    kind, meeting, rownum = uid.split(":")
                    rows = meeting_rows(kind, meeting)
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


if __name__ == "__main__":
    main()
