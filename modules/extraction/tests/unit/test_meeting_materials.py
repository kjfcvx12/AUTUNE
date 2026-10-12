"""The uploaded materials shown beside one meeting: those nearest its title (#817).

The rules under test (``docs/architecture/privacy.md``, "Uploaded documents are
masked before storage"):

- **live transcript text is not searched against materials** (#817 point 6):
  the question is the meeting's title and nothing else of the meeting, and the
  route takes nothing a caller could put a spoken line in;
- the title is a person's words like any question -- masked before it is
  embedded, and in no answer and no log line;
- what comes back is what a search gives: a title and a screened excerpt of
  masked text for each material, of the meeting's own team only;
- readers of the meeting only, and nothing at all where uploads are off.

Every value here is invented.
"""

from __future__ import annotations

import inspect
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from structlog.testing import capture_logs

from autune_core import Base, Meeting, Team, TeamMember, User, Utterance, get_session
from autune_core.errors import AutuneError
from autune_extraction import material_search, materials
from autune_extraction.config import get_settings
from autune_extraction.material_search import (
    MAX_QUESTION_CHARS,
    near_meeting_title,
    title_question,
)
from autune_extraction.models import MATERIAL_EMBEDDING_DIM, ExtMaterial
from autune_extraction.pipeline import FakeEmbedder
from autune_extraction.router import router

from .conftest import sign_in

TEAM = "team_1"
OTHER = "team_2"
MEETING = "mtg_1"
PREFIX = "/api/extraction"
NEAR = f"{PREFIX}/meetings/{MEETING}/materials/near-title"
STARTED = datetime(2026, 10, 12, 1, 0, tzinfo=UTC)

PHONE = "010-2345-6789"
TITLE = "출시 일정 점검"
LAUNCH = "출시 일정은 11월 둘째 주로 잡는다. 출시 전 점검은 QA 팀이 맡는다.\n"
BUDGET = "예산 집행 내역: 장비 구매 1200만원, 외주 개발 800만원.\n"
# What was said in the meeting: about the budget, which the title is not.
SPOKEN = "예산 집행 내역을 먼저 보죠. 장비 구매가 얼마였나요?"


class Recording(FakeEmbedder):
    """The material fake, keeping every text it was handed."""

    def __init__(self) -> None:
        super().__init__(dim=MATERIAL_EMBEDDING_DIM)
        self.seen: list[str] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.seen.extend(texts)
        return super().embed(texts)


@pytest.fixture(autouse=True)
def no_floor(monkeypatch: pytest.MonkeyPatch) -> None:
    """The fake counts shared characters; its scores mean nothing on the real
    embedder's scale, so no floor here unless a test sets one."""
    monkeypatch.setattr(get_settings(), "material_search_min_similarity", -1.0)


@pytest.fixture
def embedder(monkeypatch: pytest.MonkeyPatch) -> Recording:
    fake = Recording()
    monkeypatch.setattr(materials, "get_material_embedder", lambda: fake)
    monkeypatch.setattr(material_search, "get_material_embedder", lambda: fake)
    return fake


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    shared = {m.__tablename__ for m in (User, Team, TeamMember, Meeting, Utterance)}
    owned = {
        "ext_materials",
        "ext_material_chunks",
        "ext_material_alarms",
        "ext_material_settings",
    }
    tables = [t for name, t in Base.metadata.tables.items() if name in shared | owned]
    Base.metadata.create_all(engine, tables=tables)
    with Session(engine) as s:
        s.add(Meeting(id=MEETING, team_id=TEAM, title=TITLE, started_at=STARTED))
        s.flush()
        yield s


def upload(session: Session, body: str, *, team: str = TEAM, title: str = "자료") -> ExtMaterial:
    return materials.store_upload(
        session, team, title=title, file_name="plan.txt", data=body.encode()
    )


def say(session: Session, text: str, *, uid: str = "utt_1") -> None:
    """A line of the meeting's transcript, as module A stores one."""
    session.add(
        Utterance(
            id=uid,
            meeting_id=MEETING,
            participant_id="par_1",
            speaker_label="화자 1",
            start_sec=0.0,
            end_sec=3.0,
            text=text,
        )
    )
    session.flush()


def retitle(session: Session, title: str) -> None:
    meeting = session.get(Meeting, MEETING)
    assert meeting is not None
    meeting.title = title
    session.flush()


@pytest.fixture
def client(session: Session) -> TestClient:
    app = FastAPI()

    @app.exception_handler(AutuneError)
    async def _render(_: Request, exc: AutuneError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    app.include_router(router, prefix=PREFIX)
    app.dependency_overrides[get_session] = lambda: session
    sign_in(app, session, team_id=TEAM)
    return TestClient(app)


@pytest.fixture
def enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "material_upload", True)


# --- the question -----------------------------------------------------------------


def test_the_question_is_the_title_with_its_spaces_folded_and_cut() -> None:
    assert title_question("  출시\t일정 \n 점검  ") == TITLE
    assert title_question(None) == "" and title_question(" \n ") == ""
    long = title_question("가나 " * 200)
    assert len(long) <= MAX_QUESTION_CHARS and not long.endswith(" ")


def test_the_nearest_material_to_the_title_comes_first(
    session: Session, embedder: Recording
) -> None:
    launch = upload(session, LAUNCH * 3, title="출시 계획")
    budget = upload(session, BUDGET * 3, title="예산")

    answer = near_meeting_title(session, TEAM, MEETING)

    assert answer is not None
    assert [hit.material_id for hit in answer.hits] == [launch.id, budget.id]
    assert "출시 일정" in answer.hits[0].excerpt


def test_a_meeting_with_no_title_is_not_searched(session: Session, embedder: Recording) -> None:
    upload(session, LAUNCH)
    embedder.seen.clear()
    retitle(session, "   ")

    assert near_meeting_title(session, TEAM, MEETING) is None
    assert embedder.seen == []


# --- nothing said in the meeting is searched with -----------------------------------


def test_what_was_said_in_the_meeting_never_reaches_the_question(
    session: Session, embedder: Recording
) -> None:
    """privacy.md: live transcript text is not searched against materials.
    The meeting talks about the budget; its title is about the launch. What
    the embedder is asked with is the title, and the material that answers
    the talk does not come first."""
    launch = upload(session, LAUNCH * 3, title="출시 계획")
    upload(session, BUDGET * 3, title="예산")
    say(session, SPOKEN)
    say(session, f"담당자 번호는 {PHONE} 입니다.", uid="utt_2")
    embedder.seen.clear()

    with capture_logs() as logs:
        answer = near_meeting_title(session, TEAM, MEETING)

    assert embedder.seen == [TITLE]
    assert answer is not None and answer.hits[0].material_id == launch.id
    said = repr(embedder.seen) + repr(logs)
    assert "장비 구매가" not in said and "먼저 보죠" not in said and PHONE not in said


def test_the_search_by_title_is_handed_the_title_alone(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Held at the call, whatever the embedder: one question, and it is the
    folded title."""
    say(session, SPOKEN)
    asked: list[tuple[str, str]] = []

    def spy(_: Session, team_id: str, query: str, **__: object) -> None:
        asked.append((team_id, query))

    monkeypatch.setattr(material_search, "search_materials", spy)

    near_meeting_title(session, TEAM, MEETING)

    assert asked == [(TEAM, TITLE)]


def test_the_search_by_title_reads_no_transcript_table() -> None:
    """The function and the route name the meeting's title and no row of
    what was said: an import of the transcript's model into either would be
    the first step of searching with it."""
    from autune_extraction import router as routes

    for source in (
        inspect.getsource(near_meeting_title),
        inspect.getsource(routes.materials_near_title),
    ):
        assert "Utterance" not in source and "aud_" not in source
    assert "Utterance" not in vars(material_search)


def test_the_route_takes_the_meetings_id_and_nothing_a_line_could_ride_in(
    client: TestClient,
) -> None:
    """No body and no query parameter: a caller has nowhere to put a spoken
    line for the server to search with."""
    [route] = [r for r in router.routes if getattr(r, "path", "").endswith("/materials/near-title")]
    assert route.methods == {"GET"}  # type: ignore[attr-defined]
    dependant = route.dependant  # type: ignore[attr-defined]
    assert [p.name for p in dependant.path_params] == ["meeting_id"]
    assert dependant.query_params == [] and dependant.body_params == []

    schema = client.app.openapi()  # type: ignore[attr-defined]
    operation = schema["paths"][f"{PREFIX}/meetings/{{meeting_id}}/materials/near-title"]["get"]
    assert "requestBody" not in operation
    # Whatever a dependency adds too: who is asking rides in a header or a
    # cookie, and nothing rides in the address but the meeting's id.
    carried = {(p["in"], p["name"]) for p in operation["parameters"]}
    assert {where for where, _ in carried} <= {"path", "header", "cookie"}
    assert {name for where, name in carried if where == "path"} == {"meeting_id"}


@pytest.mark.usefixtures("enabled")
def test_a_line_sent_along_with_the_request_changes_nothing(
    client: TestClient, session: Session, embedder: Recording
) -> None:
    upload(session, LAUNCH * 3, title="출시 계획")
    upload(session, BUDGET * 3, title="예산")
    embedder.seen.clear()

    plain = client.get(NEAR)
    embedder.seen.clear()
    carried = client.request(
        "GET", f"{NEAR}?question={SPOKEN}&q={SPOKEN}", json={"question": SPOKEN}
    )

    assert carried.status_code == 200 and carried.json() == plain.json()
    assert embedder.seen == [TITLE]


# --- the title is a person's words --------------------------------------------------


def test_the_title_is_masked_before_it_is_embedded_and_kept_nowhere(
    session: Session, embedder: Recording
) -> None:
    upload(session, LAUNCH)
    embedder.seen.clear()
    retitle(session, f"출시 일정 담당 {PHONE}")

    with capture_logs() as logs:
        answer = near_meeting_title(session, TEAM, MEETING)

    [embedded] = embedder.seen
    assert PHONE not in embedded and "출시 일정" in embedded
    said = repr(answer) + repr(logs)
    assert PHONE not in said and "담당" not in said
    assert [line["event"] for line in logs] == ["extraction_material_searched"]
    assert set(logs[0]) == {"event", "team_id", "hits", "dropped", "log_level"}


# --- the route --------------------------------------------------------------------


def test_off_with_uploads_the_route_is_not_there(client: TestClient) -> None:
    answer = client.get(NEAR)

    assert answer.status_code == 404 and "error" not in answer.json()


@pytest.mark.usefixtures("enabled")
def test_a_reader_gets_the_materials_near_the_title_and_what_a_typed_question_needs(
    client: TestClient, session: Session, embedder: Recording
) -> None:
    row = upload(session, LAUNCH, title="출시 계획")

    with capture_logs() as logs:
        answer = client.get(NEAR)

    assert answer.status_code == 200
    body = answer.json()
    assert set(body) == {"team_id", "asked", "hits", "notice", "more", "max_question_chars"}
    assert (body["team_id"], body["asked"], body["more"]) == (TEAM, True, False)
    assert body["max_question_chars"] == MAX_QUESTION_CHARS
    [hit] = body["hits"]
    assert (hit["material_id"], hit["title"], hit["position"]) == (row.id, "출시 계획", 0)
    assert "출시 일정" in hit["excerpt"]
    # The title is the reader's already; the answer and the log do not repeat it.
    assert TITLE not in answer.text.replace(hit["excerpt"], "")
    assert TITLE not in repr(logs)


@pytest.mark.usefixtures("enabled")
def test_a_meeting_with_no_title_answers_that_nothing_was_asked(
    client: TestClient, session: Session, embedder: Recording
) -> None:
    upload(session, LAUNCH)
    retitle(session, "")

    body = client.get(NEAR).json()

    assert (body["asked"], body["hits"], body["notice"], body["more"]) == (False, [], None, False)
    assert body["team_id"] == TEAM


@pytest.mark.usefixtures("enabled")
def test_only_the_meetings_own_teams_uploads_are_read(
    client: TestClient, session: Session, embedder: Recording
) -> None:
    session.add(Team(id=OTHER, name="다른 팀"))
    ours = upload(session, BUDGET, title="우리 예산")
    upload(session, LAUNCH, team=OTHER, title="남의 출시")

    body = client.get(NEAR).json()

    assert [hit["material_id"] for hit in body["hits"]] == [ours.id]
    assert "남의" not in repr(body) and "출시 일정은" not in repr(body)


@pytest.mark.usefixtures("enabled")
def test_somebody_not_on_the_meetings_team_gets_the_404_of_an_unknown_meeting(
    client: TestClient, session: Session, embedder: Recording
) -> None:
    session.add(Meeting(id="mtg_other", team_id=OTHER, title=TITLE, started_at=STARTED))
    upload(session, LAUNCH, team=OTHER)
    session.flush()

    theirs = client.get(f"{PREFIX}/meetings/mtg_other/materials/near-title")
    unknown = client.get(f"{PREFIX}/meetings/mtg_none/materials/near-title")

    assert theirs.status_code == unknown.status_code == 404
    assert theirs.json()["error"]["code"] == unknown.json()["error"]["code"] == "not_found"
    assert "출시 일정은" not in theirs.text


@pytest.mark.usefixtures("enabled")
def test_an_upload_past_its_day_is_not_shown_beside_the_meeting(
    client: TestClient, session: Session, embedder: Recording
) -> None:
    row = upload(session, LAUNCH)
    row.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    session.flush()

    assert client.get(NEAR).json()["hits"] == []
