# MemBase Successor Lifecycle Audit V38

Pinned repository: `zjunlp/MemBase@a9ba9495d48541d3e68588ff097294cc7a1201bc`.

## Provenance

LightMem's pinned root README links MemBase on 2026-03-21 as the project's "more comprehensive baseline evaluation framework" for Mem0, A-MEM, EverMemOS, LangMem, LoCoMo, and LongMemEval. V38 therefore treats MemBase as a longitudinal successor implementation rather than an unrelated benchmark.

## State topology for Mem0

The construction runner rewrites the memory configuration to a deterministic per-trajectory user and appends that user to `save_dir`. `Mem0Config` then derives:

- Qdrant local path = per-user `save_dir`;
- Qdrant collection name = `user_id` by default;
- `on_disk=True`;
- history DB = `<save_dir>/history.db`.

The same trajectory therefore reopens the same persistent provider state across runs unless the caller changes the base save directory or removes the state externally.

## Ordinary resume state machine

### Case 1: hard interruption before any durable memory

`config.json` is absent and Qdrant has no relevant memory. `load_memory()` returns false and the trajectory is reconstructed. This is the cleanest case.

### Case 2: hard interruption after one or more successful writes, before finalization

`config.json` is absent, so the trajectory is not skipped. The already-persisted Qdrant state remains in the same per-user path. The runner continues construction in that store without calling a reset. This avoids false completion publication but does not create a fresh retry.

Classification: `PERSISTENT_PARTIAL_STATE_REUSED_DURING_REBUILD`.

### Case 3: one or more Mem0 add calls fail inside the layer, at least one add succeeds

`Mem0Layer.add_message()` catches the provider exception and returns. The runner's strict mode cannot observe that swallowed exception. Construction reaches finalization, and `save_memory()` writes `config.json`. A future ordinary run sees `config.json`, verifies that at least one Qdrant memory exists, and can skip the complete trajectory.

Classification: `T6_PARTIAL_FINALIZATION_MARKER_PROMOTION`.

### Case 4: explicit `--rerun`

The flag bypasses only the early-return guard. Persistent Qdrant and history paths stay unchanged. `Mem0Layer.cleanup()` closes the Qdrant client; it does not delete state. Qdrant's adapter provides a destructive `reset()` method, while this construction path never calls it.

Classification: `DOCUMENTED_REBUILD_FRESHNESS_MISMATCH`.

## Longitudinal interpretation

Compared with the older LightMem toolkit, MemBase adds a stronger completion-side gate because a raw backend memory alone no longer satisfies ordinary skip after a hard interruption. The gate still measures a weak proxy for complete ingestion. It verifies "finalization marker exists and some memory exists", while per-message success coverage is absent.

This distinction matters for C33: a completion marker can improve resume behavior and still fail to prove the benchmark unit's intended postcondition. Retry freshness and completion attestation are separate contracts.

## Published reproduction-path reachability

The exact traced-construction script checked into MemBase at the smartcomment integration commit `0712c073f5f3716d40ef6252fc0ef175623ac168` launches `memory_construction.py` with `--rerun --tracing`. Its README identifies the scripts as the reproduction code used to generate MemTraceBench and gives `sample_size=200` for LongMemEval. The Mem0 config points to a stable `traced_mem0` save directory, and the shell script performs no reset or deletion before invoking construction.

This establishes source-level reachability on an official published reproduction path. It does not establish that the actual released run started from a non-empty directory.

## Evidence level

E0 only. No provider-level fault injection or score effect is claimed in V38.
