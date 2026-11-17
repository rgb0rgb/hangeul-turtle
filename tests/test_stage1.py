import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from simulator.generate_events import generate
from agents.blue.analyze import analyze

class Stage1Tests(unittest.TestCase):
    def test_reproducible_demo_events(self):
        self.assertEqual(list(generate("login_burst", 42)), list(generate("login_burst", 42)))
        self.assertTrue(all(e["is_demo"] for e in generate("login_burst", 42)))
    def test_unknown_scenario_rejected(self):
        with self.assertRaises(ValueError): list(generate("port_scan", 1))
    def test_policy_requires_approval_and_dry_run(self):
        result = analyze(next(generate("iot_new_destination", 1)))
        self.assertTrue(result["detected"])
        self.assertTrue(result["policy_candidate"]["approval_required"])
        self.assertEqual(result["policy_candidate"]["action"], "block_dry_run")
    def test_compose_isolation_markers(self):
        compose = (ROOT / "docker-compose.yml").read_text()
        self.assertIn("internal: true", compose)
        self.assertNotIn("privileged: true", compose)
        self.assertNotIn("host", compose)

if __name__ == "__main__": unittest.main()
