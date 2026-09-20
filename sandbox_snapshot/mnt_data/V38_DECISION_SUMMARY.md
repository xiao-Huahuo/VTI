# V38 Decision Summary

Date: 2026-09-19  
Project: AM-AUTO-20260918-R1  
Primary candidate: C33  
Working title: **Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit**

Status: `FORMAL_PILOT_READY_V38_C33_PUBLIC_REPRO_PATH_AND_SUCCESSOR_LIFECYCLE_AUDIT`

## Decision

V38 keeps the V34 Redis/MemArena formal pilot unchanged. The new work closes two exploratory questions left by V37: whether LightMem exposes recoverable public experiment artifacts, and whether the newer MemBase framework preserves or changes the same lifecycle semantics.

The result is mixed and useful. LightMem does expose a public Google Drive experiment folder, so V37's artifact search should no longer be described as an absence of public raw data. File-level inspection remains pending because the current execution interface reaches the public folder landing page but does not enumerate its contents. Separately, MemBase strengthens one part of the completion predicate compared with the older LightMem toolkit, while still retaining persistent-state reuse paths that matter for C33.

## Finding A: LightMem public artifact door exists

Pinned LightMem repository: `zjunlp/LightMem@8449d574df6bae1bdf3314a1564da65e2f37e046`.

The pinned root README explicitly states that experimental results are shared on Google Drive and that the shared data includes model outputs, evaluation logs, and predictions. The public folder is:

`https://drive.google.com/drive/folders/1n1YCqq0aDeWiPILhkq-uS3sU3FDmslz9?usp=drive_link`

This changes the artifact status from "no raw artifact located" to:

`PUBLIC_ARTIFACT_LOCATOR_CONFIRMED_FILE_LEVEL_AUDIT_PENDING`

The current web interface resolves the folder as `lightmem_experiments` but exposes no file listing. Repository-wide GitHub searches for expected MemZero/LongMemEval retrieval or evaluation filenames also found no checked-in copy. Therefore V38 records the locator without inferring anything about the contents of a specific published run.

## Finding B: MemBase is the documented successor baseline framework

The same LightMem README states on 2026-03-21 that the project moved baseline evaluation to the more comprehensive `zjunlp/MemBase` framework. V38 audits MemBase at commit:

`a9ba9495d48541d3e68588ff097294cc7a1201bc`

This matters because it gives a longitudinal control: the older LightMem toolkit and its replacement can be compared at the lifecycle-contract level without changing C33's formal pilot.

## Finding C: MemBase adds a completion marker, but interruption still reuses partial state

For Mem0, MemBase stores each trajectory under a deterministic per-user `save_dir`. Qdrant uses that directory with `on_disk=True`, the collection defaults to the user ID, and the SQLite history DB also lives under the same directory.

`load_memory()` is stricter than the older LightMem MemZero loader. It requires a per-user `config.json` and then verifies that at least one Qdrant memory exists. `config.json` is written by `save_memory()` only after the construction loop reaches finalization. An abrupt process interruption before finalization therefore does not immediately satisfy the ordinary skip predicate.

That is a real partial hardening of the exact V37 LightMem branch. It does not establish fresh retry state. The Mem0 layer is instantiated against the persistent per-user Qdrant path before the skip check. When `config.json` is absent, `load_memory()` returns false and construction proceeds in the same already-populated store. No reset occurs first. An interrupted attempt with partial Qdrant state is therefore replayed over residual state rather than reconstructed from an independently empty store.

Classification: `PERSISTENT_PARTIAL_STATE_REUSED_DURING_REBUILD`, E0 source/control-flow evidence.

## Finding D: swallowed Mem0 add failures can still create a completion marker

MemBase's runner defaults to strict construction, but `Mem0Layer.add_message()` catches exceptions raised by `self.memory_layer.add(...)` and returns to the runner. Those failures therefore do not reach the runner's strict exception path. The loop can continue, `flush()` has no Mem0-specific completion validation, and `save_memory()` writes `config.json` afterward.

If at least one add succeeded and one or more later adds failed inside the swallowed path, the resulting state has both a completion marker and at least one Qdrant memory. On the next ordinary run, `load_memory()` can accept that state and the runner returns without reconstructing the trajectory.

This is a source-level T6 variant: the completion marker certifies control-flow completion, while per-message construction completeness is not part of the predicate.

Classification: `T6_PARTIAL_FINALIZATION_MARKER_PROMOTION`, E0.

## Finding E: MemBase `--rerun` still lacks fresh-state semantics for Mem0

MemBase documents `--rerun` as ignoring saved memory and rebuilding from scratch. In the audited runner, the flag only bypasses the `load_memory()` early-return condition. The same deterministic per-user save directory, Qdrant collection, and history DB are then opened again.

The Mem0 layer's `cleanup()` only closes the local Qdrant client. The Qdrant adapter has a destructive `reset()` method, but the construction rerun path does not call it. Existing collections are retained when the Qdrant adapter initializes and detects that the collection already exists.

Thus the documented Mem0 rerun route does not independently establish an empty provider state before replay.

Classification: `DOCUMENTED_REBUILD_FRESHNESS_MISMATCH`, E0.


## Finding F: the same `--rerun` path is used by the official MemTraceBench generation script

A further provenance check makes the MemBase result more relevant than a dormant CLI edge case. `examples/trace_memory_lifecycle_with_membase/run_traced_construction.sh` was introduced in commit `0712c073f5f3716d40ef6252fc0ef175623ac168` on 2026-06-03. The companion README says these configs and scripts are the reproduction code used by the MemTrace paper to generate MemTraceBench execution graphs.

The construction script always passes both `--rerun` and `--tracing`. For Mem0, its checked-in config uses the stable save directory `examples/trace_memory_lifecycle_with_membase/traced_mem0`. The script creates log and trace directories with `mkdir -p`; it contains no deletion or provider reset before the construction command. The README instructs users to set `sample_size=200` for LongMemEval when reproducing the paper's execution-graph generation.

The public MemTraceBench dataset now provides 19 Mem0 execution graphs with 66 curated failure annotations across LoCoMo, LongMemEval, and RealMem. The released file inventory contains 12 Mem0 LongMemEval graph files. This creates a public raw-trace corpus that is directly connected to the audited MemBase reproduction path.

The claim boundary remains strict: the script-level path establishes **reproduction-path exposure**, not contamination of the released MemTraceBench data. The actual generation directory may have been clean before the run. File-level graph inspection is the next gate.

## Consequence for C33

V38 sharpens the paper's lifecycle claim in two ways. First, resume safety cannot be reduced to the presence of a completion marker: the marker must encode the actual construction postcondition. Second, a retry that avoids false skip can still be contaminated when it reuses the persistent namespace without a verified reset.

This is a longitudinal source audit, not a published-score accusation. No MemBase or LightMem score is attributed to these paths. The controlled Redis/MemArena V34 pilot remains the primary experiment for E2+ causal evidence.

Formal large-scale experiment remains `NOT_STARTED`.
