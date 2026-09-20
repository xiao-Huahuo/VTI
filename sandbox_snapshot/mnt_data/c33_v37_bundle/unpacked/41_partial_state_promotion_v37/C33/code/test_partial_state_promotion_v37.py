import unittest
from partial_state_promotion_v37 import (
    memora_partial_retry,
    memora_direct_force_rebuild,
    lightmem_partial_resume,
    lightmem_rerun,
    ironcurtain_negative_control,
)


class TestV37(unittest.TestCase):
    def test_memora_partial_promoted(self):
        r = memora_partial_retry()
        self.assertTrue(r["skip_on_retry"])
        self.assertLess(r["sessions_present"], r["complete_sessions_expected"])

    def test_memora_force_rebuild_keeps_stale(self):
        r = memora_direct_force_rebuild()
        self.assertEqual(r["clear_calls"], 0)
        self.assertTrue(r["stale_survived"])

    def test_lightmem_partial_promoted(self):
        r = lightmem_partial_resume()
        self.assertFalse(r["snapshot_exists"])
        self.assertTrue(r["backend_has_any"])
        self.assertTrue(r["construction_skipped"])
        self.assertTrue(r["search_loads"])
        self.assertLess(len(r["messages_present"]), r["expected_messages"])

    def test_lightmem_rerun_does_not_reset(self):
        r = lightmem_rerun()
        self.assertFalse(r["skipped"])
        self.assertTrue(r["old_state_survived"])

    def test_ironcurtain_does_not_promote_partial(self):
        r = ironcurtain_negative_control()
        self.assertEqual(r["db_rows_after_failure"], [])
        self.assertFalse(r["checkpoint_contains_question"])
        self.assertTrue(r["resume_reruns"])


if __name__ == "__main__":
    unittest.main()
