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

启动验收补充：第 1 个正式 ingestion 已保存响应并提交 checkpoint，状态及身份哈希回读通过；第 2 个请求正在运行。验收收据：`solutions/v58/outputs/v58-formal-mac-20260930-launch/first_checkpoint_verified.json`。运行结果尚未完成。

# 2026-10-01 V58 正式运行失败状态核查

### 现状

用户查询现状，发现批次 formal-mac-20260930-r02 于北京时间 10 月 1 日 01:32 因模型 JSON 截断终止。

### 实施方案

只读核查 controller、原始 HTTP/响应、失败收据、进程及已完成 sequence 回读；不重发、不修补响应、不改变冻结参数。

### 完成与未完成状态

第 1 个 N sequence 全部 183 ingestion 与 4 answer 完成，191 checkpoint（含初始）回读 PASS。第 2 个 V sequence 已提交 3 ingestion；第 4 个请求 eval_count=2048、done_reason=length，JSON 未闭合，引发 Mem0 LLMError，未提交该步骤。共 186/4392 ingestion、1/24 sequence、191 模型请求；runner 已退出，Ollama 服务在线但模型已卸载。这是输出截断失败，现有证据不支持归因内存崩溃。失败操作不能自动恢复或重试；没有完整 N/V 配对和正式统计结论。需要先审查冻结输出上限和前瞻性失败处理；本次未调用模型。状态证据见 FORMAL_RUN_STATUS_20261001.json。

# 2026-10-01 输出截断修复与小时自主监督

### 现状

用户授权自行修复、验证并重跑，常规失败记录文档，无须确认；监督周期由半小时改为每小时。旧批次仍保留。

### 实施方案

保存前瞻性输出上限 8192 执行修订，同步预算、模型参数与 source 身份，显式 length 终止检测；新增已失败请求的独立开发重放与完整 store 启动检查。旧批次全部排除新统计，原输入、N/V 设计、主指标、完整 checkpoint 不变。建立当前聊天 heartbeat v58，每小时核查并自主处理常规故障，尊重用户主动暂停。

### 完成与未完成状态

开发资格重放 1 次自然结束 stop、365 输出 token、冻结 JSON schema 通过，门槛 <75% of 8192 达成；不是正式样本结果。离线 24/24、恢复 13/13、真实后端 fake-client 跨进程恢复 8/8、冻结审计 27/27 通过。暂无全量结果；具体修订、边界、监督规范与启动收据见 OUTPUT_REPAIR_AND_SUPERVISION_20261001.md。

北京时间 2026-10-01 12:36，完整 store 预检通过后正式新批次 `formal-mac-20261001-output8192` 已后台启动，首个请求已发送。启动记录：`solutions/v58/outputs/v58-formal-mac-20261001-output8192-launch/launch.json`。每小时监督 ACTIVE，常规修复仅写文档，完成或需用户介入才通知。

# 2026-10-01 13:30 V58 小时监督

### 现状

修订批次 formal-mac-20261001-output8192 正常运行，检查时已保存 46/4392 ingestion、完成 0/24 sequence、发送 47 请求；当前仍为第一条 N sequence。

### 实施方案

只读核对活跃 runner、caffeinate、Ollama、模型 digest/context、源码与执行修订身份及最新已提交 checkpoint 哈希；检查响应截断、日志、资源、磁盘与保守预算。对正在请求的 sequence 不执行要求无 pending call 的全量回读。

### 完成与未完成状态

身份与最新 checkpoint 回读通过，已保存响应无 length 停止；GPU 活跃，swap 约 4GiB，磁盘余量约 337GiB。缺少 spaCy 的警告是原依赖配置下的既有警告，没有 terminal failure。按原冻结继续运行，不修复、不重启、不调用模型。旧失败批次保持排除，无完整分析结论。详细收据：SUPERVISION_20261001_1330.json。

# 2026-10-01 14:30 V58 小时监督

### 现状

修订批次 formal-mac-20261001-output8192 正常运行，保存 98/4392 ingestion、0/24 完整 sequence、发送 101 请求；比上次监督增加 52 ingestion，第一条 N sequence 已进入第 3 trial。

### 实施方案

只读核对 runner/caffeinate/Ollama 存活、源码与执行修订、最新 checkpoint 身份及状态哈希、失败/截断收据、资源与冻结硬预算；不对 active pending 请求做全量回读。

### 完成与未完成状态

核验通过，无新 terminal failure 或 length 停止，GPU 活跃、swap 约 3.92GiB，磁盘余量约 337GiB，保守预算以内。无需修复或重启，无新增模型调用，继续运行；未获得完整配对/统计结论，旧批次仍排除。详见 SUPERVISION_20261001_1430.json。

# 2026-10-02 恢复进度页与原批次续跑

### 现状

用户要求右侧 HTML 重新显示并继续执行。实际 controller 为安全暂停，停于 checkpoint 141（137 ingestion、139 请求），不是旧状态摘要所示持续运行。所有 runner、Ollama 与页面服务都已退出；暂停发生的原控制日志保留。

### 实施方案

原 sequence 离线完整回读 PASS、142 checkpoints（含初始），模型 digest/版本与冻结身份一致；恢复原单路服务、固定缓存与遥测设置，使用原 full 命令、原预算，加 --resume-paused，不改变源码或冻结条件。后台启动与 caffeinate 记录在 outputs/v58-resume-20261002，页面服务恢复于 8773。

### 完成与未完成状态

原批次 formal-mac-20261001-output8192 已恢复，step 142 请求已发送，140 次请求计数；已完成 137 ingestion 不重算。右侧页面显示原进度并运行；每小时监督配置仍 ACTIVE。尚无全量结果。用户此次“继续开跑”明确撤销之前暂停，不自动恢复未获撤销的用户暂停。

# 2026-10-02 01:00 V58 小时监督

### 现状

原修订批次在用户授权安全恢复后正常推进，已保存 140 ingestion、发送 144 请求、完整 sequence 0/24。自 checkpoint 141 恢复后新增 3 ingestion。

### 实施方案

只读核查真实 runner/caffeinate/Ollama、模型驻留、源码/执行身份、最新已提交 checkpoint、length/terminal 失败与硬预算。

### 完成与未完成状态

核验通过，无新失败，GPU 活跃，swap 约 4.8GiB、磁盘剩余约 333GiB；没有无进度证据，不强杀或重启。原依赖缺 spaCy 的警告不新增安装。保持原参数运行，旧批次仍排除，无完整统计结果。本次无模型调用；详见 SUPERVISION_20261002_0100.json。

# 2026-10-02 02:00 V58 小时监督

### 现状

修订批次正常推进，已保存 180/4392 ingestion、发送 184 请求、完成 0/24 sequence；比前次监督增加 40 ingestion。

### 实施方案

只读检查规范、最新状态和执行修订、真实进程、source/执行身份、最新 checkpoint 哈希、响应停止原因、错误日志、预算与机器资源。

### 完成与未完成状态

检查通过，无新 terminal failure/length；GPU 活跃，swap 约 3.05GiB，磁盘剩余约 335GiB。按原修订条件继续运行，无需重启/修复，无新增模型调用。本次仅核验提交快照，未对 in-flight sequence 进行全量回读；暂无完整统计结论。收据 SUPERVISION_20261002_0200.json。

# 2026-10-02 原生退出异常修复与监督

### 现状

第一条 N sequence 于北京时间 02:04 完成全部 190 步后，native shutdown 抛出 recursive_mutex lock failed: Invalid argument，SIGABRT，父 controller 停止。心跳计划时间为 03:01，实际检查/修复时间见原始 checked_at_utc（本次约 05:33）；不能把计划时间当作实际检测时间。

### 实施方案

完整回读 N sequence：191 checkpoints PASS、COMPLETE，所有请求已提交，无不确定请求。保留原错误日志；不改已绑定的顶层正式源码/输出参数/设计，新增 src/ops/ 外层 controller 监督，仅对日志同时包含 COMPLETE、特定原生退出异常、SIGABRT 且完整回读通过的已完成 sequence 续调度。原 full 将已完成 N 跳过，向 V 前进，不重发模型请求。异常来源库尚未定位，不声称 C++ native 根因已消除；修复的是已完成工作被退出清理异常阻断的调度。

### 完成与未完成状态

辨识正/负测试 1/1 通过；首次完整回读和真实续调度通过，现已进入 b01-s2 V，第一请求发送。原 batch/model/source 身份不变、预算原值、旧批次仍排除。监督最多恢复 24 个不同已完成 sequence，不盲目循环同一失败、不恢复 incomplete/schema/length、不覆盖 raw、用户暂停立即停止。每小时核查要读取 controller 当前 PID（可随完成后恢复而改变）与外层 supervisor PID，不能把旧 PID 退出当作全体已死。暂无完整统计结论；证据 SUPERVISION_20261002_0300.json。

# 2026-10-02 05:36 V58 修复后监督

### 现状

外层完成后退出异常保护与原 full controller 均存活，批次在第一条 V 推进。已保存 186/4392 ingestion、完成 1/24 sequence、发送 191 请求，比修复收据增加 3 ingestion。

### 实施方案

只读核查最新规范与修订，controller 当前 PID、外层监督、caffeinate/Ollama、源码/执行身份、活跃 V 最新已提交 checkpoint、响应/失败收据、预算和资源；不重试或重启。

### 完成与未完成状态

检查通过，无新的 schema/length/terminal failure；GPU 活跃，swap 约 3.34GiB、磁盘余量约 335GiB，原预算以内。旧 native 错误仍保留，不能把修复后正常推进说成底层库缺陷已消除。原 N 完成成果未重算，尚无完整 N/V block 与统计结论。本次无模型调用，详见 SUPERVISION_20261002_0536.json。

# 2026-10-02 06:35 V58 小时监督

### 现状

修订批次正常运行，已保存 232/4392 ingestion、发送 238 请求、完成 1/24 sequence，比前次增加 46 ingestion；第一条 V 已进入第 2 trial。

### 实施方案

只读核对规范/执行修订、真实 controller/外层监督/Ollama、源码与执行身份、最新提交 checkpoint、响应截断/失败记录、预算及资源。额外核对旧失败位置 V step 4 在当前修订批次已成功提交且自然结束。

### 完成与未完成状态

检查通过，V step 4 已保存并通过生产路径 schema 校验，没有 length 停止；这不证明其余样本永不失败。无新 terminal failure，GPU 活跃、swap 约 3.06GiB、磁盘余量约 335GiB，预算以内。保持原参数运行，不重启、不新增模型调用；完整 N/V block 和统计尚未完成。详细收据 SUPERVISION_20261002_0635.json。

# 2026-10-02 07:36 V58 小时监督

### 现状

原修订批次正常运行，已保存 279/4392 ingestion、发送 286 请求，完成 1/24 sequence；比前次增加 47 ingestion。

### 实施方案

只读检查真实 controller/外层监督/Ollama、规范与修订、源码及执行身份、活跃 V 最新已提交 checkpoint、错误/响应停止原因、预算、GPU/swap/磁盘。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length，GPU 活跃、swap 约 3.35GiB、磁盘余量约 335GiB，预算以内。无需干预，不重试、不重启，无新增模型调用；活跃 sequence 不作要求无 pending call 的全量回读。当前尚无完整统计结论。收据 SUPERVISION_20261002_0736.json。

# 2026-10-02 08:36 V58 小时监督

### 现状

原修订批次正常推进，已保存 332/4392 ingestion、发送 340 请求、完成 1/24 sequence，比前次增加 53 ingestion。

### 实施方案

只读核查规范、执行修订与真实 controller/外层监督/Ollama、源码及执行身份、活跃 V 最新已提交 checkpoint、错误/响应停止原因、预算与资源。

### 完成与未完成状态

检查通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 3.58GiB、磁盘余量约 334GiB，预算以内。无需修复、重启或新增模型调用；不对存在 pending 请求的 sequence 执行全量回读。旧错误及旧批次仍保留，暂无完整统计结论。收据 SUPERVISION_20261002_0836.json。

# 2026-10-02 09:37 V58 小时监督

### 现状

第一 order block 的 N/V 两条 sequence 都完成，进入 b02-s1 N。累计保存 372/4392 ingestion、发送 381 请求、完成 2/24 sequence，比前次增加 40 ingestion。

### 实施方案

只读核对最新规范/修订、真实进程、原 source/执行身份、活跃 N 最新提交 checkpoint、错误/响应停止原因、预算与资源；对已完成 b01-s2 V 做独立完整回读。

### 完成与未完成状态

新完成 V 的 191 checkpoints 回读 PASS/COMPLETE；父 controller 自然调度进入下一条，没有新增退出异常修复。活跃 sequence 身份/checkpoint 检查通过，无新 terminal failure，GPU 活跃、swap 约 3.75GiB、磁盘余量约 333GiB，预算以内。不重启、不改参数、无新增模型调用；未作中途结果或统计分析，需完整设计完成后统一分析。收据 SUPERVISION_20261002_0937.json。

# 2026-10-02 10:37 V58 小时监督

### 现状

修订批次在 b02-s1 N 正常推进，累计保存 416/4392 ingestion、发送 426 请求、完成 2/24 sequence，比前次增加 44 ingestion。

### 实施方案

只读核查最新规范与执行修订、真实 controller/外层监督/Ollama、原源码和执行身份、最新已提交 checkpoint、错误/响应停止原因、预算和资源。

### 完成与未完成状态

核验通过，无新 terminal failure 或 length；GPU 活跃，swap 约 3.99GiB、磁盘余量约 333GiB，预算以内。原参数继续执行，无需重试、重启或新增模型调用；存在 pending 请求的 sequence 仅核验已提交快照。暂无完整统计结果。收据 SUPERVISION_20261002_1037.json。

# 2026-10-02 正式剩余时长估算

### 现状

用户询问剩余时间；当前保存 424/4392 ingestion，还剩 3968。

### 实施方案

从启动/安全暂停/恢复/native 退出/再恢复收据重建实际运行区间，扣除停机；约 9.12h 实际运行，约 46.5 ingestion/h，以该运行吞吐估算，不改变预算或统计规则。

### 完成与未完成状态

剩余纯运行点估计约 85h，安排余量 80–100h，总实际运行点估计约 94.5h；持续运行预计北京时间 10 月 6 日前后完成。不是统计置信区间，未来暂停/故障会顺延，case/order 与系统负载会影响速度。证据 RUNTIME_ESTIMATE_20261002.json。

# 2026-10-02 11:37 V58 小时监督

### 现状

修订批次 b02-s1 N 正常推进，累计保存 461/4392 ingestion、发送 472 请求、完成 2/24 sequence，比前次增加 45 ingestion。

### 实施方案

只读核查规范及执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新已提交 checkpoint、错误/响应停止原因、预算和资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 4.06GiB、磁盘余量约 333GiB，预算以内。原参数继续运行，无需重试、重启或新增模型调用；活跃 sequence 仅核验提交快照，不进行要求无 pending call 的全量回读。尚未完成全量统计，时长估算仍为有条件预测。收据 SUPERVISION_20261002_1137.json。

# 2026-10-02 12:37 V58 小时监督

### 现状

修订批次 b02-s1 N 正常推进，累计保存 508/4392 ingestion、发送 520 请求、完成 2/24 sequence，比前次增加 47 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新已提交 checkpoint、错误/响应停止原因、硬预算和资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 4.10GiB、磁盘余量约 333GiB，预算以内。原参数继续运行，无需修复、重试、重启或新增模型调用；对活跃请求只核验已提交快照，不作全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261002_1237.json。
