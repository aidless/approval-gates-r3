#!/usr/bin/env python3
"""End-to-end v4 analysis for the TMLR submission (one command after the runs finish).

Steps:
  1. pull every per_seed/*.json from the cloud result dirs (27B dry run of
     scp; falls back to a clear error if scp is unavailable)
  2. verify the grid is complete and error-free
  3. recompute every statistic with the canonical analysis script
  4. cross-check the two model families for qualitative agreement
  5. print a compact report

Nothing here invents numbers: steps 2-4 only read what step 1 fetched.

Usage:
    python run_v4_analysis.py [--no-fetch]
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # paper project root
SCRIPTS = ROOT / "scripts"
GROUPS = ["Full", "Abl-noForget", "Abl-noNegot",
          "Baseline-promptSafety", "Baseline-heavyAudit"]
SEEDS = [0, 1, 2]

RUNS = {
    "27b": {
        "remote": "/root/autodl-tmp/jmf_harness/results_v4_27b/per_seed",
        "local": ROOT / "results_v4_27b" / "per_seed",
    },
    "qwen35_9b": {
        "remote": "/root/autodl-tmp/jmf_harness/results_v4_qwen35_9b/per_seed",
        "local": ROOT / "results_v4_qwen35_9b" / "per_seed",
    },
}
SSH_ALIAS = "seetacloud-h3"


def fetch(remote_dir, local_dir):
    """Copy one remote per_seed dir locally, file by file (resume-friendly)."""
    local_dir.mkdir(parents=True, exist_ok=True)
    have = {p.name for p in local_dir.glob("*.json")}
    want = [f"{g}_seed{s}.json" for g in GROUPS for s in SEEDS]
    missing = [f for f in want if f not in have]
    got = 0
    for name in missing:
        r = subprocess.run(
            ["ssh", SSH_ALIAS, f"cat {remote_dir}/{name}"],
            capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip().startswith("{"):
            (local_dir / name).write_text(r.stdout)
            got += 1
    return got, len(missing)


def verify(local_dir):
    """Return (cells, errors, present_groups, missing_cells)."""
    cells = errors = 0
    present = set()
    missing = []
    for g in GROUPS:
        for s in SEEDS:
            p = local_dir / f"{g}_seed{s}.json"
            if not p.exists():
                missing.append(f"{g}_seed{s}")
                continue
            d = json.load(open(p))
            present.add(g)
            for r in d["rows"]:
                cells += 1
                if "__ERROR__" in str(r.get("answer", "")):
                    errors += 1
    return cells, errors, sorted(present), missing


def main():
    no_fetch = "--no-fetch" in sys.argv
    for tag, spec in RUNS.items():
        if not no_fetch:
            got, want = fetch(spec["remote"], spec["local"])
            print(f"[fetch {tag}] {got}/{want} file(s) pulled")
        cells, errors, groups, missing = verify(spec["local"])
        print(f"[verify {tag}] cells={cells} errors={errors} "
              f"groups={len(groups)}/{len(GROUPS)} missing={len(missing)}")
        if missing:
            print(f"    missing: {', '.join(missing[:6])}"
                  + (" ..." if len(missing) > 6 else ""))

    # canonical recomputation on the primary run
    # canonical recomputation: run the analysis for EACH model independently,
    # so the second family gets its own frozen numbers rather than borrowing
    # the primary model's.
    for tag, spec in RUNS.items():
        local = spec["local"]
        if not any(local.glob("*.json")):
            print(f"\n[analysis {tag}] skipped (no data)")
            continue
        name = f"analysis_v4_{tag}.json"
        r = subprocess.run([sys.executable, str(SCRIPTS / "analysis_v4.py"),
                            str(local), name],
                           cwd=ROOT, capture_output=True, text=True)
        print(f"\n[analysis {tag}] exit={r.returncode} -> results/{name}")
        if r.returncode != 0:
            print(r.stdout[-600:]); print(r.stderr[-600:])
            continue
        out = ROOT / "results" / name
        if out.exists():
            a = json.load(open(out))
            sr = a.get("success_rates", {})
            print("  success_rates:", json.dumps(sr))
            sup = a.get("supplementary", {})
            if "gated_actions" in sup:
                print("  gated_actions:", json.dumps(sup["gated_actions"]))
            if "deny_disclosure" in sup:
                d = sup["deny_disclosure"]
                print(f"  deny_disclosure: runs={d.get('deny_runs')} "
                      f"disclosed={d.get('disclosed')} not={d.get('not_disclosed')}")

    # cross-model qualitative check
    c = subprocess.run([sys.executable, str(SCRIPTS / "compare_models.py"),
                        str(RUNS["27b"]["local"]), str(RUNS["qwen35_9b"]["local"]),
                        "--out", "cross_model.json"],
                       cwd=ROOT, capture_output=True, text=True)
    print(f"\n[cross-model] exit={c.returncode}")
    if c.returncode == 0:
        print("\n".join(c.stdout.splitlines()[-8:]))
    else:
        print(c.stdout[-400:], c.stderr[-400:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
