#!/usr/bin/env python3
"""V58 guarded sequence runner, offline readback, aggregation and preflight."""
from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from audit_freeze import audit, src_and_project
from journal import Journal, immutable_json, sha, tree_sha, utc_now
from statistics import exact_randomization
from transport import ReceiptTransport
from execution import OUTPUT_LIMIT, verify_execution
from control import (STOP_REQUESTED, PAUSED_EXIT, SafePause, request_pause, requested,
                     clear_pause, checkpoint_pause, status as control_status)


SRC, PROJECT = src_and_project()
VERSION = SRC.parent
OUTPUTS = VERSION / "outputs"
OLD = PROJECT / "history/pre_v58_root_20260930"
DESIGN = OLD / "study_freeze/V58_POLICY_ORDER.json"
AMENDMENT = PROJECT / "study_freeze/V58_PRIMARY_METRIC_AMENDMENT_20260930.json"
AMENDMENT_MANIFEST = PROJECT / "study_freeze/V58_AMENDMENT_MANIFEST_20260930.json"
DATASET = VERSION / "inputs/longmemeval-v1/longmemeval_s_cleaned.json"


def frozen() -> dict[str, Any]:
    result = audit()
    if result["status"] != "PASS":
        raise RuntimeError("Freeze audit failed")
    return json.loads(DESIGN.read_text(encoding="utf-8"))


def simple_token(value: str) -> str:
    if not value or not value.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Identifier must contain only letters, digits, '-' or '_'")
    return value


def selected(block_id: int, slot: int) -> tuple[dict[str, Any], str]:
    if slot not in (1, 2) or block_id not in range(1, 13):
        raise ValueError("Invalid frozen block/slot")
    block = frozen()["blocks"][block_id - 1]
    return block, block[f"slot{slot}"]


def operation_plan(block: dict[str, Any], cases: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for trial_number, symbol in enumerate(block["order"], 1):
        for session_index in range(1, cases[symbol]["sessions"] + 1):
            result.append({"kind": "ingest", "trial": trial_number, "symbol": symbol,
                           "session": session_index})
        result.append({"kind": "observe", "trial": trial_number, "symbol": symbol})
        if trial_number < 4:
            result.append({"kind": "cleanup", "trial": trial_number, "symbol": symbol})
    if len(result) != 190:
        raise RuntimeError("V58 operation plan drift")
    return result


def runtime_preflight() -> dict[str, Any]:
    path = PROJECT / "history/v45/code/redis_v45_ollama_deterministic_gate.py"
    spec = importlib.util.spec_from_file_location("v58_runtime_v45", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Pinned engine missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    protocol = json.loads((PROJECT / "history/v55_formal/FORMAL_PROTOCOL_V55.json").read_text())
    receipt = module.ollama_runtime_receipt()
    if receipt["model_digest"] != protocol["stack"]["model_digest"] or receipt["ollama_version"] != protocol["stack"]["ollama_server_version"]:
        raise RuntimeError("Pinned Ollama runtime identity mismatch")
    return receipt


def identity(run_id: str, block: dict[str, Any], slot: int, policy: str, runtime: dict[str, Any],
             budget: dict[str, int | float]) -> dict[str, Any]:
    execution_sha = verify_execution()
    source_hashes = {p.name: sha(p) for p in SRC.glob("*.py")}
    return {"schema": "science-v58-sequence-identity-v1", "run_id": run_id,
            "execution_amendment_sha256": execution_sha, "version": "v58", "block": block["block"], "slot": slot, "order": block["order"],
            "policy": policy, "scope": f"v58_{run_id}",
            "original_freeze_sha256": sha(OLD / "study_freeze/FREEZE_MANIFEST.json"),
            "v58_design_sha256": sha(DESIGN), "amendment_sha256": sha(AMENDMENT),
            "amendment_manifest_sha256": sha(AMENDMENT_MANIFEST),
            "dataset_sha256": sha(DATASET), "code_sha256": source_hashes,
            "model_identity": runtime,
            "budget_limits": budget,
            "model_parameters": {"model": "qwen3:8b-q4_K_M", "think": False,
                                 "temperature": 0.0, "top_k": 1, "top_p": 1.0,
                                 "seed": 20260920, "num_ctx": 32768,
                                 "num_predict": OUTPUT_LIMIT, "repeat_penalty": 1.1}}


async def run_sequence(args: argparse.Namespace, *, resume: bool) -> None:
    design = frozen()
    block, policy = selected(args.block, args.slot)
    cases = {case["symbol"]: case for case in design["cases"]}
    plan = operation_plan(block, cases)
    runtime = runtime_preflight()
    run_id = args.run_id
    if not run_id.startswith("v58-"):
        raise ValueError("run_id must be a simple v58- identifier")
    simple_token(run_id)
    run_root = OUTPUTS / run_id
    batch_id = getattr(args, "batch_id", None)
    roots = [run_root]
    if batch_id:
        simple_token(batch_id)
        if not run_id.startswith(f"v58-{batch_id}-b"):
            raise ValueError("Sequence does not belong to requested batch")
        roots.append(OUTPUTS / f"v58-{batch_id}-controller")
    if any((root / "control/pause.request.json").exists() for root in roots):
        if not getattr(args, "resume_paused", False):
            raise SafePause("Pause request remains active; use --resume-paused to continue")
        for root in roots:
            clear_pause(root)
    budget = {"max_requests": args.max_requests, "max_input_tokens": args.max_input_tokens,
              "max_output_tokens": args.max_output_tokens, "max_cost": args.max_cost}
    info = identity(run_id, block, args.slot, policy, runtime, budget)
    journal = Journal(run_root, info, resume=resume)
    if resume:
        journal.readback()
    else:
        initial = journal.root / "raw/initial_state"
        initial.mkdir()
        journal.commit(0, initial, {"kind": "initial", "process_id": os.getpid()})
    transport = ReceiptTransport(journal, max_requests=args.max_requests,
                                 max_input_tokens=args.max_input_tokens,
                                 max_output_tokens=args.max_output_tokens,
                                 max_cost=args.max_cost, output_reserve_per_request=OUTPUT_LIMIT)
    from backend import FrozenBackend
    backend = FrozenBackend(journal, transport)
    backend.runtime_preflight()
    examples = {symbol: backend.case(case["question_id"], case["sessions"])
                for symbol, case in cases.items()}
    last = journal.latest()
    if last is None:
        raise RuntimeError("Initial checkpoint missing")
    next_step = last[0] + 1
    for step in range(next_step, len(plan) + 1):
        if requested(*roots):
            request_pause(run_root, "signal_or_batch_request")
            checkpoint_pause(run_root, step - 1, run_id=run_id, batch_id=batch_id)
        operation = plan[step - 1]
        control_status(run_root, phase="RUNNING", run_id=run_id, batch_id=batch_id,
                       current_step=step, last_committed_step=step - 1, operation=operation)
        journal.begin_step(step, operation["kind"])
        source = journal.checkpoint_path(step - 1) / "state"
        attempt = journal.create_attempt(step, source)
        trial_number = operation["trial"]
        symbol = operation["symbol"]
        example = examples[symbol]
        try:
            if operation["kind"] == "ingest":
                receipt = await backend.ingest(attempt, info["scope"],
                                               example.sessions[operation["session"] - 1], step)
            elif operation["kind"] == "observe":
                receipt = await backend.observe(attempt, info["scope"], example, step, trial_number)
            else:
                receipt = await backend.cleanup(attempt, info["scope"], policy)
                cleanup_path = journal.root / "raw/cleanup" / f"after-trial-{trial_number:02d}.json"
                immutable_json(cleanup_path, receipt)
                receipt = {"cleanup_sha256": sha(cleanup_path), **receipt}
            journal.commit(step, attempt, {"operation": operation, "result": receipt,
                                           "process_id": os.getpid(), "at_utc": utc_now()})
        except BaseException as exc:
            immutable_json(journal.root / "raw/failures" / f"step-{step:05d}.json",
                           {"step": step, "operation": operation, "type": type(exc).__name__,
                            "message": str(exc), "at_utc": utc_now(), "terminal": True,
                            "attempt_state_sha256": tree_sha(attempt)})
            control_status(run_root, phase="TERMINAL_INVALID", run_id=run_id,
                           current_step=step, error=type(exc).__name__)
            raise
        control_status(run_root, phase="RUNNING", run_id=run_id, batch_id=batch_id,
                       last_committed_step=step, operation=operation)
        if requested(*roots) and step < len(plan):
            request_pause(run_root, "signal_or_batch_request")
            checkpoint_pause(run_root, step, run_id=run_id, batch_id=batch_id)
    immutable_json(journal.root / "raw/sequence_complete.json",
                   {"run_id": run_id, "block": args.block, "slot": args.slot,
                    "policy": policy, "order": block["order"], "steps": len(plan),
                    "process_id": os.getpid(), "at_utc": utc_now()})
    print(json.dumps({"run_id": run_id, "status": "COMPLETE", "steps": len(plan)}))
    control_status(run_root, phase="COMPLETE", run_id=run_id, last_committed_step=len(plan))


def readback(run_id: str) -> dict[str, Any]:
    simple_token(run_id)
    path = OUTPUTS / run_id
    identity_path = path / "raw/identity.json"
    if not identity_path.is_file():
        raise FileNotFoundError(identity_path)
    info = json.loads(identity_path.read_text())
    journal = Journal(path, info, resume=True)
    checks = journal.readback()
    complete = path / "raw/sequence_complete.json"
    if complete.exists() and checks["checkpoints"] != 191:
        raise RuntimeError("Completion marker without full checkpoint chain")
    observations = sorted((path / "raw/observations").glob("trial-*.json")) if (path / "raw/observations").exists() else []
    if complete.exists() and len(observations) != 4:
        raise RuntimeError("Complete sequence lacks four raw observations")
    for observation in observations:
        item = json.loads(observation.read_text())
        if len(item["footprint"]) != 1925:
            raise RuntimeError("Malformed observation footprint")
        receipts = [json.loads((journal.checkpoint_path(step) / "_checkpoint.json").read_text())["receipt"]
                    for step in range(1, checks["checkpoints"])]
        matched = [receipt["result"] for receipt in receipts
                   if receipt["operation"]["kind"] == "observe" and
                   receipt["operation"]["trial"] == item["trial"]]
        if len(matched) != 1 or matched[0]["observation_sha256"] != sha(observation):
            raise RuntimeError("Raw observation receipt mismatch")
    for step in range(1, checks["checkpoints"]):
        receipt = json.loads((journal.checkpoint_path(step) / "_checkpoint.json").read_text())["receipt"]
        if receipt["operation"]["kind"] == "cleanup":
            trial = receipt["operation"]["trial"]
            cleanup_file = path / "raw/cleanup" / f"after-trial-{trial:02d}.json"
            if not cleanup_file.is_file() or sha(cleanup_file) != receipt["result"]["cleanup_sha256"]:
                raise RuntimeError("Raw cleanup receipt mismatch")
    return {"run_id": run_id, "status": checks["status"],
            "checkpoints": checks["checkpoints"], "complete": complete.exists(),
            "block": info["block"], "slot": info["slot"], "policy": info["policy"]}


def aggregate(batch_id: str) -> None:
    simple_token(batch_id)
    design = frozen()
    records: list[dict[str, Any]] = []
    run_ids = []
    for block in design["blocks"]:
        for slot in (1, 2):
            run_id = f"v58-{batch_id}-b{block['block']:02d}-s{slot}"
            result = readback(run_id)
            if not result["complete"] or result["policy"] != block[f"slot{slot}"]:
                raise RuntimeError("Missing or mismatched frozen sequence")
            run_ids.append(run_id)
            for position, target in enumerate(block["order"], 1):
                observation = json.loads((OUTPUTS / run_id / "raw/observations" / f"trial-{position:02d}.json").read_text())
                records.append({"block": block["block"], "slot": slot, "position": position,
                                "target": target,
                                "predecessor": block["order"][position - 2] if position > 1 else None,
                                "footprint": observation["footprint"]})
    result = exact_randomization(records, design["blocks"])
    result["run_ids"] = run_ids
    result["source_observation_sha256"] = {run_id: [sha(OUTPUTS / run_id / "raw/observations" / f"trial-{n:02d}.json")
                                                    for n in range(1, 5)] for run_id in run_ids}
    analysis_root = OUTPUTS / f"v58-{batch_id}-analysis"
    analysis_root.mkdir(parents=True, exist_ok=False)
    for name in ("raw", "checkpoints", "processed"):
        (analysis_root / name).mkdir()
    immutable_json(analysis_root / "raw/source_manifest.json",
                   {"batch_id": batch_id, "source_run_ids": run_ids,
                    "observation_sha256": result["source_observation_sha256"],
                    "design_sha256": sha(DESIGN), "amendment_sha256": sha(AMENDMENT),
                    "model_calls": 0})
    immutable_json(analysis_root / "processed/exact_randomization.json", result)
    print(json.dumps({"status": "PASS", "effect": result["effect"],
                      "p": result["exact_p_value"], "assignments": 4096}))


def full(args: argparse.Namespace) -> None:
    simple_token(args.batch_id)
    frozen()
    current_runtime = runtime_preflight()
    batch_root = OUTPUTS / f"v58-{args.batch_id}-controller"
    batch_identity = {"batch_id": args.batch_id, "design_sha256": sha(DESIGN),
                      "amendment_sha256": sha(AMENDMENT), "dataset_sha256": sha(DATASET),
                      "source_sha256": {p.name: sha(p) for p in SRC.glob("*.py")},
                      "runtime": current_runtime,
                      "execution_amendment_sha256": verify_execution(),
                      "global_budget": {"max_requests": args.max_requests,
                                        "max_input_tokens": args.max_input_tokens,
                                        "max_output_tokens": args.max_output_tokens,
                                        "max_cost": args.max_cost}}
    if batch_root.exists():
        saved = json.loads((batch_root / "raw/batch_identity.json").read_text())
        if saved != batch_identity:
            raise RuntimeError("Batch identity or budget drift; continuation rejected")
    else:
        batch_root.mkdir(parents=True)
        for name in ("raw", "checkpoints", "processed"):
            (batch_root / name).mkdir()
        immutable_json(batch_root / "raw/batch_identity.json", batch_identity)
    if (batch_root / "control/pause.request.json").exists():
        if not getattr(args, "resume_paused", False):
            raise SafePause("Batch is paused; use --resume-paused to continue")
        clear_pause(batch_root)
    consumed = {"requests": 0, "input": 0, "output": 0}
    for block in range(1, 13):
        for slot in (1, 2):
            if requested(batch_root):
                request_pause(batch_root, "signal_or_user")
                control_status(batch_root, phase="PAUSED", batch_id=args.batch_id)
                raise SafePause("Batch paused before the next sequence")
            run_id = f"v58-{args.batch_id}-b{block:02d}-s{slot}"
            existing = (OUTPUTS / run_id).exists()
            existing_info = None
            complete = False
            if existing:
                complete = readback(run_id)["complete"]
                existing_info = json.loads((OUTPUTS / run_id / "raw/identity.json").read_text())
            if not complete:
                remaining = {"requests": args.max_requests - consumed["requests"],
                             "input": args.max_input_tokens - consumed["input"],
                             "output": args.max_output_tokens - consumed["output"]}
                if remaining["requests"] < 1 or remaining["input"] < 32768 or remaining["output"] < OUTPUT_LIMIT:
                    raise RuntimeError("Global batch budget exhausted before next sequence")
                limits = existing_info["budget_limits"] if existing_info else {
                    "max_requests": remaining["requests"], "max_input_tokens": remaining["input"],
                    "max_output_tokens": remaining["output"], "max_cost": args.max_cost}
                cmd = [sys.executable, str(Path(__file__).resolve()), "resume" if existing else "single-sequence",
                       "--block", str(block), "--slot", str(slot), "--run-id", run_id,
                       "--batch-id", args.batch_id,
                       "--allow-model-calls", "--max-requests", str(limits["max_requests"]),
                       "--max-input-tokens", str(limits["max_input_tokens"]),
                       "--max-output-tokens", str(limits["max_output_tokens"]),
                       "--max-cost", str(limits["max_cost"])]
                if getattr(args, "resume_paused", False):
                    cmd.append("--resume-paused")
                control_status(batch_root, phase="RUNNING", batch_id=args.batch_id,
                               active_run_id=run_id, block=block, slot=slot)
                result_process = subprocess.run(cmd, check=False)
                if result_process.returncode == PAUSED_EXIT:
                    request_pause(batch_root, "worker_safe_pause")
                    control_status(batch_root, phase="PAUSED", batch_id=args.batch_id,
                                   active_run_id=run_id)
                    raise SafePause("Sequence saved a checkpoint and paused")
                if result_process.returncode != 0:
                    control_status(batch_root, phase="FAILED", batch_id=args.batch_id,
                                   active_run_id=run_id)
                    raise subprocess.CalledProcessError(result_process.returncode, cmd)
            result = readback(run_id)
            if not result["complete"] or result["block"] != block or result["slot"] != slot:
                raise RuntimeError("Incomplete sequence: resume it under its original identity before continuing batch")
            info = json.loads((OUTPUTS / run_id / "raw/identity.json").read_text())
            if (info["code_sha256"] != batch_identity["source_sha256"] or
                info["v58_design_sha256"] != batch_identity["design_sha256"] or
                info["amendment_sha256"] != batch_identity["amendment_sha256"] or
                info["dataset_sha256"] != batch_identity["dataset_sha256"] or
                info["model_identity"] != batch_identity["runtime"]):
                raise RuntimeError("Completed sequence identity differs from batch identity")
            for call in (OUTPUTS / run_id / "raw/model_calls").iterdir():
                if not call.is_dir() or not (call / "dispatched.json").exists():
                    continue
                consumed["requests"] += 1
                response = call / "response.json"
                item = json.loads(response.read_text()) if response.exists() else {}
                consumed["input"] += max(int(item.get("prompt_eval_count") or 0), 32768)
                consumed["output"] += max(int(item.get("eval_count") or 0), OUTPUT_LIMIT)
            if (consumed["requests"] > args.max_requests or consumed["input"] > args.max_input_tokens or
                consumed["output"] > args.max_output_tokens):
                raise RuntimeError("Global batch budget exceeded; no further sequence will start")
    completion = batch_root / "raw/batch_complete.json"
    if not completion.exists():
        immutable_json(completion, {"batch_id": args.batch_id, "sequence_count": 24,
                                    "conservative_budget_consumed": consumed,
                                    "at_utc": utc_now()})
    control_status(batch_root, phase="COMPLETE", batch_id=args.batch_id)


def dry_run_child(output: Path) -> None:
    state = output / "state"
    state.mkdir(parents=True)
    (state / "sample.txt").write_text("fake initial state", encoding="utf-8")
    info = {"run_id": f"v58-dry-{os.getpid()}", "fake": True}
    journal = Journal(output / "run", info, resume=False)
    journal.commit(0, state, {"kind": "initial", "pid": os.getpid()})
    journal.begin_step(1, "fake_trial")
    attempt = journal.create_attempt(1, journal.checkpoint_path(0) / "state")
    (attempt / "sample.txt").write_text("fake completed trial", encoding="utf-8")
    journal.commit(1, attempt, {"kind": "fake_trial_complete", "pid": os.getpid()})
    print(json.dumps({"pid": os.getpid(), "readback": journal.readback()}))


def dry_run() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        results = []
        for slot in (1, 2):
            output = subprocess.check_output([sys.executable, str(Path(__file__).resolve()),
                                              "_dry-child", "--output", str(Path(temporary) / f"slot{slot}")], text=True)
            results.append(json.loads(output))
        if results[0]["pid"] == results[1]["pid"]:
            raise RuntimeError("Dry-run process isolation failed")
        print(json.dumps({"status": "PASS", "fresh_processes": 2,
                          "different_pids": True, "model_calls": 0}))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight")
    sub.add_parser("dry-run")
    for name in ("single-sequence", "resume", "full"):
        command = sub.add_parser(name)
        command.add_argument("--allow-model-calls", action="store_true")
        command.add_argument("--resume-paused", action="store_true")
        command.add_argument("--max-requests", type=int, required=True)
        command.add_argument("--max-input-tokens", type=int, required=True)
        command.add_argument("--max-output-tokens", type=int, required=True)
        command.add_argument("--max-cost", type=float, required=True)
        if name == "full":
            command.add_argument("--batch-id", required=True)
        else:
            command.add_argument("--batch-id")
            command.add_argument("--block", type=int, required=True)
            command.add_argument("--slot", type=int, required=True)
            command.add_argument("--run-id", required=True)
    child = sub.add_parser("_dry-child")
    child.add_argument("--output", type=Path, required=True)
    rb = sub.add_parser("readback")
    rb.add_argument("--run-id", required=True)
    agg = sub.add_parser("aggregate")
    agg.add_argument("--batch-id", required=True)
    pause = sub.add_parser("pause")
    target = pause.add_mutually_exclusive_group(required=True)
    target.add_argument("--batch-id")
    target.add_argument("--run-id")
    args = parser.parse_args()
    if args.command == "preflight":
        result = audit()
        print(json.dumps({"freeze_audit": result["status"], "runtime": runtime_preflight()}, ensure_ascii=False))
    elif args.command == "dry-run":
        dry_run()
    elif args.command == "_dry-child":
        dry_run_child(args.output)
    elif args.command in ("single-sequence", "resume", "full"):
        if not args.allow_model_calls:
            raise SystemExit("Real model calls require --allow-model-calls; current preparation task forbids using it")
        STOP_REQUESTED.clear()
        def handle_stop(signum, _frame):
            STOP_REQUESTED.set()
            if args.command == "full":
                try:
                    root = OUTPUTS / f"v58-{simple_token(args.batch_id)}-controller"
                    if root.exists():
                        request_pause(root, signal.Signals(signum).name)
                except (OSError, ValueError):
                    pass
        for signum in (signal.SIGINT, signal.SIGTERM):
            signal.signal(signum, handle_stop)
        try:
            if args.command == "full":
                full(args)
            else:
                asyncio.run(run_sequence(args, resume=args.command == "resume"))
        except SafePause as exc:
            print(json.dumps({"status": "PAUSED_AT_CHECKPOINT", "detail": str(exc)}))
            raise SystemExit(PAUSED_EXIT)
    elif args.command == "pause":
        key = simple_token(args.batch_id or args.run_id)
        root = OUTPUTS / (f"v58-{key}-controller" if args.batch_id else key)
        print(json.dumps({"status": "PAUSE_REQUESTED", **request_pause(root)}, ensure_ascii=False))
    elif args.command == "readback":
        print(json.dumps(readback(args.run_id), ensure_ascii=False))
    elif args.command == "aggregate":
        aggregate(args.batch_id)


if __name__ == "__main__":
    main()
