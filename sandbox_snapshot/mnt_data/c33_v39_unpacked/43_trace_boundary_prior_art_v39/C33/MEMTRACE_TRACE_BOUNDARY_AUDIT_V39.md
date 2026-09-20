# MemTrace Trace-Boundary Audit V39

## Scope

This audit asks whether MemTrace/MemTraceBench directly observes the lifecycle transitions targeted by C33. It uses the official MemBase runner used to generate MemTraceBench traces and the official MemTrace attribution taxonomy.

## Audited revisions

- MemBase: `a9ba9495d48541d3e68588ff097294cc7a1201bc`
- MemBase construction runner blob: `a174314d5e7cde7469b6f0be30431d21f81e6a0b`
- MemBase search runner blob: `609efc9fa3e44a95d52d4369efd03530364c643d`
- MemTrace: `ed2dcf7296ae3b61292fcf643cae3071ef373e9b`
- MemTrace benchmark utilities blob: `c949c3cf868e4bf230184a22187b9dc7d0ece47e`
- MemTrace attribution instructions blob: `798de0232f650a066416f3900c3fd18a98b44fa3`

## Construction runner trace boundary

Observed order:

1. derive deterministic per-user `save_dir`;
2. instantiate the memory layer against that directory;
3. when `rerun` is false, call `layer.load_memory(user_id)` and return early if accepted;
4. obtain patch specs;
5. enter `comment_graph(...)`;
6. trace message construction and final `flush()`;
7. exit `comment_graph(...)`;
8. call `layer.save_memory()`;
9. call `layer.cleanup()`;
10. export the already-closed execution graph.

Lifecycle implications:

- Provider opening precedes the graph.
- Resume acceptance precedes the graph.
- A successful resume can bypass graph creation entirely.
- Completion-marker publication occurs after the graph.
- Provider cleanup occurs after the graph.

The exact C33 transitions `pre-run state -> admission/reset -> construction -> completion publication -> cleanup` are therefore only partially observable.

## Search runner trace boundary

Observed order:

1. derive the same per-user `save_dir`;
2. instantiate the memory layer;
3. call `layer.load_memory(user_id)`;
4. import `graph_construction.json` if present;
5. enter `comment_graph(graph=imported_graph)`;
6. trace retrieval operations;
7. exit the graph;
8. call `layer.cleanup()`;
9. export `graph_search.json`.

The decision that a persistent provider store is valid enough to search occurs before the search graph. Any stale or partially promoted state accepted at that step is already inside the memory layer when traced retrieval begins.

## Attribution vocabulary

MemTrace's memory-system error vocabulary contains exactly five classes in the audited code: extraction, update, deletion, retrieval, and response. The accompanying definitions describe information capture and propagation inside the memory pipeline.

The vocabulary has no explicit category for:

- stale namespace reuse across benchmark trials;
- retry over residual provider state;
- false-clean acknowledgement;
- partial-state promotion by resume predicates;
- completion-marker publication after swallowed write failures;
- cleanup/reset failure at the harness boundary.

This does not make those failures impossible to observe indirectly. It means the first causal lifecycle operation can fall outside the graph and outside the first-class label space.

## Clean-start provenance fields

The construction graph metadata created by the audited runner contains `save_dir`, `layer_type`, `traj_metadata`, `traced_data_save_dir`, and `dataset_cls`. It omits `rerun`, a pre-run provider-state digest/count, cleanup/reset result, resume decision, and completion-marker state.

A released graph can therefore establish what happened inside the traced operation sequence while remaining insufficient to prove that the provider namespace was empty at trial start.

## Authorized interpretation

`TRACE_BOUNDARY_LIFECYCLE_BLIND_SPOT` means the audited trace boundary excludes lifecycle operations required to establish trial freshness and completion validity. It is source/control-flow evidence, E0.

It does not mean every MemTraceBench graph is contaminated. It does not establish an attribution error in the released dataset. It does not establish that MemTrace cannot diagnose downstream symptoms. The narrower result is that current graphs do not independently attest or localize the lifecycle root cause targeted by C33.
