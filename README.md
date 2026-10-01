# Reset Is Not Isolation

**先读[《科研开发规范》](科研开发规范.md)和[当前状态](CURRENT_STATE.json)，再开始任何新版本的设计、编码、实验或整理。** [IDEA.md](IDEA.md)保留研究问题的原始表述；它不是当前实验结果或可执行协议。

## 当前状态

V58 已建立[版本协议与审查](docs/v58/RESEARCH_PROTOCOL.md)、[本版源码和入口](solutions/v58/README.md)及被 Git 忽略的固定输入。**V58 尚未正式运行，正式模型调用为 0。** 当前代码、测试、文档、数据及运行资格以 [CURRENT_STATE.json](CURRENT_STATE.json) 为入口；具体历史结论仍须回读原始收据。

V57 及以前的非规范代码、实验数据、文档、旧环境和导出物都在 [history/](history/README.md)，整个目录由保持不变的 `.gitignore` 忽略。原根目录归档在 [history/pre_v58_root_20260930/](history/pre_v58_root_20260930/)；迁移前[文件哈希清单](history/PRE_V58_ROOT_MOVE_MANIFEST_20260930.json)和迁移后[独立回读](history/PRE_V58_ROOT_MOVE_AUDIT_20260930_V2.json)可用于核验。该目录是历史资料区，布局和路径不符合新规范；不要直接在其中续跑或改写冻结收据。

历史结论只作背景：V55 有 Mem0 的 held-out 因果证据；V56 以 `UNVERIFIABLE_NULL_DIVERGENCE` 停止；V57 的 LangMem–DeepSeek Compatibility 判为 `LANGMEM_DS_INCOMPATIBLE`，正式 rank 26/27 未运行。详情见归档的[旧状态](history/pre_v58_root_20260930/CURRENT_STATE.json)和[V57 完整报告](history/pre_v58_root_20260930/study_freeze/results/V57_COMPATIBILITY_FULL_REPORT_20260930.md)。这些结果不会自动变成新版本的证据。

## V58 起的新结构

```text
docs/vXX/                         本版方案、冻结记录、审查、报告
solutions/vXX/
├── src/                          本版全部源码，包括实验代码和测试
├── inputs/                       实际输入，Git 忽略
└── outputs/<run_id>/              原始收据、检查点和分析结果，Git 忽略
.runtime/                          共享 uv 环境、模型与缓存，Git 忽略
```

`src/` 中的代码从自身所属的 `src` 推导本版路径，不依赖机器绝对路径或启动目录。`.runtime/` 可在需要时创建，供多个版本共用环境和模型；原始实验收据仍归各版 `outputs/`。每版的输入来源、哈希、运行身份和重建方式写在可跟踪的版本说明中。具体规则以[开发规范](科研开发规范.md)为准。

2026-09-30 的首次[冻结审查](docs/v58/FREEZE_AUDIT.json)发现 V58 主指标中的距离和表示未唯一绑定。用户随后提交[前瞻性补充冻结](docs/v58/PRIMARY_METRIC_AMENDMENT.md)，原冻结文件不变；[重审](docs/v58/FREEZE_AUDIT_AFTER_IMPLEMENTATION.json) 26/26 通过。离线测试、fake-client 后端与异常恢复演练已完成；[正式运行资格](docs/v58/READY_FOR_FORMAL_RUN.md)为 `READY_FOR_FORMAL_RUN`，但正式调用须等待用户下一步决策。用户决定暂只保存答案和参考答案，不对描述性 0–4 correctness 打分。

后续提出的并发提速仅做了[独立开发筛查](docs/v58/EXECUTION_PROFILING_SCREENING_20260930.md)：当前 Mac 在 32k context、2 路服务配置下出现明显 CPU offload 与内存压力，故未启动 1/2 lane 完整吞吐对照，`1.35×` 资格门未评估。已完成的两个串行开发 session 显示模型请求占主要耗时；开发请求与正式 V58 结果严格分开。**正式 runner 仍串行，正式模型调用仍为 0。**

针对武大超算，已建立[仅源码的 GPU 交接与资源预检](docs/v58/GPU_SOURCE_PREP.md)。它不包含凭据、输入、模型或环境；A100 分区的 `sbatch --test-only` 可通过，但共享登录账号的 `/home` 1GiB 配额已超限，当前无法在允许目录解包源码。超算上的正式执行资格仍需独立审查。

根目录另有本次用户明确要求的 `study_freeze/` 补充冻结清单；`docs/CHANGE_HISTORY.md` 是全项目变更记录，本版变化另见 `docs/v58/CHANGE_HISTORY.md`。`.env` 已按用户要求从旧归档移回根目录，仍由 Git 忽略且权限为 `0600`；旧迁移清单记录的是移动前位置。历史材料不会为了目录外观被批量改写，**不可将 `history/` 整体上传或公开**。

V58 新增[安全暂停与本机监控](docs/v58/PAUSE_AND_MONITOR_AUDIT.md)，页面为 `http://127.0.0.1:8773`。可随时请求暂停，实际在当前步骤 checkpoint 提交后停止；模型请求期间强杀仍不能保证恢复。正式实验尚未启动。

内存监控已更正：页面展示非文件缓存占用的页统计估计、文件缓存与压缩内存；`memory_pressure` 百分比不能当成物理剩余内存。此前短 smoke 未控制后台应用，详见筛查报告的内存口径更正。

2026-09-30 用户已授权并启动正式 Mac 串行批次 `formal-mac-20260930-r02`，当前运行中，尚无统计结论。启动记录见 `docs/v58/CHANGE_HISTORY.md`；实时进度与暂停入口为 http://127.0.0.1:8773/。此前“正式调用 0 / 未启动”描述均为启动前历史状态。

2026-10-01 最新核查：正式批次已于北京时间 01:32 因 2048 token 上限截断模型 JSON 失败停止，保存 186/4392 ingestion、完成 1/24 sequence。原始失败现场保留，未自动重试，暂无完整统计结论；详见 [状态收据](docs/v58/FORMAL_RUN_STATUS_20261001.json)。此前“运行中”为历史快照。

2026-10-01 输出截断修复：已前瞻性记录 8192 上限与同步预算，失败请求独立开发验证通过；新正式批次将从头执行，旧批次全部排除新统计。每小时自主监督已启用，见 [修复与监督](docs/v58/OUTPUT_REPAIR_AND_SUPERVISION_20261001.md)。

最新：新批次 `formal-mac-20261001-output8192` 已于 2026-10-01 12:36（北京时间）启动，全本地单路串行，每小时自主监督 ACTIVE。旧失败批次数据保留并排除新统计。

2026-10-01 13:30 小时监督：修订批次正常推进，源码/执行身份与最新已提交 checkpoint 核验通过；未采取重启或模型调用。实时数字以页面和 raw 为准，详细收据见 `docs/v58/SUPERVISION_20261001_1330.json`。

2026-10-01 14:30 小时监督：修订批次正常推进，最新提交 checkpoint、源码/执行身份、真实进程及预算核验通过，无需修复或重启。详见 `docs/v58/SUPERVISION_20261001_1430.json`。

2026-10-02 用户授权恢复原安全暂停批次，checkpoint 141 回读通过，从 step 142 接着执行；已保存的 137 ingestion 不重算，右侧页面重新在线，每小时监督保持启用。

2026-10-02 01:00 小时监督：用户授权续跑后正常推进，身份、最新提交 checkpoint、真实进程与预算核验通过；无新 terminal failure，未干预当前请求。收据 `docs/v58/SUPERVISION_20261002_0100.json`。

2026-10-02 02:00 小时监督：原修订批次继续推进，无新 terminal failure；进程、source/执行身份、最新提交 checkpoint 和预算核验通过。详细收据 `docs/v58/SUPERVISION_20261002_0200.json`。

2026-10-02 自动监督修复：第一条 N 完成后发生 native shutdown SIGABRT，完整回读通过。外层监督仅恢复“已完成且已验收”的退出异常，保持原正式源码与条件，原 N 不重跑；当前进入第一条 V。监督收据 `docs/v58/SUPERVISION_20261002_0300.json`，诊断与保护规则见输出修复/监督文档。

2026-10-02 05:36 修复后监督：外层保护、原 controller 和第一条 V 正常推进，源码/执行身份、最新提交 checkpoint、预算核验通过，无新 terminal failure。详细收据 `docs/v58/SUPERVISION_20261002_0536.json`。

2026-10-02 06:35 小时监督：第一条 V 正常推进至第 2 trial，原截断位置的 V step 4 已在本批次自然结束并提交；无新 terminal failure，身份/checkpoint/预算核验通过。详细收据 `docs/v58/SUPERVISION_20261002_0635.json`。

2026-10-02 07:36 小时监督：修订批次继续正常推进，source/执行身份、最新提交 checkpoint、真实进程及预算核验通过，无新 terminal failure。收据 `docs/v58/SUPERVISION_20261002_0736.json`。
