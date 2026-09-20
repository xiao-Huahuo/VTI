# Negative Controls V28

## ForgetEval × Mem0

Its current Mem0 path writes with `infer=False`. In Mem0 2.x that direct-add branch does not run the inferred extraction phase that reads and updates `Last k Messages`. This distinguishes persistent provider files from behaviorally active sidecar state.

Expected result for the V27/V28 message-sidecar hypothesis: no effect through this mechanism.

## Basic Memory × Mem0 published matrix

Repository commit audited: `basicmachines-co/basic-memory@3bf2d523c0a941f71cb144a5502e7557dd025d69`.

The Mem0 provider supports `MEM0_INFER=true`, but defaults to false. The published matrix summary explicitly states Mem0 was run in raw-add mode (`infer=false`). The CLI chooses a random run id by default, and grouped retrieval adds a group suffix to the run id used for the provider's user scope.

This is not evidence that every explicit run-id reuse is safe. It is a control showing that the V28 sidecar mechanism is disabled in the published default/raw-add path and scope reuse is reduced by default naming.

## MemArena Graphiti

The self-hosted Graphiti adapter deletes the local DB directory and rebuilds the graph on the first reset of a process/run. This is materially broader than MemArena's Mem0 per-user `delete_all` call.

No hidden behaviorally active residual has yet been established for this adapter. Keep it as an internal control unless a separate source/runtime trace identifies one.

## MemArena Letta

The first reset deletes any existing shared benchmark agent and creates a new agent. Later namespace resets delete passage IDs tracked for that namespace.

No comparable hidden-state mismatch is currently established.

## Excluded: Mem0 cloud integrations

A cloud `MemoryClient.delete_all(user_id)` integration should not be labeled affected by the local SQLite `history.db` mechanism without evidence about the hosted service's server-side state semantics. Such integrations are outside the current mechanism claim.
