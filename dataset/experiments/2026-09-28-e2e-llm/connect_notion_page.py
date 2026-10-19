"""Create the action-item and decision databases under a Notion page and connect
the demo team to them (not committed). Reuses #402's dev-route code from its
worktree, so the databases get exactly the property names the sync writes.

    python connect_notion_page.py <notion page URL or id>

The page must be shared with the integration first. Prints ids only.
"""

from __future__ import annotations

import json
import pathlib
import sys

import httpx

HERE = pathlib.Path(__file__).parent
WTDEV = pathlib.Path(
    r"C:\Users\hi\AppData\Local\Temp\claude\F--0final-AUTUNE"
    r"\68a23cb4-22e8-4a86-b550-caba1ee7c470\scratchpad\wtdev\modules\extraction\src"
)
sys.path.insert(0, str(WTDEV))

from autune_core import session_scope  # noqa: E402
from autune_core.integrations_config import save_integration  # noqa: E402
from autune_extraction.dev import routes  # noqa: E402
from autune_extraction.service import DECISION_NOTION_PROPERTIES, NOTION_PROPERTIES  # noqa: E402

env = {}
for line in (HERE.parents[2] / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"')

page_id = routes._parse_page_id(sys.argv[1])
team_id = json.loads((HERE / "token.json").read_text())["team_id"]
with httpx.Client(
    base_url=routes.NOTION_API,
    headers={
        "Authorization": f"Bearer {env['AUTUNE_NOTION_TOKEN']}",
        "Notion-Version": routes.NOTION_VERSION,
        "Content-Type": "application/json",
    },
    timeout=15,
) as client:
    action_db = routes._create_database(
        client, page_id=page_id, title="액션 아이템", names=dict(NOTION_PROPERTIES), status_select=True
    )
    decision_db = routes._create_database(
        client, page_id=page_id, title="결정", names=dict(DECISION_NOTION_PROPERTIES), status_select=False
    )
with session_scope() as s:
    save_integration(
        s,
        team_id,
        "notion",
        secret=env["AUTUNE_NOTION_TOKEN"],
        config={"action_db_id": action_db, "decision_db_id": decision_db, "parent_page_id": page_id},
    )
print("created action db", action_db, "decision db", decision_db)
