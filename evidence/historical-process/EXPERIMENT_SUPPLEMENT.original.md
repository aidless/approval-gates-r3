# 正式补充实验预注册 EXPERIMENT_SUPPLEMENT.md（F1）

状态：**已完成**。正式目标 N=60 pairs 已达成（qwen3:8b 20 场景×3 种子=180 cells，synthetic=false），P3 重算已完成（见 reports/P3_analysis_q3_8b.md）。下方为冻结的预注册原始内容（含试点 N=36→正式 N=60 的过渡叙述，非样本量冲突）。

## F1 目标

- 把配对样本从试点池化 N=36 补到正式目标 N=60，满足 exact McNemar 先验。
- 正式采用 H3 非劣效界 `delta=0.05`，解决 intake 阻塞项 3 的“试点预设待确认”问题。
- 不把试点合成 18 cells 转正；正式证据必须 `synthetic=false` 且 `pilot=false`。

## 样本推导

- McNemar 先验：OR=4，`p_discordant=0.3`，alpha=0.05，power=0.8，需 N=60 pairs（含 18 discordant）。
- 池化口径：配对单位=同场景同种子同配置；pooled pairs=场景数×种子数。
- 正式方案：20 场景×3 种子=60 pairs；种子保持 `[0,1,2]`，温度 0。
- paired t 先验 d=0.5 需 N=34；N=60 同样覆盖。
- 场景命名：`FORMAL_SCEN-01..20`；不得复用 `PILOT_SCEN` 合成内容；每个场景需任务定义、成功判据、失败分类。

## 组别与基线规则

- 组别沿用：Full、Abl-noForget、Abl-noNegot；基线候选：CoSkill、Compact-Memory、CONTINUITY。
- 只有同时满足以下条件才进入统计：可在本工作区运行、有版本与 commit、有明确成功判据。
- 闭源不可跑者只作动机引用，不混入统计；已由基线可用性探针记录。

## 排除与失败口径

- 环境崩溃/超时计入分母并列失败分类 E053，不剔除不利样本。
- 缺失场景或组别不得用合成补齐；缺失即报告缺失。

## 分析复用

- 复用冻结方法：任务级 0/1 用 exact McNemar；连续指标用 Wilcoxon + CLES + bootstrap 95% CI；多重比较用 Holm未舍入 p；`mean(d)` 必须等于组间均值差。
- 正式唯一分析脚本在真实数据落盘后新建；试点 `analysis_p3.py` 不得直接当作正式脚本。

## 可执行任务与门禁

- 已执行：`formal_readiness`（模板与正式证据探针）、`baseline_availability`（基线可运行性探针）。
- 未执行：真实证据采集；需用户给出 `FORMAL_EVIDENCE_DIR` 或证据包路径后才建采集任务。
- 门禁：`reports/supplement_status.json` 中 `real_cells=0` 时保持 BLOCKED，不进 P3/P4/P6。
