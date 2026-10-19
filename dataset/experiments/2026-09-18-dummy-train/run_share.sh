#!/usr/bin/env bash
# The shareable test model: one seed on `share` (no AI Hub rows), then the same
# three AI Hub evaluation sets for the model card. Counts only. From the repo root.
set -euo pipefail
E=dataset/experiments/2026-09-18-dummy-train
S=dataset/experiments/2026-09-17-ensemble-context-llm/score_models.py
PY=C:/Users/hi/miniforge3/envs/aiprj/python.exe
PD="C:/Users/hi/AppData/Local/Temp/claude/F--0final-AUTUNE/315704b3-93a1-4653-889a-4840c786d480/scratchpad/pydeps"
export PYTHONPATH="modules/extraction/src;packages/contracts/src;packages/core/src;packages/integrations/src;$PD"
export MSYS2_ENV_CONV_EXCL=PYTHONPATH HF_HUB_OFFLINE=1 PYTHONIOENCODING=utf-8
"$PY" -c "import accelerate, autune_extraction.labeling.ami" || { echo "imports failed"; exit 4; }

read -r mem < <(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
echo "$(date +%T) GPU mem ${mem} MiB"
[ "$mem" -ge 3000 ] && { echo "GPU busy - not starting"; exit 3; }

"$PY" $E/build_share.py
"$PY" $E/train_seeds.py --split share --seeds 20260910 2>&1 \
  | grep -vE 'it/s\]|s/it\]' | grep -E "^train |^wrote |^skip |eval_macro_f1|train_runtime|Error" || true

declare -A SETS=(
  [probe]=dataset/experiments/2026-09-15-decision-probe/score_input
  [blind]=dataset/extraction_eval_blind
  [chaired12]=dataset/extraction_eval_blind2/chaired_12
)
for set in probe blind chaired12; do
  echo "=== share on $set"
  "$PY" $S --sheets ${SETS[$set]} --out $E/scores/${set}_share --ckpt $E/runs/share_s20260910
done
echo "$(date +%T) done"
