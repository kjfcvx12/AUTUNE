"""#411 acceptance: the product LlmClassifier with and without roster-name substitution.

Two self-authored dummy meetings (no AI Hub, no real person), so the free-tier key
is allowed: 8.txt (test8 gold, 16 commitment rows) and EVAL_02 (23). The roster is
the names the dummy text itself addresses ("<name> 님/씨"), since a dummy meeting
has no team. Every request body is captured to prove no roster name went out.

    python roster_eval.py <model> <reps> [meetings]   e.g. gemini-3.5-flash-lite 5 8.txt

Prints per run: meeting, roster on/off, commitment P/R/F1, requests, names left.
Appends JSON lines to runs.jsonl next to this file.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "2026-09-28-flash-lite-tuning"))
import flt  # noqa: E402  (load_texts / load_eval / score, the #393 gold)

from autune_extraction.pipeline.llm import LlmClassifier  # noqa: E402

TITLES = {"팀장", "대리", "부장", "과장", "사장", "선생", "고객", "여러분", "모두", "다들",
          "실장", "이사", "차장", "선배", "매니저", "담당", "대표", "책임", "주임", "사원",
          "센터장", "본부장", "원장", "회장"}
NAME = re.compile(r"([가-힣]{2,3})\s?(?:님|씨)")
PACE = {"gemini-3.5-flash-lite": 4.5, "gemini-3.8-flash": 13.0}


def key() -> str:
    for line in (HERE.parents[2] / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("GEMINI_API_KEY missing")


def roster_of(texts: list[str]) -> list[str]:
    """Names the text addresses, as a roster would list them: a given name already
    inside a found full name ("민구" in "강민구") is that person, not another."""
    found = {m[1] for t in texts for m in NAME.finditer(t)} - TITLES
    full = {n for n in found if len(n) == 3}
    return sorted(n for n in found if not any(len(f) == 3 and f[1:] == n for f in full))


def meeting(name: str) -> list[tuple[int, str]]:
    if name == "8.txt":
        # flt's module-level gold is test8's; load_eval replaces it, so restore it.
        flt.YES = {14, 20, 29, 34, 35, 37, 45, 46, 48, 49, 68, 69, 74, 75, 77, 79}
        flt.IGNORE = {42, 43, 47, 52, 76}
        return flt.load_texts()
    return flt.load_eval(name)


def run(model: str, name: str, with_roster: bool, api_key: str) -> dict:
    items = meeting(name)
    idxs = [i for i, _ in items]
    texts = [t for _, t in items]
    roster = roster_of(texts)
    llm = LlmClassifier(api_key=api_key, model=model, timeout_sec=90.0)
    if with_roster:
        llm.use_roster(roster)
    bodies: list[str] = []
    inner = llm._client.request

    def paced(method: str, path: str, **kwargs: object) -> object:
        bodies.append(json.dumps(kwargs.get("json"), ensure_ascii=False))
        time.sleep(PACE.get(model, 5.0))
        return inner(method, path, **kwargs)

    llm._client.request = paced  # type: ignore[method-assign]
    t0 = time.perf_counter()
    preds = llm.classify(texts)
    secs = time.perf_counter() - t0
    labels = {idxs[i]: p.kind.value for i, p in enumerate(preds) if p.kind is not None}
    sent = "\n".join(bodies)
    left = sorted({n for n in roster if n in sent})
    return {"meeting": name, "model": model, "roster": with_roster, "roster_size": len(roster),
            "requests": len(bodies), "names_left": left, "sec": round(secs, 1), **flt.score(labels)}


def main() -> None:
    model, reps = sys.argv[1], int(sys.argv[2])
    meetings = sys.argv[3].split(",") if len(sys.argv) > 3 else ["8.txt", "EVAL_02"]
    api_key = key()
    out = HERE / "runs.jsonl"
    for rep in range(reps):
        for name in meetings:
            for with_roster in (False, True):
                r = run(model, name, with_roster, api_key)
                r["rep"] = rep
                with out.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                print(f"{rep} {name:8} roster={'on ' if with_roster else 'off'} "
                      f"P={r['P']} R={r['R']} F1={r['F1']} req={r['requests']} "
                      f"names_left={r['names_left']} ({r['sec']}s)", flush=True)


if __name__ == "__main__":
    main()
