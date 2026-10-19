"""Invented data for a browser check of the carried-over popup and the summary tab.

Writes one team, one user, two meetings (a week ago and today), open items on
the earlier meeting (one overdue), decisions and items on today's meeting, two
open-question labels and one unanswered ambiguous agreement. Prints the ids and
a session token for the invented user (throwaway DB only).
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import autune_extraction.models  # noqa: F401
from autune_core import Meeting, Team, TeamMember, User, Utterance, session_scope
from autune_core.auth import issue_token
from autune_extraction.models import (
    ExtActionItem,
    ExtClassification,
    ExtConfirmation,
    ExtDecision,
    ExtDecisionReview,
)

now = datetime.now(UTC)
today = date.today()

with session_scope() as s:
    team = Team(name="검증팀")
    me = User(email="checker@example.com", display_name="김검증")
    lee = User(email="lee@example.com", display_name="이승환")
    s.add_all([team, me, lee])
    s.flush()
    s.add_all([TeamMember(team_id=team.id, user_id=u.id) for u in (me, lee)])
    last = Meeting(team_id=team.id, title="지난주 스프린트 회의", started_at=now - timedelta(days=7), status="complete")
    this = Meeting(team_id=team.id, title="이번 주 스프린트 회의", started_at=now - timedelta(hours=2), status="complete")
    s.add_all([last, this])
    s.flush()

    def item(meeting, desc, status, *, due=None, who=None):
        s.add(ExtActionItem(meeting_id=meeting.id, description=desc, status=status, due_date=due,
                            assignee_id=who.id if who else None, confidence=0.9, origin="model"))

    item(last, "결제 로그 필드 추가 작업 마무리", "todo", due=today - timedelta(days=2), who=lee)
    item(last, "온보딩 문서 초안 공유", "in_progress", due=today + timedelta(days=3), who=me)
    item(last, "고객 인터뷰 일정 잡기", "todo", who=lee)
    item(last, "지난 분기 회고 정리", "done", who=me)
    item(this, "검색 정렬 A/B 테스트 설계", "needs_confirmation", due=today + timedelta(days=5), who=me)
    item(this, "배포 체크리스트 업데이트", "todo", due=today + timedelta(days=1), who=lee)

    d1 = ExtDecision(meeting_id=this.id, statement="검색 결과는 인기순으로 정렬하기로 결정", confidence=0.9)
    d2 = ExtDecision(meeting_id=this.id, statement="배포는 다음 주 화요일로 미루기로 결정", confidence=0.8)
    s.add_all([d1, d2])
    s.flush()
    s.add(ExtDecisionReview(decision_id=d1.id, meeting_id=this.id, status="confirmed"))
    for n, (uid, text) in enumerate(
        [("utt_q0", "예산은 언제 확정되나요"), ("utt_q1", "디자인 시안은 누가 보나요"), ("utt_amb0", "한번 볼게요")]
    ):
        s.add(Utterance(id=uid, meeting_id=this.id, speaker_label="S1", start_sec=n * 5.0,
                        end_sec=n * 5.0 + 3, text=text))
    s.flush()
    for n in range(2):
        s.add(ExtClassification(utterance_id=f"utt_q{n}", meeting_id=this.id, kind="open_question",
                                confidence=0.9, model_version="seed", nli_verified=False))
    s.add(ExtConfirmation(utterance_id="utt_amb0", meeting_id=this.id, reason="weak_assent"))
    ids = {"team": team.id, "user": me.id, "last": last.id, "this": this.id}

print("IDS", ids)
print("TOKEN", issue_token(ids["user"]))
