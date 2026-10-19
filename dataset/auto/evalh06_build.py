"""Build EVALH_06 — an invented museum audio-guide meeting for the hard eval set.

The dialogue is held here as one list so that row numbers, start times,
`responds_to` and the answer key's row references are generated instead of typed:
every earlier hard meeting lost a fix round to a hand-numbered reference that
moved. Rows carry optional labels; the answer key refers to labels, never to
numbers.

Writes `EVALH_06.A.csv`, `EVALH_06.C.csv`, `EVALH_06.D.csv` and
`EVALH_06.speakers.json` into `dataset/extraction_eval_dummy_hard/`.

Everything in the meeting is invented: museum, exhibition, people, numbers.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "extraction_eval_dummy_hard"
MEETING = "EVALH_06"

ROLE = {
    "SPK01": "Ops",
    "SPK02": "PM",
    "SPK03": "Design",
    "SPK04": "Data",
    "SPK05": "QA",
}

SPEAKERS = {
    "meeting": MEETING,
    "title": "하람뮤지엄 전시운영팀 특별전 오디오 가이드 개편 회의",
    "type": "team",
    "position_order": ["사원", "주임", "대리", "과장", "차장", "부장", "이사", "대표"],
    "speakers": [
        {"speaker": "SPK01", "name": "정해든", "team": "전시운영팀", "job": "Ops",
         "position": "과장", "title": "팀장"},
        {"speaker": "SPK02", "name": "윤소래", "team": "전시운영팀", "job": "PM",
         "position": "대리", "title": ""},
        {"speaker": "SPK03", "name": "배현오", "team": "전시운영팀", "job": "Design",
         "position": "주임", "title": ""},
        {"speaker": "SPK04", "name": "천미르", "team": "전시운영팀", "job": "Data",
         "position": "대리", "title": ""},
        {"speaker": "SPK05", "name": "강노을", "team": "전시운영팀", "job": "QA",
         "position": "사원", "title": ""},
    ],
}

rows: list[dict] = []
labels: dict[str, int] = {}


def say(speaker: str, text: str, kind: str = "none", decision: str = "",
        settles: str = "", rt: int | None = None, note: str = "",
        label: str | None = None) -> None:
    """One ASR segment. `rt` is an offset back to the row responded to (-1 = previous)."""
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


# --- opening -----------------------------------------------------------------
say("SPK02", "아 팀장님 이 프로젝터 오늘도 색이 누렇게 나오는데 그냥 이대로 진행해도 될까요?")
say("SPK02", "일단 화면은 제 노트북으로 띄워 둘 테니까 뒤쪽에 앉으신 분들은 이쪽 보시면 돼요.")
say("SPK02", "저기 노을 씨는 수장고 정리하다가 조금 늦는다고 아까 메신저로 얘기해 놨어요.")
say("SPK01", "네 그냥 하죠 뭐. 자 그러면 오늘은 오디오 가이드 개편 건만 보고 끊을게요.")
say("SPK01", "일단 단말기를 계속 빌려줄지부터 보고 다국어 녹음이랑 원고 마감을 이어서 볼게요.")
say("SPK01", "그 다음에 어린이 트랙까지 가면 얼추 삼십 분인데 중간에 그냥 끊고 들어오셔도 돼요.")
say("SPK01", "아 그리고 오늘은 회의록을 따로 안 쓰고 정해진 것만 메신저에 올리는 걸로 할게요.")
say("SPK01", "지난번처럼 이제 이것저것 다 적다가 정작 정해진 게 안 남으면 그게 더 곤란하더라고요.")
say("SPK01", "뭐 어차피 오늘 정할 건 세 개 정도라서 그렇게 길게 끌 일도 아니고요.")
say("SPK04", "저는 지난 전시 대여 수치만 좀 정리해 왔는데 이거 먼저 깔고 가는 게 나을까요?",
    kind="open_question", note="수치를 먼저 볼지 순서를 물음")
say("SPK01", "네 그게 먼저 있어야 얘기가 될 것 같으니까 미르 씨가 그냥 쭉 말해 주세요.")
say("SPK04", "네 그러니까 지난 기획전 기준으로 가이드 대여가 하루 평균 백사십 건 정도였고요,")
say("SPK04", "그중에 끝까지 들으신 분은 이제 절반이 조금 안 되는 걸로 로그에 찍혀 있어요.")
say("SPK04", "아 죄송해요 백사십이 아니라 백이십사 건이네요. 다른 전시랑 숫자를 헷갈렸어요.")
say("SPK04", "어쨌든 반납 줄이 길다는 민원은 이제 회차마다 두세 건씩은 꾸준히 들어왔어요.")
say("SPK04", "그 민원이 대부분 주말 낮 회차에 몰려 있어서 그때만 좀 심한 편이고요.")
say("SPK04", "평일에는 뭐 대여 자체가 적어서 줄이라고 할 것도 없긴 했어요.")
say("SPK04", "그래서 저는 이게 대수 문제라기보다 데스크 문제 같다고 보고 있어요.")
say("SPK03", "네.")

# --- D1: rental units vs QR on personal phones --------------------------------
say("SPK02", "일단 단말기 얘기부터 하면 지금 저희가 가지고 있는 게 총 삼백 대인데요,", decision="D1")
say("SPK02", "이게 배터리가 부풀어서 못 쓰게 된 게 작년 한 해에만 사십 대 넘게 나왔거든요.", decision="D1")
say("SPK02", "그게 이제 보증 기간이 다 끝난 물건이라 고쳐서 쓰는 것도 안 되는 상황이고요.", decision="D1")
say("SPK02", "작년에 한 번 수리를 맡겨 봤는데 한 대에 팔만 원씩 나와서 그냥 뺐어요.", decision="D1")
say("SPK02", "그래서 지금 실제로 돌아가는 건 삼백 대가 아니라 이백오십 대 정도예요.", decision="D1")
say("SPK02", "그래서 올해도 그대로 다 돌리려면 교체 비용이 좀 크게 들어갈 것 같아서 걱정이에요.",
    kind="concern", decision="D1", note="unprompted, 배터리 교체 비용 부담을 먼저 꺼냄")
say("SPK01", "그거 교체하면 대충 얼마나 잡아야 되는 거예요?",
    kind="open_question", decision="D1", rt=-1, note="교체 비용 규모를 물음")
say("SPK02", "어 정확한 건 견적을 다시 받아 봐야 되는데 지금 받은 걸로는 한 이천만 원 정도요.", decision="D1")
say("SPK02", "그래서 저는 이번 기회에 개인 휴대폰으로 QR 찍어서 듣는 쪽으로 가면 어떨까 싶어요.",
    decision="D1", label="d1_proposal")
say("SPK03", "음.")
say("SPK05", "저는 그게 좀 걸리는 게 어르신 관람객분들이 QR을 잘 못 찍으시더라고요.",
    kind="concern", decision="D1", rt=-2, note="고령 관람객이 QR을 못 쓴다는 반대")
say("SPK05", "지난 기획전 때도 입구 안내판 앞에 사람이 계속 몰려서 데스크가 마비됐었어요.", decision="D1")
say("SPK05", "결국 직원이 한 분씩 붙잡고 찍어 드리다가 줄이 더 길어져 버렸거든요.", decision="D1")
say("SPK05", "그날 제가 데스크에 한 시간 정도 서 있었는데 계속 같은 질문만 받았어요.", decision="D1")
say("SPK05", "화면에서 뭘 눌러야 되는지 모르시는 분이 이제 생각보다 훨씬 많더라고요.", decision="D1")
say("SPK05", "그래서 저는 그걸 전부 없애는 건 좀 위험하다고 계속 생각하고 있었어요.", decision="D1")
say("SPK01", "아 그건 저도 봤어요. 근데 그때는 안내판이 너무 낮게 붙어 있던 것도 있었고요.", decision="D1")
say("SPK01", "뭐 어쨌든 그게 다시 반복되면 곤란한 건 맞으니까 그 부분은 따로 좀 봐야겠네요.", decision="D1")
say("SPK01", "일단 안내판 위치를 눈높이로 올리는 건 어차피 한 번 해야 되는 일이고요.", decision="D1")
say("SPK01", "그건 이제 돈이 드는 일도 아니니까 이번에 같이 손보면 될 것 같아요.", decision="D1")
say("SPK01", "뭐 그거 하나로 다 해결되는 건 아니겠지만 지난번보다는 나을 거예요.", decision="D1")
say("SPK03", "그 QR로 가면 화면 디자인은 어차피 새로 해야 되는데 그건 언제까지 필요하세요?",
    kind="open_question", note="새 화면 디자인 기한을 물음")
say("SPK02", "아 그건 이따가 일정 얘기할 때 같이 말씀드릴게요.")
say("SPK04", "잠시만요, 수치 하나만 더 보태면 작년에 QR로 시범 운영한 회차가 두 번 있었어요.", decision="D1")
say("SPK04", "그때 개인 휴대폰으로 들은 비율이 이제 삼십 퍼센트가 조금 넘게 나왔었고요.", decision="D1")
say("SPK04", "그때는 뭐 안내를 따로 크게 하지도 않았는데 그 정도가 나온 거였고요.", decision="D1")
say("SPK04", "대여 데스크 줄도 그 두 회차는 좀 짧았다고 기록에 적혀 있긴 해요.", decision="D1")
say("SPK04", "근데 그게 젊은 분들이 많은 야간 개장 회차라서 그대로 믿기는 좀 어려워요.", decision="D1")
say("SPK04", "그래서 제가 이번 주에 연령대별로 다시 쪼개서 한번 뽑아 보려고요.",
    kind="commitment", decision="D1", note="본인 계획으로 연령대별 재집계를 하겠다고 함")
say("SPK01", "네 그게 있으면 좋죠.")
say("SPK05", "근데 그 수치가 나와도 못 찍으시는 분이 있다는 건 그대로 남는 거 아니에요?",
    kind="concern", decision="D1", rt=-2, note="재집계로도 해결되지 않는다는 반박")
say("SPK02", "그러니까 제 얘기는 전부 없애자는 게 아니라 일부는 남겨 두자는 거였어요.", decision="D1")
say("SPK02", "데스크에 백 대 정도만 두고 필요하신 분들한테만 빌려드리면 되는 거고요.", decision="D1")
say("SPK02", "그러면 어르신들은 그냥 지금처럼 빌려 쓰시면 되니까 달라질 게 없고요.", decision="D1")
say("SPK02", "젊은 분들은 어차피 본인 이어폰을 끼고 다니셔서 QR이 더 편하실 거예요.", decision="D1")
say("SPK02", "그러면 배터리 교체도 백 대만 하면 되니까 비용이 삼분의 일로 줄어들어요.", decision="D1")
say("SPK05", "아 그런 거면 저는 괜찮을 것 같은데요.", decision="D1")
say("SPK03", "네 저도 그 정도면 안내판만 좀 크게 고치면 될 것 같아요.", decision="D1")
say("SPK01", "음 근데 백 대가 맞는 숫자인지는 봐야 될 것 같은데 미르 씨는 어떻게 보세요?",
    kind="open_question", decision="D1", rt=-3, note="적정 대수에 대한 의견을 물음")
say("SPK04", "하루 평균이 백이십 건대니까 회전까지 생각하면 백 대면 좀 아슬아슬해요.", decision="D1")
say("SPK04", "주말 낮 회차만 몰리는 거라서 평일은 그 절반도 안 나갈 거예요.", decision="D1")
say("SPK04", "그래서 백 대로 잡으면 주말 두 시 회차만 좀 아슬아슬할 것 같아요.", decision="D1")
say("SPK04", "그때만 데스크에서 좀 빨리 돌리면 뭐 못 버틸 정도는 아니에요.", decision="D1")
say("SPK01", "그럼 단말기는 백 대만 남기고 나머지는 개인 휴대폰 QR로 돌리는 쪽으로 정리할게요.",
    kind="decision", decision="D1", settles="1",
    note="논의를 팀장이 요약해 확정, 반납 줄 우려는 안내판 보완으로 흡수", label="d1_settle")
say("SPK01", "대신 데스크 앞에 안내하는 분을 한 분 더 세우는 건 기획팀이랑 얘기해 봐야 하고요.", decision="D1")
say("SPK02", "그 인력 얘기는 제가 전시기획팀에 물어보고 공유드릴게요.",
    kind="commitment", decision="D1", rt=-1, note="팀장 요청을 받아 타 팀 문의를 맡음", label="d1_owner")
say("SPK02", "아 그리고 배터리 견적은 제가 다시 받아 볼게요.",
    kind="commitment", decision="D1", note="기한 없이 견적 재확인을 맡음")
say("SPK01", "네 그건 급하진 않으니까 편하실 때 해 주세요.")
say("SPK01", "어차피 백 대만 바꾸는 거면 예산도 지금 있는 걸로 어떻게든 될 거예요.")
say("SPK01", "그 견적서만 나오면 승인 쪽은 알아서 도니까 너무 신경 안 쓰셔도 되고요.")
say("SPK01", "일단 그건 그 정도로 두고 다음 얘기로 좀 넘어갈게요.")
say("SPK03", "그럼 안내판은 언제까지 새로 뽑아야 되는 거예요?",
    kind="open_question", decision="D1", note="안내판 교체 기한을 물음")
say("SPK01", "개막이 십일월 칠 일이니까 그 이 주 전까지는 걸려 있어야 될 것 같은데요.", decision="D1")
say("SPK01", "그러면 시월 이십사 일이 금요일이죠? 그날까지로 잡으면 맞을 것 같아요.",
    decision="D1", label="d1_due")
say("SPK03", "네 그 정도면 시안까지는 충분히 낼 수 있어요.",
    kind="commitment", decision="D1", rt=-1, note="안내판 시안을 기한 안에 내겠다고 받음")
say("SPK05", "저기 근데 백 대로 줄이면 반납 데스크는 한 곳만 두는 거죠?",
    kind="open_question", note="반납 데스크 수를 확인해 물음")
say("SPK02", "네 그건 그대로 한 곳이요. 어차피 백 대면 두 곳을 둘 이유가 없어요.")
say("SPK02", "대신 반납함을 출구 쪽에 하나 더 두면 줄이 좀 나눠지긴 할 거예요.")
say("SPK02", "그건 뭐 돈이 드는 것도 아니라서 한번 얘기는 해 볼 만한 것 같아요.")
say("SPK05", "네.")
say("SPK04", "그냥 도슨트 앱이랑 하나로 합쳐 버리면 안 돼요? 어차피 설치는 해야 되잖아요.")
say("SPK03", "그건 앱 쪽 계약이 내년에 끝나서 지금 건드리면 또 복잡해져요.")
say("SPK03", "그리고 앱에 넣으면 관람객이 앱을 또 깔아야 돼서 그게 더 번거로워요.")
say("SPK03", "지금은 QR을 찍으면 바로 브라우저에서 열리는 식이라 설치가 없거든요.")
say("SPK03", "그 차이가 생각보다 커서 저는 그냥 지금 방식이 낫다고 보는 편이에요.")
say("SPK01", "네 그 얘기는 나중에 하고요.")

# --- side talk 1 (middle of the meeting) --------------------------------------
say("SPK03", "아 맞다 그건 그렇고 어제 지하 수장고 제습기 또 멈췄다는 거 들으셨어요?", note="사담")
say("SPK04", "네 아침에 관리팀이 올라와서 한참 뭐 만지다가 그냥 내려갔다고 하던데요.", note="사담")
say("SPK05", "그거 작년 장마 때도 한 번 서지 않았어요? 그때 작품 옮기느라 난리였잖아요.", note="사담")
say("SPK03", "맞아요 그때 새벽에 다 나왔었죠. 이번엔 그 정도는 아니라고 하더라고요.", note="사담")
say("SPK01", "네 그건 관리팀이 볼 거니까 우리는 일단 가이드 얘기로 다시 갈게요.", note="사담")

# --- D2: three languages, voice actor vs synthetic voice -----------------------
say("SPK01", "자 다국어 녹음 쪽인데 소래 씨가 업체 견적 받았다고 했던 거 맞죠?",
    kind="open_question", decision="D2", note="업체 견적 수령 여부를 물음")
say("SPK02", "네 저번 회의 때 영어 원고는 제가 먼저 정리해 오기로 했었잖아요.",
    kind="commitment", decision="D2", note="상기, 이전 회의에서 맡은 영어 원고 정리를 다시 확인함")
say("SPK02", "그건 초안까지 나왔고 이제 검수만 남았는데 그 얘기는 조금 있다 할게요.", decision="D2")
say("SPK02", "업체는 저번에 도록 녹음 맡겼던 데랑 같은 곳이라 얘기는 빠른 편이고요.", decision="D2")
say("SPK02", "다만 성우 일정이 시월 말에 몰려 있어서 그 전에 답을 줘야 된대요.", decision="D2")
say("SPK02", "성우 녹음을 세 개 언어 다 하면 견적이 사천 중반 정도로 나왔어요.", decision="D2")
say("SPK01", "사천이요? 지금 잡혀 있는 돈에서 얼마나 넘는 건데요?",
    kind="open_question", decision="D2", rt=-1, note="예산 초과 폭을 물음")
say("SPK02", "작년엔 영어만 했으니까 지금 예산으로는 한 언어하고 반 정도밖에 안 돼요.", decision="D2")
say("SPK02", "그래서 어디를 줄일지를 오늘 정해야 업체에 답을 줄 수 있는 상황이에요.", decision="D2")
say("SPK03", "그럼 중국어랑 일본어는 기계 음성으로 돌리고 사람이 검수만 하면 어때요?",
    decision="D2", label="d2_proposal")
say("SPK05", "그거 저도 전에 한번 들어 봤는데 고유명사를 읽는 게 좀 이상했어요.",
    kind="concern", decision="D2", rt=-1, note="기계 음성의 고유명사 발음 품질을 문제 삼음")
say("SPK05", "작가 이름이나 작품 제목이 문단마다 다르게 읽혀서 계속 신경 쓰이더라고요.", decision="D2")
say("SPK05", "특히 한자로 된 이름이 들어가면 읽는 게 매번 달라져서 좀 곤란했어요.", decision="D2")
say("SPK05", "그게 한두 군데면 모르겠는데 이제 작품마다 나오니까 티가 나거든요.", decision="D2")
say("SPK05", "관람객이 헤드폰으로 그걸 듣고 있으면 티가 안 날 수가 없거든요.", decision="D2")
say("SPK03", "아 근데 그건 사전에 발음을 따로 넣어 주면 잡히는 거 아니었어요?", decision="D2")
say("SPK05", "넣어도 조사가 붙으면 또 달라져요. 제가 지난번에 그것 때문에 한참 봤어요.", decision="D2")
say("SPK04", "음.")
say("SPK02", "제 말은, 기계 음성을 아예 쓰지 말자는 게 아니라 언어를 나누자는 거예요.", decision="D2")
say("SPK02", "영어는 그대로 성우로 가고 나머지 둘만 기계 음성으로 하면 예산이 맞거든요.", decision="D2")
say("SPK02", "영어는 해외 단체 관람객이 제일 많이 듣는 거라 그건 좀 살려야 하고요.", decision="D2")
say("SPK02", "나머지 둘은 뭐 분량 자체가 영어의 절반도 안 돼서 부담이 덜해요.", decision="D2")
say("SPK02", "그렇게 하면 지금 예산에서 오백 정도만 넘고 그 정도는 조정이 돼요.", decision="D2")
say("SPK01", "중국어 관람객 비중이 요즘 어느 정도 되는 거예요?",
    kind="open_question", decision="D2", note="중국어 관람객 비중을 물음")
say("SPK04", "단체 예약만 보면 이번 분기에 이제 전체의 한 이 할 정도 되고요,", decision="D2")
say("SPK04", "일본어는 그보다 좀 적은데 대신 개별로 오시는 분이 꾸준히 있어요.", decision="D2")
say("SPK04", "근데 이게 여행사 예약 기준이라서 실제 입장이랑은 좀 차이가 나요.", decision="D2")
say("SPK04", "실제 입장은 이제 국적을 따로 안 받아서 정확히는 알 수가 없고요.", decision="D2")
say("SPK04", "그래서 저 수치는 그냥 참고만 하시는 게 맞을 것 같긴 해요.", decision="D2")
say("SPK03", "그럼 비중이 큰 중국어부터 샘플을 받아 보고 정하면 되지 않을까요?", decision="D2")
say("SPK01", "네 그게 맞는 것 같은데 그 샘플은 며칠이면 받을 수 있어요?",
    kind="open_question", decision="D2", rt=-1, note="샘플 수령에 걸리는 기간을 물음")
say("SPK02", "업체가 이틀이면 준다고 했으니까 이번 주 안에는 들어 볼 수 있을 거예요.",
    decision="D2", label="d2_due")
say("SPK05", "샘플은 제가 들어 보고 어디가 이상한지 정리해서 올려 둘게요.",
    kind="commitment", decision="D2", rt=-2, note="샘플 청취와 문제 정리를 본인이 맡음")
say("SPK01", "그럼 영어만 성우로 가고 중국어랑 일본어는 기계 음성으로 하되, 샘플이 통과되면요.",
    kind="decision", decision="D2", settles="1",
    note="조건부 결정, 중국어 샘플 통과를 전제로 언어별 방식을 갈라 확정", label="d2_settle")
say("SPK01", "샘플이 영 아니면 그땐 일본어를 빼는 걸 다시 봐야죠.", decision="D2")
say("SPK02", "네 알겠습니다. 업체에는 일단 그렇게 전달해 둘게요.",
    kind="commitment", decision="D2", rt=-2, note="확정 내용을 업체에 전달하겠다고 받음")
say("SPK03", "그런데 기계 음성으로 가면 거기에 맞춰서 원고를 좀 짧게 써야 돼요.",
    kind="concern", decision="D2", rt=-3, note="기계 음성에 맞춘 원고 수정 부담을 지적")
say("SPK03", "문장이 길면 숨 쉬는 데가 없어서 듣는 사람이 금방 놓쳐 버리거든요.")
say("SPK03", "저번에 다른 데서 만든 걸 들어 봤는데 문장이 길면 그냥 다 흘려듣게 되더라고요.")
say("SPK03", "그래서 한 문장을 이제 두 줄 넘지 않게 끊어 쓰는 게 제일 편하긴 해요.")
say("SPK03", "근데 그러려면 원고를 쓸 때부터 그걸 생각하고 써야 되는 거고요.")
say("SPK03", "지금 원고는 그렇게 안 돼 있어서 뭐 손이 한 번은 더 가야 될 거예요.")
say("SPK02", "아 그건 원고 정리할 때 한번 같이 볼게요.",
    kind="ambiguous", rt=-6, note="구체적인 약속 없이 나중에 보겠다는 약한 동의")
say("SPK04", "네.")
say("SPK02", "그리고 전시기획팀 쪽은 개막 주에 인력을 못 빼 준다고 어제 얘기가 왔더라고요.",
    kind="ambiguous", note="전달, 다른 팀이 하겠다는 내용을 옮김")
say("SPK02", "그래서 녹음 입회는 저희 쪽에서 한 명이 들어가야 될 것 같아요.")
say("SPK01", "그건 제가 들어갈게요. 어차피 그 주엔 다른 일정이 없어요.",
    kind="commitment", rt=-1, note="녹음 입회를 본인이 맡음")
say("SPK05", "잠깐만요, 녹음 입회면 스튜디오까지 가야 되는 거죠?",
    kind="open_question", note="입회 방식이 현장 참석인지 물음")
say("SPK02", "네 성수동 쪽인데 반나절이면 끝나요. 작년에도 그 정도 걸렸어요.")
say("SPK02", "가는 김에 그 발음 목록도 같이 들고 가면 현장에서 바로 잡을 수 있고요.")
say("SPK02", "작년에는 그걸 안 들고 가서 나중에 두 군데를 다시 녹음했거든요.")
say("SPK02", "그때 추가 비용이 이제 백만 원 가까이 나와서 좀 아까웠어요.")
say("SPK01", "네 그건 제가 알아서 할게요.")

# --- D3: manuscript freeze, false agreement then the real decision -------------
say("SPK01", "자 그러면 원고 마감을 봐야 되는데 사실 이게 오늘 제일 빡빡한 건이에요.", decision="D3")
say("SPK02", "지금 영어 초안은 나왔는데 한국어 최종본이 아직 안 닫혀 있는 상태고요.", decision="D3")
say("SPK02", "그래서 영어도 사실 뒷부분은 비워 두고 앞쪽만 번역해 둔 상태예요.", decision="D3")
say("SPK02", "뒤쪽 열두 개가 닫혀야 번역이든 녹음이든 그때부터 움직일 수 있어요.", decision="D3")
say("SPK02", "작품 설명 중에 열두 개가 학예 쪽에서 계속 수정이 들어오고 있거든요.",
    kind="concern", decision="D3", note="unprompted, 최종본이 닫히지 않는 상황을 문제로 꺼냄")
say("SPK03", "그거 몇 번째 수정이에요? 저는 지난주에 받은 게 마지막인 줄 알았는데요.",
    kind="open_question", decision="D3", rt=-1, note="수정 횟수를 물음")
say("SPK02", "세 번째요. 어제 또 두 개가 바뀌어서 제가 다시 반영해 놨어요.", decision="D3")
say("SPK04", "음.")
say("SPK05", "그럼 저희가 검수를 시작하는 건 결국 학예 쪽이 닫아 줘야 되는 거네요.", decision="D3")
say("SPK05", "저희가 아무리 빨리 봐도 그게 안 닫히면 그냥 기다리는 수밖에 없거든요.", decision="D3")
say("SPK05", "그래서 저는 마감을 좀 세게 잡아 두는 게 맞다고 보긴 해요.", decision="D3")
say("SPK02", "네 그래서 제가 그쪽에 언제까지 달라고 못을 박아야 될 것 같은데요,", decision="D3")
say("SPK01", "그거 너무 세게 얘기하면 또 감정 상하니까 제 이름 걸고 제가 얘기할게요.",
    kind="commitment", decision="D3", rt=-1, note="학예실과의 마감 협의를 본인이 맡음")
say("SPK03", "그럼 원고는 다음 주 금요일까지 다 넘기는 걸로 하죠!", decision="D3", note="번복")
say("SPK05", "아 잠시만요, 그 주에 도록이 인쇄 넘어가지 않아요?",
    kind="concern", decision="D3", rt=-1, note="도록 인쇄 일정과 겹친다며 합의를 뒤집음")
say("SPK02", "아 맞다. 도록이 시월 십육 일에 인쇄 들어가요. 그거 지나면 못 고쳐요.", decision="D3")
say("SPK02", "인쇄소가 그 주에 다른 전시 도록이랑 같이 걸어서 한 번 놓치면 그냥 밀려요.", decision="D3")
say("SPK02", "작년에 하루 늦었다가 개막 이틀 전에 겨우 받았던 거 기억나시잖아요.", decision="D3")
say("SPK02", "그때 박스 뜯어서 바로 진열대에 올렸는데 그게 진짜 아슬아슬했어요.", decision="D3")
say("SPK02", "그래서 그 날짜만큼은 저희가 먼저 맞춰 주는 게 맞다고 생각해요.", decision="D3")
say("SPK03", "아 그러면 다음 주 금요일은 안 되죠. 제가 날짜를 잘못 보고 말했네요.", decision="D3")
say("SPK01", "그럼 도록이랑 같은 원고를 써야 되는 거예요, 아니면 따로 가도 되는 거예요?",
    kind="open_question", decision="D3", rt=-6, note="도록과 원고를 같이 가야 하는지 물음")
say("SPK02", "작품 제목이랑 작가 표기는 같아야 돼요. 설명 문장은 달라도 되고요.", decision="D3")
say("SPK02", "근데 표기가 다르면 관람객이 바로 알아채서 민원이 그대로 들어와요.", decision="D3")
say("SPK02", "작품 제목은 뭐 한 글자만 달라도 바로 눈에 들어오니까 더 그렇고요.", decision="D3")
say("SPK02", "그래서 표기만큼은 도록이랑 같은 걸 써야 되는 게 맞다고 봐요.", decision="D3")
say("SPK04", "저번 상설전 때 그거 때문에 한 주 내내 전화 받았던 기억이 나요.", decision="D3")
say("SPK01", "그러면 원고는 도록 넘어가는 날보다 사흘 당겨서 확정하는 걸로 할게요.",
    kind="decision", decision="D3", settles="1",
    note="도록 인쇄일을 기준으로 삼아 상대 기한으로 확정, 번복된 다음 주 금요일 안을 대체",
    label="d3_settle")
say("SPK02", "그러면 시월 십삼 일이네요. 월요일이라 주말에 좀 봐야 될 것 같은데요.",
    decision="D3", label="d3_due")
say("SPK02", "그 주 주말에 학예 쪽이 또 뭘 보내면 그건 그냥 다음으로 넘겨야 돼요.", decision="D3")
say("SPK02", "안 그러면 십삼 일에 닫아도 그게 닫힌 게 아니게 되거든요.", decision="D3")
say("SPK02", "그리고 십삼 일이면 영어 번역까지 같이 정리가 돼야 되는 날이에요.", decision="D3")
say("SPK01", "네 그 앞 주에 제가 학예 쪽이랑 한 번 앉을게요.", decision="D3")
say("SPK02", "표기 정리는 제가 맡을게요. 어차피 도록 쪽도 제가 받고 있어서요.",
    kind="commitment", decision="D3", rt=-6, note="표기 통일 작업을 본인이 맡음", label="d3_owner")
say("SPK03", "그러면 저는 그 표기 나오는 대로 화면이랑 인쇄물에 같이 반영할게요.",
    kind="commitment", rt=-1, note="표기 확정 후 디자인 반영을 맡음")
say("SPK05", "검수는 십삼 일 지나고 바로 시작하면 되는 거죠?",
    kind="open_question", note="검수 착수 시점을 확인해 물음")
say("SPK02", "네 그때부터 사흘은 손 안 대고 두는 걸로 해요.")
say("SPK02", "그 사흘 안에는 오탈자만 보고 내용은 더 안 건드리면 될 것 같아요.")
say("SPK02", "거기서 또 문장을 고치기 시작하면 이제 끝이 안 나거든요.")

# --- side talk 2 (middle of the meeting) --------------------------------------
say("SPK05", "아 그리고 아까 주차 정산기가 또 카드가 안 먹는다고 데스크에 얘기 왔었어요.", note="사담")
say("SPK02", "그거 지난주에 고쳤다고 하지 않았어요? 저도 어제 그냥 현금으로 냈거든요.", note="사담")
say("SPK04", "저는 그냥 뒤쪽 골목에 대고 다녀요. 거기가 좀 싸기도 하고 편해요.", note="사담")
say("SPK05", "아 거기 주말에도 자리 있어요? 저는 항상 차 있길래 그냥 지나쳤는데.", note="사담")
say("SPK01", "그 얘기는 이따 점심 때 하고요, 어린이 쪽부터 좀 보고 갈게요.", note="사담")

# --- D4: children's track, deferred -------------------------------------------
say("SPK01", "어린이 트랙을 이번에 넣자는 얘기가 학예 쪽에서 또 나왔더라고요.", decision="D4")
say("SPK01", "작년에도 한 번 얘기가 나왔다가 그냥 흐지부지된 그 건이에요.", decision="D4")
say("SPK01", "그때도 원고를 따로 써야 된다는 얘기까지 나왔다가 그냥 덮였고요.", decision="D4")
say("SPK01", "올해는 학예 쪽에서 아예 문서로 올려서 답을 달라고 하는 상황이에요.", decision="D4")
say("SPK01", "그래서 하든 안 하든 오늘 얘기는 한 번 하고 가야 되는 거고요.", decision="D4")
say("SPK01", "뭐 저도 있으면 좋다고는 생각하는데 이번 일정에 되는지가 문제죠.", decision="D4")
say("SPK03", "그거 하려면 원고를 아예 따로 써야 되는 거 아니에요?",
    kind="open_question", decision="D4", rt=-5, note="어린이용 원고를 따로 써야 하는지 물음")
say("SPK02", "네 문장도 다시 쓰고 길이도 절반으로 줄여야 되니까 사실상 새로 쓰는 거예요.", decision="D4")
say("SPK02", "지금 한국어 최종본도 못 닫고 있는데 그걸 같이 가는 건 좀 무리예요.",
    kind="concern", decision="D4", rt=-1, note="현재 일정으로는 병행이 어렵다는 반대")
say("SPK05", "저도 검수 분량이 두 배가 되면 개막 전에 다 못 볼 것 같아요.",
    kind="concern", decision="D4", rt=-1, note="검수 분량 증가로 기한을 못 맞춘다는 반대")
say("SPK04", "근데 주말 가족 관람객이 이제 전체의 사 할 가까이 되긴 해요.", decision="D4")
say("SPK04", "그래서 수요가 없어서 안 하는 거라고 말하기는 좀 어려운 상황이에요.", decision="D4")
say("SPK04", "작년 설문에도 어린이용이 있으면 좋겠다는 얘기가 이제 꽤 나왔었고요.", decision="D4")
say("SPK04", "그 얘기가 매번 나오는데 매번 안 하니까 그게 또 쌓이는 거죠.", decision="D4")
say("SPK01", "음 그러니까 하긴 해야 되는데 이번은 아니다 이런 얘기인 거죠?", decision="D4")
say("SPK03", "저는 차라리 개막하고 한 달 뒤에 따로 올리는 게 나을 것 같은데요.", decision="D4")
say("SPK03", "그때는 원고도 다 정리돼 있으니까 줄이기만 하면 되잖아요.", decision="D4")
say("SPK03", "그리고 그때 하면 녹음도 한 번에 몰아서 잡을 수 있어서 비용도 덜 들어요.", decision="D4")
say("SPK03", "지금 같이 하면 스튜디오를 두 번 잡아야 돼서 그게 또 다 돈이에요.", decision="D4")
say("SPK02", "그건 그런데 학예 쪽에 뭐라고 답을 줄지가 문제예요.", decision="D4")
say("SPK01", "어린이 트랙은 오늘 말고 다음 회의에서 다시 보는 쪽으로 미룰게요.",
    kind="decision", decision="D4", settles="1",
    note="일정 부담 때문에 보류, 다음 회의로 넘기되 그 사이 준비만 진행", label="d4_settle")
say("SPK01", "대신 그냥 미뤘다고만 하면 또 같은 얘기가 나오니까 근거는 있어야 돼요.", decision="D4")
say("SPK05", "그럼 대상이 될 만한 작품 목록만 제가 먼저 추려 둘게요.",
    kind="commitment", decision="D4", rt=-1, note="보류 기간에 대상 작품 목록 정리를 맡음",
    label="d4_interim")
say("SPK01", "네 그 정도만 추려 놔도 다음에 얘기하기는 충분할 거예요.")
say("SPK04", "다음 회의가 언제였죠? 저는 그 주에 반차가 하루 있어서요.",
    kind="open_question", note="다음 회의 일정을 물음")
say("SPK02", "다음 주 수요일 오후 세 시요. 회의실은 아직 안 잡혀 있어요.", label="d4_due")
say("SPK02", "회의실은 그날 아침에 비는 데로 잡으면 되니까 그건 걱정 안 하셔도 돼요.")
say("SPK02", "그때 어린이 트랙 얘기를 제일 앞에 올려 두는 게 나을 것 같고요.")
say("SPK04", "아 그럼 저는 들어올 수 있어요.")

# --- delegation: the glossary nobody wants -------------------------------------
say("SPK01", "아 그리고 고유명사 표기 목록 있잖아요. 그건 운영 쪽에서 좀 알아서 해 주세요.",
    label="deleg_throw")
say("SPK01", "기계 음성이든 성우든 그게 없으면 어차피 계속 다시 읽어야 되니까요.")
say("SPK01", "그게 사실 한 사람이 앉아서 쭉 정리하면 반나절이면 끝나는 일이거든요.")
say("SPK01", "근데 매번 서로 미루다가 결국 아무도 안 해서 이번에도 이러고 있는 거고요.")
say("SPK01", "뭐 완벽하게 안 해도 되고 이번 전시에 나오는 것만 있으면 돼요.")
say("SPK01", "그거라도 있으면 녹음할 때 한 번에 잡고 넘어갈 수 있으니까요.")
say("SPK03", "그거 학예 쪽에서 쓰던 게 있지 않았어요? 저는 예전에 본 것 같은데요.",
    kind="open_question", note="기존 목록이 있는지 물음")
say("SPK02", "있긴 한데 전시마다 표기가 달라서 그대로 쓰기는 좀 어려워요.")
say("SPK04", "제가 예전 전시 파일을 다 뒤지면 나오기는 할 텐데 시간이 꽤 걸려요.")
say("SPK05", "아... 예... 일단 제가 한번 훑어는 볼게요.",
    kind="ambiguous", rt=-9, note="위임, 떠맡되 구체적인 범위나 기한은 말하지 않음",
    label="deleg_take")
say("SPK01", "네 노을 씨가 보시고 안 되겠다 싶으면 그때 다시 얘기해 주세요.")
say("SPK02", "저도 도록 쪽 표기는 어차피 정리하니까 그건 같이 넘겨 드릴게요.",
    kind="commitment", rt=-2, note="도록 표기 정리분을 넘겨 주기로 함")
say("SPK05", "네 그러면 좀 낫겠네요.")
say("SPK05", "그 목록이 있으면 그래도 어디부터 봐야 되는지는 감이 잡히니까요.")
say("SPK05", "일단은 이번 특별전에 나오는 것부터 보는 게 순서일 것 같아요.")

# --- D5: earphones, a lead's proposal nobody answers ---------------------------
say("SPK03", "그럼 이제 이어폰 얘기가 남았는데 이건 어떻게 하실 거예요?",
    kind="open_question", decision="D5", note="이어폰 운영 방침을 물음")
say("SPK02", "작년에는 데스크에서 천 원에 팔았는데 그게 생각보다 손이 많이 갔어요.", decision="D5")
say("SPK02", "현금을 따로 받아야 되고 재고도 매일 세야 되니까 데스크가 계속 묶여요.", decision="D5")
say("SPK02", "그 천 원 받으려고 사람이 하나 더 붙어 있는 셈이라 좀 아깝더라고요.", decision="D5")
say("SPK02", "수익으로 잡히는 것도 이제 한 회차에 몇만 원 수준밖에 안 되고요.", decision="D5")
say("SPK05", "그리고 단말기에 걸려 있는 이어폰은 위생 얘기가 계속 나와요.",
    kind="concern", decision="D5", note="unprompted, 공용 이어폰 위생 문제를 제기")
say("SPK05", "매 회차마다 닦는다고는 하는데 그걸 다 믿으시지는 않더라고요.", decision="D5")
say("SPK05", "실제로 빌리시고는 이어폰만 빼놓고 쓰시는 분들도 꽤 계시거든요.", decision="D5")
say("SPK05", "그러면 결국 소리가 밖으로 다 새서 옆에 계신 분들이 또 싫어하세요.", decision="D5")
say("SPK04", "실제로 작년 설문에 그 항목 점수가 제일 낮게 나오긴 했어요.", decision="D5")
say("SPK04", "그 항목만 다섯 점 만점에 이제 삼 점이 조금 안 되게 나왔어요.", decision="D5")
say("SPK04", "다른 항목은 다 사 점 위였는데 유독 그것만 낮았던 거예요.", decision="D5")
say("SPK03", "그럼 일회용으로 바꾸면 되는 거 아니에요? 단가도 얼마 안 할 텐데요.", decision="D5")
say("SPK02", "일회용은 쓰레기가 회차마다 몇백 개씩 나와서 그것도 말이 나와요.",
    kind="concern", decision="D5", rt=-1, note="일회용 전환은 폐기물 문제가 있다는 반대")
say("SPK01", "이어폰은 데스크에서 팔지 말고 개인 이어폰 가져오시라고 안내문만 붙여요.",
    kind="decision", decision="D5", settles="1",
    note="상급자, 팀장이 제안한 뒤 아무도 답하지 않고 다음 얘기로 넘어감", label="d5_settle")
say("SPK04", "음.")
say("SPK03", "아 그러면 안내문은 입구랑 데스크 두 군데에 붙이면 되는 거죠?", decision="D5")
say("SPK01", "네 입구 쪽은 크게 하나 붙이고 데스크는 작은 걸로 놓으면 될 것 같아요.",
    decision="D5", label="d5_where")
say("SPK03", "그럼 그 안내문 시안은 제가 안내판이랑 같이 만들어서 올릴게요.",
    kind="commitment", decision="D5", rt=-1, note="안내문 시안을 안내판과 함께 만들기로 받음")
say("SPK01", "네 그건 안내판 나갈 때 같이 나가면 돼요.", decision="D5", label="d5_due")

# --- D6: who checks the terminology, by when -----------------------------------
say("SPK01", "마지막으로 검수 당번을 정해야 되는데 이게 매번 밀리는 게 문제예요.", decision="D6")
say("SPK01", "지난 전시 때도 결국 개막 전날에 몰아서 보다가 놓친 게 나왔잖아요.", decision="D6")
say("SPK01", "그때 영어 쪽 작품 제목이 두 개 틀린 채로 그냥 나갔었잖아요.", decision="D6")
say("SPK01", "그거 결국 개막하고 사흘 뒤에 관람객이 먼저 찾아서 알려 준 거예요.", decision="D6")
say("SPK01", "그래서 이번에는 좀 나눠서 미리 보자는 얘기를 계속 하는 거고요.", decision="D6")
say("SPK02", "그때는 원고가 늦게 닫혀서 그런 거라 이번엔 좀 다를 것 같긴 해요.", decision="D6")
say("SPK05", "근데 저 혼자 다 보는 건 이번에도 좀 어려울 것 같아요.",
    kind="concern", decision="D6", note="unprompted, 혼자 검수는 무리라는 부담을 밝힘",
    label="d6_concern")
say("SPK05", "언어가 세 개로 늘어나면 한 바퀴 도는 데만 이틀씩 걸리거든요.", decision="D6")
say("SPK05", "그것도 한 번 보고 끝나는 게 아니라 고친 다음에 또 봐야 되고요.", decision="D6")
say("SPK05", "그래서 혼자 붙으면 이제 개막 직전에 또 똑같아질 것 같아요.", decision="D6")
say("SPK03", "그럼 언어별로 한 명씩 붙으면 되지 않아요? 저는 영어는 볼 수 있어요.",
    decision="D6", label="d6_split")
say("SPK04", "저는 중국어는 못 보는데 대신 숫자나 연도 틀린 건 잡을 수 있어요.", decision="D6")
say("SPK02", "중국어는 업체 쪽 검수자가 한 번 보고 넘기기로 되어 있긴 해요.",
    kind="ambiguous", decision="D6", note="전달, 업체가 하기로 되어 있다는 내용을 옮김")
say("SPK01", "그럼 우리가 볼 건 결국 한국어랑 영어 두 개인 거네요.", decision="D6")
say("SPK05", "네 그 정도면 할 만해요.", decision="D6")
say("SPK01", "그럼 용어 검수는 노을 씨가 금요일 퇴근 전까지 일 차로 보고 저한테 넘겨 주세요.",
    kind="decision", decision="D6", settles="1",
    note="담당과 기한을 확정 행 안에서 함께 지정, 혼자는 어렵다는 반대를 영어 분담으로 흡수",
    label="d6_settle")
say("SPK03", "영어는 제가 그다음에 이어서 볼게요.",
    kind="commitment", decision="D6", rt=-1, note="영어 검수를 이어받기로 함")
say("SPK05", "네 그럼 저는 한국어부터 보고 금요일에 정리해서 올릴게요.",
    kind="commitment", decision="D6", rt=-2, note="기한을 확인하며 한국어 검수를 받음")
say("SPK01", "네 그렇게 해요.")

# --- closing -------------------------------------------------------------------
say("SPK02", "그럼 제가 오늘 나온 것만 짧게 정리해서 메신저에 올려 둘게요.",
    kind="commitment", note="회의 정리본을 공유하기로 함")
say("SPK02", "단말기 백 대, 언어별 녹음 방식, 원고 확정일 이렇게 세 개가 제일 급해요.")
say("SPK02", "나머지는 뭐 오늘 정리된 대로 위에 적어 두면 다들 보실 수 있을 거예요.")
say("SPK02", "혹시 제가 잘못 적은 게 있으면 그냥 바로 댓글로 달아 주시면 되고요.")
say("SPK02", "특히 날짜는 제가 헷갈릴 수가 있어서 그 부분만 좀 봐 주세요.")
say("SPK02", "그리고 다음 회의 전까지 각자 맡은 건 그때 상황만 알려 주시면 돼요.")
say("SPK04", "아 저는 연령대 수치 나오면 그것도 같이 붙여 놓을게요.",
    kind="commitment", rt=-6, note="재집계 결과를 정리본에 붙이기로 함")
say("SPK03", "시안은 다음 주 초에 초안 보여 드릴 수 있을 것 같아요.")
say("SPK03", "안내문이랑 안내판을 같이 뽑으면 인쇄도 한 번에 넘길 수 있어서요.")
say("SPK03", "그 전에 문구만 좀 확인해 주시면 저는 그대로 진행하면 되고요.")
say("SPK01", "네 오늘은 여기까지 하고요, 다음 주에 남은 건 이어서 보죠.")
say("SPK05", "네.")
say("SPK01", "아 그리고 수장고 쪽은 관리팀에서 오후에 다시 온다고 했으니까 참고하세요.")
say("SPK02", "네 알겠습니다.")


# --- generation ----------------------------------------------------------------
LAST_START = 1782.0
FIRST_START = 9.5


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
        "statement": "대여 단말기는 백 대만 남기고 나머지 관람객은 개인 휴대폰으로 QR을 찍어 듣게 한다.",
        "owner": "SPK02",
        "due": "10월 24일(개막 2주 전) 전환 안내 완료",
        "due_as_said": "개막 이 주 전까지, 시월 이십사 일",
        "evidence_rows": ("d1_proposal", "d1_settle", "d1_owner", "d1_due"),
        "note": "고령 관람객이 QR을 못 쓴다는 반대를 백 대 잔류로 흡수해 팀장이 요약 확정, 담당과 기한은 확정 행 뒤에 있음",
    },
    {
        "decision_id": "D2",
        "settles_row": "d2_settle",
        "statement": "영어 가이드만 성우로 녹음하고 중국어와 일본어는 기계 음성으로 제작하되 중국어 샘플이 통과해야 한다.",
        "owner": "SPK03",
        "due": "중국어 샘플 확인 후 결정(회의 주 안에 샘플 수령)",
        "due_as_said": "이번 주 안에는 들어 볼 수 있을 거예요",
        "evidence_rows": ("d2_proposal", "d2_due", "d2_settle"),
        "note": "발음 품질 반대가 언어 분리로 정리된 조건부 결정, 샘플이 나쁘면 일본어 제외를 다시 논의",
    },
    {
        "decision_id": "D3",
        "settles_row": "d3_settle",
        "statement": "가이드 원고 확정일을 도록 인쇄 투입일보다 사흘 앞으로 당겨 잡는다.",
        "owner": "SPK02",
        "due": "10월 13일(도록 인쇄 10월 16일의 사흘 전)",
        "due_as_said": "도록 넘어가는 날보다 사흘 당겨서",
        "evidence_rows": ("d3_settle", "d3_due", "d3_owner"),
        "note": "다음 주 금요일로 합의되는 듯했다가 도록 인쇄 일정 때문에 뒤집힌 뒤 상대 기한으로 확정",
    },
    {
        "decision_id": "D4",
        "settles_row": "d4_settle",
        "statement": "어린이용 가이드 트랙을 이번 특별전에 넣을지는 오늘 정하지 않고 다음 회의로 미룬다.",
        "owner": "",
        "due": "다음 회의(다음 주 수요일 오후 세 시)",
        "due_as_said": "다음 회의에서 다시 보는 쪽으로",
        "evidence_rows": ("d4_settle", "d4_interim", "d4_due"),
        "note": "원고와 검수 부담 때문에 보류, 그 사이 대상 작품 목록 정리만 QA가 맡음",
    },
    {
        "decision_id": "D5",
        "settles_row": "d5_settle",
        "statement": "이어폰은 데스크에서 판매하지 않고 개인 이어폰 지참을 권하는 안내문만 붙인다.",
        "owner": "SPK01",
        "due": "안내판 교체와 같은 시점",
        "due_as_said": "안내판 나갈 때 같이",
        "evidence_rows": ("d5_settle", "d5_where", "d5_due"),
        "note": "위생과 폐기물 반대가 오간 뒤 팀장이 제안했고 아무도 답하지 않은 채 넘어감",
    },
    {
        "decision_id": "D6",
        "settles_row": "d6_settle",
        "statement": "용어 검수는 강노을이 일 차로 보고 금요일 퇴근 전까지 팀장에게 넘기며 영어는 배현오가 이어서 본다.",
        "owner": "SPK05",
        "due": "회의 주 금요일 퇴근 전",
        "due_as_said": "금요일 퇴근 전까지",
        "evidence_rows": ("d6_concern", "d6_split", "d6_settle"),
        "note": "혼자는 무리라는 반대가 언어 분담으로 정리됨, 담당과 기한이 확정 행 안에 모두 들어간 유일한 결정",
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

    # A quick read of the numbers the three checkers care about, so a fix round
    # is not spent finding out which band is out.
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
