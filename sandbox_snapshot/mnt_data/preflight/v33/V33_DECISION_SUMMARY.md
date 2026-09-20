# V33 Decision Summary: Public Score Forensics

Date: 2026-09-19

Status: `IDEA_VALIDATION_V33_C33_TWO_PUBLIC_PROVIDER_SCORE_AFFECTING_TRACES_FORMAL_PILOT_UNLOCKED`

## Decision

C33 survives the V32 empirical kill gate. The reason is empirical evidence, not conceptual novelty.

Two independent provider integrations in a frozen public Agent Memory Benchmark artifact now show behaviorally accessible state crossing benchmark lifecycle boundaries, and both contain trace-level score effects.

## Mem0 result

Four high-confidence deletion-target residuals are directly score-negative in the committed trace: `sf-02`, `sf-05`, `sf-06`, and `ce-05`. Each test asks for an empty result after the harness has invoked deletion, yet retrieves the target at score 0.9 and receives score 0.

A provenance-limited scorer counterfactual that removes only those four observed residual rows, changing nothing else, moves the exact weighted score from `7.142857` to `12.767857`, reported `7 -> 13`. This is a trace counterfactual, not a clean-rerun estimate.

The earlier `ma-03` stale `fix-agent` memory remains a separate score-neutral cross-run contamination trace.

## Zep result

The frozen Zep adapter uses one user for the full benchmark, searches only at that run-level user scope, ignores query agent identity, and implements per-memory delete as a no-op. The runner's intended per-test isolation therefore does not reach the provider state surface used by search.

The committed Layer-1 artifact has 59 query records. A same-UUID scan finds 57 queries with at least one exact memory ID first seen in another earlier test, 30 queries whose entire recorded Top result set consists of prior-test IDs, and 24 distinct reused IDs.

`tr-06-q1` is a direct score-positive contamination signature. It expects keyword `4`. All three recorded retrievals are prior-test IDs and none states the correct team size. One stale staging-URL result contains digit `4` inside `amb-user-1774992130225`; the frozen substring scorer accepts that and assigns score 1. Removing the prior-test results from the recorded trace flips this query to fail and changes the exact overall score from `10.684524` to `8.541667`, reported `11 -> 9`.

The same artifact also contains score-masked leakage: six expect-empty queries pass with three non-empty prior-test results because all retrieval scores are below 0.1.

## Research implication

The central empirical finding is now broader than one provider bug: hidden trial state can make a recorded benchmark result worse, better, appear clean despite leakage, or leave the score unchanged. The benchmark metric alone therefore cannot serve as evidence that trial state was isolated.

This does not justify a claim that AMB, Mem0, Zep, or agent-memory benchmarks generally are invalid. The public results establish concrete trace-level cases in pinned integrations.

## Stage transition

Formal large-scale experiment remains unstarted, but the **formal pilot is unlocked**. V33 freezes provisional RQs and a study set that combines:

- public forensic positives: AMB × Mem0 Cloud and AMB × Zep Cloud;
- controlled paired-runtime targets: Redis benchmark × Mem0 OSS 2.0.19 and MemArena × Mem0 OSS 2.0.11;
- negative controls: MemoryData and ForgetEval.

Redis/MemArena exact runtime remains required for cross-benchmark controlled causal replication, but it is no longer required to keep C33 alive as an empirical paper candidate.
