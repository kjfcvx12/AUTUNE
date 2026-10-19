# Roster-name substitution in the LLM classifier (#411), 2026-09-30

Branch `extraction/roster-placeholders` @ `1754bab`, the product `LlmClassifier`
with `use_roster` off and on. Free-tier key; self-authored dummy meetings only.

- 8.txt (86 utterances, test8 gold: 16 commitment, 5 ignored). Roster derived
  from the names the text addresses: 강민구, 민재, 재경, 종훈 -- 10 utterances
  change under substitution.
- EVAL_02 was dropped: its only "<x> 님" is 센터장 (a title), so the roster is
  empty and on/off send identical requests.

## Commitment F1, gemini-3.5-flash-lite, 5 runs each (`roster_eval.py`, `runs.jsonl`)

| roster | runs | mean | names in the request bodies |
| --- | --- | --- | --- |
| off | 0.903 / 1.000 / 0.903 / 0.933 / 0.933 | 0.934 | all four, every run |
| on  | 0.968 / 0.968 / 0.968 / 0.897 / 0.833 | 0.927 | none, every run |

The 0.007 difference is inside run-to-run spread (0.833-1.000 with identical
requests). Recorded before #411: 0.909 (#393, one run), 0.938 x3 with the
few-shot prompt (2026-09-28 tuning).

gemini-3.8-flash: not measured -- 503 on four consecutive attempts (the same
busy-model answers as 09-28); not retried to spare the 20-requests-a-day quota.
