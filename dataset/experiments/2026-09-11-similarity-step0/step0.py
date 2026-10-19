"""Step 0 of the mentoring suggestion "add similar sentences from further away".

No training. Two questions, answered on AMI where the truth is annotated:

  1. Distance -- for acts labelled from an adjacency pair (concern, ambiguous, and
     commitments that answer something), how far back is the act they respond to?
     If it is almost always inside the +-2 window the model already sees, far
     context has nothing to add and the experiment stops here.
  2. Retrieval -- when the source is outside the window, does embedding similarity
     (KURE-v1) find it among the earlier acts, and does it beat simply taking the
     nearest acts outside the window (recency) and chance?

Plus a side check for decision: are the most similar earlier acts inside the same
decision region more often than the nearest ones?

    python step0.py --corpus dataset/ami_public_manual_1.6.2 --out <dir>

Run with the aiprj env, PYTHONPATH on the module sources, HF_HUB_OFFLINE=1.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-09-10-none-context"))

import torch  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

import exp_ctx_none as exp  # noqa: E402
from autune_extraction.labeling.corpus import NITE, AmiReader, _pointer  # noqa: E402

WINDOW = 2          # what ctx2 already shows: the two acts before the target
MIN_WORDS = 3       # candidates shorter than this are backchannels and fillers
KS = (1, 2, 5, 10)
EMBEDDER = "nlpai-lab/KURE-v1"


def pair_sources(corpus: Path) -> dict[str, str]:
    """target act id -> source act id, first pair per target (as the labels use)."""
    out: dict[str, str] = {}
    for path in sorted((corpus / "dialogueActs").glob("*.adjacency-pairs.xml")):
        for pair in ET.parse(path).getroot().findall("adjacency-pair"):
            source, target = _pointer(pair, "source"), _pointer(pair, "target")
            if source and target:
                out.setdefault(target, source)
    return out


def decision_regions(corpus: Path) -> dict[str, list[tuple[str, int, int, str]]]:
    """words file -> (file, first, last, region id) for each decision's spans."""
    reader = AmiReader(corpus)
    out: dict[str, list[tuple[str, int, int, str]]] = defaultdict(list)
    for path in sorted((corpus / "decision" / "manual").glob("*.decision.xml")):
        for decision in ET.parse(path).getroot().findall("decision"):
            rid = decision.get(f"{NITE}id", "")
            for filename, start, end in reader.spans_of(decision):
                out[filename].append((filename, start, end, rid))
    return out


def bucket(d: int) -> str:
    if d <= 0:
        return "source after target"
    if d <= WINDOW:
        return f"1-{WINDOW} (in window)"
    for hi, name in ((5, "3-5"), (10, "6-10"), (30, "11-30")):
        if d <= hi:
            return name
    return ">30"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    rows, _ = exp.build_rows(args.corpus)
    by_meeting: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_meeting[r["meeting"]].append(r)
    pos: dict[str, tuple[str, int]] = {}
    for m, acts in by_meeting.items():
        acts.sort(key=lambda r: (r["start"], r["speaker"], r["id"]))  # exp.Encoder's order
        for i, r in enumerate(acts):
            pos[r["id"]] = (m, i)
    sources = pair_sources(args.corpus)
    print(f"rows {len(rows):,} in {len(by_meeting)} meetings, pairs {len(sources):,} | {time.time() - t0:.0f}s", flush=True)

    # --- 1. distance -------------------------------------------------------
    report: dict = {"window": WINDOW, "min_words": MIN_WORDS, "embedder": EMBEDDER, "distance": {}, "retrieval": {}}
    far: dict[str, list[tuple[str, int, int]]] = defaultdict(list)  # kind -> (meeting, target pos, source pos)
    for kind in ("concern", "ambiguous", "commitment"):
        hist: Counter = Counter()
        missing = 0
        for r in rows:
            if r["kind"] != kind or r["id"] not in sources:
                continue
            src = sources[r["id"]]
            if src not in pos or pos[src][0] != r["meeting"]:
                missing += 1
                continue
            d = pos[r["id"]][1] - pos[src][1]
            hist[bucket(d)] += 1
            if d > WINDOW:
                far[kind].append((r["meeting"], pos[r["id"]][1], pos[src][1]))
        n = sum(hist.values())
        report["distance"][kind] = {"targets": n, "source_missing": missing, "buckets": dict(hist)}
        order = ["source after target", f"1-{WINDOW} (in window)", "3-5", "6-10", "11-30", ">30"]
        print(f"\n{kind}: {n} pair targets (source not found {missing})")
        for b in order:
            print(f"  {b:<22}{hist[b]:>6}  {hist[b] / max(n, 1):6.1%}")

    # --- 2. retrieval --------------------------------------------------------
    t1 = time.time()
    model = SentenceTransformer(EMBEDDER, device="cuda")
    model.half()
    model.max_seq_length = 64
    emb: dict[str, torch.Tensor] = {}
    texts = [r["text"] for m in by_meeting for r in by_meeting[m]]
    flat = model.encode(texts, batch_size=256, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=False)
    i = 0
    for m, acts in by_meeting.items():
        emb[m] = flat[i : i + len(acts)]
        i += len(acts)
    print(f"\nembedded {len(texts):,} acts with {EMBEDDER} in {time.time() - t1:.0f}s", flush=True)

    def ranks(m: str, t: int, filt: bool) -> dict[str, list[int]]:
        acts, E = by_meeting[m], emb[m]
        cand = [j for j in range(0, t - WINDOW) if not filt or len(acts[j]["text"].split()) >= MIN_WORDS]
        if not cand:
            return {}
        C = E[cand]
        q_t = E[t]
        q_ctx = torch.nn.functional.normalize(E[max(0, t - WINDOW) : t + 1].float().sum(0), dim=0).to(E.dtype)
        out = {"recency": sorted(cand, reverse=True)}
        for name, q in (("sim_target", q_t), ("sim_target+2", q_ctx)):
            order = torch.argsort((C @ q).float(), descending=True).tolist()
            out[name] = [cand[o] for o in order]
        out["_n"] = [len(cand)]
        return out

    for kind, items in far.items():
        report["retrieval"][kind] = {}
        for filt in (False, True):
            hits: dict[str, Counter] = defaultdict(Counter)
            chance: Counter = Counter()
            n = excluded = 0
            for m, t, s in items:
                rk = ranks(m, t, filt)
                if not rk or s not in rk["recency"]:
                    excluded += 1  # the filter removed the source itself: a miss for every method
                    n += 1
                    continue
                n += 1
                for k in KS:
                    chance[k] += min(k, rk["_n"][0]) / rk["_n"][0]
                    for name in ("recency", "sim_target", "sim_target+2"):
                        hits[name][k] += s in rk[name][:k]
            label = f"min {MIN_WORDS} words" if filt else "all candidates"
            res = {name: {k: hits[name][k] / n for k in KS} for name in ("recency", "sim_target", "sim_target+2")}
            res["chance"] = {k: chance[k] / n for k in KS}
            report["retrieval"][kind][label] = {"targets": n, "source_filtered_out": excluded, "recall": res}
            print(f"\n{kind}, source outside the window: {n} targets, {label}"
                  + (f" (filter drops the source in {excluded})" if filt else ""))
            print(f"  {'recall@':<14}" + "".join(f"{k:>8}" for k in KS))
            for name in ("chance", "recency", "sim_target", "sim_target+2"):
                print(f"  {name:<14}" + "".join(f"{res[name][k]:>8.1%}" for k in KS))

    # --- 3. decision side check ------------------------------------------------
    regions = decision_regions(args.corpus)
    reader = AmiReader(args.corpus)
    region_of: dict[str, set[str]] = {}
    for act in reader.acts():
        rs = {rid for f, s, e in act.spans for (_, rs_, re_, rid) in regions.get(f, ()) if s <= re_ and rs_ <= e}
        if rs:
            region_of[act.act_id] = rs
    prec: dict[str, Counter] = defaultdict(Counter)
    base = 0.0
    n = 0
    for m, acts in by_meeting.items():
        for t, r in enumerate(acts):
            if r["kind"] != "decision" or r["id"] not in region_of:
                continue
            rk = ranks(m, t, True)
            if not rk:
                continue
            same = lambda j: bool(region_of.get(acts[j]["id"], set()) & region_of[r["id"]])  # noqa: E731
            n += 1
            base += sum(same(j) for j in rk["recency"]) / len(rk["recency"])
            for name in ("recency", "sim_target", "sim_target+2"):
                prec[name][2] += sum(same(j) for j in rk[name][:2]) / min(2, len(rk[name]))
    report["decision_same_region_precision_at_2"] = {"targets": n, "chance": base / n,
                                                     **{k: prec[k][2] / n for k in prec}}
    print(f"\ndecision acts: {n} | earlier acts outside the window that share the region, precision@2:")
    print(f"  chance {base / n:.1%} | " + " | ".join(f"{k} {prec[k][2] / n:.1%}" for k in ("recency", "sim_target", "sim_target+2")))

    (args.out / "step0.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\ndone in {(time.time() - t0) / 60:.1f} min")


if __name__ == "__main__":
    main()
