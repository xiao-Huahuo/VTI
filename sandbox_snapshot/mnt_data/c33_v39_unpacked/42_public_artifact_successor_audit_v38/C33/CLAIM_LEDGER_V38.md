# Claim Ledger V38

## Authorized

C1. Real agent-memory benchmark integrations can expose behaviorally active state outside their intended trial lifecycle.
C2. Public AMB traces exhibit score-negative, score-positive, score-masked, and score-neutral hidden-state effects.
C3. Lifecycle topology changes exposure; verified cleanup and disposable namespaces are distinct defensive designs.
C4. OmniMemEval contains a source-level false-clean acknowledgment path for Zep deletion.
C5. Microsoft Memora contains a source-level partial-state promotion path in its documented skip-existing retry workflow.
C6. LightMem MemZero contains a source-level partial-state promotion path because persistent backend state can satisfy its load/resume predicate after incomplete construction.
C7. The direct documented Memora force-rebuild and LightMem rerun paths do not independently establish fresh persistent state before construction.
C8. IronCurtain provides a source-level negative control with disposable per-question DB state and completion publication after question completion.
C9. LightMem's pinned official README exposes a public Google Drive described as containing model outputs, evaluation logs, and predictions; file-level audit of the MemZero LongMemEval artifacts remains pending.
C10. MemBase, linked by LightMem as its more comprehensive baseline evaluation framework, requires a `config.json` completion marker plus at least one Qdrant memory before ordinary Mem0 resume skips a trajectory.
C11. In MemBase Mem0, a hard interruption before `save_memory()` avoids immediate skip but partial Qdrant state is reopened and reused during reconstruction because no pre-replay reset is executed.
C12. MemBase Mem0 catches provider add exceptions inside `add_message()`. If some writes succeed and construction reaches `save_memory()`, the resulting `config.json` plus any Qdrant memory can satisfy a later ordinary skip despite failed per-message additions.
C13. MemBase documents `--rerun` as rebuilding from scratch, while the audited Mem0 construction path bypasses the load guard without deleting the deterministic on-disk Qdrant collection or history DB; Mem0 cleanup closes the client only.
C14. The official MemTraceBench generation example introduced on 2026-06-03 invokes MemBase construction with `--rerun --tracing`, uses a stable Mem0 save directory, and performs no deletion in the construction script; the public MemTraceBench release contains 19 Mem0 execution graphs with 66 failure annotations, including 12 enumerated LongMemEval Mem0 graph files.

## Blocked

B1. Memora live partial-state retrieval/score effect.
B2. LightMem live partial-state retrieval/score effect.
B3. File-level audit of LightMem's public Drive for MemZero × LongMemEval logs, retrievals, and evaluations.
B4. MemBase provider-level interruption / swallowed-add replay effect.
B5. Whether released MemTraceBench Mem0 graphs were generated with pre-existing persistent state or experienced any lifecycle-contamination path.
B6. Redis controlled E2/E3/E4.
B7. MemArena controlled E2/E3/E4.
B8. Field prevalence.

## Prohibited

P1. Generic reset/checkpoint hygiene as conceptual novelty.
P2. Calling source-level risk a confirmed published-score defect.
P3. Treating a public artifact locator as evidence that a specific run exercised the failure path.
P4. Treating source-level MemBase findings as provider-runtime evidence.
P5. Claiming all resume-capable memory benchmarks are vulnerable.
P6. Claiming MemBase regressed relative to LightMem overall; V38 establishes a mixed lifecycle change, including a stricter completion-marker gate and persistent-state reuse paths.
P7. Treating the presence of `--rerun` in the MemTraceBench reproduction script as proof that the released dataset was contaminated; clean starting directories remain compatible with the observed scripts.
