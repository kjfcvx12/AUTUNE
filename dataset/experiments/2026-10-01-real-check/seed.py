"""Real-service check (10-01): one dummy meeting in the real-account team.

A's real persistence writes it with the signed-in person as the speaker, and
TranscriptReady goes to the real worker. Dummy text only (the Gemini key is
free tier). Prints ids and counts only.

    python seed.py meeting    # write + publish
    python seed.py status     # what B made of it
    python seed.py ask        # send the confirmation DM(s) now (real Slack)
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta

import sqlalchemy as sa

TEAM = "team_caltest"
ME = "user_3aab23886652477680a0e965892aae58"
LINES = [
    ("SPEAKER_00", 0.0, 3.0, "이번 주 회의록은 제가 다음 주 금요일까지 정리해서 공유하겠습니다"),
    ("SPEAKER_01", 4.0, 6.0, "데모 일정은 다음 주 수요일로 가기로 했습니다"),
    ("SPEAKER_01", 7.0, 9.0, "발표 자료 초안도 누가 봐 주실 수 있을까요"),
    ("SPEAKER_00", 10.0, 11.0, "그럼 제가 한번 볼게요"),
]


def meeting() -> None:
    from autune_audio.persistence import persist_transcript, transcript_payload
    from autune_audio.speakers import Utterance as Spoken
    from autune_contracts import TRANSCRIPT_READY
    from autune_core import Meeting, Participant, publish, session_scope
    from autune_worker.celery_app import celery_app

    celery_app.loader.import_default_modules()
    with session_scope() as s:
        m = Meeting(team_id=TEAM, title="실서비스 확인 회의",
                    started_at=datetime.now(UTC) - timedelta(hours=2))
        s.add(m)
        s.flush()
        mid = m.id
    spoken = tuple(Spoken(speaker=sp, start=a, end=e, text=t, words=(), confidence=0.9)
                   for sp, a, e, t in LINES)
    with session_scope() as s:
        persist_transcript(s, meeting_id=mid, utterances=spoken, duration_seconds=12.0,
                           audio_deleted=True)
    with session_scope() as s:
        for p in s.scalars(sa.select(Participant).where(Participant.meeting_id == mid)):
            p.consented = True
            if p.speaker_label == "SPEAKER_00":
                p.user_id = ME
    with session_scope() as s:
        payload = transcript_payload(s, meeting_id=mid).model_dump(mode="json")
    print("meeting", mid, "->", publish(TRANSCRIPT_READY, payload))


def status() -> None:
    from autune_core import Meeting, session_scope
    from autune_extraction.models import ExtActionItem, ExtConfirmation, ExtDecision

    with session_scope() as s:
        mid = s.scalar(sa.select(Meeting.id).where(Meeting.team_id == TEAM,
                       Meeting.title == "실서비스 확인 회의").order_by(Meeting.created_at.desc()))
        items = s.scalars(sa.select(ExtActionItem).where(ExtActionItem.meeting_id == mid)).all()
        print("meeting", mid)
        for i in items:
            print("item", i.id[-6:], i.status, "resolved", i.description_resolved,
                  "related", len(i.related), "due", i.due_date)
        print("decisions", s.scalar(sa.select(sa.func.count()).select_from(ExtDecision)
                                    .where(ExtDecision.meeting_id == mid)))
        for c in s.scalars(sa.select(ExtConfirmation).where(ExtConfirmation.meeting_id == mid)):
            print("confirmation", c.utterance_id[-6:], "sent", c.sent_at is not None,
                  "answer", c.resolved_kind)


def ask() -> None:
    from autune_extraction import tasks
    from autune_worker.celery_app import celery_app

    celery_app.loader.import_default_modules()
    print("asked", len(tasks.ask_confirmations()))


if __name__ == "__main__":
    {"meeting": meeting, "status": status, "ask": ask}[sys.argv[1]]()
