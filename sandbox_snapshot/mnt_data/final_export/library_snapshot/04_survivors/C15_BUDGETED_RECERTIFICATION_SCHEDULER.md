# Idea C15: Budgeted Memory Recertification Scheduler

Working title: **Which Memory Should Be Re-Checked First? Budgeted Recertification for Long-Lived LLM Agents**

## Problem
长期 Agent 的记忆库持续增长，环境、规则、工具和来源会变化。验证预算通常远小于记忆规模。关键问题从“能否验证”转为“有限预算下先验证谁”。

## Observed Failure
arXiv:2608.25553 已证明，同样两次验证预算，只改变 allocation 就能让 stale-constraint 的 current-consistent decision 提升约 61-74 个百分点。该论文同时明确指出它使用已知 critical provenance path，不是 scheduler。

## Mechanism
构建 risk-aware recertification scheduler。对每条 memory 估计：

`priority ≈ staleness_hazard × future_use_probability × downstream_loss × dependency_fanout / verification_cost`

可从可解释启发式开始，再扩展 contextual bandit / learned scheduler。

## H1
相同 verification budget 下，风险感知 scheduler 比 random、age-only、relevance-only、TTL 等策略产生更低的 stale-memory-induced action error。

## H2
随着 memory-bank size、source churn 和 dependency depth 增长，调度收益扩大。

## H3
调度收益来自 verification allocation，而非额外模型调用或额外读取预算。

## Killer Experiment
构建动态记忆流：部分 source 在时间 t 被 supersede，每个 memory 具有不同未来访问概率、影响范围和验证成本。固定 B 次验证。比较：
1. Random
2. Oldest-first
3. Retrieval-frequency
4. Fixed TTL
5. Relevance-first
6. Oracle critical-path
7. Proposed scheduler

主指标：stale-induced decision error / unit verification cost。

## Kill Conditions
1. 简单 oldest-first 或 TTL 在多种 churn setting 下与 proposed scheduler 无稳定差异。
2. scheduler 只有在使用 oracle future access 或 gold critical path 时有效。
3. 提升完全来自更多可用 metadata，而非调度本身。
4. 新 prior art 在正式实验前直接解决同一 scheduler 问题。

## Why It Survived
目前最强 direct precursor 明确留下“不是 scheduler”的缺口，而且其 effect size 说明 allocation 值得单独研究。问题定义清晰、可精确判分、无需先依赖主观 LLM judge。
