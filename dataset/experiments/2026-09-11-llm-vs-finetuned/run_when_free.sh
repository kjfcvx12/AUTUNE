#!/usr/bin/env bash
# Wait until the GPU is free (no compute process, < 3 GB used, three checks in a
# row a minute apart), then run the LLM comparison and score it. Gives up after
# six hours. Another session's experiments share this GPU; see the memory note.
set -u
cd "$(dirname "$0")/../../.."
HERE=dataset/experiments/2026-09-11-llm-vs-finetuned
BASE=dataset/experiments/2026-09-11-official-6way
PY=/c/Users/hi/miniforge3/envs/aiprj/python.exe
export PYTHONPATH="modules/extraction/src;packages/contracts/src;packages/core/src;packages/integrations/src"
export PYTHONIOENCODING=utf-8 HF_HUB_OFFLINE=1

free=0
for _ in $(seq 1 360); do
  compute=$(nvidia-smi | grep -cE "^\|\s+[0-9]+\s+N/A\s+N/A\s+[0-9]+\s+C\s")
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | tr -d ' ')
  if [ "$compute" -eq 0 ] && [ "$used" -lt 3000 ]; then free=$((free + 1)); else free=0; fi
  echo "$(date -u +%H:%M) compute=$compute used=${used}MiB free_checks=$free"
  [ "$free" -ge 3 ] && break
  sleep 60
done
[ "$free" -ge 3 ] || { echo "gave up: GPU still busy after six hours"; exit 1; }

echo "== selftest $(date -u +%H:%M)"
"$PY" "$HERE/llm_zero_shot.py" selftest 2>&1 | grep -vE "Warning|warn|Loading"
echo "== run $(date -u +%H:%M)"
"$PY" "$HERE/llm_zero_shot.py" run 2>&1 | grep -vE "Warning|warn|Loading" || exit 1
for s in test test_closed; do
  echo "== score $s"
  uv run --frozen --package autune-extraction python -m autune_extraction.eval \
    --eval-set "$BASE/splits/$s.jsonl" --predictions "$HERE/pred_llm_$s.jsonl" | head -16 | tee "$HERE/score_llm_$s.txt"
done
echo "== done $(date -u +%H:%M)"
