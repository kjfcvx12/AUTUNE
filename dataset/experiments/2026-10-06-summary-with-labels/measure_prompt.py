"""Candidate instructions for the llm classifier against the ones on main.

One worktree, the variants swapped in turn round by round (so none has the
provider's better half-hour). Invented meetings only: 8.txt and EVAL_02 (both
LOOKED AT while writing the candidates, so they flatter them), EVAL_03 and
EVAL_04 (never looked at: the fair test), and a seven-line acknowledgement
probe written here. Prints numbers, labels and utterance indices only.

Usage: measure_prompt.py <rounds> <log> [variant ...]
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path("F:/0final/AUTUNE")
EXP = ROOT / "dataset" / "experiments"
SRC8 = EXP / "2026-09-26-local-vs-api" / "scratch_e27a3912" / "step1_chunks_overlap_8.json"
FT = EXP / "2026-09-27-llm-finetune" / "test.jsonl"
YES8 = {14, 20, 29, 34, 35, 37, 45, 46, 48, 49, 68, 69, 74, 75, 77, 79}
IGNORE8 = {42, 43, 47, 52, 76}

keys = [
    line.split("=", 1)[1].strip().strip('"').strip("'")
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines()
    if line.startswith("AUTUNE_LLM_API_KEY=")
]
if not keys:
    sys.exit("no AUTUNE_LLM_API_KEY in the root .env")
os.environ.update(
    AUTUNE_ENV="local",
    AUTUNE_LLM_API_KEY=keys[-1],
    AUTUNE_EXTRACTION_LLM_API_KEY="",
    AUTUNE_EXTRACTION_CLASSIFIER_IMPL="llm",
    AUTUNE_EXTRACTION_LLM_MODEL="gemini-3.5-flash-lite",
    AUTUNE_EXTRACTION_LLM_FALLBACK_MODEL="",
    AUTUNE_EXTRACTION_LLM_ACKNOWLEDGED_392="true",
)

from autune_extraction.pipeline import llm  # noqa: E402
from autune_extraction.pipeline.registry import get_classifier  # noqa: E402

PACE = float(os.environ.get("PACE", "1.5"))
MAIN = llm.INSTRUCTIONS


def swap(text: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in pairs:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    return text


RULES = [
    (
        "commitment: 화자가 할 일을 맡거나 요청을 수락함(기한 없어도 됨). ",
        "commitment: 화자가 자기 할 일을 맡거나 자기에게 온 요청을 수락함(기한 없어도 됨). ",
    ),
    (
        "decision: 회의가 무엇을 하기로 정함(보류·조건부 포함). ",
        "decision: 회의가 무엇을 하기로 정함(보류·조건부 포함, '그럼 확정할게요'도 정하는 말). ",
    ),
    (
        "그 외(설명·잡담·맞장구·투표·예상 수치)는 적지 마세요.\n",
        "그 외(설명·잡담·맞장구·투표·예상 수치·가능하다는 말·평소 하는 일, "
        "요청받지 않고 한 '네, 알겠습니다')는 적지 마세요.\n",
    ),
]
EXAMPLES = [
    (
        "7 [대상] 프런트엔드 한 명이요. → 적지 않음(질문에 대한 답)\n",
        "7 [대상] 프런트엔드 한 명이요. → 적지 않음(질문에 대한 답)\n"
        "8 [대상] 그건 원격으로도 처리할 수 있습니다. → 적지 않음(가능하다는 말)\n"
        "9 [문맥] 출시는 다음 달로 밀렸습니다.\n"
        "10 [대상] 네, 알겠습니다. → 적지 않음(요청받은 일 없음)\n",
    ),
]
VARIANTS = {
    "main": MAIN,
    "rules": swap(MAIN, RULES),
    "rules+examples": swap(swap(MAIN, RULES), EXAMPLES),
    "examples": swap(MAIN, EXAMPLES),
}

PROBE = [
    "다음 주 화요일에 고객사 점검이 있어서 배포는 수요일로 밀렸습니다. 그날 오전에는 서버 접근이 막힙니다.",
    "네 알겠습니다.",
    "그럼 점검 일정 공지를 내일까지 사내 채널에 올려 주실 수 있어요?",
    "네 알겠습니다.",
    "네, 제가 내일 오전까지 올리겠습니다.",
    "저희 쪽은 요청 들어오면 당일에 처리할 수 있습니다.",
    "좋습니다, 그럼 배포는 수요일로 확정할게요.",
]
PROBE_NAMES = {1: "ack after news", 3: "ack after a request", 4: "says what", 5: "can do", 6: "settles"}


def meeting_8() -> tuple[list[tuple[int, str]], set[int], set[int]]:
    payload = json.loads(SRC8.read_text(encoding="utf-8"))
    seen: dict[int, str] = {}
    for chunk in payload["chunks"]:
        for u in chunk["utterances"]:
            if u["idx"] > 0:
                seen.setdefault(u["idx"], u["text"])
    return sorted(seen.items()), set(YES8), set(IGNORE8)


def meeting_eval(name: str) -> tuple[list[tuple[int, str]], set[int], set[int]]:
    utts: dict[int, str] = {}
    yes: set[int] = set()
    ignore: set[int] = set()
    for line in FT.read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        if d["meeting"] != name:
            continue
        yes |= set(d["gold_yes"])
        ignore |= set(d["gold_ignore"])
        for row in d["user"].splitlines():
            m = re.match(r"\[#(\d+)\] \[신규\] [^:]+: (.*)", row)
            if m:
                utts[int(m.group(1))] = m.group(2)
    return sorted(utts.items()), yes, ignore


def classify(variant: str, texts: list[str]) -> tuple[list, int]:
    llm.INSTRUCTIONS = VARIANTS[variant]
    llm._BODY_OVERHEAD = len(VARIANTS[variant]) + 200
    classifier = get_classifier()
    client = classifier._client  # type: ignore[attr-defined]
    send = client.request
    count = {"n": 0}

    def request(method: str, path: str, **kwargs: object) -> object:
        count["n"] += 1
        time.sleep(PACE)
        return send(method, path, **kwargs)

    client.request = request
    return classifier.classify(texts), count["n"]


def kind(p: object) -> str:
    return p.kind.value if p.kind is not None else "none"  # type: ignore[attr-defined]


def main() -> None:
    rounds, log = int(sys.argv[1]), Path(sys.argv[2])
    names = sys.argv[3:] or list(VARIANTS)
    meetings = {
        "8.txt": meeting_8(),
        "EVAL_02": meeting_eval("EVAL_02"),
        "EVAL_03": meeting_eval("EVAL_03"),
        "EVAL_04": meeting_eval("EVAL_04"),
    }
    with log.open("a", encoding="utf-8") as out:
        for name in names:
            out.write(json.dumps({"variant": name, "chars": len(VARIANTS[name])}) + "\n")
        for rnd in range(rounds):
            for name in names:
                for meeting, (items, yes, ignore) in meetings.items():
                    try:
                        got, requests = classify(name, [text for _, text in items])
                    except Exception as exc:  # noqa: BLE001 -- one failed run is a hole, not the end
                        out.write(json.dumps({"round": rnd, "variant": name, "meeting": meeting,
                                              "error": type(exc).__name__}) + "\n")
                        out.flush()
                        continue
                    pred = {i for (i, _), p in zip(items, got, strict=True) if kind(p) == "commitment"} - ignore
                    tp, fp, fn = len(pred & yes), len(pred - yes), len(yes - pred)
                    p = tp / (tp + fp) if tp + fp else 0.0
                    r = tp / (tp + fn) if tp + fn else 0.0
                    f1 = 2 * p * r / (p + r) if p + r else 0.0
                    kinds: dict[str, int] = {}
                    for one in got:
                        kinds[kind(one)] = kinds.get(kind(one), 0) + 1
                    out.write(json.dumps({
                        "round": rnd, "variant": name, "meeting": meeting, "P": round(p, 3),
                        "R": round(r, 3), "F1": round(f1, 3), "fp": sorted(pred - yes),
                        "fn": sorted(yes - pred), "requests": requests, "kinds": kinds,
                        "summaries": sum(bool(getattr(o, "summary", "")) for o in got),
                    }) + "\n")
                    out.flush()
                try:
                    got, _ = classify(name, PROBE)
                    out.write(json.dumps({"round": rnd, "variant": name, "meeting": "probe",
                                          "labels": {PROBE_NAMES[i]: kind(got[i]) for i in PROBE_NAMES}},
                                         ensure_ascii=False) + "\n")
                except Exception as exc:  # noqa: BLE001
                    out.write(json.dumps({"round": rnd, "variant": name, "meeting": "probe",
                                          "error": type(exc).__name__}) + "\n")
                out.flush()
        out.write(json.dumps({"done": True}) + "\n")


main()
