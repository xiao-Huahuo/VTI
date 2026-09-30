# Reset Is Not Isolation

**先读[《科研开发规范》](科研开发规范.md)和[当前状态](CURRENT_STATE.json)，再开始任何新版本的设计、编码、实验或整理。** [IDEA.md](IDEA.md)保留研究问题的原始表述；它不是当前实验结果或可执行协议。

## 当前状态

仓库已在 V57 结束后清空当前工作区，准备从 V58 重新开始。**V58 尚无当前协议、源码、输入或输出，也未启动实验。** 当前代码、测试、文档、数据的监管状态以 [CURRENT_STATE.json](CURRENT_STATE.json) 为入口；具体实验结论仍须回读原始收据。不要把历史目录中的脚本或旧冻结方案当作 V58 runner。

V57 及以前的非规范代码、实验数据、文档、旧环境和导出物都在 [history/](history/README.md)，整个目录由保持不变的 `.gitignore` 忽略。原根目录归档在 [history/pre_v58_root_20260930/](history/pre_v58_root_20260930/)；迁移前[文件哈希清单](history/PRE_V58_ROOT_MOVE_MANIFEST_20260930.json)和迁移后[独立回读](history/PRE_V58_ROOT_MOVE_AUDIT_20260930_V2.json)可用于核验。该目录是历史资料区，布局和路径不符合新规范；不要直接在其中续跑或改写冻结收据。

历史结论只作背景：V55 有 Mem0 的 held-out 因果证据；V56 以 `UNVERIFIABLE_NULL_DIVERGENCE` 停止；V57 的 LangMem–DeepSeek Compatibility 判为 `LANGMEM_DS_INCOMPATIBLE`，正式 rank 26/27 未运行。详情见归档的[旧状态](history/pre_v58_root_20260930/CURRENT_STATE.json)和[V57 完整报告](history/pre_v58_root_20260930/study_freeze/results/V57_COMPATIBILITY_FULL_REPORT_20260930.md)。这些结果不会自动变成新版本的证据。

## V58 起的新结构

```text
docs/vXX/                         本版方案、冻结记录、审查、报告
solutions/vXX/
├── src/                          本版全部源码，包括实验代码和测试
├── inputs/                       实际输入，Git 忽略
└── outputs/<run_id>/              原始收据、检查点和分析结果，Git 忽略
.runtime/                          共享 uv 环境、模型与缓存，Git 忽略
```

`src/` 中的代码从自身所属的 `src` 推导本版路径，不依赖机器绝对路径或启动目录。`.runtime/` 可在需要时创建，供多个版本共用环境和模型；原始实验收据仍归各版 `outputs/`。每版的输入来源、哈希、运行身份和重建方式写在可跟踪的版本说明中。具体规则以[开发规范](科研开发规范.md)为准。

根目录只保留项目入口和控制文件；`docs/CHANGE_HISTORY.md` 是全项目变更记录，正式版本另在 `docs/vXX/` 记录版本变化。V58 的 `docs/v58/`、`solutions/v58/` 将在实际开始该版本时建立。历史材料不会为了目录外观被批量改写。`.env` 等旧凭据也已随本机旧根目录归档，**不可将 `history/` 整体上传或公开**。
