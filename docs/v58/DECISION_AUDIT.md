# V58 假设与决断审查（2026-09-30）

| 项目 | 来源与状态 | 审查结果 |
| --- | --- | --- |
| 研究问题与主张边界 | 批准原文、V58 JSON；已冻结 | 固定四题 panel 的 policy 对完整历史顺序相关 retrieval dispersion 的影响；不推导 accuracy 或排名。 |
| 样本与顺序 | V58 JSON；已冻结 | A–D 四题、12 个 order、每 order 两个独立 sequence；机械检查通过。 |
| N/V assignment | V58 JSON；已冻结 | 12 个 block 各一 N 一 V，slot 分配已物化；不可重新随机化。 |
| 统计单位与检验 | 批准原文；已冻结 | order block 内交换 policy 标签，4096 个合法 assignment；不得把 trial 当独立随机化单位。 |
| 主统计结构与阈值 | 批准原文；部分冻结 | `S_N-S_V`、单侧 exact Fisher、`p<0.05` 且 `Δ>0` 已写明。 |
| 检索表示 `v` 与距离 `d` | V58 部分未明确绑定；**阻断** | V57 有一套候选表示和 Euclidean 统计，不能由实现者擅自宣称已冻结用于 V58。 |
| Native 与 Verified 语义 | V55 冻结源码；待本版运行路径审计 | V45/V55 文件哈希匹配；尚未证明 V58 调用路径完全一致。 |
| 运行身份、恢复与预算 | 当前任务的实施要求；未实施 | 属后续工程决策和执行 gate，不能写成旧方案已通过。 |
| 事后诊断 | 尚无 V58 结果 | 若未来开展，须独立标记 POST-HOC，不改变主指标。 |

**决断：** 当前只承认历史文件级设计冻结；V58 主要 outcome 尚未达到可执行冻结。补充记录必须在任何 V58 实施与正式数据查看前完成，保留旧冻结原件并标记新身份。本次未作任何修订性科学决策。

## 2026-09-30 后续决断

用户在正式 V58 结果产生前提交[新决断原文](PRIMARY_METRIC_USER_SOURCE_20260930.txt)，将 `v` 固定为 V57 已有 footprint、`d` 固定为 `float64` Euclidean L2。其状态是 **PROSPECTIVE AMENDMENT**，不是原 V58 方案已冻结的事实。原四题、12/24 顺序与分配、D/S/Δ、4096 次检验、阈值、栈与主张边界保持原状；[amendment manifest](../../study_freeze/V58_AMENDMENT_MANIFEST_20260930.json)保存身份。

用户另决定：V58 的 0–4 correctness score 暂不判分，只保存每题回答与参考答案。这是 2026-09-30 的**实施范围决断**，并未选择新 scorer，不会成为主要指标或预注册 correctness 结论。所有实际运行身份和预算属于执行时 gate，不应倒写成研究设计冻结时已经通过。
