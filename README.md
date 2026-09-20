# AM-AUTO-20260918-R1

Agent Memory 科研项目。当前研究候选为 C33，工作标题为：

**Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit**

## 当前状态

当前权威版本为 **V44**。

- 已确认到 E1：Redis benchmark 的原生 scoped reset 会留下 Mem0 message
  sidecar；下一次 extraction 会读取由此改变的 prompt。
- 尚未因果确认 E2/E3：DeepSeek 的 clean-clean 对照也产生了同量级的
  memory、retrieval 和 answer 分叉。
- E4 未测量。
- Formal Experiment 尚未开始。
- MemArena 暂缓，直到下游终点完成随机性校准或改用可重复模型。

权威机器状态见 [CURRENT_STATE.json](CURRENT_STATE.json)，人类可读交接见
[CURRENT_HANDOFF.md](CURRENT_HANDOFF.md)。

## 文档入口

- [CURRENT_STATE.json](CURRENT_STATE.json)：当前结构化权威状态。
- [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md)：当前结论、环境与下一步。
- [V42 Decision Summary](v42/V42_DECISION_SUMMARY.md)：DeepSeek n=12
  主实验及其解释边界。
- [V43 Decision Summary](v43/V43_DECISION_SUMMARY.md)：thinking-mode
  clean-clean 随机性对照。
- [V44 Decision Summary](v44/V44_DECISION_SUMMARY.md)：non-thinking、
  temperature-zero gate。
- [KNOWN_GAPS.md](KNOWN_GAPS.md)：已知缺口和阻塞项。
- [MIGRATION_INTEGRITY_STATUS.md](MIGRATION_INTEGRITY_STATUS.md)：原始迁出包、
  清理后校验状态和恢复方式。
- [CLEANUP_RECORD.md](CLEANUP_RECORD.md)：本地缓存与原始工作状态清理记录。
- [科研开发规范.md](科研开发规范.md)：用户提供的科研开发规范原件。

## 目录

```text
v42/                 DeepSeek 主 pilot：12 个 native-vs-clean paired cases
v43/                 3 个 thinking-mode clean-clean 对照
v44/                 1 个 non-thinking temperature-zero gate
sandbox_snapshot/    V40 及更早历史研究资料
third_party/         精确 benchmark checkout 与本地虚拟环境（Git 忽略）
reports/             环境准备与 preflight 报告
ops/                 本机运行辅助脚本
```

## 历史文件说明

以下根目录文件属于 2026-09-19 的 V40 迁出快照，不再代表当前状态：

- `00_README_FIRST.md`
- `MIGRATION_STATUS.md`
- `CURRENT_STATE_V40.json`
- `SANDBOX_CONTENT_MANIFEST.tsv`
- `SHA256SUMS.txt`

它们保留用于历史审计。请勿用其“下一步”覆盖 V44 当前状态。

## 完整性

V42、V43、V44 的保留资产分别由以下文件校验：

```text
v42/common/SHA256SUMS_V42.txt
v43/common/SHA256SUMS_V43.txt
v44/common/SHA256SUMS_V44.txt
```

原始 V40 迁出 ZIP 仍保存在 Downloads，可用于恢复清理掉的虚拟环境和缓存。
正式结构化实验结果已进入 Git；`.env`、第三方 checkout、虚拟环境、数据集缓存和
临时工作状态均不进入 Git。
