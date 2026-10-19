"""How the current decision pipeline does at the level D reads: decisions, not utterances.

    python entity_eval.py

B classifies each act, then ``group_decisions`` joins runs of ``decision`` acts
(gap <= 2) into entities. AMI annotates decisions as regions: one <decision>
element points at the word ranges where the group reached it. This compares the
two on the natural test set (the 7 decision-annotated test meetings) for:

  model   the official 6-way checkpoint's predictions (../2026-09-11-official-6way)
  oracle  the gold per-act labels -- what grouping gives if classification were perfect

A predicted entity matches a gold region when they share at least one act (lenient)
or when the shared acts are at least half of the smaller one (strict). CPU only;
counts only.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORPUS = ROOT / "dataset" / "ami_public_manual_1.6.2"
OFFICIAL = HERE.parent / "2026-09-11-official-6way"
sys.path.insert(0, str(HERE.parent / "2026-09-10-none-context"))

from exp_ctx_none import build_rows  # noqa: E402

from autune_contracts.enums import UtteranceKind  # noqa: E402
from autune_extraction.decisions import ClassifiedUtterance, group_decisions  # noqa: E402
from autune_extraction.labeling.corpus import NITE, AmiReader  # noqa: E402


def kind(value: str) -> UtteranceKind | None:
    return None if value == "none" else UtteranceKind(value)


def gold_regions(reader: AmiReader, meetings: set[str]) -> dict[str, list[set[str]]]:
    """meeting -> one set of act ids per annotated decision."""
    act_words: dict[str, list[tuple[str, int, int]]] = {}
    act_meeting: dict[str, str] = {}
    for act in reader.acts():
        if act.meeting in meetings:
            act_words[act.act_id] = act.spans
            act_meeting[act.act_id] = act.meeting

    by_file: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    for act_id, spans in act_words.items():
        for filename, start, end in spans:
            by_file[filename].append((start, end, act_id))

    regions: dict[str, list[set[str]]] = defaultdict(list)
    for path in sorted((CORPUS / "decision" / "manual").glob("*.decision.xml")):
        meeting = path.name.split(".")[0]
        if meeting not in meetings:
            continue
        for decision in ET.parse(path).getroot().findall("decision"):
            acts: set[str] = set()
            for filename, start, end in reader.spans_of(decision):
                for a_start, a_end, act_id in by_file.get(filename, ()):
                    if a_start <= end and start <= a_end:
                        acts.add(act_id)
            if acts:
                regions[meeting].append(acts)
    return regions


def entities(ordered: list[dict], labels: dict[str, str]) -> list[set[str]]:
    sequence = [
        ClassifiedUtterance(id=r["id"], kind=kind(labels[r["id"]]), confidence=1.0, text="")
        for r in ordered
        if r["id"] in labels
    ]
    return [set(group.source_utterance_ids) for group in group_decisions(sequence)]


def match(predicted: list[set[str]], gold: list[set[str]], strict: bool) -> tuple[int, int]:
    def hit(p: set[str], g: set[str]) -> bool:
        shared = len(p & g)
        return shared >= 1 if not strict else shared >= 0.5 * min(len(p), len(g))

    matched_pred = sum(any(hit(p, g) for g in gold) for p in predicted)
    matched_gold = sum(any(hit(p, g) for p in predicted) for g in gold)
    return matched_pred, matched_gold


def main() -> None:
    gold_kind = {
        json.loads(l)["utterance_id"]: json.loads(l)["kind"]
        for l in (OFFICIAL / "splits" / "test.jsonl").open(encoding="utf-8")
        if l.strip()
    }
    pred_kind = {
        json.loads(l)["utterance_id"]: json.loads(l)["kind"]
        for l in (OFFICIAL / "pred_test.jsonl").open(encoding="utf-8")
        if l.strip()
    }

    rows, _ = build_rows(CORPUS)
    ordered_by_meeting: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["id"] in gold_kind:
            ordered_by_meeting[row["meeting"]].append(row)
    for acts in ordered_by_meeting.values():
        acts.sort(key=lambda r: (r["start"], r["id"]))
    meetings = set(ordered_by_meeting)

    regions = gold_regions(AmiReader(CORPUS), meetings)
    gold_all = [g for m in meetings for g in regions.get(m, [])]
    sizes = sorted(len(g) for g in gold_all)
    print(
        f"{len(meetings)} meetings, {sum(len(a) for a in ordered_by_meeting.values())} acts, "
        f"{len(gold_all)} gold decisions (acts per decision: median {sizes[len(sizes) // 2]}, "
        f"max {sizes[-1]})"
    )

    for name, labels in (("model", pred_kind), ("oracle", gold_kind)):
        predicted_all: list[set[str]] = []
        totals = {False: [0, 0], True: [0, 0]}
        for m in sorted(meetings):
            predicted = entities(ordered_by_meeting[m], labels)
            predicted_all.extend(predicted)
            for strict in (False, True):
                mp, mg = match(predicted, regions.get(m, []), strict)
                totals[strict][0] += mp
                totals[strict][1] += mg
        n_pred = len(predicted_all)
        line = f"{name:<7} entities {n_pred:>4} (vs {len(gold_all)} gold)"
        for strict in (False, True):
            mp, mg = totals[strict]
            p = mp / n_pred if n_pred else 0.0
            r = mg / len(gold_all) if gold_all else 0.0
            f = 2 * p * r / (p + r) if p + r else 0.0
            line += f" | {'strict ' if strict else 'lenient'} P {p:.2f} R {r:.2f} F1 {f:.2f}"
        esizes = sorted(len(e) for e in predicted_all) or [0]
        print(line + f" | acts/entity median {esizes[len(esizes) // 2]}")


if __name__ == "__main__" and len(sys.argv) == 1:
    main()


def sweep() -> None:
    """Grouping knobs alone: the gap and a minimum entity size, on the model's labels."""
    gold_kind = {json.loads(l)["utterance_id"]: json.loads(l)["kind"] for l in (OFFICIAL / "splits" / "test.jsonl").open(encoding="utf-8") if l.strip()}
    pred_kind = {json.loads(l)["utterance_id"]: json.loads(l)["kind"] for l in (OFFICIAL / "pred_test.jsonl").open(encoding="utf-8") if l.strip()}
    rows, _ = build_rows(CORPUS)
    by_meeting: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["id"] in gold_kind:
            by_meeting[row["meeting"]].append(row)
    for acts in by_meeting.values():
        acts.sort(key=lambda r: (r["start"], r["id"]))
    regions = gold_regions(AmiReader(CORPUS), set(by_meeting))
    n_gold = sum(len(v) for v in regions.values())
    for name, labels in (("model", pred_kind), ("oracle", gold_kind)):
        for gap in (2, 5, 10):
            for min_size in (1, 3, 5):
                preds_all, mp_t, mg_t = 0, 0, 0
                for m, acts in by_meeting.items():
                    seq = [ClassifiedUtterance(id=r["id"], kind=kind(labels[r["id"]]), confidence=1.0, text="") for r in acts]
                    preds = [set(g.source_utterance_ids) for g in group_decisions(seq, max_gap=gap) if len(g.source_utterance_ids) >= min_size]
                    mp, mg = match(preds, regions.get(m, []), strict=True)
                    preds_all += len(preds); mp_t += mp; mg_t += mg
                p = mp_t / preds_all if preds_all else 0.0
                r = mg_t / n_gold
                f = 2 * p * r / (p + r) if p + r else 0.0
                print(f"{name:<6} gap {gap:>2} min {min_size}: entities {preds_all:>4} strict P {p:.2f} R {r:.2f} F1 {f:.2f}")


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "sweep":
    sweep()
