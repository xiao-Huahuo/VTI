# CHANGE HISTORY V15

## 2026-09-18

- C28 reverse novelty audit found direct prior experiment in `AlekseiMarchenko/agent-memory-benchmark` commit `4b72bea0f6710ca48ee0fd856e9e8473e169eca2`: the same benchmark is reported at 3 s and 10 s store delays, with large Zep and Mem0 score changes. C28 is killed under the Prior-Art Kill Contract.
- Started replacement screening without rebranding C28.
- C30 False Quiescence survived initial novelty review in a narrow form. A source-level counterexample proves count-stability readiness does not logically imply semantic-state stability. Real post-ready drift remains unverified.
- C31 Measurement-Induced Memory Mutation survived initial novelty review. Current `rohitg00/agentmemory` code provides a complete read -> persistent access state -> retention score -> eviction path.
- A source-derived boundary fixture using the audited production formula shows a 180-day factual memory below the default eviction threshold can be moved above the threshold by one read for roughly 4.43 days. This is not runtime evidence.
- Current sandbox has no cached target implementation, Docker/Redis service, cloud provider keys or outbound DNS, so real C30/C31 runtime pilots remain blocked in this environment. BLOCKED is not treated as PASS or FAIL.
- Active portfolio becomes C31 + C30. C27/C16/C25 remain blocked and C18 remains reserve.
- Formal Experiment remains locked.
