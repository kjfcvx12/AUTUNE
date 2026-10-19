"""Commitment F1 of the product's llm classifier on the two gold dummy meetings.

Run from a worktree with that worktree's venv: the classifier measured is the
one checked out there. Both meetings are self-authored dummy meetings (their
README, HISTORY and the 09-28 script say so); loaders and scoring are that
script's (dataset/experiments/2026-09-28-flash-lite-tuning/flt.py). Prints
numbers and utterance indices only -- no meeting text.

Usage: measure_880.py <label> <runs>
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path("F:/0final/AUTUNE")
EXP = ROOT / "dataset" / "experiments"
SRC8 = EXP / "2026-09-26-local-vs-api" / "scratch_e27a3912" / "step1_chunks_overlap_8.json"
FT = EXP / "2026-09-27-llm-finetune" / "test.jsonl"
YES8 = {14, 20, 29, 34, 35, 37, 45, 46, 48, 49, 68, 69, 74, 75, 77, 79}
IGNORE8 = {42, 43, 47, 52, 76}

key = ""
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if line.startswith("AUTUNE_LLM_API_KEY="):
        key = line.split("=", 1)[1].strip().strip('"').strip("'")
if not key:
    sys.exit("no AUTUNE_LLM_API_KEY in the root .env")
os.environ.update(
    AUTUNE_ENV="local",
    AUTUNE_LLM_API_KEY=key,
    AUTUNE_EXTRACTION_LLM_API_KEY="",
    AUTUNE_EXTRACTION_CLASSIFIER_IMPL="llm",
    AUTUNE_EXTRACTION_LLM_MODEL="gemini-3.5-flash-lite",
    AUTUNE_EXTRACTION_LLM_FALLBACK_MODEL="",
    AUTUNE_EXTRACTION_LLM_ACKNOWLEDGED_392="true",
)

from autune_extraction.pipeline import llm as llm_module  # noqa: E402
from autune_extraction.pipeline.registry import get_classifier  # noqa: E402

PACE = float(os.environ.get("PACE", "4.5"))


def meeting_8() -> tuple[list[tuple[int, str]], set[int], set[int]]:
    payload = json.loads(SRC8.read_text(encoding="utf-8"))
    seen: dict[int, str] = {}
    for chunk in payload["chunks"]:
        for u in chunk["utterances"]:
            if u["idx"] > 0:
                seen.setdefault(u["idx"], u["text"])
    return sorted(seen.items()), set(YES8), set(IGNORE8)


def meeting_eval(name: str) -> tuple[list[tuple[int, str]], set[int], set[int]]:
    utts: dict[int, str] = {}
    yes: set[int] = set()
    ignore: set[int] = set()
    for line in FT.read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        if d["meeting"] != name:
            continue
        yes |= set(d["gold_yes"])
        ignore |= set(d["gold_ignore"])
        for row in d["user"].splitlines():
            m = re.match(r"\[#(\d+)\] \[신규\] [^:]+: (.*)", row)
            if m:
                utts[int(m.group(1))] = m.group(2)
    return sorted(utts.items()), yes, ignore


def run(items: list[tuple[int, str]], yes: set[int], ignore: set[int]) -> dict:
    classifier = get_classifier()
    client = classifier._client  # type: ignore[attr-defined]
    send = client.request
    count = {"n": 0}

    def request(method: str, path: str, **kwargs: object) -> object:
        count["n"] += 1
        time.sleep(PACE)
        return send(method, path, **kwargs)

    client.request = request
    started = time.time()
    predictions = classifier.classify([text for _, text in items])
    pred = {i for (i, _), p in zip(items, predictions, strict=True)
            if p.kind is not None and p.kind.value == "commitment"} - ignore
    tp, fp, fn = len(pred & yes), len(pred - yes), len(yes - pred)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    kinds: dict[str, int] = {}
    for one in predictions:
        if one.kind is not None:
            kinds[one.kind.value] = kinds.get(one.kind.value, 0) + 1
    summarised = sum(
        bool(getattr(one, "summary", "")) + sum(bool(s) for s in getattr(one, "piece_summaries", ()))
        for one in predictions
    )
    return {
        "P": round(p, 3), "R": round(r, 3), "F1": round(f1, 3),
        "fp": sorted(pred - yes), "fn": sorted(yes - pred),
        "requests": count["n"], "sec": round(time.time() - started),
        "kinds": dict(sorted(kinds.items())), "summaries": summarised,
    }


def main() -> None:
    label, reps = sys.argv[1], int(sys.argv[2])
    print(f"== {label}: instructions {len(llm_module.INSTRUCTIONS)} chars, "
          f"summaries asked: {'summaries' in llm_module.INSTRUCTIONS}")
    for name, loaded in (("8.txt", meeting_8()), ("EVAL_02", meeting_eval("EVAL_02"))):
        items, yes, ignore = loaded
        print(f"-- {name}: {len(items)} utterances, {len(yes)} gold commitments, {len(ignore)} ignored")
        scores = []
        for rep in range(reps):
            got = run(items, yes, ignore)
            scores.append(got["F1"])
            print(f"   run {rep + 1}: {json.dumps(got, ensure_ascii=False)}")
        print(f"   F1 mean {sum(scores) / len(scores):.3f}  min {min(scores):.3f}  max {max(scores):.3f}")


main()
