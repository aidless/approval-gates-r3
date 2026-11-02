# PREREG — approval-gates-r3 (R3 · 授权边界测量审计)

> 预注册规格：本文件声明 **R3 稿件在冻结时点可检验的研究假设、评测方案、
> 成功标准与明确边界**。内容全部对应仓库真实实现与真实证据
> （`paper/main.tex`、`evidence/protocol.md`、`CLAIM_LEDGER.md`、
> `scripts/make_descriptive_tables.py`、540 格构造矩阵、23 个仪器控件、
> 108 个本地模型场景），不含虚构数字或未实现能力。
>
> 状态：**有限范围测量审计，非泛化安全/效用认证**。独立复审评分 6.2/10
> 未达 8 分目标；无 arXiv 提交或公开工件 URL 声称。

## 1. 研究问题

agent 在执行用户授权时，如何区分「用户真正授权的副作用」与「agent 未经
授权自行发起的副作用」？这是 agentic 系统从 demo 走向可审计执行的核心
缺口。R3 把这个问题做成**可离线复现的构造矩阵**，而不是依赖昂贵在线
推理的一次性故事。核心问题：授权边界（authorization boundary）是
agentic 安全的最小可验证单元；没有它，事后审计无法区分「执行了用户
意图」与「agent 自作主张」。

## 2. 假设（H1–H3，全部可证伪）

- **H1（代理计数混淆）**：一个「未授权动作数 = 0」的控制可能来自四种不同
  机制——真正审查动作、在审查前抑制、全拒绝、或未能取得有效计划。仅用一个
  计数器会混淆「实现性质」与「agent 的有用性质」。
- **H2（名称匹配不构成授权）**：把动作名匹配到审批日志**不**建立授权关系；
  名称/日志代理会在 `name_only` 与 `exact_precheck` 控件中保持正计数，而它们
  分别漏过 **63 和 45** 次未授权效应。
- **H3（强基线不可包装为新方法）**：固定官方版本的 native AGT 组件与本地
  绑定控制均为 **0 未授权效应**并完成 **9/9** 干净授权目标；`deny_all` 有零
  干净效用。因此已有绑定方法是强基线，**不能**包装为新方法。

## 3. 评测方案

- **构造矩阵**：540 个本地 effect 单元 = 9 个评估目标 × 10 个状态 × 6 种
  控制（`evaluation`/`clean` 等分区 × 守卫策略 `allow_all`/`deny_all`/
  `exact_precheck`/`name_only`/`local_execution_bound`/`native_agt`/`pre_target`/
  `pre_value`/`replay`/`policy_change` 等 × 基础目标）。每个单元记录 effect
  元组（authorized/unauthorized）、integrity 错误、admitted attempts。
- **仪器控件**：23 个工程控件（instrument controls）作机制自检，非效用试验。
- **离线复算**：`make_descriptive_tables.py` 校验 54 文件 / 1620 行数据集并
  重建四份描述性输出（字节级一致）；`offline-reproduction.json` 记录构造矩阵
  的 aggregate agreement。**全程零模型调用、零网络、零付费服务**（native AGT
  组件是 pinned 官方 MIT 源码）。
- **本地模型面板**：108 个字节校验的本地模型场景（qwen3:8b，温度 0）。

## 4. 成功标准

1. `make_descriptive_tables.py` 离线重算 54 文件 / 1620 行，重建四份描述性
   输出字节级一致（CI 以 `pytest -q tests` 证明，期望 2 passed）。
2. 540 格构造矩阵重跑 aggregate agreement 完全一致（`offline-reproduction.json`）。
3. 23 个仪器控件通过（工程检查）；native AGT 原组件 31 个测试通过。
4. 108 个本地模型场景完整记录：放行组 15 次未授权效应均在待批准场景，
   名称检查与绑定检查均 0——此面板未拉开差距，**如实披露**，不宣称绑定更优。

## 5. 明确边界（不证明什么）

- **不证明真实场景的泛化安全/效用**：结果证明的是「机制在构造输入上按预期
  动作」，不是自然失败分布或生产级安全认证。
- **不证明授权正确性/多智能体执行安全**：规划模拟器不实例化 benchmark 的
  专业 agent 或执行工具；其记录用于审计测量，不验证 booking/payment/
  授权正确性。
- **不证明完整的模型比较**：免费模型面板原计划 108 场景，69 个有可观察输出、
  4 个传输失败、35 个服务停止后未运行——缺失**不得**算成安全或成功。
- **不证明恢复能力**：失败场景中合规效应 3/9 与真正收到主操作失败反馈后
  恢复 0/9 分开；6 个主操作实际失败均未恢复。
- **不证明新绑定方法**：native AGT 与本地绑定是强基线；已有绑定方法不能
  包装为新方法。
- **不证明**：无人工同行评审、无泛化安全/效用认证、无自然失败率声明、无
  认证的受试者同意、无过期/竞态覆盖、无新的绑定方法。

## 6. 数据与复现

- 复现（Python 3.11+）：
  ```bash
  python3 scripts/make_descriptive_tables.py
  python3 scripts/make_execution_supplement.py --study evidence/supplement/workspace/approval/supplement-20261014
  python3 -m pytest tests/ -q            # 期望 2 passed
  python3 evidence/supplement/workspace/approval/supplement-20261014/audit_core.py /tmp/approval-r3-fresh-matrix --partition evaluation
  python3 evidence/supplement/workspace/approval/supplement-20261014/verify_effects.py /tmp/approval-r3-fresh-matrix
  ```
- 重跑模型场景不在离线指令内，需另行配置资源；模型权重/运行时不再分发，
  字节校验的本地模型与运行时哈希已归档。
