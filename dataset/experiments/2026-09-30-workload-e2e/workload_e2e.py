"""Workload E2E on a dummy meeting (local only, not committed; dataset/ is ignored).

Invented people and lines only. Run from F:/0final/wte2e (origin/main) with
scratchpad e2e_env.sh sourced, a real Celery worker running, and
AUTUNE_AGENT_LLM_API_KEY set from the free Gemini key (dummy data only, #392).

1. A's real persistence writes the meeting; participants are identified and
   consent is attested by direct writes (what A's speaker-confirm and
   attest_consent endpoints do).
2. The real publish sends autune.transcript.ready through Redis; the worker
   runs B, C, D, E and the agent layer's event triggers.
3. Every drafted item is confirmed through B's board edit path
   (service.update_action_item), the way a person would on S18.
4. POST /api/agent/chat on the assembled API app (autune_api.main.app) as a
   team member, with the real Gemini router.
5. The agent_runs row and B's items are checked: L2 proposals by id, nothing
   written, no names stored.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime, timedelta

import sqlalchemy as sa

from autune_worker import celery_app

celery_app.loader.import_default_modules()

from fastapi.testclient import TestClient  # noqa: E402

from autune_agent.models import AgentRun  # noqa: E402
from autune_api.main import app  # noqa: E402
from autune_audio.persistence import persist_transcript, transcript_payload  # noqa: E402
from autune_audio.speakers import Utterance as Spoken  # noqa: E402
from autune_contracts.enums import ActionStatus  # noqa: E402
from autune_contracts.events import TRANSCRIPT_READY  # noqa: E402
from autune_core import Meeting, Team, TeamMember, User, current_user, session_scope  # noqa: E402
from autune_core.entities import Participant  # noqa: E402
from autune_core.events import publish  # noqa: E402
from autune_extraction import service as b  # noqa: E402
from autune_extraction.models import ExtActionItem  # noqa: E402
from autune_extraction.schemas import ActionItemUpdate  # noqa: E402
from autune_intelligence.models import IntelCompletion  # noqa: E402

PEOPLE = {"SPEAKER_00": "박지영", "SPEAKER_01": "김민경", "SPEAKER_02": "이승환"}
LINES = [
    ("SPEAKER_00", 0.0, "견적서는 제가 내일까지 정리하겠습니다"),
    ("SPEAKER_02", 4.0, "네 좋습니다"),
    ("SPEAKER_00", 6.0, "API 문서도 내일까지 올리겠습니다"),
    ("SPEAKER_00", 10.0, "테스트 계정은 모레까지 만들겠습니다"),
    ("SPEAKER_01", 14.0, "디자인 시안은 다음 달 말까지 공유하겠습니다"),
    ("SPEAKER_00", 18.0, "고객 인터뷰 일정은 이번 주 금요일까지 잡겠습니다"),
    ("SPEAKER_02", 22.0, "예산은 언제 나오나요"),
    ("SPEAKER_00", 26.0, "배포 체크리스트는 제가 다음 주 월요일까지 업데이트하겠습니다"),
]


def seed() -> tuple[str, str, dict[str, str]]:
    with session_scope() as s:
        team = Team(name="e2e-workload")
        users = {label: User(email=f"{label.lower()}@example.com", display_name=name) for label, name in PEOPLE.items()}
        s.add_all([team, *users.values()])
        s.flush()
        s.add_all([TeamMember(team_id=team.id, user_id=u.id) for u in users.values()])
        meeting = Meeting(team_id=team.id, title="주간 회의 (E2E)", started_at=datetime.now(UTC) - timedelta(days=10))
        s.add(meeting)
        s.flush()
        ids = {label: u.id for label, u in users.items()}
        return team.id, meeting.id, ids


def run() -> None:
    team_id, meeting_id, user_of = seed()
    spoken = tuple(Spoken(speaker=l, start=a, end=a + 3, text=t, words=(), confidence=0.9) for l, a, t in LINES)
    with session_scope() as s:
        persist_transcript(s, meeting_id=meeting_id, utterances=spoken, duration_seconds=30.0, audio_deleted=True)
    with session_scope() as s:
        for p in s.scalars(sa.select(Participant).where(Participant.meeting_id == meeting_id)):
            p.user_id = user_of[p.speaker_label]
            p.consented = True
    with session_scope() as s:
        payload = transcript_payload(s, meeting_id=meeting_id).model_dump(mode="json")
    print("published to:", publish(TRANSCRIPT_READY, payload))

    started = time.monotonic()
    items: list[ExtActionItem] = []
    aggregated = False
    while time.monotonic() - started < 240:
        with session_scope() as s:
            items = list(s.scalars(sa.select(ExtActionItem).where(ExtActionItem.meeting_id == meeting_id)))
            intel = s.get(IntelCompletion, meeting_id)
            aggregated = intel is not None and intel.aggregated_at is not None
        if items and aggregated:
            break
        time.sleep(3)
    print(f"B drafted {len(items)} item(s) after {time.monotonic() - started:.0f}s; E aggregated={aggregated}")

    name_of = {v: PEOPLE[k] for k, v in user_of.items()}
    with session_scope() as s:
        for item in s.scalars(sa.select(ExtActionItem).where(ExtActionItem.meeting_id == meeting_id)):
            b.update_action_item(s, item, ActionItemUpdate(status=ActionStatus.TODO))
    with session_scope() as s:
        rows = s.execute(
            sa.select(ExtActionItem.id, ExtActionItem.assignee_id, ExtActionItem.due_date, ExtActionItem.status)
            .where(ExtActionItem.meeting_id == meeting_id)
            .order_by(ExtActionItem.due_date)
        ).all()
        before = {r[0]: r[1] for r in rows}
        for r in rows:
            print(f"  item {r[0]} -> {name_of.get(r[1], r[1])} due {r[2]} {r[3]}")
        triggered = s.execute(
            sa.select(AgentRun.route, AgentRun.outcome, AgentRun.trigger).where(AgentRun.meeting_id == meeting_id)
        ).all()
        print("agent runs woken by events:", [(r[0], r[1], r[2].get("event")) for r in triggered])

    app.dependency_overrides[current_user] = lambda: _user(user_of["SPEAKER_01"])
    client = TestClient(app)
    for ask in ("업무 몰린 사람 있어?", "지난 회의에서 결정한 거 뭐였지?"):
        t0 = time.monotonic()
        reply = client.post("/api/agent/chat", json={"team_id": team_id, "message": ask})
        body = reply.json()
        print(f"\nASK {ask!r} -> HTTP {reply.status_code} in {time.monotonic() - t0:.1f}s")
        print(json.dumps({k: body.get(k) for k in ("route", "outcome", "answer", "proposed", "executed")}, ensure_ascii=False, indent=1))
        for f in body.get("items", []):
            print("  finding:", f.get("id"), "|", f.get("title"))
        if reply.status_code == 200:
            with session_scope() as s:
                run_row = s.get(AgentRun, body["run_id"])
                stored = json.dumps([run_row.steps, run_row.proposed, run_row.actions], ensure_ascii=False)
                print("  stored steps:", [st["tool"] for st in run_row.steps])
                print("  stored proposed:", [(p["tool"], p["level"], p["evidence"]) for p in run_row.proposed])
                print("  names in stored row:", [n for n in PEOPLE.values() if n in stored])

    with session_scope() as s:
        after = dict(
            s.execute(sa.select(ExtActionItem.id, ExtActionItem.assignee_id).where(ExtActionItem.meeting_id == meeting_id)).tuples().all()
        )
    print("\nB assignees unchanged by the chat:", after == before)


def _user(user_id: str) -> User:
    with session_scope() as s:
        user = s.get(User, user_id)
        s.expunge(user)
        return user


run()
