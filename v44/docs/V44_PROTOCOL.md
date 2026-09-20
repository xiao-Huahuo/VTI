# V44 non-thinking deterministic-mode control

V43 showed that DeepSeek thinking-mode output diverges strongly even when both
arms receive identical verified-clean state and identical first extraction
prompts. V44 tests whether the official non-thinking mode with temperature zero
materially suppresses that baseline.

The first frozen cohort case is the initial diagnostic gate. Both arms are
verified-clean. DeepSeek requests include `thinking.type=disabled`; extraction
and answer generation use temperature zero. Embeddings remain local FastEmbed
`BAAI/bge-small-en-v1.5`.

If the first clean-clean pair still shows memory/retrieval divergence at the V43
scale, no native-versus-clean rerun will be interpreted causally under this
provider stack. If divergence is materially suppressed, the control expands to
the first three frozen cases before any amended main-effect rerun.
