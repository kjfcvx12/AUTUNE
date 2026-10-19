"""Gold = the rows two independent labellers agree on.

    python merge_gold.py [folder]   # default: this script's own folder

For each ``<id>.C.csv`` (the author's labels) and ``<id>.L2.csv`` (a second
labeller who saw only ``<id>.A.csv``) this writes ``<id>.G.csv``: the same rows,
with ``kind`` kept where the two agree and set to ``disagreement`` where they do
not. A scorer reads the agreed rows and reports coverage beside the score; the
rest are what a human reviewer would have to settle.

Prints per meeting: rows, agreement, Cohen's kappa, and the disagreements by
pair. Counts only -- no utterance text is printed.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

HERE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
KINDS = ("commitment", "decision", "open_question", "concern", "ambiguous", "none")
DISAGREEMENT = "disagreement"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def kappa(pairs: list[tuple[str, str]]) -> float:
    """Cohen's kappa over the six kinds. 1.0 when the two never differ."""
    if not pairs:
        return 0.0
    n = len(pairs)
    agreed = sum(1 for a, b in pairs if a == b) / n
    first = Counter(a for a, _ in pairs)
    second = Counter(b for _, b in pairs)
    expected = sum((first[k] / n) * (second[k] / n) for k in set(first) | set(second))
    return 1.0 if expected == 1 else (agreed - expected) / (1 - expected)


def merge(meeting: str) -> tuple[int, int, float, Counter]:
    author = read(HERE / f"{meeting}.C.csv")
    second = {row["row"]: row for row in read(HERE / f"{meeting}.L2.csv")}
    if len(author) != len(second):
        raise SystemExit(f"{meeting}: {len(author)} rows labelled vs {len(second)} in L2")

    pairs: list[tuple[str, str]] = []
    mismatches: Counter = Counter()
    out: list[dict[str, str]] = []
    for row in author:
        theirs = second[row["row"]]
        if theirs["text"] != row["text"]:
            raise SystemExit(f"{meeting} row {row['row']}: the two sheets are not the same meeting")
        mine = (row["kind"] or "none").strip()
        other = (theirs["kind"] or "none").strip()
        pairs.append((mine, other))
        gold = dict(row)
        if mine != other:
            mismatches[" vs ".join(sorted((mine, other)))] += 1
            gold["kind"] = DISAGREEMENT
            # A decision region, a response and a note belong to a label nobody
            # settled on, so they go with it.
            gold["decision_id"] = gold["settles"] = gold["responds_to"] = gold["note"] = ""
        out.append(gold)

    with (HERE / f"{meeting}.G.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(author[0]))
        writer.writeheader()
        writer.writerows(out)

    agreed = sum(1 for a, b in pairs if a == b)
    return len(pairs), agreed, kappa(pairs), mismatches


def main() -> None:
    meetings = sorted(p.name.removesuffix(".C.csv") for p in HERE.glob("*.C.csv"))
    if not meetings:
        raise SystemExit(f"no *.C.csv in {HERE}")

    totals: Counter = Counter()
    every_pair: Counter = Counter()
    print(f"{'meeting':<10} {'rows':>5} {'agreed':>7} {'share':>7} {'kappa':>7}")
    for meeting in meetings:
        if not (HERE / f"{meeting}.L2.csv").exists():
            print(f"{meeting:<10} {'—':>5} (no second labelling yet)")
            continue
        rows, agreed, k, mismatches = merge(meeting)
        totals["rows"] += rows
        totals["agreed"] += agreed
        every_pair.update(mismatches)
        print(f"{meeting:<10} {rows:>5} {agreed:>7} {agreed / rows:>6.1%} {k:>7.3f}")

    if totals["rows"]:
        print(
            f"\ntotal {totals['rows']} rows, {totals['agreed']} agreed "
            f"({totals['agreed'] / totals['rows']:.1%}) -- scored rows"
        )
        print("disagreements:", ", ".join(f"{pair} {n}" for pair, n in every_pair.most_common()))


if __name__ == "__main__":
    main()
