# V35 Handoff

Canonical project: AM-AUTO-20260918-R1

Primary candidate: C33

Working title: **Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit**

Status: `FORMAL_PILOT_READY_V35_C33_INDEPENDENT_HARNESS_FALSE_CLEAN_ACK_SOURCE_FOUND`

## V35 new finding

Independent harness: `MemTensor/OmniMemEval@0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d`

Source chain:

1. `scripts/client_factory/zep_client.py::delete_user()` wraps the HTTP delete in
   `suppress(Exception)` and does not inspect the response status.
2. `scripts/utils/streaming.py::delete_user_data()` calls `delete_user()` and immediately returns
   `(True, None)` if no exception escapes.
3. The harness may therefore record delete status `ok` after an unsuccessful provider deletion.
4. `prepare_user_after_delete()` calls `add_user(user_id)`.
5. `ZepClient.add_user()` treats 409 as success.
6. A stale user that survived the failed delete can therefore be silently reused.

A deterministic source-grounded fixture reproduces the false-success control flow. It is implementation
evidence only, classified E0, because no live provider state was observed.

## Affected shared streaming families

- LongMemEval
- BEAM
- PersonaMem v2
- HaluMem

The same cleanup helper is shared across these paths.

## RQ/protocol discipline

Do not change V34 RQ1-RQ3 or the Redis/MemArena pilot sampling after seeing this source result.
Add OmniMemEval × Zep as an external source-positive audit target, not as a substitute for the two frozen
controlled replications.

## Next work without user intervention

1. Audit OmniMemEval public artifacts for any deletion/status receipts that can retrospectively test this path.
2. Search one more independent memory benchmark family for a lifecycle-safe negative control or a public
   source/trace positive.
3. Keep Redis and MemArena exact-runtime packages frozen.
4. Avoid claiming that OmniMemEval published scores are affected until a real trace or paired reproduction
   exists.
