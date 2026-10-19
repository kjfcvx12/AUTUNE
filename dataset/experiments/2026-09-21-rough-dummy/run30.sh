#!/usr/bin/env bash
# Train clean30 and rough30 on three seeds each and score both on every part of the
# evaluation set, same pattern as run.sh's clean20/rough20 pair but at 30-meeting scale.
set -euo pipefail
E=dataset/experiments/2026-09-21-rough-dummy
PY=C:/Users/hi/miniforge3/envs/aiprj/python.exe
PD="C:/Users/hi/AppData/Local/Temp/claude/F--0final-AUTUNE/315704b3-93a1-4653-889a-4840c786d480/scratchpad/pydeps"
export PYTHONPATH="modules/extraction/src;packages/contracts/src;packages/core/src;packages/integrations/src;$PD"
export MSYS2_ENV_CONV_EXCL=PYTHONPATH HF_HUB_OFFLINE=1 PYTHONIOENCODING=utf-8
"$PY" -c "import accelerate, autune_extraction.labeling.ami" || { echo "imports failed; not starting"; exit 4; }

read -r mem < <(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
echo "$(date +%T) GPU mem ${mem} MiB"
if [ "$mem" -ge 4000 ]; then echo "GPU busy - not starting"; exit 3; fi

SEEDS="${SEEDS:-20260910 20260916 20260917}"

for SPLIT in clean30 rough30; do
  echo "$(date +%T) train $SPLIT"
  "$PY" $E/train_seeds.py --split "$SPLIT" --seeds $SEEDS
done

for SPLIT in clean30 rough30; do
  echo "$(date +%T) score $SPLIT"
  for SEED in $SEEDS; do
    "$PY" dataset/extraction_eval/run_eval.py --name "${SPLIT}_s${SEED}" \
      --ckpt "$E/runs/${SPLIT}_s${SEED}"
  done
done
echo "$(date +%T) done"
