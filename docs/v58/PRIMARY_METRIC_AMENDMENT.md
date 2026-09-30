# V58 Primary Metric 前瞻性补充冻结

日期：2026-09-30。性质：**prospective design amendment**。原 V58 冻结材料中的 `d(v_i,v_j)` 未唯一指定表示与距离；这项缺口已在此前[审查](REVIEW_P0_P3.md)中记录。补充前 V58 正式运行、模型调用和结果观察均为 **0**。

本次将 `v` 明确绑定为 V57 已有的 1925 维 Ordered Top-5 Retrieval Footprint，将 `d` 明确绑定为两个 footprint 转 `float64` 后的 Euclidean L2 距离。文本来自 V55 的同一 `search(..., top_k=10)` 路径、`normalize_results` 及 `text_hashes_in_order` 所用字段；完整 Top-10 保存为 raw，footprint 只取前五条。空检索为合法全零向量。详细机械规则见[新增 amendment](../../study_freeze/V58_PRIMARY_METRIC_AMENDMENT_20260930.json)和[用户补充原文](PRIMARY_METRIC_USER_SOURCE_20260930.txt)。

选择依据是 V58 结果尚未产生、V57 已前瞻性冻结同一 footprint 和 Euclidean norm、V59 已批准设计写明沿用同一 Top-5 footprint。**这不是原 V58 冻结已包含的内容**。原 `V58_POLICY_ORDER.json`、`FREEZE_MANIFEST.json` 与历史原件保持不变；新增 manifest 单独绑定旧冻结和本次补充。

四题、12 order、24 sequence、N/V 分配、36/36 覆盖、`D`/`S`/`Δ` 公式、4096 次 exact randomization、单侧方向、`p<0.05` 和主张边界均不因本次补充改变。此次落盘本身不允许正式运行；仍需独立审计与工程 gate。
