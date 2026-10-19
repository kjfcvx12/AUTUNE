"""Cascade: one model first; the other two only where it is unsure. Simulated from the
saved per-model probabilities, so no inference. Counts only."""
from __future__ import annotations
import csv, re, shutil, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
DS = HERE.parents[1]
AG = DS / "extraction_eval_pilot" / "pilot_agreement.py"
H = ["commitment", "decision", "open_question", "concern", "ambiguous", "none"]
SETS = {
    "probe": (DS / "experiments/2026-09-15-decision-probe", ["score_v2", "score_v2_s20260916", "score_v2_s20260917"], DS / "experiments/2026-09-15-decision-probe/score_input"),
    "blind": (DS / "extraction_eval_blind", ["score_syn_none_probe", "score_v2_s20260916", "score_v2_s20260917"], DS / "extraction_eval_blind"),
    "dummy": (HERE / "scores", ["dummy_v2_s0910", "dummy_v2_s0916", "dummy_v2_s0917"], DS / "team_dummy/score_input"),
}
def load(d):
    out = {}
    for p in Path(d).glob("*.M.csv"):
        m = p.name.split(".")[0]
        for r in csv.DictReader(open(p, encoding="utf-8-sig", newline="")):
            out[(m, r["row"])] = [float(r[f"p_{h}"]) for h in H]
    return out
def score(preds, gold_dir, tag):
    out = HERE / "scores" / "cascade" / tag
    shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
    by = {}
    for (m, row), k in preds.items(): by.setdefault(m, []).append((row, k))
    for m, items in by.items():
        with open(out / f"{m}.M.csv", "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh); w.writerow(["row", "kind", "decision_id", "settles", "responds_to"])
            for row, k in items: w.writerow([row, k, "", "", ""])
        g = gold_dir / f"{m}.B.csv"
        if g.exists(): shutil.copyfile(g, out / g.name)
    t = subprocess.run([sys.executable, str(AG), str(out), "M", "B"], capture_output=True, text=True, encoding="utf-8").stdout
    return float(re.search(r"macro F1 over the five kinds.*: ([\d.]+)", t).group(1)), float(re.search(r"kappa ([\d.-]+)", t).group(1))
for name, (base, dirs, gold) in SETS.items():
    ps = [load(base / d) for d in dirs]
    keys = [k for k in ps[0] if all(k in p for p in ps)]
    print(f"== {name} ({len(keys)} rows)")
    for t in (None, 0.5, 0.6, 0.7, 0.8, 0.9, 1.01):
        preds, esc = {}, 0
        for k in keys:
            p0 = ps[0][k]
            if t is not None and max(p0) >= t:
                probs = p0
            else:
                esc += t is not None
                probs = [sum(p[k][i] for p in ps) / 3 for i in range(6)]
            preds[k] = H[max(range(6), key=probs.__getitem__)]
        label = "full ensemble" if t is None else ("single only" if t <= 0 else f"escalate if top p < {t}")
        if t == 1.01: label = "escalate everything"
        if t is not None and t < 1.01:
            cost = 1 + 2 * esc / len(keys)
        else:
            cost = 3.0
        mf, k_ = score(preds, gold, f"{name}_{t}")
        print(f"  {label:<26} cost x{cost:.2f}  escalated {esc/len(keys):5.1%}  macro5 {mf:.3f}  kappa {k_:.3f}")
    preds = {k: H[max(range(6), key=ps[0][k].__getitem__)] for k in keys}
    mf, k_ = score(preds, gold, f"{name}_single")
    print(f"  {'single model only':<26} cost x1.00  escalated   0.0%  macro5 {mf:.3f}  kappa {k_:.3f}")
