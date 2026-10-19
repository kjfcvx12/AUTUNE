# Dummy team meetings — authoring spec

Ten invented Korean workplace meetings, about 30 minutes each, shaped like the meetings
Autune is built for: **no chair**, a team lead and members, sometimes two teams or a senior
manager in the room. They exist because every real Korean set we have (AI Hub #464) is
chaired, and the classifier learned "a chair's register means decision".

Everything is invented: people, companies, products, numbers. No real person or company
names. This is team-authored data, not AI Hub data.

## What each meeting must look like

- **Length:** 260–340 rows. The last row's `start` is between 1,700 and 1,850 seconds.
  `start` increases, with realistic gaps (1–15 s; longer after a long turn).
- **A row is one ASR segment**, not one turn: a sentence, or a clause of a long sentence.
  Split long turns into 2–4 rows. Sometimes a sentence is cut across two rows
  ("그 부분은 제가 다음 주까지" / "정리해서 올릴게요").
- **Speech, not prose.** Backchannels ("네.", "음.", "그렇죠.", "아 네네"), fillers ("그 뭐지",
  "어"), self-corrections, trailing fragments, people talking over each other, a little
  off-topic talk at the start or end, numbers and dates said the way people say them
  ("다음 주 수요일", "한 삼천 정도"). Honorific office Korean ("~씨", "~님", "팀장님").
- **4–8 speakers.** No one runs the meeting formally. The lead may steer, but there is no
  "안건 상정", "의결", "선포".
- **About 75% of rows are `none`.** Most talk is explaining, reacting, filler.

## Files to write

In `F:\0final\AUTUNE\dataset\team_dummy\`, for meeting `DUMMY_NN` (NN given in your task):

1. `DUMMY_NN.speakers.json`
   ```json
   {"meeting": "DUMMY_NN", "title": "...", "type": "team | cross-team | with-senior | peers",
    "position_order": ["사원", "주임", "대리", "과장", "차장", "부장", "이사", "대표"],
    "speakers": [{"speaker": "SPK01", "name": "...", "team": "...", "job": "Dev",
                  "position": "과장", "title": "팀장"}]}
   ```
   `position` is 직위/직급; `title` is 직책 (팀장, 파트장, 본부장, 리드, or "" for none).
   If the company is flat (매니저/프로 for everyone), put its own order in
   `position_order` and use `title` to show who leads.
2. `DUMMY_NN.C.csv` — the meeting with your labels.
3. `DUMMY_NN.A.csv` — identical, but `kind`, `decision_id`, `settles`, `responds_to`, `note`
   blank.

CSV columns, in order, UTF-8 **with BOM**, quoted properly (use Python's `csv` module — do
not hand-write CSV; commas and quotes in Korean text will break it):

`row, utterance_id, start, speaker, role, text, kind, decision_id, settles, responds_to, note`

- `row`: 1, 2, 3 … ; `utterance_id`: `DUMMY_NN-0001` …; `start`: seconds with 2 decimals
- `speaker`: `SPK01` …; `role`: the speaker's `job` (PM, Dev, Design, Data, QA, Marketing,
  Sales, Ops, HR …). **Never `사회자`.**

## Labels — follow these exactly

`kind` is one of `commitment`, `decision`, `open_question`, `concern`, `ambiguous`, `none`.
Label **the row where the sentence ends**; earlier fragments of the same sentence are `none`.
If several kinds fit: `decision > concern > open_question > ambiguous > commitment > none`.

| Kind | Meaning |
| --- | --- |
| `commitment` | The speaker takes a task on (with or without a deadline), states their own plan, **or recalls** an earlier decision/commitment (`note`: `상기`) |
| `decision` | The meeting settles something — what, and possibly **who and by when**; a deferral/hold; a conditional "하기로"; **a superior's proposal nobody answers** (`note`: `상급자`) |
| `open_question` | Asks others for information, an opinion, or an action |
| `concern` | Objection or problem raised against something said (`responds_to` required; unprompted risk → blank `responds_to`, `note`: `unprompted`) |
| `ambiguous` | Weak assent ("검토해 보겠습니다", "한번 볼게요" with nothing concrete), **or relaying what another team will do** (`note`: `전달`) |
| `none` | Everything else, including an estimate with a number ("예산은 한 오천 정도 예상돼요"), a peer's proposal nobody takes up, backchannels |

Decision regions: rows of the discussion that led to a decision share `decision_id`
(`D1`, `D2` … in order). `settles = 1` only on the row that states what was settled, and
only that row has `kind = decision`; other rows in the region keep their own kind.
`responds_to` = row number, required on `concern` and `ambiguous` (except unprompted /
전달) and on a `commitment` that accepts a request.

**Write a short Korean reason in `note` for every non-`none` row** (plus the tags above), e.g.
`상급자 제안, 이후 반대 없음` or `본인이 기한 명시하고 맡음`.

## Content each meeting must contain

At least: 5 decisions — including ≥1 lead/superior proposal nobody answers, ≥1 group
summary after discussion, ≥1 deferral/hold, ≥1 conditional decision, ≥1 where the meeting
assigns who/when. 7 commitments — including ≥1 without deadline ("제가 알아볼게요"), ≥1
own plan ("-보려고요"), ≥1 recall (`상기`). 3 ambiguous — including ≥1 `전달` if another
team exists in the story. 4 concerns. 8 open questions. ≥1 peer proposal nobody takes up
(`none`). ≥1 number estimate (`none`).

**Make it hard, like real speech:**
- Decisions ending in "-겠습니다" and commitments ending in "-는 걸로 하죠" both occur.
- Some decisions are implicit (summary + moving on), not keyword-marked.
- The lead also says plenty that is not a decision.
- A request to someone ("민수 씨가 좀 봐 줄래요?") is `open_question`; the acceptance is the
  `commitment`.
- A few "네" replies after a proposal, but not after every one.

## Check before you finish

Run a Python check and fix anything it finds: row count 260–340; last `start` 1,700–1,850;
starts increasing; A and C identical except the label columns; every `responds_to` points to
an earlier row; `settles` only on `decision` rows and every `decision` row has
`settles = 1` and a `decision_id`; no `사회자`; required content counts met; `none` share
65–85%. Report the label counts and the check result — nothing else.

## Addendum for DUMMY_11 onward (2026-09-18) — training data

These meetings go into the **training set**, so a shortcut in the writing becomes a
shortcut in the model. The first ten put a closing cue (-기로 하-, -하죠, -합시다, -겠습니다,
-걸로) on 75% of decisions; real human-confirmed Korean decisions carry one about 21% of
the time, and a model trained on cue-heavy decisions learned "a decision is a sentence
with a closing cue" (synthetic v5, 2026-09-16). So:

- **At most 1 in 3 decisions carries a closing cue.** The rest settle implicitly: a
  summary that restates the choice ("그럼 A안, 배포는 화요일."), a lead's plain statement
  ("이번엔 인기순으로 가요." / "그건 다음 분기로 넘기고."), a nominal or cut-off ending, a
  choice confirmed by moving on to the next topic, "그 방향이면 될 것 같네요" after
  agreement.
- **Closing cues also appear on non-decision rows**, as often as on decisions: a peer's
  "-하죠" proposal nobody takes up (`none`), "제가 하겠습니다" (`commitment`),
  "검토해 보겠습니다" (`ambiguous`), "그렇게 하죠" as a backchannel to someone else's
  commitment (`none`).
- **Commitments** vary too: "제가 볼게요", "그건 제 쪽에서", "금요일까지 올려 둘게요",
  "제가 해 보려고요" — not all "-겠습니다".
- Everything else in this spec is unchanged (rows, timing, labels, minimum content,
  C/A/speakers files, BOM, csv module).
- Your own check script goes in the scratch folder named in your task, **never** in
  `team_dummy/` or a shared path. Add one check: count decisions whose text matches
  `기로 하|하죠|합시다|갑시다|봅시다|겠습니다|겠어요|걸로` and keep it ≤ 33%.

## Addendum for DUMMY_101 onward (2026-09-21) — write speech, not a script

Measured on 2026-09-21: the first hundred meetings and real Korean meeting speech
(AI Hub #464, 3,512 rows) differ less in what is said than in **how the talk is
laid out**.

| | first 100 dummy | AI Hub |
| --- | --- | --- |
| characters per row (median) | 22 | **45** |
| rows continuing the same speaker | 21% | **61%** |
| fillers per 100 characters | 0.9 | **2.4** |
| self-corrections per 100 characters | 0.08 | **0.14** |

The last two are counted per character, not per row: a long row has more chances
to contain a filler, so counting rows made real speech look three times as
disfluent as it is and let an author pass by putting "어" in front of every
sentence. `register_check.py` counts occurrences.

The dummy meetings are ping-pong: a short line, a new speaker, a short line, a new
speaker. Real meetings are somebody holding the floor for three, four, five rows,
circling back, correcting themselves, while the others say almost nothing. A model
trained on ping-pong learns that an act sits in a short clean line of its own; then
a real decision arrives buried in a person's fourth sentence in a row and it is
missed. This is the largest measured gap we have, and closing it is the only reason
to write more meetings — more of the old kind changed nothing (v4 30 meetings vs v5
100 meetings: dummy macro F1 0.810 vs 0.807).

So, for these meetings:

- **A turn is 3–6 rows, not 1.** One person keeps talking: sets up the problem,
  gives a number, qualifies it, then lands the point. Two speakers alternating
  row-by-row should be rare, and only in a quick exchange.
- **A row is 30–60 characters** — a whole thought, often two clauses joined with
  `-는데`, `-고`, `-니까`. Not a headline.
- **Fillers belong inside rows**, not only as standalone "음." rows: "어 그러니까
  이게", "뭐 일단은", "그 저희가 이제", "약간 좀 애매한데". About one filler per
  40 characters — in a 45-character row, roughly one. Vary them: 그, 뭐, 이제,
  일단, 좀, 약간, 그냥, 저기, 그러니까, 어쨌든. Opening every sentence with "어"
  hits the old row-based number and fails this one.
- **People correct themselves**: a wrong number then the right one, a name then the
  right name, "아니 그게 아니라" restarting a sentence. About one per 700
  characters — once every fifteen rows or so.
- **The act still lands at the end of a sentence**, and now that sentence is often
  the fourth row of somebody's turn — which is exactly the case the model needs.
  Label the row where it ends, as before.
- Everything else is unchanged: 260–340 rows, timing, the 09-17 label rules, the
  09-18 closing-cue limit (≤ 1 decision in 3), C/A/speakers files, BOM, csv module.

**Check before you finish:** the usual checks, plus `python register_check.py
DUMMY_NN` from this folder — every band must pass. Report its output.

## Addendum for DUMMY_101 onward (2026-09-21b) — make it hard to *read*, not just to hear

The register addendum above fixes how the talk is laid out. This one fixes what
the reader has to work out. A meeting can pass all six register bands and still be
trivial, because every act is stated plainly, every deadline is spelled out and
nobody ever changes their mind.

`register_check.py` measures the surface. **`hard_check.py` measures this**, and
both must pass. Run `python hard_check.py DUMMY_NN`.

### What every meeting must contain

- **Pointing instead of naming.** "그거 저번에 말한 대로 가죠", "김 대리가 말한
  그 분한테". At least ten rows where the referent is only recoverable from
  earlier talk. The pilots reach forty without trying — this is the easy one.
- **Being cut off.** At least three rows where somebody cuts in: "잠시만요",
  "잠깐만요", "그건 아닌데", "아 그게 아니고". Separately, at least six turns that
  break off mid-sentence and are taken over by another voice. The act often lands
  on the second attempt.
- **Side talk.** At least two stretches of three or more rows on something
  unrelated — a server that fell over, snacks, someone's commute — **in the middle
  of the meeting**, not only at the ends, and returning naturally to the topic.
  Tag every such row `note = 사담` (a `none` row may carry a note; only non-`none`
  rows are *required* to).
- **A false agreement.** At least once, the room appears to settle — "그럼 그렇게
  하죠!" — and the very next turn overturns it: "아 맞다, 그거 안 돼요." The
  apparent settling row is **`none`**, not `decision`; the real decision comes
  later and is the one that carries `settles = 1`. Tag the overturned row
  `note = 번복`. This is the single most valuable row in the file: it is exactly
  the shortcut the model has learned and must unlearn.
- **A task nobody wants.** Something is thrown at a team rather than a person —
  "이건 개발 쪽에서 알아서 해주세요" — and somebody eventually takes it on
  reluctantly: "아... 예... 일단 제가 볼게요". Tag the reluctant row
  `note = 위임`. Its kind is `ambiguous` when nothing concrete is promised,
  `commitment` when something is.
- **Resistance before every decision.** Every decision region carries at least one
  `concern` or `ambiguous` row **before** its settling row. Nothing is agreed
  unopposed, because nothing real is.
- **Deadlines you have to work out.** At least half the decisions do not state
  their deadline in the settling row, and at least one deadline is relative to
  something else that must be resolved first: "저번 회의 때 말한 날짜보다 이틀
  앞당겨서", "그 기획서 나오기 이틀 전까지". Owners too — "그럼 지영 씨가 저번처럼
  해주세요" names a person but not the task, and the task is three turns back.

### Fewer people is allowed now

Three speakers is a legitimate meeting and a hard one — with three people there is
no chair even by accident. `validate.py` accepts 3 to 8.

### Why these five things

The classifier's measured failure is decisions: on real speech it finds about a
quarter of them. Every rule above attacks one reason for that. Pointing and
relative deadlines break the slot filler. Being cut off moves the act off the row
a reader would guess. Side talk punishes treating every row as business. The false
agreement punishes "closing cue means decision", which is the shortcut the first
ten meetings taught it. And resistance before settling is what a real decision
looks like from the outside.

## Addendum 2026-09-21c — every meeting ships an answer key, `DUMMY_NN.D.csv`

`settles = 1` marks the row where a decision lands. In the meetings written to the
two addenda above, **that row is not readable on its own**: "그럼 그 방향으로
가시죠" says nothing without the ten rows before it, the owner was named three
turns earlier and the deadline is relative to another date. The row is evidence,
not an answer.

So each meeting also ships a summary of what was actually decided — the thing a
person would write in the minutes, and the thing module B is supposed to produce.

**`DUMMY_NN.D.csv`**, UTF-8 with BOM, `csv` module, columns in this order:

`decision_id, settles_row, statement, owner, due, due_as_said, evidence_rows, note`

| Column | What goes in it |
| --- | --- |
| `decision_id` | `D1`, `D2` … matching the `decision_id` in the `.C.csv` |
| `settles_row` | the `row` number carrying `settles = 1` |
| `statement` | **one Korean sentence saying what was settled**, readable with no other context. Not a copy of the row's text |
| `owner` | who is on the hook — the `speaker` id (`SPK03`). Blank if the meeting genuinely left it open |
| `due` | the deadline resolved to something absolute where the talk allows it ("2026-10-02"), else the clearest form you can state. Blank if there is none |
| `due_as_said` | how it was actually said: "이번 주말 전까지", "저번에 말한 날짜보다 이틀 앞당겨서". Blank if no deadline was mentioned |
| `evidence_rows` | every row a reader needs to reconstruct this, comma-separated, including the rows carrying the owner and the deadline. Not just `settles_row` |
| `note` | Korean, one line: how it was settled, and anything a labeller should know |

Rules `hard_check.py` enforces:

- one row per settled decision in the `.C.csv`, no more and no fewer
- `statement` is **not** the settling row's text, and is 15–120 characters
- at least half the decisions name an `owner`
- at least half the decisions have a `due`
- any decision whose owner or deadline is not inside the settling row lists at
  least one other row in `evidence_rows`

The same file is required for evaluation meetings (`EVALH_NN.D.csv`), where it is
the gold answer for owner and deadline — the project has never had one, so slot
filling has never been scored.
