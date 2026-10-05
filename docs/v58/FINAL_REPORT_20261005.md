# V58 正式运行与最终验收

## 结论

**在固定四题 panel、此次 8192 输出上限的执行条件下，Verified Cleanup 相比 Native Reset 降低了由完整前序历史/顺序条件化的检索结果离散度，达到冻结的主指标判定门槛。**

| 冻结指标 | 结果 |
| --- | ---: |
| Native Reset 离散度 S_N | 0.8635833941 |
| Verified Cleanup 离散度 S_V | 0.7273865832 |
| Δ = S_N − S_V | 0.1361968109 |
| 精确单侧 p | 42 / 4096 = 0.01025390625 |
| Δ > 0 且 p < 0.05 | 通过 |

相对 S_N 降低约 15.77%，为上述离散度的描述性比例，不是准确率提升。V 条件的离散度仍非零，不能宣称消除了全部顺序敏感性、模型随机性或全部隐藏状态。

## 运行身份与完整性

北京时间 2026-10-05 **21:26:30** 计算完成。逻辑结果集由 `solutions/v58/RECOVERY_MANIFEST_20261003.json` 绑定：block1–6 的12条已完成 `formal-mac-20261001-output8192` sequence，加 block7–12 的12条新 `recovery-mac-20261003` sequence。24 slots、12 order blocks、96 trials、4392 ingestion、96份答案与参考答案、4488选定模型请求全部完成。

[最终证据审计](FINAL_EVIDENCE_AUDIT_20261005.json) 对24条完整 sequence 共4584 checkpoints进行回读，唯一scope24，原source、冻结设计/输入/主指标/执行修订身份一致。96次原始检索结果按原字段规则重建文本/排序哈希，重新离线 BGE embedding 与1925D footprint **逐float32元素完全一致**，最大差异0。

72个trial边界：N/V各36；两者native vector/backend count均归零，N sidecar messages保留、V侧归零。选定4488个请求均有响应及原始HTTP收据，未选定run混入，无选定terminal错误或length停止。原raw未改。

[结果摘要](FINAL_RESULT_SUMMARY_20261005.json) 绑定分析JSON和审计哈希。另以六观测距离矩阵、独立policy分组和三对距离平均重算所有4096交换；与原统计程序全部assignment effect在1e-12内一致，右尾计数42一致。统计使用12 order block内标签交换，trial不当作96独立实验单位。

## 失败、修订与可解释边界

1. 初始2048上限批次发生JSON截断，完整保存、全部排除。用户授权后，于下一批次前记录8192执行修订及同步预算，独立开发验证通过。**结果适用于修订后的执行条件**，不能称原2048条件被原样执行或最初预注册从未改变。
2. 8192批次的旧b07-s1发生已dispatch无响应，63次尝试/61已提交ingestion现场保留，整个失败sequence排除。不得假装原请求被成功恢复。前12完整sequence身份匹配后复用，block7–12从独立空状态新run完整执行，统一预先绑定manifest；未根据科学结果选择数据。
3. 本轮8192运行选择4488请求；包括排除的旧失败63请求在内，实际尝试4551。此前2048失败191请求另行保留。开发资格调用不计正式样本。不同上限数据未混用。
4. Native库在已完成sequence退出清理时发生recursive_mutex异常，证据保留。只在COMPLETE、精确异常/信号码及完整回读通过时跳过已完成成果继续调度，未重复模型请求。后来修复了组合coordinator直接worker日志辨识误判，原实验source/参数未改。不能宣称底层native缺陷已消除。
5. 用户主动暂停与重启只在安全checkpoint完整回读后恢复；已完成部分未重算。监督存在实际间隔超过一小时的情况，计划时间与实际checked_at分开记录。

## 三层最终审查

| 审查层 | 验收与边界 |
| --- | --- |
| 语句到语句 | 原四题、12order/24slot、N/V、全量历史重放、retrieval规则、1925D float32及float64 L2、4096精确单侧、阈值、全量checkpoint/原HTTP、答案与参考保留均有对应证据；correctness按用户决定待定。 |
| 挖洞 P0 | 当前选定证据中未发现主指标错误、源/数据漂移、重复slot、原请求重发、失败run混入或恢复损坏；独立全量回读/footprint/置换重算通过。 |
| 挖洞 P1 | 无本版已承诺验收项的未解决阻塞；不将尚未冻结的correctness评分冒充已完成。若论文要声称accuracy/ranking或更广泛配置，需要额外设计，当前结果不支持。 |
| 挖洞 P2 | 四题固定panel、单栈/单机器、V非零离散度、执行修订发生于失败之后、基础设施失效/结果集恢复过程与运行时噪声必须披露；该精确p只在冻结block交换假设下解释，不能证明所有竞争机制或一般隔离性质。 |
| 假设与决断 | 单一冻结主指标/方向/阈值保持，不尝试替代表示、距离、分组或择优p。复用/排除以完成与基础设施失败身份判定，未观察中途科学效应作决策；冻结执行修订、恢复manifest和所有失败分母保留。 |

## 允许的表述

“在此固定四题 panel 与绑定的 Mem0/Qwen/BGE 执行配置中，Verified Cleanup 相比 Native Reset 显著降低完整历史/顺序条件化的检索离散度（Δ=0.1362，精确单侧p=0.01025）。”

不能推出单一直接前驱因果效应、准确率提升、0–4 score变化、排行榜变化、其他模型/数据/后端普遍成立，或完全实现trial isolation。**96份答案/参考答案保存，correctness未评分。**

## 结果位置与结束动作

- 选定run与排除现场：本版outputs及恢复manifest。
- 原始统计：`solutions/v58/outputs/v58-recovery-mac-20261003-analysis/processed/exact_randomization.json`。
- CSV：同目录 `cell_dispersion.csv`、`order_distances.csv`。
- 复核入口：`src/ops/final_audit.py`，完整审计收据已经存在，重跑时应使用新审计输出名，不能覆盖原收据。
- 实验及验收完成，停止本次本地模型服务释放资源，停用每小时监督；进度HTML继续可读。
