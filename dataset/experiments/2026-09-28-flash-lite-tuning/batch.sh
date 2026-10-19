#!/bin/sh
# Every Flash-Lite experiment of 2026-09-28, sequential (free-tier rate limits).
cd "$(dirname "$0")"
export GEMINI_API_KEY=$(grep '^GEMINI_API_KEY=' /f/0final/AUTUNE/.env | cut -d= -f2- | tr -d '\r"')
export PYTHONIOENCODING=utf-8
PY=/f/0final/AUTUNE/.venv/Scripts/python.exe
r() { $PY flt.py "$@" 2>&1 | grep -v "HTTP Request"; }
for think in none low medium high; do
  for temp in 0 1; do r g_${think}_t${temp} 3 think=$think temp=$temp; done
done
r ref38_t0 3 model=gemini-3.8-flash temp=0
r ref38_t1 3 model=gemini-3.8-flash temp=1
r schema_none_t0 3 schema=1
r schema_low_t0 3 schema=1 think=low
r fewshot_none_t0 3 prompt=fewshot
r fewshot_low_t0 3 prompt=fewshot think=low
r end_none_t0 3 prompt=end
r ctx6_none_t0 3 ctx=6
r g_none_t1 2 think=none temp=1
r g_low_t1 2 think=low temp=1
echo BATCH_DONE
