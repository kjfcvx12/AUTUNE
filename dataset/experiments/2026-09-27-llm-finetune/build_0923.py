"""A real meeting as the product would see it: dataset/회의록_2026-09-23_화자별.txt.

Lines are `[HH:MM:SS] 화자N: text` (Whisper + diarization output, three
recordings). Consecutive lines by one speaker become one turn, as
`autune_audio.speakers.assign_speakers` does; a new recording always starts a
new turn. Chunked and rendered exactly like build_sft.py. There is no gold --
the runs are compared by what they pick, so gold lists are empty.

Writes meeting0923.jsonl. Prints counts only.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from build_sft import DATA, SYSTEM, chunk, render
from build_turns import MAX_TURN_CHARS

HERE = Path(__file__).parent
SOURCE = DATA / "회의록_2026-09-23_화자별.txt"
UTTERANCE = re.compile(r"^\[(\d\d:\d\d:\d\d)\] (화자\d+): (.*)$")


def main() -> None:
    turns: list[dict] = []
    recording = 0
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if line.startswith("[녹음"):
            recording += 1
            continue
        m = UTTERANCE.match(line)
        if not m:
            continue
        _, speaker, text = m.groups()
        last = turns[-1] if turns else None
        if (
            last
            and last["recording"] == recording
            and last["speaker"] == speaker
            and len(last["text"]) + len(text) <= MAX_TURN_CHARS
        ):
            last["text"] += " " + text.strip()
        else:
            turns.append({"recording": recording, "speaker": speaker, "text": text.strip()})
    utts = [
        {"idx": n, "speaker": t["speaker"], "text": t["text"], "gold": "no"}
        for n, t in enumerate(turns, 1)
    ]
    rows = []
    for n, (ctx, new) in enumerate(chunk(utts)):
        rows.append(
            {
                "meeting": "MEETING_0923",
                "chunk": n,
                "system": SYSTEM,
                "user": render(ctx, new),
                "answer": "",
                "gold_yes": [],
                "gold_ignore": [],
                "new_idx": [u["idx"] for u in new],
            }
        )
    with (HERE / "meeting0923.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"recordings={recording} turns={len(utts)} chunks={len(rows)}")


if __name__ == "__main__":
    main()
