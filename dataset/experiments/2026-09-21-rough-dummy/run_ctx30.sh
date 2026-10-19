#!/usr/bin/env bash
# Train clean30_ctx2 and rough30_ctx2 (#323) and score both, plus the existing
# no-context clean30/rough30, on every part of the evaluation set with the
# matching --context. Isolates "does context help" from "does rough help":
# same underlying rows as the existing clean30/rough30 comparison, context is
# the only new variable.
set -euo pipefail
E=dataset/experiments/2026-09-21-rough-dummy
CTXDIR=dataset/experiments/2026-09-17-ensemble-context-llm
PY=C:/Users/hi/miniforge3/envs/aiprj/python.exe
PD="C:/Users/hi/AppData/Local/Temp/claude/F--0final-AUTUNE/315704b3-93a1-4653-889a-4840c786d480/scratchpad/pydeps"
export PYTHONPATH="modules/extraction/src;packages/contracts/src;packages/core/src;packages/integrations/src;$CTXDIR;$PD"
export MSYS2_ENV_CONV_EXCL=PYTHONPATH HF_HUB_OFFLINE=1 PYTHONIOENCODING=utf-8
"$PY" -c "import accelerate, autune_extraction.labeling.ami" || { echo "imports failed; not starting"; exit 4; }

read -r mem < <(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
echo "$(date +%T) GPU mem ${mem} MiB"
if [ "$mem" -ge 4000 ]; then echo "GPU busy - not starting"; exit 3; fi

SEEDS="${SEEDS:-20260910 20260916 20260917}"

for SPLIT in clean30_ctx2 rough30_ctx2; do
  for SEED in $SEEDS; do
    OUT="$E/runs/${SPLIT}_s${SEED}"
    if [ -f "$OUT/run.json" ]; then echo "$(date +%T) skip $SPLIT s$SEED: already trained"; continue; fi
    echo "$(date +%T) train $SPLIT seed $SEED"
    "$PY" "$CTXDIR/ctx_train.py" --data "$E/splits/$SPLIT" --out "$OUT" --seed "$SEED"
  done
done

for SPLIT in clean30_ctx2 rough30_ctx2; do
  echo "$(date +%T) score $SPLIT"
  for SEED in $SEEDS; do
    "$PY" "$CTXDIR/score_models.py" \
      --sheets "dataset/extraction_eval/runs/clean30_s20260910/aihub_chaired12/input" \
      --out "$E/scores/${SPLIT}_s${SEED}_chaired12" \
      --ckpt "$E/runs/${SPLIT}_s${SEED}" --context 2
    "$PY" "$CTXDIR/score_models.py" \
      --sheets "dataset/extraction_eval/runs/clean30_s20260910/aihub_blind1/input" \
      --out "$E/scores/${SPLIT}_s${SEED}_blind1" \
      --ckpt "$E/runs/${SPLIT}_s${SEED}" --context 2
  done
done
echo "$(date +%T) done"
