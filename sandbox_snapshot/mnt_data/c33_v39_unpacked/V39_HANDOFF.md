# V39 Handoff

## Current state

C33 remains the primary candidate. V34 Redis/MemArena is the frozen formal pilot and remains unexecuted. V39 adds a source-level prior-art boundary against MemTrace/MemTraceBench.

## New result

The official MemBase runners place the C33-critical lifecycle operations outside the MemTrace execution-graph boundary. Construction opens provider state and performs ordinary resume acceptance before `comment_graph`, then publishes `save_memory()` and performs cleanup after the graph. Search loads provider state before importing/continuing the graph. MemTrace's first-class memory error taxonomy covers extraction, update, deletion, retrieval, and response, not trial freshness/resume/cleanup semantics.

This supports the narrow source-level class `TRACE_BOUNDARY_LIFECYCLE_BLIND_SPOT` at E0. It does not establish contamination or misattribution in any released MemTraceBench graph.

## Immediate priority order

1. Preserve V34 without edits.
2. Enumerate LightMem public Drive artifacts when file listing becomes available.
3. For MemTraceBench, use graph-body inspection only for indirect carry-in markers; seek external run provenance for clean-start attestation.
4. Run provider-level MemBase interruption and swallowed-add experiments when a Qdrant-capable environment is available.
5. Execute V34 Redis exact paired pilot, then MemArena exact paired pilot.
6. Only after E2+ primary evidence, consider a small controlled trace-blindness study comparing clean and dirty MemBase runs under the same current-run inputs.

## Claim discipline

Keep MemTrace as complementary prior art. The paper can state that existing operation-level tracing leaves benchmark-trial lifecycle provenance outside the audited graph boundary. Do not state that MemTraceBench is contaminated or that its released labels are wrong without run-level provenance and controlled evidence.
