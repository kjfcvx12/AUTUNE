"""Build EVALH_02 (A/C/D csv + speakers.json) for the hard dummy evaluation set.

Authored for `team_dummy/SPEC.md` addenda 2026-09-21, 09-21b and 09-21c. The
dialogue is held here as one list so row numbers, utterance ids, start times and
every cross-reference (`responds_to`, `evidence_rows`) are generated instead of
hand-typed -- hand-numbering is what broke the earlier meetings.

    python evalh02_build.py

Writes into ../extraction_eval_dummy_hard/. Prints counts only.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

MEETING = "EVALH_02"
OUT = Path(__file__).resolve().parent.parent / "extraction_eval_dummy_hard"

SPEAKERS = {
    "meeting": MEETING,
    "title": "초록발자국 동물병원 본부 예약 시스템 교체 2차 점검 회의",
    "type": "cross-team",
    "position_order": ["사원", "주임", "대리", "과장", "차장", "부장", "이사", "대표"],
    "speakers": [
        {"speaker": "SPK01", "name": "정하람", "team": "운영지원팀", "job": "Ops",
         "position": "과장", "title": "파트장"},
        {"speaker": "SPK02", "name": "배윤슬", "team": "운영지원팀", "job": "PM",
         "position": "대리", "title": ""},
        {"speaker": "SPK03", "name": "최도경", "team": "정보시스템팀", "job": "Dev",
         "position": "주임", "title": ""},
        {"speaker": "SPK04", "name": "남지우", "team": "정보시스템팀", "job": "Data",
         "position": "대리", "title": ""},
        {"speaker": "SPK05", "name": "오해든", "team": "운영지원팀", "job": "CS",
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
r("SPK02", "아 저 지금 올라오는 중인데 주차장 차단기가 또 안 올라가더라고요.")
r("SPK02", "뒤에 차들이 이제 쭉 밀려 있어서 다른 분들도 좀 늦으실 것 같아요.")
r("SPK02", "관리실에 얘기는 해 뒀는데 오늘 안에 고쳐질지는 저도 잘 모르겠네요.")
r("SPK01", "네 뭐 어쩔 수 없죠. 일단 온 사람들끼리 그냥 시작하고 있을게요.")
r("SPK01", "오늘은 파일럿 두 지점 이 주 치 결과부터 보고 데이터 이관까지 갈게요.")
r("SPK01", "알림 문자랑 교육자료는 뒤에 시간 남으면 보고 안 되면 다음으로 넘기고요.")
r("SPK03", "네.")
r("SPK03", "저희는 그 이관 스크립트 중간 결과만 들고 왔는데 그건 언제 보시면 될까요?",
  "open_question", note="이관 결과를 언제 다룰지 순서를 물음")
r("SPK01", "그건 이제 두 번째로 보면 될 것 같고 지점 얘기부터 먼저 들을게요.")
r("SPK01", "해든 씨가 저번 주에 두 지점 돌면서 데스크 쪽 얘기 들어 왔잖아요.")
r("SPK01", "그때 들은 거 그냥 편하게 쭉 풀어 주시면 될 것 같아요.")

# --- T1: pilot result, region D1 ---------------------------------------------
r("SPK05", "네 그러면 제가 다녀온 순서대로 말씀드릴게요. 일단 상계 지점부터 보면요,")
r("SPK05", "예약 자체는 그냥 잘 들어오는데 데스크에서 취소 처리를 못 찾겠다고 하세요.")
r("SPK05", "그 화면이 이제 예약 상세 안에 한 번 더 들어가야 나오는 구조라서요.")
r("SPK05", "하루에 두세 건씩은 전화로 다시 취소해 달라고 저희한테 넘어와요.")
r("SPK02", "그게 이 주 동안 다 합치면 대충 몇 건이나 되는 거예요? 체감 말고 숫자로요.",
  "open_question", note="취소 재처리 건수를 숫자로 요구")
r("SPK05", "정확히는 상계가 스물세 건이고 목동이 열아홉 건이니까 마흔두 건이네요.")
r("SPK05", "아 아니다 목동은 스물한 건이에요. 제가 아까 표를 잘못 보고 말했어요.")
r("SPK05", "어쨌든 이 주에 마흔 건 넘게 사람 손으로 다시 처리한 거라고 보시면 돼요.")
r("SPK05", "그리고 이제 알림 문자 보고 오셨는데 예약이 없다고 하신 분도 한 분 계셨어요.")
r("SPK05", "그건 뭐 확인해 보니까 데스크에서 취소를 두 번 눌러 버린 거였고요.")
r("SPK05", "목동은 그 뭐지 접수 화면이랑 예약 화면을 왔다 갔다 하는 게 제일 불편하시대요.")
r("SPK02", "아 그건 저도 저번에 가서 봤는데 진짜 좀 번거로워 보이긴 했어요.")
r("SPK02", "보호자분 한 분 받는 데 화면을 이제 네 번인가 다섯 번은 옮기시더라고요.")
r("SPK01", "네 네.")
r("SPK05", "그래도 예약이 겹치는 건 확실히 줄었어요. 그건 다들 좋다고 하셨어요.")
r("SPK05", "예전에는 그 같은 시간에 두 건이 그냥 들어가 버리는 일이 종종 있었거든요.")
r("SPK05", "근데 이번 이 주 동안은 그런 게 아예 한 건도 없었어요.")
r("SPK04", "그거는 숫자로도 좀 보여요. 겹침 때문에 옮긴 예약이 이제 영 건이더라고요.")
r("SPK04", "작년 같은 기간에는 그게 두 지점 합쳐서 열한 건이었고요.")
r("SPK04", "그러니까 그 부분은 일단 확실하게 좋아진 걸로 봐도 될 것 같아요.")
r("SPK03", "네 그건 애초에 같은 시간대를 아예 못 잡게 막아 놔서 그래요.")
r("SPK03", "예전 시스템은 그냥 경고만 띄우고 넘어가게 되어 있었거든요.")
r("SPK03", "그때는 뭐 데스크에서 확인만 누르면 그대로 들어가 버렸던 거죠.")
r("SPK02", "아 네.")
r("SPK01", "그러면 그 취소 화면 얘기는 개발사 답 오면 다시 보고 일단 넘어갈게요.")
r("SPK01", "음.")
r("SPK01", "사실 오늘 제일 얘기하고 싶었던 건 그 전환 속도 쪽이거든요.")
r("SPK01", "음 그 정도면 적은 건 아니네요.")
r("SPK01", "도경 씨 그 취소 버튼 위치는 저희가 바꿀 수 있는 건가요 아니면 개발사 쪽인가요?",
  "open_question", note="화면 수정 권한이 어디에 있는지 물음", tag="q_button")
r("SPK03", "그 화면은 개발사 표준 화면이라서 저희가 직접 손대기는 좀 어려워요.")
r("SPK03", "다만 이제 바로가기를 하나 얹는 건 될 것 같은데 그것도 물어는 봐야 돼요.")
r("SPK03", "개발사 쪽에서는 다음 정기 배포 때 같이 보겠다고 저번에 말은 했었어요.",
  "ambiguous", note="전달, 개발사가 한다는 말만 옮김", tag="rel_vendor")
r("SPK04", "잠깐만요, 그 정기 배포라는 게 다음 달 초라고 저번에 들었던 것 같은데요.",
  "open_question", rt="rel_vendor", note="배포 시점이 언제인지 확인")
r("SPK03", "네 그게 지금 일정상으로는 다음 달 둘째 주로 한 번 밀려 있는 상태예요.")
r("SPK03", "그러니까 취소 버튼 얘기를 거기 태우면 이제 한 달 넘게 그냥 기다리는 거죠.",
  tag="wait_month")
r("SPK04", "그 사이에 데스크 분들은 계속 전화로 받으셔야 되는 건데 그건 좀 아닌 것 같아요.",
  "concern", did="D1", rt="wait_month", note="대기 기간 동안 데스크 부담이 그대로라고 반대")
r("SPK04", "지금 두 지점에서 마흔 건인데 스무 곳으로 늘리면 사백 건이 될 수도 있어요.", did="D1")
r("SPK04", "그것도 그냥 단순히 열 배 잡은 거라서 실제로는 더 나올 수도 있고요.", did="D1")
r("SPK04", "지점마다 데스크가 한 분만 계신 데도 있어서 거기는 더 힘드실 거예요.", did="D1")
r("SPK04", "분당 쪽은 아예 혼자 보고 계시니까 점심때는 전화를 아예 못 받으세요.", did="D1")
r("SPK05", "맞아요. 거기는 저희가 전화드려도 잘 안 받으세요.", did="D1")
r("SPK01", "그래서 제가 오늘 그 얘기를 하려고 했는데 전환을 한 번에 다 하는 건 무리예요.",
  did="D1", tag="lead_split")
r("SPK01", "지금 계획은 이제 다음 달 안에 스무 곳을 다 넘기는 걸로 잡혀 있잖아요.", did="D1")
r("SPK01", "근데 저 취소 건 하나만 봐도 데스크가 못 버틸 것 같다는 생각이 들어요.", did="D1")
r("SPK02", "근데 권역으로 쪼개면 지점마다 쓰는 시스템이 달라지는 기간이 길어지는데요.",
  "concern", did="D1", rt="lead_split", note="전환 기간이 길어지는 쪽이 더 위험하다고 반대")
r("SPK02", "보호자분이 다른 지점으로 옮겨서 예약하실 때 그 기록이 안 보이면 더 큰 일이에요.",
  did="D1")
r("SPK03", "그 부분은 예약 기록만 이제 양쪽에서 같이 보이게 하는 건 어렵지 않아요.", did="D1")
r("SPK03", "어차피 데이터베이스는 하나 쓰고 화면만 다르게 뜨는 구조라서요.", did="D1")
r("SPK02", "아 그러면 그건 좀 괜찮겠네요.", did="D1")
r("SPK05", "저는 그 중간에 지점끼리 예약을 넘길 일이 생각보다 많다는 것만 말씀드릴게요.", did="D1")
r("SPK05", "상계에서 못 받으면 그냥 목동으로 보내 드리는 경우가 한 주에 몇 건씩 있거든요.",
  did="D1")
r("SPK05", "그때 그 예약을 옮겨 드리려면 양쪽 화면이 다 보여야 되는 거라서요.", did="D1")
r("SPK05", "지금은 이제 전화로 물어보고 손으로 다시 잡아 드리고 있고요.", did="D1")
r("SPK03", "네 그건 아까 말씀드린 대로 같이 보이게 할 수 있어요.", did="D1")
r("SPK05", "아 그럼 됐어요.", did="D1")
r("SPK01", "그럼 이거는 전 지점 동시 전환은 접고 권역 단위로 순서대로 넘기는 쪽으로 갑니다.",
  "decision", did="D1", settles=True, note="논의를 요약하며 동시 전환을 접는 것으로 확정",
  tag="d1_settle")
r("SPK01", "권역을 어떻게 묶을지는 지우 씨가 지점별 예약 건수 보고 초안 한 번 잡아 주세요.",
  "open_question", did="D1", note="권역 초안 작성을 특정인에게 요청", tag="ask_zone")
r("SPK04", "네 그건 제가 건수랑 데스크 인원 같이 놓고 다음 회의 전까지 정리해 올게요.",
  "commitment", did="D1", rt="ask_zone", note="요청을 받아 기한까지 명시하고 맡음",
  tag="c_zone")
r("SPK04", "묶는 기준이 두 가지쯤 나올 것 같은데 그건 그때 같이 보시면 될 것 같아요.", did="D1")
r("SPK02", "아 네 그러면 저는 지점 공지 문구 쪽만 그거 나오고 나서 보면 되는 거죠?",
  "open_question", note="자기 작업 순서를 확인")
r("SPK01", "네 그렇게 보시면 돼요.")

# --- side talk 1 (middle of the meeting) -------------------------------------
r("SPK05", "아 그 얘기 나온 김에 휴게실 커피 머신 그거 어제부터 물이 안 나오던데요.",
  note="사담")
r("SPK02", "그거 저번 주에도 한 번 그랬는데 그때는 그냥 물통이 비어 있던 거였어요.", note="사담")
r("SPK05", "이번엔 물통은 차 있는데 버튼을 눌러도 아무 소리가 안 나더라고요.", note="사담")
r("SPK04", "그거 뒤에 코드가 빠져 있을 때도 있어요. 저번에도 제가 그냥 꽂아 놨었거든요.",
  note="사담")
r("SPK01", "네 그건 이따 제가 총무팀에 한번 말해 놓을게요. 자 이관 얘기로 갈게요.")

# --- T2: migrating the old booking records, region D2 ------------------------
r("SPK03", "네 그러면 이관 쪽 말씀드릴게요. 기존 시스템에 예약 기록이 오 년 치 있고요,")
r("SPK03", "건수로는 이제 백이십만 건쯤 되는데 그중에 절반이 이 년 안쪽 거예요.")
r("SPK03", "문제는 그 오래된 기록들이 보호자 계정이랑 잘 안 묶여 있다는 거예요.")
r("SPK03", "그러니까 같은 분이 계정 세 개로 흩어져 있는 경우가 생각보다 많아요.")
r("SPK04", "그거 제가 지난주에 세 봤는데 중복으로 보이는 계정이 한 팔천 개 정도였어요.")
r("SPK04", "전화번호 기준으로 묶으면 그게 삼천 개 밑으로 떨어지기는 하는데요,")
r("SPK04", "번호를 바꾸신 분들은 또 못 잡으니까 그걸 정답이라고 하기는 좀 애매해요.")
r("SPK02", "그럼 그 오 년 치를 다 넘기는 게 지금 꼭 필요한 건지부터 좀 여쭤보고 싶은데요.",
  "open_question", did="D2", note="이관 범위 자체가 필요한지 되물음", tag="q_scope")
r("SPK02", "진료 기록은 어차피 차트 쪽에 따로 있는 거잖아요. 예약 이력이 그렇게 오래 필요한가요?",
  "open_question", did="D2", note="예약 이력의 보관 기간 필요성을 물음")
r("SPK05", "저희 데스크에서는 보통 일 년 안쪽만 보거든요. 그 전 건은 거의 안 찾아요.",
  did="D2", tag="desk_year")
r("SPK05", "가끔 보호자분이 재작년에 왔었다고 하시면 그때는 좀 찾아보기는 하는데요,", did="D2")
r("SPK05", "그것도 이제 한 달에 한두 번 있을까 말까 한 정도예요.", did="D2")
r("SPK05", "그때도 대부분은 언제 왔었는지 정도만 확인하시면 그냥 끝나는 거라서요.", did="D2")
r("SPK05", "예약 상세까지 들여다보시는 경우는 진짜 거의 없어요.", did="D2", tag="q_year")
r("SPK02", "아 그러면 일 년 치만 넘겨도 되는 거 아니에요?", did="D2")
r("SPK04", "아니 근데 일 년으로 자르면 재작년 찾으시는 분들은 방법이 아예 없어지는데요.",
  "concern", did="D2", rt="q_year", note="일 년으로 줄이면 재작년 건을 못 찾는다고 반대")
r("SPK04", "한 달에 한두 번이면 일 년이면 그게 스무 번 가까이 되는 거고요.", did="D2")
r("SPK02", "아 그러네요. 제가 그 생각을 못 했네요.", did="D2")
r("SPK03", "근데 이관 범위를 자르면 나중에 옛날 기록 달라고 하실 때 방법이 없어요.",
  "concern", did="D2", rt="desk_year", note="자르면 과거 기록을 꺼낼 방법이 없다고 반대")
r("SPK03", "기존 시스템은 계약이 끝나면 그냥 서버째로 내려가 버리거든요.", did="D2")
r("SPK03", "저희가 백업을 받아 둔다고 해도 그걸 열어 볼 화면이 없는 거고요.", did="D2")
r("SPK03", "그러면 결국 개발자가 데이터베이스를 직접 열어서 뽑아 드려야 되는 거예요.", did="D2")
r("SPK03", "그게 이제 한 건 뽑는 데도 반나절씩 그냥 걸리거든요.", did="D2")
r("SPK04", "그리고 그걸 뽑을 사람이 저희 팀에 사실상 도경 씨 한 명이고요.", did="D2")
r("SPK01", "그럼 조회만 되는 화면 같은 걸 따로 남겨 둘 수는 없는 거예요?",
  "open_question", did="D2", note="조회 전용 화면이 가능한지 물음", tag="q_archive")
r("SPK03", "그거는 개발사한테 물어봐야 되는데 별도 비용 얘기가 나올 수도 있어요.", did="D2")
r("SPK03", "개발사 쪽에서는 아카이브 화면 붙이는 건 어렵지 않다고 말은 했었어요.",
  "ambiguous", did="D2", note="전달, 개발사 말을 옮긴 것뿐 확정이 아님", tag="rel_archive")
r("SPK04", "말은 그렇게 했는데 저번에 검색 화면도 그렇게 얘기했다가 견적이 나왔잖아요.",
  "concern", did="D2", rt="rel_archive", note="같은 말을 하고 비용을 청구한 전례가 있다고 반대")
r("SPK04", "그때 그거 때문에 예산 다시 올리느라 두 주가 그냥 날아갔던 거 기억하시죠?", did="D2")
r("SPK02", "아 맞아요 그건 저도 기억나요.", did="D2")
r("SPK01", "음 그러면 이렇게 하면 어떨까 싶은데요,", did="D2")
r("SPK01", "개발사가 조회 전용 화면을 추가 비용 없이 붙여 준다는 전제로 이관은 이 년 치만 합니다.",
  "decision", did="D2", settles=True,
  note="비용 없이 아카이브가 붙는 경우에만 성립하는 조건부 결정", tag="d2_settle")
r("SPK01", "비용이 붙는다고 하면 그때는 다시 얘기해야 되는 거고요.", did="D2")
r("SPK03", "네 그거 비용 나오는지는 제가 내일 오전에 개발사에 메일로 확인해 볼게요.",
  "commitment", did="D2", rt="d2_settle", note="요청을 받아 확인 시점까지 정해 맡음",
  tag="c_mail")
r("SPK01", "그 답 오기 전까지는 이관 스크립트 나머지는 그냥 잡고 계시고요.", did="D2")
r("SPK03", "네 어차피 그게 정해져야 인덱스를 어디까지 만들지도 정해져서요.", did="D2")
r("SPK03", "지금 이 년 치 기준으로 한 번 돌려 보긴 했는데 여섯 시간쯤 걸렸어요.", did="D2")
r("SPK03", "오 년 치를 다 돌리면 그게 이제 하루를 그냥 넘길 것 같고요.", did="D2")
r("SPK03", "그러면 그 사이에 예약을 못 받으니까 그것도 좀 문제예요.", did="D2")
r("SPK01", "아 그동안 아예 멈추는 거예요?",
  "open_question", did="D2", note="이관 중 예약 접수가 멈추는지 물음", tag="q_stop")
r("SPK03", "아니요 완전히 멈추는 건 아니고 새로 들어오는 건 따로 받아 뒀다가 붙여요.", did="D2")
r("SPK03", "근데 그것도 뭐 사람이 옆에서 계속 보고 있어야 되는 거라서요.", did="D2")
r("SPK03", "그 시간에는 그냥 저랑 지우 씨가 둘 다 붙어 있어야 돼요.", did="D2")
r("SPK04", "네 그건 뭐 어쩔 수 없죠.", did="D2")
r("SPK01", "그거는 그러면 주말에 하는 게 낫겠네요.", did="D2")
r("SPK03", "네.", did="D2")
r("SPK03", "주말이 예약이 제일 적게 들어와서 저희도 그게 편하긴 해요.", did="D2")
r("SPK03", "다만 그날 사람이 나와야 되는 거라 그건 미리 말씀드릴게요.", did="D2")
r("SPK04", "중복 계정은 그럼 그거랑 상관없이 제가 먼저 정리해 보려고요.",
  "commitment", note="본인 계획으로 중복 계정 정리를 먼저 하겠다고 함")
r("SPK04", "번호로 묶이는 것부터 붙여 놓으면 나중에 뭘 하든 편해질 것 같아서요.")
r("SPK02", "그거 묶을 때 보호자 동의 같은 건 따로 안 봐도 되는 거예요?",
  "open_question", note="계정 병합에 동의 절차가 필요한지 물음", tag="q_consent")
r("SPK04", "아 그건 저도 확인을 좀 해 봐야 될 것 같은데 제가 알아볼게요.",
  "commitment", rt="q_consent", note="기한 없이 확인만 맡음")
r("SPK05", "그 동의는 아마 가입할 때 한 번 받는 걸로 되어 있을 거예요.")
r("SPK05", "저희가 신규 보호자 받을 때 그 화면에서 같이 체크하게 되어 있거든요.")
r("SPK02", "그럼 그건 크게 문제없겠네요.")

# --- T3: reminder messages, region D3 (false agreement) ----------------------
r("SPK02", "그럼 알림 쪽 잠깐 보고 갈까요? 이게 지금 비용이 제일 크게 나오는 데라서요.",
  "open_question", note="다음 안건으로 넘어갈지 물음")
r("SPK02", "지금은 이제 예약 잡힐 때 한 번, 전날 저녁에 한 번, 당일 아침에 한 번 나가요.")
r("SPK02", "한 달에 문자 값만 사백만 원 좀 넘게 나가는데 이게 계속 늘고 있어요.")
r("SPK02", "지점이 스무 곳으로 다 넘어가면 이제 그게 두 배 가까이 될 거라고 보고 있고요.")
r("SPK02", "알림톡으로 바꾸면 건당 단가는 확 떨어지기는 하는데요,")
r("SPK02", "그게 이제 채널 등록이랑 템플릿 승인을 다 받아야 돼서 시간이 좀 걸려요.")
r("SPK02", "저번에 알아봤을 때는 승인만 이 주는 잡으라고 하더라고요.")
r("SPK04", "그거 지금 같이 하기는 좀 벅차지 않을까요?",
  "open_question", note="알림톡 전환을 지금 병행할 수 있는지 물음", tag="q_kakao")
r("SPK02", "네 그래서 저도 그건 전환 다 끝나고 보는 게 맞다고 생각하고 있어요.")
r("SPK04", "노쇼율은 그 문자를 세 번 보낼 때랑 두 번 보낼 때랑 차이가 거의 없었어요.",
  did="D3")
r("SPK04", "파일럿 두 지점에서 이 주 동안 보니까 팔 퍼센트랑 팔 점 사 퍼센트였거든요.", did="D3")
r("SPK04", "표본이 작아서 단정하기는 좀 그런데 그 차이는 거의 의미가 없는 수준이에요.", did="D3")
r("SPK04", "그래서 저는 그 세 번이 꼭 필요한가 싶은 생각이 계속 들었어요.", did="D3")
r("SPK04", "물론 뭐 노쇼가 한 건 줄면 그게 또 십만 원 가까이 되기는 해요.", did="D3")
r("SPK04", "그러니까 단순히 문자 값만 보고 자를 건 아니라는 것도 맞는 말이고요.", did="D3")
r("SPK03", "저도 그 얘기는 저번부터 좀 하고 싶었어요.", did="D3")
r("SPK01", "그러면 뭐 그냥 전날 저녁 한 번만 보내는 걸로 하죠.", did="D3",
  note="번복, 여기서 정해진 것처럼 보이지만 바로 뒤에 뒤집힘", tag="fake_ok")
r("SPK02", "아 네 그게 낫겠네요. 그러면 예약 잡힐 때 나가는 것도 같이 빼는 거죠?", did="D3")
r("SPK05", "아 맞다, 그거 안 돼요. 당일 오전에 선생님 일정이 바뀌는 게 있어서요.",
  "concern", did="D3", rt="fake_ok", note="당일 변경 건 때문에 합의를 뒤집음", tag="objection")
r("SPK05", "선생님이 수술 들어가시면 오전 예약이 통째로 밀리는 날이 한 주에 한두 번 있어요.",
  did="D3")
r("SPK05", "그때 연락을 못 드리면 보호자분이 그냥 헛걸음을 하시는 거라서 그건 좀 위험해요.",
  did="D3")
r("SPK05", "저번 달에도 그것 때문에 한 번 크게 항의를 받은 적이 있었어요.", did="D3")
r("SPK05", "두 시간 걸려서 오셨는데 선생님이 안 계셨던 거라서 그건 뭐 할 말이 없죠.", did="D3")
r("SPK01", "아 그게 있었네요.", did="D3")
r("SPK03", "그건 이제 전체 발송이 아니라 변경된 건만 골라서 보내는 건 만들 수 있어요.",
  did="D3", tag="only_changed")
r("SPK03", "예약 시간이 바뀐 건만 잡아서 그분들한테만 나가게 하면 되는 거니까요.", did="D3")
r("SPK04", "그러면 건수가 훨씬 줄어드니까 비용도 이제 거의 안 늘어날 거예요.", did="D3")
r("SPK02", "음 저는 일단 좀 더 보고 말씀드릴게요. 문자 업체 계약 조건도 봐야 돼서요.",
  "ambiguous", did="D3", rt="only_changed", note="구체적인 약속 없이 검토만 언급")
r("SPK02", "건수로 계약이 걸려 있으면 줄인다고 바로 돈이 줄지는 않을 수도 있거든요.", did="D3")
r("SPK02", "작년에 한 번 묶음으로 미리 사 둔 게 있어서 그것도 같이 봐야 돼요.", did="D3")
r("SPK04", "아 그러면 그건 확인되고 나서 붙이는 게 맞지 않아요?",
  "open_question", did="D3", note="계약 확인 뒤에 개발을 붙여야 하는지 물음", tag="q_order")
r("SPK03", "그건 기능은 미리 붙여 놔도 상관없어요. 켜고 끄는 거라서요.", did="D3")
r("SPK04", "아 네네.")
r("SPK02", "그러면 저는 계약서만 다시 보고 말씀드릴게요. 그건 이 주 안에는 볼게요.",
  "commitment", note="계약 조건 확인을 기한과 함께 맡음")
r("SPK01", "네 그건 그렇게 해 주시고 나온 거만 단체방에 올려 주세요.")
r("SPK01", "그럼 정기 안내는 전날 저녁 한 번으로 줄이고 당일 변경 건만 따로 나가게 합니다.",
  "decision", did="D3", settles=True,
  note="뒤집힌 합의를 변경 건 분리로 다시 정리해 확정", tag="d3_settle")
r("SPK01", "예약 잡힐 때 나가는 건 지우 씨가 노쇼율 한 번 더 보고 나서 얘기해요.", did="D3")
r("SPK03", "변경 건 발송은 제가 다음 주 화요일까지 붙여서 테스트까지 해 둘게요.",
  "commitment", did="D3", rt="d3_settle", note="본인이 기한 명시하고 맡음", tag="c_change")
r("SPK03", "그게 붙으면 그 뒤로는 손 안 대도 알아서 나가게 되어 있어요.", did="D3")
r("SPK05", "아 그러면 데스크에서 따로 전화 안 드려도 되는 거죠?",
  "open_question", note="데스크 수작업이 없어지는지 확인", tag="q_desk_call")
r("SPK03", "네 그렇게 되는 거죠.")
r("SPK05", "그럼 저희가 편해지긴 하겠네요.")

# --- side talk 2 (middle of the meeting) -------------------------------------
r("SPK04", "아 그리고 아까 목동 지점에서 간식 보내 주셨던데 그거 휴게실에 그냥 뒀어요.",
  note="사담")
r("SPK05", "아 그 쿠키요? 저 아까 하나 먹어 봤는데 그게 생각보다 되게 달더라고요.", note="사담")
r("SPK02", "저번에 상계에서 보내 주신 그 약과가 훨씬 나았어요. 그건 금방 없어졌잖아요.",
  note="사담")
r("SPK04", "그거 저는 두 개 챙겨 놨다가 결국 못 먹고 퇴근했어요.", note="사담")
r("SPK01", "자 그 얘기는 이따 하시고 교육자료 쪽만 잠깐 보고 갈게요.")

# --- T4: training material, region D4 (deferral, 위임) -----------------------
r("SPK01", "지점 데스크랑 선생님들 교육자료를 누가 만들지가 지금 정해진 게 없더라고요.",
  did="D4")
r("SPK01", "이건 뭐 운영지원 쪽에서 알아서 좀 정리해 주시면 될 것 같은데요.", did="D4",
  tag="dump")
r("SPK02", "저희가요? 저희는 지금 권역 초안이랑 문자 쪽까지 같이 보고 있는데요.",
  "concern", did="D4", rt="dump", note="이미 다른 일을 맡고 있어 받기 어렵다고 반대")
r("SPK02", "거기다 지점 공지 문구까지 하면 이 주 안에는 손도 못 댈 것 같아요.", did="D4")
r("SPK03", "저희도 이관 붙는 동안은 화면 캡처 정도밖에 못 도와드릴 것 같은데요.", did="D4")
r("SPK01", "음.", did="D4")
r("SPK05", "아... 예... 일단은 제가 한번 볼게요.",
  "ambiguous", did="D4", rt="dump", note="위임, 떠맡되 구체적인 약속은 없음", tag="reluctant")
r("SPK05", "데스크에서 뭐 물어보시는 건 제가 제일 많이 받으니까 그건 제가 아니까요.", did="D4")
r("SPK05", "근데 제가 만들면 시스템 화면 쪽은 정확하게 못 쓸 것 같아서 그게 좀 걸려요.",
  did="D4")
r("SPK05", "저는 그 화면 이름도 아직 예약 상세인지 접수 상세인지 좀 헷갈리거든요.", did="D4")
r("SPK05", "그런 걸 제가 잘못 써 놓으면 지점에서 더 헷갈리실 것 같아서요.", did="D4")
r("SPK03", "그 부분은 제가 캡처 떠서 넘겨 드릴게요. 설명까지는 좀 어렵고요.",
  "commitment", did="D4", rt="reluctant", note="범위를 좁혀 화면 캡처만 맡음")
r("SPK02", "그럼 그게 분량이 어느 정도인지부터 정해야 될 것 같은데요,", did="D4")
r("SPK02", "한 장짜리 안내문인지 이십 장짜리 매뉴얼인지에 따라 일이 완전히 달라지거든요.",
  did="D4")
r("SPK02", "저희가 작년에 차트 바꿀 때는 그걸 이십 장짜리로 만들었다가", did="D4")
r("SPK03", "아 그거 아무도 안 봤죠.", did="D4")
r("SPK02", "네 진짜 아무도 안 봤어요. 결국 한 장짜리로 다시 만들었고요.", did="D4")
r("SPK05", "그쵸.", did="D4")
r("SPK02", "그래서 저는 이번에도 얇게 가는 게 맞다고 보는데 그건 또 사람마다 다르니까요.",
  did="D4")
r("SPK02", "파트장님은 이걸 어느 쪽으로 생각하고 계셨는지 그것부터 좀 알려 주세요.",
  "open_question", did="D4", note="자료의 분량 기준을 정해 달라고 요청", tag="q_volume")
r("SPK01", "저는 그 두 장 정도로 화면 몇 개만 짚어 주는 걸 생각했는데요,", did="D4")
r("SPK01", "듣고 보니까 데스크에서 실제로 막히는 데를 먼저 모으는 게 맞는 것 같네요.",
  did="D4", tag="collect_first")
r("SPK04", "근데 그걸 모으려면 파일럿 두 지점 말고 나머지 지점 얘기도 받아야 되는데요.",
  "concern", did="D4", rt="collect_first", note="의견 수집 범위가 넓어 오늘 정하기 이르다고 반대")
r("SPK04", "그거 돌리는 데만 또 한 주는 그냥 걸릴 것 같아서 오늘 정하기는 이른 것 같아요.",
  did="D4")
r("SPK01", "그럼 교육자료는 오늘 여기서 정하지 않고 다음 회의로 넘깁니다.",
  "decision", did="D4", settles=True, note="합의가 안 되어 보류, 분량과 담당 모두 미룸",
  tag="d4_settle")
r("SPK01", "대신 해든 씨가 그동안 데스크에서 나온 질문만 좀 적어 두시면 될 것 같아요.",
  "open_question", did="D4", note="보류 기간 동안 할 일을 특정인에게 요청", tag="ask_notes")
r("SPK05", "네 그건 제가 그때그때 메모해 놓을게요. 따로 정리까지는 못 할 것 같고요.",
  "commitment", did="D4", rt="ask_notes", note="기한 없이 메모만 하기로 맡음", tag="c_notes")
r("SPK02", "저는 그럼 그거 보고 나서 목차만 잡아 보려고요.",
  "commitment", note="본인 계획으로 목차 작업을 예고")
r("SPK05", "네 그게 낫겠어요.")

# --- T5: phone bookings, region D5 (a superior's proposal nobody answers) -----
r("SPK02", "아 그리고 전화 예약 얘기는 오늘 하고 넘어가야 되는 거 아니에요?",
  "open_question", note="전화 예약 안건을 오늘 다룰지 물음")
r("SPK02", "저번에 그 앱으로만 받자는 얘기가 나왔다가 그냥 흐지부지됐잖아요.")
r("SPK05", "전화 예약이 아직 전체의 한 육십 퍼센트는 그냥 넘어요.", did="D5", tag="phone_share")
r("SPK05", "어르신 보호자분들은 앱을 아예 안 깔고 계신 경우가 대부분이거든요.", did="D5")
r("SPK05", "그분들한테 앱으로만 받는다고 하면 그건 그냥 오지 말라는 얘기라서요.", did="D5")
r("SPK03", "근데 전화로 받은 걸 데스크에서 다시 입력하다 보니까 오타가 계속 생겨요.",
  "concern", did="D5", rt="phone_share", note="수기 입력 때문에 오류가 난다고 문제 제기")
r("SPK03", "지난주에도 예약 시간이 한 시간 밀려서 들어간 건이 두 건이나 있었어요.", did="D5")
r("SPK04", "그건 그냥 전화 받으면서 바로 입력하는 구조로는 원래 좀 어려운 부분이에요.",
  did="D5")
r("SPK04", "녹취를 붙이자는 얘기도 있었는데 그건 그 동의를 또 받아야 되는 거고요.", did="D5")
r("SPK02", "그리고 전화로 받으면 시간도 오래 걸려요. 한 건에 오 분씩은 그냥 잡히니까요.",
  did="D5")
r("SPK02", "앱으로 들어오면 그게 뭐 알아서 그냥 들어오는 거고요.", did="D5")
r("SPK05", "근데 그 오 분이 이제 상담이기도 해요. 예약만 하고 끊는 게 아니라서요.", did="D5")
r("SPK05", "어디가 아픈지 먼저 말씀해 주시면 저희가 선생님을 정해 드리는 거거든요.", did="D5")
r("SPK05", "그걸 앱에서 직접 고르시라고 하면 그건 또 많이 어려우실 거예요.", did="D5")
r("SPK02", "네 맞아요.", did="D5")
r("SPK04", "그 부분은 뭐 저도 동의해요.", did="D5")
r("SPK01", "전화 예약은 일단 지금처럼 두고 앱 쪽 화면만 먼저 손보는 쪽으로 봅시다.",
  "decision", did="D5", settles=True, note="상급자 제안, 이후 아무도 답하지 않고 넘어감",
  tag="d5_settle")
r("SPK02", "그럼 앱 화면은 지금 어디까지 나와 있는 거예요?",
  "open_question", note="앱 화면 진행 상황을 물음", tag="q_app")

# --- T6: the switch date, region D6 (relative deadline) ----------------------
r("SPK03", "앱 화면은 개발사에서 이 주 뒤에 최종 빌드를 준다고 했어요.", did="D6")
r("SPK03", "근데 그게 저번에도 한 번 밀린 적이 있어서 그대로 믿기는 좀 그래요.", did="D6")
r("SPK03", "그러니까 저희가 그거 받아서 확인하는 데가", did="D6")
r("SPK04", "잠시만요, 그 확인이라는 게 저희 쪽 확인이에요 아니면 지점 확인이에요?",
  "open_question", did="D6", note="검수 주체가 누구인지 확인", tag="q_who_check")
r("SPK03", "아 저희가 먼저 보고 그 다음에 지점에 뿌리는 순서예요.", did="D6")
r("SPK05", "저희 쪽은 지점에 뿌리기 전에 최소 사흘은 봐야 될 것 같은데요.", did="D6",
  tag="three_days")
r("SPK05", "데스크 분들이 실제로 눌러 보셔야 뭐가 이상한지 나오거든요.", did="D6")
r("SPK05", "저희끼리만 보면 실제로 쓰는 순서대로는 잘 안 눌러 보게 되더라고요.", did="D6")
r("SPK05", "저번에도 그래서 그 취소 건을 못 잡고 그냥 넘어갔던 거잖아요.", did="D6")
r("SPK04", "사흘로는 좀 빠듯해요. 저번 파일럿 때도 결국 일주일이 걸렸잖아요.",
  "concern", did="D6", rt="three_days", note="과거 사례로 볼 때 사흘은 부족하다고 반대")
r("SPK04", "그때도 처음엔 이틀이면 된다고 했다가 계속 늘어났던 거 기억하시죠?", did="D6")
r("SPK04", "그러니까 저는 그 사흘이라는 숫자 자체를 좀 못 믿겠다는 거예요.", did="D6")
r("SPK03", "아 그게 아니고 그때는 화면이 통째로 바뀌었던 거라서 좀 달라요.", did="D6")
r("SPK03", "이번엔 뭐 버튼 위치 정도만 바뀌는 거라 그때만큼은 아닐 거예요.", did="D6")
r("SPK04", "음.", did="D6")
r("SPK04", "그래도 저는 나흘은 봐야 된다고 생각해요. 사흘은 진짜 좀 빠듯해서요.", did="D6")
r("SPK01", "그 하루 차이가 지금 오픈일이랑 바로 붙어 버리는 거라 그게 좀 걸리네요.", did="D6")
r("SPK01", "그러니까 앞이든 뒤든 하루는 어디선가 만들어 와야 되는 상황이에요.", did="D6")
r("SPK01", "그게 지금 오픈일이 문제인데 그건 저번에 말한 날짜에서 못 밀어요.", did="D6",
  tag="fixed_open")
r("SPK01", "본부에서 이미 지점들한테 공지가 나가 있는 상태라서 그걸 바꾸면 더 복잡해져요.",
  did="D6")
r("SPK03", "그럼 빌드를 당겨 받는 수밖에 없는데", did="D6")
r("SPK04", "제 말은 확인 기간을 못 줄일 거면 앞을 당기는 게 맞다는 거예요.", did="D6",
  tag="pull_forward")
r("SPK03", "네 그것도 개발사가 된다고 해야 되는 거라서 장담은 못 하겠어요.", did="D6")
r("SPK02", "제가 저번 회의 때 권역별로 가면 지점 공지 문구도 따로 나가야 된다고", did="D6")
r("SPK01", "아 그 얘기 하셨었죠.", did="D6")
r("SPK02", "네 그것도 빌드 날짜에 맞춰 같이 움직여야 되는 거라 제가 같이 챙길게요.",
  "commitment", did="D6", note="상기, 저번 회의에서 자기가 말한 것을 다시 꺼내 맡음",
  tag="c_notice")
r("SPK01", "그럼 일차 전환일은 저번에 말한 오픈일 그대로 두고 빌드를 이틀 앞당겨 받는 걸 전제로 갑니다.",
  "decision", did="D6", settles=True,
  note="오픈일은 고정하고 빌드 선행을 조건으로 확정, 기한은 다른 날짜에 걸려 있음",
  tag="d6_settle")
r("SPK03", "그럼 빌드 이틀 당기는 건 제가 아까 메일 보낼 때 같이 물어볼게요.",
  "commitment", did="D6", rt="d6_settle", note="개발사 문의에 묶어서 맡음", tag="c_pull")
r("SPK04", "그게 안 되면 확인 기간을 사흘로 줄이는 수밖에 없는데 그건 좀 무섭네요.",
  "concern", did="D6", rt="d6_settle", note="조건이 깨졌을 때의 위험을 다시 지적")
r("SPK01", "그건 안 된다고 오면 그때 다시 모여서 보기로 해요.", did="D6")
r("SPK05", "그럼 지점에는 언제부터 알려 드리면", did="D6")
r("SPK02", "그건 빌드 날짜 확정되고 나서 나가는 게 맞을 것 같아요.", did="D6")
r("SPK02", "지금 알려 드리면 또 바뀌었다고 연락이 스무 통씩 와요.", did="D6")
r("SPK02", "저번 파일럿 때도 날짜 바뀐 거 안내하느라 그냥 하루를 다 썼어요.", did="D6")
r("SPK05", "아 그건 그렇겠네요.", did="D6")

# --- closing -----------------------------------------------------------------
r("SPK01", "자 그러면 오늘 나온 거 제가 한 번만 훑고 마칠게요.")
r("SPK01", "권역 초안은 지우 씨, 이관 비용 확인이랑 빌드 얘기는 도경 씨가 보시고요.")
r("SPK01", "문자 쪽은 도경 씨가 붙이고 윤슬 씨가 계약 조건 같이 보시는 걸로 알고 있을게요.")
r("SPK01", "그리고 해든 씨는 데스크에서 나오는 질문 모으시는 것만 좀 부탁드릴게요.")
r("SPK05", "네 알겠습니다.")
r("SPK01", "아 그리고 권역 얘기는 아직 지점에 나가면 안 되니까 그것만 좀 조심해 주세요.")
r("SPK02", "아 저기 그 교육자료는 그럼 다음 회의 첫 번째로 보는 거죠?",
  "open_question", note="보류된 안건의 다음 순서를 확인", tag="q_next")
r("SPK01", "네 그걸 제일 먼저 보고 나머지를 보죠.")
r("SPK04", "아니 근데 다음 회의가 그 주 수요일 맞아요? 저는 목요일로 알고 있었는데요.",
  "open_question", note="다음 회의 일정이 언제인지 확인", tag="q_when_meet")
r("SPK02", "수요일로 한 번 옮겼어요. 목요일에 본부 일정이 겹쳐서요.")
r("SPK04", "아 그래요? 그럼 제 초안은 그 전날까지 올려 둘게요.",
  "commitment", rt="q_when_meet", note="변경된 일정에 맞춰 기한을 다시 정하고 맡음")
r("SPK05", "저는 메모한 거 그냥 그날 들고 갈게요.",
  "commitment", note="정리 없이 메모만 가져오기로 함")
r("SPK03", "저는 메일 답 오면 단체방에 바로 공유해 드릴게요.",
  "commitment", note="개발사 회신을 받는 대로 공유하기로 함")
r("SPK01", "네 그럼 오늘은 여기까지 할게요. 다들 고생하셨습니다.")
r("SPK03", "네 고생하셨습니다.")
r("SPK04", "수고하셨어요.")
r("SPK02", "고생하셨습니다.")
r("SPK05", "네 들어가세요.")


# --- decision answer key (addendum 2026-09-21c) -------------------------------
DECISIONS: list[dict] = []
DECISIONS = [
    {"id": "D1", "settles": "d1_settle",
     "statement": "신규 예약 시스템은 스무 개 지점을 한 번에 넘기지 않고 권역 단위로 나눠 순서대로 전환한다.",
     "owner": "SPK04", "due": "다음 회의 전 (권역 묶음 초안)", "due_as_said": "다음 회의 전까지",
     "evidence": ["lead_split", "d1_settle", "ask_zone", "c_zone"],
     "note": "데스크 부담과 전환 기간을 두고 양쪽에서 반대가 나온 뒤 파트장이 요약하며 확정, 권역 초안 담당과 기한은 확정 행 뒤에 있음"},
    {"id": "D2", "settles": "d2_settle",
     "statement": "기존 예약 기록 이관 범위를 최근 이 년 치로 줄이되, 개발사가 조회 전용 화면을 추가 비용 없이 붙여 주는 경우에만 적용한다.",
     "owner": "SPK03", "due": "개발사 회신 확인 후", "due_as_said": "내일 오전에",
     "evidence": ["q_scope", "desk_year", "rel_archive", "d2_settle", "c_mail"],
     "note": "옛 기록을 꺼낼 방법이 없다는 반대와 비용 전례 지적이 조건부로 흡수됨, 비용이 붙으면 무효"},
    {"id": "D3", "settles": "d3_settle",
     "statement": "예약 알림은 전날 저녁 정기 발송 한 번으로 줄이고, 당일 일정이 바뀐 예약에만 변경 안내를 따로 보낸다.",
     "owner": "SPK03", "due": "다음 주 화요일", "due_as_said": "다음 주 화요일까지",
     "evidence": ["fake_ok", "objection", "only_changed", "d3_settle", "c_change"],
     "note": "전날 한 번만 보내기로 합의된 듯했다가 당일 변경 건 때문에 뒤집힌 뒤 다시 정리됨, 개발 담당과 기한은 확정 행 뒤에 있음"},
    {"id": "D4", "settles": "d4_settle",
     "statement": "지점 교육자료의 분량과 담당은 이번 회의에서 정하지 않고 다음 회의로 미루며, 그동안 데스크 질문만 모아 둔다.",
     "owner": "SPK05", "due": "다음 회의", "due_as_said": "다음 회의로",
     "evidence": ["dump", "reluctant", "q_volume", "d4_settle", "ask_notes", "c_notes"],
     "note": "운영지원 쪽에 떠넘겨졌다가 아무도 온전히 받지 않아 보류, 질문 수집만 떠맡은 사람이 담당"},
    {"id": "D5", "settles": "d5_settle",
     "statement": "전화 예약 접수는 지금처럼 그대로 두고, 이번 개선은 앱 예약 화면만 손보는 범위로 한정한다.",
     "owner": "", "due": "", "due_as_said": "",
     "evidence": ["phone_share", "d5_settle", "q_app"],
     "note": "상급자 제안 뒤 아무도 답하지 않고 다음 안건으로 넘어감, 담당과 기한은 끝까지 나오지 않음"},
    {"id": "D6", "settles": "d6_settle",
     "statement": "일차 권역 전환일은 기존 오픈일을 그대로 두고, 개발사 빌드를 이틀 앞당겨 받는 것을 전제로 한다.",
     "owner": "SPK03", "due": "개발사 빌드 수령 이틀 단축", "due_as_said": "저번에 말한 오픈일 그대로, 빌드는 이틀 앞당겨서",
     "evidence": ["fixed_open", "pull_forward", "d6_settle", "c_pull"],
     "note": "검수 사흘로는 부족하다는 반대와 오픈일 고정이 부딪혀 빌드 선행으로 정리됨, 빌드가 안 당겨지면 다시 모이기로 함"},
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
