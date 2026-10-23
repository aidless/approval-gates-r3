# -*- coding: utf-8 -*-
"""正式补充探针 formal_readiness：只做状态核验，不合成数据。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

EXPECTED_SHA = "72032130232955b785cd622b7c52d893e3166f30a90e1e6279d0a28e8373beef"
ZIP_REL = "template_official/NeurIPS2025_Styles.zip"
STY_REL = "template_official/Styles/Styles/neurips_2025.sty"
PER_REL = "results/per_seed"

zip_path = ROOT / ZIP_REL
sty_path = ROOT / STY_REL
per_dir = ROOT / PER_REL

template_ok = False
sha_ok = False
sty_ok = sty_path.is_file()
if zip_path.is_file():
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    sha_ok = digest == EXPECTED_SHA
    template_ok = sha_ok and sty_ok

real_cells = 0
invalid_cells = 0
if per_dir.is_dir():
    for path in sorted(per_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            invalid_cells += 1
            continue
        if payload.get("synthetic") is False and payload.get("pilot") is False:
            real_cells += 1
        else:
            invalid_cells += 1

status = {
    "probe": "formal_readiness",
    "template": {"zip": ZIP_REL, "sty": STY_REL, "sha_ok": sha_ok, "sty_ok": sty_ok, "template_ok": template_ok},
    "formal_evidence": {"dir": PER_REL, "real_cells": real_cells, "invalid_cells": invalid_cells},
    "formal_target": {"pooled_pairs": 60, "scenarios": 20, "seeds": [0, 1, 2], "h3_delta": 0.05},
    "gate": "BLOCKED_ON_REAL_DATA" if real_cells == 0 else "READY_FOR_P3",
}
(REPORTS / "supplement_status.json").write_text(
    json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"OK readiness template_ok={template_ok} real_cells={real_cells} gate={status['gate']}")
