"""Does the resolver give a row without a summary a sentence that is right?

Order of 2026-10-08 (the user, via 리더): every row should carry a written
sentence. Before widening the resolver to every decision (W2), measure what it
writes and what its checks refuse -- on invented lines only.

Two passes, the service's own functions, the resolver as dev runs it
(``resolver_impl=llm``, first model ``gemini-3.5-flash-lite``, second
``gemini-3.8-flash``):

  items      commitments that carry no classifier summary -- the state of a
             line the classifier wrote nothing for, or one step 4 promoted --
             through ``service.resolve_commitment_summaries``. The first ten
             of 8.txt's gold commitments and ten in the meeting invented below.
  decisions  every decision of the invented meeting through
             ``service.resolve_decision_summaries`` with ``needs_write_up``
             answering yes for all of them, which is what W2 would do. Each is
             marked with what today's rule says, so the two sets can be told
             apart.

Usage: measure_rows.py count          -- batches a pass, nothing sent
       measure_rows.py run <out.json> -- at most CAP requests in all
       ... items                      -- the twenty commitments only (the
                                         re-run after the two checks of
                                         `extraction/item-sentence-guards`)

Prints counts. The sentences go to the output file: every line here is
invented (8.txt is the invented meeting of 2026-09-26), no person's name.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path("F:/0final/AUTUNE")
EXP = ROOT / "dataset" / "experiments"
SRC8 = EXP / "2026-09-26-local-vs-api" / "scratch_e27a3912" / "step1_chunks_overlap_8.json"
YES8 = {14, 20, 29, 34, 35, 37, 45, 46, 48, 49, 68, 69, 74, 75, 77, 79}
USED8 = set(sorted(YES8)[:10])  # the cap: the first ten of its gold commitments
KEY_FP = "c41ba374"  # the AUTUNE_LLM_API_KEY the process reads (HISTORY 10-07)
CAP = int(os.environ.get("CAP", "16"))  # 16 in all; a later run is given what is left
PACE = float(os.environ.get("PACE", "2.0"))

keys = [
    line.split("=", 1)[1].strip().strip('"').strip("'")
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines()
    if line.startswith("AUTUNE_LLM_API_KEY=")
]
# pydantic-settings takes the last line of a name defined twice; so does this.
prints = [hashlib.sha256(k.encode()).hexdigest()[:8] for k in keys]
print(f"key lines in .env: {len(keys)}; the one read (last): {prints[-1] if prints else None}")
if not keys or prints[-1] != KEY_FP:
    sys.exit("the key the process would read is not the one this was checked against")
os.environ.update(
    AUTUNE_ENV="local",
    AUTUNE_LLM_API_KEY=keys[-1],
    AUTUNE_EXTRACTION_LLM_API_KEY="",
    AUTUNE_EXTRACTION_RESOLVER_IMPL="llm",
    AUTUNE_EXTRACTION_RESOLVER_MODEL="gemini-3.5-flash-lite",
    AUTUNE_EXTRACTION_RESOLVER_SECOND_MODEL="gemini-3.8-flash",
    AUTUNE_EXTRACTION_RESOLVER_MIN_SIMILARITY="",
    AUTUNE_EXTRACTION_LLM_ACKNOWLEDGED_392="true",
)

from autune_contracts.enums import UtteranceKind as K  # noqa: E402
from autune_extraction import service  # noqa: E402
from autune_extraction.decisions import (  # noqa: E402
    ClassifiedUtterance,
    group_decisions,
    identified,
    needs_write_up,
)
from autune_extraction.pipeline import resolver as R  # noqa: E402
from autune_extraction.pipeline.base import Resolution  # noqa: E402
from autune_extraction.pipeline.registry import get_resolver  # noqa: E402

C, D = K.COMMITMENT, K.DECISION
DAY = date(2026, 10, 8)

# Invented for this measurement: roles only, no person's or company's name.
INVENTED: list[tuple[str, K | None, str]] = [
    ("진행", None, "오늘은 출시 일정이랑 결제 오류 건, 그리고 온보딩 화면 개편을 정리하려고 합니다."),
    ("개발", None, "결제 오류는 원인을 찾았는데, 카드사 응답이 3초를 넘으면 저희 쪽에서 타임아웃이 납니다."),
    ("기획", None, "그럼 타임아웃을 늘리면 되는 건가요?"),
    ("개발", None, "5초로 늘리고 재시도를 한 번 넣는 게 안전합니다."),
    ("진행", D, "네 그럼 타임아웃은 5초로 늘리고 재시도 한 번 넣는 걸로 하겠습니다."),
    ("개발", C, "그건 제가 볼게요."),
    ("운영", None, "고객 문의가 어제만 14건 들어왔는데 공지를 올려야 하지 않을까요?"),
    ("기획", None, "문의 채널에도 같은 내용을 걸어 두는 게 좋겠습니다."),
    ("진행", D, "공지는 오늘 오후 3시에 올리는 걸로 하죠."),
    ("운영", C, "네 제가 올리겠습니다."),
    ("디자인", None, "온보딩은 지금 5단계인데 이탈이 2단계에서 제일 많습니다."),
    ("기획", None, "2단계 약관 동의를 마지막으로 옮기는 안과 아예 3단계로 줄이는 안이 있습니다."),
    ("디자인", None, "3단계로 줄이면 일러스트를 새로 그려야 해서 2주 더 걸립니다."),
    ("진행", D, "그럼 이번에는 약관 동의만 마지막으로 옮기고 단계 수는 그대로 두기로 합시다."),
    ("기획", D, "좋습니다 그렇게 하죠."),
    ("디자인", C, "시안은 제가 챙겨 볼게요."),
    ("진행", None, "출시일 얘기로 넘어가면, QA가 금요일에 끝난다고 했죠?"),
    ("개발", None, "네 금요일 오후까지는 끝납니다."),
    ("기획", None, "그러면 다음 주 화요일 출시가 가능하겠네요."),
    ("진행", D, "그렇게 갑시다."),
    ("운영", None, "출시 당일 모니터링은 누가 하나요?"),
    ("개발", C, "그날은 제가 맡겠습니다."),
    ("진행", None, "마케팅 메일은 출시 다음 날 보내는 게 어떨까요?"),
    ("기획", None, "당일에 보내면 장애 났을 때 곤란하니까 다음 날이 낫습니다."),
    ("진행", D, "네 메일은 출시 다음 날인 수요일 오전에 보내는 걸로 결정하겠습니다."),
    ("기획", C, "문구는 제가 정리해서 공유드릴게요."),
    ("운영", None, "환불 정책 안내 문구도 바꿔야 하는데요."),
    ("기획", None, "지금 문구는 예전 정책 기준이라 문의가 계속 들어옵니다."),
    ("진행", D, "그건 법무 검토가 끝난 뒤에 하기로 하고 이번 출시에는 넣지 않겠습니다."),
    ("디자인", None, "다크 모드는 이번에 들어가나요?"),
    ("개발", None, "다크 모드는 색상 토큰 작업이 절반쯤 남았습니다."),
    ("디자인", None, "화면 수로는 40개 중에 18개가 남았습니다."),
    ("진행", D, "다크 모드는 이번 출시에서 빼고 다음 분기로 미룹니다."),
    ("개발", None, "로그 보관 기간은 30일에서 90일로 늘려도 될까요?"),
    ("운영", None, "비용이 월 20만 원 정도 늘어납니다."),
    ("개발", None, "장애 원인을 추적할 때 30일이면 모자랄 때가 많았습니다."),
    ("진행", D, "그 정도면 괜찮으니 90일로 늘립시다."),
    ("개발", C, "네 그럼 그것도 제가 반영할게요."),
    ("기획", None, "베타 사용자 설문은 몇 명한테 보낼까요?"),
    ("운영", None, "지난번에는 300명한테 보냈는데 응답이 40개였습니다."),
    ("진행", D, "200명한테 보내고 응답이 50개 넘으면 마감하는 걸로 하죠."),
    ("기획", C, "설문은 제가 목요일까지 만들어 두겠습니다."),
    ("운영", None, "고객센터 운영 시간은 출시 주에만 밤 10시까지로 늘리면 어떨까요?"),
    ("기획", None, "출시 주에는 문의가 평소의 두 배쯤 들어옵니다."),
    ("진행", D, "좋아요 그렇게 하시죠."),
    ("운영", C, "근무표는 제가 다시 짜 볼게요."),
    ("디자인", None, "앱 아이콘은 A안과 B안 중에 정해야 합니다."),
    ("기획", None, "테스트에서는 B안 클릭률이 12% 높았습니다."),
    ("진행", D, "그럼 아이콘은 B안으로 확정합니다."),
    ("디자인", C, "네 최종 파일은 내일까지 올려 둘게요."),
    ("기획", None, "출시 전에 한 번 더 모여서 점검하면 좋겠습니다."),
    ("운영", None, "월요일 오후는 다들 괜찮다고 합니다."),
    ("진행", D, "다음 회의는 출시 전날인 월요일 오후 2시에 하겠습니다."),
    ("진행", C, "회의록은 제가 정리해서 올리겠습니다."),
]


def meeting_8() -> list[ClassifiedUtterance]:
    payload = json.loads(SRC8.read_text(encoding="utf-8"))
    seen: dict[int, str] = {}
    for chunk in payload["chunks"]:
        for u in chunk["utterances"]:
            if u["idx"] > 0:
                seen.setdefault(u["idx"], u["text"])
    return [
        ClassifiedUtterance(
            id=f"utt_8_{i}", kind=C if i in USED8 else None, confidence=0.9, text=text
        )
        for i, text in sorted(seen.items())
    ]


def invented() -> list[ClassifiedUtterance]:
    return [
        ClassifiedUtterance(id=f"utt_m_{i}", kind=kind, confidence=0.9, text=text, speaker=who)
        for i, (who, kind, text) in enumerate(INVENTED)
    ]


class Probe:
    """Counts what the resolver would send or sends, and notes why each answer
    was refused. ``count`` mode replaces the call with the batching alone."""

    def __init__(self, resolver: R.LlmResolver, *, send: bool) -> None:
        self.resolver = resolver
        self.send = send
        self.sent = 0
        self.batches: list[int] = []
        self.verdicts: dict[str, list[dict]] = {}
        if send:
            client = resolver._client
            real = client.request

            def request(method: str, path: str, *, json: dict) -> dict:  # noqa: A002
                if self.sent >= CAP:
                    raise RuntimeError("request cap reached")
                self.sent += 1
                time.sleep(PACE)
                return real(method, path, json=json)

            client.request = request  # type: ignore[method-assign]
            accept = resolver._accept

            def noted(answer, request, surface, numbered):  # type: ignore[no-untyped-def]
                result = accept(answer, request, surface, numbered)
                self.verdicts.setdefault(request.target_id, []).append(
                    {
                        "model": resolver.last_model,
                        "why": self.why(answer, request, surface, numbered),
                        "wrote": self.candidate(answer, numbered),
                        "kept": result is not None and result.text != request.target,
                    }
                )
                return result

            resolver._accept = noted  # type: ignore[method-assign]
        else:

            def batched(requests: list) -> list[Resolution]:
                for purpose in dict.fromkeys(r.purpose for r in requests):
                    same = [(i, r) for i, r in enumerate(requests) if r.purpose == purpose]
                    self.batches += [len(batch) for batch in resolver._batches(same)]
                return [Resolution(r.target) for r in requests]

            resolver.resolve_with_evidence = batched  # type: ignore[method-assign]

    @staticmethod
    def candidate(answer: str, numbered) -> str:  # type: ignore[no-untyped-def]
        text = answer if numbered is None else R._read_summary(answer, numbered)[0]
        return text.strip().strip("\"'“”‘’").strip()

    def why(self, answer, request, surface, numbered) -> str:  # type: ignore[no-untyped-def]
        text = self.candidate(answer, numbered)
        if not text:
            return "empty"
        if "\n" in text:
            return "more than one line"
        restored = R._restored(text, surface)
        if restored is None:
            return "invented placeholder"
        if not R._sound(restored, request):
            return "unsound (adds a clause, drops the deadline, or runs long)"
        if not R._passes_grounding(
            restored, request, None, None, keep_ending=request.purpose != "decision"
        ):
            return "ungrounded (a number, a name or the ending is not in the lines)"
        if request.purpose != "decision" and hasattr(R, "_keeps_what_was_said"):
            if not R._keeps_what_was_said(restored, request.target):
                return "a said word changed"
            if R._filled_from_what_followed(restored, request):
                return "filled from a following line"
        if R._ends_the_same(restored, request.target):
            return "unchanged"
        return "ok"


def items_pass(probe: Probe, name: str, classified: list[ClassifiedUtterance]) -> list[dict]:
    before = probe.sent
    resolved = service.resolve_commitment_summaries(probe.resolver, classified)
    rows = []
    for u in classified:
        if u.kind is not C:
            continue
        got = resolved[u.id]
        rows.append(
            {
                "meeting": name,
                "id": u.id,
                "said": u.text,
                "written": got.text if got.text != u.text else None,
                "cited": len(got.used),
                "answers": probe.verdicts.get(u.id, []),
            }
        )
    print(f"items {name}: rows {len(rows)}, requests {probe.sent - before}")
    return rows


def decisions_pass(probe: Probe, classified: list[ClassifiedUtterance]) -> list[dict]:
    found = identified("mtg_m", group_decisions(classified, day=DAY), classified)
    asked_today = {id_: needs_write_up(group) for id_, group in found}
    before = probe.sent
    service.needs_write_up = lambda group: True  # W2: every decision without a summary
    try:
        resolved = service.resolve_decision_summaries(
            probe.resolver, classified, meeting_id="mtg_m", day=DAY
        )
    finally:
        service.needs_write_up = needs_write_up
    rows = []
    for id_, group in found:
        got = resolved.get(id_)
        rows.append(
            {
                "id": group.substance_id,
                "asked_today": asked_today[id_],
                "said": group.core_text,
                "today": group.statement,
                "written": got.text if got is not None and got.text != group.core_text else None,
                "cited": len(got.used) if got is not None else 0,
                "answers": probe.verdicts.get(group.substance_id, []),
            }
        )
    print(
        f"decisions: rows {len(rows)} (asked today {sum(asked_today.values())}, "
        f"new with W2 {len(rows) - sum(asked_today.values())}), requests {probe.sent - before}"
    )
    return rows


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "count"
    resolver = get_resolver()
    assert isinstance(resolver, R.LlmResolver)
    probe = Probe(resolver, send=mode == "run")
    decisions = [] if "items" in sys.argv else decisions_pass(probe, invented())
    items = items_pass(probe, "invented", invented()) + items_pass(probe, "8.txt", meeting_8())
    if mode != "run":
        print(f"batches: {probe.batches} -> {len(probe.batches)} first requests;")
        print("the second model is asked at most once a batch that leaves a row, five a call:")
        print(f"at most {len(probe.batches) + min(len(probe.batches), 15)} requests, cap {CAP}")
        return
    out = Path(sys.argv[2])
    out.write_text(
        json.dumps(
            {"requests": probe.sent, "items": items, "decisions": decisions},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    for name, rows in (("items", items), ("decisions", decisions)):
        written = sum(1 for r in rows if r["written"])
        silent = sum(1 for r in rows if not r["answers"])
        print(f"{name}: {len(rows)} rows, written {written}, no answer for {silent}")
    print(f"requests sent: {probe.sent} (cap {CAP})")


if __name__ == "__main__":
    main()
