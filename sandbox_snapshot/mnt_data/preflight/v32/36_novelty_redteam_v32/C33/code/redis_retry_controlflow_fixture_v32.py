#!/usr/bin/env python3
"""V32 source-grounded control-flow fixture for Redis Agent Memory Benchmark × Mem0 2.0.19.

Purpose
-------
Execute the two benchmark lifecycle routes that can reuse a LongMemEval example's
Mem0 user scope without requiring Mem0, Qdrant, a dataset download, or an LLM:

1. in-process mid-ingest retry;
2. process crash followed by resume with the same run_name and example index.

The fixture mirrors only the frozen source semantics required by the causal chain:
- Redis runner user_id = benchmark-<run_name>-<index>
- Redis runner retries reset()+ingest as one operation
- Redis Mem0 adapter ingests one Memory.add per session
- Mem0's scoped delete_all clears vector state but does not clear the messages sidecar
- inferred Memory.add reads Last-k sidecar messages before writing the current session

This is an implementation/control-flow attestation. It does not execute the real Mem0
LLM extraction or establish downstream memory/retrieval/answer/score effects.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

REDIS_COMMIT = "94192c39e2a4a154f441a5411e3d73c4f54974a6"
REDIS_RUNNER_BLOB = "c4589ef6e2a414d5c00e4e67598e3bb48dde71ce"
REDIS_MEM0_ADAPTER_BLOB = "5f8344d91fc21b062d39e8a94b704b040b654c86"
MEM0_COMMIT = "dc82354e143c2581d505d581a00286d6ef8c3605"
MEM0_MAIN_BLOB = ""  # filled in provenance, commit is the binding used here
MEM0_STORAGE_BLOB = "5bd5512436cc6f3cbd5ce03d10808d3e6eef067b"


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def escape_scope_value(value: Any) -> str:
    return str(value).replace("%", "%25").replace("&", "%26").replace("=", "%3D")


def session_scope(user_id: str) -> str:
    return f"user_id={escape_scope_value(user_id)}"


@dataclass(frozen=True)
class Session:
    label: str
    messages: tuple[tuple[str, str], ...]


def benchmark_messages(session: Session) -> list[dict[str, str]]:
    # Frozen Redis Mem0MemoryStore.ingest shape.
    values = [{"role": "user", "content": f"Conversation date: {session.label}"}]
    values.extend({"role": role, "content": text} for role, text in session.messages if text.strip())
    return values


class SidecarState:
    """Source-equivalent state surface for the causal path under test."""

    def __init__(self) -> None:
        self.messages: dict[str, list[dict[str, str]]] = {}
        self.vectors: dict[str, list[str]] = {}

    def clone(self) -> "SidecarState":
        other = SidecarState()
        other.messages = json.loads(json.dumps(self.messages))
        other.vectors = json.loads(json.dumps(self.vectors))
        return other

    def get_last_messages(self, scope: str, limit: int = 10) -> list[dict[str, str]]:
        return list(self.messages.get(scope, []))[-limit:]

    def save_messages(self, scope: str, values: list[dict[str, str]]) -> None:
        rows = self.messages.setdefault(scope, [])
        rows.extend(json.loads(json.dumps(values)))
        self.messages[scope] = rows[-10:]

    def delete_all_vectors(self, user_id: str) -> None:
        # Frozen Mem0 scoped delete_all affects logical vector memories, not messages.
        self.vectors[user_id] = []

    def verified_clean_messages(self, user_id: str) -> int:
        scope = session_scope(user_id)
        count = len(self.messages.get(scope, []))
        self.messages[scope] = []
        return count


class FakeMem0Store:
    """Minimal Mem0 adapter preserving the tested control-flow semantics."""

    def __init__(self, state: SidecarState, user_id: str) -> None:
        self.state = state
        self.user_id = user_id
        self.prompt_receipts: list[dict[str, Any]] = []
        self.successful_adds = 0
        self.fail_after: int | None = None
        self.fail_once = True

    async def reset(self) -> None:
        self.state.delete_all_vectors(self.user_id)

    async def ingest(self, sessions: list[Session]) -> None:
        for session in sessions:
            if self.fail_after is not None and self.successful_adds >= self.fail_after and self.fail_once:
                self.fail_once = False
                raise RuntimeError("V32_INJECTED_MID_INGEST_FAILURE")
            await self._add(benchmark_messages(session))
            self.successful_adds += 1

    async def _add(self, new_messages: list[dict[str, str]]) -> None:
        scope = session_scope(self.user_id)
        last_k = self.state.get_last_messages(scope, 10)
        receipt = {
            "last_k_count": len(last_k),
            "last_k_hash": sha(json.dumps(last_k, sort_keys=True, ensure_ascii=False)),
            "new_message_count": len(new_messages),
            "new_messages_hash": sha(json.dumps(new_messages, sort_keys=True, ensure_ascii=False)),
        }
        self.prompt_receipts.append(receipt)
        # The real Mem0 call performs LLM extraction before Phase 8 save_messages.
        # Here we add a deterministic vector sentinel only to model reset semantics.
        self.state.vectors.setdefault(self.user_id, []).append(receipt["new_messages_hash"])
        self.state.save_messages(scope, new_messages)


async def retry(operation: Callable[[], Any], attempts: int = 3) -> None:
    """Frozen Redis runner retry semantics minus sleep."""
    last_exc: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            await operation()
            return
        except Exception as exc:
            last_exc = exc
            if attempt == attempts:
                raise
    assert last_exc is not None
    raise last_exc


def user_id_for(run_name: str, index: int) -> str:
    # Frozen runner store_kwargs call site.
    return f"benchmark-{run_name}-{index}"


async def mid_ingest_retry_case() -> dict[str, Any]:
    state = SidecarState()
    uid = user_id_for("v32-retry", 7)
    sessions = [
        Session("2026/01/01", (("user", "alpha"), ("assistant", "ack"))),
        Session("2026/01/02", (("user", "beta"), ("assistant", "ack"))),
        Session("2026/01/03", (("user", "gamma"), ("assistant", "ack"))),
    ]
    store = FakeMem0Store(state, uid)
    store.fail_after = 1

    attempt_starts: list[dict[str, int]] = []

    async def ingest_clean() -> None:
        await store.reset()
        scope = session_scope(uid)
        attempt_starts.append({
            "message_count_after_reset": len(state.messages.get(scope, [])),
            "vector_count_after_reset": len(state.vectors.get(uid, [])),
        })
        await store.ingest(sessions)

    await retry(ingest_clean, attempts=3)
    # Receipts: first successful add on attempt 1, then all 3 adds on attempt 2.
    receipts = store.prompt_receipts
    return {
        "route": "mid_ingest_retry",
        "same_user_scope_across_attempts": True,
        "attempt_starts": attempt_starts,
        "receipt_count": len(receipts),
        "attempt1_first_add_last_k": receipts[0]["last_k_count"],
        "attempt2_first_add_last_k": receipts[1]["last_k_count"],
        "attempt2_first_add_last_k_hash": receipts[1]["last_k_hash"],
        "final_sidecar_count": len(state.messages.get(session_scope(uid), [])),
        "final_vector_count": len(state.vectors.get(uid, [])),
        "trigger_reached": (
            len(attempt_starts) == 2
            and attempt_starts[0]["message_count_after_reset"] == 0
            and attempt_starts[1]["message_count_after_reset"] > 0
            and attempt_starts[1]["vector_count_after_reset"] == 0
            and receipts[1]["last_k_count"] > 0
        ),
    }


async def crash_resume_case() -> dict[str, Any]:
    run_name = "v32-resume"
    index = 11
    uid_before = user_id_for(run_name, index)
    uid_after = user_id_for(run_name, index)
    state = SidecarState()
    sessions = [
        Session("2026/02/01", (("user", "one"),)),
        Session("2026/02/02", (("user", "two"),)),
    ]

    # Process 1: partial ingest, then process disappears before an AnswerRecord is written.
    p1 = FakeMem0Store(state, uid_before)
    await p1.reset()
    await p1._add(benchmark_messages(sessions[0]))
    before_crash_messages = len(state.messages.get(session_scope(uid_before), []))
    before_crash_vectors = len(state.vectors.get(uid_before, []))

    # Process 2: same run_name + same shuffled example index => same benchmark user_id.
    # The runner executes reset() before ingesting again.
    p2 = FakeMem0Store(state, uid_after)
    await p2.reset()
    after_resume_reset_messages = len(state.messages.get(session_scope(uid_after), []))
    after_resume_reset_vectors = len(state.vectors.get(uid_after, []))
    await p2._add(benchmark_messages(sessions[0]))

    clean_state = state.clone()
    # Reconstruct the same pre-resume snapshot and remove message scope as verified-clean control.
    # We use a fresh snapshot to keep this receipt independent of the already mutated resume state.
    baseline = SidecarState()
    bp = FakeMem0Store(baseline, uid_before)
    await bp._add(benchmark_messages(sessions[0]))
    baseline.delete_all_vectors(uid_before)
    deleted = baseline.verified_clean_messages(uid_before)
    clean = FakeMem0Store(baseline, uid_after)
    await clean._add(benchmark_messages(sessions[0]))

    return {
        "route": "crash_resume_same_run_name",
        "user_id_equal": uid_before == uid_after,
        "before_crash_message_count": before_crash_messages,
        "before_crash_vector_count": before_crash_vectors,
        "after_resume_native_reset_message_count": after_resume_reset_messages,
        "after_resume_native_reset_vector_count": after_resume_reset_vectors,
        "resumed_first_add_last_k": p2.prompt_receipts[0]["last_k_count"],
        "verified_clean_deleted_messages": deleted,
        "clean_first_add_last_k": clean.prompt_receipts[0]["last_k_count"],
        "trigger_reached": (
            uid_before == uid_after
            and before_crash_messages > 0
            and after_resume_reset_messages == before_crash_messages
            and after_resume_reset_vectors == 0
            and p2.prompt_receipts[0]["last_k_count"] > 0
            and clean.prompt_receipts[0]["last_k_count"] == 0
        ),
    }


async def run() -> dict[str, Any]:
    retry_case = await mid_ingest_retry_case()
    resume_case = await crash_resume_case()
    return {
        "schema": "redis-retry-controlflow-v32",
        "redis_commit": REDIS_COMMIT,
        "redis_runner_blob": REDIS_RUNNER_BLOB,
        "redis_mem0_adapter_blob": REDIS_MEM0_ADAPTER_BLOB,
        "mem0_commit": MEM0_COMMIT,
        "mem0_storage_blob": MEM0_STORAGE_BLOB,
        "mid_ingest_retry": retry_case,
        "crash_resume": resume_case,
        "all_routes_trigger": bool(retry_case["trigger_reached"] and resume_case["trigger_reached"]),
        "claim_level": "SOURCE_GROUNDED_CONTROL_FLOW_AND_PRE_LLM_STATE_CONSUMPTION_ONLY",
        "downstream_llm_effect": "UNVERIFIED",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    import asyncio
    result = asyncio.run(run())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
