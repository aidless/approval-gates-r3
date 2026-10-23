# 实验协议 protocol.md — Joint Memory-Forgetting + Lightweight Security Negotiation（正式版）

> v1.0，2026-09-13。取代试点 v0-pilot 合成声明。本文件为冻结预注册；修改需新 ROUND 并更新 evidence_manifest。

## 研究问题 / 假设（可证伪）

- **H1**：完整框架（记忆遗忘联合 + 轻量安全协商）在多智能体协作任务集上的任务成功率显著高于三基线（CoSkill / Compact-Memory / CONTINUITY）。配对单位=同场景同配置，exact McNemar，Holm 校正。
- **H2**：去遗忘消融（仅协商）与去协商消融（仅记忆遗忘）在记忆命中 / 安全违规率上显著劣于完整框架（Wilcoxon + CLES，bootstrap 95% CI）。
- **H3**：轻量协商开销（轮次）显著低于完整安全基线，同时安全违规率不显著上升（非劣效界 Δ=0.05）。

## 实验设计（组别 / 配置 / 消融）— v3 诚实版

- **Full**：记忆池（容量 2，LFU 遗忘）+ 协商门（危险动作前 APPROVE/DENY）
- **Abl-noForget**：仅协商门（记忆只增不忘）
- **Abl-noNegot**：仅记忆遗忘（无协商门，危险动作直通执行）
- 基线（CoSkill / Compact-Memory / CONTINUITY）：闭源不可跑，仅动机引用，不进统计
- 种子：3（0,1,2），温度 0，逐种子独立落盘 `results_qwen3_8b_v3/per_seed/{group}_seed{n}.json`
- 记忆遗忘：共享记忆池容量上限 **2**，超限淘汰命中率最低条目（LFU）；`memory_evictions` 计数落盘证明遗忘真实触发
- 协商门：危险动作（6 个资金承诺类）执行前，由 1 个审计 agent APPROVE/DENY，最多 2 轮；每次判定落盘 `negotiation_log`

## 诚实度量语义（v3，对抗审稿 R1 修正）

- **`unnegotiated_count`**：绕过协商门直接执行的危险动作数。这是**门控覆盖率**指标（门是否触发），
  **不是安全度量**——benchmark 无「该动作不安全」的 ground-truth 标签。
- 协商组的 unnegotiated=0 是**定义性结果**（每个危险动作都经门），非独立安全测量。
- 被拒动作从最终动作集移除，且 **answer 会据此重新生成**（不宣称被拒动作已完成）。

## 数据集（一手来源，正式）

- AWS Bedrock Agents Multi-Agent Collaboration Scenario Benchmark（travel 领域）
- GitHub + arXiv:2412.05449；代码 MIT-0，数据集 CC-BY-4.0
- 正式取 `scenarios_30.json` index 0..19 共 20 场景；每场景含 scenario / input_problem / assertions
- 无人类受试者/IRB

## 模型与环境

- 主模型：qwen3:8b（`think=false`，`num_ctx=4096`，`num_gpu=99` 全 GPU），温度 0
- 运行环境：seetacloud-h3（autoDL，RTX 3090 48G，共享 GPU）
- 判定程序化：agent 断言=工具执行日志；user 断言=关键词覆盖率≥0.5（启发式，披露为 limitation）；行为语义断言=unchecked

## 分析计划（检验、效应量、CI、多重比较校正）

- 任务级 0/1 → exact McNemar（净胜 + ties），配对单位=同 seed 同场景 idx
- 连续指标（v3 更名为 `unnegotiated_count`；旧名 `violations` 为其别名 / negotiation_rounds）→ Wilcoxon + CLES + paired bootstrap 95% CI（B=2000）
- Holm 校正用未舍入 p；`mean(pair_diff) == 组间均值差` assert 强制
- 唯一脚本 `scripts/analysis.py` 只读重算，不合成数据

## v3 修订记录（2026-09-14，对抗审稿 R1-R3 后）

- **指标改名**：`violations`（v1 旧名）→ `unnegotiated_count`（v3），语义为"绕过协商门的危险动作数 =
  门控覆盖率"，**非安全度量**（基准无 unsafe ground-truth）
- **Holm 家族口径**：正文主用 **k=4 去重家族**（2 McNemar + unnegotiated Full-vs-noNegot +
  negotiation-rounds Full-vs-noForget；剔除镜像对与全平局退化检验），k=6 全家族作为保守口径并列报告
- **场景级分析**：跨 seed 折叠到 20 场景单位（Wilcoxon + exact sign test）为 **post-hoc 敏感性分析**，
  **非预注册**（预注册冻结 (seed, scenario) 为配对单位）；因温度 0 下解码仍非确定、且种子仅为处理顺序，
  正文以场景级为更保守/更合适的口径
- **记忆容量**：6 → 2（强制 eviction 真实触发）；`memory_evictions` 为 seed 内累计计数器（终值 = 总淘汰数）

## 样本量口径

- 180 cells = 20 场景 × 3 组 × 3 种子；McNemar 配对 60 pairs（20 场景 × 3 种子）
- 摘要/正文/表格/caption 统一此口径

## 排除标准

- 环境崩溃/超时轮次计入分母并单独列失败分类（E053），不剔除不利样本

## 数据披露

- 正式数据 synthetic=false（真实外部基准）；试点 v0-pilot 合成数据已弃用，仅作历史