# Flash-Lite tuning on 8.txt (2026-09-28)

`gemini-3.5-flash-lite` as `classifier_impl=llm` (the product request from
`pipeline/llm.py`, one knob changed per config). Gold: test8 utterance-level
(16 commitment, 5 ignored). Free-tier key, 15 RPM -- requests paced 5 s apart;
the batch was cut short at the user's request, so every config has n=3.

`flt.py` (classifier runs -> `runs.jsonl`), `dates.py` (whole-meeting prompt,
dates scored by hand against 3.8 Flash's table), `batch.sh` (the original,
abandoned full grid).

## Classifier (commitment F1, 3 runs each)

| config | F1 runs | mean | latency | $/meeting |
| --- | --- | --- | --- | --- |
| minimal (default), temp 0 -- product today | 0.970 / 0.750 / 0.914 | 0.878 | ~3 s | 0.0018 |
| minimal, temp 1.0 | 0.941 / 0.865 / 0.821 | 0.876 | ~3 s | 0.0018 |
| thinkingLevel low | 0.968 / 0.968 / 0.914 | 0.950 | ~3 s | 0.0018 |
| thinkingLevel medium | 0.970 / 0.970 / 0.970 | 0.970 | ~3 s | 0.0020 |
| few-shot (4 FP-type negatives) | 0.938 / 0.938 / 0.938 | 0.938 | ~3 s | 0.0017 |
| thinkingLevel high (1 window only) | -- | -- | 17.7 s/window | ~0.03 |

- Recall is ~1.0 everywhere; Flash-Lite's error is false positives: proposal
  (#26), opinions/votes (#56 #57 #62-65), answer to a question (#73).
- temp 0 is not deterministic: 0.750-0.970 across three identical requests.
  Temperature 0 vs 1.0 made no measurable difference (0.878 vs 0.876).
- low and medium reported `thoughtsTokenCount` 0 on every window -- the level
  is a ceiling and the model chose not to think. high did think (5,990 tokens
  on one window), so the setting is applied. Why medium is 3/3 at 0.970 with no
  thinking is unexplained; n=3 on one meeting cannot separate it from luck.
- Few-shot removed the vote/opinion/answer FPs in all three runs but lost #77
  ("천천히 만들어볼게요") and kept #26. The examples were written against 8.txt's
  own FPs (analogues, not copies), so this is tuned on the test meeting.
- Latency means in `runs.jsonl` include 429 back-off (runs of 89 s, 30 s,
  27 s); unthrottled runs are 2.5-3.5 s.

## Offline (no new calls)

- Majority of 3 (all 20 three-run combos of the six minimal runs): mean 0.889,
  min 0.800. Union: mean 0.796 -- unions add FPs, and recall was already 1.0.
- Cascade to 3.8 Flash on disputed windows: minimal runs disagreed on 1-2 of 2
  windows, so nearly every window would be re-asked -- 3x Flash-Lite plus
  3.8 Flash costs more than 3.8 Flash alone. Not worth running.

## Dates (whole-meeting prompt, 1 run)

| | wrong dates | missed items |
| --- | --- | --- |
| Flash-Lite minimal (09-26) | 2 (#37 "내일 오전" -> 10/2, #79 "다음 주 금요일" -> 10/2) | 알림 문구 개선안, QA 인턴 자료 |
| Flash-Lite medium (1,308 thinking tokens, 6.4 s, $0.0063) | 1 (#79 -> 10/2; #37 now 9/29) | same two |
| `slots.parse_due` on the 16 gold utterances | 1 (#49 "다음 주 초" -> 10/9, known) | #77 "이번 분기 안에" unparsed; #29 #46 #75 carry no date |

`parse_due` gets both of Flash-Lite's wrong dates right; the product already
takes dates from `parse_due`, not from the LLM.

## Confirmation on a second meeting: EVAL_02 (same day, 19:2x)

Self-authored dummy from the fine-tune test set (`2026-09-27-llm-finetune/test.jsonl`):
284 utterances, 23 commitment, 40 ignored, 3 windows. Few-shot examples were
written before this meeting was looked at, so this is an untuned test for them.

| config | F1 runs | mean | $/meeting |
| --- | --- | --- | --- |
| minimal, temp 0 (product) | 0.939 / 0.786 / 0.721 | 0.815 | 0.0041 |
| thinkingLevel medium | 0.568 / 0.622 / 0.630 | 0.607 | 0.0047 |
| **few-shot** | **0.979 / 0.939 / 0.958** | **0.959** | **0.0032** |
| 3.8 Flash reference | -- (503 x7, abandoned) | | |

- medium's 3/3 0.970 on 8.txt did not replicate -- it is the worst config here
  (still 0 thinking tokens). Do not set `thinkingConfig`.
- The FPs are answers to questions and statements of capability ("원격으로 잠글 수
  있습니다", "스무 명씩입니다") -- the same family as 8.txt #73, which the few-shot
  example 6-7 targets. Few-shot kept recall 1.0 and cut FPs from 3-16 to 1-3.
- Across both meetings few-shot is the only config that is both better and
  stable run to run (8.txt 0.938 x3, EVAL_02 0.939-0.979); its cost on 8.txt is
  losing #77 ("천천히 만들어볼게요").

## Classifier + Flash-Lite (same day, 20:0x) -- `combo.py`

Few-shot Flash-Lite (PR #419's prompt), one run per meeting, on the 20 dummy
eval meetings (EVAL_01-12, EVALH_01-08; EVAL_02 = its rep0). 74 new requests,
$0.066 in all (~$0.0033/meeting). DeBERTa = saved `results/clf_test.json`
(share_s20260910). Queue columns assume a person resolves every queued item
correctly (upper bound), as in `cascade.py`.

| set (gold) | Lite | clf | AND | OR | Lite->clf (queue, true) | clf->Lite (queue, true) |
| --- | --- | --- | --- | --- | --- | --- |
| all 20 (341) | 0.905 | 0.874 | 0.921 | 0.862 | **0.951** (54, 19) | 0.944 (68, 14) |
| EVAL 12 (206) | 0.932 | 0.922 | 0.925 | 0.929 | **0.962** (27, 14) | 0.955 (25, 11) |
| EVALH 8 (135) | 0.868 | 0.811 | 0.916 | 0.777 | **0.936** (27, 5) | 0.928 (43, 3) |

- Lite alone beats the classifier on these meetings, most on the hard set.
- AND is the best combination with no person: precision 0.953 (15 FPs vs 50/69
  alone), recall 0.891.
- Lite proposing, classifier checking is the best with a person: ~2.7 queued
  items a meeting, a third of them true.
- Caveats: the classifier was trained on dummies from the same generator, so
  its numbers here are optimistic (commitment F1 ~0.3 on real speech). Lite is
  one run per meeting and varies run to run. Neither is measured on real
  meetings -- Gemini may not see AI Hub data.
