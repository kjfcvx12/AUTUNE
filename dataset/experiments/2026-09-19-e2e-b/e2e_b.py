"""Functional E2E for module B on a realistic meeting (not committed).

DUMMY_01 (team-authored, 307 rows, ~30 min) goes in through A's real persistence,
participants' consent is set in the DB (#190 / #283 not merged), and the real
``autune.transcript.ready`` is published. A real Celery worker runs B with the
local v2 ensemble (cascade) and C/D/E with their configured implementations.
This script then waits for D and E to finish and prints what each module wrote.

    python e2e_b.py            # needs AUTUNE_DATABASE_URL, AUTUNE_REDIS_URL
"""

from __future__ import annotations

import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import sqlalchemy as sa

from autune_worker import celery_app

celery_app.loader.import_default_modules()

from autune_audio.persistence import persist_transcript, transcript_payload
from autune_audio.speakers import Utterance as Spoken
from autune_contracts.events import TRANSCRIPT_READY
from autune_core import Meeting, Team, session_scope
from autune_core.entities import Participant
from autune_core.events import publish
from autune_context.models import CtxDecisionVersion, CtxMeetingStatus
from autune_extraction.models import ExtActionItem, ExtClassification, ExtConfirmation, ExtDecision
from autune_gap.models import GapGap, GapTopic, GapTopicEdge
from autune_intelligence.models import IntelCompletion

SHEET = Path(__file__).resolve().parents[2] / "team_dummy" / "DUMMY_01.A.csv"
KST = ZoneInfo("Asia/Seoul")


def spoken() -> tuple[Spoken, ...]:
    rows = list(csv.DictReader(SHEET.open(encoding="utf-8-sig")))
    out = []
    for i, r in enumerate(rows):
        start = float(r["start"])
        nxt = float(rows[i + 1]["start"]) if i + 1 < len(rows) else start + 3.0
        end = max(start + 0.5, nxt - 0.2)
        speaker = "SPEAKER_%02d" % (int(r["speaker"].removeprefix("SPK")) - 1)
        out.append(Spoken(speaker=speaker, start=start, end=end, text=r["text"], words=(), confidence=0.9))
    return tuple(out)


def start() -> str:
    utts = spoken()
    with session_scope() as s:
        team = Team(name="e2e-b-dummy01")
        s.add(team)
        s.flush()
        meeting = Meeting(team_id=team.id, title="DUMMY_01", started_at=datetime(2026, 9, 14, 10, 0, tzinfo=KST))
        s.add(meeting)
        s.flush()
        mid = meeting.id
    with session_scope() as s:
        persist_transcript(s, meeting_id=mid, utterances=utts, duration_seconds=utts[-1].end, audio_deleted=True)
    with session_scope() as s:
        for p in s.scalars(sa.select(Participant).where(Participant.meeting_id == mid)):
            p.consented = True
    with session_scope() as s:
        payload = transcript_payload(s, meeting_id=mid).model_dump(mode="json")
    print(f"meeting={mid} utterances={len(utts)} published -> {publish(TRANSCRIPT_READY, payload)}", flush=True)
    return mid


def state(mid: str) -> dict:
    with session_scope() as s:
        def n(model, where) -> int:
            return s.scalar(sa.select(sa.func.count()).select_from(model).where(where)) or 0

        kinds = dict(s.execute(sa.select(ExtClassification.kind, sa.func.count()).where(ExtClassification.meeting_id == mid).group_by(ExtClassification.kind)).all())
        ctx = s.get(CtxMeetingStatus, mid)
        intel = s.get(IntelCompletion, mid)
        return {
            "B": {"classifications": kinds, "decisions": n(ExtDecision, ExtDecision.meeting_id == mid),
                  "items": n(ExtActionItem, ExtActionItem.meeting_id == mid),
                  "confirmations": n(ExtConfirmation, ExtConfirmation.meeting_id == mid)},
            "C": {"topics": n(GapTopic, GapTopic.meeting_id == mid), "edges": n(GapTopicEdge, GapTopicEdge.meeting_id == mid),
                  "gaps": n(GapGap, GapGap.meeting_id == mid)},
            "D": None if ctx is None else {"extraction_seen": ctx.extraction_seen, "published": ctx.published_at is not None,
                                           "decision_versions": n(CtxDecisionVersion, CtxDecisionVersion.meeting_id == mid)},
            "E": None if intel is None else {"extraction_at": intel.extraction_at is not None, "context_at": intel.context_at is not None,
                                             "gap_at": intel.gap_at is not None, "aggregated": intel.aggregated_at is not None},
        }


def done(st: dict) -> bool:
    d, e = st["D"], st["E"]
    return bool(d and d["published"] and e and e["extraction_at"] and e["gap_at"] and e["aggregated"])


mid = sys.argv[1] if len(sys.argv) > 1 else start()
t0 = time.monotonic()
while time.monotonic() - t0 < 900:
    st = state(mid)
    if done(st):
        break
    time.sleep(10)
print(f"elapsed {time.monotonic() - t0:.0f}s")
print(json.dumps(state(mid), ensure_ascii=False, indent=1, default=str))
print("finished:", done(state(mid)))
