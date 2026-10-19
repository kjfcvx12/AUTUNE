# Dummy team meetings (2026-09-17)

Ten invented Korean workplace meetings, ~30 minutes each, shaped like Autune's target:
no chair, a lead and members, two teams, or a senior in the room. Authored to
`SPEC.md` by ten parallel agents, one per meeting. Everything is invented.

| Meeting | Type | Speakers | Rows | decision | commitment | ambiguous | concern | open_question |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DUMMY_01 app dev sprint | team | 6 | 307 | 8 | 25 | 7 | 11 | 38 |
| DUMMY_02 planning × dev | cross-team | 7 | 277 | 8 | 12 | 4 | 13 | 28 |
| DUMMY_03 marketing campaign | team | 5 | 269 | 7 | 15 | 6 | 12 | 29 |
| DUMMY_04 design rebrand | team | 5 | 267 | 6 | 16 | 5 | 14 | 28 |
| DUMMY_05 sales review + 본부장 | with-senior | 6 | 293 | 10 | 19 | 5 | 13 | 38 |
| DUMMY_06 outage postmortem | cross-team | 6 | 310 | 11 | 25 | 6 | 12 | 36 |
| DUMMY_07 HR × GA workshop | cross-team | 6 | 298 | 10 | 21 | 5 | 13 | 34 |
| DUMMY_08 analysts, no lead | peers | 5 | 280 | 8 | 17 | 5 | 12 | 37 |
| DUMMY_09 flat startup + CEO | with-senior | 6 | 282 | 9 | 16 | 6 | 13 | 27 |
| DUMMY_10 multi-team kickoff | cross-team | 8 | 281 | 10 | 19 | 4 | 11 | 31 |
| **Total** | | | **2,864** | **87** | **185** | **53** | **124** | **326** |

`none` is 71–77% per meeting.

Files per meeting: `speakers.json` (team, job, 직위, 직책, company position order),
`A.csv` (unlabelled), `C.csv` (author labels, a reason in `note` for every non-none row,
tags `상급자` / `상기` / `전달`). `python validate.py` re-checks everything independently of
the authors' own checks (format, A = C text, timing, label structure, minimum cases,
상급자 decisions spoken by the most senior person present, peers meeting has none):
0 problems at creation.

**The labels are planted, not gold.** Dialogue and labels come from the same author, so
the labels match the author's reading of the rules exactly. Use this set for format and
pipeline smoke tests and for "does the model pick up the rule at all"; treat model
scores on it as optimistic until a person reviews the C sheets (`review.html` pre-fills
C drafts in Review mode). Cases worth a human look: a speaker taking a task inside a
summary ("그럼 … 제가 금요일 오전에 넘기는 걸로 하겠습니다") is labelled decision.

## DUMMY_11–30 (2026-09-18) — written as training data

Twenty more, ten agents with two meetings each, to `SPEC.md` plus its addendum (closing
cue on at most 1 in 3 decisions; cues also on non-decision rows). The first ten put a cue
on 75% of decisions (65/87); 11–30 put one on 24% (40/165), near the ~21% of real
human-confirmed Korean decisions. `validate.py` now checks every `DUMMY_??` present: 30
meetings, **8,478 rows** (decision 252, commitment 564, ambiguous 128, concern 331,
open_question 987, none 6,216), 0 problems.

11 game live-ops (team) · 12 hospital 원무×의료정보 (cross-team) · 13 logistics centre +
센터장 (with-senior) · 14 fintech compliance×product (cross-team) · 15 생산×품질 defects
(cross-team) · 16 edtech content, lead on leave (peers) · 17 retail region + 지역장
(with-senior) · 18 public SI client×vendor (cross-team) · 19 SaaS CS renewals (team) · 20
legal×sales contract (cross-team) · 21 construction site (team) · 22 research lab +
책임연구원 (with-senior) · 23 F&B menu launch, three teams (cross-team) · 24 security
incident (team) · 25 data platform migration (cross-team) · 26 ad agency pitch (team) ·
27 budget + CFO (with-senior) · 28 app release go/no-go (cross-team) · 29 recruiters
(peers) · 30 hardware startup, flat titles + CEO (with-senior).

**All thirty are in the training split `v4`**
(`dataset/experiments/2026-09-18-dummy-train/`), so none of them is an evaluation set for
models trained there. Evaluation is the user's review of real meetings.
