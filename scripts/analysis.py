#!/usr/bin/env python3
"""analysis.py — 唯一重算脚本（P3）。只读 results/per_seed 逐种子数据，绝不合成。

统计纪律（frozen in protocol.md）：
  - 任务级 0/1 → exact McNemar（配对单位=同 seed 同场景 idx，Full vs Ablation）
  - 连续指标（unnegotiated_count / negotiation_rounds）→ Wilcoxon + CLES + bootstrap 95% CI
  - 多重比较 → Holm（用未舍入 p）
  - mean(pair_diff) == 组间均值差，assert 强制（数值一致性）
"""
import json, math, sys
from pathlib import Path
import numpy as np
from scipy import stats
from scipy.stats import wilcoxon, binom

GROUPS = ["Full", "Abl-noForget", "Abl-noNegot"]
SEEDS = [0, 1, 2]
PER_SEED_DIR = sys.argv[1] if len(sys.argv) > 1 else "results/per_seed"
OUT_NAME = sys.argv[2] if len(sys.argv) > 2 else "analysis_p3.json"
B = 2000          # bootstrap resamples for CLES CI
SEED_BOOT = 42


def load(group, seed):
    p = Path(PER_SEED_DIR) / f"{group}_seed{seed}.json"
    with open(p) as f:
        d = json.load(f)
    # rows keyed by scenario idx (pairing unit)
    return {r["idx"]: r for r in d["rows"]}


def align(base, other, seed):
    """Pair rows by scenario idx for one seed; returns aligned lists."""
    xs, ys = [], []
    for idx in sorted(base.keys()):
        if idx in other:
            xs.append(base[idx])
            ys.append(other[idx])
    return xs, ys


def mcnemar_exact(b, c):
    """Exact McNemar p (two-sided binomial on discordant pairs)."""
    n = b + c
    if n == 0:
        return 1.0, 0
    p = 2.0 * binom.cdf(min(b, c), n, 0.5)
    return min(1.0, p), n


def cles(x, y):
    """Common Language Effect Size (Vargha-Delaney A)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n1, n2 = len(x), len(y)
    if n1 == 0 or n2 == 0:
        return float("nan")
    # vectorized: P(x > y) + 0.5 P(x == y)
    gt = (x[:, None] > y[None, :]).sum()
    eq = (x[:, None] == y[None, :]).sum()
    return (gt + 0.5 * eq) / (n1 * n2)


def cles_bootstrap_ci(x, y, B=B, seed=SEED_BOOT):
    """Paired bootstrap: resample (x_i, y_i) pairs together, preserving the
    (seed, scenario) pairing used by the tests. Point estimate of CLES is the
    Vargha-Delaney A from the cross-product (see cles())."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    ests = []
    for _ in range(B):
        idx = rng.integers(0, n, size=n)
        ests.append(cles(x[idx], y[idx]))
    return np.percentile(ests, [2.5, 97.5])


def holm(pvals):
    """Holm-Bonferroni corrected p-values from UNROUNDED p-values."""
    pvals = [p for p in pvals if p is not None]
    if not pvals:
        return []
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [None] * m
    for rank, i in enumerate(order):
        adj[i] = min(1.0, (m - rank) * pvals[i])
    # enforce monotonicity
    for k in range(1, m):
        j = order[k]
        jprev = order[k - 1]
        adj[j] = max(adj[j], adj[jprev])
    return adj


def main():
    out_dir = Path("results")
    print(f"Loading per_seed from {PER_SEED_DIR}", flush=True)
    data = {}
    for g in GROUPS:
        for s in SEEDS:
            data[(g, s)] = load(g, s)

    # ---- success rates ----
    success_rates = {}
    for g in GROUPS:
        for s in SEEDS:
            rows = data[(g, s)]
            success_rates[f"{g}_seed{s}"] = round(
                sum(1 for r in rows.values() if r["success"]) / len(rows), 4)

    # ---- paired McNemar: Full vs each ablation ----
    mcnemar_results = {}
    for ab, label in [("Abl-noForget", "Full_vs_noForget"),
                      ("Abl-noNegot", "Full_vs_noNegot")]:
        b_total = c_total = 0
        n_pairs = 0
        per_seed_b = {}
        for s in SEEDS:
            xs, ys = align(data[("Full", s)], data[(ab, s)], s)
            b = c = 0
            for x, y in zip(xs, ys):
                fx = 1 if x["success"] else 0
                ay = 1 if y["success"] else 0
                if fx and not ay:
                    b += 1
                elif not fx and ay:
                    c += 1
            per_seed_b[s] = {"b": b, "c": c, "n": b + c}
            b_total += b
            c_total += c
            n_pairs += len(xs)
        p, n_disc = mcnemar_exact(b_total, c_total)
        mcnemar_results[label] = {
            "pairs": n_pairs,
            "discordant": n_disc,
            "Full_win(Abl_fail)": b_total,
            "Full_fail(Abl_win)": c_total,
            "exact_p": p,
            "per_seed": per_seed_b,
        }

    # ---- continuous: unnegotiated_count & negotiation_rounds (Wilcoxon + CLES) ----
    wilcoxon_results = {}
    for metric in ["unnegotiated_count", "negotiation_rounds"]:
        for ab, label in [("Abl-noForget", "Full_vs_noForget"),
                          ("Abl-noNegot", "Full_vs_noNegot")]:
            full_vals = []
            ab_vals = []
            pairs = []
            for s in SEEDS:
                xs, ys = align(data[("Full", s)], data[(ab, s)], s)
                for x, y in zip(xs, ys):
                    full_vals.append(x[metric])
                    ab_vals.append(y[metric])
                    pairs.append(x[metric] - y[metric])
            full_vals = np.array(full_vals, dtype=float)
            ab_vals = np.array(ab_vals, dtype=float)
            pairs = np.array(pairs, dtype=float)

            # assert: mean(pair diff) == group-mean difference (numerical consistency)
            mean_d = pairs.mean()
            mean_diff = full_vals.mean() - ab_vals.mean()
            assert abs(mean_d - mean_diff) < 1e-9, \
                f"mean(d)={mean_d} != mean(x)-mean(y)={mean_diff}"

            if len(pairs) == 0:
                w_p = float("nan")
            elif np.all(pairs == 0):
                w_p = 1.0
            else:
                try:
                    w_p = wilcoxon(full_vals, ab_vals).pvalue
                except ValueError:
                    w_p = float("nan")
            cl = cles(full_vals, ab_vals)
            ci = cles_bootstrap_ci(full_vals, ab_vals)
            wilcoxon_results[f"{label}_{metric}"] = {
                "mean_Full": round(float(full_vals.mean()), 4),
                "mean_Abl": round(float(ab_vals.mean()), 4),
                "mean_pair_diff": round(float(mean_d), 4),
                "wilcoxon_p": w_p if math.isnan(w_p) else float(w_p),
                "cles": round(cl, 4),
                "cles_ci95": [round(float(c), 4) for c in ci],
                "n": int(len(pairs)),
            }

    # ---- Holm correction over the hypothesis family ----
    family_p = []
    family_keys = []
    for k, v in mcnemar_results.items():
        family_p.append(v["exact_p"])
        family_keys.append(f"mcnemar:{k}")
    for k, v in wilcoxon_results.items():
        if not math.isnan(v["wilcoxon_p"]):
            family_p.append(v["wilcoxon_p"])
            family_keys.append(f"wilcoxon:{k}")
    holm_adj = holm(family_p)
    holm_map = {k: round(a, 6) for k, a in zip(family_keys, holm_adj)}

    # ---- scenario-level sensitivity (20 independent units) ----
    # seeds are processing orderings (and decoding is non-deterministic even at T=0),
    # so the effective independent unit is the scenario, not the (seed, scenario) cell.
    scen_results = {}
    for ab, label in [("Abl-noForget", "Full_vs_noForget"), ("Abl-noNegot", "Full_vs_noNegot")]:
        for metric in ["unnegotiated_count", "negotiation_rounds"]:
            f_by_scen, a_by_scen = {}, {}
            for s in SEEDS:
                for idx, row in data[("Full", s)].items():
                    f_by_scen.setdefault(idx, []).append(row[metric])
                for idx, row in data[(ab, s)].items():
                    a_by_scen.setdefault(idx, []).append(row[metric])
            keys = sorted(f_by_scen)
            fx = [sum(f_by_scen[i]) for i in keys]
            ay = [sum(a_by_scen[i]) for i in keys]
            diffs = [f - a for f, a in zip(fx, ay)]
            nz = [d for d in diffs if d != 0]
            npos = sum(1 for d in nz if d > 0)
            nneg = sum(1 for d in nz if d < 0)
            sign_p = 1.0
            if nz:
                k = min(npos, nneg)
                sign_p = min(1.0, 2 * float(binom.cdf(k, len(nz), 0.5)))
            wp = None
            if any(d != 0 for d in diffs):
                try:
                    _, wp = wilcoxon(fx, ay)
                    wp = round(float(wp), 6)
                except Exception:
                    wp = None
            min_p = (2 * (0.5 ** len(nz))) if nz else 1.0
            scen_results[f"{label}_{metric}"] = {
                "n_units": len(keys), "nonzero_units": len(nz),
                "positive": npos, "negative": nneg,
                "wilcoxon_p": wp, "sign_test_p": round(sign_p, 6),
                "min_attainable_two_sided_p": round(min_p, 6),
                "per_scenario_diff": {int(i): int(d) for i, d in zip(keys, diffs) if d != 0},
            }

    # ---- disclosure / cost / eviction / auditor statistics (auditable fields) ----
    sup = {"auditor_decisions": {}, "deny_disclosure": {}, "gated_actions": {},
           "answer_regen_runs": 0, "evictions_total_per_seed": {}, "evictions_scenarios": {}}
    _discl = ["cannot", "can not", "unable", "not able", "outside the approved", "denied"]
    for g in GROUPS:
        ap = dn = gated = 0
        ev_tot, ev_scen = {}, {}
        for s in SEEDS:
            rows = data[(g, s)]
            ev_tot[s] = max(r["memory_evictions"] for r in rows.values())
            # scenes where the cumulative counter ACTUALLY increased (walk processing order);
            # eviction only runs inside observe(), i.e. on successful scenarios
            with open(Path(PER_SEED_DIR) / f"{g}_seed{s}.json") as f:
                _order = json.load(f)["order"]
            prev, inc = 0, 0
            for idx in _order:
                cur = rows[idx]["memory_evictions"]
                if cur > prev:
                    inc += 1
                prev = cur
            ev_scen[s] = inc
            for r in rows.values():
                gated += r["negotiation_rounds"]
                for L in r["negotiation_log"]:
                    if L["decision"] == "APPROVE":
                        ap += 1
                    else:
                        dn += 1
        sup["auditor_decisions"][g] = {"APPROVE": ap, "DENY": dn}
        sup["gated_actions"][g] = gated
        sup["evictions_total_per_seed"][g] = ev_tot
        sup["evictions_scenarios"][g] = ev_scen
    # disclosure of denials to the user (counts runs whose final answer mentions the denial)
    disc_n = undisc_n = denyruns = 0
    deny_runs_per_group = {g: 0 for g in GROUPS}
    discl_detail = {"redirected_external": 0, "asked_instructions": 0}
    for g in ["Full", "Abl-noForget"]:
        for s in SEEDS:
            for r in data[(g, s)].values():
                if any(L["decision"] == "DENY" for L in r["negotiation_log"]):
                    denyruns += 1
                    deny_runs_per_group[g] += 1
                    al = r["answer"].lower()
                    if any(w in al for w in _discl):
                        disc_n += 1
                        if "instructions" in al or "clarify" in al:
                            discl_detail["asked_instructions"] += 1
                        else:
                            discl_detail["redirected_external"] += 1
                    else:
                        undisc_n += 1
    sup["deny_disclosure"] = {"deny_runs": denyruns, "disclosed": disc_n, "not_disclosed": undisc_n,
                              "per_group": deny_runs_per_group, "detail": discl_detail}
    # answer regeneration calls: one per run whose kept action set changed (>=1 DENY run)
    sup["answer_regen_runs"] = denyruns
    total_audited = sum(v["APPROVE"] + v["DENY"] for v in sup["auditor_decisions"].values())
    sup["extra_llm_calls_lower_bound"] = {
        "full_only": sup["gated_actions"]["Full"] + deny_runs_per_group["Full"],
        "all_gate_conditions": total_audited + sup["answer_regen_runs"],
        "note": "audited actions + answer regenerations; auditor may use up to 2 calls per action, so this is a lower bound",
    }

    # ---- Holm over four de-duplicated tests (drop the mirror + the degenerate all-tie test) ----
    k4_keys = ["mcnemar:Full_vs_noForget", "mcnemar:Full_vs_noNegot",
               "wilcoxon:Full_vs_noNegot_unnegotiated_count",
               "wilcoxon:Full_vs_noForget_negotiation_rounds"]
    k4_p = [mcnemar_results["Full_vs_noForget"]["exact_p"],
            mcnemar_results["Full_vs_noNegot"]["exact_p"],
            wilcoxon_results["Full_vs_noNegot_unnegotiated_count"]["wilcoxon_p"],
            wilcoxon_results["Full_vs_noForget_negotiation_rounds"]["wilcoxon_p"]]
    holm_k4 = {k: round(a, 6) for k, a in zip(k4_keys, holm(k4_p))}

    result = {
        "meta": {
            "n_scenarios": 20, "groups": GROUPS, "seeds": SEEDS,
            "bootstrap_B": B, "holm_k": len(family_p),
            "note": "exact McNemar (paired by seed+scenario idx); Wilcoxon+CLES for continuous; Holm on unrounded p; scenario-level sensitivity included"
        },
        "success_rates": success_rates,
        "mcnemar": mcnemar_results,
        "wilcoxon": wilcoxon_results,
        "holm": holm_map,
        "holm_k4_deduplicated": holm_k4,
        "scenario_level": scen_results,
        "supplementary": sup,
    }
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / OUT_NAME, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()