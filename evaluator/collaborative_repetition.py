"""Repeated independent structured-output checks for one Blue model."""
import argparse
import json
from pathlib import Path

from agents.blue.collaborative import _run_one, _safe_observation


def run_repetitions(observation, model="qwen2.5:7b", role="기준 방어 분류기", repetitions=10, timeout_seconds=90.0):
    observation = _safe_observation(observation)
    rows = []
    for index in range(repetitions):
        item = _run_one(model, role, observation, [], timeout_seconds)
        item["repetition"] = index + 1
        rows.append(item)
    successes = sum(row["status"] == "slm_inference" for row in rows)
    return {"model": model, "repetitions": repetitions, "observation": observation,
            "success_count": successes, "success_rate": successes / repetitions,
            "results": rows, "policy_mode": "dry-run", "model_training": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()
    if not 1 <= args.repetitions <= 100:
        raise ValueError("repetitions out of range")
    observation = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = run_repetitions(observation, repetitions=args.repetitions,
                             timeout_seconds=args.timeout)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"model": result["model"], "repetitions": result["repetitions"],
                      "success_count": result["success_count"],
                      "success_rate": result["success_rate"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
