# V38 Handoff

Project: AM-AUTO-20260918-R1  
Primary candidate: C33  
Status: `FORMAL_PILOT_READY_V38_C33_PUBLIC_REPRO_PATH_AND_SUCCESSOR_LIFECYCLE_AUDIT`

## What changed from V37

1. LightMem's pinned README explicitly exposes a public Google Drive with model outputs, evaluation logs, and predictions. Treat the raw-artifact gate as **locator found, file-level audit pending**, rather than "public artifacts absent".
2. LightMem's 2026-03-21 project update points to `zjunlp/MemBase` as its more comprehensive baseline evaluation framework.
3. MemBase Mem0 adds a `config.json` completion marker before ordinary resume can skip a trajectory. This blocks the exact older LightMem "partial backend row alone is enough to skip" branch after a hard interruption.
4. The same interrupted partial Qdrant state is still reopened and reused during reconstruction because the retry path performs no reset before replay.
5. MemBase Mem0 swallows core add exceptions, allowing finalization and `config.json` publication after partial construction. A later ordinary run can then skip the trajectory if any memory exists.
6. MemBase `--rerun` bypasses the load guard but keeps the same on-disk Qdrant collection and history DB; cleanup closes the client only. The available destructive Qdrant reset is not invoked by this path.
7. The official MemTraceBench construction reproduction script always invokes MemBase with `--rerun --tracing`, uses a stable Mem0 save directory, and performs no pre-run deletion in the script. The public MemTraceBench release contains 19 Mem0 graphs, including 12 LongMemEval graph files. This lifts the finding from a merely available CLI route to an official published reproduction path, while leaving actual released-data contamination unproven.

## Evidence boundary

All MemBase findings are E0 source/control-flow evidence. LightMem's Drive link is a public artifact locator, not evidence that any published score was affected. V34 Redis/MemArena sample selection, endpoints, and statistics stay frozen.

## Next work without changing the formal protocol

1. Enumerate the LightMem Drive and recover MemZero × LongMemEval construction/retrieval/evaluation artifacts if present.
2. Inspect the 12 public MemTraceBench Mem0 × LongMemEval execution graphs for run metadata, construction completeness markers, and any evidence that the trace was produced over pre-existing provider state.
3. Build a provider-level MemBase trace with three conditions: clean run, hard interruption after successful writes, and swallowed add failure followed by ordinary resume.
4. Preserve the V34 Redis n=12 and MemArena n=15 exact paired pilot as the primary E2+ causal experiment.
5. Keep Memora raw-artifact recovery open; audited GitHub surfaces still expose scripts and output contracts rather than committed runtime outputs.
