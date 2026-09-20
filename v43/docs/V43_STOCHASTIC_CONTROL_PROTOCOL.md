# V43 stochastic negative-control protocol

V42 produced downstream divergence in all 12 native-versus-clean pairs. Because
DeepSeek extraction and answering are generative, exact hash inequality alone can
also arise when two runs receive identical inputs.

V43 therefore uses the first three ranks of the already frozen cohort. Each case
reconstructs the same failed-attempt snapshot as V42, then creates two independent
arms that both receive the verified-clean intervention. Both arms must have zero
scoped message rows and zero scoped vectors before re-ingestion. Their first
extraction prompt hashes must be identical.

The control compares final memory content hashes, Top-10 retrieval content hashes,
and answer hashes. Divergence estimates the stochastic baseline under identical
lifecycle state. This control was specified after observing the V42 results and is
therefore an explicit follow-up validity check, not part of the original V42 pilot.
