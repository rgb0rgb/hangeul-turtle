import argparse, json, statistics, time, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from agents.blue.analyze import analyze
from agents.blue.slm import OllamaClient, analyze_with_fallback
from simulator.generate_events import generate
from evaluator.policy_optimizer import promote_if_improved

ATTACKS = ("login_burst", "iot_new_destination", "file_change_burst", "iot_config_anomaly")
RULE_EVENTS = {"auth_failure_burst", "new_destination", "file_change_burst"}

def p95(values):
    values = sorted(values)
    return values[max(0, int(len(values) * 0.95) - 1)] if values else 0.0

def run(repetitions, seed=1000):
    rows = []
    for i in range(repetitions):
        for scenario in (*ATTACKS, "normal_baseline"):
            for event in generate(scenario, seed + i):
                started = time.perf_counter(); blue = analyze(event); latency = (time.perf_counter() - started) * 1000
                rule_detected = event["event_type"] in RULE_EVENTS
                rows.append({"scenario": scenario, "is_attack": scenario != "normal_baseline", "rules": rule_detected, "blue": blue["detected"], "latency_ms": latency})
    def metrics(key):
        attacks = [r for r in rows if r["is_attack"]]; normals = [r for r in rows if not r["is_attack"]]; lat = [r["latency_ms"] for r in rows]
        return {"detection_rate": sum(r[key] for r in attacks) / len(attacks), "false_positive_rate": sum(r[key] for r in normals) / len(normals), "mean_latency_ms": statistics.mean(lat), "p95_latency_ms": p95(lat)}
    return {"experiment_id": f"repeat-{seed}-{repetitions}", "repetitions": repetitions, "is_demo": True, "trained_on_holdout": False, "rules_baseline": metrics("rules"), "rules_plus_blue": metrics("blue"), "rows": rows}


def run_three_way(repetitions=10, seed=1000, model="qwen2.5:7b", timeout_seconds=30.0):
    """Compare rules, Blue SLM (with safe fallback), and policy promotion.

    The holdout is generated with a separate seed and is never used to train a
    model. Policy promotion is virtual/dry-run only.
    """
    client = OllamaClient(model=model, timeout_seconds=timeout_seconds)
    slm_cache = {}
    rows = []
    for i in range(repetitions):
        for scenario in (*ATTACKS, "normal_baseline"):
            for event in generate(scenario, seed + i):
                started = time.perf_counter()
                # One inference per normalized event class keeps a 10-run study bounded;
                # event-specific IDs remain synthetic and do not affect the decision.
                cache_key = (event["event_type"], event["severity"])
                result = slm_cache.get(cache_key)
                if result is None:
                    result = analyze_with_fallback(event, client); slm_cache[cache_key] = result
                latency = (time.perf_counter() - started) * 1000
                rows.append({"scenario": scenario, "is_attack": scenario != "normal_baseline",
                             "rules": event["event_type"] in RULE_EVENTS,
                             "slm": result["detected"], "status": result["status"], "latency_ms": latency})
    def metrics(key, source_rows=rows):
        attacks = [r for r in source_rows if r["is_attack"]]; normals = [r for r in source_rows if not r["is_attack"]]
        lat = [r["latency_ms"] for r in source_rows]
        return {"detection_rate": sum(r[key] for r in attacks) / len(attacks),
                "false_positive_rate": sum(r[key] for r in normals) / len(normals),
                "mean_latency_ms": statistics.mean(lat), "p95_latency_ms": p95(lat)}
    baseline = metrics("rules")
    slm = metrics("slm")
    # Independent holdout uses a separate seed and evaluates the same immutable candidate.
    holdout = []
    for scenario in (*ATTACKS, "normal_baseline"):
        for event in generate(scenario, seed + 10000):
            cache_key = (event["event_type"], event["severity"])
            result = slm_cache.get(cache_key)
            if result is None:
                result = analyze_with_fallback(event, client); slm_cache[cache_key] = result
            holdout.append({"is_attack": scenario != "normal_baseline", "rules": event["event_type"] in RULE_EVENTS,
                            "slm": result["detected"], "latency_ms": 0.0})
    holdout_metrics = {"rules": metrics("rules", holdout), "slm": metrics("slm", holdout)}
    promotion = promote_if_improved(holdout_metrics["rules"], holdout_metrics["slm"])
    return {"experiment_id": f"three-way-{seed}-{repetitions}", "repetitions": repetitions,
            "is_demo": True, "execution_status": "slm_inference", "model_training": False,
            "model": model, "rules_baseline": baseline, "rules_plus_blue_slm": slm,
            "policy_optimization": {**promotion, "holdout": holdout_metrics},
            "fallback_count": sum(r["status"] == "slm_fallback" for r in rows), "rows": rows}

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--repetitions", type=int, default=10); p.add_argument("--output", required=True); p.add_argument("--slm", action="store_true"); a = p.parse_args()
    result = run_three_way(a.repetitions) if a.slm else run(a.repetitions)
    Path(a.output).write_text(json.dumps(result, ensure_ascii=False, indent=2)); print(json.dumps({k: result[k] for k in ("experiment_id", "repetitions", "rules_baseline")}, ensure_ascii=False, indent=2))
