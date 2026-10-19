import csv, re, sys, time, collections
from pathlib import Path

key = ""
for line in Path("F:/0final/AUTUNE/.env").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\s*GEMINI_API_KEY\s*=\s*(.*)$", line)
    if m:
        key = m.group(1).strip().strip("\"'")
if not key:
    print("no key"); sys.exit(1)

from autune_extraction.pipeline.base import ResolutionRequest
from autune_extraction.pipeline.resolver import LlmResolver, MAX_CONTEXT_UTTERANCES, MAX_CONTEXT_AFTER
import importlib.util
_spec = importlib.util.spec_from_file_location("noun_form", "F:/0final/AUTUNE/modules/extraction/src/autune_extraction/noun_form.py")
_nf = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_nf)
tidy = _nf.tidy

PER_MEETING = int(sys.argv[1]) if len(sys.argv) > 1 else 12
requests, meta = [], []
for mid in ("EVAL_01", "EVAL_02"):
    rows = list(csv.DictReader(open(f"F:/0final/AUTUNE/dataset/extraction_eval_dummy/{mid}.G.csv", encoding="utf-8-sig", newline="")))
    texts = [r["text"].strip() for r in rows]
    picked = 0
    for i, r in enumerate(rows):
        if r["kind"] != "commitment" or not texts[i]:
            continue
        ctx = tuple(t for t in texts[max(0, i - MAX_CONTEXT_UTTERANCES):i] if t)
        after = tuple(t for t in texts[i + 1:i + 1 + MAX_CONTEXT_AFTER] if t)
        requests.append(ResolutionRequest(target=texts[i], context=ctx, context_after=after))
        meta.append((mid, r["utterance_id"]))
        picked += 1
        if picked >= PER_MEETING:
            break

r = LlmResolver(api_key=key, model="gemini-3.5-flash-lite", fallback_model="gemini-3.8-flash")
calls = {"errors": 0}
orig = r._post
def counted(body, *, index):
    try:
        return orig(body, index=index)
    except Exception:
        calls["errors"] += 1
        raise
r._post = counted

out = []
asked = []   # which models each request reached
orig_to = r._post_to
cur = []
def spy(model, body, *, index):
    cur.append(model)
    return orig_to(model, body, index=index)
r._post_to = spy
for n, req in enumerate(requests):
    cur.clear()
    out.append(r._resolve_one(req, n))
    asked.append(list(cur))
    time.sleep(5.2 + (13 if len(cur) > 1 else 0))   # 3.8 free tier: 5 a minute

filled = [(q, o) for q, o in zip(requests, out) if o != q.target]
same = [(q, o) for q, o in zip(requests, out) if o == q.target]
ratio = [len(o) / len(q.target) for q, o in filled]
print(f"requests={len(requests)} filled={len(filled)} ({len(filled)/len(requests):.0%}) "
      f"raw-quote fallback={len(same)} call errors={calls['errors']}")
if ratio:
    print(f"filled length vs original: mean x{sum(ratio)/len(ratio):.2f}, max x{max(ratio):.2f}")
print("\n--- filled (original -> resolved -> tidied)")
for q, o in filled:
    print(f"* {q.target}\n    -> {o}\n    => {tidy(o)}")
print("\n--- fell back to the raw quote")
for q, o in same:
    print(f"* {q.target}")

esc = [a for a in asked if len(a) > 1]
print()
print(f"escalated to the second model: {len(esc)} of {len(asked)}")
