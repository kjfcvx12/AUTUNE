"""v4 = v2 (syn_none_probe) + every row of the team-authored dummy meetings.

    python build_split.py [split name, default v4]

v5 (2026-09-18, 100 meetings) is the same recipe over DUMMY_01-100.

Writes splits/v4/{train,validation}.jsonl. Validation stays AMI validation, the
same model-selection set as v2, so the only difference from v2 is the added rows.

The dummy meetings (dataset/team_dummy, DUMMY_*.C.csv) are no-chair Korean
meetings written with author labels under the 09-17 boundary rules. All six
kinds go in, `none` included: unlike the synthetic v4 generator, where `none`
was the leftover of a plan and was kept only where Qwen agreed, every dummy row
was labelled on purpose by its author.

The dummy meetings are therefore no longer an evaluation set for anything
trained here. Evaluation is the user's review of real meetings; the AI Hub sets
(probe, blind 1, chaired 12) are scored only as a regression check.

Team-authored text, no AI Hub rows are read here except through v2's existing
split file. Prints counts only.
"""

from __future__ import annotations

import csv
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATASET = HERE.parents[1]
V2 = DATASET / "experiments" / "2026-09-15-korean-v1" / "splits" / "syn_none_probe"
DUMMY = DATASET / "team_dummy"
KINDS = ("commitment", "decision", "open_question", "concern", "ambiguous", "none")


def dummy_rows() -> list[dict]:
    out = []
    for path in sorted(DUMMY.glob("DUMMY_*.C.csv")):
        meeting = path.name.removesuffix(".C.csv")
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                kind = (r["kind"] or "none").strip()
                assert kind in KINDS, (meeting, r["row"], kind)
                if r["text"].strip():
                    out.append({"utterance_id": f"dummy:{meeting}:{r['row']}", "kind": kind, "text": r["text"]})
    return out


def main() -> None:
    with (V2 / "train.jsonl").open(encoding="utf-8") as fh:
        v2 = [json.loads(line) for line in fh if line.strip()]
    dummy = dummy_rows()
    ids = [r["utterance_id"] for r in v2 + dummy]
    assert len(ids) == len(set(ids)), "utterance_id collision"
    meetings = len({r["utterance_id"].split(":")[1] for r in dummy})
    for label, rows in (("v2", v2), (f"dummy ({meetings} meetings)", dummy), ("total", v2 + dummy)):
        c = Counter(r["kind"] for r in rows)
        print(f"{label:<22} {len(rows):>6}  " + "  ".join(f"{k} {c[k]}" for k in KINDS))
    name = sys.argv[1] if len(sys.argv) > 1 else "v4"
    d = HERE / "splits" / name
    d.mkdir(parents=True, exist_ok=True)
    with (d / "train.jsonl").open("w", encoding="utf-8") as fh:
        for row in v2 + dummy:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    shutil.copyfile(V2 / "validation.jsonl", d / "validation.jsonl")


if __name__ == "__main__":
    main()
