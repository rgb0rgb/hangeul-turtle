"""Deterministic synthetic Red AI events; no commands, targets, or real data."""
import json
import random
from pathlib import Path
from .behavior import ROLES

CATALOG = json.loads((Path(__file__).with_name("scenarios.json")).read_text())
def generate(scenario_id, seed):
    if scenario_id not in CATALOG: raise ValueError("scenario not approved")
    spec = CATALOG[scenario_id]; rng = random.Random(seed)
    role = spec["role"]
    if role not in ROLES: raise ValueError("invalid scenario role")
    common = {"scenario_id":scenario_id, "seed":seed, "user_id":"synthetic-user-" + role,
              "role":role, "device_id":"synthetic-device-01", "session_id":"synthetic-session-" + str(seed),
              "records":10, "sensitivity":"internal", "hour":12, "action":"read", "approved_business_batch":False}
    t = spec["attack_type"]
    if t == "normal_business_batch": common.update(records=1200, sensitivity="internal", approved_business_batch=True, action="read")
    elif t == "abnormal_access": common.update(records=20, sensitivity="customer_pii", action="read", new_device=True)
    elif t == "privileged_bulk_export": common.update(records=5000, sensitivity="customer_pii", action="bulk_export", external_destination=True)
    elif t == "off_hours_sensitive_work": common.update(records=100, sensitivity="financial", action="read", hour=2)
    elif t == "blended_suspicious_activity": common.update(records=900, sensitivity="customer_pii", action="read", new_location=True, hour=21)
    elif t == "staged_intrusion": common.update(records=30, sensitivity="credentials", action="read", sequence_step=3, new_device=True)
    elif t == "untrusted_document_instruction": common.update(action="execute_untrusted_tool", untrusted_document=True, tool_request="export")
    elif t == "unauthorized_external_transfer": common.update(records=200, sensitivity="customer_pii", action="external_transfer", external_destination=True)
    elif t == "audit_log_tamper": common.update(action="modify_audit_log", sensitivity="security_audit")
    common["nonce"] = rng.randint(0, 2_147_483_647)
    return common
