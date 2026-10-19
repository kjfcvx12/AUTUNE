# 2026-09-12 — LLM zero-shot vs the fine-tuned classifier (AMI, natural distribution)

The mentor's suggestion for the final presentation: compare the trained model with
an LLM on the natural-distribution evaluation, where both can answer "none".

- **LLM:** local `Qwen/Qwen3-4B-Instruct-2507`, zero-shot, English prompt defining
  the six kinds the way the AMI mapping does; the answer is read from next-token
  probabilities over "1"–"6" (no generation, no parsing). **Context: 4 acts before,
  2 after.** `llm_zero_shot.py`.
- **Fine-tuned:** the official 6-way kf-deberta-base checkpoint
  (`../2026-09-11-official-6way`), **the act alone, no context**.
- Same splits, same harness (`score_llm_*.txt`, `../2026-09-11-official-6way/score_*.txt`).
  Selftest 7/7 on invented sentences.

## Results

| | Fine-tuned (no context) | LLM zero-shot (context ±) |
| --- | --- | --- |
| **Natural macro F1, five kinds** (`test.jsonl`, none 78.7%) | **0.329** | 0.179 |
| Closed macro F1 (`test_closed.jsonl`) | **0.654** | 0.352 |
| Action item F1, natural / closed | 0.325 / 0.774 | 0.283 / 0.456 |
| False labels per 2,400 acts (none given a kind) | 954 | 978 |
| Where false labels go | decision 1,227 | ambiguous 1,326, open_question 551 |
| Time for the 5,237-act set, same RTX 3060 | 39 s incl. model load | ≈ 860 s (6.1 acts/s) |

Per kind on the natural set, LLM (P / R / F1): commitment 0.273 / 0.294 / 0.283 ·
decision 0.135 / **0.036** / 0.057 · open_question 0.234 / 0.509 / 0.321 ·
concern 0.148 / 0.258 / 0.188 · ambiguous **0.023** / 0.606 / 0.045.

## Reading

- On AMI's own conventions the fine-tuned model is ahead on every summary number
  despite seeing no context, and is ~20x cheaper.
- The two fail differently. The fine-tuned model sprays `decision` (it learned
  "assertive act in a decision region" from one act); the LLM almost never says
  `decision` (recall 0.036 — it reads "decision" as an explicit settlement, which is
  not how AMI labels it) and floods `ambiguous` with ordinary hedged speech (1,730
  predictions for 66 gold).
- So part of the gap is **annotation convention, not understanding**: the LLM is
  scored against labels it has only a one-line definition of. One prompt, no
  few-shot, no tuning — a single data point, not the LLM's ceiling.
- Same false-label volume (954 vs 978): neither approach solves "none" by itself,
  which points back to the region framing for decisions (#149 point 3,
  `../2026-09-11-decision-entities`).

For Korean data the same comparison must stay local (AI Hub terms); this setup
(local model, counts-only output) is built for that.

AMI is CC BY 4.0.
