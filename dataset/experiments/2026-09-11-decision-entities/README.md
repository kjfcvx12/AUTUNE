# 2026-09-11 — decisions as D reads them: entities, not utterances

`entity_eval.py` (CPU, counts only). Natural test set: the 7 decision-annotated
test meetings, 5,237 acts, **35 gold decisions** (AMI `decision/manual` regions;
median 21 acts each, max 67). Predicted entities are `group_decisions` over
per-act labels. Match = shared acts ≥ half of the smaller set (strict) or ≥ 1
(lenient).

## Current pipeline (max_gap 2)

| Labels | Entities (gold 35) | Strict P / R / F1 | Lenient P / R / F1 | Acts per entity (median) |
| --- | --- | --- | --- | --- |
| model (official 6-way) | **480** (~69 per meeting) | 0.18 / 0.91 / 0.30 | 0.19 / 0.97 / 0.32 | 2 |
| oracle (gold per-act labels) | 55 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 7 |

## Grouping knobs alone (`sweep`)

Model labels, strict: precision stays 0.11–0.20 for every gap ∈ {2, 5, 10} and
minimum size ∈ {1, 3, 5}; fewer entities only costs recall. Best F1 0.31 (gap 5,
min 3, 131 entities). Oracle labels: gap 2 fragments 35 decisions into 55, gap 5
merges them into 24 — no gap does neither.

## Reading

- D receives ~69 decisions per meeting, ~81% of them false. The false ones come
  from the classifier putting `decision` on none acts across the meeting (59% of
  all false labels, see ../2026-09-11-official-6way), not from how runs are joined.
- Even perfect per-act labels do not give the right entities with a fixed gap: a
  decision is a region of ~21 acts in which only the assertive acts carry the
  label.
- So the per-utterance framing is the problem (#149 point 3): detect the region
  (where), then pick the settling act inside it (what).
