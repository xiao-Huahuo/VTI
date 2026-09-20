# V32 Decision Summary — C33 Novelty Red-Team

Date: 2026-09-19

Status: `IDEA_VALIDATION_V32_C33_EMPIRICAL_AUDIT_ONLY_GENERIC_RESET_NOVELTY_OCCUPIED_RUNTIME_EFFECT_PENDING`

## Decision

C33 remains the sole primary candidate, but V32 removes most of its remaining conceptual-method novelty.

A newly surfaced 2026 paper, **When Is an Agent Evaluation Over? Outcome Finality and Cross-Unit Separation**, directly formalizes cross-run shared-state interference, requires isolation/reset to be verified, and demonstrates a next-run score change that disappears under namespacing or verified reset. The 2025 Agentic Benchmark Checklist already requires residual state to be cleared between runs. MemSecBench additionally uses isolated runtimes, verified backend memory state, and matched branches from a common post-Write state.

Therefore C33 must not claim that verified reset, cross-run contamination, state postconditions, matched state branching, or backend-state adjudication are new ideas.

## Surviving paper object

The only defensible main-paper direction is now an **empirical systems audit of agent-memory benchmarks**:

- find behaviorally active provider state hidden outside nominal benchmark reset/isolation surfaces;
- reproduce concrete mechanisms in pinned real benchmark/provider integrations;
- emit independent per-surface receipts;
- measure native-reset versus verified-clean differences at representation, retrieval, answer, and score levels;
- contrast affected integrations with lifecycle-safe negative controls.

The working title is changed from `Trial-State Attestation for Agent-Memory Benchmarks` to:

**Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit**

Attestation remains tooling, not the novelty headline.

## V32 Redis evidence

The new source-grounded control-flow fixture executes both real lifecycle routes that reuse the same Redis LongMemEval user scope:

1. in-process retry after a successful partial ingest;
2. crash/resume with the same run name and example index before an answer record exists.

Both routes reproduce the same state asymmetry: native scoped reset empties vector state while retaining the message sidecar, and the first subsequent inferred-add transition receives non-empty Last-k context. Five offline tests pass.

This remains E1 evidence. Exact Mem0 representation/retrieval/answer/judge effects still require the credentialed frozen runtime.

## Tightened kill rule

C33 is now contingent on empirical strength rather than conceptual novelty. Kill it as a main-paper idea if either of the following holds:

- Redis and MemArena exact-stack paired replays are downstream-null; or
- fewer than two real integrations survive mechanism reproduction and fewer than one reaches a representation/retrieval effect.

In that case, preserve the findings as benchmark audit reports, upstream bug evidence, and reproducibility tooling.

Formal Experiment remains `NOT_STARTED`.
