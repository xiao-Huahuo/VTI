# V58 实施入口

版本状态见 [当前状态](../../CURRENT_STATE.json)、[协议](../../docs/v58/RESEARCH_PROTOCOL.md)、[实施审查](../../docs/v58/IMPLEMENTATION_AUDIT.md)。`src/` 是本版全部代码，`inputs/` 与 `outputs/` 被 Git 忽略。数据和运行环境身份见 [输入清单](INPUT_MANIFEST.json)。历史冻结文件只读；本版从自身 `src/` 和仓库标记解析路径。

离线命令（不调用真实模型）：

```bash
python solutions/v58/src/audit_freeze.py
python solutions/v58/src/runner.py dry-run
python -m unittest discover -s solutions/v58/src/tests -v
python solutions/v58/src/drill_recovery.py
python solutions/v58/src/drill_backend_fake.py
```

`runner.py preflight` 只读检查冻结和本机 Ollama 版本/模型 digest，需要本地服务启动；它不生成模型响应。正式 `single-sequence`、`full` 与 `resume` 命令必须显式传入 `--allow-model-calls` 和四项硬预算。在另行作出正式运行决策前，**不得使用该开关**。`readback --run-id <id>` 与 `aggregate --batch-id <id>` 为离线入口，统计只从各 sequence 的 raw observation 重建。

`src/profiling/profile.py` 是独立开发入口，不修改正式 runner 或 checkpoint。其 run_id 必须标记 `DEVELOPMENT_PROFILING / NOT_FORMAL_DATA`，要求单独的 `--allow-development-model-calls`；目标 Mac 的[资源筛查](../../docs/v58/EXECUTION_PROFILING_SCREENING_20260930.md)已停止，不应直接启动长时 2-lane 条件。profiling 调用不属于 V58 正式实验。

GPU 超算源码准备见[交接记录](../../docs/v58/GPU_SOURCE_PREP.md)。Git clone 后可在允许的项目目录下执行 `python3 solutions/v58/src/gpu/prepare_sources.py --cluster --dry-run`，再用 `--materialize` 恢复**仅源码**的冻结依赖，最后 `--verify-only` 回读。`frozen_sources/MANIFEST.json` 绑定每个文件及公开 benchmark Git bundle 的哈希。此入口不下载数据、模型或环境；超算 GPU 的正式执行身份需另外冻结，不能直接继承 Mac 的运行资格。

每个 sequence 有独立 `outputs/<run_id>/{raw,checkpoints,processed}`。`full` 另保存批次身份与全局预算，重启时回读并跳过已完成 sequence；未完成 sequence 必须先在原预算下单独恢复。运行身份绑定原冻结、补充冻结、数据、源码、模型参数和实际模型 digest。checkpoint 保留全量状态快照；从已提交步骤恢复，遇到发送后无完成标记、cleanup 未提交或身份改变时拒绝自动继续。原始请求/HTTP 响应与计算后 footprint 保留在 `raw/`，统计产物写入独立分析 run 的 `processed/`。
