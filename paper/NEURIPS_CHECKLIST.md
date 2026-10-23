# NeurIPS 2025 Paper Checklist

稿件：A Negotiation Gate for Multi-Agent Tool Execution: Cost and Null Effects on a Travel Benchmark
（本文件为交付件记录；提交时按官方表单逐项填写。）

## 1. Claims

- **Q: Do the main claims accurately reflect the paper's contributions and scope?**
  Yes. 三项发现均按证据强度限定：成功率 null（McNemar p=1.0，明写 low power → inconclusive）、
  门控覆盖为**设计不变量**且校正后不显著（场景级 p=0.102，最小可达双侧 p=0.25）、
  遗忘真实触发但无成功率收益。无 "first/best/SOTA" 类措辞。
- **Q: Does the paper discuss the limitations of the work?**
  Yes，§Limitations 逐条列出：低成功率与低功效、覆盖结论仅基于 3/20 场景、6 动作中 3 个从未触发、
  自审配置、未测误拒/误放、静默拒绝无升级路径、三基线不可复现（H1 未评估）、
  关键词启发式评分、H2/H3 预注册但未执行、种子非独立且温度 0 仍非确定。

## 2. Theory / Assumptions

- 本工作为实证测量，无理论结果；无定理或证明。

## 3. Experiments & Reproducibility

- **数据**：AWS Bedrock Agents Multi-Agent Collaboration Scenario Benchmark（travel 领域），
  公开、有许可（数据 CC-BY-4.0；脚手架代码 MIT-0）。出处与验号见 `evidence/dataset/LICENSE_PROVENANCE.md`，
  引用见 `paper/main.bib`（`shu2024effective` + `awsbench2024`）。
- **配置**：`scripts/harness.py` 内嵌全部配置（模型、温度、种子、记忆容量、危险动作白名单、采样参数），
  逐种子落盘含完整 config 快照。模型 tag `qwen3:8b-c4k`（= `qwen3:8b` 重打 tag 固定 num_ctx=4096）。
- **统计**：`scripts/analysis.py` 为唯一重算脚本；exact McNemar + Wilcoxon + CLES + bootstrap CI + Holm；
  `mean(pair_diff) = mean(X) - mean(Y)` 断言强制。
- **复算范围**：论文正文全部数字可由 `results_qwen3_8b_v3/per_seed/*.json`（9 文件 / 180 cells）独立重算。
- **对之前结果的更正**：投稿前已撤回旧口径（9 动作危险集、capacity 6、子串匹配、未重生成 answer）下的
  「违规率 38.3%→0，Holm p=0.0017」等结论，相关 v2 artifact 在 manifest 中标注为 historical。

## 4. Open access to data and code

- 数据：公开（GitHub，CC-BY-4.0）。
- 代码：harness + analysis 脚本随论文交付（`scripts/`）；除数据集与本地模型外无外部依赖。

## 5. Compute

- 单张 RTX 3090（48GB，**共享**），推理仅用 ollama。
- 180 cells 约 2 小时（含共享 GPU 排队等待）；无训练。

## 6. Ethics / Broader Impact

- §Broader Impact 讨论双向风险：**过度信任**（把「0 未协商动作」误读为「安全已解决」）与
  **过度拦截**（门拒绝率 45.5%，全在 flight booking，且被拒动作静默丢弃、无人工升级）。
- 明确声明本工作不提供真实世界安全保证。

## 7. Human subjects / Crowdsourcing

- 无人类受试者；数据集为人工设计的企业场景（authors' personas），不含真实 PII；无需 IRB。

## 8. Safeguards

- 涉及安全关键决策的 LLM 系统：论文明确说明门是已知模式、审计者与执行者同模型为非独立控制，
  不应在生产中用无独立校准审计者部署。

## 9. Licenses for existing assets

- 见 `evidence/dataset/LICENSE_PROVENANCE.md`（一手许可声明 + arXiv 验号记录）。
- 模型：`qwen3:8b`（ollama tag），遵循其上游许可。

## 10. Declaration of LLM usage

- 论文文字与代码由作者撰写；**实验执行中使用 LLM**（qwen3:8b / qwen2.5:7b 作为被测智能体），
  此为研究对象本身，已在 Methods 披露。
- **本工作的对抗审稿流程使用 LLM 作为审稿人角色**（第 1 轮 8 角色、第 2 轮 5 角色、第 3 轮 3 角色
  的独立复审），产出的问题清单已全部落盘（`REVIEW_R*_*.md` / `ROUND_R1.md`）并逐条处理；
  审稿角色由同一/相近模型扮演，属流程辅助，不构成论文证据。
- LLM 未用于生成论文中的数字；所有数字由 `scripts/analysis.py` 从逐种子数据重算。