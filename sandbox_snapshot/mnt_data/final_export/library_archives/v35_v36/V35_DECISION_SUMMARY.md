# V35 Decision Summary

Date: 2026-09-19
Project: AM-AUTO-20260918-R1
Primary candidate: C33
Working title: Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit

Status: `FORMAL_PILOT_READY_V35_C33_INDEPENDENT_HARNESS_FALSE_CLEAN_ACK_SOURCE_FOUND`

## Decision

V35 adds an independent benchmark-harness source finding in MemTensor/OmniMemEval at commit
`0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d`.

The Zep adapter's `delete_user(user_id)` suppresses all exceptions and does not inspect the returned HTTP
status. The shared streaming cleanup helper interprets a normal return from `delete_user()` as successful
cleanup and returns `(True, None)`. It can therefore record `initial_delete_status=ok` or
`final_delete_status=ok` even when the provider deletion request failed.

The next step, `prepare_user_after_delete`, calls `add_user(user_id)`. The Zep adapter accepts HTTP 409 as
success. If the earlier delete silently failed because the user still exists, user creation can therefore
also appear successful and the benchmark proceeds under the old provider scope.

This establishes a source-proved false-clean-acknowledgment path:

`delete fails -> adapter suppresses failure -> harness records clean -> recreate returns/accepts existing scope -> stale state can remain behaviorally reachable`

No live Zep execution has been performed in this environment. V35 classifies the finding as
`E0_EXECUTED_CONTROLFLOW`, not E1 provider evidence.

## Breadth inside OmniMemEval

The same shared `delete_user_data()` helper is used by the streaming paths for:

- LongMemEval
- BEAM
- PersonaMem v2
- HaluMem

Each uses version-derived stable benchmark user IDs and performs delete/add/search/delete lifecycle operations.
The source-level false-clean acknowledgment is therefore a harness-wide Zep lifecycle risk rather than a
single LongMemEval call-site quirk.

The older non-streaming LongMemEval ingestion path has the same semantic problem: it calls
`client.delete_user(user_id)` and then `client.add_user(user_id)` inside a cleanup block, while the adapter
can hide delete failure.

## Test coverage gap

The committed streaming utility tests cover:
- Mem0 choosing `delete_all`;
- Zep `prepare_user_after_delete` calling `add_user`.

They do not contain a test that forces the Zep delete operation to fail and verifies that the failure reaches
`delete_user_data()`.

## Research consequence

C33 now spans four distinct empirical integration classes:

1. public score-affecting traces in AMB × Mem0;
2. public score-positive/masked cross-test traces in AMB × Zep;
3. controlled-runtime candidates in Redis × Mem0 and MemArena × Mem0;
4. an independent harness source finding where cleanup acknowledgment itself is unsound in OmniMemEval × Zep.

RoMem DMR-MSC × Zep remains a useful lifecycle-design contrast because it uses per-example users and
provider processing waits, although its committed artifacts still lack independent cleanup receipts.

The V34 RQs and formal-pilot primary endpoints remain unchanged. This finding fits RQ1 and RQ3 and does not
justify post-hoc protocol changes.

Formal Pilot remains protocol-frozen and not yet executed on credentialed runtimes.
