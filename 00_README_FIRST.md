# AM-AUTO-20260918-R1 最终迁出包

这是 Agent Memory 自动科研项目 `AM-AUTO-20260918-R1` 的最终沙箱迁出包。

## 内容
- `sandbox_snapshot/mnt_data/`：打包时 `/mnt/data` 下的全部沙箱内容。
- `sandbox_snapshot/mnt_data/final_export/library_archives/`：额外从持久 Research Library 取回的历史累计归档和关键文档。
- `CURRENT_STATE_V40.json`：最后冻结的权威状态。
- `MIGRATION_STATUS.md`：当前阶段、下一步和真实运行环境要求。
- `SANDBOX_CONTENT_MANIFEST.tsv`：全部文件与符号链接清单。
- `SHA256SUMS.txt`：全部普通文件的 SHA256。

本包不保存 API Key、账号凭据或其他秘密信息。后续研究以 V40 为权威起点，脱离本沙箱继续。
