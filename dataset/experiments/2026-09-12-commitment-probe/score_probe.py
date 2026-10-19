"""Score the reviewed commitment probe: what Qwen's candidates turned out to be.

    python score_probe.py

Reads sheets/<meeting>.L.csv (Qwen's candidates and probabilities) and
sheets/<meeting>.R.csv (the reviewer's confirmed labels). Candidate rows are the
rows carrying `llm_kind`; neighbour rows are context and are reported apart.

The candidates are every row in the 60 scanned meetings that passed the ending
pre-filter and reached p_commitment >= 0.10, so "share of candidates that are
commitments" is Qwen's precision *on that pre-filtered Training population*. It
is not a precision for the random evaluation set and not a recall of any kind.

Counts and row numbers only, never utterance text.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Round 1 lives in sheets/; later rounds pass their folder: `python score_probe.py sheets_r2`.
SHEETS = HERE / (sys.argv[1] if len(sys.argv) > 1 else "sheets")
KINDS = ["commitment", "decision", "open_question", "concern", "ambiguous", "none"]
BUCKETS = [(0.10, 0.30), (0.30, 0.50), (0.50, 0.70), (0.70, 0.90), (0.90, 1.01)]


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def share(hit: int, n: int) -> str:
    return f"{hit}/{n} ({hit / n:.0%})" if n else "0/0"


def main() -> None:
    group_of = {u["meeting"]: u["group"]
                for f in sorted(HERE.glob("results*/used_meetings.json"))
                for u in json.loads(f.read_text("utf-8"))}
    cands: list[dict] = []
    neighbours: Counter[str] = Counter()
    neighbour_commit_dist: Counter[int] = Counter()
    per_meeting: list[tuple[str, int, int]] = []
    unconfirmed = 0

    for lpath in sorted(SHEETS.glob("*.L.csv")):
        m = lpath.name[: -len(".L.csv")]
        rpath = SHEETS / f"{m}.R.csv"
        if not rpath.exists():
            print(f"skip {m}: no R sheet")
            continue
        lrows = read(lpath)
        r_by_row = {r["row"]: r for r in read(rpath)}
        cand_rows = [int(r["row"]) for r in lrows if r["llm_kind"]]
        same = n = 0
        for lr in lrows:
            rr = r_by_row.get(lr["row"], {})
            human = rr.get("kind", "") if rr.get("reviewed", "").strip() else ""
            if lr["llm_kind"]:
                if not human:
                    unconfirmed += 1
                    continue
                n += 1
                same += human == lr["llm_kind"]
                cands.append({
                    "meeting": m, "row": int(lr["row"]), "group": group_of.get(m, "?"), "argmax": lr["llm_kind"],
                    "p": float(lr["p_commitment"]), "human": human,
                    "responds": bool(rr.get("responds_to", "").strip()),
                })
            elif human:
                neighbours[human] += 1
                if human == "commitment":
                    neighbour_commit_dist[min(abs(int(lr["row"]) - c) for c in cand_rows)] += 1
        per_meeting.append((m, same, n))

    total = len(cands)
    commit = [c for c in cands if c["human"] == "commitment"]
    print(f"candidates confirmed {total} (unconfirmed {unconfirmed}) in {len(per_meeting)} meetings")
    print("human kind:", ", ".join(f"{k} {v}" for k, v in Counter(c["human"] for c in cands).most_common()))
    print(f"commitment share of all candidates: {share(len(commit), total)}")

    print("\nby Qwen argmax")
    for kind in KINDS:
        sub = [c for c in cands if c["argmax"] == kind]
        if sub:
            print(f"  {kind:<14} {share(sum(c['human'] == 'commitment' for c in sub), len(sub)):>14}"
                  f"   human: {dict(Counter(c['human'] for c in sub).most_common())}")

    print("\nby p_commitment")
    for lo, hi in BUCKETS:
        sub = [c for c in cands if lo <= c["p"] < hi]
        print(f"  [{lo:.1f}, {min(hi, 1.0):.1f}{')' if hi <= 1 else ']'}  {share(sum(c['human'] == 'commitment' for c in sub), len(sub)):>14}")
    for cut in (0.5, 0.7, 0.9):
        sub = [c for c in cands if c["p"] >= cut]
        print(f"  p >= {cut}     {share(sum(c['human'] == 'commitment' for c in sub), len(sub)):>14}")

    print("\nby recording group")
    for g in sorted({c["group"] for c in cands}):
        sub = [c for c in cands if c["group"] == g]
        print(f"  {g:<8} {share(sum(c['human'] == 'commitment' for c in sub), len(sub)):>14}"
              f"   meetings {len({c['meeting'] for c in sub})}")

    print("\nwhat the non-commitment candidates became:",
          dict(Counter(c["human"] for c in cands if c["human"] != "commitment").most_common()))
    print(f"confirmed commitments with responds_to: {share(sum(c['responds'] for c in commit), len(commit))}")

    # A meeting whose confirmed labels all equal the pre-fill was probably not read.
    stamped = [(m, s, n) for m, s, n in per_meeting if n >= 5 and s == n]
    print(f"\nreview check: candidates equal to Qwen's suggestion {share(sum(s for _, s, _ in per_meeting), total)}; "
          f"meetings with >= 5 candidates all unchanged: {len(stamped)}"
          + (" -> " + ", ".join(f"{m} {s}/{n}" for m, s, n in stamped) if stamped else ""))

    by_meeting = defaultdict(lambda: [0, 0])
    for c in cands:
        by_meeting[c["meeting"]][0] += c["human"] == "commitment"
        by_meeting[c["meeting"]][1] += 1
    zero = [m for m, (k, n) in by_meeting.items() if k == 0]
    print(f"meetings with no confirmed commitment: {len(zero)}/{len(by_meeting)} "
          f"(their candidates: {sum(by_meeting[m][1] for m in zero)})")

    print(f"\nneighbour rows confirmed (context, not scored): {sum(neighbours.values())}  {dict(neighbours.most_common())}")
    if neighbour_commit_dist:
        print("  neighbour commitments by distance to the nearest candidate:",
              dict(sorted(neighbour_commit_dist.items())))

    # AI Hub rows are intonation phrases and the guide labels the row where the
    # sentence ends, so a candidate the reviewer called none may still sit on the
    # right sentence, one or two rows early or late.
    human_commit: dict[str, set[int]] = defaultdict(set)
    for lpath in sorted(SHEETS.glob("*.L.csv")):
        m = lpath.name[: -len(".L.csv")]
        for r in read(SHEETS / f"{m}.R.csv"):
            if r.get("reviewed", "").strip() and r["kind"] == "commitment":
                human_commit[m].add(int(r["row"]))
    # Split the nearby commitment by whether it is itself a candidate: then the
    # none candidate is a second flag on a sentence Qwen already caught, not a
    # sentence caught on the wrong row.
    cand_rows_of: dict[str, set[int]] = defaultdict(set)
    for c in cands:
        cand_rows_of[c["meeting"]].add(c["row"])
    shifted: Counter[str] = Counter()
    for c in cands:
        if c["human"] == "commitment":
            continue
        near = {c["row"] + d for d in (-2, -1, 1, 2)} & human_commit[c["meeting"]]
        near1 = {x for x in near if abs(x - c["row"]) == 1}
        if not near:
            shifted["no commitment within 2 rows"] += 1
        elif near1 - cand_rows_of[c["meeting"]]:
            shifted["wrong row: commitment 1 row away, not a candidate"] += 1
        elif near1:
            shifted["extra flag: adjacent candidate is the commitment"] += 1
        elif near - cand_rows_of[c["meeting"]]:
            shifted["commitment 2 rows away, not a candidate"] += 1
        else:
            shifted["candidate 2 rows away is the commitment"] += 1
    print(f"\nnon-commitment candidates ({total - len(commit)}) by nearest human commitment:")
    for k, v in shifted.most_common():
        print(f"  {k:<52} {v}")
    wrong_row = shifted["wrong row: commitment 1 row away, not a candidate"]
    print(f"candidates on or one row off a commitment sentence: {share(len(commit) + wrong_row, total)}")


if __name__ == "__main__":
    main()
