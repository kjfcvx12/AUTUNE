"""Flash-Lite tuning on 8.txt: the product classifier's request, one knob at a time.

Reuses ``autune_extraction.pipeline.llm``'s INSTRUCTIONS / windows / render / parse
so a run is the product request plus exactly the knob under test. Gold is the
utterance-level test8 gold (16 commitment rows, 5 ignored), the same the #393
eval scored 0.968 / 0.909 against.

8.txt is a self-authored dummy meeting (no AI Hub, no real person), so the
free-tier key is allowed (memory gemini-key-is-free-tier).

    python flt.py <name> <reps> key=value ...
      model=gemini-3.5-flash-lite  think=minimal|low|medium|high|none
      temp=0|1  schema=0|1  prompt=base|fewshot|end  ctx=3
Each run appends one JSON line to runs.jsonl (per-window labels kept, so
self-consistency and cascades are computed offline without new calls).
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

from autune_extraction.pipeline import llm as L

HERE = Path(__file__).parent
SRC = HERE.parent / "2026-09-26-local-vs-api" / "scratch_e27a3912" / "step1_chunks_overlap_8.json"
YES = {14, 20, 29, 34, 35, 37, 45, 46, 48, 49, 68, 69, 74, 75, 77, 79}
IGNORE = {42, 43, 47, 52, 76}
PRICE = {  # $ per 1M tokens (input, output incl. thinking), 2026-09-28
    "gemini-3.5-flash-lite": (0.30, 2.50),
    "gemini-3.8-flash": (0.75, 3.75),
}
BASE = "https://generativelanguage.googleapis.com/v1beta"

FEWSHOT = (
    # Targets the four false-positive kinds the baseline showed on 8.txt (26
    # proposal, 44 chair delegating, 57 opinion/vote, 73 answer to a question),
    # written as analogues, not copied -- still tuned on the test meeting.
    "\n예시(다른 회의):\n"
    "1 [문맥] 이 설문 결과는 누가 정리해 주실래요?\n"
    "2 [대상] 제가 할게요, 목요일까지요. → commitment\n"
    "3 [대상] 캐시 만료 시간을 1시간으로 늘리는 걸 제안드려요. → 적지 않음(제안은 약속 아님)\n"
    "4 [대상] 그럼 수진 님이 로그 확인하고 결과 공유해 주세요. → open_question(남에게 시킴, 화자 본인 약속 아님)\n"
    "5 [대상] 저는 영업 입장에서 2안을 밀고 싶어요. → 적지 않음(의견·투표)\n"
    "6 [문맥] 어떤 인력이 필요하세요?\n"
    "7 [대상] 프런트엔드 한 명이요. → 적지 않음(질문에 대한 답)\n"
)


FT = HERE.parent / "2026-09-27-llm-finetune" / "test.jsonl"


def load_eval(meeting: str) -> list[tuple[int, str]]:
    """A self-authored dummy eval meeting from the fine-tune test set; sets YES/IGNORE."""
    global YES, IGNORE
    utts: dict[int, str] = {}
    YES, IGNORE = set(), set()
    for line in FT.read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        if d["meeting"] != meeting:
            continue
        YES |= set(d["gold_yes"])
        IGNORE |= set(d["gold_ignore"])
        for row in d["user"].splitlines():
            m = re.match(r"\[#(\d+)\] \[신규\] [^:]+: (.*)", row)
            if m:
                utts[int(m.group(1))] = m.group(2)
    return sorted(utts.items())


def load_texts() -> list[tuple[int, str]]:
    payload = json.loads(SRC.read_text(encoding="utf-8"))
    seen: dict[int, str] = {}
    for c in payload["chunks"]:
        for u in c["utterances"]:
            if u["idx"] > 0:
                seen.setdefault(u["idx"], u["text"])
    return sorted(seen.items())


def body_for(text: str, cfg: dict) -> dict:
    instructions = L.INSTRUCTIONS + (FEWSHOT if cfg["prompt"] == "fewshot" else "")
    gen: dict = {"temperature": float(cfg["temp"]), "responseMimeType": "application/json"}
    if cfg["think"] != "none":
        gen["thinkingConfig"] = {"thinkingLevel": cfg["think"]}
    if cfg["schema"] == "1":
        kinds = [k.value for k in L.UtteranceKind]
        gen["responseSchema"] = {
            "type": "OBJECT",
            "properties": {
                "labels": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "line": {"type": "INTEGER"},
                            "kind": {"type": "STRING", "enum": kinds},
                        },
                        "required": ["line", "kind"],
                    },
                }
            },
            "required": ["labels"],
        }
    if cfg["prompt"] == "end":  # Gemini 3 guide: data first, instruction last
        return {
            "contents": [{"role": "user", "parts": [{"text": text + "\n\n" + instructions}]}],
            "generationConfig": gen,
        }
    return {
        "systemInstruction": {"parts": [{"text": instructions}]},
        "contents": [{"role": "user", "parts": [{"text": text}]}],
        "generationConfig": gen,
    }


def parse_any(answer: str, schema: bool) -> dict[int, str]:
    if schema:
        try:
            rows = json.loads(answer).get("labels", [])
            return {int(r["line"]): r["kind"] for r in rows if r.get("kind") in L._KINDS}
        except (json.JSONDecodeError, AttributeError, KeyError, TypeError, ValueError):
            return {}
    return {k: v.value for k, v in L.parse(answer).items()}


def post(client: httpx.Client, model: str, body: dict) -> tuple[dict, float]:
    for attempt in range(6):
        t0 = time.perf_counter()
        r = client.post(f"{BASE}/models/{model}:generateContent", json=body)
        dt = time.perf_counter() - t0
        if r.status_code == 200:
            return r.json(), dt
        if r.status_code in (429, 500, 503, 504):
            wait = 10 * (attempt + 1) if r.status_code == 429 else 3 * (attempt + 1)
            print(f"  {r.status_code} retry in {wait}s", flush=True)
            time.sleep(wait)
            continue
        raise RuntimeError(f"{r.status_code} {r.text[:300]}")
    raise RuntimeError("gave up after retries")


def run_once(client: httpx.Client, cfg: dict, items: list[tuple[int, str]]) -> dict:
    L.CONTEXT_LINES = int(cfg["ctx"])
    idxs = [i for i, _ in items]
    texts = [t for _, t in items]
    instructions = L.INSTRUCTIONS + (FEWSHOT if cfg["prompt"] == "fewshot" else "")
    budget = L.MAX_OUTBOUND_CHARS - (len(instructions) + 200)
    wins, secs, tin, tout, tthink = [], 0.0, 0, 0, 0
    labels: dict[int, str] = {}
    for w, (start, end) in enumerate(L.windows(texts, budget)):
        text, targets = L.render(texts, start, end)
        data, dt = post(client, cfg["model"], body_for(text, cfg))
        secs += dt
        u = data.get("usageMetadata", {})
        tin += u.get("promptTokenCount", 0)
        tout += u.get("candidatesTokenCount", 0)
        tthink += u.get("thoughtsTokenCount", 0)
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        answer = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        got = {idxs[targets[n]]: k for n, k in parse_any(answer, cfg["schema"] == "1").items() if n in targets}
        labels.update(got)
        wins.append({"w": w, "utts": [idxs[i] for i in range(start, end)], "labels": got, "sec": round(dt, 2),
                     "tin": u.get("promptTokenCount", 0),
                     "tout": u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)})
        time.sleep(float(cfg.get("gap", 4)))
    pin, pout = PRICE[cfg["model"]]
    cost = (tin * pin + (tout + tthink) * pout) / 1e6
    return {"labels": labels, "windows": wins, "sec": round(secs, 2), "tok_in": tin,
            "tok_out": tout, "tok_think": tthink, "cost": round(cost, 6), **score(labels)}


def score(labels: dict[int, str]) -> dict:
    pred = {i for i, k in labels.items() if k == "commitment"} - IGNORE
    tp, fp, fn = len(pred & YES), len(pred - YES), len(YES - pred)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn)
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return {"P": round(p, 3), "R": round(r, 3), "F1": round(f1, 3),
            "fp_ids": sorted(pred - YES), "fn_ids": sorted(YES - pred)}


def main() -> None:
    name, reps = sys.argv[1], int(sys.argv[2])
    cfg = {"model": "gemini-3.5-flash-lite", "think": "none", "temp": "0", "schema": "0",
           "prompt": "base", "ctx": "3"}
    cfg.update(dict(a.split("=", 1) for a in sys.argv[3:]))
    key = os.environ["GEMINI_API_KEY"]
    items = load_eval(cfg["meeting"]) if cfg.get("meeting") else load_texts()
    with httpx.Client(headers={"x-goog-api-key": key}, timeout=180) as client:
        for rep in range(reps):
            res = run_once(client, cfg, items)
            rec = {"name": name, "rep": rep, "cfg": cfg, **res}
            with (HERE / "runs.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"{name} rep{rep} F1={res['F1']} P={res['P']} R={res['R']} fn={res['fn_ids']} "
                  f"fp={res['fp_ids']} {res['sec']}s think={res['tok_think']} ${res['cost']}", flush=True)


if __name__ == "__main__":
    main()
