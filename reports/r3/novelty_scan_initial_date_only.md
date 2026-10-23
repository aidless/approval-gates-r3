# Novelty prescan — novelty claim 联网预检索

- claims_file: `/home/liuzewen/arxiv-publication/papers/approval-gates-r3/novelty_claims.txt`
- n_claims: 1
- arxiv_since: 2026-10-14（增量扫描下界 = 立项日期）
- scan_date: 2026-10-14
- per_claim_top: 3
- min_relevance: 0.55（候选池 IDF 加权 · ≥2 个有区分度的词命中；分数>1 属正常：标题命中加权 2x）

## 逐条检索留痕

| # | claim | 检索式 | 检索日期 | 命中/库内命中 | 最相关条目 |
|---|---|---|---|---|---|
| C1 | Our contribution is a bounded descriptive case study with four parts:  | `(all:accounting AND all:actions) AND submittedDate:[202610140000 TO 999912312359]` | 2026-10-14 | 0 / 库内 0 | — |

## 汇总

- 检索日期: 2026-10-14
- 声称条数: 1
- 成功检索: 1
- 检索失败: 0
- 命中重叠条目总数: 0
- 检索式有效性: 见上表「命中/库内命中」——库内命中过大（万级）说明检索式退化成全库扫描，**这不是干净的检索**，需改检索式

## 命中详情

### C1 — Our contribution is a bounded descriptive case study with four parts: a transparent accounting of retained names and review records; a concrete audit of assertion and refusal-marker measurements; and a separation between record-level recomputation and experimental reproducibility; and a separate local execution audit with a pinned third-party component and model-generated actions.

- 检索式: `(all:accounting AND all:actions) AND submittedDate:[202610140000 TO 999912312359]`
- 检索日期: 2026-10-14　检索式总命中: 0　取回候选: 0　判为重叠: 0

- **阶梯全部层级库内命中均为 0：这条 claim 没被真正检索到。** 请手工构造更宽的检索式（如 `all:"短语"`）重跑， 在补上有效检索之前，「未发现重叠」**不构成新颖性证据**。

