# Reserve Idea C18: Policy-Epoch Memory Reauthorization

核心现象：memory 的事实内容仍然真实，但 policy epoch 变化后，其“允许如何使用”的授权语义已经变化。  
候选机制：将 use authorization 与 memory content 分离，绑定 policy epoch，在 policy change 时做 dependency-aware reauthorization。  
当前状态：RESERVE。  
原因：与 PolicyBank、persistent-memory governance spec、authority laundering 和 policy-version architecture 的边界较近。进入主线前需要更深一轮 prior-art 审计，因此本轮不列为正式幸存 Idea。
