# V33 Public Score Forensics: Hidden Trial State in AMB

Date: 2026-09-19  
Project: AM-AUTO-20260918-R1  
Candidate: C33  
Frozen benchmark: `AlekseiMarchenko/agent-memory-benchmark@55d4f02d61388525105ffe34fe3f9d2c846d25bf`

## 1. Purpose

V32 left C33 alive only as an empirical audit. V33 therefore asks a narrower question: do committed public benchmark artifacts already contain trace-level evidence that hidden lifecycle state changes the reported benchmark score?

The answer is yes for two independent provider integrations in the same frozen benchmark artifact family. The direction of the score effect differs by provider. This report separates observed trace facts from clean-rerun counterfactuals.

## 2. Mem0 Cloud: deleted-target residuals are directly score-negative

The frozen runner handles `store-then-delete` tests by storing seed memories, invoking `adapter.delete(id)`, waiting three seconds, then executing the query. An `expectEmpty` query fails when it receives a result whose score is at least 0.1.

The committed Mem0 result contains four high-confidence cases where a target that the harness attempted to delete is still retrieved at score 0.9 after that lifecycle step:

- `sf-02-q1`: deleted temporary workaround reappears, score 0.
- `sf-05-q1`: deleted deprecated-endpoint memory reappears, score 0.
- `sf-06-q1`: deleted auth-bug memory reappears, score 0.
- `ce-05-q1`: deleted temporary test memory reappears, score 0.

The created timestamps of these rows align with the current run's selective-forgetting and cost-efficiency execution window. This is distinct from the older `ma-03` cross-run stale trace recovered in V29/V30.

Two further selective-forgetting rows, `sf-03-q1` and `sf-04-q1`, also retrieve content that the test explicitly attempted to delete, but the expected surviving content is absent from recorded Top-k. They are retained as lifecycle-residual observations and excluded from the direct score-flip lower bound.

### Trace-restricted counterfactual

V33 changes only the four provenance-matched residual rows above from fail to pass and leaves every other recorded result untouched. Under the frozen category weights:

- exact weighted score: `7.142857 -> 12.767857`;
- reported rounded score: `7 -> 13`;
- query flips: `4`.

This is a trace-level lower-bound-style scorer counterfactual. It is not a prediction of a fully clean rerun, because a clean provider may return additional correct or incorrect memories that are absent from the recorded dirty trace.

## 3. Zep Cloud: cross-test state is structural in the adapter

The frozen Zep adapter creates one run-level user, stores each test under a thread derived from the test's agent id, searches the graph using only the run-level user id, and ignores the query's agent id. Its per-memory `delete(id)` returns success without deleting state. The user is deleted only in final benchmark cleanup.

The runner, in contrast, creates a unique default agent id per test specifically to prevent cross-test pollution and calls `adapter.delete(id)` after each ordinary test. The adapter therefore violates the lifecycle boundary the runner is trying to establish.

A deterministic same-UUID scan over the committed Zep Layer-1 result finds:

- 59 query records;
- 57 queries return at least one UUID previously observed in a different earlier test;
- 30 queries have every recorded Top result drawn from UUIDs already observed in earlier tests;
- 24 distinct prior-test UUIDs recur later;
- 8 passing queries have every recorded Top result drawn from prior tests.

UUID equality is important here. This is stronger than semantic similarity: the exact same provider object is visible across test boundaries.

## 4. Zep `tr-06`: stale state creates a public false-positive score

`tr-06-q1` asks `how many people on the team` and the frozen test expects the keyword `4` after the sequence 3 engineers -> 5 engineers -> 4 engineers.

The committed query receives three Top results, all exact UUIDs previously observed in other tests:

1. GitHub Actions fact;
2. React experience fact;
3. staging URL fact containing the run-level identifier `amb-user-1774992130225`.

None states that the team has four engineers. The third stale result nevertheless contains the character `4` inside the user identifier. The frozen scorer lowercases concatenated retrieval content and applies ordinary substring containment for each expected keyword. Therefore the stale identifier satisfies expected keyword `4`, and the query receives score 1.

Removing those prior-test results from this recorded trace flips `tr-06-q1` from pass to fail. With every other recorded outcome held fixed:

- temporal-reasoning category: `1/7 -> 0/7`;
- exact weighted score: `10.684524 -> 8.541667`;
- reported rounded score: `11 -> 9`.

This proves score dependence on stale prior-test output in the committed artifact. It does not establish what a clean Zep rerun would retrieve for `tr-06`; a clean rerun could still retrieve the correct four-engineer fact.

## 5. Score-masked contamination

The same frozen scorer treats an `expectEmpty` query as passing when every returned result has a defined score below 0.1. In the committed Zep artifact, `sf-01`, `sf-02`, `sf-05`, `sf-06`, `ce-05`, and `ce-07` all pass while each records three non-empty results. Every one of those recorded result IDs had already appeared in a different earlier test, and their scores are below 0.1.

Thus the benchmark can contain observable cross-test leakage while the binary metric reports success. This is a measurement finding rather than a provider-quality judgment.

## 6. Four observable regimes

The public artifacts now exhibit four distinct relations between hidden state and score:

1. **Score-negative contamination**: Mem0 deleted-target residuals make expected-empty tests fail.
2. **Score-positive contamination**: Zep `tr-06` receives a false pass through a stale identifier substring.
3. **Score-masked contamination**: Zep expected-empty tests pass despite non-empty prior-test retrievals because scores stay below 0.1.
4. **Score-neutral contamination**: Mem0 `ma-03` retrieves an older stale memory, but its recorded score remains 0 with or without that stale result.

This taxonomy is descriptive. It is grounded in committed public artifacts and the frozen scoring code, not in a claim that all benchmark results are invalid.

## 7. Current-main persistence check

The Zep adapter blob on the current default branch has the same SHA as the frozen March 31 adapter: `ff9c2d0dc9f24191b4ad30bfbd40e8f187ef8990`. Therefore the run-level user search plus no-op per-memory delete mechanism remained present when checked on 2026-09-19. Later benchmark versions add scale testing and configurable store delay, but this adapter lifecycle contract remains unchanged.

## 8. Research consequence

V33 materially changes the project. C33 no longer depends on Redis/MemArena exact runtime merely to establish that hidden trial state can affect a real benchmark score. Two public provider integrations now contain observed trace evidence, including effects in opposite score directions.

Redis and MemArena remain valuable for controlled paired causal reproduction and cross-benchmark generalization. They are no longer the sole evidence holding the main empirical thesis open.
