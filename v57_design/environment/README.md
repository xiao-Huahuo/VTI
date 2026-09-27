# Current V57 Python environments

The workspace uses **uv-managed CPython 3.12.14**. There is no shared project-wide `venv` and no V57 formal runtime freeze yet.

| Environment | Purpose | Current key packages |
| --- | --- | --- |
| `.runtime/v57-stat-venv` | count scorer, retrieval-footprint arrays and exact randomization code | NumPy 2.5.3 only |
| `.runtime/v57-graphiti-venv` | Graphiti-Local constructor and toy component engineering | graphiti-core 0.30.2, neo4j 6.3.1, fastembed 0.8.0, NumPy 2.5.3, their resolved dependencies |

Exact installed package lists and their SHA-256 hashes are in `stat-pip-freeze-20260927.txt`, `graphiti-pip-freeze-20260927.txt` and `V57_ENV_SNAPSHOT.json`. The shared BGE model files live at `.runtime/fastembed-cache`; the active `v57_design/DOWNLOADABLE_ASSETS.json` pins the Hugging Face revision and five-file snapshot hash for a fresh server download.

For a Linux server, use the small direct-dependency inputs `requirements-stat.txt` and `requirements-graphiti.txt` through `ops/bootstrap_gpu_server.py`. The two pip-freeze files document the **Mac** engineering environments; they are not a cross-platform lock. The server must save and review its own resolved package list before formal V57 inference.

Use each environment's explicit interpreter, for example:

```bash
.runtime/v57-stat-venv/bin/python v57_design/code/test_count_unit_v1.py
env -u OPENAI_API_KEY .runtime/v57-graphiti-venv/bin/python v57_design/code/preflight_graphiti_constructor.py
```

The Graphiti environment contains the `openai` **Python package** because Graphiti's local OpenAI-compatible client uses that SDK. Its audited constructor points to `127.0.0.1`, telemetry is disabled, and no remote OpenAI API or V57 formal LLM call has been made.

Historical V50/V55/V56 virtual environments are preserved under `history/runtime/`; they should not receive package upgrades or serve as the V57 interpreter. Moving a venv can invalidate embedded absolute paths, so treat the archived environments as provenance, and recreate an isolated environment from reviewed requirements when reproducing a past run.

Before any V57 confirmatory run, freeze the actual 14B Ollama digest, Graphiti/Neo4j image and provider source hashes, full resolved dependencies, BGE cache, and per-unit runtime identity. The current pip snapshots are **engineering snapshots**, not a scientific runtime lock or permission to start V57.
