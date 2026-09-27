# Current handoff — C33 V57 design

Date: 2026-09-27 (Asia/Shanghai) | Project: `AM-AUTO-20260918-R1` | State: **V57 design draft; no V57 model runs**

## Current research gate

The active work is `v57_design/`: a matched full-predecessor randomized comparison of native reset versus pristine-shadow memory state, proposed for LangMem-Local and Graphiti-Local. Its protocol is **not frozen**. The 14B model is not installed; ranks 26–28 have not been run. The next engineering requirement is a real isolated Neo4j instance and Graphiti reset/teardown proof, followed by the 14B runtime identity, per-unit no-interference drill and frozen assignment schedule. See `v57_design/PROTOCOL_DRAFT.json` and `docs/V57_MATCHED_PREDECESSOR_REVIEW_20260927.md`.

Completed offline checks: development count scorer 46/46 synthetic vectors; ordered retrieval footprint 8/8; partial-conjunction statistic 9/9 including 10,000 synthetic null datasets. Graphiti constructor 6/6 and toy local BGE/reranker 7/7 used no LLM or database calls. These checks do not establish a V57 causal outcome.

## Historical evidence and archive

V55 Redis×Mem0 held-out formal run finished 12/12 selected cases: 11 Stage-A valid, 10 E2 evaluable and 10/10 E2 positive, with 6/10 answer-text E3 positive. Supplemental DeepSeek E4 had no common correctness direction. The full V55 run is in `history/v55_formal/`, with relocation manifests under `history/`.

V56 LangMem-Local stopped at its first clean-clean null divergence: rank 25's independent 51-session clean trajectories had final memory/retrieval counts 1 versus 3, both below the frozen floor of 5. No predecessor or native arm ran. Its terminal result remains `UNVERIFIABLE_NULL_DIVERGENCE`, independently audited 439/439. The complete version is now physically in `history/v56_cross_backend/`, unmodified, with exact relocation evidence in `history/V56_AND_LEGACY_RELOCATION_AUDIT_20260927.json`. The old V56 dashboard is stopped. Frozen V56 scripts contain original root-path assumptions; see `history/V56_REHYDRATION.md` before historical replay. No V56 causal claim was created by archival.

Legacy MemArena/Mem0 vendored source, V50/V56 Python environments, old root diagnostics and the V56 web-GPT statement were moved into `history/` and hashed before/after. The active root retains only the pinned Redis benchmark source under `third_party/`, the BGE cache and V57 environments under `.runtime/`, current docs and V57 design code.

## Literature and claim boundary

`IDEA.md` preserves the user's original idea with a dated literature addendum. The active claim-to-source map is `docs/literature/RELATED_WORK_CURRENT.md`; `docs/literature/references.bib` contains 20 starter entries and a 10/10 metadata/structure audit. It is not yet a submission-ready bibliography. V55 supports within-stack measurement distortion, not backend prevalence or a directional correctness decline. V56 contributes no independent-backend isolation result. V57 statistics and Graphiti toy engineering checks are preliminary only.

Current Python environments are described in `v57_design/environment/README.md`; both are engineering-only uv/CPython 3.12.14 environments, separate from the archived V50/V55/V56 venvs.

Portable GPU-server engineering preparation: `.gitignore` excludes history, environments, vendored checkouts, exports and downloadable weights/datasets; `v57_design/DOWNLOADABLE_ASSETS.json` pins the public source/data/BGE snapshot; `ops/bootstrap_gpu_server.py` recreates only engineering dependencies and verifies hashes. `SERVER_README.md` gives server commands. Source-only main is pushed to `git@github.com:xiao-Huahuo/VTI.git` and the remote commit was checked; V57 formal runtime is still unfrozen.
