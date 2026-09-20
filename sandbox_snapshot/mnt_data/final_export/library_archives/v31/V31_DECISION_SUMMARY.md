# V31 Decision Summary — C33

Date: 2026-09-19

Status: `IDEA_VALIDATION_V31_C33_REDIS_PRE_LLM_CONSUMPTION_ATTESTED_EXACT_RUNTIME_PENDING`

## Decision

C33 remains the sole primary candidate under the working label **Trial-State Attestation for Agent-Memory Benchmarks**.

V31 advances the Redis integration from source-proved state reachability to an executed pre-LLM consumption gate. The frozen Mem0 2.0.19 message-sidecar logic was replayed through its deterministic state and prompt-building functions. A partial successful attempt leaves three scoped message rows; the benchmark's native scoped reset surface preserves those rows; the retry consumes them in `Last k Messages`. The independently verified-clean arm has zero rows and produces a different extraction prompt hash.

This is causal evidence at the prompt boundary. It does not yet establish a change in extracted memory representation, retrieval, answer, or benchmark score.

## Protocol repair found during review

The unexecuted V28 exact-runtime script would have overridden Mem0's default extraction LLM with the probe's answer-model argument. In the frozen provider, default Mem0 OpenAI extraction resolves to `gpt-5-mini`, while the Redis benchmark answer model defaults to `gpt-4o`. V31 removes that override.

V31 also changes paired-state branching from history-only copying to full failed-attempt state cloning. Each runtime arm now begins from the same copied Qdrant plus `history.db`, invokes the native reset, and records independent vector and message receipts before re-ingestion.

The V31 runtime script supersedes V28 for execution.

## Evidence ladder after V31

- Redis retry trigger/control-flow reachability: supported by frozen benchmark source.
- Mem0 scoped sidecar persistence: supported by frozen provider source.
- Retry extraction-prompt consumption: **executed and attested** in provider-independent exact-logic replay.
- Exact Mem0 2.0.19 representation effect: pending credentialed runtime.
- Retrieval effect: pending credentialed runtime.
- Answer effect: pending credentialed runtime.
- Official LongMemEval judge-score effect: pending credentialed runtime.

## Runtime status

The current ChatGPT execution container has OpenAI's Python package and HTTPX, while `mem0`, `qdrant_client`, the dataset package/cache and an OpenAI credential are absent. The exact provider run therefore remains an external-runtime gate.

## Novelty status

A narrow 2026 refresh found adjacent reset housekeeping, memory-isolation baselines, lifecycle security, and stateful agent evaluation. These neighbors keep novelty risk high. No direct match was found in this targeted pass for the full C33 bundle of behaviorally active provider-state attestation plus paired native-reset versus independently verified-clean memory-benchmark replay.

Formal Experiment remains `NOT_STARTED`. The next hard gate is the corrected V31 Redis exact-stack paired run. A representation or retrieval difference advances C33 into formal pilot design; a prompt-positive downstream null remains scientifically useful and triggers the MemArena paired gate before any broader claim.
