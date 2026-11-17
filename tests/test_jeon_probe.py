import unittest
from red_team.jeon_probe import run

class JeonProbeTests(unittest.TestCase):
    def test_target_is_isolated_and_content_is_not_returned(self):
        result = run(42)
        self.assertEqual(result["target_name"], "jeon.txt")
        self.assertTrue(result["file_found"])
        self.assertTrue(result["read_success"])
        self.assertTrue(result["content_match"])
        self.assertIsNone(result.get("content"))
        self.assertFalse(result["host_filesystem_access"])
        self.assertFalse(result["content_recorded"])

if __name__ == "__main__": unittest.main()
