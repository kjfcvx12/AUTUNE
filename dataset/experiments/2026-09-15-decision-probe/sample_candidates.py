"""Pick a seeded sample of decision candidates and write review sheets for it.

    python sample_candidates.py [--n 200] [--seed 20260915]

The scan found 647 candidates (p_decision >= 0.10) in 30 Validation meetings.
The user reviews a random 200 of them (2026-09-15).

Sampling keeps each meeting's share of the candidates: proportional allocation with
largest remainders, then a seeded random pick inside each meeting. So the sample
stands for the whole candidate set, not for the meetings that happened to have the
most candidates.

Output:
  - results/sampled.json: the picked candidates (meeting, row, index, p, argmax).
  - sheets_review/<meeting>.L.csv for every meeting with at least one pick. It is the
    sheets/ L sheet with llm_kind (and llm_p, p_*) kept **only on sampled rows**, so
    review.html's candidate filter shows exactly the 200. sheets/ is left untouched.

Review in Blind mode: it hides llm_kind and every p_* column, so nothing pulls the
reviewer toward "decision". Counts only, never utterance text.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
KINDS = ["commitment", "decision", "open_question", "concern", "ambiguous", "none"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260915)
    args = ap.parse_args()

    candidates = json.loads((HERE / "results" / "candidates.json").read_text("utf-8"))
    by_meeting: dict[str, list[dict]] = defaultdict(list)
    for c in candidates:
        by_meeting[c["meeting"]].append(c)

    total = len(candidates)
    quota = {m: args.n * len(cs) / total for m, cs in by_meeting.items()}
    alloc = {m: int(q) for m, q in quota.items()}
    for m in sorted(quota, key=lambda m: (quota[m] - alloc[m], m), reverse=True)[: args.n - sum(alloc.values())]:
        alloc[m] += 1

    rng = random.Random(args.seed)
    sampled: list[dict] = []
    for m in sorted(by_meeting):
        pool = sorted(by_meeting[m], key=lambda c: c["index"])
        sampled.extend(rng.sample(pool, alloc[m]))
    assert len(sampled) == args.n, len(sampled)
    (HERE / "results" / "sampled.json").write_text(json.dumps(sampled, ensure_ascii=False), "utf-8")

    picked = {(c["meeting"], c["row"]) for c in sampled}
    out = HERE / "sheets_review"
    out.mkdir(exist_ok=True)
    marked_total = sheets = 0
    for m in sorted({c["meeting"] for c in sampled}):
        with (HERE / "sheets" / f"{m}.L.csv").open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            fields = list(reader.fieldnames or [])
            rows = list(reader)
        marked = 0
        for r in rows:
            if r.get("llm_kind") and (m, r["row"]) not in picked:
                r["llm_kind"], r["llm_p"] = "", ""
                for k in KINDS:
                    r[f"p_{k}"] = ""
            marked += bool(r.get("llm_kind"))
        with (out / f"{m}.L.csv").open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        marked_total += marked
        sheets += 1
        print(f"{m}: candidates {len(by_meeting[m])} sampled {alloc[m]} marked {marked} rows {len(rows)}")

    buckets = defaultdict(int)
    for c in sampled:
        p = c["p"][KINDS.index("decision")]
        buckets["0.1-0.3" if p < 0.3 else "0.3-0.5" if p < 0.5 else "0.5-0.9" if p < 0.9 else ">=0.9"] += 1
    print(f"\n{sheets} sheets, {marked_total} marked rows (expect {args.n}) -> {out}")
    print("sampled p_decision buckets:", dict(buckets))


if __name__ == "__main__":
    main()
