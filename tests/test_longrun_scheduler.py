import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from longrun.scheduler import resource_snapshot, check_budget

class LongrunTests(unittest.TestCase):
    def test_resource_guardrails_fail_closed(self):
        with self.assertRaises(Exception): check_budget({"load1": 9, "ram_available_mib": 10000, "gpu_free_mib": 1000})
        with self.assertRaises(Exception): check_budget({"load1": 1, "ram_available_mib": 1000, "gpu_free_mib": 1000})

    def test_snapshot_has_bounded_fields(self):
        value = resource_snapshot()
        self.assertIn("load1", value); self.assertIn("ram_available_mib", value)

if __name__ == "__main__": unittest.main()
