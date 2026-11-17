import argparse, json, sys
sys.path.insert(0, "/app")
from simulator.cyberbattle_adapter import CyberBattleSimAdapter

p = argparse.ArgumentParser(); p.add_argument("--seed", type=int, default=7); p.add_argument("--steps", type=int, default=3); p.add_argument("--episodes", type=int, default=1); args = p.parse_args()
adapter = CyberBattleSimAdapter(); results = [adapter.run_actual_smoke(args.seed + i, args.steps) for i in range(args.episodes)]
print(json.dumps({"adapter": "cyberbattle", "execution_status": "actual_smoke", "is_demo": True, "episodes": results, "episode_count": len(results), "blue_observation_count": sum(len(r["blue_observations"]) for r in results)}, ensure_ascii=False))
