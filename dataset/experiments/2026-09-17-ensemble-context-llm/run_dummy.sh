#!/usr/bin/env bash
# Score every model of today on the ten dummy team meetings (planted labels: C copied
# to B in team_dummy/score_input). Queued behind run_llm.sh, which is queued behind
# run_context.sh -- all three need the GPU. Counts only. Run from the repo root.
set -euo pipefail
E=dataset/experiments/2026-09-17-ensemble-context-llm
K=dataset/experiments/2026-09-15-korean-v1
S=dataset/team_dummy/score_input
PY=C:/Users/hi/miniforge3/envs/aiprj/python.exe
export MSYS2_ENV_CONV_EXCL=PYTHONPATH HF_HUB_OFFLINE=1 PYTHONIOENCODING=utf-8

echo "$(date +%T) waiting for run_context.sh and run_llm.sh"
while ps -ef | grep -v grep | grep -qE 'bash dataset/experiments/2026-09-17-ensemble-context-llm/run_(context|llm).sh'; do sleep 30; done
echo "$(date +%T) GPU queue clear"
free=0
for i in $(seq 1 60); do
  read -r util mem < <(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits | tr -d ',')
  if [ "$util" -lt 10 ] && [ "$mem" -lt 3000 ]; then free=$((free+1)); else free=0; fi
  [ "$free" -ge 3 ] && break
  sleep 10
done
echo "$(date +%T) GPU util ${util}% mem ${mem} MiB (free checks ${free})"
if [ "$free" -lt 3 ]; then echo "GPU busy for 10 minutes - not starting"; exit 3; fi

score() {  # name, context, ckpts...
  local name=$1 ctx=$2; shift 2
  local args=""; for c in "$@"; do args="$args --ckpt $c"; done
  echo "=== $name"
  "$PY" $E/score_models.py --context $ctx --sheets $S --out $E/scores/dummy_$name $args 2>&1 | grep -vE "Loading weights|^scored"
}
score v2_s0910 0 $K/run_syn_none_probe
score ens_v2 0 $K/run_syn_none_probe $K/run_syn_none_probe_s20260916 $K/run_syn_none_probe_s20260917
score ens_v3 0 $K/run_v3 $K/run_v3_s20260916 $K/run_v3_s20260917
CTX=""; for s in 20260910 20260916 20260917; do [ -f $E/runs/ctx2_s$s/run.json ] && CTX="$CTX $E/runs/ctx2_s$s"; done
[ -n "$CTX" ] && score ens_ctx2 2 $CTX
for base in ens_v2 ens_ctx2; do
  [ -d $E/scores/dummy_$base ] || continue
  echo "=== LLM boundary on $base"
  "$PY" $E/llm_boundary.py run --sheets $S --model-scores $E/scores/dummy_$base --out $E/scores/dummy_llm_$base 2>&1 | grep -vE "Loading weights|it/s\]"
done
echo "$(date +%T) done"
