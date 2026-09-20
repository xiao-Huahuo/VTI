# Local cleanup record

Date: 2026-09-20

After V42–V44 structured receipts, analyses and hashes were copied into tracked
version directories and committed, local reproducible runtime material was
removed to reduce the workspace from approximately 1.1 GiB to 281 MiB.

Removed material included:

- `experiment_outputs/` (approximately 823 MiB), including three duplicate
  LongMemEval-S caches and temporary Qdrant/SQLite work state;
- Python `__pycache__` directories;
- pytest caches;
- `.DS_Store` files.

Retained material includes:

- all V42–V44 structured case receipts and analyses;
- all V42–V44 version hashes;
- the exact benchmark checkout and Python environment under ignored
  `third_party/`;
- the original V40 migration snapshot, except removed derived virtual-environment
  and bytecode-cache files;
- the ignored local `.env` credential file.

Deleted raw runtime state is not stored in Git. Formal structured receipts are in
Git, and the public dataset can be downloaded again from its frozen revision.
