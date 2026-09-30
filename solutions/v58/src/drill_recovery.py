#!/usr/bin/env python3
"""Real subprocess-death recovery drill using synthetic state and fake client."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from journal import Journal, immutable_json, sha
from transport import ReceiptTransport


IDENTITY = {"run_id": "v58-recovery-drill", "freeze_hash": "frozen",
            "dataset_hash": "dataset", "model_identity": "qwen-pinned", "code_version": "code-pinned"}


class FakeClient:
    calls = 0

    def chat(self, **request):
        self.calls += 1
        return {"message": {"content": "synthetic"}, "prompt_eval_count": 3, "eval_count": 2}


def child(kind: str, root: Path) -> None:
    state = root / "initial"
    state.mkdir(parents=True)
    (state / "state.txt").write_text("initial")
    journal = Journal(root / "run", IDENTITY, resume=False)
    journal.commit(0, state, {"kind": "initial"})
    if kind == "A":
        journal.begin_step(1, "trial")
        attempt = journal.create_attempt(1, journal.checkpoint_path(0) / "state")
        (attempt / "state.txt").write_text("partial")
    elif kind in ("B", "C", "E"):
        journal.begin_step(1, "trial")
        attempt = journal.create_attempt(1, journal.checkpoint_path(0) / "state")
        (attempt / "state.txt").write_text("completed trial")
        journal.commit(1, attempt, {"kind": "trial_complete"})
        if kind == "C":
            journal.begin_step(2, "cleanup")
            attempt = journal.create_attempt(2, journal.checkpoint_path(1) / "state")
            (attempt / "state.txt").write_text("cleanup may have happened")
        elif kind == "E":
            journal.begin_step(2, "cleanup")
            attempt = journal.create_attempt(2, journal.checkpoint_path(1) / "state")
            (attempt / "state.txt").write_text("cleanup completed")
            journal.commit(2, attempt, {"kind": "cleanup_complete"})
    elif kind == "D":
        journal.begin_step(1, "trial")
        transport = ReceiptTransport(journal, max_requests=2, max_input_tokens=65536,
                                     max_output_tokens=4096, max_cost=0)
        transport.call_once(FakeClient(), {"model": "fake", "messages": []}, step=1)
    elif kind == "G":
        journal.begin_step(1, "trial")
        folder = journal.root / "raw/model_calls/00001-fake-dispatch"
        body = json.dumps({"model": "fake", "messages": []}, sort_keys=True, separators=(",", ":")).encode()
        immutable_json(folder / "prepared.json", {"step": 1, "request": {"model": "fake", "messages": []},
                                                  "request_sha256": hashlib.sha256(body).hexdigest()})
        immutable_json(folder / "dispatched.json", {"step": 1})
    os._exit(77)


def run() -> dict:
    checks = {}
    for kind in "ABCDEG":
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            completed = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                        "--child", kind, "--root", str(root)], check=False)
            journal = Journal(root / "run", IDENTITY, resume=True)
            if kind in "ACDG":
                try:
                    journal.readback()
                except RuntimeError:
                    rejected = True
                else:
                    rejected = False
                checks[f"{kind}_partial_rejected"] = completed.returncode == 77 and rejected
                if kind == "D":
                    calls = list((journal.root / "raw/model_calls").glob("*/response.json"))
                    checks["D_raw_response_preserved_no_completion"] = len(calls) == 1 and journal.latest()[0] == 0
                if kind == "G":
                    checks["G_dispatch_without_response_rejected"] = not list(
                        (journal.root / "raw/model_calls").glob("*/response.json"))
            else:
                before = sha(journal.checkpoint_path(1) / "_checkpoint.json")
                readback = journal.readback()
                expected = 1 if kind == "B" else 2
                checks[f"{kind}_committed_state_resumes"] = (
                    completed.returncode == 77 and readback["status"] == "PASS"
                    and journal.latest()[0] == expected and sha(journal.checkpoint_path(1) / "_checkpoint.json") == before
                )
                if kind == "E":
                    journal.begin_step(3, "next_trial")
                    attempt = journal.create_attempt(3, journal.checkpoint_path(2) / "state")
                    (attempt / "state.txt").write_text("another completed trial")
                    journal.commit(3, attempt, {"kind": "trial_complete"})
                    checks["E_second_resume"] = Journal(root / "run", IDENTITY, resume=True).readback()["checkpoints"] == 4
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "run"
        Journal(root, IDENTITY, resume=False)
        for field in ("freeze_hash", "dataset_hash", "model_identity", "code_version"):
            changed = {**IDENTITY, field: "drift"}
            try:
                Journal(root, changed, resume=True)
            except RuntimeError:
                checks[f"F_{field}_drift_rejected"] = True
            else:
                checks[f"F_{field}_drift_rejected"] = False
    return {"schema": "science-v58-fake-process-death-drill-v1",
            "status": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks, "passed": sum(checks.values()), "total": len(checks),
            "real_model_calls": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", choices=list("ABCDEG"))
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    if args.child:
        child(args.child, args.root)
    else:
        print(json.dumps(run(), ensure_ascii=False, indent=2))
