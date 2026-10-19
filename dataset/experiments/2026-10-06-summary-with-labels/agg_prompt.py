"""Aggregate measure_prompt.py's log: per variant and meeting, and the probe."""

import json
import statistics as st
import sys
from collections import Counter, defaultdict

runs = defaultdict(list)
probe = defaultdict(lambda: defaultdict(Counter))
chars = {}
errors = Counter()
for line in open(sys.argv[1], encoding="utf-8"):
    d = json.loads(line)
    if "chars" in d:
        chars[d["variant"]] = d["chars"]
    elif "error" in d:
        errors[(d["variant"], d["meeting"])] += 1
    elif d.get("meeting") == "probe":
        for name, label in d["labels"].items():
            probe[d["variant"]][name][label] += 1
    elif "F1" in d:
        runs[(d["meeting"], d["variant"])].append(d)
for (meeting, variant), rs in sorted(runs.items()):
    f = [r["F1"] for r in rs]
    fps, fns = Counter(), Counter()
    for r in rs:
        fps.update(r["fp"])
        fns.update(r["fn"])
    print(
        f"{meeting:8} {variant:15} ({chars.get(variant)}ch) n={len(rs)} F1 {st.mean(f):.3f} "
        f"sd {st.pstdev(f):.3f} [{min(f):.3f}-{max(f):.3f}] P {st.mean(r['P'] for r in rs):.3f} "
        f"R {st.mean(r['R'] for r in rs):.3f} req {st.mean(r['requests'] for r in rs):.1f} "
        f"sum {st.mean(r['summaries'] for r in rs):.0f} | fp {dict(fps.most_common(5))} fn {dict(fns.most_common(4))}"
    )
for variant, names in probe.items():
    print("probe", variant, {name: dict(c) for name, c in names.items()})
if errors:
    print("errors", dict(errors))
