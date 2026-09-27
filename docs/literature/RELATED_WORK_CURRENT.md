# C33 current related-work boundary

Date: 2026-09-27. This is the active citation and claim map for writing; older version documents remain historical. Citation keys refer to `references.bib`. Literature claims below are based on the cited primary papers or official project artifacts. The final submission still needs full-text verification of every sentence against the manuscript draft.

## What C33 must acknowledge as prior work

| Established idea or result | Sources | Consequence for C33 |
| --- | --- | --- |
| Agentic benchmark builders should clear residual task state and justify task independence. | `AgenticChecklist2025` | The need for cleanup/reset is background, not a VTI invention. |
| Outcome finality and cross-unit separation are distinct; a delayed write can change a later run's score under shared state, and verified isolation can remove that constructed effect. | `CrossUnitSeparation2026`, `InteractiveDesignScience2026` | Neither “evaluation units must be independent” nor “reset needs evidence” is new. VTI must add a specific **agent-memory benchmark intervention and quantitative audit**. |
| Isolated runtime, matched branches and backend-state evidence already appear in agent-memory security evaluation. | `MemSecBench2026` | Checkpoints, branching and receipts are necessary engineering, not by themselves a novel method. C33 targets benchmark trial boundaries, not malicious-memory Write–Execute–Forget security. |
| Counterfactual “as if target information had never been seen” and selective execution-state replay are established for forgetting. | `ExecutionUnlearning2026` | VTI should not claim first counterfactual-state equivalence or first cross-layer state reconstruction. Its estimand is predecessor-to-target **benchmark measurement dependence**. |
| Memory control-plane supersede/release/purge and heterogeneous adapters have been studied. | `ForgetEval2026` | VTI is not a new memory deletion benchmark; it asks whether independent evaluation cases stay independent after a provider's native reset. |
| Memory benchmark comparisons are sensitive to model, embedding, retrieval and write-path choices. | `MemDelta2026` | Match or freeze configurations, disclose local substitutions and avoid attributing cross-config effect-size differences to backend alone. |
| Automated auditing can uncover benchmark defects and alter rankings. | `AutomatedBenchmarkAudit2026` | “Auditing benchmarks changes conclusions” is already established broadly. C33 must demonstrate lifecycle-specific causal measurement, not relabel general auditing. |
| Persistent user-state interventions, task-order fragility, and state-scope effects have existing studies. | `TemporalIntervention2026`, `TaskOrderFragility2026`, `ScopeBeforePersist2026` | Do not claim the first temporal intervention, order dependence or memory scope control. C33's object is **independent benchmark cases under reset**, not intended within-agent continual adaptation. |
| Memory bank, retrieval and answer failures can be separated; task-level memory benchmarks already report cost/latency. | `ATMA2026`, `DolphinBench2026`, `LongMemEval2024`, `MemArena2026` | VTI cannot claim first pipeline decomposition or first outcome/cost-aware memory evaluation. It can use those layers to trace **cross-case** influence and its scoring consequences. |
| Real Mem0 reset defects have already been reported. | `Mem0QdrantResetIssue2026` and other provider issues | Concrete bug existence motivates the question but is not the main novelty. The cited Qdrant issue's correction makes its scope platform-dependent. |

## Full-text checks on the newest adjacent papers

- **Agentic Benchmark Checklist**: its T.4 explicitly calls for clearing legacy data/state before an intended independent task. This is a checklist condition, not a provider-specific randomized predecessor intervention. [Primary full text](https://arxiv.org/html/2507.02825v5).
- **MemSecBench**: its Write–Execute–Forget study uses isolated runtimes and lets Execute and Forget start independently from the same verified post-Write memory state; it matches harness/model conditions across memory backends. Its causal object is malicious-memory lifecycle security, rather than whether a benign benchmark predecessor remains active after native reset. [Primary full text](https://arxiv.org/pdf/2607.27080).
- **A-TMA**: its problem is old/current/transition facts coexisting within a user's memory stream. The paper defines a bank–retrieval–QA failure decomposition and proposes state-labeled evidence packets. It does not, in its problem and method sections, test whether one independent benchmark *case* changes the next after a reset. C33 should cite A-TMA for the layer decomposition and then state the distinct trial-boundary estimand. [Primary full text](https://arxiv.org/html/2607.01935v2).
- **Scope Before You Persist**: its unit is a recurring code-repair task family and its persistent object is a deployed skill/policy. The experiment changes which family may retrieve an accepted skill, including randomized task-order streams. Its scope-matching idea is close enough that C33 must not claim first memory-scope certification or first order sensitivity; VTI asks whether a benchmark's nominally separate evaluation units remain independent after native reset. [Primary full text](https://arxiv.org/html/2609.29144v1).
- **Cross-Unit Separation** remains the closest generic evaluation-boundary paper. Its full text explicitly discusses verified fresh state, reset, delayed writes, open effects and score interpretation. C33 must locate novelty in its *memory-backend-specific randomized predecessor/shadow design*, stochastic controls, provider receipts and measured evaluation consequences. [Primary full text](https://arxiv.org/html/2608.14940v3).

These are scope comparisons, not a proof that no identical unpublished method exists. Refresh the search before submission.

## Statistical sources for V57

Fisher exact randomization under a **sharp no-effect null** is an existing causal-inference technique (`RandomizationWeakNull2021`). The Euclidean energy statistic is established (`SzekelyRizzo2013Energy`), as is the partial-conjunction idea that asks whether at least (r) of (n) hypotheses are false (`BenjaminiHeller2008PartialConjunction`). Their formulas should be cited, not marketed as original VTI mathematics. What may be new is a correctly randomized, provider-isolated application to agent-memory **trial boundaries** with an ordered retrieval observable and explicit failure labels. The necessary no-interference and runtime-identity assumptions remain to be verified in V57 engineering preflight.

## Current contribution sentence for a manuscript draft

> We audit trial isolation in agent-memory benchmarks as a predecessor-to-target causal property, separating native reset from a pristine shadow under matched predecessor workload. We calibrate stochastic provider behavior with randomized repeated trials, retain immutable provider/runtime receipts, and measure propagation from retrieved content to answers and benchmark outcomes. Our claims are limited to the pinned systems, targets, assignment design and observable endpoints actually tested.

This paragraph is a **target claim contract**, not an assertion that all proposed V57 experiments have already succeeded.

## Version bridge and wording rules

- V32 narrowed novelty away from generic reset verification. The present related work **restores** its Agentic Benchmark Checklist and MemSecBench citations, which were not named in the user's original `IDEA.md`.
- V42–V55 add system-specific causal evidence but cannot inherit novelty over generic cross-run contamination from V32. V56 exposes a stochastic-clean-control limitation without a native-reset result. V57 proposes a randomized method but remains unfrozen; it cannot be written in past tense as an accomplished contribution.
- Historical `PASS` labels belong to their original frozen protocols. In the current stochastic design, failure to reject a sharp null is **not** evidence of equivalence or a general isolation certificate; use `INFLUENCE_NOT_DETECTED` and report (n), scope and power limits.
- The term **cross-trial memory** in agent-learning work can mean intentional learning across repeated attempts. Define C33's term as unintended influence between evaluation cases that the benchmark treats as separate observations.

## Still open

1. Resolve V32's title-level warning on *Stopping Is Not Containing*: acquire and inspect a full text before attributing a method or result. Keep it off the factual comparison table until then.
2. Verify final venue status and version metadata near submission. `references.bib` currently contains DOI-registry records for the arXiv versions and three journal statistics papers; it is a **starter library**, not a final venue-normalized bibliography.
3. Build a final claim-to-artifact ledger after V57 and order/score/reset-policy studies. Literature scope and empirical scope must agree in every manuscript claim.
