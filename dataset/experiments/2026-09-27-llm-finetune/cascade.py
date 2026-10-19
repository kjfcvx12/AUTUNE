"""Cascade instead of AND (2026-09-28): one model proposes, the other checks, and a
disagreement goes to a person rather than being dropped.

    python cascade.py

Reuses saved predictions only -- no model runs. DeBERTa = results/clf_<split>.json
(share_s20260910, commitment), local LLM = results/<split>_<tag>.json
(merged_e2 = the LoRA fine-tune, base = Qwen3-4B zero-shot).

For each split and LLM, two directions:

- ``llm->clf``: the LLM proposes. Both agree -> accepted automatically. LLM-only
  -> "needs confirmation" (a person decides). Classifier-only -> never shown.
- ``clf->llm``: the classifier proposes; the mirror image.

Reported after a person resolves the queue correctly (the best case for a queue):
recall and precision of what ends up accepted, how many utterances the queue
holds, and how many of those were real commitments. A run that did not cover a
chunk (e.g. an older ASR run) is scored on the chunks it covered only.
Prints counts only -- AI Hub text never leaves the files.
"""

from __future__ import annotations

import json

from combo_clf import HERE, clf_yes, load, prf, run_picks

RUNS = {
    "test8": ["merged_e2", "base"],
    "test_turns": ["merged_e2"],
    "test_asr_turns": ["merged_e2_asr8", "base_asr5x2"],
    "test_real_turns": ["merged_e2", "base"],
}


def evaluate(split: str, tag: str) -> dict:
    rows = load(split)
    clf = clf_yes(split)
    llm = run_picks(split, tag)
    n = {k: 0 for k in ("gold", "llm_tp", "llm_fp", "clf_tp", "clf_fp", "both_tp", "both_fp",
                        "llm_only_tp", "llm_only_fp", "clf_only_tp", "clf_only_fp", "chunks")}
    for r in rows:
        key = (r["meeting"], r["chunk"])
        if key not in llm:
            continue
        n["chunks"] += 1
        new = set(r["new_idx"])
        ignore, gold = set(r["gold_ignore"]), set(r["gold_yes"])
        c = (clf.get(r["meeting"], set()) & new) - ignore
        f = llm[key] - ignore
        n["gold"] += len(gold)
        for name, picks in (("llm", f), ("clf", c), ("both", f & c),
                            ("llm_only", f - c), ("clf_only", c - f)):
            n[f"{name}_tp"] += len(picks & gold)
            n[f"{name}_fp"] += len(picks - gold)
    return n


def report(split: str, tag: str) -> None:
    n = evaluate(split, tag)
    gold = n["gold"]
    out = {"split": split, "llm": tag, "chunks": n["chunks"], "gold": gold,
           "llm_alone": prf(n["llm_tp"], n["llm_fp"], gold - n["llm_tp"])["F1"],
           "clf_alone": prf(n["clf_tp"], n["clf_fp"], gold - n["clf_tp"])["F1"],
           "and": prf(n["both_tp"], n["both_fp"], gold - n["both_tp"])}
    for direction, queue in (("llm->clf", "llm_only"), ("clf->llm", "clf_only")):
        tp = n["both_tp"] + n[f"{queue}_tp"]  # the person keeps the true ones
        fp = n["both_fp"]                     # and rejects the false ones in the queue
        size = n[f"{queue}_tp"] + n[f"{queue}_fp"]
        out[direction] = {**prf(tp, fp, gold - tp), "queue": size,
                          "queue_true": n[f"{queue}_tp"],
                          "auto": n["both_tp"] + n["both_fp"]}
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    for split, tags in RUNS.items():
        for tag in tags:
            if (HERE / "results" / f"{split}_{tag}.json").exists():
                report(split, tag)
            else:
                print(json.dumps({"split": split, "llm": tag, "missing": True}))
