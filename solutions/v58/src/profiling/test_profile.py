from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from profile import InstrumentedJournal, JournalProbe, Timings, simple_id


class ProfilingInfrastructureTests(unittest.TestCase):
    def test_timing_wrapper_preserves_checkpoint_and_records_copy_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / "state"
            state.mkdir()
            (state / "sidecar.db").write_bytes(b"first")
            timings = Timings()
            journal = InstrumentedJournal(root / "run", {"kind": "DEVELOPMENT_PROFILING"}, timings)
            with JournalProbe(timings):
                journal.commit(0, state, {"kind": "initial"})
                journal.begin_step(1, "development_ingest")
                attempt = journal.create_attempt(1, journal.checkpoint_path(0) / "state")
                (attempt / "sidecar.db").write_bytes(b"second")
                journal.commit(1, attempt, {"kind": "fake_ingest"})
            self.assertEqual(journal.readback()["status"], "PASS")
            self.assertGreater(timings.values["attempt_copy_s"], 0)
            self.assertGreater(timings.values["checkpoint_copy_s"], 0)
            self.assertGreater(timings.values["checkpoint_hash_s"], 0)

    def test_profile_identifier_rejects_path(self):
        with self.assertRaises(ValueError):
            simple_id("../../formal")


if __name__ == "__main__":
    unittest.main()
