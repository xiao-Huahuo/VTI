# V37 Handoff

Project: AM-AUTO-20260918-R1

Primary candidate: C33

Status: `FORMAL_PILOT_READY_V37_C33_PARTIAL_STATE_PROMOTION_TWO_HARNESS_SOURCE_CHAINS_FOUND`

## New lifecycle class

`T6 PARTIAL_STATE_PROMOTION`

Definition: persistent state from an incomplete construction attempt is later accepted as a completed benchmark unit because the resume/checkpoint predicate tests coarse state existence rather than completion.

## Source-positive A: Microsoft Memora

Commit: `dec3f8f2444eace7004fc084abe1be9f3d88270e`.

Key chain: stable `question_<question_id>` scope, persistent Chroma collection, session add exceptions logged and continued, `--skip-existing` tests only `collection.count() > 0`, retry skips the whole partially built question, and search then consumes that same scope.

Additional finding: direct `memory.force_rebuild=True` skips per-question `clear()` and does not itself delete the persistent store. The parallel shell wrapper explicitly removes stores first, so the two documented rebuild routes have different freshness semantics.

## Source-positive B: LightMem MemZero

Commit: `8449d574df6bae1bdf3314a1564da65e2f37e046`; Mem0 pin: `1.0.2`.

Key chain: deterministic trajectory user/save directory, persistent Qdrant, incremental writes, swallowed add failures, `load_memory()` fallback to "any backend memory exists", construction skip on that predicate, and later retrieval from the same accepted store.

Additional finding: `--rerun` bypasses the load/skip guard but performs no reset of the persistent MemZero collection.

## Negative control

IronCurtain LongMemEval uses a disposable per-question SQLite DB with `finally` cleanup and writes the completion checkpoint only after the full question returns.

## Evidence discipline

Memora and LightMem findings are E0 source/control-flow evidence. No raw provider runtime trace or published score effect is claimed.

Do not change V34 primary pilot.

Next: search for Memora/LightMem raw runtime artifacts or documented published-run commands, then retain the Redis/MemArena exact paired protocol for credentialed execution.
