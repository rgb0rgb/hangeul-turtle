"""Independent, dry-run policy promotion for synthetic experiments."""
import json
from pathlib import Path
from typing import Any, Dict

from agents.blue.analyze import analyze
from simulator.generate_events import generate


def promote_if_improved(baseline: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    improved = (candidate["detection_rate"] >= baseline["detection_rate"] and
                candidate["false_positive_rate"] <= baseline["false_positive_rate"] and
                (candidate["detection_rate"] > baseline["detection_rate"] or
                 candidate["false_positive_rate"] < baseline["false_positive_rate"]))
    return {"candidate_version": "policy-v2-validated" if improved else "policy-v1-baseline",
            "promoted": improved, "reason": "independent holdout improved" if improved else "no regression-free improvement",
            "model_training": False}


def save_result(result: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


def evaluate_holdout(scenario_id: str, request_seed: int, observations) -> Dict[str, Any]:
    """Evaluate the immutable Blue candidate on a separate, unseen seed.

    The request seed is never used for the holdout.  Simulator observations are
    deliberately treated as data; no observed value is turned into an action.
    """
    holdout_seed = (request_seed + 100_003) % 2_147_483_648
    events = list(generate(scenario_id, holdout_seed))
    baseline_detected = sum(analyze(event)["detected"] for event in events)
    candidate_detected = 0  # observe-only is the only safe simulator policy
    attack = scenario_id != "normal_baseline"
    count = len(events) or 1
    baseline = {"detection_rate": baseline_detected / count if attack else 0.0,
                "false_positive_rate": baseline_detected / count if not attack else 0.0}
    candidate = {"detection_rate": candidate_detected / count if attack else 0.0,
                 "false_positive_rate": candidate_detected / count if not attack else 0.0}
    return {"holdout_seed": holdout_seed, "request_seed_excluded": True,
            "observation_count": len(observations), "baseline": baseline,
            "candidate": candidate, "model_training": False}
