"""One-shot CyberBattleSim worker used by the Red API.

This module is intentionally narrow: approved scenario metadata is only
attached to observations; no scenario value becomes a simulator command.
"""
import argparse
import json
import resource
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from simulator.cyberbattle_adapter import CyberBattleSimAdapter, sample_valid_action  # noqa: E402
from simulator.generate_events import generate  # noqa: E402
from agents.blue.analyze import analyze_simulator_observation  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--steps", required=True, type=int)
    args = parser.parse_args()
    if args.steps < 1 or args.steps > 8:
        raise ValueError("steps out of range")
    adapter = CyberBattleSimAdapter()
    if not adapter.package_available:
        raise RuntimeError("CyberBattleSim package is not installed")
    import gymnasium as gym
    import cyberbattle  # noqa: F401
    env = gym.make("CyberBattleChain-v0", size=4)
    observation, _ = env.reset(seed=args.seed)
    # Apply hard ceilings after library/environment initialization.  The
    # Docker service independently enforces read-only FS, internal network,
    # no-new-privileges, CPU, memory, and PID limits for the whole container;
    # these limits bound the request's active simulation phase.
    resource.setrlimit(resource.RLIMIT_CPU, (12, 12))
    # RLIMIT_AS is virtual address space (not resident memory) and NumPy's
    # masked action tensor needs more virtual space than its 768 MiB RSS
    # container budget. The Docker cgroup remains the hard resident-memory
    # ceiling; keep this process-level virtual ceiling finite as well.
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 * 1024 * 1024, 2 * 1024 * 1024 * 1024))
    trace, blue = [], []
    try:
        for step in range(args.steps):
            action = sample_valid_action(env, observation)
            observation, reward, terminated, truncated, _ = env.step(action)
            blue.append(analyze_simulator_observation(observation, step + 1))
            trace.append({"step": step + 1, "reward": float(reward),
                          "terminated": bool(terminated), "truncated": bool(truncated)})
            if terminated or truncated:
                break
    finally:
        env.close()
    # Keep synthetic scenario evidence separate from the actual simulator
    # trace; it is never presented as an attack executed by CyberBattleSim.
    print(json.dumps({"adapter": "cyberbattle", "execution_status": "actual",
                      "scenario_id": args.scenario, "seed": args.seed,
                      "events": list(generate(args.scenario, args.seed)),
                      "trace": trace, "blue_observations": blue,
                      "is_demo": True, "external_network": False}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": type(exc).__name__}), file=sys.stderr)
        raise
