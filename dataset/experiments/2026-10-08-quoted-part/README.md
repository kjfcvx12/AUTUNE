# Can the classifier's call also return the words that carry the item? (2026-10-08)

Order (the user, via 리더, 2026-10-08): for actions and decisions, a short
summary with the utterance beneath it, and for a long utterance only the part
that carries the item. S1 (#1017) keeps the sentence a turn over 300 characters
was cut into. S2 would have the same classifier request return, per commitment
or decision line, the words of that line that carry it ("parts"), and ask for a
summary of about 60 characters. This measures what S2 returns and what it costs
the labels. It decides nothing: adopting S2 is the user's choice after it.

- Script `measure_part.py`, tables `agg_part.py`, log `part.log`. Runs the
  product's own `LlmClassifier.classify` (branch `extraction/source-excerpt`
  b9c93d4e; `llm.py` is main's) with the instructions swapped in turn.
- Meetings: `8.txt`, `EVAL_02`, `EVAL_03`, `EVAL_04` -- the four invented
  meetings of `../2026-10-06-summary-with-labels`. No AI Hub text, no team
  meeting. Numbers and utterance indices only in the log.
- Model gemini-3.5-flash-lite, no fallback; the one `AUTUNE_LLM_API_KEY` line of
  the root `.env` (fingerprint c41ba374, checked by the script). 1.5 s pacing.
- **Two rounds, 52 requests, all answered, no retry** (14:09-14:17 KST). A
  round is 26: today's prompt (912 chars) 3 + 3 + 3 + 3, the new one (1,039
  chars) 3 + 4 + 4 + 3. Three rounds would have been 78, over the ~72 named to
  the user, so the third was held.

## Labels (commitment only; the gold marks nothing else)

| Meeting | today's prompt, F1 (two runs) | with parts, F1 (two runs) |
| --- | --- | --- |
| 8.txt | 0.938 (0.938, 0.938) | 0.951 (0.933, 0.968) |
| EVAL_02 | 0.907 (0.836, 0.979) | 0.947 (0.958, 0.936) |
| EVAL_03 | 0.970 (0.941, 1.000) | 0.920 (0.938, 0.903) |
| EVAL_04 | 0.948 (0.973, 0.923) | 0.971 (0.971, 0.971) |
| mean of 8 runs | **0.941** (P 0.906, R 0.985) | **0.947** (P 0.964, R 0.934) |

Reading: no difference that two runs a cell can show. The direction is
precision up, recall down: with parts the model labels fewer lines (246
commitment/decision lines over eight runs against 276) -- false positives fall
on three meetings and a few commitments are missed in both runs (EVAL_03 #152,
EVAL_04 #58, 8.txt #77 which today's prompt misses too). EVAL_02's 0.836 under
today's prompt is one run with nine false positives; the 10-06 ten-run mean
for that cell was 0.949. A ten-round comparison (260 requests) would be needed
to call 0.006 anything.

## The parts

- Returned for 246 of 246 commitment/decision lines. **All 246 are in the line
  character for character** -- none reworded, none from another line.
- 218 (88.6%) are the whole line. The lines here are short: only 16 of the 246
  are 60 characters or more.
- On those 16: the part is shorter than the line in 10, mean part/line length
  0.63, median 0.53.

## The summaries

Already short. Today's prompt: mean 28 characters, median 26, max 84, 2 of 275
over 60. Asked for "about 60": mean 31, max 61, 1 of 245 over 60. The "60자"
wording changes nothing on these meetings; none of either was over the
120-character drop limit.

## What this does not measure

**No utterance in the four meetings is over 300 characters** (`in_pieces=0` in
every run), and 16 lines in 246 are over 60. The order is about long
utterances; these meetings have almost none. That the parts are verbatim is
measured; how well a part is chosen out of a long turn is measured on 16 lines.
A meeting with long turns would have to be invented for it.

Cost of S2 as measured: one more request on two of four meetings (the longer
instructions leave less room in a window), and a longer answer.

## The long-turn check (same day, 14:34-14:35 KST)

Ordered next by the user ("진행", via 리더) because of the gap above.
`measure_long.py`, `agg_long.py`, `long.log`. One meeting invented in the
script: twelve turns of 317-412 characters (mean 357), each with one planted
promise (7) or decision (5) and a one-line question before it; 109 lines asked
about; roles only, no person's or company's name. The planted words are 9% of
their turn on average; four are a short sentence of their own, eight sit in a
longer sentence with a reason or a condition around them. Up to 600 characters
was the brief; longer turns would have taken a fourth request a run and passed
the 18 named.

**18 requests, all answered** -- 3 a run, both prompts, three rounds. Sent in
two goes of 9: the first stopped early on its own cap because the script
wrapped the classifier's client again on every run and counted each request
two and three times (fixed; the cap counted too many, never too few).

| | today's prompt | with parts |
| --- | --- | --- |
| planted sentence labelled, with the planted kind | 36/36 | 36/36 |
| other sentences of those turns, or a question, labelled | 0 | 0 |
| S1 -- the sentence, as a share of the turn | 0.180 (max 0.296) | 0.180 |
| S2 -- the returned part, as a share of the turn | -- | 0.106 |
| parts in the line character for character | -- | 36/36 |
| parts holding the planted words whole | -- | 36/36 |
| parts cut inside the planted words / elsewhere | -- | 0 / 0 |
| summary, characters (mean, max) | 38.5, 55 | 36.1, 53 |

The three rounds gave the same labels and, with parts, the same part lengths
on every turn; the summaries differed a little between rounds.

Where the planted words sit inside a longer sentence (8 turns, 24 parts): the
sentence is 0.222 of the turn and the part 0.111 -- the reason or the condition
around the promise is what S2 drops -- and every one holds the planted words
whole. Where the sentence is the promise (4 turns), the part is the sentence.

Reading: on turns over 300 characters S1 already takes a 360-character turn to
one sentence of about 65; S2 takes it to about 38, correctly in every case
here. The gain of S2 over S1 on such turns is the half of a sentence, not the
turn. What S1 cannot do and S2 can is an utterance of 300 characters or fewer
(S1 quotes it whole): on the four meetings above, the 16 lines of 60+
characters came back at 0.63 of their length.

Limits: one meeting, written by the session that scored it, in clean sentences
with full stops. A transcript without sentence ends is cut by length (200
characters) rather than by sentence, S1's part is then coarser, and S2's value
there is not measured. The planted words were judged by containment, not read.
