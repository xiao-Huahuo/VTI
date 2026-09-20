# V28 Handoff — Agent Memory Reset Attestation

Canonical state: V28 supersedes V27 as the current handoff. V27 remains the source of the first MemArena sidecar mechanism and its exact scripts.

## Current candidate

C33: **Sidecar-Aware Reset Attestation for Agent-Memory Benchmarks**.

Status: `IDEA_VALIDATION_V28_C33_CROSS_INTEGRATION_RESET_CONTRACT_MISMATCH_SOURCE_PROVED_OUTCOME_PENDING`.

Do not revert to the earlier `>100 memories` pagination-only framing. The pagination defect remains a secondary independent branch. The primary mechanism is behaviorally active state that survives the adapter's nominal reset.

## Frozen positive integrations

### A. MemArena

- repo: `stirelli/memarena`
- commit: `821752b8994b2b1927c5b6d3087c4e24670f13a9`
- Mem0: `2.0.11`, commit `f2532f072fdefa4c90264acc80af0984309f8b06`
- benchmark: LongMemEval-V1 Day-3, sample 200, seed 42
- primary pilot: exact Day-3 n=15 add-latency subsample
- failure surface: repeated-run / separate-Qdrant-store while default `history.db` remains shared

### B. Redis Agent Memory Benchmark

- repo: `redis/agent-memory-server`
- commit: `94192c39e2a4a154f441a5411e3d73c4f54974a6`
- benchmark subproject: `agent-memory-benchmark`
- lockfile: `mem0ai==2.0.19`
- Mem0 tag commit: `dc82354e143c2581d505d581a00286d6ef8c3605`
- benchmark: LongMemEval V1 runner
- user scope: `benchmark-<run_name>-<index>`
- failure surface: mid-ingest retry and incomplete-run resume

## Core invariant

Reset success is not an API-return event. It is a postcondition over every persistent provider state surface that can influence the next trial.

For current Mem0 evidence, verify both:

- vector state `V_x = 0`
- message-buffer state `M_x = 0`

Do not require unrelated audit state to be empty unless runtime tracing shows it is behaviorally read.

## Current source evidence

Mem0 2.0.11 and 2.0.19 both:

- keep default message state in `${MEM0_DIR:-~/.mem0}/history.db` unless configured otherwise;
- read scoped `last_messages` during normal inferred add;
- save messages under a deterministic entity scope;
- expose scoped `delete_all(...)` that deletes vector memories but not the message buffer;
- expose global `reset()` that is broader, but neither audited benchmark adapter uses it for per-scope reset.

Upstream prior art already covers stale message-buffer behavior and older global-reset defects. Novelty must stay at the benchmark-provider reset-contract and measurement layer.

## Negative controls

- ForgetEval × Mem0: `infer=False`, message sidecar inactive.
- Basic Memory published Mem0 matrix: `infer=false`; default run id random and grouped run ids are further namespaced.
- MemArena Graphiti: first reset whole-store wipe.
- MemArena Letta: first reset deletes/recreates the shared agent.

## Runtime work remaining

### MemArena

Use V27 scripts:

- `memarena_sidecar_gate_h0_v27.py`
- `memarena_sidecar_paired_replay_v27.py`
- `memarena_sidecar_inspector_v27.py`

Do not treat Qdrant-only cleanliness as sufficient. V27 superseded that assumption.

### Redis

Use `redis_mid_ingest_retry_probe_v28.py` from V28. The intended fault is after at least one successful session add. A failure before the first add is a negative trigger and should not be counted as evidence against the hypothesis.

## Evidence discipline

Do not claim existing committed benchmark scores were historically contaminated without direct state snapshots or a faithful reproduction showing outcome sensitivity.

Do not claim hidden-state reset problems in general are novel.

Do not claim Mem0's stale message context is novel.

The target contribution is a benchmark reset-attestation method plus empirical audits of real agent-memory benchmark integrations.
