"""Tables from measure_part.py's log. Numbers only.

Usage: agg_part.py <log>
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

rows = [json.loads(line) for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()]
runs = [r for r in rows if "F1" in r]
errors = [r for r in rows if "error" in r]
cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
for r in runs:
    cells[(r["variant"], r["meeting"])].append(r)

print("errors:", [(e["round"], e["variant"], e["meeting"], e["error"]) for e in errors])
print("requests sent:", sum(r["requests"] for r in runs), [r for r in rows if r.get("done")])
print()
print("variant meeting  n  F1 mean (min-max)  P  R  requests  fp(runs)  fn(runs)")
for (variant, meeting), got in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    f1 = [r["F1"] for r in got]
    fps: dict[int, int] = defaultdict(int)
    fns: dict[int, int] = defaultdict(int)
    for r in got:
        for i in r["fp"]:
            fps[i] += 1
        for i in r["fn"]:
            fns[i] += 1
    print(
        f"{variant:5} {meeting:8} {len(got)}  {mean(f1):.3f} ({min(f1):.3f}-{max(f1):.3f})  "
        f"{mean(r['P'] for r in got):.3f}  {mean(r['R'] for r in got):.3f}  "
        f"{[r['requests'] for r in got]}  {dict(sorted(fps.items()))}  {dict(sorted(fns.items()))}"
    )

print()
for variant in sorted({r["variant"] for r in runs}):
    got = [r for r in runs if r["variant"] == variant]
    f1 = [r["F1"] for r in got]
    chars = [c for r in got for c in r["summary_chars"]]
    lines = sum(r["lines"] for r in got)
    print(f"== {variant}: mean F1 over {len(got)} runs {mean(f1):.3f}")
    print(
        f"   commitment/decision lines {lines} (>=60 chars: {sum(r['long_lines'] for r in got)}); "
        f"summaries written {len(chars)}, kept {sum(r['summaries_kept'] for r in got)}"
    )
    if chars:
        print(
            f"   summary chars mean {mean(chars):.1f} median {median(chars)} max {max(chars)}; "
            f"over 60: {sum(r['summary_over_60'] for r in got)} "
            f"({sum(r['summary_over_60'] for r in got) / len(chars):.1%}); "
            f"over 120: {sum(r['summary_over_120'] for r in got)}"
        )
    parts = sum(r["parts"] for r in got)
    if parts:
        exact = sum(r["exact"] for r in got)
        loose = sum(r["loose"] for r in got)
        whole = sum(r["whole"] for r in got)
        ratio = [x for r in got for x in r["ratio"]]
        ratio_long = [x for r in got for x in r["ratio_long"]]
        print(
            f"   parts returned {parts} of {lines} lines ({parts / lines:.1%}); "
            f"verbatim exact {exact} ({exact / parts:.1%}), spacing aside {loose} ({loose / parts:.1%}); "
            f"not in the line {parts - loose}"
        )
        print(
            f"   of the verbatim ones: whole line {whole} ({whole / loose:.1%}); "
            f"part/line length mean {mean(ratio):.2f} median {median(ratio):.2f}"
        )
        if ratio_long:
            print(
                f"   lines of 60+ chars: {len(ratio_long)} parts, part/line mean {mean(ratio_long):.2f} "
                f"median {median(ratio_long):.2f}, shorter than the line in "
                f"{sum(x < 1 for x in ratio_long)} ({sum(x < 1 for x in ratio_long) / len(ratio_long):.1%})"
            )
