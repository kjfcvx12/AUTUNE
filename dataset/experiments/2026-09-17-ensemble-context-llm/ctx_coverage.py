"""Can every training row find its neighbours? Counts only."""
import csv, json, sys
from collections import Counter
from pathlib import Path
DATASET = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(DATASET / "experiments" / "2026-09-10-none-context"))
import exp_ctx_none as exp
split = DATASET / "experiments" / "2026-09-15-korean-v1" / "splits" / "syn_none_probe"
ids = [json.loads(l)["utterance_id"] for name in ("train", "validation") for l in open(split / f"{name}.jsonl", encoding="utf-8")]
src = Counter(i.split(":")[0] if i.startswith(("syn:", "probe:")) else "ami" for i in ids)
print("split rows by source", dict(src))
rows, _ = exp.build_rows(DATASET / "ami_public_manual_1.6.2")
ami_ids = {r["id"] for r in rows}
print("ami acts in corpus", len(ami_ids), "| ami split ids found", sum(1 for i in ids if ":" not in i and i in ami_ids), "of", src["ami"])
syn_dirs = [DATASET / "experiments" / "2026-09-12-synthetic-meetings" / "sheets_v4"]
probe_dirs = [DATASET / "experiments" / "2026-09-12-commitment-probe" / d for d in ("sheets", "sheets_r2")]
found = Counter()
for i in ids:
    if i.startswith("syn:"):
        _, m, r = i.split(":")
        found["syn"] += any((d / f"{m}.G.csv").exists() for d in syn_dirs)
    elif i.startswith("probe:"):
        _, m, r = i.split(":")
        found["probe"] += any((d / f"{m}.R.csv").exists() for d in probe_dirs)
print("sheet found", dict(found))
# are probe R sheets whole meetings (row numbers contiguous from 1)?
gaps = Counter()
for d in probe_dirs:
    for p in d.glob("*.R.csv"):
        rs = sorted(int(r["row"]) for r in csv.DictReader(open(p, encoding="utf-8-sig", newline="")))
        gaps["contiguous" if rs == list(range(rs[0], rs[0] + len(rs))) else "gapped"] += 1
print("probe sheets", dict(gaps))
