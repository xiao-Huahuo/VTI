# V36 Decision Summary

Date: 2026-09-19
Project: AM-AUTO-20260918-R1
Primary candidate: C33
Working title: Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit

Status: `FORMAL_PILOT_READY_V36_C33_LIFECYCLE_TOPOLOGY_MATRIX_FROZEN_STRUCTURAL_CONTROL_ADDED`

## Decision

V36 adds one independent exploratory lifecycle control without changing the V34 frozen primary pilot:
`basicmachines-co/basic-memory@3bf2d523c0a941f71cb144a5502e7557dd025d69`.

Its LongMemEval grouped execution provides a strong structural namespace-isolation pattern for Mem0:

- CLI default run ID is a fresh 12-hex UUID fragment.
- Each LongMemEval question is a distinct group.
- The grouped runner derives a group-specific run ID: `<base_run_id>-<question_id>`.
- Mem0 user scope is `bm-bench-<group_run_id>-mem0`.
- Local Qdrant collection and on-disk path are also derived from the group-specific run ID.
- Mem0 provider instances are fresh per group by default.
- The committed grouped-run tests explicitly assert distinct group-suffixed run IDs and fresh provider instances.
- The Mem0 benchmark default is `infer=false`, which disables the inferred-extraction message-sidecar path central to the Redis/MemArena mechanism.

This means ordinary cleanup failure does not make the next default LongMemEval group share the same Mem0 user or Qdrant namespace. A new default benchmark run also receives a fresh base run ID.

The provider cleanup routine still suppresses deletion errors. Therefore this is not classified as independently attested clean state. If an operator manually reuses the same run ID, the same namespace can be reused. Classification:

`STRUCTURAL_NAMESPACE_CONTROL_DEFAULT_PATH_UNATTESTED_CLEANUP`

This is a useful external negative/control design because it shows that Mem0 itself does not force cross-trial leakage; harness lifecycle topology determines exposure.

## OmniMemEval public-artifact follow-up

The frozen OmniMemEval git tree contains no committed `results/` runtime directory, delete-status receipt, event log, or streaming result bundle. The repository also has no GitHub release assets at the audited point.

Therefore V35's OmniMemEval × Zep false-clean path cannot be upgraded retrospectively from E0 using repository artifacts alone. A live reproduction or externally preserved raw run artifact is required.

## Lifecycle topology matrix

V36 freezes an empirical organization of the audited integrations. This is an analysis taxonomy, not a novelty claim:

- T1 shared run scope + ineffective per-trial cleanup:
  AMB × Zep. Public E4 contamination exists.
- T2 stable unit scope + false cleanup acknowledgment:
  OmniMemEval × Zep. E0 source/control-flow evidence.
- T3 stable/reused scope + partial reset of behaviorally active surfaces:
  Redis × Mem0 and MemArena × Mem0. E1/source evidence; E2+ paired runtime pending.
- T4 per-example destructive recreation:
  RoMem DMR-MSC × Zep. Strong lifecycle control, cleanup postcondition unverified.
- T5 disposable per-run + per-group namespaces:
  Basic Memory × Mem0. Strong structural control on the default path; cleanup postcondition unverified.

The matrix sharpens RQ3: prevention can come from verified cleanup, or from avoiding namespace reuse in the first place.

## Protocol discipline

Basic Memory is added only as an exploratory external control. It is excluded from the V34 primary pilot endpoint and does not alter:
- Redis n=12 selection,
- MemArena n=15 selection,
- E0-E4 evidence hierarchy,
- primary E2 endpoint,
- statistical plan.

Formal Pilot remains protocol-frozen and not yet executed on credentialed runtimes.
