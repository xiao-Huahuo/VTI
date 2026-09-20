# V31 Handoff

Canonical root: `/Research/AgentMemory/AM-AUTO-20260918-R1`

Primary candidate: C33 — Trial-State Attestation for Agent-Memory Benchmarks

Status: `IDEA_VALIDATION_V31_C33_REDIS_PRE_LLM_CONSUMPTION_ATTESTED_EXACT_RUNTIME_PENDING`

## What changed from V30

V30 closed the score counterfactual for the public AMB contamination trace. V31 returns to the primary Redis runtime gate and advances the causal chain one step before external credentials are required.

An executable provider-independent replay of the frozen Mem0 2.0.19 sidecar and prompt-builder logic now attests that a partial successful retry leaves scoped message rows across the benchmark's native reset surface and that those rows enter the next extraction prompt through `Last k Messages`.

Observed fixture receipt:

- message rows before native reset: 3
- after native reset: 3
- after verified cleanup: 0
- native retry `Last k Messages`: 3 rows
- clean retry `Last k Messages`: 0 rows
- extraction prompt byte delta: +103 in native arm
- extraction prompt SHA-256 differs

The claim stops at pre-LLM prompt consumption.

## Important protocol correction

Use `redis_mid_ingest_retry_probe_v31.py` for the real paired run. V31 supersedes the unexecuted V28 script because V28 explicitly set the Mem0 extraction LLM to its answer-model argument. The frozen benchmark leaves Mem0 extraction on its provider default, which resolves to `gpt-5-mini`; the benchmark answer model defaults to `gpt-4o`.

V31 also clones the complete failed-attempt Qdrant plus SQLite state into both paired arms before reset, rather than cloning SQLite alone.

## Next hard gate

Run the V31 probe on the exact Redis commit with `mem0ai==2.0.19`, local Qdrant dependencies, LongMemEval cache/network access, and `OPENAI_API_KEY`.

Interpret in this order:

1. vector and message post-reset receipts;
2. first extraction-prompt hash divergence;
3. final memory fingerprint divergence;
4. retrieval Top-k divergence;
5. answer divergence;
6. optional official LongMemEval judge-score divergence.

If Redis yields a downstream null after prompt divergence, run the MemArena n=15 paired sidecar replay before deciding whether to downscope C33.
