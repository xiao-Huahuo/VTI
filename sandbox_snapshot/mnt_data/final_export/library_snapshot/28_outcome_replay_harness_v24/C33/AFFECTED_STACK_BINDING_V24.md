# C33 Affected-Stack Binding V24

Project: AM-AUTO-20260918-R1  
Date: 2026-09-19

## Public benchmark binding

MemArena commit `821752b8994b2b1927c5b6d3087c4e24670f13a9` pins `mem0ai==2.0.11` in `pyproject.toml`. Its default Mem0 configuration uses the self-hosted OSS path with embedded Qdrant.

The audited Mem0 2.0.11 `Memory.delete_all()` implementation enumerates memories through `vector_store.list(filters=filters)` without supplying `top_k`. The Qdrant vector-store list implementation defaults to a 100-item page. The later Mem0 issue #6627 and merged fix #6636 document this same defect class: reset can report success after deleting only the first page.

Therefore the provider defect is version-bound to a concrete public benchmark configuration rather than being an abstract future compatibility concern.

## Namespace lifecycle

MemArena LongMemEval V1 assigns `lme_v1_<question_id>` namespaces. LongMemEval V2 uses one stable namespace per domain, `lme_v2_<domain>`, and relies on the ingestion cache so multiple questions share one ingested domain state.

The reset defect can affect an evaluation boundary only when the pre-reset namespace contains more memories than the underlying list page can enumerate, or when another reset defect leaves state for a different reason. Trigger reach must therefore be measured before any outcome claim.

## Claim discipline

This source binding supports the existence of an affected benchmark stack. It does not establish that the published MemArena result files crossed the 100-memory threshold or that any published metric was contaminated.
