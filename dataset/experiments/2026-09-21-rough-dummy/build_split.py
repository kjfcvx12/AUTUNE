"""v2 plus a chosen range of dummy meetings, so style can be compared at equal size.

    python build_split.py --name rough30 --meetings 101-130
    python build_split.py --name clean30 --meetings 1-30      # the v4 comparison

The 2026-09-18 experiment answered "does more dummy data help" (it does not: 30
meetings and 100 meetings score the same). This one asks "does *harder* dummy data
help", and the only way to read the answer is to hold the row count roughly fixed
and change nothing but how the meetings are written — so the meeting range is an
argument rather than "all of them".

Validation stays AMI validation, the same model-selection set as v2 and v4, so a
number here is comparable to the numbers already in `2026-09-18-dummy-train`.

Team-authored text only; no AI Hub rows are read except through v2's existing
split file. Prints counts only.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATASET = HERE.parents[1]
V2 = DATASET / "experiments" / "2026-09-15-korean-v1" / "splits" / "syn_none_probe"
DUMMY = DATASET / "team_dummy"
KINDS = ("commitment", "decision", "open_question", "concern", "ambiguous", "none")


def numbers(spec: str) -> list[int]:
    out: list[int] = []
    for part in spec.split(","):
        if "-" in part:
            low, high = part.split("-")
            out.extend(range(int(low), int(high) + 1))
        else:
            out.append(int(part))
    return out


def dummy_rows(wanted: list[int]) -> list[dict]:
    out: list[dict] = []
    missing: list[str] = []
    for n in wanted:
        meeting = f"DUMMY_{n:02d}"
        path = DUMMY / f"{meeting}.C.csv"
        if not path.exists():
            missing.append(meeting)
            continue
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                kind = (r["kind"] or "none").strip()
                assert kind in KINDS, (meeting, r["row"], kind)
                if r["text"].strip():
                    out.append(
                        {"utterance_id": f"dummy:{meeting}:{r['row']}", "kind": kind, "text": r["text"]}
                    )
    if missing:
        raise SystemExit(f"not written yet: {', '.join(missing)}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--meetings", required=True, help="e.g. 101-130 or 1-30")
    args = ap.parse_args()

    with (V2 / "train.jsonl").open(encoding="utf-8") as fh:
        v2 = [json.loads(line) for line in fh if line.strip()]
    wanted = numbers(args.meetings)
    dummy = dummy_rows(wanted)
    ids = [r["utterance_id"] for r in v2 + dummy]
    assert len(ids) == len(set(ids)), "utterance_id collision"

    for label, rows in (("v2", v2), (f"dummy ({len(wanted)} meetings)", dummy), ("total", v2 + dummy)):
        c = Counter(r["kind"] for r in rows)
        print(f"{label:<24} {len(rows):>6}  " + "  ".join(f"{k} {c[k]}" for k in KINDS))

    out = HERE / "splits" / args.name
    out.mkdir(parents=True, exist_ok=True)
    with (out / "train.jsonl").open("w", encoding="utf-8") as fh:
        for row in v2 + dummy:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    shutil.copyfile(V2 / "validation.jsonl", out / "validation.jsonl")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
