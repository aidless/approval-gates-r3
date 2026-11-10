# Approval Gates R3 — local manuscript and evidence package

[![CI](https://github.com/aidless/approval-gates-r3/actions/workflows/static-checks.yml/badge.svg)](https://github.com/aidless/approval-gates-r3/actions/workflows/static-checks.yml)

Current manuscript: paper/main.pdf. Current author-side round report: ROUND_R3.md. Independent retrospective AI review: reviews/approval-r3-independent-r0.md. Review score 6.2/10 is uncalibrated and below the requested target; no arXiv submission or public artifact URL is claimed.

> **Repo scale:** 11,688 tracked files (evidence 7,806 + reports 3,730). Clone with `git clone --depth 1`; start from ROUND_R3.md, not from the directory tree.

The retained 54-file / 1,620-cell travel-planning dataset and the new 540-cell constructed local effect matrix are separate studies. E05 retains 108 local model episodes; E04 retains all 108 planned rows including 4 transport-error and 35 endpoint-stopped records. Original attempts, freezes, endpoint failures and abandoned candidate development remain in the supplement workspace.

## Directory guide

11,688 tracked files, counted live with `git ls-files | awk -F/ '{print $1}' | sort | uniq -c`
on 2026-11-10 (root files, `tests/` and `.github/` add 21):

| Files | Path | Contents |
|---|---|---|
| 7,806 | `evidence/` | 7,790 in `evidence/supplement/` (workspace archives incl. `supplement-20261014`), 8 in `evidence/dataset/` (the 54-file travel-planning dataset) |
| 3,730 | `reports/` | 3,683 in `reports/r3/` — per-episode reports, generation manifests |
| 28 | `results_v5_qwen35_9b/` | Qwen3.5-9B arm: 27 `per_seed/` JSONs + aggregate |
| 28 | `results_v5_27b/` | 27B arm: 27 `per_seed/` JSONs + aggregate |
| 22 | `results/` | v1 line: 9 `per_seed/` + aggregates |
| 22 | `scripts/` | table builders, harnesses (v4/v5), `verify_claim_ledger.py`, readiness checks |
| 18 | `paper/` | `main.pdf`, TeX sources, 5 `tables/` |
| 15 | `results_v4_27b/` | v4 arm: 15 `per_seed/` JSONs |
| 1 each | root | `ROUND_R3.md` (start here), `README_R3.md`, `CLAIM_LEDGER.md`, `EXPERIMENT_SUPPLEMENT.md`, `LITERATURE_REVIEW.md`, `novelty_claims.txt`, `evidence_manifest.json`, `requirements.txt` |
| 1 | `tests/test_offline_recompute.py` | the offline byte-for-byte recompute CI gate |

## Recompute without a model or network

From this package root, use Python 3.11+:

```bash
python3 scripts/make_descriptive_tables.py
python3 scripts/make_execution_supplement.py --study evidence/supplement/workspace/approval/supplement-20261014
python3 evidence/supplement/workspace/approval/supplement-20261014/standalone_record_check.py --help
```

The R3 generator includes fallback R2 authoring inputs so it does not require an external R2 checkout. Rebuilding manifests records current absolute source paths and times; compare numeric summaries and table bytes, not incidental generation-manifest or UUID/time bytes.

CI also runs `pytest -q tests` to prove that this offline recomputation succeeds and
recreates the four committed descriptive outputs byte-for-byte. The check does
not rerun model episodes or make network calls.

## Execute a fresh local constructed matrix

Choose a new nonexistent output directory:

```bash
python3 evidence/supplement/workspace/approval/supplement-20261014/audit_core.py /tmp/approval-r3-fresh-matrix --partition evaluation
python3 evidence/supplement/workspace/approval/supplement-20261014/verify_effects.py /tmp/approval-r3-fresh-matrix
```

The packaged native AGT component is the pinned official MIT-licensed source. No inference, external message delivery or paid service is used by this offline matrix. The archived offline-reproduction.json records exact aggregate agreement for a fresh 540-cell run. Upstream component tests additionally require pytest; the archived test log reports 31 passes. The 23 instrument controls are engineering checks, not efficacy trials.

## Rebuild the paper

A TeX installation with the supplied style dependencies and BibTeX is needed. In paper/, run pdflatex main.tex, bibtex main, then pdflatex main.tex twice. Current PDF build has no undefined citations/references or overfull boxes. This is an identified preprint; the TMLR anonymity checker is not an arXiv acceptance test.

## Limits and historical files

Historical process documents (including evidence/protocol.md and LITERATURE_REVIEW.md) are retained provenance of older variants. Their old hypotheses, claims and completed/blocking labels are not adopted as R3 scientific outcomes. Current scope is in main.tex, execution_r3.tex, PROTOCOL_R0–R4, CLAIM_LEDGER.md and ROUND_R3.md. Strict reactive recovery was a post-review descriptive trace audit. No human peer review, generalized safety/utility, natural failure prevalence, authenticated human consent, expiry/race coverage, or new binding method is certified.

Model weights/runtime are not redistributed. The byte-verified local model and runtime hashes and original serving properties are archived; the remote endpoint is identified only by its serving label. Regenerating upstream output is not guaranteed. Re-running model episodes is not part of the offline instructions and requires separately configured resources. Author code/publication licenses remain author decisions before public release; upstream licenses are preserved. This bundle is prepared locally for review and reproducibility, not uploaded.
