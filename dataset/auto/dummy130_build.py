"""Build DUMMY_130 -- an invented EV charging station operations platform meeting, training data.

Same generator shape as dummy121-129_build.py. Writes DUMMY_130.{A,C,D}.csv and
DUMMY_130.speakers.json into dataset/team_dummy/.

Everything invented: company, people, numbers.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "team_dummy"
MEETING = "DUMMY_130"

ROLE = {
    "SPK01": "PM",
    "SPK02": "Field",
    "SPK03": "Maintenance",
    "SPK04": "Settlement",
    "SPK05": "CS",
}

SPEAKERS = {
    "meeting": MEETING,
    "title": "차지온 충전소 운영팀 격주 점검 회의",
    "type": "team",
    "position_order": ["사원", "주임", "대리", "과장", "차장", "부장", "이사", "대표"],
    "speakers": [
        {"speaker": "SPK01", "name": "표윤슬", "team": "차지온 운영팀", "job": "PM",
         "position": "과장", "title": "팀장"},
        {"speaker": "SPK02", "name": "가온율", "team": "차지온 운영팀", "job": "Field",
         "position": "대리", "title": ""},
        {"speaker": "SPK03", "name": "겸시온", "team": "차지온 운영팀", "job": "Maintenance",
         "position": "주임", "title": ""},
        {"speaker": "SPK04", "name": "우다림", "team": "차지온 운영팀", "job": "Settlement",
         "position": "대리", "title": ""},
        {"speaker": "SPK05", "name": "라은채", "team": "차지온 운영팀", "job": "CS",
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
say("SPK05", "음 시작 전에 하나만 짚고 갈게요, 어젯밤에 컴플레인이 하나 크게 들어왔어요.")
say("SPK05", "어 협력 정비업체가 출동 시간보다 한 시간 늦게 도착해서 고객님이 많이 화가 나셨더라고요.")
say("SPK05", "음 다른 현장이 밀려서 그랬다고는 하는데 사전 안내가 전혀 없었던 게 문제였어요.")
say("SPK03", "어 그 업체는 저도 알아요, 예전에도 지연 신고가 한 번 있었던 곳이에요.")
say("SPK01", "음 그 건은 이따 정비 얘기할 때 다시 짚고 넘어갈게요, 오늘 네 가지만 보고 마칠게요.")
say("SPK01", "음 고장 접수 확정 지연 문제랑 정기 구독 프로모션, 충전 오류 자동 재시도, 그리고 커넥터 파손 클레임이요.")
say("SPK01", "일단 그 순서로 가려고 하는데 혹시 먼저 봐야 할 급한 게 있으면 말씀해 주세요.")
say("SPK01", "그리고 오늘도 회의록은 따로 안 쓰고 정해진 것만 이따 채널에 정리해서 올릴게요.",
    kind="commitment", note="본인이 회의록 대신 정리를 맡겠다고 함")
say("SPK01", "그냥 저번처럼 다 받아 적다가 뭐가 결정됐는지 흐려지느니 그게 낫겠더라고요.")
say("SPK02", "일단 네 저도 그 방식이 편해요, 저번 회의록은 다시 봐도 헷갈리더라고요.")
say("SPK01", "음 그럼 율 씨가 준비한 고장 접수 확정 현황부터 볼까요.",
    kind="open_question", note="논의 순서를 정하며 데이터 공유를 요청함")
say("SPK02", "음 네 이번 주 목표는 접수 후 한 시간 안에 출동 확정 짓는 건데요,")
say("SPK02", "어 실제로는 평균 세 시간 정도 걸리고 있어요, 목표보다 세 배 넘게 걸리는 거예요.")
say("SPK02", "그냥 지역별로 나눠보면 도심보다 외곽 쪽이 더 심각한 상황이고요.")
say("SPK02", "음 도심은 그래도 두 시간 안팎으로는 맞춰지고 있어요.")
say("SPK02", "어 외곽은 지금 다섯 시간 넘게 걸리는 건도 꽤 있어서 상황이 더 안 좋고요.")
say("SPK01", "음 그 차이는 어디서 나는 거예요?", kind="open_question", rt=-1,
    note="도심과 외곽 출동 확정 시간 차이의 원인을 물음")
say("SPK02", "일단 외곽은 저희 쪽 협력 정비 기사님 중에 출동 가능한 분이 적어서 그런 것 같아요.")
say("SPK01", "어 그렇게 많이 차이가 나요?")
say("SPK02", "음 네 도심은 출동 가능한 기사님이 열다섯 명인데 외곽은 세 명밖에 안 돼요.")
say("SPK01", "아 그 정도면 확실히 차이가 날 수밖에 없겠네요.")
say("SPK02", "음 네 그래서 외곽 쪽이 유독 더 늦어지는 거예요.")
say("SPK02", "그냥 기사님 모집도 그래서 외곽 쪽부터 급한 거고요.")
say("SPK04", "일단 저도 짐작은 했는데 숫자로 보니까 확실히 심각하네요.")

# --- D1: dispatch confirmation delay, false agreement inside --------------------------
say("SPK02", "그리고 이번에 확정 지연 관련해서 문제가 좀 커졌어요.", decision="D1")
say("SPK02", "음 작년 이맘때는 평균 확정 시간이 두 시간 정도였거든요.", decision="D1")
say("SPK02", "아 두 시간이 아니라 두 시간 반이네요. 작년 자료랑 재작년 자료를 헷갈렸어요.", decision="D1")
say("SPK02", "음 어쨌든 그때보다 확실히 더 늦어진 건 맞아요.", decision="D1")
say("SPK02", "어 요즘 외곽 고장 문의가 늘었는데 기사님 수는 그대로라서 그런 것 같아요.", decision="D1")
say("SPK02", "음 특히 그중에 외곽 고장 두 건이 확정까지 여섯 시간 넘게 걸려서 계약 해지까지 나갔어요.", decision="D1")
say("SPK02", "음 그게 이번 달 전체 해지의 한 이십 퍼센트나 차지하는 거라 타격이 좀 크네요.", decision="D1")
say("SPK02", "어 이 상태로 가면 다음 달에는 해지가 더 늘어날 수도 있을 것 같고요.", decision="D1")
say("SPK04", "어 그건 저도 봤어요, 그 두 건 정산 데이터가 유독 안 좋더라고요.", decision="D1")
say("SPK04", "음 저희 말고 다른 충전소 운영 앱에도 비슷한 후기가 올라와 있던데요.", decision="D1")
say("SPK04", "어 저번에 고객센터 통계 볼 때도 그런 얘기가 있긴 했었어요.", decision="D1")
say("SPK04", "어 저희가 그때 좀 더 서둘러서 봤어야 했나 싶기도 하고요, 아쉽네요.", decision="D1")
say("SPK03", "음 그럼 정비 인력은 지금 접수 건수 기준으로 맞춰놓은 거라 남는 여유 있는 거 아니에요?",
    kind="open_question", decision="D1", rt=-1, note="확정 지연이 유휴 정비 인력으로 이어지는지 물음")
say("SPK03", "일단 지금 저희 셋이서 하루 스무 건은 점검할 수 있는 체제로 짜놨었거든요.", decision="D1")
say("SPK01", "음 그 얘기는 정비 쪽에서 이따 다시 할게요, 일단 확정 지연부터 정리하고요.")
say("SPK01", "어 그럼 기사님 수를 그대로 두면 외곽 고객 이탈이 계속 늘어난다는 얘기인데요.", decision="D1")
say("SPK01", "음 이번 주 안에 외곽 기사님을 좀 더 뚫어야 될 것 같은데 다들 어떻게 보세요?", decision="D1")
say("SPK02", "음 저는 일단 지금 기사님은 그대로 두고 외곽 건 출동비만 좀 올려주는 게 낫지 않을까 싶어요.",
    decision="D1")
say("SPK02", "음 근데 새 기사님을 뚫는 건 검증하는 데만도 시간이 꽤 걸리거든요.", decision="D1")
say("SPK02", "음 지금 당장 물량이 급한데 검증 기간까지 기다릴 여유는 없을 것 같아서요.", decision="D1")
say("SPK04", "음 근데 출동비를 올리면 그만큼 저희 마진이 줄어드는 거라서요.", kind="concern",
    decision="D1", rt=-2, note="출동비 인상이 마진 축소로 이어진다는 우려")
say("SPK04", "음 지금도 마진이 그렇게 넉넉한 편은 아니거든요.", decision="D1")
say("SPK04", "어 구독료를 올리지 않는 이상 출동비 인상분은 그대로 손해예요.", decision="D1")
say("SPK01", "그럼 아예 외곽 전담 신규 정비업체 채널을 새로 여는 쪽으로 가죠! 그게 더 낫겠네요.",
    decision="D1", note="번복, 합의된 것처럼 보였다가 다음 턴에서 뒤집힘", label="d1_false")
say("SPK02", "음 네 그게 나을 것 같긴 해요.", decision="D1")
say("SPK03", "아 잠깐만요, 새 채널은 저희 정비 자격 검증 기준에 맞는지 먼저 확인해야 되는데요.",
    kind="concern", decision="D1", rt=-2, note="신규 정비업체 채널이 자격 검증 기준을 충족하는지 사전 확인이 필요함을 지적")
say("SPK01", "음 그때 그 채널은 어떻게 걸러낸 거였죠?", kind="open_question", decision="D1", rt=-1,
    note="과거 불량 채널을 어떻게 발견했는지 물음")
say("SPK03", "저번에 급하게 뚫었던 채널은 결국 수리 불량 신고가 너무 많아서 두 달 만에 끊었잖아요.", decision="D1")
say("SPK03", "어 그때 배상이랑 재수리 비용이 더 나가서 오히려 손해였고요.", decision="D1")
say("SPK03", "음 그 채널은 자격 검증부터가 저희 기준이랑 많이 달랐던 걸로 기억해요.", decision="D1")
say("SPK03", "음 그러니까 새 채널을 뚫더라도 최소 한두 달은 검증 기간을 잡아야 할 것 같아요.", decision="D1")
say("SPK03", "음 그 기간 동안은 오히려 정비 인력이 그쪽에 더 붙어야 되기도 하고요.", decision="D1")
say("SPK01", "아 맞다, 그때 그 일이 있었죠.")
say("SPK01", "음 그럼 새 채널은 검증 기간이 필요하니까 이번 달에는 못 쓰겠네요.", decision="D1")
say("SPK04", "어 그러면 결국 남은 건 외곽 건 출동비 조정밖에 없는 것 같은데요.", decision="D1")
say("SPK04", "어 근데 그것도 사실 임시방편이라는 느낌은 있어서 좀 걱정이긴 해요.",
    kind="concern", decision="D1", rt=-1, note="출동비 조정이 근본 해결책은 아니라는 우려")
say("SPK02", "음 출동비를 전체로 다 올리지 말고 외곽 건만 먼저 올려보면 어때요?",
    decision="D1")
say("SPK02", "어 외곽이 원래 제일 급했으니까 거기만 잡아도 효과가 꽤 있을 것 같아요.", decision="D1")
say("SPK04", "음 그 정도면 전체 마진 하락 폭이 한 오 퍼센트 정도라서 감당은 충분히 될 것 같아요.", decision="D1")
say("SPK04", "음 도심 쪽은 지금 출동비로도 그럭저럭 기사님을 유지해주고 있어서 괜찮을 것 같고요.", decision="D1")
say("SPK01", "그럼 도심은 그대로 가고 외곽 출동비만 조정하는 방향이네요.")
say("SPK02", "음 네 맞아요.")
say("SPK01", "그럼 외곽 건 출동비만 올리고 나머지는 그대로 두는 걸로 정리할게요.",
    kind="decision", decision="D1", settles="1",
    note="신규 정비업체 채널 검증 문제로 무산된 뒤 외곽 건 출동비 조정으로 절충", label="d1_settle")
say("SPK02", "일단 그 출동비 기준은 제가 이번 주 안으로 정리해서 공유드릴게요.",
    kind="commitment", decision="D1", rt=-1, note="본인이 새 출동비 기준 작성을 맡음, 기한 명시",
    label="d1_owner")
say("SPK04", "저도 그거 정산 시스템 반영은 필요하면 같이 봐드릴 수는 있어요.",
    kind="ambiguous", decision="D1", rt=-1, note="구체적 계획 없이 필요하면 돕겠다는 약한 응답")
say("SPK02", "음 얼마나 올려야 지원이 늘지는 정비업체 쪽이랑도 얘기해봐야 알 것 같아요.", decision="D1",
    label="d1_due")
say("SPK02", "음 너무 많이 올리면 저희 쪽이 손해니까 선을 잘 잡아야 할 것 같아요.", decision="D1")
say("SPK02", "지난달 조정 폭보다 사흘 앞당겨서 이번 주 안에 먼저 제안해보려고요.", decision="D1")
say("SPK01", "그럼 그 결과 보고 다음 달에 확정 목표를 다시 잡죠.")
say("SPK03", "네.")
say("SPK03", "저는 그동안 외곽 정비 배치라도 한번 다시 짜볼게요.",
    kind="commitment", decision="D1", note="본인 계획으로 정비 배치 재검토를 시도함, 기한 없음")
say("SPK03", "혹시 임시 협력업체도 늘릴 수 있는지 이번 주에 알아볼게요.", decision="D1")
say("SPK04", "음.")
say("SPK03", "넵.")

# --- side talk 1 -------------------------------------------------------------------
say("SPK05", "그러고 보니 건물 옆에 새로 생긴 그 편의점 가보셨어요? 물건이 많더라고요.", note="사담")
say("SPK02", "저 아직 못 가봤어요. 가격대는 어때요?", note="사담")
say("SPK05", "괜찮았어요, 근데 생각보다 좀 비싸더라고요.", note="사담")
say("SPK05", "기본 도시락이 육천 원 넘던데요.", note="사담")
say("SPK03", "저도 한번 가봐야겠네요, 요즘 마땅한 데가 없어서 좀 아쉬웠거든요.", note="사담")
say("SPK03", "자주 가던 데가 얼마 전에 갑자기 문을 닫아서요.", note="사담")
say("SPK04", "요즘 임대료가 워낙 비싸다 보니까 다들 버티기 힘든가 봐요.", note="사담")
say("SPK02", "맞아요, 저희 쪽 상가도 그런 얘기 많이 들려요.", note="사담")
say("SPK02", "예전엔 이 정도는 아니었던 것 같은데 요즘 부쩍 심해진 것 같아요.", note="사담")
say("SPK03", "그러게요.", note="사담")
say("SPK01", "그 얘기는 이따 마저 하고요, 정기 구독 프로모션 쪽으로 넘어갈게요.")

# --- D2: subscription promotion participation, lead proposal unanswered ---------------------
say("SPK01", "지난주에 정기 구독 프로모션 관련해서 참여율 요청이 왔었잖아요. 그것부터 볼게요.",
    decision="D2")
say("SPK05", "네 그중에 한 건은 참여율이 너무 낮다고 페널티 얘기까지 나왔어요.", decision="D2")
say("SPK05", "저희 충전소 중에 절반 정도가 아예 프로모션에 안 들어가 있더라고요.", decision="D2")
say("SPK05", "노출 순위가 밀려서 신규 유입에도 영향이 있다고 하시면서 다들 걱정을 많이 하세요.", decision="D2")
say("SPK05", "그것도 충전소마다 사정이 달라서 생각보다 관리가 복잡해요.", decision="D2")
say("SPK05", "지점장님들도 처음엔 그냥 넘어가려다가 이용량 줄어드니까 그제야 신경 쓰시더라고요.", decision="D2")
say("SPK05", "다른 한 건은 할인율이 너무 크다고 하셨는데 그건 아직 협의 중이에요.", decision="D2")
say("SPK05", "지점장님이 캡처까지 보내주셨는데 저희가 봐도 할인율이 좀 크긴 하더라고요.", decision="D2")
say("SPK01", "지금 참여 승인 기준이 충전소 규모 확인해서 결정하는 게 전부인 거죠?", decision="D2")
say("SPK03", "네 근데 그 기준으로는 정비 처리 여력까지는 잘 안 잡혀요.", decision="D2")
say("SPK03", "그 충전소도 저희가 볼 때는 규모는 괜찮았거든요.", decision="D2")
say("SPK03", "기록 봐도 승인 기준 통과로 표시돼 있었고 저도 그때 직접 확인했었어요.", decision="D2")
say("SPK03", "그래서 이게 규모 문제인지 처리 여력 문제인지가 좀 헷갈려요.", decision="D2")
say("SPK03", "비슷한 사례가 더 있는지 한번 찾아봐야 할 것 같고요.", decision="D2")
say("SPK03", "근데 그게 처리 여력까지 다 확인하면 승인이 너무 오래 걸릴 수도 있어요.", decision="D2")
say("SPK01", "그러면 제가 보기엔 참여 승인 기준에 정비 처리 여력 점수도 같이 넣는 게 맞을 것 같은데요.",
    decision="D2", note="상급자 제안, 아무도 명확히 답하지 않고 데이터 보완 후 재논의로 넘어감", label="d2_proposal")
say("SPK02", "그렇게 하면 승인 절차가 더 오래 걸리는 거 아닌가요?",
    kind="open_question", decision="D2", rt=-1, note="승인 기준 추가가 처리 속도에 미치는 영향을 물음")
say("SPK02", "지금도 승인이 빠듯한데 항목을 늘리면 감당이 안 될 것 같아서요.", decision="D2")
say("SPK01", "그건 이따 인력 얘기할 때 같이 볼게요, 지금은 기준만이요.")
say("SPK01", "일단 뭐가 맞는 방향인지부터 정하고 인력은 그다음에 맞춰야죠.")
say("SPK03", "근데 기준을 늘려도 그 처리 여력 같은 건 충전소마다 달라서 꼭 잡힌다는 보장은 없어요.",
    kind="concern", decision="D2", rt=-4, note="승인 기준 추가만으로는 충전소별 처리 여력 차이를 못 잡을 수 있다는 우려")
say("SPK03", "저희가 볼 때는 그냥 규모만 보고 판단하는 거라서요.", decision="D2")
say("SPK04", "그럼 기준을 늘리는 것보다 정산 데이터로 사후 모니터링을 한 번 더 하는 게 낫지 않을까요?",
    decision="D2")
say("SPK04", "프로모션 끝난 뒤에 실제 매칭 지연이 어땠는지 보면 그게 더 정확할 것 같아요.", decision="D2")
say("SPK04", "저희가 예전에 그렇게 한 적이 있었는데 그때는 문제 적발률이 꽤 높았거든요.", decision="D2")
say("SPK04", "그때 기억으로는 한 팔 퍼센트 정도는 그 단계에서 추가로 걸러졌었어요.", decision="D2")
say("SPK04", "그때 왜 그만뒀는지는 저도 정확히는 기억이 안 나네요.", decision="D2")
say("SPK02", "근데 그러면 정산팀에서 한 번 더 봐야 되는 건데 그건 인력이 또 필요해요.",
    kind="concern", decision="D2", rt=-2, note="사후 모니터링 추가가 별도 인력을 필요로 한다는 우려")
say("SPK01", "음 그것도 그렇네요. 이건 조금 더 생각해봐야 할 것 같아요. 데이터를 좀 더 모으고 다시 봅니다.",
    kind="decision", decision="D2", settles="1",
    note="상급자 제안, 아무도 명확히 답하지 않고 데이터 보완 후 재논의로 넘어감", label="d2_settle")
say("SPK03", "그럼 제가 이번 주 지연 건들 중에 원인 특정 가능한 것부터 좀 정리해볼게요.",
    kind="commitment", decision="D2", rt=-1, note="본인 계획으로 지연 원인 데이터 정리를 맡음, 기한 없음")
say("SPK03", "그게 있어야 기준을 늘려야 하는지 모니터링을 넣어야 하는지 판단이 설 것 같아서요.", decision="D2")
say("SPK01", "네.")
say("SPK02", "그럼 그것도 저희 쪽 자료랑 같이 맞춰볼게요.",
    kind="ambiguous", decision="D2", rt=-2, note="구체적 계획 없이 자료를 맞춰보겠다는 약한 응답")
say("SPK01", "그럼 다음 주에 데이터 보고 다시 얘기하죠.")
say("SPK03", "네 알겠습니다.")

# --- D3: charging-error auto-retry automation, held over ------------------------------
say("SPK01", "그다음 충전 오류 자동 재시도 얘기인데요, 지금 오류 접수에 평균 며칠 걸리는 거예요?")
say("SPK03", "지금 평균 나흘이요, 근데 이용량이 늘어나면 그게 더 늘어날 것 같아서 걱정이에요.", decision="D3")
say("SPK03", "지금도 접수 받고 실제 원인 확인까지 가는 데 손이 많이 가거든요.", decision="D3")
say("SPK03", "접수는 제가 받고 원인 확인은 정비팀에 요청하고 환불 처리는 또 정산팀이라서요.", decision="D3")
say("SPK03", "그 사이에 왔다 갔다 하는 메일이랑 전화만 해도 꽤 되더라고요.", decision="D3")
say("SPK03", "그러다 보니까 고객님도 언제 처리되냐고 그 중간에 또 문의를 주시고요.", decision="D3")
say("SPK02", "그거 저희 시스템에서 자동으로 처리하는 부분은 없는 거예요?",
    kind="open_question", decision="D3", rt=-2, note="충전 오류 자동 재시도 가능 여부를 물음")
say("SPK03", "일부는 되는데 원인 확인 요청이 수동이라 거기서 늘 걸려요.", decision="D3")
say("SPK04", "그거 시스템 쪽에 자동화 요청은 넣어보신 거예요?",
    kind="open_question", decision="D3", rt=-1, note="자동화 개발 요청 여부를 확인함")
say("SPK03", "넣긴 넣었는데 개발팀 쪽 일정이 꽉 차 있어서 정확히 언제 될지는 모른다고 했어요.", decision="D3")
say("SPK03", "저번 달에 넣었는데 아직 답도 못 받은 상태예요.", decision="D3", label="d3_request")
say("SPK03", "다른 팀도 요청이 많이 밀려 있다고 하더라고요.", decision="D3")
say("SPK01", "그 순서는 누가 정하는 거예요?", kind="open_question", decision="D3", rt=-1,
    note="개발팀 요청 처리 순서 결정 주체를 물음")
say("SPK03", "저희만 급한 게 아니라서 순서를 당겨달라고 하기도 좀 애매하고요.", decision="D3")
say("SPK03", "그래도 계속 얘기는 해봐야 할 것 같아요.", decision="D3")
say("SPK02", "아 그게 아니고, 그냥 무작정 기다리기만 하면 접수가 계속 쌓일 수도 있어서 걱정이에요.",
    kind="concern", decision="D3", rt=-1, note="개발팀 응답을 기다리기만 하면 접수가 계속 쌓일 수 있다는 우려")
say("SPK01", "그럼 이건 오늘 뭘 정할 수 있는 상황은 아니네요.")
say("SPK01", "일단 오늘은 정하지 말고 개발팀 답이 오면 다시 봅니다.",
    kind="decision", decision="D3", settles="1",
    note="개발 일정 미확정으로 이번 주는 보류, 답변 오면 재논의", label="d3_settle")
say("SPK03", "그동안은 그럼 저 혼자라도 좀 더 빠르게 확인해보도록 할게요.",
    kind="commitment", decision="D3", rt=-1, note="본인 계획으로 임시 처리 속도 개선을 맡음, 기한 없음")
say("SPK03", "원인 확인 요청하는 메일이라도 좀 더 자주 보내보려고요.", decision="D3")
say("SPK01", "네 부탁드려요.")
say("SPK02", "저도 정비팀 쪽에 얘기해서 확인 좀 더 빨리 해달라고 해볼게요.",
    kind="ambiguous", decision="D3", rt=-2, note="구체적 계획 없이 협조를 요청해보겠다는 약한 응답")
say("SPK01", "감사해요, 그거라도 좀 나아지면 좋겠네요.")
say("SPK05", "네 저도 그러길 바라요.")

# --- side talk 2 ---------------------------------------------------------------------
say("SPK02", "그리고 사무실 소방 점검 이번 달까지 다시 해야 되는 거 아세요? 저번에 공지 왔었는데요.", note="사담")
say("SPK04", "아 맞다 까먹고 있었어요. 오늘 안에 확인해야겠네요.", note="사담")
say("SPK04", "안 하면 다음 달부터 과태료 나온다고 했었죠 아마.", note="사담")
say("SPK03", "저도 확인해야 되는데 계속 미루고 있었어요.", note="사담")
say("SPK03", "어디서 신청하는 건지도 가물가물하네요.", note="사담")
say("SPK02", "저는 어제 해놨어요, 별로 안 오래 걸려요.", note="사담")
say("SPK02", "관리사무소 페이지에서 하시면 돼요, 오 분도 안 걸려요.", note="사담")
say("SPK05", "저도 해야겠네요, 알려주셔서 감사해요.", note="사담")
say("SPK04", "저 방금 등록했어요, 진짜 오 분도 안 걸리네요.", note="사담")
say("SPK01", "그건 이따 각자 하시고요, 커넥터 파손 클레임으로 넘어갈게요.")

# --- D4: connector damage claim, conditional -----------------------------------------
say("SPK01", "커넥터 파손 클레임 건인데, 최근 들어 교체 요청이 좀 늘었다고 들었어요.", decision="D4")
say("SPK05", "네 세 개 충전소에서 특히 많아요, 근데 저희 기준으로는 정상 범위거든요.",
    kind="concern", decision="D4", rt=-1, note="정상 판정 커넥터에 대한 파손 클레임이 늘고 있다는 문제 제기")
say("SPK05", "저희가 내구성 기준을 표준으로 맞추긴 하는데 차종마다 커넥터 결합 방식이 달라서 그런가 봐요.", decision="D4")
say("SPK05", "특히 급속 충전 이용이 많은 충전소일수록 그런 클레임이 더 많이 들어와요.", decision="D4")
say("SPK05", "겨울철에 충전하시는 분들은 특히 더 예민하게 느끼시는 것 같고요.", decision="D4")
say("SPK05", "어 전화로 응대하다 보면 같은 얘기를 계속 반복해서 드려야 해서 저도 좀 지치더라고요.", decision="D4")
say("SPK03", "그건 아무래도 커넥터 자체가 소모품이라 그럴 수밖에 없긴 해요.", decision="D4")
say("SPK03", "다 전수 교체로 돌릴 수도 없는 노릇이고요, 예산 한계가 있어요.", decision="D4")
say("SPK03", "전수 강화형 커넥터로 바꾸면 파손은 줄겠지만 교체 비용이 꽤 커요.", decision="D4")
say("SPK03", "어 그거 다 도입하면 이제 이번 분기 설비 예산이 아예 안 남을 수도 있어서 쉽게 결정하기 어려워요.", decision="D4")
say("SPK03", "그래서 저는 웬만하면 그 예산은 안 건드리는 쪽으로 가고 싶어요.", decision="D4")
say("SPK04", "근데 교체 요청 비율이 최근 두 달 사이에 두 배 가까이 늘긴 했어요.", decision="D4")
say("SPK04", "음 그중에 절반은 급속 충전소 관련이고 나머지는 뭐 기타 사유들이에요.", decision="D4")
say("SPK04", "교체 한 번에 드는 출장 비용도 무시 못 할 수준이라 이게 계속 쌓이면 문제예요.", decision="D4")
say("SPK01", "그럼 충전 화면에 커넥터 내구성 한계를 미리 명시하는 건 어때요?", kind="open_question",
    decision="D4", rt=-4, note="커넥터 내구성 사전 고지 방안을 제안하며 의견을 물음")
say("SPK02", "그거 좋은 것 같아요, 근데 문구를 누가 어떻게 쓸지가 문제긴 하네요.", decision="D4")
say("SPK02", "너무 부정적으로 쓰면 그것대로 이용을 안 하실 것 같고 애매하네요.", decision="D4")
say("SPK02", "문구는 그럼 나중에 법무 쪽 자문도 좀 받아보는 게 좋을 것 같아요.", decision="D4")
say("SPK05", "저는 근데 그거 명시해도 결국 파손 겪어보시고 나면 똑같이 불만 들어올 것 같아요.",
    kind="concern", decision="D4", rt=-2, note="사전 고지만으로는 체감 불만을 막기 어렵다는 우려")
say("SPK05", "글로 미리 설명드려도 실제로 겪으시는 거랑은 다르다고 하시는 분들이 많거든요.", decision="D4")
say("SPK05", "그래서 저는 사전 고지보다는 다른 방법을 좀 더 찾아봐야 할 것 같아요.", decision="D4")
say("SPK05", "고지는 하되 그거 하나로 다 해결될 거라고는 기대 안 하는 게 맞을 것 같고요.", decision="D4")
say("SPK01", "그럼 화면에 명시하는 거랑 별개로, 전수 강화형 교체 대신 급속 충전소만 먼저 시범 적용하는 건 어때요?",
    decision="D4")
say("SPK01", "전수 교체 다 돌리면 비용이 또 나가는데 시범 적용이 오히려 쌀 수도 있잖아요.", decision="D4")
say("SPK04", "그건 계산을 좀 해봐야 알겠는데, 금액에 따라서는 그게 나을 수도 있을 것 같아요.", decision="D4")
say("SPK04", "전수 강화형 교체 비용이 대략 사백만 원 정도니까 그거보다 적으면 시범 적용이 낫겠네요.", decision="D4")
say("SPK02", "아니 근데, 충전소별로 나누면 표가 너무 복잡해지는 거 아니에요?", kind="concern",
    decision="D4", rt=-1, note="충전소별 세분화가 표를 지나치게 복잡하게 만들 수 있다는 우려")
say("SPK04", "근데 충전소마다 이용 패턴이 다 달라서 표로 정리해야 할 것 같아요.", decision="D4")
say("SPK04", "급속이랑 완속이랑도 커넥터 마모 속도가 다르니까 그것도 따로 잡아야 하고요.", decision="D4")
say("SPK04", "근데 표로 정리해도 결국 담당자가 상황 봐가면서 판단해야 하는 부분은 남을 것 같아요.",
    kind="concern", decision="D4", rt=-1, note="기준표가 있어도 현장 판단 여지가 남는다는 우려")
say("SPK04", "이번 주까지 다 계산해서 표로 정리해서 올려둘게요.", decision="D4")
say("SPK01", "그럼 시범 적용 비용이 전수 교체 비용보다 크면 전수 교체를 먼저 진행하는 방향으로 정리할게요.",
    kind="decision", decision="D4", settles="1",
    note="조건부 결정, 비용 비교 결과에 따라 대응 방식이 갈림", label="d4_settle")
say("SPK04", "그 기준 금액은 제가 이번 주에 계산해서 표로 정리해볼게요.",
    kind="commitment", decision="D4", rt=-1, note="본인이 비용 비교 기준표 작성을 맡음, 기한 명시",
    label="d4_owner")
say("SPK05", "그거 나오면 저는 그거 보고 응대 스크립트에 반영할게요.",
    kind="commitment", decision="D4", rt=-1, note="본인 계획으로 응대 스크립트 반영을 맡음, 기한 없음")
say("SPK01", "좋아요, 그럼 그렇게 진행하죠.")
say("SPK02", "저도 법무 쪽에 문구 자문 건 한번 전달해볼게요.",
    kind="ambiguous", decision="D4", rt=-1,
    note="전달, 구체적 계획 없이 법무팀에 자문 요청을 전달만 하겠다는 약한 응답")

# --- side talk 3 ---------------------------------------------------------------------
say("SPK03", "아까 그 출동 지연 건, CS 쪽 답은 오늘 온대요?", note="사담")
say("SPK05", "확실친 않은데 내일까지는 준다고 했어요.", note="사담")
say("SPK05", "제가 오전에 한 번 더 물어봐서 재촉은 해뒀어요.", note="사담")
say("SPK05", "그쪽 담당자도 이번엔 좀 곤란한 눈치이긴 하더라고요.", note="사담")
say("SPK04", "저번에도 그렇게 말해놓고 이틀 더 걸렸었죠 아마.", note="사담")
say("SPK04", "그때도 결국 저희가 계속 물어봐야 겨우 답이 왔었잖아요.", note="사담")
say("SPK02", "그러게요, 이번엔 좀 빨리 왔으면 좋겠네요.", note="사담")
say("SPK03", "그 배상 값이 꽤 나가서 저도 좀 신경 쓰이네요.", note="사담")

# --- D5: maintenance staffing backlog, resistance before settling -------------------------
say("SPK01", "마지막으로 정비 인력 얘기를 좀 해야 할 것 같아요. 지금 상태가 어때요?")
say("SPK03", "지금 저희 셋이서 하루 스무 건씩 보고 있는데 다음 달 되면 그게 두 배는 될 것 같아요.",
    decision="D5")
say("SPK03", "지금도 사실 빠듯하게 맞추고 있는 상황이라 더 늘면 감당이 안 될 것 같아요.", decision="D5")
say("SPK03", "음 한 명이라도 아프거나 하면 그날은 아예 목표를 못 채워요.", decision="D5")
say("SPK03", "저번 주에 저 하루 연차 썼을 때도 그날 목표 못 채우고 다음 날로 밀렸었거든요.", decision="D5")
say("SPK01", "이건 뭐 정비팀에서 알아서 좀 조정해서 맞춰주셔야 할 것 같은데요.",
    decision="D5", label="d5_thrown")
say("SPK03", "저희끼리 조정한다고 되는 문제가 아니에요, 물리적으로 사람이 부족한 거라서요.",
    kind="concern", decision="D5", rt=-1, note="인력 부족은 조정이 아니라 충원이 필요한 문제라는 반대")
say("SPK03", "음 지금도 야근을 거의 매일 하고 있는 상황이라 이 이상은 진짜 무리예요.", decision="D5")
say("SPK03", "저번 주에도 다들 아홉 시 넘어서 퇴근했었잖아요.", decision="D5")
say("SPK03", "음 금요일엔 거의 열 시까지 있었던 것 같아요.", decision="D5")
say("SPK03", "어 이러다 누구 하나 그만둔다고 할까 봐 저도 좀 걱정이에요.", decision="D5")
say("SPK03", "채용 공고는 올려주셨다고 들었는데 지원자가 별로 없다고 하더라고요.", decision="D5")
say("SPK01", "네 저도 그건 알고 있어요, 조건을 좀 조정해야 하나 고민 중이에요.")
say("SPK02", "저희 쪽에서 접수 확인하는 인원 한두 명 정도는 잠깐 도와드릴 수 있을 것 같긴 한데요.",
    decision="D5")
say("SPK02", "근데 저희도 정비 경험이 있는 건 아니라서 간단한 것만 도와드릴 수 있어요.", decision="D5")
say("SPK02", "저희 쪽도 출동량이 늘어서 딱히 여유 인력이 있는 건 아니거든요.", decision="D5")
say("SPK02", "그래도 하루에 한두 시간 정도는 빼서 도와드릴 수 있을 것 같아요.", decision="D5")
say("SPK03", "간단한 거라면 어떤 거요?", kind="open_question", decision="D5", rt=-1,
    note="지원 가능한 업무 범위를 구체적으로 물음")
say("SPK02", "접수 확인이랑 기본 정보 입력 정도는 저희도 할 수 있어요.", decision="D5")
say("SPK01", "그거 말고 다른 부분도 도움받을 수 있을까요?", kind="open_question", decision="D5", rt=-2,
    note="지원 가능한 업무 범위를 더 넓힐 수 있는지 물음")
say("SPK03", "그 정도만 덜어줘도 저희는 실제 점검이랑 판정에만 집중할 수 있어서 좀 나을 것 같아요.",
    decision="D5")
say("SPK03", "지금은 접수 확인하고 입력하는 데만도 시간이 꽤 걸리거든요.", decision="D5")
say("SPK03", "그것만 넘겨받아도 체감상 꽤 여유가 생길 것 같아요.", decision="D5")
say("SPK03", "한 건당 거의 십오 분씩은 잡아먹고 있었거든요.", decision="D5")
say("SPK03", "그거 스무 건이면 그것만 해도 다섯 시간이라 진짜 크긴 해요.", decision="D5")
say("SPK03", "근데 그것도 교육이 좀 필요한데 지금 그럴 시간이 있을지 모르겠어요.",
    kind="concern", decision="D5", rt=-3, note="지원 인력 교육 시간 확보의 어려움을 지적함")
say("SPK02", "교육은 저희가 다 같이 점심시간에 잠깐 받아도 될 것 같은데요, 오래 안 걸릴 것 같고요.", decision="D5")
say("SPK02", "음 몇 명 정도 필요하신지만 말씀해 주시면 저희 쪽에서 사람은 맞춰볼게요.", decision="D5")
say("SPK01", "그럼 접수 확인이랑 입력은 현장팀이 지원하고, 정비팀은 실제 점검과 판정에 집중하는 방향으로 정리할게요.",
    kind="decision", decision="D5", settles="1",
    note="인력 부족 반발 끝에 업무 일부를 현장팀이 지원하는 방식으로 절충", label="d5_settle")
say("SPK02", "그럼 교육은 제가 점심시간에 받으러 갈게요.",
    kind="ambiguous", decision="D5", rt=-1, note="위임, 구체적 일정 없이 교육을 막연히 받겠다고 함")
say("SPK03", "그럼 저는 짧게 교육 자료만 하나 만들어둘게요.",
    kind="commitment", decision="D5", rt=-1, note="본인 계획으로 교육 자료 제작을 맡음, 기한 없음")
say("SPK01", "감사해요, 그럼 그렇게 준비해주세요.")
say("SPK02", "몇 명 정도 보내드리면 될지는 내일 오전까지 말씀드릴게요.", decision="D5")
say("SPK01", "그럼 이번 주부터 바로 시작해보죠.")
say("SPK03", "네.")
say("SPK02", "네 알겠습니다.")
say("SPK01", "해보고 안 되겠다 싶으면 그때 다시 얘기해주세요.")
say("SPK03", "네 일단 이 주 정도 해보고 말씀드릴게요.")
say("SPK01", "그럼 이 주 뒤에 다시 한번 점검해보죠.")
say("SPK03", "네.")
say("SPK02", "저희도 그때까지 사람 좀 더 익숙해지게 해볼게요.")

# --- brief aside: energy-resale idea, a peer proposal nobody takes up ----------
say("SPK04", "이건 그냥 제 생각인데요, 피크 시간대 잉여 전력을 되팔아보면 어떨까요?")
say("SPK04", "요즘 전력 재판매 관련 문의가 좀 늘어난 것 같아서 그냥 말씀드려봐요.")
say("SPK04", "다른 충전 플랫폼들도 요즘 그런 사업을 많이 검토하고 있더라고요.")
say("SPK04", "수익성도 나쁘지 않아서 파트너사들이 꽤 관심 있어 하시는 것 같더라고요.")
say("SPK02", "그거 나쁘지 않은 생각인데 지금 당장 검토할 사람이 없긴 하죠.")
say("SPK01", "그건 나중에 좀 더 얘기해보죠. 오늘은 일단 넘어가고요.")
say("SPK05", "이번 달 전력 재판매 관련 문의만 대충 열 건 정도는 됐던 것 같아요.")
say("SPK05", "다들 유휴 시간대 활용법이 궁금하다고 많이들 물어보시더라고요.")
say("SPK01", "그 정도면 확실히 수요가 있긴 하네요.")
say("SPK04", "그렇죠, 그래서 한번 말씀드려본 거예요.")
say("SPK05", "저도 있으면 응대할 때 좀 더 편할 것 같긴 해요.")

# --- closing ---------------------------------------------------------------------
say("SPK01", "음 자 그러면 오늘 정할 건 여기까지 하고 정리만 한 번 하고 마칠게요.")
say("SPK01", "확정 지연은 외곽 출동비 조정으로 가고, 구독 프로모션 기준은 데이터 더 보고 다시 보고요.")
say("SPK01", "충전 오류 재시도는 개발팀 답 기다리는 거고, 커넥터 파손은 비용 비교해서 대응 방식 정합니다.")
say("SPK01", "정비 인력은 현장팀이 접수 확인이랑 입력 지원하는 걸로 갑니다.")
say("SPK04", "어젯밤 출동 지연 건은 결과 나오면 제가 바로 공유드릴게요.",
    kind="commitment", rt=-4, note="상기, 앞서 나온 출동 지연 클레임 건을 다시 확인함")
say("SPK01", "네 그렇게 해주세요. 다음 회의는 다음 주 화요일 같은 시간에 하겠습니다.")
say("SPK02", "그때까지 출동비 기준 정리해서 미리 공유드릴게요.")
say("SPK03", "저는 이 주 뒤에 지원 인력 운영 결과 정리해서 올려두겠습니다.")
say("SPK04", "저는 커넥터 파손 비용표 정리해서 올려두겠습니다.")
say("SPK05", "저도 오늘 나온 것들 정리해서 CS 쪽에 공유해두겠습니다.",
    kind="commitment", note="본인 계획으로 CS팀 공유를 맡음, 기한 없음")
say("SPK01", "다들 고생하셨어요.")
say("SPK02", "고생하셨습니다.", note="사담")
say("SPK03", "다음에 뵐게요.", note="사담")

# --- generated columns -----------------------------------------------------------
LAST_START = 1790.0
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
        "statement": "신규 외곽 전담 정비업체 채널 확보 대신, 외곽 건에 한해서만 출동비를 올려 기사님을 늘리기로 한다.",
        "owner": "SPK02",
        "due": "이번 주 안(출동비 기준 작성 기준)",
        "due_as_said": "이번 주 안으로",
        "evidence_rows": ("d1_settle", "d1_owner", "d1_due"),
        "note": "신규 정비업체 채널이 자격 검증 미비 문제로 두 번째로 무산된 뒤, 외곽 건 출동비 조정으로 절충됨",
    },
    {
        "decision_id": "D2",
        "settles_row": "d2_settle",
        "statement": "프로모션 승인 기준에 정비 처리 여력 점수를 추가하자는 팀장 제안에 아무도 명확히 답하지 않은 채, 원인 데이터를 더 모은 뒤 다시 논의하기로 한다.",
        "owner": "SPK03",
        "due": "",
        "due_as_said": "",
        "evidence_rows": ("d2_proposal", "d2_settle"),
        "note": "충전소별 처리 여력 차이가 기준 추가만으로는 잡히지 않을 수 있다는 우려가 오간 채 데이터 보완으로 유보됨",
    },
    {
        "decision_id": "D3",
        "settles_row": "d3_settle",
        "statement": "충전 오류 자동 재시도는 개발팀 일정이 확정되지 않아 이번 주에는 정하지 않고 답변이 오면 다시 논의한다.",
        "owner": "",
        "due": "개발팀 답변 이후",
        "due_as_said": "개발팀 답 오면 다시",
        "evidence_rows": ("d3_settle", "d3_request"),
        "note": "자동화 요청은 이미 넣었으나 개발 일정이 꽉 차 있어 보류됨",
    },
    {
        "decision_id": "D4",
        "settles_row": "d4_settle",
        "statement": "커넥터 파손 클레임은 시범 적용 비용이 전수 강화형 교체 비용보다 클 경우 전수 교체를 먼저 진행하는 방식으로 대응한다.",
        "owner": "SPK04",
        "due": "이번 주 안(기준표 작성 기준)",
        "due_as_said": "이번 주에",
        "evidence_rows": ("d4_settle", "d4_owner"),
        "note": "사전 고지만으로는 체감 불만을 막기 어렵다는 우려를 거쳐 비용 비교 기준의 조건부 대응으로 확정됨",
    },
    {
        "decision_id": "D5",
        "settles_row": "d5_settle",
        "statement": "정비팀 인력 부족은 현장팀이 접수 확인과 기본 정보 입력을 지원하고, 정비팀은 실제 점검과 판정에 집중하는 방식으로 절충한다.",
        "owner": "SPK02",
        "due": "",
        "due_as_said": "",
        "evidence_rows": ("d5_thrown", "d5_settle"),
        "note": "정비팀에 통째로 떠넘겨졌다가 인력 부족 반발을 거쳐 현장팀 일부 업무 지원으로 절충되어 확정됨",
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
