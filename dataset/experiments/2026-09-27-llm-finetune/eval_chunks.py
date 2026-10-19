"""Score Qwen3-4B (base, or base + LoRA adapter) on chunked action-item picking.

    python eval_chunks.py --split test --tag base
    python eval_chunks.py --split test --tag ft_e2 --adapter runs/lora/epoch2

Micro P/R/F1 over `[신규]` utterances; `gold_ignore` rows (recalls, labeller
disagreements) count neither way. A number the model names that is not a
`[신규]` utterance of that chunk counts as a false positive. Unparseable output
counts as an empty answer and is tallied separately.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

HERE = Path(__file__).parent
CHECKPOINT = "Qwen/Qwen3-4B-Instruct-2507"


def parse(text: str) -> list[int] | None:
    match = re.search(r"\{.*?\}", text, re.S)
    if not match:
        return None
    try:
        items = json.loads(match.group(0)).get("items")
    except (json.JSONDecodeError, AttributeError):
        return None
    if not isinstance(items, list):
        return None
    return [int(i) for i in items if isinstance(i, int) or (isinstance(i, str) and i.isdigit())]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--adapter")
    ap.add_argument("--model", default=CHECKPOINT, help="base checkpoint or a merged model dir")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    rows = [json.loads(line) for line in (HERE / f"{args.split}.jsonl").open(encoding="utf-8")]
    if args.limit:
        rows = rows[: args.limit]

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.bfloat16).to("cuda")
    if args.adapter:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()

    tp = fp = fn = bad = 0
    per_meeting: dict[str, list[int]] = {}
    out_rows = []
    start = time.time()
    for n, r in enumerate(rows, 1):
        msgs = [{"role": "system", "content": r["system"]}, {"role": "user", "content": r["user"]}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_tensors="pt").to("cuda")
        with torch.no_grad():
            gen = model.generate(
                **enc, max_new_tokens=96, do_sample=False, pad_token_id=tok.eos_token_id
            )
        answer = tok.decode(gen[0][enc["input_ids"].shape[1] :], skip_special_tokens=True)
        pred = parse(answer)
        if pred is None:
            bad += 1
            pred = []
        gold, ignore = set(r["gold_yes"]), set(r["gold_ignore"])
        p = set(pred) - ignore
        m = per_meeting.setdefault(r["meeting"], [0, 0, 0])
        m[0] += len(p & gold)
        m[1] += len(p - gold)
        m[2] += len(gold - p)
        tp, fp, fn = tp + len(p & gold), fp + len(p - gold), fn + len(gold - p)
        out_rows.append({"meeting": r["meeting"], "chunk": r["chunk"], "raw": answer, "pred": pred})
        if n % 25 == 0:
            print(f"{n}/{len(rows)} {time.time() - start:.0f}s", flush=True)

    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    summary = {
        "tag": args.tag,
        "split": args.split,
        "chunks": len(rows),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(prec, 3),
        "recall": round(rec, 3),
        "f1": round(f1, 3),
        "unparseable": bad,
        "seconds": round(time.time() - start, 1),
        "per_meeting": per_meeting,
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / f"{args.split}_{args.tag}.json").write_text(
        json.dumps({"summary": summary, "rows": out_rows}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(json.dumps({k: v for k, v in summary.items() if k != "per_meeting"}))


if __name__ == "__main__":
    main()
