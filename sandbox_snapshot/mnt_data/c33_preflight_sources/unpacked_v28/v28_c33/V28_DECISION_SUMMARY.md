# V28 Decision Summary — C33 Sidecar-Aware Reset Attestation

Status: `IDEA_VALIDATION_V28_C33_CROSS_INTEGRATION_RESET_CONTRACT_MISMATCH_SOURCE_PROVED_OUTCOME_PENDING`

## Decision

C33 remains the sole primary candidate. V28 materially strengthens it from one MemArena implementation finding into a cross-integration evaluation-validity hypothesis with two distinct, source-proved failure surfaces and several meaningful negative controls.

The defensible paper claim is **not** that reset bugs are novel, that Mem0's message buffer is novel, or that published benchmark scores are already known to be wrong. The current claim is narrower:

> Agent-memory benchmark adapters can satisfy their nominal reset API while failing to reset all provider state that is behaviorally active in the next trial. A benchmark should therefore attest reset over the provider's behaviorally active state surfaces rather than equating one public delete call with a clean experimental state.

## Positive integration A — MemArena × Mem0 OSS 2.0.11

Frozen benchmark: `stirelli/memarena@821752b8994b2b1927c5b6d3087c4e24670f13a9`.
Frozen provider: `mem0ai==2.0.11`, tag commit `f2532f072fdefa4c90264acc80af0984309f8b06`.

Source-proved chain:

1. MemArena self-hosted Mem0 config isolates Qdrant by `oss_vector_store_path` but does not configure `history_db_path`.
2. Mem0 therefore uses `${MEM0_DIR:-~/.mem0}/history.db`.
3. `Mem0Provider.reset(namespace)` calls `delete_all(user_id=namespace)`.
4. `delete_all` clears vector memories for that scope but not SQLite `messages`.
5. Normal `infer=True` extraction reads up to ten scoped rows using `get_last_messages()` and places them in the extraction prompt as `Last k Messages`.
6. Day-3 V1 uses stable `lme_v1_<question_id>` scopes. The n=15 “separate throwaway store” add-latency replay changes only Qdrant path, not the message sidecar path.

Failure surface: repeated-run / separate-store isolation.

## Positive integration B — Redis Agent Memory Benchmark × Mem0 OSS 2.0.19

Frozen benchmark: `redis/agent-memory-server@94192c39e2a4a154f441a5411e3d73c4f54974a6`.
Frozen provider: `agent-memory-benchmark/uv.lock` pins `mem0ai==2.0.19`; Mem0 tag `v2.0.19` is commit `dc82354e143c2581d505d581a00286d6ef8c3605`.

Source-proved chain:

1. `Mem0MemoryStore` constructs `Memory.from_config(config or {})`, performs ordinary inferred `Memory.add`, and resets with `delete_all(user_id=self._user_id)`.
2. The runner isolates each LongMemEval example with `user_id=benchmark-<run_name>-<index>`; this prevents ordinary cross-example contamination.
3. The runner wraps `reset()+ingest` in an ingest retry loop with up to three attempts.
4. If attempt 1 successfully ingests at least one session and a later session raises, those earlier successful calls have written scoped `messages` rows.
5. Attempt 2 invokes `delete_all(user_id)` through `store.reset()`. Mem0 2.0.19 still leaves scoped `messages` intact and still reads them before the next extraction.
6. The retry therefore restarts vector memory but not the complete behaviorally active provider state. The same condition can arise when an incomplete run is resumed with the same run name and example index.

Failure surface: mid-ingest retry / incomplete-run resume isolation.

The Redis provider-contract tests verify the public Mem0 call shape but do not assert the post-reset state of Mem0's message buffer. This is a coverage observation, not independent bug evidence.

## Negative and boundary controls

1. ForgetEval's Mem0 path uses `infer=False`; the message-buffer mechanism is not behaviorally active there.
2. Basic Memory's published matrix runs Mem0 with `infer=false`; default run IDs are random UUIDs and grouped LongMemEval adds group-specific suffixes. This is a useful design negative control rather than a positive finding.
3. MemArena's self-hosted Graphiti adapter performs a whole-store wipe on the first reset of a run; Letta deletes/recreates the shared agent on the first reset. No equally direct hidden-state mismatch has been established for them.
4. Mem0's upstream issues already establish stale message-buffer behavior. C33 must not claim provider-level stale context as new.

## Formal object

For trial scope `x`, let `S` be persistent provider state surfaces and `A_x ⊆ S` the surfaces read by the provider during the next benchmark transition. A reset implementation `R_x` is behaviorally complete only if every surface in `A_x` satisfies its declared clean postcondition after `R_x`.

A reset-contract mismatch exists when there is at least one behaviorally active surface `s ∈ A_x` for which the adapter's reset does not establish the clean postcondition.

For the Mem0 cases currently audited:

- `V`: vector-memory records, clean postcondition `count_x(V)=0`;
- `M`: scoped SQLite message buffer, clean postcondition `count_x(M)=0`;
- `H`: audit/history records, persistent but not currently shown to influence the next extraction path;
- provider-specific derived/index/cache surfaces are included only if source or runtime tracing shows behavioral reads.

A valid reset receipt therefore needs per-surface evidence, not merely “reset returned success.”

## Experimental gates

### A. MemArena repeated-run gate

Already specified in V27. Primary pilot is the exact Day-3 n=15 LongMemEval-V1 subset, followed by 200 items only if the pilot shows downstream differences.

### B. Redis retry gate

B0: choose a normal multi-session LongMemEval example under the frozen Redis benchmark.

B1: inject one deterministic failure after `k >= 1` successful session adds and confirm `M_pre > 0`.

B2: invoke the benchmark's native `store.reset()` and attest `V_post=0` while `M_post=M_pre>0`.

B3: branch from the same failed-attempt `history.db` snapshot into two fresh Qdrant stores:

- `invoke_only`: native reset, preserve `M`;
- `verified_clean`: native reset plus exact scoped deletion from `messages`, attest `V=0` and `M=0`.

Re-ingest the same example under both arms and compare hashed memory sets, retrieval Top-k, latency, and optionally judged answer outcome.

## Claim ladder

Current evidence permits: source-proved reset-contract mismatch and natural benchmark exposure paths.

Runtime H0/H1/B1/B2 would permit: mechanism reproduced on frozen stacks.

Paired H3/B3 memory/retrieval effects would permit: reset mismatch changes benchmark-observable state.

Judged-answer differences at scale would permit: benchmark outcome sensitivity.

No historical published score should be called contaminated without machine-state evidence or faithful paired reproduction.

## Kill / downscope rules

- If native reset unexpectedly clears `M` on the frozen runtime, drop that integration.
- If prompt tracing shows `M` is not consumed in the actual frozen configuration, drop the sidecar mechanism for that integration.
- If paired replay is mechanism-positive but downstream memory/retrieval effects are practically negligible, report reset-contract non-hermeticity without claiming score distortion.
- If only one integration survives runtime validation, downscope to a focused benchmark-integration audit rather than a general cross-benchmark claim.

## Next action

1. Run MemArena V27 H0/H1 and n=15 paired replay in a networked exact-stack environment.
2. Run Redis V28 mid-ingest fault-injection probe under locked Mem0 2.0.19.
3. Instrument extraction prompt hashes for one example per integration to close consumption attestation.
4. Only after mechanism and observable effects survive, scale outcome replay and draft RQs.
