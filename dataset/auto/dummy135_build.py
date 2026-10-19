"""Build DUMMY_135 -- freelancer/gig-worker matching platform ("긱브릿지") ops team meeting, training data.

Fifth meeting in the DUMMY_131-140 batch. Same two target patterns; hedges
varied ("-ㄹ지도 모르겠어요", "-아 놓으려고요", "-면 될 것 같긴 해요") and
compound-conditional shapes varied ("-확인되면 그거 갖고", "-넘어오면 바로").

Everything invented: company, people, numbers.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _dummy_common import Builder  # noqa: E402

MEETING = "DUMMY_135"
ROLE = {"SPK01": "PM", "SPK02": "Ops", "SPK03": "CS", "SPK04": "Trust", "SPK05": "Finance"}
SPEAKERS = {
    "meeting": MEETING,
    "title": "긱브릿지 프리랜서 매칭 운영팀 격주 점검 회의",
    "type": "team",
    "position_order": ["사원", "주임", "대리", "과장", "차장", "부장", "이사", "대표"],
    "speakers": [
        {"speaker": "SPK01", "name": "표시우", "team": "긱브릿지 운영팀", "job": "PM", "position": "과장", "title": "팀장"},
        {"speaker": "SPK02", "name": "감나영", "team": "긱브릿지 운영팀", "job": "Ops", "position": "대리", "title": ""},
        {"speaker": "SPK03", "name": "천도율", "team": "긱브릿지 운영팀", "job": "CS", "position": "주임", "title": ""},
        {"speaker": "SPK04", "name": "옥지안", "team": "긱브릿지 운영팀", "job": "Trust", "position": "사원", "title": ""},
        {"speaker": "SPK05", "name": "위건모", "team": "긱브릿지 운영팀", "job": "Finance", "position": "대리", "title": ""},
    ],
}

b = Builder(MEETING, ROLE, SPEAKERS)
say = b.say

# --- opening ---
say("SPK03", "음 시작 전에 하나만요, 어제 밤에 정산 지연 문의가 갑자기 몰렸어요.")
say("SPK03", "어 프로젝트 끝났는데 입금이 안 됐다는 프리랜서분들이 한 아홉 분 정도 한꺼번에 들어왔어요.")
say("SPK03", "그거 확인해보니까 검수 승인이 중간에 걸려 있었던 것 같더라고요.")
say("SPK04", "어 그 건 저도 아침에 봤어요, 그 승인 큐가 절반쯤 밀려 있었던 것 같아요.")
say("SPK01", "음 그건 이따 정산 얘기할 때 다시 짚고 갈게요, 오늘은 네 가지만 볼게요.")
say("SPK01", "음 프리랜서 노쇼 페널티, 신규 카테고리 오픈 일정, 정산 승인 지연, 그리고 프로필 어뷰징이요.")
say("SPK01", "음 일단 그 순서로 가려는데 급한 거 먼저 있으면 말씀해 주세요.")
say("SPK01", "오늘도 회의록은 따로 안 쓰고 정리된 것만 이따 채널에 올려둘게요.",
    kind="commitment", note="본인이 회의록 대신 정리를 맡겠다고 함")
say("SPK01", "그냥 저번처럼 다 받아 적다가 뭐가 정해졌는지 흐려지느니 그게 낫겠더라고요.")
say("SPK05", "음 일단 네 저도 그 방식이 편해요, 저번 회의록은 다시 봐도 헷갈리더라고요.")
say("SPK01", "음 그럼 도율 씨가 정리한 노쇼 현황부터 볼까요.",
    kind="open_question", note="논의 순서를 정하며 데이터 공유를 요청함")
say("SPK03", "음 네 이번 달 프리랜서 노쇼가 지난달보다 꽤 늘었어요,")
say("SPK03", "어 특히 신규 등록 프리랜서 쪽에서 노쇼가 많이 나오고 있고요.")
say("SPK03", "그냥 경력 프리랜서랑 비교하면 거의 세 배 가까이 차이가 나는 수준이에요.")

# --- D1: no-show penalty, false agreement inside ---
say("SPK03", "그리고 이번에 노쇼 문제가 좀 커졌어요.", decision="D1")
say("SPK03", "음 작년 이맘때는 노쇼율이 한 오 퍼센트 정도였거든요.", decision="D1")
say("SPK03", "아 오 퍼센트가 아니라 칠 퍼센트네요. 작년 자료랑 재작년 자료를 헷갈렸어요.", decision="D1")
say("SPK03", "음 어쨌든 그때보다 확실히 더 늘어난 건 맞아요.", decision="D1")
say("SPK03", "어 요즘 신규 등록은 늘었는데 실제 첫 프로젝트 완료율은 그대로라서 그런 것 같아요.", decision="D1")
say("SPK03", "음 특히 그중에 이번 주 노쇼 두 건 때문에 클라이언트 두 분이 일정을 못 맞춰서 컴플레인까지 나갔어요.", decision="D1")
say("SPK03", "음 그게 이번 달 전체 컴플레인의 한 삼십 퍼센트나 차지하는 거라 타격이 좀 크네요.", decision="D1")
say("SPK03", "어 이 상태로 가면 다음 달엔 재의뢰율에도 영향 갈 것 같고요.", decision="D1")
say("SPK05", "어 그건 저도 봤어요, 그 두 건 매칭 데이터가 유독 안 좋더라고요.", decision="D1")
say("SPK05", "음 저희 말고 다른 프리랜서 커뮤니티에도 비슷한 후기가 올라와 있던데요.", decision="D1")
say("SPK05", "어 저번에 CS 통계 볼 때도 그런 얘기가 있긴 했었어요.", decision="D1")
say("SPK05", "어 저희가 그때 좀 더 서둘러서 봤어야 했나 싶기도 하고요, 아쉽네요.", decision="D1")
say("SPK02", "음 그럼 지금 페널티는 그냥 다음 매칭 하루 제한인 거죠? 그게 전부예요?",
    kind="open_question", decision="D1", rt=-1, note="현재 페널티 수위를 물음")
say("SPK02", "어 일단 지금 체제로는 신규 등록 쪽은 딱히 잃을 게 없어서 그런 것 같거든요.", decision="D1")
say("SPK01", "음 그 얘기는 카테고리 쪽에서 이따 다시 할게요, 일단 노쇼부터 정리하고요.")
say("SPK01", "어 그럼 지금 페널티를 그대로 두면 신규 등록 노쇼가 계속 늘어난다는 얘기인데요.", decision="D1")
say("SPK01", "음 이번 주 안에 페널티를 좀 더 세게 가야 될 것 같은데 다들 어떻게 보세요?", decision="D1")
say("SPK02", "음 저는 일단 등록 절차는 그대로 두고 노쇼 시 평판 점수만 좀 더 걸어두는 게 낫지 않을까 싶어요.",
    decision="D1")
say("SPK02", "음 근데 평판 점수를 걸면 신규 등록 자체가 줄어들 수도 있거든요.", decision="D1")
say("SPK02", "음 지금 당장 신규 유입이 중요한데 그걸 막을 여유는 없을 것 같아서요.", decision="D1")
say("SPK03", "음 근데 평판 점수를 걸면 그만큼 이의 신청도 늘어나는 거라서요.", kind="concern",
    decision="D1", rt=-2, note="평판 점수 도입이 CS 이의신청 증가로 이어진다는 우려")
say("SPK03", "음 지금도 문의량이 그렇게 여유 있는 편은 아니거든요.", decision="D1")
say("SPK03", "어 안내를 새로 만들지 않는 이상 문의 증가분은 그대로 저희 부담이에요.", decision="D1")
say("SPK01", "그럼 아예 신규 등록 절차 자체를 없애고 전부 심사제로 돌리는 쪽으로 가죠! 그게 더 낫겠네요.",
    decision="D1", note="번복, 합의된 것처럼 보였다가 다음 턴에서 뒤집힘", label="d1_false")
say("SPK02", "음 네 그게 나을 것 같긴 해요.", decision="D1")
say("SPK04", "아 잠깐만요, 심사제 전환은 저희 신뢰팀 쪽 처리 용량이랑 계약된 SLA에 맞는지 먼저 확인해야 되는데요.",
    kind="concern", decision="D1", rt=-2, note="심사제 전환이 신뢰팀 용량/SLA와 맞는지 사전 확인이 필요함을 지적")
say("SPK01", "음 그때 그 SLA는 어떻게 걸려 있는 거였죠?", kind="open_question", decision="D1", rt=-1,
    note="과거 SLA를 어떻게 확인했는지 물음")
say("SPK04", "저번에 급하게 심사제 테스트했던 카테고리는 결국 등록 자체가 너무 줄어서 두 달 만에 되돌렸잖아요.", decision="D1")
say("SPK04", "어 그때 재전환 비용이랑 심사 인력비가 더 나가서 오히려 손해였고요.", decision="D1")
say("SPK04", "음 그 카테고리는 SLA 조건부터가 저희 기준이랑 많이 달랐던 걸로 기억해요.", decision="D1")
say("SPK04", "음 그러니까 심사제를 하더라도 최소 한두 달은 테스트 기간을 잡아야 할 것 같아요.", decision="D1")
say("SPK04", "음 그 기간 동안은 오히려 신규 유입 목표 숫자가 흔들리기도 하고요.", decision="D1")
say("SPK01", "아 맞다, 그때 그 일이 있었죠.")
say("SPK01", "음 그럼 심사제는 테스트 기간이 필요하니까 이번 달에는 못 쓰겠네요.", decision="D1")
say("SPK05", "어 그러면 결국 남은 건 노쇼 평판 점수 조정밖에 없는 것 같은데요.", decision="D1")
say("SPK05", "어 근데 그것도 사실 임시방편이라는 느낌은 있어서 좀 걱정이긴 해요.",
    kind="concern", decision="D1", rt=-1, note="평판 점수 조정이 근본 해결책은 아니라는 우려")
say("SPK02", "음 점수를 전체로 다 걸지 말고 신규 등록 쪽만 먼저 걸어보면 어때요?", decision="D1")
say("SPK02", "어 신규 쪽이 원래 제일 심했으니까 거기만 잡아도 효과가 꽤 있을 것 같아요.", decision="D1")
say("SPK05", "음 그 정도면 등록 이탈 폭이 한 오 퍼센트 정도라서 감당은 충분히 될 것 같아요.", decision="D1")
say("SPK05", "음 경력 프리랜서 쪽은 지금도 노쇼가 거의 없어서 괜찮을 것 같고요.", decision="D1")
say("SPK01", "그럼 경력 프리랜서는 그대로 가고 신규 등록 평판 점수만 조정하는 방향이네요.")
say("SPK02", "음 네 맞아요.")
say("SPK01", "그럼 신규 등록 노쇼만 평판 점수 걸고 나머지는 그대로 두는 걸로 정리할게요.",
    kind="decision", decision="D1", settles="1",
    note="심사제 전환은 SLA 문제로 무산된 뒤 신규 등록 평판 점수 도입으로 절충", label="d1_settle")
say("SPK02", "일단 점수 기준이랑 회복 조건은 제가 다음 주 초까지는 정리해서 공유할 수 있을 것 같아요.",
    kind="commitment", decision="D1", rt=-1,
    note="본인이 점수 기준 작성을 맡음, 완곡한 예측형 기한 표현", label="d1_owner")
say("SPK03", "저도 그거 CS 스크립트 반영은 필요하면 같이 봐드릴 수는 있어요.",
    kind="ambiguous", decision="D1", rt=-1, note="구체적 계획 없이 필요하면 돕겠다는 약한 응답")
say("SPK02", "음 얼마나 걸어야 이탈이 안 커질지는 신뢰팀이랑도 얘기해봐야 알 것 같아요.", decision="D1",
    label="d1_due")
say("SPK02", "음 너무 많이 걸면 저희 쪽 유입이 줄어드니까 선을 잘 잡아야 할 것 같아요.", decision="D1")
say("SPK02", "지난달 조정 폭보다 이틀 앞당겨서 이번 주 안에 먼저 제안해보려고요.", decision="D1")
say("SPK01", "그럼 그 결과 보고 다음 달에 목표 노쇼율을 다시 잡죠.")
say("SPK03", "네.")
say("SPK03", "저는 그동안 등록 상담 스크립트라도 한번 다시 짜보려고요.",
    kind="commitment", decision="D1", note="본인 계획으로 상담 스크립트 재검토를 시도함, 기한 없음")
say("SPK03", "혹시 첫 프로젝트 완료율을 따로 더 끌어올릴 방법도 이번 주에 알아볼게요.", decision="D1")
say("SPK05", "음.")
say("SPK03", "넵.")

# --- side talk 1 ---
say("SPK03", "그러고 보니 1층에 새로 생긴 그 도시락 가게 가보셨어요? 줄이 길더라고요.", note="사담")
say("SPK02", "저 아직 못 가봤어요. 맛은 어때요?", note="사담")
say("SPK03", "괜찮았어요, 근데 생각보다 좀 비싸더라고요.", note="사담")
say("SPK03", "기본 도시락이 팔천오백 원 넘던데요.", note="사담")
say("SPK05", "저도 한번 가봐야겠네요, 요즘 마땅한 데가 없어서 좀 아쉬웠거든요.", note="사담")
say("SPK05", "자주 가던 데가 얼마 전에 갑자기 문을 닫아서요.", note="사담")
say("SPK04", "요즘 임대료가 워낙 비싸다 보니까 다들 버티기 힘든가 봐요.", note="사담")
say("SPK02", "맞아요, 저희 건물 상가도 그런 얘기 많이 들려요.", note="사담")
say("SPK02", "예전엔 이 정도는 아니었던 것 같은데 요즘 부쩍 심해진 것 같아요.", note="사담")
say("SPK05", "그러게요.", note="사담")
say("SPK04", "음 저도 그 얘기 들었어요, 확실히 다들 힘드시겠어요.", note="사담")
say("SPK01", "그 얘기는 이따 마저 하고요, 신규 카테고리 오픈 일정 쪽으로 넘어갈게요.")

# --- D2: new category launch, lead proposal unanswered + conditional commitment ---
say("SPK01", "지난주에 신규 카테고리 오픈 준비 상황 공유해 달라고 요청했었잖아요. 그것부터 볼게요.",
    decision="D2")
say("SPK02", "네 그중에 심사 기준 쪽이 좀 늦어지고 있다고 얘기가 나왔어요.", decision="D2")
say("SPK02", "포트폴리오 검증 항목이 절반 정도밖에 안 끝났더라고요.", decision="D2")
say("SPK02", "오픈일 맞추려면 이번 주 안에는 마무리돼야 한다고 하시면서 다들 걱정을 많이 하세요.", decision="D2")
say("SPK02", "그것도 분야마다 사정이 달라서 생각보다 관리가 복잡해요.", decision="D2")
say("SPK02", "심사 담당자도 처음엔 그냥 넘어가려다가 레퍼런스 검증 늦어지니까 그제야 신경 쓰시더라고요.", decision="D2")
say("SPK02", "다른 한 건은 세무 신고 연동 일정이 밀렸다고 하셨는데 그건 아직 협의 중이에요.", decision="D2")
say("SPK02", "법무 쪽에서 서류까지 보내주셨는데 저희가 봐도 처리 기간이 좀 길긴 하더라고요.", decision="D2")
say("SPK01", "지금 오픈 승인 기준이 심사 완료율 확인해서 결정하는 게 전부인 거죠?", decision="D2")
say("SPK04", "네 근데 그 기준으로는 세무 연동 여력까지는 잘 안 잡혀요.", decision="D2")
say("SPK04", "그 카테고리도 저희가 볼 때는 완료율은 괜찮았거든요.", decision="D2")
say("SPK04", "기록 봐도 완료율 기준 통과로 표시돼 있었고 저도 그때 직접 확인했었어요.", decision="D2")
say("SPK04", "그래서 이게 심사 문제인지 행정 처리 문제인지가 좀 헷갈려요.", decision="D2")
say("SPK04", "비슷한 사례가 더 있는지 한번 찾아봐야 할 것 같고요.", decision="D2")
say("SPK04", "근데 그게 세무 연동까지 다 확인하면 승인이 너무 오래 걸릴 수도 있어요.", decision="D2")
say("SPK01", "그러면 제가 보기엔 오픈 승인 기준에 세무 신고 연동 완료 여부도 같이 넣는 게 맞을 것 같은데요.",
    decision="D2", note="상급자 제안, 아무도 명확히 답하지 않고 데이터 보완 후 재논의로 넘어감", label="d2_proposal")
say("SPK04", "그렇게 하면 승인 절차가 더 오래 걸리는 거 아닌가요?",
    kind="open_question", decision="D2", rt=-1, note="승인 기준 추가가 처리 속도에 미치는 영향을 물음")
say("SPK04", "지금도 일정이 빠듯한데 항목을 늘리면 감당이 안 될 것 같아서요.", decision="D2")
say("SPK01", "그건 이따 인력 얘기할 때 같이 볼게요, 지금은 기준만이요.")
say("SPK01", "일단 뭐가 맞는 방향인지부터 정하고 일정은 그다음에 맞춰야죠.")
say("SPK02", "근데 기준을 늘려도 그 세무 연동 같은 건 분야마다 달라서 꼭 잡힌다는 보장은 없어요.",
    kind="concern", decision="D2", rt=-4, note="승인 기준 추가만으로는 분야별 행정 차이를 못 잡을 수 있다는 우려")
say("SPK02", "저희가 볼 때는 그냥 완료율만 보고 판단하는 거라서요.", decision="D2")
say("SPK05", "그럼 기준을 늘리는 것보다 오픈 이후에 사후 심사를 한 번 더 하는 게 낫지 않을까요?", decision="D2")
say("SPK05", "오픈하고 나서 실제 지연이 어땠는지 보면 그게 더 정확할 것 같아요.", decision="D2")
say("SPK05", "저희가 예전에 그렇게 한 적이 있었는데 그때는 문제 적발률이 꽤 높았거든요.", decision="D2")
say("SPK05", "그때 기억으로는 한 팔 퍼센트 정도는 그 단계에서 추가로 걸러졌었어요.", decision="D2")
say("SPK05", "그때 왜 그만뒀는지는 저도 정확히는 기억이 안 나네요.", decision="D2")
say("SPK02", "근데 그러면 신뢰팀에서 한 번 더 봐야 되는 건데 그건 인력이 또 필요해요.",
    kind="concern", decision="D2", rt=-2, note="사후 심사 추가가 별도 인력을 필요로 한다는 우려")
say("SPK01", "음 그것도 그렇네요. 이건 조금 더 생각해봐야 할 것 같아요. 자료를 좀 더 모으고 다시 봅니다.",
    kind="decision", decision="D2", settles="1",
    note="상급자 제안, 아무도 명확히 답하지 않고 데이터 보완 후 재논의로 넘어감", label="d2_settle")
say("SPK02", "그럼 제가 이번 주 지연 건들 중에 원인 특정 가능한 것부터 좀 정리해볼게요.",
    kind="commitment", decision="D2", rt=-1, note="본인 계획으로 지연 원인 데이터 정리를 맡음, 기한 없음")
say("SPK02", "그게 있어야 기준을 늘려야 하는지 사후 심사를 넣어야 하는지 판단이 설 것 같아서요.", decision="D2")
say("SPK01", "네.")
say("SPK04", "포트폴리오 검증은 지난번 세무 연동 확인되면 그거 갖고 바로 마무리하겠습니다.",
    kind="commitment", decision="D2", rt=-9,
    note="조건부 문장이지만 새 결정 아님, 본인 후속 작업에 대한 개인 커밋먼트", label="d2_conditional_commit")
say("SPK05", "그럼 그것도 저희 쪽 자료랑 같이 맞춰볼게요.",
    kind="ambiguous", decision="D2", rt=-2, note="구체적 계획 없이 자료를 맞춰보겠다는 약한 응답")
say("SPK01", "그럼 다음 주에 자료 보고 다시 얘기하죠.")
say("SPK02", "네 알겠습니다.")

# --- D3: settlement approval delay, held over ---
say("SPK01", "그다음 정산 승인 지연 얘기인데요, 지금 확인에 평균 며칠 걸리는 거예요?")
say("SPK04", "음 지금 평균 사흘이요, 근데 프로젝트 건수가 늘어나면 그게 더 늘어날 것 같아서 걱정이에요.", decision="D3")
say("SPK04", "지금도 접수 받고 실제 검수 완료까지 가는 데 손이 많이 가거든요.", decision="D3")
say("SPK04", "접수는 제가 받고 검수 확인은 개발팀에 요청하고 승인은 또 재무팀이라서요.", decision="D3")
say("SPK04", "그 사이에 왔다 갔다 하는 메일이랑 메신저만 해도 꽤 되더라고요.", decision="D3")
say("SPK04", "그러다 보니까 프리랜서님도 언제 들어오냐고 그 중간에 또 문의를 주시고요.", decision="D3")
say("SPK02", "그거 저희 시스템에서 자동으로 처리하는 부분은 없는 거예요?",
    kind="open_question", decision="D3", rt=-2, note="정산 승인 자동화 가능 여부를 물음")
say("SPK04", "일부는 되는데 예외 케이스 확인이 수동이라 거기서 늘 걸려요.", decision="D3")
say("SPK03", "그거 개발팀 쪽에 자동화 요청은 넣어보신 거예요?",
    kind="open_question", decision="D3", rt=-1, note="자동화 개발 요청 여부를 확인함")
say("SPK04", "넣긴 넣었는데 개발팀 일정이 꽉 차 있어서 정확히 언제 될지는 모른다고 했어요.", decision="D3")
say("SPK04", "저번 달에 넣었는데 아직 답도 못 받은 상태예요.", decision="D3", label="d3_request")
say("SPK04", "어 다른 서비스도 요청이 많이 밀려 있다고 하더라고요.", decision="D3")
say("SPK01", "그 순서는 누가 정하는 거예요?", kind="open_question", decision="D3", rt=-1,
    note="개발팀 요청 처리 순서 결정 주체를 물음")
say("SPK04", "저희만 급한 게 아니라서 순서를 당겨달라고 하기도 좀 애매하고요.", decision="D3")
say("SPK04", "그래도 계속 얘기는 해봐야 할 것 같아요.", decision="D3")
say("SPK02", "아 그게 아니고, 그냥 무작정 기다리기만 하면 접수가 계속 쌓일 수도 있어서 걱정이에요.",
    kind="concern", decision="D3", rt=-1, note="개발팀 응답을 기다리기만 하면 접수가 계속 쌓일 수 있다는 우려")
say("SPK01", "그럼 이건 오늘 뭘 정할 수 있는 상황은 아니네요.")
say("SPK01", "일단 오늘은 정하지 말고 개발팀 답이 오면 다시 봅니다.",
    kind="decision", decision="D3", settles="1",
    note="개발 일정 미확정으로 이번 주는 보류, 답변 오면 재논의", label="d3_settle")
say("SPK04", "그동안은 일단 저 혼자서라도 승인 큐를 좀 더 자주 확인해봐야 할지도 모르겠어요.",
    kind="commitment", decision="D3", rt=-1,
    note="본인 계획으로 임시 처리 속도 개선을 맡음, 완곡한 예측형 표현", label="d3_hedge1")
say("SPK04", "검수 확인 요청하는 메일이라도 좀 더 자주 보내보려고요.", decision="D3")
say("SPK01", "네 부탁드려요.")
say("SPK03", "개발팀 답 넘어오면 바로 CS 응대 스크립트 고치겠습니다.",
    kind="commitment", decision="D3", rt=-6,
    note="조건부 문장이지만 새 결정 아님, 본인 후속 작업에 대한 개인 커밋먼트", label="d3_conditional_commit")
say("SPK02", "저도 개발팀 쪽에 얘기해서 확인 좀 더 빨리 해달라고 해볼게요.",
    kind="ambiguous", decision="D3", rt=-2, note="구체적 계획 없이 협조를 요청해보겠다는 약한 응답")
say("SPK01", "감사해요, 그거라도 좀 나아지면 좋겠네요.")
say("SPK03", "네 저도 그러길 바라요.")

# --- side talk 2 ---
say("SPK04", "그리고 사무실 소방 점검 이번 달까지 다시 해야 되는 거 아세요? 저번에 공지 왔었는데요.", note="사담")
say("SPK03", "아 맞다 까먹고 있었어요. 오늘 안에 확인해야겠네요.", note="사담")
say("SPK03", "안 하면 다음 달부터 과태료 나온다고 했었죠 아마.", note="사담")
say("SPK02", "저도 확인해야 되는데 계속 미루고 있었어요.", note="사담")
say("SPK02", "어디서 신청하는 건지도 가물가물하네요.", note="사담")
say("SPK04", "저는 어제 해놨어요, 별로 안 오래 걸려요.", note="사담")
say("SPK04", "관리사무소 페이지에서 하시면 돼요, 오 분도 안 걸려요.", note="사담")
say("SPK03", "저도 해야겠네요, 알려주셔서 감사해요.", note="사담")
say("SPK01", "그건 이따 각자 하시고요, 프로필 어뷰징으로 넘어갈게요.")

# --- D4: profile abuse response, conditional cost decision ---
say("SPK01", "프로필 어뷰징 건인데, 최근 들어 의심 사례가 좀 늘었다고 들었어요.", decision="D4")
say("SPK03", "음 네 두 개 분야에서 특히 많아요, 근데 저희 기준으로는 아슬아슬하게 정상 범위거든요.",
    kind="concern", decision="D4", rt=-1, note="정상 판정 분야에 어뷰징 의심 프로필이 늘고 있다는 문제 제기")
say("SPK03", "필터링 기준을 표준으로 맞추긴 하는데 분야마다 프로필 패턴이 달라서 그런가 봐요.", decision="D4")
say("SPK03", "특히 인기 분야일수록 그런 프로필이 더 많이 올라와요.", decision="D4")
say("SPK03", "클라이언트분들은 특히 더 예민하게 느끼시는 것 같고요.", decision="D4")
say("SPK03", "어 전화로 응대하다 보면 같은 얘기를 계속 반복해서 드려야 해서 저도 좀 지치더라고요.", decision="D4")
say("SPK05", "그건 아무래도 필터링 시스템 자체가 오래된 거라 그럴 수밖에 없긴 해요.", decision="D4")
say("SPK05", "다 새 시스템으로 돌릴 수도 없는 노릇이고요, 예산 한계가 있어요.", decision="D4")
say("SPK05", "전면 재구축으로 바꾸면 어뷰징은 줄겠지만 개발 비용이 꽤 커요.", decision="D4")
say("SPK05", "그거 다 도입하면 이제 이번 분기 개발 예산이 아예 안 남을 수도 있어서 쉽게 정하기 어려워요.", decision="D4")
say("SPK05", "그래서 저는 웬만하면 그 예산은 안 건드리는 쪽으로 가고 싶어요.", decision="D4")
say("SPK04", "근데 의심 비율이 최근 두 달 사이에 두 배 가까이 늘긴 했어요.", decision="D4")
say("SPK04", "음 그중에 절반은 인기 분야 관련이고 나머지는 뭐 기타 사유들이에요.", decision="D4")
say("SPK04", "재구축 한 번에 드는 비용도 무시 못 할 수준이라 이게 계속 쌓이면 문제예요.", decision="D4")
say("SPK01", "그럼 프로필 등록 화면에 실제 경력 인증 절차를 미리 명시하는 건 어때요?", kind="open_question",
    decision="D4", rt=-4, note="경력 인증 사전 고지 방안을 제안하며 의견을 물음")
say("SPK02", "그거 좋은 것 같아요, 근데 문구를 누가 어떻게 쓸지가 문제긴 하네요.", decision="D4")
say("SPK02", "너무 딱딱하게 쓰면 그것대로 등록을 안 하실 것 같고 애매하네요.", decision="D4")
say("SPK02", "문구는 그럼 나중에 마케팅 쪽 자문도 좀 받아보는 게 좋을 것 같아요.", decision="D4")
say("SPK03", "저는 근데 그거 명시해도 결국 어뷰징하시는 분들은 똑같이 우회할 것 같아요.",
    kind="concern", decision="D4", rt=-2, note="사전 고지만으로는 어뷰징을 막기 어렵다는 우려")
say("SPK03", "글로 미리 설명드려도 작정하고 하시는 분들이랑은 다르다고 하시는 CS도 많거든요.", decision="D4")
say("SPK03", "그래서 저는 사전 고지보다는 다른 방법을 좀 더 찾아봐야 할 것 같아요.", decision="D4")
say("SPK03", "고지는 하되 그거 하나로 다 해결될 거라고는 기대 안 하는 게 맞을 것 같고요.", decision="D4")
say("SPK01", "그럼 화면에 명시하는 거랑 별개로, 전면 재구축 대신 인기 분야만 먼저 시범 필터링 붙이는 건 어때요?",
    decision="D4")
say("SPK01", "전면 재구축 다 돌리면 비용이 또 나가는데 시범 필터링이 오히려 쌀 수도 있잖아요.", decision="D4")
say("SPK04", "그건 계산을 좀 해봐야 알겠는데, 금액에 따라서는 그게 나을 수도 있을 것 같아요.", decision="D4")
say("SPK04", "전면 재구축 비용이 대략 사백이십만 원 정도니까 그거보다 적으면 시범 필터링이 낫겠네요.", decision="D4")
say("SPK02", "아니 근데, 분야별로 나누면 표가 너무 복잡해지는 거 아니에요?", kind="concern",
    decision="D4", rt=-1, note="분야별 세분화가 표를 지나치게 복잡하게 만들 수 있다는 우려")
say("SPK04", "근데 분야마다 프로필 패턴이 다 달라서 표로 정리해야 할 것 같아요.", decision="D4")
say("SPK04", "인기 분야랑 비인기 분야랑도 의심 비율이 다르니까 그것도 따로 잡아야 하고요.", decision="D4")
say("SPK04", "근데 표로 정리해도 결국 담당자가 상황 봐가면서 판단해야 하는 부분은 남을 것 같아요.",
    kind="concern", decision="D4", rt=-1, note="기준표가 있어도 현장 판단 여지가 남는다는 우려")
say("SPK04", "이번 주까지 다 계산해서 표로 정리해서 올려둘게요.", decision="D4")
say("SPK01", "그럼 시범 필터링 비용이 전면 재구축 비용보다 크면 전면 재구축을 먼저 진행하는 방향으로 정리할게요.",
    kind="decision", decision="D4", settles="1",
    note="조건부 결정, 비용 비교 결과에 따라 대응 방식이 갈림", label="d4_settle")
say("SPK04", "그 기준 금액은 이번 주 안에는 계산해서 표로 정리해볼 수 있을 것 같아요.",
    kind="commitment", decision="D4", rt=-1,
    note="본인이 비용 비교 기준표 작성을 맡음, 완곡한 예측형 기한 표현", label="d4_owner")
say("SPK03", "표 나오면 그거 보고 응대 스크립트에 반영하겠습니다.",
    kind="commitment", decision="D4", rt=-1,
    note="조건부 문장이지만 새 결정 아님, 본인 후속 작업에 대한 개인 커밋먼트", label="d4_conditional_commit")
say("SPK01", "좋아요, 그럼 그렇게 진행하죠.")
say("SPK02", "저도 마케팅 쪽에 문구 자문 건 한번 전달해볼게요.",
    kind="ambiguous", decision="D4", rt=-1,
    note="전달, 구체적 계획 없이 마케팅팀에 자문 요청을 전달만 하겠다는 약한 응답")

# --- side talk 3 ---
say("SPK02", "아까 그 노쇼 건, 신뢰팀 쪽 답은 오늘 온대요?", note="사담")
say("SPK04", "확실친 않은데 내일까지는 준다고 했어요.", note="사담")
say("SPK04", "제가 오전에 한 번 더 물어봐서 재촉은 해뒀어요.", note="사담")
say("SPK04", "그쪽 담당자도 이번엔 좀 곤란한 눈치이긴 하더라고요.", note="사담")
say("SPK05", "저번에도 그렇게 말해놓고 이틀 더 걸렸었죠 아마.", note="사담")
say("SPK05", "그때도 결국 저희가 계속 물어봐야 겨우 답이 왔었잖아요.", note="사담")
say("SPK02", "그러게요, 이번엔 좀 빨리 왔으면 좋겠네요.", note="사담")

# --- brief aside: subscription tier idea, a peer proposal nobody takes up ---
say("SPK05", "이건 그냥 제 생각인데요, 활동 등급별로 수수료를 나눠보면 어떨까요?")
say("SPK05", "요즘 등급제 관련 문의가 좀 늘어난 것 같아서 그냥 말씀드려봐요.")
say("SPK05", "다른 매칭 플랫폼들도 요즘 그런 걸 많이 검토하고 있더라고요.")
say("SPK05", "수익성도 나쁘지 않아서 파트너 클라이언트들도 꽤 관심 있어 하시는 것 같더라고요.")
say("SPK02", "그거 나쁘지 않은 생각인데 지금 당장 검토할 사람이 없긴 하죠.")
say("SPK01", "그건 나중에 좀 더 얘기해보죠. 오늘은 일단 넘어가고요.")
say("SPK03", "이번 달 등급제 관련 문의만 대충 아홉 건 정도는 됐던 것 같아요.")
say("SPK03", "음 다들 수수료 할인이 궁금하다고 많이들 물어보시더라고요.")
say("SPK01", "그 정도면 확실히 수요가 있긴 하네요.")
say("SPK05", "그렇죠, 그래서 한번 말씀드려본 거예요.")
say("SPK03", "저도 있으면 응대할 때 좀 더 편할 것 같긴 해요.")

# --- D5: weekend CS staffing backlog, resistance before settling ---
say("SPK01", "마지막으로 주말 CS 인력 얘기를 좀 해야 할 것 같아요. 지금 상태가 어때요?")
say("SPK03", "음 지금 저희 둘이서 주말 이틀을 다 보고 있는데 다음 달 되면 카테고리가 하나 더 느니까 감당이 안 될 것 같아요.",
    decision="D5")
say("SPK03", "지금도 사실 빠듯하게 맞추고 있는 상황이라 더 늘면 감당이 안 될 것 같아요.", decision="D5")
say("SPK03", "음 한 명이라도 아프거나 하면 그날은 아예 응대를 못 해요.", decision="D5")
say("SPK03", "저번 주에 저 하루 연차 썼을 때도 그날 응대 못 채우고 다음 날로 밀렸었거든요.", decision="D5")
say("SPK01", "이건 뭐 CS팀에서 알아서 좀 조정해서 맞춰주셔야 할 것 같은데요.",
    decision="D5", label="d5_thrown")
say("SPK03", "저희끼리 조정한다고 되는 문제가 아니에요, 물리적으로 사람이 부족한 거라서요.",
    kind="concern", decision="D5", rt=-1, note="인력 부족은 조정이 아니라 충원이 필요한 문제라는 반대")
say("SPK03", "음 지금도 야근을 거의 매일 하고 있는 상황이라 이 이상은 진짜 무리예요.", decision="D5")
say("SPK03", "저번 주에도 다들 아홉 시 넘어서 퇴근했었잖아요.", decision="D5")
say("SPK03", "음 금요일엔 거의 열 시까지 있었던 것 같아요.", decision="D5")
say("SPK03", "어 이러다 누구 하나 그만둔다고 할까 봐 저도 좀 걱정이에요.", decision="D5")
say("SPK03", "어 채용 공고는 올려주셨다고 들었는데 지원자가 별로 없다고 하더라고요.", decision="D5")
say("SPK01", "네 저도 그건 알고 있어요, 조건을 좀 조정해야 하나 고민 중이에요.")
say("SPK02", "저희 쪽에서 매칭 검수 인원 한두 명 정도는 잠깐 도와드릴 수 있을 것 같긴 한데요.",
    decision="D5")
say("SPK02", "근데 저희도 CS 경험이 있는 건 아니라서 간단한 것만 도와드릴 수 있어요.", decision="D5")
say("SPK02", "저희 쪽도 매칭 건이 늘어서 딱히 여유 인력이 있는 건 아니거든요.", decision="D5")
say("SPK02", "그래도 하루에 한두 시간 정도는 빼서 도와드릴 수 있을 것 같아요.", decision="D5")
say("SPK03", "간단한 거라면 어떤 거요?", kind="open_question", decision="D5", rt=-1,
    note="지원 가능한 업무 범위를 구체적으로 물음")
say("SPK02", "문의 접수랑 기본 정보 입력 정도는 저희도 할 수 있어요.", decision="D5")
say("SPK01", "그거 말고 다른 부분도 도움받을 수 있을까요?", kind="open_question", decision="D5", rt=-2,
    note="지원 가능한 업무 범위를 더 넓힐 수 있는지 물음")
say("SPK03", "그 정도만 덜어줘도 저희는 실제 문의 응대에만 집중할 수 있어서 좀 나을 것 같아요.",
    decision="D5")
say("SPK03", "지금은 접수하고 입력하는 데만도 시간이 꽤 걸리거든요.", decision="D5")
say("SPK03", "그것만 넘겨받아도 체감상 꽤 여유가 생길 것 같아요.", decision="D5")
say("SPK03", "한 건당 거의 십오 분씩은 잡아먹고 있었거든요.", decision="D5")
say("SPK03", "그거 스무 건이면 그것만 해도 다섯 시간이라 진짜 크긴 해요.", decision="D5")
say("SPK03", "근데 그것도 교육이 좀 필요한데 지금 그럴 시간이 있을지 모르겠어요.",
    kind="concern", decision="D5", rt=-3, note="지원 인력 교육 시간 확보의 어려움을 지적함")
say("SPK02", "교육은 저희가 다 같이 점심시간에 잠깐 받아도 될 것 같은데요, 오래 안 걸릴 것 같고요.", decision="D5")
say("SPK02", "음 몇 명 정도 필요하신지만 말씀해 주시면 저희 쪽에서 사람은 맞춰볼게요.", decision="D5")
say("SPK01", "그럼 문의 접수랑 입력은 신뢰팀이 지원하고, CS팀은 실제 문의 응대에 집중하는 방향으로 정리할게요.",
    kind="decision", decision="D5", settles="1",
    note="인력 부족 반발 끝에 업무 일부를 신뢰팀이 지원하는 방식으로 절충", label="d5_settle")
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

# --- closing ---
say("SPK01", "음 자 그러면 오늘 정할 건 여기까지 하고 정리만 한 번 하고 마칠게요.")
say("SPK01", "노쇼는 신규 등록 평판 점수 조정으로 가고, 신규 카테고리 오픈은 자료 더 보고 다시 보고요.")
say("SPK01", "정산 승인 지연은 개발팀 답 기다리는 거고, 프로필 어뷰징은 비용 비교해서 대응 방식 정합니다.")
say("SPK01", "주말 CS 인력은 신뢰팀이 접수랑 입력 지원하는 걸로 갑니다.")
say("SPK04", "어젯밤 정산 지연 몰린 건은 결과 나오면 제가 바로 공유드릴게요.",
    kind="commitment", rt=-4, note="상기, 앞서 나온 정산 승인 지연 건을 다시 확인함")
say("SPK01", "네 그렇게 해주세요. 다음 회의는 다음 주 화요일 같은 시간에 하겠습니다.")
say("SPK02", "그때까지는 점수 기준 정리해서 미리 공유드려 놓으려고요.",
    kind="commitment", note="본인 계획, 완곡한 예측형 기한 표현", label="d_close_hedge1")
say("SPK04", "저는 이 주 뒤에 지원 인력 운영 결과 정리해서 올려두겠습니다.")
say("SPK05", "저는 프로필 어뷰징 비용표 정리해서 올려두겠습니다.")
say("SPK03", "저도 오늘 나온 것들은 정리는 해서 CS 쪽에 공유는 해둘 수 있을 것 같아요.",
    kind="commitment", note="본인 계획으로 CS팀 공유를 맡음, 완곡한 예측형 표현", label="d_close_hedge2")
say("SPK01", "다들 고생하셨어요.")
say("SPK02", "고생하셨습니다.", note="사담")
say("SPK05", "다음에 뵐게요.", note="사담")

ANSWER_KEY = [
    {"decision_id": "D1", "settles_row": "d1_settle",
     "statement": "신규 등록 프리랜서 노쇼에만 평판 점수를 걸고, 경력 프리랜서 정책과 심사제 전환은 그대로 유지한다.",
     "owner": "SPK02", "due": "다음 주 초(점수 기준 작성 기준)", "due_as_said": "다음 주 초까지는",
     "evidence_rows": ("d1_settle", "d1_owner", "d1_due"),
     "note": "심사제 전환이 SLA 문제로 두 번째로 무산된 뒤, 신규 등록 평판 점수 도입으로 절충됨"},
    {"decision_id": "D2", "settles_row": "d2_settle",
     "statement": "오픈 승인 기준에 세무 신고 연동 완료 여부를 추가하자는 팀장 제안에 아무도 명확히 답하지 않은 채, 원인 자료를 더 모은 뒤 다시 논의하기로 한다.",
     "owner": "SPK02", "due": "", "due_as_said": "",
     "evidence_rows": ("d2_proposal", "d2_settle"),
     "note": "분야별 행정 처리 차이가 기준 추가만으로는 잡히지 않을 수 있다는 우려가 오간 채 자료 보완으로 유보됨"},
    {"decision_id": "D3", "settles_row": "d3_settle",
     "statement": "정산 승인 자동화는 개발팀 일정이 확정되지 않아 이번 주에는 정하지 않고 답변이 오면 다시 논의한다.",
     "owner": "", "due": "개발팀 답변 이후", "due_as_said": "개발팀 답 오면 다시",
     "evidence_rows": ("d3_settle", "d3_request"),
     "note": "자동화 요청은 이미 넣었으나 개발 일정이 꽉 차 있어 보류됨"},
    {"decision_id": "D4", "settles_row": "d4_settle",
     "statement": "프로필 어뷰징은 시범 필터링 비용이 전면 재구축 비용보다 클 경우 전면 재구축을 먼저 진행하는 방식으로 대응한다.",
     "owner": "SPK04", "due": "이번 주 안(기준표 작성 기준)", "due_as_said": "이번 주 안에는",
     "evidence_rows": ("d4_settle", "d4_owner"),
     "note": "사전 고지만으로는 어뷰징을 막기 어렵다는 우려를 거쳐 비용 비교 기준의 조건부 대응으로 확정됨"},
    {"decision_id": "D5", "settles_row": "d5_settle",
     "statement": "CS팀 인력 부족은 신뢰팀이 문의 접수와 기본 정보 입력을 지원하고, CS팀은 실제 문의 응대에 집중하는 방식으로 절충한다.",
     "owner": "SPK02", "due": "", "due_as_said": "",
     "evidence_rows": ("d5_thrown", "d5_settle"),
     "note": "CS팀에 통째로 떠넘겨졌다가 인력 부족 반발을 거쳐 신뢰팀 일부 업무 지원으로 절충되어 확정됨"},
]

if __name__ == "__main__":
    b.write(ANSWER_KEY)
