"""Do training (ctx_train.encode_rows) and scoring (score_models.encode_meeting) build the
same token ids for the same row? Checked on the synthetic and probe rows of splits/ctx2.
Counts only."""
from __future__ import annotations
import csv, json, sys
from collections import Counter, defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from transformers import AutoTokenizer
from ctx_train import encode_rows
from score_models import encode_meeting
from meetings import full_rows

tok = AutoTokenizer.from_pretrained(str(HERE / "runs" / "ctx2_s20260910"))
SYN = HERE.parents[1] / "experiments" / "2026-09-12-synthetic-meetings" / "sheets_v4"
rows = [json.loads(l) for l in (HERE / "splits" / "ctx2" / "train.jsonl").read_text(encoding="utf-8").splitlines()]
by = defaultdict(list)
for r in rows:
    if r["utterance_id"].startswith(("syn:", "probe:")):
        kind, m, row = r["utterance_id"].split(":")
        by[(kind, m)].append((row, r))
c = Counter()
for (kind, m), items in list(by.items()):
    if kind == "syn":
        with open(SYN / f"{m}.G.csv", encoding="utf-8-sig", newline="") as fh:
            sheet = sorted(csv.DictReader(fh), key=lambda x: int(x["row"]))
        full = None
    else:
        sheet = list(full_rows(m))
    wanted = {row for row, _ in items}
    target_rows = [x for x in sheet if x["row"] in wanted]
    if kind == "syn":
        # score_models takes neighbours from full_rows() when the meeting is indexed, else from the rows it is given
        import score_models
        orig = score_models.full_rows
        score_models.full_rows = lambda _m, s=tuple(sheet): s
        got = encode_meeting(tok, m, target_rows, 2)
        score_models.full_rows = orig
    else:
        got = encode_meeting(tok, m, target_rows, 2)
    got_by_row = {x["row"]: ids for x, ids in zip(target_rows, got)}
    train_ids = encode_rows(tok, [r for _, r in items])
    for (row, _), ids in zip(items, train_ids):
        c[f"{kind} {'same' if got_by_row.get(row) == ids else 'DIFFERENT'}"] += 1
print(dict(c))
