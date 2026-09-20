# V42 prospective DeepSeek protocol amendment

V42 exists because the frozen OpenAI-backed V34 stack cannot be executed with
the available account: authenticated OpenAI requests return
`credit_balance_exhausted`, and the user cannot purchase credits.

This amendment was made before any formal cohort case was executed or observed.

## Preserved design

- Redis Agent Memory Benchmark commit and Mem0 2.0.19 remain pinned.
- The exact V34 12-case cohort remains unchanged.
- Failure is injected immediately before the fourth session-level add.
- Both arms start from the same complete failed-attempt state.
- The intervention remains native reset versus native reset plus scoped
  message-sidecar cleanup.
- E2+ remains the primary endpoint.
- The 5000-resample bootstrap and seed 20260919 remain unchanged.

## Provider changes

- Mem0 extraction: `deepseek-flash` through the official DeepSeek API with
  `reasoning_effort=low` explicitly enabled.
- Answer generation: `deepseek-flash` through the official DeepSeek API with
  `reasoning_effort=low` explicitly enabled while retaining the benchmark prompt.
- Embedding: local FastEmbed 0.8.0 with `BAAI/bge-small-en-v1.5`, 384 dimensions.
- Judge scoring: disabled for this pilot. E4 is therefore unmeasured, not null.

The local embedder is necessary because the official DeepSeek API does not
provide the OpenAI embeddings endpoint used by the original Mem0 default stack.

## Interpretation

V42 can establish whether the audited lifecycle mismatch is consumed and causes
representation, retrieval, or answer divergence under this revised provider
stack. It cannot be reported as an exact reproduction of the OpenAI-backed V34
stack, and it cannot establish E4 score divergence without an independent judge.
