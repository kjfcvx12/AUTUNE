"""Steps of the real-Jira check. Prints ids, statuses and categories only.

  confirm  -- PATCH the item to todo through the API, as the board does (the
              router then syncs it to Jira in the background)
  state    -- the item's status, its Jira key and synced_category, Jira's category
  move X   -- move the issue to category X (new/indeterminate/done) in Jira
  board X  -- set the item's status on the board directly, without syncing
  pull     -- run the periodic read-back task once
"""

import sys
import time

import httpx
from sqlalchemy import select

import autune_extraction.models  # noqa: F401
from autune_core import jira_access, session_scope
from autune_core.auth import issue_token
from autune_extraction import jira_sync, tasks
from autune_extraction.models import ExtActionItem, ExtEditEvent, ExtExternalRef
from autune_integrations import JiraClient

USER = "user_fcc0e128662140c38eba23af7517787b"
TEAM = "team_d9e343d7ff174fcd982b4df92923facc"
ITEM = "act_336387e2e0164908b0ccb8665b3ff408"


def jira() -> JiraClient:
    access = jira_access(TEAM)
    assert access is not None, "no Jira access"
    return JiraClient.for_cloud(access.access_token, access.cloud_id)


def state() -> None:
    with session_scope() as s:
        item = s.get(ExtActionItem, ITEM)
        ref = s.get(ExtExternalRef, (ITEM, jira_sync.JIRA))
        edits = s.scalars(select(ExtEditEvent.fields).where(ExtEditEvent.action_item_id == ITEM)).all()
        key = ref.external_id if ref else None
        print("board status:", item.status, "| key:", key, "| synced_category:", ref.synced_category if ref else None,
              "| edit events:", list(edits))
    if key:
        client = jira()
        try:
            print("jira category:", client.status_category(key))
        finally:
            client.close()


cmd = sys.argv[1]
if cmd == "confirm":
    r = httpx.patch(f"http://127.0.0.1:8000/api/extraction/action-items/{ITEM}", json={"status": "todo"},
                    headers={"Authorization": f"Bearer {issue_token(USER)}"}, timeout=60)
    print("PATCH", r.status_code)
    time.sleep(8)
    state()
elif cmd == "state":
    state()
elif cmd == "move":
    with session_scope() as s:
        key = s.get(ExtExternalRef, (ITEM, jira_sync.JIRA)).external_id
    client = jira()
    try:
        print("moved:", client.move_to_category(key, sys.argv[2]))
    finally:
        client.close()
    state()
elif cmd == "board":
    with session_scope() as s:
        s.get(ExtActionItem, ITEM).status = sys.argv[2]
    state()
elif cmd == "pull":
    tasks.pull_jira_changes()
    state()
