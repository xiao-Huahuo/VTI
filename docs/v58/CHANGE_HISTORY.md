# V58 变更记录

# 2026-09-30 超算源码准备与 GPU 申请预检

### 现状

用户指定武汉大学超算 GPU，并要求遵守共享账号的 `~/projects/srx/` 边界、先完成代码、暂不下载模型或环境。GitHub 当前源码 clone 缺少被忽略的冻结历史依赖。

### 实施方案

新增 15 个字节一致的冻结源文件副本、固定 benchmark 提交的 Git bundle、哈希 manifest、离线恢复入口及 Slurm `a100x4` 源码检查模板。本地全新临时项目做恢复/回读和路径安全测试；远端只做目录与 `sbatch --test-only` 检查。

### 完成与未完成状态

源码包离线验证通过，未包括凭据、数据、模型、Python 环境或正式结果。超算登录及 GPU 分区 `sbatch --test-only` 通过，但没有提交 GPU 作业。远端 GitHub HTTPS 访问超时；源码 tar 经 SSH 传到允许目录并核对哈希后，因共享账号 `/home` 1GiB 用户配额已超限而无法解包。本轮上传的 tar、部分源码和测试脚本已清理，未改动其他共享文件。完整 GPU 执行环境与 V58 正式运行仍未开始，正式模型调用为 0。

# 2026-09-30 开发执行 profiling 资源筛查

### 现状

用户允许前瞻性开发 profiling，要求正式 V58 仍串行、完整 checkpoint、不减少正式 sequence；当前 Mac 被指定为目标机器。

### 实施方案

新增独立 `src/profiling/`，冻结开发样本与 1.35× 并发门，使用单独 run_id 保存请求、checkpoint、资源与计时。正式源码、数据、N/V 分配及原始冻结文件均不修改。

### 完成与未完成状态

首个 2 路配置 smoke 在资源门终止，1 次开发请求已发送、0 份响应保存，不重试。串行配置 2/2 个开发 session 完成；总计 3 次开发请求、2 份响应，正式模型调用 0。1/2 lane 长样本对照未启动，吞吐 gate `NOT_EVALUATED_NOT_QUALIFIED`，不生成正式并发 amendment。详见[筛查报告](EXECUTION_PROFILING_SCREENING_20260930.md)。正式 `READY_FOR_FORMAL_RUN` 仅指原串行实现。

# 2026-09-30 冻结方案审查

### 现状

V58 设计文件已归档为 `DESIGN_FROZEN_EXECUTION_BLOCKED`，当前没有本版 runner、输入或输出。

### 实施方案

只读核验冻结哈希、固定 panel、order、policy 分配、统计定义和 V55 依赖；记录问题等级与实施 gate。

### 完成与未完成状态

文件哈希、12/24 设计与 36/36 覆盖通过；主要 outcome 未唯一绑定为 P0，旧审计器路径失效为 P1。未实施、未运行模型，状态为 `NOT READY FOR FORMAL RUN`。

# 2026-09-30 前瞻性主指标补充与离线 runner

### 现状

用户接受上次 P0，明确补充 V58 的 1925 维 footprint 与 Euclidean L2；要求保留旧冻结，完成重新审查和实施准备。归档的 `.env` 难以找到，用户另要求移回根目录。

### 实施方案

新增 root `study_freeze/` amendment 与哈希 manifest，复制字节一致的 V57 footprint 到本版 `src/`；建立路径固定的审计入口、版本输入、runner、raw/checkpoint、预算与精确统计；执行 fake-client、真实 Mem0/Qdrant 四 trial 和子进程死亡演练。将 `.env` 从归档目录移回根目录，核对哈希/权限且不读取内容。

### 完成与未完成状态

补充冻结审计 26/26、离线测试 17/17、恢复演练 13/13、真实后端跨进程恢复 8/8、四 trial fake 后端演练通过；N sidecar 累积，V 每次归零。Ollama、Qwen digest 与 Python 依赖只读预检匹配。逐项审查后 P0/P1 为 0，监管状态达到 `READY_FOR_FORMAL_RUN`，本轮在此停止。用户确认 0–4 correctness score 暂不判分，原始回答与参考答案保存。正式模型调用 0；正式运行未启动。`.env` 已回根目录且被 Git 忽略；旧迁移清单仍记录其历史位置，不能再把它当作当前逐文件完整性证明。

# 2026-09-30 V58 安全暂停与实时机器进度页

### 现状

已提交步骤能够恢复，但原 runner 没有日常暂停控制；用户要求随时停机和新建右侧 V58 HTML 显示机器资源。

### 实施方案

新增合作暂停请求与信号处理、批次安全续跑、本机进度服务与 CPU/GPU/统一内存/swap/磁盘/模型监控。保留完整 checkpoint 和科学冻结；以 fake client 与子进程测试暂停期间不重算，页面仅提供暂停控制。

### 完成与未完成状态

安全暂停与页面已实现。暂停在当前步骤提交后退出，强杀/断电的原失败边界仍明示；原始收据未改。正式模型调用 0，未启动正式实验。证据见 docs/v58/PAUSE_AND_MONITOR_AUDIT.md。

# 2026-09-30 V58 内存监控口径更正

用户发现空闲整机已用约 10GB。更正此前将 memory_pressure free percentage 解释为物理可用比例的错误；保留原始 profiling 收据，并说明旧 smoke 未控制后台应用。进度页改用 vm_stat 页分类显示非文件缓存占用估计、文件缓存与压缩内存；缺失采样不显示为零。监控测试 2/2 通过，现场读取 16GiB 总量、约 10.16GiB 非缓存占用、约 5.06GiB 文件缓存、swap 0。未调用模型，正式调用仍为 0。

# 2026-09-30 V58 正式 Mac 串行启动

### 现状

用户明确要求“开始跑算了,开始跑”，授权当前 Mac 正式执行。冻结检查与运行时身份匹配，保持原模型参数、完整 checkpoint、单路串行。

### 实施方案

批次 `formal-mac-20260930-r02`，24 sequences / 4392 ingestion / 96 answer，硬预算 4488 请求、147062784 input token、9191424 output token，外部 API 成本 0；使用保守 token 预留。Ollama NUM_PARALLEL=1，context=32768，Flash Attention=false，KV cache 类型未设置。Mem0 遥测关闭，FastEmbed 显式定位已验哈希缓存、离线读取。后台独立进程运行，caffeinate 在 runner 生命周期内阻止空闲睡眠（接电时阻止系统睡眠）；不能保证合盖或断电继续。

### 完成与未完成状态

首次启动缺 MEM0_TELEMETRY=false，在请求前退出；补齐后因 FastEmbed 默认缓存路径错误，在首个操作未提交且尚未发送请求时终止。旧批次 `formal-mac-20260930` 保留，0 模型请求，不恢复该 terminal 操作。完整 store 初始化及嵌入 snapshot 哈希 d43150a691d02e46b7848cb04e6db89ad74b9f1a1e00bb75e8d9f034861ff7a3 离线核验通过后启动新批次。新批次首个正式请求已发送，运行中；尚未完成实验或统计。启动与失败日志见 `solutions/v58/outputs/v58-formal-mac-20260930-launch/`，实时计数以原始收据和页面为准。运行期间不修改源码；用户可页面请求安全暂停。原 70–100h 仅为估算。
