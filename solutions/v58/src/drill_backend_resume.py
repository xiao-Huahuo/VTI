#!/usr/bin/env python3
"""Cross-process Mem0 state recovery with intercepted fake Ollama only."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

from backend import FrozenBackend
from journal import Journal, sha
from transport import ReceiptTransport


class FakeOllama:
    calls = 0

    def chat(self, **request):
        self.calls += 1
        content = (json.dumps({"memory": [{"id": "fake", "text": "User likes tea",
                                          "attributed_to": "user"}]}) if "format" in request
                   else "Synthetic answer")
        return {"message": {"content": content}, "prompt_eval_count": 10, "eval_count": 5,
                "model": "FAKE_NO_REAL_MODEL"}


def backend_for(journal: Journal) -> FrozenBackend:
    transport = ReceiptTransport(journal, max_requests=4, max_input_tokens=4 * 32768,
                                 max_output_tokens=4 * 2048, max_cost=0)
    backend = FrozenBackend(journal, transport)
    fake = FakeOllama()
    original = backend._store

    def fake_store(state: Path, scope: str):
        store = original(state, scope)
        store._memory.llm.client = fake
        return store

    backend._store = fake_store
    backend.fake = fake
    return backend


async def phase(root: Path, policy: str, number: int) -> dict:
    info = {"run_id": f"v58-resume-{policy}", "policy": policy,
            "freeze": "fixed", "dataset": "fixed", "model": "fake-fixed", "code": "fixed"}
    journal = Journal(root, info, resume=number == 2)
    if number == 1:
        initial = journal.root / "raw/initial_state"
        initial.mkdir()
        journal.commit(0, initial, {"kind": "initial"})
    else:
        journal.readback()
    backend = backend_for(journal)
    from agent_memory_benchmark.datasets.models import ContextMessage, Session
    session = Session(label="2025/01/01 10:00", messages=[ContextMessage(speaker="user", text="I like tea")])
    example = SimpleNamespace(qa_pairs=[SimpleNamespace(question="What does the user like?",
                                                        question_id=f"fake-{number}", answer="tea")],
                              metadata={"question_date": None})
    scope = f"same_scope_{policy}"
    step = 1 if number == 1 else 4
    journal.begin_step(step, "ingest")
    attempt = journal.create_attempt(step, journal.checkpoint_path(step - 1) / "state")
    ingest = await backend.ingest(attempt, scope, session, step)
    journal.commit(step, attempt, {"kind": "ingest", "receipt": ingest})
    step += 1
    journal.begin_step(step, "observe")
    attempt = journal.create_attempt(step, journal.checkpoint_path(step - 1) / "state")
    observed = await backend.observe(attempt, scope, example, step, number)
    journal.commit(step, attempt, {"kind": "observe", "receipt": observed})
    if number == 1:
        step += 1
        journal.begin_step(step, "cleanup")
        attempt = journal.create_attempt(step, journal.checkpoint_path(step - 1) / "state")
        cleanup = await backend.cleanup(attempt, scope, policy)
        journal.commit(step, attempt, {"kind": "cleanup", "receipt": cleanup})
        os._exit(77)
    return {"policy": policy, "phase": number, "scoped_message_count_after_second_ingest": ingest["scoped_message_count"],
            "fake_calls": backend.fake.calls, "checkpoints": journal.readback()["checkpoints"],
            "first_boundary_checkpoint_sha256": sha(journal.checkpoint_path(3) / "_checkpoint.json")}


def run() -> dict:
    checks = {}
    with tempfile.TemporaryDirectory() as temporary:
        for policy in ("N", "V"):
            root = Path(temporary) / f"run-{policy}"
            first = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--phase", "1",
                                    "--root", str(root), "--policy", policy], check=False)
            before = sha(root / "checkpoints/00003/_checkpoint.json")
            second = subprocess.check_output([sys.executable, str(Path(__file__).resolve()), "--phase", "2",
                                              "--root", str(root), "--policy", policy], text=True)
            result = json.loads(second)
            checks[f"{policy}_first_process_killed_after_boundary"] = first.returncode == 77
            checks[f"{policy}_checkpoint_unchanged"] = before == result["first_boundary_checkpoint_sha256"]
            checks[f"{policy}_second_process_resumed"] = result["checkpoints"] == 6 and result["fake_calls"] == 2
            checks[f"{policy}_sidecar_semantics"] = result["scoped_message_count_after_second_ingest"] == (4 if policy == "N" else 2)
    return {"schema": "science-v58-real-backend-cross-process-resume-drill-v1",
            "status": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks, "passed": sum(checks.values()), "total": len(checks),
            "real_model_calls": 0}


if __name__ == "__main__":
    os.environ["MEM0_TELEMETRY"] = "false"
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=int, choices=(1, 2))
    parser.add_argument("--root", type=Path)
    parser.add_argument("--policy", choices=("N", "V"))
    args = parser.parse_args()
    if args.phase:
        print(json.dumps(asyncio.run(phase(args.root, args.policy, args.phase))))
    else:
        print(json.dumps(run(), ensure_ascii=False, indent=2))
