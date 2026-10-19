"""The original shape of the complaint: a 900-character turn of filler by one
speaker, then "네 알겠습니다." by another -- how does main's classifier label it?

Invented text (live_dummy.py's filler). Usage: ack_probe.py <runs>
"""

from __future__ import annotations

import importlib.util
import os
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path("F:/0final/AUTUNE")
keys = [
    line.split("=", 1)[1].strip().strip('"').strip("'")
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines()
    if line.startswith("AUTUNE_LLM_API_KEY=")
]
os.environ.update(
    AUTUNE_ENV="local",
    AUTUNE_LLM_API_KEY=keys[-1],
    AUTUNE_EXTRACTION_LLM_API_KEY="",
    AUTUNE_EXTRACTION_CLASSIFIER_IMPL="llm",
    AUTUNE_EXTRACTION_LLM_MODEL="gemini-3.5-flash-lite",
    AUTUNE_EXTRACTION_LLM_FALLBACK_MODEL="",
    AUTUNE_EXTRACTION_LLM_ACKNOWLEDGED_392="true",
)

# live_dummy.py runs a meeting when executed; only its text is wanted here.
source = (HERE / "live_dummy.py").read_text(encoding="utf-8")
start = source.index("FILLER = [")
end = source.index("MEETING: list")
namespace: dict = {}
exec(source[start:end], namespace)  # noqa: S102 -- this session's own invented filler
talk = namespace["talk"]

from autune_extraction.pipeline import llm  # noqa: E402
from autune_extraction.pipeline.registry import get_classifier  # noqa: E402

TEXTS = [
    talk(800, 12) + " 근데 그 일정이면 테스트 기간이 너무 짧아서 걱정이에요.",
    talk(900, 1),
    "네 알겠습니다.",
    talk(850, 14) + " 그럼 이번 분기에는 알림 기능은 빼고 가는 걸로 결정하겠습니다.",
]
runs = int(sys.argv[1])
print(f"instructions {len(llm.INSTRUCTIONS)} chars")
seen: Counter[str] = Counter()
last: Counter[str] = Counter()
classifier = get_classifier()
for _ in range(runs):
    time.sleep(1.5)
    got = classifier.classify(TEXTS)
    kind = lambda p: p.kind.value if p.kind is not None else "none"  # noqa: E731
    seen[kind(got[2])] += 1
    last[kind(got[3])] += 1
print("the acknowledgement after a long turn:", dict(seen))
print("control, the turn that ends in a decision:", dict(last))
