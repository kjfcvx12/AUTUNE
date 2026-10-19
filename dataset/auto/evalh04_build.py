"""Build EVALH_04 (A/C/D csv + speakers.json) for the hard dummy evaluation set.

Authored for `team_dummy/SPEC.md` addenda 2026-09-21, 09-21b and 09-21c. The
dialogue is held here as one list so row numbers, utterance ids, start times and
every cross-reference (`responds_to`, `evidence_rows`) are generated instead of
hand-typed -- hand-numbering is what broke the earlier meetings.

    python evalh04_build.py

Writes into ../extraction_eval_dummy_hard/. Prints counts only.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

MEETING = "EVALH_04"
OUT = Path(__file__).resolve().parent.parent / "extraction_eval_dummy_hard"

SPEAKERS = {
    "meeting": MEETING,
    "title": "라온코스 리필 스테이션 직영점 확대 2차 준비 회의",
    "type": "cross-team",
    "position_order": ["사원", "주임", "대리", "과장", "차장", "부장", "이사", "대표"],
    "speakers": [
        {"speaker": "SPK01", "name": "류시온", "team": "매장운영팀", "job": "Ops",
         "position": "과장", "title": "파트장"},
        {"speaker": "SPK02", "name": "한겨울", "team": "상품기획팀", "job": "PM",
         "position": "대리", "title": ""},
        {"speaker": "SPK03", "name": "고은별", "team": "품질관리팀", "job": "QA",
         "position": "주임", "title": ""},
        {"speaker": "SPK04", "name": "서지훈", "team": "마케팅팀", "job": "Marketing",
         "position": "대리", "title": ""},
        {"speaker": "SPK05", "name": "윤가온", "team": "매장운영팀", "job": "Sales",
         "position": "사원", "title": ""},
    ],
}
ROLE = {s["speaker"]: s["job"] for s in SPEAKERS["speakers"]}

rows: list[dict] = []
tags: dict[str, int] = {}


def r(spk, text, kind="none", did="", settles=False, rt="", note="", tag=""):
    """One ASR segment. `rt` and `evidence` refer to tags, never to row numbers."""
    rows.append({"speaker": spk, "text": text, "kind": kind, "decision_id": did,
                 "settles": settles, "rt": rt, "note": note})
    if tag:
        if tag in tags:
            raise SystemExit(f"duplicate tag {tag}")
        tags[tag] = len(rows)


# --- opening -----------------------------------------------------------------
r("SPK01", "자 세 시 좀 넘었으니까 그냥 시작할게요. 지훈 씨는 좀 늦는다고 하셨어요.")
r("SPK01", "오늘은 일단 파일럿 세 개 매장 이 주 치 결과부터 보고 용기 쪽으로 넘어갈게요.")
r("SPK01", "가격이랑 오픈일까지 오늘 안에 정해야 되는데 그게 될지는 저도 좀 모르겠네요.")
r("SPK01", "지난번에 나왔던 것 중에 아직 안 정해진 게 뭐 네 갠가 다섯 개 되거든요.")
r("SPK01", "그거를 오늘 다 못 털면 이제 오픈 일정이 또 밀리는 상황이라서요.")
r("SPK03", "네.")
r("SPK02", "저 그 교육자료는 오늘 안 보나요? 저번에 이번 회의에서 정하자고 하셨던 것 같은데.",
  "open_question", note="교육자료 안건을 오늘 다루는지 물음", tag="q_agenda")
r("SPK01", "아 그건 이제 뒤쪽으로 좀 빼 놓고 시간 남으면 보고 아니면 다음으로 넘길게요.")
r("SPK01", "그게 사실 오늘 정한다고 해도 뭐 만들 사람이 없어서 좀 애매하거든요.")
r("SPK01", "일단 가온 씨가 지난주에 세 매장 다 돌고 오셨으니까 그것부터 먼저 들을게요.")
r("SPK01", "뭐 정리가 다 안 되셨어도 그냥 보신 대로 편하게 말씀해 주시면 돼요.")
r("SPK05", "네 그러면 제가 다녀온 순서대로 좀 말씀드릴게요. 정리는 따로 못 했는데요.")
r("SPK05", "일단 성수 매장은 리필 스테이션 자체는 손님들이 생각보다 잘 쓰시는 편인데요,")
r("SPK05", "문제는 이제 세척대 물이 자꾸 넘쳐서 바닥이 계속 젖어 있다는 거예요.")
r("SPK05", "직원분들이 하루에 몇 번씩 그거 닦으시느라 계속 왔다 갔다 하시더라고요.")
r("SPK05", "저도 한 두 시간 정도 서 있었는데 그 사이에만 세 번을 닦으셨어요.")
r("SPK05", "그래서 직원분들이 이제 리필 자체를 좀 꺼리시는 분위기도 약간 있어요.")
r("SPK05", "뭐 그래도 손님 반응은 계속 좋은 편이라 그건 좀 다행이라고 생각해요.")
r("SPK02", "음.")

# --- T1: pilot result and how far the rollout goes, region D1 -----------------
r("SPK05", "그리고 목동은 아예 배수구가 없어서 양동이로 받아서 화장실에 버리세요.")
r("SPK05", "그게 하루에 뭐 네다섯 번은 되니까 그것도 일이 꽤 되더라고요.")
r("SPK05", "그 양동이를 들고 매장 뒤쪽으로 가시는 게 좀 위험해 보이기도 하고요.")
r("SPK05", "그건 좀 아닌 것 같다고 목동 점장님이 저한테 두 번이나 말씀하시더라고요.")
r("SPK02", "그게 지금 세 군데 다 그런 건지 목동만 그런 건지가 저는 좀 궁금한데요.",
  "open_question", note="배수 문제가 어느 범위까지인지 확인", tag="q_drain")
r("SPK05", "성수는 배수구가 있긴 있는데 위치가 창고 안쪽이라 물을 들고 가야 돼요.")
r("SPK05", "그래서 뭐 없는 거보다는 낫지만 편한 구조는 아니라고 보시면 돼요.")
r("SPK05", "직원분들은 그냥 이제 화장실 쪽이 더 가깝다고 그쪽을 쓰시더라고요.")
r("SPK05", "연남은 아예 처음부터 세척대를 안 놓고 그냥 용기만 바꿔 드리고 있고요.")
r("SPK01", "아 연남은 세척을 지금 안 하고 있는 거예요? 저는 세 군데 다 하는 줄 알았는데.",
  "open_question", note="연남 매장 운영 방식을 확인", tag="q_yeonnam")
r("SPK05", "네 거기는 공간이 안 나와서 처음부터 좀 빼고 갔어요. 거기가 뭐 스무 평도 안 되거든요.", tag="a_yeonnam")
r("SPK05", "그 대신 용기를 저희가 매번 새로 드리니까 용기 값이 좀 나가는 편이에요.")
r("SPK05", "한 달에 그것만 따지면 뭐 사십만 원 정도는 더 나가는 것 같더라고요.")
r("SPK03", "잠시만요. 그러면 연남은 지금 용기 세척을 누가 하고 있는 거예요?",
  "open_question", note="세척 주체를 확인, 말을 끊고 들어옴", tag="q_who_wash")
r("SPK05", "그건 이제 손님이 집에서 씻어 오시는 걸로 안내가 나가 있어요.", tag="a_home_wash")
r("SPK03", "그건 좀 위험한데요. 저희가 위생 기준을 그렇게 잡은 적이 한 번도 없거든요.",
  "concern", rt="a_home_wash", note="손님 세척 안내가 위생 기준 밖이라는 지적")
r("SPK03", "이거 나중에 문제 생기면 결국 품질팀이 다 뒤집어쓰는 구조라서 좀 그래요.")
r("SPK03", "그래서 저는 이 부분을 오늘 어떻게든 좀 정하고 갔으면 좋겠거든요.")
r("SPK03", "저는 그 안내문을 누가 썼는지도 사실 지금 처음 들었어요.")
r("SPK01", "그 얘기는 이따 용기 쪽에서 같이 보고 지금은 일단 매장 상태만 먼저 볼게요.")
r("SPK01", "가온 씨 그래서 결론적으로 열두 개 중에 몇 군데가 배수가 되는 거예요?",
  "open_question", note="배수가 되는 매장 수를 물음", tag="q_count")
r("SPK05", "제가 도면으로만 본 거라 확실하진 않은데 여덟 군데 정도 되는 것 같아요.")
r("SPK05", "아 여덟이 아니고 일곱이에요. 하남은 작년에 리모델링하면서 막혔더라고요.")
r("SPK05", "그래서 뭐 일곱 군데는 되고 다섯 군데는 지금 상태로는 좀 어려워요.")
r("SPK01", "아 네.")
r("SPK02", "그러면 다섯 군데는 공사를 해야 된다는 얘기인데 그건 좀 큰일인데요.",
  "concern", rt="q_count", note="배수 공사가 필요한 매장이 다섯 곳이라는 문제 제기",
  tag="c_construct")
r("SPK02", "작년에 성수 배수 공사할 때 한 매장에 뭐 이백만 원 정도 나왔거든요.")
r("SPK02", "다섯 군데면 그러니까 천만 원 가까이 되는 건데 그 예산이 지금 어디에도 없어요.")
r("SPK02", "이번 분기 예산은 이미 다 잡혀 있어서 손댈 데가 진짜 없어요.")
r("SPK02", "아니 그게 아니라 예산이 없다기보다 다른 데 이미 다 붙어 있다는 얘기예요.")
r("SPK01", "그 예산 얘기는 뭐 본부장님 결재 없이는 저희끼리 정할 수 있는 게 아니고요.")
r("SPK01", "결재 올린다고 해도 이번 분기 안에 떨어질 것 같지는 않아요.")
r("SPK01", "작년에도 뭐 비슷한 거 올렸다가 그냥 다음 분기로 넘어간 적이 있거든요.")
r("SPK04", "아 죄송합니다. 지하철이 중간에 서 가지고 좀 늦었어요. 다음부터는 좀 일찍 나올게요.")
r("SPK04", "어디까지 얘기하셨어요? 제가 지금 뭘 놓친 건지 잘 모르겠는데요.",
  "open_question", note="진행 상황을 물음", tag="q_catchup")
r("SPK01", "매장 배수 얘기 하고 있었고 지훈 씨 가격 얘기는 이따가 할 거예요.")
r("SPK01", "일단 앉으셔서 가온 씨 얘기 마저 들으시면 될 것 같아요.")
r("SPK01", "아 아니라 가온 씨 얘기는 대충 끝났고 이제 범위 얘기 하려던 참이에요.")
r("SPK02", "시설팀에서는 이번 분기에 매장 공사 일정을 더 못 잡는다고 하더라고요.",
  "ambiguous", note="시설팀 입장을 대신 전달, 전달", tag="amb_facility")
r("SPK02", "그쪽은 이제 여름에 에어컨 교체가 다 잡혀 있어서 손이 없다는 얘기예요.")
r("SPK02", "그래서 저희가 아무리 급하다고 해도 순서를 바꿔 주기는 어려울 것 같아요.")
r("SPK02", "그 얘기를 어제 메일로 받아서 저도 좀 당황스러웠거든요. 회신은 아직 못 했고요.")
r("SPK02", "그래서 이제 공사를 전제로 잡는 계획은 좀 위험하다고 보는 거예요.")
r("SPK03", "그러면 배수 안 되는 매장은 이번엔 그냥 빼고 가는 게 낫지 않나요?",
  "open_question", note="제외안을 던지며 의견을 물음", tag="prop_skip")
r("SPK01", "음 그것도 방법이긴 한데 그러면 이제 오픈 매장 수가 확 줄어드는 게 문제죠.")
r("SPK01", "본부에는 열두 개 다 연다고 이미 보고가 올라가 있는 상태라서요.",
  "concern", rt="prop_skip", note="이미 보고된 매장 수와 어긋난다는 지적")
r("SPK04", "잠깐만요. 그 보고가 열두 개였어요? 저는 여덟 개로 알고 있었는데요.",
  "open_question", note="보고된 숫자를 확인, 말을 끊고 들어옴", tag="q_report")
r("SPK01", "초안은 여덟이었는데 지난달에 열둘로 올라갔어요. 그때 말씀드렸을 텐데.")
r("SPK04", "아 그건 제가 못 들었네요. 그 주에 제가 휴가였던 것 같기도 하고요.")
r("SPK04", "그러면 광고 소재에 매장 목록 들어가는 것도 다시 봐야 되는 거네요.")
r("SPK04", "그게 이미 시안까지 나와 있어서 지금 바꾸면 일정이 좀 빠듯해요.")
r("SPK04", "매체 담당이랑도 다시 얘기해야 되는 부분이라 좀 번거롭기도 하고요.")
r("SPK01", "어쨌든 지금 상태로 열둘은 무리고 뭔가 나눠서 가야 될 것 같은데요.", did="D1",
  tag="lead_split")
r("SPK01", "배수 되는 일곱 군데를 일차로 먼저 열고 나머지는 이차로 미루는 거죠.", did="D1")
r("SPK01", "그러면 공사비도 이번 분기에는 안 잡아도 되고 시설팀도 안 건드려도 되고요.", did="D1")
r("SPK01", "본부에는 제가 단계적으로 간다고 설명을 드리면 될 것 같고요.", did="D1")
r("SPK01", "어차피 한 번에 다 열어도 초반에 문제 터지면 더 크게 깨지거든요.", did="D1")
r("SPK03", "일차 이차로 나누면 매장마다 안내문이 달라지는데 그건 누가 관리해요?",
  "open_question", did="D1", note="매장별 안내 관리 주체를 물음", tag="q_manage")
r("SPK02", "그건 뭐 제가 표로 만들어서 돌리면 되긴 하는데 좀 번거롭긴 하죠.",
  "ambiguous", did="D1", rt="q_manage", note="가능은 하다는 정도의 애매한 수락")
r("SPK05", "근데 이차로 미루면 그 다섯 매장 점장님들이 좀 서운해하실 것 같은데요.",
  "concern", did="D1", rt="lead_split", note="제외되는 매장 점장들의 반발 우려")
r("SPK05", "이미 매대 자리까지 비워 놓으신 데가 두 군데나 있거든요.", did="D1")
r("SPK05", "저번에 다 같이 오픈한다고 제가 말씀을 드려 놔서 좀 난처해요.", did="D1")
r("SPK05", "그 얘기를 또 제가 가서 뒤집어야 되는 상황이 되는 거잖아요.", did="D1")
r("SPK05", "그것도 뭐 제가 할 일은 맞는데 좀 미리 알았으면 좋았을 것 같아요.", did="D1")
r("SPK01", "그건 뭐 제가 따로 전화드려서 하나하나 설명을 좀 드릴게요.", "commitment", did="D1", rt="q_manage",
  note="본인이 점장 설득을 맡음, 기한은 말하지 않음", tag="c_call")
r("SPK01", "그러면 정리하면 배수 되는 일곱 군데만 먼저 열고 나머지 다섯은 이번 범위에서 빼는 거예요.",
  "decision", did="D1", settles=True,
  note="양쪽 반대가 나온 뒤 논의를 요약하는 형태로 확정", tag="d1_settle")
r("SPK02", "네 그러면 그 일곱 군데가 정확히 어디인지는 확정이 좀 필요할 것 같은데요.", did="D1")
r("SPK01", "가온 씨가 매장별로 배수구랑 평수 정리해서 한 장으로 만들어 주실래요?",
  "open_question", did="D1", note="매장 현황 정리를 요청", tag="ask_survey")
r("SPK05", "네 그러면 다음 주 수요일까지 정리해서 메일로 공유드릴게요.", "commitment", did="D1",
  rt="ask_survey", note="요청을 받아 기한을 명시하고 맡음", tag="c_survey")
r("SPK05", "그 도면이 좀 오래된 거라 실제로 가 봐야 아는 데도 있을 것 같긴 해요.", did="D1")
r("SPK05", "그래서 이번 주에 두 군데 정도는 직접 가 보려고 하는데요.", did="D1")
r("SPK05", "목동이랑 하남은 제가 가서 사진이라도 좀 찍어 오려고요. 그래야 얘기가 되니까요.", did="D1")
r("SPK01", "네 그건 뭐 어쩔 수 없죠. 가 보고 다르면 그때 또 고치면 되는 거고요.")

# --- side talk 1 (middle of the meeting) -------------------------------------
r("SPK04", "아 근데 저 밑에 커피 머신 오늘 또 고장 났던데 그거 고쳐 주기는 하나요?",
  note="사담")
r("SPK02", "그거 지난주에도 그랬어요. 총무팀에 얘기하면 사람 부른다고는 하는데요.", note="사담")
r("SPK05", "저는 그래서 그냥 앞에 카페에서 사 와요. 거기 아메리카노가 이천 원이에요.",
  note="사담")
r("SPK04", "오 그건 좀 싸네요. 이따 내려가면서 하나 사 와야겠어요.", note="사담")
r("SPK03", "거기 오후에는 줄이 좀 길어요. 점심때는 아예 못 가요.", note="사담")
r("SPK02", "저는 그냥 믹스커피 마셔요. 탕비실에 아직 좀 남아 있더라고요.", note="사담")

# --- T2: whose container, region D2 (conditional) ----------------------------
r("SPK01", "자 그러면 용기 얘기로 넘어갈게요. 아까 은별 씨가 하시려던 얘기요.")
r("SPK03", "네 아까 그 손님이 집에서 씻어 온 용기 얘기인데요, 그게 이제 뭐냐면")
r("SPK03", "저희가 지금 그걸 받을지 말지를 한 번도 제대로 정한 적이 없어요.")
r("SPK03", "파일럿에서는 그냥 현장에서 알아서 받고 계신 상황이고요. 저희가 뭘 정해 준 게 없으니까요.")
r("SPK03", "그러니까 매장마다 기준이 다 다르게 굴러가고 있는 거예요.")
r("SPK03", "성수는 받고 목동은 안 받고 연남은 아예 그걸 전제로 돌아가고요.")
r("SPK03", "그러니까 지금은 뭐 기준이 없다기보다 매장 수만큼 기준이 있는 셈이에요.")
r("SPK02", "저번에 그건 안 받는 쪽으로 얘기가 됐던 것 같은데 제가 잘못 기억하는 건가요?",
  "open_question", note="이전 논의 내용을 확인", tag="q_recall")
r("SPK01", "맞아요. 이 주 전에 개인 용기는 일단 안 받는 걸로 정리했었어요.",
  "commitment", rt="q_recall", note="이전 결정을 상기, 상기", tag="recall")
r("SPK03", "근데 현장에는 그게 전달이 안 돼서 그냥 다 받고 계시더라고요.",
  "concern", rt="recall", note="정해진 내용이 현장에 전달되지 않았다는 문제 제기")
r("SPK05", "그건 저희가 안내문을 못 붙여서 그래요. 붙일 게 없었어요.")
r("SPK05", "직원분들도 뭐라고 말씀드려야 될지 모르니까 그냥 받으시는 거고요.")
r("SPK05", "저한테도 물어보시는데 저도 사실 정확히는 몰랐거든요. 그게 좀 민망했어요.")
r("SPK05", "그래서 그냥 이제 저번에 하시던 대로 하시라고 말씀드렸어요.")
r("SPK04", "손님들은 이제 용기 가져오는 게 이 브랜드 쓰는 이유라고 생각하시거든요.")
r("SPK04", "그걸 막으면 리필 스테이션 하는 의미가 좀 없어지는 느낌인데요.",
  "concern", rt="recall", note="개인 용기 금지가 브랜드 콘셉트와 충돌한다는 반대",
  tag="c_concept")
r("SPK04", "저희가 찍어 놓은 사진도 다 손님 용기로 찍혀 있어서 다시 찍어야 되고요.")
r("SPK04", "그 사진이 이번 달 소식지에 나가는 건데 그것도 좀 애매해지고요.")
r("SPK04", "아 그게 아니고 소식지는 다음 달인데 촬영은 이번 주에 이미 끝났어요.")
r("SPK03", "제 말은 무조건 막자는 게 아니고 기준이 없는 게 문제라는 거예요.",
  "concern", rt="c_concept", note="쟁점을 기준 부재로 되돌림, 말을 끊고 들어옴")
r("SPK03", "세척 상태를 누가 어떻게 보고 받아 주느냐가 지금 아무 데도 없거든요.")
r("SPK03", "기름때가 남은 통을 들고 오셔도 지금은 사실 거절할 근거가 없어요.")
r("SPK03", "저희가 그걸 그냥 채워 드리면 그때부터는 저희 책임이 되는 거고요.")
r("SPK03", "그래서 저는 기준만 있으면 개인 용기도 받을 수 있다고 보는 쪽이에요.")
r("SPK02", "그러면 그 기준은 어디서 가져와야 되는 거예요? 법으로 정해진 게 있나요?",
  "open_question", note="위생 기준의 근거를 물음", tag="q_standard")
r("SPK03", "화장품법 쪽에 소분 판매 관련된 게 있긴 한데 저도 정확히는 모르겠어요.")
r("SPK03", "작년에 교육 들을 때 잠깐 본 거라 지금 기억이 좀 흐릿하거든요.")
r("SPK03", "그래서 그건 이제 제가 법령집이라도 한번 찾아보려고요.", "commitment",
  note="본인 계획으로 법 기준을 확인하겠다고 함", tag="c_lookup")
r("SPK01", "그거 언제쯤 알 수 있을까요? 가격이랑 같이 봐야 되는 부분이라서요.",
  "open_question", note="확인 시점을 물음", tag="q_when_law")
r("SPK03", "한 주 정도면 대충 윤곽은 나올 것 같은데 확답은 좀 어렵습니다.")
r("SPK03", "협회 쪽에 아는 분이 계셔서 그분한테도 한번 여쭤 보려고요.")
r("SPK02", "그리고 외부 시험 같은 건 안 하나요? 그게 있으면 얘기가 좀 깔끔해지는데.",
  "open_question", note="외부 시험 진행 여부를 물음", tag="q_test")
r("SPK03", "시험기관에 의뢰는 넣어 볼게요. 다만 결과가 삼 주는 걸린다고 하더라고요.",
  "commitment", rt="q_test", note="요청을 받아 외부 시험 의뢰를 맡음", tag="c_test")
r("SPK03", "그리고 비용이 건당 한 팔십만 원쯤 나오는데 그건 저희 예산으로는 좀")
r("SPK01", "그 비용은 일단 제가 본부에 얘기해서 받아 보도록 해 볼게요.", "commitment",
  note="본인이 예산 요청을 맡음, 기한 없음")
r("SPK01", "그 정도면 뭐 결재 없이 파트 예산으로도 될 것 같기는 한데요.")
r("SPK01", "일단 얘기해 보고 안 되면 다시 말씀드릴게요. 이번 주 안에는 답 드릴 수 있어요.")
r("SPK01", "뭐 안 되면 이제 시험 항목을 좀 줄이는 수밖에 없을 것 같고요.")
r("SPK04", "그럼 시험 결과 나오기 전까지는 손님들한테 뭐라고 안내해요?",
  "open_question", note="시험 전까지의 안내 방침을 물음", tag="q_interim")
r("SPK01", "일단은 저희 용기만 받고 개인 용기는 나중에 다시 보는 게 맞을 것 같은데요.",
  did="D2", tag="prop_own")
r("SPK05", "현장에서 그거 설명하기가 좀 어려울 것 같은데요. 이미 들고 오셨는데요.",
  "concern", did="D2", rt="prop_own", note="현장 안내 부담을 이유로 반대")
r("SPK05", "가져오신 분한테 안 된다고 돌려보내는 게 제일 힘든 일이거든요.", did="D2")
r("SPK05", "그거 때문에 저번에 성수에서 한 번 크게 싸우신 적도 있어요.", did="D2")
r("SPK05", "그때 직원분이 울면서 저한테 전화하셨던 게 아직도 생각나요.", did="D2")
r("SPK05", "그래서 안내문이 먼저 내려가야 된다고 제가 계속 말씀드린 거예요.", did="D2")
r("SPK04", "그건 그냥 오늘은 받아 드리고 다음부터는 안 된다고 하면 되지 않나요?", did="D2")
r("SPK02", "그러면 그 날짜 기준이 또 애매해지는데요. 매장별로 다 달라지잖아요.", did="D2")
r("SPK02", "매장마다 시작한 날이 다 다르니까 손님은 또 헷갈리실 거고요.", did="D2")
r("SPK02", "저는 차라리 한 날짜로 딱 끊는 게 낫다고 보는 편이에요.", did="D2")
r("SPK02", "그게 이제 손님한테도 설명하기가 훨씬 편하거든요. 날짜 하나만 말씀드리면 되니까요.", did="D2")
r("SPK01", "그러면 당분간은 저희 용기만 받고 시험 결과가 괜찮게 나오면 그때 개인 용기를 다시 보는 쪽으로 가요.",
  "decision", did="D2", settles=True,
  note="조건부 확정, 시험 결과에 따라 개인 용기를 재논의", tag="d2_settle")
r("SPK03", "네 그러면 제가 의뢰서 쓰면서 개인 용기도 같이 항목에 넣을게요.",
  "commitment", did="D2", rt="d2_settle", note="확정 내용을 받아 시험 항목에 반영")
r("SPK05", "그러면 그 안내문은 언제쯤 매장으로 내려오는 거예요?", "open_question", did="D2",
  note="매장 안내문 배포 시점을 물음", tag="q_notice")
r("SPK02", "그건 제가 이번 주 안에 한 장짜리로 만들어서 매장에 뿌릴게요.",
  "commitment", did="D2", rt="q_notice", note="요청을 받아 기한을 명시하고 맡음",
  tag="c_notice")
r("SPK02", "문구는 은별 씨가 한번 봐 주시면 좋을 것 같고 초안만 제가 잡을게요.", did="D2")
r("SPK02", "저 혼자 쓰면 또 위생 쪽 표현이 틀릴 것 같아서요. 그거 한 줄 때문에 문제 되면 크니까요.", did="D2")
r("SPK02", "작년에 그거 잘못 써서 한 번 다시 만든 적도 있고요.", did="D2")
r("SPK03", "네 보내 주시면 제가 그날 안에 한번 볼게요.", did="D2")
r("SPK01", "네 그렇게 하고 다음 안건으로 갈게요. 시간이 벌써 좀 됐네요.")

# --- T3: price, region D3 (false agreement) ----------------------------------
r("SPK01", "가격 얘기를 해야 되는데 지훈 씨 안 계실 때 얘기가 좀 나왔었죠.")
r("SPK04", "네 저희 쪽 안은 리필가를 본품 대비 삼십 프로 싸게 가는 거예요.", did="D3",
  tag="prop_30")
r("SPK04", "그 정도는 돼야 손님이 무거운 용기를 들고 오실 이유가 생기거든요.", did="D3")
r("SPK04", "다른 데도 뭐 대충 그 정도 선에서 하고 있는 걸로 알고 있고요.", did="D3")
r("SPK04", "이십 프로면 그냥 인터넷에서 본품 사는 게 낫다고 생각하실 거예요.", did="D3")
r("SPK04", "저희가 지난달에 설문 돌린 것도 그 비슷하게 나왔었어요. 그 자료 보여 드릴 수도 있고요.", did="D3")
r("SPK04", "응답이 뭐 삼백 명 정도였는데 절반 넘게 그렇게 답하셨거든요.", did="D3")
r("SPK02", "삼십 프로면 원가가 안 맞을 것 같은데 그거 계산은 해 보신 거예요?",
  "open_question", did="D3", note="할인율의 원가 타당성을 물음", tag="q_margin")
r("SPK04", "저희가 본 건 매출 기준이고 원가는 이제 상품기획에서 보셔야 되는 거죠.", did="D3")
r("SPK02", "제가 대충 돌려 보면 삼십 프로 빼면 마진이 거의 안 남아요.",
  "concern", did="D3", rt="prop_30", note="할인율이 마진을 없앤다는 반대", tag="c_margin")
r("SPK02", "용기 값이랑 세척 인건비가 다 저희 쪽으로 들어오는 구조라서요.", did="D3")
r("SPK02", "본품은 그래도 물류가 한 번인데 리필은 사람 손이 계속 들어가거든요.", did="D3")
r("SPK02", "그래서 겉으로 보이는 원가하고 실제 원가가 좀 많이 달라요.", did="D3")
r("SPK02", "그걸 이제 표로 만들어서 저번에 한 번 보여 드렸었는데요.", did="D3")
r("SPK03", "어 세척 인건비는 그거 매장 쪽으로 잡히는 거 아니에요? 저는 그렇게 알고 있었는데.", did="D3")
r("SPK02", "회계상으로는 상품기획으로 떨어져요. 저도 작년에 알았어요.", did="D3")
r("SPK03", "아 네 네.", did="D3")
r("SPK01", "그러면 몇 프로면 되는 거예요? 숫자를 하나 정해야 넘어가는데요.",
  "open_question", did="D3", note="확정 가능한 할인율을 물음", tag="q_rate")
r("SPK02", "이십오 프로면 뭐 어떻게든 맞출 수는 있을 것 같아요. 마진이 많이 남는 건 아니고요.", did="D3")
r("SPK02", "그것도 용기를 지금 단가로 계속 받는다는 전제에서요. 그게 깨지면 또 달라져요.", did="D3")
r("SPK02", "단가 오르면 그때는 다시 봐야 되는 숫자예요. 그건 좀 감안해 주셨으면 해요.", did="D3")
r("SPK02", "용기 업체가 내년에 올린다는 얘기가 벌써 좀 돌고 있고요.", did="D3")
r("SPK04", "이십오도 뭐 나쁘진 않아요. 손님 입장에서 체감은 비슷하고요.", did="D3")
r("SPK01", "아 그럼 그렇게 하죠!", did="D3", note="겉으로는 합의된 듯 보이나 바로 뒤집힘, 번복",
  tag="fake_ok")
r("SPK04", "아 맞다 그거 안 돼요. 멤버십 십오 프로랑 겹치면 원가 밑으로 내려가요.",
  "concern", did="D3", rt="fake_ok", note="멤버십 중복 할인 때문에 합의가 뒤집힘",
  tag="objection")
r("SPK04", "저희 멤버십은 전 상품 자동 적용이라서 빼려면 시스템을 손봐야 돼요.", did="D3")
r("SPK04", "그걸 제가 아까 말씀드렸어야 되는데 늦게 와서 타이밍을 놓쳤네요.", did="D3")
r("SPK02", "그건 또 전산에 요청해야 되는 거네요. 그게 제일 오래 걸리는데.", did="D3")
r("SPK01", "그 전산에 요청 넣으면 보통 얼마나 걸리는 거예요? 대충이라도 알아야 될 것 같은데.", "open_question", did="D3",
  note="전산 처리 기간을 물음", tag="q_it")
r("SPK04", "간단한 건 이 주인데 결제 쪽을 건드리면 한 달도 봐야 돼요.", did="D3")
r("SPK04", "작년에 쿠폰 중복 막을 때도 뭐 한 달 넘게 걸렸거든요. 그것도 간단한 거였는데요.", did="D3")
r("SPK04", "그때도 결제 쪽을 건드린다고 계속 밀렸던 걸로 기억하고 있어요.", did="D3")
r("SPK03", "그러면 오픈 전에 안 끝날 수도 있다는 얘기잖아요. 그러면 오픈하고 나서 또 손봐야 되고요.",
  "concern", did="D3", rt="q_it", note="오픈 전에 전산 작업이 끝나지 않을 위험")
r("SPK04", "그래서 저는 그냥 리필은 멤버십 제외 품목으로 빼면 될 것 같은데요.", did="D3")
r("SPK04", "제외 품목은 화면에서 체크만 하면 되니까 하루면 끝나요. 그건 저도 해 봤거든요.", did="D3")
r("SPK04", "그건 제가 아까 전산 쪽에 물어봤을 때 그렇게 들었거든요.", did="D3")
r("SPK02", "그건 손님들이 좀 싫어하실 텐데요. 멤버십 쓰시는 분들이 제일 많이 오시거든요.", did="D3")
r("SPK04", "싫어하셔도 원가 밑으로 파는 것보다는 낫죠. 그건 진짜 답이 없잖아요.", did="D3")
r("SPK01", "그러면 리필가는 본품 대비 이십오 프로로 내리고 멤버십 중복은 빼는 걸로 하죠.",
  "decision", did="D3", settles=True,
  note="반대 의견을 받아 할인율과 중복 적용을 함께 정리", tag="d3_settle")
r("SPK04", "네 그럼 제가 가격표랑 포스 항목은 다음 주 금요일까지 고쳐 놓을게요.",
  "commitment", did="D3", rt="d3_settle", note="본인이 기한을 명시하고 맡음", tag="c_price")
r("SPK02", "그 숫자는 제가 다시 한번 검산해서 오늘 안에 보내 드릴게요.",
  "commitment", did="D3", note="본인이 기한을 명시하고 검산을 맡음")
r("SPK05", "매장에 붙어 있는 가격표도 그럼 다 바꿔야 되는 거죠? 그것도 시간이 좀 걸리는데.", "open_question",
  did="D3", note="매장 가격표 교체 여부를 확인", tag="q_tag")
r("SPK04", "네 그건 제가 인쇄해서 지점별로 보내 드릴게요. 이번 주 안에 보낼게요.", "commitment", did="D3",
  rt="q_tag", note="요청을 받아 가격표 인쇄와 배송을 맡음")
r("SPK01", "네.")

# --- side talk 2 (middle of the meeting) -------------------------------------
r("SPK05", "아 근데 아까 오면서 보니까 일 층에 공사 시작했던데요. 가림막 쳐 놨더라고요.", note="사담")
r("SPK02", "다음 주부터 한 달 동안 한대요. 소리가 꽤 클 것 같던데요.", note="사담")
r("SPK03", "저희 회의실이 바로 위인데 그럼 좀 시끄럽겠네요. 전화도 못 받겠는데요.", note="사담")
r("SPK04", "그럼 회의는 뭐 다른 층에서 하면 되죠. 그것도 방법이긴 하네요.", note="사담")
r("SPK02", "육 층 회의실이 그나마 조용해요. 거기가 창가 쪽이라서요.", note="사담")

# --- T4: training material, region D4 (a task nobody wants, deferral) --------
r("SPK01", "자 그러면 아까 미뤄 뒀던 교육자료 얘기를 좀 하고 넘어갈게요.")
r("SPK02", "그거 저번에 이번 회의에서 정하자고 하셨던 거예요. 저도 그래서 아까 여쭤본 거고요.")
r("SPK01", "매장 직원분들이 리필 절차를 아예 모르시니까 뭔가는 있어야 되는데요.")
r("SPK01", "이건 뭐 마케팅 쪽에서 알아서 좀 만들어 주시면 될 것 같은데요.",
  "open_question", did="D4", note="마케팅 쪽에 통째로 넘기며 요청", tag="dump")
r("SPK04", "저희가요? 저희는 지금 브랜드 데이 준비만 해도 사람이 없는데요.",
  "concern", did="D4", rt="dump", note="인력 부족을 이유로 거절")
r("SPK04", "영상까지 찍으려면 최소 이 주는 거기에 붙어 있어야 되거든요.", did="D4")
r("SPK04", "촬영 스튜디오도 그때는 다 잡혀 있을 거고요. 외부로 빌리면 돈이 또 들고요.", did="D4")
r("SPK04", "저희 팀이 지금 세 명인데 한 명은 다음 달에 휴직 들어가요.", did="D4")
r("SPK04", "그래서 뭐 영상은 진짜 물리적으로 좀 어려운 상황이거든요.", did="D4")
r("SPK02", "영상 말고 그냥 사진 몇 장에 설명 붙인 거면 안 되는 건가요?",
  "open_question", did="D4", note="간소한 형태로 대체 가능한지 물음", tag="q_photo")
r("SPK05", "현장에서는 사실 종이 한 장이 제일 편하긴 해요. 코팅해서 붙여 놓으면 되니까요.", did="D4")
r("SPK05", "영상은 틀어 볼 데도 없고 다들 바쁘셔서 잘 안 보세요. 휴게실에 티브이도 없고요.", did="D4")
r("SPK05", "저번에 내려온 안전교육 영상도 아직 반도 안 봤을 거예요.", did="D4")
r("SPK03", "영상은 나중에 감사 때 증빙으로 쓸 수 있어서 있으면 좋긴 한데요.", did="D4")
r("SPK03", "그게 꼭 이번에 있어야 되는 건 아니라고 저는 생각해요.", did="D4")
r("SPK03", "감사는 어차피 내년 상반기라 그때까지만 있으면 되거든요.", did="D4")
r("SPK01", "그럼 누가 하실래요? 아무도 말씀 안 하시면 제가 그냥 정합니다.",
  "open_question", did="D4", note="담당자를 정하라고 요구", tag="ask_owner")
r("SPK04", "아 예... 일단 제가 한번 볼게요.", "ambiguous", did="D4", rt="ask_owner",
  note="아무도 맡지 않아 마지못해 받음, 위임", tag="reluctant")
r("SPK04", "근데 이번 달 안에는 솔직히 좀 자신이 없어요. 그건 미리 말씀드리는 거예요.", did="D4")
r("SPK04", "브랜드 데이 끝나고 나서면 또 모르겠는데요.", did="D4")
r("SPK04", "그때는 뭐 사람도 좀 여유가 생기니까 가능할 것 같기는 해요.", did="D4")
r("SPK01", "그러면 영상은 이번엔 빼고 다음 분기로 넘기고 이번에는 한 장짜리 안내문만 만들어요.",
  "decision", did="D4", settles=True, note="담당이 정해지지 않아 영상은 보류하고 범위를 줄임",
  tag="d4_settle")
r("SPK02", "그 한 장짜리는 제가 만들어 보려고요. 어차피 매장 안내문이랑 같이 가야 돼서요.",
  "commitment", did="D4", rt="d4_settle", note="본인 계획으로 안내문 제작을 맡음",
  tag="c_onepager")
r("SPK01", "그럼 그건 다음 회의 전까지만 주시면 될 것 같아요. 급하게는 안 할게요.", did="D4", tag="due_onepager")
r("SPK05", "매장에서 나오는 질문 같은 건 제가 모아서 드릴게요. 어차피 제가 다 받고 있어서요.", "commitment", did="D4",
  note="요청 없이 질문 수집을 맡음, 기한 없음")
r("SPK05", "점장님들 단톡방에 올라오는 것만 봐도 꽤 되거든요.", did="D4")
r("SPK05", "하루에 뭐 대여섯 개씩은 계속 올라오는 것 같더라고요.", did="D4")
r("SPK04", "영상은 그럼 다음 분기 초에 다시 얘기하는 거죠? 그때는 저도 준비해 올게요.", "open_question", did="D4",
  note="보류된 영상을 언제 다시 볼지 확인", tag="q_video_again")
r("SPK01", "네 그때 인력 상황 보고 다시 보죠.", did="D4")
r("SPK04", "네.", did="D4")
r("SPK03", "그 안내문에 세척 기준도 한 줄 넣어 주시면 좋겠어요. 그게 있어야 저도 안심이 되거든요.")
r("SPK02", "네 그건 은별 씨 문구 받아서 넣을게요. 이따 메신저로 좀 주세요.", "commitment", rt="q_video_again",
  note="세척 기준 문구 반영을 맡음")

# --- T5: closing time, region D5 (a superior's proposal nobody answers) ------
r("SPK05", "아 그리고 마감 직전에 리필하러 오시는 분들 때문에 퇴근이 계속 늦어져요.",
  "concern", did="D5", note="마감 직전 리필로 퇴근이 늦어진다는 문제, unprompted",
  tag="c_closing")
r("SPK05", "세척대 정리에 이십 분은 걸리는데 그 전에 손님이 오시면 못 닫아요.", did="D5")
r("SPK05", "성수는 거의 매일 한 삼십 분씩 늦게 닫고 있는 상황이에요.", did="D5")
r("SPK05", "그것도 수당 처리가 안 되니까 다들 좀 불만이 있으시고요.", did="D5")
r("SPK05", "이게 이제 계속 쌓이면 사람이 나가는 문제로 번지거든요.", did="D5")
r("SPK02", "그거 파일럿 때도 나왔던 얘기인데 그냥 넘어갔었죠. 그때는 손님이 적어서 그랬던 것 같아요.", did="D5")
r("SPK01", "그건 그냥 마감 한 시간 전에 닫고 그 뒤로는 안 받는 게 나을 것 같은데요.",
  "decision", did="D5", settles=True, note="상급자 제안, 이후 아무도 답하지 않음, 상급자",
  tag="d5_settle")
r("SPK02", "그리고 아까 그 표 말인데요, 일차 매장 목록에 하남을 넣어야 되나요?",
  "open_question", note="일차 매장 목록에 하남 포함 여부를 물음", tag="q_hanam")
r("SPK05", "하남은 배수가 막혀서 이차로 가는 게 맞아요. 저도 그거 보고 좀 아쉬웠어요.")
r("SPK05", "거기는 공사를 해도 뒤쪽 공간이 좁아서 세척대를 놓을 데가 없어요.")
r("SPK02", "근데 하남이 매출이 제일 높은 데 아니에요? 그래서 여쭤보는 거예요.")
r("SPK05", "매출은 높은데 그건 화장품보다 잡화가 잘 나가서 그런 거예요.")
r("SPK01", "그건 아까 정한 대로 가고 예외는 지금 만들지 말죠. 하나 열어 주면 또 다 얘기 나와요.")
r("SPK02", "네.")

# --- T6: the opening date, region D6 (relative deadline) ---------------------
r("SPK02", "오픈일은 저번 회의 때 말한 그 날짜 그대로 가는 거죠? 저는 그렇게 알고 준비했는데요.", "open_question",
  did="D6", note="오픈일 유지 여부를 확인", tag="q_open")
r("SPK01", "그대로 간다고 보고는 올라가 있어요. 바꾸려면 결재를 다시 받아야 되고요.",
  did="D6", tag="fixed_open")
r("SPK01", "그 날짜가 브랜드 데이 첫날이라서 광고랑 같이 묶여 있거든요.", did="D6")
r("SPK01", "그래서 사실 저희가 지금 움직일 수 있는 건 앞쪽 일정밖에 없어요.", did="D6")
r("SPK01", "뒤로 미루는 건 이제 광고 때문에 아예 얘기가 안 되는 거고요.", did="D6")
r("SPK03", "용기 입고가 그 전에 다 들어오는 게 맞아요? 저는 좀 빠듯해 보이는데요.",
  "open_question", did="D6", note="용기 입고 일정이 맞는지 물음", tag="q_stock")
r("SPK02", "지금 발주를 넣으면 한 삼 주 뒤에 들어오니까 오픈 사흘 전쯤 들어와요.", did="D6",
  tag="a_stock")
r("SPK03", "사흘이면 검수할 시간이 없는데요. 라벨 불량 나면 그거 다 못 씁니다.",
  "concern", did="D6", rt="a_stock", note="검수 시간 부족과 라벨 불량 위험", tag="c_inspect")
r("SPK03", "작년에 그 핸드워시 용기 때 라벨이 반이나 삐뚤게 붙어 왔었잖아요.", did="D6")
r("SPK03", "그때 다시 받느라 이 주가 그냥 날아갔어요. 그거 생각하면 아직도 좀 그래요.", did="D6")
r("SPK03", "그래서 저는 최소 닷새는 있어야 된다고 보는 입장이에요.", did="D6")
r("SPK03", "닷새면 뭐 라벨 문제 생겨도 다시 받을 여유가 조금은 있거든요.", did="D6")
r("SPK02", "그건 업체를 바꿨으니까 이번엔 좀 다를 것 같긴 한데요.", did="D6")
r("SPK03", "그래도 저는 그거 그대로는 못 받아요. 제 이름으로 나가는 거라서요.", did="D6")
r("SPK01", "그러면 오픈을 미루든지 입고를 당기든지 둘 중 하나인데요.", did="D6")
r("SPK04", "오픈은 못 미뤄요. 브랜드 데이에 맞춰서 광고가 이미 다 잡혀 있어요.",
  "concern", did="D6", rt="fixed_open", note="광고 일정 때문에 오픈 연기는 불가하다는 반대")
r("SPK04", "매체 쪽은 한 달 전에 지면을 잡아 놔서 지금 빼면 위약금이 나와요.", did="D6")
r("SPK04", "그게 뭐 천만 원 단위라서 저희가 감당할 수 있는 게 아니고요.", did="D6")
r("SPK04", "그래서 오픈일은 이제 진짜 고정이라고 보시는 게 맞아요.", did="D6")
r("SPK02", "그러면 용기 입고를 저번에 말한 날짜보다 이틀 앞당겨서 받는 수밖에 없는데요.",
  did="D6", tag="rel_pull")
r("SPK02", "업체에 얘기하면 이틀 정도는 당겨 줄 수도 있다고 들었어요.", did="D6")
r("SPK02", "대신 그러면 검수를 저희가 주말에 해야 될 수도 있어요.", did="D6")
r("SPK02", "그건 뭐 은별 씨 쪽이랑 좀 더 맞춰 봐야 될 것 같긴 한데요.", did="D6")
r("SPK01", "그러면 오픈일은 그대로 두고 용기 입고만 당겨 받는 쪽으로 정리할게요.",
  "decision", did="D6", settles=True,
  note="오픈일 고정과 검수 시간 확보를 입고 선행으로 절충", tag="d6_settle")
r("SPK02", "네 그럼 제가 업체에 오늘 중으로 연락해 볼게요. 담당자가 오늘 있는지는 모르겠지만요.", "commitment", did="D6",
  rt="d6_settle", note="본인이 오늘 중으로 발주 조정을 맡음", tag="c_vendor")
r("SPK03", "당겨서 들어오면 저희가 검수는 이틀 안에 끝내겠습니다. 사람 더 붙여서라도 하겠습니다.", "commitment", did="D6",
  rt="d6_settle", note="검수 기간을 스스로 약속함", tag="c_qc")
r("SPK01", "만약에 업체가 안 된다고 하면 그때는 다시 모여서 봐야 될 것 같아요.", did="D6")
r("SPK04", "광고는 뭐 어차피 취소가 안 되니까요.")
r("SPK01", "그쵸.")

# --- closing -----------------------------------------------------------------
r("SPK01", "자 그럼 오늘 나온 거 한 번만 정리하고 마칠게요. 빠진 거 있으면 말씀해 주시고요.")
r("SPK01", "매장은 일곱 군데 먼저 열고 나머지 다섯은 이차로 미루는 거고요.")
r("SPK01", "용기는 저희 것만 받다가 시험 결과 보고 다시 보는 거예요.")
r("SPK02", "가격은 이십오 프로에 멤버십 제외고요. 그건 지훈 씨가 고치시는 거고요.")
r("SPK01", "안내문은 겨울 씨가 하시고 영상은 다음 분기로 넘어갔고요.")
r("SPK03", "저는 법 기준이랑 시험 의뢰 그렇게 두 개 맞죠? 다른 건 없는 거죠?", "open_question",
  note="본인이 맡은 일을 확인", tag="q_mine")
r("SPK01", "네 맞아요.")
r("SPK05", "저는 매장 현황 표요.")
r("SPK01", "네 그거 수요일까지 부탁드릴게요. 늦어지면 미리 말씀 주시고요.")
r("SPK04", "가격표는 제가 금요일까지 고쳐 놓는 거고요. 인쇄본은 그 전에 보내고요.", "commitment", rt="q_mine",
  note="앞서 맡은 일을 다시 확인, 상기")
r("SPK01", "다음 회의는 다음 주 목요일 같은 시간에 할게요. 장소는 따로 공지드릴게요.")
r("SPK02", "그때 안내문 초안도 같이 보면 될 것 같아요. 제가 미리 올려 놓을게요.")
r("SPK01", "네 그럼 오늘은 여기까지 할게요. 고생하셨습니다.")


# --- decision answer key (addendum 2026-09-21c) -------------------------------
DECISIONS = [
    {"id": "D1", "settles": "d1_settle",
     "statement": "리필 스테이션 확대는 열두 개 직영점을 한 번에 열지 않고, 배수구가 있는 일곱 개 매장만 일차로 열고 나머지 다섯 곳은 이차로 미룬다.",
     "owner": "SPK05", "due": "다음 주 수요일 (일차 매장 확정용 현황표)",
     "due_as_said": "다음 주 수요일까지",
     "evidence": ["q_count", "c_construct", "lead_split", "d1_settle", "ask_survey", "c_survey"],
     "note": "공사비와 제외 매장 점장 반발이 양쪽에서 나온 뒤 파트장이 요약하며 확정, 어느 일곱 곳인지는 현황표로 확정됨"},
    {"id": "D2", "settles": "d2_settle",
     "statement": "당분간 리필은 자사 용기로만 받고, 외부 위생 시험 결과가 괜찮게 나오면 그때 개인 용기 허용을 다시 논의한다.",
     "owner": "SPK03", "due": "외부 시험 결과 회신 후 (약 3주)",
     "due_as_said": "결과가 삼 주는 걸린다고 하더라고요",
     "evidence": ["q_recall", "recall", "q_test", "c_test", "d2_settle", "c_notice"],
     "note": "브랜드 콘셉트와 현장 부담 양쪽의 반대를 조건부로 흡수함, 시험 결과 전에는 매장 안내문으로 버팀"},
    {"id": "D3", "settles": "d3_settle",
     "statement": "리필 가격은 본품 대비 이십오 프로 인하로 정하고, 리필 상품은 멤버십 중복 할인 대상에서 제외한다.",
     "owner": "SPK04", "due": "다음 주 금요일 (가격표와 포스 항목 수정)",
     "due_as_said": "다음 주 금요일까지",
     "evidence": ["prop_30", "c_margin", "fake_ok", "objection", "d3_settle", "c_price"],
     "note": "이십오 프로로 합의된 듯했다가 멤버십 중복 할인 때문에 뒤집힌 뒤 두 가지를 묶어 다시 확정됨"},
    {"id": "D4", "settles": "d4_settle",
     "statement": "매장 교육용 영상 제작은 이번 확대에서 빼고 다음 분기로 미루며, 이번에는 한 장짜리 안내문만 만든다.",
     "owner": "SPK02", "due": "다음 회의 전",
     "due_as_said": "다음 회의 전까지",
     "evidence": ["dump", "reluctant", "ask_owner", "d4_settle", "c_onepager", "due_onepager"],
     "note": "마케팅 쪽에 떠넘겨졌다가 아무도 온전히 받지 않아 영상은 보류, 안내문만 상품기획이 맡음"},
    {"id": "D5", "settles": "d5_settle",
     "statement": "리필 스테이션은 매장 마감 한 시간 전에 운영을 끝내고 그 뒤로는 접수를 받지 않는다.",
     "owner": "", "due": "", "due_as_said": "",
     "evidence": ["c_closing", "d5_settle"],
     "note": "퇴근 지연 문제 뒤 파트장이 제안했으나 아무도 답하지 않고 다음 안건으로 넘어감, 담당과 시행일은 끝까지 안 나옴"},
    {"id": "D6", "settles": "d6_settle",
     "statement": "일차 오픈일은 기존 날짜를 그대로 두고, 용기 입고만 앞당겨 받아 검수 시간을 확보한다.",
     "owner": "SPK02", "due": "기존 입고일 이틀 앞당김 (오픈 닷새 전)",
     "due_as_said": "저번에 말한 날짜보다 이틀 앞당겨서",
     "evidence": ["q_open", "fixed_open", "c_inspect", "rel_pull", "d6_settle", "c_vendor"],
     "note": "검수 사흘로는 부족하다는 반대와 광고로 고정된 오픈일이 부딪혀 입고 선행으로 절충, 업체가 거절하면 다시 모이기로 함"},
]


def build() -> None:
    n = len(rows)
    if not 260 <= n <= 340:
        print(f"WARNING rows {n} outside 260-340")

    # Start times: a long row takes longer to say. Scaled so the last row lands
    # inside the 1,700-1,850 s band with every gap inside 1-15.5 s.
    raw = [1.9 + len(row["text"]) * 0.09 for row in rows[1:]]
    first, target = 9.4, 1782.0
    scale = (target - first) / sum(raw)
    for _ in range(40):
        gaps = [min(15.0, max(1.1, g * scale)) for g in raw]
        total = sum(gaps)
        if abs(first + total - target) < 0.5:
            break
        scale *= (target - first) / total
    starts, now = [first], first
    for gap in gaps:
        now += round(gap, 2)
        starts.append(round(now, 2))

    out_rows = []
    for index, row in enumerate(rows):
        number = index + 1
        rt = tags[row["rt"]] if row["rt"] else ""
        if rt and rt >= number:
            raise SystemExit(f"responds_to {rt} is not earlier than row {number}")
        out_rows.append({
            "row": str(number),
            "utterance_id": f"{MEETING}-{number:04d}",
            "start": f"{starts[index]:.2f}",
            "speaker": row["speaker"],
            "role": ROLE[row["speaker"]],
            "text": row["text"],
            "kind": row["kind"],
            "decision_id": row["decision_id"],
            "settles": "1" if row["settles"] else "",
            "responds_to": str(rt) if rt else "",
            "note": row["note"],
        })

    cols = ["row", "utterance_id", "start", "speaker", "role", "text", "kind",
            "decision_id", "settles", "responds_to", "note"]
    OUT.mkdir(parents=True, exist_ok=True)
    for suffix, labelled in ((".C.csv", True), (".A.csv", False)):
        with (OUT / f"{MEETING}{suffix}").open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=cols)
            writer.writeheader()
            for row in out_rows:
                writer.writerow(row if labelled else {**row, **{c: "" for c in cols[6:]}})

    key_cols = ["decision_id", "settles_row", "statement", "owner", "due",
                "due_as_said", "evidence_rows", "note"]
    with (OUT / f"{MEETING}.D.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=key_cols)
        writer.writeheader()
        for key in DECISIONS:
            writer.writerow({
                "decision_id": key["id"],
                "settles_row": str(tags[key["settles"]]),
                "statement": key["statement"],
                "owner": key["owner"],
                "due": key["due"],
                "due_as_said": key["due_as_said"],
                "evidence_rows": ",".join(str(tags[t]) for t in key["evidence"]),
                "note": key["note"],
            })

    (OUT / f"{MEETING}.speakers.json").write_text(
        json.dumps(SPEAKERS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    kinds: dict[str, int] = {}
    for row in rows:
        kinds[row["kind"]] = kinds.get(row["kind"], 0) + 1
    print(f"rows {n}  last start {starts[-1]}  decisions {len(DECISIONS)}")
    print("  " + "  ".join(f"{k} {v}" for k, v in sorted(kinds.items())))


if __name__ == "__main__":
    build()
