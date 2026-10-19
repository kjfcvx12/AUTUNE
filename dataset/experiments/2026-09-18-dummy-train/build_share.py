"""`share`: the split a checkpoint can be handed to the team (no AI Hub rows).

    python build_share.py

v5 minus its 1,061 ``probe:`` rows -- the human-labelled AI Hub utterances. What
is left is AMI (CC BY 4.0), the synthetic meetings (generated locally, no AI Hub
sentences) and the 100 team-authored dummy meetings, so the weights trained on it
carry no AI Hub-derived data and can be shared with the team and deployed
anywhere (#112 is about the other kind).

Validation stays AMI validation, as in every condition here. Prints counts only.
"""

from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "splits" / "v5"
KINDS = ("commitment", "decision", "open_question", "concern", "ambiguous", "none")


def main() -> None:
    with (SOURCE / "train.jsonl").open(encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    kept = [row for row in rows if not row["utterance_id"].startswith("probe:")]
    dropped = len(rows) - len(kept)

    out = HERE / "splits" / "share"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "train.jsonl").open("w", encoding="utf-8") as fh:
        for row in kept:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    shutil.copyfile(SOURCE / "validation.jsonl", out / "validation.jsonl")

    sources = Counter(row["utterance_id"].split(":")[0] if ":" in row["utterance_id"] else "ami" for row in kept)
    counts = Counter(row["kind"] for row in kept)
    print(f"dropped {dropped} AI Hub probe rows")
    print("sources  " + "  ".join(f"{name} {n}" for name, n in sorted(sources.items())))
    print(f"share    {len(kept):>6}  " + "  ".join(f"{k} {counts[k]}" for k in KINDS))


if __name__ == "__main__":
    main()
