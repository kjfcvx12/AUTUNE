"""Step 3: a local LLM re-judges only the decision / commitment boundary.

    python llm_boundary.py selftest
    python llm_boundary.py run --sheets <dir with A/B sheets> --model-scores <dir with M sheets> --out <dir>

Why only there: the classifier's largest decision error is calling a decision a
commitment (33 of the 61 probe decisions for v2), and Qwen is the stronger
decision spotter while the classifier has the better kappa overall. So the
classifier keeps every row it did not call decision or commitment, and the LLM
decides only between those two on the rows it did.

The combination rules are fixed here, before any score is seen, and both are
reported -- nothing is tuned on the probe:
  swap     the LLM picks decision vs commitment (its "neither" is ignored; the
           classifier already said the row is one of the two)
  product  argmax over {decision, commitment} of classifier p x LLM q

The prompt asks a three-way question with the meeting around the row (4 before,
2 after, from the whole meeting). Speakers are shown as S1, S2 ... by order of
appearance, with no role: the product targets meetings without a chair, and the
probe showed the model already leans on "chair = decision".

Qwen3-4B-Instruct from the local cache, HF_HUB_OFFLINE=1. Counts only.
Caveat for reading the probe: its rows were selected by Qwen's own decision
probability, so any Qwen-based step is favoured there. The blind sets are the fair
test.
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")

import torch  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from meetings import full_rows, sheet_rows  # noqa: E402

MODEL = "Qwen/Qwen3-4B-Instruct-2507"
BEFORE, AFTER = 4, 2
AGREEMENT = HERE.parents[1] / "extraction_eval_pilot" / "pilot_agreement.py"

SYSTEM = """당신은 한국어 회의 발화를 판정합니다. [대상] 발화가 아래 셋 중 무엇인지 고릅니다.

1 결정 — 회의에서 함께 정한 결론을 말하는 발화. 누가 말했든, 참석자들이 무엇을 하기로(또는 하지 않기로) 합의·확정했다는 내용. 예: "그럼 발표는 다음 주 금요일로 하겠습니다." "이 안은 보류하는 걸로 하죠."
2 약속 — 화자 본인(또는 본인 팀)이 앞으로 할 구체적인 일을 맡겠다는 발화. 예: "그 자료는 제가 내일까지 정리해서 보내 드릴게요."
3 둘 다 아님 — 설명, 질문, 의견, 맞장구 등.

구분 기준:
- "-겠습니다"로 끝나도, 내용이 회의 전체가 따를 결론이면 1입니다. 화자 개인의 할 일이면 2입니다.
- 앞뒤 발화를 보고, 논의를 마무리하며 결론을 정리하는지 확인하세요.

숫자 하나만 답합니다."""


def load_model():
    tok = AutoTokenizer.from_pretrained(MODEL)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16).to("cuda").eval()
    digits = [tok.convert_tokens_to_ids(str(i)) for i in range(1, 4)]
    if any(d is None or d == tok.unk_token_id for d in digits):
        raise SystemExit("digits 1-3 are not single tokens")
    return tok, model, digits


def prompt(tok, window: list[dict], target: int) -> str:
    names: dict[str, str] = {}
    lines = []
    for i, r in enumerate(window):
        name = names.setdefault(r["speaker"], f"S{len(names) + 1}")
        lines.append(f"{'[대상] ' if i == target else ''}{name}: {r['text']}")
    user = "회의 발화:\n" + "\n".join(lines) + "\n\n[대상] 발화는 1, 2, 3 중 무엇입니까?"
    return tok.apply_chat_template(
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
        tokenize=False, add_generation_prompt=True,
    )


@torch.no_grad()
def ask(tok, model, digits, prompts: list[str], batch: int = 8) -> list[list[float]]:
    out = []
    for s in range(0, len(prompts), batch):
        enc = tok(prompts[s : s + batch], return_tensors="pt", padding=True).to("cuda")
        logits = model(**enc).logits[:, -1, :].float()
        out.extend(torch.softmax(logits[:, digits], dim=-1).cpu().tolist())
    return out


def selftest() -> None:
    """Invented sentences only -- safe to print."""
    lead = [{"speaker": "a", "text": "일정은 두 가지 안이 있었는데 다들 금요일이 낫다고 하셨죠."},
            {"speaker": "b", "text": "네, 금요일이 좋습니다."}]
    cases = [("그럼 발표는 금요일로 하겠습니다.", 0), ("자료는 제가 목요일까지 정리해 드릴게요.", 1),
             ("금요일에는 회의실이 비어 있나요?", 2), ("이 안은 다음 달까지 보류하는 걸로 하죠.", 0)]
    tok, model, digits = load_model()
    prompts = [prompt(tok, lead + [{"speaker": "a", "text": t}], 2) for t, _ in cases]
    ok = 0
    for (t, gold), q in zip(cases, ask(tok, model, digits, prompts)):
        pred = max(range(3), key=q.__getitem__)
        ok += pred == gold
        print(f"{'OK' if pred == gold else 'XX'} gold {gold + 1} pred {pred + 1} q={[round(x, 2) for x in q]}  {t}")
    print(f"{ok}/{len(cases)}")


def run(args: argparse.Namespace) -> None:
    tok, model, digits = load_model()
    variants = {"swap": args.out / "swap", "product": args.out / "product"}
    for d in variants.values():
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.M.csv"):
            old.unlink()
    changes: Counter = Counter()
    for a_path in sorted(args.sheets.glob("*.A.csv")):
        meeting = a_path.name.split(".")[0]
        rows = sheet_rows(a_path)
        scores = {r["row"]: r for r in sheet_rows(args.model_scores / f"{meeting}.M.csv")}
        order = list(full_rows(meeting) or rows)
        pos = {r["row"]: i for i, r in enumerate(order)}
        targets = [r for r in rows if scores[r["row"]]["kind"] in ("decision", "commitment")]
        prompts = []
        for r in targets:
            i = pos[r["row"]]
            lo = max(0, i - BEFORE)
            prompts.append(prompt(tok, order[lo : i + AFTER + 1], i - lo))
        qs = dict(zip((r["row"] for r in targets), ask(tok, model, digits, prompts))) if prompts else {}
        for name, d in variants.items():
            out_rows = []
            for r in rows:
                s = dict(scores[r["row"]])
                if r["row"] in qs:
                    q_dec, q_com, q_neither = qs[r["row"]]
                    if name == "swap":
                        kind = "decision" if q_dec >= q_com else "commitment"
                    else:
                        kind = ("decision" if float(s["p_decision"]) * q_dec >= float(s["p_commitment"]) * q_com
                                else "commitment")
                    changes[f"{name}: {s['kind']} -> {kind}"] += 1
                    s["kind"] = kind
                    s["q_decision"], s["q_commitment"], s["q_neither"] = f"{q_dec:.4f}", f"{q_com:.4f}", f"{q_neither:.4f}"
                else:
                    s["q_decision"] = s["q_commitment"] = s["q_neither"] = ""
                out_rows.append(s)
            with open(d / f"{meeting}.M.csv", "w", encoding="utf-8-sig", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
                w.writeheader()
                w.writerows(out_rows)
            gold = args.sheets / f"{meeting}.B.csv"
            if gold.exists():
                shutil.copyfile(gold, d / gold.name)
    for k, v in sorted(changes.items()):
        print(f"{k}: {v}")
    for name, d in variants.items():
        res = subprocess.run([sys.executable, str(AGREEMENT), str(d), "M", "B"],
                             capture_output=True, text=True, encoding="utf-8")
        (d / "agreement.txt").write_text(res.stdout + res.stderr, encoding="utf-8")
        print(f"=== {name}")
        for line in res.stdout.splitlines():
            if line.startswith(("kind ", "commitment ", "decision ", "ambiguous ", "macro F1")) and "inside" not in line:
                print(line)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["selftest", "run"])
    ap.add_argument("--sheets", type=Path)
    ap.add_argument("--model-scores", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    selftest() if args.step == "selftest" else run(args)


if __name__ == "__main__":
    main()
