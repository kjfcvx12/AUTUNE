"""Build DUMMY_131 -- an invented shared-office ("코숨") operations team meeting, training data.

Same generator shape as dummy121-130_build.py. Writes DUMMY_131.{A,C,D}.csv and
DUMMY_131.speakers.json into dataset/team_dummy/.

Unlike DUMMY_121-130, this meeting is not part of the rough30/clean30 pair. It
targets two specific failure patterns found by manually running the
share_s20260910 checkpoint against a hand-written test meeting outside this
project's own eval sets:

1. Hedged/indirect commitments ("~까지는 봐야 할 것 같아요" instead of "~하겠습니다")
   were classified `none` -- missed entirely. Rows d1_owner, d2_owner_hedge,
   d3_hedge, d4_hedge, d5_hedge, and the closing recap use this register instead
   of the direct-promise phrasing the corpus otherwise favours.
2. Long compound sentences with a decision-flavoured conditional clause
   ("~되면", "~하면 그때") followed by the speaker's OWN commitment clause were
   mislabelled `decision`. Rows d2_conditional_commit, d3_conditional_commit and
   d4_conditional_commit are structurally decision-shaped (conditional clause,
   "-겠습니다" ending) but settle nothing new -- they reference a decision already
   made elsewhere in the meeting and are the speaker's personal follow-through,
   so they are labelled `commitment`, not `decision`, per SPEC.md's own kind
   definitions (no group settling happens in these rows).

Everything invented: company, people, numbers.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "team_dummy"
MEETING = "DUMMY_131"

ROLE = {
    "SPK01": "PM",
    "SPK02": "Facility",
    "SPK03": "Sales",
    "SPK04": "CS",
    "SPK05": "Finance",
}

SPEAKERS = {
    "meeting": MEETING,
    "title": "코숨 공유오피스 운영팀 격주 점검 회의",
    "type": "team",
    "position_order": ["사원", "주임", "대리", "과장", "차장", "부장", "이사", "대표"],
    "speakers": [
        {"speaker": "SPK01", "name": "오세인", "team": "코숨 운영팀", "job": "PM",
         "position": "과장", "title": "팀장"},
        {"speaker": "SPK02", "name": "반유주", "team": "코숨 운영팀", "job": "Facility",
         "position": "대리", "title": ""},
        {"speaker": "SPK03", "name": "하도경", "team": "코숨 운영팀", "job": "Sales",
         "position": "주임", "title": ""},
        {"speaker": "SPK04", "name": "진하늘", "team": "코숨 운영팀", "job": "CS",
         "position": "대리", "title": ""},
        {"speaker": "SPK05", "name": "남시우", "team": "코숨 운영팀", "job": "Finance",
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
say("SPK04", "음 시작 전에 하나만요, 어제 3층 라운지 쪽에서 컴플레인이 좀 크게 들어왔어요.")
say("SPK04", "어 회의실 예약한 팀이 왔는데 그 시간에 다른 팀이 안 나가고 계속 쓰고 있었대요.")
say("SPK04", "음 그거 때문에 이십 분 넘게 실랑이가 있었고 결국 저희 쪽에서 다른 방을 급하게 잡아드렸어요.")
say("SPK02", "어 그 방 저도 알아요, 그 팀이 저번 달에도 비슷한 일이 한 번 있었던 것 같은데요.")
say("SPK01", "음 그 건은 이따 예약 얘기할 때 다시 짚고 갈게요, 오늘은 네 가지만 보고 마칠게요.")
say("SPK01", "음 노쇼 페널티 개편이랑 3호점 오픈 일정, 정산 오류 알림, 그리고 회의실 소음 민원이요.")
say("SPK01", "일단 그 순서로 가려는데 혹시 먼저 봐야 할 급한 거 있으면 말씀해 주세요.")
say("SPK01", "그리고 오늘도 회의록은 따로 안 쓰고 정해진 것만 이따 채널에 정리해서 올릴게요.",
    kind="commitment", note="본인이 회의록 대신 정리를 맡겠다고 함")
say("SPK01", "그냥 저번처럼 다 받아 적다가 뭐가 정해졌는지 흐려지느니 그게 낫겠더라고요.")
say("SPK03", "일단 네 저도 그 방식이 편해요, 저번 회의록은 다시 봐도 헷갈리더라고요.")
say("SPK01", "음 그럼 유주 씨가 준비한 노쇼 현황부터 볼까요.",
    kind="open_question", note="논의 순서를 정하며 데이터 공유를 요청함")
say("SPK02", "음 네 이번 달 노쇼 건수가 지난달보다 꽤 늘었어요,")
say("SPK02", "어 특히 무료 체험 회원 쪽에서 노쇼가 많이 나오고 있고요.")
say("SPK02", "그냥 정회원이랑 비교하면 거의 세 배 가까이 차이가 나는 수준이에요.")

# --- D1: no-show penalty policy, false agreement inside --------------------------
say("SPK02", "그리고 이번에 노쇼 문제가 좀 커졌어요.", decision="D1")
say("SPK02", "음 작년 이맘때는 노쇼율이 한 오 퍼센트 정도였거든요.", decision="D1")
say("SPK02", "아 오 퍼센트가 아니라 칠 퍼센트네요. 작년 자료랑 재작년 자료를 헷갈렸어요.", decision="D1")
say("SPK02", "음 어쨌든 그때보다 확실히 더 늘어난 건 맞아요.", decision="D1")
say("SPK02", "어 요즘 체험 신청은 늘었는데 실제 이용 전환은 그대로라서 그런 것 같아요.", decision="D1")
say("SPK02", "음 특히 그중에 이번 주 노쇼 두 건 때문에 정회원 두 팀이 방을 못 잡아서 컴플레인까지 나갔어요.", decision="D1")
say("SPK02", "음 그게 이번 달 전체 컴플레인의 한 삼십 퍼센트나 차지하는 거라 타격이 좀 크네요.", decision="D1")
say("SPK02", "어 이 상태로 가면 다음 달에는 정회원 이탈로도 이어질 수 있을 것 같고요.", decision="D1")
say("SPK05", "어 그건 저도 봤어요, 그 두 건 정산 데이터가 유독 안 좋더라고요.", decision="D1")
say("SPK05", "음 저희 말고 다른 공유오피스 커뮤니티에도 비슷한 후기가 올라와 있던데요.", decision="D1")
say("SPK05", "어 저번에 CS 통계 볼 때도 그런 얘기가 있긴 했었어요.", decision="D1")
say("SPK05", "어 저희가 그때 좀 더 서둘러서 봤어야 했나 싶기도 하고요, 아쉽네요.", decision="D1")
say("SPK03", "음 그럼 지금 페널티는 그냥 다음 예약 하루 제한인 거죠? 그게 전부예요?",
    kind="open_question", decision="D1", rt=-1, note="현재 페널티 수위를 물음")
say("SPK03", "어 일단 지금 체제로는 무료 체험 쪽은 딱히 잃을 게 없어서 그런 것 같거든요.", decision="D1")
say("SPK01", "음 그 얘기는 예약 쪽에서 이따 다시 할게요, 일단 노쇼부터 정리하고요.")
say("SPK01", "어 그럼 지금 페널티를 그대로 두면 체험 회원 노쇼가 계속 늘어난다는 얘기인데요.", decision="D1")
say("SPK01", "음 이번 주 안에 페널티를 좀 더 세게 가야 될 것 같은데 다들 어떻게 보세요?", decision="D1")
say("SPK02", "음 저는 일단 지금 체험 기간은 그대로 두고 노쇼 시 보증금만 좀 걸어두는 게 낫지 않을까 싶어요.",
    decision="D1")
say("SPK02", "음 근데 보증금 걸면 신규 체험 신청 자체가 줄어들 수도 있거든요.", decision="D1")
say("SPK02", "음 지금 당장 체험 유입이 중요한데 그걸 막을 여유는 없을 것 같아서요.", decision="D1")
say("SPK04", "음 근데 보증금을 걸면 그만큼 결제 문의랑 환불 문의도 늘어나는 거라서요.", kind="concern",
    decision="D1", rt=-2, note="보증금 도입이 CS 문의 증가로 이어진다는 우려")
say("SPK04", "음 지금도 문의량이 그렇게 여유 있는 편은 아니거든요.", decision="D1")
say("SPK04", "어 환불 절차를 새로 안내하지 않는 이상 문의 증가분은 그대로 저희 부담이에요.", decision="D1")
say("SPK01", "그럼 아예 무료 체험 자체를 없애고 전부 유료 체험으로 돌리는 쪽으로 가죠! 그게 더 낫겠네요.",
    decision="D1", note="번복, 합의된 것처럼 보였다가 다음 턴에서 뒤집힘", label="d1_false")
say("SPK02", "음 네 그게 나을 것 같긴 해요.", decision="D1")
say("SPK03", "아 잠깐만요, 유료 체험은 저희 영업 쪽 전환율 목표랑 계약된 조건에 맞는지 먼저 확인해야 되는데요.",
    kind="concern", decision="D1", rt=-2, note="유료 체험 전환이 영업 목표/계약 조건과 맞는지 사전 확인이 필요함을 지적")
say("SPK01", "음 그때 그 계약 조건은 어떻게 걸려 있는 거였죠?", kind="open_question", decision="D1", rt=-1,
    note="과거 계약 조건을 어떻게 확인했는지 물음")
say("SPK03", "저번에 급하게 유료 전환 테스트했던 지점은 결국 신청 자체가 너무 줄어서 두 달 만에 되돌렸잖아요.", decision="D1")
say("SPK03", "어 그때 재전환 비용이랑 마케팅비가 더 나가서 오히려 손해였고요.", decision="D1")
say("SPK03", "음 그 지점은 계약 조건부터가 저희 기준이랑 많이 달랐던 걸로 기억해요.", decision="D1")
say("SPK03", "음 그러니까 유료 전환을 하더라도 최소 한두 달은 테스트 기간을 잡아야 할 것 같아요.", decision="D1")
say("SPK03", "음 그 기간 동안은 오히려 영업 쪽 목표 숫자가 흔들리기도 하고요.", decision="D1")
say("SPK01", "아 맞다, 그때 그 일이 있었죠.")
say("SPK01", "음 그럼 유료 전환은 테스트 기간이 필요하니까 이번 달에는 못 쓰겠네요.", decision="D1")
say("SPK05", "어 그러면 결국 남은 건 노쇼 보증금 조정밖에 없는 것 같은데요.", decision="D1")
say("SPK05", "어 근데 그것도 사실 임시방편이라는 느낌은 있어서 좀 걱정이긴 해요.",
    kind="concern", decision="D1", rt=-1, note="보증금 조정이 근본 해결책은 아니라는 우려")
say("SPK02", "음 보증금을 전체로 다 걸지 말고 무료 체험 쪽만 먼저 걸어보면 어때요?",
    decision="D1")
say("SPK02", "어 무료 체험이 원래 제일 심했으니까 거기만 잡아도 효과가 꽤 있을 것 같아요.", decision="D1")
say("SPK05", "음 그 정도면 신청 이탈 폭이 한 오 퍼센트 정도라서 감당은 충분히 될 것 같아요.", decision="D1")
say("SPK05", "음 정회원 쪽은 지금도 노쇼가 거의 없어서 괜찮을 것 같고요.", decision="D1")
say("SPK01", "그럼 정회원은 그대로 가고 체험 회원 보증금만 조정하는 방향이네요.")
say("SPK02", "음 네 맞아요.")
say("SPK01", "그럼 체험 회원 노쇼만 보증금 걸고 나머지는 그대로 두는 걸로 정리할게요.",
    kind="decision", decision="D1", settles="1",
    note="유료 전환은 계약 조건 문제로 무산된 뒤 체험 회원 보증금 도입으로 절충", label="d1_settle")
say("SPK02", "일단 보증금 기준이랑 환불 조건은 제가 다음 주 초까지는 정리해서 공유할 수 있을 것 같아요.",
    kind="commitment", decision="D1", rt=-1,
    note="본인이 보증금 기준 작성을 맡음, 완곡한 예측형 기한 표현", label="d1_owner")
say("SPK04", "저도 그거 CS 스크립트 반영은 필요하면 같이 봐드릴 수는 있어요.",
    kind="ambiguous", decision="D1", rt=-1, note="구체적 계획 없이 필요하면 돕겠다는 약한 응답")
say("SPK02", "음 얼마나 걸어야 이탈이 안 커질지는 영업 쪽이랑도 얘기해봐야 알 것 같아요.", decision="D1",
    label="d1_due")
say("SPK02", "음 너무 많이 걸면 저희 쪽이 손해니까 선을 잘 잡아야 할 것 같아요.", decision="D1")
say("SPK02", "지난달 조정 폭보다 이틀 앞당겨서 이번 주 안에 먼저 제안해보려고요.", decision="D1")
say("SPK01", "그럼 그 결과 보고 다음 달에 목표 노쇼율을 다시 잡죠.")
say("SPK03", "네.")
say("SPK03", "저는 그동안 체험 신청 상담 스크립트라도 한번 다시 짜보려고요.",
    kind="commitment", decision="D1", note="본인 계획으로 상담 스크립트 재검토를 시도함, 기한 없음")
say("SPK03", "혹시 체험 전환율을 따로 더 끌어올릴 방법도 이번 주에 알아볼게요.", decision="D1")
say("SPK05", "음.")
say("SPK03", "넵.")

# --- side talk 1 -------------------------------------------------------------------
say("SPK04", "그러고 보니 1층에 새로 생긴 그 샌드위치 가게 가보셨어요? 줄이 길더라고요.", note="사담")
say("SPK02", "저 아직 못 가봤어요. 맛은 어때요?", note="사담")
say("SPK04", "괜찮았어요, 근데 생각보다 좀 비싸더라고요.", note="사담")
say("SPK04", "기본 샌드위치가 팔천 원 넘던데요.", note="사담")
say("SPK03", "저도 한번 가봐야겠네요, 요즘 마땅한 데가 없어서 좀 아쉬웠거든요.", note="사담")
say("SPK03", "자주 가던 데가 얼마 전에 갑자기 문을 닫아서요.", note="사담")
say("SPK05", "요즘 임대료가 워낙 비싸다 보니까 다들 버티기 힘든가 봐요.", note="사담")
say("SPK02", "맞아요, 저희 건물 상가도 그런 얘기 많이 들려요.", note="사담")
say("SPK02", "예전엔 이 정도는 아니었던 것 같은데 요즘 부쩍 심해진 것 같아요.", note="사담")
say("SPK03", "그러게요.", note="사담")
say("SPK05", "음 저도 그 얘기 들었어요, 확실히 다들 힘드시겠어요.", note="사담")
say("SPK01", "그 얘기는 이따 마저 하고요, 3호점 오픈 일정 쪽으로 넘어갈게요.")

# --- D2: new branch opening, lead proposal unanswered + conditional commitment ------
say("SPK01", "지난주에 3호점 오픈 준비 상황 공유해 달라고 요청했었잖아요. 그것부터 볼게요.",
    decision="D2")
say("SPK03", "네 그중에 시설 쪽 준비가 좀 늦어지고 있다고 얘기가 나왔어요.", decision="D2")
say("SPK03", "칸막이 공사가 절반 정도밖에 안 끝났더라고요.", decision="D2")
say("SPK03", "오픈일 맞추려면 이번 주 안에는 마무리돼야 한다고 하시면서 다들 걱정을 많이 하세요.", decision="D2")
say("SPK03", "그것도 층마다 사정이 달라서 생각보다 관리가 복잡해요.", decision="D2")
say("SPK03", "현장 소장님도 처음엔 그냥 넘어가려다가 자재 수급 늦어지니까 그제야 신경 쓰시더라고요.", decision="D2")
say("SPK03", "다른 한 건은 소방 점검 일정이 밀렸다고 하셨는데 그건 아직 협의 중이에요.", decision="D2")
say("SPK03", "구청 쪽에서 서류까지 보내주셨는데 저희가 봐도 처리 기간이 좀 길긴 하더라고요.", decision="D2")
say("SPK01", "지금 오픈 승인 기준이 시설 완료율 확인해서 결정하는 게 전부인 거죠?", decision="D2")
say("SPK02", "네 근데 그 기준으로는 소방 점검 여력까지는 잘 안 잡혀요.", decision="D2")
say("SPK02", "그 지점도 저희가 볼 때는 완료율은 괜찮았거든요.", decision="D2")
say("SPK02", "기록 봐도 완료율 기준 통과로 표시돼 있었고 저도 그때 직접 확인했었어요.", decision="D2")
say("SPK02", "그래서 이게 공사 문제인지 행정 처리 문제인지가 좀 헷갈려요.", decision="D2")
say("SPK02", "비슷한 사례가 더 있는지 한번 찾아봐야 할 것 같고요.", decision="D2")
say("SPK02", "근데 그게 행정 처리까지 다 확인하면 승인이 너무 오래 걸릴 수도 있어요.", decision="D2")
say("SPK01", "그러면 제가 보기엔 오픈 승인 기준에 소방 점검 완료 여부도 같이 넣는 게 맞을 것 같은데요.",
    decision="D2", note="상급자 제안, 아무도 명확히 답하지 않고 데이터 보완 후 재논의로 넘어감", label="d2_proposal")
say("SPK02", "그렇게 하면 승인 절차가 더 오래 걸리는 거 아닌가요?",
    kind="open_question", decision="D2", rt=-1, note="승인 기준 추가가 처리 속도에 미치는 영향을 물음")
say("SPK02", "지금도 일정이 빠듯한데 항목을 늘리면 감당이 안 될 것 같아서요.", decision="D2")
say("SPK01", "그건 이따 인력 얘기할 때 같이 볼게요, 지금은 기준만이요.")
say("SPK01", "일단 뭐가 맞는 방향인지부터 정하고 일정은 그다음에 맞춰야죠.")
say("SPK03", "근데 기준을 늘려도 그 소방 점검 같은 건 지역마다 달라서 꼭 잡힌다는 보장은 없어요.",
    kind="concern", decision="D2", rt=-4, note="승인 기준 추가만으로는 지역별 행정 차이를 못 잡을 수 있다는 우려")
say("SPK03", "저희가 볼 때는 그냥 완료율만 보고 판단하는 거라서요.", decision="D2")
say("SPK05", "그럼 기준을 늘리는 것보다 오픈 이후에 사후 점검을 한 번 더 하는 게 낫지 않을까요?",
    decision="D2")
say("SPK05", "오픈하고 나서 실제 지연이 어땠는지 보면 그게 더 정확할 것 같아요.", decision="D2")
say("SPK05", "저희가 예전에 그렇게 한 적이 있었는데 그때는 문제 적발률이 꽤 높았거든요.", decision="D2")
say("SPK05", "그때 기억으로는 한 팔 퍼센트 정도는 그 단계에서 추가로 걸러졌었어요.", decision="D2")
say("SPK05", "그때 왜 그만뒀는지는 저도 정확히는 기억이 안 나네요.", decision="D2")
say("SPK02", "근데 그러면 시설팀에서 한 번 더 봐야 되는 건데 그건 인력이 또 필요해요.",
    kind="concern", decision="D2", rt=-2, note="사후 점검 추가가 별도 인력을 필요로 한다는 우려")
say("SPK01", "음 그것도 그렇네요. 이건 조금 더 생각해봐야 할 것 같아요. 자료를 좀 더 모으고 다시 봅니다.",
    kind="decision", decision="D2", settles="1",
    note="상급자 제안, 아무도 명확히 답하지 않고 데이터 보완 후 재논의로 넘어감", label="d2_settle")
say("SPK03", "그럼 제가 이번 주 지연 건들 중에 원인 특정 가능한 것부터 좀 정리해볼게요.",
    kind="commitment", decision="D2", rt=-1, note="본인 계획으로 지연 원인 데이터 정리를 맡음, 기한 없음")
say("SPK03", "그게 있어야 기준을 늘려야 하는지 사후 점검을 넣어야 하는지 판단이 설 것 같아서요.", decision="D2")
say("SPK01", "네.")
say("SPK02", "칸막이 공사는 지난번 소방 점검 결과 나오면 그거 반영해서 바로 마무리하겠습니다.",
    kind="commitment", decision="D2", rt=-9,
    note="조건부 문장이지만 새 결정 아님, 본인 후속 작업에 대한 개인 커밋먼트", label="d2_conditional_commit")
say("SPK05", "그럼 그것도 저희 쪽 자료랑 같이 맞춰볼게요.",
    kind="ambiguous", decision="D2", rt=-2, note="구체적 계획 없이 자료를 맞춰보겠다는 약한 응답")
say("SPK01", "그럼 다음 주에 자료 보고 다시 얘기하죠.")
say("SPK03", "네 알겠습니다.")

# --- D3: settlement error auto-alert, held over -----------------------------------
say("SPK01", "그다음 정산 오류 알림 얘기인데요, 지금 오류 확인에 평균 며칠 걸리는 거예요?")
say("SPK05", "지금 평균 사흘이요, 근데 이용 건수가 늘어나면 그게 더 늘어날 것 같아서 걱정이에요.", decision="D3")
say("SPK05", "지금도 접수 받고 실제 원인 확인까지 가는 데 손이 많이 가거든요.", decision="D3")
say("SPK05", "접수는 제가 받고 원인 확인은 개발팀에 요청하고 환불 처리는 또 CS팀이라서요.", decision="D3")
say("SPK05", "그 사이에 왔다 갔다 하는 메일이랑 메신저만 해도 꽤 되더라고요.", decision="D3")
say("SPK05", "그러다 보니까 회원님도 언제 처리되냐고 그 중간에 또 문의를 주시고요.", decision="D3")
say("SPK02", "그거 저희 시스템에서 자동으로 처리하는 부분은 없는 거예요?",
    kind="open_question", decision="D3", rt=-2, note="정산 오류 자동 알림 가능 여부를 물음")
say("SPK05", "일부는 되는데 원인 확인 요청이 수동이라 거기서 늘 걸려요.", decision="D3")
say("SPK04", "그거 개발팀 쪽에 자동화 요청은 넣어보신 거예요?",
    kind="open_question", decision="D3", rt=-1, note="자동화 개발 요청 여부를 확인함")
say("SPK05", "넣긴 넣었는데 개발팀 일정이 꽉 차 있어서 정확히 언제 될지는 모른다고 했어요.", decision="D3")
say("SPK05", "저번 달에 넣었는데 아직 답도 못 받은 상태예요.", decision="D3", label="d3_request")
say("SPK05", "다른 지점도 요청이 많이 밀려 있다고 하더라고요.", decision="D3")
say("SPK01", "그 순서는 누가 정하는 거예요?", kind="open_question", decision="D3", rt=-1,
    note="개발팀 요청 처리 순서 결정 주체를 물음")
say("SPK05", "저희만 급한 게 아니라서 순서를 당겨달라고 하기도 좀 애매하고요.", decision="D3")
say("SPK05", "그래도 계속 얘기는 해봐야 할 것 같아요.", decision="D3")
say("SPK02", "아 그게 아니고, 그냥 무작정 기다리기만 하면 접수가 계속 쌓일 수도 있어서 걱정이에요.",
    kind="concern", decision="D3", rt=-1, note="개발팀 응답을 기다리기만 하면 접수가 계속 쌓일 수 있다는 우려")
say("SPK01", "그럼 이건 오늘 뭘 정할 수 있는 상황은 아니네요.")
say("SPK01", "일단 오늘은 정하지 말고 개발팀 답이 오면 다시 봅니다.",
    kind="decision", decision="D3", settles="1",
    note="개발 일정 미확정으로 이번 주는 보류, 답변 오면 재논의", label="d3_settle")
say("SPK05", "그동안은 일단 저 혼자서라도 좀 더 자주 확인해봐야 할 것 같아요.",
    kind="commitment", decision="D3", rt=-1,
    note="본인 계획으로 임시 처리 속도 개선을 맡음, 완곡한 예측형 표현", label="d3_hedge")
say("SPK05", "원인 확인 요청하는 메일이라도 좀 더 자주 보내보려고요.", decision="D3")
say("SPK01", "네 부탁드려요.")
say("SPK04", "개발팀 답 오면 그거 반영해서 CS 응대 스크립트는 바로 고치겠습니다.",
    kind="commitment", decision="D3", rt=-6,
    note="조건부 문장이지만 새 결정 아님, 본인 후속 작업에 대한 개인 커밋먼트", label="d3_conditional_commit")
say("SPK02", "저도 개발팀 쪽에 얘기해서 확인 좀 더 빨리 해달라고 해볼게요.",
    kind="ambiguous", decision="D3", rt=-2, note="구체적 계획 없이 협조를 요청해보겠다는 약한 응답")
say("SPK01", "감사해요, 그거라도 좀 나아지면 좋겠네요.")
say("SPK04", "네 저도 그러길 바라요.")

# --- side talk 2 ---------------------------------------------------------------------
say("SPK02", "그리고 사무실 소방 점검 이번 달까지 다시 해야 되는 거 아세요? 저번에 공지 왔었는데요.", note="사담")
say("SPK05", "아 맞다 까먹고 있었어요. 오늘 안에 확인해야겠네요.", note="사담")
say("SPK05", "안 하면 다음 달부터 과태료 나온다고 했었죠 아마.", note="사담")
say("SPK03", "저도 확인해야 되는데 계속 미루고 있었어요.", note="사담")
say("SPK03", "어디서 신청하는 건지도 가물가물하네요.", note="사담")
say("SPK02", "저는 어제 해놨어요, 별로 안 오래 걸려요.", note="사담")
say("SPK02", "관리사무소 페이지에서 하시면 돼요, 오 분도 안 걸려요.", note="사담")
say("SPK04", "저도 해야겠네요, 알려주셔서 감사해요.", note="사담")
say("SPK05", "저 방금 등록했어요, 진짜 오 분도 안 걸리네요.", note="사담")
say("SPK01", "그건 이따 각자 하시고요, 회의실 소음 민원으로 넘어갈게요.")

# --- D4: meeting room soundproofing complaint, conditional -----------------------
say("SPK01", "회의실 소음 민원 건인데, 최근 들어 항의가 좀 늘었다고 들었어요.", decision="D4")
say("SPK04", "네 두 개 회의실에서 특히 많아요, 근데 저희 기준으로는 정상 범위거든요.",
    kind="concern", decision="D4", rt=-1, note="정상 판정 회의실에 대한 소음 민원이 늘고 있다는 문제 제기")
say("SPK04", "저희가 방음 기준을 표준으로 맞추긴 하는데 회의실 위치마다 벽 구조가 달라서 그런가 봐요.", decision="D4")
say("SPK04", "특히 복도 쪽에 붙은 회의실일수록 그런 민원이 더 많이 들어와요.", decision="D4")
say("SPK04", "화상 회의 하시는 분들은 특히 더 예민하게 느끼시는 것 같고요.", decision="D4")
say("SPK04", "어 전화로 응대하다 보면 같은 얘기를 계속 반복해서 드려야 해서 저도 좀 지치더라고요.", decision="D4")
say("SPK02", "그건 아무래도 건물 구조 자체가 오래된 거라 그럴 수밖에 없긴 해요.", decision="D4")
say("SPK02", "다 전면 시공으로 돌릴 수도 없는 노릇이고요, 예산 한계가 있어요.", decision="D4")
say("SPK02", "전면 흡음재 시공으로 바꾸면 민원은 줄겠지만 시공 비용이 꽤 커요.", decision="D4")
say("SPK02", "어 그거 다 도입하면 이제 이번 분기 시설 예산이 아예 안 남을 수도 있어서 쉽게 정하기 어려워요.", decision="D4")
say("SPK02", "그래서 저는 웬만하면 그 예산은 안 건드리는 쪽으로 가고 싶어요.", decision="D4")
say("SPK05", "근데 민원 비율이 최근 두 달 사이에 두 배 가까이 늘긴 했어요.", decision="D4")
say("SPK05", "음 그중에 절반은 복도 쪽 회의실 관련이고 나머지는 뭐 기타 사유들이에요.", decision="D4")
say("SPK05", "시공 한 번에 드는 비용도 무시 못 할 수준이라 이게 계속 쌓이면 문제예요.", decision="D4")
say("SPK01", "그럼 예약 화면에 방음 한계를 미리 명시하는 건 어때요?", kind="open_question",
    decision="D4", rt=-4, note="방음 한계 사전 고지 방안을 제안하며 의견을 물음")
say("SPK03", "그거 좋은 것 같아요, 근데 문구를 누가 어떻게 쓸지가 문제긴 하네요.", decision="D4")
say("SPK03", "너무 부정적으로 쓰면 그것대로 예약을 안 하실 것 같고 애매하네요.", decision="D4")
say("SPK03", "문구는 그럼 나중에 마케팅 쪽 자문도 좀 받아보는 게 좋을 것 같아요.", decision="D4")
say("SPK04", "저는 근데 그거 명시해도 결국 소음 겪어보시고 나면 똑같이 불만 들어올 것 같아요.",
    kind="concern", decision="D4", rt=-2, note="사전 고지만으로는 체감 불만을 막기 어렵다는 우려")
say("SPK04", "글로 미리 설명드려도 실제로 겪으시는 거랑은 다르다고 하시는 분들이 많거든요.", decision="D4")
say("SPK04", "그래서 저는 사전 고지보다는 다른 방법을 좀 더 찾아봐야 할 것 같아요.", decision="D4")
say("SPK04", "고지는 하되 그거 하나로 다 해결될 거라고는 기대 안 하는 게 맞을 것 같고요.", decision="D4")
say("SPK01", "그럼 화면에 명시하는 거랑 별개로, 전면 시공 대신 복도 쪽 회의실만 먼저 시범 시공하는 건 어때요?",
    decision="D4")
say("SPK01", "전면 시공 다 돌리면 비용이 또 나가는데 시범 시공이 오히려 쌀 수도 있잖아요.", decision="D4")
say("SPK05", "그건 계산을 좀 해봐야 알겠는데, 금액에 따라서는 그게 나을 수도 있을 것 같아요.", decision="D4")
say("SPK05", "전면 흡음재 시공 비용이 대략 삼백만 원 정도니까 그거보다 적으면 시범 시공이 낫겠네요.", decision="D4")
say("SPK03", "아니 근데, 회의실별로 나누면 표가 너무 복잡해지는 거 아니에요?", kind="concern",
    decision="D4", rt=-1, note="회의실별 세분화가 표를 지나치게 복잡하게 만들 수 있다는 우려")
say("SPK05", "근데 회의실마다 이용 패턴이 다 달라서 표로 정리해야 할 것 같아요.", decision="D4")
say("SPK05", "복도 쪽이랑 안쪽이랑도 소음 유입 정도가 다르니까 그것도 따로 잡아야 하고요.", decision="D4")
say("SPK05", "근데 표로 정리해도 결국 담당자가 상황 봐가면서 판단해야 하는 부분은 남을 것 같아요.",
    kind="concern", decision="D4", rt=-1, note="기준표가 있어도 현장 판단 여지가 남는다는 우려")
say("SPK05", "이번 주까지 다 계산해서 표로 정리해서 올려둘게요.", decision="D4")
say("SPK01", "그럼 시범 시공 비용이 전면 시공 비용보다 크면 전면 시공을 먼저 진행하는 방향으로 정리할게요.",
    kind="decision", decision="D4", settles="1",
    note="조건부 결정, 비용 비교 결과에 따라 대응 방식이 갈림", label="d4_settle")
say("SPK05", "그 기준 금액은 이번 주 안에는 계산해서 표로 정리해볼 수 있을 것 같아요.",
    kind="commitment", decision="D4", rt=-1,
    note="본인이 비용 비교 기준표 작성을 맡음, 완곡한 예측형 기한 표현", label="d4_owner")
say("SPK04", "표 나오면 그거 보고 응대 스크립트에 반영하겠습니다.",
    kind="commitment", decision="D4", rt=-1,
    note="조건부 문장이지만 새 결정 아님, 본인 후속 작업에 대한 개인 커밋먼트", label="d4_conditional_commit")
say("SPK01", "좋아요, 그럼 그렇게 진행하죠.")
say("SPK03", "저도 마케팅 쪽에 문구 자문 건 한번 전달해볼게요.",
    kind="ambiguous", decision="D4", rt=-1,
    note="전달, 구체적 계획 없이 마케팅팀에 자문 요청을 전달만 하겠다는 약한 응답")

# --- side talk 3 ---------------------------------------------------------------------
say("SPK03", "아까 그 노쇼 건, 영업 쪽 답은 오늘 온대요?", note="사담")
say("SPK04", "확실친 않은데 내일까지는 준다고 했어요.", note="사담")
say("SPK04", "제가 오전에 한 번 더 물어봐서 재촉은 해뒀어요.", note="사담")
say("SPK04", "그쪽 담당자도 이번엔 좀 곤란한 눈치이긴 하더라고요.", note="사담")
say("SPK05", "저번에도 그렇게 말해놓고 이틀 더 걸렸었죠 아마.", note="사담")
say("SPK05", "그때도 결국 저희가 계속 물어봐야 겨우 답이 왔었잖아요.", note="사담")
say("SPK02", "그러게요, 이번엔 좀 빨리 왔으면 좋겠네요.", note="사담")
say("SPK03", "그 배상 값이 꽤 나가서 저도 좀 신경 쓰이네요.", note="사담")

# --- brief aside: membership tier idea, a peer proposal nobody takes up ----------
say("SPK05", "이건 그냥 제 생각인데요, 이용 시간대별로 회원 등급을 나눠보면 어떨까요?")
say("SPK05", "요즘 등급제 관련 문의가 좀 늘어난 것 같아서 그냥 말씀드려봐요.")
say("SPK05", "다른 공유오피스 브랜드들도 요즘 그런 걸 많이 검토하고 있더라고요.")
say("SPK05", "수익성도 나쁘지 않아서 파트너사들이 꽤 관심 있어 하시는 것 같더라고요.")
say("SPK02", "그거 나쁘지 않은 생각인데 지금 당장 검토할 사람이 없긴 하죠.")
say("SPK01", "그건 나중에 좀 더 얘기해보죠. 오늘은 일단 넘어가고요.")
say("SPK04", "이번 달 등급제 관련 문의만 대충 열 건 정도는 됐던 것 같아요.")
say("SPK04", "음 다들 심야 이용 할인이 궁금하다고 많이들 물어보시더라고요.")
say("SPK01", "그 정도면 확실히 수요가 있긴 하네요.")
say("SPK05", "그렇죠, 그래서 한번 말씀드려본 거예요.")
say("SPK04", "저도 있으면 응대할 때 좀 더 편할 것 같긴 해요.")

# --- D5: weekend staffing backlog, resistance before settling -------------------------
say("SPK01", "마지막으로 주말 운영 인력 얘기를 좀 해야 할 것 같아요. 지금 상태가 어때요?")
say("SPK04", "지금 저희 둘이서 주말 이틀을 다 보고 있는데 다음 달 되면 지점이 하나 더 느니까 감당이 안 될 것 같아요.",
    decision="D5")
say("SPK04", "지금도 사실 빠듯하게 맞추고 있는 상황이라 더 늘면 감당이 안 될 것 같아요.", decision="D5")
say("SPK04", "음 한 명이라도 아프거나 하면 그날은 아예 응대를 못 해요.", decision="D5")
say("SPK04", "저번 주에 저 하루 연차 썼을 때도 그날 응대 못 채우고 다음 날로 밀렸었거든요.", decision="D5")
say("SPK01", "이건 뭐 CS팀에서 알아서 좀 조정해서 맞춰주셔야 할 것 같은데요.",
    decision="D5", label="d5_thrown")
say("SPK04", "저희끼리 조정한다고 되는 문제가 아니에요, 물리적으로 사람이 부족한 거라서요.",
    kind="concern", decision="D5", rt=-1, note="인력 부족은 조정이 아니라 충원이 필요한 문제라는 반대")
say("SPK04", "음 지금도 야근을 거의 매일 하고 있는 상황이라 이 이상은 진짜 무리예요.", decision="D5")
say("SPK04", "저번 주에도 다들 아홉 시 넘어서 퇴근했었잖아요.", decision="D5")
say("SPK04", "음 금요일엔 거의 열 시까지 있었던 것 같아요.", decision="D5")
say("SPK04", "어 이러다 누구 하나 그만둔다고 할까 봐 저도 좀 걱정이에요.", decision="D5")
say("SPK04", "채용 공고는 올려주셨다고 들었는데 지원자가 별로 없다고 하더라고요.", decision="D5")
say("SPK01", "네 저도 그건 알고 있어요, 조건을 좀 조정해야 하나 고민 중이에요.")
say("SPK02", "저희 쪽에서 주말 순찰 도는 인원 한두 명 정도는 잠깐 도와드릴 수 있을 것 같긴 한데요.",
    decision="D5")
say("SPK02", "근데 저희도 CS 경험이 있는 건 아니라서 간단한 것만 도와드릴 수 있어요.", decision="D5")
say("SPK02", "저희 쪽도 주말 순찰이 늘어서 딱히 여유 인력이 있는 건 아니거든요.", decision="D5")
say("SPK02", "그래도 하루에 한두 시간 정도는 빼서 도와드릴 수 있을 것 같아요.", decision="D5")
say("SPK04", "간단한 거라면 어떤 거요?", kind="open_question", decision="D5", rt=-1,
    note="지원 가능한 업무 범위를 구체적으로 물음")
say("SPK02", "방문 접수랑 기본 정보 입력 정도는 저희도 할 수 있어요.", decision="D5")
say("SPK01", "그거 말고 다른 부분도 도움받을 수 있을까요?", kind="open_question", decision="D5", rt=-2,
    note="지원 가능한 업무 범위를 더 넓힐 수 있는지 물음")
say("SPK04", "그 정도만 덜어줘도 저희는 실제 문의 응대에만 집중할 수 있어서 좀 나을 것 같아요.",
    decision="D5")
say("SPK04", "지금은 방문 접수하고 입력하는 데만도 시간이 꽤 걸리거든요.", decision="D5")
say("SPK04", "그것만 넘겨받아도 체감상 꽤 여유가 생길 것 같아요.", decision="D5")
say("SPK04", "한 건당 거의 십오 분씩은 잡아먹고 있었거든요.", decision="D5")
say("SPK04", "그거 스무 건이면 그것만 해도 다섯 시간이라 진짜 크긴 해요.", decision="D5")
say("SPK04", "근데 그것도 교육이 좀 필요한데 지금 그럴 시간이 있을지 모르겠어요.",
    kind="concern", decision="D5", rt=-3, note="지원 인력 교육 시간 확보의 어려움을 지적함")
say("SPK02", "교육은 저희가 다 같이 점심시간에 잠깐 받아도 될 것 같은데요, 오래 안 걸릴 것 같고요.", decision="D5")
say("SPK02", "음 몇 명 정도 필요하신지만 말씀해 주시면 저희 쪽에서 사람은 맞춰볼게요.", decision="D5")
say("SPK01", "그럼 방문 접수랑 입력은 시설팀이 지원하고, CS팀은 실제 문의 응대에 집중하는 방향으로 정리할게요.",
    kind="decision", decision="D5", settles="1",
    note="인력 부족 반발 끝에 업무 일부를 시설팀이 지원하는 방식으로 절충", label="d5_settle")
say("SPK02", "그럼 교육은 제가 점심시간에 받으러 갈게요.",
    kind="ambiguous", decision="D5", rt=-1, note="위임, 구체적 일정 없이 교육을 막연히 받겠다고 함")
say("SPK04", "그럼 저는 짧게 교육 자료만 하나 만들어둘게요.",
    kind="commitment", decision="D5", rt=-1, note="본인 계획으로 교육 자료 제작을 맡음, 기한 없음")
say("SPK01", "감사해요, 그럼 그렇게 준비해주세요.")
say("SPK02", "몇 명 정도 보내드리면 될지는 내일 오전까지 말씀드릴게요.", decision="D5")
say("SPK01", "그럼 이번 주부터 바로 시작해보죠.")
say("SPK04", "네.")
say("SPK02", "네 알겠습니다.")
say("SPK01", "해보고 안 되겠다 싶으면 그때 다시 얘기해주세요.")
say("SPK04", "네 일단 이 주 정도 해보고 말씀드릴게요.")
say("SPK01", "그럼 이 주 뒤에 다시 한번 점검해보죠.")
say("SPK04", "네.")
say("SPK02", "저희도 그때까지 사람 좀 더 익숙해지게 해볼게요.")

# --- closing ---------------------------------------------------------------------
say("SPK01", "음 자 그러면 오늘 정할 건 여기까지 하고 정리만 한 번 하고 마칠게요.")
say("SPK01", "노쇼는 체험 회원 보증금 조정으로 가고, 3호점 오픈은 자료 더 보고 다시 보고요.")
say("SPK01", "정산 오류 알림은 개발팀 답 기다리는 거고, 소음 민원은 비용 비교해서 대응 방식 정합니다.")
say("SPK01", "주말 인력은 시설팀이 방문 접수랑 입력 지원하는 걸로 갑니다.")
say("SPK05", "어젯밤 노쇼 컴플레인 건은 결과 나오면 제가 바로 공유드릴게요.",
    kind="commitment", rt=-4, note="상기, 앞서 나온 노쇼 컴플레인 건을 다시 확인함")
say("SPK01", "네 그렇게 해주세요. 다음 회의는 다음 주 화요일 같은 시간에 하겠습니다.")
say("SPK02", "그때까지는 보증금 기준 정리해서 미리 공유드릴 수 있을 것 같아요.",
    kind="commitment", note="본인 계획, 완곡한 예측형 기한 표현", label="d_close_hedge1")
say("SPK04", "저는 이 주 뒤에 지원 인력 운영 결과 정리해서 올려두겠습니다.")
say("SPK05", "저는 소음 민원 비용표 정리해서 올려두겠습니다.")
say("SPK04", "저도 오늘 나온 것들은 정리는 해서 CS 쪽에 공유는 해둘 수 있을 것 같아요.",
    kind="commitment", note="본인 계획으로 CS팀 공유를 맡음, 완곡한 예측형 표현", label="d_close_hedge2")
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
        "statement": "무료 체험 회원 노쇼에 대해서만 보증금을 걸고, 정회원 정책과 유료 전환은 그대로 유지한다.",
        "owner": "SPK02",
        "due": "다음 주 초(보증금 기준 작성 기준)",
        "due_as_said": "다음 주 초까지는",
        "evidence_rows": ("d1_settle", "d1_owner", "d1_due"),
        "note": "무료 체험 폐지가 계약 조건 문제로 두 번째로 무산된 뒤, 체험 회원 보증금 도입으로 절충됨",
    },
    {
        "decision_id": "D2",
        "settles_row": "d2_settle",
        "statement": "오픈 승인 기준에 소방 점검 완료 여부를 추가하자는 팀장 제안에 아무도 명확히 답하지 않은 채, 원인 자료를 더 모은 뒤 다시 논의하기로 한다.",
        "owner": "SPK03",
        "due": "",
        "due_as_said": "",
        "evidence_rows": ("d2_proposal", "d2_settle"),
        "note": "지역별 행정 처리 차이가 기준 추가만으로는 잡히지 않을 수 있다는 우려가 오간 채 자료 보완으로 유보됨",
    },
    {
        "decision_id": "D3",
        "settles_row": "d3_settle",
        "statement": "정산 오류 자동 알림은 개발팀 일정이 확정되지 않아 이번 주에는 정하지 않고 답변이 오면 다시 논의한다.",
        "owner": "",
        "due": "개발팀 답변 이후",
        "due_as_said": "개발팀 답 오면 다시",
        "evidence_rows": ("d3_settle", "d3_request"),
        "note": "자동화 요청은 이미 넣었으나 개발 일정이 꽉 차 있어 보류됨",
    },
    {
        "decision_id": "D4",
        "settles_row": "d4_settle",
        "statement": "회의실 소음 민원은 시범 시공 비용이 전면 흡음재 시공 비용보다 클 경우 전면 시공을 먼저 진행하는 방식으로 대응한다.",
        "owner": "SPK05",
        "due": "이번 주 안(기준표 작성 기준)",
        "due_as_said": "이번 주 안에는",
        "evidence_rows": ("d4_settle", "d4_owner"),
        "note": "사전 고지만으로는 체감 불만을 막기 어렵다는 우려를 거쳐 비용 비교 기준의 조건부 대응으로 확정됨",
    },
    {
        "decision_id": "D5",
        "settles_row": "d5_settle",
        "statement": "CS팀 인력 부족은 시설팀이 방문 접수와 기본 정보 입력을 지원하고, CS팀은 실제 문의 응대에 집중하는 방식으로 절충한다.",
        "owner": "SPK02",
        "due": "",
        "due_as_said": "",
        "evidence_rows": ("d5_thrown", "d5_settle"),
        "note": "CS팀에 통째로 떠넘겨졌다가 인력 부족 반발을 거쳐 시설팀 일부 업무 지원으로 절충되어 확정됨",
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
