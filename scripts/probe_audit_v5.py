#!/usr/bin/env python3
"""Targeted instrumentation probe: run one dangerous-action scenario across the
gate-related arms and print the audit classification, so the new fields are
exercised (the 1-scenario --probe happened to contain no dangerous action).

Usage: JMF_MODEL=qwen3.5:9b JMF_BACKEND=ollama python3 probe_audit_v5.py [idx]
"""
import importlib.util
import os
import sys

os.environ.setdefault("JMF_BACKEND", "ollama")
os.environ.setdefault("JMF_MODEL", "qwen3.5:9b")

spec = importlib.util.spec_from_file_location("h5", "harness_v5.py")
h5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h5)

idx = int(sys.argv[1]) if len(sys.argv) > 1 else 2
scen, _agents = h5.load_dataset()
s = scen[idx]
print(f"scenario idx={idx}  request={s.get('input_problem','')[:90]!r}")
print()

arms = ["Full", "Abl-noNegot", "Baseline-promptSafety", "Fact-gateOn-safetyOn",
        "Fact-gateNoRegen", "Baseline-heavyAudit"]
for g in arms:
    mem = h5.Memory(h5.CFG["memory_capacity"], forget=h5.GROUP_SPEC[g]["forget"])
    r = h5.run_scenario(s, g, mem, 0, idx)
    c = r["cost"]
    print(f"{g:24s} succ={int(r['success'])} unneg={r['unnegotiated_count']} "
          f"audited={r['audited_actions']} rounds={r['audit_rounds_used']} "
          f"regen={int(r['answer_regenerated'])} parsed={int(r['plan_parsed_ok'])} "
          f"calls={c['llm_calls']} lat={c['latency_ms']}ms "
          f"ptok={c['prompt_tokens']} ctok={c['completion_tokens']}")
    print(f"    actions={r['actions']}")
    for L in r["negotiation_log"]:
        print(f"    AUDIT {L['action']:20s} {L['decision']:8s} kind={L['kind']:16s} "
              f"rounds={L['rounds_used']} raw={[x[:45] for x in L['raw_verdicts']]}")
