import json
import unittest
from unittest.mock import patch

from agents.blue.collaborative import run_collaboration


class FakeClient:
    def __init__(self, model, timeout_seconds): self.model = model
    def generate(self, prompt):
        self.prompt = prompt
        return '{"risk":"medium","reason":"safe observation review","action":"observe","approval_required":true}'


class CollaborativeTests(unittest.TestCase):
    def test_same_observation_sequence_and_validated_policies(self):
        observation = {"source": "CyberBattleSim", "step": 1, "observation_shape": {"fields": ["action_mask"]}}
        with patch("agents.blue.collaborative.OllamaClient", FakeClient):
            result = run_collaboration(observation, timeout_seconds=1)
        self.assertEqual(len(result["results"]), 4)
        self.assertTrue(result["all_models_validated"])
        self.assertTrue(all(item["status"] == "slm_inference" for item in result["results"]))
        self.assertTrue(all(item["validated_policy"]["approval_required"] for item in result["results"]))

    def test_failure_is_not_recorded_as_sllm_success(self):
        class FailingClient(FakeClient):
            def generate(self, prompt): raise RuntimeError("model unavailable")
        with patch("agents.blue.collaborative.OllamaClient", FailingClient):
            result = run_collaboration({"source": "CyberBattleSim"}, timeout_seconds=1)
        self.assertTrue(all(item["status"] == "slm_error" for item in result["results"]))
        self.assertFalse(result["all_models_validated"])
        self.assertTrue(all("validated_policy" not in item for item in result["results"]))

    def test_conditional_router_skips_unneeded_models_when_result_is_verified(self):
        observation = {"source": "synthetic", "detected": False}
        with patch("agents.blue.collaborative.OllamaClient", FakeClient):
            result = run_collaboration(observation, timeout_seconds=1)
        self.assertEqual(result["defense_result"], "success")
        self.assertEqual(result["called_model_count"], 1)
        self.assertEqual(result["skipped_model_count"], 3)


if __name__ == "__main__": unittest.main()
