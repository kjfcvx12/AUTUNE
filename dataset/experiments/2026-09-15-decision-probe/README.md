# Decision probe — measuring decision recall on rows a person confirmed

**Problem.** No evaluation set we had could say anything about `decision`. The
blind set (`dataset/extraction_eval_blind/`, 200 rows) contains **0 decisions**;
the scripted S4 smoke set contains 4. Synthetic v5 had just tripled the
synthetic decisions, and there was no way to tell whether that bought anything.

**Why a probe and not a bigger random sample.** Decisions are rare in AI Hub
#464, which is broadcast, radio and "other recordings". A random Korean sample
large enough to hold 60 decisions would be thousands of rows to review by hand.
The commitment probe (`../2026-09-12-commitment-probe/`) solved the same shape of
problem for `commitment`; this is that method applied to `decision`.

## Method

1. **Calibration on the pilot.** A lexical decision-cue filter covered only
   **6 of 46** human decisions, so there is no cheap pre-filter. Qwen3-4B with
   `p_decision >= 0.10` covered **23 of 46**, and its flags were 64% true on
   that set.
2. **Scan.** 30 Validation 기타녹음 meetings (the pilot and blind meetings
   excluded), 10,374 rows → **647 candidates**.
3. **Sample.** A proportional seeded sample of **200**, spread over 29 meetings,
   written to `sheets_review/` as `*.L.csv` with only the sampled rows marked.
4. **Blind review.** `review.html` in Blind mode — the reviewer never sees
   Qwen's label. Exported as `*.B.csv`.
5. **Score.** `collect_review.py` then `score_decision.sh`, which applies every
   checkpoint to the same rows and runs `pilot_agreement.py` M vs B.

## What the reviewer confirmed (2026-09-16)

**195 of 200 confirmed, 0 meetings missing an export.**

| Human label | Rows |
| --- | --- |
| ambiguous | 91 |
| **decision** | **61** |
| commitment | 23 |
| none | 12 |
| open_question | 8 |
| concern | 0 |

61 decisions, against 0 in the blind set and 4 in S4.

**The review was not a rubber stamp**, and the distribution is the evidence:
every one of these 200 rows was selected by Qwen as a decision candidate, and
the reviewer called 91 of them ambiguous. Agreeing with the pre-fill would have
been the opposite shape.

Qwen's `p_decision` barely separates:

| p_decision | Truly decision |
| --- | --- |
| 0.1–0.3 | 5/25 (20%) |
| 0.3–0.5 | 3/10 (30%) |
| 0.5–0.9 | 13/42 (31%) |
| >= 0.9 | 40/118 (34%) |

Higher confidence is barely more often right. Qwen is usable as a **filter**
(recall 53/61 = 87% at the selection threshold) and not as a labeller
(κ 0.036).

## Scores

All on the same 195 rows. `qwen` selected these rows, so its row is biased
upward by construction and is shown for reference only.

| Model | decision recall /61 | decision precision | ambiguous /91 | commitment /23 | κ | macro5 |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen (picked the rows) | 53 (87%) | 53/162 = 33% | 9 | 1 | 0.036 | 0.178 |
| ko_sanity_0911 | 3 (5%) | 3/28 = 11% | 2 | 1 | 0.018 | 0.196 |
| ami_official | 3 (5%) | 3/20 = 15% | 3 | 1 | 0.021 | 0.199 |
| syn_probe | 15 (25%) | 15/30 = 50% | 22 | 20 | 0.202 | 0.350 |
| **v2** (`syn_none_probe`) | **15 (25%)** | **15/25 = 60%** | **27** | 20 | **0.212** | **0.369** |
| v3 (+ synthetic v5) | 15 (25%) | 15/29 = 52% | 24 | 20 | 0.188 | 0.314 |

## Three results

### 1. More synthetic decisions is not the lever

This probe existed to decide: *if v3 finds more decisions than v2, grow v5-style
data; otherwise look at what is missed first.*

**syn_probe, v2 and v3 all find exactly 15 of 61.** v5 tripled the synthetic
decisions (608 of them) and moved decision recall by nothing. v3 also costs
open_question (F1 0.714 → 0.462) and is worse overall (κ 0.188 vs 0.212).

The branch resolves to *look at what is missed first*. Do not generate more
decision data on the strength of the v5 result alone.

### 2. v2 is confirmed on a second, independent set

v2 was chosen on the blind set (macro4 0.378 vs v3's 0.360). This set is
differently built, differently sampled and differently distributed, and it
agrees: v2 leads on κ, macro5, decision precision and ambiguous recall. Two
independent sets pointing the same way is what the 09-15 anchoring incident
(κ 0.534 → 0.163) taught us to require.

### 3. Decision is lost to commitment, not to none

v2's most frequent disagreements, model → human:

```
commitment  -> decision     33
commitment  -> ambiguous    26
none        -> ambiguous    23
decision    -> ambiguous    10
ambiguous   -> decision       9
```

**33 of the 61 decisions are called `commitment`** — more than half. The model
reads a settled question as somebody promising to do something. Another 9 human
ambiguous rows are called decision.

This is a different axis from #149. `none` is about the classifier having no way
to say "none of these"; this is the decision / commitment / ambiguous boundary,
and it is where the decision number actually goes.

## A structural finding: regions do not exist

For **every** checkpoint, Qwen included:

```
settling rows:       model 0   human 61   F1 0.000
regions:             model 0   human 67   matched 0
inside-region kappa  0.000
responds_to same row 0/36
```

A per-utterance classifier has nowhere to put *where* a decision was settled.
The 2026-09-10 note guessed that decision needs "where (region) + what (settling
utterance)" rather than per-utterance classification. That is no longer a guess:
the region F1 is zero by construction, not by weakness.

## What this set may and may not be used for

The rows were selected by `p_decision >= 0.10`, so the sample is
**class-conditional**.

- **May:** measure recall per kind on rows a person confirmed; compare models on
  those rows; drive error analysis; feed confirmed rows into Korean training
  data (they are real reviewed text).
- **May not:** be reported as macro F1 or accuracy of a random meeting. The
  `macro5` column above is comparable *between the rows of this table* and
  nowhere else. `concern` has 0 gold rows here, so its column is noise.

## Next

1. Read the 33 `commitment -> decision` rows and find what they share. Before
   generating anything.
2. Decide whether decision stays a per-utterance class at all, or becomes
   region + settling row — a question for #149/#112 and for module D
   (`Decision` is the B → D contract entity).
3. A real evaluation set still needs team meetings recorded with consent
   (#190 demo path). Everything here is AI Hub #464.

## Files

| What | Path |
| --- | --- |
| Probe scan and sampling | `decision_probe.py`, `sample_candidates.py`, `scan.log` |
| Review sheets (29 × L, 29 × B) | `sheets_review/` |
| Collect exports and report | `collect_review.py` |
| Score every checkpoint | `score_decision.sh` |
| Per-model agreement output | `score_<model>/agreement.txt` |
| Review tool | `../../extraction_eval_pilot/review.html` |

## Constraints

AI Hub #464 text never leaves this machine — not to Claude, GitHub, Notion or
any LLM API. Every script here prints counts only. Derived work credits NIA
(한국지능정보사회진흥원 사업결과).

## Incident, for the next person who runs the script

`score_decision.sh` died at the **first** checkpoint with a `ZeroDivisionError`
and still exited 0.

`ko_sanity.py apply` ends by printing `bulk_none / bulk_total`. These sheets
label only the sampled rows, so `bulk_total` is 0 — a **summary print** killed a
five-checkpoint run that had already written all 29 M sheets. The wrapper
reported success because `bash script | tee` returns tee's status, not the
script's. Guarded in `ko_sanity.py`; if you add a `| tee` here, set `pipefail`
in the invoking shell too.
