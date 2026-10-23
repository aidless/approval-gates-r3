# Literature Review (v4 / TMLR)

> 纪律：每条引用**一手核验**（`web_fetch` abs 页，号-题-作者-许可四项比对），不采信记忆中的 arXiv id（AGENTS.md 规则 5）。
> 核验日期：2026-09-14。核验方式：逐条 `https://arxiv.org/abs/<id>` HTTP 200 + 标题/作者比对。

## 1. 检索日志

| 查询 | 通道 | 结果 |
|---|---|---|
| `LLM agent tool use safety guardrail approval gate benchmark 2025 arXiv` | web_search | 8 源 |
| `multi-agent tool execution confirmation human-in-the-loop safety evaluation arXiv` | web_search | 8 源 |
| `TS-Bench tool invocation safety LLM agents arXiv` | web_search | 8 源 |
| `GuardAgent guardrail agent ICML 2025 arXiv knowledge-enabled reasoning` | web_search | 8 源 |

## 2. 核验表（一手）

| key | arXiv | 标题 | 作者（首/末） | 年 | 许可 | 核验 |
|---|---|---|---|---|---|---|
| `shu2024effective` | 2412.05449 | Towards Effective GenAI Multi-Agent Collaboration: Design and Evaluation for Enterprise Applications | Shu, R. … Zhang, Y. | 2024 | — | ✅ 号-题-作者一致 |
| `zhang2026guard` | 2608.27009 | The Guard That Cried Wolf: How Scary Words Make Agent Guardrails Refuse Legitimate Actions | Zhang, Y.; Xie, Y.; Chen, K. | 2026-08-27 | CC BY-NC-SA 4.0 | ✅ |
| `mou2026toolsafe` | 2601.10156 | ToolSafe: Enhancing Tool Invocation Safety of LLM-based agents via Proactive Step-level Guardrail and Feedback | Mou, Y. … Shao, J. | 2026-01-15 | CC BY 4.0 | ✅ |
| `xiang2025guardagent` | 2406.09187 | GuardAgent: Safeguard LLM Agents by a Guard Agent via Knowledge-Enabled Reasoning | Xiang, Z. … Li, B. | 2024-06 (v3 2025-05) | CC BY 4.0 | ✅ ICML 2025 |

数据来源（非 arXiv，已在 `evidence/dataset/LICENSE_PROVENANCE.md` 核验）：
AWS Bedrock Agents Multi-Agent Collaboration Scenario Benchmark（数据 CC-BY-4.0；脚手架代码 MIT-0）。

## 3. 方法族表

| 族 | 代表工作 | 安全信号来源 | 评估标签 | 成本 |
|---|---|---|---|---|
| **Prompt-level policy** | 通用做法（被本文的 `Baseline-promptSafety` 具体化） | system prompt 指令 | 无独立标签 | **0 额外调用** |
| **Explicit per-action guardrail** | GuardAgent (`xiang2025guardagent`) | 动态生成 guardrail code + 知识检索 | 专用基准（EICU-AC / Mind2Web-SC，有策略标签） | 每动作 ≥1 次 LLM 调用 |
| **Step-level guard model** | TS-Guard / TS-Bench (`mou2026toolsafe`) | 多任务 RL 训练的小模型 | TS-Bench（step-level 安全标签） | 每次工具调用一次 guard 推理 |
| **Over-safety audit** | Cautious Bench (`zhang2026guard`) | 由授权策略机械导出标签 | 756 决定性 benign/twin 对 | 离线基准 |
| **本文（测量式）** | — | 显式协商门 **或** prompt 策略 | **无 unsafe 标签**（基准自带断言只判任务完成） | 门控 1–3 轮/动作；prompt 0 |

## 4. 可证伪的 GAP 陈述

- **G1（可证伪）**：现有 guardrail 工作多以**有安全标签的专用基准**报告检测准确率
  （GuardAgent 报 98%/83%；TS-Bench 报有害调用降低 65%）；**在企业任务基准（自带断言只判任务完成、无 unsafe 标签）上，显式门控相对零成本 prompt 策略的边际价值未被测量**。
  证伪条件：若存在一篇工作在同一类企业任务基准上同时报告（i）门控的额外调用成本与（ii）与 prompt-only 的覆盖/成功率对比，则本 GAP 不成立。
- **G2（可证伪）**：现有工作把"安全"作为单一标量（准确率 / 有害率）报告；
  **很少有工作把"覆盖率"与"可审计性"拆开**——即两个机制可以给出相同的未协商动作计数，却给出完全不同的审计记录量。
  证伪条件：若某工作已明确区分并分别测量这两者，则 GAP 不成立。
- **G3（可证伪）**：`zhang2026guard` 已论证"safe vs unsafe 是授权策略的选择，不由动作本身固定"——
  这**支持**本文"无 unsafe 标签时不得声称更安全"的限制声明；若该论证被推翻，本文的限制表述需相应调整。

## 5. 基线池（本文可运行 vs 不可运行）

**本文实际运行（5 组，全部可复现）**：
1. `Full` — 1 轮/危险动作的显式协商门
2. `Abl-noForget` — 同门，关闭记忆遗忘
3. `Abl-noNegot` — 无门
4. `Baseline-promptSafety` — 仅 prompt 策略（**0 额外调用**）
5. `Baseline-heavyAudit` — 3 轮/危险动作（强化门控）

**不可运行（外部，需实现 + 安全标签，本文明确不评估）**：
- GuardAgent（`xiang2025guardagent`）：需知识库 + guardrail code 生成，且其基准（EICU-AC / Mind2Web-SC）非本文任务集
- TS-Guard（`mou2026toolsafe`）：需 RL 训练与 TS-Bench 标签
- CoSkill / Compact-Memory / CONTINUITY（v3 曾计划的三基线）：无公开可复现实现 → H1 inconclusive

## 6. Novelty 候选声明（每条挂引用）

- **N1**：据我们所知，**首次**在同一企业多智能体工具执行基准上，把显式审批门与**零成本 prompt 安全**做
  同网格、同统计口径的成本-覆盖-可审计性三方对照。
  （对照系：`xiang2025guardagent`、`mou2026toolsafe` 均不报告零成本 prompt 对照。）
- **N2**：把**覆盖率与可审计性分离**作为可测量对照（相同 `unnegotiated` 计数、不同 `audited_actions`）。
  （对照系：现有工作报告单一安全标量。）
- **N3**：在**无 unsafe ground-truth 标签**的公共企业基准上给出诚实的 null/薄基础测量，
  并显式声明"覆盖 ≠ 安全"（受 `zhang2026guard` 的授权策略论证支撑）。

## 7. 新鲜度

- 检索日期：2026-09-14。
- 最相关竞品均为 2026 年（`zhang2026guard` 2026-08、`mou2026toolsafe` 2026-01）；
  Phase 5 前需按 `check_literature_freshness.py --max-age-days 30` 重跑增量门。
