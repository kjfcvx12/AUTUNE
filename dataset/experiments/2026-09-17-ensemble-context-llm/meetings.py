"""Whole-meeting utterance order, for context.

The decision-probe sheets hold only candidate windows and the commitment-probe
sheets only candidates and their neighbours, so the row above a row in a sheet is
often not the row above it in the meeting. Context is taken from the AI Hub source
file instead, cleaned exactly as the sheets were (probe.load_rows), and row numbers
are the same original utterance indices the sheets use.
"""

from __future__ import annotations

import csv
import json
import sys
from functools import lru_cache
from pathlib import Path

DATASET = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(DATASET / "extraction_eval_pilot"))
from pilot_sheets import clean  # noqa: E402

USED = [
    DATASET / "experiments" / "2026-09-12-commitment-probe" / "results" / "used_meetings.json",
    DATASET / "experiments" / "2026-09-12-commitment-probe" / "results_r2" / "used_meetings.json",
    DATASET / "experiments" / "2026-09-15-decision-probe" / "results" / "used_meetings.json",
]
EXTRA_INDEX = Path(__file__).resolve().parent / "meeting_paths.json"


def load_rows(path: Path) -> tuple[str, list[dict]]:
    """probe.load_rows, copied: probe.py parses argv at import, so it cannot be imported."""
    data = json.loads(path.read_text(encoding="utf-8"))
    mid = data.get("metadata", {}).get("id") or path.stem
    rows = []
    for i, u in enumerate(data["utterance"], start=1):
        text = clean(u.get("form") or "")
        if not text:
            continue
        rows.append({"row": str(i), "speaker": str(u.get("speaker_id") or ""), "text": text})
    return mid, rows


@lru_cache(maxsize=1)
def index() -> dict[str, str]:
    out: dict[str, str] = {}
    for f in USED:
        for m in json.loads(f.read_text(encoding="utf-8")):
            out[m["meeting"]] = m["path"]
    if EXTRA_INDEX.exists():
        out.update(json.loads(EXTRA_INDEX.read_text(encoding="utf-8")))
    return out


@lru_cache(maxsize=None)
def full_rows(meeting: str) -> tuple[dict, ...] | None:
    path = index().get(meeting)
    if not path or not Path(path).exists():
        return None
    _, rows = load_rows(Path(path))
    return tuple(rows)


def sheet_rows(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    rows.sort(key=lambda r: int(r["row"]))
    return rows


def neighbours(rows, i: int, context: int) -> tuple[list[dict], list[dict]]:
    return list(rows[max(0, i - context) : i]), list(rows[i + 1 : i + 1 + context])
