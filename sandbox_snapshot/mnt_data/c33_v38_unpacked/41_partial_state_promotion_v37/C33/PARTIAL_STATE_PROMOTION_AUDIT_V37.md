# Partial-State Promotion Audit V37

## Definition

T6 `PARTIAL_STATE_PROMOTION` occurs when a benchmark resume/retry path promotes incomplete persistent state to a completed unit because its completion predicate is weaker than the actual construction contract.

## Microsoft Memora

Question `q` maps to user `question_<q>` and a persistent Chroma collection `<collection_name>_question_<q>`. Search uses the same user ID.

During construction each session is added separately. If a session ultimately raises, `process_conversation()` logs the error and continues. Earlier successful sessions remain persistent.

The documented `--skip-existing` retry mode calls `check_question_has_memories()`, which returns true whenever collection count is above zero. Thus one successful write plus a later failed session is enough for the retry to skip reconstruction of the entire question. Search still processes that question and queries the partial collection.

Direct `memory.force_rebuild=True` has a separate freshness mismatch: `run_memora.py` does not delete the persistent path and `process_conversation()` disables normal `client.clear()` when force rebuild is set. The multi-process wrapper compensates by deleting split stores before launch, while the direct documented route does not.

A secondary, out-of-scope correctness observation is that `add_memory()` returns from inside its chunk loop, so only the first chunk is executed when a session is split into multiple chunks. V37 does not use this observation in the lifecycle claim because trigger frequency in LongMemEval was not established.

## LightMem MemZero

Memory construction derives user ID from dataset class plus trajectory ID and a deterministic save directory. MemZero defaults to Qdrant with on-disk persistence and collection name equal to the user ID.

Construction writes message by message. `MemZeroLayer.add_message()` catches broad exceptions and returns, allowing construction to continue after failed writes.

Before construction, absent `--rerun`, `memory_construction()` returns immediately when `layer.load_memory(user_id)` is true. MemZero `load_memory()` first tries explicit config/pickle completion artifacts; if they are absent or unusable it falls back to `_has_any_memory()`, which returns true when the persistent backend contains any memory.

A process interrupted after early successful writes can therefore leave Qdrant state without a completed snapshot. On rerun, any remaining backend memory can satisfy the load predicate and skip the rest of the trajectory. `memory_search()` later uses the same load predicate and retrieves that state.

The CLI describes `--rerun` as rebuilding from scratch, but implementation only bypasses the load guard and contains no delete/reset before constructing a layer pointed at the same persistent directory/collection.

## IronCurtain negative control

Each LongMemEval question receives `/tmp/longmemeval-<pid>-<question_id>.db`. `run_question()` always removes the DB and WAL/SHM sidecars in `finally` unless explicit completed-run preservation is selected. The completion checkpoint is appended only after `run_question()` returns.

The ordinary failure ordering is therefore: partial state -> cleanup -> no checkpoint -> resume reruns fresh.

## Claim boundary

Supported: two independent harnesses have source-level T6 paths; the risk can involve primary persistent memory rather than hidden sidecars; an independent harness demonstrates safer disposable-state/checkpoint ordering.

Not supported: trigger frequency in published runs, specific published score deltas, or ecosystem prevalence.
