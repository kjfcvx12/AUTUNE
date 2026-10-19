"""Ablation: {5-way, 6-way with none} x {context 0, context 2} on AMI, kf-deberta-base, GPU.

Evaluates each model twice:
  closed  -- labelled test acts only (what #115 measured)
  natural -- every act in test meetings that carry the decision layer, none included

Run with the aiprj conda env (CUDA torch) and PYTHONPATH pointing at the module sources.
"""

from __future__ import annotations

import argparse
import json
import random
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

import torch
from torch import nn
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

from autune_extraction.labeling.ami import label_for
from autune_extraction.labeling.corpus import NITE, AmiReader, Example, split_by_meeting

KINDS = ["commitment", "decision", "open_question", "concern", "ambiguous"]
NONE = "none"
BASE = "kakaobank/kf-deberta-base"
SEED = 20260910
TGT_MAX = 94      # target tokens, identical in both context settings
CTX_UTT_MAX = 36  # tokens per context utterance


# --- data ---------------------------------------------------------------------


def build_rows(corpus: Path) -> tuple[list[dict], set[str]]:
    reader = AmiReader(corpus)
    starts: dict[str, list[float]] = {}

    def start_of(filename: str, index: int) -> float:
        if filename not in starts:
            times: list[float] = []
            last = 0.0
            for el in ET.parse(corpus / "words" / filename).getroot():
                if el.get(f"{NITE}id") is None:
                    continue
                t = el.get("starttime")
                last = float(t) if t not in (None, "") else last
                times.append(last)
            starts[filename] = times
        return starts[filename][index]

    decision_meetings = {p.name.split(".")[0] for p in (corpus / "decision" / "manual").glob("*.decision.xml")}

    rows = []
    for act in reader.acts():
        text = reader.text_of(act.spans)
        if not text.split():
            continue
        label = label_for(act.evidence)
        filename, first, _ = act.spans[0]
        rows.append(
            {
                "meeting": act.meeting,
                "id": act.act_id,
                "speaker": filename.split(".")[1],
                "start": start_of(filename, first),
                "text": text,
                "kind": label.kind.value if label else NONE,
            }
        )
    return rows, decision_meetings


def meeting_splits(rows: list[dict]) -> dict[str, set[str]]:
    labelled = [Example(r["id"], r["kind"], r["text"], r["meeting"]) for r in rows if r["kind"] != NONE]
    splits = split_by_meeting(labelled)
    return {name: {e.meeting for e in examples} for name, examples in splits.items()}


# --- encoding -----------------------------------------------------------------


class Encoder:
    def __init__(self, tok, rows: list[dict], context: int) -> None:
        self.tok = tok
        self.context = context
        self.ids = {r["id"]: tok(r["text"], add_special_tokens=False)["input_ids"] for r in rows}
        self.mark = {w: tok(w, add_special_tokens=False)["input_ids"] for w in ("before:", "after:", "same:", "other:")}
        by_meeting: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            by_meeting[r["meeting"]].append(r)
        self.neigh: dict[str, tuple[list[dict], list[dict]]] = {}
        for acts in by_meeting.values():
            acts.sort(key=lambda r: (r["start"], r["speaker"], r["id"]))
            for i, r in enumerate(acts):
                self.neigh[r["id"]] = (acts[max(0, i - context) : i], acts[i + 1 : i + 1 + context])

    def encode(self, row: dict) -> list[int]:
        tok = self.tok
        ids = [tok.cls_token_id] + self.ids[row["id"]][:TGT_MAX] + [tok.sep_token_id]
        if self.context:
            before, after = self.neigh[row["id"]]
            ctx: list[int] = []
            for tag, acts in (("before:", before), ("after:", after)):
                ctx += self.mark[tag]
                for a in acts:
                    ctx += self.mark["same:" if a["speaker"] == row["speaker"] else "other:"]
                    ctx += self.ids[a["id"]][:CTX_UTT_MAX]
            ids += ctx + [tok.sep_token_id]
        return ids


def batches(encoded: list[tuple[list[int], int]], size: int, pad: int, shuffle: bool, rng: random.Random):
    order = list(range(len(encoded)))
    if shuffle:
        rng.shuffle(order)
    else:
        order.sort(key=lambda i: len(encoded[i][0]))
    for s in range(0, len(order), size):
        chunk = [encoded[i] for i in order[s : s + size]]
        width = max(len(x) for x, _ in chunk)
        input_ids = torch.full((len(chunk), width), pad, dtype=torch.long)
        mask = torch.zeros((len(chunk), width), dtype=torch.long)
        for j, (x, _) in enumerate(chunk):
            input_ids[j, : len(x)] = torch.tensor(x)
            mask[j, : len(x)] = 1
        yield order[s : s + size], input_ids, mask, torch.tensor([y for _, y in chunk])


# --- scoring ------------------------------------------------------------------


def prf(gold: list[str], pred: list[str]) -> dict:
    out = {}
    for k in KINDS:
        tp = sum(g == k and p == k for g, p in zip(gold, pred))
        fp = sum(g != k and p == k for g, p in zip(gold, pred))
        fn = sum(g == k and p != k for g, p in zip(gold, pred))
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        out[k] = {"p": pr, "r": rc, "f1": 2 * pr * rc / (pr + rc) if pr + rc else 0.0, "support": tp + fn, "pred": tp + fp}
    out["macro_f1"] = sum(out[k]["f1"] for k in KINDS) / len(KINDS)
    return out


def auroc(pos: list[float], neg: list[float]) -> float:
    """P(score of a labelled act > score of a none act), ties half."""
    allv = sorted([(v, 1) for v in pos] + [(v, 0) for v in neg])
    rank_sum, i = 0.0, 0
    while i < len(allv):
        j = i
        while j < len(allv) and allv[j][0] == allv[i][0]:
            j += 1
        avg = (i + j + 1) / 2
        rank_sum += avg * sum(1 for t in allv[i:j] if t[1] == 1)
        i = j
    n1, n0 = len(pos), len(neg)
    return (rank_sum - n1 * (n1 + 1) / 2) / (n1 * n0) if n1 and n0 else float("nan")


# --- one condition ------------------------------------------------------------


def run(rows, splits, decision_meetings, tok, context: int, with_none: bool, epochs: int, out: Path,
        train_frac: float = 1.0, none_ratio: float = 1.0) -> dict:
    rng = random.Random(SEED)
    torch.manual_seed(SEED)
    labels = KINDS + ([NONE] if with_none else [])
    index = {k: i for i, k in enumerate(labels)}
    enc = Encoder(tok, rows, context)

    train_meetings = sorted(splits["train"])
    random.Random(SEED).shuffle(train_meetings)
    kept_train = set(train_meetings[: max(1, round(len(train_meetings) * train_frac))])

    def split_rows(name: str, natural: bool) -> list[dict]:
        ms = splits[name] if name != "train" else kept_train
        if natural:
            return [r for r in rows if r["meeting"] in ms and r["meeting"] in decision_meetings]
        return [r for r in rows if r["meeting"] in ms and r["kind"] != NONE]

    def with_none_sample(name: str) -> list[dict]:
        base = split_rows(name, natural=False)
        pool = [r for r in split_rows(name, natural=True) if r["kind"] == NONE]
        ratio = none_ratio if name == "train" else 1.0
        sample = random.Random(SEED).sample(pool, min(len(pool), round(len(base) * ratio)))
        return base + sample

    train_rows = with_none_sample("train") if with_none else split_rows("train", natural=False)
    val_rows = with_none_sample("validation") if with_none else split_rows("validation", natural=False)
    closed_rows = split_rows("test", natural=False)
    natural_rows = split_rows("test", natural=True)

    counts = Counter(r["kind"] for r in train_rows)
    weights = torch.tensor([len(train_rows) / (len(labels) * max(counts[k], 1)) for k in labels], dtype=torch.float)
    weights = weights / weights.mean()

    def encoded(rs):
        return [(enc.encode(r), index.get(r["kind"], -1)) for r in rs]

    tr, va = encoded(train_rows), encoded(val_rows)
    device = "cuda"
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE, num_labels=len(labels), id2label=dict(enumerate(labels)), label2id=index
    ).to(device)
    bs = 16 if context else 32
    steps = epochs * ((len(tr) + bs - 1) // bs)
    opt = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
    sched = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    loss_fn = nn.CrossEntropyLoss(weight=weights.to(device))

    def predict(enc_rows):
        model.eval()
        probs = [None] * len(enc_rows)
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            for idx, x, m, _ in batches(enc_rows, 128, tok.pad_token_id, False, rng):
                p = torch.softmax(model(input_ids=x.to(device), attention_mask=m.to(device)).logits.float(), -1).cpu()
                for j, i in enumerate(idx):
                    probs[i] = p[j].tolist()
        model.train()
        return probs

    best, best_state, history = -1.0, None, []
    t0 = time.time()
    for epoch in range(epochs):
        model.train()
        for _, x, m, y in batches(tr, bs, tok.pad_token_id, True, rng):
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = model(input_ids=x.to(device), attention_mask=m.to(device)).logits
            loss = loss_fn(logits.float(), y.to(device))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(), sched.step(), opt.zero_grad()
        vp = predict(va)
        vscore = prf([r["kind"] for r in val_rows], [labels[max(range(len(p)), key=p.__getitem__)] for p in vp])["macro_f1"]
        history.append({"epoch": epoch + 1, "val_macro_f1": vscore, "minutes": (time.time() - t0) / 60})
        print(f"  epoch {epoch + 1}: val macro F1 {vscore:.3f}  ({(time.time() - t0) / 60:.1f} min)", flush=True)
        if vscore > best:
            best = vscore
            best_state = {k: v.detach().to("cpu", copy=True) for k, v in model.state_dict().items()}
    model.load_state_dict(best_state)

    def argmax_label(p):
        return labels[max(range(len(p)), key=p.__getitem__)]

    cp = predict(encoded(closed_rows))
    closed = prf([r["kind"] for r in closed_rows], [argmax_label(p) for p in cp])

    npr = predict(encoded(natural_rows))
    ngold = [r["kind"] for r in natural_rows]
    npred = [argmax_label(p) for p in npr]
    natural = prf(ngold, npred)
    none_idx = [i for i, g in enumerate(ngold) if g == NONE]
    lab_idx = [i for i, g in enumerate(ngold) if g != NONE]
    none_pred = Counter(npred[i] for i in none_idx)
    conf = [max(npr[i][: len(KINDS)]) if not with_none else 1 - npr[i][len(KINDS)] for i in range(len(npr))]
    thresholds = {}
    for t in (0.5, 0.6, 0.7, 0.8, 0.9):
        thresholds[str(t)] = {
            "labelled_kept": sum(conf[i] >= t for i in lab_idx) / len(lab_idx),
            "none_kept": sum(conf[i] >= t for i in none_idx) / len(none_idx),
        }
    per_meeting = defaultdict(lambda: [0, 0])
    for i, r in enumerate(natural_rows):
        per_meeting[r["meeting"]][0] += 1
        if ngold[i] == NONE and npred[i] != NONE:
            per_meeting[r["meeting"]][1] += 1
    fp_rate = sum(v[1] for v in per_meeting.values()) / sum(v[0] for v in per_meeting.values())

    result = {
        "train_frac": train_frac,
        "none_ratio": none_ratio,
        "train_meetings": len(kept_train),
        "none_pool": len([r for r in rows if r["meeting"] in kept_train and r["meeting"] in decision_meetings and r["kind"] == NONE]),
        "context": context,
        "with_none": with_none,
        "train": dict(Counter(r["kind"] for r in train_rows)),
        "history": history,
        "closed": closed,
        "natural": natural,
        "natural_sizes": {"acts": len(natural_rows), "none": len(none_idx), "labelled": len(lab_idx), "meetings": len(per_meeting)},
        "none_predicted_as": dict(none_pred),
        "false_kinds_per_2400": round(fp_rate * 2400, 1),
        "confidence_auroc_labelled_vs_none": auroc([conf[i] for i in lab_idx], [conf[i] for i in none_idx]),
        "threshold_keep": thresholds,
        "minutes": (time.time() - t0) / 60,
    }
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    del model, opt
    torch.cuda.empty_cache()
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--only", default="")
    ap.add_argument("--plan", default="grid", choices=["grid", "data", "seeds"])
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    t = time.time()
    rows, decision_meetings = build_rows(args.corpus)
    splits = meeting_splits(rows)
    print(f"rows {len(rows):,} | decision-layer meetings {len(decision_meetings)} | "
          f"test meetings {len(splits['test'])}, of them with decision layer {len(splits['test'] & decision_meetings)} "
          f"| built in {time.time() - t:.0f}s", flush=True)
    tok = AutoTokenizer.from_pretrained(BASE)

    if args.plan == "seeds":
        global SEED
        for seed in (1, 2):
            SEED = seed
            name = f"seed{seed}-frac1.0-none1"
            print(f"== {name}", flush=True)
            r = run(rows, splits, decision_meetings, tok, 0, True, args.epochs, args.out / f"{name}.json")
            print(f"  train {sum(r['train'].values()):,} | closed {r['closed']['macro_f1']:.3f} | "
                  f"natural {r['natural']['macro_f1']:.3f} | false per 2400 {r['false_kinds_per_2400']} | "
                  f"auroc {r['confidence_auroc_labelled_vs_none']:.3f}", flush=True)
        return

    if args.plan == "data":
        plan = [(f, 1.0) for f in (0.125, 0.25, 0.5)] + [(1.0, 2.0), (1.0, 99.0)]
        for frac, ratio in plan:
            name = f"data-frac{frac}-none{ratio:g}"
            print(f"== {name}", flush=True)
            r = run(rows, splits, decision_meetings, tok, 0, True, args.epochs, args.out / f"{name}.json", frac, ratio)
            print(f"  train {sum(r['train'].values()):,} (none {r['train'].get('none', 0):,}, meetings {r['train_meetings']}) | "
                  f"closed {r['closed']['macro_f1']:.3f} | natural {r['natural']['macro_f1']:.3f} | "
                  f"false per 2400 {r['false_kinds_per_2400']} | auroc {r['confidence_auroc_labelled_vs_none']:.3f}", flush=True)
        return

    for context in (0, 2):
        for with_none in (False, True):
            name = f"ctx{context}-{'6way' if with_none else '5way'}"
            if args.only and name not in args.only.split(","):
                continue
            print(f"== {name}", flush=True)
            r = run(rows, splits, decision_meetings, tok, context, with_none, args.epochs, args.out / f"{name}.json")
            print(f"  closed macro F1 {r['closed']['macro_f1']:.3f} | natural macro F1 {r['natural']['macro_f1']:.3f} | "
                  f"false kinds per 2400 {r['false_kinds_per_2400']} | auroc {r['confidence_auroc_labelled_vs_none']:.3f}", flush=True)


if __name__ == "__main__":
    main()
