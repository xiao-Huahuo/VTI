# V40 Decision Summary

Date: 2026-09-19

Project: `AM-AUTO-20260918-R1`

Primary candidate: `C33`

Working title: **Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit**

Status: `FORMAL_PILOT_EXECUTION_BLOCKED_V40_C33_REDIS_COHORT_FROZEN_RUNTIME_PACKAGE_READY`

## Decision

The provider-free preparation stage for the frozen V34 Redis formal pilot is complete. V40 does not revise the V34 protocol. It materializes the deterministic n=12 cohort, adds exact dataset provenance checks, converts the V32 single-case exact replay into a 12-case runner, freezes the V34 bootstrap analysis, and adds fail-closed runtime validation.

The Redis cohort is now concrete rather than implicit. All 500 LongMemEval-S questions satisfy the predeclared `>=4 sessions` eligibility rule in the audited public metadata, and the first 12 SHA-256-ranked question IDs are frozen in `redis_v34_cohort.json`. Formal execution recomputes the cohort from the exact upstream JSON before any model call, so the public mirror used for provider-free materialization cannot silently change the sample.

## Offline verification

Four new V40 offline tests pass. They verify deterministic cohort hashes/order, the E0-E4 evidence mapping, and synthetic 12-case aggregation. The inherited V32 retry/resume fixture also still passes all five tests.

All V40 Python files compile under the current sandbox.

## Runtime gate

The current sandbox fails exact-runtime preflight by construction. It runs Python 3.13.5, has no exact Redis checkout, lacks `mem0ai==2.0.19` and `qdrant-client`, lacks the OpenAI package in this environment, has no `OPENAI_API_KEY`, and does not contain the pinned LongMemEval file. The preflight records each missing condition and exits nonzero.

The next scientific action is therefore execution of the V34 Redis n=12 paired pilot in an isolated Python 3.10-3.12 environment with the exact benchmark checkout, locked dependencies and an OpenAI credential. No additional sample design or protocol design remains before that run.

## Claim discipline

Formal Experiment remains `NOT_STARTED`. No Redis E2/E3/E4 outcome claim is released from V40. The public and source-level evidence accumulated through V39 remains unchanged. Generic reset/isolation principles remain prior art.
