"""Independent check of all dummy meetings against SPEC.md. Prints a table and problems."""
from __future__ import annotations
import csv, json, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
COLS = ["row", "utterance_id", "start", "speaker", "role", "text", "kind", "decision_id", "settles", "responds_to", "note"]
LABEL_COLS = COLS[6:]
KINDS = {"commitment", "decision", "open_question", "concern", "ambiguous", "none"}

def read(p: Path) -> list[dict]:
    raw = p.read_bytes()
    if not raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("no BOM")
    rows = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    return rows

problems: list[str] = []
table = []
texts: Counter = Counter()
for n in sorted(int(p.name.split(".")[0][6:]) for p in HERE.glob("DUMMY_*.C.csv")):
    m = f"DUMMY_{n:02d}"
    try:
        spk = json.loads((HERE / f"{m}.speakers.json").read_text(encoding="utf-8"))
        a, c = read(HERE / f"{m}.A.csv"), read(HERE / f"{m}.C.csv")
    except Exception as e:
        problems.append(f"{m}: cannot read ({e})"); continue
    p = lambda s: problems.append(f"{m}: {s}")
    if list(c[0].keys()) != COLS or list(a[0].keys()) != COLS: p("column order")
    if len(a) != len(c): p("A/C length differ")
    for ra, rc in zip(a, c):
        if any(ra[k] != rc[k] for k in COLS[:6]): p(f"A/C differ on row {rc['row']}"); break
        if any(ra[k].strip() for k in LABEL_COLS): p(f"A has labels on row {ra['row']}"); break
    rows = c
    if [r["row"] for r in rows] != [str(i) for i in range(1, len(rows) + 1)]: p("row numbering")
    if not (260 <= len(rows) <= 340): p(f"rows {len(rows)}")
    starts = [float(r["start"]) for r in rows]
    if any(b <= a_ for a_, b in zip(starts, starts[1:])): p("start not increasing")
    if not (1700 <= starts[-1] <= 1850): p(f"last start {starts[-1]}")
    people = {s["speaker"]: s for s in spk["speakers"]}
    order = spk["position_order"]
    if not (3 <= len(people) <= 8): p(f"speakers {len(people)}")  # 3 is allowed from DUMMY_101 (2026-09-21b)
    k = Counter()
    tags = Counter()
    for r in rows:
        kind = r["kind"].strip()
        if kind not in KINDS: p(f"row {r['row']} kind {kind!r}"); continue
        k[kind] += 1
        if r["speaker"] not in people: p(f"row {r['row']} unknown speaker")
        elif r["role"] != people[r["speaker"]]["job"]: p(f"row {r['row']} role != job")
        if r["role"] == "사회자": p("사회자 role")
        if r["responds_to"].strip() and (not r["responds_to"].isdigit() or int(r["responds_to"]) >= int(r["row"])): p(f"row {r['row']} responds_to not earlier")
        if kind == "decision" and (r["settles"].strip() != "1" or not r["decision_id"].strip()): p(f"row {r['row']} decision without settles/id")
        if r["settles"].strip() and kind != "decision": p(f"row {r['row']} settles on {kind}")
        if kind in ("concern", "ambiguous") and not r["responds_to"].strip() and not re.search("unprompted|전달", r["note"]): p(f"row {r['row']} {kind} without responds_to")
        if kind != "none" and not r["note"].strip(): p(f"row {r['row']} {kind} without note")
        for t in ("상급자", "상기", "전달"):
            if t in r["note"]: tags[(t, kind)] += 1
        if kind == "decision" and "상급자" in r["note"]:
            s = people.get(r["speaker"], {})
            present = [people[x] for x in {rr["speaker"] for rr in rows}]
            rank = lambda q: (order.index(q["position"]) if q["position"] in order else -1)
            top = max(rank(q) for q in present)
            if rank(s) < top and spk["type"] != "peers":
                # flat companies rank by title; accept a titled lead when positions tie
                if not (s.get("title") and all(rank(q) == rank(s) for q in present)):
                    p(f"row {r['row']} 상급자 decision by a speaker who is not the most senior present")
        if len(r["text"]) >= 12:
            texts[r["text"]] += 1
    n_rows = len(rows)
    none_share = k["none"] / n_rows
    mins = {"decision": 5, "commitment": 7, "ambiguous": 3, "concern": 4, "open_question": 8}
    for kind, lo in mins.items():
        if k[kind] < lo: p(f"{kind} {k[kind]} < {lo}")
    if not (0.65 <= none_share <= 0.85): p(f"none share {none_share:.2f}")
    sup = tags[("상급자", "decision")]
    if spk["type"] == "peers" and sup: p("peers meeting has 상급자 decisions")
    if spk["type"] != "peers" and sup < 1: p("no 상급자 decision")
    if tags[("상기", "commitment")] < 1: p("no 상기 commitment")
    if tags[("전달", "ambiguous")] < 1: p("no 전달 ambiguous")
    table.append((m, spk["type"], len(people), n_rows, round(starts[-1] / 60, 1), f"{none_share:.0%}", k["decision"], k["commitment"], k["ambiguous"], k["concern"], k["open_question"], sup, tags[("상기", "commitment")], tags[("전달", "ambiguous")]))

print("meeting   type         spk rows min  none dec com amb con q  상급자 상기 전달")
for t in table:
    print(f"{t[0]}  {t[1]:<12} {t[2]:>3} {t[3]:>4} {t[4]:>4} {t[5]:>4} {t[6]:>3} {t[7]:>3} {t[8]:>3} {t[9]:>3} {t[10]:>2} {t[11]:>5} {t[12]:>4} {t[13]:>4}")
tot = [sum(t[i] for t in table) for i in (3, 6, 7, 8, 9, 10)]
print(f"TOTAL rows {tot[0]} | decision {tot[1]} commitment {tot[2]} ambiguous {tot[3]} concern {tot[4]} open_question {tot[5]}")
dups = {t: c for t, c in texts.items() if c > 2}
print(f"texts (>=12 chars) repeated more than twice across all meetings: {len(dups)}")
print("problems:", len(problems))
for x in problems[:40]:
    print("  -", x)
