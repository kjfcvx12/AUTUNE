"""Seed the web demo (not committed): one invented meeting in the dev token's team,
run through the real pipeline with the LLM classifier, plus the team's Notion
connection read from the repo's .env so a confirm on the board can create a page.

Dummy meeting only -- the Gemini key is free tier (#392). Prints ids and counts,
never the Notion token.
"""

from __future__ import annotations

import json
import pathlib
import time
from datetime import UTC, datetime

import sqlalchemy as sa

from autune_worker import celery_app

celery_app.loader.import_default_modules()

from autune_audio.persistence import persist_transcript, transcript_payload
from autune_contracts.events import TRANSCRIPT_READY
from autune_core import Meeting, session_scope
from autune_core.entities import Participant
from autune_core.events import publish
from autune_core.integrations_config import save_integration
from autune_extraction.models import ExtActionItem, ExtDecision
from autune_intelligence.models import IntelCompletion

HERE = pathlib.Path(__file__).parent
spec = __import__("importlib.util").util.spec_from_file_location("e2e_llm_lines", HERE / "lines.py")
lines = __import__("importlib.util").util.module_from_spec(spec)
spec.loader.exec_module(lines)

team_id = json.loads((HERE / "token.json").read_text())["team_id"]

env = {}
for line in (HERE.parents[2] / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"')

with session_scope() as s:
    save_integration(
        s,
        team_id,
        "notion",
        secret=env["AUTUNE_NOTION_TOKEN"],
        config={
            "action_db_id": env["AUTUNE_NOTION_ACTION_DB_ID"],
            "decision_db_id": env["AUTUNE_NOTION_DECISION_DB_ID"],
        },
    )
print("notion connected for the demo team")

with session_scope() as s:
    meeting = Meeting(team_id=team_id, title="결제 페이지 개편 점검 (더미)", started_at=datetime.now(UTC))
    s.add(meeting)
    s.flush()
    mid = meeting.id
with session_scope() as s:
    persist_transcript(s, meeting_id=mid, utterances=lines.SPOKEN, duration_seconds=150.0, audio_deleted=True)
with session_scope() as s:
    for p in s.scalars(sa.select(Participant).where(Participant.meeting_id == mid)):
        p.consented = True
with session_scope() as s:
    payload = transcript_payload(s, meeting_id=mid).model_dump(mode="json")
print("published ->", publish(TRANSCRIPT_READY, payload))

t0 = time.monotonic()
while time.monotonic() - t0 < 300:
    with session_scope() as s:
        intel = s.get(IntelCompletion, mid)
        if intel is not None and intel.extraction_at is not None:
            break
    time.sleep(3)
with session_scope() as s:
    items = s.scalar(sa.select(sa.func.count()).select_from(ExtActionItem).where(ExtActionItem.meeting_id == mid))
    decisions = s.scalar(sa.select(sa.func.count()).select_from(ExtDecision).where(ExtDecision.meeting_id == mid))
print(f"meeting={mid} items={items} decisions={decisions} after {time.monotonic() - t0:.1f}s")
(HERE / "demo_meeting.txt").write_text(mid)
