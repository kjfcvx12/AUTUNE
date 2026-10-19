"""Throwaway E2E probe for #31 / #191 (not committed).

A's real persistence writes an invented transcript and the real
``autune_core.publish`` sends ``autune.transcript.ready`` through Redis. A real
Celery worker (started separately) runs B, C and D; B publishes
``ExtractionResult``; D and E consume it. This script only writes the input and
then watches the tables.

Two meetings:
  M1 - participants consented (what #190 would decide), so B has something to say
  M2 - participants as A writes them today (consented=False), so B's result is empty

Needs AUTUNE_DATABASE_URL and AUTUNE_REDIS_URL pointing at the E2E containers.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime

import sqlalchemy as sa

from autune_worker import celery_app  # makes it current_app, so publish has a broker

# publish() finds subscribers among the tasks registered in *this* process. A
# worker imports every module's tasks at startup; a plain script does not, so
# load them the same way the worker does or the event goes nowhere.
celery_app.loader.import_default_modules()

from autune_audio.persistence import persist_transcript, transcript_payload
from autune_audio.speakers import Utterance as Spoken
from autune_contracts.events import TRANSCRIPT_READY
from autune_core import Meeting, Team, session_scope
from autune_core.entities import Participant
from autune_core.events import publish
from autune_context.models import CtxDecisionVersion, CtxMeetingStatus
from autune_extraction.models import ExtActionItem, ExtClassification, ExtConfirmation, ExtDecision
# C joined the pipeline after the 09-15 run: #163 writes the topic graph and
# #164 publishes GapReport. Without these counts the probe said "both finished"
# while never checking the module between B and E.
from autune_gap.models import GapGap, GapParticipation, GapTopic, GapTopicEdge
from autune_intelligence.models import IntelCompletion

LINES = [
    ("SPEAKER_00", 0.0, 2.0, "그럼 이번 분기는 A안으로 가기로 했습니다"),
    ("SPEAKER_01", 3.0, 5.0, "제가 금요일까지 정리하겠습니다"),
    ("SPEAKER_00", 6.0, 7.0, "한번 볼게요"),
    ("SPEAKER_01", 8.0, 9.0, "예산은 언제 나오나요"),
]
SPOKEN = tuple(
    Spoken(speaker=s, start=a, end=e, text=t, words=(), confidence=0.9) for s, a, e, t in LINES
)


def start_meeting(title: str, consent: bool) -> str:
    with session_scope() as s:
        team = Team(name=f"e2e-31-{title}")
        s.add(team)
        s.flush()
        meeting = Meeting(team_id=team.id, title=title, started_at=datetime.now(UTC))
        s.add(meeting)
        s.flush()
        mid = meeting.id
    with session_scope() as s:
        persist_transcript(s, meeting_id=mid, utterances=SPOKEN, duration_seconds=10.0, audio_deleted=True)
    if consent:
        with session_scope() as s:
            for p in s.scalars(sa.select(Participant).where(Participant.meeting_id == mid)):
                p.consented = True
    with session_scope() as s:
        payload = transcript_payload(s, meeting_id=mid).model_dump(mode="json")
    targets = publish(TRANSCRIPT_READY, payload)
    print(f"[{title}] meeting={mid} published {TRANSCRIPT_READY} -> {targets}")
    return mid


def state(mid: str) -> dict:
    with session_scope() as s:
        def n(model, where) -> int:
            return s.scalar(sa.select(sa.func.count()).select_from(model).where(where)) or 0

        ctx = s.get(CtxMeetingStatus, mid)
        intel = s.get(IntelCompletion, mid)
        ext_payload = intel.extraction_payload if intel is not None else None
        return {
            "B": {
                "classifications": n(ExtClassification, ExtClassification.meeting_id == mid),
                "decisions": n(ExtDecision, ExtDecision.meeting_id == mid),
                "items": n(ExtActionItem, ExtActionItem.meeting_id == mid),
                "confirmations": n(ExtConfirmation, ExtConfirmation.meeting_id == mid),
            },
            "C": {
                "topics": n(GapTopic, GapTopic.meeting_id == mid),
                "edges": n(GapTopicEdge, GapTopicEdge.meeting_id == mid),
                "participation": s.scalar(
                    sa.select(sa.func.count())
                    .select_from(GapParticipation)
                    .join(GapTopic, GapTopic.id == GapParticipation.topic_id)
                    .where(GapTopic.meeting_id == mid)
                ) or 0,
                "gaps": n(GapGap, GapGap.meeting_id == mid),
            },
            "D": None if ctx is None else {
                "extraction_seen": ctx.extraction_seen,
                "lineage_done": ctx.lineage_done,
                "topic_linking_done": ctx.topic_linking_done,
                "published": ctx.published_at is not None,
                "decision_versions": n(CtxDecisionVersion, CtxDecisionVersion.meeting_id == mid),
            },
            "E": None if intel is None else {
                "extraction_at": intel.extraction_at is not None,
                "context_at": intel.context_at is not None,
                "gap_at": intel.gap_at is not None,
                "aggregated": intel.aggregated_at is not None,
                "stored ExtractionResult": None if ext_payload is None else {
                    "decisions": len(ext_payload.get("decisions", [])),
                    "action_items": len(ext_payload.get("action_items", [])),
                    "classifications": len(ext_payload.get("classifications", [])),
                    "ambiguous_agreements": len(ext_payload.get("ambiguous_agreements", [])),
                },
            },
        }


def done(st: dict) -> bool:
    d, e = st["D"], st["E"]
    # gap_at added for #164: E now has a third input, and "finished" that does
    # not wait for it can pass while C never ran.
    return bool(
        d and d["extraction_seen"] and d["published"]
        and e and e["extraction_at"] and e["gap_at"] and e["aggregated"]
    )


m1 = start_meeting("M1-consented", consent=True)
m2 = start_meeting("M2-as-written", consent=False)

deadline = time.monotonic() + 240
while time.monotonic() < deadline:
    s1, s2 = state(m1), state(m2)
    if done(s1) and done(s2):
        break
    time.sleep(5)

for title, mid in (("M1-consented", m1), ("M2-as-written", m2)):
    print(f"--- {title} {mid}")
    for k, v in state(mid).items():
        print(f"  {k}: {v}")
print("both finished:", done(state(m1)) and done(state(m2)))
