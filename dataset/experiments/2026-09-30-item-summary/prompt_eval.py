"""Compare prompt variants on invented dummy meetings, commitments and decisions.

usage: prompt_eval.py <variant-file.py or -> <n-commitments-per-meeting> <n-decisions-per-meeting>

A variant file may define SUMMARY_PROMPT and/or DECISION_PROMPT (strings with a {lines}
placeholder and doubled braces for the JSON example). Everything printed is invented text.
"""

import csv, re, sys, time, collections, importlib.util
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
from autune_extraction.decisions import ClassifiedUtterance, group_decisions
from autune_extraction.noun_form import tidy
from autune_extraction.pipeline import resolver as R

variant, n_commit, n_dec = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
if variant != "-":
    spec = importlib.util.spec_from_file_location("variant", variant)
    v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
    if hasattr(v, "SUMMARY_PROMPT"):
        R._SUMMARY_PROMPT = v.SUMMARY_PROMPT
    if hasattr(v, "DECISION_PROMPT"):
        R._DECISION_PROMPT = v.DECISION_PROMPT

r = R.LlmResolver(api_key=key, model="gemini-3.5-flash-lite", fallback_model="gemini-3.8-flash")
calls = collections.Counter()
orig_to = r._post_to
def spy(model, body, *, index):
    calls[model] += 1
    time.sleep(5.2 if model.endswith("lite") else 13)
    return orig_to(model, body, index=index)
r._post_to = spy

WORD = re.compile(r"[가-힣A-Za-z0-9]{2,}")
def unsupported(summary, offered_texts):
    """Content words of the summary that appear in none of the lines it was offered."""
    pool = " ".join(offered_texts)
    generic = ("결정", "하기로", "했습니다", "되었", "됩니다", "정함", "정했", "것은", "것도", "것이", "하고", "해서",
               "했던", "있는", "하는", "되는", "한다", "둔다", "한번", "다시", "먼저", "우선", "대해", "대한", "위해",
               "처리", "진행", "확인")
    bad = []
    for w in WORD.findall(summary):
        if any(g in w for g in generic):
            continue
        head = w[:2]                             # let an inflection differ: 돌아간 ~ 돌아
        if head not in pool and w not in pool:
            bad.append(w)
    return bad

def load(mid):
    rows = list(csv.DictReader(open(f"F:/0final/AUTUNE/dataset/extraction_eval_dummy/{mid}.G.csv", encoding="utf-8-sig", newline="")))
    return rows

stats = {"commitment": collections.Counter(), "decision": collections.Counter()}
samples = {"commitment": [], "decision": []}

def record(kind, original, res, offered):
    st = stats[kind]
    st["n"] += 1
    changed = res.text != original
    st["summarised"] += changed
    st["cited"] += bool(res.used)
    if changed:
        bad = unsupported(res.text, offered)
        st["unsupported_words"] += len(bad)
        st["with_unsupported"] += bool(bad)
        st["growth_x100"] += int(100 * len(res.text) / max(1, len(original)))
        samples[kind].append((original, res.text, [w for w in bad]))

for mid in ("EVAL_01", "EVAL_02", "EVAL_03"):
    rows = load(mid)
    text = {row["utterance_id"]: row["text"].strip() for row in rows}
    # commitments
    seen = 0
    cl = []
    for row in rows:
        t = row["text"].strip()
        kind = None
        if row["kind"] == "commitment" and t and seen < n_commit:
            kind = UtteranceKind.COMMITMENT; seen += 1
        cl.append(ClassifiedUtterance(id=row["utterance_id"], kind=kind, confidence=0.9, text=t, speaker="화자"))
    if n_commit:
        out = service.resolve_commitment_summaries(r, cl)
        # offered lines: rebuild to measure support (window + candidates)
        for uid, res in out.items():
            idx = [c.id for c in cl].index(uid)
            win = [c.text for c in cl[max(0, idx - 4): idx + 3] if c.text]
            rel = [text[i] for i in res.used]
            record("commitment", text[uid], res, win + rel + [text[uid]])
    # decisions
    dl = []
    dseen = 0
    for row in rows:
        t = row["text"].strip()
        kind = UtteranceKind.DECISION if (row["kind"] == "decision" and t) else None
        dl.append(ClassifiedUtterance(id=row["utterance_id"], kind=kind, confidence=0.9, text=t, speaker="화자"))
    if n_dec:
        groups = group_decisions(dl)[:n_dec]
        keep = {u for g in groups for u in g.source_utterance_ids}
        dl2 = [c if c.id in keep or c.kind is None else ClassifiedUtterance(id=c.id, kind=None, confidence=0.0, text=c.text, speaker=c.speaker) for c in dl]
        out = service.resolve_decision_summaries(r, dl2, meeting_id=mid)
        from autune_extraction.decisions import decision_id
        for g in group_decisions(dl2):
            res = out[decision_id(mid, g.source_utterance_ids)]
            idx = [c.id for c in dl2].index(g.substance_id)
            win = [c.text for c in dl2[max(0, g.first_position - 4): g.last_position + 3] if c.text]
            rel = [text[i] for i in res.used]
            record("decision", g.core_text, res, win + rel)

for kind, st in stats.items():
    if not st["n"]:
        continue
    n, s = st["n"], st["summarised"]
    print(f"{kind}: n={n} summarised={s} ({s/n:.0%}) cited={st['cited']} ({st['cited']/n:.0%}) "
          f"unsupported-words/summary={st['unsupported_words']/max(1,s):.2f} "
          f"summaries-with-unsupported={st['with_unsupported']}/{s} mean-growth=x{st['growth_x100']/max(1,s)/100:.2f}")
print("model calls:", dict(calls))
print()
for kind in ("commitment", "decision"):
    print(f"--- {kind} samples (original -> summary | unsupported)")
    for orig, summ, bad in samples[kind]:
        print(f"* {orig}\n    -> {summ}" + (f"\n    !! {bad}" if bad else ""))
