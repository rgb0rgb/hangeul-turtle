"""Bounded CyberBattleSim execution boundary.

The request path uses a child process so a simulator failure cannot turn into a
mock result.  The child only imports CyberBattleSim and runs its abstract Gym
environment; it never receives a command, URL, address, or shell input.
"""
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from .generate_events import generate

ROOT = Path(__file__).parents[1]
MAX_STEPS = 8
MAX_RUNTIME_SECONDS = 15.0


def sample_valid_action(env, observation):
    """Select the first action explicitly allowed by CyberBattleSim's mask."""
    import numpy as np
    for kind, mask in observation.get("action_mask", {}).items():
        valid = np.argwhere(np.asarray(mask) == 1)
        if len(valid):
            return {kind: valid[0].astype(np.int32)}
    raise RuntimeError("CyberBattleSim returned no valid action")

class CyberBattleSimAdapter:
    def __init__(self):
        self.package_available = importlib.util.find_spec("cyberbattle") is not None

    def status(self):
        return {"package_available": self.package_available, "execution_status": "not_run"}

    def run_actual_smoke(self, seed=7, steps=3):
        """Run only CyberBattleSim's abstract Gym environment; never uses host networking."""
        if not self.package_available:
            raise RuntimeError("CyberBattleSim package is not installed")
        import gymnasium as gym
        import cyberbattle  # noqa: F401 - registers CyberBattleChain-v0
        env = gym.make("CyberBattleChain-v0", size=4)
        observation, _ = env.reset(seed=seed)
        trace = []
        blue_observations = []
        from agents.blue.analyze import analyze_simulator_observation
        started = time.perf_counter()
        for index in range(steps):
            action = sample_valid_action(env, observation)
            observation, reward, terminated, truncated, _ = env.step(action)
            blue_observations.append(analyze_simulator_observation(observation, index + 1))
            trace.append({"step": index + 1, "reward": float(reward), "terminated": bool(terminated), "truncated": bool(truncated)})
            if terminated or truncated:
                break
        env.close()
        return {"adapter": "cyberbattle", "execution_status": "actual_smoke", "is_demo": True, "seed": seed, "trace": trace, "blue_observations": blue_observations, "latency_ms": round((time.perf_counter() - started) * 1000, 3), "observation_type": type(observation).__name__}

    def run_approved_scenario(self, scenario_id, seed, timeout_seconds=MAX_RUNTIME_SECONDS, steps=MAX_STEPS):
        if scenario_id not in ("login_burst", "iot_new_destination", "file_change_burst", "iot_config_anomaly", "normal_baseline"):
            raise ValueError("scenario is not approved")
        if not isinstance(seed, int) or isinstance(seed, bool) or not 0 <= seed <= 2147483647:
            raise ValueError("seed out of range")
        if not 0 < timeout_seconds <= MAX_RUNTIME_SECONDS:
            raise ValueError("timeout exceeds execution limit")
        if isinstance(steps, bool) or not isinstance(steps, int) or not 0 < steps <= MAX_STEPS:
            raise ValueError("steps out of range")
        executor = os.environ.get("AI_HOME_SHIELD_CYBERBATTLE_EXECUTOR", "local")
        if executor == "docker":
            command = ["docker", "compose", "run", "--rm", "--no-deps",
                       "--entrypoint", "python", "cyberbattle_smoke",
                       "simulator/cyberbattle_worker.py", "--scenario", scenario_id,
                       "--seed", str(seed), "--steps", str(steps)]
        elif executor == "local":
            command = [sys.executable, "-m", "simulator.cyberbattle_worker",
                       "--scenario", scenario_id, "--seed", str(seed), "--steps", str(steps)]
        else:
            raise ValueError("unsupported execution backend")
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(ROOT)}
        started = time.perf_counter()
        try:
            completed = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                                       text=True, timeout=timeout_seconds, check=False)
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError("CyberBattleSim execution timed out") from exc
        if completed.returncode != 0:
            raise RuntimeError("CyberBattleSim execution failed")
        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("CyberBattleSim returned invalid JSON") from exc
        if result.get("execution_status") != "actual" or result.get("scenario_id") != scenario_id:
            raise RuntimeError("CyberBattleSim did not provide an actual result")
        result["executor"] = executor
        result["latency_ms"] = round((time.perf_counter() - started) * 1000, 3)
        return result
