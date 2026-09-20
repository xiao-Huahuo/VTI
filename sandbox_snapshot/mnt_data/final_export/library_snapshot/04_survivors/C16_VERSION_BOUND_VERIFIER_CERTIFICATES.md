# Idea C16: Version-Bound Verifier Certificates

Working title: **When the Verifier Changes but Memory Trust Does Not**

## Problem
长期记忆治理系统会持久化 verifier 的 label、confidence、reward 或 uncertainty，并在之后的检索、冲突处理和归档中重复使用。部署中的 verifier 本身会升级：模型版本、prompt、rubric、policy、校准阈值都会变化。旧 metadata 可能在内容完全不变时失去语义有效性。

## Observed Failure Hypothesis
Memory M 在 V1 下被标为 TRUSTED。系统升级到 V2 后，如果继续复用 V1 certificate，相当于把“过去验证器的判断”误当成“当前验证器仍认可”。当前检索未发现这一失效模式的专门 benchmark 或方法。

## Mechanism
所有 verifier-derived metadata 绑定：
`verifier_id / version / policy_hash / prompt_hash / calibration_snapshot / verified_at`

升级时估计 V1 与 V2 的 disagreement region，只对高风险 memory 做 selective recertification。

## H1
在 verifier migration 后，直接复用旧 certificate 会产生可测量的 trust-label drift，即便 memory content 一字未变。

## H2
version-bound certificate + drift-aware selective recertification 可以用显著低于 full revalidation 的成本恢复大部分 current-verifier consistency。

## H3
风险集中在 verifier decision boundary、policy changed region 和低 margin memory，而非均匀分布。

## Killer Experiment
冻结 memory bank。V1 产生 certificate。仅替换 V2，memory content 保持完全相同。比较：
1. stale V1 certificate
2. full V2 recertification
3. random partial recertification
4. margin-based partial
5. proposed drift-aware selective recertification

指标：V2-consistency error、downstream action error、recertification cost。

## Kill Conditions
1. 合理 verifier update 下 V1/V2 disagreement 极低，问题缺乏实际规模。
2. random partial 与风险感知 selective recertification 无稳定差异。
3. 现有 verifier governance 工作已经系统解决 version binding + selective recertification。
4. 下游任务对 certificate drift 不敏感。

## Novelty Boundary
不声称发明 persistent verifier metadata。该前提已有 MemGuard。研究对象是“verifier 本身变化后 metadata 的时效语义”和 recertification。
