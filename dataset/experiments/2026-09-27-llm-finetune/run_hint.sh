#!/bin/sh
# Hint runs for combo_clf.py, one after another on the GPU.
PY=/c/Users/hi/miniforge3/envs/aiprj/python.exe
export PYTHONIOENCODING=utf-8
for s in test8 test_asr_turns test_real_turns test_turns; do
  $PY eval_chunks.py --split ${s}_hint --tag merged_e2_hint --model runs/merged_e2 > eval_${s}_hint.log 2>&1
  tail -1 eval_${s}_hint.log
done
