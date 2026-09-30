# V58 开发执行 profiling：资源筛查与短样本结果

日期：2026-09-30。状态：`STOPPED_AT_RESOURCE_PREFLIGHT`。**V58 正式模型调用 0，正式 runner、checkpoint、统计与原冻结方案均未改变。** 本次开发调用仅使用历史开发问题 `b5ef892d`、`1a8a66a6`，所有收据位于被 Git 忽略的独立 `v58-profile-*` run_id，标为 `DEVELOPMENT_PROFILING / NOT_FORMAL_DATA`。

## 2 路服务配置的开发 smoke

依据[初始 profiling freeze](EXECUTION_PROFILING_FREEZE_20260930.json)与[入口修正身份](EXECUTION_PROFILING_FREEZE_V2_20260930.json)，Ollama 0.34.3 以 `OLLAMA_NUM_PARALLEL=2`、`num_ctx=32768`、同一 Qwen digest 启动。第一次入口尝试在创建 run 目录和发送请求前因模块名冲突失败，已独立记录并修复 profiling 代码，正式代码未改。

随后[资源停止收据](../../solutions/v58/outputs/v58-profile-macm5-20260930-smoke-w1/raw/RESOURCE_PREFLIGHT_STOP.json)记录了 **1 次开发请求已发送、0 次响应落盘、只有初始 checkpoint**。`ollama ps` 当时显示模型约 19GB、`42% CPU / 58% GPU`、32k context；`memory_pressure -Q` 返回 free percentage 约 6%（不是物理空闲内存比例）。Ollama 日志显示请求约 6 分 48 秒后随客户端终止取消。为避免继续加重内存压力，主动终止开发 worker，保留 prepared/dispatched 收据，不重发该不确定请求。**实际两个 worker 未启动，1.35× 吞吐 gate 没有被测量，也不能记作通过。**

## 原串行服务配置的短 smoke

按[资源后续决断](EXECUTION_PROFILING_RESOURCE_CONTINGENCY_20260930.json)，另以 `OLLAMA_NUM_PARALLEL=1`、其余模型条件不变运行两个开发 ingestion。[完成收据](../../solutions/v58/outputs/v58-profile-macm5-20260930-serial-smoke-w1/raw/development_summary.json)显示 2/2 提交、2 次开发响应保存、4 个 checkpoint 回读通过。总 wall time 157.71 秒，其中 LLM request wall time 152.69 秒，约 **96.82%**；checkpoint 总计 0.024 秒，约 **0.015%**。Qdrant 包装调用约 0.292 秒、SQLite 包装调用约 0.023 秒、backend embedding 包装调用约 0.813 秒；这些是嵌套诊断，不能简单相加成互斥时间分解。[资源收据](../../solutions/v58/outputs/v58-profile-macm5-20260930-serial-smoke-w1/raw/RESOURCE_SCREENING.json)显示模型约 14GB、`22% CPU / 78% GPU`、`memory_pressure -Q` 返回 free percentage 约 7%（不是物理空闲比例）；当时 swap 约 5.35GiB。

## 决断与边界

本次共有 **3 次开发请求发送、2 次响应保存，V58 正式调用 0**。两个成功 session 只能作瓶颈筛查，未满足预定 30–50 个 ingestion 的稳定性样本量；不把 45.65 sessions/hour 直接外推到正式 4,392 sessions，也不更新 70–100 小时正式串行预算。短样本支持“先不要优化 checkpoint”的工程判断。

当前 Mac 的 2 路配置在单 worker smoke 阶段就发生严重 GPU/CPU 分摊和内存压力，故**不启动 102-session 的 1/2 lane 对照**，也不创建正式并发 execution amendment。`1.35×` 前瞻性 gate 状态为 **NOT_EVALUATED / NOT_QUALIFIED**，原 V58 串行 `READY_FOR_FORMAL_RUN` 状态保持；若将来有更合适的资源或清理其他内存占用，须使用新的开发 run_id 和独立审计重新评估，不可重试本次不确定请求。

## 内存口径更正（2026-09-30）

撤回把 `memory_pressure -Q` 的 free percentage 当作物理可用内存的解释；不能据此推算 93%/94% 实体内存已用。Ollama 的 14GB/19GB SIZE 也不能与应用 RSS 相加当作新增物理占用。原始收据保持不变，CPU/GPU 分配、swap 和耗时仍是实测证据。此前开发 smoke 未控制后台应用占用，不能当作干净空闲机器的性能基线。

当前未加载模型的读取：统一内存 16GiB，非文件缓存占用页统计估计约 10.16GiB，文件缓存约 5.06GiB，swap 为 0。这是整机统计，不是 Codex 独占；文件缓存可被系统回收。进度页改为展示页统计估计、文件缓存和压缩内存，明确与活动监视器可能有差异。正式运行前应记录后台应用、内存与 swap 基线；不据本次空闲读取更新 70–100 小时预算。
