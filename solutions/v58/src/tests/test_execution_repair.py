import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend import FrozenBackend
from execution import OUTPUT_LIMIT, verify_execution

class ExecutionRepairTests(unittest.TestCase):
    def test_request_cap_and_truncation_rejected_before_schema(self):
        backend = FrozenBackend.__new__(FrozenBackend)
        backend.current_step = 1
        backend.memory_schema = {'type':'object'}
        backend.validate_memory_json = Mock()
        backend.v45 = SimpleNamespace(EXPECTED_MODEL='frozen-model', KEEP_ALIVE='30m',
            deterministic_options=lambda:{'seed':20260920,'num_predict':2048},
            response_content=lambda response:'{}')
        backend.transport = SimpleNamespace(call_once=Mock(return_value=SimpleNamespace(done_reason='length')))
        backend._install_v55_ollama_path()
        with self.assertRaisesRegex(RuntimeError, 'truncated'):
            backend.v45.deterministic_chat(None, [], json_mode=True)
        request = backend.transport.call_once.call_args.args[1]
        self.assertEqual(request['options']['num_predict'], OUTPUT_LIMIT)
        self.assertEqual(request['options']['seed'], 20260920)
        backend.validate_memory_json.assert_not_called()
        self.assertEqual(backend.transport.call_once.call_count, 1)

    def test_execution_amendment_and_full_budget_are_consistent(self):
        import json
        from execution import EXECUTION_AMENDMENT
        self.assertTrue(verify_execution())
        data = json.loads(EXECUTION_AMENDMENT.read_text())
        self.assertEqual(data['max_output_tokens'], data['max_requests'] * OUTPUT_LIMIT)
        self.assertEqual(data['output_reserve_per_request'], OUTPUT_LIMIT)
