"""Rebuild EVALH_03 so it passes register_check as well as hard_check.

The meeting was authored at 31 characters a row with the speaker changing every
1.6 rows, so three register bands were out: median row length, mean row length
and rows continuing the same speaker. This script applies one edit plan to
`EVALH_03.C.csv` and regenerates `.A.csv` and the row references in `.D.csv`:

* DEL   - drop 31 single-row backchannel turns (never a labelled act that the
          answer key or a `responds_to` depends on)
* INS   - add 46 rows that continue the speaker of the row they follow, so a
          turn runs 3-6 rows instead of 1
* SET / PRE / APP - lengthen rows toward the 34-56 band, keeping the act at the
          end of the row

Row numbers, utterance ids, start times, `responds_to`, `settles_row` and
`evidence_rows` are all recomputed from the original numbering, so the plan is
written in terms of the rows as they were before this script ran.
"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL = HERE.parent / "extraction_eval_dummy_hard"
MEETING = "EVALH_03"
COLS = ["row", "utterance_id", "start", "speaker", "role", "text",
        "kind", "decision_id", "settles", "responds_to", "note"]

FIRST_START = 6.31
LAST_START = 1786.0

DEL = {30, 50, 73, 76, 113, 118, 125, 133, 134, 149, 150, 151, 152, 166, 178,
       179, 190, 205, 218, 219, 224, 225, 226, 236, 241, 259, 260, 286, 293,
       309, 321}

# Full rewrites: the row absorbs a deleted answer, or was too short to extend.
SET = {
    37: "그 말씀은 그러니까 다른 기체들도 같이 봐야 된다는 얘기인가요?",
    90: "아 그리고 비파괴 결과 나오면 그거는 제가 바로 공유드릴게요.",
    93: "네 좋습니다, 그렇게 정리해서 올려 주세요.",
    105: "그러면 비용은 지금 어느 정도까지 얘기가 오가고 있는 건가요?",
    136: "그러면 운항 쪽에는 이 상황이 지금 공유가 돼 있습니까?",
    140: "판매가 이미 열린 구간이 어디까지인지도 같이 좀 받아 두면 좋겠네요.",
    155: "네 그 세 가지가 맞습니다, 그대로 정리해 두시면 됩니다.",
    161: "그 계약서는 이제 제가 다시 한번 찾아서 확인해 보겠습니다.",
    163: "그러면 찾으시면 그 조항만 캡처해서 방에 좀 올려 주세요.",
    165: "그 계약이 올해 말에 갱신이죠, 십이월 말로 기억하는데.",
    175: "그거 정기점검 들어올 때 같이 붙여서 하면 안 되는 건가요?",
    180: "이공일호기랑 이공오호기 그 두 대는 주말 운항이 많아서 평일 밤이 그나마 낫습니다.",
    258: "작년에 그 문제로 한번 지적을 받은 적이 있는데 그때는 월 단위 한도 기준이었거든요.",
    267: "교육 일정표는 이제 제가 오늘 안에 방에 올려 두겠습니다.",
    270: "아 저 잠깐 다른 건인데 자재 단가 얘기를 좀 해도 될까요?",
    280: "혹시 다른 업체 견적은 그동안 받아 본 게 좀 있나요?",
    288: "인상분은 이제 다음 분기 예산에 반영해서 미리 올려 두겠습니다.",
    289: "그 예산 반영은 이제 언제까지 올려야 되는 건가요?",
    291: "네 그럼 그 전에 제가 정리해서 넘겨 드리겠습니다.",
    294: "들어가는 거면 저희 쪽 사용량은 제가 뽑아서 미리 보내 드리겠습니다.",
    306: "네 그럼 공지에 그 기한까지 같이 붙여 두겠습니다.",
    308: "급한 거 있으면 그냥 전화로 바로 주세요.",
    312: "아 그리고 다음 주 회의는 화요일 그대로 맞죠?",
    314: "회의록은 이제 제가 오늘 안에 정리해서 올려 두겠습니다.",
}

# Openers, used where the row ends in the act and must keep ending in it.
PRE = {
    22: "그러면", 31: "저기", 40: "그리고", 45: "음", 61: "그리고", 62: "아 그리고",
    74: "네", 77: "그러면", 100: "그런데", 130: "그러면", 135: "어", 143: "자",
    202: "그러면", 230: "그런데", 234: "그래도", 247: "그러면", 250: "그러면",
    254: "아", 292: "그러면", 299: "잠깐만요", 320: "자 그러면",
}

# Tails, appended to rows that already finish their sentence.
APP = {
    2: "이제 끝나겠지 했는데 아직 그대로네요.",
    3: "그때 다시 한번 말씀해 주세요.",
    4: "그 소리가 여기까지 다 올라옵니다.",
    6: "그럼 시간 없으니까 바로 시작하죠.",
    9: "다른 건은 그 뒤에 봐도 되고요.",
    10: "주말 인원도 못 정하고요.",
    11: "그래서 좀 급합니다.",
    13: "오늘 아침에 한 번 더 맞춰 봤고요.",
    17: "이틀이 이미 더 걸린 셈입니다.",
    18: "지금은 뭐 그 계획이 의미가 없습니다.",
    23: "확답은 좀 어렵습니다.",
    24: "그럼 일정에 큰 영향은 없습니다.",
    25: "그게 지금 제일 걸리는 부분입니다.",
    26: "정비창 쪽에도 없고요.",
    29: "저도 이건 장담을 못 합니다.",
    33: "지금 바로는 못 보고 오후에 한번 보겠습니다.",
    34: "이게 처음이 아니라서요.",
    35: "작년까지 합치면 더 됩니다.",
    41: "다들 와 계시네요.",
    43: "결과 기다리는 중입니다.",
    48: "오늘 안에는 올 겁니다.",
    49: "그때 한 번에 정리하죠.",
    52: "그건 좀 아니라고 봅니다.",
    56: "그건 좀 위험합니다.",
    59: "잠깐 기다려 주세요.",
    63: "제가 아침에 본 기준입니다.",
    65: "그날은 안쪽 작업만 하고요.",
    66: "뭐 이런 식으로요.",
    70: "그게 좀 반복됐습니다.",
    79: "사람이 없습니다.",
    80: "그건 맞는 말이고요.",
    86: "그건 어쩔 수 없습니다.",
    91: "원본 그대로요.",
    92: "그래야 보시기가 편하실 것 같아서요.",
    95: "자료는 뒤쪽에 붙어 있습니다.",
    99: "오늘 중에는 파악될 것 같습니다.",
    101: "각도가 좀 그랬던 것 같아요.",
    102: "저도 몇 번을 봤는데 안 됩니다.",
    104: "그게 좀 걱정입니다.",
    106: "그건 최소로 잡은 겁니다.",
    107: "정확한 건 청구서를 봐야 알고요.",
    110: "계속 미루고 있습니다.",
    112: "그건 좀 조심하세요.",
    115: "빈 컵만 들고 서 있었습니다.",
    120: "기록으로 남겨 두는 게 낫습니다.",
    123: "그래야 근거가 남습니다.",
    129: "그게 제일 문제입니다.",
    137: "정식으로 문서를 보낸 건 아니고요.",
    139: "그 부분은 좀 걸립니다.",
    141: "이번 주 안에는 답을 받겠습니다.",
    145: "그때도 그냥 넘어갔고요.",
    146: "저는 적는 게 맞다고 봅니다.",
    153: "빠진 게 있으면 말씀해 주세요.",
    167: "그냥 두면 또 같은 일이 생깁니다.",
    168: "지금 당장은 좀 어렵고요.",
    169: "남은 것들 빠르게 보겠습니다.",
    170: "이게 좀 급한 건입니다.",
    173: "인원도 두 명이면 되고요.",
    177: "자리를 언제 비우느냐가 관건입니다.",
    188: "그냥 넘어갔습니다.",
    189: "근거가 있어야 얘기가 됩니다.",
    192: "한번 찾아보면 될 것 같습니다.",
    193: "없으면 빌려 오는 것도 알아보겠습니다.",
    194: "그건 확실합니다.",
    195: "그래서 밤밖에 없습니다.",
    201: "제가 착각했습니다.",
    208: "운항 쪽은 제가 확인하겠습니다.",
    210: "관례가 그렇습니다.",
    217: "그 정도 여유는 있어야 됩니다.",
    222: "발주는 이제 넣어 뒀습니다.",
    223: "수량도 같이 확인하겠습니다.",
    235: "상황 설명을 좀 드리겠습니다.",
    238: "다음 주 월요일부터랍니다.",
    240: "아침에 좀 서둘러야겠네요.",
    243: "이게 다음 달 얘기입니다.",
    246: "그게 규정입니다.",
    248: "그건 안 됩니다.",
    251: "그쪽도 사람이 빠듯합니다.",
    253: "물론 좀 빠듯하긴 할 겁니다.",
    261: "계산을 한번 해 보죠.",
    269: "한 번에 몰리면 감당이 안 됩니다.",
    274: "그게 제일 많이 나갑니다.",
    278: "그 조항이 아예 빠져 있습니다.",
    283: "재고가 남습니다.",
    284: "그건 좀 어렵습니다.",
    290: "저는 그 전주에 한번 보면 되고요.",
    295: "시간이 얼마 없습니다.",
    297: "그날은 아예 못 씁니다.",
    300: "그건 확인했습니다.",
    302: "그게 안 정해지면 또 밀립니다.",
    303: "그게 자연스러울 것 같습니다.",
    307: "오전에는 연락이 어려울 수 있습니다.",
    311: "다음 주에 같이 보겠습니다.",
    313: "장소도 그대로입니다.",
    315: "그게 보기 편하실 것 같아서요.",
    317: "전화로 바로 드리겠습니다.",
    319: "바로 하겠습니다.",
    324: "다들 수고 많으셨습니다.",
}

# (row to follow, text). The new row keeps the speaker, role and decision_id of
# the row it follows, carries no label, and is `none`.
INS = [
    (5, "어제 야간까지 반영된 자료라서 오전에 메일로 받으신 거랑은 숫자가 좀 다릅니다."),
    (8, "본부장님 오시면 그 부분만 다시 한번 짚어서 말씀드리면 될 것 같고요."),
    (11, "지난주에 돌린 그 일정표는 이제 거의 의미가 없어진 상태라서요."),
    (14, "회색 칸은 이제 입고 예정일만 잡혀 있고 작업은 아직 안 잡힌 기체들입니다."),
    (18, "그때만 해도 뭐 이렇게까지 길어질 거라고는 저희도 생각을 못 했고요."),
    (21, "그 결과가 나오기 전에는 저희도 다음 작업을 잡기가 좀 애매한 상황입니다."),
    (25, "작년에도 비슷한 건이 하나 있었는데 그때도 부품 때문에 두 주를 그냥 세워 놨거든요."),
    (28, "통관이 이제 제일 변수라서 저도 날짜를 딱 박아서 말씀드리기가 어렵습니다."),
    (34, "아니 분기라기보다는 최근 석 달 사이에 두 번 나온 거라 더 그렇습니다."),
    (36, "물론 뭐 우연일 수도 있는데 두 번째부터는 한번 들여다보는 게 맞다고 봅니다."),
    (42, "앞에서 예산 얘기가 나왔는데 그건 이따 따로 정리해서 얘기하겠습니다."),
    (44, "일정상으로는 이번 주 금요일까지가 사실상 마지노선이었습니다."),
    (48, "어제도 한 번 더 찔러 봤는데 그쪽은 뭐 확인 중이라는 말만 계속 반복하고 있어요."),
    (52, "지금 그 자리가 제일 좋은 자린데 거기를 이 주씩 잡고 있으면 안 되는 거죠."),
    (57, "천막이야 뭐 저번에도 쳐 봤고 그렇게 어려운 일도 아니잖아요."),
    (63, "아 잠깐만요, 제가 지금 다시 보니까 그 요일이 좀 이상한데요."),
    (70, "그러다 보면 이제 오전이 그냥 통째로 날아가는 경우가 많습니다."),
    (75, "시차 때문에 늦어지는 거지 아예 답이 없을 것 같지는 않습니다."),
    (79, "그 두 명도 지금 다른 작업이 계속 붙어 있는 상태라서 여유가 없습니다."),
    (82, "데이터는 시스템에 다 들어가 있으니까 뽑는 것 자체는 오래 안 걸립니다."),
    (89, "지난주 안건지에도 그 항목이 비슷하게 한 번 올라가 있었습니다."),
    (91, "판정이 좀 애매하게 나오는 경우도 가끔 있긴 합니다."),
    (99, "저희 출고 담당자한테도 다시 한번 확인을 부탁해 둔 상태고요."),
    (101, "그때 사진을 좀 더 찍어 뒀으면 이런 얘기가 안 나왔을 텐데 말이죠."),
    (107, "그것도 저희가 다 무는 건지는 아직 정해진 게 없는 상태라서요."),
    (115, "어제 관리팀에 얘기는 해 뒀는데 아직 아무 말이 없더라고요."),
    (123, "지난번 건도 이제 메일로 남겨 둔 게 나중에 도움이 많이 됐거든요."),
    (127, "아 재검사가 아니라 재조립부터 다시 도는 거라서 그렇게 잡힌 겁니다."),
    (137, "정식 공문으로 간 건 아니고 그쪽 담당자한테 얘기만 해 둔 겁니다."),
    (145, "그때는 뭐 사흘이 아니라 나흘이었나, 아무튼 한참 지나서 답이 왔습니다."),
    (158, "아 귀책이 아니라 책임 주체라는 말로 적혀 있었던 것 같기도 하고요."),
    (162, "그때 담당이 바뀌면서 파일이 여기저기로 흩어져서 좀 봐야 됩니다."),
    (174, "운항 스케줄을 건드려야 되는 거라 저희 선에서 정하기가 좀 어렵습니다."),
    (176, "십이월 점검까지 그냥 기다리면 그 두 대는 기한을 넘기게 됩니다."),
    (184, "그 두 건이 다 야간에 나간 작업이었다는 게 좀 걸립니다."),
    (185, "저희 쪽에서는 이제 그 부분을 계속 얘기해 오고 있었고요."),
    (199, "그날 밤에는 인원이 네 명, 아니 다섯 명은 그쪽에 붙어야 됩니다."),
    (200, "새벽까지 입고 준비가 이어질 가능성도 좀 있고요."),
    (211, "검사 항목이 스무 개, 아니 서른 개 가까이 되는 걸로 알고 있습니다."),
    (222, "그 자재가 들어와야 수요일 작업 준비가 됩니다."),
    (229, "그렇게 당기면 기한 안에는 네 대가 다 끝나는 걸로 나옵니다."),
    (245, "그 이 주가 하필 다음 달 중순이라 더 빠듯합니다."),
    (256, "물론 이제 그게 이 주를 넘어가면 얘기가 좀 달라지긴 합니다."),
    (275, "여기에 이제 운송비 인상분까지 붙으면 더 늘어날 수도 있고요."),
    (281, "납기가 긴 데는 실링재 같은 게 두 주씩 걸린다고 합니다."),
    (297, "그 시간에는 조회도 안 되고 입력도 아예 안 됩니다."),
]

# Side talk keeps its tag, otherwise a run of three would be broken in two.
INS_NOTE = {115: "사담"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


SOURCE_ROWS = 325  # the meeting as it was before this plan was applied


def source(suffix: str) -> Path:
    """Refuse to run twice: the plan is written against the 325-row original.

    No copy of the meeting is kept here. `auto/` is the folder every unattended
    run reads, and a second labelled copy of a meeting in it would spoil the
    second-labelling unit, which may only see `<id>.A.csv`.
    """
    path = EVAL / f"{MEETING}.{suffix}.csv"
    if suffix == "C" and len(read(path)) != SOURCE_ROWS:
        raise SystemExit(f"{path.name} is not the {SOURCE_ROWS}-row original; plan already applied")
    return path


def write(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build() -> tuple[list[dict[str, str]], dict[str, str]]:
    original = read(source("C"))
    by_row = {int(r["row"]): r for r in original}

    protected = {int(r["responds_to"]) for r in original if r["responds_to"]}
    for key in read(source("D")):
        protected.add(int(key["settles_row"]))
        protected.update(int(x) for x in key["evidence_rows"].split(",") if x.strip())
    clash = DEL & protected
    if clash:
        raise SystemExit(f"deleting a row something points at: {sorted(clash)}")

    out: list[dict[str, str]] = []
    mapping: dict[int, int] = {}
    inserts: dict[int, list[str]] = {}
    for anchor, text in INS:
        inserts.setdefault(anchor, []).append(text)

    for number in sorted(by_row):
        row = dict(by_row[number])
        if number not in DEL:
            text = SET.get(number, row["text"])
            if number in PRE:
                text = f"{PRE[number]} {text}"
            if number in APP:
                text = f"{text} {APP[number]}"
            row["text"] = text
            out.append(row)
            mapping[number] = len(out)
        for text in inserts.get(number, ()):
            anchor = by_row[number]
            out.append({
                "row": "", "utterance_id": "", "start": "",
                "speaker": anchor["speaker"], "role": anchor["role"], "text": text,
                "kind": "none", "decision_id": anchor["decision_id"], "settles": "",
                "responds_to": "", "note": INS_NOTE.get(number, ""),
            })

    # Numbering, ids and the pointers that carry row numbers.
    for index, row in enumerate(out, start=1):
        row["row"] = str(index)
        row["utterance_id"] = f"{MEETING}-{index:04d}"
        if row["responds_to"]:
            row["responds_to"] = str(mapping[int(row["responds_to"])])

    # Timing: a gap grows with how long the row is, scaled to land the last row
    # inside the 1,700-1,850 second window the spec asks for.
    raw = [1.0 + 0.10 * len(r["text"]) + ((i * 13) % 7) * 0.07 for i, r in enumerate(out)]
    scale = (LAST_START - FIRST_START) / sum(raw[:-1])
    start = FIRST_START
    for index, row in enumerate(out):
        row["start"] = f"{start:.2f}"
        start += min(max(raw[index] * scale, 1.05), 15.4)

    return out, mapping


def retarget_key(mapping: dict[int, int]) -> None:
    keys = read(source("D"))
    for key in keys:
        key["settles_row"] = str(mapping[int(key["settles_row"])])
        key["evidence_rows"] = ",".join(
            str(mapping[int(x)]) for x in key["evidence_rows"].split(",") if x.strip()
        )
    write(EVAL / f"{MEETING}.D.csv", list(keys[0]), keys)


def report(rows: list[dict[str, str]]) -> None:
    lengths = [len(r["text"]) for r in rows]
    same = sum(1 for a, b in zip(rows, rows[1:]) if a["speaker"] == b["speaker"])
    gaps = [float(b["start"]) - float(a["start"]) for a, b in zip(rows, rows[1:])]
    print(f"rows {len(rows)}  chars {sum(lengths)}")
    print(f"median {statistics.median(lengths):.1f}  mean {sum(lengths)/len(lengths):.1f}")
    print(f"same speaker {same/len(rows)*100:.1f}%")
    print(f"rows <= 6 chars {sum(1 for l in lengths if l <= 6)/len(rows)*100:.1f}%")
    print(f"last start {rows[-1]['start']}  gaps {min(gaps):.2f}-{max(gaps):.2f}")


def main() -> None:
    rows, mapping = build()
    write(EVAL / f"{MEETING}.C.csv", COLS, rows)
    write(EVAL / f"{MEETING}.A.csv", COLS,
          [{**{c: r[c] for c in COLS[:6]}, **{c: "" for c in COLS[6:]}} for r in rows])
    retarget_key(mapping)
    report(rows)


if __name__ == "__main__":
    main()
