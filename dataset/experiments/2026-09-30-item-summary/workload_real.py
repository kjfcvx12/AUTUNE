"""Run the real Workload subagent with B's real tools on a real Postgres.

Seeds one team of invented people: 박지영 holds 8 confirmed open items (2 overdue),
김민경 holds 3, 이승환 holds none. Then one run through the main agent, scoped to
that team, and one scoped to ANOTHER team to see that nothing crosses.
Everything printed is invented.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.orm import Session

import autune_core.entities  # noqa: F401
import autune_extraction.models  # noqa: F401
from autune_agent.main import CallBudget, RunScope, collect_subagents, collect_tools, run
from autune_agent.testing import FakeRouter
from autune_core import Meeting, Team, TeamMember, User, get_settings
from autune_extraction.models import ExtActionItem

engine = sa.create_engine(get_settings().database_url)


def seed(session: Session) -> tuple[str, str]:
    team, other = Team(name="A팀"), Team(name="B팀")
    users = {
        n: User(email=f"{n}@example.com", display_name=n) for n in ("박지영", "김민경", "이승환", "타팀원")
    }
    session.add_all([team, other, *users.values()])
    session.flush()
    for n in ("박지영", "김민경", "이승환"):
        session.add(TeamMember(team_id=team.id, user_id=users[n].id))
    session.add(TeamMember(team_id=other.id, user_id=users["타팀원"].id))
    meeting = Meeting(team_id=team.id, title="주간 회의", started_at=datetime.now(UTC) - timedelta(days=3))
    other_meeting = Meeting(team_id=other.id, title="다른 팀 회의", started_at=datetime.now(UTC) - timedelta(days=3))
    session.add_all([meeting, other_meeting])
    session.flush()

    def item(owner: str, n: int, *, late: bool = False, m: Meeting = meeting) -> None:
        session.add(
            ExtActionItem(
                meeting_id=m.id,
                description=f"{owner}의 할 일 {n}",
                assignee_id=users[owner].id,
                due_date=date.today() - timedelta(days=2) if late else date.today() + timedelta(days=5),
                status="todo",
                confidence=0.9,
                origin="user",
            )
        )

    for n in range(8):
        item("박지영", n, late=n < 2)
    for n in range(3):
        item("김민경", n)
    for n in range(4):
        item("타팀원", n, m=other_meeting)
    session.flush()
    return team.id, other.id


with Session(engine) as session:
    team_id, other_id = seed(session)
    session.commit()

    subagents = collect_subagents()
    tools = collect_tools()
    print("subagents on main:", sorted(subagents))
    print("workload tools registered:", sorted(t for t in tools if t.startswith("extraction.")))

    def go(label: str, team: str) -> None:
        budget = CallBudget()
        state = run(
            "팀 업무 분배를 정리해 주세요",
            session=session,
            router=FakeRouter({"업무": "workload"}),
            scope=RunScope(team_id=team, meeting_id=None),
            subagents={"workload": subagents["workload"]},
            tools=tools,
            budget=budget,
        )
        outcome = state["outcome"]
        print(f"\n== {label}")
        print("ok:", outcome.result.ok, "| summary:", outcome.result.summary)
        dumped = outcome.model_dump()
        print("  fields:", sorted(dumped))
        for key in ("proposed_actions", "actions", "proposals"):
            for a in dumped.get(key, []) or []:
                print("  proposal:", {k: a[k] for k in a if k in ("tool", "title", "rationale", "arguments", "level")})
        for f in dumped["result"].get("items", []):
            print("  finding:", f.get("title"), "|", f.get("summary", "")[:90])
        print("  tool calls:", [(s["tool"], s["ok"]) for s in budget.steps])

    go("scoped to the seeded team", team_id)
    go("scoped to the OTHER team (4 items of one person)", other_id)

    # The reassign write: never run by the subagent, only proposed.
    n_before = session.scalar(sa.select(sa.func.count()).select_from(ExtActionItem))
    print("\nitems in the database:", n_before, "(the run must not have written any)")

    # Clean up what the script wrote.
    session.rollback()
    for model in (ExtActionItem,):
        session.execute(sa.delete(model))
    session.execute(sa.delete(Meeting))
    session.execute(sa.delete(TeamMember))
    session.execute(sa.delete(User))
    session.execute(sa.delete(Team))
    session.commit()
