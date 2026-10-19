#!/usr/bin/env bash
# Step 3, queued behind step 2: both need the GPU (the context training holds ~9 GB,
# Qwen3-4B needs ~8 GB of the card's 12). Runs the LLM boundary judge on top of
# the v2 seed ensemble, and on top of the context ensemble if step 2 produced one.
# Counts only. Run from the repo root.
set -euo pipefail
E=dataset/experiments/2026-09-17-ensemble-context-llm
BLIND=dataset/extraction_eval_blind
PROBE=dataset/experiments/2026-09-15-decision-probe/score_input
PY=C:/Users/hi/miniforge3/envs/aiprj/python.exe
export MSYS2_ENV_CONV_EXCL=PYTHONPATH HF_HUB_OFFLINE=1 PYTHONIOENCODING=utf-8

echo "$(date +%T) waiting for run_context.sh"
while ps -ef | grep -v grep | grep -q 'bash dataset/experiments/2026-09-17-ensemble-context-llm/run_context.sh'; do sleep 30; done
echo "$(date +%T) run_context.sh exited"

free=0
for i in $(seq 1 60); do
  read -r util mem < <(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits | tr -d ',')
  if [ "$util" -lt 10 ] && [ "$mem" -lt 3000 ]; then free=$((free+1)); else free=0; fi
  [ "$free" -ge 3 ] && break
  sleep 10
done
echo "$(date +%T) GPU util ${util}% mem ${mem} MiB (free checks ${free})"
if [ "$free" -lt 3 ]; then echo "GPU busy for 10 minutes - not starting"; exit 3; fi

echo "=== selftest (invented sentences)"
"$PY" $E/llm_boundary.py selftest 2>&1 | grep -vE "Loading weights|it/s\]"

for base in ens_v2 ens_ctx2; do
  for set in probe blind; do
    scores=$E/scores/${base}_$set
    [ -d "$scores" ] || { echo "skip $base on $set: no classifier scores"; continue; }
    src=$PROBE; [ $set = blind ] && src=$BLIND
    echo "=== LLM boundary on $base, $set"
    "$PY" $E/llm_boundary.py run --sheets $src --model-scores $scores --out $E/scores/llm_${base}_$set 2>&1 | grep -vE "Loading weights|it/s\]"
  done
done
echo "$(date +%T) done"
