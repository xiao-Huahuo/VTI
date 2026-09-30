#!/usr/bin/env python3
"""Development-only V58 execution profiling; never produces formal observations."""
from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))

import journal as journal_module
from backend import FrozenBackend
from journal import Journal, immutable_json, sha, utc_now
from transport import ReceiptTransport

VERSION = SRC.parent
OUTPUTS = VERSION / "outputs"
DEV_CASES = (("b5ef892d", 52, 26), ("1a8a66a6", 51, 25))
PROJECT = next(parent for parent in SRC.parents if (parent / "CURRENT_STATE.json").is_file())


def profile_runtime_preflight() -> dict[str, Any]:
    path = PROJECT / "history/v45/code/redis_v45_ollama_deterministic_gate.py"
    spec = importlib.util.spec_from_file_location("v58_profiling_v45", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Pinned V45 runtime source missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    protocol = json.loads((PROJECT / "history/v55_formal/FORMAL_PROTOCOL_V55.json").read_text())
    observed = module.ollama_runtime_receipt()
    if (observed["model_digest"] != protocol["stack"]["model_digest"] or
        observed["ollama_version"] != protocol["stack"]["ollama_server_version"]):
        raise RuntimeError("Development runtime differs from V55 pinned identity")
    return observed


def simple_id(value: str) -> str:
    if not value or not value.replace("-", "").replace("_", "").isalnum():
        raise ValueError("profiling id must be alphanumeric with hyphen/underscore only")
    return value


class Timings:
    def __init__(self) -> None:
        self.values: dict[str, float] = defaultdict(float)
        self.phase = "other"
        self.copy_depth = 0

    def add(self, name: str, seconds: float) -> None:
        self.values[name] += seconds

    def snapshot(self) -> dict[str, float]:
        return dict(self.values)

    def difference(self, before: dict[str, float]) -> dict[str, float]:
        return {key: self.values[key] - before.get(key, 0.0)
                for key in self.values if self.values[key] - before.get(key, 0.0) > 0}


class InstrumentedJournal(Journal):
    def __init__(self, root: Path, identity: dict[str, Any], timings: Timings) -> None:
        self.timings = timings
        super().__init__(root, identity, resume=False)

    def create_attempt(self, step: int, source: Path) -> Path:
        self.timings.phase = "attempt"
        try:
            return super().create_attempt(step, source)
        finally:
            self.timings.phase = "other"

    def commit(self, step: int, source: Path, receipt: dict[str, Any]) -> Path:
        self.timings.phase = "checkpoint"
        started = time.perf_counter()
        try:
            return super().commit(step, source, receipt)
        finally:
            self.timings.add("checkpoint_total_s", time.perf_counter() - started)
            self.timings.phase = "other"


class JournalProbe:
    """Timing-only wrappers around the unchanged formal Journal operations."""

    def __init__(self, timings: Timings):
        self.timings = timings
        self.original_copy = shutil.copytree
        self.original_hash = journal_module.tree_sha

    def __enter__(self):
        def copy(*args: Any, **kwargs: Any):
            if self.timings.copy_depth:
                return self.original_copy(*args, **kwargs)
            self.timings.copy_depth += 1
            started = time.perf_counter()
            try:
                return self.original_copy(*args, **kwargs)
            finally:
                self.timings.add(f"{self.timings.phase}_copy_s", time.perf_counter() - started)
                self.timings.copy_depth -= 1

        def hash_tree(path: Path):
            started = time.perf_counter()
            try:
                return self.original_hash(path)
            finally:
                self.timings.add(f"{self.timings.phase}_hash_s", time.perf_counter() - started)

        shutil.copytree = copy
        journal_module.tree_sha = hash_tree
        return self

    def __exit__(self, *_exc):
        shutil.copytree = self.original_copy
        journal_module.tree_sha = self.original_hash


class TimedTransport(ReceiptTransport):
    def __init__(self, *args: Any, timings: Timings, **kwargs: Any):
        self.timings = timings
        super().__init__(*args, **kwargs)

    def call_once(self, client: Any, request: dict[str, Any], *, step: int) -> Any:
        started = time.perf_counter()
        started_utc = utc_now()
        try:
            return super().call_once(client, request, step=step)
        finally:
            wall = time.perf_counter() - started
            self.timings.add("llm_request_s", wall)
            immutable_json(self.journal.root / "raw/profile_request_timing" / f"step-{step:05d}.json",
                           {"step": step, "started_utc": started_utc, "ended_utc": utc_now(),
                            "request_wall_seconds": wall, "formal_data": False})


class TimedBackend(FrozenBackend):
    def __init__(self, journal: Journal, transport: ReceiptTransport, timings: Timings):
        self.timings = timings
        super().__init__(journal, transport)

    def _store(self, state: Path, scope: str) -> Any:
        store = super()._store(state, scope)
        memory = store._memory
        for owner, names, category in (
            (memory.vector_store, ("search", "insert", "update", "delete", "list", "get"), "qdrant_s"),
            (memory.db, ("save_messages", "get_last_messages", "batch_add_history",
                         "add_history", "get_history", "reset"), "sqlite_s"),
            (memory.embedding_model, ("embed",), "backend_embedding_s"),
        ):
            for name in names:
                original = getattr(owner, name, None)
                if not callable(original):
                    continue

                def timed(*args: Any, _original=original, _category=category, **kwargs: Any):
                    started = time.perf_counter()
                    try:
                        return _original(*args, **kwargs)
                    finally:
                        self.timings.add(_category, time.perf_counter() - started)

                setattr(owner, name, timed)
        return store


class ResourceMonitor:
    """Best-effort host telemetry; missing fields remain explicit in receipts."""

    def __init__(self, folder: Path, interval_seconds: float = 5.0):
        self.folder = folder
        self.interval_seconds = interval_seconds
        self.done = threading.Event()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.count = 0
        self.failures = 0

    @staticmethod
    def _output(command: list[str]) -> str | None:
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=3, check=False)
            return result.stdout if result.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            return None

    def _sample(self) -> dict[str, Any]:
        result: dict[str, Any] = {"at_utc": utc_now()}
        nvidia = self._output(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                               "--format=csv,noheader,nounits"])
        if nvidia:
            try:
                gpu, used, total = [float(x.strip()) for x in nvidia.splitlines()[0].split(",")]
                result["nvidia_gpu_util_percent"] = gpu
                result["nvidia_vram_used_mib"] = used
                result["nvidia_vram_total_mib"] = total
            except (ValueError, IndexError):
                result["nvidia_parse_error"] = True
        mac_gpu = self._output(["ioreg", "-r", "-c", "AGXAccelerator", "-l"])
        if mac_gpu:
            utilization = re.search(r'"Device Utilization %"=(\d+)', mac_gpu)
            allocated = re.search(r'"In use system memory"=(\d+)', mac_gpu)
            result["mac_gpu_util_percent"] = int(utilization.group(1)) if utilization else None
            result["mac_gpu_memory_proxy_bytes"] = int(allocated.group(1)) if allocated else None
        vm = self._output(["vm_stat"])
        if vm:
            page = re.search(r"page size of (\d+) bytes", vm)
            free = re.search(r"Pages free:\s+(\d+)", vm)
            speculative = re.search(r"Pages speculative:\s+(\d+)", vm)
            if page and free:
                result["mac_free_plus_speculative_bytes"] = int(page.group(1)) * (
                    int(free.group(1)) + (int(speculative.group(1)) if speculative else 0))
        pressure = self._output(["memory_pressure", "-Q"])
        if pressure:
            free_percent = re.search(r"System-wide memory free percentage:\s*(\d+)%", pressure)
            result["mac_memory_free_percent"] = int(free_percent.group(1)) if free_percent else None
        ollama = self._output(["ollama", "ps"])
        result["ollama_ps"] = ollama.strip() if ollama else None
        return result

    def _loop(self) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        while not self.done.is_set():
            try:
                self.count += 1
                immutable_json(self.folder / f"sample-{self.count:05d}.json", self._sample())
            except Exception:
                self.failures += 1
            self.done.wait(self.interval_seconds)

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.done.set()
        self.thread.join(timeout=10)


def profile_identity(run_id: str, runtime: dict[str, Any], lane: int, condition: int,
                     workload: tuple[tuple[str, int, int], ...]) -> dict[str, Any]:
    return {"schema": "science-v58-development-profiling-identity-v1",
            "run_id": run_id, "status": "DEVELOPMENT_PROFILING", "formal_data": False,
            "label": "NOT_FORMAL_DATA", "lane": lane, "condition_lanes": condition,
            "dev_cases": [{"question_id": qid, "expected_sessions": total, "selected_sessions": selected}
                          for qid, total, selected in workload],
            "server_config_claim": {key: os.environ.get(key, "UNSET") for key in
                                    ("OLLAMA_NUM_PARALLEL", "OLLAMA_CONTEXT_LENGTH",
                                     "OLLAMA_KEEP_ALIVE", "OLLAMA_KV_CACHE_TYPE",
                                     "OLLAMA_FLASH_ATTENTION")},
            "model_identity": runtime,
            "dataset_sha256": sha(VERSION / "inputs/longmemeval-v1/longmemeval_s_cleaned.json"),
            "profile_code_sha256": sha(Path(__file__).resolve()),
            "formal_code_sha256": {p.name: sha(p) for p in SRC.glob("*.py")},
            "budget": {"max_requests": 60, "max_input_tokens": 60 * 32768,
                       "max_output_tokens": 60 * 2048, "max_cost": 0}}


async def worker(run_id: str, lane: int, condition: int, *, smoke: bool = False) -> dict[str, Any]:
    os.environ["MEM0_TELEMETRY"] = "false"
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
    runtime = profile_runtime_preflight()
    timings = Timings()
    workload = tuple((qid, total, 1 if smoke else selected) for qid, total, selected in DEV_CASES)
    identity = profile_identity(run_id, runtime, lane, condition, workload)
    journal = InstrumentedJournal(OUTPUTS / run_id, identity, timings)
    initial = journal.root / "raw/initial_state"
    initial.mkdir()
    sessions_done = 0
    scope = f"v58dev_{run_id}"
    started = time.perf_counter()
    with JournalProbe(timings):
        journal.commit(0, initial, {"kind": "development_initial", "process_id": os.getpid()})
        transport = TimedTransport(journal, timings=timings, max_requests=60,
                                   max_input_tokens=60 * 32768,
                                   max_output_tokens=60 * 2048, max_cost=0)
        backend = TimedBackend(journal, transport, timings)
        backend.runtime_preflight()
        step = 0
        for case_number, (question_id, expected_sessions, selected_sessions) in enumerate(workload, 1):
            example = backend.examples[question_id]
            if len(example.sessions) != expected_sessions:
                raise RuntimeError("Development input binding drift")
            if case_number == 2:
                step += 1
                journal.begin_step(step, "development_cleanup")
                source = journal.checkpoint_path(step - 1) / "state"
                attempt = journal.create_attempt(step, source)
                before = timings.snapshot()
                cleanup_start = time.perf_counter()
                cleanup = await backend.cleanup(attempt, scope, "N")
                cleanup_wall = time.perf_counter() - cleanup_start
                journal.commit(step, attempt, {"kind": "development_cleanup", "receipt": cleanup})
                immutable_json(journal.root / "raw/profile_events" / f"step-{step:05d}.json",
                               {"step": step, "kind": "cleanup", "wall_seconds": cleanup_wall,
                                "timings": timings.difference(before), "formal_data": False})
            for index, session in enumerate(example.sessions[:selected_sessions], 1):
                step += 1
                started_step = time.perf_counter()
                before = timings.snapshot()
                journal.begin_step(step, "development_ingest")
                attempt = journal.create_attempt(step, journal.checkpoint_path(step - 1) / "state")
                ingestion_start = time.perf_counter()
                receipt = await backend.ingest(attempt, scope, session, step)
                ingest_wall = time.perf_counter() - ingestion_start
                journal.commit(step, attempt, {"kind": "development_ingest", "question_id": question_id,
                                               "session_index": index, "receipt": receipt})
                sessions_done += 1
                timing_delta = timings.difference(before)
                immutable_json(journal.root / "raw/profile_events" / f"step-{step:05d}.json",
                               {"step": step, "kind": "ingest", "question_id": question_id,
                                "session_index": index,
                                "session_wall_seconds": time.perf_counter() - started_step,
                                "ingest_wall_seconds": ingest_wall,
                                "backend_non_llm_seconds": max(0.0, ingest_wall - timing_delta.get("llm_request_s", 0.0)),
                                "timings": timing_delta, "formal_data": False})
    elapsed = time.perf_counter() - started
    readback = journal.readback()
    expected_sessions = sum(item[2] for item in workload)
    if sessions_done != expected_sessions or readback["status"] != "PASS" or readback["checkpoints"] != expected_sessions + 2:
        raise RuntimeError("Development profiling checkpoint/readback mismatch")
    summary = {"schema": "science-v58-development-profiling-worker-v1",
               "status": "DEVELOPMENT_PROFILING_COMPLETE", "formal_data": False,
               "run_id": run_id, "condition_lanes": condition, "lane": lane,
               "committed_sessions": sessions_done, "elapsed_seconds": elapsed,
               "sessions_per_hour": sessions_done * 3600 / elapsed,
               "timings_total": timings.snapshot(),
               "readback": readback,
               "requests_dispatched": transport.totals()["requests"],
               "formal_model_calls": 0, "development_model_calls": transport.totals()["requests"]}
    immutable_json(journal.root / "raw/development_summary.json", summary)
    return summary


def run_condition(profile_id: str, lanes: int) -> dict[str, Any]:
    if lanes not in (1, 2):
        raise ValueError("Only 1 or 2 lanes are prospectively allowed")
    simple_id(profile_id)
    controller = OUTPUTS / f"v58-profile-{profile_id}-controller"
    identity = {"status": "DEVELOPMENT_PROFILING", "formal_data": False,
                "label": "NOT_FORMAL_DATA", "profile_id": profile_id,
                "runtime": profile_runtime_preflight(),
                "profile_code_sha256": sha(Path(__file__).resolve()),
                "server_config_claim": {key: os.environ.get(key, "UNSET") for key in
                                        ("OLLAMA_NUM_PARALLEL", "OLLAMA_CONTEXT_LENGTH",
                                         "OLLAMA_KEEP_ALIVE", "OLLAMA_KV_CACHE_TYPE",
                                         "OLLAMA_FLASH_ATTENTION")},
                "dev_cases": [{"question_id": qid, "expected_sessions": total,
                               "selected_sessions": selected} for qid, total, selected in DEV_CASES]}
    if controller.exists():
        if json.loads((controller / "raw/identity.json").read_text()) != identity:
            raise RuntimeError("Profiling controller identity/config drift")
    else:
        controller.mkdir(parents=True)
        for folder in ("raw", "checkpoints", "processed"):
            (controller / folder).mkdir()
        immutable_json(controller / "raw/identity.json", identity)
    condition_path = controller / "raw" / f"condition-{lanes}.json"
    if condition_path.exists():
        raise FileExistsError("Profiling condition already exists; no rerun")
    run_ids = [f"v58-profile-{profile_id}-{lanes}lane-w{lane}" for lane in range(1, 3)]
    monitor = ResourceMonitor(controller / "raw/resource_samples" / f"{lanes}lane")
    monitor.start()
    started = time.perf_counter()
    processes = []
    summaries = []
    try:
        for lane, run_id in enumerate(run_ids, 1):
            command = [sys.executable, str(Path(__file__).resolve()), "worker",
                       "--run-id", run_id, "--lane", str(lane), "--condition", str(lanes),
                       "--allow-development-model-calls"]
            if lanes == 1:
                subprocess.run(command, check=True)
            else:
                processes.append(subprocess.Popen(command))
        for process in processes:
            process.wait()
        if any(process.returncode != 0 for process in processes):
            raise RuntimeError("Development worker failed; no automatic retry")
    finally:
        for process in processes:
            if process.poll() is None:
                process.wait()
        monitor.stop()
    wall = time.perf_counter() - started
    for run_id in run_ids:
        summary = json.loads((OUTPUTS / run_id / "raw/development_summary.json").read_text())
        if summary["status"] != "DEVELOPMENT_PROFILING_COMPLETE" or summary["formal_data"]:
            raise RuntimeError("Development receipt mismatch")
        summaries.append(summary)
    total = sum(item["committed_sessions"] for item in summaries)
    latencies = []
    for run_id in run_ids:
        folder = OUTPUTS / run_id / "raw/profile_events"
        latencies.extend(json.loads(path.read_text())["session_wall_seconds"]
                         for path in folder.glob("step-*.json")
                         if json.loads(path.read_text())["kind"] == "ingest")
    sorted_latencies = sorted(latencies)
    result = {"schema": "science-v58-development-throughput-condition-v1",
            "status": "DEVELOPMENT_PROFILING_COMPLETE", "condition_lanes": lanes,
            "run_ids": run_ids, "committed_sessions": total,
            "elapsed_seconds": wall, "sessions_per_hour": total * 3600 / wall,
            "median_session_latency_seconds": median(latencies),
            "p90_session_latency_seconds": sorted_latencies[max(0, (9 * len(sorted_latencies) + 9) // 10 - 1)],
            "resource_sample_count": monitor.count,
            "resource_sample_failures": monitor.failures,
            "development_model_calls": sum(item["development_model_calls"] for item in summaries),
            "formal_model_calls": 0}
    immutable_json(condition_path, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    worker_parser = sub.add_parser("worker")
    worker_parser.add_argument("--run-id", required=True)
    worker_parser.add_argument("--lane", type=int, choices=(1, 2), required=True)
    worker_parser.add_argument("--condition", type=int, choices=(1, 2), required=True)
    worker_parser.add_argument("--allow-development-model-calls", action="store_true")
    worker_parser.add_argument("--smoke", action="store_true")
    condition_parser = sub.add_parser("condition")
    condition_parser.add_argument("--profile-id", required=True)
    condition_parser.add_argument("--lanes", type=int, choices=(1, 2), required=True)
    condition_parser.add_argument("--allow-development-model-calls", action="store_true")
    args = parser.parse_args()
    if not args.allow_development_model_calls:
        raise SystemExit("Explicit --allow-development-model-calls is required")
    if args.command == "worker":
        print(json.dumps(asyncio.run(worker(args.run_id, args.lane, args.condition, smoke=args.smoke)), ensure_ascii=False))
    else:
        print(json.dumps(run_condition(args.profile_id, args.lanes), ensure_ascii=False))


if __name__ == "__main__":
    main()
