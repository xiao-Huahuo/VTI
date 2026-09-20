# Exact Runtime Package V32

This package is prepared now so the real gate can be executed later without redesign.

## Files

- `code/preflight_redis_exact_v32.py`: rejects wrong Python, commit, Mem0 version, missing Qdrant/OpenAI dependencies, or missing OpenAI key.
- `code/redis_exact_paired_probe_v32.py`: corrected exact-stack paired replay carried forward from V31.
- `code/validate_redis_result_v32.py`: maps the raw result to the conservative E0–E4 claim ladder.
- `code/run_redis_exact_v32.sh`: one-command wrapper that runs preflight, paired replay, claim validation, and output hashing.

## Frozen setup

The benchmark checkout must be exactly:

`redis/agent-memory-server@94192c39e2a4a154f441a5411e3d73c4f54974a6`

From its `agent-memory-benchmark/` directory, the intended dependency installation is:

`uv sync --locked --extra mem0 --group dev`

The frozen project declares Python `>=3.10,<3.13`. The V32 current ChatGPT container is Python 3.13 and lacks Mem0/Qdrant and an OpenAI credential, so it is deliberately rejected by preflight rather than silently approximated.

## State branching invariant

The two paired arms must clone the complete failed-attempt local state after all handles are closed:

- Qdrant directory;
- `history.db`;
- any other files under the isolated Mem0 root.

`invoke_only` executes the benchmark-native scoped reset. `verified_clean` executes the same native reset and then removes the scoped message sidecar before re-opening the store. Both arms attest vector state independently through Mem0 logical enumeration and exact Qdrant backend count plus paginated enumeration.

## Release rule

Do not scale to many LongMemEval cases unless the first exact case reaches E2 or stronger. A prompt-only E1 result remains scientifically useful for mechanism confirmation but does not justify expensive score experiments.
