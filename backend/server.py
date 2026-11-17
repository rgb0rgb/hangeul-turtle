import argparse
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCENARIOS = json.loads((ROOT / "simulator" / "scenarios.json").read_text())

class LabState:
    def __init__(self):
        self.events = []
        self.lock = threading.Lock()

    def submit(self, payload):
        scenario = payload.get("scenario_id")
        if scenario not in SCENARIOS:
            raise ValueError("scenario_id is not in the approved catalog")
        seed = int(payload.get("seed", 0))
        from simulator.generate_events import generate
        from agents.blue.analyze import analyze
        started = time.perf_counter()
        analyses = [analyze(event) for event in generate(scenario, seed)]
        record = {
            "scenario_id": scenario, "seed": seed, "is_demo": True,
            "red": {"status": "scenario_selected", "event_count": len(analyses)},
            "blue": {"detected_count": sum(1 for item in analyses if item["detected"]), "status": "analyzed"},
            "success": all(item["detected"] for item in analyses),
            "latency_ms": round((time.perf_counter() - started) * 1000, 3),
            "policy_mode": "dry-run", "approval_required": True,
        }
        with self.lock:
            self.events.insert(0, record); self.events = self.events[:50]
        return record

    def snapshot(self):
        with self.lock:
            cyberbattle_file = ROOT / "artifacts" / "cyberbattle_10.json"
            cyberbattle = json.loads(cyberbattle_file.read_text()) if cyberbattle_file.exists() else None
            slm = {"provider": "ollama", "model": "qwen2.5:7b", "status": "local_probe_completed", "model_training": False}
            optimization_file = ROOT / "artifacts" / "policy_optimization.json"
            optimization = json.loads(optimization_file.read_text()) if optimization_file.exists() else None
            return {"is_demo": True, "events": list(self.events), "experiments": getattr(self, "experiments", []), "cyberbattle": cyberbattle, "scenario_catalog": list(SCENARIOS), "slm": slm, "policy_optimization": optimization}

def make_handler(state, token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args): return
        def send_json(self, status, value):
            raw = json.dumps(value, ensure_ascii=False).encode()
            self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
        def do_GET(self):
            if self.path == "/api/v1/state": self.send_json(200, state.snapshot()); return
            if self.path in ("/", "/index.html"):
                raw = (ROOT / "frontend" / "index_expanded.html").read_bytes()
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw); return
            self.send_json(404, {"error": "not_found"})
        def do_POST(self):
            if self.path == "/api/v1/experiments/repeat":
                if self.headers.get("Authorization") != f"Bearer {token}": self.send_json(401, {"error": "unauthorized"}); return
                try:
                    length = int(self.headers.get("Content-Length", "0")); payload = json.loads(self.rfile.read(length)); repetitions = max(1, min(int(payload.get("repetitions", 10)), 100))
                    from evaluator.repeat_experiment import run, run_three_way
                    result = run_three_way(repetitions) if payload.get("mode") == "slm" else run(repetitions)
                    with state.lock: state.experiments = [result] + getattr(state, "experiments", [])[:9]
                    self.send_json(201, result)
                except (ValueError, TypeError, json.JSONDecodeError) as exc: self.send_json(400, {"error": str(exc)})
                return
            if self.path != "/api/v1/red/events": self.send_json(404, {"error": "not_found"}); return
            if self.headers.get("Authorization") != f"Bearer {token}": self.send_json(401, {"error": "unauthorized"}); return
            try:
                length = int(self.headers.get("Content-Length", "0")); payload = json.loads(self.rfile.read(length))
                self.send_json(201, state.submit(payload))
            except (ValueError, TypeError, json.JSONDecodeError) as exc: self.send_json(400, {"error": str(exc)})
    return Handler

def create_server(host="127.0.0.1", port=8090, token=None):
    token = token or os.environ.get("AI_HOME_SHIELD_TOKEN")
    if not token: raise ValueError("AI_HOME_SHIELD_TOKEN or token argument is required")
    return ThreadingHTTPServer((host, port), make_handler(LabState(), token))

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8090); p.add_argument("--token", required=True)
    args = p.parse_args(); server = create_server(args.host, args.port, args.token)
    print(f"Blue lab server listening on {args.host}:{args.port} (demo-only)")
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
