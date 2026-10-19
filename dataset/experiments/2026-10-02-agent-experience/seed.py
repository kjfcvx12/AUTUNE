"""Agent experience check (10-02): what the agents do after a meeting is processed.

Dummy text only (the Gemini key is free tier). Prints ids, counts and
booleans -- the dummy lines below are invented.

    python seed.py approvers   # the signed-in person approves every agent scope
    python seed.py past        # a meeting ten days ago: three items on me
    python seed.py confirm     # mark them confirmed in the DB (no Notion/Calendar send)
    python seed.py now         # today's meeting; its processing wakes the agents
    python seed.py status      # agent runs and pending proposals of the team
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta

import sqlalchemy as sa

TEAM = "team_caltest"
ME = "user_3aab23886652477680a0e965892aae58"
PAST = [
    ("SPEAKER_00", 0.0, 3.0, "고객 인터뷰 정리는 제가 내일까지 정리해서 공유하겠습니다"),
    ("SPEAKER_01", 4.0, 6.0, "좋습니다 그럼 그렇게 하죠"),
    ("SPEAKER_00", 7.0, 10.0, "경쟁사 비교표도 제가 모레까지 만들어서 보내드리겠습니다"),
    ("SPEAKER_00", 11.0, 14.0, "온보딩 문서 초안은 제가 이번 주 금요일까지 올리겠습니다"),
]
NOW = [
    ("SPEAKER_00", 0.0, 3.0, "지난주에 맡은 것들이 아직 다 안 끝났습니다"),
    ("SPEAKER_01", 4.0, 7.0, "다음 스프린트 범위는 결제 개선으로 가기로 했습니다"),
    ("SPEAKER_01", 8.0, 11.0, "출시 일정은 아직 정하지 못했는데 언제쯤이 좋을까요"),
]


def _meeting(title: str, lines: list[tuple[str, float, float, str]], started: datetime) -> None:
    from autune_audio.persistence import persist_transcript, transcript_payload
    from autune_audio.speakers import Utterance as Spoken
    from autune_contracts import TRANSCRIPT_READY
    from autune_core import Meeting, Participant, publish, session_scope
    from autune_worker.celery_app import celery_app

    celery_app.loader.import_default_modules()
    with session_scope() as s:
        m = Meeting(team_id=TEAM, title=title, started_at=started)
        s.add(m)
        s.flush()
        mid = m.id
    spoken = tuple(
        Spoken(speaker=sp, start=a, end=e, text=t, words=(), confidence=0.9) for sp, a, e, t in lines
    )
    with session_scope() as s:
        persist_transcript(
            s, meeting_id=mid, utterances=spoken, duration_seconds=lines[-1][2], audio_deleted=True
        )
    with session_scope() as s:
        for p in s.scalars(sa.select(Participant).where(Participant.meeting_id == mid)):
            p.consented = True
            if p.speaker_label == "SPEAKER_00":
                p.user_id = ME
    with session_scope() as s:
        payload = transcript_payload(s, meeting_id=mid).model_dump(mode="json")
    print("meeting", mid, "->", publish(TRANSCRIPT_READY, payload))


def approvers() -> None:
    from autune_agent.main.pending import SCOPES
    from autune_agent.models import AgentApprover
    from autune_core import session_scope

    with session_scope() as s:
        for scope in SCOPES.values():
            if s.get(AgentApprover, (TEAM, ME, scope)) is None:
                s.add(AgentApprover(team_id=TEAM, user_id=ME, scope=scope))
    print("approver scopes", sorted(SCOPES.values()))


def past() -> None:
    _meeting("지난 회의 (더미)", PAST, datetime.now(UTC) - timedelta(days=10))


def now() -> None:
    _meeting("오늘 회의 (더미)", NOW, datetime.now(UTC) - timedelta(hours=1))


def confirm() -> None:
    from autune_core import Meeting, session_scope
    from autune_extraction.models import ExtActionItem

    with session_scope() as s:
        mid = s.scalar(
            sa.select(Meeting.id).where(Meeting.team_id == TEAM, Meeting.title == "지난 회의 (더미)")
        )
        items = s.scalars(sa.select(ExtActionItem).where(ExtActionItem.meeting_id == mid)).all()
        for i in items:
            i.status = "todo"
            i.assignee_id = i.assignee_id or ME
        print("confirmed", len(items), "due", sorted(str(i.due_date) for i in items))


def status() -> None:
    from autune_agent.models import AgentPendingAction, AgentRun
    from autune_core import session_scope

    with session_scope() as s:
        for r in s.scalars(
            sa.select(AgentRun).where(AgentRun.team_id == TEAM).order_by(AgentRun.created_at)
        ):
            print("run", r.route, r.outcome if hasattr(r, "outcome") else "", "proposed", len(r.proposed or []))
        for p in s.scalars(
            sa.select(AgentPendingAction).where(AgentPendingAction.team_id == TEAM)
        ):
            print("pending", p.subagent, p.kind, p.status)


if __name__ == "__main__":
    {"approvers": approvers, "past": past, "confirm": confirm, "now": now, "status": status}[
        sys.argv[1]
    ]()
