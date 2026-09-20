# Reset Contract Formalization V28

## 1. Experimental state

For benchmark trial scope `x`, model provider persistence as a finite set of state surfaces:

`S = {s_1, ..., s_n}`.

A surface may be a vector collection, message buffer, relational table, graph store, entity index, cache, background job queue, or other durable state.

## 2. Behavioral activity

A surface is behaviorally active for the next benchmark transition if the provider reads or otherwise consults it while processing the next ingest, retrieval, update, or answer operation.

Let `A_x ⊆ S` denote behaviorally active surfaces for scope `x`.

Persistence alone is not enough. An audit/history table that is never read by the tested path should not be promoted to a causal reset requirement without evidence.

## 3. Clean postconditions

Each active surface has a benchmark-specific clean postcondition `C_s(x)`.

Examples:

- vector memory: no records for `x`;
- message buffer: no buffered messages for `x`;
- graph namespace: no nodes/episodes/edges attributable to `x` if those objects affect later search/extraction;
- cache: no entry whose lookup key can be hit by the next trial.

## 4. Reset completeness

For adapter reset `R_x`, define behavioral completeness as:

`Complete(R_x) ⇔ ∀s ∈ A_x, C_s(x) holds after R_x`.

A reset-contract mismatch exists when:

`∃s ∈ A_x` such that `C_s(x)` is false after `R_x`.

This definition deliberately separates an API-level success response from an experimental clean-slate guarantee.

## 5. Reset receipt

A reset receipt is a machine-readable artifact containing, for each audited surface:

- surface identifier and provider version;
- benchmark scope key;
- how behavioral activity was established (`source`, `trace`, or both);
- pre-reset state summary;
- reset action invoked by the benchmark;
- post-reset state summary;
- declared clean predicate;
- predicate result;
- content-safe hashes/IDs where needed for reproducibility.

A receipt can be negative: if a surface is persistent but not behaviorally active, record that classification and evidence instead of requiring it to be erased.

## 6. Outcome ladder

Mechanism evidence and benchmark-score evidence are distinct:

1. reachability: active state is populated naturally;
2. residual: benchmark reset leaves it behind;
3. consumption: next operation reads residual state;
4. representation effect: resulting memories/retrieval differ under paired clean vs native reset;
5. outcome effect: benchmark answer/judge metrics differ.

Claims must stop at the highest rung supported by evidence.
