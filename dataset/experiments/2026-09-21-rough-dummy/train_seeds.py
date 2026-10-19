"""Train splits/<name> on several seeds; RunConfig is otherwise the production default.

Copied from 2026-09-18-dummy-train so this experiment trains from its own splits
and writes into its own runs/ -- the two sets must not share a directory, because
the whole comparison is that they differ only in the meetings they were written from.

    python train_seeds.py --split v4 --seeds 20260910 20260916 20260917
"""

from __future__ import annotations

import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True)
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    args = ap.parse_args()
    from autune_extraction.training.train import RunConfig, train

    for seed in args.seeds:
        out = HERE / "runs" / f"{args.split}_s{seed}"
        if (out / "run.json").exists():
            print(f"skip {out.name}: already trained", flush=True)
            continue
        print(f"train {out.name}", flush=True)
        train(HERE / "splits" / args.split, out, RunConfig(seed=seed))
        print(f"wrote {out.name}", flush=True)


if __name__ == "__main__":
    main()
