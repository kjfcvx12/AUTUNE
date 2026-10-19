"""8.txt (self-authored, 87 turns) as a second test set, chunked like build_sft.

Utterance-level gold derived 2026-09-27 by reading the transcript -- NOT the
09-26 12-item checklist, which counted items (one item can span an offer and a
later dated confirmation, e.g. #29 + #37). Ambiguous rows are ignored:
#42/#43 (both offer the same check; #44 hands it to 재경 and #45 accepts),
#47 (restated by #49), #52 (conditional, dropped by the chair), #76 (promise to
relay a result).

Also re-scores the 09-26 v9 run's picked utterances against the same gold.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from build_sft import SYSTEM, chunk, render

HERE = Path(__file__).parent
# The 09-26/27 v9 run's files, preserved out of that session's temp scratchpad.
V9 = HERE.parent / "2026-09-26-local-vs-api" / "scratch_e27a3912"

YES = {14, 20, 29, 34, 35, 37, 45, 46, 48, 49, 68, 69, 74, 75, 77, 79}
IGNORE = {42, 43, 47, 52, 76}


def main() -> None:
    payload = json.loads((V9 / "step1_chunks_overlap_8.json").read_text(encoding="utf-8"))
    seen: dict[int, dict] = {}
    for c in payload["chunks"]:
        for u in c["utterances"]:
            if u["idx"] > 0:
                seen.setdefault(u["idx"], u)
    utts = [
        {
            "idx": i,
            "speaker": seen[i]["speaker"],
            "text": seen[i]["text"],
            "gold": "yes" if i in YES else "ignore" if i in IGNORE else "no",
        }
        for i in sorted(seen)
    ]
    rows = []
    for n, (ctx, new) in enumerate(chunk(utts)):
        rows.append(
            {
                "meeting": "8txt",
                "chunk": n,
                "system": SYSTEM,
                "user": render(ctx, new),
                "answer": json.dumps(
                    {"items": [u["idx"] for u in new if u["gold"] == "yes"]}, ensure_ascii=False
                ),
                "gold_yes": [u["idx"] for u in new if u["gold"] == "yes"],
                "gold_ignore": [u["idx"] for u in new if u["gold"] == "ignore"],
                "new_idx": [u["idx"] for u in new],
            }
        )
    with (HERE / "test8.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"test8: utterances={len(utts)} chunks={len(rows)} yes={len(YES)} ignore={len(IGNORE)}")

    raw = (V9 / "remerge_overlap_similarity_result.txt").read_text(encoding="utf-8")
    body = raw.split("=== all deduped rows ===", 1)[1]
    picked = {int(m) for m in re.findall(r"^\s*\((\d+),", body, re.M)} - IGNORE
    tp, fp, fn = len(picked & YES), len(picked - YES), len(YES - picked)
    p, r = tp / (tp + fp), tp / (tp + fn)
    print(
        f"v9 (09-26, long prompt + classifier hints): picked={len(picked)} tp={tp} fp={fp} "
        f"fn={fn} P={p:.3f} R={r:.3f} F1={2 * p * r / (p + r):.3f} "
        f"fp_ids={sorted(picked - YES)} fn_ids={sorted(YES - picked)}"
    )


if __name__ == "__main__":
    main()
