"""9/30 end-to-end check on main (not committed): module A's recording S1-S4, as its
script text, through A's real persistence, then B (llm classifier), C, D, E on a
real Celery worker, and the team's Notion connected to the existing AUTUNE page's
databases so a confirm creates a page.

No ffmpeg on this PC, so transcription is skipped: the utterances are the cue
sheet's text (dataset/0/label.txt), not Whisper's output. Team-written dummy
script -- fine for the free-tier Gemini key (#392). Prints ids and counts only.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import time
from datetime import UTC, datetime

import sqlalchemy as sa

from autune_worker import celery_app

celery_app.loader.import_default_modules()

from autune_audio.persistence import persist_transcript, transcript_payload
from autune_audio.speakers import Utterance as Spoken
from autune_contracts.events import TRANSCRIPT_READY
from autune_core import Meeting, session_scope
from autune_core.entities import Participant
from autune_core.events import publish
from autune_core.integrations_config import save_integration
from autune_extraction.models import ExtActionItem, ExtClassification, ExtDecision
from autune_intelligence.models import IntelCompletion

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parents[2]
LABEL = ROOT / "dataset" / "0" / "label.txt"

import sys

sys.path.insert(0, str(ROOT / "dataset" / "extraction_eval_pilot"))
spec = importlib.util.spec_from_file_location("add_s4", ROOT / "dataset" / "extraction_eval_pilot" / "add_s4.py")
add_s4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(add_s4)

# S2's roles; S1's template has [role] and [name] slots each reader fills in.
ROLE = {"박준호": "오디오 파이프라인", "이지훈": "구조화 추출", "최유나": "갭 탐지랑 회의 맥락 엔진", "김서연": "인텔리전스 대시보드"}
LABELS = {name: f"SPEAKER_{i:02d}" for i, name in enumerate(ROLE)}


def s1_to_s3(lines: list[str]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    s1 = lines[lines.index("S1") : lines.index("S2")]
    template = next(line for line in s1 if line.startswith("안녕하세요"))
    for name, role in ROLE.items():
        out.append((name, template.replace("[구조화 추출]", role).replace("[이지훈]", name)))
    for section, nxt in (("S2", "S3"), ("S3", "S4")):
        block = lines[lines.index(section) : lines.index(nxt)]
        for i, line in enumerate(block):
            head = line.split(" · ")[0].strip()
            if head in ROLE and i + 2 < len(block):
                out.append((head, block[i + 2].strip()))
    return out


lines = LABEL.read_text(encoding="utf-8").splitlines()
turns = s1_to_s3(lines) + [(r["speaker"], r["text"]) for r in add_s4.parse(LABEL)]
spoken = tuple(
    Spoken(speaker=LABELS[s], start=i * 8.0, end=i * 8.0 + 7.0, text=t, words=(), confidence=0.9)
    for i, (s, t) in enumerate(turns)
)
print(f"turns={len(turns)} (S1-S3 {len(turns) - 50}, S4 50)")

token = json.loads((HERE / "token.json").read_text())
team_id = token["team_id"]

env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
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
            "parent_page_id": "3e31da48e00c80bcad58f892c89757e4",
            "action_db_id": "3e91da48e00c81dcb6b9f489379bff9b",
            "decision_db_id": "3e91da48e00c81779870f3001ee567e3",
        },
    )
print("notion connected (existing AUTUNE page databases)")

with session_scope() as s:
    meeting = Meeting(
        team_id=team_id,
        title="오튠 음성 평가 녹음 S1-S4 (더미 대본)",
        started_at=datetime(2026, 9, 18, 5, 10, tzinfo=UTC),  # the script's own "9월 18일 오후 2시 10분"
    )
    s.add(meeting)
    s.flush()
    mid = meeting.id
with session_scope() as s:
    persist_transcript(s, meeting_id=mid, utterances=spoken, duration_seconds=697.1, audio_deleted=True)
with session_scope() as s:
    for p in s.scalars(sa.select(Participant).where(Participant.meeting_id == mid)):
        p.consented = True
with session_scope() as s:
    payload = transcript_payload(s, meeting_id=mid).model_dump(mode="json")
print("published ->", publish(TRANSCRIPT_READY, payload))

t0 = time.monotonic()
while time.monotonic() - t0 < 600:
    with session_scope() as s:
        intel = s.get(IntelCompletion, mid)
        if intel is not None and intel.extraction_at is not None:
            break
    time.sleep(3)
with session_scope() as s:
    items = s.scalar(sa.select(sa.func.count()).select_from(ExtActionItem).where(ExtActionItem.meeting_id == mid))
    decisions = s.scalar(sa.select(sa.func.count()).select_from(ExtDecision).where(ExtDecision.meeting_id == mid))
    kinds = s.execute(
        sa.select(ExtClassification.kind, sa.func.count())
        .where(ExtClassification.meeting_id == mid)
        .group_by(ExtClassification.kind)
    ).all()
print(f"meeting={mid} items={items} decisions={decisions} after {time.monotonic() - t0:.1f}s")
print("kinds:", {str(k): n for k, n in kinds})
(HERE / "meeting.txt").write_text(mid)
