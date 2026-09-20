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
