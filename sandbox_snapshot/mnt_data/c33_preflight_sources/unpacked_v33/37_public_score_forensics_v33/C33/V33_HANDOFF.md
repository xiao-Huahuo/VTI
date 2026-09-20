# V33 Handoff

Canonical root: `/Research/AgentMemory/AM-AUTO-20260918-R1`

Primary candidate: C33  
Working title: **Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit**

Status: `IDEA_VALIDATION_V33_C33_TWO_PUBLIC_PROVIDER_SCORE_AFFECTING_TRACES_FORMAL_PILOT_UNLOCKED`

## Critical change from V32

V32 required strong empirical evidence to keep C33 alive after generic reset-attestation novelty was removed. V33 finds that evidence in committed public benchmark artifacts.

### AMB × Mem0 Cloud

The frozen public result contains multiple deletion-target residuals after the benchmark invokes deletion. Four rows have direct binary score impact under the recorded scorer: `sf-02`, `sf-05`, `sf-06`, and `ce-05`.

Trace-restricted removal of those four residual rows changes reported score `7 -> 13`. Keep the label **trace counterfactual**. A fully clean rerun remains unobserved.

### AMB × Zep Cloud

The adapter's lifecycle boundary is structurally broader than the runner assumes: one user spans the full run, search ignores per-test agent identity, and per-memory delete is a no-op.

The public Layer-1 result shows exact UUID reuse across different tests in 57/59 query records. `tr-06` is a direct false-positive score signature: all recorded results are prior-test IDs, and keyword `4` matches the stale user identifier rather than a team-size fact. Removing prior-test results from that trace changes reported score `11 -> 9`.

Six expect-empty queries also pass with non-empty prior-test retrievals because all returned scores are below 0.1.

## Claim boundary

Defensible now:

- hidden lifecycle state is directly observable in two public provider integrations;
- committed score can depend on that state in both negative and positive directions;
- binary benchmark success can also mask visible leakage;
- public trace forensics and controlled paired replays must be reported as different evidence classes.

Still excluded:

- field-wide prevalence;
- broad invalidity of published memory benchmarks;
- clean-rerun score estimates inferred from trace deletion;
- method novelty for verified reset/isolation.

## Next action

Freeze the formal pilot protocol around RQ1 lifecycle escape surfaces, RQ2 effect ladder, and RQ3 negative-control designs. Continue public/provider audits for an additional independent benchmark family while retaining Redis and MemArena exact runtime as controlled causal replications.
