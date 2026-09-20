# V39 Decision Summary

Date: 2026-09-19  
Project: AM-AUTO-20260918-R1  
Primary candidate: C33  
Working title: **Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit**

Status: `FORMAL_PILOT_READY_V39_C33_TRACE_BOUNDARY_PRIOR_ART_AUDIT`

## Decision

V39 keeps the V34 Redis/MemArena formal pilot frozen and unchanged. It adds a source-level prior-art boundary audit against MemTrace/MemTraceBench after V38 established that the official graph-generation workflow passes through the same MemBase construction path audited for persistent-state reuse.

The key result is that MemTrace and C33 observe different failure surfaces. MemTrace's public attribution implementation defines five memory-system error classes: `ExtractionError`, `UpdateError`, `DeletionError`, `RetrievalError`, and `ResponseError`. These classes concern operations executed inside a memory workflow. The MemBase tracing runner, however, performs several trial-lifecycle decisions outside the `comment_graph` boundary.

## Finding G: construction lifecycle control is outside the execution graph

In `membase/runners/construction.py`, the runner first derives the deterministic per-user save directory and instantiates the memory layer. It then calls `layer.load_memory(user_id)` and can return early when saved state is accepted. Only after this check does it enter `comment_graph(...)` and begin tracing construction operations.

After the traced construction block exits, the runner calls `layer.save_memory()` and `layer.cleanup()` outside `comment_graph`. Therefore the ordinary resume predicate, the early skip decision, completion-marker publication, and provider cleanup are not represented as operations in the construction graph.

For C33 this boundary is important because T6 partial-state promotion is defined exactly by the relationship between persistent provider state, the resume/completion predicate, and later benchmark execution. The root lifecycle transition can therefore occur before or after the graph rather than inside it.

## Finding H: search also loads persistent state before the trace boundary

`membase/runners/search.py` instantiates the memory layer and calls `layer.load_memory(user_id)` before it imports the construction graph and enters the search `comment_graph`. Provider cleanup again occurs after the traced search block.

A provider state that was created by an earlier attempt or an earlier trial can therefore be accepted before the search trace starts. Search operations can consume that state while the execution graph lacks the lifecycle operation that admitted it.

## Finding I: MemTrace's error taxonomy has no explicit trial-lifecycle class

At audited MemTrace commit `ed2dcf7296ae3b61292fcf643cae3071ef373e9b`, `toolkits/bench_utils.py` defines the memory-error set as:

- `ExtractionError`
- `UpdateError`
- `DeletionError`
- `RetrievalError`
- `ResponseError`

`toolkits/memtrace_utils.py` defines these in terms of missing capture, degradation during update, explicit deletion, failed retrieval of information that is already in the store, or answer failure despite sufficient retrieved context.

None of those definitions encodes benchmark-trial freshness, namespace reuse, completion publication, resume acceptance, or cleanup correctness as a first-class root cause. A lifecycle-contamination event may still produce a downstream operation-level symptom, but the true orchestration fault can lie outside the candidate operation set used for earliest-decisive-fault attribution.

Classification: `TRACE_BOUNDARY_LIFECYCLE_BLIND_SPOT`, E0 source/control-flow evidence.

## Finding J: public graph metadata is insufficient to attest clean-start provenance

The construction graph metadata records `save_dir`, `layer_type`, trajectory metadata, trace output directory, and dataset class. The audited runner does not record the `rerun` flag, a pre-run provider-state fingerprint, pre-run item count, reset outcome, or resume decision in the graph metadata.

This changes the V38 plan for MemTraceBench artifact forensics. Raw graph bodies remain useful for indirect markers such as memory units with no in-graph construction ancestry, pre-existing IDs entering an update, or timestamps inconsistent with the current trace. They cannot by themselves provide a complete clean-start attestation when the relevant admission/reset operations are outside the trace.

Therefore B5 is refined from a simple file-inspection gate into a provenance gate requiring at least one of the following: external generation logs, a pre-run state snapshot, an explicit reset attestation, or a controlled replay instrumented at the runner boundary.

## Relation to MemTrace prior art

V39 supports a narrow complementarity statement rather than a novelty overclaim. MemTrace studies operation-level error tracing inside memory pipelines. C33 studies benchmark-trial state integrity across runs, attempts, namespaces, resume decisions, and cleanup boundaries. The two can interact because hidden lifecycle state can enter an execution graph as already-existing provider state and then manifest as an extraction, update, retrieval, or response symptom.

This is a source-level scope distinction. It is not yet evidence that MemTrace misattributes a released case. A controlled runtime trace-blindness study remains optional until C33 first obtains E2+ causal evidence under the frozen V34 pilot.

Formal large-scale experiment remains `NOT_STARTED`.
