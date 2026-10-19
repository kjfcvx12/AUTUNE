# Evaluation-only team meetings (2026-09-21)

Invented Korean workplace meetings with **no chair**, written to
`../team_dummy/SPEC.md` and its addendum. They exist because the 100 meetings in
`team_dummy/` are now training data (`experiments/2026-09-18-dummy-train`), which
left the project with no evaluation set shaped like its target: a team meeting in
Korean with no 사회자.

**These never go into a training split.** The builders glob `team_dummy/DUMMY_??`;
this folder is outside that path on purpose, and no split may read it.

## Why the labels are not the author's

A meeting whose dialogue and labels come from one writer scores optimistically:
the labels match that writer's reading of the rules exactly. Here the two are
split.

1. An author writes the meeting and labels it (`.C.csv`).
2. A **different** labeller sees only the unlabelled sheet (`.A.csv`) and the
   rules, and labels it blind (`.L2.csv`).
3. `merge_gold.py` keeps the rows where the two agree as the gold set
   (`.G.csv`), and records the rest as disagreements rather than deciding them.

A score is therefore reported on rows two independent readings agree on, with
the agreement itself (Cohen's kappa) and the coverage stated beside it. Rows they
disagree on are the ones a human reviewer should settle; until then they are not
scored.

## Files per meeting

| File | What |
| --- | --- |
| `<id>.A.csv` | the meeting, label columns blank |
| `<id>.C.csv` | the author's labels |
| `<id>.L2.csv` | the second labeller's, written without seeing `.C.csv` |
| `<id>.G.csv` | gold: rows both agree on, others marked `disagreement` |
| `<id>.speakers.json` | speakers, teams, 직위/직책 |
