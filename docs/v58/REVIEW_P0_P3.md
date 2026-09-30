# V58 冻结方案审查（2026-09-30）

## 结论

归档方案在文件意义上已冻结：原文、生成器、四份设计文件与 `FREEZE_MANIFEST.json` 的哈希匹配，V58 顺序与 N/V 分配也可机械复核。但**尚不能认定为可直接实施的完整 V58 主指标冻结**。按本任务“若冻结设计存在 P0，停止并报告”的要求，本轮停止在方案审查，不创建 runner，不调用模型。机器检查见 [FREEZE_AUDIT.json](FREEZE_AUDIT.json)。

## P0：主要 outcome 未唯一指定

批准原文的 V58 部分用 `d(v_1,v_2)` 定义 cell dispersion，冻结 JSON 只写“retrieval dispersion”，没有在 V58 中明确指定 `d`、`v` 的构造、空检索与重复项规则及实现身份。原文的 V57 部分定义了 1925 维 Top-5 footprint 和 Euclidean energy statistic；V59 又写“仍使用相同 Top-5 retrieval footprint”。这提示一种可能意图，但未把该表示和距离明确绑定到 V58。不同表示或距离会改变 `S_N-S_V` 与 4096 分配的排序。现在由实现者选择，会把实现决策冒充预先冻结的主要指标。

修复需以前瞻性补充记录写清 V58 的表示、距离、数值精度、空检索及重复项处理、实现或测试向量的身份和生效时间，并生成新的审计身份。保留旧冻结文件，不原地改写。本审查不代替用户作这个研究决断。

## P1：旧冻结审计器在归档后失效

原 `study_freeze/audit_design_freeze.py` 以旧根目录推导 `history/v55_formal/...`，在现目录实际寻找 `history/pre_v58_root_20260930/history/v55_formal/...` 并报 `FileNotFoundError`。独立只读核验确认 V55 实际文件在根目录 `history/v55_formal/`，V45 engine 和 V55 runner/checkpoint/schema 的哈希均匹配。执行前应另建 V58 本版审计器，不能修改旧脚本后声称原冻结审计无变化。

## 已核实与仍待 gate

- 四份设计文件、批准原文、生成器哈希均与 manifest 匹配；LongMemEval 数据集 SHA-256 匹配。
- V58 固定四题、12 个唯一 order、24 个计划 sequence、36/36 邻接位置覆盖及各 block 一 N 一 V 均通过独立只读核验。
- V59 冻结配置、六个样本 block 及每个 block 的 arm order 均存在；本轮未进入 V59 实施。
- V55 正式结论和 V56/V57 停止边界与任务书一致；V57 未运行正式 rank 26/27。
- V58 runner、隔离、恢复、fake client、4096 统计实现与成本 guard 均尚未建立或测试，不能标为通过。
- 本次 `ollama list` 只读探测无法连接本机服务；这是后续运行时 gate，不是冻结文件哈希错误。

## 解释边界

36/36 覆盖平衡的是直接前驱身份与 target 位置；各观察仍携带不同完整前序历史，因此未来即使阳性，也只能报告固定四题 panel 的 policy 对历史顺序相关检索离散度的影响，不能归因于单独的直接前驱，也不能推导 accuracy 或排名变化。随机化的 4096 次交换对应严格的 policy sharp-null；不得把它自动解释成更宽的弱零假设或总体人群结论。

当前 P0：1；P1：1；未另列 P2/P3。状态：**NOT READY FOR FORMAL RUN**。正式模型调用：**0**。

## 2026-09-30 补充冻结后复审

用户明确接受上述 P0，前瞻性补充冻结了 1925 维 Ordered Top-5 footprint 和 `float64` Euclidean L2 距离；原设计、样本与分配均保持不变。[新审计](FREEZE_AUDIT_AFTER_IMPLEMENTATION.json) 26/26 通过，**主指标 P0 已清零**。旧 P1 通过本版 `audit_freeze.py` 的固定路径、哈希核验解决，历史脚本与冻结文件未修改。

挖洞检查了以下攻击面：四 trial 是否共用 scope、N 是否误删 sidecar、V 是否遗留 sidecar、sequence 间是否使用独立进程、发送后是否二次 dispatch、response 已落盘但 checkpoint 未提交时是否重复生成、身份漂移、raw 篡改、4096 置换是否从每个 assignment 重算 cell、trial 是否被误当随机化单位、成本上界是否会在新请求前拦截。证据分别在[实施审查](IMPLEMENTATION_AUDIT.md)、[恢复审查](RECOVERY_AUDIT.md)和 fake-client 收据中；这些测试未产生正式结果。

最终代码审查还发现默认 FastEmbed 按模型名加载可能跟随缓存的 `main`，即使旧快照哈希仍匹配也无法证明实际加载它。已将实现限定为原 revision 的 `specific_model_path` 与 `local_files_only`，在实例化后检查实际模型目录，并用完全离线的真实后端演练验证；未改动补充冻结中的 embedding 身份。

当前未发现新的主指标或随机化 P0。用户已决定 0–4 correctness score 暂不判分，现仅保存原始答案与参考答案，不能报告该分数。剩余 P2：正式运行前必须再次核对实时 Ollama identity 和预算；实际模型响应路径未在本轮以真实 Qwen 调用验证。P3：无。**本轮 P0：0；P1：0；P2：1；P3：0。** 这不抹去前次 P0/P1 的发现与修复记录。
