# Auto queue — dataset and evaluation-set work done in off hours

`run_auto.ps1` starts one headless Claude run per slot; each run takes the **first
unchecked unit that is not BLOCKED**, does it, ticks it, and appends one line to
`LOG.md`. Rules for a run are in `PROMPT.md`. Edit this file by hand to add,
reorder, block or unblock work — it is the only control surface.

Marks: `- [ ]` to do, `- [x]` done, `- [~]` tried and left partial (say why in
LOG.md), `BLOCKED:` prefix = skip until a person removes the word.

## Phase 1 — hard dummy evaluation set, author pass (`extraction_eval_dummy_hard/`)

Eight invented no-chair meetings to `team_dummy/SPEC.md` addenda 2026-09-21,
09-21b, 09-21c. A unit is done when `register_check.py`, `hard_check.py` and
`validate_eval.py` all pass for that meeting (A, C, D csv + speakers.json).

- [x] EVALH_01 — exists, partial: make it pass all three checks
- [x] EVALH_03 — exists, partial: make it pass all three checks
- [x] EVALH_02 — write
- [x] EVALH_04 — write
- [x] EVALH_05 — write
- [x] EVALH_06 — write
- [x] EVALH_07 — write
- [x] EVALH_08 — write

## Phase 2 — second labelling (`<id>.L2.csv`), from `<id>.A.csv` ONLY

Rules: `extraction_eval_dummy/LABELLING.md`. The run doing a unit here must not
open that meeting's `.C.csv` or `.D.csv`. Only start a meeting whose Phase 1 unit
is `[x]`.

- [x] L2 EVALH_01
- [x] L2 EVALH_02
- [x] L2 EVALH_03
- [x] L2 EVALH_04
- [x] L2 EVALH_05
- [x] L2 EVALH_06
- [x] L2 EVALH_07
- [x] L2 EVALH_08

## Phase 3 — merge and register

- [x] Run `merge_gold.py` and `validate_eval.py` on `extraction_eval_dummy_hard/`; write agreement %, per-meeting kappa range and label counts into its README; add the part to `extraction_eval/parts.json` only if every meeting in Phase 1 and 2 is `[x]`

## Phase 4 — more rough training meetings (`team_dummy/`, DUMMY_121–130)

The three-seed clean20 vs rough20 comparison did **not** favour rough on
chaired12 (mean macro5 0.345 vs 0.350; decision F1 0.170 vs 0.214, rough behind
on every seed) — see `experiments/2026-09-21-rough-dummy/README.md`'s Result
section. The gate this section originally named is not met.

Unblocked anyway on 2026-09-22 by a person's explicit decision: 20 meetings a
side may be too small a sample for the harder style to show its effect, and
`rough30` against the already-existing `clean30` (same recipe as `v4` from
2026-09-18, rebuilt fresh here for a same-pipeline comparison) tests that
directly, at the same scale the 2026-09-18 experiment already validated isn't
itself the confound. `clean30` split is already built
(`experiments/2026-09-21-rough-dummy/splits/clean30`); DUMMY_121–130 fill out
`rough30`. Same acceptance as DUMMY_101–120, confirmed by running both checks
against DUMMY_101 directly: `register_check.py` **and** `hard_check.py` both
apply (SPEC.md's 09-21b addendum says "Run `python hard_check.py DUMMY_NN`" —
DUMMY, not only EVALH), and a `.D.csv` answer key is required (09-21c says
every meeting ships one; DUMMY_101/110/120 all carry one). `validate_eval.py`
is the eval-set-only script (cross-meeting and training-overlap checks) and
does not apply here — these are the training rows, not a scored set.

- [x] DUMMY_121
- [x] DUMMY_122
- [x] DUMMY_123
- [x] DUMMY_124
- [x] DUMMY_125
- [x] DUMMY_126
- [x] DUMMY_127
- [x] DUMMY_128
- [x] DUMMY_129
- [x] DUMMY_130

## Phase 5 — train and score rough30 vs clean30

Only eligible once every Phase 4 meeting above is `[x]`.

- [x] Build `rough30` (`python build_split.py --name rough30 --meetings 101-130`
  from `experiments/2026-09-21-rough-dummy`), then train 3 seeds
  (20260910/20260916/20260917) and score both `clean30` and `rough30` against
  every `extraction_eval` part the same way `run.sh` did for the 20-meeting
  pair — reuse or extend `run.sh` rather than writing a new script. Report
  chaired12 and blind1 macro F1 and decision F1 per seed into this
  experiment's README, same table shape as the Result section already there.
  Check GPU is free (`nvidia-smi`, must be under 4000 MiB used) before
  starting, same as `run.sh` already does.
  Done 2026-09-22: `run30.sh`/`run30.log`. Gate still not met at 30-a-side
  (chaired12 macro5 0.348 clean vs 0.340 rough, decision F1 0.213 vs 0.184;
  blind1 now favours clean too, reversing the 20-a-side result). New signal:
  `dummy_eval_hard` (didn't exist for the 20-a-side run) favours rough by a
  wide margin on every seed (macro5 0.612 vs 0.769, decision F1 0.691 vs
  0.774) — see README's 2026-09-22b Result section for the full breakdown
  and reading.

## Phase 6 — context=2 vs no-context on `clean30`/`rough30` (#323)

- [x] Build `clean30_ctx2`/`rough30_ctx2` (`build_ctx_split.py --name clean30
  --context 2`, and the same for `rough30`), train 3 seeds and score against
  `chaired12`/`blind1` with `2026-09-17-ensemble-context-llm/score_models.py
  --context 2`, via `run_ctx30.sh`. Report decision F1 and macro5 per seed
  into this experiment's README next to the no-context numbers.
  Done 2026-09-22: `run_ctx30.sh`/`run_ctx30_resume.log`. Context made no
  measurable difference on chaired12 (decision F1 mean 0.213→0.211 clean,
  0.184→0.186 rough; both moves smaller than the seed-to-seed spread) —
  see README's 2026-09-22c Result section. Posted to #323: the
  no-context-window hypothesis is tested and does not explain chaired12's
  miss rate, same negative result as Phase 5's rough-training hypothesis.

## Phase 7 -- #197's date-parsing eval columns (blocked on hand-labelling)

- [ ] BLOCKED: (a person hand-labels AI Hub text; an unattended run can never do this, and every
  run that started for it used up one of the day's slots) `dataset/extraction_eval/scaffold_due_date_eval.py` (new) writes
  `due_date_scaffold/{chaired12,blind1}.due_date_scaffold.csv` -- one row per
  commitment/ambiguous utterance (46 total: 34 chaired12, 12 blind1), blank
  `date_expression`/`gold_due_date`/`note` columns for a human to fill in.
  **Cannot be filled in by Claude**: requires reading AI Hub utterance text
  into judgment about what date it refers to, which the AI Hub data-stays-
  local rule (memory: aihub-data-stays-local.md) puts out of reach in this
  conversation -- counts only ever get read back. Whoever has legitimate
  local access hand-labels the scaffold CSVs directly; once done,
  `slots.py`'s two accepted-limitation rules (#197 #1, #2) get measured
  against it before any rule change, per #197's own plan.

## Phase 8 -- DUMMY_131, targeting two failure patterns found outside this project's own eval sets (2026-09-23)

- [x] Author one training meeting, `DUMMY_131` (`dataset/auto/dummy131_build.py`),
  written after manually running the `share_s20260910` fp16 checkpoint against
  a hand-written test meeting outside `extraction_eval*`. Two concrete misses
  were found there: (1) a hedged/indirect commitment ("~까지는 봐야 할 것
  같습니다" instead of "~하겠습니다") was classified `none`, missed entirely;
  (2) two long compound sentences with a decision-flavoured conditional clause
  ("~되면", "~하고 그때 ~하면") followed by the speaker's own commitment clause
  were mislabelled `decision` even though no group decision was actually being
  made in either sentence. `DUMMY_131` weights 5 commitment rows toward the
  hedged/indirect register and 3 rows toward the compound-conditional-but-
  personal-commitment shape (all labelled `commitment`, per SPEC.md's own kind
  definitions -- no new group settling happens in those rows), on top of every
  other requirement `register_check.py`/`hard_check.py` already enforce.
  `register_check.py DUMMY_131` and `hard_check.py DUMMY_131` both pass (see
  `dataset/auto/LOG.md`). This is **one meeting only** -- not a clean/rough
  matched pair, not part of the rough30 comparison, and no training/scoring run
  was done. Whether this actually improves `aihub_chaired12`/`blind1` decision
  or commitment F1 is untested; a person should decide whether it's worth a
  training+scoring pass (same shape as Phase 5) before spending GPU time on it,
  especially given Phase 5 and 6 both found that a training-data fix for one
  kind of difficulty did not transfer to `chaired12`'s difficulty.

## Phase 8b -- DUMMY_132-140, scaling the Phase 8 set to 10 meetings (2026-09-23)

A 1-seed pilot (`share_s20260910` + `DUMMY_131` alone, see LOG.md's
`Phase8-pilot-share_plus131` entry) came back mixed: `chaired12` decision F1
moved the right direction (0.205 -> 0.222) but commitment F1 -- the metric
this whole effort targets -- moved backward by more (0.286 -> 0.203), and of
the three motivating sentences only one of two compound-conditional cases
flipped correctly; the hedged-commitment case did not move at all. Consistent
with this project's own standing rule (rough20/rough30 needed 10-20 meetings
and 3 seeds before a direction could be trusted over noise), one meeting was
never going to be conclusive.

- [x] Author nine more meetings, `DUMMY_132` through `DUMMY_140`
  (`dataset/auto/dummy132_build.py` .. `dummy140_build.py`, sharing boilerplate
  via the new `dataset/auto/_dummy_common.py`), bringing the targeted set to
  10 total alongside `DUMMY_131`. Same two patterns, weighted higher per the
  pilot's own finding that 5 hedged-commitment rows left zero signal: each new
  meeting carries 5 hedged/indirect commitment rows and 3 compound-conditional-
  personal-commitment rows, phrasing varied meeting to meeting (not the same
  template sentence with nouns swapped) per SPEC.md's closing-cue-overfitting
  reasoning applied to the new patterns. Nine fresh settings, none reused from
  DUMMY_101-131 (online tutoring, apartment community app, fitness equipment
  rental, freelancer matching, meal-kit delivery, elder-care coordination,
  reading subscription box, parking sharing, wedding planning). All ten
  (`DUMMY_131`-`DUMMY_140`) pass `register_check.py` and `hard_check.py`
  together -- see `dataset/auto/LOG.md`.
- [x] Train 3 seeds (20260910/20260916/20260917) on `share_s20260910`'s corpus
  plus all 10 `DUMMY_131`-`DUMMY_140` meetings, score against
  `aihub_chaired12`/`aihub_blind1`/`dummy_eval_hard` via `run_eval.py`, same
  shape as Phase 5. Done 2026-09-23 on the user's explicit go-ahead
  (`build_share_plus10.py`, `runs/share_plus10_s{20260910,20260916,20260917}`):
  does not transfer, and got worse than the pilot suggested -- chaired12
  decision F1 mean 0.211 -> 0.153 (reversing the pilot's single-seed gain),
  commitment F1 mean 0.286 -> 0.242 (confirming the pilot's drop).
  `dummy_eval_hard` favours `share_plus10` on every seed, same shape as
  Phase 5/6. Full tables and reading in
  `experiments/2026-09-21-rough-dummy/README.md`'s Result (2026-09-23)
  section.

## Phase 9 -- ASR-shaped evaluation set (`extraction_eval_asr/`, 2026-09-28)

Why and how: `dataset/extraction_eval_asr/README.md` -- read it first, whole
(it is short). Team-meeting content per `team_dummy/SPEC.md` and its 09-21,
09-21b, 09-21c addenda, then rendered as Whisper + diarization output. A unit
is done when all four checks in that README pass. Each meeting a new setting
not in `LOG.md`.

- [x] ASR_01 — write
- [x] ASR_02 — write
- [x] ASR_03 — write
- [x] ASR_04 — write
- [x] ASR_05 — write
- [ ] BLOCKED: (paused 2026-09-28 by the user — mentor: accuracy work parked) ASR_06 — write
- [ ] BLOCKED: (paused 2026-09-28 by the user — mentor: accuracy work parked) ASR_07 — write
- [ ] BLOCKED: (paused 2026-09-28 by the user — mentor: accuracy work parked) ASR_08 — write

## Phase 9b -- second labelling of ASR_01-08 (`<id>.L2.csv`), from `<id>.A.csv` ONLY

Same rules as Phase 2 (`extraction_eval_dummy/LABELLING.md`; never open that
meeting's `.C.csv`, `.D.csv` or `speakers.json`'s `asr_artifacts`). Only eligible
once the same meeting's Phase 9 unit is `[x]`.

- [ ] BLOCKED: (paused 2026-09-28) L2 ASR_01
- [ ] BLOCKED: (paused 2026-09-28) L2 ASR_02
- [ ] BLOCKED: (paused 2026-09-28) L2 ASR_03
- [ ] BLOCKED: (paused 2026-09-28) L2 ASR_04
- [ ] BLOCKED: (paused 2026-09-28) L2 ASR_05
- [ ] BLOCKED: (paused 2026-09-28) L2 ASR_06
- [ ] BLOCKED: (paused 2026-09-28) L2 ASR_07
- [ ] BLOCKED: (paused 2026-09-28) L2 ASR_08
