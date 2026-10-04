# 全项目变更记录

这里记录跨版本的规则、入口和仓库结构变化。具体实验设计、代码和结果的变更，应同时记录在相应的 `docs/vXX/CHANGE_HISTORY.md`；V57 及以前的旧记录位于 `history/`，不在这里重写。

# 2026-09-30 武大超算 V58 源码与 GPU 申请预检

### 现状

GitHub 主分支已同步，但 V58 依赖的冻结源码仍在 Git 忽略的历史目录；超算账户说明限制远端工作在 `~/projects/srx/`，并要求先准备代码、暂不下载模型或环境。

### 实施方案

打包字节一致的 V45/V55 与设计冻结源文件和公开 benchmark Git bundle，建立离线源码恢复/回读入口与 5 分钟 GPU 源码检查作业模板；仅在允许目录验证登录、调度器关联及 `sbatch --test-only`，不提交作业或调用模型。

### 完成与未完成状态

本地全新临时目录恢复与哈希回读通过，源码包不含数据、模型、环境和凭据。超算 SSH 可登录；`a100x4` 指定项目账户后 `sbatch --test-only` 可给出调度估计，未实际申请或占用 GPU。登录节点直连 GitHub HTTPS 超时；经 Mac SSH 上传的源码 tar 哈希正确，但解包时发现共享账号 `/home` 的 1GiB 用户配额已超限。本轮部分源码、tar 和测试脚本已从允许目录清理，远端没有完整源码树；未触碰共享账号其他文件。超算模型/环境/输入未下载，GPU 运行资格尚未建立；Mac 串行 V58 状态与正式模型调用 0 均保持不变。

# 2026-09-30 V58 开发执行 profiling 资源筛查

### 现状

用户收紧并发优化方案，要求保持正式串行 runner 和完整 checkpoint 不变，先用开发数据测瓶颈和 1/2 lane 资格；目标机器随后确认为当前 Mac。

### 实施方案

在 `solutions/v58/src/profiling/` 建立独立、显式授权的开发计时入口，前瞻性记录开发 case、服务参数、1.35× gate、run 身份和零重试。开发收据保存在独立、Git 忽略的 `v58-profile-*` 目录；正式 runner 与 checkpoint 哈希保持不变。对 2 路服务配置做短 smoke，再用原串行配置做开发瓶颈短测。

### 完成与未完成状态

2 路配置的首个开发请求导致 19GB 模型占用、42% CPU offload 和memory_pressure free percentage 约 6%（非物理空闲比例），已安全终止并保留发送现场，不重试；未启动两个 worker。原串行配置的 2 个开发 ingestion 回读通过，LLM 请求约占 wall time 的 96.82%，checkpoint 约占 0.015%。总计 3 次开发请求发送、2 份响应保存；**V58 正式模型调用 0**。因资源风险未完成 30–50 个 ingestion 或 1/2 lane 吞吐对照，1.35× gate 未评估、未通过；没有正式并发 execution amendment。正式串行 `READY_FOR_FORMAL_RUN` 状态不变，详见 `docs/v58/EXECUTION_PROFILING_SCREENING_20260930.md`。

# 2026-09-30 V58 主指标前瞻性补充与离线实现

### 现状

上次 V58 审查发现主指标表示和距离未唯一指定、旧审计脚本在归档后路径失效。用户提交前瞻性补充冻结并要求开始实施；另要求将 `.env` 移回根目录。

### 实施方案

保留原冻结文件，在根目录 `study_freeze/` 单独记录 amendment 与哈希；按新版结构建立 `docs/v58/` 和 `solutions/v58/`，完成版本输入、runner、审计、raw 收据、恢复、统计及成本预检。只读核对 V55/V45、模型与 embedding 身份，使用 fake client 进行离线验证。

### 完成与未完成状态

主指标补充后的冻结审计通过；已建立 V58 源码与离线收据。最终 17/17 单元测试、13/13 子进程故障检查及 8/8 真实后端跨进程 fake-client 恢复检查通过，监管状态为 `READY_FOR_FORMAL_RUN`。`.env` 已移至根目录且权限、内容哈希不变，原归档迁移清单描述的是移动前状态。未进行真实 V58 模型调用或正式实验；0–4 correctness 依用户决定暂不判分。详见 `docs/v58/CHANGE_HISTORY.md` 与当前状态文件。

# 2026-09-30 V58 冻结方案审查

### 现状

用户提供 V58 实现与正式运行准备任务，要求先深入确认方案冻结；若发现冻结设计 P0，应停止实施。当前仓库尚无 V58 runner 或实验结果。

### 实施方案

只读核对归档批准原文、`FREEZE_MANIFEST.json`、V58 order、V55/V45 冻结依赖、数据哈希与当前状态；独立复算 36/36 覆盖与 N/V 配对；将结论写入 `docs/v58/`，不改历史冻结文件。

### 完成与未完成状态

哈希与分配机械核验通过。发现 V58 主统计中的距离及 retrieval 表示未在 V58 冻结材料中唯一绑定（P0），归档审计脚本旧路径失效（P1）。依任务停止 runner 实施和正式运行；没有真实模型调用。V58 未达到 `READY_FOR_FORMAL_RUN`。

# 2026-09-30 采用完整科研开发规范并建立当前状态入口

### 现状

仓库已在 V57 结束后重置，根目录保留研究 idea、README 和旧版开发规范；旧 `CURRENT_STATE.json` 随历史根目录归档。用户提供了更完整的科研开发规范，要求纳入项目并维护新的状态交接文件。

### 实施方案

以用户提供的完整规范为主体保留研究、审查、代码、快照、历史转移和绘图要求，补充本项目的 trial-isolation 研究边界、V55–V57 证据范围和 V58 新起点。明确 `docs/vXX/`、`solutions/vXX/{src,inputs,outputs}/`、全项目与版本两级变更记录、版本归档的 `vXX_README.md`，以及根目录 `CURRENT_STATE.json` 的维护责任。同步更新 README 与 IDEA 的当前入口。

### 完成与未完成状态

规范和新的状态文件已建立；V58 仍没有协议、runner、输入或实验结果。未修改历史原始收据、未移动历史目录，也未运行模型。旧版本的非规范目录仅作为被 Git 忽略的历史证据保留。

# 2026-09-30 在版本结构中加入共享运行时层

### 现状

目录规范已定义 `docs/vXX/` 与 `solutions/vXX/{src,inputs,outputs}/`，但结构图没有展示用户要求的根目录共享运行时层。

### 实施方案

在规范及 README 的结构图中加入 `.runtime/`，说明其存放可跨版本共用的 uv 环境、模型权重和缓存，由现有 `.gitignore` 忽略；版本清单仍须记录实际环境和模型身份，原始实验收据留在本版 `outputs/`。

### 完成与未完成状态

仅更新文档与规范校验和；尚未创建新的运行环境、模型或 V58 实验。历史运行时和实验原件未改动。

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

# 2026-10-02 13:38 V58 小时监督

### 现状

b02-s1 N 已完成，原 controller 正常进入 b02-s2 V。累计保存 564/4392 ingestion、发送 577 请求、完成 3/24 sequence，比前次增加 56 ingestion。

### 实施方案

只读核查规范/修订、真实 controller/外层监督/Ollama、原 source/执行身份、活跃 V 最新提交 checkpoint、错误/响应停止原因、预算及资源；独立完整回读新完成 b02-s1 N。

### 完成与未完成状态

新完成 N 的 191 checkpoints PASS/COMPLETE；自然调度下一条，无新 native teardown 干预。活跃 V 身份/checkpoint 通过，无新 terminal failure 或 length，GPU 活跃、swap 约 4.30GiB、磁盘余量约 332GiB，预算以内。不修复、不重启、无新增模型调用；仅对已完成 sequence 全量回读，未做中途统计。收据 SUPERVISION_20261002_1338.json。

# 2026-10-02 14:39 V58 小时监督

### 现状

修订批次 b02-s2 V 正常推进，累计保存 618/4392 ingestion、发送 632 请求、完成 3/24 sequence，比前次增加 54 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新已提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新 terminal failure 或 length；GPU 活跃，swap 约 4.54GiB、磁盘余量约 332GiB，预算以内。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 只验证已提交快照，不进行要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261002_1439.json。

# 2026-10-02 15:39 V58 小时监督

### 现状

修订批次 b02-s2 V 正常推进，累计保存 666/4392 ingestion、发送 681 请求、完成 3/24 sequence，比前次增加 48 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新已提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 4.43GiB、磁盘余量约 332GiB，预算以内。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 只验证已提交快照，不进行要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261002_1539.json。

# 2026-10-02 16:40 V58 小时监督

### 现状

修订批次 b02-s2 V 正常推进，累计保存 717/4392 ingestion、发送 733 请求、完成 3/24 sequence，比前次增加 51 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 4.27GiB、磁盘余量约 332GiB，预算以内。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 只验证已提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261002_1640.json。

# 2026-10-02 17:40 V58 小时监督

### 现状

b02-s2 V 已完成，第二 N/V order block 完成，原 controller 进入冻结 slot 的 b03-s1 V。累计保存 771/4392 ingestion、发送 788 请求、完成 4/24 sequence，比前次增加 54 ingestion。

### 实施方案

只读核查规范/修订、真实 controller/外层监督/Ollama、原 source/执行身份、活跃 V 最新提交 checkpoint、错误/响应停止原因、预算与资源；对新完成 b02-s2 V 做独立完整回读。

### 完成与未完成状态

新完成 V 的 191 checkpoints PASS/COMPLETE；父 controller 正常调度下一条，无新增退出异常修复。活跃 V 身份/checkpoint 检查通过，无新 terminal failure 或 length，GPU 活跃、swap 约 4.48GiB、磁盘余量约 332GiB，预算以内。不重启、不改参数、无新增模型调用；仅对已完成 sequence 全量回读，未做中途统计。收据 SUPERVISION_20261002_1740.json。

# 2026-10-02 18:40 V58 小时监督

### 现状

修订批次 b03-s1 V 正常推进，累计保存 823/4392 ingestion、发送 841 请求、完成 4/24 sequence，比前次增加 52 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、预算及资源。

### 完成与未完成状态

核验通过，无新 terminal failure 或 length；GPU 活跃，swap 约 4.39GiB、磁盘余量约 330GiB，预算以内。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261002_1840.json。

# 2026-10-02 19:40 V58 小时监督

### 现状

修订批次 b03-s1 V 正常推进，累计保存 872/4392 ingestion、发送 892 请求、完成 4/24 sequence，比前次增加 49 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 4.39GiB、磁盘余量约 331GiB，预算以内。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261002_1940.json。

# 2026-10-02 20:41 V58 小时监督

### 现状

b03-s1 V 已完成，原 controller 正常进入冻结 slot 的 b03-s2 N。累计保存 922/4392 ingestion、发送 943 请求、完成 5/24 sequence，比前次增加 50 ingestion。

### 实施方案

只读核查规范/修订、真实 controller/外层监督/Ollama、原 source/执行身份、活跃 N 最新提交 checkpoint、错误/响应停止原因、预算与资源；对新完成 b03-s1 V 做独立完整回读。

### 完成与未完成状态

新完成 V 的 191 checkpoints PASS/COMPLETE；父 controller 正常调度下一条，无新增退出异常修复。活跃 N 身份/checkpoint 检查通过，无新 terminal failure 或 length，GPU 活跃、swap 约 4.33GiB、磁盘余量约 331GiB，预算以内。不重启、不改参数、无新增模型调用；仅对已完成 sequence 全量回读，未做中途统计。收据 SUPERVISION_20261002_2041.json。

# 2026-10-02 21:43 V58 小时监督

### 现状

修订批次 b03-s2 N 正常推进，累计保存 978/4392 ingestion、发送 1000 请求、完成 5/24 sequence，比前次增加 56 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 4.66GiB、磁盘余量约 330GiB，预算以内。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261002_2143.json。

# 2026-10-02 22:45 V58 小时监督

### 现状

修订批次 b03-s2 N 正常推进，累计保存 1033/4392 ingestion、发送 1056 请求、完成 5/24 sequence，比前次增加 55 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 4.72GiB、磁盘余量约 330GiB，预算以内。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261002_2245.json。

# 2026-10-02 23:47 V58 小时监督

### 现状

修订批次 b03-s2 N 正常推进，累计保存 1084/4392 ingestion、发送 1108 请求、完成 5/24 sequence，比前次增加 51 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 4.79GiB、磁盘余量约 329GiB，预算以内。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261002_2347.json。

# 2026-10-03 00:48 V58 小时监督

### 现状

b03-s2 N 已完成，第三 N/V order block 完成，原 controller 正常进入冻结 slot 的 b04-s1 V。累计保存 1132/4392 ingestion、发送 1157 请求、完成 6/24 sequence，比前次增加 48 ingestion。

### 实施方案

只读核查规范/修订、真实 controller/外层监督/Ollama、原 source/执行身份、活跃 V 最新提交 checkpoint、错误/响应停止原因、预算与资源；对新完成 b03-s2 N 做独立完整回读。

### 完成与未完成状态

新完成 N 的 191 checkpoints PASS/COMPLETE；父 controller 正常调度下一条，无新增退出异常修复。活跃 V 身份/checkpoint 检查通过，无新 terminal failure 或 length，GPU 活跃、swap 约 4.77GiB、磁盘余量约 329GiB，预算以内。不重启、不改参数、无新增模型调用；仅对已完成 sequence 全量回读，未做中途统计。收据 SUPERVISION_20261003_0048.json。

# 2026-10-03 01:50 V58 小时监督

### 现状

修订批次 b04-s1 V 正常推进，累计保存 1182/4392 ingestion、发送 1208 请求、完成 6/24 sequence，比前次增加 50 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 5.00GiB、磁盘余量约 329GiB，预算以内。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261003_0150.json。

# 2026-10-03 02:52 V58 小时监督

### 现状

修订批次 b04-s1 V 正常推进，累计保存 1235/4392 ingestion、发送 1262 请求、完成 6/24 sequence，比前次增加 53 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 5.06GiB、磁盘余量约 329GiB，预算以内。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261003_0252.json。

# 2026-10-03 03:53 V58 小时监督

### 现状

b04-s1 V 已完成，原 controller 正常进入冻结 slot 的 b04-s2 N。累计保存 1283/4392 ingestion、发送 1312 请求、完成 7/24 sequence，比前次增加 48 ingestion。

### 实施方案

只读核查规范/修订、真实 controller/外层监督/Ollama、原 source/执行身份、活跃 N 最新提交 checkpoint、错误/响应停止原因、预算与资源；对新完成 b04-s1 V 做独立完整回读。

### 完成与未完成状态

新完成 V 的 191 checkpoints PASS/COMPLETE；父 controller 正常调度下一条，无新增退出异常修复。活跃 N 身份/checkpoint 检查通过，无新 terminal failure 或 length，GPU 活跃、swap 约 4.50GiB、磁盘余量约 329GiB，预算以内。不重启、不改参数、无新增模型调用；仅对已完成 sequence 全量回读，未做中途统计。收据 SUPERVISION_20261003_0353.json。

# 2026-10-03 04:53 V58 小时监督

### 现状

修订批次 b04-s2 N 正常推进，累计保存 1336/4392 ingestion、发送 1366 请求、完成 7/24 sequence，比前次增加 53 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 4.63GiB、磁盘余量约 328GiB，预算以内。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261003_0453.json。

# 2026-10-03 05:53 V58 小时监督

### 现状

修订批次 b04-s2 N 正常推进，累计保存 1387/4392 ingestion、发送 1418 请求、完成 7/24 sequence，比前次增加 51 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 4.96GiB、磁盘余量约 328GiB，预算以内。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261003_0553.json。

# 2026-10-03 06:54 V58 小时监督

### 现状

修订批次 b04-s2 N 正常推进，累计保存 1440/4392 ingestion、发送 1472 请求、完成 7/24 sequence，比前次增加 53 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 5.00GiB、磁盘余量约 328GiB，预算以内。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261003_0654.json。

# 2026-10-03 07:55 V58 小时监督

### 现状

b04-s2 N 已完成，第四 N/V order block 完成，原 controller 正常进入冻结 slot 的 b05-s1 V。累计保存 1491/4392 ingestion、发送 1524 请求、完成 8/24 sequence，比前次增加 51 ingestion。

### 实施方案

只读核查规范/修订、真实 controller/外层监督/Ollama、原 source/执行身份、活跃 V 最新提交 checkpoint、错误/响应停止原因、预算与资源；对新完成 b04-s2 N 做独立完整回读。

### 完成与未完成状态

新完成 N 的 191 checkpoints PASS/COMPLETE；父 controller 正常调度下一条，无新增退出异常修复。活跃 V 身份/checkpoint 检查通过，无新 terminal failure 或 length，GPU 活跃、swap 约 4.82GiB、磁盘余量约 328GiB，预算以内。不重启、不改参数、无新增模型调用；仅对已完成 sequence 全量回读，未做中途统计。收据 SUPERVISION_20261003_0755.json。

# 2026-10-03 08:56 V58 小时监督

### 现状

修订批次 b05-s1 V 正常推进，累计保存 1539/4392 ingestion、发送 1573 请求、完成 8/24 sequence，比前次增加 48 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 5.45GiB、磁盘余量约 328GiB，预算以内。虽然 swap 比上一采样上升，进度持续推进，没有停滞或 OOM 证据，不据单次资源读数重启。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261003_0856.json。

# 2026-10-03 09:58 V58 小时监督

### 现状

修订批次 b05-s1 V 正常推进，累计保存 1590/4392 ingestion、发送 1625 请求、完成 8/24 sequence，比前次增加 51 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 5.46GiB、磁盘余量约 327GiB，预算以内，进度持续推进，无停滞或 OOM 证据。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261003_0958.json。

# 2026-10-03 10:59 V58 小时监督

### 现状

修订批次 b05-s1 V 正常推进，累计保存 1640/4392 ingestion、发送 1676 请求、完成 8/24 sequence，比前次增加 50 ingestion。

### 实施方案

只读核查规范与执行修订、真实 controller/外层监督/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU 活跃，swap 约 5.44GiB、磁盘余量约 327GiB，预算以内，进度持续推进，无停滞或 OOM 证据。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261003_1059.json。

# 2026-10-03 用户授权安全续跑

### 现状

用户要求“继续一下”。实际已安全暂停在 b05-s2 N checkpoint 12，保存 1659/4392 ingestion、完成 9/24 sequence，先前状态文件仍为运行中快照。

### 实施方案

原 sequence 完整回读 PASS（13 checkpoints 含初始）、运行时 digest/版本匹配，无不确定请求；在 src/ops 外层保护新增显式 --resume-paused 入口及独立新事件目录，只有 PAUSED 且完整回读通过才能恢复。保留原顶层 runner/source、预算和所有模型条件，原 full 自行清除已获用户撤销的暂停请求并跳过已完成 sequence。

### 完成与未完成状态

外层保护测试 3/3 通过，包括非安全暂停和不确定回读拒绝；真实原批次恢复成功，第 13 步已发新请求（计数 1696），已提交前 12 步不重算。新外层 supervisor/caffeinate 保持运行，用户暂停仍会停止。每小时监督仍启用；原始暂停/恢复控制历史保留，无全量统计结论。恢复收据 outputs/v58-resume-20261003/launch.json，外层事件目录见 CURRENT_STATE.json。

# 2026-10-03 11:59 V58 恢复后小时监督

### 现状

用户授权恢复后，b05-s2 N 正常推进。累计保存 1687/4392 ingestion、发送 1724 请求、完成 9/24 sequence，比前次心跳增加 47 ingestion；安全恢复后新增 28 ingestion。

### 实施方案

只读核查规范/执行修订、controller 当前 PID、新外层监督/caffeinate/Ollama、原 source/执行身份、活跃 N 最新提交 checkpoint、错误/响应停止原因、预算与资源；独立完整回读已完成 b05-s1 V。

### 完成与未完成状态

已完成 V 的 191 checkpoints PASS/COMPLETE；恢复后的 N 身份/checkpoint 检查通过，无新 terminal failure 或 length。GPU/CPU 有推理活动，swap 约 5.28GiB、磁盘余量约 327GiB，预算以内，进度持续推进。无需修复或重启，无新增模型调用；用户此前暂停与本次明确恢复授权均保留，未重算已提交步骤。暂无完整统计结果。收据 SUPERVISION_20261003_1159.json。

# 2026-10-03 13:00 V58 小时监督

### 现状

修订批次 b05-s2 N 正常推进，累计保存 1734/4392 ingestion、发送 1772 请求、完成 9/24 sequence，比前次增加 47 ingestion。

### 实施方案

只读核查规范与执行修订、当前 controller PID/新外层监督/caffeinate/Ollama、原 source/执行身份、最新提交 checkpoint、错误/响应停止原因、硬预算及资源。

### 完成与未完成状态

核验通过，无新的 terminal failure 或 length；GPU/CPU 有推理活动，swap 约 5.77GiB、磁盘余量约 326GiB，预算以内，进度持续推进，无停滞或 OOM 证据。原参数继续运行，不重试、不重启、无新增模型调用；活跃 sequence 仅核验提交快照，不作要求无 pending call 的全量回读或中途统计。暂无全量结果。收据 SUPERVISION_20261003_1300.json。

# 2026-10-03 本地模型连接失败诊断

### 现状

用户询问为何运行失败。北京时间 23:34，b07-s1 step 64（D trial 2 session 15）请求已发送但没有响应收据，client RemoteProtocolError；累计保存 2257 ingestion、完成 12 sequence，发送 2307 请求。

### 实施方案

只读对照失败 raw、客户端异常、Ollama 服务日志和进程。服务日志 /api/chat 约 62s 返回 500、取消对应 task，服务随后仍可读取 /api/ps。

### 完成与未完成状态

直接原因是模型请求连接中断，不是已知 output length/schema 或 completed teardown 情况。不能据现有证据归因 OOM/内存或指定网络层；底层触发原因仍待定位。不重发原不确定请求，不修补 raw，不自动原地恢复；本次仅诊断解释，无模型调用。状态已更正 FAILED，收据 CONNECTION_FAILURE_20261003.json。

# 2026-10-03 重启前中断点审查

### 现状

用户准备重启刷新内存，要求检查中断点。正式 runner 与外层监督已退出，只有 Ollama 服务仍在线。

### 实施方案

对 b01–b06 共 12 条已完成 sequence 独立完整回读；对 terminal b07-s1 仅回读已提交 checkpoint 链并验证自动恢复门拒绝未响应的 dispatch。不删失败现场、不修补响应。按用户重启意图设置控制暂停请求与 execution_hold，监督不得自行启动模型任务，等待重启后用户明确继续。

### 完成与未完成状态

12 条完整 sequence 各 191 checkpoints PASS/COMPLETE。b07-s1 初始至 step 63 共 64 checkpoints 哈希/身份通过；step 64 已发送而无响应，自动恢复仍拒绝。2257 已提交 ingestion 保留，但不等于全批次能自动恢复或最终统计已合格。当前无正式计算，用户可以重启；重启不消除不确定请求。审查收据 PRE_REBOOT_AUDIT_20261003.json。本次无模型调用，所有旧 raw 未改。

# 2026-10-04 重启后连接失败恢复与组合批次

### 现状

用户明确授权继续并显示 HTML。旧 b07-s1 step64 无响应，terminal 保持，不允许原地重试；前12完整sequence已验收。

### 实施方案

恢复manifest前瞻性绑定24slot：旧 block1–6共12条完整成果复用，旧failed block7sequence整个排除（61 ingestion/63请求原样保留），block7–12在新 recovery-mac-20261003 从pristine重新执行。原顶层runner/source、模型、数据、schema、checkpoint、order/slot、主指标都不改；新增代码在src/ops。Direct localhost环境去代理仅为预防，根因尚未证明。原新旧scope独立，原不确定请求不重发。

### 完成与未完成状态

manifest24slot/12完整身份回读PASS，外层保护负测试及暂停测试6/6，模型/冻结与完整Mem0 store预检PASS无模型调用；新恢复controller已后台启动。新剩余预算2244请求，页面总量包含复用2244请求，监督不能把合计与剩余预算比较。页面排除旧失败61个session，选定进度从2196起。全部完成后按manifest统一原统计，不按单一batch命名猜路径；仍无最终统计结论。依据 RECOVERY_AFTER_CONNECTION_20261003.md。

恢复启动验收：新 b07-s1 第1步 checkpoint 身份与状态哈希通过，已保存至少2个新ingestion，右侧页面显示2198/4392及12/24完整sequence，暂停按钮可用。启动收据 `outputs/v58-recovery-reboot-20261003/first_checkpoint_verified.json`。

# 2026-10-04 00:39 恢复组合批次监督

### 现状

recovery-mac-20261003 在新 b07-s1 V 正常推进，选定进度 2225/4392、完整 sequence 12/24，含12复用完整成果；新恢复调用 30，页面选定总调用 2274。

### 实施方案

只读核查最新规范/恢复方案、当前 controller/caffeinate/Ollama、原 source/执行身份与 recovery manifest哈希、最新提交checkpoint、错误/响应停止原因、资源及新恢复run实际预算消耗。

### 完成与未完成状态

检查通过，无新 terminal failure/length，GPU活跃，swap约3.21GiB、磁盘余量约326GiB。预算以新run真实dispatch及保守token预留核查，不把复用2244请求计入新剩余2244预算。持续推进，原失败现场保留排除，不修复、不重启、无新增模型调用；暂无全量统计结论。收据 SUPERVISION_20261004_0039.json。

# 2026-10-04 01:39 恢复组合批次监督

### 现状

新 b07-s1 V 正常推进，选定进度 2276/4392、完整 sequence 12/24；新调用 82，选定总调用 2326，比前次新增 51 ingestion。

### 实施方案

只读核查规范/恢复方案、controller/caffeinate/Ollama、原source/执行与manifest身份、最新提交checkpoint、错误/响应停止原因、新调用真实预算和资源；额外验证原失败位置 step64 在新独立sequence已提交。

### 完成与未完成状态

身份/checkpoint通过，新step64已保存响应、通过生产路径schema并提交，无新 terminal failure/length；这不是原不确定请求重试，不能证明根因已消除。GPU单次读数0但CPU推理活动且进度增加，无停滞证据；swap约3.53GiB、磁盘余量约326GiB。新run预算以内，复用2244调用不计入剩余预算。不修复、不重启、无新增模型调用，未做中途统计。收据 SUPERVISION_20261004_0139.json。

# 2026-10-04 02:40 恢复组合批次监督

### 现状

新 b07-s1 V 正常推进，选定进度 2329/4392、完整 sequence 12/24；新调用 136，选定总调用 2380，比前次新增 53 ingestion。

### 实施方案

只读核查规范/恢复方案、controller/caffeinate/Ollama、原source/执行与manifest身份、最新提交checkpoint、错误/响应停止原因、新run真实预算消耗及资源。

### 完成与未完成状态

核验通过，无新 terminal failure/length，GPU活跃，swap约3.82GiB、磁盘余量约325GiB。新run预算以内，复用2244调用不计入剩余预算，进度持续推进；旧failed sequence保持排除。不修复、不重试、不重启、无新增模型调用；活跃sequence只核验提交快照，无中途统计。收据 SUPERVISION_20261004_0240.json。

# 2026-10-04 03:41 恢复组合批次监督

### 现状

新 b07-s1 V 完整完成，coordinator自然进入b07-s2 N；选定进度 2382/4392、完整sequence 13/24，新调用 191、选定总调用 2435，比前次新增 53 ingestion。

### 实施方案

只读核查规范/恢复方案、coordinator/caffeinate/Ollama、原source/执行及manifest身份、活跃N最新checkpoint、失败/响应、新run实际预算及资源；独立完整回读新完成V。

### 完成与未完成状态

新完成V的191 checkpoints PASS/COMPLETE，原不确定sequence保持排除，没有修补或重发旧请求。N快照/身份通过，无新terminal failure/length，GPU活跃，swap约3.53GiB、磁盘余量约325GiB，新run预算以内（复用2244调用不占剩余预算）。不修复、不重启、无新增模型调用，无中途统计。收据 SUPERVISION_20261004_0341.json。

# 2026-10-04 04:42 恢复组合批次监督

### 现状

新 b07-s2 N 正常推进，选定进度 2437/4392、完整sequence 13/24；新调用 247、选定总调用 2491，比前次新增 55 ingestion。

### 实施方案

只读核查规范/恢复方案、coordinator/caffeinate/Ollama、原source/执行和manifest身份、最新提交checkpoint、错误/响应停止原因、新run预算及资源。

### 完成与未完成状态

核验通过，无新terminal failure/length，GPU活跃，swap约3.73GiB、磁盘余量约325GiB，新run预算以内；复用2244调用不占剩余预算，旧failed sequence保留排除。不修复、不重试、不重启、无新增模型调用；只核验活跃sequence已提交快照，无中途统计。收据 SUPERVISION_20261004_0442.json。

# 2026-10-04 05:43 恢复组合批次监督

### 现状

新 b07-s2 N 正常推进，选定进度 2488/4392、完整sequence 13/24；新调用 299、选定总调用 2543，比前次新增 51 ingestion。

### 实施方案

只读核查规范/恢复方案、coordinator/caffeinate/Ollama、原source/执行和manifest身份、最新提交checkpoint、错误/响应停止原因、新run预算及资源。

### 完成与未完成状态

核验通过，无新terminal failure/length，GPU活跃，swap约3.97GiB、磁盘余量约325GiB，新run预算以内；复用2244调用不占剩余预算，旧failed sequence保留排除。不修复、不重试、不重启、无新增模型调用；只核验活跃sequence已提交快照，无中途统计。收据 SUPERVISION_20261004_0543.json。

# 2026-10-04 06:43 恢复组合批次监督

### 现状

新 b07-s2 N 正常推进，选定进度 2540/4392、完整sequence 13/24；新调用 352、选定总调用 2596，比前次新增 52 ingestion。

### 实施方案

只读核查规范/恢复方案、coordinator/caffeinate/Ollama、原source/执行和manifest身份、最新提交checkpoint、错误/响应停止原因、新run预算及资源。

### 完成与未完成状态

核验通过，无新terminal failure/length，GPU活跃，swap约4.23GiB、磁盘余量约324GiB，新run预算以内；复用2244调用不占剩余预算，旧failed sequence保留排除。不修复、不重试、不重启、无新增模型调用；只核验活跃sequence已提交快照，无中途统计。收据 SUPERVISION_20261004_0643.json。

# 2026-10-04 07:43 恢复组合批次监督

### 现状

新b07-s2 N完整完成，第七N/V block选定两条均完成，coordinator自然进入b08-s1 N；选定进度 2590/4392、完整sequence 14/24，新调用 403、选定总调用 2647，比前次新增 50 ingestion。

### 实施方案

只读核查规范/恢复方案、coordinator/caffeinate/Ollama、原source/执行和manifest身份、活跃N最新checkpoint、失败/响应、新run真实预算及资源；独立完整回读新完成N。

### 完成与未完成状态

新完成N的191 checkpoints PASS/COMPLETE；原不确定sequence保持排除，未重发旧请求。活跃N快照/身份通过，无新terminal failure/length，GPU活跃，swap约4.14GiB、磁盘余量约324GiB，新run预算以内。复用2244调用不占剩余预算。不修复、不重启、无新增模型调用，无中途统计。收据 SUPERVISION_20261004_0743.json。

# 2026-10-04 08:43 恢复组合批次监督

### 现状

新 b08-s1 N 正常推进，选定进度 2636/4392、完整sequence 14/24；新调用 450、选定总调用 2694，比前次新增 46 ingestion。

### 实施方案

只读核查规范/恢复方案、coordinator/caffeinate/Ollama、原source/执行和manifest身份、最新提交checkpoint、错误/响应停止原因、新run预算及资源。

### 完成与未完成状态

核验通过，无新terminal failure/length，GPU活跃，swap约4.27GiB、磁盘余量约324GiB，新run预算以内；复用2244调用不占剩余预算，旧failed sequence保留排除。不修复、不重试、不重启、无新增模型调用；只核验活跃sequence已提交快照，无中途统计。收据 SUPERVISION_20261004_0843.json。

# 2026-10-04 09:44 恢复组合批次监督

### 现状

新 b08-s1 N 正常推进，选定进度 2689/4392、完整sequence 14/24；新调用 504、选定总调用 2748，比前次新增 53 ingestion。

### 实施方案

只读核查规范/恢复方案、coordinator/caffeinate/Ollama、原source/执行和manifest身份、最新提交checkpoint、错误/响应停止原因、新run预算及资源。

### 完成与未完成状态

核验通过，无新terminal failure/length，GPU活跃，swap约4.44GiB、磁盘余量约324GiB，新run预算以内；复用2244调用不占剩余预算，旧failed sequence保留排除。不修复、不重试、不重启、无新增模型调用；只核验活跃sequence已提交快照，无中途统计。收据 SUPERVISION_20261004_0944.json。

# 2026-10-04 10:45 恢复组合批次监督

### 现状

新 b08-s1 N 正常推进，选定进度 2741/4392、完整sequence 14/24；新调用 557、选定总调用 2801，比前次新增 52 ingestion。

### 实施方案

只读核查规范/恢复方案、coordinator/caffeinate/Ollama、原source/执行和manifest身份、最新提交checkpoint、错误/响应停止原因、新run预算及资源。

### 完成与未完成状态

核验通过，无新terminal failure/length，GPU活跃，swap约4.72GiB、磁盘余量约322GiB，新run预算以内；复用2244调用不占剩余预算，旧failed sequence保留排除。不修复、不重试、不重启、无新增模型调用；只核验活跃sequence已提交快照，无中途统计。收据 SUPERVISION_20261004_1045.json。

# 2026-10-04 11:46 恢复组合批次监督

### 现状

新b08-s1 N完整完成，coordinator自然进入b08-s2 V；选定进度 2790/4392、完整sequence 15/24，新调用 608、选定总调用 2852，比前次新增 49 ingestion。

### 实施方案

只读核查规范/恢复方案、coordinator/caffeinate/Ollama、原source/执行及manifest身份、活跃V最新checkpoint、失败/响应、新run真实预算及资源；独立完整回读新完成N。

### 完成与未完成状态

新完成N的191 checkpoints PASS/COMPLETE；活跃V快照/身份通过，无新terminal failure/length，GPU活跃，swap约4.49GiB、磁盘余量约323GiB，新run预算以内。复用2244调用不占剩余预算，原不确定sequence仍排除，未重发旧请求。不修复、不重启、无新增模型调用，无中途统计。收据 SUPERVISION_20261004_1146.json。

# 2026-10-04 12:46 恢复组合批次监督

### 现状

新 b08-s2 V 正常推进，选定进度 2839/4392、完整sequence 15/24；新调用 658、选定总调用 2902，比前次新增 49 ingestion。

### 实施方案

只读核查规范/恢复方案、coordinator/caffeinate/Ollama、原source/执行和manifest身份、最新提交checkpoint、错误/响应停止原因、新run预算及资源。

### 完成与未完成状态

核验通过，无新terminal failure/length，GPU活跃，swap约4.71GiB、磁盘余量约322GiB，新run预算以内；复用2244调用不占剩余预算，旧failed sequence保留排除。不修复、不重试、不重启、无新增模型调用；只核验活跃sequence已提交快照，无中途统计。收据 SUPERVISION_20261004_1246.json。

# 2026-10-04 13:48 恢复组合批次监督

### 现状

新 b08-s2 V 正常推进，选定进度 2892/4392、完整sequence 15/24；新调用 712、选定总调用 2956，比前次新增 53 ingestion。

### 实施方案

只读核查规范/恢复方案、coordinator/caffeinate/Ollama、原source/执行和manifest身份、最新提交checkpoint、错误/响应停止原因、新run预算及资源。

### 完成与未完成状态

核验通过，无新terminal failure/length，GPU活跃，swap约5.01GiB、磁盘余量约322GiB，新run预算以内。负载采样升高但进度持续增加，无停滞证据，不据单次资源读数干预。复用2244调用不占剩余预算，旧failed sequence保留排除。不修复、不重试、不重启、无新增模型调用；只核验活跃sequence已提交快照，无中途统计。收据 SUPERVISION_20261004_1348.json。

# 2026-10-04 14:49 恢复组合批次监督

### 现状

新b08-s2 V完整完成，第八N/V block两条均完成，coordinator自然进入b09-s1 N；选定进度 2940/4392、完整sequence 16/24，新调用 761、选定总调用 3005，比前次新增 48 ingestion。

### 实施方案

只读核查规范/恢复方案、coordinator/caffeinate/Ollama、原source/执行及manifest身份、活跃N最新checkpoint、失败/响应、新run真实预算及资源；独立完整回读新完成V。

### 完成与未完成状态

新完成V的191 checkpoints PASS/COMPLETE；活跃N快照/身份通过，无新terminal failure/length，GPU单次读数0但CPU推理活跃且进度增加，无停滞证据，swap约4.70GiB、磁盘余量约322GiB，新run预算以内。复用2244调用不占剩余预算，原不确定sequence仍排除。不修复、不重启、无新增模型调用，无中途统计。收据 SUPERVISION_20261004_1449.json。
