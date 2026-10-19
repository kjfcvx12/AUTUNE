#!/usr/bin/env bash
# Score every checkpoint on the decision probe's blind-reviewed candidates.
# Run from the repo root after `python .../collect_review.py` copied the exports.
#
#   bash dataset/experiments/2026-09-15-decision-probe/score_decision.sh
#
# Only the sampled candidate rows are confirmed, so pilot_agreement.py scores exactly
# those; neighbour rows stay unconfirmed and are skipped. What the numbers mean:
#   - recall per kind on rows a human confirmed (decision above all) -- the point
#   - NOT precision or macro F1 of a random set: the rows were chosen by Qwen's
#     p_decision >= 0.10, so the set is class-conditional
#   - Qwen's own row is biased upward by construction (it picked the rows); reported
#     for reference only
# ko_sanity.py `apply` writes <meeting>.M.csv next to the A sheets, so each model's
# sheets are copied into its own folder straight away. Counts only.
set -euo pipefail

DEC=dataset/experiments/2026-09-15-decision-probe
EXP=dataset/experiments/2026-09-15-korean-v1
WORK="$DEC/score_input"
PY=C:/Users/hi/miniforge3/envs/aiprj/python.exe
export HF_HUB_OFFLINE=1
export PYTHONIOENCODING=utf-8
export PYTHONPATH="modules/extraction/src;packages/contracts/src;packages/core/src;packages/integrations/src"
export MSYS2_ENV_CONV_EXCL=PYTHONPATH
"$PY" -c "import autune_extraction.labeling.ami" || { echo "autune_extraction not importable; not starting"; exit 4; }

n_b=$(ls "$DEC"/sheets_review/*.B.csv 2>/dev/null | wc -l)
echo "$(date +%T) B exports in sheets_review: $n_b"
[ "$n_b" -gt 0 ] || { echo "no exports yet - run collect_review.py first"; exit 5; }

read -r util mem < <(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits | tr -d ',')
echo "$(date +%T) GPU util ${util}% mem ${mem} MiB"
if [ "$util" -ge 10 ] || [ "$mem" -ge 3000 ]; then echo "GPU busy - not starting"; exit 3; fi

rm -rf "$WORK"; mkdir -p "$WORK"
for l in "$DEC"/sheets_review/*.L.csv; do
  m=$(basename "$l" .L.csv)
  [ -f "$DEC/sheets_review/$m.B.csv" ] || continue
  cp "$DEC/sheets/$m.A.csv" "$l" "$DEC/sheets_review/$m.B.csv" "$WORK"/
done
echo "  meetings scored: $(ls "$WORK"/*.B.csv | wc -l)"

mkdir -p "$DEC/score_qwen"
cp "$WORK"/*.L.csv "$WORK"/*.B.csv "$DEC/score_qwen"/
"$PY" dataset/extraction_eval_pilot/pilot_agreement.py "$DEC/score_qwen" L B > "$DEC/score_qwen/agreement.txt" 2>&1
echo "=== qwen (selected these rows; biased)"; grep -E "rows labelled|^(commitment|decision|open_question|concern|ambiguous|none) " "$DEC/score_qwen/agreement.txt"

for pair in \
  "ko_sanity_0911:dataset/experiments/2026-09-11-ko-sanity/ckpt" \
  "ami_official:dataset/experiments/2026-09-11-official-6way/run" \
  "syn_probe:$EXP/run_syn_probe" \
  "v2:$EXP/run_syn_none_probe" \
  "v3:$EXP/run_v3"; do
  name=${pair%%:*}; ckpt=${pair#*:}; out="$DEC/score_$name"
  [ -d "$ckpt" ] || { echo "skip $name: no checkpoint"; continue; }
  mkdir -p "$out"; rm -f "$out"/*.M.csv
  echo "$(date +%T) apply $name"
  "$PY" dataset/experiments/2026-09-11-ko-sanity/ko_sanity.py apply --ckpt "$ckpt" --pilot "$WORK" --out "$out" > "$out/apply.txt" 2>&1
  cp "$WORK"/*.M.csv "$WORK"/*.B.csv "$out"/
  "$PY" dataset/extraction_eval_pilot/pilot_agreement.py "$out" M B > "$out/agreement.txt" 2>&1
  echo "=== $name"; grep -E "rows labelled|^(commitment|decision|open_question|concern|ambiguous|none) " "$out/agreement.txt"
done
rm -f "$WORK"/*.M.csv
echo "$(date +%T) done"
