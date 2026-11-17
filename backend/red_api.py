"""Dedicated, fail-closed Red API for an approved virtual lab.

This service is intentionally separate from the browser demo on 127.0.0.1:8090.
It accepts only a scenario ID and bounded seed; it never accepts commands, URLs,
addresses, or arbitrary simulator actions.
"""
import argparse
import hmac
import json
import os
import threading
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parents[1]
CATALOG = json.loads((ROOT / "simulator" / "scenarios.json").read_text(encoding="utf-8"))
MAX_BODY = 2048
RATE_LIMIT = 20
WINDOW_SECONDS = 60
EXECUTION_TIMEOUT_SECONDS = 15.0


class RateLimiter:
    def __init__(self): self._items, self._lock = defaultdict(deque), threading.Lock()
    def allow(self, ip):
        now = time.monotonic()
        with self._lock:
            q = self._items[ip]
            while q and q[0] <= now - WINDOW_SECONDS: q.popleft()
            if len(q) >= RATE_LIMIT: return False
            q.append(now); return True


def validate_request(value):
    if not isinstance(value, dict) or set(value) != {"scenario_id", "seed"}: raise ValueError("schema violation")
    if not isinstance(value["scenario_id"], str) or value["scenario_id"] not in CATALOG: raise ValueError("scenario not approved")
    if isinstance(value["seed"], bool) or not isinstance(value["seed"], int) or not 0 <= value["seed"] <= 2147483647: raise ValueError("seed out of range")
    return value


class RedAPIHandler(BaseHTTPRequestHandler):
    server_version = "AIHomeShieldRedAPI/1.0"
    def log_message(self, fmt, *args): return
    def _json(self, status, value):
        raw = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path == "/health": self._json(200, {"service": "red-api", "status": "ready", "external_network": False}); return
        self._json(404, {"error": "not_found"})
    def do_POST(self):
        if self.path not in ("/api/v1/red/scenario", "/api/v1/red/battle"): self._json(404, {"error": "not_found"}); return
        peer = self.client_address[0]
        if peer not in self.server.allowed_ips: self._json(403, {"error": "source_ip_not_allowed"}); return
        supplied = self.headers.get("X-Red-Token", "")
        if not hmac.compare_digest(supplied, self.server.token): self._json(401, {"error": "unauthorized"}); return
        if not self.server.limiter.allow(peer): self._json(429, {"error": "rate_limit"}); return
        try:
            length = int(self.headers.get("Content-Length", "-1"))
            if length < 0 or length > MAX_BODY: raise ValueError("request too large")
            raw_value = json.loads(self.rfile.read(length))
            if self.path == "/api/v1/red/battle":
                from red_team.battle import run
                result = run(raw_value, adapter=self.server.cyberbattle_adapter, timeout_seconds=EXECUTION_TIMEOUT_SECONDS)
                self._json(201, result)
                return
            value = validate_request(raw_value)
            result = self.server.cyberbattle_adapter.run_approved_scenario(
                value["scenario_id"], value["seed"], timeout_seconds=EXECUTION_TIMEOUT_SECONDS)
            from agents.blue.analyze import analyze_simulator_observation
            observations = result.get("blue_observations", [])
            blue = [analyze_simulator_observation(item, item.get("step", i + 1))
                    for i, item in enumerate(observations)]
            from evaluator.policy_optimizer import evaluate_holdout, promote_if_improved
            evaluation = evaluate_holdout(value["scenario_id"], value["seed"], blue)
            promotion = promote_if_improved(evaluation["baseline"], evaluation["candidate"])
            self._json(201, {"service": "red-api", "execution_status": result["execution_status"],
                             "scenario_id": value["scenario_id"], "seed": value["seed"],
                             "execution": result, "blue": {"observations": blue,
                             "status": "analyzed", "policy_mode": "dry-run",
                             "approval_required": True}, "independent_evaluation": evaluation,
                             "policy_promotion": promotion, "external_network": False})
        except ValueError as exc: self._json(400, {"error": str(exc)})
        except TimeoutError: self._json(504, {"error": "execution_timeout", "execution_status": "failed"})
        except (RuntimeError, OSError): self._json(502, {"error": "execution_failed", "execution_status": "failed"})


def create_server(host="127.0.0.1", port=8091, token=None, allowed_ips=None):
    token = token or os.environ.get("AI_HOME_SHIELD_RED_TOKEN")
    if not token or token == "demo-token": raise ValueError("AI_HOME_SHIELD_RED_TOKEN must be a dedicated non-demo token")
    server = ThreadingHTTPServer((host, port), RedAPIHandler)
    server.token, server.allowed_ips, server.limiter = token, set(allowed_ips or {"127.0.0.1", "::1"}), RateLimiter()
    from simulator.cyberbattle_adapter import CyberBattleSimAdapter
    server.cyberbattle_adapter = CyberBattleSimAdapter()
    server.timeout = 5
    return server


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8091); p.add_argument("--token", default=None); p.add_argument("--allow-ip", action="append", default=[])
    a = p.parse_args(); server = create_server(a.host, a.port, a.token, set(a.allow_ip) or {"127.0.0.1", "::1"})
    print(f"Red API listening on {a.host}:{a.port}; approved virtual scenarios only")
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
