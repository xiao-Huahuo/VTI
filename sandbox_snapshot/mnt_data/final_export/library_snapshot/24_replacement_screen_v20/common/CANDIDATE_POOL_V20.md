# Candidate Pool V20

V20 excludes the asynchronous-readiness family killed with C30 and screens for structurally different Agent Memory problems.

## C33 Benchmark-to-Deployment Path Drift

Status: PRIMARY_PROVISIONAL.

Three independent public repositories provide concrete benchmark/deployment path or configuration divergence, including two projects whose histories explicitly repaired the mismatch. General benchmark-fidelity prior art is strong, and Agent Memory Atlas already performs manual case-by-case audits, so the surviving contribution requires a systematic corpus study plus executable conformance and matched replay.

## C34 Derived-Projection Consistency

Status: KILLED_IN_SCREENING.

Canonical-versus-derived state, stale summaries/graph edges and deletion propagation into derived artifacts are already explicitly treated in current Agent Memory architecture/practitioner work and Agent Memory Atlas tests.

## C35 Retry-Induced False Corroboration

Status: KILLED_IN_SCREENING.

Current Agent Memory design work already documents retry without request-id dedup as a source of duplicate indexing, top-k crowding and false corroboration, with idempotent ingestion as the remedy.

## C36 Restart-Only Durability Gap

Status: KILLED_IN_SCREENING.

Cross-process and restart durability already appear in released memory-system tests and benchmark discussions. The generic contribution is too crowded.

## C37 Embedding/Indexer Migration Drift

Status: KILLED_IN_SCREENING.

Model/index migration mismatch, re-embedding, schema evolution and version guards are already explicit in production memory tooling and adjacent vector-system practice.

## Portfolio decision

Promote C33 only. Kill C18 as a main idea. Keep C31 as reserve and C16/C25/C27 as blocked diagnostic assets.
