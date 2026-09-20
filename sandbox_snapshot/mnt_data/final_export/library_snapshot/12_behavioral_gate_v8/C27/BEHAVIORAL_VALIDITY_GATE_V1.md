# C27 Behavioral Validity Gate V1

日期：2026-09-18

## 当前结论

C27 从静态 identifiability diagnostic 前进到 protocol-level shortcut proof。InMind raw release 中，target pair 在完整 pre-query timeline 里可由 serialization format 100% 识别；官方 Target Recall 又直接以“target fact 是否进入 answer context”为判分条件。两者组合后，query-independent format selector 可以获得 100% Target Recall，而无需求解 benchmark 想测量的 memory-query implicit association。

该结果满足 behavioral gate 的 retrieval-side 条件，因为 Target Recall 是 InMind 官方 primary metric 之一，并且 selector 输出直接改变官方 judge 的输入 `context`。

Application 层仍采用严格分离。论文报告 In-context Control 84.0% 和 Always-in-state 68.8%，证明 target visibility 会显著改变最终 answer behavior；当前 release 尚未公开 paper-aligned per-task results，本轮也没有同配置调用 GPT-5-mini answerer/judge，因此 format selector 的直接 Application score保持 `UNVERIFIED`。

## Red-Team interpretation

最强替代解释是“这只是 release packaging bug”。当前证据支持把它视为 release-level evaluation vulnerability，而非 memory algorithm failure。C27 主 claim 因而继续收缩：研究重点是 Agent Memory benchmark 的 dual-axis validity，包括 query-time retrievability 与 pre-query target identifiability，并要求 validity-preserving counterfactual neutralization。

WRIT 与 LongMemEval 的 V7 结果继续提供跨 benchmark 支撑：WRIT 的稳定 signature 主要来自 length；LongMemEval 的 signature 依 question type 变化。它们支持“signature 类型由数据构造决定”，同时也限制任何“timestamp artifact 普遍存在”的表述。

## 下一 Gate

1. 在 InMind 上构造 content-salience matched target/background control，分解去除 timestamp 后残余 14.4% Top-2 signal。
2. 获得 GPT-5-mini 同配置执行能力或作者公开 per-task outputs 后，冻结 format-selector Application run。
3. 对 WRIT 的 length signature 做 matched-length counterfactual，检查 Target Recall / task validity 是否随长度中和而变化。
4. 将 CHASE 作为强近邻，比较 general protocol-shortcut neutralization 与 Agent Memory dual-axis audit 的差异。

若 matched controls 只留下单一 release packaging defect，C27 降级为 InMind release audit。若多个 benchmark 在有效 counterfactual 后仍存在可利用 pre-query signature，C27 进入 full benchmark-method study。
