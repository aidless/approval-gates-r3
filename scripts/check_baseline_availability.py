# -*- coding: utf-8 -*-
"""正式补充探针 baseline_availability：只核验可运行基线，不编造版本。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

BASELINES = ["coskill", "compact_memory", "continuity"]
MANIFEST_DIR_REL = "evidence/baselines"
manifest_dir = ROOT / MANIFEST_DIR_REL

results = []
for name in BASELINES:
    manifest = manifest_dir / f"{name}.json"
    runnable = False
    detail = "no runnable manifest"
    if manifest.is_file():
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            if payload.get("version") and payload.get("commit") and payload.get("entry"):
                runnable = True
                detail = "runnable manifest present"
            else:
                detail = "manifest incomplete"
        except (OSError, json.JSONDecodeError):
            detail = "manifest unreadable"
    results.append({"baseline": name, "runnable": runnable, "detail": detail})

pilot_cfg_rel = "../paper_joint_mem_forget/results/cfg_snapshot.json"
pilot_cfg = (ROOT / pilot_cfg_rel).resolve()
pilot_note = "pilot cfg does not provide runnable baseline artifacts"
if pilot_cfg.is_file():
    try:
        cfg = json.loads(pilot_cfg.read_text(encoding="utf-8"))
        if not any(key in cfg for key in ("baseline_versions", "baseline_commits", "baselines")):
            pilot_note = "pilot cfg lists groups only; no runnable baseline versions/commits"
    except (OSError, json.JSONDecodeError):
        pilot_note = "pilot cfg unreadable"

out = {
    "probe": "baseline_availability",
    "manifest_dir": MANIFEST_DIR_REL,
    "pilot_cfg": pilot_cfg_rel,
    "pilot_note": pilot_note,
    "baselines": results,
    "stats_rule": "exclude non-runnable baselines from stats; cite only as motivation",
}
(REPORTS / "baseline_availability.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"OK baselines runnable={[r['baseline'] for r in results if r['runnable']]}")
