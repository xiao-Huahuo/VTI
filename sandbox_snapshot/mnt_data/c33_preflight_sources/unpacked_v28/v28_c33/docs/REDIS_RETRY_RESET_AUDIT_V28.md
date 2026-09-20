# Redis Agent Memory Benchmark × Mem0: Retry/Resume Reset Audit V28

## Frozen stack

- repository: `redis/agent-memory-server`
- commit: `94192c39e2a4a154f441a5411e3d73c4f54974a6`
- benchmark package: `agent-memory-benchmark`
- lockfile: `agent-memory-benchmark/uv.lock`
- Mem0: `2.0.19`
- Mem0 tag commit: `dc82354e143c2581d505d581a00286d6ef8c3605`

## Benchmark lifecycle

`run_longmemeval_v1()` shuffles examples with seed 42. Each unfinished example gets an isolated scope:

`benchmark-<run_name>-<index>`.

Before ingest, `ingest_clean()` calls `store.reset()` and then ingests all sessions. The entire function is retried up to `retries` times, default 3.

`Mem0MemoryStore.reset()` calls:

`self._memory.delete_all(user_id=self._user_id)`.

The adapter uses ordinary inferred `Memory.add` calls for each session.

## Trigger condition

A sidecar-bearing retry requires a partial successful ingest:

1. reset succeeds;
2. at least one session add succeeds and writes scoped message-buffer rows;
3. a later add raises;
4. retry invokes the same scoped `delete_all`;
5. vector memories are removed, message rows remain;
6. retry starts again from session 1 and Mem0 reads those old rows as extraction context.

A failure before the first successful session add is a negative trigger and must not be interpreted as disconfirming the mechanism.

## Resume condition

The runner derives the same user scope from run name and shuffled index. If an example did not reach persisted completion and the same run is resumed, its pre-ingest reset again deletes vector memories but does not establish a clean message buffer.

Completed examples are skipped, so the primary resume concern is an incomplete/failed/crashed example, not ordinary completed-example reuse.

## Why this is distinct from MemArena

MemArena's current strongest natural exposure is reuse of stable dataset scopes across separate runs / separate Qdrant stores sharing the default history DB.

Redis isolates examples well during ordinary success but its retry abstraction treats `delete_all(user_id)` as a clean rollback. This exposes the same state-surface mismatch under fault recovery rather than ordinary repetition.

## Test-coverage observation

The provider SDK contract test uses a fake Mem0 object and checks public call shape. It does not assert the post-reset contents of Mem0's internal message buffer. Several other provider tests explicitly verify their scoped purge/clear behavior.

This is evidence about contract coverage, not proof of outcome contamination.

## Runtime experiment

1. Select one multi-session example from the frozen runner order.
2. Use an isolated Mem0 config with separate Qdrant path and history DB while preserving Mem0 2.0.19 semantics.
3. Fail once immediately before session `k+1` after `k>=1` successful adds.
4. Snapshot `history.db`.
5. Create paired arms from the same snapshot:
   - native retry: adapter reset only;
   - verified retry: adapter reset plus exact deletion of scoped `messages` rows.
6. Assert vector state is empty before both arms ingest.
7. Compare final memory fingerprints and retrieval Top-k hashes.
8. If they differ, add judged-answer replay.

Persist no raw benchmark text in the research artifact. Store counts, IDs where safe, hashes, latencies, configuration digests, and version identities.
