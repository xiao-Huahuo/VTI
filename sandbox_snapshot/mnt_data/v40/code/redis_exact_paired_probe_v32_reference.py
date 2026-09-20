#!/usr/bin/env python3
"""V32 exact-stack paired runtime probe for Redis Agent Memory Benchmark × Mem0 2.0.19.

Improvements over V28:
1. preserves the Redis benchmark's default Mem0 extraction configuration instead of
   overriding Mem0's LLM with the benchmark answer model;
2. clones the complete failed-attempt local state, including Qdrant and history.db,
   before branching into native-reset and verified-clean arms;
3. records post-reset vector and message receipts independently;
4. captures hashes of Mem0 extraction prompts so sidecar consumption is attested in
   the real frozen runtime;
5. records representation, retrieval and answer hashes separately, with optional
   official LongMemEval judge scoring.

No raw LongMemEval question, answer, memory or prompt text is persisted.
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
MEM0_COMMIT = "dc82354e143c2581d505d581a00286d6ef8c3605"
EXPECTED_MEM0_DEFAULT_EXTRACTION_MODEL = "gpt-5-mini"
EXPECTED_REDIS_DEFAULT_ANSWER_MODEL = "gpt-4o"


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def git_head(repo: Path) -> str:
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def scope_for_user(user_id: str) -> str:
    # Frozen Mem0 _build_session_scope({"user_id": ...}) shape for this single-id benchmark.
    escaped = str(user_id).replace("%", "%25").replace("&", "%26").replace("=", "%3D")
    return f"user_id={escaped}"


def message_summary(db_path: Path, user_id: str) -> dict[str, Any]:
    scope = scope_for_user(user_id)
    if not db_path.is_file():
        return {"exists": False, "count": 0, "row_hashes": []}
    con = sqlite3.connect(db_path)
    try:
        table = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'").fetchone()
        if not table:
            return {"exists": True, "count": 0, "row_hashes": []}
        rows = con.execute(
            "SELECT role, content, name, created_at FROM messages WHERE session_scope = ? ORDER BY created_at, id",
            (scope,),
        ).fetchall()
    finally:
        con.close()
    return {
        "exists": True,
        "count": len(rows),
        "row_hashes": [sha_text(json.dumps(row, default=str, separators=(",", ":"))) for row in rows],
    }


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
    if hasattr(memory, "close"):
        try:
            memory.close()
        except Exception:
            pass
    for obj in (getattr(memory, "vector_store", None), getattr(memory, "_telemetry_vector_store", None)):
        client = getattr(obj, "client", None)
        if client is not None and hasattr(client, "close"):
            try:
                client.close()
            except Exception:
                pass


def make_config(root: Path) -> dict[str, Any]:
    """Isolate storage while retaining Mem0 2.0.19's default LLM/embedder semantics."""
    root.mkdir(parents=True, exist_ok=True)
    return {
        "vector_store": {"provider": "qdrant", "config": {"path": str(root / "qdrant")}},
        "history_db_path": str(root / "history.db"),
    }


def normalize_results(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, dict):
        values = raw.get("results", raw.get("memories", []))
    else:
        values = raw or []
    return [x for x in values if isinstance(x, dict)]


def fingerprint_rows(rows: list[dict[str, Any]]) -> list[str]:
    hashes = []
    for row in rows:
        text = str(row.get("memory") or row.get("text") or row.get("data") or "")
        hashes.append(sha_text(text))
    return sorted(hashes)


def jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


def vector_summary(memory: Any, user_id: str, top_k: int = 1000) -> dict[str, Any]:
    """Logical Mem0-visible vector summary."""
    raw = memory.get_all(filters={"user_id": user_id}, top_k=top_k)
    rows = normalize_results(raw)
    return {"count": len(rows), "hashes": fingerprint_rows(rows)}


def qdrant_backend_summary(memory: Any, user_id: str, page_size: int = 100) -> dict[str, Any]:
    """Independent backend-visible Qdrant receipt for the scoped vector state."""
    from qdrant_client.http import models

    store = memory.vector_store
    filt = models.Filter(
        must=[
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(value=user_id),
            )
        ]
    )
    count = int(
        store.client.count(
            collection_name=store.collection_name,
            count_filter=filt,
            exact=True,
        ).count
    )
    payload_hashes: list[str] = []
    ids: list[str] = []
    offset = None
    while True:
        records, next_offset = store.client.scroll(
            collection_name=store.collection_name,
            scroll_filter=filt,
            limit=page_size,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for record in records:
            ids.append(str(record.id))
            payload = record.payload or {}
            payload_hashes.append(sha_text(str(payload.get("data", ""))))
        if next_offset is None:
            break
        offset = next_offset
    return {
        "count": count,
        "enumerated_count": len(ids),
        "id_hashes": sorted(sha_text(value) for value in ids),
        "payload_hashes": sorted(payload_hashes),
        "count_matches_enumeration": count == len(ids),
    }


def install_prompt_recorder(memory: Any) -> tuple[list[dict[str, Any]], Any]:
    llm = memory.llm
    original = llm.generate_response
    records: list[dict[str, Any]] = []

    def wrapped(*args: Any, **kwargs: Any):
        messages = kwargs.get("messages")
        if messages is None and args:
            messages = args[0]
        if isinstance(messages, list):
            user_prompts = [
                str(m.get("content", "")) for m in messages
                if isinstance(m, dict) and m.get("role") == "user"
            ]
            for prompt in user_prompts:
                if "## Last k Messages" in prompt and "## New Messages" in prompt:
                    marker = "## Last k Messages\n"
                    end_marker = "\n\n## Recently Extracted Memories"
                    last = ""
                    if marker in prompt:
                        tail = prompt.split(marker, 1)[1]
                        last = tail.split(end_marker, 1)[0] if end_marker in tail else tail
                    records.append({
                        "prompt_sha256": sha_text(prompt),
                        "prompt_bytes": len(prompt.encode("utf-8")),
                        "last_k_sha256": sha_text(last),
                        "last_k_bytes": len(last.encode("utf-8")),
                        "last_k_nonempty": bool(last.strip()),
                    })
        return original(*args, **kwargs)

    llm.generate_response = wrapped
    return records, original


def restore_prompt_recorder(memory: Any, original: Any) -> None:
    memory.llm.generate_response = original


async def judge_answer(repo: Path, *, example: Any, example_idx: int, split: str, answer: str, model: str) -> dict[str, Any]:
    from openai import AsyncOpenAI
    from agent_memory_benchmark.benchmark.judge import _judge_one
    from agent_memory_benchmark.benchmark.models import AnswerRecord

    qa = example.qa_pairs[0]
    record = AnswerRecord(
        example_idx=example_idx,
        question_id=qa.question_id,
        dataset="LongMemEval",
        split=split,
        provider="mem0",
        question=qa.question,
        ground_truth=qa.answer,
        predicted_answer=answer,
        question_type=qa.question_type,
    )
    judged = await _judge_one(record, client=AsyncOpenAI(), model=model, attempts=3)
    return {"score": judged.score, "reasoning_hash": sha_text(judged.reasoning), "judge_model": model}


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
    if args.index is None:
        selected = next((i for i, ex in enumerate(examples) if len(ex.sessions) > args.fail_after), None)
        if selected is None:
            raise RuntimeError("No shuffled example has enough sessions for the requested failure point")
        example_idx = selected
    else:
        example_idx = args.index
    example = examples[example_idx]
    if len(example.sessions) <= args.fail_after:
        raise RuntimeError(f"example has {len(example.sessions)} sessions; fail_after must be smaller")
    if args.fail_after < 1:
        raise RuntimeError("fail_after must be >=1")

    work = args.work.resolve()
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    user_id = f"benchmark-v32-fault-{example_idx}"

    seed_root = work / "seed"
    seed_store = Mem0MemoryStore(config=make_config(seed_root), user_id=user_id, model=args.answer_model)
    extraction_model = str(getattr(getattr(seed_store._memory.llm, "config", None), "model", ""))
    if extraction_model != EXPECTED_MEM0_DEFAULT_EXTRACTION_MODEL:
        raise RuntimeError(
            f"Frozen Mem0 default extraction model drifted: expected {EXPECTED_MEM0_DEFAULT_EXTRACTION_MODEL}, got {extraction_model!r}"
        )
    await seed_store.reset()
    original_add = seed_store._memory.add
    calls = {"ok": 0, "faulted": False}

    def fail_once(*a: Any, **kw: Any):
        if calls["ok"] >= args.fail_after and not calls["faulted"]:
            calls["faulted"] = True
            raise RuntimeError("V32_INJECTED_MID_INGEST_FAILURE")
        out = original_add(*a, **kw)
        calls["ok"] += 1
        return out

    seed_store._memory.add = fail_once
    saw_fault = False
    try:
        await seed_store.ingest(example.sessions)
    except RuntimeError as exc:
        if str(exc) != "V32_INJECTED_MID_INGEST_FAILURE":
            raise
        saw_fault = True
    finally:
        seed_store._memory.add = original_add

    if not saw_fault:
        raise RuntimeError("Injected fault was not reached")
    pre_messages = message_summary(seed_root / "history.db", user_id)
    pre_vectors = vector_summary(seed_store._memory, user_id)
    pre_backend_vectors = qdrant_backend_summary(seed_store._memory, user_id)
    if pre_messages["count"] <= 0:
        raise RuntimeError("Partial ingest did not populate scoped messages")
    close_memory(seed_store._memory)

    snapshot = work / "failed_attempt_snapshot"
    shutil.copytree(seed_root, snapshot)

    async def run_arm(name: str, verified_clean: bool) -> dict[str, Any]:
        root = work / name
        shutil.copytree(snapshot, root)
        store = Mem0MemoryStore(config=make_config(root), user_id=user_id, model=args.answer_model)
        before_messages = message_summary(root / "history.db", user_id)
        before_vectors = vector_summary(store._memory, user_id)
        before_backend_vectors = qdrant_backend_summary(store._memory, user_id)
        await store.reset()
        after_native_messages = message_summary(root / "history.db", user_id)
        after_native_vectors = vector_summary(store._memory, user_id)
        after_native_backend_vectors = qdrant_backend_summary(store._memory, user_id)
        deleted = 0
        if verified_clean:
            close_memory(store._memory)
            deleted = delete_scope_messages(root / "history.db", user_id)
            store = Mem0MemoryStore(config=make_config(root), user_id=user_id, model=args.answer_model)
        after_clean_messages = message_summary(root / "history.db", user_id)
        after_clean_vectors = vector_summary(store._memory, user_id)
        after_clean_backend_vectors = qdrant_backend_summary(store._memory, user_id)

        prompt_records, original_generate = install_prompt_recorder(store._memory)
        try:
            await store.ingest(example.sessions)
        finally:
            restore_prompt_recorder(store._memory, original_generate)

        final_raw = store._memory.get_all(filters={"user_id": user_id}, top_k=1000)
        final_rows = normalize_results(final_raw)
        qa = example.qa_pairs[0]
        search_raw = store._memory.search(qa.question, filters={"user_id": user_id}, top_k=args.top_k)
        search_rows = normalize_results(search_raw)
        query_result = await store.query(qa.question, question_date=example.metadata.get("question_date"))
        answer = str(query_result.answer)
        judged = None
        if args.with_judge:
            judged = await judge_answer(repo, example=example, example_idx=example_idx, split=args.split, answer=answer, model=args.judge_model)
        result = {
            "arm": name,
            "before_reset_messages": before_messages,
            "before_reset_vectors": before_vectors,
            "before_reset_qdrant_backend": before_backend_vectors,
            "after_native_reset_messages": after_native_messages,
            "after_native_reset_vectors": after_native_vectors,
            "after_native_reset_qdrant_backend": after_native_backend_vectors,
            "verified_delete_count": deleted,
            "after_verified_cleanup_messages": after_clean_messages,
            "after_verified_cleanup_vectors": after_clean_vectors,
            "after_verified_cleanup_qdrant_backend": after_clean_backend_vectors,
            "extraction_prompt_records": prompt_records,
            "final_memory_count": len(final_rows),
            "final_memory_hashes": fingerprint_rows(final_rows),
            "retrieval_hashes": fingerprint_rows(search_rows),
            "answer_sha256": sha_text(answer),
            "judge": judged,
        }
        close_memory(store._memory)
        return result

    native = await run_arm("invoke_only", verified_clean=False)
    clean = await run_arm("verified_clean", verified_clean=True)

    native_m = native["after_native_reset_messages"]["count"]
    clean_m = clean["after_verified_cleanup_messages"]["count"]
    native_v = native["after_native_reset_qdrant_backend"]["count"]
    clean_v = clean["after_verified_cleanup_qdrant_backend"]["count"]
    vector_receipts_consistent = (
        native["after_native_reset_qdrant_backend"]["count_matches_enumeration"]
        and clean["after_verified_cleanup_qdrant_backend"]["count_matches_enumeration"]
        and native["after_native_reset_vectors"]["count"] == native_v
        and clean["after_verified_cleanup_vectors"]["count"] == clean_v
    )
    trigger = (
        native_m == pre_messages["count"]
        and native_m > 0
        and clean_m == 0
        and native_v == 0
        and clean_v == 0
        and vector_receipts_consistent
    )
    prompt_native = native["extraction_prompt_records"]
    prompt_clean = clean["extraction_prompt_records"]
    first_prompt_diff = bool(prompt_native and prompt_clean and prompt_native[0]["prompt_sha256"] != prompt_clean[0]["prompt_sha256"])
    memory_equal = native["final_memory_hashes"] == clean["final_memory_hashes"]
    retrieval_equal = native["retrieval_hashes"] == clean["retrieval_hashes"]
    answer_equal = native["answer_sha256"] == clean["answer_sha256"]
    score_equal = None
    if args.with_judge:
        score_equal = native["judge"]["score"] == clean["judge"]["score"]

    if not trigger:
        decision = "INCOMPLETE_OR_TRIGGER_NOT_REACHED"
    elif not first_prompt_diff:
        decision = "MECHANISM_REACHED_PROMPT_CONSUMPTION_NOT_ATTESTED"
    elif not memory_equal or not retrieval_equal or not answer_equal or (score_equal is False):
        decision = "MECHANISM_AND_DOWNSTREAM_EFFECT"
    else:
        decision = "MECHANISM_AND_PROMPT_EFFECT_DOWNSTREAM_NULL"

    return {
        "schema": "redis-mid-ingest-retry-v32",
        "redis_commit": REDIS_COMMIT,
        "mem0_version": version,
        "mem0_commit": MEM0_COMMIT,
        "mem0_extraction_model": extraction_model,
        "answer_model": args.answer_model,
        "judge_model": args.judge_model if args.with_judge else None,
        "split": args.split,
        "example_index": example_idx,
        "question_id_hash": sha_text(str(example.qa_pairs[0].question_id or example_idx)),
        "session_count": len(example.sessions),
        "fail_after_successful_sessions": args.fail_after,
        "failed_attempt_message_state": pre_messages,
        "failed_attempt_vector_state": pre_vectors,
        "failed_attempt_qdrant_backend_state": pre_backend_vectors,
        "native": native,
        "verified_clean": clean,
        "trigger_reached": trigger,
        "vector_receipts_consistent": vector_receipts_consistent,
        "first_extraction_prompt_diff": first_prompt_diff,
        "memory_equal": memory_equal,
        "memory_jaccard": jaccard(native["final_memory_hashes"], clean["final_memory_hashes"]),
        "retrieval_equal": retrieval_equal,
        "retrieval_jaccard": jaccard(native["retrieval_hashes"], clean["retrieval_hashes"]),
        "answer_equal": answer_equal,
        "judge_score_equal": score_equal,
        "decision": decision,
        "raw_benchmark_text_persisted": False,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--work", type=Path, required=True)
    p.add_argument("--cache-dir", type=Path)
    p.add_argument("--split", default="oracle", choices=["oracle", "small", "medium"])
    p.add_argument("--index", type=int)
    p.add_argument("--fail-after", type=int, default=1)
    p.add_argument("--top-k", type=int, default=10)
    p.add_argument("--answer-model", default=EXPECTED_REDIS_DEFAULT_ANSWER_MODEL)
    p.add_argument("--with-judge", action="store_true")
    p.add_argument("--judge-model", default="gpt-4o")
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
