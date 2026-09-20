# Change History V12

## 2026-09-18 V12

C27:

- Added LoCoMo as an independent threshold-calibration family using the official 10-conversation release.
- Evaluated 1,977 evidence-bearing QA instances with query-independent selectors.
- Character-length Top-2 evidence hit was 2.23% versus 0.49% random expectation, producing 4.57x lift.
- The result falsifies use of `lift@2 > 1.5` as a standalone cross-benchmark leakage trigger because large candidate pools can create high relative lift with low absolute target residency.
- Fixed lift trigger changed from provisional supported to challenged.
- Gate B now requires a multi-effect control envelope; numeric thresholds remain unfrozen.

C16:

- Novelty refresh found direct conceptual prior art for certificate dependency metadata and invalidation after data/tool/model dependency updates.
- All architecture/design novelty around certificate version binding and invalidation is removed.
- C16 remains alive only as an empirical measurement claim about real persistent-memory verifier boundary crossing and downstream lifecycle/action forks.
- DriftJudge-to-MemGuard cross-scale normalization remains prohibited as an arbitrary mapping.

No claim was upgraded to FROZEN_RUN in V12.
