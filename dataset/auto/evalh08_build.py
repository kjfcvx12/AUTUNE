"""Build EVALH_08 — an invented seafood plant HACCP re-certification meeting.

The dialogue is held here as one list so that row numbers, start times,
`responds_to` and the answer key's row references are generated instead of typed:
a hand-numbered reference moves the moment a row is inserted. Rows carry optional
labels; `responds_to` and the answer key refer to labels, never to numbers.

Writes `EVALH_08.A.csv`, `EVALH_08.C.csv`, `EVALH_08.D.csv` and
`EVALH_08.speakers.json` into `dataset/extraction_eval_dummy_hard/`.

Everything in the meeting is invented: company, plant, product, people, numbers.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "extraction_eval_dummy_hard"
MEETING = "EVALH_08"

ROLE = {
    "SPK01": "QA",
    "SPK02": "Ops",
    "SPK03": "Data",
    "SPK04": "Sales",
    "SPK05": "QA",
}

SPEAKERS = {
    "meeting": MEETING,
    "title": "바다온식품 가공2공장 해썹 재심사 준비 및 파우치 라인 시운전 회의",
    "type": "cross-team",
    "position_order": ["사원", "주임", "대리", "과장", "차장", "부장", "이사", "대표"],
    "speakers": [
        {"speaker": "SPK01", "name": "차유리", "team": "품질관리팀", "job": "QA",
         "position": "과장", "title": "팀장"},
        {"speaker": "SPK02", "name": "남기훈", "team": "생산2팀", "job": "Ops",
         "position": "대리", "title": ""},
        {"speaker": "SPK03", "name": "표은겸", "team": "품질관리팀", "job": "Data",
         "position": "주임", "title": ""},
        {"speaker": "SPK04", "name": "배시우", "team": "영업팀", "job": "Sales",
         "position": "대리", "title": ""},
        {"speaker": "SPK05", "name": "윤가람", "team": "품질관리팀", "job": "QA",
         "position": "사원", "title": ""},
    ],
}

rows: list[dict] = []
labels: dict[str, int] = {}


def say(speaker: str, text: str, kind: str = "none", decision: str = "",
        settles: str = "", rt: int | str | None = None, note: str = "",
        label: str | None = None) -> None:
    """One ASR segment. `rt` is a label name, or an offset back (-1 = previous row)."""
    rows.append({
        "speaker": speaker,
        "text": text,
        "kind": kind,
        "decision_id": decision,
        "settles": settles,
        "rt": rt,
        "note": note,
    })
    if label:
        labels[label] = len(rows)


# --- opening -------------------------------------------------------------------
say("SPK05", "저기 이 방 에어컨이 아까부터 계속 돌아가는데 리모컨이 어디 갔는지를 모르겠어요.")
say("SPK05", "지난주에도 이랬는데 그때는 설비 쪽에서 올라와서 그냥 차단기를 내리고 갔거든요.")
say("SPK05", "일단 문이라도 좀 열어 놓을까요? 이러다 또 한 시간 내내 이 소리 듣게 되는데.")
say("SPK02", "아 그 리모컨은 저쪽 창틀 위에 그냥 올려져 있던데요. 아까 들어오면서 봤어요.")
say("SPK02", "어제 설비 쪽에서 점검 왔다 가면서 거기다 두고 그대로 간 것 같더라고요.")
say("SPK01", "뭐 그건 이따 보고요. 자 시간 다 됐으니까 그냥 바로 시작할게요.")
say("SPK01", "오늘 볼 건 크게 네 가지인데 이제 재심사 실사 준비가 제일 급하고요,")
say("SPK01", "그다음에 파우치 라인 시운전 일정이랑 검사 기록 복원 건, 그리고 라벨 표기 건이에요.")
say("SPK01", "살균 조건 재검증은 시간 봐서 하고 안 되면 그냥 뒤로 넘기려고 생각하고 있어요.")
say("SPK01", "아 그리고 오늘은 회의록 대신에 정해진 것만 제가 따로 추려서 올려 둘게요.",
    kind="commitment", note="본인이 결정 사항 정리를 맡겠다고 함")
say("SPK01", "지난번에는 통으로 다 받아 적었더니 정작 뭘 정했는지가 안 남더라고요.")
say("SPK01", "그러니까 중간에 막히는 거 있으면 그냥 끊고 들어오셔도 되니까 편하게 하세요.")
say("SPK04", "네 저도 그게 편할 것 같아요.")
say("SPK03", "그럼 제가 어제 인증원에서 받은 공문 내용부터 깔고 가는 게 나을까요?",
    kind="open_question", note="브리핑 순서를 먼저 물음")
say("SPK01", "네 그게 깔려 있어야 나머지 얘기가 되니까 은겸 씨가 그냥 쭉 해 주세요.")
say("SPK03", "네 그러니까 이번에 온 공문 기준으로 실사 날짜가 시월 이십육 일로 잡혀 있고요,")
say("SPK03", "아 아니다 이십육 일이 아니라 이십칠 일이네요. 공문 날짜랑 접수 날짜를 헷갈렸어요.")
say("SPK03", "어쨌든 그 주 월요일 아침에 심사원 두 분이 들어온다고 보시면 될 것 같아요.")
say("SPK03", "그리고 이번에는 서류만 보는 게 아니라 라인을 직접 돌려 보겠다고 적혀 있더라고요.")
say("SPK03", "저희가 삼 년 전에 받을 때는 뭐 문서만 훑고 한 시간 만에 끝났었거든요.")
say("SPK03", "그때랑 같은 준비로 들어가면 이제 좀 곤란해질 수 있다고 보는 게 맞아요.")
say("SPK02", "음 그건 좀 빠듯한데요.")
say("SPK03", "아 그리고 제일 중요한 게, 서류는 실사 닷새 전까지 인증원에 미리 넘겨야 해요.",
    label="doc_due")
say("SPK03", "그러니까 실제로 손볼 수 있는 기간은 이제 다음 주까지밖에 안 남은 셈이에요.")
say("SPK03", "그리고 문서 쪽을 보면 지금 열두 종 중에 아홉 종이 개정이 안 돼 있어요.")
say("SPK03", "그중에 네 종은 작년에 라인 바뀌면서 같이 고쳤어야 하는 건데 그대로 남아 있고요,")
say("SPK03", "제 생각에는 이대로 들어가면 첫날 오전에 그것부터 바로 걸릴 것 같아요.",
    kind="concern", note="unprompted, 문서 미개정 상태를 먼저 지적함")
say("SPK05", "아 예...")
say("SPK04", "그 아홉 종이라는 게 혹시 저희 영업 쪽 규격서도 다 들어가는 거예요?",
    kind="open_question", note="개정 대상에 영업 문서가 포함되는지 물음", label="q_spec")
say("SPK03", "규격서 자체는 이번 범위가 아닌데 원료 바뀐 건은 따로 반영을 해 주셔야 해요.",
    kind="commitment", rt="q_spec", note="요청에 답하며 반영 범위를 정리해 주기로 함")
say("SPK03", "그건 이따 라벨 얘기할 때 같이 보면 될 것 같고요.")
say("SPK01", "네 그럼 그 순서대로 가고요. 저도 어제 인증원 담당자랑 통화를 한번 했는데,")
say("SPK01", "이번에는 현장 위주로 본다는 얘기를 저한테도 똑같이 하더라고요.")
say("SPK01", "그러니까 작업자분들 손 씻는 것부터 기록 쓰는 것까지 다 본다고 보시면 돼요.")
say("SPK01", "서류는 이제 그 뒤에 맞춰서 확인하는 정도로 간다는 얘기였어요.")
say("SPK05", "아 네.")
say("SPK02", "그럼 저는 실사 전날에 현장을 한 바퀴 미리 돌아보려고요.",
    kind="commitment", note="본인 계획으로 전날 현장 점검을 잡음")
say("SPK02", "작년에도 그렇게 돌다가 배수구 쪽에서 하나 걸렸던 적이 있거든요.")
say("SPK04", "그럼 그날 저희 쪽 사람은 안 들어가는 게 낫겠네요.")
say("SPK01", "네 그날은 외부에서 오시는 분들 일정도 다 빼 주세요.")
say("SPK04", "그건 제가 이번 주 안에 한 번 정리해서 돌리겠습니다.",
    kind="commitment", rt=-1, note="요청 수락, 외부 방문 일정 정리를 맡음")

# --- D1: whether the new pouch line goes into the audit scope --------------------
say("SPK01", "자 그럼 제일 얽혀 있는 그 라인 얘기부터 먼저 정리하고 갈게요.", decision="D1")
say("SPK01", "파우치 라인 시운전이 지금 실사랑 완전히 같은 주에 걸려 있잖아요.", decision="D1")
say("SPK01", "저는 이걸 어떻게 할지부터 정해야 나머지가 다 굴러간다고 보고 있어요.", decision="D1")
say("SPK01", "기훈 씨 쪽에서는 그 시운전을 원래 언제로 잡고 계셨던 거예요?", decision="D1",
    kind="open_question", note="생산 쪽 시운전 일정을 물음", label="d1_ask")
say("SPK02", "저희는 이제 이십일 일 주부터 한 사흘 정도 돌려 보려고 잡아 놨어요.", decision="D1",
    kind="commitment", rt="d1_ask", note="요청에 답하며 본인 팀 계획을 밝힘")
say("SPK02", "설비 입고가 이번 주 목요일이라서 그 뒤로는 더 당길 수가 없는 상황이고요,", decision="D1")
say("SPK02", "포장기 두 대를 동시에 세팅해야 해서 사람도 그 주에 다 몰려 있어요.", decision="D1")
say("SPK02", "그리고 그 주에 협력업체 기사님도 두 분 들어오시기로 돼 있거든요.", decision="D1")
say("SPK02", "그분들 일정은 한 달 전에 잡아 놓은 거라 이제 와서 바꾸기가 어려워요.", decision="D1")
say("SPK02", "근데 실사랑 겹치면 라인을 아예 세워야 되는 거 아닌가 싶긴 한데요.", decision="D1",
    kind="concern", rt="d1_ask", note="시운전과 실사가 겹치는 것을 문제로 제기함")
say("SPK03", "아 근데 그 라인은 지금 변경 신고 자체가 아직 안 올라가 있는 상태예요.", decision="D1",
    label="d1_block")
say("SPK03", "도면 승인이 나야 신고서에 배치도를 붙일 수가 있는데 그게 아직 안 났거든요.", decision="D1")
say("SPK03", "그래서 실사 때 그게 그대로 보이면 오히려 질문이 한참 길어져요.", decision="D1",
    kind="concern", rt="d1_block", note="미신고 설비가 노출되면 심사가 길어진다고 반대함")
say("SPK03", "저희가 뭘 숨긴 건 아닌데 설명이 길어지면 그때부터 다른 걸 또 보자고 해요.", decision="D1")
say("SPK03", "그리고 그 도면이 지금 설계 쪽에서 한 번 반려가 된 상태이기도 하고요.", decision="D1")
say("SPK03", "아 반려가 아니라 보완 요청이 온 거네요. 제가 말을 좀 잘못했어요.", decision="D1")
say("SPK03", "어쨌든 그거 고쳐서 다시 올리는 데만 일 주일은 더 잡아야 해요.", decision="D1")
say("SPK04", "잠깐만요, 그럼 거래처에 시월 말부터 공급된다고 말해 놓은 건 어떻게 되는 거예요?",
    decision="D1", kind="open_question", note="영업 약속과의 충돌을 끊고 들어와 물음",
    label="d1_sales")
say("SPK04", "제가 저번 주에 이미 그 일정 기준으로 견적을 한 번 돌려 놨거든요.", decision="D1")
say("SPK04", "그쪽은 이제 초도 물량을 십일월 첫 주에 받는 걸로 알고 기다리고 있어요.", decision="D1")
say("SPK02", "아 저는 그 얘기를 못 들었네요.", decision="D1")
say("SPK01", "그러니까 지금 서로 다른 두 개가 한 주에 붙어 있는 거네요. 시운전이랑 실사요.",
    decision="D1")
say("SPK01", "뭐 제일 편한 건 시운전을 실사 끝나고 다음 주로 그냥 미루는 건데요,", decision="D1")
say("SPK01", "그러면 이제 방금 말씀하신 영업 쪽 약속이 이 주가 통째로 밀리는 거고.", decision="D1")
say("SPK01", "반대로 같이 가면 라인은 돌아가는데 신고가 안 된 설비가 그대로 보이는 거고요.",
    decision="D1")
say("SPK04", "그럼 신고를 이번에 같이 올려 버리면 되는 거 아니에요? 어차피 한 번은 할 거잖아요.",
    decision="D1", kind="open_question", note="신고와 실사를 함께 처리하자고 물음")
say("SPK04", "저는 그게 일을 두 번 안 하는 제일 깔끔한 방법 같아 보이는데요.", decision="D1")
say("SPK01", "아 그러네요. 그럼 그렇게 하죠. 신고랑 실사를 한 번에 같이 가는 걸로.", decision="D1",
    note="번복, 도면 승인 문제로 바로 뒤집힘")
say("SPK01", "은겸 씨 그러면 그 신고서 초안은 언제까지 나올 수 있는 거예요?", decision="D1",
    kind="open_question", note="신고서 초안 일정을 물음")
say("SPK03", "아 맞다, 그거 안 돼요. 제가 아까 말씀드린 게 정확히 그거였거든요.", decision="D1")
say("SPK03", "도면 승인이 안 나면 신고서에 설비 배치도를 아예 못 붙이게 돼 있어요.", decision="D1")
say("SPK03", "그러니까 승인이 먼저 나야 신고가 되고, 신고가 돼야 실사 범위에 넣을 수 있어요.",
    decision="D1")
say("SPK03", "근데 지금 그 승인이 빨라야 다음 달 초라고 들었어요.", decision="D1")
say("SPK04", "아 예...", decision="D1")
say("SPK02", "차라리 실사를 좀 미뤄 달라고 인증원에 얘기해 보죠.", decision="D1",
    note="동료 제안, 아무도 받지 않음")
say("SPK03", "그건 사유서를 내야 하고 받아 줄지도 모르는 거라서 좀 위험해요.", decision="D1")
say("SPK02", "그러면 이제 남는 선택지가 사실상 하나밖에 없는 것 같은데요.", decision="D1")
say("SPK02", "라인은 돌리되 실사 범위에서는 빼고, 신고는 승인 나오면 그때 따로 올리는 거요.",
    decision="D1")
say("SPK02", "그 대신 심사원 들어오는 날에는 그 라인만 딱 세워 놓으면 되는 거고요.", decision="D1")
say("SPK05", "근데 그날 하루 세워 놓으면 시운전이 또 하루 밀리는 거 아니에요?", decision="D1",
    kind="concern", rt=-1, note="라인 정지로 시운전 일정이 밀린다고 반대함")
say("SPK05", "저희 검사 일정도 그 사흘에 맞춰서 이미 잡아 놓은 게 있거든요.", decision="D1")
say("SPK05", "수분이랑 중량은 첫날부터 붙어서 봐야 하는 항목이라 빼기가 좀 그래요.", decision="D1")
say("SPK02", "뭐 하루 정도는 앞쪽에서 당기면 그건 어떻게든 맞출 수 있어요.", decision="D1")
say("SPK02", "포장기 세팅을 이십일 일 오전으로 옮기면 그날 저녁부터는 돌릴 수 있고요.", decision="D1")
say("SPK02", "어차피 첫날은 빈 파우치로만 돌리니까 검사는 그다음 날부터 붙으시면 돼요.", decision="D1")
say("SPK05", "아 그러면 저는 괜찮아요.", decision="D1")
say("SPK05", "대신 그 전날에 검사 장비 교정만 미리 좀 봐 주시면 좋겠어요.", decision="D1",
    kind="open_question", note="장비 교정을 미리 봐 달라고 요청함", label="d1_cal")
say("SPK02", "아 그건 제가 화요일 오전에 같이 봐 드릴게요.", decision="D1",
    kind="commitment", rt="d1_cal", note="요청 수락, 장비 교정을 맡음")
say("SPK02", "어차피 그날 포장기 세팅하면서 계기 쪽은 한 번 다 볼 거라서요.", decision="D1")
say("SPK03", "그럼 실사 서류에는 그 라인이 아예 없는 걸로 나가는 거네요. 그게 맞죠?",
    decision="D1", kind="open_question", note="서류상 범위 제외가 맞는지 확인을 물음")
say("SPK01", "네 그렇게 가는 게 지금은 제일 사고가 안 나는 방향인 것 같아요.", decision="D1")
say("SPK01", "그럼 파우치 라인은 이번 실사 범위에서 빼고 갑니다. 시운전은 그대로 가고요.",
    decision="D1", kind="decision", settles="1",
    note="논의 요약 후 팀장이 범위 제외로 정리함", label="d1_settle")
say("SPK01", "신고는 도면 승인이 나오는 대로 그때 따로 올리는 걸로 하고요.", decision="D1")
say("SPK01", "은겸 씨가 저번에 포장실 바꿀 때처럼 그건 좀 맡아 주세요.", decision="D1",
    kind="open_question", note="담당을 지정하는 요청, 과업은 앞 발언에서만 확인됨",
    label="d1_owner")
say("SPK03", "네 그럼 승인 떨어지면 제가 이 주 안에 올리는 걸로 하겠습니다.", decision="D1",
    kind="commitment", rt="d1_owner", note="요청 수락, 본인이 기한을 명시함", label="d1_due")
say("SPK03", "실사 서류 목록에서도 그 라인 건은 오늘 중으로 빼 놓을게요.", decision="D1",
    kind="commitment", rt="d1_owner", note="서류 목록 수정까지 함께 맡음")
say("SPK04", "그럼 거래처에는 제가 초도 물량 날짜를 다시 잡아서 말해 볼게요.",
    kind="commitment", rt="d1_sales", note="영업 일정 재조정을 본인이 맡음")
say("SPK04", "어차피 그쪽도 창고가 비어야 받는다고 했으니까 조정은 될 것 같긴 해요.")
say("SPK04", "안 되면 뭐 일 주 정도는 저희가 먼저 받아 두는 방법도 있긴 하고요.")

# --- side talk (middle of the meeting) -------------------------------------------
say("SPK05", "아 맞다 혹시 아래층 식당 배식 시간 바뀐 거 아세요?", note="사담")
say("SPK05", "열한 시 반부터라고 붙어 있던데 저번처럼 늦게 가면 또 국만 남아 있어요.", note="사담")
say("SPK04", "아 그래요? 저는 어제도 열두 시에 내려갔다가 그냥 라면 먹고 올라왔어요.", note="사담")
say("SPK04", "그날 하필 생선가스 나오는 날이었는데 그것도 다 떨어졌더라고요.", note="사담")
say("SPK02", "그건 원래 열한 시 반에 딱 맞춰서 가야 남아 있어요.", note="사담")
say("SPK01", "네 뭐 그 얘기는 이따 내려가면서 하고요. 다시 돌아와서,")

# --- D2: restoring missing microbiology records -----------------------------------
say("SPK01", "다음은 검사 기록 복원 건인데 이게 사실 오늘 제일 골치 아픈 건이에요.", decision="D2")
say("SPK03", "그 미생물 검사 기록이 이 년 치가 지금 전산 파일로만 남아 있는 상태예요.", decision="D2")
say("SPK03", "작년에 시스템 바꾸면서 옮긴 것까지는 됐는데 서명이 안 들어간 게 많고요,", decision="D2")
say("SPK03", "실사에서 원본 확인을 하자고 하면 그건 사실상 인정이 안 되는 기록이에요.", decision="D2")
say("SPK03", "어제 한번 세어 봤는데 서명이 빠진 게 대략 백이십 건 정도 되더라고요.", decision="D2")
say("SPK03", "아 그리고 저번 회의 때 그 서명 건은 제가 정리하기로 했었는데요,", decision="D2",
    kind="commitment", note="상기, 지난 회의에서 본인이 맡기로 한 건을 다시 꺼냄")
say("SPK03", "그때는 한 스무 건쯤인 줄 알고 받았던 거라 지금이랑 규모가 완전히 달라요.", decision="D2")
say("SPK01", "백이십 건이면 뭐 그거 다시 받으러 다니는 것도 일이 되겠네요.", decision="D2")
say("SPK03", "아 잠시만요, 그 백이십 건이 전부 서명만 빠진 건 아니거든요.", decision="D2")
say("SPK03", "그중에 한 삼십 건은 아예 기록 자체가 안 남아 있는 것들이에요.", decision="D2")
say("SPK01", "이건 그냥 품질 쪽에서 알아서 좀 정리해 주시면 좋겠어요.", decision="D2",
    kind="open_question", note="담당자 없이 품질팀에 통째로 넘김", label="d2_thrown")
say("SPK01", "저는 그 주에 인증원이랑 일정 조율하느라 계속 붙어 있기가 어려울 것 같아서요.",
    decision="D2")
say("SPK02", "음...", decision="D2")
say("SPK05", "아... 예... 그럼 일단은 제가 한번 들여다볼게요.", decision="D2",
    kind="ambiguous", rt="d2_thrown", note="위임, 구체적인 범위 없이 마지못해 받음",
    label="d2_delegate")
say("SPK05", "근데 그 서명은 그때 계셨던 분들이 직접 해 주셔야 하는 거라서요,", decision="D2")
say("SPK05", "확인해 보니까 그중에 두 분은 작년에 이미 퇴사를 하셨더라고요.", decision="D2")
say("SPK03", "그러면 그 두 분 건은 소급해서 받을 방법이 아예 없는 거예요.", decision="D2",
    kind="concern", rt=-1, note="퇴사자 서명은 소급이 불가능하다고 지적함")
say("SPK03", "차라리 없는 건 없다고 사유서로 쓰는 게 낫지 않을까 싶은데 어떠세요?", decision="D2",
    kind="open_question", note="사유서 대체안을 제안하며 의견을 물음")
say("SPK03", "저번 심사 때도 그렇게 써서 넘어간 적이 한 번 있었던 걸로 기억해요.", decision="D2")
say("SPK05", "음 글쎄요.", decision="D2")
say("SPK05", "사유서를 쓰면 그 뒤로도 계속 그 건으로 물어보지 않을까 싶은데요.", decision="D2",
    kind="concern", rt=-2, note="사유서 대체가 이후 지적으로 이어진다고 반대함")
say("SPK05", "저번에 다른 항목에서 그렇게 해 놓고 두 번 더 설명한 적이 있어서요.", decision="D2")
say("SPK01", "그 방법도 생각은 해 봤는데 전수로 다 쓰면 그건 그것대로 지적이 나와요.", decision="D2")
say("SPK01", "그러니까 이번 실사 대상 품목만 보면 이제 두 개잖아요. 손질 고등어랑 파우치 국물이요.",
    decision="D2", label="d2_scope")
say("SPK01", "그 두 개만 복원하고 나머지는 전부 사유서로 대체합니다.", decision="D2",
    kind="decision", settles="1", note="상급자 제안, 이후 아무도 답하지 않음",
    label="d2_settle")
say("SPK01", "나머지 품목은 어차피 이번 범위에 안 들어가니까 굳이 손댈 필요가 없어요.", decision="D2")
say("SPK03", "그럼 그 두 품목 기록은 제가 먼저 목록부터 쭉 뽑아 놓을게요.", decision="D2",
    kind="commitment", note="기한 없이 목록 작성을 본인이 맡음")
say("SPK03", "저번에 제가 만들어 둔 양식 그대로 쓰시면 따로 만들 필요는 없어요.", decision="D2")
say("SPK03", "거기에 날짜랑 담당자만 채우면 되니까 한 건에 이 분도 안 걸려요.", decision="D2")
say("SPK03", "다만 원본 대조를 누가 했는지는 꼭 같이 적어 주셔야 해요.", decision="D2")
say("SPK05", "네 그건 제가 다 적으면서 갈게요.", decision="D2",
    kind="commitment", rt=-1, note="요청 수락, 대조자 기재까지 맡음")
say("SPK05", "그럼 그 두 개는 제가 금요일까지 서명을 다 받아 볼게요.", decision="D2",
    kind="commitment", rt="d2_settle", note="결정 수락, 본인이 기한을 명시함", label="d2_due")
say("SPK05", "안 계신 분들 건은 그냥 사유서 쪽으로 따로 빼 놓는 걸로 하고요.", decision="D2",
    kind="commitment", rt="d2_settle", note="사유서 처리까지 함께 맡음")
say("SPK05", "아 근데 그 사유서 양식은 지금 어디에 들어 있는 거예요?", decision="D2",
    kind="open_question", note="사유서 양식 위치를 물음", label="d2_form")
say("SPK03", "그건 제가 이따 회의 끝나고 메일로 같이 보내 드릴게요.", decision="D2",
    kind="commitment", rt="d2_form", note="요청 수락, 양식 전달을 맡음")
say("SPK04", "혹시 저희 쪽 출하 기록도 이번에 같이 보자고 하면 어떻게 되는 거예요?",
    kind="open_question", note="출하 기록도 범위에 들어가는지 물음", label="q_ship")
say("SPK01", "그건 이번엔 안 봐요. 작년 정기 심사 때 이미 다 본 부분이라서요.",
    kind="commitment", rt="q_ship", note="요청에 답하며 범위 밖임을 확인해 줌")
say("SPK01", "혹시라도 물어보면 그때 작년 보고서를 그대로 보여 드리면 돼요.")

# --- D3: sterilisation re-validation is deferred -----------------------------------
say("SPK01", "자 그다음에 살균 조건 재검증 건을 좀 보고 가야 할 것 같아요.", decision="D3")
say("SPK01", "이거는 원래 이번 실사 전에 같이 끝내려고 했던 건데.", decision="D3")
say("SPK02", "그 에프 제로 값을 다시 잡으려면 열전대를 파우치 안에 넣고 돌려야 하거든요.", decision="D3")
say("SPK02", "그러니까 라인을 한 번 통째로 비워야 되는데 지금은 그럴 시간이 안 나와요.", decision="D3")
say("SPK02", "외부 기관에 맡기는 방법도 있는데 그건 결과 나오는 데만 삼 주가 걸리고요,", decision="D3")
say("SPK02", "비용도 저번에 알아봤을 때 한 사백 정도는 나올 거라고 들었어요.", decision="D3")
say("SPK02", "그리고 그 기관이 지금 예약이 밀려서 접수도 바로는 안 된다고 하더라고요.", decision="D3")
say("SPK02", "전화했을 때 한 이 주 뒤에나 자리가 난다는 얘기를 들었어요.", decision="D3")
say("SPK02", "그러니까 지금 맡겨도 결과는 십이월에나 받아 보게 되는 거예요.", decision="D3")
say("SPK05", "근데 그걸 안 하고 실사에 들어가도 진짜 괜찮은 거예요?", decision="D3",
    kind="open_question", note="재검증 없이 실사가 가능한지 물음", label="d3_ask")
say("SPK05", "저번에 팀장님이 그 부분을 꼭 확인해야 한다고 하셨던 걸로 기억하는데요.", decision="D3")
say("SPK03", "그건 검증 계획서만 제대로 들어가 있으면 그냥 넘어가는 부분이에요.", decision="D3")
say("SPK03", "다만 그 계획서 안에 언제 할 건지가 날짜로 적혀 있어야 하긴 해요.", decision="D3")
say("SPK04", "근데 그걸 또 뒤로 미루면 거래처 규격서에는 그럼 뭐라고 쓰죠?", decision="D3",
    kind="concern", rt="d3_ask", note="연기 시 규격서에 적을 값이 없다고 반대함")
say("SPK04", "저쪽에서 이제 그 값을 달라고 계속 얘기하고 있는 상황이라서요.", decision="D3")
say("SPK04", "저번 주에도 담당자가 메일로 한 번 물어보고 갔었어요.", decision="D3")
say("SPK03", "아 그게 아니고, 규격서에 들어가는 값은 지금 걸 그대로 쓰시면 돼요.", decision="D3")
say("SPK03", "재검증은 그 값이 맞는지 다시 보는 절차라서 값 자체가 바뀌는 건 아니에요.", decision="D3")
say("SPK01", "그건 일단 지금 값 그대로 쓰시고 재검증 중이라고만 한 줄 달아 주세요.", decision="D3")
say("SPK01", "재검증은 이번에는 접고 정기 회의 때 다시 보는 걸로 합니다.", decision="D3",
    kind="decision", settles="1", note="시간과 비용 문제로 보류하기로 정리함",
    label="d3_settle")
say("SPK01", "정기 회의가 다음 달 첫 주니까 그때 결과 보고 다시 정하죠.", decision="D3",
    label="d3_due")
say("SPK02", "아 그러면 열전대는 제가 미리 좀 알아보고 있을게요.", decision="D3",
    kind="commitment", note="기한 없이 장비 확보를 본인이 맡음", label="d3_interim")
say("SPK02", "빌려주는 데가 근처에 두 군데 정도 있는 걸로 알고 있거든요.", decision="D3")
say("SPK02", "그거를 미리 잡아 놓으면 나중에 이 주 정도는 그냥 줄어들어요.", decision="D3")
say("SPK02", "가격도 빌리는 게 훨씬 싸니까 그쪽으로 알아보는 게 맞을 것 같아요.", decision="D3")
say("SPK01", "네 그럼 그건 그렇게 알아봐 주시고요.", decision="D3")
say("SPK03", "검증 계획서 초안은 제가 이번 주 안에 한번 써 보려고요.", decision="D3",
    kind="commitment", note="본인 계획으로 계획서 초안 작성을 잡음")
say("SPK03", "어차피 그것도 실사 서류에 같이 들어가야 하는 문서라서요.", decision="D3")
say("SPK05", "네.")

# --- side talk, second stretch -----------------------------------------------------
say("SPK05", "아 그리고 아까 주차장에 차 빼 달라고 방송 나왔는데 혹시 흰색 차 누구세요?", note="사담")
say("SPK05", "번호가 뭐였더라, 앞에 두 자리가 삼칠이었던 것 같기도 하고요.", note="사담")
say("SPK02", "어 그거 제 차 아닌가 모르겠네요. 오늘 후문 쪽에 대충 대 놨거든요.", note="사담")
say("SPK02", "아 아니다. 저는 흰색이 아니라 은색이니까 제 차는 아니겠네요.", note="사담")
say("SPK04", "저는 오늘 아예 차를 안 가져왔어요.", note="사담")
say("SPK01", "그럼 이따 끝나고 한번 나가서 보시고요. 자 그럼 다음 건 갈게요.", note="사담")

# --- D4: consolidating raw material suppliers, conditionally ------------------------
say("SPK01", "원료 입고처 건도 짧게 보고 넘어가는 게 좋을 것 같아요.", decision="D4")
say("SPK01", "지금 고등어를 두 군데서 받고 있잖아요. 그중에 한 곳은 협력업체 실사가 밀려 있고요.",
    decision="D4")
say("SPK01", "시우 씨 쪽에서는 그게 언제쯤 나온다고 들으신 게 있으세요?", decision="D4",
    kind="open_question", note="협력업체 실사 결과 시점을 물음", label="d4_ask")
say("SPK04", "저쪽은 이제 이번 달 안에 자기들 실사가 끝난다고는 얘기를 하는데요,", decision="D4",
    kind="ambiguous", note="전달, 협력업체가 말한 일정을 옮겨 전함")
say("SPK04", "작년에도 저희가 그 얘기를 그대로 듣고 두 달을 기다렸던 적이 있거든요.", decision="D4")
say("SPK04", "그래서 저는 솔직히 그쪽에서 말하는 날짜를 믿기가 좀 그래요.", decision="D4")
say("SPK04", "단가는 확실히 거기가 킬로당 한 이백 원 정도 싸긴 한 게 맞아요.", decision="D4")
say("SPK04", "연간으로 따지면 그게 이제 꽤 큰 금액으로 벌어지는 건 맞고요.", decision="D4")
say("SPK04", "그래서 위에서도 계속 한쪽으로 몰자는 얘기가 나오는 거예요.", decision="D4")
say("SPK01", "저는 뭐 이참에 한 곳으로 몰아서 관리하는 게 낫다고 보는 쪽인데요.", decision="D4",
    label="d4_propose")
say("SPK01", "두 곳이면 입고 검사도 두 번이고 서류도 계속 두 배로 나오잖아요.", decision="D4")
say("SPK02", "근데 한 군데로 몰면 입고가 하루만 밀려도 라인이 그냥 서 버려요.", decision="D4",
    kind="concern", rt="d4_propose", note="단일 공급처의 결품 위험을 지적함")
say("SPK02", "저희가 원료 재고를 이틀 치밖에 안 들고 가는 구조라서 더 그래요.", decision="D4")
say("SPK02", "그러니까 그건 싸지긴 해도 그것대로 위험을 지는 거라고 봐야죠.", decision="D4")
say("SPK05", "검사는 뭐 한 곳으로 되면 저희 입장에서는 편해지긴 해요.", decision="D4")
say("SPK05", "근데 그쪽 원료가 저번에 수분 값이 좀 튀었던 게 계속 걸리거든요.", decision="D4",
    kind="concern", rt="d4_propose", note="해당 공급처 원료의 편차를 근거로 반대함")
say("SPK03", "아 그건 그때 확인해 보니까 운송 쪽 문제였던 걸로 정리가 됐었어요.", decision="D4")
say("SPK03", "기록에도 그렇게 남아 있고 그 뒤로는 값이 계속 안정적으로 나오고 있어요.", decision="D4")
say("SPK03", "제가 올해 들어온 것만 따로 뽑아 봤는데 편차가 거의 없었어요.", decision="D4")
say("SPK05", "아 그러면 제가 잘못 기억하고 있었던 거네요.", decision="D4")
say("SPK01", "그럼 저쪽 실사가 통과되면 그때 한 곳으로 몰고, 안 되면 지금처럼 두 곳 유지합니다.",
    decision="D4", kind="decision", settles="1",
    note="조건부 결정, 협력업체 실사 결과에 따라 갈림", label="d4_settle")
say("SPK01", "그 결과는 시우 씨가 받는 대로 바로 공유 좀 해 주세요.", decision="D4",
    kind="open_question", note="결과 공유를 요청함", label="d4_owner")
say("SPK01", "결과가 나오기 전까지는 지금 체제에서 아무것도 바꾸지 마시고요.", decision="D4")
say("SPK04", "네 저쪽 결과 나오면 제가 바로 단톡방에 올려 드릴게요.", decision="D4",
    kind="commitment", rt="d4_owner", note="요청 수락, 결과 공유를 맡음")
say("SPK04", "저도 이제 그거 기다리고 있는 입장이라서 오면 바로 알 수 있어요.", decision="D4")

# --- D5: hygiene training, owner named without the task ------------------------------
say("SPK03", "그리고 아까 잠깐 말씀하신 그 교육 건도 이번에 같이 걸릴 것 같아요.", decision="D5",
    label="d5_task")
say("SPK03", "작년 위생교육 이수 기록이 지금 열네 명분이 비어 있는 상태거든요.", decision="D5")
say("SPK03", "그중에 아홉 명은 올해 들어오신 분들이라 아예 못 받으신 거고요,", decision="D5")
say("SPK03", "실사 들어오면 그 명단부터 보자고 할 게 거의 확실해 보여요.", decision="D5")
say("SPK02", "근데 지금 라인 돌리면서 교육까지 또 빼면 인원이 도저히 안 나와요.", decision="D5",
    kind="concern", rt="d5_task", note="시운전과 겹쳐 인원을 뺄 수 없다고 반대함")
say("SPK02", "한 시간짜리라고 해도 스무 명을 한 번에 빼는 건 솔직히 좀 무리예요.", decision="D5")
say("SPK02", "차라리 조별로 쪼개서 두세 번에 나눠 하는 게 나을 것 같은데요.", decision="D5")
say("SPK05", "조별로 하면 저희가 같은 걸 세 번 들어가야 되는 건데요.", decision="D5")
say("SPK05", "뭐 그건 어떻게든 되긴 할 것 같아요.", decision="D5",
    kind="ambiguous", rt=-2, note="구체적인 것 없이 약하게 수긍함")
say("SPK01", "그러면 뭐 조별로 나눠서 돌리는 수밖에 없겠네요.", decision="D5")
say("SPK01", "그럼 지난번 입사 교육 때처럼 은겸 씨가 맡아서 좀 돌려 주세요.", decision="D5",
    kind="decision", settles="1",
    note="논의 요약 후 담당 지정, 과업은 앞선 발언에서만 확인됨", label="d5_settle")
say("SPK01", "금요일 퇴근 전까지는 명단이랑 같이 정리가 다 돼 있어야 해요.", decision="D5",
    label="d5_due")
say("SPK01", "실사 서류에 그 명단이 같이 들어가야 해서 그 뒤로는 못 미뤄요.", decision="D5")
say("SPK03", "네 그럼 제가 조별로 시간표부터 한번 짜 볼게요.", decision="D5",
    kind="commitment", rt="d5_settle", note="요청 수락, 시간표 작성을 맡음", label="d5_owner")
say("SPK03", "이 주 목요일까지 세 번 다 돌리고 금요일 오전에 명단 정리하려고요.", decision="D5",
    kind="commitment", note="본인 계획으로 진행 순서를 잡음")
say("SPK03", "아 근데 야간조는 제가 시간이 안 되는데 그건 어떻게 하죠?", decision="D5",
    kind="open_question", note="야간조 교육 담당을 물음", label="d5_night")
say("SPK02", "야간조는 그냥 제가 대신 해 드릴게요.", decision="D5",
    kind="commitment", rt="d5_night", note="요청 수락, 야간조 교육을 맡음")
say("SPK02", "어차피 저는 그 시간에 라인에 붙어 있으니까 따로 시간 뺄 것도 없어요.", decision="D5")
say("SPK02", "대신 자료는 좀 미리 주셔야 그날 바로 돌릴 수 있을 것 같아요.", decision="D5",
    kind="open_question", note="교육 자료를 미리 달라고 요청함", label="d5_ask_doc")
say("SPK03", "네 그건 시간표 짜면서 같이 넘겨 드릴게요.", decision="D5",
    kind="commitment", rt="d5_ask_doc", note="요청 수락, 자료를 미리 전달하기로 함")
say("SPK05", "네 네.", decision="D5")
say("SPK05", "교육 자료는 저번에 쓰던 거 그대로 쓰면 되는 거죠?", decision="D5",
    kind="open_question", note="교육 자료를 재사용해도 되는지 물음", label="d5_material")
say("SPK03", "그건 올해 바뀐 부분만 제가 고쳐서 내일 중으로 드릴게요.", decision="D5",
    kind="commitment", rt="d5_material", note="요청 수락, 자료 개정을 맡음")
say("SPK03", "작년 거 그대로 쓰면 개정 전 기준이 들어가 있어서 그게 또 걸려요.", decision="D5")
say("SPK03", "바뀐 데가 두 장 정도라서 고치는 건 금방 될 것 같아요.", decision="D5")
say("SPK05", "그쵸.", decision="D5")

# --- D6: label mis-statement, settled as a summary -----------------------------------
say("SPK04", "마지막으로 라벨 건인데 사실 이게 오늘 중에 제일 급한 건일 수도 있어요.", decision="D6")
say("SPK04", "파우치 뒷면에 원산지가 국내산으로만 돼 있는데 지금 물량 절반이 수입이거든요.",
    decision="D6")
say("SPK04", "그러니까 지금 창고에 남아 있는 라벨이 한 삼만 장 정도 되는 상황이에요.", decision="D6")
say("SPK04", "이걸 다 버리고 새로 찍으면 이제 비용이 꽤 크게 나올 것 같은데요.", decision="D6")
say("SPK03", "근데 그건 표시 기준 위반이라서 그냥 두고 갈 수가 없는 부분이에요.", decision="D6",
    kind="concern", rt=-1, note="법적 표시 기준 위반이라 방치가 불가하다고 지적함")
say("SPK03", "실사가 아니라 그냥 일반 점검에서도 바로 걸리는 항목이라서요.", decision="D6")
say("SPK02", "스티커로 덧붙이는 건 가능해요. 저번에 유통기한 건으로 한번 해 봤고요,", decision="D6")
say("SPK02", "근데 파우치 표면이 좀 미끄러워서 접착이 잘 안 될 수도 있어요.", decision="D6",
    kind="concern", note="unprompted, 파우치 재질에서 스티커가 떨어질 위험을 먼저 지적함")
say("SPK02", "그때는 종이 상자였으니까 그냥 붙어 있었던 거라고 봐야 해요.", decision="D6")
say("SPK05", "그럼 샘플 몇 장만 먼저 붙여 보고 정하면 되지 않을까요?", decision="D6",
    kind="open_question", note="샘플 시험 후 결정하자고 물음", label="d6_sample")
say("SPK04", "인쇄소에서는 이틀이면 스티커가 나온다고 얘기를 하긴 했어요.", decision="D6",
    kind="ambiguous", note="전달, 인쇄소가 말한 납기를 옮겨 전함")
say("SPK04", "근데 그것도 이제 저희가 오늘 발주를 넣었을 때 기준인 거고요.", decision="D6")
say("SPK01", "네 그럼 정리하면, 창고 재고는 스티커로 덮고 새로 찍는 것부터 표기를 고치는 거예요.",
    decision="D6", kind="decision", settles="1",
    note="논의를 요약하며 재고와 신규 인쇄분을 나눠 정리함", label="d6_settle")
say("SPK01", "스티커는 아까 말한 서류 넘기는 날짜보다 이틀 앞으로 잡아 주세요.", decision="D6",
    label="d6_due")
say("SPK01", "그래야 실사 들어오기 전에 창고 정리까지 다 끝낼 수가 있어요.", decision="D6")
say("SPK01", "그건 시우 씨가 인쇄소랑 같이 좀 봐 주시고요.", decision="D6",
    kind="open_question", note="인쇄소 협의 담당을 지정하는 요청", label="d6_owner")
say("SPK04", "네 인쇄소는 제가 오늘 바로 연락해 보려고요.", decision="D6",
    kind="commitment", rt="d6_owner", note="요청 수락, 본인 계획으로 오늘 연락하기로 함")
say("SPK04", "샘플은 내일 오면 제가 가람 씨한테 바로 가져다드릴게요.", decision="D6",
    kind="commitment", rt="d6_sample", note="샘플 전달을 맡음")
say("SPK05", "네 오면 제가 붙여 보고 결과 바로 알려 드릴게요.", decision="D6",
    kind="commitment", rt="d6_sample", note="요청 수락, 부착 시험을 맡음")
say("SPK05", "냉장고에 하루 넣었다 빼는 것까지 해 봐야 제대로 알 수 있을 거예요.", decision="D6")
say("SPK05", "그 결과가 안 좋게 나오면 그때는 다시 찍어야 할 수도 있고요.", decision="D6")
say("SPK04", "아 그건 아닌데요. 그러면 이제 비용이 두 번 나가는 거잖아요.", decision="D6")
say("SPK02", "뭐 그럴 일은 거의 없을 거예요. 저번 상자 때도 잘 붙어 있었고요.", decision="D6")
say("SPK02", "붙이는 건 그럼 야간조 쪽에 부탁해서 이틀에 나눠 하면 될 것 같아요.", decision="D6",
    kind="commitment", note="스티커 부착 인력 배분을 본인이 맡음")

# --- wrap-up ---------------------------------------------------------------------
say("SPK01", "자 그럼 오늘 정한 것만 다시 한번 짚고 마무리할게요.")
say("SPK01", "라인은 이번 실사 범위에서 빼고, 기록은 두 품목만 복원하는 거고요,",
    kind="commitment", note="상기, 앞서 정해진 내용을 다시 확인함")
say("SPK01", "교육은 은겸 씨가 금요일까지, 라벨은 스티커로 덮는 걸로 갑니다.")
say("SPK01", "살균 재검증이랑 입고처 건은 이번에 안 정하고 그냥 넘어간 거예요.")
say("SPK03", "아 그럼 서류는 최종적으로 누가 묶어서 넘기게 되는 거예요?",
    kind="open_question", note="서류 최종 제출 담당을 물음", label="w_final")
say("SPK01", "그건 제가 다 받아서 한 번에 넘기는 걸로 할게요.",
    kind="commitment", rt="w_final", note="요청 수락, 최종 제출을 맡음")
say("SPK01", "그러니까 각자 하신 건 그 전날까지만 저한테 주시면 되는 거예요.")
say("SPK03", "아 그리고 실사 당일에 심사원분들 회의실은 어디로 잡을까요?",
    kind="open_question", note="실사 당일 회의실 배정을 물음", label="w_room")
say("SPK01", "그건 제가 이 방으로 미리 잡아 놓을게요.",
    kind="commitment", rt="w_room", note="요청 수락, 회의실 예약을 맡음")
say("SPK01", "여기가 그래도 현장에서 제일 가까우니까 오가기가 편해요.")
say("SPK04", "네 알겠습니다.")
say("SPK05", "저는 그럼 서명 받는 것부터 먼저 돌리고 있을게요.",
    kind="commitment", note="기한 없이 먼저 착수하겠다고 밝힘")
say("SPK05", "아 그리고 이 에어컨은 진짜 좀 어떻게 해 주셔야 할 것 같아요.", note="사담")
say("SPK01", "네 그건 제가 이따 설비 쪽에 따로 얘기해 둘게요.",
    kind="commitment", note="설비 요청 전달을 본인이 맡음")
say("SPK02", "저는 그럼 포장기 세팅부터 당겨 놓겠습니다.",
    kind="commitment", note="본인이 세팅 일정을 당기겠다고 함")
say("SPK01", "네 오늘 다들 고생하셨어요.")

# --- generated columns ---------------------------------------------------------
LAST_START = 1788.0
FIRST_START = 7.0


def build_starts() -> list[float]:
    """Gaps grow with the length of the row just spoken and with a speaker change."""
    weights = []
    for index in range(1, len(rows)):
        text = rows[index - 1]["text"]
        weight = 1.0 + len(text) * 0.09
        if rows[index]["speaker"] != rows[index - 1]["speaker"]:
            weight += 1.9
        weights.append(weight)
    scale = (LAST_START - FIRST_START) / sum(weights)
    starts = [FIRST_START]
    for weight in weights:
        gap = round(min(max(weight * scale, 1.05), 15.0), 2)
        starts.append(round(starts[-1] + gap, 2))
    return starts


COLS = ["row", "utterance_id", "start", "speaker", "role", "text",
        "kind", "decision_id", "settles", "responds_to", "note"]


def write_csv(path: Path, records: list[dict], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)


def rownum(label: str) -> int:
    return labels[label]


def evidence(*names: str) -> str:
    return ",".join(str(labels[n]) for n in names)


ANSWER_KEY = [
    {
        "decision_id": "D1",
        "settles_row": "d1_settle",
        "statement": "신규 파우치 라인은 이번 재심사 범위에서 빼고 시운전은 예정대로 돌리며, 변경 신고는 도면 승인 후 따로 올린다.",
        "owner": "SPK03",
        "due": "도면 승인 후 2주 이내(승인은 빨라야 11월 초)",
        "due_as_said": "승인 떨어지면 이 주 안에",
        "evidence_rows": ("d1_settle", "d1_owner", "d1_due", "d1_block"),
        "note": "신고와 실사를 한 번에 올리는 것으로 합의되는 듯했다가 도면 승인이 아직이라는 이유로 뒤집힌 뒤 범위 제외로 정리됨",
    },
    {
        "decision_id": "D2",
        "settles_row": "d2_settle",
        "statement": "서명이 빠진 미생물 검사 기록은 실사 대상 두 품목만 복원하고 나머지는 사유서로 대체한다.",
        "owner": "SPK05",
        "due": "2026-10-16(금)",
        "due_as_said": "금요일까지",
        "evidence_rows": ("d2_settle", "d2_scope", "d2_due", "d2_delegate"),
        "note": "품질팀에 통째로 넘겨진 뒤 퇴사자 서명이 불가능하다는 반대를 거쳐 팀장이 범위를 좁혀 제안했고 아무도 답하지 않은 채 넘어감",
    },
    {
        "decision_id": "D3",
        "settles_row": "d3_settle",
        "statement": "살균 조건 재검증은 이번 재심사 전에는 하지 않고 다음 달 첫 주 정기 회의에서 다시 논의한다.",
        "owner": "",
        "due": "2026년 11월 첫 주 정기 회의",
        "due_as_said": "다음 달 첫 주 정기 회의",
        "evidence_rows": ("d3_settle", "d3_due", "d3_interim"),
        "note": "라인을 비울 시간과 외부 의뢰 비용 문제로 보류, 그 사이 열전대 확보와 검증 계획서 초안만 진행",
    },
    {
        "decision_id": "D4",
        "settles_row": "d4_settle",
        "statement": "협력업체 실사가 통과되면 고등어 원료를 한 곳으로 몰고, 통과되지 않으면 지금의 두 곳 체제를 유지한다.",
        "owner": "SPK04",
        "due": "",
        "due_as_said": "",
        "evidence_rows": ("d4_settle", "d4_owner", "d4_propose"),
        "note": "결품 위험과 수분 편차에 대한 반대가 오간 뒤 협력업체 실사 결과를 조건으로 건 조건부 결정",
    },
    {
        "decision_id": "D5",
        "settles_row": "d5_settle",
        "statement": "누락된 위생교육은 조별로 나눠 다시 실시하고 표은겸이 진행과 명단 정리를 맡는다.",
        "owner": "SPK03",
        "due": "2026-10-16(금) 퇴근 전",
        "due_as_said": "금요일 퇴근 전까지",
        "evidence_rows": ("d5_settle", "d5_task", "d5_due", "d5_owner"),
        "note": "인원을 한 번에 뺄 수 없다는 반대로 조별 진행으로 좁혀진 뒤 담당만 지목되어 결정됨, 과업 내용은 세 턴 앞에 있음",
    },
    {
        "decision_id": "D6",
        "settles_row": "d6_settle",
        "statement": "원산지 오기 라벨은 창고 재고에 스티커를 덧붙여 덮고 새로 인쇄하는 분부터 표기를 고친다.",
        "owner": "SPK04",
        "due": "2026-10-20(서류 제출 10월 22일의 이틀 전)",
        "due_as_said": "서류 넘기는 날짜보다 이틀 앞으로",
        "evidence_rows": ("d6_settle", "d6_due", "doc_due", "d6_owner"),
        "note": "재인쇄 비용과 스티커 접착 불안에 대한 반대를 거쳐 재고와 신규 인쇄분을 나누는 요약으로 정리됨",
    },
]


def main() -> None:
    starts = build_starts()
    c_records, a_records = [], []
    for index, row in enumerate(rows):
        number = index + 1
        rt = row["rt"]
        if rt is None:
            responds_to = ""
        elif isinstance(rt, str):
            responds_to = str(labels[rt])
        else:
            responds_to = str(number + rt)
        shared = {
            "row": str(number),
            "utterance_id": f"{MEETING}-{number:04d}",
            "start": f"{starts[index]:.2f}",
            "speaker": row["speaker"],
            "role": ROLE[row["speaker"]],
            "text": row["text"],
        }
        c_records.append({**shared, "kind": row["kind"], "decision_id": row["decision_id"],
                          "settles": row["settles"], "responds_to": responds_to,
                          "note": row["note"]})
        a_records.append({**shared, "kind": "", "decision_id": "", "settles": "",
                          "responds_to": "", "note": ""})

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / f"{MEETING}.C.csv", c_records, COLS)
    write_csv(OUT / f"{MEETING}.A.csv", a_records, COLS)

    key_cols = ["decision_id", "settles_row", "statement", "owner", "due",
                "due_as_said", "evidence_rows", "note"]
    key_records = [
        {**entry,
         "settles_row": str(rownum(entry["settles_row"])),
         "evidence_rows": evidence(*entry["evidence_rows"])}
        for entry in ANSWER_KEY
    ]
    write_csv(OUT / f"{MEETING}.D.csv", key_records, key_cols)
    (OUT / f"{MEETING}.speakers.json").write_text(
        json.dumps(SPEAKERS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # A quick read of the numbers the three checkers care about, so a fix round is
    # not spent finding out which band is out.
    lengths = [len(r["text"]) for r in rows]
    filler = re.compile(
        r"(?<![가-힣])(음+|어+|아+|그+|저기|뭐|뭐지|뭐냐|뭐랄까|그러니까|그니까|어쨌든|아무튼|약간|이제|일단|좀|그냥|막)(?![가-힣])")
    fixes = re.compile(r"(아니|아니라|그게 아니라|다시 말해|정정)")
    total = sum(lengths)
    same = sum(1 for a, b in zip(rows, rows[1:]) if a["speaker"] == b["speaker"])
    kinds: dict[str, int] = {}
    for row in rows:
        kinds[row["kind"]] = kinds.get(row["kind"], 0) + 1
    print(f"rows {len(rows)}  last start {starts[-1]:.2f}")
    print(f"median {sorted(lengths)[len(lengths) // 2]}  mean {total / len(lengths):.1f}  "
          f"same-speaker {same / len(rows) * 100:.1f}%  "
          f"short<=6 {sum(1 for n in lengths if n <= 6) / len(rows) * 100:.1f}%")
    print(f"fillers {sum(len(filler.findall(r['text'])) for r in rows) / total * 100:.2f}/100  "
          f"self-fix {sum(len(fixes.findall(r['text'])) for r in rows) / total * 100:.2f}/100")
    print("kinds " + " ".join(f"{k} {v}" for k, v in sorted(kinds.items())))


if __name__ == "__main__":
    main()
