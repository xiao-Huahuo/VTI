# AM-AUTO-20260918-R1 — C33

**Reset Is Not Isolation：Agent-memory benchmark 的 trial isolation 审计。** 当前源码已推送至 [GitHub VTI](https://github.com/xiao-Huahuo/VTI)；`history/` 和本机运行环境不在仓库当前树中。

## 当前状态

当前工作仅是 **V57 方案与工程预检**，尚无 V57 LongMemEval 模型运行，协议也未冻结。14B 模型未安装；Graphiti-Local 只完成无数据库的玩具组件测试，Neo4j reset/teardown 仍未验收。见 [当前交接](CURRENT_HANDOFF.md)、[V57 未冻结草案](v57_design/PROTOCOL_DRAFT.json)及[方案审查](docs/V57_MATCHED_PREDECESSOR_REVIEW_20260927.md)。

V55 正式结果和原始收据在 [history/v55_formal](history/v55_formal)；V56 因 clean-clean 分叉按冻结规则停止，**不是 LangMem isolation PASS/FAIL**，完整归档于 [history/v56_cross_backend](history/v56_cross_backend)。V56 的独立回读为 439/439；[决策摘要](history/v56_cross_backend/V56_DECISION_SUMMARY.md)和[迁移审计](history/V56_AND_LEGACY_RELOCATION_AUDIT_20260927.json)可追溯原结果。旧 V56 进度页已关闭。

## 当前入口

- [IDEA.md](IDEA.md)：用户研究 idea，含注明日期的文献补充；旧阶段数字以当前状态和终止收据为准。
- [CURRENT_STATE.json](CURRENT_STATE.json)：机器状态；[CURRENT_HANDOFF.md](CURRENT_HANDOFF.md)：当前交接。
- [V57 设计](v57_design/PROTOCOL_DRAFT.json)：尚未冻结。[计数器审计](v57_design/results/COUNT_UNIT_V1_AUDIT.json)、[检索表示审计](v57_design/results/RETRIEVAL_FOOTPRINT_DRY_RUN.json)、[统计干跑](v57_design/results/PARTIAL_CONJUNCTION_DRY_RUN.json)与[Graphiti 玩具组件审计](v57_design/results/GRAPHITI_LOCAL_COMPONENT_AUDIT.json)只验证离线代码和工程接口。
- [当前 Related Work 对照](docs/literature/RELATED_WORK_CURRENT.md)、[20 条起始参考文献](docs/literature/references.bib)及[10/10 参考文献审计](docs/literature/REFERENCE_LIBRARY_AUDIT.json)。
- [当前 Python 环境说明](v57_design/environment/README.md)与[依赖快照](v57_design/environment/V57_ENV_SNAPSHOT.json)：V57 工程环境隔离，正式运行身份未冻结。
- [显卡服务器准备说明](SERVER_README.md)、[可下载资产清单](v57_design/DOWNLOADABLE_ASSETS.json)、[源码包导出](ops/export_gpu_source.py)和[轻量 Git bundle 导出](ops/export_gpu_git_bundle.py)：历史、模型、环境不进入可迁移源码；服务器按哈希重新获取。
- [科研开发规范](科研开发规范.md)、[已知缺口](KNOWN_GAPS.md)、[变更记录](docs/CHANGE_HISTORY.md)、[历史索引](history/README.md)。

## 目录

```text
IDEA.md / CURRENT_*       当前研究入口
v57_design/               当前未冻结的 V57 方案、代码、离线审计
docs/                     研究方案、文献、变更记录
third_party/agent-memory-server/   当前保留的固定 Redis benchmark 源码
.runtime/                 当前 BGE 缓存与 V57 隔离 Python 环境
ops/                      当前工作流工具
exports/                  当前可分享产物目录
history/                  V42–V56、旧依赖、旧运行环境与迁移清单
```

历史冻结代码中的旧根路径不作内容修改；如需复跑，先阅读 [V56 布局恢复说明](history/V56_REHYDRATION.md)，在隔离工作副本中恢复布局并核对哈希。
