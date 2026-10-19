"""Can the classifier's own call also say which words of a line carry the item?

Order of 2026-10-08 (the user, via 리더): show only the part of the utterance an
action or a decision is about, and keep the summary short. S1 keeps the sentence
a long turn was cut into. This measures S2: the same request asks, per
commitment / decision line, for the words of that line that carry it ("parts")
and for a summary of about 60 characters -- and what that costs the labels.

Two instructions taken in turn round by round, on the four invented meetings
(8.txt, EVAL_02, EVAL_03, EVAL_04; loaders are measure_prompt.py's). Prints
numbers and utterance indices only, never a line or an answer.

Usage: measure_part.py count            -- requests a round, nothing sent
       measure_part.py run <rounds> <log>
"""

from __future__ import annotations

import hashlib
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
KEY_FP = "c41ba374"  # the one AUTUNE_LLM_API_KEY line of the root .env (HISTORY 10-07)

keys = [
    line.split("=", 1)[1].strip().strip('"').strip("'")
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines()
    if line.startswith("AUTUNE_LLM_API_KEY=")
]
if len(keys) != 1 or hashlib.sha256(keys[0].encode()).hexdigest()[:8] != KEY_FP:
    sys.exit("the root .env's AUTUNE_LLM_API_KEY is not the one line this was checked against")
os.environ.update(
    AUTUNE_ENV="local",
    AUTUNE_LLM_API_KEY=keys[0],
    AUTUNE_EXTRACTION_LLM_API_KEY="",
    AUTUNE_EXTRACTION_CLASSIFIER_IMPL="llm",
    AUTUNE_EXTRACTION_LLM_MODEL="gemini-3.5-flash-lite",
    AUTUNE_EXTRACTION_LLM_FALLBACK_MODEL="",
    AUTUNE_EXTRACTION_LLM_ACKNOWLEDGED_392="true",
)

from autune_extraction.pipeline import llm  # noqa: E402
from autune_extraction.pipeline.registry import get_classifier  # noqa: E402

PACE = float(os.environ.get("PACE", "1.5"))
MAIN = llm.INSTRUCTIONS


def swap(text: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in pairs:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    return text


PART = swap(
    MAIN,
    [
        (
            '"summaries": {"줄번호": "요약", ...}}. 해당 없으면',
            '"summaries": {"줄번호": "요약", ...}, "parts": {"줄번호": "옮긴 부분", ...}}. 해당 없으면',
        ),
        (
            "그 줄의 내용을 한 문장으로 적으세요",
            "그 줄의 내용을 60자 안팎의 짧은 한 문장으로 적으세요",
        ),
        (
            "쓰지 말고 [사람N]은 그대로 두세요.",
            "쓰지 말고 [사람N]은 그대로 두세요. parts에는 같은 줄마다, 그 약속·결정을 말한 "
            "부분만 줄에서 글자 그대로 옮겨 적으세요(고치거나 줄이지 말고, 줄 전체가 그 "
            "내용이면 줄 전체).",
        ),
    ],
)
VARIANTS = {"main": MAIN, "part": PART}


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


def use(variant: str) -> None:
    llm.INSTRUCTIONS = VARIANTS[variant]
    llm._BODY_OVERHEAD = len(VARIANTS[variant]) + 200


def planned(variant: str, texts: list[str]) -> int:
    """Requests one run sends, counted the way ``classify`` cuts them."""
    use(variant)
    _, lines = llm._in_pieces(texts, None)
    return len(llm.windows(lines, llm.MAX_OUTBOUND_CHARS - llm._BODY_OVERHEAD))


def squeeze(text: str) -> str:
    return "".join(text.split())


def parts_of(answer: str) -> dict[int, str]:
    match = re.search(r"\{.*\}", answer, re.S)
    if not match:
        return {}
    try:
        written = json.loads(match.group(0)).get("parts", {})
    except (json.JSONDecodeError, AttributeError):
        return {}
    if not isinstance(written, dict):
        return {}
    return {
        int(str(k).strip()): v
        for k, v in written.items()
        if isinstance(v, str) and str(k).strip().isdigit()
    }


def classify(variant: str, texts: list[str]) -> tuple[list, int, dict]:
    use(variant)
    classifier = get_classifier()
    client = classifier._client  # type: ignore[attr-defined]
    send = client.request
    count = {"n": 0}

    def request(method: str, path: str, **kwargs: object) -> object:
        count["n"] += 1
        time.sleep(PACE)
        return send(method, path, **kwargs)

    client.request = request

    seen: list[tuple[list[str], dict[int, int]]] = []
    answers: list[str] = []
    render, answer_text = llm.render, llm._answer_text

    def rendered(lines: list[str], context: int, start: int, end: int):  # type: ignore[no-untyped-def]
        text, targets = render(lines, context, start, end)
        seen.append((lines, targets))
        return text, targets

    def answered(body: object) -> str:
        answer = answer_text(body)
        answers.append(answer)
        return answer

    llm.render, llm._answer_text = rendered, answered
    try:
        got = classifier.classify(texts)
    finally:
        llm.render, llm._answer_text = render, answer_text

    stats: dict = {
        "lines": 0,  # commitment / decision lines of the answers
        "long_lines": 0,  # ... of 60 characters or more
        "parts": 0,  # of them, with a part returned
        "exact": 0,  # the part is in the line character for character
        "loose": 0,  # ... or is, spacing aside
        "whole": 0,  # the part is all of the line
        "ratio": [],  # part / line length, where the part is in the line
        "ratio_long": [],  # the same, lines of 60 characters or more
        "summary_chars": [],
        "summary_over_60": 0,
        "summary_over_120": 0,
    }
    for (lines, targets), answer in zip(seen, answers, strict=False):
        labels = llm.parse(answer)
        quoted = parts_of(answer)
        summaries = llm.parse_summaries(answer)
        for n, kind_ in labels.items():
            if n not in targets or kind_ not in llm.SUMMARISED:
                continue
            line = lines[targets[n]]
            stats["lines"] += 1
            long = len(line) >= 60
            stats["long_lines"] += long
            if n in summaries:
                size = len(summaries[n])
                stats["summary_chars"].append(size)
                stats["summary_over_60"] += size > 60
                stats["summary_over_120"] += size > 120
            part = quoted.get(n, "").strip()
            if not part:
                continue
            stats["parts"] += 1
            exact = part in line
            loose = bool(squeeze(part)) and squeeze(part) in squeeze(line)
            stats["exact"] += exact
            stats["loose"] += loose
            if loose:
                stats["whole"] += squeeze(part) == squeeze(line)
                ratio = round(len(squeeze(part)) / len(squeeze(line)), 3)
                stats["ratio"].append(ratio)
                if long:
                    stats["ratio_long"].append(ratio)
    return got, count["n"], stats


def kind(p: object) -> str:
    return p.kind.value if p.kind is not None else "none"  # type: ignore[attr-defined]


def meetings() -> dict[str, tuple[list[tuple[int, str]], set[int], set[int]]]:
    return {
        "8.txt": meeting_8(),
        "EVAL_02": meeting_eval("EVAL_02"),
        "EVAL_03": meeting_eval("EVAL_03"),
        "EVAL_04": meeting_eval("EVAL_04"),
    }


def count() -> None:
    total = 0
    for name in VARIANTS:
        for meeting, (items, _, _) in meetings().items():
            n = planned(name, [text for _, text in items])
            total += n
            print(name, len(VARIANTS[name]), meeting, len(items), "utterances", n, "requests")
    print("a round:", total, "requests")


def run(rounds: int, log: Path) -> None:
    sent = 0
    with log.open("a", encoding="utf-8") as out:
        for name in VARIANTS:
            out.write(json.dumps({"variant": name, "chars": len(VARIANTS[name])}) + "\n")
        for rnd in range(rounds):
            for name in VARIANTS:
                for meeting, (items, yes, ignore) in meetings().items():
                    try:
                        got, requests, stats = classify(name, [text for _, text in items])
                    except Exception as exc:  # noqa: BLE001 -- one failed run is a hole, not the end
                        out.write(
                            json.dumps(
                                {
                                    "round": rnd,
                                    "variant": name,
                                    "meeting": meeting,
                                    "error": type(exc).__name__,
                                }
                            )
                            + "\n"
                        )
                        out.flush()
                        continue
                    sent += requests
                    pred = {
                        i for (i, _), p in zip(items, got, strict=True) if kind(p) == "commitment"
                    } - ignore
                    tp, fp, fn = len(pred & yes), len(pred - yes), len(yes - pred)
                    p = tp / (tp + fp) if tp + fp else 0.0
                    r = tp / (tp + fn) if tp + fn else 0.0
                    f1 = 2 * p * r / (p + r) if p + r else 0.0
                    kinds: dict[str, int] = {}
                    for one in got:
                        kinds[kind(one)] = kinds.get(kind(one), 0) + 1
                    kept = sum(bool(getattr(o, "summary", "")) for o in got) + sum(
                        bool(s) for o in got for s in getattr(o, "piece_summaries", ())
                    )
                    out.write(
                        json.dumps(
                            {
                                "round": rnd,
                                "variant": name,
                                "meeting": meeting,
                                "P": round(p, 3),
                                "R": round(r, 3),
                                "F1": round(f1, 3),
                                "fp": sorted(pred - yes),
                                "fn": sorted(yes - pred),
                                "requests": requests,
                                "kinds": kinds,
                                "summaries_kept": kept,
                                **stats,
                            }
                        )
                        + "\n"
                    )
                    out.flush()
        out.write(json.dumps({"done": True, "requests": sent}) + "\n")


if sys.argv[1] == "count":
    count()
else:
    run(int(sys.argv[2]), Path(sys.argv[3]))
