# CHANGE HISTORY

## 2026-09-18 / AM-AUTO-20260918-R1

- 初始化 Agent Memory 自动科研批次。
- 建立 2026 年领域拥挤度地图。
- 生成 18 个候选 Idea。
- 14 个候选因直接 prior art 或方法空间过度拥挤进入 Dead Idea Registry。
- C18 保留为 reserve。
- C15、C16、C17 通过当前 Novelty Audit。
- 对三个幸存候选执行 deterministic synthetic feasibility fixtures。
- 执行 proxy noise、verifier shift、environment volatility 等压力测试，记录失败边界。
- 冻结 IDEA_NOVELTY_FREEZE_V1 与 Draft Claim Contracts。
- 当前状态从 IDEA_DISCOVERY 迁移至 PILOT_DESIGN。
- C15 被设为下一阶段 active Idea；C16 进入并行低成本 diagnostic；C17 等待真实维护成本 census。


### Initial Review V1

- 对 C15、C16、C17 重新执行 2026-09-18 截止的新颖性检索和近邻反查。
- C15 新增 Plan Pointers、PlanFence、开源 MemGuard 等直接近邻，创新边界收缩到 unknown-critical-path 的长期 budgeted recertification optimization。
- C15 加入 MemGuard-like 强基线并运行 100-seed synthetic pilot 与 budget/noise sweep，当前进入真实 Pilot 设计。
- C16 确认 generic judge drift 已有直接 prior art，删除该首创表述。
- C16 source-grounded stress pilot 产生负结果：global/mild verifier shift 下 decision-margin 基线优于复杂 drift-aware 策略；仅 structured policy-region shift 下 region-aware 策略显示额外收益。Claim Contract 已据此修订。
- C16 当前进入真实 verifier-drift census，暂缓复杂方法开发。
- C17 新增 Dual-Layer cost-aware write routing、Selective Memory Retention、Agent Memory systems characterization 等近邻，创新边界收缩到 future recurring maintenance externality。
- C17 lifecycle pilot 显示低 volatility 区域 NLV 劣于强 static penalty，高 volatility 后才形成稳定优势。当前暂停方法开发，等待真实 maintenance-cost census。
- 新增 `06_initial_review/` 有序保存 source snapshot、search log、Claim Contract V2、protocol、代码、原始 JSON、结果、Red-Team、novelty refresh、decision log、manifest 与 SHA256。
- 上一版 Research State 已另存为 `RESEARCH_STATE_V1_SNAPSHOT.json`，当前主状态保持 `PILOT_DESIGN`，Initial Review 标记为 COMPLETE。

### Real Evidence Gate V3

- 对 C15 读取并重算 `horizonmonkey` 公开 `paper/episodes.csv` 的 1,020 条 episode，确认简单 target-blind triage 已是强基线，并保留条件、预算、模型异质性统计。
- 发现 BAVAR 已直接覆盖长期 Agent 的 sequential budgeted verification allocation、periodic revalidation、risk/reuse/reliability/budget 与 lifecycle verification cost，C15 按 Kill Contract 进入 Dead Idea Registry。
- C16 使用 DriftJudge 已发表的真实 silent version bump 与 strict-prompt 结果建立真实 verifier-drift census。删除“version binding”首创表述，主问题收缩为 persistent certificate drift 的测量、生命周期翻转和 downstream impact。
- C17 经 Dual-Layer、BAVAR 与 Agent Memory systems profiling 的组合性审查后终止，保留 maintenance cost 作为后续系统评测指标。
- 新建 `07_real_evidence_gate/`，保存公开数据重算、真实 drift 表、Claim Contract V3、Kill Memo、provenance、manifest、checksum、Red-Team 与状态快照。
- 状态从单线 Pilot 设计回滚到 Idea Discovery，同时保留 C16 作为 diagnostic survivor。

### Replacement Screening V4

- 在 Dead Idea Memory 与 V3 prior art 基础上生成替补候选，优先搜索维护策略反馈、共享 trust 语义与 implicit-association routing 等二阶问题。
- C19 `Endogenous Exposure Bias / Memory Value Lock-In` 因 retrieval-policy feedback loop、intervention credit、propensity/OPE 与 causal memory selection 的直接 prior art 被淘汰。
- C22 `Semantic Replica Divergence` 因与 stale-read consistency、Governed Shared Memory 和 PlanFence 缺少足够结构分离而淘汰。
- C20 `Shared Trust Fork` 通过当前新颖性审计。真实 verifier-drift 参数校准的合成压力测试显示 same-threshold / heterogeneous-threshold / wide-policy-gap 三种设置均能产生可稳定测量的 certificate fork；该结果仅用于可实施性，不作为真实 fleet 效果证据。
- C21 `Applicability-Sketch Routing` 通过当前新颖性审计。直接解析 InMind 官方 125 条任务，原始 memory 到 indirect query 的 TF-IDF R@5 为 7.2%；77 条结构化 bridge 任务的 gold-derived bridge oracle R@5 为 85.7%。Oracle 只用于确认问题可分离，正式方法严禁使用 gold bridge。
- 当前正式研究池更新为 `C16 + C20 + C21`。C16 聚焦时间维度的 persistent certificate drift，C20 聚焦异构共享消费者的 trust fork，C21 聚焦 query 出现前的 applicability routing。
- 真实 LLM 方法实验仍处于未启动状态，下一 Gate 为 `REAL_PILOT_C16_C20_C21`。

### Screening V5

- Re-ran C21's query-independent residency diagnostic with the target included in the same unlabeled 241-item corpus used to compute IDF. The signal remained large: top-2 71.2%, top-8 99.2%.
- Suspended C21 method development and promoted the benchmark-validity finding to new C27 rather than rewriting C21 in place.
- Merged C20 Shared Trust Fork into C16 as RQ2 because both share verifier/policy-induced certificate drift as the causal variable.
- Derived conservative published-data lower bounds for C16 score-vector certificate forks from DriftJudge exact-agreement results.
- Killed C23 cross-model procedural transfer, C24 resident-memory privacy exposure, and C26 resident-memory over-application due direct prior art.
- Added C25 multi-user capacity fairness. No direct Agent Memory fairness benchmark was found; strong adjacent multi-tenant cache fairness prior art raises novelty risk.
- Ran a 100-seed MUMBench-scale synthetic fairness fixture to verify metrics and Pareto structure. It is retained as feasibility evidence only.
- Updated active research pool to C16 + C27 + C25.

### Real Pilot V6

- 将基于旧 V4 状态产生的 `09_candidate_extension` 整体移动到 archive，并标记为 `SUPERSEDED_09_candidate_extension_stale_v4`，防止覆盖 V5 主线。
- C16 直接审查 MemGuard 官方论文代码，确认 persistent verifier metadata 进入真实 lifecycle decision：0.35/0.70 label boundary、0.55 injection score gate、0.50 confidence gate，以及 retention、conflict、consolidation、archive 排序。
- C16 因此完成“机制绑定” Gate，但现实 item-level boundary crossing 规模仍未完成，下一步必须在冻结 memory bank 上重放 V1/V2 verifier metadata。
- DriftJudge raw artifact 公开列出并提供 SHA256，但本运行环境无法直接下载 raw `evaluations.jsonl`，该限制被记录为 evidence block，不以均值推断替代 crossing 结果。
- C27 在 WRIT 公开 benchmark 上完成 16 类场景各 1 个的分层复核。Average-IDF top-2 为 31.3%，平均候选池约 9 条；InMind 的 top-2 为 71.2%，候选池 241 条。要求后续使用 random-normalized lift 和 normalized rank 比较，避免小候选池偏差。
- C27 状态升级为 `PARTIAL_CROSS_BENCHMARK_REPLICATION`，下一步完成 WRIT 77 场景全量审计、自然会话 benchmark 负对照和 InMind salience-matched control。
- C25 从 AIM/MUMBench 正文提取 domain aggregate：Coding 49 users/150 interactions，Customer Support 25/218，Education 11/160，Travel 8/144。该结果只证明 domain-level density 异质性。
- GitHub 全局检索与论文关联入口未发现官方 MUMBench per-user raw trace。C25 改为 `BLOCKED_ON_PUBLIC_PER_USER_TRACE`，暂停算法开发，synthetic fairness fixture 继续只作为 metric feasibility。
- 新建 `10_real_pilot_v6/` 保存 C16 mechanism audit、C25 real-trace gate、C27 cross-benchmark audit、原始派生 JSON、search log、manifest、SHA256 和 V6 state。
## Real Pilot V7

- C27 对 InMind release 执行格式审计，确认 240/240 background user messages带 `---TIMESTAMP:`，125/125 target messages缺少该标记。format-only selector因此达到125/125 Top-1。
- 重新冻结可执行 Average-IDF定义。raw release Top-2为65.6%；移除 timestamp marker后Top-2降至14.4%，median rank由2变为21；为target补齐同类timestamp后Top-8为0。V5的44.0% / 71.2%历史结果因缺少selector代码改为 `STALE_FOR_MAIN_CLAIM`。
- 完成WRIT 77场景全量审计。76个单一provenance场景进入评分。Average-IDF Top-2为15.8%，低于随机期望21.3%；Length Top-2为44.7%，随机期望21.3%，lift约2.10。V6的小样本IDF解释被推翻。
- 完成LongMemEval 60题分层自然会话pilot。总体Length Top-2为16.7%，随机至少命中gold的期望6.7%，lift约2.48；signal具有显著question-type异质性。
- Novelty refresh纳入2026-09-16发布的Bad Genius / CHASE。C27删除通用benchmark shortcut与counterfactual audit首创叙事，范围收缩为Agent Memory特定的pre-query identifiability与dual-axis evaluation。
- C27进入 `BEHAVIORAL_VALIDITY_GATE`，下一步要求end-to-end shortcut replay与content-salience matched control。
- C16定位DriftJudge Hugging Face frozen raw artifact，确认item-level paired snapshot score vector存在。由于其rubric量表与MemGuard verifier gate不同，完整boundary crossing仍保持未验证。
- C25再次检索MUMBench公开raw trace，仍停留在论文与aggregate层，状态保持blocked。

### Behavioral Gate V8

- 对 InMind 官方 public release 完成 turn-level serialization census：486/486 background turns 含 literal `---TIMESTAMP:`，125 个 task 的 target user/assistant pair 共 250 条 target turns 均缺失该 marker。
- 将该 release invariant 与官方 `judge_target_recall.txt` 和 evaluation context contract 绑定。query-independent format selector 可以在 125/125 tasks 中识别 target pair，并把 target personal fact送入 indirect-query context，构造 100% Target Recall success。
- 该 shortcut 不读取 future query、`explanation`、structured bridge 或 provenance，因此 Target Recall 的成功来自 release serialization signature，而非 implicit-association routing。
- 论文报告 target-visible In-context Control Application 84.0% 与 Always-in-state 68.8%。V8 将两者记录为 target visibility 的 external conditional evidence；format selector 的直接 matched GPT-5-mini Application score继续标记为 `UNVERIFIED`。
- 审查 InMind GitHub 完整 tree，当前公开仓库没有 paper-aligned aggregate/per-task baseline outputs，README roadmap仍将 baseline adapters 和 paper-aligned results列为后续发布项。
- C27 状态更新为 `TARGET_RECALL_PROTOCOL_SHORTCUT_CONFIRMED_APPLICATION_REPLAY_PENDING`，下一 Gate 为 content-salience matching 与 matched Application replay。
- 新建 `12_behavioral_gate_v8/`，保存 shortcut proof、Behavioral Gate、Claim Ledger、search log、manifest、checksum 与 V8 state。

### Reverse Novelty Gate V9

- C27 content-salience follow-up completed after timestamp normalization. Fully label-free leave-one-out selectors still reveal residual target/background distribution shift; LOO-IDF Top-2 is 11.2% and LOO unique-token Top-2 is 13.6%, versus 0.83% random.
- Shallow-style matched controls confirm residual lexical separation across several matching widths, while effect magnitude varies with control-pool size. These runs remain audit evidence rather than a standalone method claim.
- Reverse novelty search found RAMR `memaudit.py`. Git history places the generic partial-input shortcut-floor method at 2026-08-12, with a LoCoMo audit committed the same day.
- RAMR already supplies surface probes, permuted-label nulls, a published shortcut floor, and structural re-cut neutralization. This directly covers C27's broad benchmark-method claim.
- C27 is therefore killed as a main research idea under the Prior-Art Kill Contract. The InMind timestamp/protocol vulnerability remains frozen as a specific benchmark audit finding.
- Active portfolio shrinks to C16; C25 remains blocked; C18 remains high-risk reserve.
- Project state rolls back to `IDEA_DISCOVERY_V10_AFTER_C27_KILL` and starts a new replacement screening round.


### Salience Gate V9

- Continued C27 after V8 protocol-level timestamp shortcut confirmation.
- Removed timestamp markers and quantified residual target/background writing-distribution differences.
- Held-out generic-feature classifier using nine query-independent style features reached ROC-AUC 0.9693 with bootstrap 95% CI [0.9357, 0.9935].
- Nearest-neighbor style matching reduced absolute Average-IDF target identifiability while preserving above-random residual lift.
- Added C27-C3 and C27-C4 as SUPPORTED claims. Matched end-to-end Application effect remains UNVERIFIED.
- DriftJudge artifact source, record count and checksum were re-confirmed; direct item-level cache transfer remains blocked in the current environment. C16 status unchanged.
- Added `13_salience_gate_v9/` with audit report, claim ledger, raw derived metrics, state snapshot, manifest, checksums and decision summary.

### Counterfactual Neutralization V10

- Applied deterministic surface-form neutralization to timestamp-normalized InMind targets while keeping each original personal fact verbatim.
- Adding only `What do you think?` reduced the frozen generic-style classifier AUC from 0.969 to 0.853 and eliminated Average-IDF Top-8 hits.
- Longer generic conversational wrappers reduced held-out AUC to 0.588 and 0.570.
- Added C27-C6 as SUPPORTED: residual pre-query identifiability is materially sensitive to surface-form neutralization.
- Refreshed prior art with Bad Genius / CHASE, protocol-validity benchmark audits, and homogeneous-haystack semantic-contrast controls.
- Narrowed C27 novelty to Agent Memory dual-axis benchmark validity: future-query retrievability versus pre-query target identifiability.
- Added `14_counterfactual_v10/` with counterfactual audit, prior-art refresh, claim ledger, derived metrics, state snapshot, manifest, checksums and decision summary.

### Repair Protocol V11

- Converted C27 findings into a provisional dual-axis Agent Memory benchmark audit and repair protocol.
- Added Gate A for serialization parity and Gate B for pre-query salience.
- Proposed provisional audit triggers of simple-selector lift@2 > 1.5 and held-out generic-feature AUC > 0.60, pending cross-benchmark calibration.
- Validated the protocol against InMind raw, timestamp-normalized, minimal-question counterfactual and long-wrapper counterfactual variants.
- Applied the same Gate B framing to WRIT full audit and LongMemEval stratified pilot; both exhibit benchmark-specific pre-query salience through length.
- Added C27-C7 as SUPPORTED_PILOT. Matched Application and human naturalness remain open.
- Added `15_repair_protocol_v11/` with protocol, repair pilot, claim ledger, derived results, state snapshot, manifest, checksums and decision summary.

### V18 Novelty and Runtime Gate

- Restored V17 as the immediate authoritative predecessor and continued C30 as the sole primary provisional idea.
- Re-audited the pinned Redis Agent Memory benchmark and current main; the relevant Zep count-stability readiness behavior remains present.
- Found generic quiescence/settle prior art in agent-memory-atlas plus fixed-settle protocols in Engram and RECON; narrowed C30 to paired empirical readiness-predicate validation.
- Raised C30 novelty risk to HIGH while preserving C30-C3 and C30-C4 as unverified real-effect claims.
- Frozen Zep paired-pilot protocol now compares benchmark count-stable readiness with per-message provider-native `processed` readiness and records canonical edge/fact fingerprints plus fixed retrieval through 300 seconds post-ready.
- Current runtime lacks Zep/AWS credentials and provider SDKs. This is recorded as BLOCK and carries no effect inference.
- Zep pilot harness, offline summarizer, frozen diagnostic workloads and four unit tests were implemented; compilation, unit tests and synthetic end-to-end analysis all pass.
- Added `22_novelty_runtime_gate_v18/` with novelty refresh, runtime block, protocol, code, tests, synthetic implementation fixture, search/source audits, Claim Ledger, Research State, manifest and SHA256.
- Formal Experiment remains NOT_STARTED. The next hard gate is the real Zep paired pilot in a credentialed runtime.

### V19 Red-Team Kill Gate

- Re-audited C30 against public live Zep evidence and raw benchmark timing artifacts.
- Found Waku Agent live evidence predating this project showing `processed=true` can precede derived-graph queryability and can yield an unrelated answer under an early probe.
- Invalidated V18's use of provider `processed` status as a semantic-completion oracle.
- Added MemArena public Zep Cloud accept-versus-settle timing evidence and generic systems steady-state-detection prior art.
- Determined that the remaining Redis count-stability mismatch is a useful benchmark-specific audit finding but no longer a sufficient main-paper contribution.
- Killed C30 as the primary research idea under claim-integrity and prior-art rules; retained its source audit, falsifier, trace tooling, and frozen protocol as reusable assets.
- Returned the project to Idea Discovery and excluded the asynchronous-readiness / settle / write-to-readable family from the immediate replacement round.

### Replacement Screen V20

- Continued from V19 after C30 was killed and excluded the full asynchronous-readiness family from replacement generation.
- Re-audited C18 `Policy-Epoch Memory Reauthorization`; direct versioned policy-memory and policy-bound authorization prior art now covers its central mechanism, so C18 moved from reserve to killed.
- Screened C34 derived-projection consistency, C35 retry-induced false corroboration, C36 restart-only durability and C37 embedding/index migration drift; all were rejected as already crowded.
- Promoted C33 `Benchmark-to-Deployment Path Drift in Agent Memory Systems` as the sole primary provisional candidate.
- Source-grounded C33 evidence includes Aelfrice's historical `retrieve_v2` eval versus legacy production `retrieve` split, claude-mem-lite's historical FTS-only benchmark versus production-hybrid path, and YourMemory's current benchmark/production ranking-config drift.
- Added current claude-mem-lite production-hybrid and Redis shipping-REST-API attestations as controls.
- Implemented the V20 Path Contract comparator. Five curated source-grounded cases matched their expected drift labels; six unit tests passed.
- The V20 pilot is feasibility evidence only. Automated path discovery, representative prevalence and matched dynamic score impact remain UNVERIFIED.
- Formal Experiment remains NOT_STARTED. Next Gate is a 12-system source-grounded mini-census and matched dynamic replay on at least two runnable systems.

### Path Census V21

- Expanded C33 from the V20 five-case feasibility set into a pinned 12-system source-grounded purposive mini-census.
- Identified multiple benchmark/deployment path-fidelity mechanisms: ranking/config drift, intentional dual retrieval paths, historical wrong-instrument repair, direct fixture ingestion versus production capture, benchmark-specific trajectory logic, lifecycle side-effect differences, and backend substitution risk.
- Added production-path controls including Klypix and deja-vu, which explicitly import or execute production retrieval paths during evaluation.
- Classified Aelfrice and claude-mem-lite as natural repair evidence rather than current broad retrieval divergence.
- Explicitly prohibited prevalence inference from the purposive 12-system corpus.
- Froze a representative sampling protocol that constructs a neutral registry-derived eligible frame and uses deterministic hash selection before labels are inspected.
- Added C33-C7 as SUPPORTED_PURPOSIVE_MINICENSUS and C33-C8 as FROZEN_PROTOCOL; population prevalence and automated-audit performance remain unverified.
- Root research state advanced to V21. Formal Experiment remains NOT_STARTED; next hard gate is representative sampling plus matched dynamic replay on at least two runnable systems.

### Representative Sample Freeze V22

- Pinned Agent Memory Atlas at `65e1225e122e366e641f4ab7632d4d5f25e5bf46` as a neutral external registry before representative C33 labels.
- Parsed 580 generated system reports and 68 reports referenced by the benchmark page at the same revision.
- Froze N=12, public-evaluation-plus-deployment eligibility, SHA-256 ranking and exclusion rules before labeling.
- Deterministic scan reached the twelfth eligible system at hash rank 20; every preceding exclusion and reason is retained.
- Frozen sample: Perseus Vault, Redis Agent Memory Server, PRO-LONG, open-cowork, Lethe, Cortex, RainBox, OpenExecutive, Verel, llm-wiki-memory, Veracium and Basic Memory.
- Redis is the only prior-known C33 case in the representative sample; sensitivity analysis excluding it is preregistered.
- Frozen Path Label Rubric defines six contract fields and EQUIVALENT / DIVERGENT / PARTIAL / INDETERMINATE before source audit.
- Sample validator and tests pass; no representative labels or prevalence estimate were produced at V22.

### Replacement Screening V20 / Reset Attestation

- C30 remained closed as a main research idea; asynchronous readiness variants were excluded from replacement generation.
- Screened benchmark-to-production path fidelity, shadow-memory attribution, derived-state correction reach, and reset completeness.
- C34, C35, and C36 were killed during screening because direct or strongly occupying prior art already covers their broad contribution space.
- Promoted C33 `Residual-State Contamination in Agent Memory Benchmarks` as the sole primary provisional candidate.
- Bound C33 to Redis Agent Memory Benchmark reset semantics and Mem0 v2.0.14 issue #6627, where `delete_all(user_id=...)` could return success while leaving memories beyond the first vector-store page.
- Confirmed Redis benchmark commit `94192c39e2a4a154f441a5411e3d73c4f54974a6` calls provider reset before each LongMemEval example; its Mem0 adapter implements reset via `Memory.delete_all(user_id=...)`.
- Ran a deterministic source-integration fixture using the affected control-flow shape: Run A stores 150 memories, reset reports success, 50 remain, and Run B retrieves Run-A canary state.
- C33-C1, C33-C2, and C33-C3 are supported at code/upstream/source-integration level. Real prevalence and benchmark score impact remain unverified.
- Added `24_reset_attestation_v20/` with Idea Card, source-integration gate, fixture code/result, candidate screen, prior-art matrix, Claim Ledger, Research State, handoff, bundle, and checksums.
- Formal Experiment remains locked. Next hard Gate is a frozen-version reset-attestation census followed by ordinary-reset versus verified-clean paired benchmark replay.

### Reset Census V21

- Continued C33 reset-attestation validation after V20 promotion.
- Confirmed the Redis benchmark leaves `mem0ai` unpinned, so current installs resolve the repaired Mem0 line; the historical v2.0.14 defect is retained as version-bound evidence rather than a claim about the current default environment.
- Audited the current Redis Agent Memory reset implementation and its upstream tests.
- Added C33-C6: `RedisAgentMemoryStore._delete_memories()` can return normally when the post-delete memory-id set stops shrinking even though memories remain; `test_redis_agent_memory_reset_stops_when_search_does_not_shrink` explicitly pins this behavior.
- Added C33-C7: a runner-level source-integration fixture reproduces the upstream-tested response pattern and shows a Run-A canary remains visible after Run-B ingestion while reset returned normally.
- Audited Zep, Bedrock AgentCore, Vertex Memory Bank, Graphiti, and Supermemory reset paths. No additional failure was asserted where the available contracts did not support it.
- Bedrock `ListEvents` pagination was checked against AWS documentation and SDK behavior; the benchmark's one-event-per-session pattern did not support the suspected residual mechanism.
- C33 now has two distinct supported mechanisms: a historical provider-side silent partial reset and a current benchmark-side silent partial reset contract.
- Real-provider prevalence and downstream metric impact remain UNVERIFIED. Formal Experiment remains locked.
- Added `25_reset_census_v21/` with current-harness gate, runner fixture, reset census, Claim Ledger, state, decision summary, manifest, checksums, handoff, and complete bundle.

### Reset Contract Census V23

- Continued from authoritative Reset-C33 V22 and preserved the older V20 branch as intermediate evidence rather than overwriting later state.
- Refreshed prior art with Agent Memory Harness, Engram v3, ForgetEval and Agent Memory Atlas. Cross-run contamination, clean-run isolation and reset invocation are now treated as established prior art.
- Narrowed C33 to independent post-reset state attestation plus measured benchmark outcome impact.
- Froze a purposive static reset-contract census covering 19 adapter implementations across Redis Agent Memory Benchmark, MemArena and ForgetEval.
- Four audited paths establish clean state by constructing a fresh local substrate. Fifteen reuse persistent, remote or otherwise reused state and execute cleanup procedures; zero of those fifteen enforce an explicit independent empty-state or frozen-canary postcondition before subsequent writes.
- The 19-adapter result is scoped to the pinned audited implementations and is not used as a field prevalence estimate.
- Reverse search of Mem0 issue #6995 found no raw artifact supporting the reported ~3,400 stale-document / Recall@1=0.000 benchmark collapse; that number remains outside frozen evidence.
- Current environment lacks a runnable affected Redis/Valkey or Mem0 backend and package installation is network-blocked. This remains an execution BLOCK with no effect inference.
- C33 remains primary provisional, novelty risk is HIGH, and C33-C5 outcome impact remains UNVERIFIED.
- Formal Experiment remains NOT_STARTED. Next Gate is the frozen invoke-only reset versus independently verified-clean reset paired benchmark replay on a real affected backend.

### Outcome Replay Harness V24

- Bound C33 to MemArena's pinned public default Mem0 stack: `mem0ai==2.0.11` with self-hosted Qdrant.
- Confirmed the historical one-page `delete_all()` defect class is present in that dependency line, while the benchmark adapter invokes `delete_all(user_id=namespace)` as its reset contract.
- Audited the committed 600-row Day3 Mem0 LongMemEval-V1 journal. Rep 0 contains 200 ingests; rep 1 and rep 2 contain zero ingests and reuse the ingestion cache; all 600 rows complete without infra errors.
- Combined with V1's question-specific namespaces, this is a negative control: current evidence does not support claiming that the published Day3 scores were contaminated by #6627.
- Added C33-C14 affected-stack binding, C33-C15 published-run negative control, and C33-C16 trigger-reach uncertainty.
- Froze the real paired outcome protocol before execution: measure natural reset-threshold reach first, then compare invoke-only reset against identical reset plus independently verified clean state.
- Froze JSONL trace schema, exact McNemar analysis for paired binary outcomes, and seeded 5,000-resample paired bootstrap analysis for continuous metrics.
- Synthetic paired-analysis fixture passed 9 assertions and remains implementation-only evidence.
- Formal Experiment remains NOT_STARTED. Real outcome replay is still blocked on a runnable affected backend.


### V31 Redis Pre-LLM Consumption Gate

- Resumed C33 from V30 and returned to the Redis × Mem0 2.0.19 primary runtime gate.
- Re-audited the exact frozen Redis retry path and Mem0 sidecar/prompt path.
- Found and corrected an unexecuted V28 probe fidelity issue: V28 would have overridden Mem0 extraction with the benchmark answer-model argument. V31 preserves the frozen Mem0 default extraction model `gpt-5-mini` and keeps the benchmark answer model separate.
- Strengthened paired branching from SQLite-only copying to complete failed-attempt Qdrant plus `history.db` cloning.
- Added an independent backend-visible vector receipt using exact Qdrant count plus paginated enumeration, cross-checked against Mem0's logical view.
- Executed the provider-independent deterministic consumption gate. A successful partial attempt wrote 3 scoped rows; native scoped reset preserved all 3; verified cleanup reduced the scope to 0; the retry extraction prompt consumed 3 rows in the native arm and 0 in the clean arm, with a 103-byte prompt delta and different SHA-256.
- Raised Redis evidence from source-only reachability to executed pre-LLM prompt consumption. Representation, retrieval, answer, and LongMemEval judge effects remain pending exact credentialed runtime.
- Ran five offline unit/protocol tests and Python compilation checks; all passed.
- Performed a narrow 2026 prior-art refresh. Adjacent reset-hygiene, memory-isolation, lifecycle-security, and stateful-agent benchmarks keep novelty risk HIGH; the targeted pass did not locate a direct match to the complete C33 contribution bundle.
- Formal Experiment remains locked. The next hard gate is the corrected V31 Redis exact-stack paired replay.

### V33 Public Score Forensics

- Continued C33 after V32 removed generic reset-attestation method novelty and required stronger empirical evidence.
- Re-audited the frozen Agent Memory Benchmark v2 public Mem0 and Zep artifacts at commit `55d4f02d61388525105ffe34fe3f9d2c846d25bf` against the frozen runner, scorer and adapter code.
- Mem0 public results contain four high-confidence deletion-target residuals with direct binary score impact: `sf-02`, `sf-05`, `sf-06`, and `ce-05`. Each retrieves the target after the harness invokes deletion, at retrieval score 0.9, and fails an `expectEmpty` query.
- A trace-restricted scorer counterfactual removing only those four observed residual rows changes Mem0 exact weighted score from 7.142857 to 12.767857 and reported rounded score from 7 to 13. This is recorded as trace-level score dependence, not a clean-rerun estimate.
- Preserved the earlier Mem0 `ma-03` historical stale retrieval as a distinct score-neutral cross-run event.
- Established a stronger Zep lifecycle mismatch: one run-level user spans the full benchmark, search uses that user scope while ignoring per-test agent identity, and per-memory delete returns success without removing provider state.
- Same-UUID forensics over the committed Zep Layer-1 result finds 57/59 queries with at least one result ID first seen in a different earlier test, 30/59 with all recorded Top results from prior tests, and 24 unique reused provider object IDs.
- Identified a direct score-positive trace at `tr-06-q1`: all recorded Top results are prior-test IDs, while expected keyword `4` is satisfied only by digit `4` embedded in a stale run-level user identifier. Trace-restricted removal flips the query from pass to fail and reported score from 11 to 9.
- Identified score-masked leakage in six Zep `expectEmpty` queries that pass despite three non-empty prior-test retrievals because all returned scores fall below the benchmark's 0.1 threshold.
- Confirmed the audited Zep adapter blob is unchanged on the current default branch as of 2026-09-19.
- Froze a four-regime empirical taxonomy: score-negative, score-positive, score-masked, and score-neutral hidden-state contamination.
- Froze provisional RQ1-RQ3 and study set. Formal large-scale experiment remains unstarted, while the formal pilot is now unlocked.
- Added `37_public_score_forensics_v33/` with public forensics report, derived evidence JSON, deterministic audit code/tests, claim ledger, RQ freeze, source provenance, test report, manifest and checksums.
