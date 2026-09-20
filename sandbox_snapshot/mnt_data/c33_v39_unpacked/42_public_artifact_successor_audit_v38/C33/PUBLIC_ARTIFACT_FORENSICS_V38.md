# Public Artifact Forensics V38

## Scope

This audit follows the V37 request to locate raw runtime artifacts or exact published-run outputs for Microsoft Memora and LightMem without modifying the frozen V34 controlled pilot.

## Microsoft Memora

Pinned commit: `dec3f8f2444eace7004fc084abe1be9f3d88270e`.

Audited public surfaces:

- repository tree;
- LongMemEval runner scripts;
- GitHub release collection;
- workflow runs associated with the pinned commit;
- code search for documented output directory and score filenames;
- issue search for skip-existing / force-rebuild LongMemEval paths.

Observed result: the public repository exposes executable output contracts, retry flags, aggregation scripts, and documented commands. No committed LongMemEval output directory, score artifact, release asset, or pinned-commit workflow artifact was located on these surfaces.

Status: `RAW_RUNTIME_ARTIFACT_NOT_LOCATED_ON_AUDITED_GITHUB_SURFACES`.

This status is narrower than "no public artifact exists".

## LightMem

Pinned commit: `8449d574df6bae1bdf3314a1564da65e2f37e046`.

The root README at this commit states that experimental results are shared on Google Drive and include model outputs, evaluation logs, and predictions. Folder:

`https://drive.google.com/drive/folders/1n1YCqq0aDeWiPILhkq-uS3sU3FDmslz9?usp=drive_link`

The public folder resolves as `lightmem_experiments`. The current research runtime reaches the folder landing page but does not expose its file listing. Direct GitHub searches for expected MemZero LongMemEval output patterns found no checked-in mirror.

Status: `PUBLIC_ARTIFACT_LOCATOR_CONFIRMED_FILE_LEVEL_AUDIT_PENDING`.

## Search terms frozen in V38

- `MemZero_gpt-4o-mini_LongMemEval_10_0_500.json`
- `MemZero_gpt-4o-mini_LongMemEval`
- `MemZero` + `_evaluation.json` + `LongMemEval`
- `token_cost` + `MemZero` + `LongMemEval`
- Memora `longmemeval_outputs`
- Memora `memora-default`
- Memora `memora_semantic_scores.json`

The absence of an indexed filename match is not used as evidence about the Drive contents.


## MemTraceBench

A second public artifact route is now identified through the LightMem-to-MemBase lineage. `zjunlp/MemTraceBench` is a 6.39 GB public execution-graph dataset produced with MemBase/smartcomment instrumentation. Its dataset card reports 19 Mem0 execution graphs and 66 failure annotations. The repository file inventory exposes 12 Mem0 LongMemEval graph files:

- `longmemeval_longmemeval-0a995998.json`
- `longmemeval_longmemeval-2ce6a0f2.json`
- `longmemeval_longmemeval-46a3abf7.json`
- `longmemeval_longmemeval-6e984302.json`
- `longmemeval_longmemeval-70b3e69b.json`
- `longmemeval_longmemeval-9ee3ecd6.json`
- `longmemeval_longmemeval-affe2881.json`
- `longmemeval_longmemeval-c9f37c46.json`
- `longmemeval_longmemeval-e8a79c70.json`
- `longmemeval_longmemeval-e982271f.json`
- `longmemeval_longmemeval-f8c5f88b.json`
- `longmemeval_longmemeval-gpt4_d31cdae3.json`

The current web interface exposes the inventory and dataset-level metadata but does not stream the Xet-backed JSON bodies into this runtime. These files are therefore a concrete next source for provider-level observational evidence, rather than a completed V38 inspection.
