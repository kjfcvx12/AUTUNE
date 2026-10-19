"""Real-stack check of what merged on 2026-10-01 (#574, #576, #577; #573's task).

Postgres + Redis + a real Celery worker started separately; every model fake;
Slack/Notion tokens blank. Prints ids, counts and booleans only.

    stage 1 (seed + registration): python drive.py seed
    stage 2 (flows, worker running): python drive.py flows
"""

from __future__ import annotations

import sys
import time
from datetime import UTC, datetime

from sqlalchemy import select

TEAM = "team_e2e1001"
MEETING = "mtg_e2e1001"
LINES = [
    ("utt_e1", "par_kim", "결제 로그에 필드 하나 더 넣는 건 지난주에 얘기했죠"),
    ("utt_e2", "par_lee", "그 필드는 정산팀도 쓴다고 했어요"),
    ("utt_e3", "par_kim", "그거 제가 금요일까지 할게요"),
    ("utt_e4", "par_kim", "그럼 제가 한번 볼게요"),
    ("utt_e5", "par_no", "제 번호로 연락 주세요"),
]


def seed() -> None:
    from autune_core import Meeting, Participant, Team, TeamMember, User, Utterance, session_scope
    from autune_extraction.models import ExtConfirmation
    from autune_worker.celery_app import celery_app

    celery_app.loader.import_default_modules()
    names = set(celery_app.tasks)
    for task in (
        "autune.extraction.summarise_confirmed_draft",
        "autune.extraction.backfill_notion",
    ):
        print("registered", task, task in names)

    with session_scope() as s:
        s.add(Team(id=TEAM, name="E2E팀"))
        for uid, name in (("user_e2ekim", "김"), ("user_e2elee", "이")):
            s.add(User(id=uid, email=f"{uid}@example.com", display_name=name))
        s.flush()
        for uid in ("user_e2ekim", "user_e2elee"):
            s.add(TeamMember(team_id=TEAM, user_id=uid))
        s.add(
            Meeting(
                id=MEETING, team_id=TEAM, title="주간 회의",
                started_at=datetime(2026, 9, 29, 1, tzinfo=UTC),
            )
        )
        s.flush()
        s.add_all(
            [
                Participant(id="par_kim", meeting_id=MEETING, user_id="user_e2ekim",
                            speaker_label="김", consented=True),
                Participant(id="par_lee", meeting_id=MEETING, user_id="user_e2elee",
                            speaker_label="이", consented=True),
                Participant(id="par_no", meeting_id=MEETING, speaker_label="박", consented=False),
            ]
        )
        s.flush()
        for n, (uid, who, text) in enumerate(LINES):
            s.add(Utterance(id=uid, meeting_id=MEETING, participant_id=who, speaker_label="화자",
                            start_sec=float(n), end_sec=float(n) + 0.5, text=text))
        s.flush()
        s.add(ExtConfirmation(utterance_id="utt_e4", meeting_id=MEETING, reason="weak_assent",
                              sent_at=datetime.now(UTC)))
    print("seeded")


def flows() -> None:
    from autune_agent.main.actions import collect_actions, run_action
    from autune_agent.main.registry import RunScope
    from autune_contracts.enums import UtteranceKind
    from autune_core import session_scope
    from autune_extraction import service, tools
    from autune_extraction.confirmations import ConfirmationResponse
    from autune_extraction.models import ExtActionItem, ExtEditEvent
    from autune_worker.celery_app import celery_app

    celery_app.loader.import_default_modules()
    actions = collect_actions()
    scope = RunScope(team_id=TEAM, meeting_id=MEETING)

    # 1. Chat draft through the agent's action executor (L1).
    print("level add_action_item", actions["extraction.add_action_item"].level)
    with session_scope() as s:
        result = run_action(actions["extraction.add_action_item"],
                            {"meeting_id": MEETING, "utterance_id": "utt_e3"}, session=s, scope=scope)
    print("chat draft ok", result.ok)
    with session_scope() as s:
        chat = s.scalars(select(ExtActionItem).where(ExtActionItem.origin == "chat")).one()
        detail = service.read_detail(s, chat)
        print("chat draft status", chat.status, "sources shown", len(detail.sources),
              "assignee is speaker", chat.assignee_id == "user_e2ekim",
              "due set", chat.due_date is not None)
        refused = run_action(actions["extraction.add_action_item"],
                             {"meeting_id": MEETING, "utterance_id": "utt_e5"}, session=s, scope=scope)
        print("non-consenting utterance refused", not refused.ok)
    with session_scope() as s:
        chat = s.get(ExtActionItem, chat.id)
        service.update_action_item(s, chat, service.ActionItemUpdate(status="todo"))
    with session_scope() as s:
        chat = s.get(ExtActionItem, chat.id)
        detail = service.read_detail(s, chat)
        print("confirmed chat item: sources shown", len(detail.sources), "ids", detail.source_utterance_ids,
              "deleted count", detail.deleted_source_count,
              "contract keeps source", service.contract_action_item(chat).source_utterance_ids)

    # 2. "약속입니다" -> draft at once -> summarise job on the real worker.
    service.apply_confirmation_response(
        ConfirmationResponse(utterance_id="utt_e4", resolved_kind=UtteranceKind.COMMITMENT,
                             responder_id="user_e2ekim")
    )
    with session_scope() as s:
        drafted = s.scalars(
            select(ExtActionItem).join(ExtActionItem.sources).where(
                ExtActionItem.origin == "model"
            )
        ).all()
        print("confirmed-agreement drafts", len(drafted))
    print("job queued; check the worker log for extraction_confirmed_draft_summarised")

    # 3. Follow-up: L2 through the same executor an approval uses, then the read.
    print("level add_followup_item", actions["extraction.add_followup_item"].level)
    with session_scope() as s:
        first = run_action(actions["extraction.add_followup_item"], {"meeting_id": MEETING},
                           session=s, scope=scope)
        second = run_action(actions["extraction.add_followup_item"], {"meeting_id": MEETING},
                            session=s, scope=scope)
        print("followup first ok", first.ok, "second refused", not second.ok)
    with session_scope() as s:
        read = tools.open_followup_item(s, TEAM)
        print("open followup items", len(read["items"]))
        print("edit events (agent items record none)",
              s.scalar(select(ExtEditEvent.id).where(ExtEditEvent.kind == "created").limit(1)) is None)

    time.sleep(8)
    with session_scope() as s:
        for row in s.scalars(select(ExtActionItem).where(ExtActionItem.origin == "model")):
            print("confirmed draft after job: status", row.status, "resolved", row.description_resolved)


if __name__ == "__main__":
    {"seed": seed, "flows": flows}[sys.argv[1]]()
