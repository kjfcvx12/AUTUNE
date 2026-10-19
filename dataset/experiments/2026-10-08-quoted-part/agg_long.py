"""Tables from measure_long.py's log. Numbers only.

Usage: agg_long.py <log>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import mean, median

rows = [json.loads(line) for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()]
runs = [r for r in rows if "turns" in r]
print("errors:", [r for r in rows if "error" in r])
print("requests:", [r["requests"] for r in runs], [r for r in rows if r.get("done")])


def share(n: int, of: int) -> str:
    return f"{n}/{of} ({n / of:.0%})" if of else "0/0"


for variant in sorted({r["variant"] for r in runs}):
    got = [r for r in runs if r["variant"] == variant]
    turns = [t for r in got for t in r["turns"]]
    found = [t for t in turns if t["found"]]
    print(f"\n== {variant}: {len(got)} runs, {len(turns)} planted turns")
    print(
        f"   planted sentence labelled {share(len(found), len(turns))}; "
        f"with the planted kind {share(sum(t['kind_right'] for t in turns), len(turns))}; "
        f"per run {[sum(t['found'] for t in r['turns']) for r in got]}"
    )
    missed: dict[int, int] = {}
    for t in turns:
        if not t["found"]:
            missed[t["turn"]] = missed.get(t["turn"], 0) + 1
    print(f"   missed turn -> runs {dict(sorted(missed.items()))}")
    print(
        f"   other sentences of the planted turns labelled: {sum(t['others'] for t in turns)} "
        f"(per run {[sum(t['others'] for t in r['turns']) for r in got]}); "
        f"questions labelled commitment/decision: {[r['questions_labelled'] for r in got]}"
    )
    print(
        f"   planted words / turn: mean {mean(t['core_of_turn'] for t in turns):.3f}; "
        f"S1 sentence / turn (found): mean {mean(t['s1_of_turn'] for t in found):.3f} "
        f"median {median(t['s1_of_turn'] for t in found):.3f} max {max(t['s1_of_turn'] for t in found):.3f}"
    )
    sizes = [t["summary_chars"] for t in found if t["summary_chars"]]
    if sizes:
        print(
            f"   summaries on found sentences: {len(sizes)}, chars mean {mean(sizes):.1f} "
            f"max {max(sizes)}, over 60: {sum(s > 60 for s in sizes)}"
        )
    parts = [t for t in found if t.get("part")]
    if not parts:
        continue
    inside = [t for t in parts if t["verbatim_spacing_aside"]]
    print(
        f"   parts returned on {share(len(parts), len(found))} found sentences; "
        f"verbatim exact {share(sum(t['verbatim'] for t in parts), len(parts))}, "
        f"spacing aside {share(len(inside), len(parts))}"
    )
    holds = sum(t["holds_core"] for t in inside)
    cut_in = sum(t["inside_core"] for t in inside)
    print(
        f"   of the verbatim parts: hold the planted words whole {share(holds, len(inside))}; "
        f"cut inside them {share(cut_in, len(inside))}; "
        f"elsewhere or overlapping {len(inside) - holds - cut_in}"
    )
    print(
        f"   S2 part / turn: mean {mean(t['s2_of_turn'] for t in inside):.3f} "
        f"median {median(t['s2_of_turn'] for t in inside):.3f}; "
        f"S2 part / its sentence: mean {mean(t['s2_of_sentence'] for t in inside):.3f}; "
        f"the whole sentence in {share(sum(t['s2_of_sentence'] >= 1 for t in inside), len(inside))}"
    )
    # The six planted inside a longer sentence are where S2 can add to S1.
    wide = [t for t in inside if t["s1_of_turn"] > 1.5 * t["core_of_turn"]]
    if wide:
        print(
            f"   where the sentence is over 1.5x the planted words ({len(wide)} parts): "
            f"S1 {mean(t['s1_of_turn'] for t in wide):.3f} of the turn -> "
            f"S2 {mean(t['s2_of_turn'] for t in wide):.3f}; hold the planted words "
            f"{share(sum(t['holds_core'] for t in wide), len(wide))}"
        )
    by_turn: dict[int, list[dict]] = {}
    for t in turns:
        by_turn.setdefault(t["turn"], []).append(t)
    print("   turn: chars planted | found | S1/turn | S2/turn per run | holds planted words per run")
    for at, ts in sorted(by_turn.items()):
        print(
            f"   {at:>3}: {ts[0]['chars']} {ts[0]['planted'][:3]} | {sum(t['found'] for t in ts)}/{len(ts)} | "
            f"{ts[0]['s1_of_turn']:.2f} | {[t.get('s2_of_turn') for t in ts]} | "
            f"{[t.get('holds_core') for t in ts]}"
        )
