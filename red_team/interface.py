"""Validate Red AI experiment requests without accepting commands or targets."""
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
CATALOG = json.loads((ROOT / "red_team" / "scenarios.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((ROOT / "red_team" / "RED_BATTLE_REQUEST_SCHEMA.json").read_text(encoding="utf-8"))

def validate_request(value):
    if not isinstance(value, dict) or set(value) != set(SCHEMA["required"]):
        raise ValueError("red battle schema violation")
    if value["scenario_id"] not in CATALOG:
        raise ValueError("red scenario is not approved")
    spec = CATALOG[value["scenario_id"]]
    if value["environment"] != "cyberbattlesim" or value["objective"] != "evaluate_detection":
        raise ValueError("unsupported red experiment")
    if value["strategy"] != spec["strategy"]:
        raise ValueError("strategy does not match approved scenario")
    if isinstance(value["max_steps"], bool) or not isinstance(value["max_steps"], int) or not 1 <= value["max_steps"] <= 8:
        raise ValueError("max_steps out of range")
    if isinstance(value["seed"], bool) or not isinstance(value["seed"], int) or not 0 <= value["seed"] <= 2147483647:
        raise ValueError("seed out of range")
    return dict(value)
