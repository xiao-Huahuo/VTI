from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import progress_server as dashboard


class DashboardTests(unittest.TestCase):
    def test_only_formal_batches_are_counted_and_pause_api_is_local_control(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            outputs = project / "outputs"
            controller = outputs / "v58-test-controller"
            (controller / "raw").mkdir(parents=True)
            (controller / "raw/batch_identity.json").write_text(json.dumps({"batch_id": "test", "global_budget": {}}))
            dev = outputs / "v58-profile-test-controller/raw"
            dev.mkdir(parents=True)
            (dev / "batch_identity.json").write_text(json.dumps({"status": "DEVELOPMENT_PROFILING"}))
            (project / "CURRENT_STATE.json").write_text('{"v58_execution_gates":{"formal_model_calls":0}}')
            with patch.object(dashboard, "PROJECT", project), patch.object(dashboard, "OUTPUTS", outputs):
                snapshot = dashboard.progress()
                self.assertEqual(snapshot["batch_id"], "test")
                self.assertEqual(snapshot["completed_sessions"], 0)
                self.assertEqual(len(snapshot["sequences"]), 24)
                server = ThreadingHTTPServer(("127.0.0.1", 0), dashboard.Handler)
                server.batch_id = "test"
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    url = f"http://127.0.0.1:{server.server_port}/api/pause"
                    body = json.dumps({"batch_id": "test"}).encode()
                    bad = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
                    with self.assertRaises(urllib.error.HTTPError) as failure:
                        urllib.request.urlopen(bad)
                    self.assertEqual(failure.exception.code, 403)
                    good = urllib.request.Request(url, data=body,
                                                  headers={"Content-Type": "application/json", "X-Control-Token": dashboard.TOKEN})
                    with urllib.request.urlopen(good) as response:
                        self.assertEqual(json.load(response)["status"], "PAUSE_REQUESTED")
                    self.assertTrue((controller / "control/pause.request.json").exists())
                    self.assertEqual(list((controller / "raw").iterdir()), [controller / "raw/batch_identity.json"])
                finally:
                    server.shutdown()
                    server.server_close()
