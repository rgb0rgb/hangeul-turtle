import json
from urllib.request import Request, urlopen

class RedClient:
    """Safe Red client: submits catalog IDs only, never shell commands."""
    def __init__(self, blue_url, token, timeout=5): self.blue_url, self.token, self.timeout = blue_url.rstrip("/"), token, timeout
    def submit_scenario(self, scenario_id, seed=0):
        body = json.dumps({"scenario_id": scenario_id, "seed": seed}).encode()
        request = Request(self.blue_url + "/api/v1/red/events", data=body, method="POST", headers={"Authorization": "Bearer " + self.token, "Content-Type": "application/json"})
        with urlopen(request, timeout=self.timeout) as response: return json.loads(response.read())
