# Replacement Candidate Screen V20

Project: AM-AUTO-20260918-R1
Date: 2026-09-19

C30 is closed as a main idea. V20 explicitly excludes asynchronous readiness variants from replacement generation.

## C33 Residual-State Contamination / Reset Attestation

Decision: PRIMARY_PROVISIONAL.

Reason: real benchmark reset calls can be bound to a real provider reset defect that silently leaves state behind. The phenomenon affects experimental independence rather than ordinary retrieval quality. A deterministic exact-logic fixture reproduces cross-run retrieval contamination.

Next Gate: current-version and historical-version paired reset census, followed by score-impact replay.

## C34 Benchmark-to-Production Path Fidelity

Decision: KILLED_AT_SCREEN.

Reason: public Agent Memory projects already explicitly distinguish benchmark and production paths, document historical cases where benchmarked retrieval lanes were absent from the live path, and increasingly require production/shipped-path measurement. The observation is useful as an audit dimension but the broad contribution is already occupied.

## C35 Shadow-Memory Attribution

Decision: KILLED_AT_SCREEN.

Reason: a public 2026 research track already frames evaluation contamination and shadow-memory attribution around the same causal question: successful recall does not prove the evaluated memory layer caused it. Retain as an experimental control, not a new primary idea.

## C36 Derived-State Correction Reach

Decision: KILLED_AT_SCREEN.

Reason: current public benchmark critiques already specify correction tests that inspect summaries, profiles, graph edges and other derived artifacts after a correction. The mechanism is valuable but direct prior-art overlap is too strong.
