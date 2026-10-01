# V58 输出截断修复与每小时监督

## 原因与处理决断

旧批次 `formal-mac-20260930-r02` 在 V 条件第 4 个 session 达到 2048 输出 token 上限，`done_reason=length`，JSON 未闭合。失败与所有旧成果完整保存；旧批次的全部 sequence 都排除在本次修订后的正式统计之外。不得只替换失败 V 条件、沿用原 N 条件。

用户授权修复后自主重跑，常规故障自行处理且记录文档；监督周期为 1 小时，只有完全推翻实验或无法解决的外部阻塞需要用户介入。本轮修订依据已观察到的运行失败，因此它是**失败之后、下一正式批次之前**的执行条件修订，不宣称原预注册条件从未改变。

## 前瞻性执行修订

`study_freeze/V58_EXECUTION_AMENDMENT_20261001.json` 固定输出上限 8192，24 sequences、96 trials、4392 ingestion、4488 请求，保守 input 预算 147062784，output 预算 36765696，外部 API 成本 0。原模型 digest、context 32768、随机参数、schema、memory backend、embedding snapshot、完整 checkpoint、N/V 分配、顺序、主指标和统计不变。所有请求使用同一新上限，不按输出是否失败临时变更。

执行修订哈希绑定源码、冻结审计、sequence 与 controller 身份。模型输出上限与每请求预留、全批次消耗记账一致；任何 `length` 停止立即视为 terminal，完整 raw HTTP 仍先保存。没有自动补 JSON、删记忆、缩短样本或重试。模型输出的有效性是实际 schema 验证，不能仅靠 `done=true` 判通过。

正式开启之前，`src/qualify_output.py` 用独立 `v58-dev-output-20261001` 重放原失败请求，唯一改变 num_predict。门槛为自然结束、schema 合法、使用低于上限的 75%；收据必须保存。这是开发诊断，受失败样本选择影响，不计入正式数据，也不保证全部其他样本永远不失败。

## 完整启动检查

`src/launch_formal.py` 只允许新 batch ID，拒绝重复 full runner，要求开发资格门及其执行修订身份一致；核对冻结、Ollama/model digest、依赖、benchmark commit，并实际初始化完整 Mem0 store（不发模型请求），检查实际加载的 embedding snapshot。显式设置 MEM0_TELEMETRY=false、固定 FastEmbed 缓存、HF_HUB_OFFLINE=1，避免此前缺少启动配置的错误。以脱离终端的后台进程运行，日志/启动收据写本版 outputs。

启动命令（用户已授权，无须再次确认）：

```bash
history/runtime/v55-venv/bin/python solutions/v58/src/launch_formal.py \
  --batch-id formal-mac-20261001-output8192 --allow-model-calls
```

## 每小时监督规则

Codex heartbeat `v58` 已设为每小时在当前聊天执行，正常推进保持安静。查看真实 PID、控制状态、最新响应/检查点时间、请求耗时、GPU、swap、磁盘与预算，日志以 raw 证据为准；监督摘要不可覆盖旧事实。监督依赖 Mac 开机且 Codex 在运行，不保证设备休眠、应用退出或服务断线时按时执行（[官方文档](https://learn.chatgpt.com/docs/automations?surface=app)）。

- 用户暂停：保持暂停，不自动恢复。
- 安全边界意外退出：检查无存活重复 runner，身份、预算、完整 checkpoint 和无 pending operation/call 均通过后用原预算恢复；不删除原始失败证据。
- 明确失败/截断/schema/身份漂移：保存现场，自行诊断并修复，必要执行条件变化先另存修订、验证、使用新批次；不把原 uncertain request 重发为“恢复”。不同执行条件数据不混用。
- 没有推进：先检查是否真实推理或长请求；单次超过一小时不自动认定失败。不强杀仍有推理进展的请求。
- 重复失败：查清根因再继续，不能无界循环启动相同失败配置。
- 全量完成：停止模型执行，离线回读与按冻结规则统计，更新文档并报告；停用监督。

## 验收边界

离线测试、恢复演练、开发资格及首次新正式 checkpoint 的具体证据将在本文件补充。禁止在资格门未通过时先跑正式实验。旧预算 70–100h 未按这一个失败样本重算；上限提高不是每个请求固定生成 8192 token，墙钟时间仍以真实运行估计。

验收：开发请求自然结束 `stop`、eval_count=365、schema 通过，1 次开发调用。离线测试 24/24、恢复检查 13/13、真实 Mem0 fake-client 跨进程恢复 8/8、冻结检查 27/27。源码到需求审查及挖洞审查：已知参数漂移通过新批次和身份绑定隔离，不复用旧 N；无 P0/P1 未解决项。仍有 P2 边界：单次资格门不能保证全样本无截断，模型可能输出其他 malformed JSON；监督不会修补响应或盲目重试。开发收据 `solutions/v58/outputs/v58-dev-output-20261001/raw/qualification.json`。
