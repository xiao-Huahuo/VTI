# 当前研究状态与后续执行

项目：`AM-AUTO-20260918-R1`

主候选：`C33`

工作标题：**Hidden Trial State in Agent-Memory Benchmarks: An Empirical Audit**

当前状态：
`FORMAL_PILOT_EXECUTION_BLOCKED_V40_C33_REDIS_COHORT_FROZEN_RUNTIME_PACKAGE_READY`

## 已完成
C33 已确定。宽泛的 cross-run contamination、verified reset 等概念已有 prior art，论文贡献已经收窄为 Agent Memory benchmark 的 empirical systems audit。

V34 是 Formal Pilot 的协议权威版本。V40 完成 Redis pilot 的执行材料化，没有修改 V34 实验设计。

Redis Formal Pilot：
- Redis Agent Memory Benchmark commit：`94192c39e2a4a154f441a5411e3d73c4f54974a6`
- Mem0：`2.0.19`
- n = 12
- 样本规则：`SHA256(C33-V34-REDIS|question_id)`，session 数 >= 4
- fault injection：3 次成功 session add 后触发失败
- primary success：E2 或更高
- bootstrap：5000
- seed：20260919

冻结 question_id：
`b5ef892d`
`58470ed2`
`1a8a66a6`
`gpt4_31ff4165`
`2133c1b5`
`9a707b81`
`gpt4_731e37d7`
`gpt4_c27434e8`
`2698e78f_abs`
`7401057b`
`0862e8bf`
`gpt4_5438fa52`

LongMemEval：
- revision：`98d7416c24c778c2fee6e6f3006e7a073259d48f`
- SHA256：`d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`

V40 新离线测试：4 PASS
V32 control-flow 测试：5 PASS

## 下一步
直接执行 Redis V34 n=12 exact paired pilot。

真实环境：
- Python 3.10 至 3.12，推荐 3.12
- checkout `redis/agent-memory-server@94192c39e2a4a154f441a5411e3d73c4f54974a6`
- 在 `agent-memory-benchmark/` 执行 `uv sync --locked --extra mem0 --group dev`
- 设置 `OPENAI_API_KEY`
- 可访问 HuggingFace 与 OpenAI
- 新的空实验目录

执行入口：
`v40/code/run_redis_v34_v40.sh`

Redis 完成后进入 MemArena n=15 frozen paired pilot。Redis/MemArena gate review 以前不进入大规模 Formal Experiment。

Formal Experiment：`NOT_STARTED`
