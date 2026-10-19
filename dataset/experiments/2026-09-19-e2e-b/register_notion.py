"""Connect a team to Notion for a local demo (not committed; dataset/ is gitignored).

Writing ``team_integrations`` is the settings layer's job (screen S28), which does
not exist yet, so module B's code never does it. This is the stand-in for a demo:
it stores the Notion token and the two database ids from ``.env`` as the team's
integration, the way S28 would.

    # AUTUNE_DATABASE_URL and AUTUNE_ENCRYPTION_KEY must be the ones the API and
    # worker use -- the secret is encrypted with that key.
    python register_notion.py --meeting mtg_...      # the meeting's team
    python register_notion.py --team team_...

Prints the stored config's repr (``secret=<set>``), never the token.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from autune_core import Meeting, session_scope
from autune_core.integrations_config import load_integration, save_integration

ENV = Path(__file__).resolve().parents[3] / ".env"


def notion_env() -> dict[str, str]:
    values = {}
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("AUTUNE_NOTION") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value.strip().strip('"')
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--meeting")
    target.add_argument("--team")
    args = parser.parse_args()

    env = notion_env()
    missing = [k for k in ("AUTUNE_NOTION_TOKEN", "AUTUNE_NOTION_ACTION_DB_ID") if not env.get(k)]
    if missing:
        raise SystemExit(f"missing in .env: {', '.join(missing)}")

    with session_scope() as session:
        team_id = args.team
        if args.meeting:
            meeting = session.get(Meeting, args.meeting)
            if meeting is None:
                raise SystemExit(f"no meeting {args.meeting}")
            team_id = meeting.team_id
        config = {"action_db_id": env["AUTUNE_NOTION_ACTION_DB_ID"]}
        if env.get("AUTUNE_NOTION_DECISION_DB_ID"):
            config["decision_db_id"] = env["AUTUNE_NOTION_DECISION_DB_ID"]
        save_integration(session, team_id, "notion", secret=env["AUTUNE_NOTION_TOKEN"], config=config)

    with session_scope() as session:
        print(repr(load_integration(session, team_id, "notion")))


if __name__ == "__main__":
    main()
