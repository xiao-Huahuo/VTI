# Lifecycle Topology Matrix V38

This matrix is descriptive evidence organization, not a novelty claim.

| Class / role | Integration | Lifecycle property | Evidence | V38 interpretation |
|---|---|---|---|---|
| T1 | AMB × Zep | shared run scope + ineffective cleanup | public E4 contamination | established positive |
| T2 | OmniMemEval × Zep | stable unit scope + false clean acknowledgement | E0 | source-positive external harness |
| T3 | Redis × Mem0; MemArena × Mem0 | reused scope + incomplete reset of behaviorally active state | E1/source; E2+ pending | frozen V34 controlled targets |
| T4 | IronCurtain / RoMem-style disposable state | per-example destructive recreation | source control | lifecycle negative/control pattern |
| T5 | Basic Memory × Mem0 | disposable per-run/per-group namespace | source control | structural isolation on ordinary path |
| T6a | LightMem MemZero | backend existence can promote incomplete state to complete | E0 | coarse existence predicate |
| T6a | Microsoft Memora | any non-empty question collection can satisfy skip-existing retry | E0 | coarse existence predicate |
| T6b | MemBase Mem0 | finalization marker can be published after swallowed per-message add failures; later skip requires marker + any memory | E0 | stronger marker, incomplete success contract |
| T3-like retry carryover | MemBase Mem0 | hard-interrupted partial store is reopened for replay without reset | E0 | avoids immediate false skip yet lacks fresh retry state |

## Key distinction added in V38

A completion marker and a clean retry are separate properties. MemBase demonstrates both sides in one framework: the marker prevents one exact false-skip branch after abrupt interruption, while the stable persistent namespace still carries partial state into reconstruction. Separately, swallowed per-message failures can let finalization publish the marker after incomplete ingestion.


## Reproduction-path note

MemBase's traced construction example used for MemTraceBench always passes `--rerun`. For Mem0 this reaches the V38 freshness-mismatch route on a stable save directory. This raises practical exposure of the route, while the released graph data still requires direct inspection before any run-specific contamination claim.
