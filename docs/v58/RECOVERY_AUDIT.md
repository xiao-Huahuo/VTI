# V58 恢复与故障演练

2026-09-30 使用 fake client 和真实子进程异常退出执行[首轮演练收据](RECOVERY_DRILL.json)及[补充演练](RECOVERY_DRILL_02.json)，最新 **13/13 检查通过，真实模型调用 0**。

| 场景 | 结果 |
| --- | --- |
| A：trial 未提交时进程死亡 | 部分状态未被标为完成，自动恢复拒绝。 |
| B：trial 完整提交后死亡 | checkpoint 哈希不变，恢复从下一步骤开始。 |
| C：cleanup 开始但未提交时死亡 | 拒绝自动重做 cleanup。 |
| D：raw 响应已保存但步骤未提交时死亡 | 响应保留，未重发请求，恢复拒绝。 |
| E：再次中断后恢复 | 两次已提交步骤链均可回读。 |
| F：freeze、dataset、model、code 身份改变 | 四种漂移均被拒绝。 |
| G：已记录 dispatch、尚无响应时死亡 | 请求被标为不确定，自动恢复拒绝。 |

另以真实 Mem0/Qdrant 持久化后端、拦截的 fake Ollama 客户端执行四 trial sequence，[收据](BACKEND_FAKE_DRILL_03.json)显示 N 的 sidecar 消息跨边界从 2 增至 4、6，V 每次归零；[更新演练](BACKEND_FAKE_DRILL_05.json)通过。该演练不包含真实 Qwen 生成，也不把合成回答作为科学结果。

最后执行了[真实后端跨进程恢复演练](BACKEND_RESUME_DRILL.json)：N/V 两臂均在第一个 trial 和 cleanup checkpoint 后强制退出，再由新进程从原 Qdrant/sidecar 快照继续第二个 trial。**8/8 检查通过**；首个边界 checkpoint 哈希未变，N 的第二次 ingestion 后消息数为 4，V 为 2，证明恢复没有重做已提交 trial 或误清 sidecar。真实模型调用 0。
