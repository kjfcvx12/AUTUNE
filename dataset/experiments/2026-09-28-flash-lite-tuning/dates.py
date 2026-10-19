"""Knob 6: do Flash-Lite's two wrong dates on the whole-meeting prompt go away
with thinking on? Same prompt and meeting as run_gemini_test_8.py (09-26), only
thinkingConfig / temperature differ. Output tables are scored by hand against
3.8 Flash's (0 wrong dates in the 09-28 re-score).

    python dates.py <think> <temp> <rep>
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import httpx

HERE = Path(__file__).parent
OLD = HERE.parent / "2026-09-26-local-vs-api"
SYSTEM_PROMPT = (OLD / "scratch_e27a3912" / "gemini_system_prompt.txt").read_text(encoding="utf-8")
MEETING_DATE_STR = "2026-09-28, 월요일"


def main() -> None:
    think, temp, rep = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    body_text = (OLD / "8.txt").read_text(encoding="utf-8").split("테스트용 정답 체크리스트")[0].strip()
    user_message = (
        f"다음은 오늘({MEETING_DATE_STR}) 진행된 회의의 녹취록입니다. "
        "이 회의는 사용자가 나중에 자동으로 처리를 요청한 것이라 지금 질문에 답할 사람이 없습니다 "
        "-- 애매한 점이 있으면 프롬프트 규칙대로 권장 선택지를 적용하고 그 가정을 결과 상단에 적으세요. "
        "사용자는 이 회의 참석자가 아닙니다.\n\n"
        f"{body_text}\n\n위 회의록을 시스템 규칙에 따라 처리해서 최종 결과만 출력하세요."
    )
    gen: dict = {"temperature": temp, "maxOutputTokens": 8000}
    if think != "none":
        gen["thinkingConfig"] = {"thinkingLevel": think}
    body = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": gen,
    }
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"
    with httpx.Client(headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]}, timeout=180) as c:
        for attempt in range(6):
            t0 = time.perf_counter()
            r = c.post(url, json=body)
            dt = time.perf_counter() - t0
            if r.status_code == 200:
                break
            time.sleep(10 * (attempt + 1))
        r.raise_for_status()
    data = r.json()
    parts = data["candidates"][0]["content"]["parts"]
    text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    u = data.get("usageMetadata", {})
    out_tok = u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)
    cost = (u.get("promptTokenCount", 0) * 0.30 + out_tok * 2.50) / 1e6
    tag = f"dates_{think}_t{int(temp)}_{rep}"
    (HERE / f"{tag}.md").write_text(text, encoding="utf-8")
    print(f"{tag} {dt:.1f}s think={u.get('thoughtsTokenCount', 0)} out={u.get('candidatesTokenCount', 0)} ${cost:.4f}")


if __name__ == "__main__":
    main()
