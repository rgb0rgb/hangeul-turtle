import json, threading, unittest
from http.client import HTTPConnection
from backend.server import create_server

class FakeActualAdapter:
    def run_approved_scenario(self, scenario_id, seed, timeout_seconds):
        return {"execution_status": "actual", "scenario_id": scenario_id, "seed": seed,
                "trace": [], "blue_observations": [], "is_demo": True,
                "external_network": False}

class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server("127.0.0.1", 0, "test-token"); cls.server.cyberbattle_adapter = FakeActualAdapter(); cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start(); cls.port = cls.server.server_address[1]
    @classmethod
    def tearDownClass(cls): cls.server.shutdown(); cls.server.server_close()
    def request(self, method, path, body=None, auth=True):
        c = HTTPConnection("127.0.0.1", self.port); raw = json.dumps(body).encode() if body else None; headers = {"Content-Type": "application/json"} if body else {}
        if auth: headers["Authorization"] = "Bearer test-token"
        c.request(method, path, raw, headers); r = c.getresponse(); data = r.read(); c.close()
        return r.status, (json.loads(data) if data and r.getheader("Content-Type", "").startswith("application/json") else data)
    def test_red_blue_demo_exchange(self):
        status, result = self.request("POST", "/api/v1/red/events", {"scenario_id": "login_burst", "seed": 42}); self.assertEqual(status, 201); self.assertTrue(result["is_demo"]); self.assertTrue(result["success"]); self.assertEqual(result["policy_mode"], "dry-run")
    def test_rejects_missing_auth_and_unknown_scenario(self):
        self.assertEqual(self.request("POST", "/api/v1/red/events", {"scenario_id": "login_burst"}, auth=False)[0], 401); self.assertEqual(self.request("POST", "/api/v1/red/events", {"scenario_id": "port_scan"})[0], 400)
    def test_korean_dashboard_is_served(self): self.assertEqual(self.request("GET", "/", auth=False)[0], 200)
    def test_repeat_endpoint_returns_comparison(self):
        status, result = self.request("POST", "/api/v1/experiments/repeat", {"repetitions": 2})
        self.assertEqual(status, 201); self.assertFalse(result["trained_on_holdout"]); self.assertIn("p95_latency_ms", result["rules_plus_blue"])
    def test_state_exposes_actual_cyberbattle_result_when_present(self):
        status, result = self.request("GET", "/api/v1/state", auth=False); self.assertEqual(status, 200)
        self.assertEqual(result["cyberbattle"]["execution_status"], "actual_smoke"); self.assertEqual(result["cyberbattle"]["episode_count"], 10)

if __name__ == "__main__": unittest.main()
