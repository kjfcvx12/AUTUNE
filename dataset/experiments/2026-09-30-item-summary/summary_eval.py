import csv, re, sys, time, collections
from pathlib import Path

key = ""
for line in Path("F:/0final/AUTUNE/.env").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\s*GEMINI_API_KEY\s*=\s*(.*)$", line)
    if m:
        key = m.group(1).strip().strip("\"'")
if not key:
    print("no key"); sys.exit(1)

from autune_contracts.enums import UtteranceKind
from autune_extraction import service
from autune_extraction.decisions import ClassifiedUtterance
from autune_extraction.noun_form import tidy
from autune_extraction.pipeline.resolver import LlmResolver

PER = int(sys.argv[1]) if len(sys.argv) > 1 else 12
import os
if os.environ.get("NO_RELATED"):
    service.related_ids = lambda *a, **k: []   # ablation: the window only
r = LlmResolver(api_key=key, model="gemini-3.5-flash-lite", fallback_model="gemini-3.8-flash")
calls = collections.Counter()
orig_to = r._post_to
def spy(model, body, *, index):
    calls[model] += 1
    time.sleep(5.2 if model.endswith("lite") else 13)
    return orig_to(model, body, index=index)
r._post_to = spy

total = filled = cited_any = 0
cited_counts = collections.Counter()
shown = []
for mid in ("EVAL_01", "EVAL_02"):
    rows = list(csv.DictReader(open(f"F:/0final/AUTUNE/dataset/extraction_eval_dummy/{mid}.G.csv", encoding="utf-8-sig", newline="")))
    seen = 0
    classified = []
    text = {}
    for row in rows:
        t = row["text"].strip()
        kind = None
        if row["kind"] == "commitment" and t and seen < PER:
            kind = UtteranceKind.COMMITMENT; seen += 1
        classified.append(ClassifiedUtterance(id=row["utterance_id"], kind=kind, confidence=0.9, text=t, speaker="화자"))
        text[row["utterance_id"]] = t
    out = service.resolve_commitment_summaries(r, classified)
    for uid, res in out.items():
        total += 1
        if res.text != text[uid]:
            filled += 1
        cited_counts[len(res.used)] += 1
        cited_any += bool(res.used)
        shown.append((text[uid], res, [text[i] for i in res.used]))

print(f"commitments={total} summarised={filled} ({filled/total:.0%}) cited at least one line={cited_any} ({cited_any/total:.0%})")
print("cited-line counts:", dict(sorted(cited_counts.items())), "| model calls:", dict(calls))
print()
for orig, res, used in shown:
    if res.text == orig:
        continue
    print(f"* {orig}\n    -> {res.text}\n    => {tidy(res.text)}")
    for u in used:
        print(f"       ~ {u}")
print("\n--- raw quote")
for orig, res, used in shown:
    if res.text == orig:
        print(f"* {orig}")
