#!/usr/bin/env bash
# Build v4, train three seeds, score single seeds and the x3 ensemble on the AI Hub
# sets as a regression check against v2 (same sheets, same scorer). Counts only.
# Run from the repo root.
set -euo pipefail
SPLIT=${1:-v4}
E=dataset/experiments/2026-09-18-dummy-train
S=dataset/experiments/2026-09-17-ensemble-context-llm/score_models.py
PY=C:/Users/hi/miniforge3/envs/aiprj/python.exe
PD="C:/Users/hi/AppData/Local/Temp/claude/F--0final-AUTUNE/315704b3-93a1-4653-889a-4840c786d480/scratchpad/pydeps"
export PYTHONPATH="modules/extraction/src;packages/contracts/src;packages/core/src;packages/integrations/src;$PD"
export MSYS2_ENV_CONV_EXCL=PYTHONPATH HF_HUB_OFFLINE=1 PYTHONIOENCODING=utf-8
"$PY" -c "import accelerate, autune_extraction.labeling.ami" || { echo "imports failed; not starting"; exit 4; }

echo "$(date +%T) build"
if [ "$SPLIT" = chairless ]; then "$PY" $E/build_chairless.py; else "$PY" $E/build_split.py $SPLIT; fi

read -r util mem < <(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits | tr -d ',')
echo "$(date +%T) GPU util ${util}% mem ${mem} MiB"
if [ "$mem" -ge 3000 ]; then echo "GPU busy - not starting"; exit 3; fi

SEEDS="20260910 20260916 20260917"
"$PY" $E/train_seeds.py --split $SPLIT --seeds $SEEDS 2>&1 \
  | grep -vE 'it/s\]|s/it\]' | grep -E "^train |^wrote |^skip |eval_macro_f1|train_runtime|Error" || true

ENS=""
for s in $SEEDS; do ENS="$ENS --ckpt $E/runs/${SPLIT}_s$s"; done
declare -A SETS=(
  [probe]=dataset/experiments/2026-09-15-decision-probe/score_input
  [blind]=dataset/extraction_eval_blind
  [chaired12]=dataset/extraction_eval_blind2/chaired_12
  [heldout]=$E/splits/chairless/heldout_sheets
)
LIST="probe blind chaired12"; [ "$SPLIT" = chairless ] && LIST="$LIST heldout"
for set in $LIST; do
  for s in $SEEDS; do
    echo "=== ${SPLIT}_s$s on $set"
    "$PY" $S --sheets ${SETS[$set]} --out $E/scores/${set}_${SPLIT}_s$s --ckpt $E/runs/${SPLIT}_s$s
  done
  echo "=== ens_$SPLIT on $set"
  "$PY" $S --sheets ${SETS[$set]} --out $E/scores/${set}_ens_$SPLIT $ENS
done
echo "$(date +%T) done"
