#!/usr/bin/env python3
"""Pre-submission gate for the TMLR manuscript.

Refuses to call the paper ready while any of the following remains. Each check is
designed so that it FAILS on the current working state (the gates must be able to
fail, otherwise they are decoration):

  G1  unresolved PENDING markers in the manuscript  (\\pend{...})
  G2  LaTeX reported an undefined reference
  G3  LaTeX reported an undefined citation
  G4  a \\input{tables/...} file is missing
  G5  a \\ref{...} target never gets a \\label from the built document
  G6  the compiled PDF still prints "??" (LaTeX's unresolved-reference marker)

Usage:
    python3 scripts/check_submission_ready.py <paper_dir> [--json out.json]
Exit: 0 = all gates pass, 1 = at least one gate failed.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def read(p: Path) -> str:
    try:
        return p.read_text(errors="ignore")
    except FileNotFoundError:
        return ""


def resolve_inputs(tex: str, paper_dir: Path):
    """Every \\input{...} target, as a path that should exist."""
    missing = []
    for m in re.finditer(r"\\input\{([^}]*)\}", tex):
        rel = m.group(1).strip()
        cand = paper_dir / (rel if rel.endswith(".tex") else rel + ".tex")
        if not cand.exists():
            missing.append(rel)
    return missing


def main():
    paper_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("paper")
    out_json = None
    if "--json" in sys.argv:
        out_json = sys.argv[sys.argv.index("--json") + 1]

    tex_path = paper_dir / "main_tmlr.tex"
    tex = read(tex_path)
    log = read(paper_dir / "main_tmlr.log")
    aux = read(paper_dir / "main_tmlr.aux")
    pdf = paper_dir / "main_tmlr.pdf"

    gates = {}

    # G1 unresolved placeholders
    pend = re.findall(r"\\pend\{([^}]*)\}", tex)
    gates["G1_no_pending_markers"] = {
        "pass": len(pend) == 0, "count": len(pend), "detail": sorted(set(pend))[:12]}

    # G2 undefined references reported by LaTeX
    undef_ref = re.findall(r"Reference `([^']*)' on page", log)
    undef_ref += re.findall(r"LaTeX Warning: Reference `([^']*)'", log)
    gates["G2_no_undefined_reference"] = {
        "pass": len(undef_ref) == 0, "count": len(undef_ref),
        "detail": sorted(set(undef_ref))[:12]}

    # G3 undefined citations
    undef_cite = re.findall(r"Citation `([^']*)'", log)
    gates["G3_no_undefined_citation"] = {
        "pass": len(undef_cite) == 0, "count": len(undef_cite),
        "detail": sorted(set(undef_cite))[:12]}

    # G4 table inputs exist
    missing_inputs = resolve_inputs(tex, paper_dir)
    gates["G4_table_inputs_present"] = {
        "pass": len(missing_inputs) == 0, "count": len(missing_inputs),
        "detail": missing_inputs[:12]}

    # G5 every \ref target has a \label somewhere in the built document
    refs = set(re.findall(r"\\ref\{([^}]*)\}", tex))
    labels = set(re.findall(r"\\label\{([^}]*)\}", tex))
    labels |= set(re.findall(r"\\newlabel\{([^}]*)\}", aux))
    dangling = sorted(refs - labels)
    gates["G5_all_refs_labelled"] = {
        "pass": len(dangling) == 0, "count": len(dangling), "detail": dangling[:12]}

    # G6 the PDF must not print LaTeX's unresolved marker
    qq = None
    if pdf.exists():
        try:
            txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True,
                                 text=True, timeout=60).stdout
            qq = txt.count("??")
        except Exception:
            qq = None
    gates["G6_pdf_has_no_question_marks"] = {
        "pass": (qq == 0) if qq is not None else None,
        "count": qq,
        "detail": "pdftotext unavailable" if qq is None else ""}

    failed = [k for k, v in gates.items() if v["pass"] is False]
    unknown = [k for k, v in gates.items() if v["pass"] is None]

    print(f"# submission-ready gate: {paper_dir}")
    for k, v in gates.items():
        state = "PASS" if v["pass"] else ("SKIP" if v["pass"] is None else "FAIL")
        extra = f" ({v['count']})" if v.get("count") is not None else ""
        print(f"[{state}] {k}{extra}")
        if v["pass"] is False and v.get("detail"):
            print(f"        {v['detail']}")
    print()
    print(f"failed: {len(failed)}  skipped: {len(unknown)}")
    if out_json:
        Path(out_json).write_text(json.dumps({"gates": gates, "failed": failed},
                                             indent=2, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
