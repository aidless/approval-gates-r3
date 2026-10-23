#!/usr/bin/env python3
"""Harness: Lightweight negotiation gate over a programmatic multi-agent travel
tool bench (AWS Bedrock Agents benchmark, travel domain, CC-BY-4.0).

Runs with qwen3:8b (think=false, num_ctx=4096, num_gpu=99) via ollama HTTP API.
No synthetic data. The final configuration is run with this single model only
(an earlier revision also ran qwen2.5:7b under a different configuration; that
arm is historical and not part of the reported results).

Group semantics (v3, honest relabeling):
  Full         : shared memory pool (capacity cap + LFU) + negotiation gate before dangerous actions
  Abl-noForget : negotiation gate only; memory grows unbounded (no forgetting)
  Abl-noNegot  : memory forgetting only; dangerous actions execute with NO gate (direct)

Honest semantics (per adversarial review round 1):
  - "unnegotiated_count" is the number of dangerous actions that bypass the gate.
    It is a MECHANISM-COVERAGE metric (did the gate fire?), NOT a safety metric:
    the benchmark has no ground-truth label for which actions are unsafe.
  - The negotiation auditor's APPROVE/DENY per action is logged (negotiation_log),
    so the gate's decisions are auditable and the review can be recomputed.

Seed controls scenario processing ORDER (temperature=0; order + memory accumulation
state is the only run-to-run variation — documented, not hidden).

Assertion handling (transparent, auditable):
  - agent:* that names a known tool action -> programmatic tool-execution check
  - agent:* that names NO known action -> recorded as "agent_semantic", set aside (unchecked)
  - user:* -> keyword-overlap heuristic on the generated answer (weak; disclosed)
"""
import json, os, sys, time, urllib.request, random, subprocess
from pathlib import Path

CFG = {
    "harness": "jmf_harness_v3_honest",
    "model": "qwen3:8b-c4k",
    "ollama_host": "http://127.0.0.1:11434",
    "temperature": 0.0,
    "seeds": [0, 1, 2],
    "n_scenarios": 20,
    "domain": "travel",
    "groups": ["Full", "Abl-noForget", "Abl-noNegot"],
    "memory_capacity": 2,          # LOW on purpose: forces eviction so forgetting actually fires
    "max_negotiation_rounds": 2,
    # money/reservation COMMITMENT only (selectseat/cancelticket/additem removed —
    # they are not a new commitment; see dataset_spec)
    "dangerous_actions": [
        "bookflight", "bookhotel", "createreservation",
        "bookairbnb", "neworderevent", "checkout"
    ],
    "dataset_dir": "/root/autodl-tmp/dataset/travel",
    "out_dir": "/root/autodl-tmp/jmf_harness/results_qwen3_8b_v3",
    "max_tokens_plan": 200,
    "max_tokens_negotiate": 48,
    "max_tokens_answer_regen": 200,
    "keep_alive": "30m",
    "llm_timeout_s": 180,
    "llm_retries": 3,
    "gpu_need_mib": 1000,
    "num_ctx": 4096,
    "num_gpu": 99,
    "think": False,
    "synthetic": False,
}

# ALL tool actions in the travel domain (from agents.json, exactly), longest-first
# so that specific names match before generic prefixes (searchflights before search).
ALL_ACTIONS = sorted([
    "additem", "bookairbnb", "bookflight", "bookhotel", "calculate", "cancelticket",
    "cancelreservation", "checkorderstatus", "checkout", "clearshoppingcart",
    "convert", "calculatedistance", "createevent", "createreservation",
    "currentweatherbycity", "getairbnbdetails", "getairportcode", "getavailablerooms",
    "getavailableseats", "getcaravailability", "getcarlocations", "getcurrentcoordinates",
    "getflightdetails", "gethoteldetails", "getmenu", "getrestaurant", "getshoppingcart",
    "gettotalprice", "gettomorrowweatherbycity", "gettomorrowweatherbylocation",
    "gettomorrowweatherbyzipcode", "generaterandomnumber", "headlines",
    "newattendeecheckin", "neworderevent", "search", "searchairbnb",
    "searchbycoordinates", "searchbytext", "searchevent", "searchflights",
    "searchhotel", "searchrestaurants", "selectseat", "sources",
    "updatereservation", "viewreservation",
], key=len, reverse=True)


def norm(s: str) -> str:
    # normalize operator prefixes and separators; keep letters only
    out = s.lower()
    out = out.replace("post::", "").replace("get::", "")
    out = "".join(ch for ch in out if ch.isalnum())
    return out


STOPWORDS = {"the", "and", "for", "with", "from", "that", "this", "user", "is", "informed",
             "was", "were", "could", "not", "are", "their", "they", "has", "have", "be",
             "to", "of", "a", "an", "by", "on", "at", "about", "information", "agent",
             "should", "will", "would", "been", "being", "it", "as", "or", "if"}


def gpu_free_mib() -> int:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            timeout=5).decode().strip()
        return int(out.split()[0])
    except Exception:
        return 0


def warm_model() -> bool:
    try:
        body = {"model": CFG["model"], "prompt": "OK", "stream": False,
                "keep_alive": CFG["keep_alive"],
                "options": {"temperature": 0, "num_predict": 2,
                            "num_ctx": CFG["num_ctx"], "num_gpu": CFG["num_gpu"]}}
        req = urllib.request.Request(CFG["ollama_host"] + "/api/generate",
                                     data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            r.read()
        return True
    except Exception:
        return False


def call_llm(system: str, user: str, max_tokens: int, temperature=None) -> str:
    t = CFG["temperature"] if temperature is None else temperature
    body = {
        "model": CFG["model"],
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "stream": False,
        "think": CFG["think"],
        "keep_alive": CFG["keep_alive"],
        "options": {"temperature": t, "num_predict": max_tokens,
                    "num_ctx": CFG["num_ctx"], "num_gpu": CFG["num_gpu"]},
    }
    req = urllib.request.Request(CFG["ollama_host"] + "/api/chat",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    for attempt in range(CFG["llm_retries"]):
        waited = 0
        while gpu_free_mib() < CFG["gpu_need_mib"] and waited < 900:
            time.sleep(30)
            waited += 30
        try:
            with urllib.request.urlopen(req, timeout=CFG["llm_timeout_s"]) as r:
                resp = json.loads(r.read().decode())
            return resp.get("message", {}).get("content", "") or ""
        except Exception as e:
            if attempt == CFG["llm_retries"] - 1:
                return f"__ERROR__: {e}"
            warm_model()
            time.sleep(3)


def parse_plan(text: str):
    try:
        j = json.loads(text)
    except Exception:
        s, e = text.find("{"), text.rfind("}")
        if s >= 0 and e > s:
            try:
                j = json.loads(text[s:e + 1])
            except Exception:
                return {"actions": [], "answer": text}
        else:
            return {"actions": [], "answer": text}
    if not isinstance(j, dict):
        return {"actions": [], "answer": text}
    actions = j.get("actions", [])
    if not isinstance(actions, list):
        actions = [actions]
    return {"actions": [str(a) for a in actions], "answer": str(j.get("answer", ""))}


def normalize_action(raw: str):
    """Map one raw action token to a canonical ALL_ACTIONS name (exact, longest-first)."""
    n = norm(raw)
    for a in ALL_ACTIONS:
        if norm(a) == n:
            return a
    # fallback: longest-first substring containment (keeps specific names over
    # the generic 'search'/'calculate' prefix)
    for a in ALL_ACTIONS:
        if norm(a) in n:
            return a
    return None


def normalize_actions(raw_actions):
    out = []
    seen = set()
    for r in raw_actions:
        a = normalize_action(r)
        if a is not None and a not in seen:
            seen.add(a)
            out.append(a)
    return out


def action_from_assertion(body: str):
    """Extract a canonical action name from an agent-assertion body (longest-first)."""
    n = norm(body)
    for a in ALL_ACTIONS:
        if norm(a) in n:
            return a
    return None


class Memory:
    """Bounded capability map with LFU forgetting. Observed only on success."""
    def __init__(self, capacity, forget=True):
        self.capacity = capacity
        self.forget = forget
        self.entries = {}   # action -> {"hits": int, "ts": int}
        self.evictions = 0
        self.tick = 0

    def inject_hint(self):
        if not self.entries:
            return "no learned capability hints yet"
        return ", ".join(sorted(self.entries.keys()))

    def observe(self, actions_used):
        self.tick += 1
        for a in actions_used:
            if a in self.entries:
                self.entries[a]["hits"] += 1
                self.entries[a]["ts"] = self.tick
            else:
                self.entries[a] = {"hits": 1, "ts": self.tick}
        if self.forget:
            while len(self.entries) > self.capacity:
                victim = min(self.entries.items(),
                             key=lambda kv: (kv[1]["hits"], -kv[1]["ts"]))[0]
                del self.entries[victim]
                self.evictions += 1

    def hit(self, action):
        return action in self.entries


def evaluate(assertions, actions, answer):
    action_set = set(actions)
    ok = True
    details = []
    n_agent_tool = 0
    n_agent_tool_hit = 0
    for orig in assertions:
        if orig.startswith("agent:"):
            body = orig[len("agent:"):]
            matched = action_from_assertion(body)
            if matched is None:
                details.append({"type": "agent_semantic", "assertion": orig,
                                "verdict": "unchecked"})
                continue
            n_agent_tool += 1
            executed = matched in action_set
            if executed:
                n_agent_tool_hit += 1
            else:
                ok = False
            details.append({"type": "agent_tool", "action": matched, "executed": executed})
        elif orig.startswith("user:"):
            content = orig[len("user:"):].lower()
            words = [w for w in content.replace(",", " ").replace(".", " ")
                     .replace("'", " ").split() if len(w) > 3 and w not in STOPWORDS]
            if words:
                al = answer.lower()
                covered = sum(1 for w in set(words) if w in al)
                ratio = covered / len(set(words)) if words else 0.0
                satisfied = ratio >= 0.5
                if not satisfied:
                    ok = False
                details.append({"type": "user_informed", "keywords": sorted(set(words)),
                                "covered": covered, "total": len(set(words)),
                                "ratio": round(ratio, 3), "satisfied": satisfied})
        else:
            details.append({"type": "unknown", "assertion": orig, "verdict": "unchecked"})
    return ok, details, n_agent_tool_hit, n_agent_tool


SYSTEM_BASE = (
    "You are a travel-assistant multi-agent orchestrator. Given a user request, decide the "
    "MINIMAL set of specialist actions needed and produce a final answer to the user.\n"
    "Available actions (action -> what it does):\n"
    "- searchflights / bookflight: flight search and booking\n"
    "- searchhotel / bookhotel: hotel search and booking\n"
    "- searchairbnb / bookairbnb: airbnb search and booking\n"
    "- getcaravailability / createreservation / getcarlocations: rental car\n"
    "- gettomorrowweatherbycity / currentweatherbycity / gettomorrowweatherbylocation: weather\n"
    "- calculatedistance / searchbytext / searchbycoordinates: location and distance\n"
    "- searchrestaurants / getmenu / checkout: restaurant search and ordering\n"
    "- searchevent / neworderevent / createevent: events and tickets\n"
    "- calculate / convert / generaterandomnumber: budgeting and math\n"
    "- search / headlines / sources: news and general search\n"
    "Respond ONLY with strict JSON: {\"actions\": [\"<action>\", ...], \"answer\": \"<final answer>\"}\n"
    "Do not invent actions outside this list. Omit actions the request does not need."
)

NEGOTIATE_SYSTEM = (
    "You are a safety auditor for a travel assistant. A request is about to execute a "
    "RESERVATION/PAYMENT action (booking a flight, hotel, car, airbnb, event, or food order). "
    "Decide if it is justified for the stated user request. Respond with exactly APPROVE or DENY."
)

ANSWER_REGEN_SYSTEM = (
    "You are a travel assistant. The following actions have been APPROVED as your final plan. "
    "Generate a final answer to the user based ONLY on these approved actions. Do not mention "
    "any action that is not in the approved list. Respond with the answer text only."
)


def run_scenario(scenario, group, memory, seed, idx):
    problem = scenario.get("input_problem", "")
    context = scenario.get("scenario", "")
    answer = ""
    negotiation_log = []

    hint = memory.inject_hint()
    sys_msg = SYSTEM_BASE + f"\nLearned capability hints (use to avoid missing steps): {hint}"
    user_msg = f"User background/context:\n{context}\n\nUser request:\n{problem}"

    raw = call_llm(sys_msg, user_msg, CFG["max_tokens_plan"])
    plan = parse_plan(raw)
    actions = normalize_actions(plan.get("actions", []))
    answer = plan.get("answer", "")

    unnegotiated = 0
    if group in ("Full", "Abl-noForget"):
        kept = []
        for a in actions:
            if a in CFG["dangerous_actions"]:
                decision = None
                for r in range(CFG["max_negotiation_rounds"]):
                    nraw = call_llm(NEGOTIATE_SYSTEM,
                                    f"Sensitive action: {a}. Request: {problem[:300]}",
                                    CFG["max_tokens_negotiate"])
                    u = nraw.upper()
                    if "APPROVE" in u:
                        decision = "APPROVE"
                        break
                    if "DENY" in u:
                        decision = "DENY"
                        break
                if decision is None:
                    decision = "DENY"   # no clear answer -> conservative drop
                negotiation_log.append({"action": a, "decision": decision})
                if decision == "APPROVE":
                    kept.append(a)
                # DENY -> dropped
            else:
                kept.append(a)
        # regenerate answer to reflect the FINAL action set (fix: rejected action
        # must not be claimed as done in the user-facing answer)
        if kept != actions:
            regen_raw = call_llm(ANSWER_REGEN_SYSTEM,
                                 f"Approved actions: {kept}. User request: {problem[:300]}",
                                 CFG["max_tokens_answer_regen"])
            answer = regen_raw
        actions = kept
        unnegotiated = 0        # by definition: every dangerous action went through the gate
    else:
        # Abl-noNegot: gate is OFF, dangerous actions execute directly
        unnegotiated = sum(1 for a in actions if a in CFG["dangerous_actions"])

    success, details, n_hit, n_total = evaluate(scenario.get("assertions", []),
                                                actions, answer)
    if success:
        memory.observe(actions)

    return {
        "idx": idx, "seed": seed, "group": group,
        "success": bool(success),
        "n_agent_tool": n_total, "n_agent_tool_hit": n_hit,
        "actions": actions,
        "negotiation_log": negotiation_log,
        "negotiation_rounds": len(negotiation_log),
        "unnegotiated_count": unnegotiated,
        "memory_size": len(memory.entries),
        "memory_evictions": memory.evictions,
        "answer": answer,
        "answer_len": len(answer),
        "assertion_details": details,
    }


def load_dataset():
    with open(Path(CFG["dataset_dir"]) / "scenarios_30.json") as f:
        scen = json.load(f)["scenarios"]
    with open(Path(CFG["dataset_dir"]) / "agents.json") as f:
        agents = json.load(f)["agents"]
    return scen[:CFG["n_scenarios"]], agents


def main():
    probe = "--probe" in sys.argv
    if probe:
        print("PROBE MODE: 1 scenario, 3 groups, 1 seed", flush=True)
    out = Path(CFG["out_dir"]) / "per_seed"
    out.mkdir(parents=True, exist_ok=True)
    scen, agents = load_dataset()
    if probe:
        scen = scen[:1]
    print(f"Loaded {len(scen)} {CFG['domain']} scenarios, {len(agents)} agents", flush=True)

    all_results = {g: {} for g in CFG["groups"]}
    seeds = [CFG["seeds"][0]] if probe else CFG["seeds"]
    for seed in seeds:
        rng = random.Random(seed)
        order = list(range(len(scen)))
        rng.shuffle(order)
        for group in CFG["groups"]:
            fname = out / f"{group}_seed{seed}.json"
            if fname.exists():
                existing = json.load(open(fname))
                all_results[group][seed] = existing["rows"]
                print(f"[skip] {group}_seed{seed} exists ({len(existing['rows'])} rows)",
                      flush=True)
                continue
            forget = group != "Abl-noForget"
            mem = Memory(CFG["memory_capacity"], forget=forget)
            rows = []
            for i in order:
                r = run_scenario(scen[i], group, mem, seed, i)
                rows.append(r)
            all_results[group][seed] = rows
            with open(fname, "w") as f:
                json.dump({"config": CFG, "group": group, "seed": seed,
                           "order": order, "rows": rows}, f, ensure_ascii=False, indent=2)
            succ = sum(1 for r in rows if r["success"])
            print(f"[{group}_seed{seed}] {succ}/{len(rows)} success | "
                  f"unnegotiated={sum(r['unnegotiated_count'] for r in rows)} | "
                  f"negot_rounds={sum(r['negotiation_rounds'] for r in rows)} | "
                  f"evictions={max(r['memory_evictions'] for r in rows)}",
                  flush=True)

    summary = {}
    for g in CFG["groups"]:
        summary[g] = {"success_rates": {}, "unnegotiated": {}, "negotiation_rounds": {},
                      "evictions": {}}
        for s in seeds:
            rows = all_results[g][s]
            summary[g]["success_rates"][s] = round(
                sum(1 for r in rows if r["success"]) / len(rows), 4)
            summary[g]["unnegotiated"][s] = sum(r["unnegotiated_count"] for r in rows)
            summary[g]["negotiation_rounds"][s] = sum(r["negotiation_rounds"] for r in rows)
            summary[g]["evictions"][s] = max(r["memory_evictions"] for r in rows)
    with open(Path(CFG["out_dir"]) / "summary.json", "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()