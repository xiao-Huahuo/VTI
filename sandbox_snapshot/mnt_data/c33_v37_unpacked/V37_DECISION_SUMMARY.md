# V37 Decision Summary

Date: 2026-09-19
Project: AM-AUTO-20260918-R1
Primary candidate: C33
Working title: Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit

Status: `FORMAL_PILOT_READY_V37_C33_PARTIAL_STATE_PROMOTION_TWO_HARNESS_SOURCE_CHAINS_FOUND`

## Decision

V37 adds a new descriptive lifecycle class, `T6 PARTIAL_STATE_PROMOTION`, supported by two independent benchmark harnesses: Microsoft Memora and LightMem.

T6 means an incomplete persistent memory state is later accepted as a completed benchmark unit because resume/retry logic tests coarse state existence rather than the unit's actual construction-completion contract.

## Finding A: Microsoft Memora LongMemEval

Pinned repository: `microsoft/Memora@dec3f8f2444eace7004fc084abe1be9f3d88270e`.

The documented retry path uses `--skip-existing` to retry failed questions. Each question uses stable scope `question_<question_id>` and a persistent Chroma collection. Session-level add failures are caught and construction continues. `check_question_has_memories()` then defines existing as `collection.count() > 0`, so any partially populated question is skipped on retry. The search stage still evaluates the full selected question set from the same stable scope.

A second source finding affects the direct documented `memory.force_rebuild=True` route. `run_memora.py` does not delete the persistent path, while `process_conversation()` skips `client.clear()` when `force_rebuild` is true. Reusing a store name therefore does not establish a verified fresh rebuild. The separate multi-process shell wrapper is safer because its `--force-rebuild` branch explicitly removes split memory-store directories first.

No committed raw LongMemEval runtime artifact is present, so these remain source/control-flow findings rather than published-score claims.

## Finding B: LightMem MemZero

Pinned repository: `zjunlp/LightMem@8449d574df6bae1bdf3314a1564da65e2f37e046`; baseline pin `mem0ai==1.0.2`.

Memory construction uses deterministic per-trajectory users and persistent Qdrant by default. Writes occur incrementally. `MemZeroLayer.add_message()` catches broad write failures and returns. At construction start, `load_memory()` acts as the completion predicate. If the explicit config/pickle snapshot is absent or unusable, it falls back to `_has_any_memory()`, which returns true when the persistent backend contains even one memory. `memory_construction()` then exits early and `memory_search()` later consumes that accepted store.

Thus an interrupted or partially successful construction can be promoted to complete by the next rerun. The documented `--rerun` flag also only bypasses the load/skip guard; it does not delete the persistent collection first, so it is not independently equivalent to a fresh rebuild for persistent backends.

## Negative control: IronCurtain LongMemEval

Pinned repository: `provos/ironcurtain@c1ef8ad66b3c6be042d6a51a5721bb0df96dc2d5`.

Each question receives a disposable SQLite DB. The whole question runs inside `try/finally`, and the DB plus WAL/SHM sidecars are removed before an incomplete question can become a completion checkpoint. The checkpoint row is appended only after `run_question()` returns. Resume therefore re-runs incomplete questions from a fresh per-question store on the ordinary path.

## Consequence

C33 is no longer tied only to reset incompleteness or Mem0's message sidecar. The audit now contains a second lifecycle failure mode in which partial primary memory state itself is promoted to a completed trial.

V34's primary Redis/MemArena pilot remains unchanged. V37 is exploratory external evidence and does not alter preregistered sample selection, endpoints, or statistics.

Formal large-scale experiment remains `NOT_STARTED`.
