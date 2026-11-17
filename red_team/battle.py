"""Red scenario -> isolated CyberBattleSim -> Blue -> independent evaluation."""
import copy
import uuid
from red_team.interface import CATALOG, validate_request
from simulator.cyberbattle_adapter import CyberBattleSimAdapter, MAX_RUNTIME_SECONDS
from agents.blue.analyze import analyze
from evaluator.red_blue_evaluator import evaluate

def run(request, adapter=None, timeout_seconds=MAX_RUNTIME_SECONDS):
    value = validate_request(request)
    adapter = adapter or CyberBattleSimAdapter()
    spec = CATALOG[value["scenario_id"]]
    execution = adapter.run_approved_scenario(spec["simulator_scenario"], value["seed"], timeout_seconds, value["max_steps"])
    # Only observed events cross into Blue; objective, strategy and truth stay private.
    blue_events = [analyze(event) for event in execution.get("events", [])]
    private_request = copy.deepcopy(value)
    private_request["_truth"] = spec["truth"]
    return {"run_id": "red-run-" + uuid.uuid4().hex, "red_request": value,
            "execution_status": execution["execution_status"], "execution": execution,
            "blue": {"events": blue_events, "policy_mode": "dry-run", "approval_required": True},
            "independent_evaluation": evaluate(private_request, execution, blue_events),
            "policy_applied": False, "external_network": False}
