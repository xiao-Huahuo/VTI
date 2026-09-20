# V44 decision summary

Date: 2026-09-20

## Decision

DeepSeek non-thinking mode with temperature zero does not make the Mem0
extraction/retrieval pipeline deterministic enough for single-run exact-hash
causal inference.

The predeclared first-case gate used two verified-clean arms. Both arms had zero
scoped messages and vectors before re-ingestion, and their first extraction
prompt hashes were identical. Nevertheless:

- final memory sets differed; Jaccard = `0.1182519280`;
- Top-10 retrieval sets differed; Jaccard = `0.0`;
- answer hashes differed.

The control therefore stopped after one real case as specified. Running the
remaining V44 cases or a new native-versus-clean n=12 with the same exact-hash
endpoint would spend API resources without repairing identification.

## Current evidence boundary

E1 remains supported: benchmark-native reset leaves 10 scoped Mem0 message rows,
verified cleanup removes them, and later extraction reads a different prompt.

E2 and E3 remain unmeasured causally. V42's downstream inequalities and V43/V44
clean-clean inequalities overlap, so exact hash differences cannot be attributed
to hidden trial state.

## Required redesign

Any next downstream-effect study must use at least one of:

1. a model/API with reproducible seeded or greedy decoding;
2. replicated native-clean and clean-clean arms with a distributional estimand;
3. semantic or task-level outcomes calibrated against repeated clean-clean
   baselines rather than exact text hashes.

MemArena execution is deferred because substituting the same DeepSeek stack
would inherit the same identification failure.
