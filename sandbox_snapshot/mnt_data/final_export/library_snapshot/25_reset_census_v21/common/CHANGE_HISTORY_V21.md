# Change History V21

- Continued C33 reset-attestation validation.
- Confirmed Redis benchmark leaves Mem0 dependency unpinned; current installs are not automatically affected by the historical v2.0.14 defect.
- Audited current Redis Agent Memory reset implementation and its tests.
- Added C33-C6: current adapter can return normally with residual long-term memory when post-delete search does not shrink; upstream test explicitly expects this behavior.
- Added C33-C7: deterministic runner-level fixture shows Run-A canary remains visible in Run B after a normal reset return under the upstream-tested no-shrink response pattern.
- Audited Zep, Bedrock AgentCore, Vertex, Graphiti and Supermemory reset paths and recorded negative/undetermined findings rather than inferring failures.
- Kept real-provider prevalence and score impact unverified.
