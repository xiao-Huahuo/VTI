# V58 Development Execution Profiling（待目标机器确认）

状态：`STOPPED_AT_RESOURCE_PREFLIGHT`，实际收据与解释见[短样本筛查](EXECUTION_PROFILING_SCREENING_20260930.md)。目标机器已由用户确认为当前 Mac；原计划机械身份见[profiling freeze](EXECUTION_PROFILING_FREEZE_20260930.json)。本文件是 2026-09-30 用户提出的**前瞻性执行评估计划**，不改写 V58 原冻结方案、补充主指标、正式串行 runner、checkpoint、预算或已有 `READY_FOR_FORMAL_RUN` 证据。profiling 结果只能进入独立 `solutions/v58/outputs/<profiling_run_id>/`，身份须标记 `DEVELOPMENT_PROFILING`、`NOT_FORMAL_DATA`。V58 正式模型调用维持 0。

## 目的与身份

在计划承担正式 V58 的同一机器上，先定位每个 session 的时间来源，再比较 1 与 2 lane 的**成功提交 sessions/hour**。8GB RTX 4060 Laptop 上的结果不能由当前 Mac 的测量代替。任何开发调用不得使用 V58 正式 ranks 29–32，不进入正式统计、run_id 或分母。

开发 workload 固定为历史开发案例 rank 1 `b5ef892d` 与 rank 3 `1a8a66a6`，每条 profiling sequence 依次取两例的前 26、25 个 session，中间按同一已冻结 cleanup 路径执行一次边界操作。两条 profiling sequence 使用相同开发输入、不同新进程与独立 scope。1 lane 时两条依次执行；2 lanes 时两条同时执行。每种条件均为 102 次计划 ingestion；所有实际请求、失败和已提交单元须逐项记录。此短 workload 只用于资格门，不能直接推出完整 183-session 正式 sequence 的墙钟时间。

## 固定比较与停止

在开始模型开发调用前，固定目标机器、GPU/CPU/驱动、Ollama 版本、模型文件 digest、`num_ctx=32768`、`keep_alive=30m`、`OLLAMA_NUM_PARALLEL`、`OLLAMA_KV_CACHE_TYPE`、Flash Attention 状态、Python/Mem0/BGE/Qdrant 版本及输入哈希。1/2 lane 比较保持这些服务配置相同；只改变活跃 worker 数。若同机服务无法容纳两路，请记录排队/回退，不缩减 context 或修改 KV 精度以硬凑 gate。每次运行使用新 `profiling_run_id`，不复用状态或重发不确定请求。

第一阶段只做 1 lane 的瓶颈分解：LLM 请求 wall time、ingestion 总 wall time、除 LLM 外的 backend wall time、Qdrant 调用、SQLite sidecar、checkpoint copy、checkpoint hash/验证、cleanup/reset。无法直接归因的时间列为 `unattributed`，不凭差值伪称某个组件。第二阶段在相同开发 workload 上比较 1 与 2 lane 的整体完成 wall time、成功提交 sessions/hour、median/P90 session latency、峰值 VRAM/RAM、GPU utilization、Ollama 排队、503/timeout/OOM、状态泄漏和恢复失败。运行身份另记录开始顺序与模型热身状态。

## 前瞻性资格门

`2-lane throughput / 1-lane throughput ≥ 1.35`，且 OOM、非预期 503、无法解释的 timeout、sequence 间状态泄漏、恢复失败均为 0，才有资格提出正式并发修订。`1.35×` 是本次新增的工程判定，不是原 V58 冻结事实。任何缺失收据、不同模型配置或不能核查的并发状态使 gate 失败，不事后换样本或阈值。只有 2 lane 合格，才另行决定是否设计 4 lane 开发试验；当前没有 4 lane 的执行许可或时间承诺。

## 通过后的正式修订边界

若 gate 通过，先新增 `V58_EXECUTION_AMENDMENT_<date>.json`，固定 lane 数、完整 order block 到 lane 的分配、wave 与 slot 顺序、Ollama 配置、GPU/运行环境身份、全局预算和恢复语义。同一 block 的 N/V 保持在同一 lane、按原 slot 顺序运行；不同 block 可并行。随后重审 freeze hash、进程隔离、真实后端跨进程恢复、零重发、P0–P3、成本和时间预检。原正式串行代码和每 session 完整 Qdrant/SQLite 状态快照在此之前保持不变。若 gate 不通过，继续串行，保留约 70–100 小时的当前预算。
