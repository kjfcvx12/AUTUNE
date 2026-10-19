# Commitment F1 of the llm classifier with and without the summary sentences (2026-10-06)

Does asking the classifier for a one-line summary of each commitment and
decision (#880) change the labels it gives?

- Script: `measure.py` (loaders and scoring are `../2026-09-28-flash-lite-tuning/flt.py`'s).
  It runs the product's own `LlmClassifier.classify` from whichever worktree's
  venv runs it, and prints numbers and utterance indices only.
- Meetings: `8.txt` (86 utterances, 16 gold commitments, 5 ignored) and
  `EVAL_02` (284 utterances, 23 gold commitments, 40 ignored). Both are
  self-authored dummy meetings: `../../extraction_eval_dummy/README.md`
  ("Invented Korean workplace meetings"), HISTORY ("self-authored,
  non-AI-Hub"), and `flt.py`'s docstrings. No AI Hub text was sent.
- Model: gemini-3.5-flash-lite, no fallback, the last `AUTUNE_LLM_API_KEY` of
  the root `.env`; 4.5 s between requests (the script's pacing). Three runs each.
- Only commitment is scored: the gold marks commitments only.

| Code | Instructions | 8.txt F1 (min-max) | EVAL_02 F1 (min-max) |
| --- | --- | --- | --- |
| main `401721e5` -- labels only | 714 chars | **0.946** (0.903-0.968) | **0.979** (0.978-0.979) |
| #880 `c28b4ff6` -- labels and summaries | 912 chars | **0.938** (0.938 x3) | **0.958** (0.936-0.979) |

For comparison, 2026-09-28 (before turns were read by sentence, #869): 0.938 x3
and 0.959 (0.939-0.979).

Per run, #880: 8.txt -- P 0.938 R 0.938, one false positive (#33) and one miss
(#77) in all three; 23 summaries kept each run. EVAL_02 -- recall 0.957 / 1.0 /
1.0; false positives #159 in all three, plus #192 or #225 in two; 40-44
summaries kept. main: 8.txt misses #49 in all three (and #77 once), one false
positive once; EVAL_02 at most one false positive or one miss a run.

Reading: no large change. On 8.txt the two are within each other's spread. On
EVAL_02 the summary sentences cost about 0.02 of F1 -- one false positive
(#159) that main did not have in any run -- with recall the same or better.
Three runs a cell, one model, two meetings: enough to say the prompt was not
broken, not enough to say 0.02 is real.

Requests: 2-3 a meeting either way.

## Ten more runs a cell, the two prompts in turn (same day, afternoon)

`measure_repeat.sh` in the session scratchpad: ten rounds, each round one run of
"labels only" (the code before #880) and one of "labels + summaries" (main with
#880), on both meetings, so that neither prompt has the provider's better
half-hour. Same model, same key line, same scoring.

| Prompt | 8.txt F1 mean (sd, min-max) | P / R | EVAL_02 F1 mean (sd, min-max) | P / R |
| --- | --- | --- | --- | --- |
| labels only, 714 chars | **0.961** (0.014, 0.933-0.968) | 1.000 / 0.925 | **0.974** (0.016, 0.957-1.000) | 0.962 / 0.987 |
| labels + summaries, 912 chars | **0.920** (0.025, 0.875-0.938) | 0.914 / 0.925 | **0.949** (0.014, 0.917-0.958) | 0.938 / 0.961 |

False positives, runs out of ten: with summaries 8.txt #33 in 9 and #26 in 5;
EVAL_02 #225 in 7, #159 in 5, #192 in 3. Labels only: 8.txt none; EVAL_02 #202
in 6, #159 in 3. Misses: with summaries 8.txt #77 in 10 and #34 in 2, EVAL_02
#137 in 9; labels only 8.txt #49 in 8 and #77 in 4, EVAL_02 #99 in 3.
Requests a run: 8.txt 3 with summaries against 2 without (the longer
instructions leave less room in a window); EVAL_02 3 either way.

Reading: the three-run table above said "not enough to say 0.02 is real". With
ten alternated runs the difference is there on both meetings and in the same
direction: about 0.04 on 8.txt and 0.025 on EVAL_02, larger than either cell's
spread, and it is precision that is lost (a few utterances the summary prompt
labels a commitment in most runs) while recall is level on 8.txt and slightly
lower on EVAL_02. Still two dummy meetings, one model, commitment only.

## Three rewrites of the instructions, screened (same day, 15:04-17:20)

`measure_prompt.py 3 prompt_screen.log`, aggregated by `agg_prompt.py`. Four
versions swapped in turn, round by round, in one worktree at main (#880 in):
`main` (912 chars); `rules` (979: a commitment is the speaker's own task or a
request made to them; "그럼 확정할게요" is a decision; capability, routine and
an unasked "네, 알겠습니다" are nothing); `examples` (1018: two more worked
examples); `rules+examples` (1085). Four dummy meetings: 8.txt and EVAL_02,
whose misses I READ before writing the rewrites, and EVAL_03 and EVAL_04,
which I did not look at. Three rounds; commitment F1 mean; 48 runs, no errors.
The provider slowed from about 15 s to about 90 s a request after 17:00.

| Version | 8.txt (read) | EVAL_02 (read) | EVAL_03 (unseen) | EVAL_04 (unseen) |
| --- | --- | --- | --- | --- |
| main | 0.938 | 0.957 | **0.942** | **1.000** |
| rules | 0.989 | 0.933 | 0.979 | 0.951 |
| examples | 0.980 | 0.958 | 0.958 | 0.981 |
| rules+examples | 0.980 | 0.978 | 0.900 | 0.981 |

Unseen mean: main 0.971, examples 0.970, rules 0.965, rules+examples 0.941.
Requests a run: 3 for main everywhere; 4 on EVAL_02 and/or EVAL_03 for the
longer versions.

Acknowledgement probe (seven invented lines, 3 rounds): "네 알겠습니다." after a
piece of news -- main `ambiguous` 3/3, every rewrite `none` 3/3; after a request
addressed to the speaker -- main and rules+examples `commitment` 3/3, rules and
examples `none` 3/3. Controls (says what / can do / settles) right in all 12.
`ack_probe.py`, the original shape (a 900-character turn, then "네 알겠습니다."),
main, 5 runs: `none` 5/5.

Reading: every rewrite looks better on the two meetings it was written from and
none is better on the two it was not. Not adopted. n=3 a cell; sd about 0.015.

`greeting_392.py`: the #392 run (a greeting + attendance notice as a first
utterance): `none` 40/40 under both prompts.
