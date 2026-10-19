"""#392: how the llm classifier labels a first utterance that greets, calls the
roll and announces an attendance arrangement ending "...참석하시기로 했습니다".

Every line is invented here: no real person, nothing from dataset/. Run from a
worktree with its venv; the classifier is the one checked out there.
Usage: greeting_392.py <label> <runs>
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path("F:/0final/AUTUNE")
keys = [
    line.split("=", 1)[1].strip().strip('"').strip("'")
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines()
    if line.startswith("AUTUNE_LLM_API_KEY=")
]
if not keys:
    sys.exit("no AUTUNE_LLM_API_KEY in the root .env")
key = keys[-1]
os.environ.update(
    AUTUNE_ENV="local",
    AUTUNE_LLM_API_KEY=key,
    AUTUNE_EXTRACTION_LLM_API_KEY="",
    AUTUNE_EXTRACTION_CLASSIFIER_IMPL="llm",
    AUTUNE_EXTRACTION_LLM_MODEL="gemini-3.5-flash-lite",
    AUTUNE_EXTRACTION_LLM_FALLBACK_MODEL="",
    AUTUNE_EXTRACTION_LLM_ACKNOWLEDGED_392="true",
)

from autune_extraction.pipeline import llm as llm_module  # noqa: E402
from autune_extraction.pipeline.registry import get_classifier  # noqa: E402

FIRST = {
    "A greeting + roll call + notice": (
        "안녕하세요, 다들 들어오셨죠. 오늘 한 분 빼고 다 오셨네요. "
        "그리고 이번부터 품질팀 한서윤 책임님이 이 회의에 참석하시기로 했습니다."
    ),
    "B the notice alone": "이번부터 품질팀에서 한 분이 이 회의에 참석하시기로 했습니다.",
    "C the notice with a name": "이번부터 한서윤 책임님이 이 회의에 참석하시기로 했습니다.",
    "D a past arrangement": (
        "지난 분기에 배포는 목요일에만 하기로 했습니다. 오늘은 그 얘기는 아니고 일정부터 보겠습니다."
    ),
}
REST = [
    "네, 안녕하세요. 잘 부탁드립니다.",
    "먼저 결제 화면 개편 일정부터 볼까요. 지금 디자인 시안이 두 개 나와 있습니다.",
    "저는 버튼을 위로 올린 두 번째 시안이 낫다고 봅니다. 이탈이 줄 것 같아요.",
    "다른 의견 없으시면 결제 화면은 두 번째 시안으로 확정하겠습니다.",
    "네, 좋습니다.",
    "그러면 제가 두 번째 시안 기준으로 화면 명세를 금요일까지 정리해서 공유하겠습니다.",
    "테스트 서버가 요즘 자주 느려지는데 원인이 뭔지 아시는 분 있나요?",
    "아직 모르겠습니다. 로그를 더 봐야 할 것 같아요.",
]
DECISION_AT, COMMITMENT_AT = 4, 6  # positions in [first, *REST]


def main() -> None:
    label, reps = sys.argv[1], int(sys.argv[2])
    print(f"== {label}: instructions {len(llm_module.INSTRUCTIONS)} chars; key line fp "
          f"{hashlib.sha256(key.encode()).hexdigest()[:8]} ({len(keys)} such line(s) in .env)")
    classifier = get_classifier()
    for name, first in FIRST.items():
        firsts: Counter[str] = Counter()
        summaries: list[str] = []
        controls: Counter[str] = Counter()
        for _ in range(reps):
            time.sleep(4.5)
            got = classifier.classify([first, *REST])
            kind = lambda p: p.kind.value if p.kind is not None else "none"  # noqa: E731
            firsts[kind(got[0])] += 1
            pieces = getattr(got[0], "pieces", ()) or ()
            if pieces:
                firsts[f"  read in {len(pieces)} pieces"] += 1
            line = getattr(got[0], "summary", "") or ""
            if line:
                summaries.append(line)
            controls[f"decision line={kind(got[DECISION_AT])}, commitment line={kind(got[COMMITMENT_AT])}"] += 1
        print(f"-- {name}")
        print(f"   first utterance: {dict(firsts)}")
        if summaries:
            print(f"   summaries written for it: {sorted(set(summaries))}")
        print(f"   controls: {dict(controls)}")


main()
