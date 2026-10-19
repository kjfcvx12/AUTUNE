"""QLoRA fine-tune of Qwen3-4B-Instruct-2507 on train.jsonl (aiprj env, RTX 3060 12GB).

    python train_lora.py --epochs 2 --out runs/lora

4-bit NF4 base, bf16 compute, LoRA r=16 on every attention and MLP projection,
gradient checkpointing, batch 1 with gradient accumulation. Loss on the answer
tokens only. Saves the adapter after each epoch and logs val loss.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

HERE = Path(__file__).parent
CHECKPOINT = "Qwen/Qwen3-4B-Instruct-2507"


def encode(tok, row: dict) -> tuple[torch.Tensor, torch.Tensor]:
    msgs = [{"role": "system", "content": row["system"]}, {"role": "user", "content": row["user"]}]
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    full = tok.apply_chat_template(
        [*msgs, {"role": "assistant", "content": row["answer"]}], tokenize=False
    )
    assert full.startswith(prompt), "chat template does not extend the prompt"
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    f_ids = tok(full, add_special_tokens=False)["input_ids"]
    ids = torch.tensor(f_ids)
    labels = ids.clone()
    labels[: len(p_ids)] = -100
    return ids, labels


def answer_loss(model, ids: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
    """Cross-entropy on the answer tokens only, computing logits only there.

    The answer (JSON + end-of-turn) is always the tail of the sequence, so
    `logits_to_keep` skips the lm_head over the ~1.8k prompt positions -- a
    1.8k x 151k logits tensor (plus its fp32 upcast and gradient) was what
    filled the 12 GB card.
    """
    n_ans = int((labels != -100).sum())
    keep = n_ans + 1
    logits = model(input_ids=ids[None].cuda(), logits_to_keep=keep).logits[0]
    return torch.nn.functional.cross_entropy(
        logits[:-1].float(), labels[-n_ans:].cuda()
    )


def val_loss(model, data) -> float:
    model.eval()
    total, n = 0.0, 0
    with torch.no_grad():
        for ids, labels in data:
            total += answer_loss(model, ids, labels).item()
            n += 1
    model.train()
    return total / n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--accum", type=int, default=8)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--out", default="runs/lora")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    out = HERE / args.out
    out.mkdir(parents=True, exist_ok=True)

    tok = AutoTokenizer.from_pretrained(CHECKPOINT)
    train = [encode(tok, json.loads(x)) for x in (HERE / "train.jsonl").open(encoding="utf-8")]
    val = [encode(tok, json.loads(x)) for x in (HERE / "val.jsonl").open(encoding="utf-8")]
    lens = sorted(len(i) for i, _ in train)
    print(f"train={len(train)} val={len(val)} tokens median={lens[len(lens) // 2]} max={lens[-1]}")

    model = AutoModelForCausalLM.from_pretrained(
        CHECKPOINT,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        ),
        dtype=torch.bfloat16,
        device_map={"": 0},
    )
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    model = get_peft_model(
        model,
        LoraConfig(
            r=args.rank,
            lora_alpha=2 * args.rank,
            lora_dropout=0.05,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            task_type="CAUSAL_LM",
        ),
    )
    model.print_trainable_parameters()

    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=args.lr, weight_decay=0.0)
    steps = math.ceil(len(train) / args.accum) * args.epochs
    warmup = max(1, steps // 20)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt,
        lambda s: (s + 1) / warmup
        if s < warmup
        else 0.5 * (1 + math.cos(math.pi * (s - warmup) / max(1, steps - warmup))),
    )

    log = (out / "train_log.jsonl").open("a", encoding="utf-8")
    print(f"optimizer steps={steps} warmup={warmup}")
    print(f"val loss before: {val_loss(model, val):.4f}", flush=True)
    model.train()
    step, start = 0, time.time()
    for epoch in range(1, args.epochs + 1):
        order = list(range(len(train)))
        random.shuffle(order)
        running = 0.0
        for n, i in enumerate(order, 1):
            ids, labels = train[i]
            loss = answer_loss(model, ids, labels) / args.accum
            loss.backward()
            running += loss.item()
            if n % args.accum == 0 or n == len(order):
                torch.nn.utils.clip_grad_norm_(params, 1.0)
                opt.step()
                sched.step()
                opt.zero_grad(set_to_none=True)
                step += 1
                if step % 10 == 0:
                    rec = {
                        "epoch": epoch,
                        "step": step,
                        "loss": round(running / 10, 4),
                        "lr": sched.get_last_lr()[0],
                        "elapsed_min": round((time.time() - start) / 60, 1),
                        "peak_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2),
                    }
                    print(json.dumps(rec), flush=True)
                    log.write(json.dumps(rec) + "\n")
                    running = 0.0
        v = val_loss(model, val)
        print(f"epoch {epoch} val loss {v:.4f}", flush=True)
        log.write(json.dumps({"epoch": epoch, "val_loss": v}) + "\n")
        model.save_pretrained(out / f"epoch{epoch}")
    log.close()
    print(f"done in {(time.time() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
