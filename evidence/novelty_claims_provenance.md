# novelty_claims 抽取溯源

- source: `/home/liuzewen/arxiv-publication/papers/approval-gates-r3/paper/main.tex`
- 候选总数: 1（K4 排除 1）

抽取器只认句式，不判断「这句是否真的在主张新颖」。**K1 closest 是实测中新颖性真正被主张的地方**（`the closest prior work is X`），K3 assertive（五篇仅 1~2 处）不足以单独支撑检索。

## 候选（未排除）

| ID | kind | 源行 | 原文 | 是否被作者删除 | 删除理由 |
|---|---|---|---|---|---|
| C1 | K2 | 61 | Our contribution is a bounded descriptive case study with four parts: a transparent accounting of retained names and review records; a concrete audit of asserti | 否 | — |

### kind 含义

- `K1` closest — closest/nearest prior work、unlike prior、no prior work
- `K2` contribution — 贡献块 item 或 `Our contribution is ...`
- `K3` assertive — we are the first / first work / novel contribution

## 排除项（不是 claim，勿送去检索）

| ID | kind | 源行 | 原文 | 排除理由 |
|---|---|---|---|---|
| C2 | K4 | 345 | The supplement measures finite executed effects, with the existing bound component as a strong baseline rather than a new method. | 否定式新颖声明：我们不主张什么，不是主张 |

## 门怎么用这份文件

`novelty_claim_search_gate.py` 会核对：provenance 里的候选 − `novelty_claims.txt` 里的 claim，是否都在 `novelty_claims.rejected.txt` 有对应理由；没有理由的删除报 `NOV-CLAIM-SILENT-DROP`（Major）。

