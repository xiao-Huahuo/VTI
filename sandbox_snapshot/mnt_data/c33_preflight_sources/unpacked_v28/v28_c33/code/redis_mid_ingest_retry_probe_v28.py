#!/usr/bin/env python3
"""V28 paired probe for Redis agent-memory-benchmark × Mem0 2.0.19.

This script is intentionally an exact-stack runtime probe, not a synthetic proof.
It injects one failure after >=1 successful LongMemEval session additions, snapshots
Mem0's SQLite message sidecar, then replays native-reset vs verified-clean arms
from the identical snapshot and fresh Qdrant stores.

It persists hashes/counts only; no raw LongMemEval text is written to output.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import random
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

REDIS_COMMIT = "94192c39e2a4a154f441a5411e3d73c4f54974a6"
MEM0_VERSION = "2.0.19"


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def git_head(repo: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()


def scope_for_user(user_id: str) -> str:
    return f"user_id={user_id}"


def message_summary(db_path: Path, user_id: str) -> dict[str, Any]:
    scope = scope_for_user(user_id)
    if not db_path.is_file():
        return {"exists": False, "count": 0, "row_hashes": []}
    con = sqlite3.connect(db_path)
    try:
        rows = con.execute(
            "SELECT id, role, content, created_at FROM messages "
            "WHERE session_scope = ? ORDER BY id",
            (scope,),
        ).fetchall()
    finally:
        con.close()
    row_hashes = [
        sha_text(json.dumps(row, default=str, separators=(",", ":"))) for row in rows
    ]
    return {"exists": True, "count": len(rows), "row_hashes": row_hashes}


def delete_scope_messages(db_path: Path, user_id: str) -> int:
    scope = scope_for_user(user_id)
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute("DELETE FROM messages WHERE session_scope = ?", (scope,))
        con.commit()
        return int(cur.rowcount if cur.rowcount is not None else 0)
    finally:
        con.close()


def close_memory(memory: Any) -> None:
    for obj in (getattr(memory, "vector_store", None), getattr(memory, "_telemetry_vector_store", None)):
        client = getattr(obj, "client", None)
        if client is not None and hasattr(client, "close"):
            try:
                client.close()
            except Exception:
                pass
    if hasattr(memory, "close"):
        try:
            memory.close()
        except Exception:
            pass


def make_config(root: Path, model: str) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    return {
        "llm": {"provider": "openai", "config": {"model": model, "temperature": 0.0}},
        "vector_store": {"provider": "qdrant", "config": {"path": str(root / "qdrant")}},
        "history_db_path": str(root / "history.db"),
    }


def normalize_results(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, dict):
        values = raw.get("results", [])
    else:
        values = raw or []
    return [x for x in values if isinstance(x, dict)]


def fingerprint_rows(rows: list[dict[str, Any]]) -> list[str]:
    hashes = []
    for row in rows:
        text = str(row.get("memory") or row.get("text") or "")
        hashes.append(sha_text(text))
    return sorted(hashes)


def jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo.resolve()
    if git_head(repo) != REDIS_COMMIT:
        raise RuntimeError(f"Redis repo HEAD must be {REDIS_COMMIT}")
    version = importlib.metadata.version("mem0ai")
    if version != MEM0_VERSION:
        raise RuntimeError(f"mem0ai must be {MEM0_VERSION}, got {version}")
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for the exact inferred Mem0 path")

    pkg = repo / "agent-memory-benchmark" / "src"
    sys.path.insert(0, str(pkg))
    from agent_memory_benchmark.datasets import LongMemEvalAdapter
    from agent_memory_benchmark.memory.mem0_store import Mem0MemoryStore

    examples = LongMemEvalAdapter(args.split, cache_dir=args.cache_dir).load()
    random.Random(42).shuffle(examples)
    example = examples[args.index]
    if len(example.sessions) <= args.fail_after:
        raise RuntimeError(
            f"example has {len(example.sessions)} sessions; choose fail_after < session count"
        )
    if args.fail_after < 1:
        raise RuntimeError("fail_after must be >=1 to reach the sidecar trigger")

    work = args.work.resolve()
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    user_id = f"benchmark-v28-fault-{args.index}"

    # Seed one natural partial attempt.
    seed_root = work / "seed"
    seed_store = Mem0MemoryStore(
        config=make_config(seed_root, args.model), user_id=user_id, model=args.model
    )
    await seed_store.reset()
    original_add = seed_store._memory.add
    calls = {"ok": 0, "faulted": False}

    def fail_once(*a: Any, **kw: Any):
        if calls["ok"] >= args.fail_after and not calls["faulted"]:
            calls["faulted"] = True
            raise RuntimeError("V28_INJECTED_MID_INGEST_FAILURE")
        out = original_add(*a, **kw)
        calls["ok"] += 1
        return out

    seed_store._memory.add = fail_once
    saw_fault = False
    try:
        await seed_store.ingest(example.sessions)
    except RuntimeError as exc:
        if str(exc) != "V28_INJECTED_MID_INGEST_FAILURE":
            raise
        saw_fault = True
    finally:
        seed_store._memory.add = original_add

    if not saw_fault:
        raise RuntimeError("injected fault was not reached")
    seed_db = seed_root / "history.db"
    pre = message_summary(seed_db, user_id)
    if pre["count"] <= 0:
        raise RuntimeError("natural partial ingest did not populate scoped messages")
    close_memory(seed_store._memory)

    snapshot = work / "history.seed.db"
    shutil.copy2(seed_db, snapshot)

    async def run_arm(name: str, verified_clean: bool) -> dict[str, Any]:
        root = work / name
        root.mkdir(parents=True, exist_ok=True)
        shutil.copy2(snapshot, root / "history.db")
        store = Mem0MemoryStore(
            config=make_config(root, args.model), user_id=user_id, model=args.model
        )
        before_reset = message_summary(root / "history.db", user_id)
        await store.reset()
        after_native_reset = message_summary(root / "history.db", user_id)
        deleted = 0
        if verified_clean:
            # Close/reopen SQLite around direct attestation mutation to avoid
            # relying on concurrent SQLite connection behavior.
            close_memory(store._memory)
            deleted = delete_scope_messages(root / "history.db", user_id)
            store = Mem0MemoryStore(
                config=make_config(root, args.model), user_id=user_id, model=args.model
            )
        after_verified = message_summary(root / "history.db", user_id)
        await store.ingest(example.sessions)
        all_raw = store._memory.get_all(filters={"user_id": user_id}, top_k=1000)
        all_rows = normalize_results(all_raw)
        q = example.qa_pairs[0].question
        search_raw = store._memory.search(q, filters={"user_id": user_id}, top_k=args.top_k)
        search_rows = normalize_results(search_raw)
        final_messages = message_summary(root / "history.db", user_id)
        result = {
            "arm": name,
            "before_reset": before_reset,
            "after_native_reset": after_native_reset,
            "verified_delete_count": deleted,
            "after_verified_cleanup": after_verified,
            "final_message_count": final_messages["count"],
            "final_memory_count": len(all_rows),
            "final_memory_hashes": fingerprint_rows(all_rows),
            "retrieval_hashes": fingerprint_rows(search_rows),
        }
        close_memory(store._memory)
        return result

    native = await run_arm("invoke_only", verified_clean=False)
    clean = await run_arm("verified_clean", verified_clean=True)

    native_residual = native["after_native_reset"]["count"]
    clean_residual = clean["after_verified_cleanup"]["count"]
    trigger = native_residual == pre["count"] and native_residual > 0 and clean_residual == 0
    memory_equal = native["final_memory_hashes"] == clean["final_memory_hashes"]
    retrieval_equal = native["retrieval_hashes"] == clean["retrieval_hashes"]
    return {
        "schema": "redis-mid-ingest-retry-v28",
        "redis_commit": REDIS_COMMIT,
        "mem0_version": version,
        "split": args.split,
        "example_index": args.index,
        "question_id_hash": sha_text(str(example.qa_pairs[0].question_id or args.index)),
        "session_count": len(example.sessions),
        "fail_after_successful_sessions": args.fail_after,
        "seed_message_state": pre,
        "native": native,
        "verified_clean": clean,
        "trigger_reached": trigger,
        "memory_equal": memory_equal,
        "memory_jaccard": jaccard(native["final_memory_hashes"], clean["final_memory_hashes"]),
        "retrieval_equal": retrieval_equal,
        "retrieval_jaccard": jaccard(native["retrieval_hashes"], clean["retrieval_hashes"]),
        "decision": (
            "MECHANISM_AND_OBSERVABLE_EFFECT"
            if trigger and (not memory_equal or not retrieval_equal)
            else "MECHANISM_REACHED_OBSERVABLE_NULL"
            if trigger
            else "INCOMPLETE_OR_TRIGGER_NOT_REACHED"
        ),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--work", type=Path, required=True)
    p.add_argument("--cache-dir", type=Path)
    p.add_argument("--split", default="oracle", choices=["oracle", "small", "medium"])
    p.add_argument("--index", type=int, default=0)
    p.add_argument("--fail-after", type=int, default=1)
    p.add_argument("--top-k", type=int, default=10)
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument("--output", type=Path, required=True)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    result = asyncio.run(main_async(args))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": result["decision"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
