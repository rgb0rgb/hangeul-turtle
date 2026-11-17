import json
import threading
import unittest
from http.client import HTTPConnection
from backend.red_api import create_server


class RedAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server("127.0.0.1", 0, "dedicated-test-token", {"127.0.0.1"})
        cls.server.cyberbattle_adapter = FakeActualAdapter()
        threading.Thread(target=cls.server.serve_forever, daemon=True).start(); cls.port = cls.server.server_address[1]
    @classmethod
    def tearDownClass(cls): cls.server.shutdown(); cls.server.server_close()
    def post(self, body, token="dedicated-test-token"):
        c = HTTPConnection("127.0.0.1", self.port); raw = json.dumps(body).encode(); c.request("POST", "/api/v1/red/scenario", raw, {"Content-Type":"application/json", "X-Red-Token":token}); r=c.getresponse(); data=json.loads(r.read()); c.close(); return r.status, data
    def test_approved_request_returns_actual_execution_and_evaluation(self):
        status, result = self.post({"scenario_id":"login_burst", "seed":42}); self.assertEqual(status, 201); self.assertEqual(result["execution_status"], "actual"); self.assertFalse(result["external_network"]); self.assertFalse(result["policy_promotion"]["promoted"]); self.assertTrue(result["independent_evaluation"]["request_seed_excluded"])
    def test_auth_and_schema_are_fail_closed(self):
        self.assertEqual(self.post({"scenario_id":"login_burst", "seed":42}, "demo-token")[0], 401)
        self.assertEqual(self.post({"scenario_id":"port_scan", "seed":42})[0], 400)
        self.assertEqual(self.post({"scenario_id":"login_burst", "seed":-1})[0], 400)
        self.assertEqual(self.post({"scenario_id":"login_burst", "seed":42, "command":"nmap"})[0], 400)
    def test_dedicated_service_rejects_demo_token_configuration(self):
        with self.assertRaises(ValueError): create_server("127.0.0.1", 0, "demo-token", {"127.0.0.1"})

    def test_execution_failure_never_becomes_mock_success(self):
        original = self.server.cyberbattle_adapter
        self.server.cyberbattle_adapter = FailingAdapter()
        try:
            status, result = self.post({"scenario_id": "login_burst", "seed": 42})
            self.assertEqual(status, 502); self.assertEqual(result["execution_status"], "failed")
        finally:
            self.server.cyberbattle_adapter = original

    def test_execution_timeout_is_explicit(self):
        original = self.server.cyberbattle_adapter
        self.server.cyberbattle_adapter = TimeoutAdapter()
        try:
            status, result = self.post({"scenario_id": "login_burst", "seed": 42})
            self.assertEqual(status, 504); self.assertEqual(result["execution_status"], "failed")
        finally:
            self.server.cyberbattle_adapter = original

if __name__ == "__main__": unittest.main()


class FakeActualAdapter:
    def run_approved_scenario(self, scenario_id, seed, timeout_seconds):
        return {"execution_status": "actual", "scenario_id": scenario_id, "seed": seed,
                "trace": [{"step": 1, "reward": 0.0, "terminated": False, "truncated": False}],
                "blue_observations": [{"step": 1, "node": 1}], "is_demo": True,
                "external_network": False}

class FailingAdapter:
    def run_approved_scenario(self, scenario_id, seed, timeout_seconds):
        raise RuntimeError("internal detail must not reach API")

class TimeoutAdapter:
    def run_approved_scenario(self, scenario_id, seed, timeout_seconds):
        raise TimeoutError("internal detail must not reach API")
