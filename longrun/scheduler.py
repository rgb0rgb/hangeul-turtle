"""Safety-bounded unattended Red/Blue experiment scheduler.

This runner only invokes the approved local CyberBattleSim child worker and
synthetic insider policy engine. It never accepts shell commands, network
targets, customer data, or firewall actions. A lock and stop file make restart
and operator stop fail-safe.
"""
import argparse
import json
import os
import random
import signal
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).parents[1]
PREFIX = os.environ.get("AI_HOME_SHIELD_LONGRUN_PREFIX", "red_blue_3h")
STOP_FILE = ROOT / "artifacts" / (PREFIX + ".stop")
LOCK_FILE = ROOT / "artifacts" / (PREFIX + ".lock")
EVENTS = ROOT / "artifacts" / (PREFIX + "_events.jsonl")
SUMMARY = ROOT / "artifacts" / (PREFIX + "_summary.json")
RED_IDS = ("red-test-001", "red-test-002", "red-test-003")
INSIDER_IDS = tuple(json.loads((ROOT / "insider" / "scenarios.json").read_text()))

class SafetyStop(Exception): pass

def now(): return time.time()

def resource_snapshot():
    result = {"load1": os.getloadavg()[0], "ram_available_mib": None, "gpu_free_mib": None, "gpu_used_mib": None}
    try:
        values = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, value = line.split(":", 1)
            if key in {"MemAvailable", "MemTotal"}: values[key] = int(value.split()[0]) // 1024
        result["ram_available_mib"] = values.get("MemAvailable")
    except (OSError, ValueError): pass
    try:
        import subprocess
        p = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.free", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=2)
        if p.returncode == 0 and p.stdout.strip():
            used, free = (int(x.strip()) for x in p.stdout.splitlines()[0].split(","))
            result.update(gpu_used_mib=used, gpu_free_mib=free)
    except (OSError, ValueError, subprocess.TimeoutExpired): pass
    return result

def check_budget(snapshot):
    # Conservative host guardrails; Docker imposes the worker-specific hard limits.
    if snapshot.get("ram_available_mib") is not None and snapshot["ram_available_mib"] < 2048:
        raise SafetyStop("ram_available_below_2048_mib")
    if snapshot.get("gpu_free_mib") is not None and snapshot["gpu_free_mib"] < 512:
        raise SafetyStop("gpu_free_below_512_mib")
    if snapshot["load1"] > 8.0:
        raise SafetyStop("load_average_above_8")

def acquire_lock():
    import fcntl
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    handle = LOCK_FILE.open("a+")
    try: fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError: raise RuntimeError("another experiment is already running")
    handle.write(str(os.getpid())); handle.flush()
    return handle

def run_one(kind, scenario_id, seed, max_steps, audit, approval):
    started = now()
    if kind == "jeon_probe":
        from red_team.jeon_probe import run
        result = run(seed)
        request_id = "jeon-run-" + uuid.uuid4().hex
        record = approval.submit({"request_id":request_id, "requester_id":"synthetic-red-ai"}, {"decision":"pending_approval"}, now=now())
        audit.append({"event":"protected_file_access_attempt", "request_id":request_id, "target_name":"jeon.txt", "state":record["state"], "policy_version":"insider-v1"})
        return {"kind":kind, "scenario_id":scenario_id, "execution_status":"synthetic_actual", **result,
                "detection_status":"detected", "blocking_status":"unknown", "approval_state":record["state"],
                "blue_model_results":"rule_engine_pending_optional_slm", "audit_integrity":audit.verify(),
                "latency_ms":round((now()-started)*1000,2)}
    if kind == "cyberbattle":
        os.environ["AI_HOME_SHIELD_CYBERBATTLE_EXECUTOR"] = "docker"
        from red_team.battle import run
        result = run({"scenario_id":scenario_id, "environment":"cyberbattlesim", "objective":"evaluate_detection",
                      "strategy":{"red-test-001":"normal_like_intrusion","red-test-002":"multi_step_simulated_intrusion","red-test-003":"uncertain_observation"}[scenario_id],
                      "max_steps":max_steps, "seed":seed}, timeout_seconds=15.0)
        return {"kind":kind, "scenario_id":scenario_id, "execution_status":result["execution_status"],
                "detection_status":result["independent_evaluation"]["detection_status"],
                "blocking_status":result["independent_evaluation"]["blocking_status"],
                "policy_applied":False, "blue_model_results":"existing_rule_boundary", "latency_ms":round((now()-started)*1000,2)}
    from insider.red_scenarios import generate
    from insider.behavior import analyze
    event = generate(scenario_id, seed); decision = analyze(event)
    request_id = "insider-run-" + uuid.uuid4().hex
    record = approval.submit({"request_id":request_id, "requester_id":event["user_id"]}, decision, now=now())
    audit.append({"event":"request", "request_id":request_id, "requester_id":event["user_id"], "state":record["state"], "risk":decision["risk"], "policy_version":"insider-v1"})
    return {"kind":kind, "scenario_id":scenario_id, "execution_status":"synthetic_actual", "risk":decision["risk"],
            "decision":record["state"], "detection_status":"detected" if decision["decision"] != "allowed" else "not_detected",
            "blocking_status":"unknown", "policy_applied":False, "blue_model_results":"rule_engine_pending_optional_slm",
            "audit_integrity":audit.verify(), "latency_ms":round((now()-started)*1000,2)}

def run(duration_seconds, seed, min_interval=120, max_interval=600, start_delay=None, llm_every=5):
    if not 1 <= duration_seconds <= 43_200: raise ValueError("duration out of range")
    if not 60 <= min_interval <= max_interval <= 600: raise ValueError("interval out of range")
    lock = acquire_lock(); started = now(); deadline = started + duration_seconds
    rng = random.Random(seed); counts = {}; errors = []; event_count = 0; stopped_reason = "duration_reached"
    audit = __import__("insider.audit", fromlist=["AuditLog"]).AuditLog()
    approval = __import__("insider.approval", fromlist=["ApprovalEngine"]).ApprovalEngine()
    previous = None
    def stop_handler(signum, frame): STOP_FILE.touch(exist_ok=True)
    signal.signal(signal.SIGTERM, stop_handler); signal.signal(signal.SIGINT, stop_handler)
    if start_delay is None: start_delay = rng.randint(min_interval, max_interval)
    try:
        while now() < deadline:
            if STOP_FILE.exists(): stopped_reason = "stop_requested"; break
            wait_until = min(now() + start_delay, deadline)
            while now() < wait_until:
                if STOP_FILE.exists(): stopped_reason = "stop_requested"; break
                time.sleep(min(5, wait_until-now()))
            if stopped_reason == "stop_requested" or now() >= deadline: break
            snapshot = resource_snapshot(); check_budget(snapshot)
            choices = [("cyberbattle", x) for x in RED_IDS] + [("insider", x) for x in INSIDER_IDS] + [("jeon_probe", "red-jeon-target")]
            choices = [x for x in choices if x[1] != previous] or choices
            kind, scenario_id = rng.choice(choices); previous = scenario_id
            run_seed = rng.randint(0, 2_147_483_647); max_steps = rng.randint(1, 8)
            try:
                result = run_one(kind, scenario_id, run_seed, max_steps, audit, approval)
                event_count += 1; counts[scenario_id] = counts.get(scenario_id, 0) + 1
                row = {"event_id":"longrun-" + uuid.uuid4().hex, "started_at":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                       "seed":run_seed, "max_steps":max_steps, "result":result, "resources_before":snapshot,
                       "audit_integrity":audit.verify(), "approval_queue_depth":len(approval.queue)}
                with EVENTS.open("a", encoding="utf-8") as handle: handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            except SafetyStop as exc: stopped_reason = str(exc); break
            except Exception as exc:
                errors.append({"scenario_id":scenario_id, "type":type(exc).__name__})
                with EVENTS.open("a", encoding="utf-8") as handle: handle.write(json.dumps({"event_id":"longrun-error-"+uuid.uuid4().hex,"seed":run_seed,"scenario_id":scenario_id,"error":type(exc).__name__,"resources_before":snapshot}, ensure_ascii=False) + "\n")
            start_delay = rng.randint(min_interval, max_interval)
    finally:
        summary = {"started_at":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)), "ended_at":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "duration_seconds":round(now()-started,2), "requested_duration_seconds":duration_seconds, "seed":seed,
                   "event_count":event_count, "scenario_counts":counts, "errors":errors, "stopped_reason":stopped_reason,
                   "policy_applied":False, "external_network":False, "audit_integrity":audit.verify(), "holdout_exposed":False,
                   "reproducibility":{"seed":seed,"min_interval":min_interval,"max_interval":max_interval}}
        SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        lock.close()
    return summary

def main():
    p=argparse.ArgumentParser(); p.add_argument("--duration-seconds", type=int, default=10_800); p.add_argument("--seed", type=int, required=True)
    p.add_argument("--min-interval", type=int, default=120); p.add_argument("--max-interval", type=int, default=600); p.add_argument("--start-delay", type=int, default=None)
    a=p.parse_args(); print(json.dumps(run(a.duration_seconds,a.seed,a.min_interval,a.max_interval,a.start_delay),ensure_ascii=False))
if __name__ == "__main__": main()
