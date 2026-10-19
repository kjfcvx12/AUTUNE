#!/bin/sh
# Ten more runs a cell, the two prompts taken in turn so that neither has the
# provider's better half-hour. Dummy meetings only (measure_880.py's loaders).
SP="/c/Users/hi/AppData/Local/Temp/claude/F--0final-AUTUNE/3a412e2e-90ef-4a99-bd9d-70632044d325/scratchpad"
OUT="$SP/measure_repeat.log"
: > "$OUT"
export PYTHONIOENCODING=utf-8 PYTHONUTF8=1
i=1
while [ $i -le 10 ]; do
  for wt in wtretry wtwin; do
    (cd "$SP/$wt" && .venv/Scripts/python ../measure_880.py "$wt round $i" 1 2>&1 \
      | grep -E "^== |^-- |^   run " >> "$OUT")
  done
  i=$((i + 1))
done
echo done >> "$OUT"
