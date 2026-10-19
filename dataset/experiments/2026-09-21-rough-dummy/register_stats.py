"""How far the invented meetings are from real speech, in numbers.

    python register_stats.py

Compares the team-authored dummy meetings with the AI Hub sheets on surface
features a reader would call "spoken": how long a row is, whether it ends like a
finished sentence, how often a filler or a self-correction appears, how often one
speaker's turn is broken across rows.

Counts only. No utterance text is printed -- the AI Hub rules forbid it, and the
dummy side is held to the same rule so the two columns are comparable.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

DATASET = Path(__file__).resolve().parents[2]

# A row that ends a sentence: a final ending, or a question/exclamation mark.
sys.path.insert(0, str(DATASET / "team_dummy"))
from register_check import FILLER, FINAL, SELF_FIX, measure  # noqa: E402


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def describe(name: str, sheets: list[Path]) -> None:
    lengths: list[int] = []
    finished = short = filler = selffix = split_turn = total = 0
    for sheet in sheets:
        data = rows(sheet)
        previous_speaker = None
        for row in data:
            text = (row.get("text") or "").strip()
            if not text:
                continue
            total += 1
            lengths.append(len(text))
            if FINAL.search(text):
                finished += 1
            if len(text) <= 6:
                short += 1
            if FILLER.search(text):
                filler += 1
            if SELF_FIX.search(text):
                selffix += 1
            if row.get("speaker") == previous_speaker:
                split_turn += 1
            previous_speaker = row.get("speaker")
    lengths.sort()
    median = lengths[len(lengths) // 2] if lengths else 0
    print(
        f"{name:<14}{total:>8}{median:>9}{sum(lengths) / total:>9.1f}"
        f"{finished / total:>11.1%}{short / total:>9.1%}{filler / total:>9.1%}"
        f"{selffix / total:>10.1%}{split_turn / total:>11.1%}"
    )


def main() -> None:
    print(
        f"{'set':<14}{'rows':>8}{'median':>9}{'mean':>9}{'ends sent.':>11}"
        f"{'<=6ch':>9}{'filler':>9}{'self-fix':>10}{'same spk':>11}"
    )
    describe("dummy (train)", sorted((DATASET / "team_dummy").glob("DUMMY_*.A.csv")))
    describe("dummy (eval)", sorted((DATASET / "extraction_eval_dummy").glob("EVAL_*.A.csv")))
    describe("aihub", sorted((DATASET / "extraction_eval_blind2" / "chaired_12").glob("*.A.csv")))


if __name__ == "__main__":
    main()
