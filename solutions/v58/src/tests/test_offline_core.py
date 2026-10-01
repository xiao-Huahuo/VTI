from __future__ import annotations

import json
import asyncio
import argparse
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from journal import Journal, immutable_json
from statistics import exact_randomization, load_records
from transport import AmbiguousExternalCall, BudgetStop, ReceiptTransport
from backend import FrozenBackend
from retrieval_footprint import footprint, normalize_text, OUTPUT_DIMS
import runner


class FakeClient:
    def __init__(self, outcome):
        self.outcome = outcome
        self.calls = 0

    def chat(self, **request):
        self.calls += 1
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        return self.outcome


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.state = self.root / "state"
        self.state.mkdir()
        (self.state / "memory.db").write_bytes(b"initial")
        self.identity = {"run_id": "v58-fake-1", "freeze_hash": "abc", "dataset_hash": "def",
                         "model": "fixed", "budget_limits": {"requests": 2}}

    def tearDown(self):
        self.tmp.cleanup()

    def journal(self, resume=False):
        return Journal(self.root / "outputs/v58-fake-1", self.identity, resume=resume)

    def test_completed_step_resumes_without_reexecution(self):
        journal = self.journal()
        journal.commit(0, self.state, {"phase": "initialized"})
        journal.begin_step(1, "trial")
        (self.state / "memory.db").write_bytes(b"completed")
        journal.commit(1, self.state, {"phase": "trial_complete"})
        resumed = self.journal(resume=True)
        self.assertEqual(resumed.latest()[0], 1)
        self.assertEqual(resumed.readback()["status"], "PASS")
        with self.assertRaises(FileExistsError):
            resumed.commit(1, self.state, {})

    def test_cleanup_started_without_commit_is_not_replayed(self):
        journal = self.journal()
        journal.commit(0, self.state, {"phase": "initialized"})
        journal.begin_step(1, "cleanup")
        with self.assertRaisesRegex(RuntimeError, "Uncommitted operation"):
            self.journal(resume=True).readback()

    def test_raw_response_without_completion_marker_stops(self):
        journal = self.journal()
        journal.commit(0, self.state, {"phase": "initialized"})
        journal.begin_step(1, "trial")
        client = FakeClient({"message": {"content": "ok"}, "prompt_eval_count": 2, "eval_count": 1})
        transport = ReceiptTransport(journal, max_requests=2, max_input_tokens=65536,
                                     max_output_tokens=4096, max_cost=0)
        transport.call_once(client, {"model": "fixed", "messages": []}, step=1)
        self.assertEqual(client.calls, 1)
        with self.assertRaises(RuntimeError):
            self.journal(resume=True).readback()

    def test_failure_after_dispatch_is_never_retried(self):
        for failure in (TimeoutError("after send"), RuntimeError("429"), RuntimeError("402"),
                        RuntimeError("provider error")):
            with self.subTest(failure=str(failure)):
                run = self.root / f"run-{type(failure).__name__}-{abs(hash(str(failure)))}"
                journal = Journal(run, self.identity, resume=False)
                journal.commit(0, self.state, {"phase": "initialized"})
                journal.begin_step(1, "trial")
                client = FakeClient(failure)
                transport = ReceiptTransport(journal, max_requests=2, max_input_tokens=65536,
                                             max_output_tokens=4096, max_cost=0)
                with self.assertRaises(AmbiguousExternalCall):
                    transport.call_once(client, {"model": "fixed", "messages": []}, step=1)
                self.assertEqual(client.calls, 1)
                with self.assertRaises(RuntimeError):
                    journal.readback()

    def test_identity_drift_and_corruption_rejected(self):
        journal = self.journal()
        journal.commit(0, self.state, {"phase": "initialized"})
        with self.assertRaises(RuntimeError):
            Journal(journal.root, {**self.identity, "model": "drift"}, resume=True)
        with self.assertRaises(RuntimeError):
            Journal(journal.root, {**self.identity, "budget_limits": {"requests": 3}}, resume=True)
        (journal.checkpoint_path(0) / "state/memory.db").write_bytes(b"corrupt")
        with self.assertRaisesRegex(RuntimeError, "corruption"):
            journal.latest()

    def test_request_guard_stops_before_dispatch(self):
        journal = self.journal()
        journal.commit(0, self.state, {"phase": "initialized"})
        client = FakeClient({"message": {"content": "ok"}})
        transport = ReceiptTransport(journal, max_requests=1, max_input_tokens=32768,
                                     max_output_tokens=2048, max_cost=0)
        transport.call_once(client, {"model": "fixed", "messages": []}, step=1)
        with self.assertRaises(BudgetStop):
            transport.call_once(client, {"model": "fixed", "messages": []}, step=2)
        self.assertEqual(client.calls, 1)

    def test_input_and_output_token_guards_stop_before_dispatch(self):
        for input_cap, output_cap in ((32767, 2048), (32768, 2047)):
            with self.subTest(input_cap=input_cap, output_cap=output_cap):
                run = self.root / f"token-{input_cap}-{output_cap}"
                journal = Journal(run, self.identity, resume=False)
                journal.commit(0, self.state, {"phase": "initialized"})
                client = FakeClient({"message": {"content": "ok"}})
                transport = ReceiptTransport(journal, max_requests=1, max_input_tokens=input_cap,
                                             max_output_tokens=output_cap, max_cost=0)
                with self.assertRaises(BudgetStop):
                    transport.call_once(client, {"model": "fixed", "messages": []}, step=1)
                self.assertEqual(client.calls, 0)

    def test_second_dispatch_for_same_step_is_rejected(self):
        journal = self.journal()
        journal.commit(0, self.state, {"phase": "initialized"})
        client = FakeClient({"message": {"content": "ok"}, "prompt_eval_count": 3, "eval_count": 2})
        transport = ReceiptTransport(journal, max_requests=3, max_input_tokens=3 * 32768,
                                     max_output_tokens=3 * 2048, max_cost=0)
        transport.call_once(client, {"model": "fixed", "messages": []}, step=1)
        with self.assertRaises(AmbiguousExternalCall):
            transport.call_once(client, {"model": "fixed", "messages": []}, step=1)
        self.assertEqual(client.calls, 1)

    def test_raw_response_tamper_rejected(self):
        journal = self.journal()
        journal.commit(0, self.state, {"phase": "initialized"})
        journal.begin_step(1, "trial")
        client = FakeClient({"message": {"content": "ok"}})
        transport = ReceiptTransport(journal, max_requests=2, max_input_tokens=65536,
                                     max_output_tokens=4096, max_cost=0)
        transport.call_once(client, {"model": "fixed", "messages": []}, step=1)
        journal.commit(1, self.state, {"phase": "done"})
        response = next((journal.root / "raw/model_calls").glob("*/response.json"))
        response.write_text('{"message":{"content":"tampered"}}')
        with self.assertRaisesRegex(RuntimeError, "Raw response hash mismatch"):
            journal.readback()

    def test_http_bytes_saved_before_sdk_json_parse(self):
        journal = self.journal()
        journal.commit(0, self.state, {"phase": "initialized"})
        journal.begin_step(1, "trial")

        class RawResponse:
            status_code = 200
            content = b'{"model":"fixed","message":{"content":"ok"},"prompt_eval_count":2,"eval_count":1}'

            def json(self):
                captures = list((journal.root / "raw/model_calls").glob("*/raw_http_response.bin"))
                if len(captures) != 1 or captures[0].read_bytes() != self.content:
                    raise AssertionError("SDK parsed before raw HTTP bytes were persisted")
                return json.loads(self.content)

        class FakeSdk:
            def _request_raw(self):
                return RawResponse()

            def chat(self, **request):
                return self._request_raw().json()

        transport = ReceiptTransport(journal, max_requests=2, max_input_tokens=65536,
                                     max_output_tokens=4096, max_cost=0)
        transport.call_once(FakeSdk(), {"model": "fixed", "messages": []}, step=1)
        journal.commit(1, self.state, {"phase": "done"})
        self.assertEqual(journal.readback()["status"], "PASS")

    def test_returned_model_drift_is_terminal(self):
        journal = self.journal()
        journal.commit(0, self.state, {"phase": "initialized"})
        journal.begin_step(1, "trial")

        class RawResponse:
            status_code = 200
            content = b'{"model":"wrong","message":{"content":"ok"}}'

            def json(self):
                return json.loads(self.content)

        class FakeSdk:
            calls = 0

            def _request_raw(self):
                return RawResponse()

            def chat(self, **request):
                self.calls += 1
                return self._request_raw().json()

        client = FakeSdk()
        transport = ReceiptTransport(journal, max_requests=2, max_input_tokens=65536,
                                     max_output_tokens=4096, max_cost=0)
        with self.assertRaises(AmbiguousExternalCall):
            transport.call_once(client, {"model": "fixed", "messages": []}, step=1)
        self.assertEqual(client.calls, 1)

    def test_malformed_response_is_terminal(self):
        journal = self.journal()
        journal.commit(0, self.state, {"phase": "initialized"})
        journal.begin_step(1, "trial")
        client = FakeClient("not a response object")
        transport = ReceiptTransport(journal, max_requests=2, max_input_tokens=65536,
                                     max_output_tokens=4096, max_cost=0)
        with self.assertRaises(AmbiguousExternalCall):
            transport.call_once(client, {"model": "fixed", "messages": []}, step=1)
        self.assertEqual(client.calls, 1)


class StatisticsTests(unittest.TestCase):
    def test_exact_4096_with_zero_verified_dispersion(self):
        orders = ["CBAD", "BCDA", "ABDC", "ACBD", "CADB", "BACD", "ADCB", "DABC",
                  "DCAB", "CDBA", "BDAC", "DBCA"]
        blocks = [{"block": i + 1, "order": order, "slot1": "N", "slot2": "V"}
                  for i, order in enumerate(orders)]
        records = []
        for block in blocks:
            for slot in (1, 2):
                policy = block[f"slot{slot}"]
                for position, target in enumerate(block["order"], 1):
                    predecessor = block["order"][position - 2] if position > 1 else None
                    footprint = np.zeros(1925, dtype=np.float32)
                    if policy == "N" and predecessor is not None:
                        footprint[0] = float("ABCD".index(predecessor))
                    records.append({"block": block["block"], "slot": slot, "position": position,
                                    "target": target, "predecessor": predecessor,
                                    "footprint": footprint.tolist()})
        with tempfile.TemporaryDirectory() as directory:
            raw = Path(directory) / "raw_observations.jsonl"
            raw.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
            rebuilt = load_records([raw])
        result = exact_randomization(rebuilt, blocks)
        self.assertEqual(result["number_of_assignments"], 4096)
        self.assertEqual(result["verified_dispersion"], 0)
        self.assertGreater(result["native_dispersion"], 0)
        self.assertEqual(result["exact_p_value"], result["right_tail_count"] / 4096)
        self.assertEqual(len(result["per_cell_statistics"]), 24)
        records[1]["target"] = "A" if records[1]["target"] != "A" else "B"
        with self.assertRaises(ValueError):
            exact_randomization(records, blocks)


class CleanupRoutingTests(unittest.TestCase):
    def test_native_does_not_delete_sidecar_and_verified_does(self):
        async def one(policy):
            state = {"messages": 5, "vectors": 7, "reset_calls": 0, "delete_calls": 0}

            class FakeStore:
                _memory = object()

                async def reset(self):
                    state["reset_calls"] += 1
                    state["vectors"] = 0

            fake = SimpleNamespace(
                message_summary=lambda path, scope: {"count": state["messages"]},
                vector_summary=lambda memory, scope: {"count": state["vectors"]},
                qdrant_backend_summary=lambda memory, scope: {"count": state["vectors"]},
                close_memory=lambda memory: None,
            )

            def delete(path, scope):
                state["delete_calls"] += 1
                old = state["messages"]
                state["messages"] = 0
                return old

            fake.delete_scope_messages = delete
            backend = object.__new__(FrozenBackend)
            backend.v45 = fake
            backend._store = lambda path, scope: FakeStore()
            result = await backend.cleanup(Path("/unused"), "same_scope", policy)
            return state, result

        native, n_receipt = asyncio.run(one("N"))
        verified, v_receipt = asyncio.run(one("V"))
        self.assertEqual((native["reset_calls"], native["delete_calls"], native["messages"]), (1, 0, 5))
        self.assertEqual((verified["reset_calls"], verified["delete_calls"], verified["messages"]), (1, 1, 0))
        self.assertEqual(n_receipt["verified_deleted_messages"], 0)
        self.assertEqual(v_receipt["verified_deleted_messages"], 5)


class FootprintTests(unittest.TestCase):
    @staticmethod
    def fake_embed(texts):
        rows = []
        for text in texts:
            vector = np.zeros(384, dtype=np.float32)
            vector[sum(text.encode()) % 384] = 1.0
            rows.append(vector)
        return rows

    def test_normalization_padding_order_and_duplicates(self):
        self.assertEqual(normalize_text("  cafe\u0301\r\n  tea "), "café tea")
        empty = footprint([], self.fake_embed)
        self.assertEqual((empty.shape, empty.dtype), ((OUTPUT_DIMS,), np.dtype("float32")))
        self.assertFalse(empty.any())
        first = footprint(["tea", "coffee"], self.fake_embed)
        swapped = footprint(["coffee", "tea"], self.fake_embed)
        self.assertFalse(np.array_equal(first, swapped))
        self.assertNotEqual(first[-5], 0)
        self.assertEqual(first[-1], 0)
        self.assertTrue(np.array_equal(footprint(["tea", "tea"], self.fake_embed)[:384],
                                       footprint(["tea"], self.fake_embed)[:384]))


class AggregationTests(unittest.TestCase):
    def test_full_processed_result_rebuilds_from_raw_observations(self):
        project = next(parent for parent in Path(__file__).resolve().parents if (parent / "CURRENT_STATE.json").exists())
        design = json.loads((project / "history/pre_v58_root_20260930/study_freeze/V58_POLICY_ORDER.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            outputs = Path(directory)
            for block in design["blocks"]:
                for slot in (1, 2):
                    run_id = f"v58-synthetic-b{block['block']:02d}-s{slot}"
                    folder = outputs / run_id / "raw/observations"
                    folder.mkdir(parents=True)
                    for trial, target in enumerate(block["order"], 1):
                        vector = np.zeros(1925, dtype=np.float32)
                        if block[f"slot{slot}"] == "N" and trial > 1:
                            vector[0] = float("ABCD".index(block["order"][trial - 2]))
                        (folder / f"trial-{trial:02d}.json").write_text(json.dumps({"footprint": vector.tolist()}))

            def fake_readback(run_id):
                parts = run_id.rsplit("-", 2)
                block_id = int(parts[-2][1:])
                slot = int(parts[-1][1:])
                return {"complete": True, "policy": design["blocks"][block_id - 1][f"slot{slot}"]}

            with patch.object(runner, "OUTPUTS", outputs), patch.object(runner, "frozen", return_value=design), \
                    patch.object(runner, "readback", side_effect=fake_readback):
                runner.aggregate("synthetic")
            result_path = outputs / "v58-synthetic-analysis/processed/exact_randomization.json"
            result = json.loads(result_path.read_text())
            source_manifest = json.loads((outputs / "v58-synthetic-analysis/raw/source_manifest.json").read_text())
            self.assertEqual(result["number_of_assignments"], 4096)
            self.assertEqual(len(result["run_ids"]), 24)
            self.assertEqual(len(result["source_observation_sha256"]), 24)
            self.assertEqual(len(source_manifest["source_run_ids"]), 24)
            self.assertGreater(result["effect"], 0)

    def test_global_batch_budget_and_completed_sequence_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            outputs = Path(directory)
            started = []
            runtime = {"model_digest": "fake-fixed"}
            args = argparse.Namespace(batch_id="fakebatch", max_requests=24,
                                      max_input_tokens=24 * 32768,
                                      max_output_tokens=24 * runner.OUTPUT_LIMIT, max_cost=0.0)
            info = {"code_sha256": {p.name: runner.sha(p) for p in runner.SRC.glob("*.py")},
                    "v58_design_sha256": runner.sha(runner.DESIGN),
                    "amendment_sha256": runner.sha(runner.AMENDMENT),
                    "dataset_sha256": runner.sha(runner.DATASET),
                    "model_identity": runtime}

            def fake_start(command, check):
                run_id = command[command.index("--run-id") + 1]
                started.append(run_id)
                root = outputs / run_id / "raw"
                call = root / "model_calls/one"
                call.mkdir(parents=True)
                (root / "identity.json").write_text(json.dumps(info))
                (call / "dispatched.json").write_text("{}")
                (call / "response.json").write_text('{"prompt_eval_count":1,"eval_count":1}')
                return SimpleNamespace(returncode=0)

            def fake_readback(run_id):
                tail = run_id.rsplit("-", 2)
                return {"complete": True, "block": int(tail[-2][1:]), "slot": int(tail[-1][1:])}

            with patch.object(runner, "OUTPUTS", outputs), patch.object(runner, "frozen", return_value={}), \
                    patch.object(runner, "runtime_preflight", return_value=runtime), \
                    patch.object(runner.subprocess, "run", side_effect=fake_start), \
                    patch.object(runner, "readback", side_effect=fake_readback):
                runner.full(args)
                self.assertEqual(len(started), 24)
                runner.full(args)
                self.assertEqual(len(started), 24)
                with self.assertRaisesRegex(RuntimeError, "identity or budget drift"):
                    runner.full(argparse.Namespace(**{**vars(args), "max_requests": 25}))


if __name__ == "__main__":
    unittest.main()
