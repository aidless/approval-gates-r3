import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_descriptive_recompute_matches_committed_outputs():
    outputs = [
        ROOT / "paper" / "tables" / "descriptive.tex",
        ROOT / "results" / "descriptive_r2.json",
        ROOT / "evidence" / "scorer_counterexamples_r2.json",
        ROOT / "reports" / "raw-record-hashes.json",
    ]
    before = {path: digest(path) for path in outputs}
    result = subprocess.run(
        [sys.executable, "scripts/make_descriptive_tables.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Validated 54 files / 1620 rows" in result.stdout
    assert {path: digest(path) for path in outputs} == before


def test_claim_trace_references_existing_artifacts():
    trace = json.loads((ROOT / "evidence" / "figure_table_trace_r3.json").read_text())
    assert trace.get("schema"), "trace schema is missing"
    artifacts = trace.get("artifacts")
    assert isinstance(artifacts, list) and artifacts
    ids = [artifact.get("artifact_id") for artifact in artifacts]
    assert all(isinstance(artifact_id, str) and artifact_id for artifact_id in ids)
    assert len(ids) == len(set(ids)), "artifact ids must be unique"
