import unittest
from evaluator.repeat_experiment import run
from simulator.cyberbattle_adapter import CyberBattleSimAdapter
from agents.blue.analyze import analyze_simulator_observation

class NextStageTests(unittest.TestCase):
    def test_repeat_metrics_are_reproducible_and_separate_training(self):
        result = run(2, seed=9); self.assertTrue(result["is_demo"]); self.assertFalse(result["trained_on_holdout"]); self.assertEqual(result["experiment_id"], "repeat-9-2"); self.assertIn("p95_latency_ms", result["rules_plus_blue"])
    def test_cyberbattle_adapter_does_not_claim_real_run(self):
        adapter = CyberBattleSimAdapter(); self.assertEqual(adapter.status()["execution_status"], "not_run")
        if not adapter.package_available:
            with self.assertRaises(RuntimeError): adapter.run_approved_scenario("login_burst", 1, timeout_seconds=1)
    def test_blue_observation_boundary_is_dry_run(self):
        result = analyze_simulator_observation({"node": 1}, 1); self.assertIsNone(result["detected"]); self.assertEqual(result["response"], "observe_only"); self.assertTrue(result["approval_required"])

if __name__ == "__main__": unittest.main()
