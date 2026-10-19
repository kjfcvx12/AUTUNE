"""The things that make a real meeting hard to read, counted.

    python hard_check.py DUMMY_101 ...     # or no arguments for DUMMY_101 and up
    python hard_check.py --dir ../extraction_eval_dummy_hard

`register_check.py` measures the *surface* of the talk — how long a row is, who
is speaking, how many hedges. A meeting can pass all six of its bands and still
be trivially easy to read, because every act is stated plainly and every deadline
is written out. This checks the other half, the half a person has to reason
through:

- **Vague reference.** "그거 저번에 말한 대로 가죠" — the model must carry what
  "그거" points at. Written dialogue names things; speech points at them.
- **Broken-off turns.** Somebody is cut off mid-sentence and another voice takes
  over. The act often lands on the second attempt, not the first.
- **Side talk.** Three or four rows of something unrelated in the middle of the
  meeting, tagged `note = 사담`. A model that treats every row as business finds
  decisions in the lunch conversation.
- **Resistance before settling.** No decision is reached unopposed: every decision
  region carries an objection or a hedge *before* the row that settles it.
- **Owner and deadline off the settling row.** "그럼 지영 씨가 저번처럼 해주세요.
  이번 주말 전까지요." — who and by when are in the rows around the decision, not
  inside it. This is what module B's slot filling actually faces.

Reads `<id>.C.csv` (labels included). Counts only; no utterance text is printed.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Pointing at something instead of naming it.
VAGUE = re.compile(
    r"(?<![가-힣])(그거|그건|그걸|그게|저거|저번|지난번|아까|그때|그쪽|그 부분|그 건|그 얘기|"
    r"저희가 말한|말씀하신 거|어제 그|전에 그)(?![가-힣])"
)
# Ends without finishing: no final ending and no closing punctuation.
FINISHED = re.compile(r"(니다|세요|어요|아요|에요|예요|네요|죠|군요|는데요|거든요)[.?!]?$|[?!]$|다[.?!]?$")
# A deadline said out loud. "까지" needs the guard: "오늘은 여기까지요" ends a
# meeting and sets no deadline, and reading it as one made a decision look dated
# when it was not (found while revising DUMMY_107).
WHEN = re.compile(
    r"(월\s*\d|\d+\s*일|요일|(?<!여기)(?<!거기)(?<!이쯤)(?<!그쯤)까지|"
    r"이번 주|다음 주|이번 달|다음 달|내일|모레|주말)"
)
# A deadline said relative to something else, which has to be resolved first:
# "저번에 말한 날짜보다 이틀 앞당겨서", "그 기획서 나오기 이틀 전까지".
RELATIVE_WHEN = re.compile(
    r"(앞당겨|당겨서|미뤄서|늦춰서|보다\s*\S{0,4}\s*(전|후|앞|뒤)|나오기\s*\S{0,6}\s*전|"
    r"끝나고\s*나서|그 다음\s*\S{0,3}에|말한 날짜)"
)
# Cutting in on somebody.
INTERRUPT = re.compile(r"(잠시만요|잠깐만요|잠깐만|그건 아닌데|아 그게 아니고|아니 근데|제 말은)")

MINIMUMS = (
    ("rows pointing at something vague", 10),
    ("turns broken off mid-sentence", 6),
    ("rows cutting in on somebody", 3),
    ("side-talk stretches (note 사담, 3+ rows)", 2),
    ("relative deadlines (resolve another date first)", 1),
    ("false agreements later overturned (note 번복)", 1),
    ("tasks nobody volunteers for (note 위임)", 1),
    ("decisions met with resistance first", None),  # all of them
    ("decisions whose deadline is not in the settling row", None),  # at least half
)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def answer_key(rows: list[dict[str, str]], path: Path) -> list[str]:
    """Check `<id>.D.csv` — the summary of what was decided (addendum 2026-09-21c).

    The settling row is evidence, not an answer: in these meetings it reads
    "그럼 그 방향으로 가시죠" and the owner and the deadline are somewhere else.
    """
    settled = {
        (r.get("decision_id") or "").strip(): r
        for r in rows
        if (r.get("settles") or "").strip() == "1"
    }
    if not path.exists():
        return [f"no answer key: {path.name} (addendum 2026-09-21c)"] if settled else []

    with path.open(encoding="utf-8-sig", newline="") as fh:
        keys = list(csv.DictReader(fh))
    problems: list[str] = []
    named = dated = 0
    numbers = {r["row"] for r in rows}
    for key in keys:
        name = (key.get("decision_id") or "").strip()
        source = settled.pop(name, None)
        if source is None:
            problems.append(f"answer key has {name or '(blank)'}, which settles nothing")
            continue
        statement = (key.get("statement") or "").strip()
        if statement == source["text"].strip():
            problems.append(f"{name}: statement copies the settling row instead of summarising it")
        elif not 15 <= len(statement) <= 120:
            problems.append(f"{name}: statement is {len(statement)} characters, want 15-120")
        named += bool((key.get("owner") or "").strip())
        dated += bool((key.get("due") or "").strip())
        evidence = [r.strip() for r in (key.get("evidence_rows") or "").split(",") if r.strip()]
        unknown = [r for r in evidence if r not in numbers]
        if unknown:
            problems.append(f"{name}: evidence_rows has no such row: {', '.join(unknown)}")
        elsewhere = not WHEN.search(source["text"]) or (key.get("owner") or "").strip() not in source["text"]
        if elsewhere and len(evidence) < 2:
            problems.append(f"{name}: owner or deadline is not in the settling row, so evidence_rows needs more than it")
    for name in settled:
        problems.append(f"{name} settles a decision but is missing from the answer key")
    if keys and named * 2 < len(keys):
        problems.append(f"only {named} of {len(keys)} decisions name an owner; want at least half")
    if keys and dated * 2 < len(keys):
        problems.append(f"only {dated} of {len(keys)} decisions have a due; want at least half")
    return problems


def inspect(rows: list[dict[str, str]]) -> tuple[dict[str, int], list[str]]:
    vague = broken = cutting = relative = reversed_ = delegated = 0
    side_runs = run = 0
    for index, row in enumerate(rows):
        text = (row.get("text") or "").strip()
        note = row.get("note") or ""
        if VAGUE.search(text):
            vague += 1
        if INTERRUPT.search(text):
            cutting += 1
        if RELATIVE_WHEN.search(text):
            relative += 1
        reversed_ += "번복" in note
        delegated += "위임" in note
        following = rows[index + 1] if index + 1 < len(rows) else None
        if not FINISHED.search(text) and following and following["speaker"] != row["speaker"]:
            broken += 1
        if "사담" in note:
            run += 1
        else:
            side_runs += run >= 3
            run = 0
    side_runs += run >= 3

    regions: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if (row.get("decision_id") or "").strip():
            regions[row["decision_id"].strip()].append(row)

    resisted = vague_when = decisions = 0
    problems: list[str] = []
    for name, region in sorted(regions.items()):
        settling = [r for r in region if (r.get("settles") or "").strip() == "1"]
        if not settling:
            problems.append(f"{name}: no settling row")
            continue
        decisions += 1
        settle_row = int(settling[0]["row"])
        before = [r for r in region if int(r["row"]) < settle_row]
        if any(r["kind"] in ("concern", "ambiguous") for r in before):
            resisted += 1
        else:
            problems.append(f"{name}: settled with no concern or ambiguous row before it")
        if not WHEN.search(settling[0]["text"]):
            vague_when += 1

    counts = {
        "rows pointing at something vague": vague,
        "turns broken off mid-sentence": broken,
        "rows cutting in on somebody": cutting,
        "side-talk stretches (note 사담, 3+ rows)": side_runs,
        "relative deadlines (resolve another date first)": relative,
        "false agreements later overturned (note 번복)": reversed_,
        "tasks nobody volunteers for (note 위임)": delegated,
        "decisions met with resistance first": resisted,
        "decisions whose deadline is not in the settling row": vague_when,
        "decisions": decisions,
    }
    if decisions and vague_when * 2 < decisions:
        problems.append(
            f"{vague_when} of {decisions} decisions leave the deadline out of the settling row; want at least half"
        )
    return counts, problems


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="meeting ids; default: DUMMY_101 and up")
    ap.add_argument("--dir", type=Path, default=HERE)
    args = ap.parse_args()

    folder = args.dir.resolve()
    names = args.names
    if not names:
        names = sorted(
            p.name.removesuffix(".C.csv")
            for p in folder.glob("*.C.csv")
            if not p.name.startswith("DUMMY_") or int(p.name.split(".")[0][6:]) >= 101
        )
    if not names:
        raise SystemExit(f"nothing to check in {folder}")

    failures = 0
    for name in names:
        path = folder / f"{name}.C.csv"
        if not path.exists():
            print(f"{name}: no such meeting")
            failures += 1
            continue
        rows = read(path)
        counts, problems = inspect(rows)
        problems += answer_key(rows, folder / f"{name}.D.csv")
        bad = list(problems)
        for label, least in MINIMUMS:
            if least is not None and counts[label] < least:
                bad.append(f"{label}: {counts[label]}, want at least {least}")
        print(f"\n{name}  {'OK' if not bad else 'NOT HARD ENOUGH'}")
        for label, least in MINIMUMS:
            want = f"at least {least}" if least is not None else (
                f"all {counts['decisions']}" if "resistance" in label else f"at least {(counts['decisions'] + 1) // 2}"
            )
            print(f"  {label:<52}{counts[label]:>5}   want {want}")
        for problem in problems:
            print(f"  ! {problem}")
        failures += bool(bad)

    print(f"\n{len(names) - failures} of {len(names)} meetings hard enough")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
