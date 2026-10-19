"""Does this meeting sound like speech? Measured, not judged.

    python register_check.py DUMMY_101 DUMMY_102     # or no arguments for all

The first hundred dummy meetings read like a script: 22 characters a row, and the
speaker changes almost every row. Real Korean meeting speech (AI Hub #464, our
only reference) is 45 characters a row and stays with the same speaker for three
rows out of five. A model trained on ping-pong dialogue never learns to find a
decision inside somebody's fourth sentence in a row.

The targets below come from measuring 3,512 AI Hub rows on 2026-09-21. A meeting
passes when every number is inside its band. Counts only -- no text is printed.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Ends like a finished sentence: a final ending, or a question/exclamation mark.
FINAL = re.compile(r"(니다|세요|어요|아요|에요|예요|네요|죠|군요|는데요|거든요)[.?!]?$|[?!]$|다[.?!]?$")
# A filler or a hedge anywhere in the row. The lookarounds stop a token from
# matching inside a longer word (`어` in `어제`, `막` in `막히다`) without
# requiring whitespace -- an earlier version demanded spaces on both sides, so a
# sentence-initial "어 " was the only cheap way to raise the number and one author
# hit 55% on `어` openers alone while `그러니까` counted for nothing.
FILLER = re.compile(
    r"(?<![가-힣])(음+|어+|아+|그+|저기|뭐|뭐지|뭐냐|뭐랄까|그러니까|그니까|어쨌든|아무튼|약간|이제|일단|좀|그냥|막)(?![가-힣])"
)
# Saying it again a different way.
SELF_FIX = re.compile(r"(아니|아니라|그게 아니라|다시 말해|정정)")

# (name, low, high) -- the AI Hub value is inside every band.
TARGETS = (
    ("median row length", 34, 56),
    ("mean row length", 34, 56),
    ("rows continuing the same speaker %", 45, 72),
    ("fillers per 100 characters", 1.7, 3.6),
    ("self-corrections per 100 characters", 0.08, 0.30),
    ("rows of 6 characters or fewer %", 2, 12),
)


def measure(rows: list[dict[str, str]]) -> dict[str, float]:
    lengths: list[int] = []
    same = filler = fix = short = 0
    previous = None
    for row in rows:
        text = (row.get("text") or "").strip()
        if not text:
            continue
        lengths.append(len(text))
        # Counted per character, not per row. A row's *chance* of containing a
        # filler rises with its length, so "rows with a filler %" made the AI Hub
        # column (45-character rows) look three times as disfluent as it is.
        filler += len(FILLER.findall(text))
        fix += len(SELF_FIX.findall(text))
        if len(text) <= 6:
            short += 1
        if row.get("speaker") == previous:
            same += 1
        previous = row.get("speaker")
    n = len(lengths) or 1
    ordered = sorted(lengths)
    return {
        "rows": len(lengths),
        "median row length": ordered[len(ordered) // 2] if ordered else 0,
        "mean row length": sum(lengths) / n,
        "rows continuing the same speaker %": same / n * 100,
        "fillers per 100 characters": filler / max(sum(lengths), 1) * 100,
        "self-corrections per 100 characters": fix / max(sum(lengths), 1) * 100,
        "rows of 6 characters or fewer %": short / n * 100,
    }


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    names = sys.argv[1:] or sorted(p.name.removesuffix(".A.csv") for p in HERE.glob("DUMMY_*.A.csv"))
    failures = 0
    for name in names:
        path = HERE / f"{name}.A.csv"
        if not path.exists():
            print(f"{name}: no such meeting")
            failures += 1
            continue
        got = measure(read(path))
        bad = [t for t, low, high in TARGETS if not low <= got[t] <= high]
        print(f"\n{name}  ({got['rows']:.0f} rows)  {'OK' if not bad else 'OUT OF BAND'}")
        for target, low, high in TARGETS:
            mark = " <-- fix" if target in bad else ""
            print(f"  {target:<38}{got[target]:>7.1f}   want {low}-{high}{mark}")
        failures += bool(bad)
    print(f"\n{len(names) - failures} of {len(names)} meetings inside every band")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
