import unittest
from teardown_supervisor import teardown_abort

class TeardownRecognitionTests(unittest.TestCase):
    def test_complete_teardown_only(self):
        signature='libc++abi: recursive_mutex lock failed: Invalid argument SIGABRT'
        self.assertFalse(teardown_abort(signature))
        self.assertTrue(teardown_abort('{"status": "COMPLETE"}\n'+signature))
        self.assertFalse(teardown_abort('{"status": "COMPLETE"}\nLLMError truncated JSON'))

if __name__=='__main__':unittest.main()
