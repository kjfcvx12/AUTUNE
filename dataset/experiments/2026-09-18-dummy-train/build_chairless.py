"""chairless = the team-authored no-chair dummy meetings only. No AMI, no AI Hub.

    python build_chairless.py

Train on 90 meetings, validate (best-epoch selection) on 10 held out: DUMMY_10, 20,
... 100, which spread over the four meeting types. Validation is dummy rather than AMI
because AMI's region-shaped labels are exactly what this run leaves out.

Also writes splits/chairless/heldout_sheets/ (A sheets + C copied as B) so the 10
held-out meetings can be scored like any other set. Their labels come from the same
authors as the training meetings, so that score is optimistic.
"""

from __future__ import annotations

import csv
import json
import shutil
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DUMMY = HERE.parents[1] / "team_dummy"
KINDS = ("commitment", "decision", "open_question", "concern", "ambiguous", "none")
HELD_OUT = {f"DUMMY_{n:02d}" for n in range(10, 101, 10)}


def main() -> None:
    out = HERE / "splits" / "chairless"
    sheets = out / "heldout_sheets"
    sheets.mkdir(parents=True, exist_ok=True)
    split: dict[str, list[dict]] = {"train": [], "validation": []}
    for path in sorted(DUMMY.glob("DUMMY_*.C.csv")):
        meeting = path.name.removesuffix(".C.csv")
        name = "validation" if meeting in HELD_OUT else "train"
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                if r["text"].strip():
                    split[name].append({"utterance_id": f"dummy:{meeting}:{r['row']}", "kind": r["kind"] or "none", "text": r["text"]})
        if name == "validation":
            shutil.copyfile(DUMMY / f"{meeting}.A.csv", sheets / f"{meeting}.A.csv")
            shutil.copyfile(path, sheets / f"{meeting}.B.csv")
    for name, rows in split.items():
        with (out / f"{name}.jsonl").open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        c = Counter(r["kind"] for r in rows)
        print(f"{name:<10} {len(rows):>6}  " + "  ".join(f"{k} {c[k]}" for k in KINDS))


if __name__ == "__main__":
    main()
