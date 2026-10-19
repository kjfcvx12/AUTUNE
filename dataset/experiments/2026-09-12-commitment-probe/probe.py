"""Find real commitment rows in AI Hub #464's Training split, for review.

    python probe.py scan   [--meetings 40] [--seed 20260912] [--pmin 0.10] [--groups A,B]
    python probe.py sheets [--context 3]

Why: the random evaluation set has 9 commitment rows in 802 reviewed rows, so
commitment F1 means nothing. Broadcast and council recordings simply contain few
of them. A lexical cue filter was tried first and caught 0 of those 9 (AI Hub
rows are intonation phrases, so the ending often sits in the next row), while
Qwen3-4B, over the same 802 rows, predicted commitment 7 times and was right 6
times. So the model is the filter: scan unlabelled Training meetings, keep every
row whose commitment probability clears --pmin, and give a person those rows
with their neighbours for review.

What the result may be used for: **recall on commitment rows a human confirmed**
(biased towards commitments Qwen can find) and per-class error analysis. It is a
class-conditional sample, so it must never be mixed into the random evaluation
set's macro F1, and precision keeps coming from that random set.

Training meetings used here are recorded in `used_meetings.json` and must be
excluded from any pseudo-labelled training set later, or the evaluation leaks.

Counts and ids only, never utterance text -- AI Hub terms forbid showing the data
to anyone not approved for it, which includes whatever reads this terminal.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path

PILOT = Path(r"F:\0final\AUTUNE\dataset\extraction_eval_pilot")
ROOT = Path(
    r"F:\0final\AUTUNE\dataset\002.주요 영역별 회의 음성인식 데이터\01.데이터\1.Training\라벨링데이터"
)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(PILOT))

from pilot_sheets import COLUMNS, clean  # noqa: E402

KINDS = ["commitment", "decision", "open_question", "concern", "ambiguous", "none"]

# Cheap pre-filter, so Qwen only reads rows that could plausibly carry a
# commitment. Calibrated on the 802 reviewed rows: looking at the row plus one
# before and two after (AI Hub rows are intonation phrases, so the ending often
# lands in a later row) keeps 37% of rows and covers 7 of the 9 reviewed
# commitments. Row-only keeps 12% but covers 5 of 9. The cost is recorded: the
# probe can only find commitments whose neighbourhood carries one of these
# endings, on top of the Qwen bias.
ENDING = re.compile(r"겠|ㄹ게|를게|을게|게요|려고|예정|드리|볼게")
PRE_BACK, PRE_FWD = 1, 2


def meetings_by_group() -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = {}
    for group_dir in sorted(ROOT.iterdir()):
        if group_dir.is_dir():
            out[group_dir.name] = sorted(group_dir.rglob("*.json"))
    return out


def load_rows(path: Path) -> tuple[str, list[dict]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    mid = data.get("metadata", {}).get("id") or path.stem
    rows = []
    for i, u in enumerate(data["utterance"], start=1):
        text = clean(u.get("form") or "")
        if not text:
            continue
        rows.append(
            {
                "row": str(i),
                "utterance_id": u.get("id") or f"{mid}-{i}",
                "start": f"{float(u.get('start') or 0):.2f}",
                "speaker": str(u.get("speaker_id") or ""),
                "role": str(u.get("speaker_role") or ""),
                "text": text,
            }
        )
    return mid, rows


def scan(args: argparse.Namespace) -> None:
    from local_llm_label import AFTER, BEFORE, load_model, prompt, score  # noqa: PLC0415

    groups = meetings_by_group()
    if args.groups:
        wanted_groups = args.groups.split(",")
        missing = [g for g in wanted_groups if g not in groups]
        if missing:
            raise SystemExit(f"unknown group(s): {missing}; have {sorted(groups)}")
        groups = {g: groups[g] for g in wanted_groups}
    rng = random.Random(args.seed)
    # Meetings an earlier round already scanned: their candidates were reviewed,
    # so drawing them again would hand the reviewer the same rows twice.
    seen: set[str] = {
        Path(u["path"]).stem
        for f in filter(None, args.exclude.split(","))
        for u in json.loads((HERE / f).read_text("utf-8"))
    }
    excluded = len(seen)
    picked: list[tuple[str, Path]] = []
    names = sorted(groups)
    # Round-robin over the four recording groups so no single one dominates.
    while len(picked) < args.meetings:
        for group in names:
            if len(picked) >= args.meetings:
                break
            pool = groups[group]
            for _ in range(50):
                path = pool[rng.randrange(len(pool))]
                if path.stem in seen:
                    continue
                seen.add(path.stem)
                picked.append((group, path))
                break

    print(f"excluded {excluded} meetings from earlier rounds; picked {len(picked)}", flush=True)
    tok, model, digit_ids = load_model()
    out_dir = HERE / args.out
    out_dir.mkdir(exist_ok=True)
    candidates: list[dict] = []
    used: list[dict] = []
    scanned = asked = 0
    started = time.time()

    for group, path in picked:
        mid, rows = load_rows(path)
        if not rows:
            continue
        wanted = [
            i
            for i in range(len(rows))
            if not args.prefilter
            or ENDING.search(
                " ".join(r["text"] for r in rows[max(0, i - PRE_BACK) : i + PRE_FWD + 1])
            )
        ]
        prompts = [
            prompt(tok, rows[max(0, i - BEFORE) : i + AFTER + 1], min(i, BEFORE)) for i in wanted
        ]
        # Longest first: the batch is padded to its longest prompt, so grouping
        # similar lengths together cuts the padding that is paid for.
        order = sorted(range(len(prompts)), key=lambda k: -len(prompts[k]))
        scored = score(tok, model, digit_ids, [prompts[k] for k in order], batch=args.batch)
        probs: list[list[float]] = [[]] * len(prompts)
        for k, p in zip(order, scored):
            probs[k] = p
        kinds = Counter(KINDS[max(range(6), key=p.__getitem__)] for p in probs)
        hits = [
            {"meeting": mid, "group": group, "row": rows[i]["row"], "index": i,
             "p": [round(x, 4) for x in p], "argmax": KINDS[max(range(6), key=p.__getitem__)]}
            for i, p in zip(wanted, probs)
            if p[0] >= args.pmin
        ]
        candidates.extend(hits)
        used.append({"meeting": mid, "group": group, "path": str(path), "rows": len(rows),
                     "candidates": len(hits), "argmax": dict(kinds)})
        scanned += len(rows)
        asked += len(prompts)
        elapsed = time.time() - started
        print(f"{mid} [{group}] rows {len(rows)} candidates {len(hits)} "
              f"| total rows {scanned} asked {asked} candidates {len(candidates)} "
              f"| {scanned / elapsed:.1f} rows/s ({asked / elapsed:.1f} asked/s)", flush=True)
        (out_dir / "candidates.json").write_text(json.dumps(candidates, ensure_ascii=False), "utf-8")
        (out_dir / "used_meetings.json").write_text(json.dumps(used, ensure_ascii=False, indent=1), "utf-8")
        if args.limit_rows and scanned >= args.limit_rows:
            break

    print(f"\nscanned {scanned} rows in {len(used)} meetings, "
          f"{len(candidates)} candidates (p_commitment >= {args.pmin}), "
          f"argmax commitment {sum(c['argmax'] == 'commitment' for c in candidates)}")


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
    s.add_argument("--meetings", type=int, default=40)
    s.add_argument("--seed", type=int, default=20260912)
    s.add_argument("--pmin", type=float, default=0.10)
    s.add_argument("--limit-rows", type=int, default=0)
    s.add_argument("--batch", type=int, default=16)
    s.add_argument("--groups", default="", help="comma-separated recording groups (default: all four)")
    s.add_argument("--prefilter", action="store_true", default=True)
    s.add_argument("--no-prefilter", dest="prefilter", action="store_false")
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


main()
