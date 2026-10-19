#!/usr/bin/env bash
# Step 2: v2 with +-2 utterances of context, three seeds, then single and ensemble
# scores on the blind set and the decision probe. Same seeds as v2's three.
# Counts only. Run from the repo root.
set -euo pipefail
E=dataset/experiments/2026-09-17-ensemble-context-llm
BLIND=dataset/extraction_eval_blind
PROBE=dataset/experiments/2026-09-15-decision-probe/score_input
PY=C:/Users/hi/miniforge3/envs/aiprj/python.exe
PD="C:/Users/hi/AppData/Local/Temp/claude/F--0final-AUTUNE/315704b3-93a1-4653-889a-4840c786d480/scratchpad/pydeps"
export PYTHONPATH="modules/extraction/src;packages/contracts/src;packages/core/src;packages/integrations/src;$PD"
export MSYS2_ENV_CONV_EXCL=PYTHONPATH HF_HUB_OFFLINE=1 PYTHONIOENCODING=utf-8
"$PY" -c "import accelerate, autune_extraction.training.train" || { echo "imports failed; not starting"; exit 4; }
read -r util mem < <(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits | tr -d ',')
echo "$(date +%T) GPU util ${util}% mem ${mem} MiB"
if [ "$util" -ge 10 ] || [ "$mem" -ge 3000 ]; then echo "GPU busy - not starting"; exit 3; fi

SEEDS="20260910 20260916 20260917"
for seed in $SEEDS; do
  echo "$(date +%T) train ctx2 seed $seed"
  "$PY" $E/ctx_train.py --data $E/splits/ctx2 --out $E/runs/ctx2_s$seed --seed $seed 2>&1 \
    | grep -vE 'it/s\]|s/it\]|Loading weights' | grep -E -i "rows, tokens|eval_macro_f1|train_runtime|wrote|skip|error|traceback|usage" | tail -12
  [ -f $E/runs/ctx2_s$seed/run.json ] || { echo "seed $seed produced no checkpoint - stopping"; exit 5; }
done

CK=""
for seed in $SEEDS; do CK="$CK --ckpt $E/runs/ctx2_s$seed"; done
for set in probe blind; do
  src=$PROBE; [ $set = blind ] && src=$BLIND
  for seed in $SEEDS; do
    echo "=== ctx2 seed $seed on $set"
    "$PY" $E/score_models.py --context 2 --sheets $src --out $E/scores/ctx2_s${seed}_$set --ckpt $E/runs/ctx2_s$seed 2>&1 | grep -v -E "Loading weights|^scored"
  done
  echo "=== ENSEMBLE ctx2 x3 on $set"
  "$PY" $E/score_models.py --context 2 --sheets $src --out $E/scores/ens_ctx2_$set $CK 2>&1 | grep -v -E "Loading weights|^scored"
done
echo "$(date +%T) done"
