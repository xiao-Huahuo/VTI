# Change History V40

## 2026-09-19

1. Persisted the complete V39 C33 research bundle into the canonical AgentMemory Library tree.
2. Materialized the frozen V34 Redis n=12 cohort from the deterministic SHA-256 selection rule without using gold answers or outcome data.
3. Pinned LongMemEval-S to upstream revision `98d7416c24c778c2fee6e6f3006e7a073259d48f` and SHA-256 `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`.
4. Upgraded the V32 exact single-case paired probe into a V34 cohort-bound V40 probe with `question_id` selection, small-split enforcement and fault-after-three default.
5. Added fail-closed dataset fetch and preflight tooling.
6. Added a 12-case orchestrator that retains failed cases instead of silently reducing sample size.
7. Added V34 statistical aggregation with 5000 bootstrap resamples, seed 20260919 and exact paired McNemar reporting when judge pairs are present.
8. Added four V40 offline tests. All pass.
9. Re-ran the inherited V32 retry/resume source-control-flow suite. All five tests pass.
10. Audited the current sandbox and recorded exact-runtime blockers. Formal pilot remains unexecuted.
