# V28 Experimental Plan

## RQ0 — Does nominal reset satisfy the behavioral clean-state contract?

For each audited integration, enumerate behaviorally active persistent surfaces from source and confirm with runtime trace where feasible. Produce a reset receipt after the benchmark's own reset call.

Primary output: per-surface pre/post counts and hashes, plus a binary postcondition result.

## RQ1 — Does residual state alter constructed memory or retrieval?

Use paired replay from an identical sidecar snapshot. Change only whether the residual behaviorally active surface is cleaned after invoking the native benchmark reset.

Primary measures:

- final memory-set equality and Jaccard overlap on content hashes;
- retrieval Top-k equality/Jaccard on content hashes;
- fraction of paired examples with any difference;
- add/retrieval latency difference.

## RQ2 — Does residual state alter benchmark answer outcomes?

Only open RQ2 after RQ1 shows nontrivial observable differences. Reuse the benchmark's own answer/judge path. Report paired discordance and confidence intervals rather than only aggregate averages.

## RQ3 — Which benchmark designs avoid the failure mode?

Use negative controls to separate provider persistence from benchmark exposure:

- inference bypass (`infer=False`);
- unique disposable scopes;
- whole-store or whole-agent reset;
- explicit sidecar isolation.

## Pilot progression

1. MemArena exact n=15 Day-3 add-latency subset.
2. Redis one-example deterministic mid-ingest fault; then a small stratified set of multi-session examples.
3. Expand only integrations with confirmed residual + consumption + RQ1 effect.

## Statistics

Do not predeclare a historical score bias direction. For full paired runs:

- report paired difference rate with confidence interval;
- report Top-k set-overlap distribution;
- for binary judged correctness, report discordant pair counts and exact McNemar test when sample size supports it;
- for latency, report paired median difference and bootstrap confidence interval;
- report all mechanism-positive but outcome-null results.

Use effect estimates and confidence intervals as the main evidence. Avoid significance-only claims.

## Reproducibility

Freeze repository SHA, provider package version/tag SHA, model identifier, temperature, embedding config, dataset digest, exact sample IDs, arm order seed, state-snapshot hash, and all reset receipts.
