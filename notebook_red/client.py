"""Python 3.12 notebook-side Red client. No shell or network target is accepted."""
import argparse
import json
from urllib.request import Request, urlopen

SCENARIOS = {"login_burst", "iot_new_destination", "file_change_burst", "iot_config_anomaly", "normal_baseline"}

def submit(base_url, token, scenario_id, seed, timeout=5):
    if scenario_id not in SCENARIOS: raise ValueError("scenario is not approved")
    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed <= 2147483647: raise ValueError("seed out of range")
    body = json.dumps({"scenario_id": scenario_id, "seed": seed}).encode()
    req = Request(base_url.rstrip("/") + "/api/v1/red/scenario", data=body, method="POST", headers={"Content-Type": "application/json", "X-Red-Token": token})
    with urlopen(req, timeout=timeout) as response: return json.loads(response.read())

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--url", required=True); p.add_argument("--token", required=True); p.add_argument("--scenario", default="login_burst", choices=sorted(SCENARIOS)); p.add_argument("--seed", type=int, default=42); p.add_argument("--timeout", type=float, default=5)
    a = p.parse_args(); print(json.dumps(submit(a.url, a.token, a.scenario, a.seed, a.timeout), ensure_ascii=False, indent=2))
