# Does *harder* dummy data help? (2026-09-21)

The 2026-09-18 experiment settled the quantity question: 30 dummy meetings and 100
dummy meetings train to the same model (dummy macro F1 0.810 vs 0.807, and the
100-meeting one is slightly worse on real speech). So writing more of the same is
not a lever.

`register_stats.py` says what the difference between the dummy meetings and real
speech actually is, and it is not vocabulary:

| | rows | median chars | <=6 chars | fillers /100 chars | self-fix /100 chars | same speaker as previous row |
| --- | --- | --- | --- | --- | --- | --- |
| dummy (train, 100 meetings) | 27,438 | 22 | 8.5% | 0.93 | 0.08 | 21.3% |
| dummy (eval, 12 meetings) | 3,502 | 15 | 13.7% | 1.07 | 0.14 | 14.4% |
| AI Hub, chaired 12 | 3,512 | **45** | 5.7% | **2.44** | 0.14 | **60.6%** |

Fillers and self-corrections are counted per character, not per row. Per row they
looked far worse for AI Hub (31% against 11%) purely because its rows are twice as
long, and a meeting could pass by opening every sentence with "어" — the first
pilot did exactly that, reaching 28.6% of rows while carrying 1.3 fillers per 100
characters, the same as the meetings it was replacing.

The dummy meetings are ping-pong — a short line, then a different speaker. Real
meetings are one person holding the floor for several long rows while the others
say nothing. An act therefore lands, in real speech, in the middle of somebody's
turn; in the dummy data it always lands in a short clean line of its own.

`team_dummy/SPEC.md`'s 2026-09-21 addendum turns that table into authoring rules,
and `team_dummy/register_check.py` is the acceptance check — bands chosen to
contain the AI Hub column. DUMMY_101 onward are written to it.

## The comparison

Hold the size fixed and change only the style:

    python build_split.py --name clean20 --meetings 1-20
    python build_split.py --name rough20 --meetings 101-120

then train one seed on each and score both with `extraction_eval/run_eval.py`.
Twenty a side rather than thirty: the quantity question is already settled (30
meetings and 100 meetings train to the same model), so the count only has to be
equal, and each meeting written to the 2026-09-21 addenda costs real effort.
`clean20` is the control — the same recipe over the old ping-pong meetings. The
question is whether `rough20` beats it **on `aihub_chaired12`**, on real
speech. Its score on `dummy_eval` is not the answer — `dummy_eval` is written in
the old clean style, so it measures the old register either way, and a drop there
is expected rather than alarming.

Nothing in `extraction_eval*` is read as training data here.

## Result (2026-09-22) — rough20 does not win

Three seeds a side (20260910, 20260916, 20260917), scored by `run_eval.py`
(`run.log` for the first seed, `run_seeds2.log` for the other two — the tiny
`train_clean20.log` / `train_rough20.log` are a failed first attempt,
`ModuleNotFoundError: No module named 'autune_extraction'`, superseded by
`run.sh`, which checks the import and the GPU before starting).

**`aihub_chaired12` (1,200 rows, the decisive part per the plan above), macro F1
over the five acted-on kinds:**

| seed | clean20 | rough20 |
| --- | --- | --- |
| 20260910 | 0.340 | 0.353 |
| 20260916 | 0.353 | 0.355 |
| 20260917 | 0.357 | 0.327 |
| **mean** | **0.350** | **0.345** |

Rough loses the mean, and the spread (0.327–0.355) is wider than the 0.013 gap
the first seed alone could not separate from noise. Three seeds do not separate
it either, in the other direction.

**Decision F1 alone, same rows** — the one category this whole rewrite was
aimed at:

| seed | clean20 | rough20 |
| --- | --- | --- |
| 20260910 | 0.215 | 0.189 |
| 20260916 | 0.222 | 0.184 |
| 20260917 | 0.204 | 0.138 |
| **mean** | **0.214** | **0.170** |

Rough is behind on **every seed**, by about 20% relative on the mean. This is
the opposite of the hypothesis: harder, more realistic training meetings were
supposed to teach the model to find a decision buried in someone's fourth row,
and on the one number that tests exactly that, on real speech, they do worse.

`aihub_blind1` (200 rows, noisy) tips the other way on average (macro5 0.260
clean vs 0.286 rough), but it is too small a slice to weigh against
`chaired12`, and the plan above named `chaired12` the one that decides this.

`dummy_eval` drops for rough on both splits' own report, as expected — it is
written in the old ping-pong style either model is being asked to leave, so a
drop there was never the question.

**Conclusion:** the gate in `dataset/auto/QUEUE.md` Phase 4 — "favours rough on
chaired12 and blind1" — is not met. `chaired12`, the part the plan itself
called decisive, does not favour rough, and decision F1 specifically favours
clean on every seed. Writing ten more rough meetings (DUMMY_121–130) is not
supported by this comparison and stays blocked.

What this does not rule out: a *larger* rough set, a mix of the two styles, or
a fix to whatever in the rough style is costing decision recall specifically
(three training meetings' worth of harder acts is a small sample to generalise
from) are all still open questions — this experiment only answers the one
question it was built to answer, at this size, on this one axis.

## Result (2026-09-22b) — rough30 at 30-a-side: still no, but a real signal elsewhere

Unblocked on 2026-09-22 by a person's explicit decision (recorded in
`dataset/auto/QUEUE.md` Phase 4): 20-a-side may be too small a sample for the
harder style to show its effect, and `rough30` (DUMMY_101–130, i.e. the 20
meetings above plus ten more written the same way) against `clean30` (same
recipe, `experiments/2026-09-18-dummy-train`'s v4 rebuilt fresh here for a
same-pipeline comparison) tests that directly, at the scale the 2026-09-18
experiment already validated isn't itself a confound. Same three seeds
(20260910, 20260916, 20260917), same `run_eval.py`, run via `run30.sh`
(`run30.log`).

**`aihub_chaired12`, macro F1 over the five acted-on kinds:**

| seed | clean30 | rough30 |
| --- | --- | --- |
| 20260910 | 0.349 | 0.346 |
| 20260916 | 0.347 | 0.336 |
| 20260917 | 0.349 | 0.338 |
| **mean** | **0.348** | **0.340** |

Rough loses the mean again, by about the same margin as at 20-a-side — going
from 20 to 30 meetings a side did not close the gap.

**Decision F1 alone, `aihub_chaired12`:**

| seed | clean30 | rough30 |
| --- | --- | --- |
| 20260910 | 0.208 | 0.176 |
| 20260916 | 0.222 | 0.193 |
| 20260917 | 0.208 | 0.184 |
| **mean** | **0.213** | **0.184** |

Rough is still behind on every seed. The relative gap narrows somewhat (~14%
at 30-a-side vs ~20% at 20-a-side), but clean is still ahead on the number the
whole rewrite targeted.

**`aihub_blind1` (200 rows) — this one reverses:**

| seed | clean30 macro5 | rough30 macro5 |
| --- | --- | --- |
| 20260910 | 0.300 | 0.246 |
| 20260916 | 0.328 | 0.244 |
| 20260917 | 0.285 | 0.267 |
| **mean** | **0.304** | **0.252** |

At 20-a-side, `blind1` was the one part that tipped toward rough (0.260 vs
0.286). At 30-a-side it tips the other way, clean ahead by about the same
margin. `blind1` gold has zero decision rows, so decision F1 is 0.000 on both
splits every seed — not a meaningful comparison on that axis.

**`dummy_eval_hard` — the one part that clearly favours rough:**

This part did not exist when the 20-a-side comparison ran (Phase 1–3 of the
hard eval set finished afterward, same session as DUMMY_121–130). It is
scored here for the first time.

| seed | clean30 macro5 | rough30 macro5 | clean30 decision F1 | rough30 decision F1 |
| --- | --- | --- | --- | --- |
| 20260910 | 0.592 | 0.790 | 0.672 | 0.800 |
| 20260916 | 0.621 | 0.762 | 0.696 | 0.782 |
| 20260917 | 0.623 | 0.754 | 0.705 | 0.739 |
| **mean** | **0.612** | **0.769** | **0.691** | **0.774** |

Rough wins by a wide margin here, on every seed, on both metrics. This is the
one eval part deliberately written to be hard to read — vague references,
broken-off turns, side talk, resistance before a decision settles, owner and
deadline off the settling row (`team_dummy/SPEC.md`'s 09-21b/09-21c addenda,
`hard_check.py`) — the exact texture `dummy_eval` and `chaired12` mostly lack.

`dummy_eval` (the original, easier eval part) drops for rough on both splits'
own report again, same as at 20-a-side and for the same reason — it is
written in the old ping-pong style either model is being asked to leave.

**Conclusion:** the QUEUE.md gate — "favours rough on chaired12 and blind1" —
is still not met at 30-a-side; if anything `blind1` now goes the other way
too. Going from 20 to 30 meetings a side did not turn this around, so sample
size at this scale was not the missing piece. But `dummy_eval_hard` gives the
first clean, wide-margin, every-seed result in rough's favour, and it is on
exactly the property the rough style was written to teach — a decision that
has to be found inside resistance and vague reference, not stated plainly.
The likeliest reading: rough training helps on inputs that are actually hard
in the way rough training is hard, but `aihub_chaired12`'s difficulty for
this model is not currently register difficulty (filler density, turn
length, same-speaker runs) in a way that rough's harder *semantics* fixes —
the two axes are not the same thing, and closing one does not obviously close
the other. A follow-up that scores rough30 against a harder *AI Hub* slice,
if one can be identified or built, would separate "rough helps on hard
inputs in general" from "rough helps on inputs shaped like `dummy_eval_hard`
specifically."

## Result (2026-09-22c) — context (±2 utterances) does not move chaired12 either (#323)

`build_ctx_split.py` in this directory rebuilt `clean30`/`rough30` with two
neighbouring utterances of context on each side, same rows and labels as the
no-context split -- only the input changes, so this isolates context as the
one variable. Trained with `ctx_train.py` and scored with `score_models.py
--context 2` (from `2026-09-17-ensemble-context-llm/`, reused rather than
rewritten), same three seeds, run via `run_ctx30.sh` (`run_ctx30.log` +
`run_ctx30_resume.log` after a shared-environment `accelerate` reinstall
mid-run).

This follows directly from issue #323's diagnosis: `diagnose_chaired12.py`
found the classifier mispredicting a missed decision as `commitment` more
than half the time, and `TrainExample`/`encode()` (`training/dataset.py`,
`training/train.py`) confirmed the model sees one utterance at a time, no
context window -- a real architectural gap, and the obvious hypothesis for
*why* a decision/commitment boundary that often depends on what was said just
before or after (`1.txt`'s distinction: a decision settles something now, a
commitment is one person's promise about later) goes unresolved.

**`aihub_chaired12`, decision F1 alone -- no-context vs context=2:**

| | clean30 (no ctx) | clean30_ctx2 | rough30 (no ctx) | rough30_ctx2 |
| --- | --- | --- | --- | --- |
| 20260910 | 0.208 | 0.102 | 0.176 | 0.152 |
| 20260916 | 0.222 | 0.139 | 0.193 | 0.194 |
| 20260917 | 0.208 | 0.392 | 0.184 | 0.211 |
| **mean** | **0.213** | **0.211** | **0.184** | **0.186** |

Context lands within noise of no-context on both splits' mean -- a 0.002
move either way, dwarfed by the seed-to-seed spread context itself shows
(clean30_ctx2 alone ranges 0.102 to 0.392 across seeds, wider than the whole
no-context-vs-context gap). **Giving the model the two neighbouring
utterances did not fix chaired12's decision/commitment confusion.**

**`aihub_chaired12` macro F1 (five kinds) and `aihub_blind1` macro F1, same
comparison:**

| | clean30 (no ctx) | clean30_ctx2 | rough30 (no ctx) | rough30_ctx2 |
| --- | --- | --- | --- | --- |
| chaired12 macro5 | 0.348 | 0.342 | 0.340 | 0.352 |
| blind1 macro5 | 0.304 | 0.323 | 0.252 | 0.272 |

Same story: every number moves by roughly a seed's worth of noise, nothing
resembling the jump from `dummy_eval` to `dummy_eval_hard` two sections up.
The one shift worth naming -- rough30_ctx2 edges ahead of clean30_ctx2 on
chaired12 macro5 (0.352 vs 0.342), reversing the no-context direction -- is
smaller than the seed spread within either column, so it is not read as a
real effect here.

**Conclusion, and where this leaves #323's open question:** the architectural
gap `diagnose_chaired12.py` and `dataset.py`/`train.py` found is real -- the
classifier still sees one utterance at a time in production -- but it is not
the explanation for chaired12's specific decision/commitment miss rate.
Two utterances of neighbouring context, the most direct fix for "the model
can't see what came before or after," made no measurable difference. Combined
with the 30-a-side result above (rough training helps on `dummy_eval_hard`'s
kind of difficulty, not on chaired12's), the two most concrete hypotheses
raised for chaired12's misses -- harder training semantics, and no context
window -- have both now been tested directly and both came back negative.
Posted to #323: whatever chaired12 is actually missing on, it is neither of
the two things this experiment and the 30-a-side one were built to test, and
it does not look like a data-authoring or architecture problem addressable by
kind of training/what the classifier can literally see. What is left
untested: whether ±2 is simply too narrow a window (a wider one was not run,
since the gain here is already indistinguishable from noise) and whether
chaired12's difficulty is a property of the specific 12 AI Hub meetings
sampled into it rather than of decisions-in-context generally.

## Result (2026-09-23) — a third hypothesis, targeted register additions, also does not transfer

A different line from the two above: not "harder dummy data in general" (rough20/30)
and not "give the classifier a context window" (ctx30), but two narrow, specific
register gaps found by manually running `share_s20260910` against a hand-written
test meeting outside `extraction_eval*` (`2.txt`, not part of training or eval):

1. **Hedged/indirect commitments** — a promise phrased as a soft prediction
   ("...10월 1일까지는 봐야 할 것 같습니다") rather than a direct "~하겠습니다"/
   "~할게요". `share_s20260910` missed this entirely (`none`, 0.99 confidence).
2. **Decision-shaped-but-personal compound sentences** — a conditional clause
   ("~되면", "~하고 그때 ~하면") followed by the speaker's own commitment, with no
   new group decision actually settling in the row. `share_s20260910` mislabelled
   two such sentences `decision` instead of `commitment`.

`DUMMY_131` (one meeting, 260 rows, 5 decisions/13 commitments weighted toward
these two patterns) was written and a 1-seed pilot (`share_plus131`, seed
20260910 only) came back mixed: chaired12 decision F1 rose (0.205→0.222) but
commitment F1 — the metric this was aimed at — fell more (0.286→0.203). Scaled
to ten meetings (`DUMMY_131`-`140`, `share_plus10`, same two patterns, varied
phrasing, no template reuse) and run properly at three seeds (20260910/16/17,
same as every comparison above) to separate signal from the ~0.03 seed noise
floor this project has measured before.

**`aihub_chaired12`, macro F1 / decision F1 / commitment F1:**

| seed | share (baseline) macro5 | share decision F1 | share commitment F1 | share_plus10 macro5 | share_plus10 decision F1 | share_plus10 commitment F1 |
| --- | --- | --- | --- | --- | --- | --- |
| 20260910 | 0.323 | 0.205 | 0.286 | 0.315 | 0.201 | 0.254 |
| 20260916 | 0.338 | 0.232 | 0.333 | 0.309 | 0.103 | 0.325 |
| 20260917 | 0.324 | 0.195 | 0.239 | 0.277 | 0.155 | 0.148 |
| **mean** | **0.328** | **0.211** | **0.286** | **0.300** | **0.153** | **0.242** |

**`aihub_blind1` macro F1 and `dummy_eval_hard` macro F1 / decision F1 / commitment F1:**

| | share blind1 | share_plus10 blind1 | share hard macro5 | share_plus10 hard macro5 | share hard decision F1 | share_plus10 hard decision F1 | share hard commitment F1 | share_plus10 hard commitment F1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260910 | 0.250 | 0.386 | 0.631 | 0.678 | 0.685 | 0.648 | 0.815 | 0.842 |
| 20260916 | 0.282 | 0.288 | 0.610 | 0.684 | 0.649 | 0.717 | 0.802 | 0.831 |
| 20260917 | 0.339 | 0.280 | 0.640 | 0.690 | 0.630 | 0.652 | 0.828 | 0.854 |
| **mean** | **0.290** | **0.318** | **0.627** | **0.684** | **0.655** | **0.672** | **0.815** | **0.842** |

The exact `rough30` shape again: `dummy_eval_hard` favours `share_plus10` on
every seed, on both decision and commitment F1 (macro5 mean 0.627→0.684).
`blind1` moves up on mean but is noisy and inconsistent per seed. On
`chaired12`, the part this whole line of work is about, `share_plus10` loses
on every metric that matters: macro5 mean 0.328→0.300, and **decision F1 falls
from 0.211 to 0.153 — the opposite of the 1-seed pilot's direction** (0.211
was itself already close to the pilot's post-training 0.222; the pilot's
apparent gain did not survive going from one seed to three). Commitment F1
confirms the pilot's finding at the same rough magnitude (0.286→0.242, pilot
was 0.286→0.203). `share_plus10`'s worst chaired12 decision F1 seed (0.103) is
also its best (0.201) sits below `share`'s worst seed (0.195) — the separation
is not just a mean artifact of one bad seed.

**The 2.txt three sentences, checked against all three `share_plus10` seeds:**

| Sentence | 910 | 916 | 917 |
| --- | --- | --- | --- |
| 박재경 hedged commitment | none (unfixed) | none (unfixed) | none (unfixed) |
| 문민재 compound ("온보딩 확정되면...") | commitment 1.00 (fixed) | commitment 1.00 (fixed) | commitment 0.81 (fixed) |
| 김민경 compound ("...출시일 조정 논의하겠습니다") | decision 1.00 (unfixed) | decision 1.00 (unfixed) | decision 0.99 (unfixed) |

This part is stable across all three seeds, not seed noise: one of the two
compound-sentence cases is reliably fixed regardless of seed, the hedged
commitment is reliably *not* fixed in any of ten meetings' worth of direct
exposure across three seeds, and the other compound case is reliably not
fixed either.

**Conclusion:** does not transfer, and going from one meeting to ten made the
aggregate chaired12 numbers worse, not just "still not proven." The reading
that best fits both the qualitative and quantitative results together: this
training addition teaches the model a genuinely learnable, stable fact (one
specific compound-sentence shape resolves to `commitment`), which is real and
reproduces across seeds, but it does not teach the hedged-commitment register
at all even directly exposed to it, and whatever the net effect on chaired12
is, it is negative on the metric this project measures the classifier by
(ADR 0006's macro F1) rather than neutral. Combined with `rough30`
(register/hardness training helps `dummy_eval_hard`, not chaired12) and
`ctx30` (context window helps neither), this is now a third targeted
training-data intervention that improves the specifically-authored-hard
synthetic part while not helping, and here actively hurting, the real-speech
part the product ships against. The pattern across all three: **whatever
`aihub_chaired12` is missing on is not being reached by changing what
training data looks like, in three different specific ways tried so far.**
