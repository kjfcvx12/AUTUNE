"""Shared scaffolding for dummy131_build.py-style generators (DUMMY_132-140).

Not imported by anything outside dataset/auto/ -- pulls the boilerplate (the
`say()` row collector, timing synthesis, CSV writing, register stats printer)
out of each per-meeting script so those scripts hold only the actual dialogue
and answer key. Same output shape as dummy121-131_build.py.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "team_dummy"

COLS = ["row", "utterance_id", "start", "speaker", "role", "text",
        "kind", "decision_id", "settles", "responds_to", "note"]

FILLER = re.compile(
    r"(?<![가-힣])(음+|어+|아+|그+|저기|뭐|뭐지|뭐냐|뭐랄까|그러니까|그니까|어쨌든|아무튼|약간|이제|일단|좀|그냥|막)(?![가-힣])")
SELF_FIX = re.compile(r"(아니|아니라|그게 아니라|다시 말해|정정)")


class Builder:
    def __init__(self, meeting: str, role: dict[str, str], speakers: dict) -> None:
        self.meeting = meeting
        self.role = role
        self.speakers = speakers
        self.rows: list[dict] = []
        self.labels: dict[str, int] = {}

    def say(self, speaker: str, text: str, kind: str = "none", decision: str = "",
            settles: str = "", rt: int | None = None, note: str = "",
            label: str | None = None) -> None:
        self.rows.append({
            "speaker": speaker, "text": text, "kind": kind, "decision_id": decision,
            "settles": settles, "rt": rt, "note": note,
        })
        if label:
            self.labels[label] = len(self.rows)

    def rownum(self, label: str) -> int:
        return self.labels[label]

    def evidence(self, *names: str) -> str:
        return ",".join(str(self.labels[n]) for n in names)

    def build_starts(self, first: float = 6.0, last: float = 1790.0) -> list[float]:
        rows = self.rows
        weights = []
        for index in range(1, len(rows)):
            text = rows[index - 1]["text"]
            weight = 1.0 + len(text) * 0.09
            if rows[index]["speaker"] != rows[index - 1]["speaker"]:
                weight += 1.9
            weights.append(weight)
        scale = (last - first) / sum(weights)
        starts = [first]
        for weight in weights:
            gap = round(min(max(weight * scale, 1.05), 15.0), 2)
            starts.append(round(starts[-1] + gap, 2))
        return starts

    def write(self, answer_key: list[dict]) -> None:
        starts = self.build_starts()
        c_records, a_records = [], []
        for index, row in enumerate(self.rows):
            number = index + 1
            responds_to = str(number + row["rt"]) if row["rt"] is not None else ""
            shared = {
                "row": str(number),
                "utterance_id": f"{self.meeting}-{number:04d}",
                "start": f"{starts[index]:.2f}",
                "speaker": row["speaker"],
                "role": self.role[row["speaker"]],
                "text": row["text"],
            }
            c_records.append({**shared, "kind": row["kind"], "decision_id": row["decision_id"],
                               "settles": row["settles"], "responds_to": responds_to,
                               "note": row["note"]})
            a_records.append({**shared, "kind": "", "decision_id": "", "settles": "",
                               "responds_to": "", "note": ""})

        OUT.mkdir(parents=True, exist_ok=True)
        _write_csv(OUT / f"{self.meeting}.C.csv", c_records, COLS)
        _write_csv(OUT / f"{self.meeting}.A.csv", a_records, COLS)

        key_cols = ["decision_id", "settles_row", "statement", "owner", "due",
                    "due_as_said", "evidence_rows", "note"]
        key_records = [
            {**entry,
             "settles_row": str(self.rownum(entry["settles_row"])),
             "evidence_rows": self.evidence(*entry["evidence_rows"])}
            for entry in answer_key
        ]
        _write_csv(OUT / f"{self.meeting}.D.csv", key_records, key_cols)
        (OUT / f"{self.meeting}.speakers.json").write_text(
            json.dumps(self.speakers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        self._report(starts)

    def _report(self, starts: list[float]) -> None:
        rows = self.rows
        lengths = [len(r["text"]) for r in rows]
        total = sum(lengths)
        same = sum(1 for a, b in zip(rows, rows[1:]) if a["speaker"] == b["speaker"])
        kinds: dict[str, int] = {}
        for row in rows:
            kinds[row["kind"]] = kinds.get(row["kind"], 0) + 1
        print(f"{self.meeting}: rows {len(rows)}  last start {starts[-1]:.2f}")
        print(f"  median {sorted(lengths)[len(lengths) // 2]}  mean {total / len(lengths):.1f}  "
              f"same-speaker {same / len(rows) * 100:.1f}%  "
              f"short<=6 {sum(1 for n in lengths if n <= 6) / len(rows) * 100:.1f}%")
        print(f"  fillers {sum(len(FILLER.findall(r['text'])) for r in rows) / total * 100:.2f}/100  "
              f"self-fix {sum(len(SELF_FIX.findall(r['text'])) for r in rows) / total * 100:.2f}/100")
        print("  kinds " + " ".join(f"{k} {v}" for k, v in sorted(kinds.items())))


def _write_csv(path: Path, records: list[dict], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)
