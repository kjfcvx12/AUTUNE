"""Make a checkpoint smaller, and say what it costs.

    python export_light.py --ckpt runs/share_s20260910 --out runs/share_light \
        --sheets ../../extraction_eval_blind2/chaired_12

Writes two things beside the original and measures all three the same way:

  fp16/   the same weights at half precision (`save_pretrained`), loadable by
          `from_pretrained`, so nothing in module B changes to use it.
  int8.pt a dynamically quantised state dict (`torch.ao.quantization`), Linear
          layers only. CPU inference is the deployment path, and that is where
          dynamic quantisation both shrinks and speeds up.

For each: directory size on disk, seconds to classify a fixed set of utterances
on CPU, and the labels it produces — how many rows differ from the fp32 model's,
and the score against the sheets' gold.

Read the `macro5` and `acts` columns, not `acc`. `none` is about three rows in
four, so a variant that goes quiet *gains* accuracy while losing the product:
int8 here scores 81.8% against fp32's 81.3% and finds 65 acts where fp32 finds
165 (macro F1 0.160 against 0.289).

Counts only: no utterance text is printed.
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")

import torch  # noqa: E402
from transformers import AutoModelForSequenceClassification, AutoTokenizer  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "experiments" / "2026-09-17-ensemble-context-llm"))
from score_models import LABELS, TGT_MAX, read_sheet  # noqa: E402


def size_mb(path: Path) -> float:
    """What would actually be shipped: the weights and the tokenizer.

    A training run's directory also holds `checkpoints/`, the per-epoch copies the
    trainer keeps. Counting those reported 7.4 GB for a 710 MB model.
    """
    if path.is_file():
        return path.stat().st_size / 1e6
    return (
        sum(
            f.stat().st_size
            for f in path.rglob("*")
            if f.is_file() and "checkpoint" not in str(f.relative_to(path)).lower()
        )
        / 1e6
    )


def rows_of(sheets: Path, limit: int) -> tuple[list[str], list[str]]:
    """Utterances to classify and their gold labels, from the A/B sheets."""
    texts: list[str] = []
    gold: list[str] = []
    for a_path in sorted(sheets.glob("*.A.csv")):
        meeting = a_path.name.split(".")[0]
        b_path = sheets / f"{meeting}.B.csv"
        if not b_path.exists():
            continue
        labels = {r["row"]: (r.get("kind") or "").strip() for r in read_sheet(b_path)}
        for row in read_sheet(a_path):
            kind = labels.get(row["row"], "")
            if kind in LABELS:
                texts.append(row["text"])
                gold.append(kind)
            if len(texts) >= limit:
                return texts, gold
    return texts, gold


def encode(tok, texts: list[str]) -> list[list[int]]:
    return [tok(t, truncation=True, max_length=TGT_MAX)["input_ids"] for t in texts]


def predict(model, tok, encoded: list[list[int]], batch: int = 16) -> tuple[list[str], float]:
    """Labels and wall-clock seconds, on CPU.

    ``score_models.probabilities`` moves its tensors to cuda -- it was written for
    the GPU scorer -- and the whole point here is what a worker costs on a CPU.
    """
    order = sorted(range(len(encoded)), key=lambda i: len(encoded[i]))
    labels: list[str] = [""] * len(encoded)
    started = time.perf_counter()
    with torch.inference_mode():
        for start in range(0, len(order), batch):
            idx = order[start : start + batch]
            width = max(len(encoded[i]) for i in idx)
            ids = torch.tensor(
                [encoded[i] + [tok.pad_token_id] * (width - len(encoded[i])) for i in idx]
            )
            mask = torch.tensor([[1] * len(encoded[i]) + [0] * (width - len(encoded[i])) for i in idx])
            logits = model(input_ids=ids, attention_mask=mask).logits
            for position, row in zip(idx, logits.argmax(-1).tolist(), strict=True):
                labels[position] = LABELS[row]
    return labels, time.perf_counter() - started


def kappa(pairs: list[tuple[str, str]]) -> float:
    """Cohen's kappa over the six kinds -- the same one the scorer reports."""
    n = len(pairs)
    agreed = sum(1 for a, b in pairs if a == b) / n
    first, second = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    expected = sum((first[k] / n) * (second[k] / n) for k in set(first) | set(second))
    return 1.0 if expected == 1 else (agreed - expected) / (1 - expected)


def macro5(labels: list[str], gold: list[str]) -> float:
    """Macro F1 over the five acts, `none` excluded from the average (ADR 0006).

    Plain accuracy is close to useless here: `none` is roughly three rows in four,
    so a model that says nothing at all already scores in the seventies.
    """
    scores = []
    for kind in (k for k in LABELS if k != "none"):
        pred = sum(1 for a in labels if a == kind)
        want = sum(1 for b in gold if b == kind)
        hit = sum(1 for a, b in zip(labels, gold, strict=True) if a == b == kind)
        scores.append(0.0 if not hit else 2 * hit / (pred + want))
    return sum(scores) / len(scores)


def report(name: str, size: float, seconds: float, n: int, labels: list[str], base: list[str], gold: list[str]) -> None:
    same = sum(1 for a, b in zip(labels, base, strict=True) if a == b)
    hit = sum(1 for a, b in zip(labels, gold, strict=True) if a == b)
    per_meeting = seconds / n * 2400
    print(
        f"{name:<8}{size:>9.0f} MB{seconds:>9.1f} s{per_meeting:>10.0f} s"
        f"{same / n:>10.1%}{hit / n:>10.1%}"
        f"{kappa(list(zip(labels, gold, strict=True))):>9.3f}{macro5(labels, gold):>9.3f}"
        f"{sum(1 for a in labels if a != 'none'):>7}"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--sheets", type=Path, required=True, help="A/B sheets to measure on")
    ap.add_argument("--rows", type=int, default=600)
    args = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(args.ckpt)
    texts, gold = rows_of(args.sheets, args.rows)
    encoded = encode(tok, texts)
    print(f"{len(texts)} utterances from {args.sheets.name}, CPU, batch as scored\n")
    print(
        f"{'model':<8}{'size':>12}{'time':>11}{'per 45min':>12}{'= fp32':>10}{'acc':>10}"
        f"{'kappa':>9}{'macro5':>9}{'acts':>7}"
    )

    torch.set_num_threads(os.cpu_count() or 4)
    fp32 = AutoModelForSequenceClassification.from_pretrained(args.ckpt).eval()
    base_labels, base_seconds = predict(fp32, tok, encoded)
    report("fp32", size_mb(args.ckpt), base_seconds, len(texts), base_labels, base_labels, gold)

    half_dir = args.out / "fp16"
    half_dir.mkdir(parents=True, exist_ok=True)
    AutoModelForSequenceClassification.from_pretrained(args.ckpt, dtype=torch.float16).save_pretrained(half_dir)
    for name in ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "spiece.model"):
        source = args.ckpt / name
        if source.exists():
            shutil.copyfile(source, half_dir / name)
    # Loaded back in fp32 on CPU: half precision is how it is stored, not how a
    # CPU multiplies it. The point is the file, and what the rounding costs.
    half = AutoModelForSequenceClassification.from_pretrained(half_dir, dtype=torch.float32).eval()
    labels, seconds = predict(half, tok, encoded)
    report("fp16", size_mb(half_dir), seconds, len(texts), labels, base_labels, gold)

    quantised = torch.ao.quantization.quantize_dynamic(
        AutoModelForSequenceClassification.from_pretrained(args.ckpt).eval(),
        {torch.nn.Linear},
        dtype=torch.qint8,
    )
    int8_path = args.out / "int8.pt"
    int8_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(quantised.state_dict(), int8_path)
    labels, seconds = predict(quantised, tok, encoded)
    report("int8", size_mb(int8_path), seconds, len(texts), labels, base_labels, gold)

    # Linear layers in int8 and the embedding table in fp16. Dynamic quantisation
    # leaves embeddings alone, and here they are 100M of the 186M parameters — so
    # the int8 file above is mostly a full-precision vocabulary. Found by measuring.
    mixed = torch.ao.quantization.quantize_dynamic(
        AutoModelForSequenceClassification.from_pretrained(args.ckpt).eval(),
        {torch.nn.Linear},
        dtype=torch.qint8,
    )
    # Halved **on disk only**: a quantised Linear multiplies in float, and an
    # embedding kept in half feeds one a Half tensor ("expected scalar type Float
    # but found Half"). The loader casts them back, so the labels and the speed are
    # int8's and only the file is smaller.
    # A quantised state dict is not all tensors -- a packed Linear stores its
    # dtype and its scales as plain objects -- so ask before halving.
    state = {
        key: (
            value.half()
            if isinstance(value, torch.Tensor) and value.dtype is torch.float32 and "embed" in key
            else value
        )
        for key, value in mixed.state_dict().items()
    }
    mixed_path = args.out / "int8_fp16emb.pt"
    torch.save(state, mixed_path)
    labels, seconds = predict(mixed, tok, encoded)
    report("int8+16", size_mb(mixed_path), seconds, len(texts), labels, base_labels, gold)

    print("\nlabel counts (fp32):", dict(Counter(base_labels)))


if __name__ == "__main__":
    main()
