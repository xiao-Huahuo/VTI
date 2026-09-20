# V32 Handoff

Canonical root: `/Research/AgentMemory/AM-AUTO-20260918-R1`

Primary candidate: C33

Working title: **Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit**

Status: `IDEA_VALIDATION_V32_C33_EMPIRICAL_AUDIT_ONLY_GENERIC_RESET_NOVELTY_OCCUPIED_RUNTIME_EFFECT_PENDING`

## Critical V32 correction

Do not resume with `Trial-State Attestation` as a method-novelty thesis.

Generic residual-state cleanup, verified reset/isolation, cross-unit separation, matched state branching, and backend-state verification are occupied by prior art, especially Zhu et al. 2025, Casheekar 2026, and MemSecBench 2026.

C33 survives only as a memory-benchmark-specific empirical audit if the real integrations produce sufficiently strong evidence.

## Current evidence ladder

- AMB × Mem0 Cloud: public historical stale retrieval confirmed; recovered trace score delta is zero.
- Redis × Mem0 2.0.19: source mechanism + executed pre-LLM consumption + V32 retry/resume control-flow coverage; exact downstream pairing pending.
- MemArena × Mem0 2.0.11: source mechanism and natural protocol reachability; exact paired replay pending.
- MemoryData: lifecycle-safe negative control.
- ForgetEval infer=False: sidecar-mechanism negative control.

## New V32 executable work

`36_novelty_redteam_v32/C33/code/` contains:

- `redis_retry_controlflow_fixture_v32.py`
- `test_redis_retry_controlflow_fixture_v32.py`
- `preflight_redis_exact_v32.py`
- `redis_exact_paired_probe_v32.py`
- `validate_redis_result_v32.py`
- `run_redis_exact_v32.sh`

The current ChatGPT runtime is intentionally classified as exact-runtime blocked because it is Python 3.13, lacks `mem0ai` and `qdrant-client`, has no OpenAI API credential, and has no direct GitHub network access.

## Next research action without user intervention

Continue public-trace and source-level audit work, prioritizing additional observed real contamination or strong negative controls. Avoid spending cycles polishing a generic attestation framework until an exact runtime establishes E2+ downstream effect.

When a credentialed runtime becomes available, run the frozen Redis V32 package first. Scale only if E2+ appears.
