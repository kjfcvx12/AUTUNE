"""Score one checkpoint or an ensemble of them on a sheet set, optionally with context.

    python score_models.py --sheets <dir with *.A.csv and *.B.csv> --out <dir> \
        --ckpt <dir> [--ckpt <dir> ...] [--context 2]

Each checkpoint's softmax is computed per row and the ensemble is their mean, so
one --ckpt reproduces a single model and three give the seed ensemble. No
checkpoint is chosen here and none is weighted: every seed counts the same, so the
evaluation set never picks a winner.

--context N encodes the target the way the AMI context experiment did
(2026-09-10-none-context/exp_ctx_none.py: target, then "before:" and "after:"
with "same:"/"other:" per neighbour, each neighbour cut at 36 tokens). It must
match how the checkpoint was trained; a context-0 checkpoint is scored with 0.

Writes <meeting>.M.csv into --out (row, kind, p, p_<label>; never text), copies
the gold B sheets beside them, and runs pilot_agreement.py there. The source
folder is never written to -- ko_sanity.py's apply wrote next to the A sheets,
which is how two scoring scripts once overwrote each other.

Prints counts only. AI Hub text never leaves this machine.
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")

import torch  # noqa: E402
from transformers import AutoModelForSequenceClassification, AutoTokenizer  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from meetings import full_rows  # noqa: E402

LABELS = ["commitment", "decision", "open_question", "concern", "ambiguous", "none"]
TGT_MAX = 94
CTX_UTT_MAX = 36
DATASET = Path(__file__).resolve().parents[2]
AGREEMENT = DATASET / "extraction_eval_pilot" / "pilot_agreement.py"


def read_sheet(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    rows.sort(key=lambda r: int(r["row"]))
    return rows


def encode_meeting(tok, meeting: str, rows: list[dict], context: int) -> list[list[int]]:
    """Neighbours come from the whole meeting when its source file is known (the
    decision-probe sheets are candidate windows), else from the sheet itself."""
    mark = {w: tok(w, add_special_tokens=False)["input_ids"] for w in ("before:", "after:", "same:", "other:")}
    full = list(full_rows(meeting) or []) if context else []
    order = full if full else rows
    pos = {r["row"]: i for i, r in enumerate(order)}
    cache: dict[int, list[int]] = {}

    def ids(i: int) -> list[int]:
        if i not in cache:
            cache[i] = tok(order[i]["text"], add_special_tokens=False)["input_ids"]
        return cache[i]

    out = []
    for r in rows:
        i = pos[r["row"]]
        seq = [tok.cls_token_id] + ids(i)[:TGT_MAX] + [tok.sep_token_id]
        if context:
            ctx: list[int] = []
            for tag, rng in (("before:", range(max(0, i - context), i)), ("after:", range(i + 1, min(len(order), i + 1 + context)))):
                ctx += mark[tag]
                for j in rng:
                    ctx += mark["same:" if order[j]["speaker"] == order[i]["speaker"] else "other:"]
                    ctx += ids(j)[:CTX_UTT_MAX]
            seq += ctx + [tok.sep_token_id]
        out.append(seq)
    return out


@torch.no_grad()
def probabilities(model, pad: int, encoded: list[list[int]], batch: int = 64) -> list[list[float]]:
    order = sorted(range(len(encoded)), key=lambda i: len(encoded[i]))
    probs: list[list[float]] = [[] for _ in encoded]
    for start in range(0, len(order), batch):
        idx = order[start : start + batch]
        width = max(len(encoded[i]) for i in idx)
        x = torch.full((len(idx), width), pad, dtype=torch.long)
        m = torch.zeros((len(idx), width), dtype=torch.long)
        for k, i in enumerate(idx):
            x[k, : len(encoded[i])] = torch.tensor(encoded[i])
            m[k, : len(encoded[i])] = 1
        with torch.autocast("cuda", dtype=torch.bfloat16):
            logits = model(input_ids=x.to("cuda"), attention_mask=m.to("cuda")).logits
        for i, p in zip(idx, torch.softmax(logits.float(), -1).cpu().tolist()):
            probs[i] = p
    return probs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheets", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--ckpt", type=Path, action="append", required=True)
    ap.add_argument("--context", type=int, default=0)
    args = ap.parse_args()

    meetings = {p.name.split(".")[0]: read_sheet(p) for p in sorted(args.sheets.glob("*.A.csv"))}
    if not meetings:
        raise SystemExit(f"no A sheets in {args.sheets}")
    summed = {m: [[0.0] * len(LABELS) for _ in rows] for m, rows in meetings.items()}

    for ckpt in args.ckpt:
        tok = AutoTokenizer.from_pretrained(ckpt)
        model = AutoModelForSequenceClassification.from_pretrained(ckpt).to("cuda").eval()
        order = [model.config.id2label[i] for i in range(model.config.num_labels)]
        if order != LABELS:
            raise SystemExit(f"{ckpt}: label order {order} is not {LABELS}")
        for m, rows in meetings.items():
            for acc, p in zip(summed[m], probabilities(model, tok.pad_token_id, encode_meeting(tok, m, rows, args.context))):
                for k, v in enumerate(p):
                    acc[k] += v
        del model
        torch.cuda.empty_cache()
        print(f"scored {ckpt.name}", flush=True)

    args.out.mkdir(parents=True, exist_ok=True)
    for old in args.out.glob("*.M.csv"):
        old.unlink()
    n = len(args.ckpt)
    for m, rows in meetings.items():
        out_rows = []
        for r, acc in zip(rows, summed[m]):
            p = [v / n for v in acc]
            top = max(range(len(LABELS)), key=p.__getitem__)
            out_rows.append({"row": r["row"], "kind": LABELS[top], "p": f"{p[top]:.4f}",
                             **{f"p_{lab}": f"{v:.4f}" for lab, v in zip(LABELS, p)},
                             "decision_id": "", "settles": "", "responds_to": ""})
        with open(args.out / f"{m}.M.csv", "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
            w.writeheader()
            w.writerows(out_rows)
        gold = args.sheets / f"{m}.B.csv"
        if gold.exists():
            shutil.copyfile(gold, args.out / gold.name)

    result = subprocess.run([sys.executable, str(AGREEMENT), str(args.out), "M", "B"], capture_output=True, text=True, encoding="utf-8")
    (args.out / "agreement.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
    for line in result.stdout.splitlines():
        if line.startswith(("kind ", "commitment ", "decision ", "open_question ", "concern ", "ambiguous ", "none ", "macro F1")) and "inside" not in line:
            print(line)


if __name__ == "__main__":
    main()
