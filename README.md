# Approval Gates R3 — local manuscript and evidence package

Current manuscript: paper/main.pdf. Current author-side round report: ROUND_R3.md. Independent retrospective AI review: reviews/approval-r3-independent-r0.md. Review score 6.2/10 is uncalibrated and below the requested target; no arXiv submission or public artifact URL is claimed.

The retained 54-file / 1,620-cell travel-planning dataset and the new 540-cell constructed local effect matrix are separate studies. E05 retains 108 local model episodes; E04 retains all 108 planned rows including 4 transport-error and 35 endpoint-stopped records. Original attempts, freezes, endpoint failures and abandoned candidate development remain in the supplement workspace.

## Recompute without a model or network

From this package root, use Python 3.11+:

```bash
python3 scripts/make_descriptive_tables.py
python3 scripts/make_execution_supplement.py --study evidence/supplement/workspace/approval/supplement-20261014
python3 evidence/supplement/workspace/approval/supplement-20261014/standalone_record_check.py --help
```

The R3 generator includes fallback R2 authoring inputs so it does not require an external R2 checkout. Rebuilding manifests records current absolute source paths and times; compare numeric summaries and table bytes, not incidental generation-manifest or UUID/time bytes.

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
