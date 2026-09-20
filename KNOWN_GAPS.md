# Known gaps

## Missing historical MemArena scripts

Historical V27/V28 handoffs reference the following files, but no copies were
found in the migration snapshot or nested research archives:

- `memarena_sidecar_gate_h0_v27.py`
- `memarena_sidecar_paired_replay_v27.py`
- `memarena_sidecar_inspector_v27.py`

The MemArena protocol description, repository commit, provider version and design
rationale remain available, but its executable package is incomplete. Any future
MemArena run must reconstruct and re-audit the runner before execution.

## DeepSeek causal identification

DeepSeek thinking-mode and non-thinking temperature-zero runs both show large
clean-clean divergence under identical prompt hashes. Single-run exact-hash
outcomes cannot identify lifecycle-caused E2/E3 on this stack.

## V44 timestamp metadata

V44 was launched as a direct diagnostic probe rather than through the formal
orchestrator. The result and file hash are preserved, but start/finish timestamps
were not recorded. This is disclosed in `v44/results/V44_RUN_RECORD.json`.

## Formal experiment

No full formal experiment has started. Only pilot and diagnostic runs are
available. No paper claim should imply population prevalence or E4 score effect.
