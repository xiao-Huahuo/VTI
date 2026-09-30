#!/usr/bin/env python3
"""V45 deterministic local causal-identification gate.

Stage 0 verifies repeated native Ollama output under a fixed seed/options bundle.
Stage A runs verified-clean versus independently verified-clean on the first
frozen Redis benchmark case. Stage B runs native reset versus verified cleanup
only when Stage A is exactly reproducible.

No raw LongMemEval question, answer, memory, or extraction prompt text is
persisted in the structured result.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import random
import shutil
import sqlite3
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

REDIS_COMMIT = "94192c39e2a4a154f441a5411e3d73c4f54974a6"
MEM0_VERSION = "2.0.19"
MEM0_COMMIT = "dc82354e143c2581d505d581a00286d6ef8c3605"
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_PYTHON_VERSION = "0.6.2"
EXPECTED_MODEL = "qwen3:8b-q4_K_M"
EXPECTED_MODEL_DIGEST_PREFIX = "500a1f067a9f"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIMS = 384
SEED = 20260920
NUM_CTX = 32768
NUM_PREDICT = 2048
TOP_K_SAMPLING = 1
TOP_P = 1.0
TEMPERATURE = 0.0
KEEP_ALIVE = "30m"
QUALITY_MEMORY_MIN = 100


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def git_head(repo: Path) -> str:
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def http_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def ollama_runtime_receipt() -> dict[str, Any]:
    version_payload = http_json(f"{OLLAMA_BASE_URL}/api/version")
    tags_payload = http_json(f"{OLLAMA_BASE_URL}/api/tags")
    models = tags_payload.get("models", [])
    selected = None
    for item in models:
        if str(item.get("name") or item.get("model")) == EXPECTED_MODEL:
            selected = item
            break
    if selected is None:
        raise RuntimeError(
            f"Ollama model {EXPECTED_MODEL!r} is not installed. Run: ollama pull {EXPECTED_MODEL}"
        )
    digest = str(selected.get("digest") or "")
    if not digest.startswith(EXPECTED_MODEL_DIGEST_PREFIX):
        raise RuntimeError(
            f"Ollama model digest drift: expected prefix {EXPECTED_MODEL_DIGEST_PREFIX}, got {digest!r}"
        )
    return {
        "ollama_version": str(version_payload.get("version") or ""),
        "model": EXPECTED_MODEL,
        "model_digest": digest,
        "model_size": selected.get("size"),
        "modified_at": selected.get("modified_at"),
    }


def scope_for_user(user_id: str) -> str:
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
    root.mkdir(parents=True, exist_ok=True)
    return {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "path": str(root / "qdrant"),
                "embedding_model_dims": EMBEDDING_DIMS,
            },
        },
        "history_db_path": str(root / "history.db"),
        "llm": {
            "provider": "ollama",
            "config": {
                "model": EXPECTED_MODEL,
                "ollama_base_url": OLLAMA_BASE_URL,
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "top_k": TOP_K_SAMPLING,
                "max_tokens": NUM_PREDICT,
            },
        },
        "embedder": {
            "provider": "fastembed",
            "config": {
                "model": EMBEDDING_MODEL,
                "embedding_dims": EMBEDDING_DIMS,
            },
        },
    }


def response_content(response: Any) -> str:
    if isinstance(response, dict):
        message = response.get("message") or {}
        return str(message.get("content") or "")
    message = getattr(response, "message", None)
    return str(getattr(message, "content", "") or "")


def response_stat(response: Any, key: str) -> int:
    if isinstance(response, dict):
        return int(response.get(key) or 0)
    return int(getattr(response, key, 0) or 0)


def deterministic_options() -> dict[str, Any]:
    return {
        "seed": SEED,
        "temperature": TEMPERATURE,
        "top_k": TOP_K_SAMPLING,
        "top_p": TOP_P,
        "num_ctx": NUM_CTX,
        "num_predict": NUM_PREDICT,
    }


def deterministic_chat(client: Any, messages: list[dict[str, str]], *, json_mode: bool) -> Any:
    kwargs: dict[str, Any] = {
        "model": EXPECTED_MODEL,
        "messages": [dict(item) for item in messages],
        "stream": False,
        "options": deterministic_options(),
        "keep_alive": KEEP_ALIVE,
        "think": False,
    }
    if json_mode:
        kwargs["format"] = "json"
    response = client.chat(**kwargs)
    content = response_content(response)
    if not content.strip():
        raise RuntimeError("Ollama returned an empty response")
    return response


def install_deterministic_ollama(memory: Any) -> None:
    llm = memory.llm

    def wrapped(
        messages: list[dict[str, str]],
        response_format: Any = None,
        tools: Any = None,
        tool_choice: str = "auto",
        **kwargs: Any,
    ) -> str:
        if tools:
            raise RuntimeError("V45 extraction path unexpectedly requested tools")
        json_mode = bool(isinstance(response_format, dict) and response_format.get("type") == "json_object")
        response = deterministic_chat(llm.client, messages, json_mode=json_mode)
        return response_content(response)

    llm.generate_response = wrapped


def provider_microprobe() -> dict[str, Any]:
    from ollama import Client

    client = Client(host=OLLAMA_BASE_URL)
    warmup_messages = [
        {"role": "system", "content": "Return a valid JSON object only."},
        {"role": "user", "content": "Return an object with key warmup and boolean value true."},
    ]
    deterministic_chat(client, warmup_messages, json_mode=True)

    probe_messages = [
        {"role": "system", "content": "Return a valid JSON object only."},
        {"role": "user", "content": "Extract the stable fact from: Alice likes tea. Use key memory."},
    ]
    hashes = []
    sizes = []
    for _ in range(3):
        response = deterministic_chat(client, probe_messages, json_mode=True)
        content = response_content(response)
        hashes.append(sha_text(content))
        sizes.append(len(content.encode("utf-8")))
    return {
        "repetitions": 3,
        "response_hashes": hashes,
        "response_bytes": sizes,
        "all_equal": len(set(hashes)) == 1,
        "raw_response_persisted": False,
    }


def normalize_results(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, dict):
        values = raw.get("results", raw.get("memories", []))
    else:
        values = raw or []
    return [x for x in values if isinstance(x, dict)]


def text_hashes_in_order(rows: list[dict[str, Any]]) -> list[str]:
    out = []
    for row in rows:
        text = str(row.get("memory") or row.get("text") or row.get("data") or "")
        out.append(sha_text(text))
    return out


def fingerprint_rows(rows: list[dict[str, Any]]) -> list[str]:
    return sorted(text_hashes_in_order(rows))


def jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


def vector_summary(memory: Any, user_id: str, top_k: int = 1000) -> dict[str, Any]:
    raw = memory.get_all(filters={"user_id": user_id}, top_k=top_k)
    rows = normalize_results(raw)
    return {"count": len(rows), "hashes": fingerprint_rows(rows)}


def qdrant_backend_summary(memory: Any, user_id: str, page_size: int = 100) -> dict[str, Any]:
    from qdrant_client.http import models

    store = memory.vector_store
    filt = models.Filter(
        must=[models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))]
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
                str(m.get("content", ""))
                for m in messages
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
                    records.append(
                        {
                            "prompt_sha256": sha_text(prompt),
                            "prompt_bytes": len(prompt.encode("utf-8")),
                            "last_k_sha256": sha_text(last),
                            "last_k_bytes": len(last.encode("utf-8")),
                            "last_k_nonempty": bool(last.strip()),
                        }
                    )
        return original(*args, **kwargs)

    llm.generate_response = wrapped
    return records, original


def restore_prompt_recorder(memory: Any, original: Any) -> None:
    memory.llm.generate_response = original


async def answer_with_ollama(
    store: Any,
    *,
    search_raw: Any,
    question: str,
    question_date: str | None,
) -> tuple[str, dict[str, int]]:
    from agent_memory_benchmark.memory.llm import build_prompt

    context = "\n".join(store._memory_text(item) for item in store._items(search_raw))
    messages = build_prompt(context, question, question_date=question_date)
    response = await asyncio.to_thread(
        deterministic_chat,
        store._memory.llm.client,
        messages,
        json_mode=False,
    )
    content = response_content(response)
    prompt_tokens = response_stat(response, "prompt_eval_count")
    completion_tokens = response_stat(response, "eval_count")
    return content, {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }


async def build_failed_snapshot(
    *,
    Mem0MemoryStore: Any,
    example: Any,
    user_id: str,
    work: Path,
    fail_after: int,
) -> tuple[Path, dict[str, Any]]:
    seed_root = work / "seed"
    seed_store = Mem0MemoryStore(config=make_config(seed_root), user_id=user_id, model=EXPECTED_MODEL)
    install_deterministic_ollama(seed_store._memory)
    extraction_model = str(getattr(getattr(seed_store._memory.llm, "config", None), "model", ""))
    if extraction_model != EXPECTED_MODEL:
        raise RuntimeError(f"V45 extraction model drift: expected {EXPECTED_MODEL}, got {extraction_model!r}")

    await seed_store.reset()
    original_add = seed_store._memory.add
    calls = {"ok": 0, "faulted": False}

    def fail_once(*a: Any, **kw: Any):
        if calls["ok"] >= fail_after and not calls["faulted"]:
            calls["faulted"] = True
            raise RuntimeError("V45_INJECTED_MID_INGEST_FAILURE")
        out = original_add(*a, **kw)
        calls["ok"] += 1
        return out

    seed_store._memory.add = fail_once
    saw_fault = False
    try:
        await seed_store.ingest(example.sessions)
    except RuntimeError as exc:
        if str(exc) != "V45_INJECTED_MID_INGEST_FAILURE":
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
    return snapshot, {
        "extraction_model": extraction_model,
        "failed_attempt_message_state": pre_messages,
        "failed_attempt_vector_state": pre_vectors,
        "failed_attempt_qdrant_backend_state": pre_backend_vectors,
    }


async def run_arm(
    *,
    Mem0MemoryStore: Any,
    example: Any,
    user_id: str,
    snapshot: Path,
    root: Path,
    verified_clean: bool,
    top_k: int,
) -> dict[str, Any]:
    shutil.copytree(snapshot, root)
    store = Mem0MemoryStore(config=make_config(root), user_id=user_id, model=EXPECTED_MODEL)
    install_deterministic_ollama(store._memory)

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
        store = Mem0MemoryStore(config=make_config(root), user_id=user_id, model=EXPECTED_MODEL)
        install_deterministic_ollama(store._memory)

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
    search_raw = store._memory.search(qa.question, filters={"user_id": user_id}, top_k=top_k)
    search_rows = normalize_results(search_raw)
    answer, answer_usage = await answer_with_ollama(
        store,
        search_raw=search_raw,
        question=qa.question,
        question_date=example.metadata.get("question_date"),
    )

    result = {
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
        "retrieval_count": len(search_rows),
        "retrieval_ordered_hashes": text_hashes_in_order(search_rows),
        "retrieval_set_hashes": fingerprint_rows(search_rows),
        "answer_sha256": sha_text(answer),
        "answer_usage": answer_usage,
        "raw_benchmark_text_persisted": False,
    }
    close_memory(store._memory)
    return result


async def run_pair(
    *,
    Mem0MemoryStore: Any,
    example: Any,
    work: Path,
    example_idx: int,
    design: str,
    fail_after: int,
    top_k: int,
) -> dict[str, Any]:
    pair_work = work / design
    pair_work.mkdir(parents=True, exist_ok=True)
    user_id = f"benchmark-c33-v45-{design}-{example_idx}"
    snapshot, seed_receipt = await build_failed_snapshot(
        Mem0MemoryStore=Mem0MemoryStore,
        example=example,
        user_id=user_id,
        work=pair_work,
        fail_after=fail_after,
    )

    if design == "clean_clean":
        left = await run_arm(
            Mem0MemoryStore=Mem0MemoryStore,
            example=example,
            user_id=user_id,
            snapshot=snapshot,
            root=pair_work / "clean_a",
            verified_clean=True,
            top_k=top_k,
        )
        right = await run_arm(
            Mem0MemoryStore=Mem0MemoryStore,
            example=example,
            user_id=user_id,
            snapshot=snapshot,
            root=pair_work / "clean_b",
            verified_clean=True,
            top_k=top_k,
        )
        labels = ("clean_a", "clean_b")
    elif design == "native_clean":
        left = await run_arm(
            Mem0MemoryStore=Mem0MemoryStore,
            example=example,
            user_id=user_id,
            snapshot=snapshot,
            root=pair_work / "invoke_only",
            verified_clean=False,
            top_k=top_k,
        )
        right = await run_arm(
            Mem0MemoryStore=Mem0MemoryStore,
            example=example,
            user_id=user_id,
            snapshot=snapshot,
            root=pair_work / "verified_clean",
            verified_clean=True,
            top_k=top_k,
        )
        labels = ("invoke_only", "verified_clean")
    else:
        raise ValueError(f"Unknown design: {design}")

    first_left = left["extraction_prompt_records"]
    first_right = right["extraction_prompt_records"]
    first_prompt_equal = bool(
        first_left
        and first_right
        and first_left[0]["prompt_sha256"] == first_right[0]["prompt_sha256"]
    )
    memory_equal = left["final_memory_hashes"] == right["final_memory_hashes"]
    retrieval_order_equal = left["retrieval_ordered_hashes"] == right["retrieval_ordered_hashes"]
    retrieval_set_equal = left["retrieval_set_hashes"] == right["retrieval_set_hashes"]
    answer_equal = left["answer_sha256"] == right["answer_sha256"]

    return {
        "design": design,
        "seed_receipt": seed_receipt,
        labels[0]: left,
        labels[1]: right,
        "first_extraction_prompt_equal": first_prompt_equal,
        "memory_equal": memory_equal,
        "memory_jaccard": jaccard(left["final_memory_hashes"], right["final_memory_hashes"]),
        "retrieval_order_equal": retrieval_order_equal,
        "retrieval_set_equal": retrieval_set_equal,
        "retrieval_jaccard": jaccard(left["retrieval_set_hashes"], right["retrieval_set_hashes"]),
        "answer_equal": answer_equal,
    }


def clean_arm_preconditions(arm: dict[str, Any], top_k: int) -> bool:
    return (
        arm["after_verified_cleanup_messages"]["count"] == 0
        and arm["after_verified_cleanup_qdrant_backend"]["count"] == 0
        and arm["after_verified_cleanup_vectors"]["count"] == 0
        and arm["after_verified_cleanup_qdrant_backend"]["count_matches_enumeration"]
        and arm["final_memory_count"] >= QUALITY_MEMORY_MIN
        and arm["retrieval_count"] == top_k
    )


def stage_a_decision(stage: dict[str, Any], top_k: int) -> tuple[bool, str]:
    a = stage["clean_a"]
    b = stage["clean_b"]
    preconditions = clean_arm_preconditions(a, top_k) and clean_arm_preconditions(b, top_k)
    if not preconditions:
        return False, "EVALUATION_INVALID_PIPELINE_PRECONDITION"
    if not stage["first_extraction_prompt_equal"]:
        return False, "EVALUATION_INVALID_CLEAN_PROMPT_MISMATCH"
    if not (stage["memory_equal"] and stage["retrieval_order_equal"] and stage["answer_equal"]):
        return False, "EVALUATION_INVALID_PIPELINE_NONDETERMINISM"
    return True, "PIPELINE_NULL_CONTROL_PASS"


def stage_b_decision(stage: dict[str, Any], top_k: int) -> tuple[bool, bool, str]:
    native = stage["invoke_only"]
    clean = stage["verified_clean"]
    seed_messages = stage["seed_receipt"]["failed_attempt_message_state"]["count"]
    native_message_count = native["after_native_reset_messages"]["count"]
    clean_message_count = clean["after_verified_cleanup_messages"]["count"]
    native_qdrant = native["after_native_reset_qdrant_backend"]["count"]
    clean_qdrant = clean["after_verified_cleanup_qdrant_backend"]["count"]
    vector_receipts = (
        native["after_native_reset_qdrant_backend"]["count_matches_enumeration"]
        and clean["after_verified_cleanup_qdrant_backend"]["count_matches_enumeration"]
        and native["after_native_reset_vectors"]["count"] == native_qdrant
        and clean["after_verified_cleanup_vectors"]["count"] == clean_qdrant
    )
    quality = (
        native["final_memory_count"] >= QUALITY_MEMORY_MIN
        and clean["final_memory_count"] >= QUALITY_MEMORY_MIN
        and native["retrieval_count"] == top_k
        and clean["retrieval_count"] == top_k
    )
    trigger = (
        native_message_count == seed_messages
        and native_message_count > 0
        and clean_message_count == 0
        and native_qdrant == 0
        and clean_qdrant == 0
        and vector_receipts
        and quality
        and not stage["first_extraction_prompt_equal"]
    )
    if not trigger:
        return False, False, "INCOMPLETE_OR_E1_TRIGGER_NOT_ATTESTED"

    e2 = (not stage["memory_equal"]) or (not stage["retrieval_order_equal"])
    e3 = not stage["answer_equal"]
    if e2 and e3:
        return True, True, "PROMISING_CAUSAL_E2_E3"
    if e2:
        return True, False, "PROMISING_CAUSAL_E2"
    return False, e3, "ONE_CASE_CAUSAL_NULL"


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo.resolve()
    if git_head(repo) != REDIS_COMMIT:
        raise RuntimeError(f"Redis repo HEAD must be {REDIS_COMMIT}")

    mem0_version = importlib.metadata.version("mem0ai")
    if mem0_version != MEM0_VERSION:
        raise RuntimeError(f"mem0ai must be {MEM0_VERSION}, got {mem0_version}")
    ollama_py_version = importlib.metadata.version("ollama")
    if ollama_py_version != OLLAMA_PYTHON_VERSION:
        raise RuntimeError(f"ollama Python package must be {OLLAMA_PYTHON_VERSION}, got {ollama_py_version}")

    runtime = ollama_runtime_receipt()
    microprobe = provider_microprobe()
    base_result: dict[str, Any] = {
        "schema": "c33-v45-deterministic-local-causal-gate",
        "protocol_authority": "V45_PROSPECTIVE_FROZEN_GATE",
        "redis_commit": REDIS_COMMIT,
        "mem0_version": mem0_version,
        "mem0_commit": MEM0_COMMIT,
        "ollama_python_version": ollama_py_version,
        "ollama_runtime": runtime,
        "model_options": {
            "think": False,
            **deterministic_options(),
            "keep_alive": KEEP_ALIVE,
        },
        "embedding_provider": "fastembed",
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dims": EMBEDDING_DIMS,
        "provider_microprobe": microprobe,
        "stage_a": None,
        "stage_b": None,
        "highest_supported_evidence": "E1",
        "raw_benchmark_text_persisted_in_result_json": False,
    }
    if not microprobe["all_equal"]:
        base_result["decision"] = "EVALUATION_INVALID_PROVIDER_NONDETERMINISM"
        return base_result

    pkg = repo / "src"
    sys.path.insert(0, str(pkg))
    from agent_memory_benchmark.datasets import LongMemEvalAdapter
    from agent_memory_benchmark.memory.mem0_store import Mem0MemoryStore

    cohort = json.loads(args.cohort_file.read_text(encoding="utf-8"))
    allowed = {str(case["question_id"]): case for case in cohort.get("cases", [])}
    if args.question_id not in allowed:
        raise RuntimeError(f"question_id {args.question_id!r} is not in the frozen cohort")

    examples = LongMemEvalAdapter(args.split, cache_dir=args.cache_dir).load()
    random.Random(42).shuffle(examples)
    matches = [
        (i, ex)
        for i, ex in enumerate(examples)
        if str(ex.qa_pairs[0].question_id) == str(args.question_id)
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one shuffled example for question_id={args.question_id}, got {len(matches)}"
        )
    example_idx, example = matches[0]
    frozen_case = allowed[str(args.question_id)]
    if len(example.sessions) != int(frozen_case["session_count"]):
        raise RuntimeError(
            f"Frozen cohort drift for {args.question_id}: expected {frozen_case['session_count']} sessions, "
            f"got {len(example.sessions)}"
        )
    if args.fail_after < 1 or len(example.sessions) <= args.fail_after:
        raise RuntimeError("fail_after must be >=1 and smaller than session_count")

    base_result.update(
        {
            "split": args.split,
            "example_index_after_seed42_shuffle": example_idx,
            "question_id": str(example.qa_pairs[0].question_id),
            "question_type": str(example.qa_pairs[0].question_type),
            "question_id_hash": sha_text(str(example.qa_pairs[0].question_id)),
            "selection_sha256": frozen_case["selection_sha256"],
            "session_count": len(example.sessions),
            "fail_after_successful_sessions": args.fail_after,
            "top_k": args.top_k,
            "quality_memory_min": QUALITY_MEMORY_MIN,
        }
    )

    work = args.work.resolve()
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    stage_a = await run_pair(
        Mem0MemoryStore=Mem0MemoryStore,
        example=example,
        work=work,
        example_idx=example_idx,
        design="clean_clean",
        fail_after=args.fail_after,
        top_k=args.top_k,
    )
    stage_a_pass, stage_a_status = stage_a_decision(stage_a, args.top_k)
    stage_a["status"] = stage_a_status
    base_result["stage_a"] = stage_a
    if not stage_a_pass:
        base_result["decision"] = stage_a_status
        return base_result

    stage_b = await run_pair(
        Mem0MemoryStore=Mem0MemoryStore,
        example=example,
        work=work,
        example_idx=example_idx,
        design="native_clean",
        fail_after=args.fail_after,
        top_k=args.top_k,
    )
    e2, e3, stage_b_status = stage_b_decision(stage_b, args.top_k)
    stage_b["causal_e2_positive"] = e2
    stage_b["causal_e3_positive"] = e3
    stage_b["status"] = stage_b_status
    base_result["stage_b"] = stage_b
    if e2:
        base_result["highest_supported_evidence"] = "E3" if e3 else "E2"
    base_result["decision"] = stage_b_status
    return base_result


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--work", type=Path, required=True)
    p.add_argument("--cache-dir", type=Path, required=True)
    p.add_argument("--split", default="small", choices=["small"])
    p.add_argument("--question-id", default="b5ef892d")
    p.add_argument("--cohort-file", type=Path, required=True)
    p.add_argument("--fail-after", type=int, default=3)
    p.add_argument("--top-k", type=int, default=10)
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
