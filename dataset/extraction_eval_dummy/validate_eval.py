"""Independent check of every EVAL meeting, and of the set as a whole.

    python validate_eval.py [folder]     # default: this script's own folder

Per meeting: the spec's structure (rows, timing, A == C outside the label
columns, responds_to, settles, no 사회자, none share, minimum content) and the
addendum's closing-cue limit. Across the set: sentences repeated between
meetings, and whether any sentence also appears in `team_dummy/`, which is
training data -- a meeting that shares its sentences with the training set is not
an evaluation meeting.

Prints counts only.
"""
from __future__ import annotations

import csv, json, re, sys
from collections import Counter
from pathlib import Path

# A second evaluation folder (the speech-register rewrite) is checked by the same
# rules, so the folder is an argument and only the training set is fixed.
SCRIPT = Path(__file__).resolve().parent
HERE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else SCRIPT
TRAIN = SCRIPT.parent / "team_dummy"
KINDS = {"commitment", "decision", "open_question", "concern", "ambiguous", "none"}
CUE = re.compile(r"기로 하|하죠|합시다|갑시다|봅시다|겠습니다|겠어요|걸로")
COLS = ["row","utterance_id","start","speaker","role","text","kind","decision_id","settles","responds_to","note"]

def read(path: Path) -> list[dict]:
    raw = path.read_bytes()
    if not raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"{path.name}: no BOM")
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))

problems: list[str] = []
texts: Counter = Counter()
rows_total = 0
kinds_total: Counter = Counter()

for c_path in sorted(HERE.glob("*.C.csv")):
    meeting = c_path.name.removesuffix(".C.csv")
    def bad(msg: str) -> None:
        problems.append(f"{meeting}: {msg}")
    rows = read(c_path)
    a_rows = read(HERE / f"{meeting}.A.csv")
    spk = json.loads((HERE / f"{meeting}.speakers.json").read_text(encoding="utf-8"))

    if list(rows[0]) != COLS: bad(f"columns {list(rows[0])}")
    if not 260 <= len(rows) <= 340: bad(f"rows {len(rows)}")
    if [r["row"] for r in rows] != [str(i) for i in range(1, len(rows) + 1)]: bad("row numbering")
    starts = [float(r["start"]) for r in rows]
    if starts != sorted(starts): bad("start not increasing")
    if not 1700 <= starts[-1] <= 1850: bad(f"last start {starts[-1]}")
    if any(not 1 <= b - a <= 15.5 for a, b in zip(starts, starts[1:])): bad("gap outside 1-15s")
    if len(a_rows) != len(rows): bad("A and C differ in length")
    for a, c in zip(a_rows, rows):
        if any(a[k] != c[k] for k in COLS[:6]): bad(f"A != C at row {c['row']}"); break
        if any(a[k] for k in COLS[6:]): bad(f"A carries a label at row {c['row']}"); break

    kinds = Counter((r["kind"] or "none").strip() for r in rows)
    if set(kinds) - KINDS: bad(f"unknown kinds {set(kinds) - KINDS}")
    none_share = kinds["none"] / len(rows)
    if not 0.65 <= none_share <= 0.85: bad(f"none share {none_share:.0%}")
    for need, kind in ((5, "decision"), (7, "commitment"), (3, "ambiguous"), (4, "concern"), (8, "open_question")):
        if kinds[kind] < need: bad(f"{kind} {kinds[kind]} < {need}")
    for r in rows:
        kind = (r["kind"] or "none").strip()
        if r["responds_to"] and int(r["responds_to"]) >= int(r["row"]): bad(f"responds_to not earlier at {r['row']}")
        if r["settles"] and kind != "decision": bad(f"settles on {kind} at {r['row']}")
        if kind == "decision" and (not r["settles"] or not r["decision_id"]): bad(f"decision without settles/id at {r['row']}")
        if kind != "none" and not r["note"]: bad(f"no note at {r['row']}")
        if r["role"] == "사회자": bad(f"사회자 at {r['row']}")
    decisions = [r for r in rows if (r["kind"] or "").strip() == "decision"]
    cues = sum(1 for r in decisions if CUE.search(r["text"]))
    if decisions and cues / len(decisions) > 0.34: bad(f"closing cue {cues}/{len(decisions)}")
    if spk.get("type") == "peers" and any("상급자" in (r["note"] or "") for r in rows): bad("peers meeting has a 상급자 decision")

    rows_total += len(rows)
    kinds_total.update(kinds)
    texts.update({r["text"] for r in rows if len(r["text"]) >= 12})
    print(f"{meeting}  {spk.get('type','?'):<11} spk {len(spk['speakers'])}  rows {len(rows):>4}  none {none_share:>4.0%}  "
          f"dec {kinds['decision']:>2}  com {kinds['commitment']:>2}  amb {kinds['ambiguous']:>2}  "
          f"con {kinds['concern']:>2}  q {kinds['open_question']:>2}  cue {cues}/{len(decisions)}")

shared = [t for t, n in texts.items() if n > 1]
train_texts = set()
for path in TRAIN.glob("DUMMY_*.C.csv"):
    train_texts.update(r["text"] for r in read(path) if len(r["text"]) >= 12)
overlap = [t for t in texts if t in train_texts]

print(f"\nTOTAL rows {rows_total} | " + " ".join(f"{k} {kinds_total[k]}" for k in sorted(KINDS)))
print(f"sentences (>=12 chars) shared between EVAL meetings: {len(shared)}")
print(f"sentences also present in team_dummy (training data): {len(overlap)}")
print(f"problems: {len(problems)}")
for p in problems[:20]:
    print("  -", p)
