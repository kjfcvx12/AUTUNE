"""The meeting summary (#421 v2) against a real model, through the shipped task.

Local only; never committed. Invented meetings only -- nothing of dev's,
nothing of AI Hub's. The user's allowance (2026-10-08): 12 requests at most,
separate from the resolver's 16; the count is kept in ``sent.count`` beside
this file, so it holds across runs.

    measure_summary.py count                 -- every meeting with a fake
                                                provider: requests, nothing sent
    measure_summary.py run <meeting> [noboard]
                                             -- one meeting through
                                                ``tasks.summarize_meeting``

Meetings: ``short`` (the resolver measurement's invented meeting), ``eight``
(the dummy meeting 8), ``long`` (``meeting_long.py``), ``toolong`` (``long``
nine times over; count mode only).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path("F:/0final/AUTUNE")
EXP = ROOT / "dataset" / "experiments"
SRC8 = EXP / "2026-09-26-local-vs-api" / "scratch_e27a3912" / "step1_chunks_overlap_8.json"
ROWS = EXP / "2026-10-08-resolver-rows"
KEY_FP = "c41ba374"
CAP = int(os.environ.get("CAP", "12"))
PACE = 2.0
# The second measurement (the three fixes) has its own allowance of 12.
ROUND = os.environ.get("ROUND", "2")
COUNT = HERE / ("sent.count" if ROUND == "1" else f"sent{ROUND}.count")

mode = sys.argv[1] if len(sys.argv) > 1 else ""
if mode not in ("count", "run"):
    sys.exit(__doc__)

keys = [
    line.split("=", 1)[1].strip().strip('"').strip("'")
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines()
    if line.startswith("AUTUNE_LLM_API_KEY=")
]
prints = [hashlib.sha256(k.encode()).hexdigest()[:8] for k in keys]
print(f"key lines in .env: {len(keys)}; the one read (last): {prints[-1] if prints else None}")
if not keys or prints[-1] != KEY_FP:
    sys.exit("the key the process would read is not the one this was checked against")
os.environ.update(
    AUTUNE_ENV="local",
    AUTUNE_LLM_API_KEY=keys[-1] if mode == "run" else "not-a-key",
    AUTUNE_EXTRACTION_LLM_API_KEY="",
    # What one line in dev's compose would switch on; the models are the defaults.
    AUTUNE_EXTRACTION_SUMMARY_IMPL="llm",
    AUTUNE_EXTRACTION_LLM_ACKNOWLEDGED_392="true",
)

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from structlog.testing import capture_logs  # noqa: E402

from autune_core import Base, Meeting, Participant, TeamMember, User  # noqa: E402
from autune_core import Utterance as StoredUtterance  # noqa: E402
from autune_extraction import service, tasks  # noqa: E402
from autune_extraction.models import ExtActionItem, ExtDecision, ExtMeetingSummary  # noqa: E402
from autune_extraction.pipeline import registry  # noqa: E402
from autune_extraction.pipeline import summary as summary_module  # noqa: E402

sys.path.insert(0, str(HERE))
import meeting_long  # noqa: E402

TEAM = "team_m"


def short_meeting() -> dict:
    src = (ROWS / "measure_rows.py").read_text(encoding="utf-8")
    start = src.index("INVENTED: list")
    end = src.index("\n]\n", start) + 3
    ns: dict = {"K": None, "C": "c", "D": "d"}
    exec(src[start:end].replace("INVENTED: list[tuple[str, K | None, str]]", "INVENTED"), ns)  # noqa: S102
    rows = json.loads((ROWS / "rows.json").read_text(encoding="utf-8"))
    guards = json.loads((ROWS / "rows_guards.json").read_text(encoding="utf-8"))
    return {
        "people": [],
        "lines": [(who, text) for who, _kind, text in ns["INVENTED"]],
        "decisions": [d["written"] or d["said"] for d in rows["decisions"]],
        "items": [
            i["written"] or i["said"] for i in guards["items"] if i["meeting"].startswith("inv")
        ],
    }


def eight() -> dict:
    data = json.loads(SRC8.read_text(encoding="utf-8"))
    seen: dict[int, dict] = {}
    for chunk in data["chunks"]:
        for u in chunk["utterances"]:
            if u["idx"] > 0:
                seen.setdefault(u["idx"], u)
    guards = json.loads((ROWS / "rows_guards.json").read_text(encoding="utf-8"))
    lines = [(str(u["speaker"]), u["text"]) for _, u in sorted(seen.items())]
    return {
        "people": sorted({who for who, _ in lines if who != "전원"}),
        "lines": lines,
        # No decisions: the resolver measurement ran its commitments only.
        "decisions": [],
        "items": [
            i["written"] or i["said"] for i in guards["items"] if not i["meeting"].startswith("inv")
        ],
    }


def long_meeting(times: int = 1) -> dict:
    return {
        "people": meeting_long.PEOPLE,
        "lines": meeting_long.LINES * times,
        "decisions": meeting_long.DECISIONS,
        "items": meeting_long.ITEMS,
    }


MEETINGS = {
    "short": short_meeting,
    "eight": eight,
    "long": long_meeting,
    "toolong": lambda: long_meeting(9),
}


def seeded(meeting: dict, *, board: bool) -> tuple[Session, str]:
    engine = create_engine("sqlite://", poolclass=StaticPool)
    shared = {m.__tablename__ for m in (Meeting, User, TeamMember, Participant, StoredUtterance)}
    tables = [
        t for name, t in Base.metadata.tables.items() if name in shared or name.startswith("ext_")
    ]
    Base.metadata.create_all(engine, tables=tables)
    s = Session(engine)
    mid = "mtg_m"
    s.add(Meeting(id=mid, team_id=TEAM, title="측정용 회의", started_at=datetime(2026, 10, 8, 1, tzinfo=UTC)))
    for n, name in enumerate(meeting["people"]):
        s.add(User(id=f"user_{n}", email=f"p{n}@example.com", display_name=name))
        s.add(TeamMember(team_id=TEAM, user_id=f"user_{n}"))
    speakers = sorted({who for who, _ in meeting["lines"]})
    for n, who in enumerate(speakers):
        s.add(Participant(id=f"par_{n}", meeting_id=mid, speaker_label=who, consented=True))
    for n, (who, text) in enumerate(meeting["lines"]):
        s.add(
            StoredUtterance(
                id=f"utt_{n:04d}",
                meeting_id=mid,
                participant_id=f"par_{speakers.index(who)}",
                speaker_label=who,
                start_sec=float(n),
                end_sec=float(n) + 0.5,
                text=text,
            )
        )
    if board:
        for n, text in enumerate(meeting["decisions"]):
            s.add(ExtDecision(id=f"dec_{n:02d}", meeting_id=mid, statement=text, confidence=0.9, origin="model"))
        for n, text in enumerate(meeting["items"]):
            s.add(
                ExtActionItem(
                    id=f"act_{n:02d}",
                    meeting_id=mid,
                    description=text,
                    status="needs_confirmation",
                    confidence=0.9,
                    origin="model",
                )
            )
    s.commit()
    return s, mid


class Counted:
    """The summarizer's transport, counted: every request is one of the twelve."""

    def __init__(self, inner, *, send: bool) -> None:
        self.inner, self.send = inner, send
        self.calls: list[dict] = []

    def request(self, method: str, path: str, *, json: dict):  # noqa: A002
        prompt = "".join(part["text"] for c in json["contents"] for part in c["parts"])
        model = path.split("/")[2].split(":")[0]
        final = '"overview"' in prompt
        if not self.send:
            answer = (
                '{"overview": "회의입니다.", "points": ["결정: 하나로 했습니다."]}'
                if final
                else '{"points": ["첫째 문장입니다.", "둘째 문장입니다.", "셋째 문장입니다.", "넷째 문장입니다."]}'
            )
            self.calls.append({"model": model, "final": final, "prompt_chars": len(prompt)})
            return {"candidates": [{"content": {"parts": [{"text": answer}]}}]}
        sent = int(COUNT.read_text()) if COUNT.exists() else 0
        if sent >= CAP:
            raise RuntimeError(f"the allowance of {CAP} requests is spent")
        COUNT.write_text(str(sent + 1))
        time.sleep(PACE)
        response = self.inner.request(method, path, json=json)
        text = "".join(
            part.get("text", "")
            for cand in response.get("candidates", [])
            for part in cand.get("content", {}).get("parts", [])
        )
        self.calls.append(
            {
                "model": model,
                "final": final,
                "prompt_chars": len(prompt),
                "prompt": prompt,
                "answer": text,
                "usage": response.get("usageMetadata"),
            }
        )
        return response


def one(name: str, *, board: bool, send: bool) -> dict:
    meeting = MEETINGS[name]()
    session, mid = seeded(meeting, board=board)

    @contextmanager
    def scope():
        yield session
        session.commit()

    tasks.session_scope = scope
    summarizer = registry.get_summarizer()
    assert summarizer is not None
    counted = Counted(summarizer._client, send=send)
    summarizer._client = counted
    tasks.get_summarizer = lambda: summarizer
    lines = service.summary_lines(session, mid)
    board_rows = service.summary_board(session, mid)
    with capture_logs() as logs:
        stored = tasks.summarize_meeting(mid)
    row = session.get(ExtMeetingSummary, mid)
    shown = service.meeting_summary(session, mid).generated if row is not None else None
    return {
        "meeting": name,
        "board": board,
        "lines": len(lines),
        "chars": sum(map(len, lines)),
        "sections": len(summary_module.sections(lines)),
        "board_rows": len(board_rows),
        "board_chars": sum(map(len, board_rows)),
        "requests": len(counted.calls),
        "stored": stored,
        "overview": row.overview if row is not None else None,
        "points": row.points.split("\n") if row is not None and row.points else [],
        "too_long": bool(row.too_long) if row is not None else None,
        "tab_too_long": service.meeting_summary(session, mid).generated_too_long,
        "on_the_tab": shown is not None,
        "model_version": row.model_version if row is not None else None,
        "calls": counted.calls,
        "events": [
            {k: v for k, v in e.items() if k != "log_level"}
            for e in logs
            if e["event"].startswith("extraction_")
        ],
    }


def main() -> None:
    if mode == "count":
        for name in MEETINGS:
            for board in (True, False):
                r = one(name, board=board, send=False)
                print(
                    f"{name:8s} board={'yes' if board else 'no ':3s} lines {r['lines']:4d} chars {r['chars']:6d} "
                    f"sections {r['sections']:2d} board rows {r['board_rows']:2d} ({r['board_chars']} chars) "
                    f"-> requests {r['requests']:2d}, stored {r['stored']}, "
                    f"too long row {r['too_long']} tab {r['tab_too_long']}, "
                    f"events {[e['event'] for e in r['events']]}"
                )
        print("sent so far:", COUNT.read_text() if COUNT.exists() else 0, "of", CAP)
        return
    name = sys.argv[2]
    board = "noboard" not in sys.argv
    if name == "toolong":
        sys.exit("count mode only")
    r = one(name, board=board, send=True)
    out = HERE / f"r{ROUND}_summary_{name}{'' if board else '_noboard'}.json"
    out.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{name}: requests {r['requests']}, stored {r['stored']}; sent so far {COUNT.read_text()} of {CAP}")
    for e in r["events"]:
        print("  ", e)


main()
