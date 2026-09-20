# CHANGE HISTORY V17

## 2026-09-18

- Audited the native lifecycle closure of C31 in `rohitg00/agentmemory v0.9.29`.
- Confirmed that explicit retention-score/retention-evict functions consume read-updated access state, while the default hourly auto-forget path uses separate TTL, contradiction, age and importance logic.
- Downgraded C31 from active survivor to reserve because the observed production path lacks automatic closure from evaluation reads to retention eviction.
- Audited Redis Agent Memory Benchmark's Zep readiness logic.
- Confirmed that Zep `list_memories()` returns graph-edge fact strings while generic readiness compares only list length.
- Confirmed current Zep documentation recommends task/episode processed status for asynchronous ingestion completion.
- Promoted C30 to sole primary provisional candidate with a paired benchmark-readiness versus provider-native-readiness pilot.
- Formal Experiment remains locked.
