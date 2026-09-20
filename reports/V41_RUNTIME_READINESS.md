# V41 macOS runtime readiness

Date: 2026-09-20

Project: `AM-AUTO-20260918-R1`

## Completed

- Initialized the project Git repository and committed the V40 migration baseline.
- Protected and ignored the local `.env` secret file.
- Checked out `redis/agent-memory-server` at exact commit
  `94192c39e2a4a154f441a5411e3d73c4f54974a6`.
- Created the benchmark environment with Python 3.12.14 via `uv sync --locked
  --extra mem0 --group dev --python 3.12`.
- Verified `mem0ai==2.0.19`, `qdrant-client==1.19.0`, `openai==2.54.0`, and
  `pytest==9.1.1`.
- Re-ran the four V40 offline tests and five inherited V32 control-flow tests:
  9 passed.
- Downloaded the pinned LongMemEval-S dataset and verified its frozen SHA-256.
- Passed every V40 exact-runtime preflight check, including deterministic
  re-derivation of the frozen 12-case cohort.
- Confirmed authenticated access to the OpenAI model listing and visibility of
  both `gpt-5-mini` and `gpt-4o`.

## Packaging defect found

The migrated V40 legacy test is named
`test_redis_retry_controlflow_fixture_v32_reference.py`, but imports the sibling
filename `redis_retry_controlflow_fixture_v32.py`. The migrated fixture actually
has the `_reference.py` suffix. The frozen package was left unchanged. The test
was re-run in a temporary directory using the expected original fixture name and
all five cases passed.

## Current external blocker

A synthetic, non-benchmark smoke test reached the OpenAI embeddings endpoint but
received `429 insufficient_quota` with code `credit_balance_exhausted`. No formal
cohort case was executed and no pilot result was observed.

Formal Redis execution can begin immediately after API credits are available.
Use `ops/run_redis_v34_v40_macos.sh`; it loads the ignored `.env`, applies the
local proxy settings, activates the exact benchmark virtual environment, and
runs the frozen V40 fail-closed pipeline into a new timestamped output directory.
