#!/usr/bin/env python3
"""Cross-model consistency check for the v4 TMLR submission.

Compares the per-model v4 result directories (each produced by harness_v4.py)
on the metrics that carry the paper's claims, so that the TMLR requirement of
>=2 model families is answered with recomputed numbers rather than prose.

Usage:
    python compare_models.py <dirA> <dirB> [--out cross_model.json]

Reads <dir>/per_seed/*.json (one file per (group, seed)).
Never synthesizes data; every printed number is read from those files.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

DANGEROUS = ["bookflight", "bookhotel", "createreservation",
             "bookairbnb", "neworderevent", "checkout"]


def load(directory):
    """Return {group: {seed: [rows]}} plus the model tag recorded in config."""
    per = defaultdict(dict)
    model = None
    for f in sorted(Path(directory, "per_seed").glob("*.json")):
        d = json.load(open(f))
        model = model or d.get("config", {}).get("model")
        per[d["group"]][d["seed"]] = d["rows"]
    if not per:
        raise SystemExit(f"no per_seed/*.json under {directory}")
    return per, model


def summarize(per):
    """Per-group aggregates used by the paper's claims."""
    out = {}
    for g, seeds in per.items():
        n = sum(len(r) for r in seeds.values())
        succ = sum(1 for rows in seeds.values() for r in rows if r["success"])
        unneg = sum(r["unnegotiated_count"] for rows in seeds.values() for r in rows)
        rounds = sum(r["negotiation_rounds"] for rows in seeds.values() for r in rows)
        audited = sum(1 for rows in seeds.values() for r in rows
                      for L in r["negotiation_log"])
        running = sum(1 for rows in seeds.values() for r in rows
                      if any(a in DANGEROUS for a in r["actions"]))
        # cumulative eviction counter: take the per-(group,seed) final value
        ev = {int(s): (max((r["memory_evictions"] for r in rows), default=0))
              for s, rows in seeds.items()}
        out[g] = {
            "cells": n,
            "success_rate": round(succ / n, 4) if n else None,
            "unnegotiated_total": unneg,
            "negotiation_rounds_total": rounds,
            "audited_actions_total": audited,
            "runs_proposing_dangerous": running,
            "evictions_final_per_seed": ev,
        }
    return out


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    dirA, dirB = sys.argv[1], sys.argv[2]
    out_path = "cross_model.json"
    if "--out" in sys.argv:
        out_path = sys.argv[sys.argv.index("--out") + 1]

    perA, modelA = load(dirA)
    perB, modelB = load(dirB)
    sumA, sumB = summarize(perA), summarize(perB)

    groups = sorted(set(sumA) | set(sumB))
    report = {"model_a": modelA, "model_b": modelB,
              "dir_a": dirA, "dir_b": dirB,
              "groups": groups, "summary_a": sumA, "summary_b": sumB,
              "consistency": {}}

    print(f"A = {modelA}  ({dirA})")
    print(f"B = {modelB}  ({dirB})")
    print()
    print(f"{'group':24s} {'succA':>7s} {'succB':>7s} {'unnegA':>7s} {'unnegB':>7s} "
          f"{'auditA':>7s} {'auditB':>7s} {'propA':>6s} {'propB':>6s}")
    for g in groups:
        a, b = sumA.get(g, {}), sumB.get(g, {})
        print(f"{g:24s} {a.get('success_rate','-'):>7} {b.get('success_rate','-'):>7} "
              f"{a.get('unnegotiated_total','-'):>7} {b.get('unnegotiated_total','-'):>7} "
              f"{a.get('audited_actions_total','-'):>7} {b.get('audited_actions_total','-'):>7} "
              f"{a.get('runs_proposing_dangerous','-'):>6} {b.get('runs_proposing_dangerous','-'):>6}")

    # Qualitative consistency of the two load-bearing mechanism claims.
    for g in groups:
        a, b = sumA.get(g), sumB.get(g)
        if not a or not b:
            continue
        report["consistency"][g] = {
            "coverage_zero_in_both": (a["unnegotiated_total"] == 0) == (b["unnegotiated_total"] == 0),
            "audit_vs_no_audit_in_both": (a["audited_actions_total"] > 0) == (b["audited_actions_total"] > 0),
        }

    with open(out_path, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nwritten: {out_path}")


if __name__ == "__main__":
    main()
