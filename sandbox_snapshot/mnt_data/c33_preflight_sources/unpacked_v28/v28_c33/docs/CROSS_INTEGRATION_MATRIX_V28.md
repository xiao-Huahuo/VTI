# Cross-Integration Reset Matrix V28

| Integration | Behaviorally active sidecar | Native reset | Natural exposure | V28 classification |
|---|---|---|---|---|
| MemArena × Mem0 OSS 2.0.11 | SQLite scoped `messages` read by extraction | `delete_all(user_id)` | repeated run; Day-3 n=15 separate-Qdrant replay | positive source-proved |
| Redis Agent Memory Benchmark × Mem0 OSS 2.0.19 | SQLite scoped `messages` read by extraction | `delete_all(user_id)` | mid-ingest retry; incomplete-run resume | positive source-proved |
| ForgetEval × Mem0 | same storage may exist, but benchmark writes `infer=False` | `delete_all` | sidecar not read by tested write path | negative mechanism control |
| Basic Memory × Mem0 published matrix | `infer=false` in published results | cleanup `delete_all(user_id)` | random run IDs; group-specific suffixes | negative/default-design control |
| MemArena × Graphiti | graph store | first reset deletes local DB directory and rebuilds | ordinary fresh run | no comparable mismatch established |
| MemArena × Letta | shared agent/passages | first reset deletes/recreates shared agent | ordinary fresh run | no comparable mismatch established |
| MCP Memory Service × Mem0 cloud | server-side provider state | cloud `delete_all(user_id)` | per-item stable cloud user | SQLite sidecar mechanism not applicable; excluded |

## Interpretation

The matrix supports a methodology claim only after runtime reproduction. It already shows why a useful audit must reason about state surfaces and execution lifecycle together: the same `delete_all` call can be harmless under an `infer=False` or unique-scope design and invalid under retry/replay with a behaviorally active message sidecar.
