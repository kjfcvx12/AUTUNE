"""Fold a LoRA adapter into the bf16 base weights (CPU; no GPU needed).

    python merge_adapter.py runs/lora/epoch2 runs/merged_e2

bf16 on purpose: the fp32 upcast path segfaults on this machine (HISTORY 09-26).
"""

from __future__ import annotations

import sys
import time

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

CHECKPOINT = "Qwen/Qwen3-4B-Instruct-2507"


def main() -> None:
    adapter, out = sys.argv[1], sys.argv[2]
    start = time.time()
    base = AutoModelForCausalLM.from_pretrained(CHECKPOINT, dtype=torch.bfloat16)
    merged = PeftModel.from_pretrained(base, adapter).merge_and_unload()
    merged.save_pretrained(out)
    AutoTokenizer.from_pretrained(CHECKPOINT).save_pretrained(out)
    print(f"merged -> {out} in {time.time() - start:.0f}s")


if __name__ == "__main__":
    main()
