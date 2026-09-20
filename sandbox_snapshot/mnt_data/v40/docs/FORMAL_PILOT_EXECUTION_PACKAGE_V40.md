# V40 Redis Formal Pilot Execution Package

This package converts the frozen V34 Redis protocol into an executable, fail-closed 12-case run. It does not change V34 sample size, selection rule, fault point, evidence hierarchy, bootstrap plan or primary endpoint.

## Frozen stack

Benchmark: `redis/agent-memory-server@94192c39e2a4a154f441a5411e3d73c4f54974a6`

Provider: `mem0ai==2.0.19`, source tag commit `dc82354e143c2581d505d581a00286d6ef8c3605`

Dataset: LongMemEval cleaned Small, 500 questions, pinned by revision and SHA-256 in `redis_v34_cohort.json`

Python: 3.10, 3.11 or 3.12

Fault injection: fail immediately before the fourth session-level `Memory.add`, after three successful adds

Paired arms: complete failed-attempt local state is cloned. `invoke_only` runs benchmark-native `delete_all(user_id=...)`. `verified_clean` runs the same native reset and then clears the scoped behaviorally active message sidecar before reopening the provider.

Primary endpoint: E2 or higher, meaning memory representation or retrieval diverges between paired arms. E3 answer divergence and E4 judge-score divergence are retained as later levels, not substituted for E2.

## Fail-closed execution

`fetch_frozen_longmemeval_v40.py` downloads the exact dataset revision and rejects a SHA mismatch.

`preflight_redis_v34_v40.py` verifies the benchmark commit, Python range, Mem0 version, Qdrant/OpenAI dependencies, credential presence, dataset hash, 500-row population, eligibility count, deterministic cohort and fault-point validity.

`redis_v34_exact_paired_probe_v40.py` executes one frozen question and persists hashes, counts, reset receipts, prompt-consumption receipts and answer/judge results without persisting raw LongMemEval text or raw Mem0 extraction prompts.

`run_redis_v34_pilot_v40.py` runs all 12 cases and retains per-case stdout/stderr hashes and byte counts plus error receipts. Temporary Qdrant/history work state is deleted after each case because it can contain raw benchmark text; the scientific receipts remain in the result JSON. An infrastructure failure makes the pilot incomplete rather than silently shrinking n.

`validate_redis_v34_pilot_v40.py` maps every executed case onto E0 to E4, reports the E2+ count, uses the frozen 5000-resample bootstrap with seed 20260919, and computes exact paired McNemar statistics when binary judge pairs exist.

## One-command run

From a Python 3.10 to 3.12 environment with the exact Redis checkout:

```bash
cd agent-memory-benchmark
uv sync --locked --extra mem0 --group dev
export OPENAI_API_KEY='...'
cd /path/to/v40/package
./code/run_redis_v34_v40.sh /path/to/agent-memory-server /path/to/isolated/output
```

The output directory is a new experiment unit. Reusing a directory requires the explicit `--resume` behavior inside the runner and preserves already completed case receipts.

## Model alias limitation

The exact Mem0 2.0.19 default extraction path resolves to the provider configuration expected by the frozen source and is runtime-checked as `gpt-5-mini`; the Redis answering and judge defaults used by this package are `gpt-4o`. These are model aliases rather than dated snapshots. V40 preserves the exact historical benchmark/provider behavior instead of silently overriding Mem0 defaults. A later large experiment should version model snapshots or record provider-returned model identities where supported. This limitation is recorded before seeing pilot results and does not alter the V34 pilot.

## Interpretation

One or more E2+ cases unlock the empirical downstream-effect claim for the executed Redis cohort. A Redis null across all 12 remains informative and moves the independent MemArena paired pilot to the decisive next gate. Either result is retained.
