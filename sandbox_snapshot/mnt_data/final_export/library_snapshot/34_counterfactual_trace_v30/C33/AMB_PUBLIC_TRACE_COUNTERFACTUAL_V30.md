# V30 Public-Trace Counterfactual Audit: AMB × Mem0 Cloud

## Scope

This audit continues C33, **Trial-State Attestation for Agent-Memory Benchmarks**, from V29. It closes one previously open question for the committed Agent Memory Benchmark v2.0.0 Mem0 result: whether the already observed stale Layer-1 retrieval changed the frozen benchmark score in that historical artifact.

Frozen target: `AlekseiMarchenko/agent-memory-benchmark@55d4f02d61388525105ffe34fe3f9d2c846d25bf`.

The audit is intentionally narrow. It evaluates the committed `ma-03-q1` trace under the benchmark's own Layer-1 scoring rule. Provider-backed paired replay remains a separate runtime gate.

## Provenance chain

The frozen runner executes Layer 1 before Layer 2. In Layer 1, `ma-03` stores its intended root-cause memory under `debug-agent`, while the query `what is the bug` searches under `fix-agent`. The Mem0 adapter maps `agentId` directly to Mem0 `user_id`.

The committed `amb-results-mem0/results.json` records one `fix-agent` retrieval for `ma-03-q1`:

> User applied a fix that increased the connection pool to 100 and added a connection timeout of 5 seconds

The frozen Layer-2 fixture `l2-04` contains the stable `fix-agent` seed:

> Fix applied: increased connection pool to 100, added connection timeout of 5 seconds

A repository-wide check over the frozen Layer-1 category definitions found `fix-agent` only at the `ma-03` query, while the Layer-2 fixtures use it only for the `l2-04` fix seed. A second scan compared every committed Layer-1 retrieved result against strings in all five Layer-2 fixtures. At normalized Jaccard threshold 0.45, exactly one hit appeared, the same `ma-03` retrieval against `l2-04`, with normalized Jaccard 1.0 after stopword normalization.

Because Layer 2 runs after Layer 1, that retrieved `l2-04`-derived memory predates the current Layer-1 execution. The public artifact therefore contains a behaviorally visible stale-state retrieval.

## Counterfactual scoring

Layer-1 scoring is retrieval-direct. For an `expectedKeywords` query, the query passes only when every expected keyword occurs somewhere in the retrieved contents. `ma-03-q1` expects `race condition` and `queue`.

The committed dirty trace retrieves only the stale fix memory. It contains neither expected keyword, so the recorded query score is 0. The verified-clean counterfactual removes only that provenance-identified stale retrieval. The resulting retrieval set is empty and still contains neither expected keyword, so the query score remains 0.

This yields a clean causal result for the frozen artifact:

| Outcome | Dirty public trace | Clean counterfactual | Delta |
|---|---:|---:|---:|
| Retrieved results | 1 | 0 | -1 |
| `ma-03-q1` score | 0 | 0 | 0 |
| Multi-agent passed queries | 1/6 | 1/6 | 0 |
| Multi-agent score | 16.6667% | 16.6667% | 0 pp |
| Overall reported score | 7 | 7 | 0 |
| `ma-03-q1` estimated tokens | 30 | 4 | -26 |
| Total estimated tokens | 1276 | 1250 | -26 |

The token result follows the benchmark's own estimator `ceil(text.length / 4)`. The query contributes 4 estimated tokens. The stale 104-character retrieval contributes 26, producing the recorded 30.

## Representation → retrieval → answer → score

For this Layer-1 case, the causal chain resolves as follows.

**Representation:** stale provider state is present under the behaviorally queried `fix-agent` scope.

**Retrieval:** the stale state is observable in the committed result and disappears in the clean counterfactual.

**Answer:** Layer 1 has no separate answer-generation stage. The benchmark scores retrieved contents directly.

**Score:** this exact contamination event is score-neutral. It changes the retrieval set and token proxy while leaving pass/fail unchanged.

## Scientific interpretation

V30 converts the AMB historical trace from an open score-causality question into a bounded negative result. The trace demonstrates real benchmark-observable contamination, while the frozen scoring rule shows zero score distortion for this specific query and artifact.

That result strengthens the paper's claim discipline. C33 has direct evidence that trial-state cleanliness can fail at the benchmark/provider boundary and alter observable retrieval behavior. The current evidence does not support a claim that this AMB artifact's reported score was inflated or depressed by the identified stale memory.

The remaining paper-critical bottleneck is provider-backed paired causality on a benchmark path where stale state can alter later representation or retrieval under an ordinary lifecycle event. Redis mid-ingest retry remains the first runtime target, followed by the MemArena repeated-run sidecar replay. A real AMB preseeded-scope replay remains useful as a reproducibility confirmation, while its historical score-causality question is now closed for the observed trace.

## Decision

C33 remains the sole primary candidate. V30 keeps the working title **Trial-State Attestation for Agent-Memory Benchmarks** and advances the public-trace branch to `RETRIEVAL_CONTAMINATION_CONFIRMED_SCORE_NEUTRAL_FOR_OBSERVED_TRACE`.

Formal experiment status remains `NOT_STARTED`. The next hard gate is a real clean-vs-native paired runtime trial on the frozen Redis/Mem0 path, with representation, retrieval, answer where applicable, and score recorded separately.
