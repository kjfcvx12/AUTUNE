"""Which of my existing labels might change under the 2026-09-17 boundary rules?

    python scan.py

A keyword screen, not a relabelling: it flags rows whose text *looks like* one of
the new cases and whose current label disagrees with that case. A person decides.
Writes <set>/<meeting>.flags.csv (row, current kind, rule id -- no text) and
prints counts only. AI Hub text never leaves this machine.
"""

from __future__ import annotations

import csv
import glob
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SETS = {
    "blind1": "dataset/extraction_eval_blind/*[0-9].B.csv",
    "decision_probe": "dataset/experiments/2026-09-15-decision-probe/score_input/*.B.csv",
    "pilot": "dataset/extraction_eval_pilot/*.R.csv",
    "commitment_probe_train": "dataset/experiments/2026-09-12-commitment-probe/sheets*/*.R.csv",
}

RECALL = re.compile(r"지난\s*(번|회의|주|달|시간)|저번|전에\s*(말씀|얘기|정한|하기로)|하기로\s*했었|정했었|말씀드렸던|약속드렸던")
ESTIMATE = re.compile(r"예상|추정|전망|정도\s*(될|로\s*보)|것으로\s*보")
SETTLE = re.compile(r"하기로\s*(하|했)|걸로\s*(하|가|정리)|로\s*확정|합시다|하시죠|하죠\b|로\s*하겠습니다")
SELF = re.compile(r"(제가|저희가|저희\s*쪽에서|제\s*쪽에서)")
VOLUNTEER = re.compile(r"알아보|알아볼|확인해\s*(보|볼|드리)|챙기|찾아보|정리해\s*(보|드리)")
OTHER_TEAM = re.compile(r"(팀|부서|과|국|실|측|쪽)(에서|이|가)\s.*(하기로|할\s*예정|한다고|하겠다고)")
OWN = re.compile(r"저희|제가|우리")
PROPOSAL_END = re.compile(r"(하죠|합시다|하시죠|하도록\s*하겠습니다|로\s*하겠습니다|걸로\s*하겠습니다)[.?!\s]*$")


def rules(r: dict, nxt: list[dict]) -> list[str]:
    k, t, role = r["kind"], r["text"], r.get("role", "")
    out = []
    if RECALL.search(t) and k in ("decision", "none", "ambiguous"):
        out.append("R2 recall -> commitment")
    if k == "decision" and ESTIMATE.search(t) and not SETTLE.search(t):
        out.append("R4 estimate -> none")
    if k == "ambiguous" and SELF.search(t) and VOLUNTEER.search(t):
        out.append("R5 self-volunteer -> commitment")
    if k in ("commitment", "none") and OTHER_TEAM.search(t) and not OWN.search(t):
        out.append("R6 relay -> ambiguous")
    if k == "commitment" and SETTLE.search(t) and not SELF.search(t):
        out.append("R-assign settled -> decision")
    if k in ("none", "open_question") and PROPOSAL_END.search(t) and role == "사회자":
        replied = any(n["speaker"] != r["speaker"] for n in nxt)
        out.append("R1 chair proposal -> decision?" + ("" if not replied else " (someone spoke next)"))
    return out


def main() -> None:
    total: dict[str, Counter] = defaultdict(Counter)
    for name, pattern in SETS.items():
        out_dir = HERE / name
        out_dir.mkdir(exist_ok=True)
        for path in sorted(glob.glob(str(ROOT / pattern))):
            with open(path, encoding="utf-8-sig", newline="") as fh:
                rows = sorted(csv.DictReader(fh), key=lambda r: int(r["row"]))
            flags = []
            for i, r in enumerate(rows):
                if not r.get("kind", "").strip() or ("reviewed" in r and not r["reviewed"].strip()):
                    continue
                total[name]["labelled"] += 1
                for rule in rules(r, rows[i + 1 : i + 3]):
                    total[name][rule] += 1
                    flags.append({"row": r["row"], "kind": r["kind"], "rule": rule})
            if flags:
                meeting = Path(path).name.split(".")[0]
                with open(out_dir / f"{meeting}.flags.csv", "w", encoding="utf-8-sig", newline="") as fh:
                    w = csv.DictWriter(fh, fieldnames=["row", "kind", "rule"])
                    w.writeheader()
                    w.writerows(flags)
    for name, c in total.items():
        print(f"== {name}: labelled {c.pop('labelled')}")
        for rule, n in sorted(c.items()):
            print(f"   {rule}: {n}")


if __name__ == "__main__":
    main()
