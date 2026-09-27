# 科研开发规范改写

### 现状

原《科研开发规范》强调结果与失败的可审计性，但未明确规定长时间实验启动前检查断点重建与定期快照。V45 在 Stage B 中断后，Stage A 的完整阶段收据因仅保存在内存而未落盘。

### 实施方案

以用户提供的《数学建模开发规范》为骨架，改写首要规范、科研规范、代码开发规范和绘图规范；删除数学建模竞赛专属表述，保留全部 54 个与科研可能相关的 Skill 条目，不以安装状态决定删留。将长实验前的中断恢复试验、阶段性原子快照、配置校验和旧运行保护写入快照规范。

### 完成与未完成状态

已重写根目录 `科研开发规范.md`，同步更新 README 与规范校验值。V45 已发生的中断不会因规范改写而补成完整实验结果；后续实验仍需按新规范实现并验证快照恢复。

# V46 逐会话快照与实验续跑

### 现状

V45 在 Stage B 遇到 Ollama token-repeat-limit 错误，Stage A 的内存收据随进程退出而丢失，因而没有 E2/E3 因果结果。

### 实施方案

先用探索性双会话探针筛选确定性解码参数，再冻结 V46 协议。新运行器将模型原始响应、每个成功会话的后端快照及判定收据原子化保存；恢复时严格校验运行身份、快照哈希和连续编号。每个阶段结果在进入下一阶段前单独落盘，错误尝试保留现场且不自动重试。

### 完成与未完成状态

`repeat_penalty=1.1` 探针的前两会话成功。离线快照演练和真实中断续跑演练均通过：`v46-20260924-01` 的 clean_a 第 1 会话快照未改变，恢复进程从第 2 会话继续。V46 Stage A 正在运行；完整因果结果仍未产生。
另提供本机实时进度面板和独立续跑检查入口；面板从不可覆盖快照读取会话数，续跑入口在启动前校验 Ollama 服务版本、模型 digest 与检查点哈希。

# V46 Stage A 输出格式故障归档

### 现状

V46 完成真实中断续跑验证后，在 clean_a 第 13 会话遇到模型输出结构错误。前 12 个会话已保存快照，第 13 个失败尝试及原始响应仍在本机。

### 实施方案

读取 Mem0 堆栈和失败响应的结构类型，确认 `memory` 列表混入字符串，依据冻结停止规则停止；保存六字段失败记录，更新项目状态，不对 V46 输出做事后修补或自动重试。

### 完成与未完成状态

已归档 `v46/results/V46_EXECUTION_INCIDENT.json`。V46 Stage A 没有完整判定，Stage B 未启动，E2/E3 仍未识别。下一次因果实验需要另行冻结能约束输出结构或采用分布式估计的方案。

# V47 提取结构约束与独立续跑 pilot

### 现状

V46 的第 13 会话模型响应违反 Mem0 提取结果结构，导致 Stage A 停止；前 12 会话快照可用于故障诊断，不可直接作为另一配置的 clean-clean 证据。

### 实施方案

依据 Mem0 提取字段和 Ollama 的 JSON Schema 接口写结构约束及本地校验。先在 V46 失败检查点做探索性两会话探针；通过后冻结 V47 协议、模型与代码哈希，从独立运行目录重做清理对照，并保留逐会话原始输出、快照和严格运行身份。启动全量回放前实际暂停并恢复一次。

### 完成与未完成状态

schema 探针通过会话 13、14；单元检查和冻结校验通过。`v47-20260924-01` 的真实中断续跑演练通过，第 1 会话快照哈希不变。当前 Stage A 运行中；尚无 clean-clean 或因果判定。

# V47 Stage A 校准通过

### 现状

V47 两条 verified-clean 回放臂均完成 52 个会话，并在进入 Stage B 前保存了不可覆盖的阶段结果。

### 实施方案

依冻结规则核对首个提取 prompt、最终记忆、Top-10 检索顺序和回答哈希，并检查质量下限与检索完整性。

### 完成与未完成状态

`PIPELINE_NULL_CONTROL_PASS` 已保存于 `v47/runs/v47-20260924-01/stages/stage_a.json`；两臂均为 319 条最终记忆、10 条检索，四项相等。Stage B 原生 reset 臂正在运行，尚不能宣称 E2/E3。

# V47 单案例结果与独立审计

### 现状

V47 已完成四条 52 会话臂，Stage A 收据持久化并通过；Stage B 的配对比较及最终判定已保存。

### 实施方案

独立读取冻结结果与阶段收据，逐一校验全部检查点、协议和代码/数据哈希、reset 后端收据、质量下限，并重新计算 E2/E3 判定。另对两条原始回答作与参考答案的事后阅读，明确文本差异与任务评分的界限。

### 完成与未完成状态

258/258 项独立检查通过。V47 冻结判定为 `PROMISING_CAUSAL_E2_E3`：最终记忆 350 对 319，Top-10 有 4 条文本重合，回答哈希不同。两条回答都只说至少 5 天，参考答案为 8 天；E4 未测量。下一步是单独冻结三案例扩展及语义/评分分析，不能把一个案例推广为普遍评测缺陷。
运行记录另核算了 222 次本地模型调用、2,357,260 个输入 token、85,680 个输出 token 和 220 个检查点，写入 `v47/results/V47_RUN_RECORD.json`。

# C33/V47 网页版交接打包

### 现状

项目根目录包含历史资料、本地实验检查点和可重建的第三方运行环境，直接压缩整目录会混入虚拟环境、缓存和模型无关文件，不适合交给网页版审阅。

### 实施方案

依据显式文件清单制作网页版精简交接包及完整检查点审计包。保留 V42–V47 协议、代码、结果、历史研究记录、固定 benchmark 源码和必要运行收据；排除虚拟环境、缓存、模型权重与环境文件。包内附 `START_HERE.md`、逐文件 SHA256 清单与元数据；输出后逐文件核对 ZIP CRC 和哈希，并扫描常见密钥模式。

### 完成与未完成状态

`exports/C33_V47_WEB_HANDOFF_20260924.zip` 与 `exports/C33_V47_FULL_AUDIT_20260924.zip` 已生成，另有可单独上传的 `exports/C33_V47_START_HERE.md`。精简包为网页阅读优先，完整包含 V47 的全部检查点链。两包内容一致性及常见密钥模式扫描通过。网页版对 ZIP 的实际解析能力和账户上传上限仍需在用户界面验证。

# V48 三案例扩展应用与续跑演练

### 现状

V47 已有一例本地配置的受控 E2 与回答文本 E3；用户提供 V48 增量包，要求继续实验并自行处理中断。

### 实施方案

先核验增量 ZIP 与冻结清单，再应用到新 `v48/` 目录。运行前修正阶段性续跑、零残留收据、E1 seed 数量及质量下限、停止决策和 E4 输入保护，并记录更正及新旧校验清单。通过离线测试后，实际在 rank-2 clean_ref 第 1 会话暂停并同 run_id 恢复，校验快照未变化。监督器仅对无科学错误的进程中断自动续跑。

### 完成与未完成状态

`v48-20260924-01` 的真实暂停/恢复演练通过，rank 2 正在运行；V48 扩展判定和 E4 官方评分尚未产生。原 V48 增量包未覆盖 V47 结果。

# V48 三案例实时 HTML 面板

### 现状

V48 是长时间的三案例、每例最多三臂回放，用户需要在右侧直观看到已落盘进度与中断状态。

### 实施方案

添加仅监听本机 `127.0.0.1:8768` 的只读 HTML 面板。每 5 秒读取三案例检查点、阶段判定、监督器状态与 Ollama 模型加载信息；进度只统计已保存的成功会话。

### 完成与未完成状态

面板已在右侧打开，并验证 Rank 2 clean_ref、Rank 3/4 等待及监督器 RUNNING 状态正常显示。V48 科学结果仍由冻结运行器产生，面板不修改任何实验状态。

# V48 Rank 2 阶段结果

### 现状

三案例扩展的首例 `58470ed2` 已完成三条 50 会话臂，后续 Rank 3 已启动。

### 实施方案

读取已落盘的 Stage A/Stage B 判定与答案原文，核对 clean-clean 一致性、reset 后状态及答案文本与标准答案的差别，不把哈希差异解释成评分差异。

### 完成与未完成状态

Rank 2 的 clean-clean 对照通过，原生 reset 对清理臂产生 E2 与回答文本 E3 差异；记忆 Jaccard `0.02586207`，Top-10 检索 Jaccard `0.05263158`。两条回答都遗漏标准答案的核心句。Rank 3/4 尚未完成，E4 官方评分尚未执行。

# V48 Rank 3 阶段结果

### 现状

`1a8a66a6` 已完成三条 51 会话臂，Rank 4 已启动。

### 实施方案

核对 clean-clean、E1 收据和下游哈希差异，并事后阅读两条原始答案与参考答案；正式 E4 仍依冻结方案等待完整扩展结束后的官方评判。

### 完成与未完成状态

Rank 3 clean-clean 完全一致，原生 reset 对清理臂产生 E2 和回答文本 E3；记忆 Jaccard `0.03963964`，Top-10 检索无共同文本。原生臂回答 2，清理臂回答 1，参考为 2；这只是人工语义观察，官方评分 E4 尚未测量。

# V48 三案例完成与 E4 资源失败

### 现状

V48 三案例的九条完整回放臂已完成，监督器生成了全部回答不同案例的 E4 官方评判输入。

### 实施方案

独立核验冻结身份、450 个检查点、三个 clean-clean 控制、reset 收据及 E2/E3 判定，得到 111/111 通过。另阅读三个问答对的原始答案并记录事后语义观察。按预先规定尝试官方 GPT-4o judge：先对 native 三题各调用一次，失败后立即停止，保留失败指标和六字段资源失败记录，未调用 clean 臂。

### 完成与未完成状态

三例均显示本地配置的 E2 和回答文本 E3；V48 聚合决策为 `THREE_CASE_EXTENSION_COMPLETE_WITH_CAUSAL_E2`。rank 3 人工阅读显示原生臂答 2、清理臂答 1、参考为 2；另外两题两臂均未给出参考答案。官方 judge 返回三次 HTTP 429 `credit_balance_exhausted`，零条判分；E4 仍未测量。全部结构化结果、审计、调用量和失败资产已保留。若 API 余额恢复，使用相同输入和模型另记新判分尝试，不覆盖旧失败记录。

# 移除 OpenAI API Key 与调整下一研究门槛

### 现状

项目根目录 `.env` 仍配置 `OPENAI_API_KEY`，但相应 Platform 账户从未充值；V48 的官方判分尝试已因余额耗尽停止。此前全项目 ZIP 可能保留修改前的密钥。

### 实施方案

原子化删除 `.env` 中的 OpenAI key 赋值，保留其他配置。重建位于 Science 目录之外的整项目 ZIP，并验证新包中不再有该赋值或旧 key 的精确字节。将下一研究任务调整为无需 OpenAI API 的 MemArena × Mem0 第二集成最小 E1 门；继续保持 E4 未测量。

### 完成与未完成状态

`.env` 的 OpenAI key 赋值已删除；新的整项目 ZIP 验证不含旧 key。`docs/NEXT_GATE_MEMARENA_PLAN.md` 为计划而非冻结实验。若旧 ZIP 已被上传或复制，修改本地文件无法撤回其中的旧凭据，仍须在 Platform 端吊销。MemArena 执行和 E4 官方判分均未开始或完成。
# V49 无 OpenAI API 的 E4 补充判分

### 现状

V48 三案例 E2 与回答文本 E3 已完成，但 GPT-4o 官方判分因账户余额不足没有成功调用。用户明确要求彻底去除 GPT API 依赖，改用数值规则与 DeepSeek，对已保存答案进行配对正确性判分。

### 实施方案

将评分变更记录为答案生成后的 V49 补充终点，不改写 V48 冻结协议或失败收据。先冻结协议、代码、官方 LongMemEval rubric 与输入哈希；实际做一次模拟中断续跑演练。原文相同的答案跳过，直接计数题按同一规则判，未解决的题对两臂分别使用 `deepseek-flash`、非思考模式、温度零、每臂三票。逐次原子保存原始请求和响应；独立回读审计。DeepSeek 模型 ID 是可能漂移的别名，结果不得称为官方 GPT-4o 分数。

### 完成与未完成状态

V49 运行 `v49-e4-20260925-01` 已完成。六次 DeepSeek 调用全部判 Borges 题两臂错误，三票完全一致；杂志订阅题由规则判原生臂正确、清理臂错误；健康设备题两臂均错误。三例配对结局为原生臂较好一例、两臂均错两例。独立审计 10/10 通过，原始收据和结果位于 `v49_e4/runs/v49-e4-20260925-01/`。原版 GPT-4o 终点仍未测量，跨集成复现和正式实验仍未开始；本次规则在看到答案后制定，论文须如实写成事后评分修订。

# V50–V51 MemArena 第二集成最小验证

### 现状

Redis × Mem0 已有四个选定案例的受控 E2/回答文本 E3；缺少第二真实集成的运行证据。MemArena 固定源码和 Mem0 2.0.11 的历史脚本缺失，默认自托管构造函数要求 OpenAI API，与用户当前硬约束冲突。

### 实施方案

核对固定 Git 提交并在独立环境重建 E1 探针。通过适配器支持的 `client=` 注入保留原生 `reset` 调用，用合成消息与本地捕获后端只测状态残留和下一次 prompt 消费；冻结源码、协议和代码哈希，保存逐阶段收据。E1 通过后用固定 Day-3 样本的首个真实 LongMemEval 会话，以本地 Qwen 和冻结 JSON Schema 做一次模型/输出失败点探针。

### 完成与未完成状态

V50 原生 reset 把向量 1→0、消息保持 1→1；旧消息进入下一次提取 prompt，清理对照没有，独立审计 11/11。V51 首个真实会话完成有效提取，共 6 条记忆，独立审计 9/9。两次均无 OpenAI API 调用。V50 采用合成消息与本地后端仪表化，V51 只运行一会话且嵌入为确定性仪表化；因此 MemArena 的 E2/E3/E4 配对效应、总体发生率与正式实验仍未完成。下一步另冻带 clean-clean 对照及逐会话检查点的一例 pilot。

# V52 MemArena 一例配对 pilot 的零效应校准失败

### 现状

V50 的固定 MemArena × Mem0 路径显示 E1 状态残留与 prompt 消费，V51 真实首会话通过本地 Qwen/schema 探针；仍缺少第二集成的受控下游效应。

### 实施方案

在首个固定抽样案例上冻结先前会话种子、独立清理臂两次重放、原生/清理配对和精确零效应停止规则。使用真实 FastEmbed、SQLite、Qdrant、固定本地 Qwen；每会话以独立状态快照和原始模型响应落盘。实际在清理臂第 1 会话后暂停、记录检查点哈希、按同一 run_id 续跑并核验未改写。

### 完成与未完成状态

两条清理臂均完成 8/8 会话，暂停/续跑检查点字节哈希不变；无模型或 schema 错误。但第 1 会话请求与 prompt 相同，原始 Qwen 输出已不同。最终记忆 54 对 59、记忆文本哈希 Jaccard `0.18947`、Top-5 检索重合为零；答案文本相同。Stage A 清理对照失败，按冻结规则没有启动原生臂。独立审计 10/10。当前配置不能支持 MemArena E2/E3 因果结论；后续须另冻确定性后端或有充分重复对照的分布式端点，不能事后放宽校准阈值。

# 历史 V 版本目录集中归档

### 现状

根目录并列放置 V42–V52 多轮版本，V47/V48 的逐会话状态占用最大，查找当前状态困难；用户要求把历史版本放入 `history/`，并写入科研开发规范。

### 实施方案

把已结束的 V42–V52 与旧 `Science_V45_patch` 移入 `history/`，根目录不再并列放历史 V 目录。移动前后对每个文件计算内容哈希并记录目录汇总，不编辑归档内的冻结协议、代码、结果或检查点。更新当前 README、状态、交接及已知缺口的路径；重启历史只读进度页。开发规范增加历史版本归档与完整性核验要求。

### 完成与未完成状态

12 个目录、9,544 个文件移动前后校验一致，记录于 `history/RELOCATION_MANIFEST.json`。本机 8765–8768 进度页重新启动并返回 HTTP 200。此举仅整理目录，不释放磁盘空间。部分冻结旧脚本与 `ops/` 中旧工具仍假定原根目录路径，若需重跑，应在独立副本恢复布局并核验身份；本次没有改写其冻结内容。

# 非版本历史资料继续归档

### 现状

版本目录迁入 `history/` 后，根目录仍有旧 ZIP、V40 快照、早期报告、旧辅助脚本与 V45–V48 诊断文件。运行依赖 `third_party/` 与 `.runtime/` 仍供后续实验使用。

### 实施方案

按用途将 `exports/`、`sandbox_snapshot/`、`reports/`、`ops/`、`.local/` 和七个 V40 迁出记录归档到 `history/`，保留原始文件字节。对每项移动前后计算内容哈希，更新当前入口、状态与开发规范；保留 Python 环境、嵌入模型缓存和固定源码的现用路径。

### 完成与未完成状态

共移动 12 项、939 个文件，约 104 MB 原始文件内容；移动前后校验一致，见 `history/NONVERSION_RELOCATION_MANIFEST.json`。项目总占用未减少。`third_party/` 约 350 MB、`.runtime/` 约 305 MB 是可复现运行所需依赖与缓存，未移动或删除。历史脚本仍可能依赖旧路径，运行前需恢复布局或重新审计；8765–8768 只读看板不依赖本次移动的目录，仍保持可访问。

# 当前科研证据精简交接包

### 现状

用户需要把必要结果和当前相关文件发给网页版继续审查，而历史目录约 1.5 GB，不适合整体上传。

### 实施方案

显式选择当前状态文档、V47/V48 受控结果与审计、V49 E4 事后判分、V50/V51 机制与真实首会话探针、V52 clean-clean 校准失败证据，以及少量相关代码。生成中文 `START_HERE.md`、逐文件 SHA-256 清单、ZIP 校验和外部摘要。排除密钥文件、完整检查点、虚拟环境、模型权重、原始 LongMemEval 数据集和 V52 原始会话 prompt；对本机配置的密钥字节进行泄漏扫描。

### 完成与未完成状态

当前包位于 `exports/Science_C33_CURRENT_HANDOFF_20260925.zip`，由 `ops/package_current_handoff.py` 可重建。ZIP 内有明确的证据边界和给网页版的审查问题；未替代本地全量运行资产，也没有产生新的科学结论。

# V53/V54 增量门槛与 V54b 校准修订

### 现状

V52 的两条清理臂在首个相同 Qwen 请求上产生不同输出，原生臂未启动。用户提供 V53/V54 增量包，要求继续依科研开发规范执行。当前工作区已有历史目录迁移改动，未覆盖或回退。

### 实施方案

先验证 ZIP CRC 与原始逐文件 SHA-256，再核对 V52 原始首请求、固定源码、数据集及模型摘要。执行前修正 V53 重复收据恢复和冷加载失败处理、V54 检查点树哈希恢复校验，并将改动哈希记录于预执行清单。V53 通过才启动 V54。V54 按其原代码停止后，对差异做只读法证回查；另冻 V54b 新协议和新 run ID，明确以 scoped message 内容哈希多重集比较，保留逐次请求/响应及下一 prompt 的精确比对，重新运行而不改判 V54。完成后独立回读检查点、门槛、终点和先后顺序，并归档已结束版本，逐文件哈希核验。

### 完成与未完成状态

V53 `gpu_cold` 三次完整输出 SHA-256 一致，CPU 候选未运行。原 V54 在第 1 对会话按有序消息哈希比较失败，原生臂未启动；消息内容哈希多重集实际相同，顺序差来自 SQLite 插入时间。V54b 八对清理会话和最终检索/答案校准通过；原生 reset 保留 10 条消息、零向量，首 prompt 变化。最终清理/原生记忆数 57/49，Top-5 重合零，E2 阳性；答案文本相同，E3 文本阴性。E4 与正式实验未执行。独立回读审计 50/50；V53/V54/V54b 版本目录归档前后内容哈希一致，见 `history/V53_V54_RELOCATION_MANIFEST.json`。该结果只是一例选定案例和一个本地冷加载后端；不能估计发生率或官方分数。V54b 执行前验证了检查点哈希与合成篡改检测，但未做真实进程暂停/续跑演练；本次运行没有中断，所有已完成分支检查点在事后通过树哈希核验。未来多案例运行须在全量前补做真实中断续跑。

# V55 正式实验准备包审查与预执行修订

### 现状

用户提供 V55 formal-prep 增量包；此前 V54b 仅有一例 MemArena 校准 E2 pilot，正式实验尚未开始。包内提出 Redis×Mem0 12 例正式样本 ranks 5–16，但 V42 已执行 ranks 1–12，原“未参与协议开发的新 case”描述不成立。

### 实施方案

校验 ZIP CRC 与逐文件 SHA-256，保留原包 cohort、协议和运行器。使用固定 500-row LongMemEval 数据集与未改变的 V34 SHA256 排序，在任何 V55 正式结果前将主样本修订为 ranks 13–24，并逐项核对 ID、题型、会话数和哈希。对照成功的 V48 运行器恢复 clean reset 收据、E1 seed 计数、native 质量门和 Stage A/B 恢复；加入每例真实首提取三次探针、完整模型摘要与运行时版本校验，修改聚合器拒绝试点混入或不完整 12 例，并实现预先统一的 no-OpenAI DeepSeek E4 三票评分器。用隔离环境做离线测试、运行时预检及历史 rank 1 的真实 SIGTERM/同 ID 续跑演练。

### 完成与未完成状态

原包清单校验通过。修订后 ranks 13–24 与固定数据集一致且不与 V42 ranks 1–12 重叠；Redis/Mem0/Ollama/FastEmbed/Qwen/数据哈希预检通过。最终运行器哈希的真实续跑演练通过：完成检查点未重算、字节哈希不变，部分尝试未误判完成，身份漂移被拒绝。一次早期干跑因清单生成误用系统 Python 而中断，失败现场保留；后续均使用隔离环境及新 run ID。E4 评分器仅通过无 API 的输入绑定测试，没有正式答案或在线判分。**V55 正式 ranks 13–24 未运行，正式结果为零。**尚须解决 generation/schema 错误在协议中的单例终止记录与运行器整批停止之间的差异，并在修改后重冻和复做真实续跑门槛。

后续完成：将 generation/schema 错误记为预选案例的终止无效结果，不重试不替换；Stage A 后缺失的 E2/E3 不计为阴性。12 例模拟错误核算通过。重新冻结最终运行器及协议哈希后，历史 rank 1 上再次通过真实 SIGTERM/同 ID 续跑，收据见 `v55_formal/results/FINAL_CODE_RESUME_DRILL.json`。V55 现为预执行就绪、正式 12 例仍未启动。

# V55 正式实验启动

### 现状

V55 held-out ranks 13–24 预执行门槛与最终运行器真实续跑演练通过，正式案例结果仍为零。用户提供启动增量包并明确要求继续执行。

### 实施方案

核验启动 ZIP 内 CRC 和 7 个文件的 SHA-256；核对 V45 engine 与本地冻结文件字节一致，不覆盖原文件。仅安装 launcher、guard 和进度查看工具，不改 11 个冻结科研文件。以隔离的 `.runtime/v55-venv` Python 置于 `PATH` 前端，启动 Ollama 与固定 run ID `v55-formal-20260925-01`，运行前再次核验数据集、cohort 和恢复收据。正式运行遵守逐例 Stage A 硬门与预定全局停止规则。

### 完成与未完成状态

启动包与科学文件哈希校验通过，正式运行已进入 rank 13；目前尚无正式案例终止收据或聚合结果。运行日志在 `.runtime/v55_formal_launch.log`，不可覆盖检查点与身份收据在 `v55_formal/runs/v55-formal-20260925-01/`。E4 尚未调用。此记录只证明启动，不预告任何正式结果。

# V55 正式实验只读 HTML 进度页

### 现状

V55 正式运行耗时较长，已有 JSON 状态工具，但用户需要可直接查看的 HTML。

### 实施方案

在 `v55_formal/ops/` 增加单页 HTML 与只绑定本机 `127.0.0.1:8769` 的只读服务。服务按冻结 cohort 读取状态、探针、Stage A/B 和不可覆盖检查点，只返回案例 ID、阶段、计数及判定，不暴露原始 prompt、答案或密钥。页面每 15 秒刷新，桌面和窄屏均可读。

### 完成与未完成状态

HTML、本机服务和 `/api/status` 已启动；根页面、健康检查与 12 例 JSON 均返回 HTTP 200，浏览器检查了窄屏摘要和案例列表。页面目前显示 rank 13 运行中且正式结果未生成。该工具只显示既有收据，不改变 V55 冻结科研代码或实验判定。

# 保存研究 idea 原文并建立规范入口

### 现状

用户提供完整 idea 文本，要求保存于项目根目录并在《科研开发规范》中注明位置。原文含成文时的研究阶段描述，当前 V55 实验状态仍应以运行收据和权威状态文件为准。

### 实施方案

将附件按原始字节复制为根目录 `IDEA.md`，不改写其主张或把其中叙述当执行指令。于 `科研开发规范.md` 增加 idea 入口和状态证据优先级说明，同步更新 README、规范 SHA-256 校验文件与当前精简交接包文件清单。

### 完成与未完成状态

`IDEA.md` 已与源附件逐字节哈希一致；规范和 README 均可定位该文件。此举仅保存研究想法及入口，不改变 V55 冻结协议、正在运行的正式实验或既有结论。

# V55 rank 13 首例正式终止收据

### 现状

固定正式 run `v55-formal-20260925-01` 已从 rank 13 进入 rank 14。rank 13 是 12 个预选案例中的首个终止案例；尚无全体聚合或 E4。

### 实施方案

独立回读 rank 13 的探针、Stage A/B、四条分支最终检查点、E1 reset 计数、质量门及端点哈希；不重跑模型、不修改冻结代码或结果。中期审计单独写入 `v55_formal/results/RANK13_INTERIM_READBACK_AUDIT.json`，并在当前状态中标明单例边界。

### 完成与未完成状态

中期回读 12/12 通过。Stage A 完全通过；seed 与 native reset 后 scoped message 均为 10，clean cleanup 为 0；clean/native 最终记忆 283/292、记忆 Jaccard `0.017699115`、Top-10 检索 Jaccard `0`，答案文本哈希不同。冻结决策为该例 `CAUSAL_E2_E3_TEXT_POSITIVE`。这是首例的局部结果，不能推断 12 例比例或答案正确性；rank 14 仍在运行，E4 未调用。

# V55 rank 14 模型断连与冻结规则裁定

### 现状

rank 14 的探针与 Stage A 已通过，native 第 11 会话完成检查点；第 12 会话 Ollama 未返回完整响应，Mem0 抛出 `LLMError`。冻结运行器只捕获自身的 `CaseGenerationOrSchemaError`，故整批提前退出，没有写单例终止收据。

### 实施方案

保留原始错误收据、部分尝试和既有检查点，不重试 native 第 12 会话，不修改 11 个冻结科研文件。独立校验运行身份、清理臂、Stage A、native 最后检查点、失败单元及全局错误；将原冻结协议的单例生成失败规则显式人工应用为 rank 14 无效终止收据。先验证冻结 runner 在同一 run ID 下会跳过终止案例，再继续 rank 15。

### 完成与未完成状态

失败回读 12/12 通过。rank 14 记为 `EVALUATION_INVALID_GENERATION_OR_SCHEMA`；Stage A 有效，但 E2/E3 是缺失而非阴性，E4 不测；无模型重试或样本替换。人工裁定与异常包装原因见 `v55_formal/results/RANK14_TERMINAL_ADJUDICATION.md`。同一冻结 run ID 的 rank 15 已启动，正式 12 例聚合尚不可得。

# V55 同类失败自动接续监督器

### 现状

rank 14 曾因 Mem0 包装的 `LLMError` 绕过冻结 runner 的窄异常捕获而整批停下，需要人工按冻结规则记无效再用同一 run ID 继续。用户要求后续同类问题自动接上，避免长时间中断。

### 实施方案

在 `v55_formal/ops/` 新增独立监督器，不修改 11 个冻结科研文件。监督器每 15 秒观察同一 run ID，先确认无在跑的实验进程，再核验文件哈希、身份、最新检查点、案例与全局错误收据。仅对 Mem0 `LLMError` 包装的 Ollama 生成或 memory schema 错误按预定不重试规则写审计与不可覆盖的案例无效终止收据，再继续下一预选案例；无科研错误的进程中断从验证后的检查点恢复。其他错误、冲突收据、哈希漂移或重复进程均停止复核。代码哈希在启用前冻结；合成测试覆盖同类错误、普通中断与非模型错误拒绝。

### 完成与未完成状态

监督器合成检查通过并已挂接正式 run，状态为 `WATCHING/NO_DUPLICATE_PROCESS`；rank 15 原有 runner 正常运行，未启动第二份实验。科研文件 11/11 哈希一致。此机制不重试已失败的会话，不改变 rank 14 的手工裁定，也不自动执行 E4；若出现未识别异常仍需人工诊断。

# V55 rank 15 中期结果回读

### 现状

固定 run 已从 rank 15 进入 rank 16，rank 15 是第三个预选案例终止收据。正式 12 例聚合与 E4 均未完成。

### 实施方案

独立回读 rank 15 的三次首提取探针、Stage A、E1 reset 计数、三条完整 53 会话轨迹的最终检查点、质量门及 E2/E3 哈希。审计保存为 `v55_formal/results/RANK15_INTERIM_READBACK_AUDIT.json`，不重跑模型、不修改冻结科研文件。

### 完成与未完成状态

回读 11/11 通过。rank 15 Stage A 与 E1 通过；clean/native 记忆数 325/331、记忆 Jaccard `0.0348101266`、检索 Jaccard `0`，E2 阳性。两臂最终答案文本相同，E3 文本阴性；E4 未触发。仅为单例中期结论，不能当作 12 例比例。rank 16 正在运行。

# V55 rank 16 clean-clean 校准失败

### 现状

固定正式 run 从 rank 16 进入 rank 17。rank 16 是第四个预选案例终止收据，尚未形成 12 例聚合。

### 实施方案

独立回读三次首提取探针、两条完整 44 会话 clean 臂、Stage A 各项检查和 native 未启动事实；不放宽答案文本精确一致门槛，不重跑或替换案例。审计写入 `v55_formal/results/RANK16_CALIBRATION_READBACK_AUDIT.json`。

### 完成与未完成状态

回读 12/12 通过。探针、清理 reset、首提取 prompt、最终记忆、ordered Top-10 检索和质量门均通过；两条 clean 臂最终答案文本哈希不同，唯一失败项为 `answer_text`。按冻结规则 rank 16 标为校准无效，native 没有启动，E2/E3 不可评估，不计为阴性。rank 17 正在运行。

# V55 rank 17 中期结果回读

### 现状

固定正式 run 已从 rank 17 进入 rank 18；rank 17 是第五个预选案例终止收据。正式 12 例聚合与 E4 仍未完成。

### 实施方案

独立回读三次首提取探针、Stage A、E1 reset 计数、三条完整 45 会话轨迹的最终检查点、质量门和 E2/E3 哈希；将结果写入 `v55_formal/results/RANK17_INTERIM_READBACK_AUDIT.json`。不重跑模型或修改冻结科研文件。

### 完成与未完成状态

回读 12/12 通过。Stage A 与 E1 均通过；清理/原生记忆数 282/326、记忆 Jaccard `0.0305084746`、检索 Jaccard `0`，E2 阳性；答案文本不同，E3 文本阳性。仅为单例中期结果，不能据此计算正式 12 例比例或正确性效应。rank 18 正在运行。

# V55 rank 18 中期结果回读

### 现状

固定正式 run 已从 rank 18 进入 rank 19；rank 18 是第六个预选案例终止收据。正式 12 例聚合与 E4 仍未完成。

### 实施方案

独立回读三次首提取探针、Stage A、E1 reset 计数、三条完整 48 会话轨迹的最终检查点、质量门和 E2/E3 哈希；审计保存于 `v55_formal/results/RANK18_INTERIM_READBACK_AUDIT.json`，不重跑模型或修改冻结科研文件。

### 完成与未完成状态

回读 12/12 通过。Stage A 与 E1 均通过；清理/原生记忆数 320/331、记忆 Jaccard `0.0203761755`、检索 Jaccard `0`，E2 阳性；答案文本不同，E3 文本阳性。仅为单例中期结果，不能据此计算正式 12 例比例或正确性效应。rank 19 正在运行。

# V55 rank 19 中期结果回读

### 现状

固定正式 run 已从 rank 19 进入 rank 20；rank 19 是第七个预选案例终止收据。正式 12 例聚合与 E4 仍未完成。

### 实施方案

独立回读三次首提取探针、Stage A、E1 reset 计数、三条完整 52 会话轨迹的最终检查点、质量门，并重算记忆与检索 Jaccard。审计保存于 `v55_formal/results/RANK19_INTERIM_READBACK_AUDIT.json`，不重跑模型或修改冻结科研文件。

### 完成与未完成状态

回读 12/12 通过。Stage A 与 E1 均通过；清理/原生记忆数 336/298、记忆 Jaccard `0.0411861614`、检索 Jaccard `0.1764705882`，E2 阳性；答案文本相同，E3 文本阴性。仅为单例中期结果，不能据此计算正式 12 例比例。rank 20 正在运行。

# V55 rank 20 中期结果回读

### 现状

固定正式 run 已从 rank 20 进入 rank 21；rank 20 是第八个预选案例终止收据。正式 12 例聚合与 E4 仍未完成。

### 实施方案

独立回读三次首提取探针、Stage A、E1 reset 计数、三条完整 44 会话轨迹的最终检查点、质量门，并重算记忆与检索 Jaccard。审计保存于 `v55_formal/results/RANK20_INTERIM_READBACK_AUDIT.json`，不重跑模型或修改冻结科研文件。

### 完成与未完成状态

回读 12/12 通过。Stage A 与 E1 均通过；清理/原生记忆数 295/287、记忆 Jaccard `0.0337477798`、检索 Jaccard `0`，E2 阳性；答案文本不同，E3 文本阳性。仅为单例中期结果，不能据此计算正式 12 例比例或正确性效应。rank 21 正在运行。

# V55 rank 21 中期结果回读

### 现状

固定正式 run 已从 rank 21 进入 rank 22；rank 21 是第九个预选案例终止收据。正式 12 例聚合与 E4 仍未完成。

### 实施方案

独立回读三次首提取探针、Stage A、E1 reset 计数、三条完整 44 会话轨迹的最终检查点、质量门，并重算记忆与检索 Jaccard。审计保存于 `v55_formal/results/RANK21_INTERIM_READBACK_AUDIT.json`，不重跑模型或修改冻结科研文件。

### 完成与未完成状态

回读 12/12 通过。Stage A 与 E1 均通过；清理/原生记忆数 264/261、记忆 Jaccard `0.0334645669`、检索 Jaccard `0`，E2 阳性；答案文本相同，E3 文本阴性。仅为单例中期结果，不能据此计算正式 12 例比例。rank 22 正在运行。

# V55 rank 22 中期结果回读

### 现状

固定正式 run 已从 rank 22 进入 rank 23；rank 22 是第十个预选案例终止收据。正式 12 例聚合与 E4 仍未完成。

### 实施方案

独立回读三次首提取探针、Stage A、E1 reset 计数、三条完整 48 会话轨迹的最终检查点、质量门，并重算记忆与检索 Jaccard。审计保存于 `v55_formal/results/RANK22_INTERIM_READBACK_AUDIT.json`，不重跑模型或修改冻结科研文件。

### 完成与未完成状态

回读 12/12 通过。Stage A 与 E1 均通过；清理/原生记忆数 293/291、记忆 Jaccard `0.0409982175`、检索 Jaccard `0`，E2 阳性；答案文本相同，E3 文本阴性。仅为单例中期结果，不能据此计算正式 12 例比例。rank 23 正在运行。

# V55 rank 23 中期结果回读

### 现状

固定正式 run 已从 rank 23 进入最后一例 rank 24；rank 23 是第十一个预选案例终止收据。正式 12 例聚合与 E4 仍未完成。

### 实施方案

独立回读三次首提取探针、Stage A、E1 reset 计数、三条完整 44 会话轨迹的最终检查点、质量门，并重算记忆与检索 Jaccard。审计保存于 `v55_formal/results/RANK23_INTERIM_READBACK_AUDIT.json`，不重跑模型或修改冻结科研文件。

### 完成与未完成状态

回读 12/12 通过。Stage A 与 E1 均通过；清理/原生记忆数 300/329、记忆 Jaccard `0.0500834725`、检索 Jaccard `0`，E2 阳性；答案文本不同，E3 文本阳性。仅为单例中期结果，不能据此计算正式 12 例比例或正确性效应。rank 24 正在运行。

# V55 held-out 正式实验与补充 E4 完成

### 现状

固定 run `v55-formal-20260925-01` 的 ranks 13–24 已全部有终止收据。rank 14 生成中断后按冻结不重试规则人工裁定无效；rank 16 clean-clean 答案文本分叉而校准无效。其余 10 例完成 native。之前的逐例通知均是中期结果，尚未构成正式 12 例汇总。

### 实施方案

运行器按冻结身份生成 12 例结构化结果与固定分母聚合。独立脚本逐例核对 cohort、探针、Stage A、Stage B、不可覆盖检查点、E1/质量门、记忆和检索 Jaccard、答案文本哈希、缺失处理、Wilson 描述区间与原结果的一致性。审计通过后，仅对六个 E3 文本阳性配对答案按预先统一的 LongMemEval rubric 使用 DeepSeek `deepseek-flash`、非思考、温度零、每臂三票判分；保存 36 条原始请求/响应，不调用 OpenAI。另行核验输入绑定、模型 ID、逐票原始响应、多数票与配对结局。写决策摘要并更新权威入口。

### 完成与未完成状态

V55 **12/12 预选例终止**，Stage A 有效 11，E2 可评估 10；10/10 E2 阳性，6/10 答案文本 E3 阳性。rank 14 E2/E3 缺失、rank 16 校准无效均未计作阴性。正式独立回读 **121/121** 通过。补充 E4 对 6 配对、36 调用全部完成且投票一致：原生较好 1、清理较好 1、都对 1、都错 3；E4 回读 **113/113** 通过。官方 GPT-4o 端点仍未测；DeepSeek 是可能漂移的别名，不能宣称总体发生率、自然榜单污染、跨 backend 一般性或统一方向的正确性提升。rank 14 的人工执行修复和 rank 13 数值答案内部日期不一致的事后阅读均已在决策摘要披露。下一步是审查论文 claim 与是否另冻 VTI／独立 backend 扩展，而非直接追加样本。

V55 完成与 E4 审计后，按任务范围暂停了每小时 V55 跟进自动化；本机监督器已经终止，不再运行重复检查。

# V55 完整归档、V56 导入与 LangMem-Local Stage 0

### 现状

V55 正式实验和补充 E4 已完成；用户要求将 V55 完整移入 `history/`、清理旧入口，并开始 V56，同时在右侧显示 HTML 进度。V56 增量包只提供拟定协议和依赖预检，没有可运行的科学适配器；其 ZIP CRC 通过，但 `MANIFEST.sha256` 对自身写入了空文件哈希。

### 实施方案

先停止 V55 只读页面，逐文件哈希核验后将完整 V55 版本目录搬入 `history/v55_formal/`，再单独校验归档其启动脚本、旧导出包、专用 Python 环境与日志；不删除结果或检查点。把 V56 源包原样保留在 `source_original/`，导入拟定协议，冻结未被 V42/V55 执行的 SHA256 ranks 25–28 及固定 predecessor rank 1。建立只绑定本机的 V56 只读 HTML。创建隔离依赖环境，明确本地替换原 LangMem 适配器的 OpenAI 提取、嵌入与答题三个调用面，继承其 `ingest/reset/list_memories` 语义；冻结包版本、模型摘要、嵌入缓存、代码及合成 Stage 0 规则后才调用本地模型。

### 完成与未完成状态

V55 23,174 个文件、3,134,816,611 字节迁移前后逐文件哈希一致；12 个旧入口/环境/日志项单独核验，详见 `history/V55_RELOCATION_MANIFEST.json` 和 `history/V55_NONVERSION_RELOCATION_MANIFEST.json`。V56 包 7/8 列表项哈希匹配，唯一不匹配是清单自身。V56 LangMem-Local Stage 0 使用 5 次本地 Qwen 调用，两个合成会话各产生 1 条记忆；native reset 后声明状态为空，第二会话未读取首会话状态，本地答题成功。独立回读 **14/14**。这只是适配器工程可行性，**V56 真实 target 的 Stage 1/2 结果仍为零**。四例真实 replay 之前还须冻结运行器、不可覆盖快照、质量门并完成真实中断续跑演练。

# V56 Stage 1/2 freeze and formal launch

Frozen LangMem-Local gate protocol, four prospective targets, fixed predecessor, code and quality rules before real-target model calls. Read-only identity guard passed 9/9, including model digest, package source and embedding cache hashes. Real SIGTERM drill resumed the same run ID: unit 1 immutable receipt remained hash-identical, unit 2 completed, interrupted partial attempt stayed outside committed checkpoints. Formal run `v56-gate-20260926-01` launched on rank 25 clean-clean calibration. No V56 target causal outcome yet; live status is `v56_cross_backend/STATUS.json`.

# V56 exact-null stop and independent readback

The fixed rank-25 LangMem-Local target completed clean_ref and clean_rep (51 sessions each). Exact clean-clean endpoints diverged; final memory/retrieval counts were 1 versus 3, both below the frozen quality floor of 5. Different random first-session memory IDs entered the second manager input. By frozen rule the gate stopped at 1/4 selected targets with `UNVERIFIABLE_NULL_DIVERGENCE`; no predecessor/native run and no cross-backend causal result. Independent terminal readback passed 439/439 checks. See `v56_cross_backend/V56_DECISION_SUMMARY.md` and `v56_cross_backend/results/GATE_TERMINAL_AUDIT.json`.

# V56 网页版 GPT 陈述文档
### 现状
V56 已按冻结规则因第 25 例 clean-clean 校准分叉停止；本地独立回读 439/439 通过。用户需要一份可单独发给网页版 GPT 的陈述。
### 实施方案
将 V55 背景、V56 预先规则、真实分母、质量门失败、随机记忆 ID 的候选混杂与结论边界整理为自包含文档；附待决策问题和本地证据索引。
### 完成与未完成状态
已生成 `exports/V56_STATEMENT_FOR_WEB_GPT_20260927.md` 及 SHA-256 sidecar，README 已加入入口。未授权、未启动任何后继实验；V56 原始收据与冻结规则未变。

# 网页版 GPT V57 方案独立审查
### 现状
用户提供 V57A 兼容性门、V57B 随机性 null 因果门及候选后端梯队。V56 已冻结停止，不能重标或续跑。
### 实施方案
原文保存在 `docs/proposals/V57_WEB_GPT_PROPOSAL_20260927.txt` 并记录哈希；对照冻结 V56 收据、V47/V48 已用样本、当前 Redis Graphiti adapter 和精确排列概率审查。
### 完成与未完成状态
审查文档 `docs/V57_WEB_GPT_PROPOSAL_REVIEW_20260927.md` 已形成。认可先兼容性、后分布 null 的主轴；发现 3+3 envelope 阳性规则无错误率控制、gold 质量门未机械冻结、早期前缀阴性不能代表完整隔离，以及 Graphiti 仍需 Neo4j 与本地 provider 适配。未冻结或运行 V57；V56 科研文件和收据未改。

# V57 双后端随机化方案冻结前审查与统计脚本干跑
### 现状
用户提供修订方案：LangMem/Graphiti 固定 panel、开发兼容性门、完整 target 的 5+5 随机分配、统一 retrieval primary 和精确分层检验。V56 冻结停止。
### 实施方案
保存方案原文；核对 V49 count parser 与 rank1/3/4 reference；审查生命周期干预、独立 run 边界、统计假设及计算量。建立未冻结协议草案和无模型调用的 exact energy randomization 代码，使用合成向量做实施干跑。旧版 V57A 未使用代码移入 `history/drafts/v57a_pre_revision_20260927/`。
### 完成与未完成状态
统计实施干跑 6/6 通过；审查与协议草案已保存。V49 scorer、primary lifecycle estimand、Graphiti 数据库/本地 provider、assignment schedule 与 footprint 身份仍未解决，因此 **V57 未冻结、未启动、未调用模型**；14B 下载保持停止。

# V57 前例匹配设计的离线实现与工程预检
### 现状
用户给出全前例负载匹配、native reset 对 pristine shadow、独立重复、两例复现的 V57 修订；明确要求冻结前完成 scorer、Graphiti 工程预检和统计干跑，暂不启动 V57 或恢复 14B 下载。
### 实施方案
保存原文；从固定数据集绑定 ranks 1/3/4 的 raw reference 与单位；另写 `count_unit_v1` 和 46 条合成向量，避免 V49 解析器的纯整数限制。实现有序 Top-5 的 1925 维检索表示及 252 分配 exact energy/2-of-3 partial conjunction，做假 embedding 与 1 万组合成 null 干跑。创建隔离 Graphiti core 环境并以 stub 客户端做零模型调用构造测试，检查 Neo4j/容器实际可用性。旧 global-mean 草案移入 history。
### 完成与未完成状态
计数器 46/46、检索表示 8/8、统计 9/9 均通过；Graphiti 构造注入通过，但 Docker/Colima/Neo4j 尚未就绪，Homebrew 安装因元数据获取缓慢终止，未安装容器运行时。14B 未下载、无 V57 模型或正式样本调用。协议保持 `DRAFT_NOT_FROZEN`，仍缺 Graphiti reset/teardown、实际 BGE/14B 身份、随机分配和逐 unit 隔离恢复演练。

# Graphiti-Local 玩具输入组件预检补充
### 现状
Graphiti 0.30.2 构造器预检通过，但本机没有容器/Neo4j。
### 实施方案
实现自定义 FastEmbed BGE 384 维 embedder 与明示非 stock 的 BGE-cosine reranker；在关闭 Graphiti telemetry、设置 EMBEDDING_DIM=384 且无 OpenAI key 下，仅用合成文本做注入/维度/缓存哈希/重复排序检查。
### 完成与未完成状态
组件干跑 7/7，通过 `v57_design/results/GRAPHITI_LOCAL_COMPONENT_AUDIT.json` 保存；零 LLM 和数据库调用。Neo4j 健康、stock reset、teardown、Graphiti 实际 query、14B structured output 仍未测，不能冻结或运行 V57。

# C33 资料与文献准备状态审计
### 现状
用户询问 A 会研究所需资料和文献是否齐全。V55/V56 原始材料已归档并审计，V57 尚未冻结；IDEA.md 中状态段停在 V55 结果产生以前，活跃目录没有统一 BibTeX 库或论文稿。
### 实施方案
核对 V55/V56 冻结结果、V57 草案/离线审计和文稿入口；以官方 Redis harness、arXiv 原文页和 Mem0 官方 issue 核实直接相关工作，并补查 2026 年 7–9 月新近论文。
### 完成与未完成状态
审计保存于 `docs/MATERIALS_AND_LITERATURE_AUDIT_20260927.md`。已确认实验 provenance 强于当前论文/文献准备；新增 A-TMA、Scope Before You Persist、DolphinBench 等需全文比较的来源。尚无完整系统综述、核对过元数据的 references.bib、claim-to-artifact 总账、正式论文和 V57 跨后端结果。未改用户 IDEA 原文或历史实验收据。

# C33 各版本文献承接审计
### 现状
用户询问各版本文献是否接得上，要求仅核对文献脉络而非实验结果。V32 已进行强 prior-art 降级，当前 IDEA 延续了核心边界，但尚无统一 BibTeX 和跨版本引用矩阵。
### 实施方案
对照 V32 prior-art delta、当前 IDEA Related Work/novelty sections、V56 后端选择与 V57 统计草案；用 arXiv/期刊原始页核对早期与新近相关工作，并检查统计方法源流。
### 完成与未完成状态
形成 `docs/LITERATURE_LINEAGE_AUDIT_20260927.md`。主线承接成立；发现 V32 Agentic Benchmark Checklist/MemSecBench 未进入当前 IDEA、V57 Fisher/energy/partial-conjunction 方法未引源、新近 A-TMA/Scope/DolphinBench 尚未全文对比。原用户 IDEA 与历史版本未改。references.bib 和可投稿 Related Work 仍未完成。

# C33 文献承接修复与起始参考文献库
### 现状
用户要求修复各版本文献的断点。V32 prior-art delta 中 Checklist/MemSecBench 未进入 IDEA；V57 使用的 Fisher/energy/partial-conjunction 缺方法引源；A-TMA/Scope 等新论文缺当前 claim 边界，活跃目录没有参考文献库。
### 实施方案
核对 arXiv 原始页与部分高危论文 HTML 全文；从 DataCite/Crossref 保存 18 份 DOI 元数据快照，另录官方 Redis harness/Mem0 issue 两项，生成 20 条起始 BibTeX；形成当前 Related Work claim-to-source 表；给 IDEA 追加日期明确的文献补充，不改历史论证正文。
### 完成与未完成状态
`docs/literature/references.bib` 共 20 条，结构/元数据审计 10/10；`docs/literature/RELATED_WORK_CURRENT.md` 已把 V32、IDEA、V57 方法和新近相关工作接起来。已对 Cross-Unit Separation、A-TMA、Scope 做针对性原文对比。仍需其他高危论文逐句全文审查、最终会议发表元数据标准化、投稿前刷新检索和正式论文引用核验。实验状态未改。

# V56 与旧材料归档及根目录清理
### 现状
用户要求重新整理 Science 文件结构，将历史资料放入 history。V56 已按规则停止，但版本目录、旧导出、旧 MemArena/Mem0 源码和 V50/V56 环境仍在根目录或 .runtime；V57 当前草案仍需 Redis 源码和 BGE 缓存。
### 实施方案
先建立独立 V57 统计环境并验证 NumPy、计数器和检索表示；停掉旧 V56 只读页面。按逐文件 SHA-256 搬迁 17 项版本/导出/源码/环境/诊断材料，保存搬迁前文件清单与搬迁后审计，并独立二次回读。旧提案审查与 MemArena 计划另按哈希迁入 history。冻结 V56 文件不作路径编辑；编写历史原路径恢复说明。更新当前状态、交接、README、已知缺口、活跃 V57 Graphiti 预检路径和历史索引。
### 完成与未完成状态
17 项共 18,351 文件、493,389,469 字节原样归档，搬迁审计和独立二次回读均 PASS；其中 V56 为 831 文件、9,044,020 字节。另五份已取代方案文件搬迁哈希一致。当前根目录保留 IDEA、CURRENT、docs、v57_design、固定 Redis 源码、活跃 V57 环境/BGE 缓存和空的 ops/exports 目录。V56 看板已停止；V57 未冻结或运行。旧冻结脚本因 Path.resolve 根路径假设只能在隔离工作副本中按 `history/V56_REHYDRATION.md` 恢复后执行，不能直接从归档目录重跑。

# 当前 Python 环境管理说明与依赖快照
### 现状
用户询问 Python 环境如何管理。当前根目录只有两个 V57 工程虚拟环境和共享 BGE 缓存；V50/V55/V56 环境已经归档。
### 实施方案
核对 uv/Python 版本、两环境安装包和路径；保存各环境的 pip freeze 与 SHA-256；说明 V57 工程环境与冻结科研运行环境的区别，并更新入口。
### 完成与未完成状态
`v57_design/environment/README.md` 与 `V57_ENV_SNAPSHOT.json` 已生成。统计环境仅 NumPy 2.5.3；Graphiti 工程环境 46 个包，含 graphiti-core 0.30.2/neo4j 6.3.1/fastembed 0.8.0。两者使用 uv 管理的 CPython 3.12.14，互不混装。当前没有 uv.lock 或正式 V57 runtime manifest；14B 与 Neo4j 镜像身份未固定，未调用正式模型。

# Git 忽略规则与显卡服务器源码准备
### 现状
用户要求重点忽略 history 和可重新下载的大文件，使当前代码能迁移到显卡服务器。原 `.gitignore` 只忽略了 history 的部分子目录和全部 third_party/.runtime；V57 一个预检脚本仍依赖 history 内的 V56 哈希。当前 Git 仓库无 remote，旧 HEAD 跟踪 459 个老根目录文件且有大量未提交迁移。
### 实施方案
将 `/history/` 整体忽略，同时忽略本机虚拟环境、第三方 checkout、导出包、下载型模型和数据格式；保留当前小型协议/代码/文献/依赖清单。将 BGE 哈希提取到活跃 `v57_design/DOWNLOADABLE_ASSETS.json`，按固定 HF revision 和 snapshot 哈希验证，去除对 history 的执行依赖。加入跨 Linux/Mac 的 Python 工程 bootstrap、输入依赖清单、服务器说明和只含当前源码的 tar 导出脚本。
### 完成与未完成状态
.gitignore、可下载资产清单、服务器准备脚本已写；本机 BGE 组件预检在改为活跃清单后仍 7/7 通过，服务器 bootstrap 的只读验证通过。14B 与 Neo4j 仍不会自动下载或运行。Git 尚无 remote；当前源码已在本地 main 提交，可配置 remote 后推送，或直接传输轻量源码包/Git bundle。V57 正式协议仍未冻结。

# Git 被追踪容量与轻量传输清理
### 现状
用户追问已追踪文件大小并要求去掉一些垃圾。当前旧 HEAD 追踪 459 文件、4,408,462 字节，其中 452 个旧根路径因归档已从工作树删除；本机 .git 约 738 MB，包含 Codex turn-diff 的历史引用，不能误判为可直接清除的临时文件。仓库没有 remote。
### 实施方案
保持本机 Git 历史和 Codex 引用不动；用当前源码 tar 生成无父提交的单分支 Git bundle，仅含可迁移的协议、代码、文档和小审计文件。实际 git clone 该 bundle 并逐文件对照 SOURCE_MANIFEST 哈希，确保 history/.runtime/third_party 不进入服务器传输。
### 完成与未完成状态
轻量 Git bundle 已输出并通过真实 clone 与逐文件哈希验收；源 tar 亦可直接传给服务器。旧工作树中的历史文件已经物理归档到 history，未删除科研原件；本机旧 HEAD 与 Codex turn-diff refs 暂留，尚未重写 Git 历史或清理对象。

# 本地 Git 追踪清理完成
### 现状
旧 main HEAD 追踪 459 文件、4,408,462 逻辑字节；452 个历史根路径已经迁入被忽略的 history。`.git` 本机体积大主要因为 Codex turn-diff refs，不应删作垃圾。
### 实施方案
核对源 tar 清单和 `.gitignore` 后，暂存历史根路径的删除与当前 65 个源码文件，检查无意外未跟踪源文件及 Git diff whitespace；在 main 做本地 source-only 提交。保留原科研档案及 Codex refs。
### 完成与未完成状态
本地 main 当前 HEAD 只追踪 65 个实际存在的源文件（约 0.5 MB），工作树无未提交变更；旧提交历史仍可回看，`.git` 对象不清理。轻量独立 Git bundle 经真实 clone 与逐文件哈希核对通过。尚无 remote，未向服务器或 Git 托管服务推送；V57 仍未冻结。
