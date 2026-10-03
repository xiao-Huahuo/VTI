import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch
from teardown_supervisor import verify_safe_pause
from teardown_supervisor import teardown_abort

class TeardownRecognitionTests(unittest.TestCase):
    def test_complete_teardown_only(self):
        signature='libc++abi: recursive_mutex lock failed: Invalid argument SIGABRT'
        self.assertFalse(teardown_abort(signature))
        self.assertTrue(teardown_abort('{"status": "COMPLETE"}\n'+signature))
        self.assertFalse(teardown_abort('{"status": "COMPLETE"}\nLLMError truncated JSON'))

    def test_resume_rejects_nonpaused_controller(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);control=root/'v58-test-controller/control';control.mkdir(parents=True)
            (control/'status.json').write_text(json.dumps({'phase':'FAILED'}))
            with self.assertRaisesRegex(RuntimeError, 'safe paused'):
                verify_safe_pause(root,'test')

    def test_resume_propagates_ambiguous_readback_without_dispatch(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);control=root/'v58-test-controller/control';control.mkdir(parents=True)
            (control/'status.json').write_text(json.dumps({'phase':'PAUSED','active_run_id':'v58-test-b01-s1'}))
            with patch('teardown_supervisor.readback',side_effect=RuntimeError('ambiguous call')):
                with self.assertRaisesRegex(RuntimeError,'ambiguous call'):
                    verify_safe_pause(root,'test')

if __name__=='__main__':unittest.main()
