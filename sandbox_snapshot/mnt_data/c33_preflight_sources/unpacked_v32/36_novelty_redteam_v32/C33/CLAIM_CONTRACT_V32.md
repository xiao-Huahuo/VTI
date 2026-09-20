# C33 Claim Contract V32

Working title: **Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit**

Status: provisional, late idea validation, conceptual novelty downscoped.

## Central empirical question

When an agent-memory benchmark believes a trial has been reset or isolated, are all provider state surfaces that can influence the next trial actually clean?

## Evidence ladder

### Level E0 — source reachability

Pinned source proves a state surface is written, survives the benchmark's nominal reset/isolation action, and is read on the next transition.

Allowed claim: a reset-contract mismatch is source-reachable.

### Level E1 — executed mechanism

A source-grounded fixture or exact runtime shows the residual surface survives reset and is consumed by the next transition.

Allowed claim: the mechanism executes under the tested route. No downstream outcome claim.

### Level E2 — representation or retrieval effect

Matched native-reset and verified-clean arms from identical pre-reset state produce different stored representations or retrieval sets/ranks.

Allowed claim: hidden trial state changes a benchmark-observable memory result for the tested integration/case.

### Level E3 — answer effect

The benchmark's ordinary answer stage differs under the paired arms.

Allowed claim: hidden trial state changes the generated answer for the tested integration/case.

### Level E4 — score effect

The official frozen scorer/judge yields a different score under the paired arms.

Allowed claim: benchmark outcome sensitivity for the tested integration/case or preregistered sample.

Population or published-score invalidity claims require separate prevalence and historical evidence.

## Current evidence

- Agent Memory Benchmark × Mem0 Cloud: observed historical retrieval contamination; exact recovered trace is score-neutral.
- Redis Agent Memory Benchmark × Mem0 2.0.19: E1 pre-LLM prompt-consumption evidence; real representation/retrieval/answer/score pairing pending.
- MemArena × Mem0 2.0.11: E0 source and protocol reachability; paired runtime pending.
- MemoryData × local Mem0: lifecycle-safe negative control.
- ForgetEval × Mem0 infer=False: mechanism-negative control for the message-sidecar path.

## Novelty boundary after V32

The paper cannot be sold as a new reset principle or generic trial-isolation method. Its only plausible main contribution is a strong empirical audit of real agent-memory evaluation stacks, including concrete hidden-state mechanisms, reproducible receipts, paired causal replays, and negative controls.

## Main-paper survival gate

A main paper requires at minimum:

- two distinct real benchmark/provider integrations with exact runtime mechanism reproduction; and
- at least one integration with E2 or stronger paired effect; and
- no newly found paper that already performs the same memory-benchmark-specific audit object.

Preferred gate: two integrations with E2+, with at least one reaching E3 or E4.

If these conditions fail, downscope to an audit/bug-report artifact rather than stretching the claim.
