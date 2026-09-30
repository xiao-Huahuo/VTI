#!/usr/bin/env python3
"""V55 prospective 12-case formal deterministic experiment.

Three arms share the same frozen failed-attempt seed per case:
clean_ref, clean_rep, native. Native executes only after exact clean-clean pass.
"""
from __future__ import annotations

import argparse
import asyncio
import contextvars
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import random
import sys
from pathlib import Path
from typing import Any

from checkpoint import Checkpoints, atomic_json, now, sha_file, sha_tree
from schema import MEMORY_SCHEMA, validate_memory_json

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "third_party/agent-memory-server/agent-memory-benchmark"
V45_PATH = next((p for p in [ROOT / "history/v45/code/redis_v45_ollama_deterministic_gate.py", ROOT / "v45/code/redis_v45_ollama_deterministic_gate.py", ROOT / "Science_V45_patch/v45/code/redis_v45_ollama_deterministic_gate.py"] if p.is_file()), ROOT / "history/v45/code/redis_v45_ollama_deterministic_gate.py")
PROTOCOL = ROOT / "v55_formal/FORMAL_PROTOCOL_V55.json"
COHORT = ROOT / "v55_formal/FROZEN_COHORT_V55.json"
DATASET = Path.home() / ".cache/agent-memory-benchmark/longmemeval-v1/longmemeval_s_cleaned.json"
RUNS = ROOT / "v55_formal/runs"
DRILLS = ROOT / "v55_formal/drills"
RESULTS = ROOT / "v55_formal/results"
REPEAT_PENALTY = 1.1
FAIL_AFTER = 3
TOP_K = 10
QUALITY_MIN = 100
CASE_SPECS = json.loads(COHORT.read_text(encoding="utf-8"))["cases"]

spec = importlib.util.spec_from_file_location("v45_frozen_engine", V45_PATH)
v45 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(v45)
old_options = v45.deterministic_options
v45.deterministic_options = lambda: {**old_options(), "repeat_penalty": REPEAT_PENALTY}
raw_log_path: contextvars.ContextVar[Path | None] = contextvars.ContextVar("v48_raw_log_path", default=None)


class CaseGenerationOrSchemaError(RuntimeError):
    """Terminal single-case model or response-schema failure; never retried."""


def schema_chat(client: Any, messages: list[dict[str, str]], *, json_mode: bool) -> Any:
    kwargs: dict[str, Any] = {
        "model": v45.EXPECTED_MODEL,
        "messages": [dict(item) for item in messages],
        "stream": False,
        "options": v45.deterministic_options(),
        "keep_alive": v45.KEEP_ALIVE,
        "think": False,
    }
    if json_mode:
        kwargs["format"] = MEMORY_SCHEMA
    try:
        response = client.chat(**kwargs)
    except Exception as exc:
        raise CaseGenerationOrSchemaError(f"Ollama generation failed: {type(exc).__name__}: {exc}") from exc
    if not v45.response_content(response).strip():
        raise CaseGenerationOrSchemaError("Empty Ollama response")
    return response


def logged_chat(client: Any, messages: list[dict[str, str]], *, json_mode: bool) -> Any:
    response = schema_chat(client, messages, json_mode=json_mode)
    path = raw_log_path.get()
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "at": now(),
            "prompt_sha256": v45.sha_text(json.dumps(messages, ensure_ascii=False, sort_keys=True)),
            "json_mode": json_mode,
            "raw_response": v45.response_content(response),
            "prompt_tokens": v45.response_stat(response, "prompt_eval_count"),
            "completion_tokens": v45.response_stat(response, "eval_count"),
        }
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    if json_mode:
        try:
            validate_memory_json(v45.response_content(response))
        except Exception as exc:
            raise CaseGenerationOrSchemaError(f"Memory response schema failed: {type(exc).__name__}: {exc}") from exc
    return response


v45.deterministic_chat = logged_chat


def status(path: Path, **payload: Any) -> None:
    atomic_json(path, {"updated_at": now(), **payload})


def load_cases() -> tuple[dict[str, tuple[int, Any]], Any]:
    sys.path.insert(0, str(BENCH / "src"))
    from agent_memory_benchmark.datasets import LongMemEvalAdapter
    from agent_memory_benchmark.memory.mem0_store import Mem0MemoryStore

    examples = LongMemEvalAdapter("small", cache_dir=DATASET.parents[1]).load()
    random.Random(42).shuffle(examples)
    by_qid: dict[str, tuple[int, Any]] = {}
    wanted = {spec["question_id"]: spec for spec in CASE_SPECS}
    for i, example in enumerate(examples):
        qid = str(example.qa_pairs[0].question_id)
        if qid in wanted:
            by_qid[qid] = (i, example)
    if set(by_qid) != set(wanted):
        raise RuntimeError("Frozen V55 frozen formal cohort selection drift: missing case")
    for qid, (idx, example) in by_qid.items():
        expected = wanted[qid]["session_count"]
        if len(example.sessions) != expected:
            raise RuntimeError(f"Frozen V55 session-count drift for {qid}: {len(example.sessions)} != {expected}")
        if example.qa_pairs[0].question_type != wanted[qid]["question_type"]:
            raise RuntimeError(f"Frozen V55 question-type drift for {qid}")
    return by_qid, Mem0MemoryStore


def global_identity(run_id: str, runtime: dict[str, Any]) -> dict[str, Any]:
    if os.environ.get("MEM0_TELEMETRY", "").lower() != "false":
        raise RuntimeError("MEM0_TELEMETRY=false is required for V55")
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if [item["rank"] for item in CASE_SPECS] != list(range(13, 25)):
        raise RuntimeError("Formal cohort must contain held-out ranks 13-24")
    if sha_file(COHORT) != protocol["selection"]["source_sha256"]:
        raise RuntimeError("Protocol / cohort SHA-256 mismatch")
    if sha_file(DATASET) != json.loads(COHORT.read_text())["source_dataset"]["expected_sha256"]:
        raise RuntimeError("Pinned LongMemEval dataset SHA-256 mismatch")
    if runtime["model_digest"] != protocol["stack"]["model_digest"]:
        raise RuntimeError("Pinned Ollama model digest drift")
    if runtime["ollama_version"] != protocol["stack"].get("ollama_server_version", runtime["ollama_version"]):
        raise RuntimeError("Ollama server version drift")
    if protocol["stack"]["redis_commit"] != v45.REDIS_COMMIT or protocol["stack"]["mem0_version"] != v45.MEM0_VERSION:
        raise RuntimeError("Protocol / frozen Redis-Mem0 engine identity drift")
    expected_schema = protocol["stack"]["extraction_schema_sha256"]
    actual_schema = hashlib.sha256(json.dumps(MEMORY_SCHEMA, sort_keys=True).encode()).hexdigest()
    if actual_schema != expected_schema:
        raise RuntimeError("V55 extraction schema drift")
    if v45.git_head(BENCH) != v45.REDIS_COMMIT:
        raise RuntimeError("Redis benchmark commit drift")
    if importlib.metadata.version("mem0ai") != v45.MEM0_VERSION:
        raise RuntimeError("Mem0 version drift")
    if importlib.metadata.version("ollama") != v45.OLLAMA_PYTHON_VERSION:
        raise RuntimeError("Ollama Python version drift")
    if importlib.metadata.version("fastembed") != protocol["stack"]["fastembed_version"]:
        raise RuntimeError("FastEmbed version drift")
    if importlib.metadata.version("qdrant-client") != protocol["stack"]["qdrant_client_version"]:
        raise RuntimeError("Qdrant client version drift")
    return {
        "schema": "c33-v55-run-identity",
        "run_id": run_id,
        "protocol_sha256": sha_file(PROTOCOL),
        "runner_sha256": sha_file(Path(__file__)),
        "checkpoint_code_sha256": sha_file(Path(__file__).with_name("checkpoint.py")),
        "schema_code_sha256": sha_file(Path(__file__).with_name("schema.py")),
        "v45_engine_sha256": sha_file(V45_PATH),
        "cohort_sha256": sha_file(COHORT),
        "dataset_sha256": sha_file(DATASET),
        "redis_commit": v45.REDIS_COMMIT,
        "mem0_version": v45.MEM0_VERSION,
        "ollama_python_version": v45.OLLAMA_PYTHON_VERSION,
        "ollama_server_version": runtime["ollama_version"],
        "fastembed_version": importlib.metadata.version("fastembed"),
        "qdrant_client_version": importlib.metadata.version("qdrant-client"),
        "model_digest": runtime["model_digest"],
        "model_options": v45.deterministic_options(),
        "extraction_schema_sha256": actual_schema,
        "case_specs": CASE_SPECS,
        "fail_after_successful_sessions": FAIL_AFTER,
        "top_k": TOP_K,
        "quality_memory_min": QUALITY_MIN,
    }


def case_identity(global_id: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    return {**global_id, "schema": "c33-v55-case-identity", "case": spec}


async def ingest_one(store: Checkpoints, arm: str, unit: int, source: Path, session: Any,
                     user_id: str, Mem0MemoryStore: Any, total_sessions: int) -> Path:
    attempt = store.attempt(arm, unit, source)
    memory_store = None
    records: list[dict[str, Any]] = []
    try:
        memory_store = Mem0MemoryStore(config=v45.make_config(attempt), user_id=user_id,
                                       model=v45.EXPECTED_MODEL)
        v45.install_deterministic_ollama(memory_store._memory)
        records, original = v45.install_prompt_recorder(memory_store._memory)
        raw_token = raw_log_path.set(attempt / "raw_model_outputs.jsonl")
        try:
            await memory_store.ingest([session])
        finally:
            raw_log_path.reset(raw_token)
            v45.restore_prompt_recorder(memory_store._memory, original)
        v45.close_memory(memory_store._memory)
        memory_store = None
        receipt = {
            "session_index_one_based": unit,
            "prompt_records": records,
            "scoped_message_count": v45.message_summary(attempt / "history.db", user_id)["count"],
        }
        snapshot = store.commit(arm, unit, attempt, receipt)
        status(store.root / "status.json", phase="INGESTING", arm=arm,
               completed_session=unit, total_sessions=total_sessions)
        return snapshot
    except BaseException as exc:
        if memory_store is not None:
            v45.close_memory(memory_store._memory)
        if isinstance(exc, Exception):
            error_path = store.record_error(arm, unit, exc, attempt)
            status(store.root / "status.json", phase="ERROR", arm=arm, failed_session=unit,
                   error_record=str(error_path.relative_to(store.root)))
        raise


async def ensure_seed(store: Checkpoints, example: Any, example_idx: int, qid: str,
                      Mem0MemoryStore: Any) -> tuple[Path, dict[str, Any], str]:
    arm = "seed_matched"
    user_id = f"benchmark-c33-v55-{qid}-{example_idx}"
    latest = store.latest(arm)
    if latest is None:
        initial = store.root / "attempts" / arm / f"000-seed-{random.getrandbits(48):012x}"
        initial.mkdir(parents=True, exist_ok=False)
        memory_store = Mem0MemoryStore(config=v45.make_config(initial), user_id=user_id,
                                       model=v45.EXPECTED_MODEL)
        v45.install_deterministic_ollama(memory_store._memory)
        await memory_store.reset()
        v45.close_memory(memory_store._memory)
        latest_path = store.commit(arm, 0, initial, {"state": "EMPTY_AFTER_NATIVE_RESET"})
        latest_unit = 0
    else:
        latest_unit, latest_path, _ = latest
    for unit in range(latest_unit + 1, FAIL_AFTER + 1):
        latest_path = await ingest_one(store, arm, unit, latest_path, example.sessions[unit - 1],
                                       user_id, Mem0MemoryStore, len(example.sessions))
    fault_path = store.root / "stages" / "seed_matched_injected_fault.json"
    if not fault_path.is_file():
        fault_attempt = store.attempt(arm, FAIL_AFTER + 1, latest_path)
        memory_store = Mem0MemoryStore(config=v45.make_config(fault_attempt), user_id=user_id,
                                       model=v45.EXPECTED_MODEL)
        v45.install_deterministic_ollama(memory_store._memory)
        original_add = memory_store._memory.add
        memory_store._memory.add = lambda *a, **kw: (_ for _ in ()).throw(
            RuntimeError("V55_INJECTED_MID_INGEST_FAILURE"))
        saw_fault = False
        try:
            await memory_store.ingest([example.sessions[FAIL_AFTER]])
        except RuntimeError as exc:
            saw_fault = str(exc) == "V55_INJECTED_MID_INGEST_FAILURE"
            if not saw_fault:
                raise
        finally:
            memory_store._memory.add = original_add
            v45.close_memory(memory_store._memory)
        if not saw_fault:
            raise RuntimeError("Injected fault not observed")
        if v45.message_summary(fault_attempt / "history.db", user_id) != v45.message_summary(latest_path / "history.db", user_id):
            raise RuntimeError("Injected fault altered persisted seed message state")
        atomic_json(fault_path, {
            "fault_seen": True,
            "after_successful_sessions": FAIL_AFTER,
            "snapshot_sha256": store.validate(arm, FAIL_AFTER)["snapshot_sha256"],
        })
    state_path = store.attempt(arm, FAIL_AFTER + 2, latest_path)
    memory_store = Mem0MemoryStore(config=v45.make_config(state_path), user_id=user_id,
                                   model=v45.EXPECTED_MODEL)
    try:
        receipt = {
            "failed_attempt_message_state": v45.message_summary(state_path / "history.db", user_id),
            "failed_attempt_vector_state": v45.vector_summary(memory_store._memory, user_id),
            "failed_attempt_qdrant_backend_state": v45.qdrant_backend_summary(memory_store._memory, user_id),
        }
    finally:
        v45.close_memory(memory_store._memory)
    if receipt["failed_attempt_message_state"]["count"] <= 0:
        raise RuntimeError("Failed-attempt seed has no scoped sidecar messages")
    return latest_path, receipt, user_id


async def ensure_arm_start(store: Checkpoints, arm: str, seed: Path, user_id: str,
                           Mem0MemoryStore: Any, verified_clean: bool) -> None:
    if store.latest(arm) is not None:
        return
    attempt = store.attempt(arm, 0, seed)
    memory_store = Mem0MemoryStore(config=v45.make_config(attempt), user_id=user_id,
                                   model=v45.EXPECTED_MODEL)
    v45.install_deterministic_ollama(memory_store._memory)
    try:
        before_messages = v45.message_summary(attempt / "history.db", user_id)
        before_vectors = v45.vector_summary(memory_store._memory, user_id)
        before_backend = v45.qdrant_backend_summary(memory_store._memory, user_id)
        await memory_store.reset()
        native_messages = v45.message_summary(attempt / "history.db", user_id)
        native_vectors = v45.vector_summary(memory_store._memory, user_id)
        native_backend = v45.qdrant_backend_summary(memory_store._memory, user_id)
        v45.close_memory(memory_store._memory)
        memory_store = None
        deleted = v45.delete_scope_messages(attempt / "history.db", user_id) if verified_clean else 0
        memory_store = Mem0MemoryStore(config=v45.make_config(attempt), user_id=user_id,
                                       model=v45.EXPECTED_MODEL)
        clean_messages = v45.message_summary(attempt / "history.db", user_id)
        clean_vectors = v45.vector_summary(memory_store._memory, user_id)
        clean_backend = v45.qdrant_backend_summary(memory_store._memory, user_id)
        v45.close_memory(memory_store._memory)
        memory_store = None
        store.commit(arm, 0, attempt, {
            "arm": arm,
            "verified_clean": verified_clean,
            "before_reset_messages": before_messages,
            "before_reset_vectors": before_vectors,
            "before_reset_qdrant_backend": before_backend,
            "after_native_reset_messages": native_messages,
            "after_native_reset_vectors": native_vectors,
            "after_native_reset_qdrant_backend": native_backend,
            "verified_delete_count": deleted,
            "after_verified_cleanup_messages": clean_messages,
            "after_verified_cleanup_vectors": clean_vectors,
            "after_verified_cleanup_qdrant_backend": clean_backend,
        })
    except BaseException:
        if memory_store is not None:
            v45.close_memory(memory_store._memory)
        raise


async def ensure_arm_final(store: Checkpoints, arm: str, example: Any, user_id: str,
                           Mem0MemoryStore: Any) -> dict[str, Any]:
    existing = store.read_stage(f"arm_{arm}")
    if existing is not None:
        return existing
    total_sessions = len(example.sessions)
    latest = store.latest(arm)
    if latest is None:
        raise RuntimeError(f"Arm {arm} lacks reset checkpoint")
    latest_unit, latest_path, _ = latest
    for unit in range(latest_unit + 1, total_sessions + 1):
        latest_path = await ingest_one(store, arm, unit, latest_path, example.sessions[unit - 1],
                                       user_id, Mem0MemoryStore, total_sessions)
    store.validate(arm, total_sessions)
    analysis = store.attempt(arm, total_sessions + 1, latest_path)
    memory_store = Mem0MemoryStore(config=v45.make_config(analysis), user_id=user_id,
                                   model=v45.EXPECTED_MODEL)
    v45.install_deterministic_ollama(memory_store._memory)
    try:
        final_raw = memory_store._memory.get_all(filters={"user_id": user_id}, top_k=1000)
        final_rows = v45.normalize_results(final_raw)
        qa = example.qa_pairs[0]
        search_raw = memory_store._memory.search(qa.question, filters={"user_id": user_id}, top_k=TOP_K)
        search_rows = v45.normalize_results(search_raw)
        raw_token = raw_log_path.set(analysis / "raw_model_outputs.jsonl")
        try:
            answer, usage = await v45.answer_with_ollama(
                memory_store, search_raw=search_raw, question=qa.question,
                question_date=example.metadata.get("question_date"))
        finally:
            raw_log_path.reset(raw_token)
        answer_path = analysis / "answer.txt"
        answer_path.write_text(answer, encoding="utf-8")
        first = store.validate(arm, 1)["receipt"]["prompt_records"]
        reset = store.validate(arm, 0)["receipt"]
        result = {
            **reset,
            "extraction_prompt_records": first,
            "final_memory_count": len(final_rows),
            "final_memory_hashes": v45.fingerprint_rows(final_rows),
            "retrieval_count": len(search_rows),
            "retrieval_ordered_hashes": v45.text_hashes_in_order(search_rows),
            "retrieval_set_hashes": v45.fingerprint_rows(search_rows),
            "answer_sha256": v45.sha_text(answer),
            "answer_usage": usage,
            "answer_text_path": str(answer_path.relative_to(ROOT)),
            "checkpoint_count": total_sessions + 1,
        }
        v45.close_memory(memory_store._memory)
        memory_store = None
        store.save_stage(f"arm_{arm}", result)
        return result
    except BaseException:
        if memory_store is not None:
            v45.close_memory(memory_store._memory)
        raise


def compare(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    lp, rp = left["extraction_prompt_records"], right["extraction_prompt_records"]
    return {
        "first_extraction_prompt_equal": bool(lp and rp and lp[0]["prompt_sha256"] == rp[0]["prompt_sha256"]),
        "memory_equal": left["final_memory_hashes"] == right["final_memory_hashes"],
        "memory_jaccard": v45.jaccard(left["final_memory_hashes"], right["final_memory_hashes"]),
        "retrieval_order_equal": left["retrieval_ordered_hashes"] == right["retrieval_ordered_hashes"],
        "retrieval_set_equal": left["retrieval_set_hashes"] == right["retrieval_set_hashes"],
        "retrieval_jaccard": v45.jaccard(left["retrieval_set_hashes"], right["retrieval_set_hashes"]),
        "answer_equal": left["answer_sha256"] == right["answer_sha256"],
    }


def clean_checks(a: dict[str, Any], b: dict[str, Any], cmp: dict[str, Any]) -> dict[str, bool]:
    quality = (
        a["final_memory_count"] >= QUALITY_MIN and b["final_memory_count"] >= QUALITY_MIN and
        a["retrieval_count"] == TOP_K and b["retrieval_count"] == TOP_K
    )
    clean_receipts = all(
        arm["after_verified_cleanup_messages"]["count"] == 0
        and arm["after_verified_cleanup_vectors"]["count"] == 0
        and arm["after_verified_cleanup_qdrant_backend"]["count"] == 0
        and arm["after_verified_cleanup_qdrant_backend"]["count_matches_enumeration"]
        for arm in (a, b)
    )
    return {"quality": quality, "clean_reset_receipts": clean_receipts,
            "first_extraction_prompt": cmp["first_extraction_prompt_equal"],
            "memory": cmp["memory_equal"],
            "ordered_retrieval": cmp["retrieval_order_equal"],
            "answer_text": cmp["answer_equal"]}


def clean_pass(a: dict[str, Any], b: dict[str, Any], cmp: dict[str, Any]) -> bool:
    return all(clean_checks(a, b, cmp).values())


def e1_pass(native: dict[str, Any], clean: dict[str, Any], cmp: dict[str, Any], seed_count: int) -> bool:
    return all([
        seed_count > 0,
        native["after_native_reset_messages"]["count"] == seed_count,
        clean["after_verified_cleanup_messages"]["count"] == 0,
        native["after_verified_cleanup_vectors"]["count"] == 0,
        clean["after_verified_cleanup_vectors"]["count"] == 0,
        native["after_verified_cleanup_qdrant_backend"]["count"] == 0,
        clean["after_verified_cleanup_qdrant_backend"]["count"] == 0,
        native["after_verified_cleanup_qdrant_backend"]["count_matches_enumeration"],
        clean["after_verified_cleanup_qdrant_backend"]["count_matches_enumeration"],
        not cmp["first_extraction_prompt_equal"],
    ])


async def first_extraction_probe(store: Checkpoints, example: Any, user_id: str,
                                 Mem0MemoryStore: Any) -> dict[str, Any]:
    """Repeat the actual first clean extraction from the same reset checkpoint."""
    reset = store.checkpoint_path("clean_ref", 0)
    store.validate("clean_ref", 0)
    repetitions = []
    for rep in range(1, 4):
        saved = store.read_stage(f"probe_rep_{rep:02d}")
        if saved is not None:
            attempt_path = ROOT / saved["attempt_path"]
            if sha_tree(attempt_path) != saved["attempt_sha256"]:
                raise RuntimeError(f"Probe repetition {rep} receipt drift")
            repetitions.append(saved)
            continue
        attempt = store.attempt("provider_probe", rep, reset)
        memory_store = None
        try:
            memory_store = Mem0MemoryStore(config=v45.make_config(attempt), user_id=user_id,
                                           model=v45.EXPECTED_MODEL)
            v45.install_deterministic_ollama(memory_store._memory)
            records, original = v45.install_prompt_recorder(memory_store._memory)
            raw_path = attempt / "raw_model_outputs.jsonl"
            token = raw_log_path.set(raw_path)
            try:
                await memory_store.ingest([example.sessions[0]])
            finally:
                raw_log_path.reset(token)
                v45.restore_prompt_recorder(memory_store._memory, original)
            v45.close_memory(memory_store._memory)
            memory_store = None
            calls = [json.loads(line) for line in raw_path.read_text().splitlines() if line.strip()]
            if not calls or not records:
                raise RuntimeError("First extraction probe captured no model response or prompt")
            receipt = {"rep": rep,
                       "prompt_hashes": [r["prompt_sha256"] for r in records],
                       "content_hashes": [v45.sha_text(r["raw_response"]) for r in calls],
                       "raw_receipt_path": str(raw_path.relative_to(ROOT)),
                       "attempt_path": str(attempt.relative_to(ROOT)),
                       "attempt_sha256": sha_tree(attempt)}
            store.save_stage(f"probe_rep_{rep:02d}", receipt)
            repetitions.append(receipt)
        except BaseException:
            if memory_store is not None:
                v45.close_memory(memory_store._memory)
            raise
    signatures = [(tuple(r["prompt_hashes"]), tuple(r["content_hashes"])) for r in repetitions]
    return {"repetitions": repetitions, "all_equal": len(set(signatures)) == 1,
            "source": "actual_case_first_clean_extraction_from_shared_reset"}


async def run_case(parent_run: Path, global_id: dict[str, Any], spec: dict[str, Any],
                   example_idx: int, example: Any, Mem0MemoryStore: Any) -> dict[str, Any]:
    case_root = parent_run / f"rank_{spec['rank']:02d}_{spec['question_id']}"
    store = Checkpoints(case_root, case_identity(global_id, spec))
    completed = store.read_stage("final")
    if completed is not None:
        if store.read_stage("provider_probe") != completed.get("provider_microprobe"):
            raise RuntimeError("Completed case provider-probe receipt mismatch")
        if completed.get("stage_a") is not None:
            if store.read_stage("stage_a") != completed["stage_a"]:
                raise RuntimeError("Completed case Stage A receipt mismatch")
            for arm in ("clean_ref", "clean_rep"):
                store.validate(arm, len(example.sessions))
        if completed.get("stage_b") is not None:
            if store.read_stage("stage_b") != completed["stage_b"]:
                raise RuntimeError("Completed case Stage B receipt mismatch")
            store.validate("native", len(example.sessions))
        return completed
    status(store.root / "status.json", phase="STARTED", case=spec)

    seed, seed_receipt, user_id = await ensure_seed(store, example, example_idx,
                                                     spec["question_id"], Mem0MemoryStore)
    await ensure_arm_start(store, "clean_ref", seed, user_id, Mem0MemoryStore, True)

    probe = store.read_stage("provider_probe")
    if probe is None:
        probe = await first_extraction_probe(store, example, user_id, Mem0MemoryStore)
        store.save_stage("provider_probe", probe)
    if not probe["all_equal"]:
        result = {"case": spec, "status": "EVALUATION_INVALID_PROVIDER_NONDETERMINISM",
                  "provider_microprobe": probe, "decision": "EVALUATION_INVALID_PROVIDER_NONDETERMINISM"}
        store.save_stage("final", result)
        status(store.root / "status.json", phase="COMPLETE", decision=result["decision"])
        return result

    stage_a = store.read_stage("stage_a")
    if stage_a is None:
        await ensure_arm_start(store, "clean_ref", seed, user_id, Mem0MemoryStore, True)
        await ensure_arm_start(store, "clean_rep", seed, user_id, Mem0MemoryStore, True)
        clean_ref = await ensure_arm_final(store, "clean_ref", example, user_id, Mem0MemoryStore)
        clean_rep = await ensure_arm_final(store, "clean_rep", example, user_id, Mem0MemoryStore)
        null_cmp = compare(clean_ref, clean_rep)
        checks = clean_checks(clean_ref, clean_rep, null_cmp)
        stage_a_pass = all(checks.values())
        stage_a = {"status": "PIPELINE_NULL_CONTROL_PASS" if stage_a_pass else "PIPELINE_NULL_CONTROL_FAIL",
                   "seed_receipt": seed_receipt, "comparison": null_cmp,
                   "checks": checks, "failure_reasons": sorted(k for k, ok in checks.items() if not ok),
                   "clean_ref": clean_ref, "clean_rep": clean_rep}
        store.save_stage("stage_a", stage_a)
    else:
        clean_ref = stage_a["clean_ref"]
        stage_a_pass = stage_a["status"] == "PIPELINE_NULL_CONTROL_PASS"
        for arm in ("clean_ref", "clean_rep"):
            store.validate(arm, len(example.sessions))
            if store.read_stage(f"arm_{arm}") != stage_a[arm]:
                raise RuntimeError(f"Persisted Stage A / {arm} receipt mismatch")
    if not stage_a_pass:
        result = {"case": spec, "provider_microprobe": probe, "stage_a": stage_a,
                  "stage_b": None, "decision": "STOP_EXTENSION_CLEAN_CALIBRATION_FAIL"}
        store.save_stage("final", result)
        status(store.root / "status.json", phase="COMPLETE", decision=result["decision"])
        return result

    stage_b = store.read_stage("stage_b")
    if stage_b is None:
        await ensure_arm_start(store, "native", seed, user_id, Mem0MemoryStore, False)
        native = await ensure_arm_final(store, "native", example, user_id, Mem0MemoryStore)
        causal_cmp = compare(native, clean_ref)
        e1 = e1_pass(native, clean_ref, causal_cmp,
                     seed_receipt["failed_attempt_message_state"]["count"])
        quality = native["final_memory_count"] >= QUALITY_MIN and native["retrieval_count"] == TOP_K
        e2 = e1 and quality and (not causal_cmp["memory_equal"] or not causal_cmp["retrieval_order_equal"])
        e3 = e2 and not causal_cmp["answer_equal"]
        if not e1:
            decision = "EVALUATION_INVALID_E1_RECEIPT"
        elif not quality:
            decision = "EVALUATION_INVALID_QUALITY_FLOOR"
        elif e3:
            decision = "CAUSAL_E2_E3_TEXT_POSITIVE"
        elif e2:
            decision = "CAUSAL_E2_POSITIVE_E3_TEXT_NULL"
        else:
            decision = "CALIBRATED_E2_E3_TEXT_NULL"
        stage_b = {"status": decision, "e1_pass": e1, "native_quality_pass": quality,
                   "causal_e2_positive": e2, "causal_e3_text_positive": e3,
                   "comparison": causal_cmp, "native": native, "clean_ref": clean_ref}
        store.save_stage("stage_b", stage_b)
    else:
        decision = stage_b["status"]
        store.validate("native", len(example.sessions))
        if store.read_stage("arm_native") != stage_b["native"]:
            raise RuntimeError("Persisted Stage B / native receipt mismatch")
    result = {"case": spec, "provider_microprobe": probe, "stage_a": stage_a,
              "stage_b": stage_b, "decision": decision}
    store.save_stage("final", result)
    status(store.root / "status.json", phase="COMPLETE", decision=decision)
    return result


async def run(args: argparse.Namespace) -> dict[str, Any]:
    runtime = v45.ollama_runtime_receipt()
    identity = global_identity(args.run_id, runtime)
    run_root = RUNS / args.run_id
    if run_root.exists() and not (run_root / "identity.json").exists() and any(run_root.iterdir()):
        raise RuntimeError("Refusing to adopt an unregistered nonempty V55 run directory")
    run_root.mkdir(parents=True, exist_ok=True)
    identity_path = run_root / "identity.json"
    if identity_path.exists():
        existing = json.loads(identity_path.read_text(encoding="utf-8"))
        if existing != identity:
            raise RuntimeError("V55 run identity drift")
    else:
        atomic_json(identity_path, identity)
    status(run_root / "status.json", phase="STARTED", run_id=args.run_id)

    cases, Mem0MemoryStore = load_cases()
    results: list[dict[str, Any]] = []
    for spec in CASE_SPECS:
        qid = spec["question_id"]
        idx, example = cases[qid]
        try:
            result = await run_case(run_root, identity, spec, idx, example, Mem0MemoryStore)
        except CaseGenerationOrSchemaError as exc:
            case_root = run_root / f"rank_{spec['rank']:02d}_{qid}"
            store = Checkpoints(case_root, case_identity(identity, spec))
            result = {"case": spec, "status": "EVALUATION_INVALID_GENERATION_OR_SCHEMA",
                      "decision": "EVALUATION_INVALID_GENERATION_OR_SCHEMA",
                      "error_type": type(exc).__name__, "error": str(exc)[:1000],
                      "provider_microprobe": store.read_stage("provider_probe"),
                      "stage_a": store.read_stage("stage_a"),
                      "stage_b": store.read_stage("stage_b"),
                      "e2_evaluable": False, "automatic_retry": False}
            store.save_stage("final", result)
            status(store.root / "status.json", phase="COMPLETE_INVALID",
                   decision=result["decision"], error=result["error"])
        results.append(result)
        # Formal batch stop: among the first three selected cases, two identical
        # calibration/provider failures indicate a systemic null-control problem.
        if len(results) <= 3:
            bad = []
            for row in results:
                if row["decision"] == "EVALUATION_INVALID_PROVIDER_NONDETERMINISM":
                    bad.append(("provider_nondeterminism",))
                elif row["decision"] == "STOP_EXTENSION_CLEAN_CALIBRATION_FAIL":
                    bad.append(tuple(row["stage_a"]["failure_reasons"]))
            if len(bad) >= 2 and len(set(bad)) == 1:
                break

    complete_formal = len(results) == len(CASE_SPECS)
    valid_count = sum(bool(r.get("stage_a") and r["stage_a"].get("status") == "PIPELINE_NULL_CONTROL_PASS") for r in results)
    evaluable_count = sum(bool(r.get("stage_b") and r["stage_b"].get("e1_pass")
                               and r["stage_b"].get("native_quality_pass")) for r in results)
    e2_count = sum(bool(r.get("stage_b") and r["stage_b"].get("causal_e2_positive")) for r in results)
    e3_count = sum(bool(r.get("stage_b") and r["stage_b"].get("causal_e3_text_positive")) for r in results)
    answer_diff_cases = [r["case"]["question_id"] for r in results
                         if r.get("stage_b") and not r["stage_b"]["comparison"]["answer_equal"]]
    if not complete_formal:
        decision = "FORMAL_BATCH_INCOMPLETE_STOP_RULE"
    elif evaluable_count == 0:
        decision = "FORMAL_12_CASE_COMPLETE_NO_E2_EVALUABLE_CASES"
    elif e2_count:
        decision = "FORMAL_12_CASE_COMPLETE_WITH_CAUSAL_E2"
    else:
        decision = "FORMAL_12_CASE_COMPLETE_E2_NULL_AMONG_EVALUABLE_CASES"
    aggregate = {
        "schema": "c33-v55-formal-result",
        "run_id": args.run_id,
        "protocol_authority": "V55_PROSPECTIVE_FROZEN_FORMAL",
        "identity": identity,
        "cases": results,
        "selected_case_count": len(CASE_SPECS),
        "terminal_case_count": len(results),
        "stage_a_valid_count": valid_count,
        "e2_evaluable_count": evaluable_count,
        "generation_schema_invalid_count": sum(r.get("decision") == "EVALUATION_INVALID_GENERATION_OR_SCHEMA" for r in results),
        "causal_e2_positive_count": e2_count,
        "answer_text_e3_positive_count": e3_count,
        "answer_different_question_ids": answer_diff_cases,
        "official_e4_measured": False,
        "decision": decision,
    }
    final_path = run_root / "final.json"
    if final_path.exists():
        prior = json.loads(final_path.read_text(encoding="utf-8"))
        if prior != aggregate:
            raise RuntimeError("Existing V48 final result differs from recomputation")
    else:
        atomic_json(final_path, aggregate)
    status(run_root / "status.json", phase="COMPLETE", run_id=args.run_id, decision=decision)
    return aggregate


async def run_drill(args: argparse.Namespace) -> None:
    """Exercise the real runner on a prior V42 case, isolated from formal results."""
    if args.drill_qid != "b5ef892d":
        raise RuntimeError("Only the historical V42 rank-1 case is allowed for the resume drill")
    runtime = v45.ollama_runtime_receipt()
    identity = global_identity(args.run_id, runtime)
    sys.path.insert(0, str(BENCH / "src"))
    from agent_memory_benchmark.datasets import LongMemEvalAdapter
    from agent_memory_benchmark.memory.mem0_store import Mem0MemoryStore
    examples = LongMemEvalAdapter("small", cache_dir=DATASET.parents[1]).load()
    random.Random(42).shuffle(examples)
    matches = [(i, e) for i, e in enumerate(examples)
               if str(e.qa_pairs[0].question_id) == args.drill_qid]
    if len(matches) != 1:
        raise RuntimeError("Historical drill case missing or duplicated")
    idx, example = matches[0]
    spec = {"rank": 1, "question_id": args.drill_qid,
            "question_type": example.qa_pairs[0].question_type,
            "session_count": len(example.sessions), "role": "PRE_FORMAL_RESUME_DRILL"}
    await run_case(DRILLS / args.run_id, identity, spec, idx, example, Mem0MemoryStore)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--drill-qid", default=None)
    args = parser.parse_args()
    if not args.run_id.startswith("v55-") or not args.run_id.replace("-", "").replace("_", "").isalnum():
        raise SystemExit("run_id must be a simple v55-... identifier")
    if bool(args.drill_qid) != args.run_id.startswith("v55-drill-"):
        raise SystemExit("Drill run IDs and --drill-qid must be used together")
    try:
        if args.drill_qid:
            asyncio.run(run_drill(args))
            print(json.dumps({"run_id": args.run_id, "drill": "COMPLETE"}))
            return
        result = asyncio.run(run(args))
    except BaseException as exc:
        base = DRILLS if args.drill_qid else RUNS
        path = base / args.run_id / "errors" / "global" / f"{now().replace(':', '').replace('+', '_')}.json"
        atomic_json(path, {"run_id": args.run_id, "at": now(), "type": type(exc).__name__,
                           "message": str(exc), "state": "INCOMPLETE_NO_EXTENSION_DECISION"})
        raise
    out = RESULTS / f"{args.run_id}_RESULT.json"
    if out.exists():
        existing = json.loads(out.read_text(encoding="utf-8"))
        if existing != result:
            raise FileExistsError(out)
    else:
        atomic_json(out, result)
    print(json.dumps({"run_id": args.run_id, "decision": result["decision"], "result": str(out)}))


if __name__ == "__main__":
    main()
