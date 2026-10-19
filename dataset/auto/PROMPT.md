# Instructions for one unattended run

You were started by a scheduler with nobody watching. Do **exactly one unit** from
`dataset/auto/QUEUE.md`, record it, and stop. Write everything in English except
the meeting text itself, which is Korean.

## Pick the unit

The first line in `QUEUE.md` that starts with `- [ ]` and does not contain
`BLOCKED:`. A Phase 2 unit is only eligible if the same meeting's Phase 1 unit is
`[x]`; otherwise take the next eligible line. If nothing is eligible, append
`<timestamp> nothing eligible` to `dataset/auto/LOG.md` and stop.

## Hard rules

- **Never open anything under `dataset/002.주요 영역별 회의 음성인식 데이터/`,
  `dataset/한국어 대화 요약/`, `dataset/extraction_eval/`, `dataset/extraction_eval_blind*/`
  or `dataset/extraction_eval_pilot/`.** AI Hub text stays out of every
  conversation. Nothing you write may quote or paraphrase it.
- Write only under `dataset/extraction_eval_dummy_hard/`, `dataset/team_dummy/`
  (Phase 4 only), `dataset/extraction_eval_asr/` (Phase 9/9b only) and `dataset/auto/`. Do not touch code, docs, `HISTORY.md`, or
  anything tracked by git.
- No `git` commands that change anything, no `gh`, no network, no package installs,
  no GPU jobs. No subagents.
- Every person, company and product in a meeting is invented. No real names.
- Keep context narrow: read the part of `team_dummy/SPEC.md` you need (the three
  2026-09-21 addenda and the column definitions), one existing passing meeting as
  a format example (`team_dummy/DUMMY_113.*`), and the files of your own unit.
  Do not read other meetings "for inspiration" — they cost tokens and make the
  new one a copy.
- A Phase 2 unit reads `<id>.A.csv` and `extraction_eval_dummy/LABELLING.md` and
  nothing else about that meeting. Opening its `.C.csv` or `.D.csv` voids the unit.

## Doing a Phase 1 unit

Write or repair `<id>.A.csv`, `<id>.C.csv`, `<id>.D.csv`, `<id>.speakers.json`,
then run from `dataset/`:

    python team_dummy/register_check.py ../extraction_eval_dummy_hard/<id>
    python team_dummy/hard_check.py --dir extraction_eval_dummy_hard <id>
    python extraction_eval_dummy/validate_eval.py extraction_eval_dummy_hard

(`register_check.py` has no `--dir`; it resolves the name relative to
`team_dummy/`, hence the `../`. Read a script's argument handling if one refuses.) Fix what they
report and rerun. **At most four fix rounds.** Vary the setting so the eight
meetings do not share one: different team, product, conflict and deadline shape
each time — `LOG.md` lists what earlier runs used.

## Doing a Phase 9 or 9b unit

Read `dataset/extraction_eval_asr/README.md` first; it names the checks and the
extra files. A Phase 9 unit writes `ASR_NN.A.csv`, `.C.csv`, `.D.csv`,
`.speakers.json` (with `asr_artifacts`) into `dataset/extraction_eval_asr/`
and runs the four checks listed there, same four-round limit. The format
example is still `team_dummy/DUMMY_113.*`. A Phase 9b unit is a Phase 2 unit
on that folder: it reads `ASR_NN.A.csv` and `extraction_eval_dummy/LABELLING.md`
only and writes `ASR_NN.L2.csv`.

## Finishing

1. Tick the unit in `QUEUE.md`: `[x]` if every check passes, `[~]` if you ran out
   of rounds (leave the files, they are the next run's starting point — but a
   `[~]` unit is not retried automatically, so say exactly what still fails).
2. Append one line to `dataset/auto/LOG.md`:
   `<YYYY-MM-DD HH:MM> <unit> <x|~> rows=<n> decisions=<n> setting=<five words> checks=<pass/fail per script> note=<one sentence>`
   Counts and invented settings only.
3. Stop. Do not start a second unit; the scheduler decides when the next one runs.
