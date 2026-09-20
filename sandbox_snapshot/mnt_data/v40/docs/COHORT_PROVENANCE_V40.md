# V40 Redis V34 Cohort Provenance

Project: `AM-AUTO-20260918-R1`

Candidate: `C33`

Protocol authority: `V34`

This document freezes the concrete 12-unit Redis cohort that was previously specified only by a deterministic selection rule.

## Frozen population

The Redis benchmark commit is `redis/agent-memory-server@94192c39e2a4a154f441a5411e3d73c4f54974a6`. Its LongMemEval adapter uses the public cleaned LongMemEval Small file `longmemeval_s_cleaned.json`.

The V40 execution package pins the dataset to revision `98d7416c24c778c2fee6e6f3006e7a073259d48f` and requires SHA-256:

`d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`

The file contains 500 questions. Public independent benchmark artifacts report 38 to 62 haystack sessions per question, so every question satisfies the V34 eligibility condition `session_count >= 4`. Formal execution still recomputes this fact from the pinned upstream JSON before any provider call.

## Selection rule

For each eligible question, compute:

`SHA256("C33-V34-REDIS|" + question_id)`

Sort by hexadecimal digest in ascending order and retain the first 12.

The resulting cohort is fixed in `redis_v34_cohort.json`:

| Rank | question_id | Type | Sessions | Digest prefix |
|---:|---|---|---:|---|
| 1 | b5ef892d | multi-session | 52 | 0002b9d74b5e |
| 2 | 58470ed2 | single-session-assistant | 50 | 0044bef1a40c |
| 3 | 1a8a66a6 | multi-session | 51 | 0089793cbfaf |
| 4 | gpt4_31ff4165 | multi-session | 42 | 0155e8dafbd0 |
| 5 | 2133c1b5 | knowledge-update | 51 | 01afa4f5e431 |
| 6 | 9a707b81 | temporal-reasoning | 54 | 0248f2f1441d |
| 7 | gpt4_731e37d7 | multi-session | 48 | 0283e0b56df1 |
| 8 | gpt4_c27434e8 | temporal-reasoning | 51 | 02aa0a0a1f37 |
| 9 | 2698e78f_abs | knowledge-update | 46 | 02ad5032aee9 |
| 10 | 7401057b | knowledge-update | 47 | 02afc64716f4 |
| 11 | 0862e8bf | single-session-user | 50 | 02e6f9ecb7f3 |
| 12 | gpt4_5438fa52 | temporal-reasoning | 50 | 033209a22840 |

## Provider-free derivation check

Before access to the upstream file was available in the current sandbox, the selection was independently materialized from the public `kargarisaac/lerim` LongMemEval full retrieval artifact at commit `5fed45a55e587d2844e3c408e937ee3e5fd178ba`, blob `df39a0cb06938aee66ed8c7c38cb3b44f4bdea9b`. That artifact contains all 500 question IDs, question types and haystack session counts for the same cleaned-S snapshot.

This mirror is not the execution authority. `preflight_redis_v34_v40.py` derives the cohort again from the frozen upstream JSON and rejects the run if any question ID, type, session count or selection digest differs.

## Leakage control

Selection uses only `question_id` and the predeclared eligibility predicate over session count. Gold answers, answer-session IDs, retrieval outputs, model outputs and scores never enter cohort selection.
