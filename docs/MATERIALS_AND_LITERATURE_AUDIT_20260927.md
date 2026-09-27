# C33 materials and literature readiness audit

Date: 2026-09-27. Scope: readiness for an A-level evaluation-methodology paper, not a claim of exhaustive global novelty search.

## Verdict

**Experimental provenance is strong for the completed V55 and stopped V56 runs; the manuscript and related-work package are incomplete.** V57 is still an engineering/statistical draft with no 14B, Neo4j or confirmatory model calls. A full paper cannot be assembled honestly from the current evidence alone.

## Available primary project materials

| Material | Status | Primary location / limit |
| --- | --- | --- |
| Original research question and falsification criteria | Available | `IDEA.md`; its dated status section still says V55 0/12 and is historical, not the current machine state. |
| V55 formal cohort/protocol, raw checkpoints and E4 receipts | Available and archived | `history/v55_formal/`; 12/12 selected terminal, 11 Stage-A-valid, 10 E2-evaluable, 10/10 E2-positive, 6/10 answer-text E3-positive. |
| V55 independent result checks | Available | `history/v55_formal/results/V55_FORMAL_READBACK_AUDIT.json` (121/121) and `V55_E4_READBACK_AUDIT.json` (113/113). E4 is supplemental DeepSeek, not the official GPT-4o score. |
| V56 independent-backend attempt | Available and stopped | `history/v56_cross_backend/`; first of four targets failed clean-clean null and quality gate, no predecessor/native arm. Independent readback 439/439. No cross-backend causal label. |
| V57 prospective statistical machinery | Draft and dry-run audited | `v57_design/`; count scorer 46/46 synthetic vectors, retrieval footprint 8/8 fake-embedding checks, 2-of-3 statistic 9/9 plus 10,000 synthetic null datasets. These are implementation checks, not scientific outcomes. |
| Graphiti-Local execution stack | Partial only | Graphiti core 0.30.2 constructor and toy local BGE/reranker tests passed. No Neo4j health/reset/teardown, 14B runtime, independent-unit drill or LongMemEval compatibility results. |
| Order/score/ranking distortion and reset-policy cost | Missing | Central planned VTI contributions; no confirmatory result/artifact yet. |
| Manuscript, figure set, reproducibility package | Missing | No current paper draft or single submission-ready data/code package. |

## Literature source ledger

Primary pages below were verified as of 2026-09-27. This is a **seed ledger**, not a completed full-text review or reference bibliography.

| Source | Relationship to C33 | Review status |
| --- | --- | --- |
| [Redis agent-memory-benchmark README](https://github.com/redis/agent-memory-server/blob/main/agent-memory-benchmark/README.md) | States per-example isolation/reset as harness-level conditions and describes provider-specific memory internals. | Official source checked. |
| [When Is an Agent Evaluation Over?](https://arxiv.org/abs/2608.14940) | Explicit cross-unit separation and delayed-write next-run score effect. Removes novelty of “evaluation units should be isolated.” | Primary abstract checked; line-by-line method comparison pending. |
| [Forgetting Without Restarting](https://arxiv.org/abs/2609.04875) | Counterfactual execution-state unlearning and selective replay; adjacent to reset certification. | Primary abstract checked; full-text claim mapping pending. |
| [MemDelta](https://arxiv.org/abs/2606.29914) | Controlled model/embedding/retrieval confounds in agent-memory evaluation. | Primary abstract checked; detailed baseline matrix pending. |
| [Automated Benchmark Auditing](https://arxiv.org/abs/2605.26079) | Broad benchmark defect auditing and ranking consequences; key novelty threat. | Primary abstract checked; automation and ranking methods need full-text comparison. |
| [Control-Plane Placement / ForgetEval](https://arxiv.org/abs/2606.15903) | Memory supersede/release/purge semantics and adapter protocol; adjacent but not trial-boundary independence. | Primary abstract checked; adapter overlap pending. |
| [Toward User-Conditioned Evaluation under Temporal Interventions](https://arxiv.org/abs/2607.21635) | Persistent user-state interventions; overlaps intervention language. | Primary abstract checked; relation to benchmark units pending. |
| [On the Fragility of Self-Improving Agents](https://arxiv.org/abs/2608.18066) | Task-order effects in adapting agents; distinct from reset-isolation mechanism. | Primary abstract checked; order-analysis comparison pending. |
| [A-TMA](https://arxiv.org/abs/2607.01935) | Newly identified related work decoupling memory bank, retrieval and answer failures; important for VTI endpoint hierarchy. | Primary abstract checked; **not yet integrated into IDEA related-work section**. |
| [Scope Before You Persist](https://arxiv.org/abs/2609.29144) | Newly identified cross-family memory interference and scope-matched certification, published 2026-09-24; likely relevant to localization/scope claims. | Primary abstract checked; **full-text novelty comparison urgent**. |
| [DolphinBench](https://arxiv.org/abs/2609.24971) | Newly identified agent-memory benchmark emphasizing task outcomes, cost and latency; relevant to evaluation-consequence framing. | Primary abstract checked; full-text comparison pending. |
| [Mem0 local-Qdrant reset issue #6411](https://github.com/mem0ai/mem0/issues/6411) | Concrete prior reset failure; its own correction limits the defect to affected platforms/storage semantics. Do not cite as a universal local-Qdrant failure. | Official issue checked; fix/version and platform qualification need precise citation. |

## Missing literature work before an A-level submission

1. **2026-09-27 update:** a 20-entry DOI-registry-backed starter bibliography now exists at `docs/literature/references.bib` with a 10/10 structural/metadata audit. It is not yet venue-normalized or submission-ready; `docs/literature/RELATED_WORK_CURRENT.md` tracks the claim boundaries.
2. The highest-risk Cross-Unit Separation paper, V32 Agentic Benchmark Checklist / MemSecBench, and newly identified A-TMA / Scope Before You Persist papers received targeted primary full-text comparison in `docs/literature/RELATED_WORK_CURRENT.md`. Other adjacent papers and final manuscript sentences still need full-text, claim-by-claim checks before a novelty assertion.
3. Literature search must be refreshed near submission because adjacent memory and benchmark-audit work is appearing rapidly. This audit did not establish that no closer unpublished or newly posted work exists.
4. The final paper needs a claim-to-artifact ledger: every numerical claim linked to cohort denominator, frozen code/model, terminal receipts and the correct judge boundary. V55/V56 have many such pieces, but a consolidated paper ledger is not yet built.

## Current priority

Finish and audit the V57 runtime/causal protocol before additional expensive model calls; in parallel, turn this source ledger into a verified BibTeX library and a concise novelty matrix. Do not rewrite V55/V56 history, and do not treat the stale dated status paragraph inside the user's original `IDEA.md` as the current state.
