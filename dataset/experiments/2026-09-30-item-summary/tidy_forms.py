import csv, glob, re, collections
from autune_extraction.noun_form import tidy
forms = collections.Counter()
for p in sorted(glob.glob("F:/0final/AUTUNE/dataset/extraction_eval_dummy/EVAL_*.G.csv")):
    for r in csv.DictReader(open(p, encoding="utf-8-sig", newline="")):
        if r["kind"] in ("commitment", "decision") and r["text"].strip():
            out = tidy(r["text"].strip())
            if out != r["text"].strip():
                w = re.sub(r"\s*\(.*\)$", "", out).split()
                forms[" ".join(w[-2:])] += 1
print(len(forms), "distinct two-word tails of changed sentences:")
print(" | ".join(f for f, _ in sorted(forms.items())))
