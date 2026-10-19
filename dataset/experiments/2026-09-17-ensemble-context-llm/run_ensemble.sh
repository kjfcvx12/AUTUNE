#!/usr/bin/env bash
# Step 1: seed ensembles of v2 and v3, on the blind set and the decision probe.
# First a single-checkpoint run that must reproduce the 09-16 v2 probe score
# (15/61, macro5 0.369) -- if it does not, the encoder differs from ko_sanity.py
# and nothing after it means anything. Counts only. Run from the repo root.
set -euo pipefail
E=dataset/experiments/2026-09-17-ensemble-context-llm
K=dataset/experiments/2026-09-15-korean-v1
BLIND=dataset/extraction_eval_blind
PROBE=dataset/experiments/2026-09-15-decision-probe/score_input
PY=C:/Users/hi/miniforge3/envs/aiprj/python.exe
export MSYS2_ENV_CONV_EXCL=PYTHONPATH HF_HUB_OFFLINE=1 PYTHONIOENCODING=utf-8
read -r util mem < <(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits | tr -d ',')
echo "$(date +%T) GPU util ${util}% mem ${mem} MiB"
if [ "$util" -ge 10 ] || [ "$mem" -ge 3000 ]; then echo "GPU busy - not starting"; exit 3; fi

echo "=== CHECK v2 seed 20260910 alone, probe (expect decision 25/61/15, macro 0.369)"
"$PY" $E/score_models.py --sheets $PROBE --out $E/scores/check_v2_s0910_probe --ckpt $K/run_syn_none_probe

V2="--ckpt $K/run_syn_none_probe --ckpt $K/run_syn_none_probe_s20260916 --ckpt $K/run_syn_none_probe_s20260917"
V3="--ckpt $K/run_v3 --ckpt $K/run_v3_s20260916 --ckpt $K/run_v3_s20260917"
for set in probe blind; do
  src=$PROBE; [ $set = blind ] && src=$BLIND
  for name in v2 v3; do
    ck=$V2; [ $name = v3 ] && ck=$V3
    echo "=== ENSEMBLE $name x3 on $set"
    "$PY" $E/score_models.py --sheets $src --out $E/scores/ens_${name}_$set $ck
  done
done
echo "$(date +%T) done"
