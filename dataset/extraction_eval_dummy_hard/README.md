# The hard dummy evaluation set (2026-09-21)

Eight invented no-chair meetings written to `team_dummy/SPEC.md`'s **2026-09-21
register addendum**: turns of three to six rows, rows of thirty to sixty
characters, a filler in about a third of rows, a self-correction in about one row
in seventeen. `team_dummy/register_check.py` is the acceptance check and every
meeting here passes every band.

Nothing here is training data.

## Why a second dummy evaluation set

The first one (`../extraction_eval_dummy`, 12 meetings) is the cleanest text the
project holds — cleaner than the training data it was meant to judge:

| | median chars | ends a sentence | same speaker as previous row |
| --- | --- | --- | --- |
| dummy training meetings | 22 | 43.7% | 20.0% |
| **the first dummy eval set** | **15** | **53.8%** | **14.3%** |
| AI Hub, real speech | 45 | 45.3% | 60.6% |

An exam that easy stops telling models apart: the 30-meeting and the 100-meeting
checkpoints score 0.810 and 0.807 on it, which is one number, not two. And every
act in it lands in a short clean line of its own, so it never asks the question
the product actually faces — a decision buried in the fourth row of somebody's
turn.

It stays where it is, unchanged, so the numbers already reported against it remain
comparable. This set is the one to read from now on.

## What it is for, and what it is not for

It is the closest proxy the project has to **the product's real input**: Korean
team meetings with no chair, spoken the way people speak. AI Hub cannot fill that
role (every meeting has a chair) and the first dummy set cannot (it is not speech).

It is **not** the place to settle whether the register rewrite worked. The
training meetings from DUMMY_101 on are written to this same addendum, so a model
trained on them matches this set's style for free. That comparison —
`clean30` against `rough30` — is settled on `aihub_chaired12`, which neither model
was written toward. See `experiments/2026-09-21-rough-dummy/README.md`.

## Labels

Same protocol as the first set: the author labels the meeting, a second labeller
who has seen only `<id>.A.csv` labels it again, and `merge_gold.py` keeps the rows
where the two agree. The rest become `disagreement` and are scored by nobody.

    python ../extraction_eval_dummy/merge_gold.py .
    python ../extraction_eval_dummy/validate_eval.py .

The second labeller's rules are `../extraction_eval_dummy/LABELLING.md`.

## Result (2026-09-22)

All eight meetings, both labelling passes, done. `merge_gold.py`:

| meeting | rows | agreed | share | kappa |
| --- | --- | --- | --- | --- |
| EVALH_01 | 276 | 242 | 87.7% | 0.743 |
| EVALH_02 | 279 | 258 | 92.5% | 0.804 |
| EVALH_03 | 340 | 305 | 89.7% | 0.773 |
| EVALH_04 | 294 | 267 | 90.8% | 0.786 |
| EVALH_05 | 280 | 245 | 87.5% | 0.663 |
| EVALH_06 | 284 | 264 | 93.0% | 0.810 |
| EVALH_07 | 300 | 280 | 93.3% | 0.809 |
| EVALH_08 | 270 | 237 | 87.8% | 0.732 |

**2323 rows total, 2098 agreed (90.3%) — the scored rows.** Kappa ranges 0.663
(EVALH_05) to 0.810 (EVALH_06); every meeting lands in substantial-to-near-perfect
agreement (Landis & Koch bands), none in the range that would call the label
definitions themselves into question.

Disagreement pairs, most to least common: `concern vs none` 87, `none vs
open_question` 48, `commitment vs none` 32, `decision vs none` 25, `ambiguous vs
none` 14, `concern vs open_question` 9, `ambiguous vs commitment` 5, `ambiguous vs
concern` 4, `commitment vs open_question` 1. The shape is what the spec's own
harder rules predict: most misses are one labeller reading an implicit act
(`concern`, `open_question`) where the other read plain narration (`none`) — the
"resistance before every decision" and "pointing instead of naming" rules ask a
reader to catch acts that never announce themselves, and two independent readings
sometimes catch a different subset. `decision vs none` (25) is mostly the
false-agreement rows every meeting carries at least one of: the row that looks
like a settling statement until the very next turn reopens it, which the label
rules place on the *later* row and which a first read can miss on a pure
skim.

Label counts, `validate_eval.py` over the merged set (author's C.csv, the scored
rows): 51 `decision`, 156 `commitment`, 195 `open_question`, 100 `concern`, 32
`ambiguous`, 1789 `none`, out of 2323 total rows.

`*.G.csv` (the merged gold, `disagreement` on the unscored rows) is written
alongside `*.A/C/D.csv` and `*.L2.csv` for each meeting, and is not registered as
a separate part — a scorer reads it directly from this folder once `parts.json`
points here.
