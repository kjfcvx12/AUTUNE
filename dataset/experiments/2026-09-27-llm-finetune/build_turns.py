"""Turn-merged test sets: what module A actually produces.

`autune_audio.speakers.assign_speakers` cuts at speaker changes, so several
Whisper segments by one speaker in a row become ONE utterance. The dummy sets
(DUMMY_101+, EVALH) and AI Hub are written/segmented as several rows per turn;
this merges consecutive same-speaker rows into one turn row, like A would.

Turn gold: yes if any row is yes; no if every row is a labelled no; otherwise
ignore (a turn holding an unlabelled or ambiguous row could hide a commitment).

Writes test_turns.jsonl (EVAL + EVALH) and test_real_turns.jsonl (AI Hub,
local only), each row carrying `turn_rows` so a row-level run can be re-scored
at turn level (score_turns.py). Prints counts only.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from build_real import PARTS
from build_sft import DATA, SYSTEM, chunk, load_meeting, render

HERE = Path(__file__).parent


MAX_TURN_CHARS = 2000
"""A chaired AI Hub meeting has single turns of 10k characters, which OOM the
3060 (naive attention). Past this, the same speaker's next row starts a new
utterance -- B would have to split a monologue that long anyway."""


def turns_of(rows: list[dict]) -> list[dict]:
    turns: list[dict] = []
    for r in rows:
        if (
            turns
            and turns[-1]["speaker"] == r["speaker"]
            and len(turns[-1]["text"]) + len(r["text"]) <= MAX_TURN_CHARS
        ):
            turns[-1]["text"] += " " + r["text"]
            turns[-1]["rows"].append(r)
        else:
            turns.append({"speaker": r["speaker"], "text": r["text"], "rows": [r]})
    out = []
    for n, t in enumerate(turns, 1):
        golds = {r["gold"] for r in t["rows"]}
        gold = "yes" if "yes" in golds else "no" if golds == {"no"} else "ignore"
        out.append(
            {
                "idx": n,
                "speaker": t["speaker"],
                "text": t["text"],
                "gold": gold,
                "row_idx": [r["idx"] for r in t["rows"]],
            }
        )
    return out


def examples(meeting: str, turns: list[dict]) -> list[dict]:
    out = []
    for n, (ctx, new) in enumerate(chunk(turns)):
        out.append(
            {
                "meeting": meeting,
                "chunk": n,
                "system": SYSTEM,
                "user": render(ctx, new),
                "answer": "",
                "gold_yes": [u["idx"] for u in new if u["gold"] == "yes"],
                "gold_ignore": [u["idx"] for u in new if u["gold"] == "ignore"],
                "new_idx": [u["idx"] for u in new],
                "turn_rows": {str(u["idx"]): u["row_idx"] for u in new},
            }
        )
    return out


def real_rows(path: Path) -> list[dict]:
    rows = []
    for i, r in enumerate(csv.DictReader(path.open(encoding="utf-8-sig")), start=1):
        kind = (r.get("kind") or "").strip()
        gold = "yes" if kind == "commitment" else "ignore" if kind in ("", "ambiguous") else "no"
        role = r.get("role") or ""
        speaker = f"{r['speaker']}({role})" if role else r["speaker"]
        rows.append({"idx": i, "speaker": speaker, "text": r["text"].strip(), "gold": gold})
    return rows


def write(name: str, rows: list[dict]) -> None:
    with (HERE / f"{name}.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    n_turns = sum(len(r["new_idx"]) for r in rows)
    yes = sum(len(r["gold_yes"]) for r in rows)
    ign = sum(len(r["gold_ignore"]) for r in rows)
    print(f"{name}: chunks={len(rows)} turns={n_turns} yes={yes} no={n_turns - yes - ign} ignore={ign}")


def main() -> None:
    dummy = []
    for folder in ("extraction_eval_dummy", "extraction_eval_dummy_hard"):
        for p in sorted((DATA / folder).glob("*.G.csv")):
            mid = p.name.split(".")[0]
            rows = load_meeting(p, p.with_name(f"{mid}.speakers.json"))
            dummy += examples(mid, turns_of(rows))
    write("test_turns", dummy)

    # Product-shaped ASR set: G.csv once the second labeller has run, else the
    # author's C.csv (say which when reporting).
    asr = []
    # ASR_ = written by the Claude runner, ASRX_ = by another AI (EXTERNAL_AI_PROMPT.md).
    for c in sorted((DATA / "extraction_eval_asr").glob("ASR*_*.C.csv")):
        mid = c.name.split(".")[0]
        g = c.with_name(f"{mid}.G.csv")
        rows = load_meeting(g if g.exists() else c, c.with_name(f"{mid}.speakers.json"))
        asr += examples(mid, turns_of(rows))
    if asr:
        write("test_asr_turns", asr)

    real = []
    for part, files in PARTS.items():
        for f in files:
            if ".first" in f.name or "recheck" in f.name:
                continue
            real += examples(f"{part}/{f.name.split('.')[0]}", turns_of(real_rows(f)))
    write("test_real_turns", real)


if __name__ == "__main__":
    main()
