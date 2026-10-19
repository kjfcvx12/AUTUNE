"""Build DUMMY_121 -- an invented e-scooter/e-bike sharing ops meeting, training data.

Same generator shape as the evalh0N_build.py scripts: the dialogue is held as one
list so row numbers, start times, responds_to and the answer key's row references
are computed instead of typed. Writes DUMMY_121.{A,C,D}.csv and
DUMMY_121.speakers.json into dataset/team_dummy/.

Everything invented: company, people, numbers.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "team_dummy"
MEETING = "DUMMY_121"

ROLE = {
    "SPK01": "PM",
    "SPK02": "Ops",
    "SPK03": "Data",
    "SPK04": "Ops",
    "SPK05": "CS",
}

SPEAKERS = {
    "meeting": MEETING,
    "title": "씽씽모빌리티 운영팀·파워스테이션 11월 배터리 운영 회의",
    "type": "cross-team",
    "position_order": ["사원", "주임", "대리", "과장", "차장", "부장", "이사", "대표"],
    "speakers": [
        {"speaker": "SPK01", "name": "이도현", "team": "씽씽모빌리티 운영팀", "job": "PM",
         "position": "과장", "title": "팀장"},
        {"speaker": "SPK02", "name": "박서연", "team": "씽씽모빌리티 운영팀", "job": "Ops",
         "position": "대리", "title": ""},
        {"speaker": "SPK03", "name": "김태우", "team": "씽씽모빌리티 운영팀", "job": "Data",
         "position": "주임", "title": ""},
        {"speaker": "SPK04", "name": "최은지", "team": "파워스테이션(배터리 협력사)", "job": "Ops",
         "position": "대리", "title": ""},
        {"speaker": "SPK05", "name": "정하늘", "team": "씽씽모빌리티 운영팀", "job": "CS",
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
say("SPK03", "아 창문 좀 열까요, 방금 배터리 창고 쪽에서 뭐 타는 냄새가 나는 것 같아서요.")
say("SPK03", "어제도 그러더니 오늘도 그러네요. 뭐 큰 건 아니겠죠 설마.")
say("SPK03", "제가 어제 가서 봤을 때는 뭐 딱히 이상한 건 안 보이긴 했거든요.")
say("SPK03", "근데 냄새만 나고 연기 같은 건 없어서 저도 좀 긴가민가했어요.")
say("SPK02", "그거 아마 저쪽 충전 랙 쪽 팬이 좀 오래돼서 그럴 거예요. 총무팀에 얘기는 해놨어요.")
say("SPK02", "지난달에도 한 번 그랬는데 그때는 뭐 며칠 지나니까 그냥 괜찮아지더라고요.")
say("SPK02", "그때도 결국 팬 교체까지는 안 가고 그냥 청소만 하고 끝났었거든요.")
say("SPK01", "일단 창문만 열어두고 시작할게요. 오늘은 뭐 길게 안 끌고 넷만 좀 볼게요.")
say("SPK01", "배터리 회수 주기랑 우천 중단 기준, 앱 로그인 오류, 그리고 신규 구역 확장이요.")
say("SPK01", "그 순서대로 갈 건데 혹시 더 급한 거 있으시면 먼저 말씀해 주세요.")
say("SPK01", "기기 점검 밀린 건 시간 되면 보고 안 되면 그냥 다음으로 넘길게요.")
say("SPK01", "아 그리고 오늘은 회의록 따로 안 쓰고 정해진 것만 제가 메신저에 올릴게요.",
    kind="commitment", note="본인이 회의록 대신 정리를 맡겠다고 함")
say("SPK01", "지난번처럼 다 받아 적다가 정작 뭘 정했는지 안 남으면 그게 더 곤란하더라고요.")
say("SPK01", "그러니까 중간에 궁금한 거 있으면 그냥 끊고 들어오셔도 돼요, 편하게 하세요.")
say("SPK04", "네 저도 그게 편해요. 저희 쪽도 회의록 두 벌 쓰는 거라 그게 좀 번거로웠거든요.")
say("SPK04", "매번 저희 팀장님한테 따로 정리해서 보내드려야 하는데 그것도 일이라서요.")
say("SPK01", "그럼 은지 씨가 어제 보내주신 그 회수 데이터부터 보고 시작하죠.",
    kind="open_question", note="논의 순서를 정하며 데이터 공유를 요청함")
say("SPK04", "네 그러니까 이번 주 기준으로 트럭 한 대당 도는 정류소가 열여덟 곳이고요,")
say("SPK04", "그 열여덟 곳을 하루에 두 번씩 돌고 있는 구조예요, 오전 오후로 나눠서요.")

# --- D1: swap truck route frequency (false agreement inside) ---------------------
say("SPK04", "그중에 배터리가 이십 퍼센트 아래로 떨어진 채 방치된 게 평균 삼십 대 정도예요.", decision="D1")
say("SPK04", "아 삼십이 아니라 스물여덟 대네요. 어제 자 수치랑 헷갈렸어요.", decision="D1")
say("SPK04", "어쨌든 그게 그 뭐지, 하루 반나절씩은 그냥 방치되고 있다고 보시면 돼요.", decision="D1")
say("SPK04", "저희도 이게 계속 걸려서 이번에 한번 수치로 정리해서 가져와 봤어요.", decision="D1")
say("SPK04", "예전에는 그냥 감으로만 얘기했었는데 이번엔 좀 제대로 뽑아봤거든요.", decision="D1")
say("SPK04", "표로 정리한 것도 있는데 이따 메일로 같이 보내드릴게요.", decision="D1")
say("SPK02", "그건 저희도 느끼고 있었어요. 민원도 그쪽 정류소에서 유독 많이 들어오고요.",
    decision="D1")
say("SPK02", "특히 역 앞쪽 정류소가 제일 심한데 거기는 뭐 아침마다 거의 텅 비어 있어요.", decision="D1")
say("SPK02", "출근 시간대에 그쪽 가면 탈 수 있는 게 하나도 없다고 매번 그러시더라고요.", decision="D1")
say("SPK02", "저희 현장 직원들도 그 얘기 들을 때마다 뭐라고 설명해야 할지 난감해하고요.", decision="D1")
say("SPK02", "그냥 죄송하다는 말밖에는 딱히 드릴 말씀이 없거든요.", decision="D1")
say("SPK03", "제가 지난달 데이터로 보면요, 배터리 부족으로 인한 취소가 전체 대여 시도의",
    decision="D1")
say("SPK01", "그게 몇 프로쯤 되는 거예요?", kind="open_question", decision="D1", rt=-1,
    note="취소 비율 수치를 물음")
say("SPK03", "한 칠 퍼센트요. 근데 이게 자정 이후로만 보면 십오 퍼센트까지 올라가요.", decision="D1")
say("SPK03", "그러니까 낮에는 뭐 그럭저럭인데 밤에 특히 심하다는 거예요, 그게 문제고요.", decision="D1")
say("SPK03", "낮에 충전된 게 저녁부터 계속 빠지니까 자정 즈음이면 남는 게 별로 없거든요.", decision="D1")
say("SPK03", "요일별로 봐도 그 패턴이 거의 똑같이 나와서 우연은 아닌 것 같아요.", decision="D1")
say("SPK03", "주말은 그나마 좀 낫긴 한데 평일은 매일 그렇더라고요.", decision="D1")
say("SPK04", "저희 쪽에서는 지금 그 뭐지, 하루 두 번 도는 걸 세 번으로 늘리면 되지 않을까 싶긴 한데요.",
    decision="D1")
say("SPK04", "근데 그러면 트럭 인건비가 지금보다 한 오십 퍼센트는 더 들어가요.", decision="D1")
say("SPK04", "그것도 뭐 대충 잡은 거라 실제로는 더 나올 수도 있고요.", decision="D1")
say("SPK04", "기사님을 한 분 더 뽑아야 되는데 그것도 시간이 좀 걸리는 일이라서요.", decision="D1")
say("SPK01", "그 기사님 뽑는 것도 저희랑 같이 논의해야 되는 부분인가요?",
    kind="open_question", decision="D1", rt=-1, note="신규 채용이 양사 공동 논의 사항인지 물음")
say("SPK04", "아뇨 그건 저희 쪽에서 알아서 뽑는 거라 따로 상의드릴 건 없어요.")
say("SPK02", "잠깐만요, 세 번으로 늘리면 그 사이에 저희 현장 인력이랑 동선이 겹치는데요.",
    kind="concern", decision="D1", rt=-6, note="트럭 증편이 현장 인력 동선과 겹친다는 문제 제기")
say("SPK02", "지금도 아침 점검이랑 오후 회수가 거의 붙어서 돌아서 자리가 빠듯하거든요.", decision="D1")
say("SPK02", "거기다 하나 더 끼면 저희 순회 자체가 밀릴 수도 있어요.", decision="D1")
say("SPK02", "지난달에도 인력이 부족해서 점검 하나를 통으로 다음날로 미룬 적이 있었어요.", decision="D1")
say("SPK05", "그리고 그 세 번째 회수가 새벽이면 저희 CS 쪽에는 그 시간에 민원 응대할 사람이 없어요.",
    kind="concern", decision="D1", rt=-10, note="새벽 회수 시 CS 응대 공백을 지적함")
say("SPK05", "지금은 야간에 사람이 아예 없어서 자동응답만 나가고 있거든요.", decision="D1")
say("SPK04", "그건 뭐 저희 트럭 기사님들이 알아서 하시는 거라 CS랑은 안 겹칠 텐데요.", decision="D1")
say("SPK05", "아뇨 그게 아니라, 회수하고 나면 그 정류소에 기기가 갑자기 확 빠지잖아요.",
    kind="concern", decision="D1", rt=-1, note="회수 직후 발생하는 대여 불가 민원을 지적함")
say("SPK05", "그럼 새벽에 대여하려던 분들 민원이 그 시간에 몰리는데 그건 누가 받아요.", decision="D1")
say("SPK05", "지금도 자정 넘어서 오는 문의는 다음날 오전에나 확인하고 있거든요.", decision="D1")
say("SPK01", "음 그 부분은 생각을 못 했네요. 그건 좀 걸리긴 하네요.")
say("SPK04", "그럼 이렇게 하죠! 세 번째는 새벽 대신 저녁 여덟 시로 당기면 되겠네요.",
    decision="D1", note="번복, 합의된 것처럼 보였다가 다음 턴에서 뒤집힘", label="d1_false")
say("SPK01", "네 그 정도면 저도 괜찮을 것 같은데요. 그럼 그렇게 가죠.", decision="D1")
say("SPK02", "아 잠깐만요, 저녁 여덟 시면 그때가 퇴근 대여 몰리는 시간이라 트럭이 못 들어가요.",
    kind="concern", decision="D1", rt=-2, note="저녁 시간대 회수가 퇴근 수요와 겹친다는 반대")
say("SPK02", "그 시간에 정류소마다 사람이 몰려 있어서 트럭 대기만 이십 분씩 걸려요.", decision="D1")
say("SPK02", "저번에 한 번 그 시간에 돌려봤다가 결국 순회를 다 못 끝낸 적도 있었고요.", decision="D1")
say("SPK04", "아 그러네요. 그 시간대는 저희도 생각을 못 했어요, 죄송해요.", decision="D1")
say("SPK03", "그러면 방치 시간이 제일 긴 정류소만 따로 추려서 도는 건 어때요?", decision="D1")
say("SPK03", "전체 정류소를 다 세 번 돌 필요 없이 상위 스무 곳만 추가로 도는 거죠.", decision="D1")
say("SPK03", "그 스무 곳이 전체 방치 시간의 한 육십 퍼센트 정도를 차지하거든요.", decision="D1")
say("SPK03", "그러니까 나머지 백 곳은 지금처럼 두 번만 돌아도 큰 차이는 없을 것 같아요.", decision="D1")
say("SPK03", "제가 지도에 표시까지 해서 보여드릴 수 있어요, 그게 이해하기 더 편하실 것 같아서요.", decision="D1")
say("SPK04", "그 정도면 트럭을 더 안 늘려도 지금 두 대로 돌릴 수 있을 것 같긴 해요.", decision="D1")
say("SPK04", "그 뭐지, 지금 도는 순서에 그 스무 곳만 끼워 넣으면 되니까요.", decision="D1")
say("SPK04", "동선만 좀 손보면 시간도 크게 안 늘어날 것 같고요.", decision="D1")
say("SPK04", "그럼 기사님 채용 건은 일단 보류해도 되겠네요, 그건 좀 다행이에요.", decision="D1")
say("SPK01", "정리하면 트럭 증편 대신 방치 상위 스무 곳을 오후 순회에 추가로 넣는 걸로 갑니다.",
    kind="decision", decision="D1", settles="1",
    note="트럭 증편 반대가 정리된 뒤 기존 대수로 절충안 확정", label="d1_settle")
say("SPK03", "그 상위 스무 곳 목록은 제가 이번 주 안으로 뽑아서 은지 씨한테 넘겨드릴게요.",
    kind="commitment", decision="D1", rt=-1, note="본인이 정류소 목록 산출을 맡음, 기한 명시",
    label="d1_owner")
say("SPK04", "네 목록 받으면 저희 기사님들한테 공유하고 다음 주 월요일부터 반영할게요.",
    decision="D1", label="d1_due")
say("SPK05", "그럼 그 스무 곳은 저희 CS 쪽에도 미리 공지해주시면 좋겠어요.",
    kind="open_question", decision="D1", rt=-1, note="정류소 변경 사항을 CS에도 공유해달라고 요청함")
say("SPK05", "미리 알고 있어야 문의 오면 저희도 설명을 드릴 수 있어서요.", decision="D1")
say("SPK01", "네 그건 목록 나오면 다 같이 공유할게요.")
say("SPK02", "그럼 아침 점검 동선도 그거에 맞춰서 다시 짜야겠네요.",
    kind="commitment", decision="D1", note="본인 계획으로 점검 동선 재조정을 언급함, 기한 없음")
say("SPK02", "겹치는 구간만 좀 조정하면 될 것 같은데 그건 제가 한번 해볼게요.", decision="D1")
say("SPK02", "다음 주 월요일 전까지는 새 동선표 만들어서 공유드릴게요.", decision="D1")
say("SPK03", "음.")
say("SPK04", "네.")

# --- side talk 1 -------------------------------------------------------------------
say("SPK05", "아 근데 어제 일 층에 새로 생긴 그 샌드위치 가게 가보셨어요? 줄이 엄청 길던데요.", note="사담")
say("SPK02", "저 아침에 가봤는데 웨이팅이 삼십 분이더라고요. 결국 그냥 편의점 갔어요.", note="사담")
say("SPK03", "저는 어제 퇴근하고 가서 하나 사 먹었는데 뭐 그럭저럭이었어요.", note="사담")
say("SPK03", "가격 대비 양이 좀 적다는 느낌은 들었어요, 뭐 맛은 나쁘지 않았고요.", note="사담")
say("SPK05", "그래도 한 번은 먹어봐야겠어요. 다들 맛있다고 하시니까 궁금하긴 해요.", note="사담")
say("SPK01", "자 그 얘기는 이따 하고요, 우천 중단 기준 넘어갈게요.")

# --- D2: rain suspension threshold, lead proposal unanswered ---------------------
say("SPK01", "지난주에 비 왔을 때 사고가 두 건 있었잖아요. 그거 정리를 좀 해야 할 것 같은데요.",
    decision="D2")
say("SPK05", "네 그중에 한 건은 접수까지 됐어요. 미끄러져서 무릎 다치셨다고 하시더라고요.", decision="D2")
say("SPK05", "그분이 이제 병원비 얘기까지 하고 계셔서 저희 쪽에서 계속 연락드리고 있어요.", decision="D2")
say("SPK05", "일단 진단서 받으시는 대로 다시 연락 주시기로 했는데 그게 좀 시간이 걸릴 것 같아요.", decision="D2")
say("SPK05", "다른 한 건은 접수까지는 안 갔는데 그것도 비슷한 상황이었다고 들었어요.", decision="D2")
say("SPK05", "그분은 다행히 크게 안 다치셔서 그냥 죄송하다는 말씀만 드리고 마무리됐어요.", decision="D2")
say("SPK05", "그래도 그런 일 겪으시면 다들 좀 예민해지시더라고요.", decision="D2")
say("SPK01", "지금은 우천 기준이 그냥 시간당 강수량 십오 밀리 이상이면 중단인 거죠?", decision="D2")
say("SPK03", "네 근데 그 기준이 지역 전체 평균이라서 국지성 비는 잘 안 잡혀요.", decision="D2")
say("SPK03", "지난주 사고도 그 시간에 그 동네만 비가 세게 왔던 거라 기준에는 안 걸렸어요.", decision="D2")
say("SPK03", "전체 평균으로 보면 그날 오 밀리도 안 됐었거든요.", decision="D2")
say("SPK03", "근데 사고 난 그 동네만 따로 보면 그 시간에 이십 밀리 가까이 왔었더라고요.", decision="D2")
say("SPK05", "아 잠깐만요, 그 동네가 저번 주에 민원 왔던 데랑 같은 데 아니에요?",
    kind="open_question", decision="D2", rt=-1, note="사고 지역이 이전 민원 지역과 동일한지 확인함")
say("SPK03", "어 맞아요, 같은 동네예요. 거기가 원래 배수가 좀 안 좋은 구간이거든요.")
say("SPK01", "그 정도면 뭐 거의 두 배 넘게 차이가 나는 거네요.", decision="D2")
say("SPK01", "그러면 제가 보기엔 기준을 아예 시간당 십 밀리로 낮추는 게 맞을 것 같은데요.",
    decision="D2", label="d2_proposal")
say("SPK04", "그렇게 하면 저희 배터리 회수 트럭도 그 기준 따라서 같이 멈춰야 되는 건가요?",
    kind="open_question", decision="D2", rt=-1, note="우천 기준 변경이 회수 업무에도 적용되는지 물음")
say("SPK01", "아 그건 아니고 대여 서비스만이요. 회수는 그대로 가셔도 돼요.")
say("SPK02", "근데 기준을 낮추면 중단 횟수가 확 늘 텐데 그럼 민원이 그것대로 또 늘잖아요.",
    kind="concern", decision="D2", rt=-3, note="기준 완화 시 서비스 중단 관련 민원 증가를 우려함")
say("SPK02", "지금도 중단될 때마다 왜 안 되냐는 문의가 꽤 들어오고 있고요.", decision="D2")
say("SPK02", "그 중단 시간에 막 대여하려던 분들은 특히 더 짜증을 내시더라고요.", decision="D2")
say("SPK05", "맞아요 저희 쪽은 이미 그것 때문에 하루에도 몇 건씩 문의가 들어와요.", decision="D2")
say("SPK05", "비 그친 지 한참 됐는데 왜 아직도 안 풀리냐는 문의도 꽤 있고요.", decision="D2")
say("SPK03", "그 대신 사고 나면 그게 훨씬 크게 터지는 거니까 뭐가 더 나은지는 좀 애매해요.",
    decision="D2")
say("SPK03", "숫자로만 보면 민원은 늘어도 사고는 줄 것 같은데 그것도 확실친 않고요.", decision="D2")
say("SPK03", "표본이 아직 좀 적어서 더 지켜봐야 확실히 알 수 있을 것 같아요.", decision="D2")
say("SPK05", "그러면 다친 분한테는 저희가 뭐라고 안내를 드리면 될까요?",
    kind="open_question", decision="D2", note="사고 접수 건 응대 방식을 물음")
say("SPK01", "그건 뭐 통상적인 절차대로 안내하시면 돼요, 특별히 다를 건 없어요.")
say("SPK02", "그렇죠.")
say("SPK01", "음 일단 그 얘기는 더 해봐야겠네요. 데이터를 좀 더 보고 다음에 다시 봅니다.",
    kind="decision", decision="D2", settles="1",
    note="상급자 제안, 아무도 명확히 답하지 않고 데이터 보완 후 재논의로 넘어감",
    label="d2_settle")
say("SPK03", "그럼 제가 지역별 국지성 강수 데이터를 기상청 쪽에서 좀 받아볼게요.",
    kind="commitment", decision="D2", rt=-1, note="본인 계획으로 세분화된 강수 데이터 확보를 맡음")
say("SPK03", "그게 있어야 비교가 좀 정확해질 것 같아서요.", decision="D2")
say("SPK04", "네.")

# --- D3: app login bug, held over --------------------------------------------------
say("SPK01", "그다음 앱 로그인 오류인데요, 이게 지금 얼마나 심각한 거예요?")
say("SPK05", "저희 쪽에 하루에 스무 건 정도는 그 문의가 들어오고 있어요.", decision="D3")
say("SPK05", "카카오 로그인만 그런 건데 왜 그런지는 저도 정확히는 몰라요.", decision="D3")
say("SPK05", "네이버나 다른 건 다 괜찮은데 유독 그것만 그래요.", decision="D3")
say("SPK05", "어제는 한 분이 아예 앱을 지웠다 다시 깔았다고까지 하셨어요.", decision="D3")
say("SPK05", "그래도 안 되니까 결국 전화로 저희한테 연락을 주셨고요.", decision="D3")
say("SPK02", "그거 진짜 답답하셨겠네요.")
say("SPK03", "저도 그 로그 좀 봤는데 에러 코드가 매번 다르게 찍혀서 패턴을 못 찾겠더라고요.", decision="D3")
say("SPK03", "어떨 때는 타임아웃이고 어떨 때는 뭐 토큰 오류고 그래요.", decision="D3")
say("SPK03", "기기 종류별로도 좀 갈리는 것 같은데 그것도 아직 확실친 않아요.", decision="D3")
say("SPK01", "음.")
say("SPK04", "그거 저희 개발팀 쪽에서도 재현이 잘 안 돼서 원인 파악이 늦어지고 있다고 들었어요.",
    kind="ambiguous", decision="D3", note="전달, 파트너사 개발팀 상황을 대신 전함")
say("SPK04", "저도 자세히는 몰라서 여쭤봤는데 계속 확인 중이라는 답만 들었어요.", decision="D3")
say("SPK04", "재현이 안 되니까 로그만 계속 들여다보고 있다고 하더라고요.", decision="D3")
say("SPK04", "그것도 뭐 카카오 쪽 응답이 가끔 느려지는 거랑 관련 있을 수도 있다고는 했어요.", decision="D3")
say("SPK04", "확실친 않은데 일단 그쪽도 의심은 하고 있다고 들었어요.", decision="D3")
say("SPK01", "그거 언제쯤 고쳐진다고 하던가요?", kind="open_question", decision="D3",
    note="수정 일정을 물음")
say("SPK04", "정확한 날짜는 저도 못 들었어요. 다음 주 초에는 뭐 좀 나올 거라고만 들었고요.",
    decision="D3")
say("SPK02", "그럼 이거는 오늘 뭘 정할 수 있는 상황은 아니네요.", decision="D3")
say("SPK01", "네 이건 오늘 정하지 말고 다음 주에 다시 봐야 될 것 같아요.",
    kind="decision", decision="D3", settles="1",
    note="원인 파악 전이라 이번 주는 보류, 다음 회의로 넘김", label="d3_settle")
say("SPK05", "저는 그럼 그 문의 들어오는 거 유형별로 정리해서 같이 올릴게요.",
    kind="commitment", decision="D3", rt=-1, note="본인 계획으로 문의 유형 정리를 맡음, 기한 없음")
say("SPK05", "그래야 나중에 원인 나왔을 때 어디부터 봐야 할지 감이 잡힐 것 같아서요.", decision="D3")
say("SPK05", "시간대별로도 좀 나눠서 봐야 할 것 같고요, 그것도 같이 넣을게요.", decision="D3")
say("SPK02", "그거 다 되면 저희도 같이 좀 볼 수 있을까요?",
    kind="open_question", decision="D3", rt=-1, note="문의 유형 정리 결과 공유를 요청함")
say("SPK05", "네 정리되는 대로 같이 올릴게요.")
say("SPK01", "네.")

# --- side talk 2 ---------------------------------------------------------------------
say("SPK02", "아 그리고 주차장 저쪽 자리 며칠째 어떤 차가 계속 대놓고 있던데 혹시 아세요?", note="사담")
say("SPK03", "그거 저도 봤어요. 번호판 보니까 다른 층 직원 차 같던데요.", note="사담")
say("SPK03", "저번에 관리실에서 방송도 한 번 했었는데 그때도 안 빠지더라고요.", note="사담")
say("SPK04", "저희 회사 쪽은 아닐 거예요. 저희는 다 지하 이 층에 대거든요.", note="사담")
say("SPK02", "그럼 관리실에 얘기해서 확인해봐야겠네요.", note="사담")
say("SPK02", "계속 저러면 나중에 견인이라도 해야 될 것 같은데요.", note="사담")
say("SPK01", "자 그건 이따 총무팀에 물어보고요, 신규 구역 얘기로 넘어갈게요.")

# --- D4: new deployment zone, conditional ------------------------------------------
say("SPK01", "신규 구역 확장 건인데, 남쪽 지구까지 넓히자는 얘기가 계속 나오고 있잖아요.",
    decision="D4")
say("SPK02", "거기는 지금 인도 폭이 좁아서 저희 기기 두 대만 세워도 통행이 막히는 구간이 많아요.",
    kind="concern", decision="D4", rt=-1, note="남쪽 지구 인도 폭 문제로 확장에 반대")
say("SPK02", "저번에 다른 지구에서 그거 때문에 민원 들어와서 결국 철수했던 적도 있었고요.",
    decision="D4")
say("SPK02", "그 동네도 지금 남쪽 지구랑 도로 폭이 비슷한 편이었거든요.", decision="D4")
say("SPK03", "근데 그 수요 조사로는 남쪽 지구가 지금 대기 수요 상위 세 곳 안에 들어요.", decision="D4")
say("SPK03", "설문에서도 그쪽 사시는 분들이 왜 여기는 없냐고 계속 물어보셨거든요.", decision="D4")
say("SPK03", "댓글로도 요청이 꽤 많이 올라오고 있는 편이고요.", decision="D4")
say("SPK03", "월별로 봐도 그 요청이 계속 늘어나는 추세라서 이제 무시하기는 어려울 것 같아요.", decision="D4")
say("SPK03", "처음에는 한 달에 열 건 정도였는데 지금은 서른 건 가까이 돼요.", decision="D4")
say("SPK01", "그 정도면 뭐 확실히 수요가 있다는 얘기긴 하네요.")
say("SPK04", "저희 쪽 배터리 인프라는 그 지구에 충전 랙을 하나 더 설치해야 되는데,", decision="D4")
say("SPK04", "그건 설치까지 한 이 주 정도 걸린다고 보시면 돼요.", decision="D4")
say("SPK04", "부지 선정만 되면 그때부터 바로 시공 들어갈 수 있어요.", decision="D4")
say("SPK01", "그럼 인도 폭 문제는 어떻게 풀 수 있는 거예요?", kind="open_question", decision="D4",
    rt=-12, note="확장의 전제 조건인 인도 폭 문제 해결 방안을 물음")
say("SPK02", "거치대를 아예 정해두고 그 안에서만 세우게 하면 좀 나아질 수는 있어요.", decision="D4")
say("SPK02", "다른 지구에서도 그렇게 해서 민원이 꽤 줄었다고 들었거든요.", decision="D4")
say("SPK02", "근데 그것도 구청 쪽 협의가 먼저 돼야 하는 거라 저희끼리 정할 문제는 아니에요.",
    decision="D4")
say("SPK02", "예전에 다른 구청은 그거 협의하는 데만 한 달 넘게 걸렸었어요.", decision="D4")
say("SPK02", "담당 부서가 여러 군데로 나뉘어 있어서 오히려 더 오래 걸렸던 걸로 기억해요.", decision="D4")
say("SPK02", "그래도 남쪽 지구 구청은 이전에 저희랑 한번 협의해본 적이 있어서 좀 나을 수도 있어요.",
    decision="D4")
say("SPK01", "그럼 구청 협의가 되면 확장하고, 안 되면 이번 분기는 보류하는 걸로 하죠.",
    kind="decision", decision="D4", settles="1",
    note="조건부 결정, 구청 협의 여부에 따라 확장 진행 여부가 갈림", label="d4_settle")
say("SPK02", "그 협의는 제가 다음 주에 구청 쪽에 먼저 연락해서 일정을 잡아볼게요.",
    kind="commitment", decision="D4", rt=-1, note="본인이 구청 협의 착수를 맡음, 기한 없음",
    label="d4_owner")
say("SPK04", "협의 되는 대로 저희 쪽 충전 랙 설치는 그다음 주부터 바로 들어갈 수 있어요.", decision="D4")
say("SPK04", "자재는 미리 좀 준비해둘 테니까 연락만 빨리 주세요.", decision="D4")
say("SPK04", "저번에 다른 지구 설치할 때 자재가 늦게 와서 며칠 밀렸던 적이 있었거든요.", decision="D4")
say("SPK04", "그때 그거 때문에 오픈일이 결국 일주일 밀렸었어요.", decision="D4")
say("SPK04", "이번엔 그런 일 없게 미리미리 좀 챙겨보려고요.", decision="D4")
say("SPK03", "혹시 협의가 안 되면 다른 지구로 대신 알아보는 것도 검토해야 할까요?",
    kind="open_question", decision="D4", rt=-7, note="구청 협의 불발 시 대안 지구 검토 여부를 물음")
say("SPK01", "그건 그때 가서 다시 얘기하죠, 지금은 일단 남쪽 지구로 가보고요.")
say("SPK02", "네.")

# --- D5: CS response script, group summary with owner+deadline --------------------
say("SPK01", "그럼 이제 저번에 얘기 나온 그 CS 응대 스크립트 건을 마무리하고 갈게요.")
say("SPK05", "네 지금 스크립트가 작년 거 그대로라서 최근에 바뀐 정책이 하나도 안 들어가 있어요.",
    decision="D5")
say("SPK05", "특히 배터리 부족 대여 실패에 대한 안내 문구가 아예 없어서 상담원마다 다르게 말해요.",
    decision="D5")
say("SPK05", "신입 상담원분들은 아예 뭐라고 해야 할지 몰라서 저한테 계속 물어보시고요.", decision="D5")
say("SPK05", "저도 매번 다르게 설명해드리다 보니까 저조차 헷갈릴 때가 있어요.", decision="D5")
say("SPK05", "이럴 거면 차라리 문서로 딱 정리해두는 게 낫겠다 싶더라고요.", decision="D5")
say("SPK02", "저도 그거 현장에서 몇 번 들었는데 사람마다 설명이 달라서 좀 헷갈리더라고요.", decision="D5")
say("SPK02", "어떤 분은 환불된다고 하고 어떤 분은 안 된다고 하고 그러더라고요.", decision="D5")
say("SPK02", "그러다 보니까 현장에서도 손님들한테 뭐라고 말씀드려야 할지 저희도 좀 헷갈려요.", decision="D5")
say("SPK03", "그거는 그 뭐지, 아까 얘기한 그 취소율 데이터랑 같이 묶어서 설명하면 좋을 것 같아요.",
    decision="D5")
say("SPK03", "숫자를 같이 보여주면 왜 그런지 이해도 더 빠를 것 같고요.", decision="D5")
say("SPK05", "근데 저 혼자 초안까지 다 쓰기는 지금 문의 응대하면서는 시간이 좀 빠듯할 것 같아요.",
    kind="concern", decision="D5", rt=-2, note="CS 업무 병행 중 초안 작성 시간 부족을 우려함")
say("SPK05", "요즘 하루에도 문의가 꽤 많이 들어와서 따로 시간 내기가 쉽지 않거든요.", decision="D5")
say("SPK01", "그럼 정리하면, 스크립트는 하늘 씨가 초안 잡고 서연 씨랑 태우 씨가 검토해서",
    kind="decision", decision="D5", settles="1",
    note="논의 끝에 담당과 검토 절차, 기한이 함께 확정됨", label="d5_settle")
say("SPK01", "다음 회의 전까지 확정하는 걸로 하죠.", decision="D5", label="d5_due")
say("SPK05", "네 그럼 제가 초안은 이번 주 목요일까지 만들어서 올려둘게요.",
    kind="commitment", decision="D5", rt=-1, note="본인이 확정 기한보다 앞선 초안 마감을 스스로 잡음",
    label="d5_owner")
say("SPK02", "저는 그거 받으면 현장에서 실제로 쓰는 표현이랑 맞는지 한번 봐볼게요.",
    kind="commitment", decision="D5", rt=-1, note="본인 계획으로 현장 표현 검토를 맡음, 기한 없음")
say("SPK03", "저도 그 취소율 수치 부분은 최신 걸로 다시 뽑아서 드릴게요.",
    kind="commitment", decision="D5", rt=-2, note="본인 계획으로 최신 수치 제공을 맡음, 기한 없음")
say("SPK03", "이번 달 것까지 다 포함해서 뽑으면 좀 더 설득력이 있을 것 같아서요.", decision="D5")
say("SPK04", "저희 쪽 안내 문구도 좀 맞춰야 할 것 같긴 한데, 그건 저도 한번 검토는 해볼게요.",
    kind="ambiguous", decision="D5", rt=-1, note="구체적 계획 없이 검토만 하겠다는 약한 응답")
say("SPK04", "저희도 배터리 관련 안내는 저희 쪽 매뉴얼이 따로 있긴 하거든요.", decision="D5")
say("SPK01", "네 급한 건 아니니까 편하게 봐주세요.")

# --- side talk 3 ---------------------------------------------------------------------
say("SPK04", "아 그리고 저희 배터리 창고 냄새 그거, 아까 총무팀에 얘기하신다고 하셨죠?", note="사담")
say("SPK01", "네 이따 내려가면서 바로 얘기할게요.", note="사담")
say("SPK03", "저 근데 그 팬이 문제면 그냥 랙 위치를 옮기는 게 낫지 않아요?", note="사담")
say("SPK02", "그건 이따 따로 보죠. 지금은 일단 창문으로 버텨요.", note="사담")

# --- D6: device inspection backlog, resistance before settling --------------------
say("SPK01", "마지막으로 기기 점검 밀린 거 짧게 보고 갈게요. 지금 얼마나 밀려 있는 거예요?")
say("SPK02", "정기 점검 대상이 이백 대인데 그중에 백이십 대가 아직 안 돌았어요.", decision="D6")
say("SPK02", "저희 인원이 지금 세 명인데 뭐 하루에 스무 대씩 돌아도 일주일은 걸리는 양이에요.", decision="D6")
say("SPK02", "그것도 다른 업무 없이 이것만 했을 때 얘기고요.", decision="D6")
say("SPK02", "실제로는 중간에 민원 처리나 회수도 껴 있어서 더 걸릴 거예요.", decision="D6")
say("SPK02", "지난주에도 점검을 반나절 하다가 민원 때문에 두 번이나 끊겼었거든요.", decision="D6")
say("SPK02", "그러다 보니까 하루에 스무 대는커녕 열 대도 못 돌 때가 많아요.", decision="D6")
say("SPK01", "그럼 지금 속도로는 언제쯤 다 돌 수 있는 거예요?",
    kind="open_question", decision="D6", rt=-1, note="현재 속도 기준 전체 완료 시점을 물음")
say("SPK02", "이대로면 한 달은 더 걸릴 것 같아요, 그것도 낙관적으로 본 거고요.", decision="D6")
say("SPK01", "그 백이십 대 중에서 특히 오래된 게 얼마나 되는 거예요?",
    kind="open_question", decision="D6", rt=-1, note="점검 대상 중 노후 기기 비중을 물음")
say("SPK02", "한 삼십 대 정도는 벌써 두 달 넘게 밀려 있는 것들이에요.", decision="D6")
say("SPK02", "그것들부터라도 먼저 봐야 하는데 순서를 못 잡고 있는 상황이고요.", decision="D6")
say("SPK01", "이건 뭐 현장운영팀에서 알아서 좀 당겨서 해주셔야 할 것 같은데요.",
    decision="D6", label="d6_thrown")
say("SPK02", "저희도 지금 아까 그 순회 동선도 다시 짜야 되는 상황이라 인원이 더 빠듯해질 것 같은데요.",
    kind="concern", decision="D6", rt=-1, note="점검 밀림 해소가 순회 동선 재조정과 겹쳐 인력 부족하다는 반대")
say("SPK02", "거기다 점검까지 당기라고 하시면 저희 셋이서는 진짜 못 버텨요.", decision="D6")
say("SPK02", "누구 하나 휴가라도 가면 그날은 아예 아무것도 못 돌 수도 있고요.", decision="D6")
say("SPK02", "인원 충원 얘기도 몇 번 드렸는데 그게 아직 답이 없는 상태고요.", decision="D6")
say("SPK01", "그건 저도 위에 계속 얘기는 하고 있는데 아직 답을 못 받았어요.")
say("SPK01", "그것도 이따 다시 한번 물어볼게요.")
say("SPK02", "아... 예... 그럼 일단 저희가 오래된 것부터라도 좀 당겨서 돌아는 볼게요.",
    kind="ambiguous", decision="D6", rt=-2, note="위임, 인원 문제가 해결 안 된 채로 밀린 점검을 마지못해 떠안음")
say("SPK04", "저희 쪽에서 트럭 도는 김에 육안 점검 정도는 같이 봐드릴 수 있을 것 같긴 한데요.",
    decision="D6")
say("SPK04", "근데 저희 기사님들이 전문 점검은 아니라서 이상 있는 것만 표시해드리는 정도예요.",
    decision="D6")
say("SPK04", "타이어 마모나 외관 파손처럼 눈에 딱 보이는 것만 가능하다고 보시면 돼요.", decision="D6")
say("SPK03", "그 정도만 돼도 심한 것부터 먼저 골라낼 수 있으니까 도움이 될 것 같은데요.", decision="D6")
say("SPK03", "지금은 그 순서를 정할 기준 자체가 없어서 그냥 오래된 순서로만 보고 있었거든요.", decision="D6")
say("SPK03", "그러다 보니까 정작 위험한 건 뒤로 밀리는 경우도 있었을 것 같고요.", decision="D6")
say("SPK02", "그건 그런데, 저희 체크리스트를 트럭 기사님들한테 따로 교육을 시켜야 되는 거라서요.",
    kind="concern", decision="D6", rt=-3, note="파트너사 기사 교육 부담을 근거로 반대")
say("SPK04", "체크리스트가 복잡한 거 아니면 저희 쪽에서 하루 정도 시간 내서 들을 수는 있어요.", decision="D6")
say("SPK02", "복잡하진 않아요. 그냥 타이어 마모랑 배터리 외관 정도만 보시면 돼요.", decision="D6")
say("SPK02", "사진 몇 장 찍어서 표로만 남겨주시면 저희가 나머지는 알아서 볼게요.", decision="D6")
say("SPK02", "양식도 간단하게 만들어서 드릴 테니까 그거에 체크만 해주시면 돼요.", decision="D6")
say("SPK01", "그럼 육안 점검은 파워스테이션 기사님들이 순회하면서 같이 봐주시고,",
    kind="decision", decision="D6", settles="1",
    note="반발 끝에 협력사 지원으로 절충된 방식으로 확정", label="d6_settle")
say("SPK01", "저희는 그중에 이상 표시된 것만 우선으로 도는 걸로 하죠.", decision="D6")
say("SPK04", "네 그럼 체크리스트 교육은 제가 이번 주 안으로 기사님들 모아서 진행할게요.",
    kind="commitment", decision="D6", rt=-2, note="본인이 기사 교육 진행을 맡음, 기한 명시",
    label="d6_owner")
say("SPK02", "저는 그럼 이상 표시된 것 위주로 우선순위 리스트를 다시 짜볼게요.",
    kind="commitment", decision="D6", rt=-1, note="본인 계획으로 우선순위 재조정을 맡음, 기한 없음")
say("SPK02", "그것도 다음 주 초까지는 한번 만들어볼게요.", decision="D6")
say("SPK05", "혹시 점검 중에 파손 심한 기기 나오면 저희 CS 쪽에도 바로 알려주시는 거죠?",
    kind="open_question", decision="D6", rt=-2, note="파손 기기 발견 시 CS 공유 여부를 확인함")
say("SPK02", "네 그건 바로바로 공유드릴게요.")
say("SPK04", "네.")
say("SPK03", "음.")

# --- brief aside: device damage insurance, a peer proposal nobody takes up ------
say("SPK03", "아 그리고 이건 그냥 제 생각인데요, 파손 기기 보험 같은 걸 들어두면 어떨까요?")
say("SPK03", "요즘 파손 건이 좀 늘어난 것 같아서 그냥 한번 말씀드려 봐요.")
say("SPK02", "그거 좋은 생각이긴 한데 지금 당장 알아볼 사람이 없긴 하죠.")
say("SPK01", "음 그건 나중에 좀 더 얘기해보죠. 오늘은 넘어가고요.")
say("SPK05", "저는 이번 달 파손 접수 건수만 대충 삼십 건 정도였던 것 같아요.")

# --- closing ---------------------------------------------------------------------
say("SPK01", "자 그러면 오늘은 여기까지 하고 정리만 한 번 하고 끊을게요.")
say("SPK01", "빠진 거 있으면 편하게 말씀해 주세요, 다들 오늘 얘기 많이 나눠주셔서 좋았어요.")
say("SPK01", "배터리 회수는 상위 스무 곳 추가 순회로 가고, 우천 기준은 데이터 더 보고 다시 보고요.")
say("SPK04", "로그인 오류는 저희 개발팀 쪽 원인 파악 되면 다음 주에 다시 말씀드릴게요.",
    kind="ambiguous", rt=-1, note="원인 파악 이후 재보고를 막연히 약속함")
say("SPK01", "신규 구역은 구청 협의 결과에 따라 가고, CS 스크립트는 목요일 초안으로 갑니다.")
say("SPK01", "점검은 협력사 육안 점검이랑 저희 우선순위 리스트 같이 가는 거고요.")
say("SPK05", "저는 그럼 스크립트 초안 잡는 대로 단톡방에 먼저 올릴게요.",
    kind="commitment", rt=-4, note="상기, 앞서 정해진 본인 일정을 다시 확인함")
say("SPK01", "네 그렇게 해주세요. 다음 회의는 다다음 주 화요일 같은 시간에 하겠습니다.")
say("SPK01", "장소는 오늘이랑 같은 데로 잡아둘게요, 바뀌면 따로 공지드리고요.")
say("SPK03", "그때까지 강수 데이터 정리해서 미리 공유드릴게요.")
say("SPK02", "저는 그럼 순회 동선부터 다시 짜보겠습니다.")
say("SPK05", "저도 오늘 나온 것들 정리해서 CS 팀 단톡방에 공유해두겠습니다.",
    kind="commitment", note="본인 계획으로 CS팀 공유를 맡음, 기한 없음")
say("SPK01", "네 다들 고생하셨어요.")
say("SPK04", "고생하셨습니다.", note="사담")
say("SPK02", "다음에 뵐게요.", note="사담")

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
        "statement": "새벽·저녁 대신 배터리 방치 상위 20개 정류소를 기존 오후 순회에 추가하는 방식으로, 트럭 증차 없이 회수 공백을 메운다.",
        "owner": "SPK03",
        "due": "2026-09-28(다음 주 월요일 반영 기준)",
        "due_as_said": "다음 주 월요일부터",
        "evidence_rows": ("d1_settle", "d1_owner", "d1_due"),
        "note": "트럭을 하루 세 번으로 늘리는 안이 새벽·저녁 시간대 문제로 두 번 뒤집힌 뒤 상위 정류소 추가 순회로 절충됨",
    },
    {
        "decision_id": "D2",
        "settles_row": "d2_settle",
        "statement": "우천 서비스 중단 기준을 시간당 10밀리로 낮추자는 팀장 제안에 아무도 답하지 않은 채, 지역별 강수 데이터를 더 확보한 뒤 다시 논의하기로 한다.",
        "owner": "SPK03",
        "due": "",
        "due_as_said": "",
        "evidence_rows": ("d2_proposal", "d2_settle"),
        "note": "국지성 강수 미탐지로 인한 사고 재발 방지 목적의 제안이었으나, 민원 증가 우려만 오간 채 데이터 보완으로 유보됨",
    },
    {
        "decision_id": "D3",
        "settles_row": "d3_settle",
        "statement": "카카오 로그인 오류는 파트너사 개발팀의 원인 파악이 끝나지 않아 이번 주에는 정하지 않고 다음 회의로 넘긴다.",
        "owner": "",
        "due": "다음 주 회의",
        "due_as_said": "다음 주에 다시",
        "evidence_rows": ("d3_settle",),
        "note": "원인조차 재현이 안 되는 상태라 회의에서 정할 수 있는 것이 없어 보류됨",
    },
    {
        "decision_id": "D4",
        "settles_row": "d4_settle",
        "statement": "남쪽 지구 서비스 확장은 구청과의 거치대 구역 협의가 성사되면 진행하고, 안 되면 이번 분기는 보류한다.",
        "owner": "SPK02",
        "due": "",
        "due_as_said": "",
        "evidence_rows": ("d4_settle", "d4_owner"),
        "note": "인도 폭으로 인한 통행 민원 우려가 거치대 지정이라는 조건으로 절충되었고, 그 조건이 구청 협의에 달려 있어 조건부로 확정됨",
    },
    {
        "decision_id": "D5",
        "settles_row": "d5_settle",
        "statement": "CS 응대 스크립트는 정하늘이 초안을 작성하고 박서연과 김태우가 현장 표현과 데이터 정합성을 검토하여 다음 회의 전까지 확정한다.",
        "owner": "SPK05",
        "due": "다음 회의 전",
        "due_as_said": "다음 회의 전까지",
        "evidence_rows": ("d5_settle", "d5_due", "d5_owner"),
        "note": "작년 스크립트에 최근 정책이 반영 안 되어 상담원마다 설명이 달랐던 문제를 논의한 뒤 담당·검토자·기한이 한 번에 정리됨",
    },
    {
        "decision_id": "D6",
        "settles_row": "d6_settle",
        "statement": "밀린 기기 점검 120대는 파워스테이션 기사들이 순회 중 육안 점검을 지원하고, 운영팀은 이상이 표시된 기기부터 우선 점검한다.",
        "owner": "SPK04",
        "due": "이번 주 안(기사 교육 기준)",
        "due_as_said": "이번 주 안으로",
        "evidence_rows": ("d6_thrown", "d6_settle", "d6_owner"),
        "note": "현장운영팀에 통째로 떠넘겨졌다가 인력 부족 반발을 거쳐 협력사 지원으로 절충되어 확정됨",
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
