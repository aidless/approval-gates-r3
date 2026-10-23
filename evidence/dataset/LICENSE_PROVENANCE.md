# 许可与出处一手记录 (LICENSE PROVENANCE)

本文件为论文中「数据 CC-BY-4.0 / 代码 MIT-0」断言的**可核验载体**（此前仅正文声称，仓库内无实物）。

## 数据集

- 名称：Multi-agent Collaboration Scenario Benchmark（AWS Bedrock Agents）
- GitHub：https://github.com/aws-samples/multiagent-collab-scenario-benchmark
- 技术报告：arXiv:2412.05449

## 一手许可声明（引自数据集官方仓库 README.md「License」节）

> This library is licensed under the MIT-0 License. See the LICENSE file.
>
> The dataset is licensed under the CC-BY-4.0 license.

（来源：本仓库 `evidence/dataset/README.md`，即数据集官方仓库 README 的副本。）

## 独立验号记录（2026-09-14，web_fetch）

| 项 | 核验值 | 结论 |
|---|---|---|
| arXiv id | 2412.05449 | — |
| 标题 | Towards Effective GenAI Multi-Agent Collaboration: Design and Evaluation for Enterprise Applications | 与 main.bib 一致 ✓ |
| 作者 | Raphael Shu, Nilaksh Das, Michelle Yuan, Monica Sunkara, Yi Zhang | 与 main.bib 一致 ✓ |
| 提交 | 6 Dec 2024 (v1) | 与 main.bib year=2024 一致 ✓ |
| 许可（arXiv 页） | CC-BY-4.0（view license → creativecommons.org/licenses/by/4.0/） | 与数据集 README 一致 ✓ |

## 使用范围

- 本工作仅使用 travel 领域的 `scenarios_30.json`（本轮记录覆盖index 0..29；旧稿曾仅用0..19）与 `agents.json`
- 场景为人工设计的企业场景，非真实用户流量；不含真实 PII
- 无人类受试者，无需 IRB
- 按 CC-BY-4.0 要求注明出处（见 main.bib 与正文 Dataset 节）