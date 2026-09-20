# V42 decision summary

Date: 2026-09-20

## Execution

The V42 prospective amendment replaced the unavailable OpenAI stack with:

- DeepSeek Flash in low-thinking mode for Mem0 extraction and answers;
- local FastEmbed 0.8.0 using `BAAI/bge-small-en-v1.5`;
- no judge, so E4 was not measured.

The frozen V34 cohort, Redis commit, Mem0 2.0.19 version, failure point, paired
snapshot, cleanup intervention, Top-10 retrieval endpoint and bootstrap seed were
preserved. All 12 cases completed. A local-proxy outage affected cases 10–12;
fail-closed recovery reran only those cases by direct API connection.

## Mechanical result

- Trigger reached: 12/12.
- Native post-reset message rows: 10 in every case.
- Verified-clean message rows: 0 in every case.
- Post-reset scoped vectors: 0 in both arms.
- First extraction prompt differed: 12/12.
- Memory, retrieval and answer hashes differed: 12/12.
- Mechanical classifier label: E3 in 12/12.

The nominal E2+ bootstrap estimate was 1.0 with percentile interval `[1.0, 1.0]`.

## Superseding interpretation

V43 and V44 clean-clean controls produced downstream divergence with identical
clean state and identical first extraction prompts. Their divergence overlapped
the V42 effect. Therefore V42's mechanical E3 labels must not be interpreted as
lifecycle-caused E3 evidence.

V42 supports E1. Causal E2/E3 remain unresolved.
