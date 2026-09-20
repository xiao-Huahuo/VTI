# V33 Provisional RQ Freeze

Working title: **Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit**

## Scope

The paper is an empirical benchmark-systems audit. It does not claim invention of reset hermeticity, verified isolation, state postconditions, matched branching, or generic cross-run contamination analysis.

## RQ1: Where does behaviorally accessible trial state escape the lifecycle boundary declared or implied by agent-memory benchmarks?

Unit of analysis: pinned benchmark-provider integration. For each integration, enumerate state surfaces and compare the harness lifecycle action with the state surfaces read by subsequent benchmark transitions.

Primary evidence: source audit plus public traces or exact runtime receipts. A source-only mismatch is reported separately from an observed contamination event.

## RQ2: When hidden state is behaviorally visible, what measurement effect does it have?

Outcome ladder is kept separate:

`state -> representation -> retrieval -> answer -> score`

Report the highest directly supported level for each event. Do not infer score impact from retrieval impact alone.

For committed public traces, use provenance-limited scorer counterfactuals that modify only identified stale/residual rows. Label them trace counterfactuals rather than clean-rerun estimates.

For runnable systems, use paired native-lifecycle versus independently verified-clean replay from matched pre-branch state.

## RQ3: Which lifecycle designs prevent the observed failure surfaces?

Use implementation-level negative controls rather than generic advice. Current controls include MemoryData's trial-local Mem0 substrate and ForgetEval's `infer=False` path for the specific Mem0 message-sidecar mechanism.

## Primary study set

Positive/public evidence:

- Agent Memory Benchmark v2 × Mem0 Cloud.
- Agent Memory Benchmark v2 × Zep Cloud.

Controlled paired-runtime targets:

- Redis Agent Memory Benchmark × Mem0 OSS 2.0.19.
- MemArena × Mem0 OSS 2.0.11.

Negative controls:

- MemoryData × local Mem0 lifecycle-local state.
- ForgetEval × Mem0 `infer=False` for sidecar inactivity.

## Outcome reporting rule

Every result table must distinguish:

- mechanism/source support;
- observed state contamination;
- observed retrieval effect;
- trace-restricted score effect;
- paired-runtime score effect.

A blank higher-level cell means unmeasured, not zero.
