# Redis Trigger Audit V32

Frozen benchmark: `redis/agent-memory-server@94192c39e2a4a154f441a5411e3d73c4f54974a6`

Frozen Mem0: `mem0ai==2.0.19`, upstream commit `dc82354e143c2581d505d581a00286d6ef8c3605`

## Source route

The frozen LongMemEval runner derives each example scope as `benchmark-<run_name>-<index>`. Its retry operation wraps both `store.reset()` and the complete session ingest. Therefore every retry of a partially ingested example reuses the same provider user scope.

The Mem0 adapter performs one inferred `Memory.add` per session. Its reset delegates to `Memory.delete_all(user_id=...)`.

In frozen Mem0 2.0.19, normal inferred add builds a deterministic session scope, reads up to ten rows from the SQLite `messages` sidecar, embeds them in the extraction prompt's `Last k Messages` section, and saves the current messages back to that table. Scoped `delete_all` removes vector memories but does not clear that message table.

## V32 executed control-flow fixture

`redis_retry_controlflow_fixture_v32.py` runs two source-grounded routes without an LLM:

1. **Mid-ingest retry.** Attempt 1 completes one session, then faults. Attempt 2 begins after the benchmark-style native reset. Vector state is empty, while three message rows remain. The first add of attempt 2 reads those three rows as Last-k context.
2. **Crash/resume.** A process completes one session and exits before writing an answer record. Re-running the same `run_name` and example index derives the same user id. The resumed native reset clears vector state while two message rows remain; the first resumed add consumes those rows. The verified-clean control consumes zero rows.

All five offline fixture tests pass.

## Interpretation

This upgrades the Redis route from a single hand-constructed sidecar example to executed coverage of both benchmark lifecycle paths that reuse the same scope. It remains E1 evidence because the fixture substitutes deterministic state for the real Mem0 extraction model and vector backend.

The exact-stack V32 probe is frozen separately. It must run in Python 3.10–3.12 with the exact benchmark checkout, `mem0ai==2.0.19`, Qdrant client dependencies, LongMemEval access/cache, and an OpenAI key. It records representation, retrieval, answer, and optional official judge effects separately.
