# C33 Source-Grounded Mini-Census V21

Project: AM-AUTO-20260918-R1  
Idea: C33 Benchmark-to-Deployment Path Drift in Agent Memory Systems  
Date: 2026-09-18  
Status: PURPOSIVE_MINICENSUS_COMPLETE

## Purpose

This census tests whether C33 is larger than one or two anecdotal repositories. It deliberately does not estimate field prevalence. The 12 projects were selected because both an evaluation surface and a user-facing deployment or integration surface were publicly inspectable at a pinned commit.

## Result

The audit found several structurally different relationships between benchmark and deployment paths.

1. **Direct current path divergence.** YourMemory maintains benchmark-side ranking constants and post-processing that differ from its shipped retrieval implementation. Fidelis explicitly maintains a production atomic-fact path and a separate LongMemEval session-retrieval path.
2. **Historical divergence followed by repair.** Aelfrice converged production retrieval onto the benchmark/eval `retrieve_v2` implementation in v4.0. claude-mem-lite later documented that an earlier benchmark statistic had used the wrong instrument and added the real `production_hybrid` path.
3. **Partial-path validation.** Paxm measures retrieval on directly seeded fixtures while separately validating production capture. inbrain shares the hybrid retrieval core but has a benchmark-specific trajectory exception. Claude Self Reflect contains both direct calls into production retrieval and research harness material that mirrors logic locally.
4. **Explicit path-equivalence controls.** Klypix imports production ranker primitives into evaluation, and deja-vu routes benchmark data through the normal ingestion and production search ladder. Redis Agent Memory and ByteRover state an explicit production-path policy, though those two controls are partly self-attested.
5. **Backend substitution without demonstrated semantic mismatch.** AgentOS benchmarks SQLite while production deployments use Postgres with the same higher-level brain code. This is a transfer assumption to audit, not evidence of a retrieval-quality failure.

These cases establish mechanism diversity. They do not establish a population rate because repository selection was purposive and evidence discoverability influenced inclusion.

## Taxonomy

The useful audit unit is a Path Contract rather than a binary `same code / different code` label. The contract compares at least:

`ingestion -> retrieval core -> ranking/config -> feature gates -> post-processing -> lifecycle side effects -> storage backend`

A benchmark can share the retrieval function and still diverge through write-path bypass, default flags, post-processing, mutable side effects, or backend substitution. Conversely, separate wrappers may remain semantically equivalent when both delegate to one canonical implementation.

## Natural repair evidence

Aelfrice and claude-mem-lite provide unusually strong natural repair cases. Their repositories document a mismatch, then change the evaluation/deployment wiring or measurement instrument to converge the paths. These cases support the engineering relevance of path equivalence without requiring us to manufacture a fault.

## Claim boundary after V21

Supported:
- multiple independent Agent Memory projects contain source-grounded benchmark/deployment path divergence or explicit repairs;
- the phenomenon spans more than one implementation mechanism;
- the normalized Path Contract can represent both divergences and equivalence controls.

Still unverified:
- field prevalence;
- sensitivity/specificity of an automated detector on a representative corpus;
- whether correcting a path mismatch materially changes the headline benchmark metric in matched dynamic replay;
- whether the final method generalizes beyond manually inspected repositories.

## Next hard gate

Freeze a representative sampling frame before looking at labels, then run the audit on that sample. Separately, execute matched dynamic replay on at least two runnable natural-repair or current-divergence systems. The main claim advances only if path correction changes measured behavior or reported metrics in a reproducible way.
