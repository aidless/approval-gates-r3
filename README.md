# Approval Gates R3 — local manuscript and evidence package

## Overview（面试叙事）

**解决什么问题**：agent 在执行用户授权时，如何区分「用户真正授权的副作用」与「agent 未经授权自行发起的副作用」——这是 agentic 系统从 demo 走向可审计执行的核心缺口。R3 把这个问题做成**可离线复现的构造矩阵**，而不是依赖昂贵在线推理的一次性故事。

**为什么重要**：授权边界（authorization boundary）是 agentic 安全的最小可验证单元；没有它，事后审计无法区分「执行了用户意图」与「agent 自作主张」。

**我用了什么方法**：构造 540 个本地 effect 单元（`evaluation`/`clean` 等分区 × 守卫策略 `allow_all`/`deny_all`/`exact_precheck`/`name_only`/`local_execution_bound`/`native_agt`/`pre_target`/`pre_value`/`replay`/`policy_change` 等 × 基础目标），每个单元记录 effect 元组（authorized/unauthorized）、integrity 错误、admitted attempts；配套 23 个工程控件（instrument controls）作机制自检。全程**零模型调用、零网络、零付费服务**（native AGT 组件是 pinned 官方 MIT 源码）。

**结果如何**：离线复算 `make_descriptive_tables.py` 校验 54 文件 / 1620 行数据集并重建四份描述性输出（字节级一致）；构造矩阵的 aggregate agreement 记录在 `offline-reproduction.json`。**注意**：结果证明的是「机制在构造输入上按预期动作」，不是「真实场景的泛化安全/效用」——见下方 Limits。

**边界在哪**：无人工同行评审、无泛化安全/效用认证、无自然失败率声明、无认证的受试者同意、无过期/竞态覆盖、无新的绑定方法。详见「Limits and historical files」。

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

CI also runs `pytest -q tests` to prove that this offline recomputation succeeds and
recreates the four committed descriptive outputs byte-for-byte. The check does
not rerun model episodes or make network calls. 本地等价复算：

```bash
python3 -m pytest tests/ -q     # 期望：2 passed
```

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
