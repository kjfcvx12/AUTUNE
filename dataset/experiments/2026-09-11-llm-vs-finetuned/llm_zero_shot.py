"""Zero-shot 6-way with a local LLM, scored by the same harness as the fine-tuned model.

    python llm_zero_shot.py windows   # build the prompts only (CPU), print counts
    python llm_zero_shot.py selftest  # invented sentences, GPU
    python llm_zero_shot.py run       # both test sets, GPU; writes pred_llm_*.jsonl

The mentor's suggestion (HISTORY 09-10): compare the trained model with an LLM on
the natural-distribution evaluation, where an LLM can answer "none" and the old
five-way model could not. AMI is CC BY 4.0, so any LLM could read it; this uses the
local Qwen3-4B anyway, because the same comparison on Korean data must be local
(AI Hub terms) and one setup should serve both.

Same trick as the Korean pilot's first pass: the prompt ends where the answer digit
goes, and the next-token probabilities of "1".."6" are read off -- one forward pass
per act, no parsing.

**Not the same input as the fine-tuned model.** The LLM sees 4 acts before and 2
after (concern and ambiguous are defined by what an act answers); the fine-tuned
baseline in ../2026-09-11-official-6way reads the act alone. The report says so.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SPLITS = HERE.parent / "2026-09-11-official-6way" / "splits"
CORPUS = ROOT / "dataset" / "ami_public_manual_1.6.2"
sys.path.insert(0, str(HERE.parent / "2026-09-10-none-context"))

MODEL = "Qwen/Qwen3-4B-Instruct-2507"
KINDS = ["commitment", "decision", "open_question", "concern", "ambiguous", "none"]
BEFORE, AFTER = 4, 2

SYSTEM = """You label utterances from design-team meetings. Classify the one utterance marked [TARGET] into exactly one of six kinds.
1 commitment - the speaker offers or undertakes to do something themselves. e.g. "I'll send the slides round after the meeting."
2 decision - said while the group settles something: what they will do, or have now agreed. e.g. "So we're going with the rubber case then."
3 question - a genuine request for information, an opinion, or a suggestion. e.g. "What do you think about the colour?"
4 concern - a negative response to something just said: disagreement, objection, or doubt about it. e.g. "I don't think that'll work, it's too expensive."
5 ambiguous - an uncertain or partial response to something just said: hedged or half agreement. e.g. "Maybe, I'm not sure."
6 none - everything else: giving information, backchannels ("Okay.", "Yeah."), fragments, stalls, greetings, managing the meeting.
Rules:
- Most utterances are 6.
- If several apply, prefer 2 > 4 > 3 > 5 > 1.
Answer with a single digit."""


def ordered_meetings() -> dict[str, list[dict]]:
    """Every act of every meeting, in time order, with its speaker."""
    from exp_ctx_none import build_rows  # noqa: PLC0415 - the join from yesterday, unchanged

    rows, _ = build_rows(CORPUS)
    meetings: dict[str, list[dict]] = {}
    for row in rows:
        meetings.setdefault(row["meeting"], []).append(row)
    for acts in meetings.values():
        acts.sort(key=lambda r: (r["start"], r["id"]))
    return meetings


def wanted() -> dict[str, list[str]]:
    return {
        name: [json.loads(line)["utterance_id"] for line in (SPLITS / f"{name}.jsonl").open(encoding="utf-8") if line.strip()]
        for name in ("test", "test_closed")
    }


def build_prompts(tok) -> tuple[dict[str, str], dict[str, list[str]]]:  # noqa: ANN001
    meetings = ordered_meetings()
    position = {row["id"]: (m, i) for m, acts in meetings.items() for i, row in enumerate(acts)}
    ids = wanted()
    prompts: dict[str, str] = {}
    missing = 0
    for uid in {u for us in ids.values() for u in us}:
        if uid not in position:
            missing += 1
            continue
        meeting, i = position[uid]
        acts = meetings[meeting]
        window = acts[max(0, i - BEFORE) : i + AFTER + 1]
        target = min(i, BEFORE)
        lines = [f"{'[TARGET] ' if j == target else ''}Speaker {r['speaker']}: {r['text']}" for j, r in enumerate(window)]
        user = "Meeting excerpt (with context):\n" + "\n".join(lines) + "\n\nWhich kind is the [TARGET] utterance?"
        messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
        prompts[uid] = (
            tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True) if tok else user
        )
    if missing:
        raise SystemExit(f"{missing} evaluation ids were not found in the corpus join")
    return prompts, ids


def load_model():
    import torch  # noqa: PLC0415
    from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: PLC0415

    tok = AutoTokenizer.from_pretrained(MODEL)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16).to("cuda").eval()
    digits = [tok.convert_tokens_to_ids(str(i)) for i in range(1, 7)]
    if any(d is None or d == tok.unk_token_id for d in digits):
        raise SystemExit("digits 1-6 are not single tokens for this tokenizer")
    return tok, model, digits


def score(tok, model, digits, prompts: list[str], batch: int = 8) -> list[list[float]]:  # noqa: ANN001
    import torch  # noqa: PLC0415

    out: list[list[float]] = []
    with torch.no_grad():
        for s in range(0, len(prompts), batch):
            enc = tok(prompts[s : s + batch], return_tensors="pt", padding=True).to("cuda")
            logits = model(**enc).logits[:, -1, :].float()
            out.extend(torch.softmax(logits[:, digits], dim=-1).cpu().tolist())
    return out


def main(mode: str) -> None:
    if mode == "windows":
        prompts, ids = build_prompts(None)
        sizes = sorted(len(p) for p in prompts.values())
        print(f"{len(prompts)} prompts; test {len(ids['test'])}, test_closed {len(ids['test_closed'])}; "
              f"chars median {sizes[len(sizes) // 2]}, max {sizes[-1]}")
        return

    tok, model, digits = load_model()
    if mode == "selftest":
        cases = [
            ("I'll send the slides round after the meeting.", "commitment"),
            ("Okay, so we're going with the rubber case then.", "decision"),
            ("What do you think about the colour?", "open_question"),
            ("I don't think that'll work, it's too expensive.", "concern"),
            ("Maybe, I'm not sure.", "ambiguous"),
            ("Yeah.", "none"),
            ("The battery lasts about two years.", "none"),
        ]
        before = "Speaker A: Should we use solar power for the remote?"
        prompts = []
        for text, _ in cases:
            user = f"Meeting excerpt (with context):\n{before}\n[TARGET] Speaker B: {text}\n\nWhich kind is the [TARGET] utterance?"
            messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
            prompts.append(tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True))
        right = 0
        for (text, gold), p in zip(cases, score(tok, model, digits, prompts), strict=True):
            pred = KINDS[max(range(6), key=p.__getitem__)]
            right += pred == gold
            print(f"{'OK' if pred == gold else 'XX'} {gold:<14} -> {pred:<14} p={max(p):.2f}  {text}")
        print(f"{right}/{len(cases)}")
        return

    prompts, ids = build_prompts(tok)
    order = sorted(prompts)
    started = time.time()
    probs = dict(zip(order, score(tok, model, digits, [prompts[u] for u in order]), strict=True))
    elapsed = time.time() - started
    for name, uids in ids.items():
        kinds = [KINDS[max(range(6), key=probs[u].__getitem__)] for u in uids]
        (HERE / f"pred_llm_{name}.jsonl").write_text(
            "\n".join(json.dumps({"utterance_id": u, "kind": k}) for u, k in zip(uids, kinds, strict=True)),
            encoding="utf-8",
        )
        print(f"{name}: {len(uids)} acts -> {dict(Counter(kinds))}")
    print(f"{len(order)} prompts in {elapsed:.0f}s ({len(order) / elapsed:.1f}/s) on {MODEL}")


if __name__ == "__main__":
    main(sys.argv[1])
