# Known gaps

## Missing historical MemArena scripts

Historical V27/V28 handoffs reference the following files, but no copies were
found in the migration snapshot or nested research archives:

- `memarena_sidecar_gate_h0_v27.py`
- `memarena_sidecar_paired_replay_v27.py`
- `memarena_sidecar_inspector_v27.py`

The MemArena protocol description, repository commit, provider version and design
rationale remain available, but its executable package is incomplete. Any future
MemArena run must reconstruct and re-audit the runner before execution.

## DeepSeek causal identification

DeepSeek thinking-mode and non-thinking temperature-zero runs both show large
clean-clean divergence under identical prompt hashes. Single-run exact-hash
outcomes cannot identify lifecycle-caused E2/E3 on this stack.

## V44 timestamp metadata

V44 was launched as a direct diagnostic probe rather than through the formal
orchestrator. The result and file hash are preserved, but start/finish timestamps
were not recorded. This is disclosed in `history/v44/results/V44_RUN_RECORD.json`.

## Formal experiment

No full formal experiment has started. Only pilot and diagnostic runs are
available. No paper claim should imply population prevalence or an official
GPT-4o E4 score effect.

## V45 local runtime

The deterministic local gate passed preflight with the pinned model digest and
advanced through Stage A, but Ollama aborted a Stage B extraction due to a
token repeat limit. No structured causal result was produced. See
`history/v45/results/V45_EXECUTION_INCIDENT.json`.

V46 re-froze the local configuration with `repeat_penalty=1.1` and verified
per-session interruption recovery. It stopped in Stage A because the model
returned a string where Mem0 expected a memory object. The 12 completed
clean_a sessions remain checkpointed; no clean-clean or causal decision exists.
Neither E2/E3 nor E4 is established.

V47 added prospective JSON Schema enforcement and ran from an independent
clean start with validated per-session checkpoints. It completed the one-case
clean-clean and native-versus-clean gate, supporting E2 and answer-text E3 for
that exact local stack. The official score endpoint E4, replication across
cases/integrations, and prevalence remain open. Both observed answer variants
failed to state the reference total of eight days.

V48 completed its matched three-arm extension on frozen cohort ranks 2–4.
All three calibrated local pairs showed E2 and answer-text E3 differences,
but the official E4 judge is resource-blocked by exhausted GPT-4o API credits.
The local project no longer configures `OPENAI_API_KEY`.
No official score-effect or prevalence claim is authorized. A second real
benchmark/provider integration remains unreplicated.

## V49 supplemental E4 interpretation

V49 scored the saved V48 ranks 2–4 without OpenAI API. Its post-answer-generation
hybrid endpoint found one native-better pair and two both-wrong pairs. This is
one selected local-stack correctness difference, not a population estimate.
The direct count rule was chosen after the answers existed, and only the Borges
pair received DeepSeek judgments. The six DeepSeek votes agreed, but agreement
does not establish judge validity. `deepseek-flash` is a provider alias; the
six receipts show the same returned model ID, not immutable weights. The
original GPT-4o LongMemEval endpoint remains unmeasured.

## Historical directory relocation

V42–V54b live under `history/`. Frozen code, manifests and raw receipts were
left byte-for-byte unchanged. Some historical runners and `history/ops/` helpers
still assume the former root-level `vNN/` paths; they are archival tools and
must not be executed in place without restoring or independently updating
their path assumptions. The relocation does not affect the recorded results;
see `history/RELOCATION_MANIFEST.json`.

## MemArena second-integration status

V50 reproduced the pinned MemArena × Mem0 2.0.11 E1 reset-contract chain with
synthetic messages and instrumented inference/embeddings. V51 passed one real
LongMemEval session through the same adapter and pinned Mem0 source with local
Qwen schema-constrained extraction. Neither is a clean-clean calibrated
downstream replay. At that stage, independent MemArena E2/E3/E4 effects, natural published-run
contamination, and cross-integration outcome replication remained open.

V52 attempted the first one-case downstream paired pilot. Both verified-clean
arms completed, but identical first prompt and request produced different raw
Qwen extractions. Final memory and Top-5 retrieval also diverged. The frozen
null-control gate failed and the native arm did not run. This is a P0 obstacle
to attributing any MemArena downstream difference to reset state under the
current local model configuration. V50's instrumented E1 path is unaffected;
it cannot be promoted to an E2/E3 outcome claim.

## V53–V54b current boundary

V53 found exact three-repeat output under GPU cold loading for one preserved V52 request. The original V54 stopped at session 1 because its ordered SQLite message-hash comparison was sensitive to insertion timestamp order, although the message-content multiset was equal. Its stop is preserved. A newly frozen V54b run compared content multisets from the start, passed eight clean-clean sessions plus final retrieval and answer calibration, and observed a one-case E1/E2 difference after native reset. The final answer text was identical. This is cross-integration E2 feasibility under one local backend and selected case; MemArena E3/E4, population prevalence, alternative model robustness, and natural benchmark contamination remain open. See `history/v54b_memarena/runs/v54b-pilot-20260925-01/AUDIT.json` and `CURRENT_HANDOFF.md`.

V54b completed without interruption. Before execution, checkpoint content validation and a synthetic tamper check were exercised, but an actual process-stop/resume drill was not performed. This is a reproducibility-procedure gap under the project norm, even though the 27 completed branch checkpoints passed post-run tree-hash verification. A future multi-case run must pass a real interruption/resume drill before full execution.

## V55 final evidence boundaries

The original V55 proposal's ranks 5–12 had already been executed in V42; before any V55 outcome the primary cohort was corrected to held-out ranks 13–24 with the unchanged SHA256 ordering. Both source proposal and correction remain preserved.

V55 completed all 12 selected cases, but only 10 had calibrated, quality-passing native outcomes. Rank 14 passed Stage A then suffered an Ollama disconnect during native session 12; Mem0 wrapped the generation exception beyond the frozen runner's narrow catcher. The case was explicitly adjudicated invalid after independent readback, with no retry or replacement; E2/E3 are missing. Rank 16 failed exact clean-clean answer-text calibration despite matching prompt, memory and retrieval; native was not started. Neither case is an E2/E3 null. Rank 14's manual execution repair must remain visible in paper methods.

The 10/10 E2 result is conditional on Stage A validity and completed E1-positive native outcomes, from one Redis × Mem0 local stack and a fixed SHA256-ranked cohort. It does not estimate population prevalence or show natural contamination of a published leaderboard. MemArena evidence remains one selected E2 pilot; no independent memory backend has yet supplied comparable formal causal evidence.

Supplemental E4 used six E3-positive pairs and the mutable `deepseek-flash` alias. All 36 votes were unanimous and receipts audited, but this is not the official GPT-4o LongMemEval score or an immutable-model judge. Native-better and clean-better each occurred once; there is no established directional score advantage. Post-run reading found rank 13's reference-accepted clean numerical answer accompanied internally inconsistent dates, so the judge verdict should not be treated as a substitute for answer-quality analysis. The original official E4 endpoint remains unmeasured.

## V56 independent-backend gate status

The supplied V56 ZIP passed CRC, but its SHA-256 manifest claims the empty-file digest for `MANIFEST.sha256` itself; seven other listed files match. The original package is preserved and this self-hash defect is disclosed in `history/v56_cross_backend/PACKAGE_INTEGRITY.json`.

The stock Redis LangMem adapter hard-codes OpenAI in extraction and embeddings, while the inherited benchmark answer path also calls OpenAI. The disclosed LangMem-Local adapter uses pinned local ChatOllama, FastEmbed and local answer generation while inheriting the stock `ingest`, `reset` and `list_memories` methods. This is a distinct local configuration, not a result for the unmodified public LangMem adapter. LangMem also places random UUIDs in its session wrapper; raw requests must be retained and exact null calibration must be checked on actual target endpoints.

V56 Stage 0 passed one synthetic ingest/reset/ingest/query conformance sequence (14/14 readback). It does not establish behavioral predecessor invariance or cross-backend E1/E2/E3 on LongMemEval. The four target cases were selected prospectively. The Stage 1/2 protocol and code are frozen, the identity preflight passed 9/9, and the SIGTERM checkpoint/resume drill passed. Rank 25 clean-clean calibration has started; no V56 independent-backend causal outcome is available yet.

## V56 terminal null-control limitation

The first prespecified LangMem-Local target completed clean_ref and clean_rep but failed exact clean-clean equality and the 5-memory/retrieval quality floor (1 versus 3). Random first-session memory IDs entered the second manager input; the final memory and retrieval sets had zero overlap. Frozen first-null stopping halted the gate at 1/4 targets, before predecessor/native execution. No LangMem isolation result, backend-wide rate, or cross-backend generality follows. See `history/v56_cross_backend/V56_DECISION_SUMMARY.md` and 439/439 independent audit. A new prospective stochastic-null or backend-compatibility protocol is needed; the existing run must remain immutable.
