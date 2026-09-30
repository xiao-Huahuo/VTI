"""V58 adapter for the hash-pinned V45/V55 Mem0 and Ollama execution path."""
from __future__ import annotations

import asyncio
import importlib.metadata
import importlib.util
import json
import os
import random
import sys
from pathlib import Path
from typing import Any

from audit_freeze import audit, src_and_project
from journal import Journal, immutable_json, sha
from retrieval_footprint import footprint
from transport import ReceiptTransport


class FrozenBackend:
    def __init__(self, journal: Journal, transport: ReceiptTransport):
        if audit()["status"] != "PASS":
            raise RuntimeError("V58 freeze audit failed")
        self.src, self.project = src_and_project()
        self.journal = journal
        self.transport = transport
        self.current_step = -1
        self.historical = self.project / "history"
        self.bench = self.historical / "pre_v58_root_20260930/third_party/agent-memory-server/agent-memory-benchmark"
        self.dataset = self.src.parent / "inputs/longmemeval-v1/longmemeval_s_cleaned.json"
        self.asset_cache = self.historical / "pre_v58_root_20260930/.runtime/fastembed-cache"
        self.v45 = self._load_module("v58_frozen_v45", self.historical / "v45/code/redis_v45_ollama_deterministic_gate.py")
        schema = self._load_module("v58_frozen_v55_schema", self.historical / "v55_formal/code/schema.py")
        self.memory_schema = schema.MEMORY_SCHEMA
        self.validate_memory_json = schema.validate_memory_json
        self._install_v55_ollama_path()
        sys.path.insert(0, str(self.bench / "src"))
        from agent_memory_benchmark.datasets import LongMemEvalAdapter
        from agent_memory_benchmark.memory.mem0_store import Mem0MemoryStore
        self.Mem0MemoryStore = Mem0MemoryStore
        examples = LongMemEvalAdapter("small", cache_dir=self.dataset.parents[1]).load()
        random.Random(42).shuffle(examples)
        self.examples = {str(example.qa_pairs[0].question_id): example for example in examples}
        self.embedding = None

    @staticmethod
    def _load_module(name: str, path: Path) -> Any:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load frozen dependency {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _install_v55_ollama_path(self) -> None:
        v45 = self.v45
        previous_options = v45.deterministic_options
        v45.deterministic_options = lambda: {**previous_options(), "repeat_penalty": 1.1}

        def logged_chat(client: Any, messages: list[dict[str, str]], *, json_mode: bool) -> Any:
            if self.current_step < 0:
                raise RuntimeError("Model call lacks journal step")
            request: dict[str, Any] = {
                "model": v45.EXPECTED_MODEL,
                "messages": [dict(item) for item in messages],
                "stream": False,
                "options": v45.deterministic_options(),
                "keep_alive": v45.KEEP_ALIVE,
                "think": False,
            }
            if json_mode:
                request["format"] = self.memory_schema
            response = self.transport.call_once(client, request, step=self.current_step)
            content = v45.response_content(response)
            if not content.strip():
                raise RuntimeError("Empty Ollama response; no retry")
            if json_mode:
                self.validate_memory_json(content)
            return response

        v45.deterministic_chat = logged_chat

    def runtime_preflight(self) -> dict[str, Any]:
        v45 = self.v45
        protocol = json.loads((self.historical / "v55_formal/FORMAL_PROTOCOL_V55.json").read_text())
        stack = protocol["stack"]
        if os.environ.get("MEM0_TELEMETRY", "").lower() != "false":
            raise RuntimeError("MEM0_TELEMETRY=false is required")
        runtime = v45.ollama_runtime_receipt()
        if runtime["model_digest"] != stack["model_digest"] or runtime["ollama_version"] != stack["ollama_server_version"]:
            raise RuntimeError("Ollama model/server identity drift")
        versions = {"mem0ai": v45.MEM0_VERSION, "ollama": v45.OLLAMA_PYTHON_VERSION,
                    "fastembed": stack["fastembed_version"], "qdrant-client": stack["qdrant_client_version"]}
        if any(importlib.metadata.version(name) != expected for name, expected in versions.items()):
            raise RuntimeError("Pinned Python dependency drift")
        if v45.git_head(self.bench.parent) != v45.REDIS_COMMIT:
            raise RuntimeError("Frozen Redis source commit drift")
        return {"runtime": runtime, "packages": versions, "benchmark_commit": v45.REDIS_COMMIT}

    def case(self, question_id: str, sessions: int) -> Any:
        example = self.examples[question_id]
        if len(example.sessions) != sessions:
            raise RuntimeError("Frozen case session count drift")
        return example

    def _store(self, state: Path, scope: str) -> Any:
        memory_store = self.Mem0MemoryStore(config=self.v45.make_config(state), user_id=scope,
                                            model=self.v45.EXPECTED_MODEL)
        self.v45.install_deterministic_ollama(memory_store._memory)
        return memory_store

    async def ingest(self, state: Path, scope: str, session: Any, step: int) -> dict[str, Any]:
        self.current_step = step
        memory_store = self._store(state, scope)
        records, original = self.v45.install_prompt_recorder(memory_store._memory)
        try:
            await memory_store.ingest([session])
            self.v45.restore_prompt_recorder(memory_store._memory, original)
            return {"prompt_records": records,
                    "scoped_message_count": self.v45.message_summary(state / "history.db", scope)["count"]}
        finally:
            self.v45.close_memory(memory_store._memory)
            self.current_step = -1

    def _embed(self, texts: list[str]) -> list[Any]:
        if self.embedding is None:
            from fastembed import TextEmbedding
            snapshot = (self.asset_cache / "models--Qdrant--bge-small-en-v1.5-onnx-Q/snapshots"
                        / "aa8f8b060edb00e03bfdd08813a2949946c8ba55")
            if not snapshot.is_dir():
                raise RuntimeError("Pinned BGE snapshot missing")
            self.embedding = TextEmbedding(model_name="BAAI/bge-small-en-v1.5",
                                           cache_dir=str(self.asset_cache),
                                           specific_model_path=str(snapshot),
                                           local_files_only=True)
            loaded = getattr(self.embedding.model, "_model_dir", None)
            if loaded is None or Path(loaded).resolve() != snapshot.resolve():
                raise RuntimeError("FastEmbed loaded a different measurement snapshot")
        return list(self.embedding.embed(texts))

    async def observe(self, state: Path, scope: str, example: Any, step: int,
                      trial_number: int) -> dict[str, Any]:
        self.current_step = step
        memory_store = self._store(state, scope)
        try:
            qa = example.qa_pairs[0]
            search_raw = memory_store._memory.search(qa.question, filters={"user_id": scope}, top_k=10)
            rows = self.v45.normalize_results(search_raw)
            texts = [str(row.get("memory") or row.get("text") or row.get("data") or "") for row in rows]
            vector = footprint(texts, self._embed)
            answer, usage = await self.v45.answer_with_ollama(
                memory_store, search_raw=search_raw, question=qa.question,
                question_date=example.metadata.get("question_date"))
            raw = {"trial": trial_number, "step": step, "question_id": str(qa.question_id),
                   "query": qa.question, "reference_answer": str(qa.answer),
                   "search_raw": search_raw, "normalized_rows": rows, "retrieval_texts": texts,
                   "retrieval_ordered_hashes": self.v45.text_hashes_in_order(rows),
                   "footprint": vector.tolist(), "footprint_dtype": "float32",
                   "answer": answer, "answer_usage": usage}
            immutable_json(self.journal.root / "raw/observations" / f"trial-{trial_number:02d}.json", raw)
            return {"trial": trial_number, "retrieval_count": len(rows),
                    "observation_sha256": sha(self.journal.root / "raw/observations" / f"trial-{trial_number:02d}.json"),
                    "answer_sha256": self.v45.sha_text(answer), "usage": usage}
        finally:
            self.v45.close_memory(memory_store._memory)
            self.current_step = -1

    async def cleanup(self, state: Path, scope: str, policy: str) -> dict[str, Any]:
        if policy not in ("N", "V"):
            raise ValueError("Invalid frozen policy")
        store = self._store(state, scope)
        try:
            before_messages = self.v45.message_summary(state / "history.db", scope)
            before_vectors = self.v45.vector_summary(store._memory, scope)
            before_backend = self.v45.qdrant_backend_summary(store._memory, scope)
            await store.reset()
            native_messages = self.v45.message_summary(state / "history.db", scope)
            native_vectors = self.v45.vector_summary(store._memory, scope)
            native_backend = self.v45.qdrant_backend_summary(store._memory, scope)
        finally:
            self.v45.close_memory(store._memory)
        deleted = self.v45.delete_scope_messages(state / "history.db", scope) if policy == "V" else 0
        reopened = self._store(state, scope)
        try:
            after_messages = self.v45.message_summary(state / "history.db", scope)
            after_vectors = self.v45.vector_summary(reopened._memory, scope)
            after_backend = self.v45.qdrant_backend_summary(reopened._memory, scope)
        finally:
            self.v45.close_memory(reopened._memory)
        if native_vectors["count"] != 0 or native_backend["count"] != 0:
            raise RuntimeError("Native Reset failed its vector gate")
        if policy == "V" and (after_messages["count"] != 0 or after_vectors["count"] != 0 or after_backend["count"] != 0):
            raise RuntimeError("Verified Cleanup failed its zero-state gate")
        return {"policy": policy, "before_messages": before_messages, "before_vectors": before_vectors,
                "before_backend": before_backend, "after_native_messages": native_messages,
                "after_native_vectors": native_vectors, "after_native_backend": native_backend,
                "verified_deleted_messages": deleted, "after_cleanup_messages": after_messages,
                "after_cleanup_vectors": after_vectors, "after_cleanup_backend": after_backend}
