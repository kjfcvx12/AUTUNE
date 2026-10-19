# Commitment probe — finding real commitment rows for the Korean evaluation set

**Problem.** The random Korean evaluation set has 802 reviewed rows and only
**9 commitment rows** (none 388, concern 177, open_question 107, ambiguous 75,
decision 46). Commitment F1 on that set is noise. The cause is the corpus, not
the sampling: AI Hub #464 is broadcast, radio, internet broadcast and "other
recordings", where people rarely take work on themselves.

**Rejected option: writing dummy rows.** Invented sentences carry the label the
author had in mind, and they would be scored against models rather than the
other way round — the same failure as the two sheets that were confirmed
without reading (measuring Qwen against itself). Synthetic rows are fine for
*training* and for a scripted smoke test (`AUTUNE_S4`), never inside the
evaluation number.

**What this does instead.** Scan unlabelled meetings from the **Training**
split (the evaluation set is drawn from Validation only) and keep the rows a
model flags as commitments, for a person to review.

## Why the model is the filter, not a word list

A lexical cue filter was calibrated first on the 802 reviewed rows: first-person
markers plus volitional endings *inside one row* caught **0 of the 9** real
commitments. AI Hub rows are intonation phrases, so a sentence's ending often
lands in a later row. Over the same 802 rows, Qwen3-4B predicted commitment 7
times and 6 were right.

A widened version is still used as a cheap pre-filter, to keep the GPU from
reading rows that cannot carry a commitment: the row plus one before and two
after must contain one of `겠 · ㄹ게 · 를게 · 을게 · 게요 · 려고 · 예정 · 드리 · 볼게`.
On the reviewed rows that keeps 37% of them and covers 7 of the 9 commitments.
Row-only would keep 12% and cover 5 of 9.

## What the result may and may not be used for

The output is a **class-conditional sample**, so:

- **May:** measure recall on commitment rows a person confirmed, compare models
  on those rows, and drive error analysis. Feed the confirmed rows into Korean
  training data (they are real text, reviewed by a person).
- **May not:** be merged into the random evaluation set's macro F1, or produce a
  precision number — precision keeps coming from the random 802 rows, where
  rows were not chosen by a model.
- **Known bias, in this order:** the pre-filter's endings → Qwen's commitment
  recall (6 of 9 on the reviewed rows) → `--pmin`. A commitment none of the
  three would surface is invisible to this probe.

Meetings used here are listed in `results/used_meetings.json`. They must be
excluded from any pseudo-labelled Korean training set, or the evaluation leaks.

## Running it

```
python probe.py scan  --meetings 60 --groups 기타녹음,인터넷방송   # writes results/
python probe.py sheets --context 3                              # writes sheets/
```

`scan` prints per meeting: rows, how many the pre-filter sent to the model, how
many cleared `--pmin` (default 0.10), and throughput. Counts and ids only —
never utterance text, per AI Hub's terms.

`sheets` writes `<meeting>.A.csv` / `.L.csv` in the pilot's format: each
candidate row plus three rows either side, so the neighbours can be read. Only
candidate rows carry `llm_kind`, and `review.html`'s filter **Commitment
candidates (probe sheets)** shows exactly those. Leave the neighbours
unconfirmed: `pilot_agreement.py` counts confirmed rows only, which is what
keeps this set class-conditional instead of half a random sample.

Group choice: a first pass over all four groups gave candidates at 0.2% of rows
in 공중파방송 and 0% in 라디오 against ~1.9% in 기타녹음, so the scan runs over
기타녹음 and 인터넷방송.

## Review result (2026-09-14)

Reviewed in `review.html`, one pass by the user, exports copied to
`sheets/<meeting>.R.csv`. `python score_probe.py` prints the numbers below
(counts only).

- **183/183 candidates confirmed**, 42 meetings: commitment **76**, none 90,
  decision 14, ambiguous 3. Not rubber-stamped: 44% equal Qwen's suggestion.
- **Only 42% of candidates are commitments** (argmax commitment 70/154 = 45%).
  The "~85%" expected beforehand came from 6 of 7 on the random set, which was
  too small to plan on.
- **Confidence does not separate them**: p ≥ 0.9 gives 55/122 (45%), p ≥ 0.5
  69/150 (46%). Raising `--pmin` would not have cleaned the set.
- **Group matters**: 기타녹음 65/129 (50%), 인터넷방송 11/54 (20%). 20 of 42
  meetings have no commitment at all.
- **Not a row-offset artefact**: of the 107 non-commitment candidates, 84 have no
  human commitment within two rows; only 5 sit one row off an unflagged
  commitment.
- **Qwen misses commitments next to its own hits**: the reviewer also labelled
  the context rows (756 of them, against the "leave neighbours unconfirmed"
  instruction above) and found 56 commitments there that were not candidates
  (29 one row away). Those rows are scored by nothing here; they show that the
  probe's recall bias is large, not only theoretical.
- Neighbour labels do not leak into `pilot_agreement.py … L R`, because L has no
  kind on those rows. They would leak into any scoring that pairs R with a model
  labelling every row (the AMI `M` sheets), so restrict that to candidate rows.

## Prompt refinement on the reviewed rows (2026-09-14, `refine.py`)

Dev set: the 939 human-labelled rows (183 candidates + 756 neighbours, 132
commitments). `python refine.py score` (GPU, ~22 min for three prompts at
1.6–2.3 rows/s, batch 6), then `python refine.py report`.

- **Rerun noise:** the scan prompt rerun differs from the scan's p by 0.036 on
  average (max 0.32; padding and bf16), flipping candidate status on 3 rows.
  Treat 1–2 point differences as noise.
- **Why commitments are missed:** of the 56 neighbour commitments, 6 fail the
  ending pre-filter and **50 pass it but get p_commitment < 0.10**. Widening the
  pre-filter or lowering `--pmin` a little would not find them.

| Rule (exact = subset of scan candidates) | Flagged | Commitment share | Of 76 kept | 기타녹음 | 인터넷방송 |
| --- | --- | --- | --- | --- | --- |
| Scan candidates | 183 | 42% | 76 | 50% | 20% |
| ∧ v1 argmax commitment | 104 | 52% | 54 | 64% | 23% |
| ∧ yes/no ≥ 0.5 | 104 | 48% | 50 | 56% | 26% |
| ∧ v1 argmax ∧ yes/no ≥ 0.5 | 78 | 54% | 42 | 66% | 23% |

Rules that may flag non-candidate rows (measured near candidates only, so
optimistic): pre ∧ v1 argmax 126 flagged, 48%, 7 of the 56 missed recovered;
pre ∧ yes/no ≥ 0.5 220 flagged, 31%, 19 recovered.

**Reading.** Prompt wording moves precision by about ten points and costs a
third of the commitments. 인터넷방송 stays at 20–26% under every prompt, so
"announcing what I am about to say" is not what goes wrong there. The recording
group is the biggest lever, and recall is limited by the model rather than the
prompt.

**Decision for the next scan:** 기타녹음 only, scan prompt unchanged (keeps
86% of the commitments at 50%). The v1 filter is an option when review time,
not data, is the constraint. Neighbours within two rows are worth reviewing:
47 of the 56 neighbour commitments lie there.

## Round 2 (2026-09-14)

```
python probe.py scan --meetings 30 --groups 기타녹음 --seed 20260914 --batch 6 --out results_r2 --exclude results/used_meetings.json
python probe.py sheets --context 2 --results results_r2 --out sheets_r2
```

30 new 기타녹음 meetings (round 1's 60 excluded): 8,271 rows, **124
candidates** (1.50% of rows), 20 sheets, 487 rows. Context is ±2 rows this time.
Both rounds' `used_meetings.json` must be excluded from pseudo-labelled training
data.

## Round 2 review result (2026-09-15)

Exports collected with `python collect_r2.py`, then `python score_probe.py sheets_r2`.

- **122/124 candidates confirmed** in 20 meetings (2 left in SRBEG21000550).
- Human labels: commitment **73**, ambiguous 21, none 16, decision 9, concern 3.
- **Commitment share 60%**, against 42% in round 1 (and 50% for round 1's
  기타녹음 meetings). Scanning 기타녹음 only did what the refinement predicted.
- By Qwen argmax: commitment 69/100 (69%), decision 4/12, ambiguous 0/9.
- By p_commitment: p ≥ 0.9 gives 59/77 (77%), p ≥ 0.5 gives 69/98 (70%). Unlike
  round 1, confidence does separate a little here.
- Review check: 76/122 (62%) equal Qwen's suggestion. One meeting with ≥ 5
  candidates kept all of them (SRBEG21000383, 5/5); 5 rows is too few to call it
  unreviewed.
- Neighbour rows were not labelled this round (0 confirmed), as instructed. So
  unlike round 1 there is no view of missed commitments next to the candidates.
- 64/73 confirmed commitments carry `responds_to`.

## After review

1. Score the confirmed rows: `python score_probe.py`, and for the pairwise view `python ../../extraction_eval_pilot/pilot_agreement.py <sheets dir> L R`.
2. For the AMI 6-way model, run `ko_sanity.py apply` over the sheets first, then
   `… M R`.
3. Report commitment recall from here and everything else from the random set,
   in separate rows of the table. Never one averaged number.
