import json
import tempfile
import unittest
from suricata_offline.parser import parse_eve, to_common_event
from suricata_offline.blue import analyze

class SuricataOfflineTests(unittest.TestCase):
    def test_eve_is_converted_without_becoming_demo_data(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as f:
            f.write(json.dumps({"event_type":"alert", "alert":{"signature":"test", "severity":1}}) + "\n")
            f.flush()
            event = to_common_event(parse_eve(f.name)[0], 0)
        self.assertFalse(event["is_demo"])
        self.assertTrue(analyze(event)["detected"])
        self.assertTrue(analyze(event)["policy_candidate"]["approval_required"])

if __name__ == "__main__": unittest.main()
