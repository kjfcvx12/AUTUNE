"""Does the context model use its context? Dummy meetings, ctx2 ensemble, three inputs:
true neighbours, no neighbours (markers only), neighbours from a random other place in
the same meeting. Team-authored data, so rows may be printed."""
from __future__ import annotations
import csv, random, shutil, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from score_models import LABELS, TGT_MAX, CTX_UTT_MAX, probabilities, read_sheet, AGREEMENT

S = HERE.parents[1] / "team_dummy" / "score_input"
CK = [HERE / "runs" / f"ctx2_s{s}" for s in (20260910, 20260916, 20260917)]

def encode(tok, rows, mode, rng):
    mark = {w: tok(w, add_special_tokens=False)["input_ids"] for w in ("before:", "after:", "same:", "other:")}
    ids = [tok(r["text"], add_special_tokens=False)["input_ids"] for r in rows]
    out = []
    for i, r in enumerate(rows):
        seq = [tok.cls_token_id] + ids[i][:TGT_MAX] + [tok.sep_token_id]
        if mode == "shuffled":
            j = rng.randrange(len(rows)); 
            while abs(j - i) < 10: j = rng.randrange(len(rows))
            before, after = range(max(0, j - 2), j), range(j + 1, min(len(rows), j + 3))
        elif mode == "empty":
            before, after = [], []
        elif mode == "before_only":
            before, after = range(max(0, i - 2), i), []
        elif mode == "after_only":
            before, after = [], range(i + 1, min(len(rows), i + 3))
        else:
            before, after = range(max(0, i - 2), i), range(i + 1, min(len(rows), i + 3))
        ctx = []
        for tag, rngs in (("before:", before), ("after:", after)):
            ctx += mark[tag]
            for k in rngs:
                ctx += mark["same:" if rows[k]["speaker"] == r["speaker"] else "other:"] + ids[k][:CTX_UTT_MAX]
        out.append(seq + ctx + [tok.sep_token_id])
    return out

meetings = {p.name.split(".")[0]: read_sheet(p) for p in sorted(S.glob("*.A.csv"))}
results = {}
for mode in sys.argv[1:] or ("true", "empty", "shuffled"):
    rng = random.Random(7)
    summed = {m: [[0.0] * 6 for _ in rows] for m, rows in meetings.items()}
    for ck in CK:
        tok = AutoTokenizer.from_pretrained(ck)
        model = AutoModelForSequenceClassification.from_pretrained(ck).to("cuda").eval()
        for m, rows in meetings.items():
            for acc, p in zip(summed[m], probabilities(model, tok.pad_token_id, encode(tok, rows, mode, rng))):
                for k, v in enumerate(p): acc[k] += v
        del model; torch.cuda.empty_cache()
    out = HERE / "scores" / f"dummy_ablation_{mode}"
    out.mkdir(parents=True, exist_ok=True)
    preds = {}
    for m, rows in meetings.items():
        with open(out / f"{m}.M.csv", "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh); w.writerow(["row", "kind", "p", "decision_id", "settles", "responds_to"])
            for r, acc in zip(rows, summed[m]):
                k = max(range(6), key=acc.__getitem__); w.writerow([r["row"], LABELS[k], f"{acc[k]/3:.4f}", "", "", ""])
                preds[(m, r["row"])] = LABELS[k]
        shutil.copyfile(S / f"{m}.B.csv", out / f"{m}.B.csv")
    res = subprocess.run([sys.executable, str(AGREEMENT), str(out), "M", "B"], capture_output=True, text=True, encoding="utf-8").stdout
    results[mode] = preds
    lines = [l for l in res.splitlines() if l.startswith(("kind ", "decision ", "commitment ", "concern ", "ambiguous ", "macro F1")) and "inside" not in l]
    print(f"=== {mode}"); print("\n".join(lines))
t = results.get("true")
for mode in [m for m in results if m != "true" and t]:
    same = sum(t[k] == results[mode][k] for k in t)
    print(f"predictions identical to true-context: {mode} {same}/{len(t)} ({same/len(t):.1%})")
