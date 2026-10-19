"""PATCH the check item's status through the API, as the board does, then show state."""

import subprocess
import sys
import time

import httpx

from autune_core.auth import issue_token

USER = "user_fcc0e128662140c38eba23af7517787b"
ITEM = "act_336387e2e0164908b0ccb8665b3ff408"

r = httpx.patch(
    f"http://127.0.0.1:8000/api/extraction/action-items/{ITEM}",
    json={"status": sys.argv[1]},
    headers={"Authorization": f"Bearer {issue_token(USER)}"},
    timeout=60,
)
print("PATCH", sys.argv[1], r.status_code)
time.sleep(8)
subprocess.run([sys.executable, sys.argv[0].replace("jira_patch.py", "jira_step.py"), "state"], check=False)
