"""Re-score a row-level run at turn level, for a like-for-like comparison.

    python score_turns.py test test_turns ft_e2
    python score_turns.py test_real test_real_turns ft_e2

A turn counts as picked if the row-level run picked any row in it; turn gold
comes from the turn-level split, so both runs are scored on the same turns.
Prints counts only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def main() -> None:
    row_split, turn_split, tag = sys.argv[1:4]
    picked_rows: dict[str, set[int]] = {}
    run = json.loads((HERE / "results" / f"{row_split}_{tag}.json").read_text(encoding="utf-8"))
    for r in run["rows"]:
        picked_rows.setdefault(r["meeting"], set()).update(r["pred"])
    tp = fp = fn = 0
    for line in (HERE / f"{turn_split}.jsonl").open(encoding="utf-8"):
        t = json.loads(line)
        picked = {
            int(turn)
            for turn, rows in t["turn_rows"].items()
            if picked_rows.get(t["meeting"], set()) & set(rows)
        }
        gold, ignore = set(t["gold_yes"]), set(t["gold_ignore"])
        p = picked - ignore
        tp, fp, fn = tp + len(p & gold), fp + len(p - gold), fn + len(gold - p)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    print(
        json.dumps(
            {"row_run": f"{row_split}_{tag}", "turns": turn_split, "tp": tp, "fp": fp, "fn": fn,
             "precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3)}
        )
    )


if __name__ == "__main__":
    main()
