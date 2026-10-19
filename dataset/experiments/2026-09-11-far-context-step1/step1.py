"""Step 1: does context from beyond the +-2 window help, and how much could it?

    python step1.py --corpus dataset/ami_public_manual_1.6.2 --out <dir>

Step 0 found that ~40% of concern sources sit outside the window, mostly 3-5 acts
back, and that the two nearest acts of >= 3 words beyond the window hold the
source 73% of the time while embedding similarity finds it 11%. So this trains:

  base    ctx2                       (exp_ctx_none, unchanged)
  far     ctx2 + the 2 nearest acts of >= 3 words before the window
  oracle  same shape as far, but when the true adjacency-pair source is before
          the window it takes the first slot -- the ceiling for "far"

The oracle keeps far's shape on purpose: every act gets exactly two extra acts
either way, so the input never reveals whether an act has a source at all
(which would leak the label: concern and ambiguous come only from pairs).

All conditions: 6-way with none (1:1), kf-deberta-base, 3 epochs, seeds
20260910 / 1 / 2. base at 20260910 is yesterday's ctx2-6way run (reproducible
exactly, checked today) and is read from its JSON instead of retrained.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-09-10-none-context"))
sys.path.insert(0, str(HERE.parent / "2026-09-11-similarity-step0"))

from transformers import AutoTokenizer  # noqa: E402

import exp_ctx_none as exp  # noqa: E402
from step0 import pair_sources  # noqa: E402

MIN_WORDS = 3
FAR = 2
SEEDS = (20260910, 1, 2)
MODE = "base"
SOURCES: dict[str, str] = {}
YESTERDAY_BASE = HERE.parent / "2026-09-10-none-context" / "results" / "ctx2-6way.json"


class FarEncoder(exp.Encoder):
    """exp.Encoder plus an `earlier:` segment of FAR acts from before the window."""

    def __init__(self, tok, rows, context):
        super().__init__(tok, rows, context)
        self.mark["earlier:"] = tok("earlier:", add_special_tokens=False)["input_ids"]
        self.far: dict[str, list[dict]] = {}
        if MODE == "base":
            return
        by_meeting: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            by_meeting[r["meeting"]].append(r)
        for acts in by_meeting.values():
            acts.sort(key=lambda r: (r["start"], r["speaker"], r["id"]))
            where = {r["id"]: i for i, r in enumerate(acts)}
            for i, r in enumerate(acts):
                edge = max(0, i - context)
                picks: list[int] = []
                for j in range(edge - 1, -1, -1):
                    if len(acts[j]["text"].split()) >= MIN_WORDS:
                        picks.append(j)
                        if len(picks) == FAR:
                            break
                if MODE == "oracle":
                    s = where.get(SOURCES.get(r["id"], ""))
                    if s is not None and s < edge and s not in picks:
                        picks = [s] + picks[: FAR - 1]
                self.far[r["id"]] = [acts[j] for j in sorted(picks)]

    def encode(self, row):
        ids = super().encode(row)
        if MODE == "base":
            return ids
        seg = list(self.mark["earlier:"])
        for a in self.far[row["id"]]:
            seg += self.mark["same:" if a["speaker"] == row["speaker"] else "other:"]
            seg += self.ids[a["id"]][: exp.CTX_UTT_MAX]
        return ids + seg + [self.tok.sep_token_id]


def summary(results: dict[str, list[dict]]) -> dict:
    out = {}
    for cond, rs in results.items():
        def agg(get):
            v = [get(r) for r in rs]
            return {"mean": st.mean(v), "sd": st.stdev(v) if len(v) > 1 else 0.0, "runs": v}
        out[cond] = {
            "closed_macro_f1": agg(lambda r: r["closed"]["macro_f1"]),
            "natural_macro_f1": agg(lambda r: r["natural"]["macro_f1"]),
            "false_kinds_per_2400": agg(lambda r: r["false_kinds_per_2400"]),
            **{f"closed_{k}": agg(lambda r, k=k: r["closed"][k]["f1"]) for k in exp.KINDS},
            **{f"natural_{k}": agg(lambda r, k=k: r["natural"][k]["f1"]) for k in exp.KINDS},
        }
    return out


def main() -> None:
    global MODE
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    exp.Encoder = FarEncoder  # run() builds its encoder by this name
    SOURCES.update(pair_sources(args.corpus))
    rows, decision_meetings = exp.build_rows(args.corpus)
    splits = exp.meeting_splits(rows)
    tok = AutoTokenizer.from_pretrained(exp.BASE)

    results: dict[str, list[dict]] = defaultdict(list)
    results["base"].append(json.loads(YESTERDAY_BASE.read_text(encoding="utf-8")))
    plan = [("base", s) for s in SEEDS[1:]] + [(m, s) for m in ("far", "oracle") for s in SEEDS]
    for mode, seed in plan:
        MODE, exp.SEED = mode, seed
        name = f"{mode}-seed{seed}"
        path = args.out / f"{name}.json"
        if path.exists():  # resumable: a finished run is not retrained
            r = json.loads(path.read_text(encoding="utf-8"))
        else:
            print(f"== {name}", flush=True)
            r = exp.run(rows, splits, decision_meetings, tok, 2, True, 3, path)
        results[mode].append(r)
        print(f"  {name}: closed {r['closed']['macro_f1']:.3f} | natural {r['natural']['macro_f1']:.3f} | "
              f"concern {r['closed']['concern']['f1']:.3f} | ambiguous {r['closed']['ambiguous']['f1']:.3f} | "
              f"decision {r['closed']['decision']['f1']:.3f} | false/2400 {r['false_kinds_per_2400']}", flush=True)

    s = summary(results)
    (args.out / "summary.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
    print(f"\n{'mean ± sd over 3 seeds':<24}" + "".join(f"{c:>18}" for c in s))
    for key in ("closed_macro_f1", "natural_macro_f1", "closed_concern", "closed_ambiguous", "closed_decision",
                "closed_commitment", "closed_open_question", "natural_concern", "natural_ambiguous", "false_kinds_per_2400"):
        print(f"{key:<24}" + "".join(f"{s[c][key]['mean']:>11.3f} ±{s[c][key]['sd']:.3f}" for c in s))


if __name__ == "__main__":
    main()
