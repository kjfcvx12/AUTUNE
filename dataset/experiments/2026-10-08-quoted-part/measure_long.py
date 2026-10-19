"""On long turns, does the returned part (S2) narrow further than the sentence (S1)?

measure_part.py found the parts verbatim, but its four meetings have no turn
over 300 characters. This is the check the user ordered next (via 리더,
2026-10-08, "진행"): one invented meeting of twelve turns of 300-600 characters,
each holding one planted promise or decision, short questions between them.
Written here, by the session; no real person, company or meeting.

For each planted turn, per run: was the planted sentence labelled; how long is
what S1 would show (that sentence) against the turn; under the prompt that
returns parts, is the part in the line character for character, does it hold
the planted words (``core``), and how long is it against the turn.

Prints numbers only.

Usage: measure_long.py count
       measure_long.py run <rounds> <log>
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
CAP = int(os.environ.get("CAP", "18"))  # requests still allowed of the 18 named to the user; a retry counts
SENT = {"n": 0}
MAIN = llm.INSTRUCTIONS


def swap(text: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in pairs:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    return text


# The same instructions measure_part.py measured.
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

C, D = "commitment", "decision"

# (the question asked before it, the turn, the kind planted, the planted words)
MEETING: list[tuple[str, str, str, str]] = [
    (
        "결제 쪽 상황부터 들어 볼까요?",
        "지난주에 결제 화면 이탈률이 갑자기 올라간 건 다들 보셨을 텐데요. 로그를 보면 카드 등록 단계에서 "
        "멈추는 분들이 평소의 두 배 가까이 됩니다. 원인은 아직 확실하지 않은데 화요일 배포 때 들어간 입력 "
        "검증이 너무 엄격해진 게 아닌가 싶어요. 특히 유효기간 칸에서 슬래시를 직접 치면 오류가 나는 경우가 "
        "있었습니다. 고객센터 문의도 그 무렵부터 하루 열 건 정도씩 늘었고요. "
        "휴대폰 기종별로 보면 특정 브라우저에 몰려 있지는 않았습니다. 재시도해서 결국 등록에 성공하는 비율은 절반 정도였고요. "
        "그래서 원인을 추측만 하고 있을 "
        "수는 없으니까 카드 등록 단계 오류 로그는 제가 이번 주 목요일까지 유형별로 정리해서 공유하겠습니다. "
        "그 전까지는 검증 규칙을 되돌릴지 말지 판단할 근거가 부족한 상태입니다.",
        C,
        "카드 등록 단계 오류 로그는 제가 이번 주 목요일까지 유형별로 정리해서 공유하겠습니다",
    ),
    (
        "알림은 몇 번 보내는 걸로 할까요?",
        "알림 기능은 지금 두 가지 안이 있습니다. 하나는 예약 하루 전에 한 번만 보내는 거고, 다른 하나는 "
        "하루 전과 한 시간 전에 두 번 보내는 겁니다. 두 번 보내는 쪽이 노쇼는 확실히 줄어드는데, 지난 분기 "
        "설문에서는 알림이 많다는 불만이 삼십 퍼센트 가까이 나왔어요. 푸시 발송 비용은 건수가 적어서 크게 "
        "차이 나지 않습니다. 매장 쪽 의견은 반반이었고요. 여러 의견을 들어 봤는데 불만을 더 키우는 건 피해야 "
        "하니까 이번 버전에서는 알림을 예약 하루 전에 한 번만 보내는 걸로 정하겠습니다. 한 시간 전 알림을 "
        "원하는 매장이 어느 정도인지는 아직 숫자가 없습니다.",
        D,
        "이번 버전에서는 알림을 예약 하루 전에 한 번만 보내는 걸로 정하겠습니다",
    ),
    (
        "디자인 시안은 어디까지 왔나요?",
        "디자인 시안은 지난주 금요일에 2차까지 나왔습니다. 1차 때 지적받았던 글자 크기 문제는 본문을 한 단계 "
        "키워서 해결했고, 버튼 색은 접근성 기준에 맞춰 대비를 높였습니다. 다만 태블릿 가로 화면에서는 예약 "
        "목록이 두 줄로 밀리는 현상이 아직 남아 있어요. 이건 그리드 간격을 다시 잡아야 해서 하루 이틀로는 안 "
        "됩니다. 아이콘 세트는 외주에서 받은 것 중 절반 정도만 쓸 수 있는 상태고요. "
        "나머지 절반은 선 굵기가 달라서 화면에 같이 놓으면 어색합니다. 색상 표는 지난번과 달라진 게 없고 글꼴도 그대로입니다. "
        "태블릿 시안은 제가 다음 "
        "주 수요일까지 고쳐서 올리겠습니다. 휴대폰 화면 쪽은 더 손댈 곳이 없어 보입니다.",
        C,
        "태블릿 시안은 제가 다음 주 수요일까지 고쳐서 올리겠습니다",
    ),
    (
        "그러면 출시 날짜는 어떻게 되는 건가요?",
        "출시 일정 얘기를 해야 할 것 같습니다. 원래 계획은 이달 말이었는데 지금 남은 작업을 세어 보면 결제 "
        "검증 수정, 태블릿 화면, 알림 설정까지 세 덩어리가 남아 있어요. 테스트 기간을 일주일은 잡아야 하는데 "
        "그러면 이달 말은 사실상 어렵습니다. 무리해서 맞추면 지난번처럼 출시 직후에 긴급 수정을 두 번 하게 될 "
        "가능성이 높고요. "
        "개발 인원은 이번 달에 한 명이 휴가라서 실제로 쓸 수 있는 날이 더 적습니다. 지난 출시 때 긴급 수정 두 건은 모두 테스트 기간을 줄인 데서 나온 것이었습니다. "
        "마케팅 쪽 캠페인은 날짜가 아직 확정되지 않아서 옮길 여지가 있다고 들었습니다. "
        "그러니까 품질 문제를 다시 겪느니 일정을 조정하는 게 낫다고 보고 출시는 다음 달 둘째 주로 미루기로 "
        "하겠습니다. 캠페인 담당자에게는 회의록으로 전달될 겁니다.",
        D,
        "출시는 다음 달 둘째 주로 미루기로 하겠습니다",
    ),
    (
        "서버 비용이 늘었다고 들었는데요?",
        "서버 비용 얘기인데요, 지난달 청구서가 그 전달보다 이십 퍼센트 정도 더 나왔습니다. "
        "항목별로 보면 계산 서버는 오히려 조금 줄었고 데이터베이스는 그대로입니다. "
        "트래픽은 거의 "
        "그대로였으니까 사용량 때문은 아니고, 이미지 저장소 쪽 전송량이 크게 늘어난 게 눈에 띕니다. 썸네일을 "
        "매번 원본에서 새로 만들고 있어서 그런 것 같아요. 캐시를 붙이면 꽤 줄어들 텐데 정확히 얼마나 줄지는 "
        "재 봐야 압니다. 일단 숫자가 있어야 예산 얘기를 할 수 있으니 제가 금요일까지 항목별 비용 비교표를 "
        "만들어 오겠고, 캐시 적용 여부는 그 표를 본 다음에 얘기하면 될 것 같습니다. 다른 항목들은 전달과 "
        "비슷한 수준이었습니다.",
        C,
        "제가 금요일까지 항목별 비용 비교표를 만들어 오겠고",
    ),
    (
        "문의 채널은 정리가 됐나요?",
        "문의 응대 채널이 지금 메일, 채팅, 전화 세 군데로 나뉘어 있는데요. 지난달 통계를 보면 채팅이 전체의 "
        "육십 퍼센트이고 전화는 십 퍼센트가 안 됩니다. 그런데 전화 한 통에 들어가는 시간은 채팅의 네 배쯤 "
        "돼요. 전화로 들어오는 문의 내용도 대부분 예약 변경이라 앱에서 직접 할 수 있는 것들이고요. 상담 인원은 "
        "당분간 늘릴 계획이 없습니다. "
        "야간에는 전화가 거의 오지 않는데도 대기 인력은 그대로 두고 있었습니다. 메일은 답변까지 평균 하루가 걸리지만 불만은 거의 없었어요. "
        "전화 상담은 이번 달 말로 종료하기로 합시다. 종료 안내 문구는 앱 공지와 "
        "자동 응답 양쪽에 같은 내용으로 들어가 있어야 혼란이 없을 것 같습니다.",
        D,
        "전화 상담은 이번 달 말로 종료하기로 합시다",
    ),
    (
        "검색 개선은 범위가 어느 정도인가요?",
        "검색 기능 개선은 생각보다 범위가 큽니다. 지금은 매장 이름이 정확히 일치해야만 결과가 나오는데, "
        "사용자들은 보통 동네 이름이나 업종으로 찾거든요. 지난주 검색어 상위 백 개를 뽑아 보니 절반 이상이 "
        "결과 없음으로 끝났습니다. "
        "오타가 섞인 검색어도 스무 개 가까이 됐는데 지금은 전부 결과가 없습니다. "
        "형태소 분석을 붙이면 나아지겠지만 색인을 다시 만들어야 해서 서버 작업이 "
        "같이 필요합니다. 색인 재구축 계획서는 제가 다음 주 월요일까지 초안을 써 오겠는데, 서버 작업 일정이 "
        "정해지지 않으면 날짜를 못 박는다는 점은 미리 말씀드립니다. 업종 분류표는 운영 쪽에 이미 있는 걸 "
        "그대로 쓸 수 있을 것 같습니다.",
        C,
        "색인 재구축 계획서는 제가 다음 주 월요일까지 초안을 써 오겠는데",
    ),
    (
        "회원 등급 개편안은 검토해 보셨어요?",
        "회원 등급 제도 개편안을 검토했습니다. 현재는 누적 예약 횟수만으로 등급을 매기는데, 취소가 잦은 "
        "분들도 높은 등급을 받는 문제가 있어요. 개편안은 취소율을 반영하는 안과 최근 석 달 실적만 보는 안 두 "
        "가지입니다. 취소율을 반영하면 공정하긴 한데 계산이 복잡해서 고객에게 설명하기가 어렵습니다. 석 달 "
        "실적만 보는 쪽은 단순하지만 오래된 단골이 불리해지고요. "
        "지난 개편 때는 등급 계산식을 안내 문서로 만들었는데 조회 수가 아주 낮았습니다. 등급별 혜택 자체는 이번 개편 범위에 들어 있지 않습니다. "
        "설명하기 쉬운 쪽이 문의도 덜 들어온다는 게 "
        "지난 개편 때 경험이라 등급은 최근 석 달 실적 기준으로 바꾸는 안으로 확정하겠습니다. 기존 등급에서 "
        "내려가는 분들이 얼마나 되는지는 아직 계산해 보지 않았습니다.",
        D,
        "등급은 최근 석 달 실적 기준으로 바꾸는 안으로 확정하겠습니다",
    ),
    (
        "보안 점검 결과는 나왔나요?",
        "보안 점검 결과가 어제 나왔습니다. 심각한 항목은 없었고 중간 등급이 세 건입니다. 하나는 관리자 화면 "
        "세션이 너무 오래 유지되는 것, 하나는 비밀번호 재설정 링크가 한 번 쓴 뒤에도 살아 있는 것, 마지막은 "
        "오류 화면에 서버 버전이 노출되는 겁니다. 세 건 다 수정 자체는 어렵지 않은데 재설정 링크는 메일 발송 "
        "쪽 코드와 얽혀 있어서 확인이 필요합니다. 점검 업체의 재검사는 다음 달 초로 잡혀 있어요. "
        "지난 점검 때 나왔던 다섯 건은 이번에는 모두 통과했습니다. "
        "세션 만료와 "
        "버전 노출 두 건은 제가 내일까지 고치겠습니다. 재설정 링크 건은 영향 범위가 어디까지인지 아직 모르는 "
        "상태입니다.",
        C,
        "세션 만료와 버전 노출 두 건은 제가 내일까지 고치겠습니다",
    ),
    (
        "번역은 두 언어 다 가는 건가요?",
        "번역 작업 범위를 정리했습니다. 영어와 일본어 두 개 언어를 동시에 여는 게 원래 목표였는데, 일본어는 "
        "매장 정보 자체가 번역돼 있지 않아서 화면만 바꿔서는 의미가 없어요. 매장 정보까지 번역하려면 운영 "
        "인력이 따로 붙어야 합니다. 영어는 화면 문구가 사백 개 정도이고 외주 견적은 이미 받아 뒀습니다. "
        "일본어 사용자 비중은 전체의 이 퍼센트 정도로 영어보다 조금 낮습니다. 번역 품질 검수는 외주 견적에 포함돼 있었습니다. "
        "그래서 "
        "두 언어를 한꺼번에 하다가 둘 다 늦어지는 것보다는 이번에는 영어만 먼저 열기로 하고, 일본어는 매장 "
        "정보 번역 방법이 나온 뒤에 일정을 잡는 게 맞겠습니다. 외주 견적서는 공유 폴더에 올라가 있습니다.",
        D,
        "이번에는 영어만 먼저 열기로 하고",
    ),
    (
        "매장 등록이 오래 걸린다는 얘기가 있던데요?",
        "신규 매장 등록 절차에 대한 불만이 계속 들어옵니다. 서류를 올리고 승인까지 평균 닷새가 걸리는데, "
        "그중 사흘은 저희 쪽 검토 대기 시간이에요. 검토 항목이 열두 개인데 실제로 반려 사유가 되는 건 사업자 "
        "등록증과 통장 사본 두 가지가 대부분입니다. 나머지 열 개는 형식 확인이라 자동으로 돌릴 수 있을 것 "
        "같습니다. 담당자가 한 명뿐이라 휴가 때는 대기가 더 길어지고요. "
        "지난달 신청은 마흔 건 남짓이었고 그 가운데 반려는 여섯 건이었습니다. 반려된 곳 중 절반은 다시 신청하지 않았어요. "
        "절차를 줄이려면 어디서 시간이 새는지부터 "
        "봐야 하니까 최근 석 달 반려 사유는 제가 다음 주 화요일까지 뽑아서 정리해 두겠습니다. 자동화 얘기는 "
        "그 숫자를 보고 하는 게 순서일 것 같습니다.",
        C,
        "최근 석 달 반려 사유는 제가 다음 주 화요일까지 뽑아서 정리해 두겠습니다",
    ),
    (
        "회의록은 누가 정리하죠?",
        "마지막으로 회의록 얘기만 짧게 하겠습니다. 지난 세 번의 회의록이 각각 다른 양식으로 올라와서 찾기가 "
        "어려웠습니다. "
        "검색이 안 되는 이유는 제목 형식이 제각각이기 때문이었습니다. "
        "결정 사항이 본문 중간에 섞여 있어서 나중에 확인하려면 처음부터 다시 읽어야 했고요. 양식 "
        "자체는 예전에 쓰던 게 공유 폴더에 남아 있습니다. 담당과 기한이 빠진 항목도 몇 개 있었습니다. 지난달 "
        "회의록 가운데 두 건은 아직 초안 상태로 남아 있기도 합니다. 오늘 회의록은 제가 내일 오전까지 정리해서 "
        "올리겠습니다. 양식을 하나로 맞추는 문제는 다음 회의 안건 목록에 이미 올라가 있습니다.",
        C,
        "오늘 회의록은 제가 내일 오전까지 정리해서 올리겠습니다",
    ),
]

TEXTS: list[str] = []
PLANTED: dict[int, tuple[str, str]] = {}  # index into TEXTS -> (kind, core)
for question, said, planted_kind, core in MEETING:
    TEXTS.append(question)
    assert 300 < len(said) <= 600, (len(said), said[:20])
    assert said.count(core) == 1, core
    PLANTED[len(TEXTS)] = (planted_kind, core)
    TEXTS.append(said)


def squeeze(text: str) -> str:
    return "".join(text.split())


def use(variant: str) -> None:
    llm.INSTRUCTIONS = VARIANTS[variant]
    llm._BODY_OVERHEAD = len(VARIANTS[variant]) + 200


def cut_lines() -> tuple[list[int], list[str]]:
    return llm._in_pieces(TEXTS, None)


def planned(variant: str) -> int:
    use(variant)
    _, lines = cut_lines()
    return len(llm.windows(lines, llm.MAX_OUTBOUND_CHARS - llm._BODY_OVERHEAD))


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


def classify(variant: str) -> tuple[int, list[dict], int]:
    use(variant)
    classifier = get_classifier()
    client = classifier._client  # type: ignore[attr-defined]
    send = client.request
    count = {"n": 0}

    def request(method: str, path: str, **kwargs: object) -> object:
        if SENT["n"] >= CAP:
            raise RuntimeError("request cap reached")
        SENT["n"] += 1
        count["n"] += 1
        time.sleep(PACE)
        return send(method, path, **kwargs)

    client.request = request

    seen: list[dict[int, int]] = []
    answers: list[str] = []
    render, answer_text = llm.render, llm._answer_text

    def rendered(lines: list[str], context: int, start: int, end: int):  # type: ignore[no-untyped-def]
        text, targets = render(lines, context, start, end)
        seen.append(targets)
        return text, targets

    def answered(body: object) -> str:
        answer = answer_text(body)
        answers.append(answer)
        return answer

    llm.render, llm._answer_text = rendered, answered
    try:
        classifier.classify(TEXTS)
    finally:
        llm.render, llm._answer_text = render, answer_text
        # The classifier is one object for the process: left wrapped, the next
        # run wraps the wrapper and every request is counted (and paced) twice.
        # That is how the first run of this script stopped at 9 sent, not 18.
        client.request = send

    owners, lines = cut_lines()
    label: dict[int, str] = {}  # index into lines -> kind
    part: dict[int, str] = {}
    summary: dict[int, str] = {}
    for targets, answer in zip(seen, answers, strict=False):
        quoted, written = parts_of(answer), llm.parse_summaries(answer)
        for n, kind in llm.parse(answer).items():
            if n in targets:
                label[targets[n]] = kind.value
                if n in quoted:
                    part[targets[n]] = quoted[n].strip()
                if n in written:
                    summary[targets[n]] = written[n]

    turns: list[dict] = []
    for at, (kind, core) in PLANTED.items():
        own = [i for i, owner in enumerate(owners) if owner == at]
        holds = [i for i in own if squeeze(core) in squeeze(lines[i])]
        assert len(holds) == 1, (at, len(holds))
        line = holds[0]
        whole = len(squeeze(TEXTS[at]))
        got = label.get(line)
        row: dict = {
            "turn": at,
            "chars": len(TEXTS[at]),
            "sentences": len(own),
            "planted": kind,
            "label": got or "none",
            "found": got in (C, D),
            "kind_right": got == kind,
            # Rows the turn would make from sentences nothing was planted in.
            "others": sum(label.get(i) in (C, D) for i in own if i != line),
            "core_of_turn": round(len(squeeze(core)) / whole, 3),
            "s1_of_turn": round(len(squeeze(lines[line])) / whole, 3),
            "summary_chars": len(summary.get(line, "")),
        }
        said = part.get(line, "")
        if said:
            inside = squeeze(said) in squeeze(lines[line])
            row.update(
                part=True,
                verbatim=said in lines[line],
                verbatim_spacing_aside=inside,
                # The part holds the planted words whole / is cut inside them /
                # is somewhere else in the sentence.
                holds_core=squeeze(core) in squeeze(said),
                inside_core=squeeze(said) in squeeze(core) and squeeze(said) != squeeze(core),
                s2_of_turn=round(len(squeeze(said)) / whole, 3),
                s2_of_sentence=round(len(squeeze(said)) / len(squeeze(lines[line])), 3),
            )
        else:
            row["part"] = False
        turns.append(row)
    labelled_questions = sum(
        label.get(i) in (C, D) for i, owner in enumerate(owners) if owner not in PLANTED
    )
    return count["n"], turns, labelled_questions


def count() -> None:
    owners, lines = cut_lines()
    sizes = [len(TEXTS[at]) for at in PLANTED]
    print("turns", len(PLANTED), "chars min/mean/max", min(sizes), sum(sizes) // len(sizes), max(sizes))
    print("lines asked about", len(lines), "of which long-turn sentences", sum(o in PLANTED for o in owners))
    cores = [len(squeeze(core)) / len(squeeze(TEXTS[at])) for at, (_, core) in PLANTED.items()]
    print("planted words / turn, mean", round(sum(cores) / len(cores), 3))
    total = 0
    for name in VARIANTS:
        n = planned(name)
        total += n
        print(name, len(VARIANTS[name]), "chars", n, "requests a run")
    print("a round:", total, "requests")


def run(rounds: int, log: Path) -> None:
    sent = 0
    done = set()
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if "turns" in row:
                done.add((row["round"], row["variant"]))
    with log.open("a", encoding="utf-8") as out:
        for rnd in range(rounds):
            for name in VARIANTS:
                if (rnd, name) in done:
                    continue
                try:
                    requests, turns, questions = classify(name)
                except Exception as exc:  # noqa: BLE001 -- one failed run is a hole, not the end
                    out.write(
                        json.dumps({"round": rnd, "variant": name, "error": type(exc).__name__})
                        + "\n"
                    )
                    out.flush()
                    continue
                sent += requests
                out.write(
                    json.dumps(
                        {
                            "round": rnd,
                            "variant": name,
                            "requests": requests,
                            "questions_labelled": questions,
                            "turns": turns,
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
