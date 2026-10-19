import csv, glob, re, sys, random, collections
from autune_extraction.noun_form import tidy

rows = []
for p in sorted(glob.glob("F:/0final/AUTUNE/dataset/extraction_eval_dummy/EVAL_*.G.csv")):
    with open(p, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r["kind"] in ("commitment", "decision") and r["text"].strip():
                rows.append((p.split("/")[-1][:7], r["kind"], r["text"].strip()))

NOUN_END = re.compile(r"(예정|함|됨|결정|진행)$")
stat = collections.defaultdict(lambda: collections.Counter())
changed, same = [], []
for meeting, kind, text in rows:
    out = tidy(text)
    ok = out != text
    stat[kind]["n"] += 1
    stat[kind]["changed"] += ok
    if ok:
        stat[kind]["ends_noun_form"] += bool(NOUN_END.search(re.sub(r"\s*\(.*\)$", "", out)))
        changed.append((kind, text, out))
    else:
        same.append((kind, text))

for kind, c in stat.items():
    print(f"{kind}: n={c['n']}  changed={c['changed']} ({c['changed']/c['n']:.0%})  of changed ending in a noun form={c['ends_noun_form']}")

def ending(t):
    t = re.sub(r"[.!?…\s]+$", "", t)
    last = t.split()[-1] if t.split() else t
    return last[-4:]

print("\nMost common endings among UNCHANGED sentences:")
for e, n in collections.Counter(ending(t) for _, t in same).most_common(25):
    print(f"  {n:3d}  ...{e}")

neg = sum(bool(re.search(r"(?:^|\s)(?:안|못)\s|않", t)) for _, t in same)
q = sum(t.rstrip().endswith("?") for _, t in same)
print(f"\nunchanged with a negation: {neg}; question mark: {q}; total unchanged: {len(same)}")

random.seed(7)
print("\n--- 15 changed (kind | said -> tidied)")
for k, a, b in random.sample(changed, min(15, len(changed))):
    print(f"{k[:4]} | {a}\n     -> {b}")
print("\n--- 12 unchanged")
for k, a in random.sample(same, min(12, len(same))):
    print(f"{k[:4]} | {a}")
