# V58 逐项验收与最后审查

日期：2026-09-30。范围：正式运行前的实现准备；**正式 V58 模型调用 0**。每项结论以本版审计和原始收据为准，不能解释为已经产生科学实验结果。

| # | 验收项 | 结果与证据 |
| ---: | --- | --- |
| 1 | 读取当前状态 | PASS；README、开发规范、IDEA、V55/V56/V57 与旧冻结均回读。 |
| 2 | `CURRENT_STATE.json` 冲突 | PASS；原文件只记录重置起点，先前 P0 被保留为历史发现，现状态新增补充冻结和当前 gate。 |
| 3 | V45/V55 冻结依赖 | PASS；engine、runner、checkpoint、schema 哈希与 V55 manifest 匹配。 |
| 4 | V58 freeze audit | PASS；[补充后审计](FREEZE_AUDIT_AFTER_IMPLEMENTATION.json) 26/26。 |
| 5 | 12 order、24 sequence | PASS；无替换、无额外 case。 |
| 6 | 36/36 coverage | PASS；每个有向邻接 pair × target 位置恰一次。 |
| 7 | N/V 语义 | PASS；真实 Mem0 + fake client 四 trial 演练中 N 的 sidecar 累积为 2/4/6，V 每次归零。 |
| 8 | process isolation | PASS；dry-run 两个独立 PID；正式 full 入口逐 sequence 起新子进程。 |
| 9 | fake-client tests | PASS；success、402、429、timeout、provider failure、malformed response、model drift、HTTP 原件顺序及预算均覆盖。 |
| 10 | 发送后零自动重试 | PASS；同一步第二次 dispatch 本地拒绝，故障后不会自动重发。 |
| 11 | 原子 checkpoint | PASS；临时目录、fsync、原子 rename 与哈希回读；不可覆盖。 |
| 12 | crash/resume | PASS；[子进程死亡演练](RECOVERY_DRILL_02.json) 13/13，[真实 Mem0 跨进程恢复](BACKEND_RESUME_DRILL.json) 8/8。 |
| 13 | 配置不一致恢复拒绝 | PASS；freeze、dataset、model、code、预算身份漂移被拒绝。 |
| 14 | exact 4096 randomization | PASS；完整枚举并从每个 assignment 重算 cell，合成结果 `p=1/4096`。 |
| 15 | processed 从 raw 重建 | PASS；24 个合成 sequence 的 raw observation 经离线 aggregate 重建完整统计与来源哈希；正式 raw 尚不存在。 |
| 16 | 预计模型请求 | 4,488 = 4,392 ingestion + 96 回答，假设每次 ingestion 一请求；超出时由硬预算停止。 |
| 17 | 预计 token | V55 收据外推输入 50,164,493、输出 1,767,868、合计 51,932,361；不确定性见成本预检。 |
| 18 | 预计费用及最坏预算 | 本地 Ollama 外部 API 费 ¥0；电力/硬件未计。一次请求最大预留 32,768 输入及 2,048 输出 token，总计划上界 147,062,784/9,191,424；硬预算由正式命令显式指定。 |
| 19 | P0 数量 | 0（原主要指标 P0 已前瞻性补充并重审通过）。 |
| 20 | P1 数量 | 0（旧路径审计器问题已由新入口解决；历史原件未改）。 |
| 21 | P2/P3 | P2：真实 Qwen 响应尚未产生，运行前需再次核对现场身份和预算；P3：0。用户确认描述性 correctness score 暂不判分。 |
| 22 | README | 已更新 V58 入口、状态及 `.env` 当前路径。 |
| 23 | 变更记录 | 全项目和 `docs/v58/` 均已更新。 |
| 24 | CURRENT_STATE | 已记录本版代码、测试、数据、模型、收据与正式调用为 0。 |
| 25 | 运行资格 | **READY_FOR_FORMAL_RUN**；正式模型调用仍需用户下一步明确决策，并在实际启动时执行 run-specific preflight。 |

## 语句到语句审查

任务书的设计范围、目录、路径、冻结依赖、12/24/36 分配、单 process 四 trial、N/V cleanup、raw、checkpoint、请求规则、恢复 A–F、fake client、4096 统计、成本、离线测试、P0–P3、决断、状态与禁止事项均有对应实现或收据。用户后续只修订了主指标唯一性；原冻结设计与历史结果未改写。用户对 0–4 correctness 作出“先保存答案，评分待定”的实施决断，本版不报告该分数。

## 挖洞结论

重点攻击了随机化单位、数据身份、scope carryover、sequence 间隔离、异常发送后重试、response 落盘时点、raw 篡改、cleanup 在恢复中重复、预算漂移和正式结果过度解释。无未解决 P0/P1。真正的 Qwen 输出格式与长批次耗时仍只能在后续获准的正式执行中观察；遇到任何身份、收据、预算或运行时漂移，runner 必须停止而不能补抽。无 V58 正式 outcome 可供结果审查。

**FORMAL MODEL CALLS DURING THIS TASK: 0**

2026-09-30 暂停与监控实现修订后，最新离线测试 21/21、冻结检查 26/26、真实后端 fake-client 恢复 8/8 通过；见 [审计收据](PAUSE_MONITOR_TEST_AUDIT.json)。正式模型调用 0。
