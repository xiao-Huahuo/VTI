# V58 实施审查

## 已完成

- 原冻结与前瞻性 amendment 的独立[审计](FREEZE_AUDIT_AFTER_IMPLEMENTATION.json)：26/26 PASS；原件哈希未变。
- FastEmbed 使用 `specific_model_path` 和 `local_files_only` 固定到已哈希的 revision 快照，并检查实际加载目录；`HF_HUB_OFFLINE=1` 的[真实后端 fake 演练](BACKEND_FAKE_DRILL_OFFLINE.json)通过，避免后续跟随 `main` 漂移。
- V45 engine、V55 runner/checkpoint/schema、LongMemEval 输入、BGE snapshot 及复制的 V57 footprint 哈希匹配。四题由本版 `inputs/` 的独立 CoW 副本加载；未依赖启动目录。
- runner 已提供 preflight、dry-run、single-sequence、full、resume、readback 和离线 aggregate。full 顺序启动 24 个新进程；同一 sequence 内四题共用 scope。真实 Mem0 fake-client 演练验证 N 保留 sidecar、V 清空 sidecar。
- 原始 request 在发送前保存并哈希；对固定 Ollama 0.6.2 SDK 的 `_request_raw` 接口拦截成功 HTTP 字节，在 SDK JSON 解析前落盘。每个步骤至多一次 dispatch，返回模型 ID 与请求模型不一致即终止。原始响应和状态快照不可覆盖，读取时验证哈希。
- 统计程序以 `float64` Euclidean distance 完整重算 4096 个合法分配；合成数据、raw 重建、进程隔离和异常恢复均离线测试通过。成本预检见 [COST_PREFLIGHT.json](COST_PREFLIGHT.json)。
- 真实 Mem0/Qdrant 的跨进程 fake-client 恢复演练 8/8 通过，已提交的 trial 与 cleanup 均未重算，N/V sidecar 语义在新进程保持一致。
- 本机只读预检曾核实 Ollama 0.34.3、Qwen3 8B Q4 完整 digest 与 V55 冻结版本一致；服务在预检后结束。正式运行必须再次核验。

## 未完成与边界

- **正式 V58 模型调用为 0；没有完整四题真实 Qwen sequence，也没有正式统计结果。** 当前只验证了同一后端的 fake-client 科学路径。正式运行仍需单独决策。
- 用户已选择只保存答案与参考答案，0–4 correctness score 暂不判分；这是公开标记的次要端点缺口，不参与主指标或判定。
- 成本中的 token 数是 V55 收据外推值，四题共享历史可能改变提示长度。硬预算按单次上下文/输出上界保守预留；实际运行由用户设定上限，不自动扩大。

本审查不把离线演练写成正式因果结果。运行前须复核当前源码 hash、模型服务、输入与剩余预算。
