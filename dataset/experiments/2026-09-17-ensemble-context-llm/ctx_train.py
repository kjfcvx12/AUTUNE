"""Train v2 with context: autune_extraction.training.train, with only the input changed.

    python ctx_train.py --data splits/ctx2 --out runs/ctx2_s20260910 --seed 20260910

Everything that is not the input is the production training loop's: the base
encoder, 3 epochs, batch 16, lr 2e-5, inverse-frequency class weights, best epoch
by the harness's macro F1 on AMI validation. The input is the encoding
score_models.py uses at inference -- target cut at 94 tokens, then "before:" and
"after:" with "same:"/"other:" per neighbour cut at 36 -- so training and scoring
cannot drift apart.

Writes a checkpoint plus run.json. Prints metrics only.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch
from torch import nn
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
    set_seed,
)

from autune_extraction.eval.metrics import score
from autune_extraction.labels import kind_or_none
from autune_extraction.training.dataset import LABELS, class_weights, read_split
from autune_extraction.training.train import RunConfig, fingerprint

TGT_MAX = 94
CTX_UTT_MAX = 36


def encode_rows(tok, rows: list[dict]) -> list[list[int]]:
    mark = {w: tok(w, add_special_tokens=False)["input_ids"] for w in ("before:", "after:", "same:", "other:")}
    out = []
    for r in rows:
        seq = [tok.cls_token_id] + tok(r["text"], add_special_tokens=False)["input_ids"][:TGT_MAX] + [tok.sep_token_id]
        ctx: list[int] = []
        for tag in ("before", "after"):
            ctx += mark[f"{tag}:"]
            for n in r[tag]:
                ctx += mark["same:" if n["same"] else "other:"]
                ctx += tok(n["text"], add_special_tokens=False)["input_ids"][:CTX_UTT_MAX]
        out.append(seq + ctx + [tok.sep_token_id])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed", type=int, required=True)
    args = ap.parse_args()
    if (args.out / "run.json").exists():
        print(f"skip: {args.out} already trained")
        return

    config = RunConfig(seed=args.seed, max_length=512)
    set_seed(config.seed)
    tok = AutoTokenizer.from_pretrained(config.base_checkpoint)
    model = AutoModelForSequenceClassification.from_pretrained(
        config.base_checkpoint, num_labels=len(LABELS),
        id2label=dict(enumerate(LABELS)), label2id={label: i for i, label in enumerate(LABELS)},
    )

    data = {}
    for name in ("train", "validation"):
        examples = read_split(args.data, name)
        rows = [json.loads(line) for line in (args.data / f"{name}.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        assert [r["utterance_id"] for r in rows] == [e.utterance_id for e in examples]
        ids = encode_rows(tok, rows)
        data[name] = (examples, [{"input_ids": x, "attention_mask": [1] * len(x), "labels": e.label_id} for x, e in zip(ids, examples)])
        lengths = sorted(len(x) for x in ids)
        print(f"{name}: {len(ids)} rows, tokens median {lengths[len(lengths) // 2]} max {lengths[-1]}", flush=True)

    weights = torch.tensor(class_weights(data["train"][0]), dtype=torch.float)

    class WeightedTrainer(Trainer):
        def compute_loss(self, model, inputs, return_outputs=False, **kwargs):  # noqa: ANN001, ANN201
            labels = inputs.pop("labels")
            outputs = model(**inputs)
            loss = nn.CrossEntropyLoss(weight=weights.to(outputs.logits.device))(outputs.logits, labels)
            return (loss, outputs) if return_outputs else loss

    def macro_f1(prediction) -> dict[str, float]:  # noqa: ANN001
        predicted = np.argmax(prediction.predictions, axis=1)
        report = score(
            [kind_or_none(LABELS[int(i)]) for i in prediction.label_ids],
            [kind_or_none(LABELS[int(i)]) for i in predicted],
        )
        return {**{f"f1_{s.kind.value}": s.f1 for s in report.per_class}, "macro_f1": report.macro_f1}

    trainer = WeightedTrainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(args.out / "checkpoints"),
            num_train_epochs=config.epochs,
            per_device_train_batch_size=config.batch_size,
            per_device_eval_batch_size=config.batch_size * 2,
            learning_rate=config.learning_rate,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="macro_f1",
            seed=config.seed,
            report_to=[],
        ),
        train_dataset=data["train"][1],
        eval_dataset=data["validation"][1],
        data_collator=DataCollatorWithPadding(tok),
        compute_metrics=macro_f1,
    )
    trainer.train()
    metrics = trainer.evaluate()
    args.out.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(args.out))
    tok.model_max_length = 512
    tok.save_pretrained(str(args.out))
    (args.out / "run.json").write_text(json.dumps({
        "config": asdict(config), "context": {"target_max": TGT_MAX, "neighbour_max": CTX_UTT_MAX},
        "labels": list(LABELS),
        "splits": {n: {"fingerprint": fingerprint(args.data / f"{n}.jsonl")} for n in ("train", "validation")},
        "validation": metrics,
    }, indent=2), encoding="utf-8")
    print(f"wrote {args.out} | validation macro F1 {metrics.get('eval_macro_f1')}", flush=True)


if __name__ == "__main__":
    main()
