"""Republish TranscriptReady for an existing meeting (redelivery check)."""
import sys, time
from autune_worker import celery_app
celery_app.loader.import_default_modules()
from autune_audio.persistence import transcript_payload
from autune_contracts.events import TRANSCRIPT_READY
from autune_core import session_scope
from autune_core.events import publish
mid = sys.argv[1]
with session_scope() as s:
    payload = transcript_payload(s, meeting_id=mid).model_dump(mode="json")
print(publish(TRANSCRIPT_READY, payload))
