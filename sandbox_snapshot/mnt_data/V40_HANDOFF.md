# V40 Handoff

Project: `AM-AUTO-20260918-R1`

Candidate: `C33`

Status: `FORMAL_PILOT_EXECUTION_BLOCKED_V40_C33_REDIS_COHORT_FROZEN_RUNTIME_PACKAGE_READY`

## What is finished

V39 is preserved in persistent Library as a complete research bundle. V40 completes every provider-free step needed to execute the frozen V34 Redis pilot.

The exact n=12 Redis cohort is frozen in `redis_v34_cohort.json`. Selection uses only the predeclared question ID hash rule and session-count eligibility. The formal preflight re-derives the cohort from the pinned upstream LongMemEval-S file and checks its SHA-256 before any provider call.

The V40 execution package contains dataset fetch, fail-closed preflight, exact paired replay, 12-case orchestration, E0-E4 aggregation, frozen bootstrap analysis, runtime tree hashing, offline tests and reference copies of the V32 mechanism fixtures.

## Frozen next execution

Use a clean Python 3.10-3.12 environment and checkout:

`redis/agent-memory-server@94192c39e2a4a154f441a5411e3d73c4f54974a6`

From `agent-memory-benchmark/`, install with:

`uv sync --locked --extra mem0 --group dev`

Provide `OPENAI_API_KEY`, then execute `code/run_redis_v34_v40.sh` from this package. The script fetches and verifies the pinned dataset, executes all 12 paired cases, validates the primary E2 endpoint and hashes the runtime outputs.

## Gate after Redis

If one or more Redis cases reach E2+, preserve the result as the first controlled downstream-effect evidence and then execute the already frozen MemArena n=15 paired pilot.

If all 12 Redis cases remain downstream-null, retain the null and proceed to MemArena. A Redis-only null does not close C33.

No large-scale expansion occurs before Redis/MemArena gate review or a versioned protocol amendment.
