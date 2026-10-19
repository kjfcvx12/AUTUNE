"""Generation-based kind classification, scored against decision-probe's 195
human-reviewed rows -- the same set that already showed digit-readoff Qwen
(local_llm_label.py's next-token approach) at kappa=0.036, far worse than the
fine-tuned classifier (v2: kappa=0.212). This tests whether letting the model
generate a brief judgment first, instead of reading softmax over "1".."6",
does better on the same decision/commitment boundary problem (#323).

    python gen_classify.py

Writes <meeting>.M.csv next to the existing sheets_review sheets, then scores
with pilot_agreement.py the same way score_decision.sh does for every other
checkpoint. Counts and row ids only -- never utterance text -- in anything
this script prints.
"""
from __future__ import annotations

import csv
import os
import re
import sys
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")

import torch  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

MODEL = "Qwen/Qwen3-4B-Instruct-2507"
DEC = Path(r"F:\0final\AUTUNE\dataset\experiments\2026-09-15-decision-probe")
SHEETS = DEC / "sheets"
REVIEW = DEC / "sheets_review"
KINDS = ["commitment", "decision", "open_question", "concern", "ambiguous", "none"]
BEFORE, AFTER = 4, 2

SYSTEM = """당신은 회의 발화를 분류하는 전문가입니다. [대상] 표시가 붙은 발화 하나를 아래 여섯 가지 중 하나로 분류합니다.

결정(decision): "우리 조직은 어디로/무엇을 하기로 했는가?"에 대한 답 -- 참석자 전원 또는 리더가 논의 끝에 확정한 것. 회의록의 '의결 사항/결론'에 해당.
약속(commitment): "그 일을 누가, 언제까지 하기로 했는가?"에 대한 답 -- 특정 개인/팀이 스스로 하겠다고 말한 것. 회의록의 'Action Item'에 해당.
질문(open_question): 다른 사람에게 정보.의견.조치를 요청하는 진짜 질문.
우려(concern): 앞의 말에 대한 반대.이의.문제 제기.
애매(ambiguous): 요청이나 제안에 대한 약하거나 불확실한 수락.
해당없음(none): 그 외 전부 -- 설명, 사실 전달, 맞장구, 진행 멘트, 문장 조각.

절차: 먼저 [대상] 발화가 결정과 약속 사이에서 헷갈리면, "이게 조직 전체가 확정한 것인가, 특정 한 사람이 스스로 하겠다고 한 것인가"를 한 문장으로 판단합니다. 그 다음 마지막 줄에 반드시 "답: <kind>" 형식으로 씁니다. <kind>는 commitment, decision, open_question, concern, ambiguous, none 중 하나만 영어로 씁니다."""

ANSWER_RE = re.compile(r"답\s*[:：]\s*(commitment|decision|open_question|concern|ambiguous|none)", re.IGNORECASE)
FALLBACK_RE = re.compile(r"\b(commitment|decision|open_question|concern|ambiguous|none)\b", re.IGNORECASE)


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_model():
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16).to("cuda").eval()
    return tok, model


@torch.no_grad()
def classify(tok, model, window: list[dict], target_index: int) -> str:
    lines = []
    for i, r in enumerate(window):
        mark = "[대상] " if i == target_index else ""
        lines.append(f"{mark}{r['speaker']}({r['role']}): {r['text']}")
    user = "회의 발화 (앞뒤 문맥 포함):\n" + "\n".join(lines) + "\n\n[대상] 발화를 분류하세요."
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
    prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    enc = tok(prompt, return_tensors="pt").to("cuda")
    out = model.generate(**enc, max_new_tokens=120, do_sample=False)
    reply = tok.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()

    m = ANSWER_RE.search(reply)
    if m:
        return m.group(1).lower()
    m = FALLBACK_RE.findall(reply)
    if m:
        return m[-1].lower()
    return "none"


def main() -> None:
    print("loading model...")
    t0 = time.time()
    tok, model = load_model()
    print(f"loaded in {time.time() - t0:.0f}s")

    meetings_done = 0
    rows_done = 0
    started = time.time()

    for l_path in sorted(REVIEW.glob("*.L.csv")):
        meeting = l_path.name.removesuffix(".L.csv")
        b_path = REVIEW / f"{meeting}.B.csv"
        a_path = SHEETS / f"{meeting}.A.csv"
        if not b_path.exists() or not a_path.exists():
            continue

        a_rows = load_csv(a_path)
        l_rows = {r["row"]: r for r in load_csv(l_path)}
        sampled = [r["row"] for r in a_rows if l_rows.get(r["row"], {}).get("llm_kind", "").strip()]
        if not sampled:
            continue

        index_of = {r["row"]: i for i, r in enumerate(a_rows)}
        out_rows = []
        for row_id in sampled:
            i = index_of[row_id]
            window = a_rows[max(0, i - BEFORE): i + AFTER + 1]
            target_index = min(i, BEFORE)
            kind = classify(tok, model, window, target_index)
            out_rows.append({"row": row_id, "kind": kind, "decision_id": "", "settles": "", "responds_to": ""})
            rows_done += 1

        with (REVIEW / f"{meeting}.M.csv").open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["row", "kind", "decision_id", "settles", "responds_to"])
            writer.writeheader()
            writer.writerows(out_rows)
        meetings_done += 1

    elapsed = time.time() - started
    print(f"{meetings_done} meetings, {rows_done} rows classified in {elapsed:.0f}s ({rows_done / max(elapsed,1):.2f} rows/s)")


if __name__ == "__main__":
    main()
