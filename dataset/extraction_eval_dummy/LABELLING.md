# Second labelling — the rules, and nothing else

You label a meeting you did not write, from `<id>.A.csv` alone. Do not open
`<id>.C.csv`; it holds the author's labels, and the whole point of this pass is
that two readings are independent. Write `<id>.L2.csv`.

`merge_gold.py` then keeps the rows where the two of you agree. The rest are not
scored — a row two careful readers disagree on is not something a model should be
graded on without a person settling it.

## The six kinds

Label **the row where the sentence ends**. Earlier fragments of the same sentence
are `none`. If several fit: `decision > concern > open_question > ambiguous >
commitment > none`.

| Kind | Meaning |
| --- | --- |
| `commitment` | The speaker takes a task on (with or without a deadline), states their own plan, or **recalls** an earlier decision/commitment |
| `decision` | The meeting settles something — what, and possibly who and by when; a deferral or hold; a conditional "하기로"; **a superior's proposal nobody answers** |
| `open_question` | Asks others for information, an opinion, or an action |
| `concern` | An objection or a problem raised against something said; an unprompted risk counts |
| `ambiguous` | Weak assent ("검토해 보겠습니다", "한번 볼게요" with nothing concrete), or relaying what another team will do |
| `none` | Everything else: backchannels, explaining, an estimate with a number ("한 오천 정도 예상돼요"), a peer's proposal nobody takes up |

The boundary that decides most rows (agreed 2026-09-17): **who settled it.**

- The meeting fixing what happens — including who and by when — is a `decision`.
- A team lead or a senior proposing and nobody answering is a `decision`.
  A peer proposing and nobody answering is `none`.
- A deferral ("다음 회의에서 다시 보죠") and a conditional ("예산 나오면 진행하죠")
  are `decision`s.
- Volunteering ("제가 알아볼게요"), with or without a deadline, is a
  `commitment`; so is stating your own plan.
- A closing cue (`-기로 하-`, `-하죠`, `-겠습니다`) is **not** what makes a
  decision. Many decisions here have none, and many non-decisions have one.

## What to write

Fill `kind` on every row (`none` included). Leave `decision_id`, `settles`,
`responds_to` and `note` empty — the merge takes those from the author's sheet
for the rows you agree on, and clears them where you do not.

Keep the file identical to `<id>.A.csv` otherwise: same rows, same order, same
`row`/`utterance_id`/`start`/`speaker`/`role`/`text`, UTF-8 with BOM, written with
Python's `csv` module.

## Before you finish

Check, and say the numbers in your reply:

- every row has a `kind`, and every `kind` is one of the six
- row count and every `text` match `<id>.A.csv` exactly
- your label counts, and your `none` share
