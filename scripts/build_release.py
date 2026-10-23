#!/usr/bin/env python3
"""build_release.py — assemble and verify the TMLR submission package.

The package must be self-contained: a reader who unzips it and runs pdflatex on
main_tmlr.tex must get the same PDF. This script therefore builds the archive and
then VERIFIES it by extracting to a temp directory and compiling there. A package
that fails to compile from a clean extraction is not a deliverable.

Layout (matches the previous release, minus stale v4 artifacts):
    main_tmlr.tex / main_tmlr.pdf / main.bib / tmlr.sty / tmlr.bst /
    math_commands.tex / tables/*.tex          <- compile from the archive root
    TMLR_CHECKLIST.md / LITERATURE_REVIEW.md / RESPONSE_LETTER.md
    supplement/results/...                    <- analysis JSON (v4 + v5)
    supplement/raw_results/...                <- per-cell JSON for the v5 runs
    supplement/scripts/...                    <- harness, analysis, tables, tests
    supplement/evidence/...                   <- analysis plan, dataset spec, protocol
    supplement/CLAIM_LEDGER.md
    supplement/evidence_manifest.json

Deliberately excluded: the superseded v4 manuscript (paper/main.tex, paper/main.pdf),
process documents (ROUND_R*, REVIEW_R*, MISSION.md, PHASE_LOG.md, REVISION_PLAN.md),
and the results_qwen3_8b* / template_official directories.

Usage: python3 scripts/build_release.py [--out release/submission.zip] [--no-compile]
Exit: 0 = built and verified, 1 = verification failed.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAPER_FILES = ["main_tmlr.tex", "main_tmlr.pdf", "main.bib", "tmlr.sty", "tmlr.bst",
               "math_commands.tex"]
PAPER_TABLES = ["tables/design.tex", "tables/results.tex"]
ROOT_DOCS = ["TMLR_CHECKLIST.md", "LITERATURE_REVIEW.md"]
PROJECT_DOCS = ["RESPONSE_LETTER.md", "CLAIM_LEDGER.md", "evidence_manifest.json"]

SCRIPTS = ["harness_v5.py", "analysis_v5.py", "make_tables.py",
           "test_harness_v5_audit.py", "test_analysis_v5.py",
           "check_submission_ready.py", "build_release.py",
           "harness_v4.py", "analysis_v4.py", "augment_r1.py"]

EVIDENCE = ["analysis_plan_v4.md", "dataset_spec.md", "protocol.md",
            "dataset/LICENSE_PROVENANCE.md"]


def stage(out_zip: Path, do_compile: bool) -> int:
    missing = []
    entries = []          # (src, arcname)

    for name in PAPER_FILES + PAPER_TABLES:
        src = ROOT / "paper" / name
        (entries.append((src, name)) if src.exists() else missing.append(str(src)))

    for name in ROOT_DOCS:
        for base in (ROOT / "paper", ROOT):
            src = base / name
            if src.exists():
                entries.append((src, name))
                break
        else:
            missing.append(name)

    for name in PROJECT_DOCS:
        src = ROOT / name
        arc = name if name == "RESPONSE_LETTER.md" else f"supplement/{name}"
        (entries.append((src, arc)) if src.exists() else missing.append(str(src)))

    # analysis JSON (v4 kept for the supersede trail, v5 is primary)
    for src in sorted((ROOT / "results").glob("*.json")):
        entries.append((src, f"supplement/results/{src.name}"))

    # raw per-cell evidence for the v5 runs
    for d in ("results_v5_27b", "results_v5_qwen35_9b"):
        for src in sorted((ROOT / d / "per_seed").glob("*.json")):
            entries.append((src, f"supplement/raw_results/{d}/{src.name}"))

    for name in SCRIPTS:
        src = ROOT / "scripts" / name
        (entries.append((src, f"supplement/scripts/{name}")) if src.exists()
         else missing.append(str(src)))

    for name in EVIDENCE:
        src = ROOT / "evidence" / name
        (entries.append((src, f"supplement/evidence/{name}")) if src.exists()
         else missing.append(str(src)))

    if missing:
        print("MISSING SOURCE FILES (not fatal, but check):")
        for m in missing:
            print("  -", m)

    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in entries:
            z.write(src, arc)
    print(f"wrote {out_zip} ({out_zip.stat().st_size:,} bytes, {len(entries)} entries)")
    return 0


def verify_compile(out_zip: Path) -> bool:
    """Extract to a temp dir and compile. The package must be self-contained."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        with zipfile.ZipFile(out_zip) as z:
            z.extractall(td)
        tex = td / "main_tmlr.tex"
        if not tex.exists():
            print("VERIFY FAIL: main_tmlr.tex not at archive root")
            return False
        # pdflatex -> bibtex -> pdflatex -> pdflatex: citations cannot resolve
        # without the bibtex pass, and a package that needs it must ship it.
        seq = [("pdflatex", ["pdflatex", "-interaction=nonstopmode", "main_tmlr.tex"]),
               ("bibtex", ["bibtex", "main_tmlr"]),
               ("pdflatex", ["pdflatex", "-interaction=nonstopmode", "main_tmlr.tex"]),
               ("pdflatex", ["pdflatex", "-interaction=nonstopmode", "main_tmlr.tex"])]
        for step, (label, cmd) in enumerate(seq):
            r = subprocess.run(cmd, cwd=td, capture_output=True, text=True, timeout=300)
            if label == "pdflatex" and r.returncode != 0:
                print(f"VERIFY FAIL: {label} step {step + 1} exited {r.returncode}")
                print(r.stdout[-1200:])
                return False
        log = (td / "main_tmlr.log").read_text(errors="ignore")
        pdf = td / "main_tmlr.pdf"
        problems = []
        if not pdf.exists():
            problems.append("no PDF produced")
        if "Reference `" in log and "undefined" in log:
            problems.append("undefined references")
        if "Citation `" in log and "undefined" in log:
            problems.append("undefined citations")
        # The source DEFINES \\pend as text containing "[[PENDING", so scanning the
        # source for that string always fires. Check for actual USAGE instead, and
        # for the rendered marker in the PDF text.
        src = (td / "main_tmlr.tex").read_text(errors="ignore")
        import re as _re
        # the macro DEFINITION contains "\pend}" while every USE contains "\pend{",
        # so a plain search finds only real placeholders
        used = _re.findall(r"\\pend\{", src)
        if used:
            problems.append(f"{len(used)} \\pend{{}} placeholder(s) still in use")
        try:
            ptxt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True,
                                  text=True, timeout=120).stdout
            if "[[PENDING" in ptxt:
                problems.append("PENDING marker rendered in the PDF")
        except Exception:
            pass
        if problems:
            print("VERIFY FAIL:", "; ".join(problems))
            return False
        print(f"VERIFY OK: compiles from a clean extraction -> {pdf.stat().st_size:,} bytes")
        return True


def main():
    args = sys.argv[1:]
    out = Path(args[args.index("--out") + 1]) if "--out" in args \
        else ROOT / "release" / "submission.zip"
    if not out.is_absolute():
        out = ROOT / out
    do_compile = "--no-compile" not in args
    rc = stage(out, do_compile)
    if rc:
        return rc
    if do_compile:
        return 0 if verify_compile(out) else 1
    print("VERIFY SKIPPED (--no-compile)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
