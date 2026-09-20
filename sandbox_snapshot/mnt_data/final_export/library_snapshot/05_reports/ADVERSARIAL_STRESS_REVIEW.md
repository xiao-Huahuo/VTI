# Adversarial Stress Review

## C15
攻击：风险分数过于依赖准确的 staleness/use estimate。  
结果：在 synthetic proxy noise 提高到 0.35 时仍保留正向区分，但这只是构造性证明。  
保留条件：真实实验禁止使用 gold future access、gold stale label、gold critical path 作为 scheduler 输入。

攻击：问题只是经典 cache refresh。  
处理：论文贡献需要落在 persistent agent memory 的 provenance dependency、downstream action consequence 和 verification-cost coupling，并与 TTL/cache policy 正面对比。

## C16
攻击：这是普通 metadata versioning 工程规范。  
处理：单纯绑定 version 不足以构成论文。核心科学问题必须是 verifier migration 引起的 certificate drift 规模、分布和 downstream behavior，以及 selective recertification 是否能显著低成本恢复一致性。

攻击：真实 verifier 更新差异太小。  
结果：stress fixture 明确显示轻微 shift 时问题规模很小。该项被写入 Kill Contract。

## C17
攻击：只是给 utility 减一个 cost。  
处理：若真实实验表明 one-shot latency/storage penalty 已足够，本 Idea 淘汰。论文成立需要 recurring revalidation/conflict/migration cost 在长程中形成结构性差异。

攻击：环境稳定时无收益。  
结果：fixture 已验证该边界。研究范围应明确针对 dynamic long-lived agents，而非所有 memory workload。

## 审查结论
C15 保留，风险为 precursor 很近但缺口清晰。  
C16 保留，风险为实际 effect size 未知。  
C17 保留但进入高风险标记，必须先做真实 workload cost census，再投入完整方法开发。
