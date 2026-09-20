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
