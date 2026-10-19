"""share_plus131's train.jsonl (share + DUMMY_131) plus DUMMY_132-140's rows.

Not a general tool -- a one-off extension of splits/share_plus131 to cover the
full DUMMY_131-140 set (Phase 8/8b), same non-glob approach the pilot used so
DUMMY_101-130 stay out of it. Validation is copied unchanged (AMI validation,
same as share and share_plus131).

    python build_share_plus10.py
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATASET = HERE.parents[1]
DUMMY = DATASET / "team_dummy"
BASE = HERE / "splits" / "share_plus131"
OUT = HERE / "splits" / "share_plus10"
KINDS = ("commitment", "decision", "open_question", "concern", "ambiguous", "none")


def dummy_rows(meetings: list[str]) -> list[dict]:
    out: list[dict] = []
    for meeting in meetings:
        path = DUMMY / f"{meeting}.C.csv"
        if not path.exists():
            raise SystemExit(f"not written yet: {meeting}")
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                kind = (r["kind"] or "none").strip()
                assert kind in KINDS, (meeting, r["row"], kind)
                if r["text"].strip():
                    out.append(
                        {"utterance_id": f"dummy:{meeting}:{r['row']}", "kind": kind, "text": r["text"]}
                    )
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (BASE / "train.jsonl").open(encoding="utf-8") as fh:
        base = [json.loads(line) for line in fh if line.strip()]
    added = dummy_rows([f"DUMMY_{n}" for n in range(132, 141)])
    ids = [r["utterance_id"] for r in base + added]
    assert len(ids) == len(set(ids)), "utterance_id collision"
    with (OUT / "train.jsonl").open("w", encoding="utf-8") as fh:
        for row in base + added:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    shutil.copyfile(BASE / "validation.jsonl", OUT / "validation.jsonl")
    print(f"share_plus10: {len(base)} base rows (share + DUMMY_131) + {len(added)} new (DUMMY_132-140) = {len(base) + len(added)}")


if __name__ == "__main__":
    main()
