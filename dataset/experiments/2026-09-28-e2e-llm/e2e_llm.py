"""E2E probe: B on classifier_impl=llm through a real Celery worker (not committed).

Same shape as ../2026-09-15-e2e-31/e2e_31.py: A's real persistence writes an
invented meeting, ``publish`` sends ``autune.transcript.ready`` through Redis,
a separately started worker runs B (LLM classifier), C, D and E. This script
writes the input and prints what B stored.

Dummy meeting only -- the Gemini key in .env is free tier (#392).
Needs AUTUNE_DATABASE_URL and AUTUNE_REDIS_URL pointing at the E2E containers.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime

import sqlalchemy as sa

from autune_worker import celery_app

celery_app.loader.import_default_modules()

from autune_audio.persistence import persist_transcript, transcript_payload
from autune_audio.speakers import Utterance as Spoken
from autune_contracts.events import TRANSCRIPT_READY
from autune_core import Meeting, Team, Utterance, session_scope
from autune_core.entities import Participant
from autune_core.events import publish
from autune_extraction.models import ExtActionItem, ExtClassification, ExtDecision
from autune_intelligence.models import IntelCompletion

# Invented: a payment-page sprint check-in, three speakers.
LINES = [
    ("SPEAKER_00", "자 그럼 결제 페이지 개편 건부터 볼게요"),
    ("SPEAKER_01", "네 지난주에 시안 두 개 올려놨는데요"),
    ("SPEAKER_01", "A안은 한 페이지에 다 보여주는 거고 B안은 단계별로 나눈 거예요"),
    ("SPEAKER_02", "개발 쪽에서는 A안이 훨씬 편하긴 해요"),
    ("SPEAKER_00", "음 전환율 데이터 보면 단계 나누면 이탈이 좀 있더라고요"),
    ("SPEAKER_02", "그쵸 저도 그게 걱정이었어요"),
    ("SPEAKER_00", "그럼 이번에는 A안으로 가는 걸로 하죠"),
    ("SPEAKER_01", "네 좋습니다"),
    ("SPEAKER_01", "그러면 제가 A안 기준으로 상세 화면을 목요일까지 다시 그려서 공유드릴게요"),
    ("SPEAKER_00", "네 부탁드려요"),
    ("SPEAKER_02", "근데 카드사 할부 안내 문구는 법무 검토가 필요하지 않나요"),
    ("SPEAKER_00", "아 그거 누가 확인해 봤나요"),
    ("SPEAKER_02", "아직 아무도 안 본 것 같아요"),
    ("SPEAKER_00", "그럼 그건 제가 법무팀에 이번 주 안에 물어볼게요"),
    ("SPEAKER_01", "그리고 간편결제 버튼 순서는 어떻게 할까요"),
    ("SPEAKER_02", "그건 좀 더 얘기해 봐야 할 것 같은데요"),
    ("SPEAKER_00", "네 그건 다음 회의에서 다시 보죠"),
    ("SPEAKER_02", "아 그리고 결제 실패 로그가 지금 안 쌓이고 있어요"),
    ("SPEAKER_02", "그거 제가 오늘 중으로 로그 수집 붙여 놓을게요"),
    ("SPEAKER_00", "좋아요 그게 제일 급하네요"),
    ("SPEAKER_01", "QA 일정은 언제로 잡을까요"),
    ("SPEAKER_00", "다음 주 수요일쯤이면 될 것 같은데 개발 일정 괜찮아요"),
    ("SPEAKER_02", "음 아마 될 거예요"),
    ("SPEAKER_00", "네 그럼 오늘은 여기까지 하겠습니다"),
]
SPOKEN = tuple(
    Spoken(speaker=s, start=i * 6.0, end=i * 6.0 + 5.0, text=t, words=(), confidence=0.9)
    for i, (s, t) in enumerate(LINES)
)


def start_meeting(title: str) -> str:
    with session_scope() as s:
        team = Team(name=f"e2e-llm-{title}")
        s.add(team)
        s.flush()
        meeting = Meeting(team_id=team.id, title=title, started_at=datetime.now(UTC))
        s.add(meeting)
        s.flush()
        mid = meeting.id
    with session_scope() as s:
        persist_transcript(
            s, meeting_id=mid, utterances=SPOKEN, duration_seconds=150.0, audio_deleted=True
        )
    with session_scope() as s:
        for p in s.scalars(sa.select(Participant).where(Participant.meeting_id == mid)):
            p.consented = True
    with session_scope() as s:
        payload = transcript_payload(s, meeting_id=mid).model_dump(mode="json")
    targets = publish(TRANSCRIPT_READY, payload)
    print(f"[{title}] meeting={mid} published -> {targets}")
    return mid


def extraction_done(mid: str) -> bool:
    with session_scope() as s:
        intel = s.get(IntelCompletion, mid)
        return intel is not None and intel.extraction_at is not None


t0 = time.monotonic()
mid = start_meeting("결제 페이지 개편 점검")
deadline = t0 + 300
while time.monotonic() < deadline and not extraction_done(mid):
    time.sleep(3)
print(f"extraction finished: {extraction_done(mid)} after {time.monotonic() - t0:.1f}s")

with session_scope() as s:
    text = {u.id: u.text for u in s.scalars(sa.select(Utterance).where(Utterance.meeting_id == mid))}
    rows = s.scalars(
        sa.select(ExtClassification).where(ExtClassification.meeting_id == mid)
    ).all()
    print(f"--- classifications ({len(rows)}), model {rows[0].model_version if rows else '-'}")
    for r in sorted(rows, key=lambda r: r.utterance_id):
        print(f"  {r.kind:14} {text.get(r.utterance_id, '?')}")
    items = s.scalars(sa.select(ExtActionItem).where(ExtActionItem.meeting_id == mid)).all()
    print(f"--- action items ({len(items)})")
    for it in items:
        print(f"  [{it.status}] {it.description} | {it.assignee_label} | {it.due_date}")
    decisions = s.scalars(sa.select(ExtDecision).where(ExtDecision.meeting_id == mid)).all()
    print(f"--- decisions ({len(decisions)})")
    for d in decisions:
        print(f"  {d.statement}")
    intel = s.get(IntelCompletion, mid)
    print("E stored ExtractionResult:", intel is not None and intel.extraction_payload is not None)
