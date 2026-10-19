import collections, csv, glob, json, os
kind = {}
for f in glob.glob("../../extraction_eval_dummy*/*.G.csv"):
    m = os.path.basename(f).split(".")[0]
    for i, r in enumerate(csv.DictReader(open(f, encoding="utf-8-sig")), 1):
        kind[(m, i)] = r["kind"] or "none"
test = {(r["meeting"], r["chunk"]): r for r in map(json.loads, open("test.jsonl", encoding="utf-8"))}
for t in ["ft_e1", "ft_e2"]:
    rows = json.load(open(f"results/test_{t}.json", encoding="utf-8"))["rows"]
    fp = collections.Counter()
    for row in rows:
        r = test[(row["meeting"], row["chunk"])]
        for i in set(row["pred"]) - set(r["gold_yes"]) - set(r["gold_ignore"]):
            fp[kind[(row["meeting"], i)] if i in r["new_idx"] else "not-[신규]"] += 1
    print(t, "FP by gold kind:", dict(fp.most_common()))
