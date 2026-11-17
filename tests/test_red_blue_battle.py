import unittest
from red_team.interface import validate_request
from red_team.battle import run
from evaluator.red_blue_evaluator import evaluate

REQUEST = {"scenario_id":"red-test-002", "environment":"cyberbattlesim", "objective":"evaluate_detection", "strategy":"multi_step_simulated_intrusion", "max_steps":3, "seed":100010}

class FakeAdapter:
    def run_approved_scenario(self, scenario, seed, timeout, steps):
        return {"execution_status":"actual", "scenario_id":scenario, "seed":seed,
                "events":[{"is_demo":True,"event_id":"e1","event_type":"file_change_burst","device_id":"d"}],
                "trace":[{"step":1}]}

class RedBlueTests(unittest.TestCase):
    def test_schema_rejects_target_and_unknown_scenario(self):
        with self.assertRaises(ValueError): validate_request({**REQUEST, "target":"192.0.2.1"})
        with self.assertRaises(ValueError): validate_request({**REQUEST, "scenario_id":"bad"})

    def test_battle_keeps_truth_private_and_never_applies_policy(self):
        result = run(REQUEST, adapter=FakeAdapter())
        self.assertEqual(result["execution_status"], "actual")
        self.assertNotIn("_truth", result["red_request"])
        self.assertTrue(result["blue"]["events"][0]["detected"])
        self.assertEqual(result["independent_evaluation"]["detection_status"], "detected")
        self.assertEqual(result["independent_evaluation"]["blocking_status"], "unknown")
        self.assertFalse(result["policy_applied"])

    def test_failed_execution_is_unknown(self):
        self.assertEqual(evaluate(REQUEST, {"execution_status":"failed"}, [] )["overall_status"], "unknown")

if __name__ == "__main__": unittest.main()
