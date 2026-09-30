# V58 固定四题 Policy × Order 研究协议

本文件整理[原冻结方案](../../history/pre_v58_root_20260930/study_freeze/V58_POLICY_ORDER.json)及[2026-09-30 前瞻性主指标补充](../../study_freeze/V58_PRIMARY_METRIC_AMENDMENT_20260930.json)，不替代两份原件。补充前 V58 正式模型调用和正式结果均为 0；旧冻结文件未改动。当前实施身份须同时绑定[补充 manifest](../../study_freeze/V58_AMENDMENT_MANIFEST_20260930.json)。

## 问题与竞争解释

检验固定四题 panel 中，Native Reset 与 V55 Verified Cleanup 是否改变由先前完整顺序决定的 retrieval dispersion。竞争解释包括模型/抽取随机性、scope 或 sequence 隔离错误、与 V55 路径不一致、target 位置效应、trial 伪重复、恢复重发、源码/模型/数据漂移及检索变化被过度解释为准确率或排名变化。

## 固定设计

A=`gpt4_ec93e27f`(47 sessions)，B=`gpt4_45189cb4`(45)，C=`08f4fc43`(47)，D=`e8a79c70`(44)。12 个 order 与每个 order 的 N/V slot 均以原 JSON 为准；共 24 个相互独立的四 trial sequence、96 个 trial、4,392 次 session ingestion。每个 sequence 在新 Python process、新 scope 和新持久化 store 中执行，同一 sequence 内四个 trial 共用 scope。trial 间只运行本 sequence 的冻结 N 或 V policy。

N 是 V55 benchmark-native `Mem0MemoryStore.reset()`；V 是相同 native reset 后删除该 scope 的 sidecar messages 并重新打开 store。两者均以同一个哈希固定的 V45 engine 与 V55 stack 为准。不得增加 cleanup，也不得对每个 trial 使用新 scope。

## 主指标与检验

每个 trial 完成 ingestion 后按 V55 路径运行 `search(question, filters={"user_id": scope}, top_k=10)`，先保存完整原始 Top-10，再按 V45 `normalize_results` 和 `text_hashes_in_order` 的字段规则取文本。前五条用哈希固定的 Ordered Top-5 BGE footprint 转成 1925 维 `float32`；空检索是合法全零向量。两向量先转 `float64`，距离为 Euclidean L2。

每个 target × position(2–4) × policy cell 的三条 observation 两两距离取平均为 `D`；12 个 cell 的平均为 `S_policy`；主效应 `Δ=S_N−S_V`。在 12 个 order block 内交换 N/V 标签，完整重算 `D→S→Δ` 共 4096 种，`p=#(Δ_perm≥Δ_obs−1e−12)/4096`。只有 `Δ>0` 且 `p<0.05` 才允许固定四题 panel 中 Verified Cleanup 降低顺序相关检索敏感性的主结论。

## 次要记录、停止与解释边界

保存四题回答、问题和参考答案。用户于 2026-09-30 确认 **0–4 correctness score 暂不判分**；判分器待另一项前瞻性决断，不参与本次主判定。每个 request 在发送前落盘并绑定哈希；发送后任何不确定失败都停止该单元，不自动重发。每一已完成步骤原子保存状态；未提交的步骤在恢复时拒绝自动继续。

冻结文件、数据、模型 digest、Native/V 路径、scope、checkpoint、预算或统计实现任一 gate 失败即停止新的请求。本设计平衡直接前驱与 target 位置，但 observation 仍受完整前序历史影响；不能归因于单一直接前驱，也不能推导 accuracy、score 或 ranking 变化。
