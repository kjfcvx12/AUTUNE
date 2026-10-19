"""Average the weights of v2's three seed checkpoints into one checkpoint ("model soup").

If it scores like the 3-model ensemble, the product gets the ensemble's accuracy at one
model's inference cost and no code change. All three share the base encoder and head
shape, so a plain mean of every floating-point tensor is well defined.
"""
from __future__ import annotations
import shutil
from pathlib import Path
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

K = Path(__file__).resolve().parents[1] / "2026-09-15-korean-v1"
SRC = [K / "run_syn_none_probe", K / "run_syn_none_probe_s20260916", K / "run_syn_none_probe_s20260917"]
OUT = Path(__file__).resolve().parent / "runs" / "soup_v2"

models = [AutoModelForSequenceClassification.from_pretrained(p) for p in SRC]
states = [m.state_dict() for m in models]
avg = {}
for key, t in states[0].items():
    avg[key] = torch.stack([s[key].float() for s in states]).mean(0).to(t.dtype) if t.is_floating_point() else t
soup = models[0]
soup.load_state_dict(avg)
OUT.mkdir(parents=True, exist_ok=True)
soup.save_pretrained(OUT)
AutoTokenizer.from_pretrained(SRC[0]).save_pretrained(OUT)
shutil.copyfile(SRC[0] / "run.json", OUT / "source_run.json")
print("tensors averaged:", sum(1 for t in states[0].values() if t.is_floating_point()), "| wrote", OUT.name)
