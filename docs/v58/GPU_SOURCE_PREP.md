# 武大超算 V58 源码准备记录

状态：`SOURCE_ONLY_PREPARATION`。本阶段只恢复与校验源码、检查资源申请资格。**不下载 LongMemEval 数据、BGE/Qwen 模型或 Python 环境，不运行 V58 正式或开发模型请求。** 原 Mac 串行方案的科学冻结与运行结果均不改变；GPU 环境尚未获得 `READY_FOR_FORMAL_RUN` 资格。

## 用户给定的账户边界

账户说明限定所有远端工作在 `~/projects/srx/`。该目录最初不存在，已建立专用目录；后续检查与作业测试均从此目录进行。账户文件、密码、根目录 `.env` 和整个历史目录均不得上传到超算或 GitHub。

## 可移植源码包

Git 已跟踪 `solutions/v58/frozen_sources/`：15 个逐文件 SHA-256 固定的 V45/V55 与 V57–V59 冻结源文件，及固定 Redis benchmark 提交的公开 Git bundle。清单见 [`MANIFEST.json`](../../solutions/v58/frozen_sources/MANIFEST.json)，恢复入口见 [`prepare_sources.py`](../../solutions/v58/src/gpu/prepare_sources.py)。它仅从本地包恢复原代码期待的被 Git 忽略的 `history/` 路径，拒绝路径穿越和已有文件哈希漂移；不访问网络或执行模型。全新临时项目中的 `--materialize`、`--verify-only` 均通过，2 条安全测试通过。

源码 clone 在超算登录节点直连 GitHub HTTPS 超时，因此后续使用 Mac 端经过代理取得的**当前提交源码快照**经 SSH 上传到 `~/projects/srx/`。这只是源码交接；数据、模型和运行时须另行前瞻性准备与核验。

## GPU 资源申请预检

登录节点提供 Python 3.7.6、Git 和 Slurm。可见 `a100x4`、`gpu` 分区；Slurm 账户关联显示默认账户不适用于 GPU 分区，指定项目关联后，`a100x4` 的 `sbatch --test-only` 返回可调度估计。测试用 [`source_preflight.sbatch`](../../solutions/v58/src/gpu/source_preflight.sbatch) 只要求 1 张 GPU、5 分钟、4GB RAM，内容仅回读源码哈希和 `nvidia-smi`；**`--test-only` 未提交作业，也未占用 GPU**。当时的预计排队时间只是瞬时调度估计，不代表已预订资源。

## 正式 GPU 运行前仍缺的 gate

目标节点实际 GPU 型号与驱动、代码/模型/数据/embedding 身份、Linux Python 依赖、Ollama 版本、单路吞吐、Qdrant/SQLite 本地存储、完整 crash/resume 与预算均尚未核验。下一阶段应先建立 `V58_EXECUTION_ENVIRONMENT_AMENDMENT` 并做非正式资格测试；不得因为源文件和 `sbatch --test-only` 通过就启动正式 V58。超算可能有排队与作业时限，实验输出必须留在允许路径并按 run_id 回读。
