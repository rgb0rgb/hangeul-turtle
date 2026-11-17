"""Synthetic Red/Blue insider-risk evaluation with a separate holdout seed."""
from insider.red_scenarios import CATALOG, generate
from insider.behavior import analyze
from insider.approval import ApprovalEngine
from insider.audit import AuditLog

def run_scenario(scenario_id, seed):
    event = generate(scenario_id, seed)
    decision = analyze(event)
    approvals = ApprovalEngine()
    audit = AuditLog()
    submitted = approvals.submit({"request_id":"req-" + scenario_id, "requester_id":event["user_id"]}, decision, now=1000)
    audit.append({"event":"request_received", "request_id":submitted["request_id"], "requester_id":event["user_id"], "state":submitted["state"], "risk":decision["risk"], "policy_version":"insider-v1"})
    return {"scenario_id":scenario_id, "seed":seed, "expected":CATALOG[scenario_id]["expected"], "event":event,
            "analysis":decision, "approval":submitted, "audit_integrity":audit.verify(), "policy_applied":False}

def evaluate_holdout(seed=700001):
    development = [run_scenario(sid, seed + i) for i, sid in enumerate(CATALOG)]
    holdout = [run_scenario(sid, seed + 100003 + i) for i, sid in enumerate(CATALOG)]
    def metrics(rows):
        positives = [x for x in rows if x["expected"] != "allowed"]
        negatives = [x for x in rows if x["expected"] == "allowed"]
        tp = sum(x["approval"]["state"] == x["expected"] for x in positives)
        fp = sum(x["approval"]["state"] == "pending_approval" for x in negatives)
        return {"detection_rate": tp / len(positives), "false_positive_rate": fp / len(negatives), "audit_complete": all(x["audit_integrity"] for x in rows)}
    return {"development": metrics(development), "holdout": metrics(holdout), "holdout_seed_offset":100003,
            "development_results":development, "holdout_results":holdout,
            "policy_promotion":{"promoted":False,"reason":"evaluation is report-only; no automatic promotion"}}
