#!/usr/bin/env python3
"""Real Mem0/Qdrant cleanup path with intercepted fake Ollama responses only."""
from __future__ import annotations

import asyncio
import json
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace

from backend import FrozenBackend
from journal import Journal
from transport import ReceiptTransport


class FakeOllama:
    calls = 0

    def chat(self, **request):
        self.calls += 1
        if "format" in request:
            content = json.dumps({"memory": [{"id": "fake-memory-1", "text": "User likes tea",
                                               "attributed_to": "user"}]})
        else:
            content = "Synthetic answer"
        return {"message": {"content": content}, "prompt_eval_count": 12, "eval_count": 8,
                "model": "FAKE_CLIENT_NO_REAL_MODEL"}


async def one(policy: str, root: Path) -> dict:
    info = {"run_id": f"v58-fake-backend-{policy}", "policy": policy, "fake_client": True}
    journal = Journal(root / policy, info, resume=False)
    initial = journal.root / "raw/initial_state"
    initial.mkdir()
    journal.commit(0, initial, {"kind": "initial"})
    transport = ReceiptTransport(journal, max_requests=8, max_input_tokens=8 * 32768,
                                 max_output_tokens=8 * 2048, max_cost=0)
    backend = FrozenBackend(journal, transport)
    fake = FakeOllama()
    original_store = backend._store

    def store_with_fake(state: Path, scope: str):
        store = original_store(state, scope)
        store._memory.llm.client = fake
        return store

    backend._store = store_with_fake
    from agent_memory_benchmark.datasets.models import ContextMessage, Session
    session = Session(label="2025/01/01 10:00", messages=[ContextMessage(speaker="user", text="I like tea")])
    scope = f"fake_{policy}"
    example = SimpleNamespace(qa_pairs=[SimpleNamespace(question="What does the user like?",
                                                     question_id="fake-question", answer="tea")],
                              metadata={"question_date": None})
    step = 0
    boundary_counts = []
    retrieval_counts = []
    for trial in range(1, 5):
        step += 1
        journal.begin_step(step, "ingest")
        attempt = journal.create_attempt(step, journal.checkpoint_path(step - 1) / "state")
        ingestion = await backend.ingest(attempt, scope, session, step)
        journal.commit(step, attempt, {"kind": "ingest", "trial": trial, "receipt": ingestion})
        step += 1
        journal.begin_step(step, "observe")
        attempt = journal.create_attempt(step, journal.checkpoint_path(step - 1) / "state")
        observed = await backend.observe(attempt, scope, example, step, trial)
        journal.commit(step, attempt, {"kind": "observe", "trial": trial, "receipt": observed})
        retrieval_counts.append(observed["retrieval_count"])
        if trial < 4:
            step += 1
            journal.begin_step(step, "cleanup")
            attempt = journal.create_attempt(step, journal.checkpoint_path(step - 1) / "state")
            cleanup = await backend.cleanup(attempt, scope, policy)
            journal.commit(step, attempt, {"kind": "cleanup", "trial": trial, "receipt": cleanup})
            boundary_counts.append({"before": cleanup["before_messages"]["count"],
                                    "after_native": cleanup["after_native_messages"]["count"],
                                    "after_cleanup": cleanup["after_cleanup_messages"]["count"]})
    return {"policy": policy, "fake_client_calls": fake.calls,
            "retrieval_counts": retrieval_counts,
            "boundary_counts": boundary_counts,
            "vectors_after_cleanup": cleanup["after_cleanup_vectors"]["count"],
            "readback": journal.readback()["status"], "checkpoints": journal.readback()["checkpoints"]}


def main() -> None:
    os.environ["MEM0_TELEMETRY"] = "false"
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
    with tempfile.TemporaryDirectory() as temporary:
        results = [asyncio.run(one(policy, Path(temporary))) for policy in ("N", "V")]
    valid = all(row["readback"] == "PASS" and row["vectors_after_cleanup"] == 0
                and row["checkpoints"] == 12 and row["fake_client_calls"] == 8 for row in results)
    valid &= all(x["after_native"] == x["after_cleanup"] for x in results[0]["boundary_counts"])
    valid &= all(x["after_cleanup"] == 0 for x in results[1]["boundary_counts"])
    valid &= results[0]["boundary_counts"][2]["before"] > results[0]["boundary_counts"][0]["before"]
    print(json.dumps({"schema": "science-v58-real-backend-fake-client-drill-v1",
                      "status": "PASS" if valid else "FAIL", "results": results,
                      "real_model_calls": 0}, ensure_ascii=False, indent=2))
    if not valid:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
