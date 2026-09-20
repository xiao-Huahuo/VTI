# Prior-Art Delta V32 — C33 Novelty Red-Team

Date: 2026-09-19

## Decision

V32 materially narrows C33. The generic methodological thesis that an agent benchmark must clear residual state, verify reset/isolation, and avoid cross-run interference is already occupied by prior work. C33 must not present those principles as novel.

The surviving research object is **memory-benchmark-specific empirical systems evidence**: identify hidden provider state that remains behaviorally active outside a benchmark's nominal reset/isolation surface, demonstrate the mechanism in pinned real integrations, and measure whether that hidden state changes representation, retrieval, answer, or score under paired replay.

## Direct and near-direct prior art

### 1. Agentic Benchmark Checklist (Zhu et al., 2025)

The checklist explicitly requires residual data and state to be fully cleared between runs (T.4) to preserve task independence. This occupies the broad claim that benchmark trial hygiene requires state cleanup.

Source: https://arxiv.org/abs/2507.02825

### 2. When Is an Agent Evaluation Over? Outcome Finality and Cross-Unit Separation (Casheekar, 2026)

This is the most important V32 discovery. The paper separates outcome finality from cross-unit separation, states that a run may be counted separately only when no relevant operation or shared state can alter another run, and explicitly requires isolation/reset to be verified rather than merely invoked. Its controlled replay shows a delayed write changing the next run's score under shared state, with the effect absent under namespacing or verified reset. It also proposes an open-effects record for persistent resources and operations.

This occupies all generic C33 claims of:

- cross-run contamination as an evaluation-validity problem;
- reset success as something requiring evidence rather than an API return;
- verified reset as a general evaluation method;
- score changes caused by persistent shared state in a constructed agent-evaluation setting.

Source: https://arxiv.org/abs/2608.14940

### 3. MemSecBench (Chen et al., 2026)

MemSecBench runs exact agent/memory/LLM configurations in isolated runtimes, creates independent branches from verified post-Write memory state, and evaluates persistence and repair using backend-state evidence rather than trusting agent or delete-call claims. This occupies broad novelty around state snapshots, matched state branching, and backend-state adjudication in agent-memory evaluation.

Its scientific target is memory-poisoning lifecycle security, not trial-to-trial benchmark contamination, but C33 may not claim the underlying verification pattern as new.

Source: https://arxiv.org/abs/2607.27080

### 4. Interactive Evaluation Requires a Design Science (Xuan et al., 2026)

This work establishes the broader claim-matched evaluation framing for interactive systems: trajectory evidence and evaluation procedures must support the system-level claims drawn from them. C33 should treat this as conceptual background rather than claim novelty for "evaluate the system, not a single model call."

Source: https://arxiv.org/abs/2605.17829

### 5. Stopping Is Not Containing: Measuring Post-Stop Residual State in AI-Agent Systems (RAISE 2026)

A workshop program and institutional research record confirm the title and publication status. Full text was not located in the V32 search, so no substantive result is attributed. The title is close enough to C33's residual-state theme that it remains an unresolved novelty risk and should be inspected if the paper becomes accessible.

Sources:
- https://raise-workshop.github.io/
- University of Hertfordshire research profile for Liang Chen

## Surviving contribution boundary

C33 survives only as an empirical, domain-specific measurement study if the real evidence becomes strong enough. The prospective contribution is:

1. audit real agent-memory benchmark/provider integrations at pinned revisions;
2. enumerate provider state surfaces that are behaviorally read by the next memory transition;
3. show cases where benchmark-visible reset/isolation covers only a strict subset of those active surfaces;
4. produce independent per-surface receipts for the affected integrations;
5. run matched native-reset versus verified-clean replays and measure the causal effect chain separately at representation, retrieval, answer, and score levels;
6. include lifecycle-safe implementations as negative controls.

The attestation machinery is supporting infrastructure, not the primary novelty claim.

## Claims removed in V32

C33 must not claim any of the following as original:

- residual state between agent benchmark trials is a new evaluation problem;
- benchmark independence requires clearing legacy state;
- reset/isolation should be verified rather than trusted;
- persistent shared state can change later-run scores in agent evaluation;
- backend-state evidence is preferable to trusting a delete/reset call;
- matched branches from a common state snapshot are themselves novel.

## Kill rule tightened

C33 remains provisional only because no direct source was found in the V32 targeted search that performs the same **agent-memory-benchmark-specific multi-integration empirical audit** of hidden behaviorally active provider state with paired native-reset versus verified-clean downstream replay.

If the Redis and MemArena exact-stack paired replays are downstream-null, or if only one integration exhibits a material observable effect, C33 should be killed as a main-paper idea and retained as benchmark audit/bug-report material. A purely conceptual paper is no longer defensible after this V32 prior-art pass.
