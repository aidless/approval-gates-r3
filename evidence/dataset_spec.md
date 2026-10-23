# 数据集规格 dataset_spec.md — 正式版（D0 闭合，2026-09-12）

> 本文件是正式任务集的一手来源（first-hand source），替换试点 v0-pilot 的合成声明。
> 数据来自 AWS Bedrock Agents 多智能体协作场景基准，可溯源、有许可、可下载。

## 一手来源

- 名称：AWS Bedrock Agents Multi-Agent Collaboration Scenario Benchmark
- GitHub: https://github.com/aws-samples/multiagent-collab-scenario-benchmark（commit: main，2024）
- 技术报告（引用对象）: arXiv:2412.05449 "Towards Effective GenAI Multi-Agent Collaboration: Design and Evaluation for Enterprise Applications"
- 许可：代码 MIT-0（LICENSE）；数据集 CC-BY-4.0（DATA_LICENSE）
- 本目录 copies：`evidence/dataset/{travel,mortgage,software}/`（本机下载，未改动）

## 任务集定义（正式）

- 领域：**travel**（旅行规划，10 个 agent；weather/location/car/flight/hotel/budget/restaurant/expert/airbnb）
- 选定理由：mortgage/software 领域断言多为「越权拒绝」「行为描述」等不可程序化判定的语义断言；travel 的工具执行断言最多且协作链路最清晰，可程序化判定
- 场景数：正式取 `scenarios_30.json` 的 **index 0..19 共 20 场景**（确定性选取，明文记录）
- 每场景字段：`scenario`（目标+背景）、`input_problem`（用户输入）、`assertions`（成功判据列表）
- 成功判据：`assertions` 全满足 = 任务成功（1），否则失败（0）
  - `agent:` 命名已知工具 action 的断言 = 工具调用日志程序化判定
  - `agent:` 未命名任何已知工具（行为语义断言，如「total budget is estimated」）= 记录为 unchecked，不参与成功/失败（透明披露）
  - `user:` 断言 = 生成 answer 的关键词覆盖率 ≥0.5 启发式判定（弱，披露为 limitation，无 LLM judge）
- 多 agent 定义：`agents.json`（agent_id / agent_instruction / tools / reachable_agents 触发条件与 context_sharing）

## 组别（冻结于 protocol.md）

- Full：记忆-遗忘联合 + 轻量安全协商
- Abl-noForget：仅协商（记忆只增不忘）
- Abl-noNegot：仅记忆-遗忘（无协商，直通执行）
- Baselines（CoSkill / Compact-Memory / CONTINUITY）：闭源不可跑，仅动机引用，不进统计

## 方法语义（v3 诚实版，对抗审稿 R1 后修正）

- 记忆遗忘：共享记忆池容量上限 **2**，超限淘汰「使用次数最低」条目（LFU）；`memory_evictions` 计数落盘证明遗忘触发
- 协商门：agent 执行「危险动作」前，由 1 个审计 agent APPROVE/DENY，最多 2 轮，判定落盘
- **`unnegotiated_count`**：绕过门直通执行的危险动作数 = **门控覆盖率**指标，**非安全度量**（基准无 unsafe ground-truth）
- **危险动作定义**（6 个资金承诺类，收窄后；去掉非承诺的 selectseat/cancelticket/additem）：
  - flight_agent → `bookflight`（购票）
  - hotel_agent → `bookhotel`（酒店预订）
  - car_rental_agent → `createreservation`（租车预订）
  - airbnb_agent → `bookairbnb`（民宿预订）
  - local_expert_agent → `neworderevent`（活动订票）
  - restaurant_agent → `checkout`（点餐付款）

## 运行口径

- 种子：3（0,1,2），温度 0，逐种子独立落盘 `results_qwen3_8b_v3/per_seed/{group}_seed{n}.json`
- 配对单位：同场景同配置；McNemar 60 pairs（20 场景 × 3 种子）
- 模型：qwen3:8b（think=false，num_ctx=4096，num_gpu=99 全 GPU）
- synthetic 标记：**false**（真实外部数据，写入 config 快照）
- **伪重复披露**：温度 0 下 3 种子仅改场景处理顺序 + 共享记忆，3 种子=3 排序非 3 次独立复现；有效独立单位更接近 20 场景（在正文披露）

## 环境

- 云端：seetacloud-h3（autoDL，RTX 3090 48GB 共享），ollama 实际服务 tag `qwen3:8b-c4k`（= `qwen3:8b` 重新打 tag 以固定 num_ctx=4096；think=false，num_gpu=99 全 GPU）；qwen2.5:7b 与 qwen2.5:1.5b 仅历史（旧 harness 修订用，非 v3 主张口径）
- 本机：Python 3.12（仅数据落盘与重算，不跑模型）

## 合规

- 无人类受试者/IRB；数据为 AWS 公开基准，CC-BY-4.0 允许注明出处后复用
- 引用必须包含 arXiv:2412.05449 与 GitHub 出处（见一手来源）