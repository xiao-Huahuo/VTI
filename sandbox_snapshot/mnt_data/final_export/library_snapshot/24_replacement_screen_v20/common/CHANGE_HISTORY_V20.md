# Change History V20

- Started replacement screening after C30 kill, with the entire asynchronous-readiness family excluded.
- Re-audited C18 and killed it after direct versioned policy-memory and policy-bound authorization prior art was confirmed.
- Screened derived-projection consistency, retry-induced false corroboration, restart durability and embedding/index migration candidates; all were rejected as crowded.
- Promoted C33 `Benchmark-to-Deployment Path Drift in Agent Memory Systems` as the sole primary provisional candidate.
- Bound C33 to three independent source-grounded positive cases: Aelfrice historical eval/live path split, claude-mem-lite historical FTS-only versus production-hybrid instrumentation, and YourMemory benchmark/production ranker drift.
- Added current claude-mem-lite and Redis shipping-REST-API attestations as controls.
- Implemented a Path Contract comparison prototype. Five curated cases matched expected classifications and six unit tests passed.
- Explicitly limited the pilot to representation/comparison feasibility; automated path discovery, prevalence and matched score impact remain unverified.
- Formal Experiment remains locked. Next Gate is a 12-system source-grounded mini-census followed by matched dynamic replay on at least two runnable systems.
