"""A team, a meeting and one draft item for the signed-in user (throwaway DB)."""

from datetime import UTC, date, datetime, timedelta

import autune_extraction.models  # noqa: F401
from autune_core import Meeting, Team, TeamMember, session_scope
from autune_extraction.models import ExtActionItem

USER = "user_fcc0e128662140c38eba23af7517787b"

with session_scope() as s:
    team = Team(name="Jira 검증팀")
    s.add(team)
    s.flush()
    s.add(TeamMember(team_id=team.id, user_id=USER))
    meeting = Meeting(team_id=team.id, title="Jira 역동기화 검증 회의",
                      started_at=datetime.now(UTC) - timedelta(hours=1), status="complete")
    s.add(meeting)
    s.flush()
    item = ExtActionItem(meeting_id=meeting.id, description="[Autune 검증] Jira 상태 역동기화 확인",
                         status="needs_confirmation", due_date=date.today() + timedelta(days=3),
                         assignee_id=USER, confidence=0.9, origin="model")
    s.add(item)
    s.flush()
    print("TEAM", team.id)
    print("MEETING", meeting.id)
    print("ITEM", item.id)
