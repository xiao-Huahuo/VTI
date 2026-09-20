# Lifecycle Topology Matrix V37

| Class | Lifecycle pattern | Audited examples | Current evidence |
|---|---|---|---|
| T1 | shared run scope + ineffective per-trial cleanup | AMB × Zep | public score-affecting traces |
| T2 | stable unit scope + false-clean acknowledgment | OmniMemEval × Zep | E0 source/control-flow |
| T3 | reused scope + partial reset of behaviorally active state | Redis/MemArena × Mem0 | E1/E0; paired runtime pending |
| T4 | per-example destructive recreation | RoMem DMR-MSC × Zep | strong lifecycle control, cleanup un-attested |
| T5 | disposable per-run/per-group namespace | Basic Memory × Mem0 | structural control |
| T6 | partial persistent state promoted as complete by coarse resume predicate | Microsoft Memora; LightMem MemZero | E0 source/control-flow |

T1-T6 is a descriptive organization of audited implementations, not a novel theoretical taxonomy.
