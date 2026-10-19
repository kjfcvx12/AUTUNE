"""Build chunked SFT / eval data for fine-tuning Qwen3-4B as an action-item picker.

Task (same split of labour as the 09-26 v9 combo): the model sees one chunk of a
meeting, each utterance numbered `[#N]`, and answers only WHICH `[신규]`
utterances are action items, as JSON. Assignee and due date come from the
utterance itself (speaker lookup + parse_due), and description from B's
existing slots/resolver path, so the model never writes free text -- which
removes v6-v11's language-contamination and rambling failure modes by
construction.

Gold = kind == "commitment", minus recalls (note contains 상기), which the
SPEC also labels commitment but which are not new work. Recalls are recorded
as `ignore` so eval neither rewards nor punishes them.

Sources (all self-authored dummy data, no AI Hub):
- train: team_dummy DUMMY_001..130 (C.csv, planted labels)
- val:   team_dummy DUMMY_131..140
- test:  extraction_eval_dummy EVAL_* + extraction_eval_dummy_hard EVALH_*
         (G.csv = rows two labellers agreed on; `disagreement` rows -> ignore)

Prints counts only.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE.parent.parent

SYSTEM = (
    "당신은 회의 녹취록 조각에서 액션아이템 발화를 고르는 도구입니다.\n"
    "액션아이템 발화: 화자 본인이 앞으로 할 일을 맡겠다고 말한 발화, 또는 요청받은 일을 "
    "수락한 발화입니다. 기한이 없어도 됩니다.\n"
    "아닌 것: 남에게 하는 요청이나 질문 자체, 제안, 투표, 이미 끝났거나 진행 중인 일의 설명, "
    "예전 약속을 다시 언급한 것, 취소된 일, 잡담.\n"
    "[이전] 발화는 앞 조각에서 이미 판단했으니 문맥으로만 쓰고, [신규] 발화 번호만 답하세요.\n"
    '답은 JSON 한 줄입니다: {"items": [번호, ...]}. 없으면 {"items": []}.'
)

CHUNK_CHARS = 1200
CONTEXT_TURNS = 3


def speaker_names(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    meta = json.loads(path.read_text(encoding="utf-8"))
    return {s["speaker"]: s.get("name") or s["speaker"] for s in meta.get("speakers", [])}


def load_meeting(label_csv: Path, speakers_json: Path) -> list[dict]:
    names = speaker_names(speakers_json)
    rows = list(csv.DictReader(label_csv.open(encoding="utf-8-sig")))
    out = []
    for i, r in enumerate(rows, start=1):
        kind = (r.get("kind") or "none").strip()
        note = r.get("note") or ""
        if kind == "disagreement" or (kind == "commitment" and "상기" in note):
            gold = "ignore"
        elif kind == "commitment":
            gold = "yes"
        else:
            gold = "no"
        name = names.get(r["speaker"], r["speaker"])
        role = r.get("role") or ""
        out.append(
            {
                "idx": i,
                "speaker": f"{name}({role})" if role else name,
                "text": r["text"].strip(),
                "gold": gold,
            }
        )
    return out


def chunk(utts: list[dict]) -> list[tuple[list[dict], list[dict]]]:
    chunks, cur, size = [], [], 0
    for u in utts:
        if cur and size + len(u["text"]) > CHUNK_CHARS:
            chunks.append(cur)
            cur, size = [], 0
        cur.append(u)
        size += len(u["text"])
    if cur:
        chunks.append(cur)
    out, prev_end = [], []
    for c in chunks:
        out.append((prev_end[-CONTEXT_TURNS:], c))
        prev_end = c
    return out


def render(context: list[dict], new: list[dict]) -> str:
    lines = [f"[#{u['idx']}] [이전] {u['speaker']}: {u['text']}" for u in context]
    lines += [f"[#{u['idx']}] [신규] {u['speaker']}: {u['text']}" for u in new]
    return "\n".join(lines)


def examples(meeting_id: str, utts: list[dict]) -> list[dict]:
    out = []
    for n, (ctx, new) in enumerate(chunk(utts)):
        yes = [u["idx"] for u in new if u["gold"] == "yes"]
        out.append(
            {
                "meeting": meeting_id,
                "chunk": n,
                "system": SYSTEM,
                "user": render(ctx, new),
                "answer": json.dumps({"items": yes}, ensure_ascii=False),
                "gold_yes": yes,
                "gold_ignore": [u["idx"] for u in new if u["gold"] == "ignore"],
                "new_idx": [u["idx"] for u in new],
            }
        )
    return out


def meeting_num(p: Path) -> int:
    return int(re.search(r"_(\d+)\.", p.name).group(1))


def main() -> None:
    splits: dict[str, list[dict]] = {"train": [], "val": [], "test": []}
    team = sorted((DATA / "team_dummy").glob("DUMMY_*.C.csv"), key=meeting_num)
    for p in team:
        mid = p.name.split(".")[0]
        split = "train" if meeting_num(p) <= 130 else "val"
        splits[split] += examples(mid, load_meeting(p, p.with_name(f"{mid}.speakers.json")))
    for folder in ("extraction_eval_dummy", "extraction_eval_dummy_hard"):
        for p in sorted((DATA / folder).glob("*.G.csv")):
            mid = p.name.split(".")[0]
            splits["test"] += examples(mid, load_meeting(p, p.with_name(f"{mid}.speakers.json")))

    for name, rows in splits.items():
        with (HERE / f"{name}.jsonl").open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        yes = sum(len(r["gold_yes"]) for r in rows)
        ign = sum(len(r["gold_ignore"]) for r in rows)
        empty = sum(1 for r in rows if not r["gold_yes"])
        chars = [len(r["user"]) for r in rows]
        print(
            f"{name}: meetings={len({r['meeting'] for r in rows})} chunks={len(rows)} "
            f"yes={yes} ignore={ign} empty_chunks={empty} "
            f"user_chars max={max(chars)} mean={sum(chars) // len(chars)}"
        )


if __name__ == "__main__":
    main()
