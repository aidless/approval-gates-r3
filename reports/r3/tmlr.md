# TMLR compliance scan report

Target: `paper`  |  findings: 7  |  failures: 4
- [G1] FAIL :: non-anonymous tmlr option '\\usepackage[preprint]{tmlr}' @ paper/main.tex: submission must use \usepackage{tmlr} with NO option ([accepted] = camera-ready, [preprint] = de-anonymized)
- [G3] FAIL :: identity block '\\author{Zewen Liu \\\\ Independent Researcher \\\\ \\texttt{17353' @ paper/main.tex:13
- [G3] FAIL :: email '17353895263@163.com' @ paper/main.tex:13
- [G3] FAIL :: name residue 'Zewen Liu' @ paper/main.tex:13
- [G6] PASS :: bibliography mechanism present
- [G7] PASS :: Broader Impact section @ paper/main.tex:348 (73 words, 3 keywords)
- [G9] WARN :: no evidence/protocol.md found; cannot verify dataset-license/compute declarations (FM-27/FM-29)