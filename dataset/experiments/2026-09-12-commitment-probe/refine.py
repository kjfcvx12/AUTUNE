"""Try prompt changes on the reviewed probe rows before scanning again.

    python refine.py score  [--variants base,v1,yn] [--batch 6]   # GPU
    python refine.py report                                       # counts only

The review left 939 human-labelled rows: the 183 candidates and the 756
neighbours the reviewer also labelled (132 commitments between them). That is a
development set for the probe's filter. Three prompts are scored on every row:

- base: local_llm_label.SYSTEM, the prompt the scan used (reproducibility check)
- v1:   the same six-way prompt, with "a concrete action after this meeting" in
        the commitment definition and a list of "~겠습니다" forms that are not
        commitments (announcing what the speaker is about to say, running order,
        guesses and wishes, open-ended pledges)
- yn:   a yes/no question, "is this a commitment?", with the same exclusions

Rules that only keep a subset of the scan's candidates are measured exactly on
the scanned population. Rules that can flag other rows are measured only on the
rows near a candidate, so their precision is optimistic: the report says which.

Every example sentence in the prompts is invented. Counts and ids only, never
utterance text -- AI Hub terms.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PILOT = Path(r"F:\0final\AUTUNE\dataset\extraction_eval_pilot")
sys.path.insert(0, str(PILOT))

from pilot_sheets import clean  # noqa: E402

SHEETS = HERE / "sheets"
OUT = HERE / "results" / "refine_scores.json"
KINDS = ["commitment", "decision", "open_question", "concern", "ambiguous", "none"]
# Same as probe.py and local_llm_label.py, so "pre" and the windows match the scan.
ENDING = re.compile(r"겠|ㄹ게|를게|을게|게요|려고|예정|드리|볼게")
PRE_BACK, PRE_FWD = 1, 2
BEFORE, AFTER = 4, 2

NOT_COMMITMENT = """"~겠습니다", "~드리겠습니다"로 끝나도 약속이 아닌 경우:
- 지금 이 자리에서 바로 하는 말하기의 예고: "설명드리겠습니다." "소개해 드리겠습니다." "말씀드리겠습니다." "질문 하나 드리겠습니다."
- 진행·순서 안내와 인사: "다음 순서로 넘어가겠습니다." "이상으로 마치겠습니다." "감사드리겠습니다."
- 추측·느낌·희망: "그러면 좋겠습니다." "많이 힘드시겠어요." "곧 끝나겠네요."
- 이미 했거나 늘 하는 일의 설명: "매년 그렇게 해 오고 있습니다."
- 다른 사람에게 하라고 하는 말: "이건 담당 부서에서 정리해 주시죠.\""""

SYSTEM_V1 = f"""당신은 한국어 회의록의 발화를 분류하는 라벨러입니다. 표시된 [대상] 발화 하나를 아래 여섯 가지 중 하나로 분류합니다.

1 약속 — 화자가 자신(또는 자기 팀)이 이 자리가 끝난 뒤에 할 구체적인 일을 떠맡음. 무엇을 할지가 드러나야 합니다. 예: "제가 내일까지 정리해서 메일로 드리겠습니다." "그 자료는 저희 팀에서 다음 주에 보내 드릴게요." "검토해서 다음 회의 때 보고드리겠습니다."
2 결정 — 논의 끝에 무엇을 하기로 확정했는지 말하는 발화. 예: "원안대로 가결되었음을 선포합니다." "그럼 다음 회의 때 다시 보는 걸로 하겠습니다."
3 질문 — 다른 사람에게 정보·의견·조치를 묻거나 요청하는 진짜 질문. 예: "그 일정은 왜 다음 달로 밀린 거죠?" "이 부분 자료로 주실 수 있습니까?"
4 우려 — 앞의 말이나 제안에 대한 반대·이의·문제 제기. 반박하는 수사 의문문 포함. 예: "그 방식이면 같은 비용이 두 번 잡혀서 맞지 않는 것 같습니다."
5 애매 — 요청이나 제안에 대한 약하거나 불확실한 수락, 또는 무엇을 언제까지 할지 없는 다짐. 예: "검토해 보겠습니다." "한번 볼게요." "아마 될 겁니다." "노력하겠습니다."
6 해당없음 — 그 밖의 모든 것: 설명, 사실 전달, 맞장구("네.", "예."), 말 더듬음, 인사, 진행 멘트, 문장의 앞부분만 있는 조각.

{NOT_COMMITMENT}
위의 경우는 모두 6입니다.

규칙:
- 문장이 여러 발화에 걸쳐 잘려 있으면, 문장이 끝나는 발화에만 라벨을 붙이고 앞 조각은 6입니다.
- 다른 사람에게 일을 시키는 말 자체는 6(또는 질문 형태면 3)이고, 그 요청을 받아들이는 발화가 1 또는 5입니다.
- 여러 개가 해당하면 2 > 4 > 3 > 5 > 1 순서로 앞의 것을 고릅니다.
- 대부분의 발화는 6입니다.

숫자 하나만 답합니다."""

SYSTEM_YN = f"""당신은 회의록에서 '약속'만 골라내는 검토자입니다. [대상] 발화에서 화자가 자신(또는 자기 팀)이 이 자리가 끝난 뒤에 할 구체적인 일을 떠맡는지 판단합니다.

1 예 — 무엇을 할지가 드러나는 약속. 예: "제가 내일까지 정리해서 메일로 드리겠습니다." "그 자료는 저희 팀에서 챙기겠습니다." 앞사람이 구체적으로 요청한 일을 "네, 그렇게 하겠습니다."라고 받아들이는 것도 예입니다.
2 아니오 — 그 밖의 모든 것.

{NOT_COMMITMENT}
- 무엇을 언제까지 할지 없는 다짐이나 약한 수락: "노력하겠습니다." "검토해 보겠습니다."
위의 경우는 모두 아니오입니다.

문장이 여러 발화에 걸쳐 잘려 있으면, 문장이 끝나는 발화만 예가 될 수 있고 앞 조각은 아니오입니다.

숫자 하나만 답합니다."""

QUESTION = {
    "base": "[대상] 발화의 분류 번호는?",
    "v1": "[대상] 발화의 분류 번호는?",
    "yn": "[대상] 발화는 약속입니까? 1(예) 또는 2(아니오)로 답하세요.",
}


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_meeting(path: str) -> list[dict]:
    """The same rows probe.py's load_rows produced, so row ids line up."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = []
    for i, u in enumerate(data["utterance"], start=1):
        text = clean(u.get("form") or "")
        if text:
            rows.append({"row": str(i), "speaker": str(u.get("speaker_id") or ""),
                         "role": str(u.get("speaker_role") or ""), "text": text})
    return rows


def dev_set() -> tuple[list[dict], dict[str, list[dict]]]:
    used = {u["meeting"]: u for u in json.loads((HERE / "results" / "used_meetings.json").read_text("utf-8"))}
    items: list[dict] = []
    for lpath in sorted(SHEETS.glob("*.L.csv")):
        m = lpath.name[: -len(".L.csv")]
        r_by_row = {r["row"]: r for r in read(SHEETS / f"{m}.R.csv")}
        for lr in read(lpath):
            rr = r_by_row.get(lr["row"])
            if not rr or not rr.get("reviewed", "").strip():
                continue
            items.append({"meeting": m, "group": used[m]["group"], "row": lr["row"], "human": rr["kind"],
                          "candidate": bool(lr["llm_kind"]),
                          "scan_p": float(lr["p_commitment"]) if lr["llm_kind"] else None})
    rows_of = {m: load_meeting(used[m]["path"]) for m in sorted({it["meeting"] for it in items})}
    for it in items:
        rows = rows_of[it["meeting"]]
        index = next((i for i, r in enumerate(rows) if r["row"] == it["row"]), None)
        if index is None:
            raise SystemExit(f"{it['meeting']} row {it['row']}: not in the source file")
        it["index"] = index
        it["pre"] = bool(ENDING.search(" ".join(r["text"] for r in rows[max(0, index - PRE_BACK): index + PRE_FWD + 1])))
    return items, rows_of


def build(tok, system: str, question: str, window: list[dict], target: int) -> str:
    # Identical to local_llm_label.prompt apart from the system text and the question.
    lines = [f"{'[대상] ' if i == target else ''}{r['speaker']}({r['role']}): {r['text']}" for i, r in enumerate(window)]
    user = "회의 발화 (앞뒤 문맥 포함):\n" + "\n".join(lines) + "\n\n" + question
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def score_cmd(args: argparse.Namespace) -> None:
    from local_llm_label import SYSTEM, load_model, score  # noqa: PLC0415 -- torch only here

    systems = {"base": SYSTEM, "v1": SYSTEM_V1, "yn": SYSTEM_YN}
    items, rows_of = dev_set()
    saved = json.loads(OUT.read_text("utf-8")) if OUT.exists() else {}
    tok, model, digit_ids = load_model()
    for variant in args.variants.split(","):
        if variant in saved:
            print(f"{variant}: already scored, skipped", flush=True)
            continue
        keys, prompts = [], []
        for it in items:
            rows, i = rows_of[it["meeting"]], it["index"]
            prompts.append(build(tok, systems[variant], QUESTION[variant], rows[max(0, i - BEFORE): i + AFTER + 1], min(i, BEFORE)))
            keys.append(f"{it['meeting']}:{it['row']}")
        # Longest first: a batch is padded to its longest prompt.
        order = sorted(range(len(prompts)), key=lambda k: -len(prompts[k]))
        ids = digit_ids[:2] if variant == "yn" else digit_ids
        result: dict[str, list[float]] = {}
        started = time.time()
        for s in range(0, len(order), 120):
            chunk = order[s: s + 120]
            for k, p in zip(chunk, score(tok, model, ids, [prompts[k] for k in chunk], batch=args.batch)):
                result[keys[k]] = [round(x, 4) for x in p]
            print(f"{variant}: {len(result)}/{len(order)} rows, {len(result) / (time.time() - started):.1f} rows/s", flush=True)
        saved[variant] = result
        OUT.write_text(json.dumps(saved), "utf-8")


def pct(hit: int, n: int) -> str:
    return f"{hit}/{n} {hit / n:.0%}" if n else "0/0"


def report_cmd(_: argparse.Namespace) -> None:
    items, _rows = dev_set()
    saved = json.loads(OUT.read_text("utf-8")) if OUT.exists() else {}
    for it in items:
        for variant, probs in saved.items():
            it[variant] = probs[f"{it['meeting']}:{it['row']}"]
    commit = [it for it in items if it["human"] == "commitment"]
    n_cand = sum(it["candidate"] for it in commit)
    print(f"dev rows {len(items)} (candidates {sum(it['candidate'] for it in items)}), "
          f"human commitments {len(commit)} (on candidates {n_cand}, on neighbours {len(commit) - n_cand})")

    def top(p: list[float]) -> str:
        return KINDS[max(range(len(p)), key=p.__getitem__)]

    if "base" in saved:
        diffs = [abs(it["base"][0] - it["scan_p"]) for it in items if it["candidate"]]
        flips = sum(it["candidate"] != (it["pre"] and it["base"][0] >= 0.10) for it in items)
        print(f"reproducibility: |p_commitment rerun - scan| max {max(diffs):.3f}, mean {sum(diffs) / len(diffs):.4f}; "
              f"rows whose candidate status flips {flips}")

    neigh = [it for it in commit if not it["candidate"]]
    line = f"missed neighbour commitments ({len(neigh)}): pre-filter fails {sum(not it['pre'] for it in neigh)}"
    if "base" in saved:
        line += (f", passes but base p < 0.10 {sum(it['pre'] and it['base'][0] < 0.10 for it in neigh)}"
                 f", passes with p >= 0.10 {sum(it['pre'] and it['base'][0] >= 0.10 for it in neigh)}")
    print(line)

    rules: list[tuple[str, bool, object]] = [("scan candidates", True, lambda it: it["candidate"])]
    if "v1" in saved:
        rules += [
            ("candidates ∧ v1 argmax commitment", True, lambda it: it["candidate"] and top(it["v1"]) == "commitment"),
            ("candidates ∧ v1 p ≥ 0.5", True, lambda it: it["candidate"] and it["v1"][0] >= 0.5),
            ("pre ∧ v1 argmax commitment", False, lambda it: it["pre"] and top(it["v1"]) == "commitment"),
            ("v1 argmax commitment (no pre-filter)", False, lambda it: top(it["v1"]) == "commitment"),
        ]
    if "yn" in saved:
        for cut in (0.5, 0.7, 0.9):
            rules.append((f"candidates ∧ yn ≥ {cut}", True, lambda it, c=cut: it["candidate"] and it["yn"][0] >= c))
        rules += [
            ("pre ∧ yn ≥ 0.5", False, lambda it: it["pre"] and it["yn"][0] >= 0.5),
            ("yn ≥ 0.5 (no pre-filter)", False, lambda it: it["yn"][0] >= 0.5),
        ]
    if "v1" in saved and "yn" in saved:
        rules.append(("candidates ∧ v1 argmax ∧ yn ≥ 0.5", True,
                      lambda it: it["candidate"] and top(it["v1"]) == "commitment" and it["yn"][0] >= 0.5))

    groups = sorted({it["group"] for it in items})
    print(f"\n{'rule':<40}{'flagged':>8}{'precision':>14}{'recall/132':>13}{'of 76':>7}{'of 56':>7}  "
          + "  ".join(f"{g} prec" for g in groups) + "  measured")
    for name, exact, keep in rules:
        flagged = [it for it in items if keep(it)]
        hits = [it for it in flagged if it["human"] == "commitment"]
        by_group = []
        for g in groups:
            fg = [it for it in flagged if it["group"] == g]
            by_group.append(pct(sum(it["human"] == "commitment" for it in fg), len(fg)))
        print(f"{name:<40}{len(flagged):>8}{pct(len(hits), len(flagged)):>14}{len(hits) / len(commit):>13.0%}"
              f"{sum(it['candidate'] for it in hits):>7}{sum(not it['candidate'] for it in hits):>7}  "
              + "  ".join(f"{b:>14}" for b in by_group) + ("  exact" if exact else "  near candidates only"))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("--variants", default="base,v1,yn")
    s.add_argument("--batch", type=int, default=6)
    s.set_defaults(func=score_cmd)
    r = sub.add_parser("report")
    r.set_defaults(func=report_cmd)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
