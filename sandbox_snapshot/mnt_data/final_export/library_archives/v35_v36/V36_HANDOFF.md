# V36 Handoff

Project: AM-AUTO-20260918-R1

Primary candidate: C33

Status: `FORMAL_PILOT_READY_V36_C33_LIFECYCLE_TOPOLOGY_MATRIX_FROZEN_STRUCTURAL_CONTROL_ADDED`

## New external control

Pinned source:
`basicmachines-co/basic-memory@3bf2d523c0a941f71cb144a5502e7557dd025d69`

LongMemEval grouped execution uses:
- random default base run ID;
- one group per question;
- group-suffixed run IDs;
- Mem0 user IDs derived from the group run ID;
- Qdrant collection/path derived from the same group run ID;
- fresh provider instances per group;
- default `MEM0_INFER=false`.

Classification:
`STRUCTURAL_NAMESPACE_CONTROL_DEFAULT_PATH_UNATTESTED_CLEANUP`

Cleanup exceptions are still suppressed, so do not call it independently proven clean. Manual reuse of a fixed run ID can reuse a namespace. On the ordinary default path, cross-group and cross-run namespace reuse is structurally avoided.

## OmniMemEval follow-up

No committed raw runtime result directory, delete receipt, streaming event bundle, or GitHub release artifact was found in the frozen public repository. V35 therefore stays E0 until a live or external raw trace is available.

## Frozen lifecycle topology classes

T1 shared scope + ineffective cleanup
T2 stable scope + false clean acknowledgment
T3 reused scope + partial active-surface reset
T4 per-example destructive recreation
T5 disposable per-run/per-group namespace

Use the classes as an empirical reporting framework, not as method novelty.

## Next work

1. Continue searching public benchmark artifacts for direct object provenance, especially score-affecting traces outside AMB.
2. Audit one benchmark family that uses persistent local state plus resume/retry to test whether T3 generalizes beyond Mem0 sidecars.
3. Keep V34 Redis and MemArena exact paired protocols unchanged.
