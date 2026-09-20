# Idea C17: Maintenance-Aware Memory Admission

Working title: **The Hidden Cost of Remembering: Maintenance-Aware Admission for Long-Lived Agents**

## Problem
现有 admission policy 主要判断一条记忆未来有没有用、是否可信、是否新颖、是否近期。长期 Agent 接受一条 memory 后，还会持续付出维护成本：验证 freshness、处理冲突、重嵌入、迁移 schema/model/tool、参与更多 retrieval candidates、执行删除与 retention policy。

两个候选 memory 的即时 usefulness 相同，其 lifetime burden 可以完全不同。

## Mechanism
将准入目标改成 expected lifetime net value：

`NLV = expected_future_task_utility - expected_lifecycle_maintenance_cost`

维护成本按事件建模，而非只算 storage bytes：
- revalidation cost
- conflict-resolution cost
- retrieval/index cost
- migration/re-embedding cost
- deletion/compliance cost

通过 use hazard、change hazard 与 cost model 估计。

## H1
在动态环境和固定长期预算下，utility-only admission 会积累更高维护负担，使长期 cumulative task utility 下降。

## H2
maintenance-aware admission 在相同总生命周期预算下提高 cumulative task success / cost，并降低 stale/conflict backlog。

## H3
收益主要出现在 high-volatility、low-reuse 或 high-verification-cost memory；稳定高复用记忆仍会被保留。

## Killer Experiment
构造流式候选记忆。让候选具有相近 initial utility，但不同：
- future use probability
- source volatility
- verification cost
- dependency fanout

比较：
1. admit-all
2. recency
3. A-MAC-like utility score
4. fixed capacity eviction
5. proposed NLV admission
6. oracle lifetime-value

指标：累计任务收益、总维护成本、stale backlog、单位总成本成功率。

## Kill Conditions
1. 把简单 latency/storage penalty 加到 A-MAC-like score 后即可得到同等效果。
2. recurring maintenance cost 在现实 workload 中占比很小。
3. NLV 估计误差使长期收益低于简单策略。
4. 新 prior art 已直接提出 lifecycle-maintenance-aware admission objective。

## Novelty Boundary
不使用“首次提出 Agentic Technical Debt”之类 claim。2026 已有 Agentic Technical Debt taxonomy。论文只研究一个可操作优化问题：memory admission 如何内生化长期维护外部性。
