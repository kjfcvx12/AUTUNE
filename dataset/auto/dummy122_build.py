"""Build DUMMY_122 -- an invented refurbished-appliance resale platform meeting, training data.

Same generator shape as dummy121_build.py. Writes DUMMY_122.{A,C,D}.csv and
DUMMY_122.speakers.json into dataset/team_dummy/.

Everything invented: company, people, numbers.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "team_dummy"
MEETING = "DUMMY_122"

ROLE = {
    "SPK01": "PM",
    "SPK02": "Ops",
    "SPK03": "QA",
    "SPK04": "Data",
    "SPK05": "CS",
}

SPEAKERS = {
    "meeting": MEETING,
    "title": "다시가전 리퍼브 플랫폼 운영팀 겨울 성수기 준비 회의",
    "type": "team",
    "position_order": ["사원", "주임", "대리", "과장", "차장", "부장", "이사", "대표"],
    "speakers": [
        {"speaker": "SPK01", "name": "한지원", "team": "다시가전 운영팀", "job": "PM",
         "position": "과장", "title": "팀장"},
        {"speaker": "SPK02", "name": "오세훈", "team": "다시가전 운영팀", "job": "Ops",
         "position": "대리", "title": ""},
        {"speaker": "SPK03", "name": "임수아", "team": "다시가전 운영팀", "job": "QA",
         "position": "주임", "title": ""},
        {"speaker": "SPK04", "name": "배준형", "team": "다시가전 운영팀", "job": "Data",
         "position": "대리", "title": ""},
        {"speaker": "SPK05", "name": "강나윤", "team": "다시가전 운영팀", "job": "CS",
         "position": "사원", "title": ""},
    ],
}

rows: list[dict] = []
labels: dict[str, int] = {}


def say(speaker: str, text: str, kind: str = "none", decision: str = "",
        settles: str = "", rt: int | None = None, note: str = "",
        label: str | None = None) -> None:
    rows.append({
        "speaker": speaker, "text": text, "kind": kind, "decision_id": decision,
        "settles": settles, "rt": rt, "note": note,
    })
    if label:
        labels[label] = len(rows)


# --- opening ---------------------------------------------------------------------
say("SPK03", "음 저 오늘 좀 늦을 뻔했어요, 아침부터 물류센터에서 전화가 계속 와서요.")
say("SPK03", "어제 입고된 세탁기 중에 두 대가 외관 파손으로 들어왔다고 하더라고요.")
say("SPK03", "박스는 멀쩡한데 안에서 뭐가 부딪혔는지 문짝이 좀 찌그러져 있었대요.")
say("SPK03", "다행히 작동은 되는데 문짝은 새로 주문해야 될 것 같아요.")
say("SPK02", "어 그거 저도 사진으로 봤어요. 일단 택배사 쪽에는 클레임 넣어두셨어요?")
say("SPK03", "음 네 넣긴 넣었는데 그쪽에서도 자기들 잘못인지 확인해봐야 한다고만 하더라고요.")
say("SPK03", "며칠 걸린다고 하는데 저는 그게 좀 답답하더라고요.")
say("SPK01", "음 일단 그건 이따가 물류 얘기할 때 같이 볼게요. 오늘은 일단 넷만 좀 보고 갈게요.")
say("SPK01", "겨울 성수기 재고 확보랑 검수 기준, 반품 처리, 그리고 고객 불만 응대 건이요.")
say("SPK01", "그 순서대로 갈 건데 혹시 더 급한 거 있으시면 먼저 말씀해 주세요.")
say("SPK01", "택배 파손 건도 오늘 안에 시간 되면 같이 보고 안 되면 다음으로 넘길게요.")
say("SPK01", "아 그리고 오늘은 회의록 대신 정해진 것만 제가 메신저에 올려둘게요.",
    kind="commitment", note="본인이 회의록 대신 정리를 맡겠다고 함")
say("SPK01", "지난번처럼 다 받아 적다가 정작 뭘 정했는지 안 남으면 그게 더 곤란하더라고요.")
say("SPK01", "그러니까 중간에 궁금한 거 있으면 그냥 끊고 들어오셔도 돼요, 편하게 하세요.")
say("SPK04", "네 저도 그게 편해요, 저번 회의록은 저도 나중에 다시 봐도 뭐가 뭔지 모르겠더라고요.")
say("SPK01", "그럼 준형 씨가 정리해온 그 재고 수치부터 보고 시작하죠.",
    kind="open_question", note="논의 순서를 정하며 데이터 공유를 요청함")
say("SPK04", "음 그러니까 이번 겨울 시즌 목표 물량이 냉장고 세탁기 다 합쳐서 이천 대인데요,")
say("SPK04", "어 지금 확보된 게 그중에 팔백 대 정도밖에 안 돼요, 사십 퍼센트도 안 되는 거예요.")
say("SPK04", "음 품목별로 나눠보면 냉장고보다 세탁기 쪽이 더 심각한 상황이고요.")
say("SPK04", "세탁기는 목표 대비 이제 삼십 퍼센트 정도밖에 안 채워졌어요.")
say("SPK04", "냉장고는 그나마 오십오 퍼센트 정도는 채워져서 사정이 좀 낫고요.")
say("SPK04", "그래도 목표까지는 아직 한참 남은 상황이긴 해요.")
say("SPK01", "어 근데 그 차이는 왜 그런 거예요?", kind="open_question", rt=-1, note="냉장고와 세탁기 확보율 차이의 원인을 물음")
say("SPK04", "그러니까 세탁기 쪽 매입처가 상대적으로 더 적어서 그런 것 같아요.")
say("SPK01", "매입처가 몇 군데나 되길래 그렇게 차이가 나는 거예요?")
say("SPK04", "냉장고는 다섯 군데인데 세탁기는 세 군데밖에 안 돼요.")
say("SPK01", "아 그 정도면 차이 날 만하네요.")
say("SPK04", "네 그래서 세탁기 쪽이 유독 더 심각한 거예요.")
say("SPK04", "매입처 늘리는 것도 그래서 세탁기 쪽부터 급한 거고요.")
say("SPK02", "저도 예상은 했는데 숫자로 보니까 좀 심각하네요.")

# --- D1: sourcing shortfall, false agreement inside --------------------------------
say("SPK04", "작년 같은 시기에는 이맘때 천이백 대 정도는 확보돼 있었거든요.", decision="D1")
say("SPK04", "아 천이백이 아니라 천백이네요. 작년 자료랑 재작년 자료를 헷갈렸어요.", decision="D1")
say("SPK04", "어쨌든 그때보다 확실히 확보 속도가 느린 건 맞아요.", decision="D1")
say("SPK04", "어 저희가 지금 매입처를 세 군데만 쓰고 있는데 거기서 나오는 물량이 줄었더라고요.", decision="D1")
say("SPK04", "세 곳 다 조금씩은 줄었는데 그중 한 곳이 특히 많이 줄었어요.", decision="D1")
say("SPK04", "특히 그중에 제일 큰 곳이 요즘 물량을 반 정도로 줄였다고 하더라고요.", decision="D1")
say("SPK04", "그게 저희 전체 물량의 한 육십 퍼센트를 차지하던 곳이라 타격이 좀 크네요.", decision="D1")
say("SPK04", "이 상태로 가면 다음 달에는 아예 물량이 더 줄어들 수도 있을 것 같고요.", decision="D1")
say("SPK02", "그건 저도 들었어요. 거기 담당자가 다른 업체랑도 계약했다고 하더라고요.", decision="D1")
say("SPK02", "저희 말고 다른 리퍼브 업체한테도 같이 넘기고 있는 것 같아요.", decision="D1")
say("SPK02", "저번 주에 담당자 만났을 때도 그런 뉘앙스로 말씀하시긴 했었어요.", decision="D1")
say("SPK02", "저희가 그때 좀 더 적극적으로 먼저 얘기했어야 했나 싶기도 하고요, 아쉽네요.", decision="D1")
say("SPK03", "어 그럼 검수 인력은 지금 물량 기준으로 맞춰놓은 거라 남는 거 아니에요?",
    kind="open_question", decision="D1", rt=-1, note="확보량 감소가 검수 인력 여유로 이어지는지 물음")
say("SPK03", "지금 저희 셋이서 하루에 백 대는 볼 수 있는 체제로 짜놨었거든요.", decision="D1")
say("SPK01", "그 얘기는 검수 쪽에서 이따 다시 할게요, 일단 물량부터 정리하고요.")
say("SPK01", "음 그럼 목표를 못 채우면 성수기에 판매할 재고 자체가 없다는 얘기인데요.", decision="D1")
say("SPK01", "이번 주 안에 매입처를 좀 더 뚫어야 될 것 같은데 다들 어떻게 보세요?", decision="D1")
say("SPK02", "저는 일단 지금 매입처 세 군데를 그대로 두고 단가를 좀 올려주는 게 낫지 않을까 싶어요.",
    decision="D1")
say("SPK02", "근데 새 업체 뚫는 건 검증하는 데만도 시간이 꽤 걸리거든요.", decision="D1")
say("SPK02", "지금 당장 물량이 급한데 검증 기간까지 기다릴 여유는 없을 것 같아서요.", decision="D1")
say("SPK04", "음 근데 단가를 올리면 그만큼 저희 마진이 줄어드는 거라서요.", kind="concern",
    decision="D1", rt=-2, note="매입 단가 인상이 마진 축소로 이어진다는 우려")
say("SPK04", "일단 지금도 마진이 그렇게 넉넉한 편은 아니거든요.", decision="D1")
say("SPK04", "성수기 판매가를 올리지 않는 이상 단가 인상분은 그대로 손해예요.", decision="D1")
say("SPK01", "그럼 새 매입처를 하나 더 뚫는 쪽으로 가죠! 그게 더 낫겠네요.",
    decision="D1", note="번복, 합의된 것처럼 보였다가 다음 턴에서 뒤집힘", label="d1_false")
say("SPK02", "네 그게 나을 것 같긴 해요.", decision="D1")
say("SPK03", "아 잠깐만요, 그 새 매입처는 저희 검수 기준에 맞는지 먼저 확인해야 되는데요.",
    kind="concern", decision="D1", rt=-2, note="신규 매입처가 검수 기준을 충족하는지 사전 검증이 필요함을 지적")
say("SPK01", "그때 그 업체는 어떻게 걸러낸 거였죠?", kind="open_question", decision="D1", rt=-1,
    note="과거 불량 업체를 어떻게 발견했는지 물음")
say("SPK03", "저번에 급하게 뚫었던 데는 결국 불량률이 너무 높아서 석 달 만에 끊었잖아요.", decision="D1")
say("SPK03", "그때 반품이랑 재검수 비용이 더 나가서 오히려 손해였고요.", decision="D1")
say("SPK03", "그 업체는 포장 상태부터가 저희 기준이랑 많이 달랐던 걸로 기억해요.", decision="D1")
say("SPK03", "그러니까 좀 새 곳을 뚫더라도 최소 한두 달은 검증 기간을 잡아야 할 것 같아요.", decision="D1")
say("SPK03", "그 기간 동안은 오히려 검수 인력이 그쪽에 더 붙어야 되기도 하고요.", decision="D1")
say("SPK01", "아 그러네요, 그때 그 일이 있었죠.")
say("SPK01", "그럼 새 매입처는 검증 기간이 필요하니까 이번 성수기에는 못 쓰겠네요.", decision="D1")
say("SPK04", "음 그러면 결국 남은 건 단가 조정밖에 없는 것 같은데요.", decision="D1")
say("SPK04", "근데 그것도 사실 임시방편이라는 느낌은 있어서 좀 걱정이긴 해요.",
    kind="concern", decision="D1", rt=-1, note="단가 조정이 근본 해결책은 아니라는 우려")
say("SPK02", "어 단가를 다 올리지 말고 물량을 제일 많이 주던 그 업체만 먼저 올려보면 어때요?",
    decision="D1")
say("SPK02", "거기가 원래 제일 컸으니까 거기만 잡아도 효과가 꽤 있을 것 같아요.", decision="D1")
say("SPK04", "음 그 정도면 전체 마진 하락 폭이 한 삼 퍼센트 정도라서 감당은 충분히 될 것 같아요.", decision="D1")
say("SPK04", "나머지 두 곳은 지금 단가로도 그럭저럭 물량을 유지해주고 있어서 괜찮을 것 같고요.", decision="D1")
say("SPK01", "그럼 두 곳은 그대로 가고 제일 큰 곳만 조정하는 방향이네요.")
say("SPK04", "네 맞아요.")
say("SPK01", "그럼 제일 큰 매입처 단가만 올리고 나머지는 그대로 가는 걸로 정리할게요.",
    kind="decision", decision="D1", settles="1",
    note="신규 매입처 검증 문제로 무산된 뒤 기존 최대 매입처 단가 조정으로 절충", label="d1_settle")
say("SPK04", "일단 그 업체 담당자한테는 제가 이번 주 안으로 연락해서 조율해볼게요.",
    kind="commitment", decision="D1", rt=-1, note="본인이 매입처 협상 착수를 맡음, 기한 명시",
    label="d1_owner")
say("SPK02", "음 저도 그쪽이랑 좀 친분이 있어서 필요하면 같이 얘기해볼 수는 있어요.",
    kind="ambiguous", decision="D1", rt=-1, note="구체적 계획 없이 필요하면 돕겠다는 약한 응답")
say("SPK04", "얼마나 올려야 물량이 늘어날지는 저쪽이랑 얘기해봐야 알 것 같아요.", decision="D1",
    label="d1_due")
say("SPK04", "너무 많이 올리면 이제 저희 쪽이 손해니까 그 선을 잘 잡아야 할 것 같아요.", decision="D1")
say("SPK04", "일단 삼 퍼센트 선에서 먼저 제안해보고 반응 보면서 조정하려고요.", decision="D1")
say("SPK01", "음 그럼 그 결과 보고 다음 주에 물량 목표를 다시 잡죠.")
say("SPK03", "네.")
say("SPK02", "저도 일단 그동안 다른 매입처들 물량도 좀 더 당길 수 있는지 알아볼게요.",
    kind="commitment", decision="D1", note="본인 계획으로 기존 매입처 추가 확보를 시도함, 기한 없음")
say("SPK02", "혹시 물량 좀 더 주실 수 있는지 이번 주에 연락 돌려볼게요.", decision="D1")
say("SPK04", "음.")
say("SPK01", "네 그럼 다음 주 회의 때 두 분 다 결과 좀 공유해 주세요.")
say("SPK02", "네 알겠습니다.")
say("SPK04", "네.")

# --- side talk 1 -------------------------------------------------------------------
say("SPK05", "아 근데 옆 건물에 그 카페 리모델링 끝났던데 가보셨어요? 인테리어가 예쁘더라고요.", note="사담")
say("SPK02", "저 아직 안 가봤어요. 커피 맛은 어때요?", note="사담")
say("SPK05", "저는 괜찮았어요, 근데 가격이 좀 있더라고요.", note="사담")
say("SPK05", "아메리카노 한 잔에 육천 원이었나 그랬어요.", note="사담")
say("SPK03", "저도 한번 가봐야겠네요, 요즘 마땅한 데가 없어서 좀 아쉬웠거든요.", note="사담")
say("SPK03", "예전에 자주 가던 데가 얼마 전에 문을 닫아서요.", note="사담")
say("SPK02", "거기 왜 닫았대요? 장사 잘 되는 것 같았는데.", note="사담")
say("SPK03", "저도 정확히는 몰라요, 그냥 어느 날 갑자기 안 열려 있더라고요.", note="사담")
say("SPK02", "요즘 그런 데가 은근히 많더라고요.", note="사담")
say("SPK05", "저도 자주 가던 분식집이 얼마 전에 없어졌어요.", note="사담")
say("SPK04", "요즘 임대료가 워낙 비싸다 보니까 다들 힘든가 봐요.", note="사담")
say("SPK02", "그러게요, 저희 동네도 그런 얘기 많이 들려요.", note="사담")
say("SPK02", "예전엔 이 정도는 아니었던 것 같은데 요즘 들어 유독 심해진 것 같아요.", note="사담")
say("SPK01", "자 그 얘기는 이따 하고요, 검수 기준 넘어갈게요.")

# --- D2: inspection criteria, lead proposal unanswered -----------------------------
say("SPK01", "지난주에 반품 들어온 것 중에 검수 통과했던 게 두 건 있었잖아요. 그거 좀 봐야 할 것 같은데요.",
    decision="D2")
say("SPK05", "음 네 그중에 한 건은 고객님이 전원이 아예 안 켜진다고 하셨어요.", decision="D2")
say("SPK05", "받자마자 켜봤는데 그냥 안 되더라고 하시면서 많이 화가 나신 상태였어요.", decision="D2")
say("SPK05", "일단 환불 처리는 해드렸는데 배송비도 저희가 부담했어요.", decision="D2")
say("SPK05", "그것도 왕복이라 생각보다 금액이 좀 나갔어요.", decision="D2")
say("SPK05", "고객님도 처음엔 화가 많이 나셨는데 환불 처리해드리니까 그나마 좀 누그러지셨어요.", decision="D2")
say("SPK05", "어 다른 한 건은 소음이 너무 크다고 하셨는데 그건 아직 처리 중이에요.", decision="D2")
say("SPK05", "고객님이 영상까지 찍어서 보내주셨는데 저희가 들어봐도 좀 크긴 하더라고요.", decision="D2")
say("SPK01", "음 지금 검수 기준이 전원 켜서 오 분 작동 확인하는 게 전부인 거죠?", decision="D2")
say("SPK03", "네 근데 그 기준으로는 순간적으로 꺼지는 문제는 잘 안 잡혀요.", decision="D2")
say("SPK03", "그 세탁기도 저희가 볼 때는 오 분 내내 잘 돌았거든요.", decision="D2")
say("SPK03", "기록 봐도 이상 없음으로 표시돼 있었고 저도 그때 직접 확인했었어요.", decision="D2")
say("SPK03", "그래서 이게 검수 단계 문제인지 배송 과정 문제인지가 좀 헷갈려요.", decision="D2")
say("SPK03", "비슷한 사례가 더 있는지 한번 찾아봐야 할 것 같고요.", decision="D2")
say("SPK03", "근데 그게 배송 중에 흔들리면서 접촉 불량이 생겼을 수도 있어요.", decision="D2")
say("SPK01", "그러면 제가 보기엔 검수를 이십 분으로 늘리는 게 맞을 것 같은데요.",
    decision="D2", label="d2_proposal")
say("SPK02", "어 근데 그렇게 하면 하루에 볼 수 있는 대수가 확 줄어드는 거 아닌가요?",
    kind="open_question", decision="D2", rt=-1, note="검수 시간 연장이 일일 처리량에 미치는 영향을 물음")
say("SPK02", "지금도 백 대 보는 게 빠듯한데 시간을 네 배로 늘리면 감당이 안 될 것 같아서요.", decision="D2")
say("SPK01", "아 그건 이따 인력 얘기할 때 같이 볼게요, 지금은 기준만이요.")
say("SPK01", "일단 뭐가 맞는 방향인지부터 정하고 인력은 그다음에 맞춰야죠.")
say("SPK03", "근데 시간을 늘려도 그 접촉 불량 같은 건 흔들어봐야 나오는 거라 꼭 잡힌다는 보장은 없어요.",
    kind="concern", decision="D2", rt=-4, note="검수 시간 연장만으로는 배송 중 접촉 불량을 못 잡을 수 있다는 우려")
say("SPK03", "저희가 검수할 때는 그냥 고정된 자리에 두고 켜보는 거라서요.", decision="D2")
say("SPK04", "음 그럼 시간을 늘리는 것보다 배송 후 재검수를 한 번 더 하는 게 낫지 않을까요?",
    decision="D2")
say("SPK04", "고객한테 가기 직전에 흔들린 상태 그대로 켜보면 그게 더 정확할 것 같아요.", decision="D2")
say("SPK04", "저희가 예전에 그렇게 한 적이 있었는데 그때는 불량 적발률이 꽤 높았거든요.", decision="D2")
say("SPK04", "그때 기억으로는 한 오 퍼센트 정도는 그 단계에서 추가로 걸러졌었어요.", decision="D2")
say("SPK04", "그때 왜 그만뒀는지는 저도 정확히는 기억이 안 나네요.", decision="D2")
say("SPK02", "근데 그러면 좀 물류센터에서 한 번 더 열어봐야 되는 건데 그건 인력이 또 필요해요.",
    kind="concern", decision="D2", rt=-2, note="배송 전 재검수 추가가 별도 인력을 필요로 한다는 우려")
say("SPK01", "음 그것도 그렇네요. 이건 조금 더 생각해봐야 할 것 같아요. 데이터를 좀 더 모으고 다시 봅니다.",
    kind="decision", decision="D2", settles="1",
    note="상급자 제안, 아무도 명확히 답하지 않고 데이터 보완 후 재논의로 넘어감", label="d2_settle")
say("SPK03", "음 그럼 제가 이번 주 반품 건들 중에 원인 특정 가능한 것부터 좀 정리해볼게요.",
    kind="commitment", decision="D2", rt=-1, note="본인 계획으로 반품 원인 데이터 정리를 맡음, 기한 없음")
say("SPK03", "그게 있어야 검수를 늘려야 하는지 재검수를 넣어야 하는지 판단이 설 것 같아서요.", decision="D2")
say("SPK01", "네.")
say("SPK02", "그럼 그것도 저희 쪽 자료랑 같이 맞춰볼게요.",
    kind="ambiguous", decision="D2", rt=-2, note="구체적 계획 없이 자료를 맞춰보겠다는 약한 응답")
say("SPK01", "네 그럼 다음 주에 데이터 보고 다시 얘기하죠.")
say("SPK03", "네 알겠습니다.")

# --- D3: return process, held over --------------------------------------------------
say("SPK01", "그다음 반품 처리 얘기인데요, 지금 반품 처리에 평균 며칠 걸리는 거예요?")
say("SPK05", "어 지금 평균 나흘이요, 근데 성수기 되면 그게 더 늘어날 것 같아서 걱정이에요.", decision="D3")
say("SPK05", "지금도 반품 접수하고 실제 환불까지 가는 데 손이 많이 가거든요.", decision="D3")
say("SPK05", "접수는 제가 받고 재입고 확인은 물류센터에 요청하고 환불은 또 회계팀이라서요.", decision="D3")
say("SPK05", "그 사이에 왔다 갔다 하는 메일이랑 전화만 해도 꽤 되더라고요.", decision="D3")
say("SPK05", "그러다 보니까 고객님도 언제 환불되냐고 중간에 또 문의를 주시고요.", decision="D3")
say("SPK02", "음 그거 저희 시스템에서 자동으로 처리하는 부분은 없는 거예요?",
    kind="open_question", decision="D3", rt=-2, note="반품 처리 자동화 가능 여부를 물음")
say("SPK05", "일부는 되는데 물류센터 재입고 확인이 수동이라 거기서 늘 걸려요.", decision="D3")
say("SPK04", "그거 시스템 쪽에 자동화 요청은 넣어보신 거예요?",
    kind="open_question", decision="D3", rt=-1, note="자동화 개발 요청 여부를 확인함")
say("SPK05", "음 넣긴 넣었는데 개발팀 쪽 일정이 꽉 차 있어서 정확히 언제 될지는 모른다고 했어요.", decision="D3")
say("SPK05", "저번 달에 넣었는데 아직 답도 못 받은 상태예요.", decision="D3", label="d3_request")
say("SPK05", "다른 팀도 요청이 많이 밀려 있다고 하더라고요.", decision="D3")
say("SPK01", "그 순서는 누가 정하는 거예요?", kind="open_question", decision="D3", rt=-1,
    note="개발팀 요청 처리 순서 결정 주체를 물음")
say("SPK05", "저희만 급한 게 아니라서 순서를 당겨달라고 하기도 좀 애매하고요.", decision="D3")
say("SPK05", "그래도 계속 얘기는 해봐야 할 것 같아요.", decision="D3")
say("SPK04", "아 그게 아니고, 그냥 무작정 기다리기만 하면 성수기 다 놓칠 수도 있어서 걱정이에요.",
    kind="concern", decision="D3", rt=-1, note="개발팀 응답을 기다리기만 하면 성수기를 놓칠 수 있다는 우려")
say("SPK01", "그럼 이건 오늘 뭘 정할 수 있는 상황은 아니네요.")
say("SPK01", "일단 오늘은 정하지 말고 개발팀 답이 오면 다시 봅니다.",
    kind="decision", decision="D3", settles="1",
    note="개발 일정 미확정으로 이번 주는 보류, 답변 오면 재논의", label="d3_settle")
say("SPK05", "일단 그동안은 그럼 저 혼자라도 좀 더 빠르게 처리해보도록 할게요.",
    kind="commitment", decision="D3", rt=-1, note="본인 계획으로 임시 처리 속도 개선을 맡음, 기한 없음")
say("SPK05", "재입고 확인 요청하는 메일이라도 좀 더 자주 보내보려고요.", decision="D3")
say("SPK01", "네 부탁드려요.")
say("SPK02", "저도 물류센터 쪽에 얘기해서 재입고 확인 좀 더 빨리 해달라고 해볼게요.",
    kind="ambiguous", decision="D3", rt=-2, note="구체적 계획 없이 협조를 요청해보겠다는 약한 응답")
say("SPK01", "네 감사해요, 그거라도 좀 나아지면 좋겠네요.")
say("SPK05", "네 저도 그러길 바라요.")

# --- side talk 2 ---------------------------------------------------------------------
say("SPK02", "아 그리고 주차 등록 이번 달까지 다시 해야 되는 거 아세요? 저번에 공지 왔었는데요.", note="사담")
say("SPK04", "아 맞다 까먹고 있었어요. 오늘 안에 해야겠네요.", note="사담")
say("SPK04", "안 하면 다음 달부터 주차비 다 내야 된다고 했었죠 아마.", note="사담")
say("SPK03", "저도 등록해야 되는데 계속 미루고 있었어요.", note="사담")
say("SPK03", "어디서 하는 건지도 가물가물하네요.", note="사담")
say("SPK02", "저는 어제 해놨어요, 별로 안 오래 걸려요.", note="사담")
say("SPK02", "총무팀 페이지에서 하시면 돼요, 오 분도 안 걸려요.", note="사담")
say("SPK05", "저도 해야겠네요, 알려주셔서 감사해요.", note="사담")
say("SPK04", "저 방금 등록했어요, 진짜 오 분도 안 걸리네요.", note="사담")
say("SPK01", "자 그건 이따 각자 하시고요, 고객 불만 응대 얘기로 넘어갈게요.")

# --- D4: complaint escalation, conditional -----------------------------------------
say("SPK01", "고객 불만 응대 건인데, 최근 들어 재발송 요청이 좀 늘었다고 들었어요.", decision="D4")
say("SPK05", "음 네 소음 관련 불만이 특히 많아요, 근데 저희 기준으로는 정상 범위거든요.",
    kind="concern", decision="D4", rt=-1, note="정상 판정 제품에 대한 소음 불만이 늘고 있다는 문제 제기")
say("SPK05", "저희가 소음 기준을 데시벨로 재긴 하는데 고객님이 체감하시는 거랑은 좀 다른가 봐요.", decision="D4")
say("SPK05", "특히 오래된 모델일수록 그런 불만이 더 많이 들어와요.", decision="D4")
say("SPK05", "밤에 쓰시는 분들은 특히 더 예민하게 느끼시는 것 같고요.", decision="D4")
say("SPK05", "전화로 응대하다 보면 같은 얘기를 계속 반복해서 드려야 해서 저도 좀 지치더라고요.", decision="D4")
say("SPK03", "어 그건 아무래도 부품 자체가 오래돼서 그럴 수밖에 없긴 해요.", decision="D4")
say("SPK03", "새 부품으로 다 갈 수도 없는 노릇이고요, 리퍼브다 보니까 한계가 있어요.", decision="D4")
say("SPK03", "모터 베어링 쪽이 특히 소음에 영향을 많이 주는데 그건 교체 비용이 꽤 커요.", decision="D4")
say("SPK03", "그거 하나 갈면 이제 마진이 아예 안 남을 수도 있어서 쉽게 결정하기 어려워요.", decision="D4")
say("SPK03", "그래서 저는 웬만하면 그 부품은 안 건드리는 쪽으로 가고 싶어요.", decision="D4")
say("SPK04", "근데 재발송 비율이 최근 두 달 사이에 두 배 가까이 늘긴 했어요.", decision="D4")
say("SPK04", "그중에 절반은 소음 관련이고 나머지는 뭐 기타 사유들이에요.", decision="D4")
say("SPK04", "재발송 한 번에 드는 비용도 무시 못 할 수준이라 이게 계속 쌓이면 문제예요.", decision="D4")
say("SPK01", "음 그럼 소음 기준을 아예 상세 페이지에 미리 명시하는 건 어때요?", kind="open_question",
    decision="D4", rt=-4, note="소음 기준 사전 고지 방안을 제안하며 의견을 물음")
say("SPK02", "음 그거 좋은 것 같아요, 근데 문구를 누가 어떻게 쓸지가 문제긴 하네요.", decision="D4")
say("SPK02", "너무 부정적으로 쓰면 그것대로 구매를 안 하실 것 같고 애매하네요.", decision="D4")
say("SPK02", "문구는 그럼 나중에 마케팅팀 자문도 좀 받아보는 게 좋을 것 같아요.", decision="D4")
say("SPK05", "저는 근데 그거 명시해도 결국 받아보시고 다르다고 느끼시면 똑같이 불만 들어올 것 같아요.",
    kind="concern", decision="D4", rt=-2, note="사전 고지만으로는 체감 불만을 막기 어렵다는 우려")
say("SPK05", "글로 미리 설명드려도 실제로 들으시는 거랑은 다르다고 하시는 분들이 많거든요.", decision="D4")
say("SPK05", "그래서 저는 사전 고지보다는 다른 방법을 좀 더 찾아봐야 할 것 같아요.", decision="D4")
say("SPK05", "고지는 하되 그거 하나로 다 해결될 거라고는 기대 안 하는 게 맞을 것 같고요.", decision="D4")
say("SPK01", "그럼 페이지에 명시하는 거랑 별개로, 재발송 대신 부분 환불을 제안하는 건 어때요?",
    decision="D4")
say("SPK01", "재발송하면 물류비가 또 나가는데 부분 환불이 오히려 쌀 수도 있잖아요.", decision="D4")
say("SPK04", "음 그건 계산을 좀 해봐야 알겠는데, 금액에 따라서는 그게 나을 수도 있을 것 같아요.", decision="D4")
say("SPK04", "재발송 왕복 물류비가 대략 삼만 원 정도니까 그거보다 적으면 부분 환불이 낫겠네요.", decision="D4")
say("SPK02", "아니 근데, 가격대별로 나누면 표가 너무 복잡해지는 거 아니에요?", kind="concern",
    decision="D4", rt=-1, note="가격대별 세분화가 표를 지나치게 복잡하게 만들 수 있다는 우려")
say("SPK04", "근데 제품 가격대별로 그 기준이 다 다를 것 같아서 표로 정리해야 할 것 같아요.", decision="D4")
say("SPK04", "냉장고랑 세탁기랑도 물류비가 다르니까 그것도 따로 잡아야 하고요.", decision="D4")
say("SPK04", "근데 표로 정리해도 결국 담당자가 상황 봐가면서 판단해야 하는 부분은 남을 것 같아요.",
    kind="concern", decision="D4", rt=-1, note="기준표가 있어도 현장 판단 여지가 남는다는 우려")
say("SPK04", "이번 주까지 다 계산해서 표로 정리해서 올려둘게요.", decision="D4")
say("SPK01", "그럼 재발송 비용이 부분 환불 금액보다 크면 부분 환불을 먼저 제안하는 방향으로 정리할게요.",
    kind="decision", decision="D4", settles="1",
    note="조건부 결정, 비용 비교 결과에 따라 대응 방식이 갈림", label="d4_settle")
say("SPK04", "그 기준 금액은 제가 이번 주에 계산해서 표로 정리해볼게요.",
    kind="commitment", decision="D4", rt=-1, note="본인이 비용 비교 기준표 작성을 맡음, 기한 명시",
    label="d4_owner")
say("SPK05", "그거 나오면 저는 그거 보고 응대 스크립트에 반영할게요.",
    kind="commitment", decision="D4", rt=-1, note="본인 계획으로 응대 스크립트 반영을 맡음, 기한 없음")
say("SPK01", "네 좋아요, 그럼 그렇게 진행하죠.")
say("SPK02", "저도 마케팅팀 쪽에 문구 자문 건 한번 물어볼게요.",
    kind="ambiguous", decision="D4", rt=-1,
    note="전달, 구체적 계획 없이 마케팅팀에 자문 요청을 전달만 하겠다는 약한 응답")

# --- side talk 3 ---------------------------------------------------------------------
say("SPK03", "아 그리고 아까 그 세탁기 파손 건, 택배사 쪽 답은 오늘 온대요?", note="사담")
say("SPK02", "확실친 않은데 내일까지는 준다고 했어요.", note="사담")
say("SPK02", "제가 오전에 한 번 더 전화해서 재촉은 해뒀어요.", note="사담")
say("SPK02", "그쪽 담당자도 이번엔 좀 곤란한 눈치이긴 하더라고요.", note="사담")
say("SPK04", "저번에도 그렇게 말해놓고 이틀 더 걸렸었죠 아마.", note="사담")
say("SPK04", "그때도 결국 저희가 계속 전화해야 겨우 답이 왔었잖아요.", note="사담")
say("SPK02", "그러게요, 이번엔 좀 빨리 왔으면 좋겠네요.", note="사담")
say("SPK03", "그 문짝 값이 꽤 나가서 저도 좀 신경 쓰이네요.", note="사담")
say("SPK02", "그러게요, 부품값만 몇 십만 원은 될 것 같던데요.", note="사담")
say("SPK04", "그건 저희가 아니라 택배사 과실이니까 결국 청구할 수 있지 않을까요.", note="사담")
say("SPK02", "그렇겠죠, 저도 그렇게 얘기는 해뒀어요.", note="사담")
say("SPK03", "잘 좀 받아냈으면 좋겠네요.", note="사담")
say("SPK03", "이런 일이 자꾸 있으면 택배사도 좀 바꿔봐야 하나 싶어요.", note="사담")

# --- D5: inspection staffing backlog, resistance before settling -------------------
say("SPK01", "마지막으로 검수 인력 얘기를 좀 해야 할 것 같아요. 지금 상태가 어때요?")
say("SPK03", "음 지금 저희 셋이서 하루 백 대씩 보고 있는데 성수기 되면 그게 두 배는 될 것 같아요.",
    decision="D5")
say("SPK03", "지금도 사실 빠듯하게 맞추고 있는 상황이라 더 늘면 감당이 안 될 것 같아요.", decision="D5")
say("SPK03", "한 명이라도 아프거나 하면 그날은 아예 목표를 못 채워요.", decision="D5")
say("SPK03", "저번 주에 저 하루 연차 썼을 때도 그날 목표 못 채우고 다음 날로 밀렸었거든요.", decision="D5")
say("SPK01", "음 이건 뭐 검수팀에서 알아서 좀 조정해서 맞춰주셔야 할 것 같은데요.",
    decision="D5", label="d5_thrown")
say("SPK03", "아니 저희끼리 조정한다고 되는 문제가 아니에요, 물리적으로 사람이 부족한 거라서요.",
    kind="concern", decision="D5", rt=-1, note="인력 부족은 조정이 아니라 충원이 필요한 문제라는 반대")
say("SPK03", "지금도 야근을 거의 매일 하고 있는 상황이라 이 이상은 진짜 무리예요.", decision="D5")
say("SPK03", "저번 주에도 다들 아홉 시 넘어서 퇴근했었잖아요.", decision="D5")
say("SPK03", "금요일엔 거의 열 시까지 있었던 것 같아요.", decision="D5")
say("SPK03", "이러다 누구 하나 그만둔다고 할까 봐 저도 좀 걱정이에요.", decision="D5")
say("SPK03", "채용 공고는 올려주셨다고 들었는데 지원자가 별로 없다고 하더라고요.", decision="D5")
say("SPK01", "네 저도 그건 알고 있어요, 조건을 좀 조정해야 하나 고민 중이에요.")
say("SPK02", "음 저희 쪽에서 입고 확인하는 인원 한두 명 정도는 잠깐 도와드릴 수 있을 것 같긴 한데요.",
    decision="D5")
say("SPK02", "근데 저희도 검수 경험이 있는 건 아니라서 간단한 것만 도와드릴 수 있어요.", decision="D5")
say("SPK02", "저희 쪽도 입고량이 늘어서 딱히 여유 인력이 있는 건 아니거든요.", decision="D5")
say("SPK02", "그래도 하루에 한두 시간 정도는 빼서 도와드릴 수 있을 것 같아요.", decision="D5")
say("SPK03", "음 간단한 거라면 구체적으로 어떤 거요?", kind="open_question", decision="D5", rt=-1,
    note="지원 가능한 검수 범위를 구체적으로 물음")
say("SPK02", "일단 박스 개봉이랑 외관 사진 찍는 정도는 저희도 할 수 있어요.", decision="D5")
say("SPK03", "그 정도만 덜어줘도 저희는 작동 확인이랑 판정에만 집중할 수 있어서 좀 나을 것 같아요.",
    decision="D5")
say("SPK01", "그거 말고 다른 부분도 도움받을 수 있을까요?", kind="open_question", decision="D5", rt=-2,
    note="지원 가능한 업무 범위를 더 넓힐 수 있는지 물음")
say("SPK03", "지금은 박스 뜯고 사진 찍는 데만도 시간이 꽤 걸리거든요.", decision="D5")
say("SPK03", "그것만 넘겨받아도 체감상 꽤 여유가 생길 것 같아요.", decision="D5")
say("SPK03", "한 대당 거의 삼 분씩은 잡아먹고 있었거든요.", decision="D5")
say("SPK03", "그거 백 대면 그것만 해도 다섯 시간이라 진짜 크긴 해요.", decision="D5")
say("SPK03", "근데 그것도 교육이 일단 좀 필요한데 지금 그럴 시간이 있을지 모르겠어요.",
    kind="concern", decision="D5", rt=-3, note="지원 인력 교육 시간 확보의 어려움을 지적함")
say("SPK02", "음 교육은 저희가 다 같이 점심시간에 잠깐 받아도 될 것 같은데요, 오래 안 걸릴 것 같고요.", decision="D5")
say("SPK02", "몇 명 정도 필요하신지만 말씀해 주시면 저희 쪽에서 사람은 맞춰볼게요.", decision="D5")
say("SPK01", "그럼 개봉이랑 사진 촬영은 입고팀이 지원하고, 검수팀은 작동 확인에 집중하는 방향으로 정리할게요.",
    kind="decision", decision="D5", settles="1",
    note="인력 부족 반발 끝에 업무 일부를 입고팀이 지원하는 방식으로 절충", label="d5_settle")
say("SPK02", "그럼 교육은 제가 점심시간에 받으러 갈게요.",
    kind="ambiguous", decision="D5", rt=-1, note="위임, 구체적 일정 없이 교육을 막연히 받겠다고 함")
say("SPK03", "네 그럼 저는 짧게 교육 자료만 하나 만들어둘게요.",
    kind="commitment", decision="D5", rt=-1, note="본인 계획으로 교육 자료 제작을 맡음, 기한 없음")
say("SPK01", "네 감사해요, 그럼 그렇게 준비해주세요.")
say("SPK02", "몇 명 정도 보내드리면 될지는 내일 오전까지 말씀드릴게요.", decision="D5")
say("SPK01", "그럼 이번 주부터 바로 시작해보는 걸로 하죠.")
say("SPK03", "네.")
say("SPK02", "네 알겠습니다.")
say("SPK01", "혹시 해보고 안 되겠다 싶으면 그때 다시 얘기해주세요.")
say("SPK03", "네 일단 이 주 정도 해보고 말씀드릴게요.")
say("SPK01", "네 그럼 이 주 뒤에 다시 한번 점검해보죠.")
say("SPK03", "네.")
say("SPK02", "저희도 그때까지 사람 좀 더 익숙해지게 해볼게요.")

# --- brief aside: extended warranty idea, a peer proposal nobody takes up ------
say("SPK04", "아 이건 그냥 제 생각인데요, 연장보증 같은 걸 옵션으로 팔면 어떨까요?")
say("SPK04", "요즘 리퍼브 제품 보증 관련 문의가 좀 늘어난 것 같아서 그냥 말씀드려봐요.")
say("SPK04", "다른 리퍼브 업체들도 요즘 그런 상품을 많이 내놓고 있더라고요.")
say("SPK04", "가격도 그렇게 비싸지 않아서 고객분들이 꽤 찾으시는 것 같더라고요.")
say("SPK02", "그거 나쁘지 않은 생각인데 지금 당장 검토할 사람이 없긴 하죠.")
say("SPK01", "음 그건 나중에 좀 더 얘기해보죠. 오늘은 일단 넘어가고요.")
say("SPK05", "이번 달 보증 관련 문의만 대충 스무 건 정도는 됐던 것 같아요.")
say("SPK05", "다들 리퍼브라서 더 걱정되신다고 많이들 물어보시더라고요.")
say("SPK01", "그 정도면 확실히 수요가 있긴 하네요.")
say("SPK04", "그렇죠, 그래서 한번 말씀드려본 거예요.")
say("SPK05", "저도 있으면 응대할 때 좀 더 편할 것 같긴 해요.")

# --- closing ---------------------------------------------------------------------
say("SPK01", "자 그러면 오늘은 여기까지 하고 정리만 한 번 하고 끊을게요.")
say("SPK01", "매입은 최대 매입처 단가 조정으로 가고, 검수 기준은 데이터 더 보고 다시 보고요.")
say("SPK01", "반품 처리는 개발팀 답 기다리는 거고, 불만 응대는 비용 비교해서 부분 환불 검토합니다.")
say("SPK01", "검수 인력은 입고팀이 개봉이랑 사진 촬영 지원하는 걸로 갑니다.")
say("SPK04", "택배 파손 건은 결과 나오면 제가 바로 공유드릴게요.",
    kind="commitment", rt=-4, note="상기, 앞서 나온 택배사 클레임 건을 다시 확인함")
say("SPK01", "네 그렇게 해주세요. 다음 회의는 다음 주 화요일 같은 시간에 하겠습니다.")
say("SPK04", "그때까지 매입 단가 조율 결과 정리해서 미리 공유드릴게요.")
say("SPK02", "저도 그때까지 매입처 쪽 연락 돌린 결과 정리해둘게요.")
say("SPK03", "저는 반품 원인 데이터 정리해서 올려두겠습니다.")
say("SPK03", "그리고 교육 자료도 그 전까지 다 만들어둘게요.")
say("SPK05", "저도 오늘 나온 것들 정리해서 CS 쪽에 공유해두겠습니다.",
    kind="commitment", note="본인 계획으로 CS팀 공유를 맡음, 기한 없음")
say("SPK01", "네 다들 고생하셨어요.")
say("SPK02", "고생하셨습니다.", note="사담")
say("SPK03", "다음에 뵐게요.", note="사담")

# --- generated columns -----------------------------------------------------------
LAST_START = 1780.0
FIRST_START = 6.0


def build_starts() -> list[float]:
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
        "statement": "신규 매입처 확보 대신, 물량이 가장 큰 기존 매입처의 단가만 올려 확보량을 늘리기로 한다.",
        "owner": "SPK04",
        "due": "이번 주 안(매입처 협상 착수 기준)",
        "due_as_said": "이번 주 안으로",
        "evidence_rows": ("d1_settle", "d1_owner", "d1_due"),
        "note": "신규 매입처 확보가 검수 기준 미검증 문제로 두 번째로 무산된 뒤, 기존 최대 매입처의 단가 조정으로 절충됨",
    },
    {
        "decision_id": "D2",
        "settles_row": "d2_settle",
        "statement": "검수 시간을 20분으로 늘리자는 팀장 제안에 아무도 명확히 답하지 않은 채, 반품 원인 데이터를 더 모은 뒤 다시 논의하기로 한다.",
        "owner": "SPK03",
        "due": "",
        "due_as_said": "",
        "evidence_rows": ("d2_proposal", "d2_settle"),
        "note": "배송 중 접촉 불량이 검수 시간 연장만으로는 잡히지 않을 수 있다는 우려가 오간 채 데이터 보완으로 유보됨",
    },
    {
        "decision_id": "D3",
        "settles_row": "d3_settle",
        "statement": "반품 처리 자동화는 개발팀 일정이 확정되지 않아 이번 주에는 정하지 않고 답변이 오면 다시 논의한다.",
        "owner": "",
        "due": "개발팀 답변 이후",
        "due_as_said": "개발팀 답 오면 다시",
        "evidence_rows": ("d3_settle", "d3_request"),
        "note": "자동화 요청은 이미 넣었으나 개발 일정이 꽉 차 있어 보류됨",
    },
    {
        "decision_id": "D4",
        "settles_row": "d4_settle",
        "statement": "소음 불만 재발송 요청은 재발송 비용이 부분 환불 금액보다 클 경우 부분 환불을 먼저 제안하는 방식으로 대응한다.",
        "owner": "SPK04",
        "due": "이번 주 안(기준표 작성 기준)",
        "due_as_said": "이번 주에",
        "evidence_rows": ("d4_settle", "d4_owner"),
        "note": "사전 고지만으로는 체감 불만을 막기 어렵다는 우려를 거쳐 비용 비교 기준의 조건부 대응으로 확정됨",
    },
    {
        "decision_id": "D5",
        "settles_row": "d5_settle",
        "statement": "검수팀 인력 부족은 입고팀이 박스 개봉과 외관 사진 촬영을 지원하고, 검수팀은 작동 확인과 판정에 집중하는 방식으로 절충한다.",
        "owner": "SPK02",
        "due": "",
        "due_as_said": "",
        "evidence_rows": ("d5_thrown", "d5_settle"),
        "note": "검수팀에 통째로 떠넘겨졌다가 인력 부족 반발을 거쳐 입고팀 일부 업무 지원으로 절충되어 확정됨",
    },
]


def main() -> None:
    starts = build_starts()
    c_records, a_records = [], []
    for index, row in enumerate(rows):
        number = index + 1
        responds_to = str(number + row["rt"]) if row["rt"] is not None else ""
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
