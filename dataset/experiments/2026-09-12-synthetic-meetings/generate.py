"""Write synthetic Korean team meetings whose labels are planted, not guessed.

    python generate.py --meetings 10 --seed 20260912 [--out sheets]

Why: the Korean evaluation set has 9 commitment rows in 802, and no Korean data
at all carries decision *regions*, `settles` rows or `responds_to` links. A
pseudo-labelled real meeting cannot supply those — the labels there are a model's
guess. Here the structure is decided first (in `plan_meeting`, plain Python) and
the model only writes the words for each planned beat, so the labels are exact.

Training data only. Never the evaluation set: the text is what Qwen thinks a
Korean meeting sounds like, and scoring a model on it would measure the wrong
thing. Files are written as `SYN_*` into their own folder, and whether it helps
is settled by an ablation on the 802 human-reviewed real rows (real-only vs
synthetic-only vs mixed), not by any number computed here.

Nothing from AI Hub is used as a seed — topics and names below are invented — so
this output carries none of that corpus's terms.

Style: the rows imitate what module A's STT hands B — no punctuation, fillers,
and sentences broken across rows at intonation-phrase boundaries. A sentence
split over several rows is labelled only on the row where it ends (the labelling
guide's rule); the earlier fragments are `none`.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import sys
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")

PILOT = Path(r"F:\0final\AUTUNE\dataset\extraction_eval_pilot")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(PILOT))

KINDS_KO = {
    "commitment": "약속(자기가 할 일을 맡음)",
    "decision": "결정(무엇으로 하기로 확정)",
    "open_question": "질문(정보나 조치를 물음)",
    "concern": "우려(앞의 제안에 반대하거나 문제 제기)",
    "ambiguous": "애매(약하거나 불확실한 수락)",
    "none": "해당없음(설명, 사실 전달, 맞장구, 진행 멘트)",
}

TOPICS = [
    "신규 기능 출시 일정 조정", "고객 문의 응대 절차 정리", "사내 교육 프로그램 개편",
    "물류 창고 재고 실사 계획", "홈페이지 접근성 개선", "분기 예산 재배정",
    "협력사 계약 갱신 조건", "재택근무 규정 손질", "행사 부스 운영 방안",
    "품질 검사 기준 통일", "신입 온보딩 문서 정비", "데이터 보관 기간 정책",
]
ROLES = ["팀장", "기획", "개발", "디자인", "품질", "운영", "영업", "총무"]
NAMES = ["가온", "나래", "다움", "라온", "마루", "바름", "새롬", "슬기", "여울", "한별"]
FORMALITY = ["합쇼체(습니다체)", "해요체", "합쇼체와 해요체를 섞어서"]


FILLER = [
    "동의한다는 뜻으로 아주 짧게 한마디만 한다",
    "앞사람 말을 짧게 따라 확인한다",
    "말을 하다가 스스로 고쳐 말한다",
    "다음 순서로 넘어가자는 진행 멘트를 한다",
    "회의와 큰 상관없는 잡담을 한마디 한다",
    "앞에서 나온 숫자나 날짜를 짧게 덧붙인다",
    "앞사람 말에 짧게 웃거나 감탄한다",
]

# Rotated per meeting: a fixed example in the system prompt came back verbatim
# in the generated rows (v3 produced the decision example word for word).
EXAMPLES = {
    "commitment": ["그럼 그 표는 제가 목요일까지 정리해서 올릴게요",
                   "제가 오늘 안에 담당자한테 메일 넣어 두겠습니다",
                   "그 부분 수치는 제가 다시 뽑아서 내일 공유할게요"],
    "decision": ["그럼 2안으로 가는 걸로 하겠습니다",
                 "그러면 이번 분기는 기존 방식 그대로 두는 걸로 정리하죠",
                 "일정은 한 주 미루는 걸로 확정하겠습니다"],
    "open_question": ["그 수치는 어느 기준으로 뽑은 건가요",
                      "설치는 언제부터 들어갈 수 있나요",
                      "이 항목은 누가 맡고 있는 건가요"],
    "concern": ["그렇게 하면 검수 기간이 사라지는데요",
                "그 일정이면 현장 인력이 모자랄 것 같습니다",
                "비용이 두 번 잡히는 거 아닌가요"],
    "ambiguous": ["네 한번 볼게요", "음 그건 좀 더 생각해 봐야 할 것 같아요",
                  "일단 알겠습니다"],
}
PLAIN_DECISION = (
    "앞의 논의가 어느 쪽으로 정해졌는지를 그냥 사실처럼 말한다. "
    "이미 그렇게 되어 있는 것처럼 담담하게 한 문장으로 말한다. "
    "다음 표현은 절대 쓰지 않는다: '-하기로', '-합시다', '-하시죠', '-할게요', '-하겠습니다', "
    "'-겠-' 이 들어간 말, 그리고 '-죠' 나 '-지요' 로 끝나는 말. "
    "'정했습니다' '결정했습니다' 처럼 결정했다고 밝히는 말도 쓰지 않는다. "
    "평서형 종결('-습니다', '-입니다', '-해요', '-이에요')로만 끝낸다"
)
"""The v6 decision hint. See ``plan_meeting``: real Korean decisions are plain.

The first pilot forbade "하죠" and the model answered with every other ``-죠``
form instead -- the cue rate went 27% -> 45% while ``-겠-`` fell 50% -> 9%. Real
decisions use ``-죠`` in **0** of 61 rows, so the particle is named here rather
than one verb that carries it."""

MARKED_DECISION = (
    "앞의 논의가 어느 쪽으로 정해졌는지를 '-하겠습니다' 로 끝나는 한 문장으로 말한다. "
    "자기가 개인적으로 맡는다는 뜻이 아니라 회의가 그렇게 가기로 되었다는 뜻이다. "
    "누가 언제까지 무엇을 하겠다는 개인 약속처럼 쓰지 않는다"
)
"""Used for ``DECISION_MARKED_SHARE`` of v6 decisions, so the synthetic rate of
cue-bearing decisions lands near the real one instead of at zero.

The second pilot drove decision cues to 6% against a real 21%. Zero is the same
mistake as 70%, pointing the other way: a model that never sees ``-겠-`` on a
decision learns "``-겠-`` is never a decision", which is exactly the rule that
loses 33 of the 61 real ones. The aim is to match the distribution, not to
minimise the cue."""

DECISION_MARKED_SHARE = 0.20
"""0.20 x ~0.9 cue-bearing + 0.80 x ~0.06 lands around the real 21%."""

SITUATIONS = [
    "예산이 지난 분기보다 줄었다", "마감이 2주 앞당겨졌다", "담당자가 이번 주에 바뀌었다",
    "외부 점검이 다음 달에 있다", "인력이 한 명 빠진 상태다", "지난번 결정을 다시 보게 됐다",
    "새 도구를 시험 삼아 쓰는 중이다", "협력사 회신이 늦어지고 있다",
]


def plan_meeting(rng: random.Random, topic: str, speakers: list[dict], profile: str = "v4") -> list[dict]:
    """The label structure, decided before a single word exists.

    A beat is one planned sentence: its kind, who says it, and (for the relational
    kinds) which earlier beat it answers. Segments are shaped so the guide's rules
    hold by construction: a request is `none`/`open_question` and the *acceptance*
    is the commitment; a decision only ever appears as the settling beat of a
    region; concern and ambiguous always point back at something.

    profile "v5" (user, 2026-09-15: the real corpora rarely decide or commit
    anything, so the Korean decision/commitment signal has to come from here):
      - extra segments come from a pool where commitment and region weigh 3x the
        others, and there are 6-10 of them instead of 5-8;
      - 40% of commitments are volunteered, not answers to a request ("that one I
        will take"), since real meetings have both;
      - 30% of regions are settled by someone other than the lead.

    profile "v6" (2026-09-16) is v5's structure with **unmarked decisions**.
    Measured on the decision probe: 70% of v5's synthetic decisions carry a
    closing cue (-기로 하-, -죠, -ㅂ시다, -겠-) and only **21%** of the 61
    human-confirmed real ones do -- 79% of real decisions are plain statements.
    Synthetic commitments match reality (69% vs 65%), so only the decision beat
    changes. v5 therefore taught "a decision is a sentence with a closing cue",
    which is a rule real decisions do not follow; a real decision carrying -겠-
    then falls to `commitment`, which is 33 of the 61 misses.

    The v6 hint forbids the cues, so the sentence alone cannot say it is a
    decision and the surrounding region has to. That is the point: if the model
    still cannot learn it, the signal is not in the utterance at all.
    """
    beats: list[dict] = []
    region_no = 0

    def add(kind: str, speaker: int, **extra) -> int:
        beats.append({"kind": kind, "speaker": speaker, **extra})
        return len(beats) - 1

    lead = 0
    add("none", lead, hint="회의 시작을 알리고 오늘 다룰 주제를 말한다")
    add("none", rng.randrange(len(speakers)), hint="지난번 이야기의 현재 상태를 짧게 전한다")

    segments = ["question", "concern", "commitment", "ambiguous", "region"]
    rng.shuffle(segments)
    rich = profile in ("v5", "v6")
    if rich:
        pool = ["question", "concern", "ambiguous"] + ["commitment", "region"] * 3
        extra = [rng.choice(pool) for _ in range(rng.randrange(6, 11))]
    else:
        extra = ["question", "concern", "commitment", "ambiguous", "region"] * 2
        rng.shuffle(extra)
        extra = extra[: rng.randrange(5, 9)]
    segments = segments + extra

    def filler(n: int) -> None:
        for _ in range(n):
            add("none", rng.randrange(len(speakers)), hint=rng.choice(FILLER))

    for seg in segments:
        filler(rng.randrange(1, 4))
        a, b = rng.sample(range(len(speakers)), 2)
        if seg == "question":
            q = add("open_question", a, hint="상대에게 사실이나 일정을 묻는 진짜 질문")
            add("none", b, hint="앞 질문에 사실로 답한다", answers=q)
            if rng.random() < 0.5:
                add("none", a, hint="답을 듣고 맞장구를 친다")
        elif seg == "concern":
            p = add("none", a, hint="구체적인 방안을 제안한다. 확정하는 말은 쓰지 않는다")
            add("concern", b, hint="그 제안의 문제점을 짚는다", responds_to=p)
            add("none", a, hint="지적을 받아 사정을 설명한다")
        elif seg == "commitment":
            if rich and rng.random() < 0.4:
                s = add("none", a, hint="아직 맡은 사람이 없는 일을 언급한다. 누구에게 부탁하지는 않는다")
                add("commitment", b, hint="그 일을 자기가 맡아 무엇을 언제까지 하겠다고 먼저 나선다",
                    responds_to=s)
            else:
                r = add("none", a, hint="상대에게 어떤 일을 해 달라고 부탁한다. 묻는 형태로 쓰지 않는다")
                add("commitment", b, hint="자기가 무엇을 언제까지 하겠다고 말한다", responds_to=r)
                if rng.random() < 0.6:
                    add("none", a, hint="고맙다고 말한다")
        elif seg == "ambiguous":
            r = add("none", a, hint="상대에게 어떤 일을 검토해 달라고 부탁한다. 묻는 형태로 쓰지 않는다")
            add("ambiguous", b, hint="거절하지 않고 수락하되 무엇을 언제까지 할지는 말하지 않는다",
                responds_to=r)
        elif seg == "region":
            region_no += 1
            region = f"D{region_no}"
            add("none", a, hint="선택지 두 가지를 놓고 무엇으로 할지 논의를 연다. 확정하지 않는다",
                region=region)
            add("none", b, hint="한쪽 안의 장단점을 말한다", region=region)
            if rng.random() < 0.5:
                prev = len(beats) - 1
                add("concern", rng.choice([a, b]), hint="다른 쪽 안의 위험을 짚는다",
                    region=region, responds_to=prev)
            closer = rng.choice([a, b]) if rich and rng.random() < 0.3 else lead
            if profile == "v6":
                hint = (MARKED_DECISION if rng.random() < DECISION_MARKED_SHARE else PLAIN_DECISION)
            else:
                hint = "논의를 닫고 무엇으로 하기로 확정한다"
            add("decision", closer, hint=hint, region=region, settles=True)

    add("none", lead, hint="다음 회의 일정을 알리고 회의를 닫는다")
    return beats


SYSTEM = """당신은 한국어 팀 회의의 발화를 만드는 작가입니다. 결과는 음성인식 자막처럼 보여야 합니다.

규칙:
- 구두점을 쓰지 않습니다. 마침표, 쉼표, 물음표 모두 쓰지 않습니다.
- 반말을 쓰지 않습니다. 지정된 말투(해요체 또는 합쇼체)를 지킵니다.
- 말버릇과 머뭇거림을 자연스럽게 섞습니다: 어, 음, 그, 뭐, 아니 그게, 어 그러니까.
- 한 발화는 한 문장 정도로 짧게 씁니다. 길어도 40자 안쪽입니다.
- 지시를 설명하지 말고 그 말을 실제로 합니다. "그 요청 받아들이고" 처럼 자기 행동을 설명하는 말은 쓰지 않습니다.
- 이름을 부를 때는 참석자 명단에 있는 이름만 부릅니다.
- 숫자와 날짜 같은 구체적인 내용을 넣습니다. 실제 회사나 사람 이름은 쓰지 않습니다.

종류별로 이런 말입니다:
- 약속: 자기가 할 일을 맡습니다.
- 결정: 논의를 닫고 확정합니다.
- 질문: 정보나 조치를 묻습니다.
- 우려: 앞의 제안에 반대하거나 문제를 짚습니다.
- 애매: 수락은 하되 무엇을 언제까지 할지 말하지 않습니다. 거절이 아닙니다.
- 해당없음: 설명, 사실 전달, 맞장구, 진행 멘트입니다.
{examples}
출력 형식: 요청받은 줄 수만큼, 한 줄에 하나씩, 다른 말 없이 발화만 씁니다. 번호나 화자 이름을 붙이지 않습니다."""


def system_for(rng: random.Random) -> str:
    """One example per kind, drawn per meeting — and for one meeting in four, none
    at all, so no phrase can become the corpus's house style."""
    if rng.random() < 0.25:
        return SYSTEM.format(examples="")
    lines = ["", "말투 참고 (그대로 베끼지 말고 표현을 바꿔 씁니다):"]
    for kind, pool in EXAMPLES.items():
        lines.append(f"- {KINDS_KO[kind].split('(')[0]}: \"{rng.choice(pool)}\"")
    return SYSTEM.format(examples="\n".join(lines) + "\n")


def chunk_prompt(tok, meeting: dict, beats: list[dict], history: list[str]) -> str:
    lines = []
    for b in beats:
        who = meeting["speakers"][b["speaker"]]
        target = ""
        if "responds_to" in b or "answers" in b:
            idx = b.get("responds_to", b.get("answers"))
            target = f" (바로 앞 대화 중 '{meeting['texts'][idx][:20]}...' 에 대한 반응)" if idx < len(meeting["texts"]) else ""
        lines.append(f"- {who['name']}({who['role']}) / {KINDS_KO[b['kind']]}: {b['hint']}{target}")
    ctx = "\n".join(history[-6:]) or "(회의 시작)"
    user = (
        f"회의 주제: {meeting['topic']}\n"
        f"참석자: {', '.join(f'{s['name']}({s['role']})' for s in meeting['speakers'])}\n"
        f"말투: {meeting['formality']}\n\n"
        f"앞의 대화:\n{ctx}\n\n"
        f"다음 {len(beats)}개의 발화를 순서대로 쓰세요. 각 줄의 지시:\n" + "\n".join(lines)
    )
    return tok.apply_chat_template(
        [{"role": "system", "content": meeting["system"]}, {"role": "user", "content": user}],
        tokenize=False, add_generation_prompt=True,
    )


def clean_line(text: str) -> str:
    text = re.sub(r"^[\s\-\*\d\.\)]+", "", text.strip())
    text = re.sub(r"^[가-힣]{2,4}\s*\([^)]*\)\s*:\s*", "", text)  # a speaker prefix, if it slipped in
    text = re.sub(r"^[가-힣]{2,4}\s*:\s*", "", text)
    text = re.sub(r"[.,!?·…]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def split_rows(text: str, rng: random.Random) -> list[str]:
    """Break a sentence into intonation-phrase rows, as the STT output does."""
    words = text.split()
    if len(words) < 6 or rng.random() < 0.55:
        return [text]
    cut = rng.randrange(2, len(words) - 2)
    parts = [" ".join(words[:cut]), " ".join(words[cut:])]
    return [p for p in parts if p]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--meetings", type=int, default=10)
    ap.add_argument("--seed", type=int, default=20260912)
    ap.add_argument("--out", default="sheets")
    ap.add_argument("--chunk", type=int, default=6, help="beats written per model call")
    ap.add_argument("--wave", type=int, default=10, help="meetings generated in one batch")
    ap.add_argument("--profile", choices=["v4", "v5", "v6"], default="v4",
                    help="label mix; v5 weighs commitments and decision regions 3x, "
                         "v6 is v5 with unmarked decisions (see plan_meeting)")
    ap.add_argument("--repeat-cap", type=int, default=3,
                    help="how often one sentence may appear across the corpus (short filler is exempt)")
    args = ap.parse_args()

    import torch  # noqa: PLC0415
    from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: PLC0415

    from local_llm_label import MODEL  # noqa: PLC0415

    rng = random.Random(args.seed)
    meetings = []
    for i in range(args.meetings):
        n = rng.randrange(3, 6)
        names = rng.sample(NAMES, n)
        roles = ["팀장"] + rng.sample([r for r in ROLES if r != "팀장"], n - 1)
        speakers = [{"name": nm, "role": ro, "label": f"S{j + 1}"} for j, (nm, ro) in enumerate(zip(names, roles))]
        topic = TOPICS[(args.seed + i) % len(TOPICS)]
        m = {
            "id": f"SYN_{args.seed}_{i + 1:02d}", "topic": topic, "speakers": speakers,
            "formality": rng.choice(FORMALITY), "situation": rng.choice(SITUATIONS),
            "system": system_for(rng), "texts": [],
        }
        m["beats"] = plan_meeting(rng, topic, speakers, args.profile)
        m["history"] = []
        meetings.append(m)

    tok = AutoTokenizer.from_pretrained(MODEL)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16).to("cuda").eval()

    out_dir = HERE / args.out
    raw_dir = out_dir / "_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    # One wave at a time: every meeting in a wave is a prompt in the same batch,
    # so the wave size is the batch size, and a 12 GB card will not hold 100.
    # Each finished wave's text is saved, so a run that dies (v4 did, in wave 3)
    # resumes from the next wave. The plan comes from the seed alone, so a resumed
    # run rebuilds the same beats; sheets are still written once, at the end, so
    # the repeat cap and row splitting see the whole corpus in the same order.
    waves = [meetings[i : i + args.wave] for i in range(0, len(meetings), args.wave)]
    for w, wave in enumerate(waves):
        raw = raw_dir / f"wave_{w + 1:02d}.json"
        if raw.exists():
            saved = json.loads(raw.read_text("utf-8"))
            for m in wave:
                m["texts"] = saved[m["id"]]
            print(f"wave {w + 1}/{len(waves)} loaded from {raw.name}", flush=True)
            continue
        run_wave(tok, model, wave, args, torch)
        raw.write_text(json.dumps({m["id"]: m["texts"] for m in wave}, ensure_ascii=False), "utf-8")
        print(f"wave {w + 1}/{len(waves)} done, {time.time() - started:.0f}s elapsed", flush=True)

    write_sheets(meetings, out_dir, random.Random(args.seed + 1), args.repeat_cap)
    print(f"{len(meetings)} meetings -> {out_dir} in {time.time() - started:.0f}s")


def run_wave(tok, model, meetings: list[dict], args, torch) -> None:
    rounds = max((len(m["beats"]) + args.chunk - 1) // args.chunk for m in meetings)
    for _r in range(rounds):
        active = [m for m in meetings if len(m["texts"]) < len(m["beats"])]
        if not active:
            break
        prompts, spans = [], []
        for m in active:
            start = len(m["texts"])
            beats = m["beats"][start : start + args.chunk]
            prompts.append(chunk_prompt(tok, m, beats, m["history"]))
            spans.append((m, beats))
        enc = tok(prompts, return_tensors="pt", padding=True).to("cuda")
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=48 * args.chunk, do_sample=True,
                                 temperature=0.95, top_p=0.95, pad_token_id=tok.pad_token_id)
        new = out[:, enc["input_ids"].shape[1]:]
        for (m, beats), row in zip(spans, new):
            text = tok.decode(row, skip_special_tokens=True)
            lines = [clean_line(x) for x in text.splitlines() if clean_line(x)]
            for j, beat in enumerate(beats):
                line = lines[j] if j < len(lines) else ""
                m["texts"].append(line)
                who = m["speakers"][beat["speaker"]]
                m["history"].append(f"{who['name']}: {line}")
        done = sum(len(m["texts"]) for m in meetings)
        print(f"  round {_r + 1}/{rounds}: {len(active)} meetings, {done} beats written", flush=True)


def write_sheets(meetings: list[dict], out_dir: Path, rng: random.Random, repeat_cap: int = 3) -> None:
    from collections import Counter  # noqa: PLC0415

    from pilot_sheets import COLUMNS  # noqa: PLC0415

    seen: Counter[str] = Counter()
    dropped = 0
    manifest = []
    for m in meetings:
        rows, beat_row = [], {}
        start_sec = 0.0
        for i, (beat, text) in enumerate(zip(m["beats"], m["texts"])):
            if not text:
                continue
            who = m["speakers"][beat["speaker"]]
            if len(text) > 10:
                seen[text] += 1
                if seen[text] > repeat_cap:
                    dropped += 1
                    continue
            parts = split_rows(text, rng)
            for k, part in enumerate(parts):
                last = k == len(parts) - 1
                rows.append({
                    "row": str(len(rows) + 1),
                    "utterance_id": f"{m['id']}-{len(rows) + 1}",
                    "start": f"{start_sec:.2f}",
                    "speaker": who["label"],
                    "role": who["role"],
                    "text": part,
                    # Only the row a sentence ends on carries its label.
                    "kind": beat["kind"] if last else "none",
                    "decision_id": beat.get("region", "") if last else "",
                    "settles": "1" if last and beat.get("settles") else "",
                    "responds_to": "",
                    "note": "",
                })
                start_sec += 2.0 + len(part) * 0.08
            beat_row[i] = len(rows)  # the row the sentence ended on
        for i, beat in enumerate(m["beats"]):
            target = beat.get("responds_to")
            if target is not None and i in beat_row and target in beat_row:
                rows[beat_row[i] - 1]["responds_to"] = str(beat_row[target])
        settled = {r["decision_id"] for r in rows if r["settles"] == "1"}
        for r in rows:
            if r["decision_id"] and r["decision_id"] not in settled:
                r["decision_id"] = ""
        with (out_dir / f"{m['id']}.A.csv").open("w", encoding="utf-8-sig", newline="") as fa, \
             (out_dir / f"{m['id']}.G.csv").open("w", encoding="utf-8-sig", newline="") as fg:
            wa, wg = csv.DictWriter(fa, fieldnames=COLUMNS), csv.DictWriter(fg, fieldnames=COLUMNS)
            wa.writeheader(); wg.writeheader()
            for row in rows:
                wa.writerow({**row, "kind": "", "decision_id": "", "settles": "", "responds_to": ""})
                wg.writerow(row)
        manifest.append({"meeting": m["id"], "topic": m["topic"], "speakers": len(m["speakers"]),
                         "formality": m["formality"], "rows": len(rows),
                         "beats": len(m["beats"]), "empty_beats": sum(1 for t in m["texts"] if not t)})
    print(f"dropped {dropped} rows over the repeat cap ({repeat_cap})")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), "utf-8")


# Guarded so `import generate` (e.g. to inspect plan_meeting) never starts a
# generation run with the default --out, which would overwrite sheets/.
if __name__ == "__main__":
    main()
