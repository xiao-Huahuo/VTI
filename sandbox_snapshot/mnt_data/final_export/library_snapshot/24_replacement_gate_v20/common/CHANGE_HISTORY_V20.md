# Change History V20

- Continued replacement screening after C30's V19 Red-Team kill.
- Downgraded production-path fidelity after finding direct public examples and explicit shipped-path evaluation guidance.
- Rejected shadow-memory attribution as a new main idea after finding direct 2026 research-track prior art.
- Added C33 `Reset Attestation for Stateful Agent Memory Benchmarks`.
- Bound C33 to MemArena's pinned `mem0ai==2.0.11`, stable LongMemEval-V2 domain namespaces and reset-before-ingest contract.
- Verified in Mem0 v2.0.11 that scoped `delete_all` performs one vector-store list without `top_k`; Qdrant defaults the page to 100.
- Linked this source behavior to public mem0 issue #6627 and merged pagination fix #6636.
- Recorded a second reset-risk mechanism from MemArena's hosted path: async `Delete in progress...` semantics with no post-reset empty-state barrier in the audited adapter.
- Implemented and executed the C33 source-integration fixture. A 150-memory old state leaves 50 residual records after benchmark-style reset; fixed canary queries expose residual state. Attested reset removes the fixture contamination.
- Frozen C33 Claim Contract and real paired pilot design. Real provider effect remains UNVERIFIED_CORE.
- Promoted C33 to primary provisional. Formal Experiment remains NOT_STARTED.

- Added an independent Supermemory reset-attestation audit. Redis benchmark ignores bulk-delete success/count/error evidence and clears local state unconditionally.
- Added a Supermemory source-integration falsifier showing adapter-local empty state can coexist with provider-reported residual remote state. This remains mechanism evidence only.

- Added a trigger-reach Gate after auditing the actual LongMemEval-V2 scope cap: six trajectories per domain do not imply more than 100 distilled Mem0 memories. Public journals omit the final namespace count, so threshold reach remains unverified.
- Inspected the committed Mem0 platform journal as a no-credential fallback; it lacks reset-state snapshots and cannot resolve C33's real-effect claim.
- Recorded the current container dependency/network limitation as a BLOCK rather than a negative result.

- Late prior-art refresh found `agent-memory-harness` explicitly discussing cross-run contamination from persistent memory substrates; C33 novelty was narrowed again to reset-postcondition attestation.
- Audited ForgetEval's runner and adapters: reset is a mandatory pre-case operation, yet the runner does not independently verify post-reset emptiness; several adapters rely on destructive APIs or best-effort exception handling. This motivates a cross-benchmark reset-contract census in the next Gate.
