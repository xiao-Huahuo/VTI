# V43 decision summary

Date: 2026-09-20

Project: `AM-AUTO-20260918-R1`

## Decision

The V42 DeepSeek pilot establishes the lifecycle mechanism at E1 but does not
identify a causal E2 or E3 effect.

All 12 V42 native-versus-clean pairs reached the mechanical trigger: native
reset left 10 scoped message rows, verified cleanup left zero, both arms had zero
scoped vectors before re-ingestion, and the first extraction prompt differed.
All 12 pairs subsequently produced different memory sets, retrieval sets, and
answer hashes.

However, the prospective V43 clean-clean negative control invalidates the causal
interpretation of those downstream inequalities. In all three control cases,
both arms had zero messages and vectors and their first extraction prompt hashes
were identical, yet memory, retrieval, and answer hashes still diverged.

V43 median memory Jaccard was `0.0119363395` and median retrieval Jaccard was
`0.0`. These values overlap the V42 first-three-case values; the retrieval
Jaccards were exactly the same sequence: `0.0`, `0.0`, `0.0526315789`.

## Supported claims

- E1: the benchmark-native scoped reset leaves behaviorally consumed Mem0
  message state, while verified cleanup removes it.
- DeepSeek thinking-mode exact-hash comparisons have a very large stochastic
  baseline under identical clean state.

## Unsupported claims

- V42 does not establish that residual state caused the observed representation,
  retrieval, or answer divergence.
- The 12/12 nominal E3 labels from the V42 mechanical classifier must not be
  reported as causal E3 evidence after V43.
- E4 was not measured.

## Next gate

DeepSeek officially supports non-thinking mode. The next experiment must first
test a non-thinking, temperature-zero clean-clean control. A native-versus-clean
rerun is justified only if that control materially suppresses baseline
divergence. Otherwise this provider stack cannot identify the causal endpoint
with exact-hash outcomes and requires replicated distributional estimands.
