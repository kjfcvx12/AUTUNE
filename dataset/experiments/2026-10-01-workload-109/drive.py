"""Workload 10/9 gate (agent-layer.md section 14): end to end on one real meeting.

A's real persistence writes an invented (dummy) meeting, the real worker runs
B's pipeline, the real API confirms the items, a chat turn reaches Workload
through the Gemini router, the proposals wait in plan mode, and the team lead's
approval runs B's real `reassign_action_item`. Dummy content only (free Gemini
key). Prints ids, counts and booleans -- no utterance text.

    python drive.py seed      # team, people, the meeting; publishes TranscriptReady
    python drive.py chat      # after the worker drafted: confirm, ask, approve
"""

from __future__ import annotations

import sys
import time
from datetime import UTC, datetime, timedelta

import httpx
import sqlalchemy as sa

API = "http://127.0.0.1:8765"
TEAM = "team_wl109"
LEAD, KIM, LEE = "user_wl109lead", "user_wl109kim", "user_wl109lee"
LINES = [
    ("SPEAKER_00", 0.0, 2.0, "이번 분기 보고서는 제가 내일까지 정리하겠습니다"),
    ("SPEAKER_01", 3.0, 4.0, "좋습니다"),
    ("SPEAKER_00", 5.0, 7.0, "예산표도 제가 모레까지 보내드리겠습니다"),
    ("SPEAKER_01", 8.0, 9.0, "예산은 언제 확정되나요"),
]


def seed() -> None:
    from autune_audio.persistence import persist_transcript, transcript_payload
    from autune_audio.speakers import Utterance as SpokenUtterance
    from autune_agent.models import AgentApprover
    from autune_contracts import TRANSCRIPT_READY
    from autune_core import Meeting, Participant, Team, TeamMember, User, publish, session_scope
    from autune_worker.celery_app import celery_app

    celery_app.loader.import_default_modules()
    with session_scope() as s:
        s.add(Team(id=TEAM, name="10/9 관문 팀"))
        for uid, name in ((LEAD, "팀장"), (KIM, "김"), (LEE, "이")):
            s.add(User(id=uid, email=f"{uid}@example.com", display_name=name))
        s.flush()
        for uid in (LEAD, KIM, LEE):
            s.add(TeamMember(team_id=TEAM, user_id=uid))
        s.add(AgentApprover(team_id=TEAM, user_id=LEAD, scope="workload"))
        meeting = Meeting(team_id=TEAM, title="주간 회의",
                          started_at=datetime.now(UTC) - timedelta(days=7))
        s.add(meeting)
        s.flush()
        mid = meeting.id
    spoken = tuple(SpokenUtterance(speaker=sp, start=a, end=e, text=t, words=(), confidence=0.9)
                   for sp, a, e, t in LINES)
    with session_scope() as s:
        persist_transcript(s, meeting_id=mid, utterances=spoken, duration_seconds=10.0,
                           audio_deleted=True)
    with session_scope() as s:
        for p in s.scalars(sa.select(Participant).where(Participant.meeting_id == mid)):
            p.consented = True
            p.user_id = KIM if p.speaker_label == "SPEAKER_00" else LEE
    with session_scope() as s:
        payload = transcript_payload(s, meeting_id=mid).model_dump(mode="json")
    print("meeting", mid, "published to", publish(TRANSCRIPT_READY, payload))


def client(user_id: str) -> httpx.Client:
    from autune_core import SESSION_COOKIE, issue_token

    return httpx.Client(base_url=API, cookies={SESSION_COOKIE: issue_token(user_id)}, timeout=120)


def chat() -> None:
    from autune_core import session_scope
    from autune_extraction.models import ExtActionItem

    with session_scope() as s:
        items = list(s.execute(sa.select(ExtActionItem.id, ExtActionItem.assignee_id,
                                          ExtActionItem.status, ExtActionItem.due_date)))
    print("drafted", len(items), "assignees", sorted({a for _, a, _, _ in items if a}))
    kim = client(KIM)
    for item_id, _, status, _ in items:
        if status == "needs_confirmation":
            r = kim.patch(f"/api/extraction/action-items/{item_id}", json={"status": "todo"})
            print("confirm", item_id, r.status_code)

    lead = client(LEAD)
    t0 = time.monotonic()
    r = lead.post("/api/agent/chat", json={"team_id": TEAM, "message": "업무 몰린 사람 있어?"})
    body = r.json()
    print("chat", r.status_code, "route", body.get("route"), "outcome", body.get("outcome"),
          "proposed", body.get("proposed"), "executed", body.get("executed"),
          f"{time.monotonic() - t0:.1f}s")

    pending = lead.get("/api/agent/pending", params={"team_id": TEAM}).json()
    print("pending", len(pending), [(p["tool"], p["status"]) for p in pending])
    for p in pending:
        r = lead.post(f"/api/agent/pending/{p['id']}/approve")
        print("approve", p["id"], r.status_code, r.json().get("status"), r.json().get("result_ok"))

    with session_scope() as s:
        after = dict(s.execute(sa.select(ExtActionItem.id, ExtActionItem.assignee_id)).all())
    moved = {i: a for i, a in after.items() if a == LEE}
    print("moved to the free member", len(moved), "of", len(after))


if __name__ == "__main__":
    {"seed": seed, "chat": chat}[sys.argv[1]]()
