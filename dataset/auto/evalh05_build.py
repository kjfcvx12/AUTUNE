"""Build EVALH_05 (A/C/D csv + speakers.json) for the hard dummy evaluation set.

Authored for `team_dummy/SPEC.md` addenda 2026-09-21, 09-21b and 09-21c. The
dialogue is held here as one list so row numbers, utterance ids, start times and
every cross-reference (`responds_to`, `evidence_rows`) are generated instead of
hand-typed -- hand-numbering is what broke the earlier meetings.

    python evalh05_build.py

Writes into ../extraction_eval_dummy_hard/. Prints counts only.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

MEETING = "EVALH_05"
OUT = Path(__file__).resolve().parent.parent / "extraction_eval_dummy_hard"

SPEAKERS = {
    "meeting": MEETING,
    "title": "한빛로지스 동탄 2센터 피킹 로봇 파일럿 확대 회의",
    "type": "with-senior",
    "position_order": ["사원", "주임", "대리", "과장", "차장", "부장", "이사", "대표"],
    "speakers": [
        {"speaker": "SPK01", "name": "정해든", "team": "물류운영팀", "job": "Ops",
         "position": "과장", "title": "파트장"},
        {"speaker": "SPK02", "name": "노선재", "team": "물류운영팀", "job": "Ops",
         "position": "대리", "title": ""},
        {"speaker": "SPK03", "name": "임세라", "team": "자동화기술팀", "job": "Data",
         "position": "대리", "title": ""},
        {"speaker": "SPK04", "name": "배도현", "team": "센터운영본부", "job": "Ops",
         "position": "부장", "title": "본부장"},
        {"speaker": "SPK05", "name": "최유나", "team": "안전보건팀", "job": "HR",
         "position": "주임", "title": ""},
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
r("SPK01", "자 두 시 십 분이니까 본부장님 오시기 전에 일단 먼저 시작할게요.")
r("SPK01", "오늘은 비동 파일럿 이 주 돌린 결과부터 보고 확대 범위를 좀 정하려고요.")
r("SPK01", "설 물량 들어오기 전에 정할 건 정해 놔야 되는데 솔직히 시간이 빠듯하죠.")
r("SPK01", "저번에 나왔던 것 중에 아직 안 정해진 게 한 네다섯 개는 남아 있거든요.")
r("SPK01", "그중에 그 확대 범위랑 교육 두 개는 오늘 안 정하면 진짜 답이 없어요.")
r("SPK01", "나머지는 뭐 다음 주로 넘어가도 일정상 크게 문제는 없을 것 같고요.")
r("SPK01", "그래서 오늘은 그 두 개에 시간을 좀 많이 쓰려고 생각하고 있어요.")
r("SPK02", "네.")
r("SPK01", "그거 오늘 못 털면 이제 성수기 들어가서는 아예 손도 못 대는 상황이에요.")
r("SPK02", "근데 파트장님, 현장에는 다음 주에 뭐가 어떻게 바뀌는지 아직 공지가 안 나갔어요.",
  "concern", note="unprompted, 현장 공지가 아직 안 나간 위험을 먼저 꺼냄")
r("SPK02", "저희 조 사람들은 그 로봇이 비동 전체에 다 깔리는 걸로 알고 있더라고요.")
r("SPK02", "그래서 이번 주에만 두 명이 저한테 와서 자리 옮기는 거냐고 물어봤어요.")
r("SPK02", "그때마다 저는 아직 정해진 게 없다고만 얘기하고 있는 상황이거든요.")
r("SPK02", "근데 그게 몇 번 반복되니까 이제 다들 뭔가 숨긴다고 생각하시더라고요.")
r("SPK01", "아 그 얘기는 이따 교육이랑 묶어서 할게요. 그것도 오늘 안건이긴 해요.")
r("SPK01", "일단 세라 씨가 이 주 치 숫자를 정리해 오셨으니까 그것부터 좀 들을게요.")
r("SPK01", "숫자가 다 안 맞아도 되니까 일단 눈에 띄는 것 위주로만 말씀해 주세요.")
r("SPK03", "네 그러면 제가 그 대시보드에서 뽑은 순서대로 좀 말씀드릴게요.")
r("SPK03", "일단 이 주 동안 로봇 여섯 대를 비동 이 층 피킹 존에서만 돌렸는데요,")
r("SPK03", "하루 평균 처리량은 사람만 했을 때보다 한 십팔 프로 정도 올라갔어요.")
r("SPK03", "근데 이게 첫 주에는 십 프로도 안 나왔고 둘째 주에 확 올라간 거라서요.")
r("SPK03", "그 숫자를 그대로 성수기에 대입하는 건 저도 좀 조심스럽긴 하더라고요.")
r("SPK05", "음.")
r("SPK01", "그 십팔 프로는 야간까지 다 합친 거예요, 아니면 주간만 보신 거예요?",
  "open_question", note="처리량 숫자의 집계 범위를 물음", tag="q_range")
r("SPK03", "주간만 본 거예요. 야간은 두 번밖에 못 돌려서 아예 빼고 계산했어요.")
r("SPK03", "야간은 그 충전이 좀 걸리는 게 있어서 그 얘기는 이따 따로 드릴게요.")
r("SPK03", "아 그리고 첫 주 숫자에는 로봇이 그냥 서 있던 시간도 다 들어가 있어요.")
r("SPK03", "그거를 빼고 다시 계산하면 첫 주도 한 십사 프로 정도는 나오기는 해요.")
r("SPK03", "그래서 둘째 주에 확 좋아졌다기보다 첫 주가 좀 깎인 쪽에 가까워요.")

# --- pilot numbers -----------------------------------------------------------
r("SPK03", "그리고 오배송률은 이제 파일럿 존만 보면 영점 사에서 영점 일칠로 떨어졌고요,")
r("SPK03", "이건 로봇이 잘해서라기보다 그 피킹 순서를 시스템이 잡아 줘서 그런 것 같아요.")
r("SPK03", "사람이 동선을 알아서 짜던 걸 이제 화면이 시키는 대로만 하니까요.")
r("SPK03", "그러니까 그 숙련자하고 신입 차이가 좀 줄어드는 그런 효과가 있는 거예요.")
r("SPK03", "대신 숙련자 입장에서는 좀 답답하다는 얘기도 나오긴 하더라고요.")
r("SPK02", "그건 맞아요. 신입들은 그게 편하다고 하더라고요.")
r("SPK03", "대신 로봇이 중간에 선 횟수가 이 주 동안 서른한 번인데 이게 좀 많아요.")
r("SPK03", "한 번 서면 다시 붙는 데까지 평균 사 분 정도 걸리거든요.")
r("SPK01", "서른한 번이면 하루에 두 번 넘게 선 거네요. 주로 왜 서는 거예요?",
  "open_question", note="로봇 정지 원인을 물음", tag="q_stop")
r("SPK03", "제일 많은 게 그 파레트가 통로에 삐져나와 있는 경우고요,")
r("SPK03", "그 다음이 사람이 로봇 앞으로 그냥 지나가 버리는 경우예요.")
r("SPK03", "둘이 합치면 서른한 번 중에 스물세 번이라서 사실 거의 다예요.")
r("SPK03", "나머지 여덟 번은 뭐 통신이 끊기거나 배터리가 애매할 때 선 거고요.")
r("SPK03", "그건 무브온에서 펌웨어만 한 번 올리면 좀 줄어든다고 하더라고요.")
r("SPK03", "그래서 저는 이제 사람하고 부딪히는 그 두 개가 진짜 문제라고 봐요.")
r("SPK02", "아 그거는 저희가 말한 대로 통로 폭이 좁아서 그런 거예요.",
  "concern", rt="q_stop", note="정지 원인을 로봇이 아니라 통로 폭 문제로 돌림")
r("SPK02", "비동 이 층은 원래 카트 두 대가 겨우 비껴가는 폭이거든요.")
r("SPK02", "거기에 로봇이 들어오면 사람이 옆으로 붙어서 기다려야 되는 구조라서요.")
r("SPK02", "그게 하루에 몇 번씩 반복되니까 다들 좀 예민해져 있는 상태거든요.")
r("SPK02", "저희 조장들은 그래서 차라리 로봇을 한 줄에 몰아 달라고 하더라고요.")
r("SPK02", "한 줄만 로봇이 쓰고 나머지 세 줄은 사람이 쓰면 부딪힐 일이 없잖아요.")
r("SPK02", "근데 그렇게 하면 이제 그 줄에 있는 물건만 로봇이 나르게 되는 거라서요.")
r("SPK02", "그게 되는 건지는 저도 잘 몰라서 일단 얘기만 좀 꺼내 놓는 거예요.")
r("SPK05", "음…")
r("SPK04", "아 늦었네요. 주차장에서 좀 걸렸어요. 하던 거 그냥 계속하세요.")
r("SPK01", "네 본부장님 마침 파일럿 숫자 막 끝났어요. 세라 씨가 정리해 왔거든요.")
r("SPK04", "그 숫자는 아까 메일로 봤어요. 십팔 프로짜리 그거 맞죠?",
  "open_question", rt="q_range", note="메일로 본 숫자가 같은 건지 확인함")
r("SPK03", "네 맞습니다. 근데 그게 주간만 본 거라서 야간은 아직 못 넣었어요.")
r("SPK04", "알겠어요. 어차피 성수기는 야간이 관건이라 그건 좀 봐야 될 텐데.")
r("SPK01", "그래서 그 얘기를 오늘 하긴 할 거예요. 일단 확대 범위부터 정리할게요.")

# --- D1: how far the pilot expands -------------------------------------------
r("SPK01", "원래 계획은 이제 비동 삼 층까지 한 번에 올리는 거였잖아요.", "none", "D1",
  note="")
r("SPK01", "근데 저는 그게 성수기 전에 되겠나 싶은 생각이 좀 들거든요.", "none", "D1")
r("SPK01", "삼 층은 그 랙도 높고 물건도 좀 달라서 손댈 게 많더라고요.", "none", "D1")
r("SPK01", "그래서 오늘 그거를 그대로 갈지 아니면 좀 바꿀지를 정해야 돼요.", "none", "D1")
r("SPK01", "세라 씨 보기에는 삼 층까지 이제 이 주 안에 까는 게 가능한 거예요?",
  "open_question", "D1", note="확대 범위가 일정상 가능한지 물음", tag="q_scope")
r("SPK03", "물리적으로 로봇 까는 거는 뭐 사흘이면 되는데요,", "none", "D1")
r("SPK03", "삼 층은 그 랙 높이가 달라서 맵을 아예 새로 떠야 돼요.", "none", "D1")
r("SPK03", "그 맵 뜨는 걸 무브온 쪽에서 해 줘야 하는데 지금 대기가 좀 길더라고요.", "none", "D1")
r("SPK03", "지금 걸어 놓은 센터가 네 갠가 다섯 개 된다고 저번에 들었거든요.", "none", "D1")
r("SPK03", "저희가 먼저 해 달라고 해도 그 순서를 바꿔 주지는 않더라고요.", "none", "D1")
r("SPK03", "지난번에 비동 이 층 할 때도 맵만 열흘 넘게 걸렸거든요.", "concern", "D1",
  rt="q_scope", note="벤더 맵 작업 대기 때문에 일정이 어렵다고 봄", tag="c_map")
r("SPK02", "잠시만요, 저는 삼 층보다 씨동 입고 존이 먼저인 것 같은데요.", "none", "D1")
r("SPK02", "거기가 지금 성수기 때마다 제일 먼저 터지는 데거든요.", "none", "D1")
r("SPK02", "작년에도 그 입고 존에서 밀려서 이 층이 통째로 세 시간 멈췄잖아요.", "none", "D1")
r("SPK02", "삼 층은 사실 물량이 그렇게 많지도 않아요. 급한 데가 아니에요.", "none", "D1")
r("SPK02", "씨동은 지금 그 입고 검수를 사람이 손으로 다 옮겨서 쌓고 있거든요.", "none", "D1")
r("SPK02", "거기에 로봇이 두 대만 들어가도 그 라인은 아예 달라질 거예요.", "none", "D1")
r("SPK05", "그렇죠.")
r("SPK01", "음 씨동 입고 존은 그 바닥이 좀 안 좋지 않아요? 작년에 다시 깐다고 했던 데 아니에요?",
  "open_question", "D1", note="씨동 바닥 상태를 확인함", tag="q_floor")
r("SPK02", "거기는 작년 가을에 보수했어요. 지금은 이 층보다 오히려 평평해요.", "none", "D1")
r("SPK03", "아 그러면 씨동은 맵을 새로 안 떠도 되나요? 거기 도면이 있었던 것 같은데.",
  "open_question", "D1", rt="q_floor", note="씨동 맵 작업이 필요한지 물음")
r("SPK02", "작년에 그 자동창고 검토할 때 떠 놓은 게 있을 거예요. 제가 찾아볼게요.",
  "commitment", "D1", rt="q_scope", note="기한 없이 도면 찾아보겠다고 맡음", tag="com_map")
r("SPK02", "그때 업체가 와서 다 재 갔으니까 아마 그 파일이 어딘가 있을 거예요.", "none", "D1")
r("SPK02", "없으면 뭐 그때 그 업체한테 다시 달라고 하면 되는 거기도 하고요.", "none", "D1")
r("SPK03", "그 도면 있으면 진짜 빨라져요. 그러면 다음 주 안에도 충분히 가능하고요.", "none", "D1")
r("SPK03", "맵만 있으면 이제 로봇 옮기는 거는 뭐 반나절이면 끝나는 일이라서요.", "none", "D1")
r("SPK03", "대신 씨동은 그 바닥에 붙이는 마커를 다시 깔아야 되긴 할 거예요.", "none", "D1")
r("SPK03", "그건 저희 팀에서 저녁에 두 시간 정도만 받으면 할 수 있어요.", "none", "D1")
r("SPK04", "삼 층을 빼면 그 위에 보고한 대수는 어떻게 맞출 거예요?", "open_question", "D1",
  note="본부 보고 대수와 어긋나는 점을 물음", tag="q_count")
r("SPK01", "대수는 그대로예요. 여섯 대를 삼 층 대신 씨동에 넣는 거라서요.", "none", "D1")
r("SPK04", "그러면 뭐 나는 상관없어요. 현장이 편한 데로 하는 게 맞죠.", "none", "D1")
r("SPK01", "그럼 이번에는 그 여섯 대를 씨동 입고 존에 넣고 비동 삼 층은 빼요.", "decision", "D1",
  settles=True, note="논의 정리형 결정, 종결 어미 없이 범위만 다시 말함", tag="d1_settle")
r("SPK01", "삼 층은 성수기 끝나고 나서 그때 다시 얘기하는 게 나을 것 같아요.", "none", "D1")
r("SPK01", "어차피 삼 층은 그 랙 바꾸는 얘기도 같이 나와야 되는 데라서요.", "none", "D1")
r("SPK03", "네 그러면 제가 그 씨동 도면 받는 대로 무브온에 맵 작업 걸어 둘게요.",
  "commitment", "D1", rt="d1_settle", note="확대 결정에 따라 맵 작업 의뢰를 맡음", tag="com_vendor")
r("SPK01", "그거 다음 주 수요일까지는 걸려야 성수기 전에 한 바퀴 돌려 보거든요.", "none", "D1",
  tag="due_wed")
r("SPK03", "수요일이요? 그러면 도면을 월요일에는 받아야 되는데.", "none", "D1")
r("SPK02", "네 월요일 오전까지 드릴게요. 어디 있는지는 대충 아니까요.", "commitment", "D1",
  rt="due_wed", note="도면 전달 기한을 스스로 월요일로 당겨 맡음", tag="com_mon")

# --- side talk 1 -------------------------------------------------------------
r("SPK05", "아 근데 아까 본부장님 주차장에서 걸리셨다는 게 그 공사 때문이에요?", "none", "",
  note="사담")
r("SPK04", "네 그 뒤쪽을 다 파 놔서 지금 한 바퀴를 돌아서 들어와야 돼요.", "none", "",
  note="사담")
r("SPK02", "저희 조 사람들도 요즘 그거 때문에 십 분씩 일찍 나온대요.", "none", "", note="사담")
r("SPK02", "아침에 그 사거리에서 좌회전이 아예 안 되니까 다들 돌아서 오는 거죠.", "none", "",
  note="사담")
r("SPK05", "셔틀은 그래도 앞쪽으로 들어오더라고요. 저는 그거 타고 다녀요.", "none", "",
  note="사담")
r("SPK01", "공사 언제 끝난다고 그랬죠? 뭐 다음 달이라고 들은 것 같은데.", "none", "",
  note="사담")
r("SPK04", "몰라요 그건. 자 그건 됐고 야간 얘기 한다고 하지 않았어요?", "none", "")

# --- D2: night shift on hold -------------------------------------------------
r("SPK01", "네 야간이요. 세라 씨 아까 충전이 걸린다고 하셨는데 그게 무슨 얘기예요?",
  "open_question", "D2", note="야간 운영의 충전 문제를 물음", tag="q_charge")
r("SPK03", "지금 충전기가 세 대인데요, 한 번 완충에 두 시간 반이 걸리거든요.", "none", "D2")
r("SPK03", "주간에는 쉬는 시간에 돌려 가면서 하니까 여섯 대가 다 돌아가는데,", "none", "D2")
r("SPK03", "그것도 사실 누가 시간 맞춰서 꽂아 주니까 그렇게 도는 거거든요.", "none", "D2")
r("SPK03", "지금은 그걸 저희 팀 인턴분이 오전 오후로 나눠서 해 주고 있어요.", "none", "D2")
r("SPK03", "야간은 사람이 적어서 그 돌리는 걸 누가 봐 줘야 되는 게 좀 애매해요.", "none", "D2")
r("SPK03", "그래서 지난주에 두 번 돌렸을 때는 제가 열 시까지 남아서 봤어요.", "none", "D2")
r("SPK03", "그때 보니까 한 번에 두 대씩밖에 못 꽂아서 계속 왔다 갔다 해야 되고요.", "none", "D2")
r("SPK03", "그걸 야간조 반장님이 하시기에는 솔직히 좀 번거로운 일이더라고요.", "none", "D2")
r("SPK02", "그걸 매일 하실 수는 없잖아요. 그건 사람이 붙어야 되는 일이에요.", "concern", "D2",
  rt="q_charge", note="야간 충전 관리에 사람이 필요하다는 점을 지적함", tag="c_night")
r("SPK02", "야간조는 지금도 한 조에 네 명이에요. 거기서 한 명 빼면 라인이 안 돌아가요.", "none", "D2")
r("SPK02", "성수기 되면 그 네 명으로도 빠듯해서 지원을 더 받아야 되는 상황이고요.", "none", "D2")
r("SPK02", "거기서 로봇까지 보라고 하면 이제 아무도 야간 안 하려고 할 거예요.", "none", "D2")
r("SPK05", "야간에 로봇 붙이시려면 그 야간 안전 교육을 따로 또 해야 돼요.", "concern", "D2",
  rt="q_charge", note="야간 운영 시 추가 안전 교육 부담을 제기함", tag="c_train")
r("SPK05", "주간 교육하고 내용이 달라서 그건 본사 안전팀 승인도 받아야 되거든요.", "none", "D2")
r("SPK05", "야간은 조명이랑 시야가 다르다고 아예 다른 과정으로 보더라고요.", "none", "D2")
r("SPK04", "음.")
r("SPK04", "그 승인은 얼마나 걸리는데요?", "open_question", "D2", rt="c_train",
  note="안전 교육 승인 소요 기간을 물음", tag="q_approve")
r("SPK05", "빠르면 이 주고요, 작년에 저희 삼 센터는 한 달 넘게 걸렸다고 들었어요.", "none", "D2")
r("SPK05", "그것도 그때는 설비가 좀 단순한 거였고 로봇은 처음이라 더 걸릴 거예요.", "none", "D2")
r("SPK05", "저희가 서류를 다 맞춰서 올려도 그쪽 일정이라는 게 있으니까요.", "none", "D2")
r("SPK04", "한 달이면 성수기 다 지나가네요. 그러면 이거는 뭐 답이 없는 건데.", "none", "D2")
r("SPK01", "충전기를 두 대 더 넣으면 사람 없이도 되는 거 아니에요?", "open_question", "D2",
  note="충전기 증설로 해결되는지 물음", tag="q_charger")
r("SPK03", "충전기만 넣는다고 되는 게 아니고요, 그 자리 전기 공사를 해야 돼요.", "none", "D2")
r("SPK03", "견적을 한번 받아 보긴 했는데 공사까지 하면 한 천이백 정도 나오더라고요.", "none", "D2")
r("SPK03", "아 천이백이 아니라 천사백이었나 그러네요. 견적서에 그렇게 적혀 있었어요.", "none", "D2")
r("SPK03", "어쨌든 그 정도 금액이면 올해 예산으로는 못 하는 거라고 봐야 돼요.", "none", "D2")
r("SPK01", "천이백이요? 그건 올해 예산으로는 아예 안 되는 금액이네요.", "none", "D2")
r("SPK02", "저희 그냥 야간은 사람으로 가고 로봇은 주간만 돌리죠.", "none", "D2",
  note="")
r("SPK03", "음 그것도 방법이긴 한데 그러면 야간 숫자는 계속 없는 거예요.", "ambiguous", "D2",
  rt="c_night", note="동료 제안에 약한 유보만 표함")
r("SPK01", "야간은 일단 성수기 지나고 다시 봐요. 지금 붙일 방법이 없네요.", "decision", "D2",
  settles=True, note="논의 끝에 보류로 정리, 기한은 말하지 않음", tag="d2_settle")
r("SPK04", "그래요. 대신 성수기 때 야간이 얼마나 밀리는지는 기록은 남겨 놔요.", "none", "D2")
r("SPK03", "그건 제가 야간 물량이랑 같이 그냥 뽑아 두려고요.", "commitment", "D2",
  rt="d2_settle", note="본인 계획으로 야간 기록 수집을 밝힘", tag="com_log")

# --- D3: mixed aisles, safety fence, the false agreement ---------------------
r("SPK01", "다음은 안전 동선인데 이게 오늘 제일 오래 걸릴 것 같아요.", "none", "D3")
r("SPK01", "유나 씨가 저번에 그 혼합 동선은 안 된다고 하셨던 것 같은데요.", "none", "D3")
r("SPK05", "제가 안 된다고 한 게 아니라, 펜스 없이 가려면 근거가 있어야 된다고 한 거예요.",
  "none", "D3")
r("SPK05", "지금 비동 이 층은 로봇하고 사람이 같은 통로를 그냥 같이 쓰고 있잖아요.", "none", "D3")
r("SPK05", "그걸 저희는 이제 혼합 동선이라고 부르는데 기준이 좀 빡빡한 편이에요.", "none", "D3")
r("SPK05", "그거를 정식으로 하려면 위험성 평가를 다시 돌려야 되는 상황이고요.", "none", "D3")
r("SPK05", "그게 서류 몇 장이 아니라 구간별로 다 따져서 쓰는 거라 시간이 좀 걸려요.", "none", "D3")
r("SPK05", "로봇 다니는 통로는 그 속도랑 정지 거리까지 다 적어야 되거든요.", "none", "D3")
r("SPK05", "파일럿이니까 지금까지는 그냥 넘어간 건데 확대하면 얘기가 달라져요.", "concern", "D3",
  note="unprompted, 확대 시 위험성 평가 재실시가 필요하다고 봄", tag="c_risk")
r("SPK01", "그 평가는 누가 하는 거예요? 저희가 하는 거예요 본사가 하는 거예요?",
  "open_question", "D3", rt="c_risk", note="위험성 평가 주체를 물음", tag="q_who_risk")
r("SPK05", "센터에서 초안 쓰고 본사가 확인하는 구조인데, 초안이 좀 일이에요.", "none", "D3")
r("SPK05", "저번에 컨베이어 바꿀 때 제가 써 봤는데 그때 사흘은 꼬박 걸렸어요.", "none", "D3")
r("SPK05", "지금은 그 성수기 준비 서류도 같이 쓰고 있어서 좀 애매하긴 한데요.", "none", "D3")
r("SPK02", "펜스를 치면 그 평가를 안 해도 되는 거예요?", "open_question", "D3", rt="c_risk",
  note="펜스 설치 시 평가 면제 여부를 물음", tag="q_fence")
r("SPK05", "펜스로 완전히 분리되면 그건 또 다른 기준으로 가는 거라 훨씬 간단해져요.", "none", "D3")
r("SPK05", "대신 그 펜스는 아무거나 치면 안 되고 인증된 걸로 해야 되는 거고요.", "none", "D3")
r("SPK05", "비용은 한 구간에 삼백 정도 들었다고 저번에 들은 것 같아요.", "none", "D3")
r("SPK04", "그러면 그냥 펜스 치죠. 그게 제일 깔끔한 거 아니에요?", "none", "D3")
r("SPK03", "펜스를 치면 로봇 동선이랑 사람 동선이 아예 갈라지는 건데요,", "none", "D3")
r("SPK03", "그러면 피킹은 사람이 하고 로봇은 실어 나르기만 하게 되거든요.", "none", "D3")
r("SPK03", "지금 십팔 프로 올라간 게 그 둘이 같이 붙어 다녀서 나온 숫자라서요.", "none", "D3")
r("SPK03", "사람이 집어서 바로 옆에 있는 로봇에 얹으니까 걸음 수가 확 줄거든요.", "none", "D3")
r("SPK03", "갈라 놓으면 그 얹는 자리까지 사람이 다시 걸어가야 되는 거예요.", "none", "D3")
r("SPK03", "갈라 놓으면 그 숫자가 얼마나 남을지는 저도 자신이 없어요.", "concern", "D3",
  rt="c_risk", note="펜스 분리 시 성능 이득이 사라진다고 반대함", tag="c_split")
r("SPK01", "아 그러면 펜스가 답이 아니네요. 그럼 뭐 평가를 돌리는 수밖에 없는데.", "none", "D3")
r("SPK05", "초안은 사실 제가 쓰면 되긴 해요. 양식은 있으니까요.", "none", "D3")
r("SPK01", "그럼 그렇게 하죠. 유나 씨가 초안 쓰시고 저희는 그대로 가는 걸로.", "none", "D3",
  note="번복, 합의된 것처럼 보이지만 바로 뒤에서 뒤집힘", tag="fake_ok")
r("SPK05", "아 맞다, 그게 안 되겠네요. 보험 갱신이 이번 달이잖아요.", "none", "D3")
r("SPK05", "평가 결과가 나오기 전에 갱신이 들어가면 그 조항이 그대로 넘어가요.", "none", "D3")
r("SPK05", "그 조항이 한 번 들어가면 내년 갱신 전까지는 못 바꾸는 거고요.", "none", "D3")
r("SPK05", "그러면 사고 났을 때 로봇 구간은 보상이 안 되는 걸로 잡힐 수도 있어요.", "concern", "D3",
  rt="fake_ok", note="보험 갱신 시점 때문에 앞의 합의가 성립하지 않는다고 뒤집음",
  tag="c_insure")
r("SPK04", "잠깐만요, 그거 지금 처음 듣는 얘긴데요.", "none", "D3")
r("SPK04", "보험 쪽은 왜 아무도 미리 확인을 안 한 거예요?", "open_question", "D3",
  rt="c_insure", note="보험 조건을 사전에 확인하지 않은 점을 따짐")
r("SPK05", "제가 지난주에 알았어요. 그것도 담당자가 지나가다가 말해 준 거고요.", "none", "D3")
r("SPK05", "저희도 그 갱신 서류를 이번 주에 받아서 이제 보고 있는 중이었어요.", "none", "D3")
r("SPK01", "음 그러면 이제 갱신 전에 뭘 해 놔야 되는 거예요?", "open_question", "D3",
  rt="c_insure", note="보험 갱신 전 필요한 조치를 물음", tag="q_before")
r("SPK05", "무브온에서 그 안전 인증 서류를 받아서 같이 넣으면 된다고 하더라고요.", "none", "D3")
r("SPK05", "그 서류가 있으면 로봇 구간도 그냥 일반 설비로 잡힌다고 하더라고요.", "none", "D3")
r("SPK05", "그게 그 유럽 인증 같은 건데 로봇마다 번호가 따로 있는 거래요.", "none", "D3")
r("SPK03", "그 서류는 제가 요청하면 돼요. 저번에 다른 센터 것도 받아 줬거든요.", "none", "D3")
r("SPK03", "그때는 메일 한 번 보내니까 그냥 바로 보내 주기는 했었어요.", "none", "D3")
r("SPK03", "근데 그게 이제 한글로 된 게 아니라서 그건 좀 봐 주셔야 돼요.", "none", "D3")
r("SPK01", "그거 언제까지 받을 수 있는지가 관건이겠네요.", "none", "D3")
r("SPK03", "무브온 쪽은 그 서류는 보통 사흘이면 준다고 하더라고요.", "ambiguous", "D3",
  note="전달, 벤더가 하겠다고 한 내용을 옮김", tag="amb_vendor")
r("SPK04", "사흘이면 갱신 전에는 되겠네. 그럼 그건 그렇게 가고.", "none", "D3")
r("SPK01", "그럼 펜스는 일단 안 치고 지금처럼 같이 쓰되, 그 서류가 갱신 전에 안 오면 그때는 로봇 세우는 걸로 해요.",
  "decision", "D3", settles=True,
  note="조건부 결정, 서류 도착 여부에 따라 운영 중단까지 걸어 둠", tag="d3_settle")
r("SPK05", "네 그러면 저는 위험성 평가 초안은 그거랑 별개로 써 볼게요.", "commitment", "D3",
  rt="d3_settle", note="결정과 별개로 평가 초안 작성을 맡음", tag="com_draft")
r("SPK05", "그건 어차피 나중에 본사에서 달라고 할 서류라 미리 해 두는 게 나아요.", "none", "D3")
r("SPK02", "세우면 그날 물량은 어떻게 되는 거예요? 그건 좀 정해 놔야 되는데.",
  "open_question", "D3", rt="d3_settle", note="중단 시 물량 처리 방식을 물음")
r("SPK01", "세울 일이 없어야죠. 그건 그때 가서 봐야 될 것 같아요.", "none", "D3")

# --- side talk 2 -------------------------------------------------------------
r("SPK04", "아 근데 오늘 식당에 그 갈비탕 나온 거 드신 분 있어요?", "none", "", note="사담")
r("SPK02", "저 먹었어요. 줄이 밖에까지 서 있어서 이십 분 기다렸어요.", "none", "", note="사담")
r("SPK03", "저는 그 줄 보고 그냥 편의점 갔어요. 요즘 계속 그래요.", "none", "", note="사담")
r("SPK03", "거기도 그 시간에는 사람이 몰려서 결국 뭐 비슷하긴 한데요.", "none", "", note="사담")
r("SPK05", "다음 주부터 그 업체 바뀐다고 공지 붙었던데 보셨어요?", "none", "", note="사담")
r("SPK02", "아 그래요? 그러면 좀 나아지려나 모르겠네요.", "none", "", note="사담")
r("SPK01", "자 그 얘기는 이따 하고요, 교육이랑 설명회 얘기 해야 돼요.", "none", "")

# --- the job nobody wants, D5 owner and relative deadline --------------------
r("SPK01", "아까 선재 씨가 말한 그 공지가 사실 이 건이랑 같이 가는 거거든요.", "none", "D5")
r("SPK01", "확대되면 작업자분들한테 설명회를 한 번은 해야 되는 상황이에요.", "none", "D5")
r("SPK01", "로봇이 어디로 다니는지 그것만 알아도 사고가 확 줄어든다고 하더라고요.", "none", "D5")
r("SPK01", "자료 만들고 조별로 돌리고 하는 게 생각보다 일이 좀 많아요.", "none", "D5")
r("SPK01", "조가 여섯 개니까 같은 얘기를 이제 여섯 번은 해야 되는 거잖아요.", "none", "D5")
r("SPK01", "그리고 야간조는 시간이 안 맞아서 따로 한 번 더 해야 되고요.", "none", "D5")
r("SPK01", "이건 현장 쪽에서 알아서 좀 정리해 주시면 좋을 것 같은데요.", "none", "D5",
  tag="dump")
r("SPK02", "…")
r("SPK03", "음.")
r("SPK01", "선재 씨 조장님들하고 제일 많이 얘기하시잖아요.", "none", "D5")
r("SPK02", "아… 예… 일단 제가 한번 보긴 할게요. 근데 자료는 제가 못 만들어요.",
  "ambiguous", "D5", rt="dump", note="위임, 떠넘겨진 일을 마지못해 일부만 받음",
  tag="reluctant")
r("SPK02", "저는 그 화면 캡처 같은 것도 잘 못하고 시간도 솔직히 없거든요.", "none", "D5")
r("SPK02", "성수기 준비하면서 그 입고 스케줄도 제가 다시 짜야 되는 상황이라서요.", "none", "D5")
r("SPK05", "자료는 그 안전 교육 자료에 붙이면 되지 않을까요?", "none", "D5")
r("SPK05", "어차피 저희가 그 로봇 구간 교육 자료를 새로 만들어야 되거든요.", "none", "D5")
r("SPK05", "거기에 로봇이 어떻게 도는지 한 장만 더 붙이면 되는 거니까요.", "none", "D5")
r("SPK05", "같은 사람들한테 같은 시간에 하는 건데 두 번 모을 이유가 없잖아요.", "none", "D5")
r("SPK01", "아 그러네. 그러면 두 개를 따로 만들 이유가 없네요.", "none", "D5")
r("SPK03", "그 교육 자료는 무브온에서 기본 틀을 주기로 했어요. 그거 받아서 고치면 돼요.",
  "none", "D5", tag="vendor_deck")
r("SPK03", "그 틀이 좀 외국 자료를 번역한 거라 손볼 데가 있긴 할 거예요.", "none", "D5")
r("SPK01", "그 틀은 언제 온대요?", "open_question", "D5", rt="vendor_deck",
  note="벤더 교육 자료 도착 시점을 물음", tag="q_deck")
r("SPK03", "다음 주 초에 준다고 했는데 그쪽도 좀 밀리는 것 같더라고요.", "none", "D5")
r("SPK02", "그거 안 오면 설명회도 못 하는 거 아니에요?", "concern", "D5", rt="q_deck",
  note="벤더 자료 지연이 설명회 일정을 막는다고 지적함", tag="c_deck")
r("SPK03", "안 오면 제가 저번 센터 거라도 받아서 드릴게요. 그건 어차피 내용이 비슷해요.",
  "commitment", "D5", rt="c_deck", note="자료 지연 시 대체본을 구해 주기로 맡음")
r("SPK03", "대신 그 센터는 로봇이 여덟 대라서 숫자는 좀 고쳐서 쓰셔야 돼요.", "none", "D5")
r("SPK01", "그럼 설명회는 유나 씨가 저번처럼 해 주시고, 그 자료 나오기 이틀 전까지 조장님들한테는 돌려 주세요.",
  "decision", "D5", settles=True,
  note="담당과 기한을 지정한 결정, 기한이 다른 일정에 걸려 있음", tag="d5_settle")
r("SPK05", "저번처럼이면 그 점심시간에 조별로 십 분씩 하는 거 말씀하시는 거죠?",
  "open_question", "D5", rt="d5_settle", note="지시된 방식이 저번 방식인지 확인함")
r("SPK01", "네 그거요. 그게 사람들 안 빼고 할 수 있는 유일한 방법이더라고요.", "none", "D5")
r("SPK01", "라인 세우고 다 모으면 그날 물량이 그대로 밀려 버리니까요.", "none", "D5")
r("SPK05", "알겠습니다. 그러면 저는 자료 오는 대로 조별 일정부터 잡을게요.",
  "commitment", "D5", rt="d5_settle", note="설명회 담당을 받고 일정 수립을 맡음",
  tag="com_sess")
r("SPK02", "저는 그러면 조장 모으는 것까지만 할게요. 그 정도는 해 드릴 수 있어요.",
  "commitment", "D5", rt="d5_settle", note="기한 없이 조장 소집만 맡음")

# --- D6: what gets measured --------------------------------------------------
r("SPK04", "그 설명회에서 사람들이 제일 궁금해하는 게 뭘 것 같아요?", "open_question", "D6",
  note="작업자 관심사를 물음", tag="q_worry")
r("SPK02", "그거야 뭐 평가죠. 시간당 몇 개 집었냐로 보는 거 아니냐고 다들 그래요.", "none", "D6")
r("SPK02", "로봇 붙은 조는 숫자가 잘 나오고 아닌 조는 안 나오는 게 당연하잖아요.", "none", "D6")
r("SPK02", "그거를 사람들이 모르는 것도 아니고 이미 다 계산하고 있어요.", "none", "D6")
r("SPK02", "벌써 저한테 와서 그 파일럿 조에 넣어 달라는 분도 두 명 있었고요.", "none", "D6")
r("SPK02", "그거를 그대로 조별로 비교해 버리면 진짜 난리 나요.", "concern", "D6", rt="q_worry",
  note="기존 지표를 그대로 쓰면 조별 형평성 문제가 생긴다고 반대함", tag="c_kpi")
r("SPK05", "그건 저희 쪽에도 작년에 비슷한 민원이 들어온 적 있어요.", "none", "D6")
r("SPK05", "그때는 그 설비 들어간 조가 유리하다고 해서 한참 시끄러웠거든요.", "none", "D6")
r("SPK02", "맞아요.")
r("SPK01", "음 그러면 파일럿 기간 동안은 그 지표를 좀 다르게 봐야 되는데.", "none", "D6")
r("SPK03", "제 생각에는 시간당 피킹 수보다 오배송률이 더 맞는 것 같아요.", "none", "D6")
r("SPK03", "그건 로봇이 붙든 안 붙든 조가 얼마나 정확한지가 나오는 거라서요.", "none", "D6")
r("SPK03", "오배송은 이제 그 반품이랑 클레임으로 바로 이어지는 거기도 하고요.", "none", "D6")
r("SPK03", "숫자도 조별로 이미 다 쌓여 있어서 따로 만들 것도 없어요.", "none", "D6")
r("SPK03", "아까 말씀드린 그 영점 일칠도 사실 사람이 잘해서 나온 부분이 커요.", "none", "D6")
r("SPK04", "근데 위에는 처리량으로 보고가 나가고 있어요. 그건 바꾸기가 좀 그런데.", "concern", "D6",
  rt="c_kpi", note="상부 보고 지표와 어긋난다고 우려함", tag="c_report")
r("SPK04", "연초에 그 목표를 처리량으로 잡아 놔서 중간에 바꾸면 또 설명을 해야 돼요.", "none", "D6")
r("SPK01", "보고는 보고대로 하고 조 평가만 오배송률로 보면 안 되나요?", "open_question", "D6",
  rt="c_report", note="보고 지표와 평가 지표 분리 가능성을 물음", tag="q_split")
r("SPK04", "그건 되죠. 어차피 평가는 센터 안에서 하는 거니까.", "none", "D6")
r("SPK01", "그러면 성수기 동안은 조 평가를 시간당 피킹 수 말고 오배송률로 봐요.", "decision", "D6",
  settles=True, note="논의 정리형 결정, 평가 지표만 바꾸기로 함", tag="d6_settle")
r("SPK02", "그거 설명회 때 같이 말해 주시면 좋겠어요. 그게 제일 클 거예요.", "none", "D6")
r("SPK05", "네 그건 제가 그 자료에 한 장 넣을게요.", "commitment", "D6", rt="d6_settle",
  note="평가 지표 변경 안내를 자료에 넣기로 맡음", tag="com_slide")
r("SPK02", "저번 회의 때도 확대 전에 현장 의견 먼저 받기로 했었잖아요.", "commitment", "D6",
  note="상기, 이전 회의에서 정한 사항을 다시 꺼냄", tag="recall")
r("SPK02", "그거를 설명회에서 같이 받아 오면 되지 않을까 싶은데요.", "none", "D6")
r("SPK02", "따로 자리 만들면 어차피 아무도 안 와요. 저번에도 세 명 왔잖아요.", "none", "D6")
r("SPK01", "아 맞다 그거 있었죠. 그럼 그 자리에서 같이 받아 주세요.", "none", "D6")

# --- D4: the senior's proposal nobody answers, and the close -----------------
r("SPK04", "그 보고 얘기가 나와서 말인데 지금 주간 보고가 너무 길어요.", "none", "D4")
r("SPK04", "지난주 거 보니까 표가 여섯 개던데 그거 누가 다 보겠어요.", "none", "D4")
r("SPK04", "나도 사실 맨 위에 두 줄만 보고 나머지는 잘 안 보거든요.", "none", "D4")
r("SPK03", "그거는 이제 처음에 본부에서 항목을 다 달라고 하셔서 넣은 거예요.", "concern", "D4",
  rt="q_worry", note="보고 항목이 늘어난 책임이 본부 요청에 있다고 반박함", tag="c_hist")
r("SPK03", "저도 그거 만드는 데 목요일 오후를 거의 다 쓰거든요.", "none", "D4")
r("SPK03", "표마다 그 데이터 뽑는 데가 달라서 그걸 맞추는 게 일이에요.", "none", "D4")
r("SPK03", "그중에 두 개는 사실 아무도 안 보실 것 같긴 했어요.", "none", "D4")
r("SPK01", "항목을 줄이면 나중에 또 달라고 하실 것 같아서 안 줄인 것도 있어요.", "none", "D4")
r("SPK04", "그럼 성수기 전까지는 하루 처리량이랑 오배송률 두 개로만 정리합시다.", "decision", "D4",
  settles=True, note="상급자 제안, 아무도 답하지 않고 다음 얘기로 넘어감", tag="d4_settle")
r("SPK02", "저 그러면 아까 그 통로 폭은 오늘 안 하나요?", "open_question", "",
  note="미처 다루지 않은 안건을 다시 꺼냄", tag="q_aisle")
r("SPK01", "아 그거 맞다. 그거는 씨동 깔면서 같이 봐야 되는 건데.", "none", "")
r("SPK03", "씨동은 통로가 넓어서 거기는 지금 폭 문제는 없어요.", "none", "")
r("SPK02", "비동 이 층 말한 거예요. 거기는 확대하든 말든 그대로잖아요.", "none", "")
r("SPK01", "제 말은 씨동 맵 뜰 때 이 층도 같이 손보자는 얘기였어요.", "none", "")
r("SPK03", "그거는 맵만으로는 안 되고 랙을 실제로 옮겨야 되는 거라서요.", "concern", "",
  rt="q_aisle", note="통로 폭 문제는 랙 이동이 필요해 맵으로 해결되지 않는다고 함")
r("SPK03", "랙 옮기는 건 주말에 라인 세우고 해야 되는 일이에요.", "none", "")
r("SPK03", "그것도 한 주말에 다 못 하고 두 번은 나눠서 해야 될 거예요.", "none", "")
r("SPK01", "그거는 오늘 정할 수 있는 게 아니네요. 다음에 따로 잡을게요.", "none", "")
r("SPK04", "그 주말 작업은 인건비가 따로 잡혀야 되니까 미리 올려 줘요.", "none", "")
r("SPK04", "그거 성수기 끝나고 하면 예산 항목이 아예 달라져서 더 복잡해져요.", "none", "")
r("SPK01", "네 제가 그건 다음 주에 견적 받아서 올려 보려고요.", "commitment", "",
  note="본인 계획으로 주말 작업 견적 진행을 밝힘", tag="com_quote")
r("SPK05", "저 하나만 더요. 그 설명회 자료에 사진 써도 되는지도 물어봐야 돼요.",
  "open_question", "", note="현장 사진 사용 가능 여부를 확인해야 한다고 물음",
  tag="q_photo")
r("SPK01", "사진이요? 그냥 현장 사진인데 뭐가 문제예요?", "open_question", "", rt="q_photo",
  note="사진 사용에 문제가 있는지 되물음")
r("SPK05", "사람 얼굴이 나오면 그건 동의를 받아야 되는 거라서요.", "none", "")
r("SPK05", "뒷모습만 나온 건 괜찮다고 들었는데 저도 확실하지는 않더라고요.", "none", "")
r("SPK05", "그건 제가 본사에 확인해 보겠습니다.", "ambiguous", "", rt="q_photo",
  note="확인만 하겠다고 하고 구체적인 약속은 없음")
r("SPK01", "네 그럼 오늘은 여기까지 할게요. 다들 고생하셨어요.", "none", "")
r("SPK04", "아 그리고 그 씨동 건은 다음 주 회의 때 한 번 더 봐요.", "none", "")
r("SPK01", "네 그때 맵 진행이랑 같이 보겠습니다.", "none", "")

DECISIONS = [
    {"id": "D1", "settles": "d1_settle",
     "statement": "피킹 로봇 확대 대상을 비동 삼 층 대신 씨동 입고 존으로 바꾸고, 로봇 여섯 대를 그대로 옮겨 넣는다.",
     "owner": "SPK03", "due": "2026-09-30 (맵 작업 의뢰 기준)",
     "due_as_said": "다음 주 수요일까지",
     "evidence": ["q_scope", "c_map", "q_count", "d1_settle", "com_vendor", "due_wed", "com_mon"],
     "note": "벤더 맵 대기와 씨동 우선 주장이 부딪혀 삼 층을 빼는 쪽으로 정리됨, 기한은 결정 뒤 맵 의뢰 일정으로 나옴"},
    {"id": "D2", "settles": "d2_settle",
     "statement": "야간 시간대 로봇 운영은 성수기가 끝날 때까지 하지 않고 보류하며, 야간 지연 기록만 따로 남긴다.",
     "owner": "SPK03", "due": "", "due_as_said": "",
     "evidence": ["q_charge", "c_night", "c_train", "q_approve", "d2_settle", "com_log"],
     "note": "충전 관리 인력과 안전 교육 승인 기간 때문에 보류, 재논의 시점은 성수기 이후로만 말해 날짜가 없음"},
    {"id": "D3", "settles": "d3_settle",
     "statement": "안전 펜스는 설치하지 않고 사람과 로봇이 통로를 같이 쓰되, 벤더 안전 인증 서류가 보험 갱신 전에 오지 않으면 로봇 운영을 중단한다.",
     "owner": "SPK03", "due": "보험 갱신일 전 (서류 접수 기준)",
     "due_as_said": "갱신 전에 안 오면",
     "evidence": ["c_risk", "q_fence", "c_split", "fake_ok", "c_insure", "amb_vendor", "d3_settle"],
     "note": "초안 작성으로 합의된 듯했다가 보험 갱신 시점 때문에 뒤집힌 뒤 서류 도착을 조건으로 다시 정리됨"},
    {"id": "D4", "settles": "d4_settle",
     "statement": "성수기 전까지 주간 보고 항목을 하루 처리량과 오배송률 두 가지로만 줄인다.",
     "owner": "", "due": "성수기 전", "due_as_said": "성수기 전까지",
     "evidence": ["c_hist", "d4_settle", "q_aisle"],
     "note": "본부장이 제안했고 아무도 답하지 않은 채 다음 안건으로 넘어감, 정리할 사람은 끝까지 나오지 않음"},
    {"id": "D5", "settles": "d5_settle",
     "statement": "작업자 설명회는 최유나가 지난번과 같은 조별 십 분 방식으로 맡아 진행한다.",
     "owner": "SPK05", "due": "벤더 교육 자료 도착 이틀 전",
     "due_as_said": "그 자료 나오기 이틀 전까지",
     "evidence": ["dump", "reluctant", "vendor_deck", "q_deck", "c_deck", "d5_settle", "com_sess"],
     "note": "현장에 떠넘겨졌다가 아무도 온전히 받지 않아 안전보건팀이 맡음, 기한이 벤더 자료 도착일에 걸려 있어 날짜가 아직 없음"},
    {"id": "D6", "settles": "d6_settle",
     "statement": "성수기가 끝날 때까지 조별 평가는 시간당 피킹 수가 아니라 오배송률로만 본다.",
     "owner": "SPK05", "due": "설명회 자료 반영 시점",
     "due_as_said": "성수기 동안은",
     "evidence": ["q_worry", "c_kpi", "c_report", "q_split", "d6_settle", "com_slide", "recall"],
     "note": "로봇이 붙은 조가 유리해진다는 반발과 상부 보고 형식 우려를 보고와 평가를 분리해 흡수함"},
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
