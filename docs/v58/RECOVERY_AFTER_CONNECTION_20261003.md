# 本地连接失败后的显式恢复

用户在重启后明确授权继续并显示 HTML。原 b07-s1 step64 已 dispatch 无响应，保持 terminal；不重发原请求、不补写响应、不恢复原失败步骤。

前 12 条（block1–6）全部已完成、独立完整回读通过，model/runtime/source/输出上限/设计/主指标条件相同，保留并绑定 identity 哈希。旧 block7 的整个失败 sequence（含61已提交 ingestion、63请求）排除选定正式样本且原样保留。block7–12 全部使用新 batch ID，从独立空状态完整重放，按原冻序与 slot N/V 分配串行执行。原 block7 slot2 尚未执行，无选择性丢弃已完成对照。不是删除检查点后把第64步当成“重试成功”。

`solutions/v58/RECOVERY_MANIFEST_20261003.json` 在新调用前记录全部24选定run_id、12复用身份、排除现场、剩余预算及恢复原因。这是观察到基础设施失败后的操作性修订，不能写成最初预注册从未改变。未按科学结果选择复用/重跑，最终报告须披露所有失败与恢复过程，不能以成功重跑隐藏不确定请求。

## 条件与预算

顶层正式 runner/backend/transport 和原绑定 source 不变，模型参数、schema、BGE/后端、checkpoint、case、order、主要指标、随机化规则不变。新增代码仅在 `src/ops/`。

新恢复 controller 的剩余预算为2244请求、73531392 input token、18382848 output token、外部API成本0；原12条复用2244请求。最终选定正式样本4488请求；这轮8192执行的全部尝试预算4551（含排除的失败sequence63请求），此前2048失败191请求另外保留。新 controller 预算只针对 **新恢复run的实际调用**；页面总请求包括复用2244，不能拿页面合计去对比2244剩余预算。

Ollama仍0.34.3、原Qwen digest、单路32k上下文、原cache/flash设置。启动环境去除HTTP/HTTPS/ALL代理，NO_PROXY localhost/127.0.0.1，避免本地调用被代理干扰；上次断线根因仍未归因，不能宣称此举已证明根治。

## 验证与执行

`ops/recovery_batch.py --audit-only` 检查24唯一冻slot、N/V/order、复用完整回读及身份/source。外层负测试3项（缺slot、重复run、变更policy）加已有暂停保护3项共6/6通过；不调用模型。原模型与冻结只读预检通过。

coordinator仅从 pristine 启动新sequence，父controller接受退出异常的唯一例外仍为 COMPLETE日志+特定native teardown signature+完整回读；任何未完成模型/操作故障仍fail closed，不盲目重试。暂停通过新controller控制文件传播至原runner；用户主动暂停仍不自动恢复。新scope身份按原runner独立sequence规则生成。

`ops/recovery_dashboard.py` 复用原页面/API及暂停token验证，仅按manifest映射展示12旧完成与12新run；旧失败61个ingestion不计入选定进度（2257回到2196），原始文件未删。

最终分析必须使用 `ops/recovery_batch.py --aggregate` 读取manifest选定的24run_id，先全部完整回读，使用原 exact_randomization 算法4096分配、原footprint/statistic。不使用原runner按单一batch ID自动推导路径的aggregate入口，也不把排除的失败run加入统计。

监督读最新 CURRENT_STATE：新controller剩余调用计数与page合计区分，原始raw预算优先。当前尚无全量统计结论。
