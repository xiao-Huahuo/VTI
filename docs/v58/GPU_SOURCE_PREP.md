# 武大超算 V58 源码准备记录

状态：`CODE_READY_REMOTE_HOME_QUOTA_BLOCKED`。本阶段只恢复与校验源码、检查资源申请资格。**不下载 LongMemEval 数据、BGE/Qwen 模型或 Python 环境，不运行 V58 正式或开发模型请求。** 原 Mac 串行方案的科学冻结与运行结果均不改变；GPU 环境尚未获得 `READY_FOR_FORMAL_RUN` 资格。

## 用户给定的账户边界

账户说明限定所有远端工作在 `~/projects/srx/`。该目录最初不存在，已建立专用目录；后续检查与作业测试均从此目录进行。账户文件、密码、根目录 `.env` 和整个历史目录均不得上传到超算或 GitHub。

## 可移植源码包

Git 已跟踪 `solutions/v58/frozen_sources/`：15 个逐文件 SHA-256 固定的 V45/V55 与 V57–V59 冻结源文件，及固定 Redis benchmark 提交的公开 Git bundle。清单见 [`MANIFEST.json`](../../solutions/v58/frozen_sources/MANIFEST.json)，恢复入口见 [`prepare_sources.py`](../../solutions/v58/src/gpu/prepare_sources.py)。它仅从本地包恢复原代码期待的被 Git 忽略的 `history/` 路径，拒绝路径穿越和已有文件哈希漂移；不访问网络或执行模型。全新临时项目中的 `--materialize`、`--verify-only` 均通过，2 条安全测试通过。

源码 clone 在超算登录节点直连 GitHub HTTPS 超时，因此已尝试把 Mac 端核验的 **`dc3e0104` 源码快照**经 SSH 上传到 `~/projects/srx/`。本地 tar 安全检查与远端 SHA-256 一致；但解包中遇到用户磁盘配额阻塞，远端**没有完整可用的 Science 源码树**。上传的 tar、部分解包目录和本轮测试脚本已仅从指定目录删除，未清理共享账号其他文件。当前源码仍可从已推送的 GitHub 提交和本地源码包恢复。

## GPU 资源申请预检

登录节点提供 Python 3.7.6、Git 和 Slurm。可见 `a100x4`、`gpu` 分区；Slurm 账户关联显示默认账户不适用于 GPU 分区，指定项目关联后，`a100x4` 的 `sbatch --test-only` 返回可调度估计。测试用 [`source_preflight.sbatch`](../../solutions/v58/src/gpu/source_preflight.sbatch) 只要求 1 张 GPU、5 分钟、4GB RAM，内容仅回读源码哈希和 `nvidia-smi`；**`--test-only` 未提交作业，也未占用 GPU**。当时估计最早在 2026-10-04 左右开始，仅为瞬时调度预测。

`/home` 为 Lustre，系统仍有空间，但该共享登录用户的**个人磁盘配额 1,048,576 KiB（1 GiB）已超限**。清理本轮上传后，用户占用仍约 1,115,206 KiB；文件数未超限。账户说明只允许在 `~/projects/srx/` 操作，故不能转去其他未授权路径，也不会删除共享账号既有文件。这个条件必须由账户管理者或超算管理员解决，或明确提供合规的大容量项目路径后，才能继续源码部署、更不用说数据/模型与原始检查点。

## 正式 GPU 运行前仍缺的 gate

目标节点实际 GPU 型号与驱动、代码/模型/数据/embedding 身份、Linux Python 依赖、Ollama 版本、单路吞吐、Qdrant/SQLite 本地存储、完整 crash/resume 与预算均尚未核验。下一阶段应先建立 `V58_EXECUTION_ENVIRONMENT_AMENDMENT` 并做非正式资格测试；不得因为源文件和 `sbatch --test-only` 通过就启动正式 V58。超算可能有排队与作业时限，实验输出必须留在允许路径并按 run_id 回读。
