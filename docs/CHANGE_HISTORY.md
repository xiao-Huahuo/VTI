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
