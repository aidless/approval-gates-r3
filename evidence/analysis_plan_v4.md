# v4 分析计划（TMLR 版）— 2026-09-14

> 本文件在 v4 数据全部落盘**之前**写定，用于防止事后挑选检验（HARKing）。
> 任何偏离本计划的检验必须在论文中显式标注为 exploratory。

## 0. 数据口径

- 数据：AWS Bedrock Agents Multi-Agent Collaboration Scenario Benchmark，**travel 域全部 30 个场景**（v3 只用 20）
- 网格：30 场景 × 5 组 × 3 种子 = **450 cells**
- 模型：**Qwen3.8-27B**（AWQ-INT4，vllm 0.27.1，`enable_thinking=false`），新一代骨干
- 配对单位：**(seed, scenario_idx)** —— 同种子同场景跨组配对
- **独立单位**：温度 0 下解码仍非确定（v3 已实测），种子仅改变处理顺序 →
  有效独立单位是 **30 个场景**，不是 90 个 (seed, scenario) 单元

## 1. 组别定义

| 组 | 协商门 | 记忆遗忘 | 安全机制 |
|---|---|---|---|
| `Full` | 1 轮/危险动作 | 开（capacity 2） | 显式门控 |
| `Abl-noForget` | 1 轮 | 关 | 显式门控 |
| `Abl-noNegot` | 无 | 开 | 无 |
| `Baseline-promptSafety` | 无 | 开 | **仅 system prompt 安全指令（0 额外调用）** |
| `Baseline-heavyAudit` | **3 轮**/危险动作 | 开 | 强化门控 |

危险动作白名单（6 个）：`bookflight, bookhotel, createreservation, bookairbnb, neworderevent, checkout`

## 2. 预注册假设

- **H1（覆盖率等价）**：`Baseline-promptSafety` 的 `unnegotiated_count` 与 `Full` 无差异。
  *预期为结构性零*（两组都可能恒为 0）——**若如此，应报告为「指标不可区分」而非「统计等价」**，
  并明示未做 equivalence test。
- **H2（可审计性差异，核心）**：`Full` 产生 `negotiation_log` 记录（每个危险动作 ≥1 条），
  `Baseline-promptSafety` 产生 **0** 条。→ 这是**设计属性**（机制不同），不是统计假设。
  度量：`audited_actions`（APPROVE+DENY 总数）、`runs_proposing_dangerous_actions`。
- **H3（任务成功）**：Full vs each ablation/baseline 的任务成功率无显著差异（exact McNemar）。
- **H4（成本）**：额外 LLM 调用数 `promptSafety = 0 < Full ≈ 1×危险动作 < heavyAudit ≈ 3×危险动作`。
  度量为**下界**（审计模型每动作可能多次调用）。
- **H5（记忆）**：记忆淘汰在 forgetting-enabled 条件下真实触发，但**无成功率收益**。

## 3. 统计方法（预先指定）

- 0/1 成功 → **exact McNemar**（配对，报 discordant b/c）
- 计数指标（`unnegotiated_count`, `negotiation_rounds`）→ **Wilcoxon signed-rank**
  （并列修正正态近似 + 精确 p，报告有效非零 n）
- 效应量 → **改用描述性计数差**（如 `24` vs 构造零、`20` vs `0`）。原因：稿件不再承诺 CLES/CI
  （R2 审稿指出承诺未兑现），且主口径为场景级计数，CLES 的 run 级口径与主口径不一致
- 多重比较 → **Holm–Bonferroni**，用**未舍入 p**，**仅在 run 级应用**；
  场景级用 exact sign test 并报其**最小可达 p**（informative 单位 ≤7 时任何校正都无法使其显著）
- **场景级分析为主要口径**（30 独立单位）；(seed, scenario) 级为敏感性分析
- 强制断言：`mean(pair_diff) == mean(Full) - mean(Abl)`

## 4. 主要对比家族（Holm 家族）

1. `mcnemar: Full vs Abl-noNegot`（成功）
2. `mcnemar: Full vs Baseline-promptSafety`（成功）
3. `wilcoxon: Full vs Abl-noNegot`（unnegotiated_count）
4. `wilcoxon: Full vs Baseline-promptSafety`（unnegotiated_count）
5. `wilcoxon: Full vs Abl-noForget`（negotiation_rounds）

镜像检验与被试全平局的退化检验剔除（去重家族）。同时报告保守全家族口径。

## 5. 禁止事项

- 不得把 `unnegotiated_count` 称为安全度量（基准无 unsafe ground-truth 标签）
- 不得声称「统计等价」（未做 equivalence test）
- 不得跨口径混用统计量（场景级 vs run 级）
- 不得用累计计数器求和（`memory_evictions` 是单调累计，取终值）

## 6. 偏离记录

| # | 偏离 | 原因 | 标注 |
|---|---|---|---|
| D1 | 增加第二骨干 **Qwen3.5-9B**（本计划只预注册 27B） | 审稿意见要求 ≥2 模型族 | 9B 全部结果标为 **exploratory replication** |
| D2 | 9B 的任务成功对比采用**场景级符号检验**（计划预注册 exact McNemar） | 计划 §3 已定场景为独立单位；McNemar 的 90 对是伪重复 | 标为 exploratory，并在正文同时报 run 级 |
| D3 | 覆盖率的门控-无门对比改为**描述性**陈述（原计划含 Wilcoxon） | R1 审稿指出门控臂该字段为硬编码常量，检验无意义 | 已改为描述性 |
| D4 | 可审计性对比改为**描述性**（原计划含显著性） | 计划 §2 本已声明 H2 是设计属性 | 已在正文声明为 design property |
| D5 | Holm 家族实现为**去重 5 检验**（剔除镜像与全平局退化检验） | 剔除镜像检验与全平局退化检验 | 同时报保守 k=12 口径 |
