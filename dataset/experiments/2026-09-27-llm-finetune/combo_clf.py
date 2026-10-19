"""Classifier + fine-tuned LLM together (2026-09-28): does the DeBERTa kind
classifier help the LoRA action-item picker?

    python combo_clf.py classify test_asr_turns     # DeBERTa on every [신규] utterance
    python combo_clf.py hint test_asr_turns         # writes test_asr_turns_hint.jsonl
    python combo_clf.py score test_asr_turns merged_e2 [merged_e2_hint]

`classify` runs share_s20260910 (the no-AI-Hub checkpoint the 09-26 v1-v12
combo used) the way B does: text only, cut at the checkpoint's own
model_max_length (96), kind = best of the five kinds unless `none` beats it.
The checkpoint was trained on team_dummy DUMMY_001-100, so only the eval sets
(EVAL/EVALH, ASR/ASRX, 8.txt, AI Hub) are fair ground -- never the FT train split.

`hint` tags each [신규] line the classifier calls a commitment with
` (분류기: 약속)` and adds one line to the system prompt; the LoRA was not
trained with tags, so this is zero-shot use of the hint.

`score` compares, on the same utterances: classifier alone (commitment), the FT
run alone, FT AND classifier, FT OR classifier, and any extra FT runs given
(e.g. the hint run). Prints counts only (AI Hub text never leaves the files).
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
CLF = Path.home() / ".cache" / "autune" / "models" / "share_s20260910_fp16"
LINE = re.compile(r"^\[#(\d+)\] \[신규\] (.*?): (.*)$")
TAG = " (분류기: 약속)"
HINT_SYSTEM = "\n(분류기: 약속) 표시는 별도 분류 모델의 판단입니다. 참고만 하고 최종 판단은 직접 하세요."


def load(split: str) -> list[dict]:
    return [json.loads(line) for line in (HERE / f"{split}.jsonl").open(encoding="utf-8")]


def new_lines(row: dict) -> dict[int, str]:
    out = {}
    for line in row["user"].split("\n"):
        m = LINE.match(line)
        if m:
            out[int(m.group(1))] = m.group(3)
    return out


def classify(split: str) -> None:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(CLF)
    # CLF_DEVICE=cpu while the GPU is busy with an LLM run.
    device = os.environ.get("CLF_DEVICE", "cuda")
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModelForSequenceClassification.from_pretrained(CLF, dtype=dtype).to(device)
    model.eval()
    id2label = {int(k): v for k, v in model.config.id2label.items()}
    max_len = min(tok.model_max_length, model.config.max_position_embeddings)

    rows = load(split)
    keys, texts = [], []
    for r in rows:
        for idx, text in new_lines(r).items():
            keys.append((r["meeting"], idx))
            texts.append(text)
    kinds: dict[str, dict[str, list]] = {}
    for start in range(0, len(texts), 32):
        batch = texts[start : start + 32]
        enc = tok(batch, truncation=True, max_length=max_len, padding=True, return_tensors="pt").to(device)
        with torch.no_grad():
            probs = torch.softmax(model(**enc).logits.float(), dim=-1).tolist()
        for (meeting, idx), p in zip(keys[start : start + 32], probs, strict=True):
            *kind_p, none_p = p
            best = max(range(5), key=lambda i: kind_p[i])
            kind = "none" if none_p > kind_p[best] else id2label[best]
            kinds.setdefault(meeting, {})[str(idx)] = [kind, round(kind_p[0], 4)]
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / f"clf_{split}.json").write_text(json.dumps(kinds), encoding="utf-8")
    flat = [k for m in kinds.values() for k, _ in m.values()]
    print(json.dumps({"split": split, "utterances": len(flat), "commitment": flat.count("commitment"),
                      "max_len": max_len}))


def clf_yes(split: str) -> dict[str, set[int]]:
    kinds = json.loads((HERE / "results" / f"clf_{split}.json").read_text(encoding="utf-8"))
    return {m: {int(i) for i, (k, _) in v.items() if k == "commitment"} for m, v in kinds.items()}


def hint(split: str) -> None:
    yes = clf_yes(split)
    tagged = 0
    with (HERE / f"{split}_hint.jsonl").open("w", encoding="utf-8") as f:
        for r in load(split):
            lines = []
            for line in r["user"].split("\n"):
                m = LINE.match(line)
                if m and int(m.group(1)) in yes.get(r["meeting"], set()):
                    line += TAG
                    tagged += 1
                lines.append(line)
            r = dict(r, user="\n".join(lines), system=r["system"] + HINT_SYSTEM)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps({"split": f"{split}_hint", "tagged": tagged}))


def run_picks(split: str, tag: str) -> dict[tuple[str, int], set[int]]:
    run = json.loads((HERE / "results" / f"{split}_{tag}.json").read_text(encoding="utf-8"))
    return {(r["meeting"], r["chunk"]): set(r["pred"]) for r in run["rows"]}


def prf(tp: int, fp: int, fn: int) -> dict:
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "P": round(p, 3), "R": round(r, 3), "F1": round(f, 3)}


def score(split: str, ft_tag: str, extra: list[str]) -> None:
    rows = load(split)
    clf = clf_yes(split)
    ft = run_picks(split, ft_tag)
    others = {t: run_picks(split + ("_hint" if t.endswith("_hint") else ""), t) for t in extra}
    systems = ["classifier", ft_tag, f"{ft_tag} AND classifier", f"{ft_tag} OR classifier", *extra]
    counts = {s: [0, 0, 0] for s in systems}
    for r in rows:
        new = set(r["new_idx"])
        c = clf.get(r["meeting"], set()) & new
        # Like eval_chunks.py, an FT pick that is not a [신규] number of this chunk
        # stays in and counts as a false positive.
        f = ft.get((r["meeting"], r["chunk"]), set())
        picks = {systems[0]: c, systems[1]: f, systems[2]: f & c, systems[3]: f | c}
        for t in extra:
            picks[t] = others[t].get((r["meeting"], r["chunk"]), set())
        gold, ignore = set(r["gold_yes"]), set(r["gold_ignore"])
        for s, p in picks.items():
            p = p - ignore
            n = counts[s]
            n[0] += len(p & gold)
            n[1] += len(p - gold)
            n[2] += len(gold - p)
    print(f"split={split} gold_yes={sum(len(r['gold_yes']) for r in rows)}")
    for s in systems:
        print(json.dumps({"system": s, **prf(*counts[s])}, ensure_ascii=False))


def main() -> None:
    cmd, split, *rest = sys.argv[1:]
    if cmd == "classify":
        classify(split)
    elif cmd == "hint":
        hint(split)
    elif cmd == "score":
        score(split, rest[0], rest[1:])
    else:
        raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
