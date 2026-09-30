# Reset Is Not Isolation

> **2026-09-27 文献维护注记：** 下文保留 idea 形成时的原始论证与阶段状态；当时的文献边界和引用现归档在 [`RELATED_WORK_CURRENT.md`](history/pre_v58_root_20260930/docs/literature/RELATED_WORK_CURRENT.md)，参考文献库见 [`references.bib`](history/pre_v58_root_20260930/docs/literature/references.bib)。当时的实验状态以[旧 `CURRENT_STATE.json`](history/pre_v58_root_20260930/CURRENT_STATE.json)和终止收据为准。

> **2026-09-30 新起点注记：** V57 及以前的代码、数据和文档已整体归入 [`history/`](history/README.md)。上文旧的 `docs/` 链接、`CURRENT_STATE.json` 路径及阶段数字均属于归档时的历史语境；对应旧根目录见 [`history/pre_v58_root_20260930/`](history/pre_v58_root_20260930/)。本文件保留原始 idea，不代表 V58 已有协议或实验结果；当前入口以根目录 [`README.md`](README.md) 和 [`科研开发规范.md`](科研开发规范.md) 为准。

## Interventional Auditing and Certification of Cross-Trial State in Agent-Memory Benchmarks

**中文暂定题目：**
**Reset 不等于隔离：Agent-Memory Benchmark 中跨 Trial 状态的干预式审计与认证**

**项目定位：** Agent Memory / Agent Evaluation / Benchmark Methodology
**当前阶段：** Idea-level causal feasibility 已完成；V55 held-out formal experiment 已冻结，正式结果尚未产生
**目标：** CCF-A / ICML / NeurIPS / KDD 等级的 evaluation methodology / empirical systems paper

---

# 1. 研究问题

现代 Agent Memory benchmark 通常把每一个 evaluation case 当作独立样本。

一个典型执行过程为：

```text
Trial i
→ ingest history
→ build/update memory
→ retrieve
→ answer
→ score
→ reset

Trial i+1
→ ingest another history
→ ...
```

公开的 Redis LongMemEval harness 甚至显式把 **per-example isolation and reset** 列为 harness 统一保证的评测条件。

因此，benchmark 实际依赖一个没有被单独验证的假设：

$$
\text{reset succeeds}
\Rightarrow
\text{next trial is independent}
$$

对于无状态 QA benchmark，这个假设通常近似成立。

但现代 memory agent 的完整运行状态不是一个 vector database，而可能包含：

$$
S=
(
S^{vector},
S^{message},
S^{history},
S^{entity},
S^{metadata},
S^{cache},
S^{queue},
S^{runtime},
S^{external}
)
$$

其中部分状态可能：

* 不属于 benchmark adapter 显式管理范围；
* 被 provider 内部持久化；
* 由异步任务重新生成；
* 由前一次 LLM extraction 派生；
* 使用共享 namespace；
* 存在于 process-local runtime；
* reset 之后仍然能够进入下一次 computation。

于是：

$$
R(S_i)\neq S_0
$$

其中 $R$ 是 benchmark 使用的 native reset，$S_0$ 是真正 pristine initialization。

如果这个残留状态进一步改变 Trial $i+1$，那么 benchmark 的独立样本假设被破坏：

$$
Y_{i+1}
=
F(X_{i+1},R(S_i))
\neq
F(X_{i+1},S_0)
$$

这里的核心问题不是：

> 某个 memory backend 有没有一个 reset bug？

而是：

> **对于声称 case 独立的 stateful benchmark，我们有什么证据证明上一 case 不会改变下一 case 的测量结果？**

---

# 2. 已知 prior art 对本项目的约束

经过最新查重，必须主动放弃以下 novelty 表述。

## 2.1 不能声称首次发现 reset 不彻底

Mem0 已经公开出现多种 reset / isolation failure。

例如：

* Valkey backend 中，删除 index 后底层 documents 仍存在，重新建立 index 后旧 memory 重新出现；
* 某些 local Qdrant 环境中，collection reset 不能真正清除底层 point；
* rolling message buffer 会把上一 session 的 stale message 带入下一 session 的 extraction context。

因此：

> **Mem0 reset failure 是现实动机和 case study，不是本文首要科研贡献。**

---

## 2.2 不能声称首次提出 cross-run separation

2026 年 8 月的：

**When Is an Agent Evaluation Over? Outcome Finality and Cross-Unit Separation**

已经明确提出：

* outcome finality；
* cross-unit separation；

并通过 delayed write 证明：

```text
shared state
→ previous run changes next run score

verified reset / isolation
→ effect disappears
```

因此本文不能把：

> “Agent evaluation runs should be isolated”

本身作为 novelty。

---

## 2.3 不能声称首次提出 counterfactual clean-state equivalence

2026 年 9 月：

**Forgetting Without Restarting: Execution-State Unlearning for Stateful LLM Agents**

已经正式定义：

> 删除后状态应该与“从未见过目标信息”的 counterfactual twin 等价。

并提出 checkpoint + selective replay，从 prompt、memory 到 KV cache 修复派生状态。

因此：

> behavior-as-if-never-observed

以及：

> counterfactual state reconstruction

也不能作为本文首创。

---

# 3. 查重后真正剩余的研究空白

现有工作分别覆盖了：

```text
Cross-Unit Separation
→ evaluation units 不应共享状态

Execution-State Unlearning
→ 一个持续运行 Agent 如何删除某段历史信息的派生影响

ForgetEval
→ memory control plane 中 supersede / release / purge 是否正确

MemDelta
→ memory benchmark 中 model / embedding / retrieval 等配置混杂

Auto Benchmark Audit
→ task specification / environment / grader 的 benchmark defects

Temporal Intervention Evaluation
→ persistent user state 下 intervention 如何跨组件传播

Task-Order Fragility
→ intentionally self-improving agents 对任务顺序敏感
```

但它们没有直接解决下面这个更窄的问题：

> **对于一个宣称 evaluation cases 相互独立的 agent-memory benchmark，如何以黑盒干预方式检验 predecessor trial 是否仍能影响 target trial；如何在 LLM 本身具有随机性的情况下进行因果识别；如何量化这种 influence 对 case order、aggregate score 和 system ranking 的影响；以及如何找到满足 isolation 条件的最低成本 reset policy。**

这成为本文最终研究边界。

---

# 4. 核心概念：Trial Isolation

设 benchmark target case 为 $x_j$。

如果直接从 pristine state 运行：

$$
Z_j^{0}
=
E(x_j,S_0,\xi)
$$

其中：

* $E$：完整 evaluation pipeline；
* $S_0$：pristine state；
* $\xi$：LLM sampling、runtime noise 等随机因素；
* $Z$：可观察 endpoint。

现在先执行 predecessor case $x_i$：

$$
S_i
=
T(S_0,x_i)
$$

再调用 benchmark native reset：

$$
S_i^R
=
R(S_i)
$$

之后运行相同 target：

$$
Z_{i\rightarrow j}^{R}
=
E(x_j,S_i^R,\xi)
$$

如果 benchmark 声称两个 trials 独立，那么应满足：

$$
\mathcal L
\left(
Z_{i\rightarrow j}^{R}
\right)
\approx
\mathcal L
\left(
Z_j^{0}
\right)
$$

其中 $\mathcal L$ 表示结果分布。

本文把这一定义称为：

## Trial Isolation Property

对于指定 predecessor 集合 $\mathcal P$、target 集合 $\mathcal T$ 和 endpoint $Z$：

$$
D
\left[
\mathcal L(Z_{i\rightarrow j}^{R}),
\mathcal L(Z_j^0)
\right]
\le \epsilon
$$

对审计范围中的 $(i,j)$ 成立。

关键点：

> **Isolation 是一个需要被测量的性质，而不是 reset API 的返回值。**

---

# 5. Hidden Trial State

如果：

$$
R(S_i)\neq S_0
$$

但这部分差异从 benchmark 可见 primary store 中看不到，则定义：

$$
H_i=R(S_i)\setminus S_0
$$

为 Hidden Trial State。

只有满足：

$$
H_i
\rightarrow
Z_j
$$

时，它才是 **behaviorally active hidden state**。

本文不把单纯残留文件、数据库行或缓存定义为 benchmark contamination。

必须证明：

> 它进入下一 trial 的真实 computation，或者能够改变下一 trial 的 observable outcome。

---

# 6. Failure Propagation Chain

在 Agent Memory 中，一个跨 trial residue 可以经过：

$$
H_i
\rightarrow
P_j
\rightarrow
M_j
\rightarrow
R_j
\rightarrow
A_j
\rightarrow
C_j
$$

其中：

* $H$：hidden residual state；
* $P$：下一 trial 的 prompt / computation input；
* $M$：memory representation；
* $R$：retrieval；
* $A$：answer；
* $C$：correctness / score。

对应五级 evidence：

### E1 — Residual Activation

上一 trial 状态在 reset 后仍然存在，并进入下一 trial computation。

### E2 — Representation / Retrieval Effect

native-reset 与 pristine / verified-clean 在 memory 或 retrieval 上发生超出 null variation 的差异。

### E3 — Answer Effect

$$
A^{native}\neq A^{clean}
$$

### E4 — Correctness Effect

$$
Correct(A^{native})
\neq
Correct(A^{clean})
$$

### E5 — Benchmark-Level Distortion

$$
Score_{native}\neq Score_{isolated}
$$

或进一步：

$$
Ranking_{native}\neq Ranking_{isolated}
$$

本文真正的 A 类目标是从 E1/E2 推进到 E5。

---

# 7. 为什么 clean-clean control 是必要的

LLM 本身具有随机性。

即使：

```text
same state
same prompt
same model
temperature = 0
```

也可能产生：

```text
different extraction
different memory
different retrieval
different answer
```

本项目此前 V42–V44 已经实际观察到这一点。

因此：

$$
Z^{native}\neq Z^{clean}
$$

本身不能证明 treatment effect。

必须首先测量：

$$
Z^{clean_1}
\quad vs \quad
Z^{clean_2}
$$

得到 null variation。

定义：

$$
D_0(j)
=
D
(
Z_j^{clean_1},
Z_j^{clean_2}
)
$$

在 stochastic setting 中重复得到：

$$
\mathcal D_{null,j}
$$

只有：

$$
D
(
Z_{i\rightarrow j}^{native},
Z_j^{clean}
)
>
Q_{1-\alpha}
(
\mathcal D_{null,j}
)
$$

才认为存在 calibrated cross-trial influence。

这是本文相对于普通：

```text
before reset
after reset
```

实验的关键区别。

---

# 8. Proposed Method：VTI

本文提出：

# Verified Trial Isolation（VTI）

VTI 不是新的 reset algorithm。

它是：

> **一套对 stateful benchmark 的 trial independence 进行干预式审计、定位、修复和认证的方法。**

VTI 分为两个运行模式：

```text
Audit Mode
→ 判断 native benchmark 是否满足 isolation

Certified Execution Mode
→ 使用已经通过审计的最低成本隔离方案运行正式 benchmark
```

---

# 9. VTI-A：Null-Calibrated Target Replay

对于 target $x_j$，首先执行两个独立 pristine / verified-clean arm：

```text
clean_ref
clean_rep
```

估计 target 自身的 stochastic variation。

随后执行：

```text
predecessor x_i
→ native reset
→ target x_j
```

得到 treatment arm。

形成：

```text
clean_ref
clean_rep
native_after_predecessor
```

只有 Stage A：

```text
clean_ref ≈ clean_rep
```

通过以后，Stage B 的 native-clean difference 才能被解释。

---

# 10. VTI-B：Cross-Trial Influence Matrix

单个 case pair 只能证明 existence。

为了研究 contamination structure，定义：

$$
C_{ij}
=
I(x_i\rightarrow x_j)
$$

其中：

$$
I(x_i\rightarrow x_j)
=
\max
\left(
0,
D_{ij}^{treatment}
-
Q_{1-\alpha}(\mathcal D_{null,j})
\right)
$$

得到：

# Cross-Trial Influence Matrix

$$
\mathbf C=
[C_{ij}]
$$

它回答：

* 哪些 predecessor 容易留下影响；
* 哪些 target 容易被污染；
* 是否只存在局部 pair；
* 是否存在高影响 predecessor；
* effect 是否与 session count / memory count / task type 有关。

这比只报告：

```text
8/12 case changed
```

提供更强的机制解释。

---

# 11. VTI-C：Order-Invariance Test

这是终稿新增的关键设计。

对于一个声称：

> cases are independent

的 benchmark，改变 case 顺序理论上不应该系统性改变最终能力估计。

设 benchmark case permutation 为：

$$
\pi
$$

native 执行得到：

$$
Score^{native}_{\pi}
$$

如果存在跨 trial contamination，则：

$$
Score^{native}_{\pi_1}
\neq
Score^{native}_{\pi_2}
$$

可能不再只是正常模型 sampling noise，而是由：

$$
x_i\rightarrow x_j
$$

的顺序关系导致。

因此运行：

```text
Order π1
Order π2
Order π3
...
```

同时建立：

```text
same-order stochastic replicate
```

估计 null variance。

定义：

$$
OD
=
Var_{\pi}(Score_{\pi})
-
Var_{null}(Score)
$$

或者使用 permutation-conditioned distributional test。

如果：

```text
native reset
→ strong order dependence

VTI-certified isolation
→ order dependence disappears
```

则可以直接证明：

> hidden trial state 已经从 implementation detail 上升为 benchmark measurement distortion。

---

# 12. 与 Self-Improving Agent Task-Order 工作的区别

2026 年已有工作证明：

> memory-based self-improving agents 对 task order 很敏感。

但那里：

```text
previous task
→ memory
→ future task
```

是算法设计中**有意允许**的 cross-task learning。

本文研究的是：

```text
previous benchmark case
→ unintended hidden residue
→ next independent benchmark case
```

即：

> 对于协议上声称独立的 evaluation units，order dependence 本身就是 measurement failure。

两者必须在论文中明确分开。

---

# 13. VTI-D：State Surface Localization

发现 influence 后，下一问题是：

> 什么状态造成了它？

对系统可观察 state surfaces 建立 registry：

$$
\mathcal S
=
\{
S_1,\ldots,S_k
\}
$$

例如：

```text
vector store
message buffer
history DB
entity index
metadata
filesystem
cache
background queue
runtime/session state
```

逐级收集：

```text
count
scope
content fingerprint
namespace
generation
timestamp
```

但：

> surface registry 只用于 localization，不用于证明 isolation。

因为未知 state surface 永远可能存在。

真正的 isolation evidence 仍来自 interventional target replay。

---

# 14. VTI-E：Reset Policy Ladder

对于发生 contamination 的配置，定义 reset policies：

$$
R_0,R_1,R_2,\ldots,R_k
$$

例如：

```text
R0  native reset

R1  declared-surface verified cleanup

R2  fresh logical namespace / run id / workspace

R3  fresh backend instance

R4  fresh process / container
```

对每一种 policy 做同样的 VTI test。

寻找：

$$
R^*
=
\arg\min_R Cost(R)
$$

满足：

$$
Isolation(R)\ge\tau
$$

这形成：

# Minimum-Cost Certified Isolation

目标不是发明最复杂的 cleanup。

如果：

```text
fresh namespace
```

已经足够且成本最低，那么论文应该诚实推荐 fresh namespace。

---

# 15. VTI-F：Isolation Certificate

每一个被审计的：

```text
benchmark
× adapter
× backend
× model
× runtime
```

最终产生一个 scope-bounded certificate：

```text
PASS
FAIL
UNVERIFIABLE
```

Certificate 包含：

```text
benchmark commit
adapter commit
backend version
model digest
runtime
hardware / OS
target set
predecessor set
null repetitions
distance metrics
ε / α
tested reset policy
state-surface receipts
order test
timestamp
artifact hashes
```

重要的是：

> VTI certificate 不是“这个产品永远安全”。

而是：

> **在这个明确冻结的 evaluation configuration 和审计范围内，没有观察到超出预定义阈值的 predecessor influence。**

---

# 16. 为什么 VTI 不只是 Fresh Instance

最简单的 isolation 方法显然是：

```text
每个 case 创建一套新容器 / backend
```

但这有三个问题：

1. hosted memory system 未必支持完全重建；
2. 数据 ingest 和服务启动成本可能很高；
3. benchmark 原本声称 reset 足以隔离，那么首先需要知道它是否真的足够。

VTI 的目标不是取代 fresh instance。

而是回答：

```text
native reset 足够吗？
        │
        ├─ 是 → 不增加额外成本
        │
        └─ 否
            ↓
        最便宜的哪一种 stronger reset 可以达到同样隔离？
```

---

# 17. 当前已经完成的验证

## 17.1 Redis × Mem0

当前 selected pilot / extension 共 4 个 calibrated cases。

所有 case 均先通过 case-specific：

```text
clean_ref == clean_rep
```

随后 native reset 相对于 verified clean 均观察到：

```text
memory difference
retrieval difference
answer-text difference
```

因此当前支持：

```text
E1 positive
E2 positive
E3 possible
```

但这 4 个 case 参与过研究开发：

> 不允许用于 population prevalence。

---

# 18. MemArena × Mem0

第二条真实 integration 中已经观察到：

```text
native reset
→ residual message state
→ next extraction input
```

并在一个真实 case 上完成 clean-clean calibrated replay。

结果：

```text
E1 positive
E2 positive
E3 text null
```

其中：

```text
memory count: 49 vs 57
Top-5 retrieval overlap: 0
final answer: identical
```

这个 null 非常重要。

它说明：

> E2 并不必然传播到 E3。

---

# 19. 当前 E4

V49 对已经保存的 V48 answers 做补充性 correctness evaluation。

结果：

```text
1 case:
native correct / clean incorrect

2 cases:
both incorrect
```

这里有一个非常重要的科学含义：

> contamination 不一定降低 benchmark score。

它可能：

```text
harm
help
or leave correctness unchanged
```

因此本文从现在开始不应使用：

```text
performance degradation
```

作为默认 framing。

应该使用：

# Measurement Distortion

因为 hidden state 可能同时产生：

$$
\Delta Score>0
$$

或：

$$
\Delta Score<0
$$

---

# 20. V55 正式 Held-Out Experiment

**状态：协议已冻结，正式结果尚未产生。**

V55 使用 12 个完全不参与 protocol development 的 held-out cases：

```text
SHA256 cohort ranks 13–24
```

正式 case 不允许：

* 根据中间结果替换；
* 增减 denominator；
* 与 V47/V48 pilot 合并计算 prevalence；
* 在结果出来后修改 threshold；
* calibration failure 后重复运行直到通过。

每 case：

```text
clean_ref
clean_rep
native
```

Primary endpoint：

```text
E2 calibrated memory / retrieval effect
```

Secondary：

```text
E3 answer-text effect
```

Task endpoint：

```text
E4 correctness transition
```

---

# 21. V55 的作用

V55 不再回答：

> hidden trial state 是否存在？

这个问题已经完成 feasibility。

它回答：

> 在完全 held-out 的正式样本中，已观察到的 causal effect 能否继续复现？

如果 V55 大部分有效 case 均为 E2 positive，则进入更大的 VTI study。

如果基本全部 null，则论文必须收缩：

```text
general trial-isolation threat
```

到：

```text
specific lifecycle failure mode
```

---

# 22. A-Level Study 1：Cross-Backend Audit

当前最大的 reviewer attack 是：

> 这是不是 Mem0-specific？

因此 V55 之后必须加入独立 backend。

Redis harness 当前已经提供多个 adapter，包括：

```text
Mem0
LangMem
Zep
Graphiti
Supermemory
Redis Agent Memory
Google Vertex Memory Bank
AWS Bedrock AgentCore
Oracle Agent Memory
```

不需要全部测试。

A 类版本至少选择：

```text
≥ 3 memory backends
```

其中至少：

```text
≥ 1 independent OSS backend
```

不是 Mem0。

重要的是允许：

```text
Backend A PASS
Backend B FAIL
Backend C PASS
```

VTI 的价值恰恰是区分：

> isolation-safe 和 isolation-unsafe configurations。

---

# 23. A-Level Study 2：Cross-Harness Replication

建议至少保留两个 execution paths：

```text
LongMemEval-style Redis harness
MemoryArena integration
```

如果资源允许再加入第三种 stateful harness。

目的不是证明所有 benchmark 都坏。

而是检验：

> isolation auditing 是否具有 harness-level portability。

---

# 24. A-Level Study 3：Broad First-Transition Audit

完整三臂 replay 成本高。

因此把 breadth 和 depth 分开。

对于更大样本：

```text
100–500 targets
```

只运行：

```text
predecessor
→ reset
→ first target transition
```

检测：

```text
prompt
request
response
first memory mutation
```

作为廉价 E1/E2 early-layer audit。

这不能替代完整 causal study，但可以测：

> reset-isolation failure 的覆盖范围。

---

# 25. A-Level Study 4：Deep Causal Subset

从正式预注册的 stratified subset 中选：

```text
30–60 target cases
```

完整执行：

```text
clean_ref
clean_rep
native
```

并测：

```text
memory
retrieval
answer
correctness
```

分层至少考虑：

```text
question type
history length
session count
memory volume
predecessor state volume
```

---

# 26. A-Level Study 5：Predecessor Stress Design

不能只测试：

```text
上一条恰好是什么 case
```

应设计 predecessor classes：

### P1 — Random Real Predecessor

代表普通 benchmark order。

### P2 — High-State Predecessor

产生大量：

```text
messages
memories
entities
metadata
```

用于 stress test。

### P3 — Semantically Related Predecessor

检测语义相近 case 是否更容易通过 residual state 传播。

### P4 — Semantically Unrelated Predecessor

作为对照。

### P5 — Canary Predecessor

加入高 entropy、任务无关 witness，用于 localization。

最终不是穷举：

$$
N^2
$$

pair，而是预注册 stratified pair sample。

---

# 27. A-Level Study 6：Cross-Trial Influence Matrix

在 sampled predecessor-target pairs 上建立：

$$
\mathbf C
$$

可以进一步计算：

### Predecessor Influence

$$
PI_i
=
E_j[C_{ij}]
$$

表示：

> case $i$ 作为 predecessor 时多容易污染别人。

### Target Susceptibility

$$
TS_j
=
E_i[C_{ij}]
$$

表示：

> target $j$ 多容易被之前状态改变。

然后分析：

$$
PI_i
$$

与：

```text
state volume
message count
entity count
session count
```

的关系。

---

# 28. A-Level Study 7：Order Distortion

在至少两个存在 native isolation failure 的 backend 上，对相同 case subset 运行多个预注册 order：

```text
π1
π2
π3
...
```

分别比较：

```text
Native reset
VTI-certified reset
```

核心结果：

$$
Score^{native}_{\pi}
$$

是否具有超过 sampling null 的 order variation。

进一步测试：

$$
Var_{\pi}
(
Score^{VTI}_{\pi}
)
<
Var_{\pi}
(
Score^{native}_{\pi}
)
$$

如果成立，这是论文最强的 benchmark-validity evidence 之一。

---

# 29. A-Level Study 8：Score Distortion

定义：

$$
\Delta Score
=
Score_{native}
-
Score_{VTI}
$$

注意：

$$
\Delta Score
$$

可以正，也可以负。

真正的问题不是：

> native 一定更差。

而是：

> native benchmark 是否测到了不同的 quantity。

如果评测多个 memory systems，还比较：

$$
Ranking_{native}
$$

与：

$$
Ranking_{VTI}
$$

如果 system ranking 发生变化，论文从 case-level audit 上升到 leaderboard validity。

---

# 30. A-Level Study 9：Reset Policy Comparison

对于 isolation-failing backend 比较：

```text
native reset
verified surface cleanup
fresh namespace
fresh backend instance
fresh process/container
```

评价两个轴：

## Isolation

$$
I(R)
$$

## Cost

$$
C(R)
$$

最终报告 Pareto frontier：

```text
isolation guarantee
vs
runtime / compute / API / storage cost
```

VTI 推荐的是：

$$
\arg\min_R C(R)
\quad
s.t.
\quad
I(R)\ge\tau
$$

---

# 31. Metrics

## 31.1 Calibrated Trial Isolation Failure Rate

$$
TIFR
=
\frac{
N_{influence-positive}
}{
N_{calibration-valid}
}
$$

calibration failure 不计为 negative。

---

## 31.2 Cross-Trial Influence

$$
I_{ij}
=
\max
(
0,
D_{ij}
-
Q_{1-\alpha}(\mathcal D_{null,j})
)
$$

---

## 31.3 Answer Shift Rate

$$
ASR
=
P
(
A^{native}\neq A^{isolated}
)
$$

---

## 31.4 Correctness Transition

分四类报告：

```text
clean correct / native wrong
clean wrong / native correct
both correct
both wrong
```

---

## 31.5 Order Distortion

比较：

```text
cross-order variance
vs
same-order stochastic variance
```

而不是只报告原始 variance。

---

## 31.6 Benchmark Distortion

$$
\Delta Score
=
Score_{native}
-
Score_{certified}
$$

---

## 31.7 Ranking Stability

对于系统 $a,b$：

$$
Rank_{native}(a,b)
$$

是否与：

$$
Rank_{certified}(a,b)
$$

一致。

---

# 32. 正式 E4

当前硬约束：

> 不依赖 OpenAI API。

V55 evaluator 已在结果生成前冻结。

对于：

```text
native answer == clean answer
```

不调用 judge。

对于：

```text
native answer != clean answer
```

分别评价：

```text
(question, reference, native)
(question, reference, clean)
```

而不是：

```text
Which answer is better?
```

固定：

```text
same rubric
same model
same prompt
temperature = 0
3 independent votes
majority decision
```

保存全部 disagreement。

正式论文明确写：

> LongMemEval-style rubric using a fixed non-GPT-4o evaluator.

不能称作 official LongMemEval GPT-4o score。

---

# 33. 与高危竞品的边界

## 33.1 Cross-Unit Separation

**危险等级：最高。**

它已经占据：

> evaluation runs should be separated。

本文必须强调：

它解决的是：

```text
是否有 evidence 把不同 evaluation units 当独立 trial
```

本文进一步研究：

```text
memory-specific hidden state
+
black-box influence quantification
+
stochastic null calibration
+
predecessor-target graph
+
order-level score distortion
+
minimum-cost isolation policy
```

---

## 33.2 Mem0 Reset / Message Issues

**危险等级：最高，但属于 prior art，不是竞争论文。**

这些 issue 已经公开具体 bug。

因此本文绝不能依赖：

> 我们首先发现 Mem0 message 没清。

应在 Related Work / Motivation 中主动引用。

---

## 33.3 Execution-State Unlearning

**危险等级：高。**

它已经占据：

```text
counterfactual equivalence
cross-layer state contamination
checkpoint-and-replay
```

本文不能复制其：

> behavior-as-if-never-seen

作为主要方法创新。

区别：

```text
Execution-State Unlearning
→ one running agent
→ revoke one target item
→ reconstruct contaminated suffix

VTI
→ independent benchmark units
→ detect whether previous unit changes next unit
→ certify evaluation isolation
```

---

## 33.4 ForgetEval

**危险等级：高。**

ForgetEval 已经：

```text
13 configurations
1000 templated cases
385 adversarial cases
supersede / release / purge
adapter protocol
```

因此本文不能把：

> memory control plane is under-evaluated

作为 novelty。

本文针对：

> benchmark lifecycle boundary，而不是 memory item mutation semantics。

---

## 33.5 MemDelta

**危险等级：高。**

MemDelta 已经建立：

> memory evaluation conclusions can be flipped by hidden configuration confounds。

本文应该把自己定位为其补充：

```text
MemDelta
→ configuration confounds

VTI
→ lifecycle dependence between evaluation units
```

---

## 33.6 Auto Benchmark Audit

**危险等级：高，未来最可能直接扩张到本领域。**

ABA 已经有：

```text
benchmark audit
environment defects
ranking distortion
large-scale automation
```

如果 ABA 下一版加入 runtime lifecycle / cross-run state，它会直接进入本文领域。

因此本文必须抢先建立：

```text
stateful-memory specific formalism
interventional isolation test
null calibration
order distortion
```

而不是只做 static audit。

---

## 33.7 Temporal Intervention Evaluation

**危险等级：中高。**

该工作已经提出：

```text
persistent state
temporal intervention
cross-component propagation
```

但目前是 personal-agent evaluation position paper。

本文区别：

```text
user-conditioned persistent state
≠
unintended evaluation-unit residue
```

---

## 33.8 Always-On Evaluation Protocol

**危险等级：中高。**

AOEP 已经把：

```text
state mutation
recovery
rollback
governance
```

纳入 always-on agent evaluation。

本文必须保持：

> benchmark trial independence measurement

这个更窄的边界。

---

## 33.9 Task-Order Fragility

**危险等级：中。**

已有 self-improving agent 工作发现 task order 会显著影响结果。

但它的 cross-task memory 是 intended。

本文中的 order dependence 是：

> benchmark 声称独立时出现的 unintended carryover。

---

## 33.10 Engineering Harnesses

**危险等级：中。**

新的 harness 已经开始提供：

```text
per_trial fresh container
task-local memory
fresh stack
```

这说明工程社区正在快速补 isolation。

因此：

> “每 case 开新容器”

不是研究贡献。

研究贡献必须是：

> 如何知道什么时候需要它，以及更便宜的 reset 是否已经足够。

---

# 34. 未来最危险的竞争方向

## Threat A — Mem0 / Redis 自己快速修复

具体 bug 很可能在论文投稿前消失。

应对：

* pin historical version；
* 保留 reproducible artifact；
* 不把 bug existence 当主要 novelty；
* 加入独立 backend。

---

## Threat B — ABA 扩展到 Runtime Lifecycle

这是最危险的论文竞争者。

如果 ABA 加入：

```text
run A
→ reset
→ run B
```

动态审计，本文 generic benchmark-audit novelty 会明显下降。

应对：

尽快完成：

```text
memory-specific influence matrix
stochastic calibration
order distortion
certification
```

---

## Threat C — ForgetEval 增加 Reset Primitive

其 adapter protocol 已经非常接近。

如果新增：

```text
reset semantics
cross-session leakage
```

会与本文明显靠近。

应对：

本文重点必须是：

```text
evaluation case independence
```

而不是 memory delete correctness。

---

## Threat D — Execution-State Unlearning 扩展到 Evaluation Boundaries

如果该团队把 full-reset counterfactual 用到 benchmark case boundary，也会产生重叠。

应对：

VTI 的贡献必须集中在：

```text
measurement design
pair sampling
null calibration
order distortion
score correction
```

而不是 state reconstruction algorithm。

---

## Threat E — Cross-Unit Separation 后续工作

这是最直接的危险竞争者。

如果它下一版增加：

```text
memory systems
multiple backends
statistical certification
```

将非常接近。

因此本项目需要尽快做出：

```text
agent-memory-specific large empirical evidence
```

而不能停在 conceptual paper。

---

# 35. Falsification Criteria

## K1 — V55 Held-Out Failure

如果 12 个正式 held-out case 中，大部分 calibration valid，但 E2 几乎全为 null：

停止 general threat claim。

论文降级为：

> specific demonstrated lifecycle failure.

---

## K2 — Mem0 Only

如果多个独立 backend 均稳定通过 isolation，只有 Mem0 failure：

不能声称：

> agent-memory benchmarks generally suffer isolation failure.

只能声称：

> VTI identifies implementation-specific evaluation failures.

---

## K3 — No Score Effect

如果 E2 常见，但：

```text
E3 / E4 / aggregate score
```

几乎不变：

不能声称 leaderboard invalid。

只能声称：

> internal evaluation state is not isolated, but observed task-level impact is limited.

---

## K4 — No Order Effect

如果不同 case permutations 在 native 与 VTI 下没有超出 null 的 score difference：

不使用：

> benchmark order distortion

作为主结论。

---

## K5 — Fresh Namespace Solves Everything

如果：

```text
fresh namespace
```

已经可靠达到 isolation，并且开销几乎为零：

最终 mitigation 应该就是 fresh namespace。

不要为了方法复杂度继续设计额外算法。

---

# 36. 预期贡献

如果 A 类实验全部完成，论文贡献可以收敛为四项。

## C1 — Formalization

针对 stateful agent-memory benchmark，将 **trial isolation** 定义为：

> target outcome 对 admissible predecessor history 的 interventional invariance。

---

## C2 — Measurement Method

提出 VTI：

```text
null-calibrated replay
cross-trial influence measurement
state localization
order-invariance stress test
minimum-cost reset certification
```

---

## C3 — Empirical Audit

跨：

```text
multiple memory backends
multiple harnesses
held-out cases
```

量化真实 cross-trial influence。

---

## C4 — Benchmark Reassessment

比较：

```text
native reset evaluation
vs
certified-isolation evaluation
```

量化：

```text
score distortion
order sensitivity
ranking stability
cost
```

---

# 37. 最终论文最重要的结果应该长什么样

最理想的主结果不是：

> 我们发现某个表没清空。

而是：

```text
Native benchmark:
case order changes score by X
system A > system B

After VTI-certified isolation:
order effect falls to null range
system ranking changes / stabilizes
```

或者：

```text
Backend A native reset PASS
Backend B native reset FAIL
Backend C native reset FAIL

B:
fresh namespace is sufficient

C:
fresh process is required
```

这才证明：

> VTI 测量的是一个真实且有区分度的 benchmark property。

---

# 38. 论文主线

最终不要写成：

```text
Mem0 has stale messages.
```

也不要写成：

```text
Reset APIs are unreliable.
```

更不要写成：

```text
Persistent state can influence future behavior.
```

这些都已有充分 prior art。

最终应写成：

> **Stateful agent benchmarks often treat reset as sufficient evidence that evaluation units are independent. Existing work has established the need for cross-unit separation and documented concrete reset failures, but does not provide a memory-specific, stochasticity-calibrated method for measuring predecessor-to-target influence or quantifying its effect on benchmark order and aggregate conclusions. We study trial isolation as an interventional property, measure its violations, and certify the lowest-cost reset policy that restores evaluation invariance.**

---

# 39. 推荐标题

首选：

## Reset Is Not Isolation: Interventional Auditing of Cross-Trial State in Agent-Memory Benchmarks

如果最终做出了明显 aggregate score distortion：

## Reset Is Not Isolation: Cross-Trial State Distorts Agent-Memory Evaluation

如果 VTI method 成为论文中心：

## Verified Trial Isolation for Stateful Agent-Memory Benchmarks

不建议继续使用：

```text
Hidden Trial State in Agent-Memory Benchmarks
```

作为最终主标题。

原因是：

> “hidden state / cross-unit leakage”本身已经过于接近现有文献。

---

# 40. 当前项目状态

截至 2026-09-25：

```text
Specific failure existence
→ 已验证

Redis×Mem0 E1
→ 已验证

Redis×Mem0 calibrated E2
→ 4 selected cases 已验证

Redis×Mem0 E3
→ 4 selected cases observed

MemArena×Mem0 E1
→ 已验证

MemArena×Mem0 calibrated E2
→ 1 case 已验证

MemArena E3
→ 当前 case null

Correctness change
→ 有 pilot evidence，不是 prevalence

V55
→ 正式 held-out protocol frozen
→ 12 cases
→ 0/12 formal outcomes

Cross-backend study
→ 未开始

Cross-Trial Influence Matrix
→ 未开始

Order-invariance study
→ 未开始

Native-vs-certified score distortion
→ 未开始

VTI implementation
→ 方法已定义，正式实验未开始
```

---

# 41. 从当前到 A 类投稿的执行顺序

严格保持 V55 不动。

```text
Step 1
Run frozen V55
↓
12-case held-out result

Step 2
Analyze V55
↓
决定是否继续 A-level expansion

Step 3
Implement VTI audit harness
↓
clean calibration
pair intervention
surface receipts
reset ladder

Step 4
Add independent memory backends
↓
至少 3 backend

Step 5
Broad first-transition audit
↓
larger target sample

Step 6
Stratified deep causal study
↓
30–60 cases

Step 7
Cross-Trial Influence Matrix
↓
predecessor / target structure

Step 8
Order-invariance experiment
↓
native vs certified

Step 9
Aggregate score / ranking reassessment

Step 10
VTI cost + ablation + artifact release
```

---

# 42. 最终判断

经过这轮查重后，原始 idea 中有三块已经不能再作为 novelty：

```text
reset bug
cross-run separation
counterfactual clean equivalence
```

但研究并没有失去价值。

它应该被进一步收缩为一个更难被替代的问题：

> **How can we empirically establish that the outcome of one stateful benchmark case is invariant to the cases executed before it?**

这才是最终核心。

形式上：

$$
\boxed{
\text{Trial isolation}
=
\text{interventional predecessor invariance}
}
$$

而 reset 只是尝试实现这个性质的一种操作。

因此整篇论文最核心的一句话应为：

> **Reset is an operation. Trial independence is an empirical property.**

本文要做的，就是测量、定位、量化并认证这个 property。

---

# 43. 2026-09-27 文献补充（不改写上文历史论证）

V32 已发现、但上文未点名的 [Agentic Benchmark Checklist](https://arxiv.org/abs/2507.02825) 和 [MemSecBench](https://arxiv.org/abs/2607.27080) 必须进入最终 Related Work。前者占据独立任务应清理残余状态的规范性主张；后者已有 agent-memory 的隔离运行、匹配分支和后端状态证据。C33 不能把这些通用做法单独说成新贡献。

新增相关工作 [A-TMA](https://arxiv.org/abs/2607.01935) 已将 memory bank、retrieval、answer 的失效层次拆开；[Scope Before You Persist](https://arxiv.org/abs/2609.29144) 已研究持久 skill 的跨任务家族干扰与作用域匹配；[DolphinBench](https://arxiv.org/abs/2609.24971) 已强调 agent-memory 任务结果、成本和延迟。C33 的剩余差异是：**对声称彼此独立的 benchmark case，干预前例并测量 native reset 后目标 case 的依赖性及评测后果**。不能声称首次提出分层失效、memory scope、顺序敏感或成本感知评测。

V57 拟用的 Fisher sharp-null 随机化检验、energy statistic 和 2-of-3 partial conjunction 都是已有统计方法，应分别引用 [Wu–Ding](https://doi.org/10.1080/01621459.2020.1750415)、[Székely–Rizzo](https://doi.org/10.1016/j.jspi.2013.03.018) 和 [Benjamini–Heller](https://doi.org/10.1111/j.1541-0420.2007.00984.x)。潜在新贡献是将它们以正确的实验单元、随机化与无干扰约束用于 agent-memory benchmark 的 trial boundary；V57 仍未冻结，不能在论文里写成已完成结果。

逐篇 claim 边界、版本承接和仍待核查的文献见归档的 [`RELATED_WORK_CURRENT.md`](history/pre_v58_root_20260930/docs/literature/RELATED_WORK_CURRENT.md) 与 [`LITERATURE_LINEAGE_AUDIT_20260927.md`](history/pre_v58_root_20260930/docs/LITERATURE_LINEAGE_AUDIT_20260927.md)。
