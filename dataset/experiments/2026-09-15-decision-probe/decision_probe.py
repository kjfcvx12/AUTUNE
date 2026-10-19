"""Find real decision rows in AI Hub #464's **Validation** split, for review.

    python decision_probe.py scan   [--meetings 30] [--seed 20260915] [--pmin 0.10] [--groups 기타녹음]
    python decision_probe.py sheets [--context 3]

Why: every Korean evaluation set we have is nearly empty of decisions -- the blind
set has 0 in 200 rows, S4 has 4, the anchored pilot 46 in 802 -- so no number we
report says anything about the class the product is built around. The corpora are
mostly meetings that do not decide anything. This probe collects the decisions
that do exist, for a person to confirm.

Differences from the commitment probe (../2026-09-12-commitment-probe/probe.py):

  - **Validation split.** These rows are evaluation data. Training never reads
    Validation, and the pilot's six meetings and the blind set's two are excluded,
    so the confirmed rows overlap nothing a model was trained or scored on.
  - **No lexical pre-filter.** Calibrated on the 802 reviewed pilot rows, a window
    of decision cues (하기로, 걸로, 결정/확정/합의, 가결/의결/통과, ...) over the row
    plus one before and two after covered 6 of 46 human decisions. Every row goes
    to Qwen.
  - **Candidates are p_decision >= --pmin.** On the same rows Qwen's p_decision >= 0.10
    caught 23 of 46 decisions (argmax 21).

What the result may be used for: **decision recall on rows a human confirmed** and
error analysis. Known bias: only decisions Qwen gives >= --pmin are visible (about
half on the pilot). It is a class-conditional sample -- never mix it into a random
set's macro F1, and take precision from a random set instead.

Counts and ids only, never utterance text -- AI Hub terms forbid showing the data
to anyone not approved for it, which includes whatever reads this terminal.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

PILOT = Path(r"F:\0final\AUTUNE\dataset\extraction_eval_pilot")
ROOT = Path(
    r"F:\0final\AUTUNE\dataset\002.주요 영역별 회의 음성인식 데이터\01.데이터\2.Validation\라벨링데이터_260312_add\VL1"
)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(PILOT))

from pilot_sheets import COLUMNS, clean  # noqa: E402

KINDS = ["commitment", "decision", "open_question", "concern", "ambiguous", "none"]
DECISION = KINDS.index("decision")
# Validation meetings already used for evaluation: the pilot's six AI Hub meetings
# and the blind set's two. Scanning them again would put the same rows in two sets.
ALREADY_USED = {
    "DGBEB21000006", "DGBEB21000048", "DGBED21000061", "SRBAA21000085", "SRBBC21000010", "SRBDD21000008",
    "DGBED21000059", "DGBEC21000021",
}


def meetings_by_group() -> dict[str, list[Path]]:
    return {d.name: sorted(d.rglob("*.json")) for d in sorted(ROOT.iterdir()) if d.is_dir()}


def load_rows(path: Path) -> tuple[str, list[dict]]:
    data = json.loads(path.read_bytes().decode("utf-8-sig"))
    mid = data.get("metadata", {}).get("title") or path.stem
    rows = []
    for i, u in enumerate(data["utterance"], start=1):
        text = clean(u.get("form") or "")
        if not text:
            continue
        rows.append({
            "row": str(i),
            "utterance_id": u.get("id") or f"{mid}-{i}",
            "start": f"{float(u.get('start') or 0):.2f}",
            "speaker": str(u.get("speaker_id") or ""),
            "role": str(u.get("speaker_role") or ""),
            "text": text,
        })
    return mid, rows


def scan(args: argparse.Namespace) -> None:
    from local_llm_label import AFTER, BEFORE, load_model, prompt, score  # noqa: PLC0415

    groups = meetings_by_group()
    wanted_groups = [g for g in args.groups.split(",") if g] or sorted(groups)
    missing = [g for g in wanted_groups if g not in groups]
    if missing:
        raise SystemExit(f"unknown group(s): {missing}; have {sorted(groups)}")
    rng = random.Random(args.seed)
    seen = set(ALREADY_USED) | {
        Path(u["path"]).stem for f in filter(None, args.exclude.split(",")) for u in json.loads((HERE / f).read_text("utf-8"))
    }
    pools = {g: [p for p in groups[g] if p.stem not in seen] for g in wanted_groups}
    for g in pools:
        rng.shuffle(pools[g])
    picked: list[tuple[str, Path]] = []
    while len(picked) < args.meetings and any(pools.values()):
        for g in wanted_groups:
            if pools[g] and len(picked) < args.meetings:
                picked.append((g, pools[g].pop()))

    print(f"groups {wanted_groups}; picked {len(picked)} meetings (excluding {len(seen)} already used)", flush=True)
    tok, model, digit_ids = load_model()
    out_dir = HERE / args.out
    out_dir.mkdir(exist_ok=True)
    candidates: list[dict] = []
    used: list[dict] = []
    scanned = 0
    started = time.time()

    for group, path in picked:
        mid, rows = load_rows(path)
        if not rows:
            continue
        if args.limit_rows:
            rows = rows[: args.limit_rows]
        prompts = [prompt(tok, rows[max(0, i - BEFORE): i + AFTER + 1], min(i, BEFORE)) for i in range(len(rows))]
        order = sorted(range(len(prompts)), key=lambda k: -len(prompts[k]))
        scored = score(tok, model, digit_ids, [prompts[k] for k in order], batch=args.batch)
        probs: list[list[float]] = [[]] * len(prompts)
        for k, p in zip(order, scored):
            probs[k] = p
        argmax = Counter(KINDS[max(range(6), key=p.__getitem__)] for p in probs)
        hits = [
            {"meeting": mid, "group": group, "row": rows[i]["row"], "index": i,
             "p": [round(x, 4) for x in p], "argmax": KINDS[max(range(6), key=p.__getitem__)]}
            for i, p in enumerate(probs)
            if p[DECISION] >= args.pmin
        ]
        candidates.extend(hits)
        used.append({"meeting": mid, "group": group, "path": str(path), "rows": len(rows),
                     "candidates": len(hits), "argmax": dict(argmax)})
        scanned += len(rows)
        elapsed = time.time() - started
        print(f"{mid} [{group}] rows {len(rows)} candidates {len(hits)} (argmax decision {argmax['decision']}) "
              f"| total rows {scanned} candidates {len(candidates)} | {scanned / elapsed:.1f} rows/s", flush=True)
        (out_dir / "candidates.json").write_text(json.dumps(candidates, ensure_ascii=False), "utf-8")
        (out_dir / "used_meetings.json").write_text(json.dumps(used, ensure_ascii=False, indent=1), "utf-8")

    print(f"\nscanned {scanned} rows in {len(used)} meetings, {len(candidates)} candidates "
          f"(p_decision >= {args.pmin}), argmax decision {sum(c['argmax'] == 'decision' for c in candidates)}")


def sheets(args: argparse.Namespace) -> None:
    """Write review sheets: every candidate row plus `--context` rows either side."""
    out_dir = HERE / args.out
    out_dir.mkdir(exist_ok=True)
    candidates = json.loads((HERE / args.results / "candidates.json").read_text("utf-8"))
    used = {u["meeting"]: u for u in json.loads((HERE / args.results / "used_meetings.json").read_text("utf-8"))}
    by_meeting: dict[str, list[dict]] = {}
    for c in candidates:
        by_meeting.setdefault(c["meeting"], []).append(c)

    total_rows = total_targets = 0
    for mid, hits in sorted(by_meeting.items()):
        _, rows = load_rows(Path(used[mid]["path"]))
        keep: set[int] = set()
        for c in hits:
            keep.update(range(max(0, c["index"] - args.context), min(len(rows), c["index"] + args.context + 1)))
        p_by_index = {c["index"]: c["p"] for c in hits}
        with (out_dir / f"{mid}.A.csv").open("w", encoding="utf-8-sig", newline="") as fa, \
             (out_dir / f"{mid}.L.csv").open("w", encoding="utf-8-sig", newline="") as fl:
            wa = csv.DictWriter(fa, fieldnames=COLUMNS)
            lcols = COLUMNS + ["llm_kind", "llm_p"] + [f"p_{k}" for k in KINDS] + ["llm_responds_to"]
            wl = csv.DictWriter(fl, fieldnames=lcols)
            wa.writeheader()
            wl.writeheader()
            for i in sorted(keep):
                base = {c: rows[i].get(c, "") for c in COLUMNS}
                wa.writerow(base)
                p = p_by_index.get(i)
                row = dict(base)
                if p is not None:
                    best = max(range(6), key=p.__getitem__)
                    row["llm_kind"] = KINDS[best]
                    row["llm_p"] = f"{p[best]:.3f}"
                    row.update({f"p_{k}": f"{v:.4f}" for k, v in zip(KINDS, p)})
                    total_targets += 1
                else:
                    row["llm_kind"] = ""
                    row["llm_p"] = ""
                wl.writerow(row)
            total_rows += len(keep)
    print(f"{len(by_meeting)} sheets, {total_rows} rows, {total_targets} candidate rows -> {out_dir}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--meetings", type=int, default=30)
    s.add_argument("--seed", type=int, default=20260915)
    s.add_argument("--pmin", type=float, default=0.10)
    s.add_argument("--limit-rows", type=int, default=0, help="per meeting; for a smoke test")
    s.add_argument("--batch", type=int, default=6, help="6 held 2.6 rows/s on the 12 GB card; 16 collapsed")
    s.add_argument("--groups", default="기타녹음", help="comma-separated recording groups")
    s.add_argument("--out", default="results", help="results directory, relative to this folder")
    s.add_argument("--exclude", default="", help="comma-separated used_meetings.json files of earlier rounds")
    s.set_defaults(func=scan)
    b = sub.add_parser("sheets")
    b.add_argument("--context", type=int, default=3)
    b.add_argument("--results", default="results")
    b.add_argument("--out", default="sheets")
    b.set_defaults(func=sheets)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
