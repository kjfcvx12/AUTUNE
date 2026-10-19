"""DeBERTa classifier (saved predictions) x Flash-Lite (runs.jsonl), commitment only.

No model calls. Same roles as 2026-09-27-llm-finetune/cascade.py:
- AND / OR of the two pick sets.
- ``A->B``: A proposes. Both agree -> accepted; A-only -> a person confirms
  (queue); B-only -> never shown. Upper bound: the person resolves the queue
  perfectly, so queue items that are true count as TP and false ones cost
  nothing but review time.

    python combo.py [run-name-prefix ...]
"""

from __future__ import annotations

import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
FT = HERE.parent / "2026-09-27-llm-finetune"
TEST8_YES = {14, 20, 29, 34, 35, 37, 45, 46, 48, 49, 68, 69, 74, 75, 77, 79}
TEST8_IGN = {42, 43, 47, 52, 76}


def gold() -> dict[str, tuple[set[int], set[int]]]:
    out: dict[str, tuple[set[int], set[int]]] = {"8txt": (TEST8_YES, TEST8_IGN)}
    for line in (FT / "test.jsonl").read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        y, i = out.setdefault(d["meeting"], (set(), set()))
        y |= set(d["gold_yes"])
        i |= set(d["gold_ignore"])
    return out


def clf() -> dict[str, set[int]]:
    out: dict[str, set[int]] = {}
    for split in ("test8", "test"):
        kinds = json.loads((FT / "results" / f"clf_{split}.json").read_text(encoding="utf-8"))
        for m, v in kinds.items():
            out[m] = {int(i) for i, (k, _) in v.items() if k == "commitment"}
    return out


def prf(tp: int, fp: int, fn: int) -> float:
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return 2 * p * r / (p + r) if p + r else 0.0


def evaluate(yes: set[int], ign: set[int], lite: set[int], c: set[int]) -> dict[str, tuple]:
    lite, c = lite - ign, c - ign
    res = {}
    for name, picks in (("lite", lite), ("clf", c), ("AND", lite & c), ("OR", lite | c)):
        res[name] = (prf(len(picks & yes), len(picks - yes), len(yes - picks)), 0, 0)
    for name, prop, chk in (("lite->clf", lite, c), ("clf->lite", c, lite)):
        both, queue = prop & chk, prop - chk
        accepted = both | (queue & yes)  # a person keeps the true ones
        tp, fp = len(accepted & yes), len(both - yes)
        res[name] = (prf(tp, fp, len(yes - accepted)), len(queue), len(queue & yes))
    return res


def main() -> None:
    prefixes = sys.argv[1:] or [""]
    g, c = gold(), clf()
    runs = [json.loads(line) for line in (HERE / "runs.jsonl").read_text(encoding="utf-8").splitlines()]
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in runs:
        if r["cfg"]["model"] != "gemini-3.5-flash-lite" or not r["name"].startswith(tuple(prefixes)):
            continue
        meeting = r["cfg"].get("meeting") or "8txt"
        groups[(r["name"], meeting)].append(r)
    cols = ("lite", "clf", "AND", "OR", "lite->clf", "clf->lite")
    print(f"{'run':18} {'meeting':9} n  " + "  ".join(f"{k:>16}" for k in cols))
    for (name, meeting), rs in sorted(groups.items()):
        yes, ign = g[meeting]
        per = [evaluate(yes, ign, {int(i) for i, k in r["labels"].items() if k == "commitment"}, c[meeting]) for r in rs]
        cells = []
        for k in cols:
            f = st.mean(p[k][0] for p in per)
            q = st.mean(p[k][1] for p in per)
            t = st.mean(p[k][2] for p in per)
            cells.append(f"{f:.3f}" + (f" (q{q:.0f}/t{t:.0f})" if k.endswith(("clf", "lite")) and "->" in k else ""))
        print(f"{name:18} {meeting:9} {len(rs)}  " + "  ".join(f"{x:>16}" for x in cells))


if __name__ == "__main__":
    main()


def counts(yes: set[int], ign: set[int], lite: set[int], c: set[int]) -> dict[str, list[int]]:
    """[tp, fp, fn, queue, queue_true] per combination, for pooling across meetings."""
    lite, c = lite - ign, c - ign
    out = {}
    for name, picks in (("lite", lite), ("clf", c), ("AND", lite & c), ("OR", lite | c)):
        out[name] = [len(picks & yes), len(picks - yes), len(yes - picks), 0, 0]
    for name, prop, chk in (("lite->clf", lite, c), ("clf->lite", c, lite)):
        both, queue = prop & chk, prop - chk
        accepted = both | (queue & yes)
        out[name] = [len(accepted & yes), len(both - yes), len(yes - accepted), len(queue), len(queue & yes)]
    return out


def pooled(picks: dict[str, dict]) -> None:
    """Micro F1 over meetings; ``picks`` maps meeting -> one run record."""
    g, c = gold(), clf()
    tot: dict[str, list[int]] = defaultdict(lambda: [0] * 5)
    for meeting, r in picks.items():
        yes, ign = g[meeting]
        lite = {int(i) for i, k in r["labels"].items() if k == "commitment"}
        for k, v in counts(yes, ign, lite, c[meeting]).items():
            tot[k] = [a + b for a, b in zip(tot[k], v)]
    n_gold = sum(len(g[m][0]) for m in picks)
    print(f"{len(picks)} meetings, {n_gold} gold commitments")
    for k, (tp, fp, fn, q, qt) in tot.items():
        p = tp / (tp + fp) if tp + fp else 0.0
        rr = tp / (tp + fn) if tp + fn else 0.0
        extra = f"  queue {q} ({qt} true)" if "->" in k else ""
        print(f"  {k:10} P={p:.3f} R={rr:.3f} F1={prf(tp, fp, fn):.3f}  fp={fp} fn={fn}{extra}")
