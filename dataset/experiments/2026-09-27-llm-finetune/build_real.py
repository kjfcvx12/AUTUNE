"""Real-speech test set from AI Hub (local only -- prints counts, never text).

Parts, as dataset/extraction_eval/parts.json defines them:
- aihub_chaired12: extraction_eval_blind2/chaired_12/*.B.csv (hand-reviewed 2026-09-17)
- aihub_blind1:    extraction_eval_blind/*.B.csv (blind-labelled 2026-09-16)

Each meeting is chunked whole, like the dummy sets, so the model sees real
context. Only labelled rows are scored: commitment = yes, any other labelled
kind = no, ambiguous and unlabelled rows = ignore. Writes test_real.jsonl,
which holds AI Hub text and must never be read into a conversation or sent
anywhere. Derived work: 한국지능정보사회진흥원 (NIA) 사업결과.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from build_sft import SYSTEM, chunk, render

HERE = Path(__file__).parent
DATA = HERE.parent.parent
PARTS = {
    "aihub_chaired12": sorted((DATA / "extraction_eval_blind2" / "chaired_12").glob("*.B.csv")),
    "aihub_blind1": sorted((DATA / "extraction_eval_blind").glob("*.B.csv")),
}


def main() -> None:
    rows_out = []
    for part, files in PARTS.items():
        files = [f for f in files if ".first" not in f.name and "recheck" not in f.name]
        yes = no = 0
        for f in files:
            mid = f.name.split(".")[0]
            utts = []
            for i, r in enumerate(csv.DictReader(f.open(encoding="utf-8-sig")), start=1):
                kind = (r.get("kind") or "").strip()
                gold = "yes" if kind == "commitment" else "ignore" if kind in ("", "ambiguous") else "no"
                yes += gold == "yes"
                no += gold == "no"
                role = r.get("role") or ""
                speaker = f"{r['speaker']}({role})" if role else r["speaker"]
                utts.append({"idx": i, "speaker": speaker, "text": r["text"].strip(), "gold": gold})
            for n, (ctx, new) in enumerate(chunk(utts)):
                rows_out.append(
                    {
                        "meeting": f"{part}/{mid}",
                        "chunk": n,
                        "system": SYSTEM,
                        "user": render(ctx, new),
                        "answer": "",
                        "gold_yes": [u["idx"] for u in new if u["gold"] == "yes"],
                        # Unlabelled rows are neither right nor wrong to pick.
                        "gold_ignore": [u["idx"] for u in new if u["gold"] == "ignore"],
                        "new_idx": [u["idx"] for u in new],
                    }
                )
        print(f"{part}: meetings={len(files)} labelled yes={yes} no={no}")
    with (HERE / "test_real.jsonl").open("w", encoding="utf-8") as out:
        for r in rows_out:
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"test_real: chunks={len(rows_out)}")


if __name__ == "__main__":
    main()
