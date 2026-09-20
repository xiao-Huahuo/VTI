# Current handoff — V44

Date: 2026-09-20

Project: `AM-AUTO-20260918-R1`

Candidate: `C33`

Status: `V44_DEEPSEEK_NONTHINKING_CONTROL_FAILED_IDENTIFICATION_E1_CONFIRMED_E2_E3_UNMEASURED`

## What is established

The exact Redis benchmark checkout and Mem0 2.0.19 path were executed on macOS
with the frozen 12-case cohort. In all 12 V42 cases, native scoped reset left 10
Mem0 message rows while verified cleanup left zero. Both arms had zero scoped
vectors before re-ingestion. The first extraction prompt differed in all 12
native-versus-clean pairs.

This directly supports E1: behaviorally active state escapes the lifecycle
boundary implied by the benchmark reset and is consumed by the next transition.

## What is not established

V42 produced different memory, Top-10 retrieval and answer hashes in all 12
pairs, but V43 produced the same pattern in three clean-clean controls whose
first extraction prompts were identical. V44 disabled DeepSeek thinking and set
temperature to zero; its real clean-clean case still diverged.

Consequently, V42's mechanical E3 labels are not causal E3 evidence. E2 and E3
remain unmeasured causally; E4 was not measured.

## Version chain

1. **V40** — OpenAI-backed exact protocol materialized, but unavailable due API
   credit constraints.
2. **V42** — Prospective DeepSeek + local FastEmbed amendment; 12/12 completed.
3. **V43** — Three thinking-mode clean-clean controls exposed a stochastic
   baseline matching the nominal V42 effect.
4. **V44** — One non-thinking, temperature-zero clean-clean gate still diverged;
   exact-hash DeepSeek reruns were stopped.

## Next scientific action

Do not rerun V42 unchanged and do not start MemArena with the same endpoint.
Freeze a new design before further provider calls. Acceptable directions are:

1. deterministic or seeded model inference;
2. replicated native-clean and clean-clean arms with a distributional treatment
   estimand;
3. semantic/task-level outcomes calibrated against repeated clean-clean
   baselines rather than exact string hashes.

A small V45 feasibility gate should precede any n=12 expansion. Kill or downscope
C33 if a redesigned pilot cannot separate treatment effect from stochastic
baseline.

## Runtime state

- Python 3.12 virtual environment remains under the ignored `third_party/` tree.
- Exact Redis checkout remains at commit
  `94192c39e2a4a154f441a5411e3d73c4f54974a6`.
- `mem0ai==2.0.19`, FastEmbed 0.8.0 and local Qdrant remain installed.
- `.env` is ignored and contains the local provider credential.
- Dataset caches and raw experiment work directories were intentionally removed
  after structured receipts were committed. They can be downloaded/recreated.
- Direct DeepSeek access was more reliable than the optional local proxy during
  long runs.

## Known gaps

The historical MemArena V27 scripts referenced by old handoffs are absent from
the migration package. See [KNOWN_GAPS.md](KNOWN_GAPS.md).

## Git checkpoints

- `c15be3c` — V40 migration baseline.
- `3ec0b7f` — macOS Redis runtime preparation.
- `6f020e9` — DeepSeek pilot and stochastic-control implementation.
- `f40637d` — V42–V44 results and decisions.
