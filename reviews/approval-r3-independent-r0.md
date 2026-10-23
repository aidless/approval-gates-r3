# Approval R3 independent read-only scientific review R0

Reviewer: separate Codex reviewer subagent, 2026-10-14. This is an uncalibrated AI scientific review of supplied local evidence, not human peer review, an acceptance prediction, or an independent laboratory replication. No inference, experiments, original analysis scripts, or upstream tests were run. The only permitted write is this review. Small read-only count, field, storage, digest and hash checks were performed directly, without importing the study's modules.

## Scope and reviewed snapshot

Read PROTOCOL_R0 through R4, the original primary-design and Qwen pilot reviews, RUBRIC.md, current main.tex, execution_r3.tex, tables/execution_r3.tex, historical table generator, supplemental runner/verifiers/controls, native AGT component and official test source, all preflight manifests/snapshots, development eligibility records and E03/E04/E05 final records. Inspected the 14-page PDF's supplemental table pages 9–10. This is not a full typography inspection or a new external literature search. Novelty assessment is restricted to the manuscript's stated contribution relative to its supplied prior-work discussion and primary-source AGT snapshot.

The initial manuscript snapshot read during this review has SHA256:

- paper/main.tex: `9916430a6b74a175718c96f538cf139c6939b9c13364780b6b1cb3d366d0a8d7`
- paper/execution_r3.tex: `cbdcdc7be4cdd9a8a92170b20b1086dcbb4b76a5026a4b55fa762d282e6f922f`
- paper/tables/execution_r3.tex: `89aa80f1a0e1765d203cf8ddca4e960f53ccb4434dfadc72955c399a8c06a354`
- paper/main.pdf: `75446edb495a2706eeea78e30c30ed124f6ad544967f726a82818a95df8a69c1`

Later changes by the parent are outside this initial snapshot until explicitly checked below. The prospective independent subagent review failed before the batch; the weak local-model second opinion and parent triage cannot retroactively become that missing prospective review. This retrospective review has now succeeded and should be dated/labeled accordingly.

## Verdict

**The corrected source supports the bounded descriptive audit, with no unresolved Critical or Major count/measurement-interpretation blocker found.** One newly identified Major issue (M1) was corrected in source during this review; the original finding is retained below. The finite effect counts and availability accounting are supported. The paper cannot support a new defense, natural action-substitution prevalence, general safety/utility superiority, authenticated consent, complete endpoint comparison, or scientific quality >=8. Final PDF regeneration and the minor documentation consistency edits remain to be checked.

The supplement meaningfully improves evidence reliability: three actual adapter implementations replace dictionary labels, native AGT is a real component baseline, final storage is read independently, failed development and missing service output are retained. These improvements do not by themselves establish a substantial new scientific contribution.

## Claim-by-claim checks

| Claim | Verdict | Direct evidence and limits |
|---|---|---|
| Historical grid contains 54 files / 1,620 cells, with nine arms and three orders for each service | supported | Read all retained per-seed JSONs, checked scenario coverage and their saved file hashes; independently recomputed descriptive counts, refusals, costs and assertion totals. No differences from descriptive_r2.json. This verifies saved records, not unknown historical models or their generation. |
| Booked-hotel assertion false positives are assertion-level examples, not a whole-cell false-positive-rate estimate | supported | Read both idx=10 counterexamples and original per-seed records. The 6/9 and 8/9 keyword overlaps are consistent; both whole cells fail other assertions. |
| E03 contains 540 constructed cells on nine evaluation base goals / three adapters | supported | Read 540 case/trace/persisted-state directories. Each guard has 90 cells; repeated faults and guards are not independent tasks. |
| E03 unauthorized effects are 72/0/63/45/0/0 for allow-all/deny-all/name-only/exact-precheck/local-bound/native-AGT | supported | Independently reloaded all file/outbox records and read SQLite tables in read-only mode. Effects total 99/0/90/72/27/27. No storage-integrity discrepancies. Name-only and exact-precheck proxy misses are 63 and 45 cells respectively. |
| Bound controls and native AGT have 9/9 clean utility; deny-all 0/9 | supported | Clean goals have original exact tool/target/value matching and no unauthorized effect. The bound controls tie, so no new-method superiority follows. |
| Native AGT is the unmodified official component at the recorded commit | supported within snapshot provenance | All eight vendored files, including LICENSE and official test module, have Git-blob hashes matching the saved official commit tree at 47abed7446d47e74cfa76d01a5913bb873ffcad9. The saved official test log records 31 passed; I did not rerun tests. It is component integration, not full-framework validation. |
| Local model panel has 108 episodes and 180 requests; statuses 36 completed / 63 stops / 7 turn limits / 2 parse failures / 0 transport errors | supported | Read records, actual request files and all final storage; all counts agree. `completed` is an effect-triggered controller status, not a general semantic task-completion certificate. |
| Local allow-all admits 15 unauthorized effects, all in pending contexts; name-only/native each zero | supported | All 108 final states checked directly. Fifteen effects occur across nine pending allow-all episodes. This natural-proposal panel cannot distinguish name-only from binding. |
| Local native clean utility is 9/9 and recovery is 3/9 | corrected during review | Original “recovery” wording needed work. Revised source now correctly separates 3/9 safe authorized effects in the failure context from 0/9 actual failure→fallback recovery. All three successful native episodes execute t1 immediately on turn zero; six other episodes have actual primary errors. Same distinction holds for allow-all and name-only. See M1. |
| Free panel has 108 planned / 69 observable / 4 transport-error / 35 skipped episodes and 102 requests | supported | Independently counted record statuses and actual request files. Statuses: 38 completed / 29 model stops / 2 turn limits / 4 transport errors / 35 endpoint stopped. Available counts by guard are 21,16,15,17. Missingness is not successful restraint. |
| Free safe completions in recovery contexts follow actual operation failures | supported for observed successful episodes | All 20 successful recovery-context episodes have t0 actual error followed by t1 success: allow-all 7, name-only 5, native 8. Their observed denominators remain incomplete and selection-dependent. |
| HTTP 429 stopping deviated from the protocol | supported | All four transport-error bodies contain `upstream HTTP 429` under outer HTTP 502; detector at model_episodes.py:81 misses the numeric code and uses the three-consecutive-error stop. No retries/substitutions/resumption were found. See M2. |
| Same initial goal/permission and serving request options across guards | supported | Checked every E04/E05 request: same initial messages for each goal/context across observed guards, no base-goal ID in prompt, requested temperature=0 / seed=20261014 / max_tokens=256 / stream=false. Returned IDs match requested IDs in 98 successful free and 180 local responses. Upstream identity is still only a label. |
| Local bytes/runtime are verifiable | supported | Independently SHA256-read current model file and runtime binary, matching launch hashes dde5aa3f…ccdff and 234b05b2…5696b. This identifies the local bytes; it does not independently certify a remote checkpoint or all canonical training/model provenance. |
| Prior Qwen all-abstain and failed Liquid/Cohere candidates remain visible | supported | Read 12 Qwen pilot records: all abstain, including six grants, zero-effect guard replay. Development-r1 has Nemotron six completions / Liquid six parse errors. Cohere has five parse errors and one completion. Local development has three clean and one recovery-context completion. Candidate additions remain exploratory. |

All saved E03/E04/E05 standalone checks report zero errors, with 540/108/108 checked cases and 90/36/36 native binding checks. I independently reproduced the same effect counts and native binding digests rather than accepting those PASS reports alone.

## M1 — Major: failure-context completion is not observed post-error recovery

Initial evidence: execution_r3.tex and Table 8 use “Recovery” and “3/9 recovery goals.” `model_episodes.py:111–112` stops as soon as any safe authorized effect appears. `verify_effects.py:35–45` accepts either individually granted action in the recovery case; it does not require the primary to have failed or enforce action order.

Concrete examples: E05-evaluation-r0/model-3/enqueue_message-{1,2,3}/native_agt/trace.json each contains one event, ticket t1, successful operation, no preceding primary. All nine successes across allow-all/name-only/native share this pattern. File and SQLite recovery-context successes are zero. Thus the local 3/9 is entirely direct fallback, not adaptation to actual failure feedback. The free panel's 20 successful episodes do meet the latter sequence.

Required disposition without rerunning: preserve original outcome fields/counts; label the column “failure-context safe effect” or equally explicit wording; separately report trace-derived primary-error→successful-fallback counts (local 0/9 under native; observed free native 8/8). State that the extra trace-derived measure is a post-review descriptive check. Do not call direct fallback a recovered failure, successful temporal goal completion, or proof of feedback adaptation. Also distinguish controller `completed` from the semantic success concept.

Parent was informed during review and accepted this correction. Independently rechecked revised execution_r3.tex, tables/execution_r3.tex and evidence/supplement/summary.json: “Failure ctx.” and “Reactive” are separate; local native 3/9 vs 0/9 and six primary errors are correct; free allow-all/name-only/native reactive counts 7/5/8 are correct. The source explicitly limits the old field to permission-compatible effects, identifies direct fallback, and declares sequence checking a post-review descriptive secondary audit. M1 is **resolved in revised source without changing raw records or rerunning models**. Original issue remains in this report.

## M2 — Major protocol limitation, already disclosed: free-panel availability and 429 stop defect

The predeclared “stop at first rate limit” rule was not implemented for HTTP502-wrapped numeric429. Four actual error responses exist. Concurrent in-flight requests further prevent interpreting stop as instantaneous cancellation of all work. The records support only the partial observational accounting above.

This is not repaired by relabeling errors or by substituting the local model. Preserve the frozen defective source and raw responses, retain 108 as planned denominator, and keep observed and planned counts visible. Any later repair is a new version and must not retroactively alter E04. The current prose already takes this appropriate restricted position. No complete endpoint-effect comparison is justified.

## Other material limits and minor edits

- **Concurrency coverage:** two workers are launched, and native validation/consumption is not wrapper-serialized. However there is no start barrier or recorded overlapping validation interval. The nine parallel fixtures therefore show two threaded uses, not verified coverage of difficult overlapping schedules. Source inspection confirms the reference store has a locking consume primitive. Keep the finite two-thread wording; do not promote it to race/crash/distributed guarantees.
- **Oracle boundary:** storage readers use direct field comparisons without gate canonicalization or receipt success. The standalone checker derives grants from the base-goal manifest and reimplements native digest encoding. This is useful implementation separation. It still shares the parent author and authored truth source; action-effect quota correctness cannot authenticate actual approver identities, receipts, tickets, or all mediation paths. The paper's present exclusions are necessary.
- **Time boundary:** the component's coordinator uses a fixed time while dataclass metadata uses wall time. The manuscript explicitly discloses this; expiry/chronology is unmeasured, not disproven or validated. Current source snapshots need to remain as run.
- **Partition boundary:** identifier-disjoint development/evaluation is implemented and prompts are frozen; every supplemental goal still shares three templates and authored permission rules. This is not an external task-distribution split or model-training contamination check.
- **Feasibility selection:** eligibility is correctly frozen before evaluation for each candidate. Adding candidates after failures limits any prospectively fixed model-selection or family comparison. One verified local blob plus a serving label does not fulfill two verified model-family replication.
- **Public reproducibility:** local evidence and source snapshots are extensive, but no independent public artifact endpoint is issued. Abstract “We release” should mean an actual accompanying public release or be stated as prepared material until release. Model/runtime retrieval provenance and redistribution/licensing still require final author packaging decisions.
- **Claim ledger scope:** its blanket statement excluding all “model-effect” and “task-completion” claims is stale relative to the finite supplemental effect claims. Update it to exclude generalized/causal/model-comparison claims while explicitly allowing the verified finite local effect and clean exact-match outcomes.
- **Review chronology:** update the AI-use section so the failed prospective subagent review and this completed retrospective independent AI review are not conflated. Neither is human peer review.

## Research gaps versus finite-audit runnability

The limited offline matrix and model panels were feasible, and the frozen files support finite descriptive reporting. Their feasibility and engineering validation should not be treated as proof of novelty or significance. No further model batch is needed to correct M1; the relevant traces already exist. No Critical data corruption or unexplained count mismatch was found.

Major research gaps remain for a strong scientific contribution: no independently sourced natural failure distribution or externally labeled authorization corpus; only nine evaluation templates/instances; no observed local action-substitution advantage of native over name-only; established binding mechanisms simply pass their authored contracts; historical policies remain mismatched; public artifact regeneration and remote identities remain incomplete. The large historical cell count and expanded constructed grid do not remove these gaps. New evidence would need an externally grounded question and sufficiently distinct contribution; merely increasing model calls on these templates would not establish one.

## Uncalibrated independent AI score using unchanged rubric

This scores the present **bounded descriptive audit paper plus supplied evidence**, not a new defense, submission readiness, acceptance probability, or all future corrected versions. It is not calibrated against venue decisions. It is independent of the previous 5.0 anchor and of any requested target score.

| Dimension | Weight | Score / 10 | Reason |
|---|---:|---:|---|
| Novelty | 25% | 4.0 | Useful concrete measurement defects, but binding, zero-vs-utility distinctions and designed TOCTOU examples are established; no strong new external empirical finding. |
| Claim/evidence reliability | 30% | 8.0 | Extensive count/source/state checks and honest limitations; M1 is corrected in revised source, while historical response/identity gaps and service censoring remain. |
| Significance | 20% | 4.5 | Practically instructive audit, limited beyond this harness and nine authored goals. No demonstrated robust external metric ranking change or deployment benefit. |
| Reproducibility | 15% | 7.5 | Strong local hashes, snapshots, traces and deterministic offline checks; unknown historical and remote checkpoints, model/runtime retrieval details and no independent public release constrain full regeneration. |
| Presentation | 10% | 8.0 | Clear bounded framing and readable original supplemental tables; revised recovery terminology is precise. Minor ledger/review chronology consistency and updated PDF checks remain. |

Weighted total for the corrected source = 0.25×4.0 + 0.30×8.0 + 0.20×4.5 + 0.15×7.5 + 0.10×8.0 = **6.225/10, rounded 6.2/10**. The original snapshot with M1 was 6.025/10 (6.0 rounded). The correction improves precision/reliability, not novelty or significance; it cannot alone close the gap to 8.

## Resolution tracking

- M1: resolved in revised source; original record kept. Latest checked execution_r3.tex SHA256 `7fb2338e1fd1b1dfd235bb20c99a569c6322686f7e9b32991ed6a9300466f7af`, table SHA256 `7e589f14408d00d1e376e42e540ed7d590b0462af6ae20909a2005f2ec663202`.
- M2: historical protocol defect retained; current finite-accounting restriction is appropriate.
- Two-thread fixture wording: revised source now states there is no barrier/admission-interval evidence of overlapping race schedules; checked and appropriate.
- At this recheck the PDF still had the initial hash, so source corrections were not yet verified in a regenerated PDF.
- No code, model output, manuscript, raw experiment record or data was changed by this reviewer.

## Final acceptance addendum — 2026-10-14

At the parent's request, performed the final read-only acceptance check after recompilation. Only this review was amended. No experiments, inference, existing verification scripts, analysis generators, or compilation were run by this reviewer. Original Major findings and the 6.2/10 uncalibrated AI score above are unchanged. This addendum supersedes the earlier pending-PDF and minor-documentation status notes, while retaining their chronology.

**Final scoped verdict: accepted for the stated finite descriptive audit. No unresolved Critical/Major count or interpretation blocker found in this review.** This is an independent retrospective AI record audit, not human peer review, a claim of >=8 quality, or authorization/verification of submission or public release.

Checks completed:

1. Abstract now says “We prepare local finite-count recomputation and execution provenance.” The generated main.tex, generator template and final PDF page 1 agree; it no longer claims an already issued public release.
2. CLAIM_LEDGER.md scope now permits verified finite adapter effects and clean exact-match completion, explicitly excludes generalized/causal effects and population safety, and states that failure-context effects do not certify temporal task completion. The generator contains the corresponding update.
3. The generative-AI section in main.tex and final PDF page 12 separates the failed initial prospective subagent review from the subsequently completed retrospective independent AI review and its recovery-label correction. It separately labels local-model opinions and parent checks, and expressly says none is human peer review. The generator agrees.
4. Final main.pdf is 14 pages. Read the relevant PDF text directly and visually inspected final-page-01.png, final-page-10.png, final-page-11.png and final-page-12.png. Table 8 on page 10 visibly contains distinct “Failure ctx.” and “Reactive” columns. Native local clean=9/9, failure-context safe effect=3/9 and reactive=0/9 are correct and legible. Pages 10–11 explain direct fallback, six observed primary-operation failures, the old verifier's effect-only definition and post-review secondary sequence audit. Free native remains 8/8 observed reactive recovery with availability limits. No clipping/overlap was seen on these checked pages; this does not assert inspection of every final page.
5. M1 is resolved in both the source and final rendered PDF. M2 remains an explicitly disclosed historical protocol defect. The two-thread coverage exclusion remains appropriately stated. No change to raw records or original endpoint outcomes is required for these editorial/semantic dispositions.

Final accepted artifact SHA256 values (paths relative to `/home/liuzewen/arxiv-publication/papers/approval-gates-r3`):

| Artifact | SHA256 |
|---|---|
| paper/main.tex | `e1a354be0c9c2d10448c89da5cb7b441e9300717ca73cc4f32d3de841d743cd8` |
| paper/execution_r3.tex | `7fb2338e1fd1b1dfd235bb20c99a569c6322686f7e9b32991ed6a9300466f7af` |
| paper/tables/execution_r3.tex | `7e589f14408d00d1e376e42e540ed7d590b0462af6ae20909a2005f2ec663202` |
| paper/main.pdf | `3b8065c8771229222a53294eb1e0108cb462ce8a868242f576f122a88cc01572` |
| CLAIM_LEDGER.md | `17dac732bb5f2e9ab55af1d953ceab8d9dab7ef2f67fd2f3d7586a323894279b` |
| scripts/make_execution_supplement.py | `621ddfb9f90dd7d180da88e5e4903f8d6912c2861453ce49a87d65385acf974e` |
| reports/r3/final-page-01.png | `1ef3f9ac7a746c68be437c175099166f52fff30e5ff3265338a1a3959c7cb2d2` |
| reports/r3/final-page-10.png | `1dd0654948fd690d9abcd4eda364cfec7d382c1ab6501d7ecda987be3e00d43a` |
| reports/r3/final-page-11.png | `0fcc9f0a166d44594198d0d2b1f3f7654a068cde74f3e5fd72fa1280b4bec98c` |
| reports/r3/final-page-12.png | `b3d21f8f05b65df59b27ef4ceb86e447f758757dac3512148a6be82b7e05f1e1` |

The evidence still supports only the bounded descriptive claims and limitations already listed. Acceptance of the corrections does not close the novelty/significance or external-validity research gaps.
