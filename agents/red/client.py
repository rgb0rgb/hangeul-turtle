import json
from pathlib import Path
from urllib.request import Request, urlopen

APPROVED_SCENARIOS = tuple(json.loads((Path(__file__).parents[1] / "../simulator/scenarios.json").resolve().read_text()).keys())

def select_scenario(scenario_id, seed=0):
    """Return a bounded Red action; never accepts a command, URL, or IP."""
    if scenario_id not in APPROVED_SCENARIOS:
        raise ValueError("scenario_id is not approved")
    if not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    return {"scenario_id": scenario_id, "seed": seed, "status": "approved_virtual_action", "external_network": False}

class RedClient:
    """Safe Red client: submits catalog IDs only, never shell commands."""
    def __init__(self, blue_url, token, timeout=5): self.blue_url, self.token, self.timeout = blue_url.rstrip("/"), token, timeout
    def submit_scenario(self, scenario_id, seed=0):
        body = json.dumps(select_scenario(scenario_id, seed)).encode()
        request = Request(self.blue_url + "/api/v1/red/events", data=body, method="POST", headers={"Authorization": "Bearer " + self.token, "Content-Type": "application/json"})
        with urlopen(request, timeout=self.timeout) as response: return json.loads(response.read())
