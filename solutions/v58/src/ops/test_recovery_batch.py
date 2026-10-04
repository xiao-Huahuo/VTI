import copy,json,unittest
from recovery_batch import mapping_check,MANIFEST,worker_teardown_abort

class RecoveryMappingTests(unittest.TestCase):
    def test_missing_frozen_slot_rejected(self):
        m=json.loads(MANIFEST.read_text());m['sequences'].pop()
        with self.assertRaisesRegex(RuntimeError,'24 frozen slots'):mapping_check(m)
    def test_duplicate_run_selection_rejected(self):
        m=json.loads(MANIFEST.read_text());m['sequences'][1]['run_id']=m['sequences'][0]['run_id']
        with self.assertRaisesRegex(RuntimeError,'Duplicate run'):mapping_check(m)
    def test_policy_change_rejected_before_reuse(self):
        m=json.loads(MANIFEST.read_text());r=m['sequences'][0];r['policy']='V' if r['policy']=='N' else 'N'
        with self.assertRaisesRegex(RuntimeError,'design mismatch'):mapping_check(m)
    def test_direct_native_abort_requires_complete_and_actual_signal(self):
        signature='libc++abi: recursive_mutex lock failed: Invalid argument'
        complete='{"status": "COMPLETE"}\n'+signature
        self.assertTrue(worker_teardown_abort(complete,-6))
        self.assertFalse(worker_teardown_abort(signature,-6))
        self.assertFalse(worker_teardown_abort(complete,1))
        self.assertFalse(worker_teardown_abort('{"status": "COMPLETE"} Server disconnected',-6))
if __name__=='__main__':unittest.main()
