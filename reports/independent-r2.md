# Approval Gates R2 独立复核

日期：2026-10-13。对象：`paper/main.tex`、`paper/tables/design.tex`、`paper/tables/descriptive.tex`、`paper/tables/policy_text.tex`、`scripts/make_descriptive_tables.py`、`results/descriptive_r2.json`、`evidence/scorer_counterexamples_r2.json`，并参照上轮已读 harness 与原始记录。

本轮只读审稿，没有修改稿件、没有重新运行实验或分析。新生成器的计算逻辑与保留 JSON/表格做了静态检查和关键行核对；这不是本审稿人独立重新计算全部 1,620 条记录的认证。

## 总体结论

**R2 实质收窄为描述性测量审计，主张较 R1 已合理。可以沿该定位推进 arXiv 发布准备；当前还不是完成发布验收，也不意味着原实验问题已经解决。** 没有发现新的关键数字冲突或需要重新做实验才能维持“有限记录的测量失败案例”这一定位的问题。顶会主会研究论文的证据缺口保持不变。

标题、摘要与正文现在明确承认单模型动作名模拟器、政策/信息不匹配、跨场景记忆依赖、断言假阳性、标记指标的语义盲区、未知检查点及成本记录缺失。正文不再靠 p 值或区间暗示总体效果，也没有把“指标能重算”等同于“实验可精确再生”。这不是简单将显著结论换成弱形容词，而是改变了论文回答的问题。

## 对前轮六条 Major 的处置判断

| 前轮问题 | R2 主张处置 | 原实验缺陷是否解决 | 依据 |
|---|---|---|---|
| 不同授权政策与信息集 | supported：如实转为 intervention bundles | 否；没有同策略对照 | `main.tex:100–117, 281–287`；审计 justified、提示 explicit confirmation，审计请求截断仍存在。 |
| 跨场景记忆与独立单位 | supported：撤去不可靠推断 | 否；设计依赖保留 | `main.tex:139–143, 191–200`；无显著性/总体置信区间结论。 |
| 任务评分器语义错误 | supported：给出反例并改称 proxy pass | 否；未修评分器或估误判率 | `main.tex:156–164, 219–242`；明确仅单断言假阳性、整 run 仍失败，表 5/90 等仅是代理计数。 |
| 无执行层且仅按动作名匹配 | supported：对象与 coverage 均收窄 | 否；仍不能验证执行授权 | `main.tex:28–34, 119–125, 146–154`；明确归一化去重及 args/IDs/执行盲区。 |
| 审计记录结果是部分设计属性，增量有限 | supported：不再包装为新机制或新一般规律 | 否；贡献限于案例 | `main.tex:43–47, 65–72, 274–287`；适合公开讨论，不是顶会贡献充分性证明。 |
| 服务身份/原始规划/成本日志缺口 | supported：区分重算与再生 | 否；不可恢复元数据仍缺失 | `main.tex:82–87, 134–137, 166–170, 183–189, 289–296`。 |

## 数字与实现静态核查

1. `make_descriptive_tables.py:12–21` 检查 9 配置 × 3 顺序文件唯一、每文件 30 行且 idx 集合 0..29、行 group/seed 一致和 non-synthetic 标记。`:28–30` 从 retained names + APPROVE 记录重推 bypass 并比较存储字段。`:41–46` 对 proxy pass、retained、parse failed 和两类 marker 与继承分析作交叉检查。它没有重新执行原评分器；正文已经叫 harness assertion pass，这个限定必须保持。
2. 新表及 `descriptive_r2.json` 的关键值一致：Full 保留 18/3；prompt-only 保留 0/2；ungated 保留 24/25；Full proxy pass 5/90、4/90；prompt-only 6/90、8/90；9B Full parse failed 15、prompt-only 5。没有发现主文这些数字的新冲突。
3. Full 与 alternative regeneration 的 marker 表分别是 27B B=0/6 → 6/6，9B B=2/13 → 14/14；A=0/6 → 0/6、2/13 → 8/14。正文明确 9B 拒绝集合不同且 B 含 refus，不再声称语义解释被修好。
4. 成本表中的 27B fixed rule 111 logical calls、Full 120，平均时间 12.91 与 11.71 秒/格，符合所展示 JSON。正文没有从该反转推出一般速度优势。14.4% 现在明确是整个 bundle/sequence 的 token 差，避免声称全部是固定 suffix 的净成本。
5. idx10 两个反例的摘录及酒店断言关键词结果 6/9、8/9 与已读原始记录相符；`run_pass:false` 两处明确保存。不能把这两个选中反例扩展为已知 cell-level 总体假阳性率，R2 没这样做。

## 尚应修正或进一步限定的地方

### A. 保留一个轻微的 proposal suppression 归因措辞

`main.tex:211–215`：“prompt-only suppresses most designated names before review”。前面 `:208` 的保留总数少本身不能识别 suffix 的净提议抑制；输入政策、记忆与解析也变了。虽然接下句和 `:216–217` 已限定 bundle，建议仍改成 **“the prompt-only records contain few retained designated names and no auditor decisions”**，并把“suppression”写成该设计可能产生零的一种路径，而非已隔离的因果效应。此处是改稿问题，不需要为描述性论文新增实验。

### B. 成本量的标题最好与计算单位完全一致

`main.tex:184–186` 与 cost 表题的 “mean recorded request time per cell” 容易误读为单次请求时长的均值。实际是每格各逻辑 call 的最后尝试时间之和，再对 90 格取均值。建议直接写 **“mean per-cell sum of recorded last-attempt request times”**；保留当前重试/等待未完整记录的说明。不是数字错误。

### C. 许可证据仍残留旧数据范围

`evidence/dataset/LICENSE_PROVENANCE.md` 的“使用范围”仍写 index 0..19，而 R2 用 0..29。应以当前副本的 30 场景更新，并注明这是修订口径、保留旧记录历史。否则公开 evidence bundle 会对同一研究给出矛盾 provenance。不要声称这项旧范围错误影响了本轮结果数值，现有文件计数与主文是 30。

### D. 可重算的公共材料尚未落实

`main.tex:289–296` 如实说只有 local evidence bundle，尚无 public artifact URL。摘要 `:18` “reproducible audit” 可理解为记录级可重算，但读者目前拿到 TeX 不能获得这些 JSON/脚本。若以此作为核心贡献，发布版应提供固定 commit/release 或持久归档入口、最小重算说明及输入输出哈希；否则摘要应改为 **“a record-level audit with a local recomputation bundle”** 并明确材料未公开。

### E. Grid 验证措辞不能扩大为所有配置 provenance 已认证

`make_descriptive_tables.py:12–21` 验证的是文件键、行数/idx、行标签与 synthetic 标记，未逐字段核对 group_spec、服务配置、实际处理 order、脚本版本或数据版本。`main.tex:192` 若“configuration/order grid”仅指 group/seed 文件键可以保留，最好改为 “file-key grid and scenario-ID coverage”。若声称配置快照已被验证，须在发布材料中另附对应检查记录。

## 仍未满足的发布条件

以下是当前描述性预印本的具体收尾条件，不是要求把旧实验改造成新研究：

- 修正 A/C 两项（归因残留和 provenance 范围）；B/E 为建议一并消歧。
- 提供读者可访问的固定证据版本，包含 54 个 per-seed 文件、必要 travel 数据出处/许可证、实际使用的 harness/生成器、最小 README、哈希和反例；或撤下摘要的公共可重算暗示。未知权重、缺失原始回复及运行元数据继续明确为缺失，不得补造。
- 完成最终 PDF 目检、引用与来源终审、TeX 源码包独立编译，并将公开证据版本/哈希写入发布版；本审稿人未执行这些最终步骤。已有编译日志含多轮构建早期警告，不能把整份日志里出现 undefined 当成最终 PDF 引用仍错，也不能仅凭 11 页输出认定排版验收完成。
- 作者已由本人确认为独著、Independent Researcher；发布许可选择、分类与 arXiv 账户/endorsement 状态仍按提交时真实状态处理，本报告不替代平台审核。

**无需为了这份狭义 arXiv 描述性案例立即做新的模型实验。** 若恢复公平控制效果、真实安全或顶会主会贡献的目标，则仍须统一政策/信息、校准语义断言、重置/冻结记忆或独立序列设计、执行层和固定模型日志；这些不能由 R2 的文字收窄宣告完成。

最终 verdict：**supported for the narrowed descriptive scope; needs-work for final public-artifact and manuscript release readiness.** 这是独立复核意见，不是同行评审接受、顶会质量认证或 arXiv 收录保证。
