# TMLR Submission Checklist (v4)

稿件：*Cost, Coverage, and Auditability of Approval Gates versus Prompt-Level Safety in Multi-Agent Tool Execution*
（本文件为交付件记录；提交时按 OpenReview 表单逐项填写。）

## 0. 与 v3 (NeurIPS 版) 的差异

| 项 | v3 | v4 (TMLR) |
|---|---|---|
| 模型 | qwen3:8b（单模型，旧一代） | **Qwen3.8-27B** + **Qwen3.5-9B**（两个新一代骨干） |
| 场景 | travel 20 | travel **30**（全量） |
| 组别 | 3（Full/noForget/noNegot） | **5**（+ promptSafety 成本基线 + heavyAudit 强化门控） |
| 模板 | neurips_2025.sty | **官方 tmlr.sty + tmlr.bst**（MD5 与 JmlrOrg 仓库一致） |
| 核心发现 | 门控覆盖不显著 | **覆盖率相同但可审计性不同**（两机制对照） |

## G1 — Template

- `\usepackage{tmlr}`（**无 option** = 匿名提交）；无 jmlr class；`\bibliographystyle{tmlr}`。
- `tmlr.sty` MD5 `e302463e460a0173d5bee936bc95a625`、`tmlr.bst` MD5 `9c641e8d820e63bb21b670dde311bfb2`，
  与技能自带官方模板一致（`check_tmlr_compliance.py` G1 PASS）。

## G2 — Page limit / format

- US Letter（tmlr.sty 默认）；无页数硬限制（TMLR 无页数上限，只要求格式合规）。

## G3 — Anonymization

- **author 块整体移除**（注释替代），`\maketitle` 渲染为匿名作者；
  这是技能 `init_paper.py:neutralize_author_block` 的推荐做法（官方模板自带真实示例名会被 G3 判 FAIL）。
- 正文无致谢、无基金、无邮箱、无机构；`check_tmlr_compliance.py` G3 无 FAIL。

## G4 — Anonymous code/data repository

- 正文不含作者仓库 URL（无作者自建仓库、无 anonymous.4open.science 链接）。
- **已知 FAIL 属数据溯源声明**（非身份泄露）：`paper/main.bib` 的 `awsbench2024` 条目、
  `evidence/dataset/LICENSE_PROVENANCE.md`、`evidence/dataset_spec.md` 中的**公开数据集** URL
  （AWS Samples 的 multiagent-collab-scenario-benchmark）。TMLR 要求披露数据集出处，
  因此**保留**；`check_submission_package.py` 的 C3 无法区分「作者仓库」与「数据来源」，
  故其 FAIL 在此显式说明为**预期**。
- 提交时在 OpenReview 的匿名说明栏注明：「the only repository URLs are dataset-provenance
  links to a public third-party benchmark (AWS Samples, CC-BY-4.0), not author-owned code」。

## G5 — Supplementary material size

- 补充材料 zip < 100 MB（阈值内）。

## G6 — Citations

- `\bibliographystyle{tmlr}` + `\bibliography{main}`；G6 PASS。
- 引用逐条一手来源核验（FM-27）：`shu2024effective`（arXiv:2412.05449，号-题-作者-许可四项一致）、
  `awsbench2024`（GitHub 仓库 + 许可说明）。

## G7 — Broader Impact

- 含 Broader Impact 段落（技能扫描器 G7 PASS，145 words / 3 keywords）。
- 要点：审批门是安全模式而非安全保证；覆盖 ≠ 安全；无 unsafe ground-truth 标签下不得声称"更安全"。

## G8 — OpenReview form fields

- [ ] 标题 / 摘要与 PDF 一致
- [ ] 作者列表在提交时才填（匿名阶段为空）
- [ ] 主题领域选择
- [ ] 声明：无跨投稿重叠（G9）
- [ ] 声明：数据集与代码许可已注明
- [ ] LLM 使用声明（本工作使用 LLM 作为被测系统与审计器，需按 TMLR 政策披露）

## G9 — Originality / cross-paper overlap

- 本稿是 v3（NeurIPS 未投）的**同一项目续作**：v3 未向任何 venue 提交过；
  本次为首次投稿（无重叠投稿）。
- dataset license 与 compute 声明在 protocol.md 中（扫描器 G9 PASS）。

## G10 — Double-blind separation

- 证据包中不含作者姓名/机构；`--names "Anonymous"` 扫描无残留。
- 历史文件（`results_qwen3_8b*`、`template_official/`）为项目内部记录，**不进入投稿包**。

## G11 — Hash reconciliation

- `evidence_manifest.json` SHA-256 逐文件对账；Phase 5 交付前跑 `--verify` 要求字节级一致。

## 核心 claim 的证据强度（对齐 ledger）

1. **任务成功无显著差异** —— exact McNemar；低功效，未做 equivalence test → 表述为 "no detectable change"。
2. **覆盖率相同、可审计性不同** —— `unnegotiated_count` 对两机制不可区分（结构性零）；
   `audited_actions` / `runs_proposing_dangerous_actions` 区分二者。这是**机制对照**，不是统计发现。
3. **成本排序** —— 额外调用数下界：promptSafety 0 < Full ≈ 1×/动作 < heavyAudit ≈ 3×/动作。
4. **记忆遗忘真实触发但不产生成功率收益** —— 累计淘汰计数器终值。

## 统计与复现

- 唯一重算脚本 `scripts/analysis_v4.py`（只读 per-seed JSON，不合成数据）。
- 配对单位 (seed, scenario)；因温度 0 仍非确定，**独立单位取 30 场景**（场景级为主口径，
  预注册于 `evidence/analysis_plan_v4.md`）。
- exact McNemar / Wilcoxon+CLES / paired bootstrap 95% CI (B=2000) / Holm（未舍入 p）；
  `mean(pair_diff) == mean(Full) - mean(Abl)` 断言强制。

---

# v5 修订轮（instrumented revision，2026-09-15）

## 网格与流水线

- **9 配置 × 3 种子 × 30 场景 = 810 cells/模型**，两模型合计 1620；`__ERROR__` = 0。
- 配置为 2×2 factorial（auditor × safety sentence）+ 隔离臂（regen / 记忆 / 轮数预算 / 确定性规则）。
- 流水线：`scripts/harness_v5.py` → `scripts/analysis_v5.py` → `scripts/make_tables.py` → `paper/tables/*.tex`。
  **表格由 JSON 机器生成，无手抄数字。**

## 测试与门（全部实跑）

| 检查 | 结果 |
|---|---|
| `test_harness_v5_audit.py`（审计五分类/轮数/regen/成本/大小写/parse/确定性门/强制披露） | **70/70 PASS** |
| `test_analysis_v5.py`（不变量，独立重算，每模型） | **94/94 PASS ×2** |
| `make_tables.py --verify`（往返格式化校验） | 0 缺失；**篡改注入 `9999` 被检出**（门可失败） |
| `check_submission_ready.py`（6 门：待填/未定义引用/未定义文献/表输入/悬空 ref/PDF `??`） | **6/6 PASS** |
| `verify_claim_ledger.py`（C01–C56） | **56 PASS / 0 FAIL / 2 WARN**（WARN = C19/C20 合法 inconclusive） |
| `build_evidence_manifest.py --verify` | **247 PASS / 0 FAIL / 25 WARN**（WARN = 已排除目录） |
| `check_submission_package.py`（target=项目根） | C1/C2/C4/C6/C7 **PASS**，C3 FAIL（见下） |
| `scan_number_consistency.py` | stale 0 / 倒置 CI 0 / 表-正文不符 0 |
| `scan_hallucination.py` | 引用错误 0 / 方法文件缺失 0 / 算术矛盾 0 / 强断言 0 |
| `check_writing_style.py` | findings 0 / failures 0 |
| `scan_stats_consistency.py` | 0 |
| `build_release.py` 自解压编译 | **VERIFY OK**（干净解压 → 275,260 B PDF） |

## C3（匿名化）FAIL 的处置：保留，理由如下

3 处命中经逐条审计，**全部是同一个第三方公开数据集仓库**
`https://github.com/aws-samples/multiagent-collab-scenario-benchmark`，分别位于
`main.bib`（数据集条目）、`supplement/evidence/dataset_spec.md`、
`supplement/evidence/dataset/LICENSE_PROVENANCE.md`。其余 URL 均为被引文献的 arXiv 摘要页。

- 该 URL 指向**第三方**（AWS），不标识本文作者；
- TMLR 要求数据许可与来源可核验，删除会损害可复现性；
- `main_tmlr.tex` 中**无 `\author`、无 `\affil`、无致谢、无资助声明、无 ORCID、无邮箱**（已 grep 确认），
  作者块按 G3 整段移除。

故判定为检查器「任何 URL 皆视为泄漏」启发式的**误报**，保留并在本文件记录。

## 相对 v4 的口径变更（不可混用）

覆盖率字段由**硬编码常量**改为**推导**（语义：保留但无 APPROVE 记录）；成本由**上界**改为**实测**
（轮数/延迟/token）；空计划拆分为 parse 失败与真空计划；断言前缀匹配改为大小写不敏感；
审计判定新增五分类。v4 数字（450 cells、retained 20、披露 4/54、12.9%、p=0.03125）**全部作废**，
取代关系见 `CLAIM_LEDGER.md` 的 S 列表。

## 交付物

- `release/submission_v5.zip`（1,022,251 B，92 条目；**不含** v4 旧稿 `main.tex`/`main.pdf` 与过程文档）
- `RESPONSE_LETTER.md`（逐条覆盖 8 weaknesses + 7 suggestions + 7 questions = 22 条，0 待填）
