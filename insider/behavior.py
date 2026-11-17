"""Explainable, synthetic user-behavior risk analysis."""
ROLES = {"general_user", "business_user", "manager", "system_admin", "super_admin", "security_officer"}
SENSITIVE = {"customer_pii", "financial", "credentials", "security_audit"}
HIGH_RISK_ACTIONS = {"bulk_export", "external_transfer", "disable_policy", "bulk_permission_change", "delete_audit_log", "modify_audit_log", "execute_untrusted_tool"}

def analyze(event):
    if not isinstance(event, dict) or event.get("role") not in ROLES:
        raise ValueError("invalid synthetic identity")
    reasons, score = [], 0
    hour = int(event.get("hour", 12))
    if hour < 6 or hour >= 22:
        score += 15; reasons.append("off_hours")
    sensitivity = event.get("sensitivity")
    amount = int(event.get("records", 0))
    if sensitivity in SENSITIVE:
        score += 15
    if amount >= 1000:
        score += 35; reasons.append("bulk_volume")
    if event.get("action") in HIGH_RISK_ACTIONS:
        score += 40; reasons.append("high_risk_action")
    if event.get("external_destination"):
        score += 30; reasons.append("external_destination")
    if event.get("new_device") or event.get("new_location"):
        score += 15; reasons.append("novel_context")
    if event.get("untrusted_document") or event.get("tool_request"):
        score += 30; reasons.append("untrusted_instruction")
    if event.get("sequence_step", 0) >= 2:
        score += 20; reasons.append("staged_sequence")
    # Role never waives a policy. Context can reduce suspicion for a normal,
    # approved batch, but not for explicit prohibited actions.
    explicit = event.get("action") in HIGH_RISK_ACTIONS
    if event.get("approved_business_batch") and not explicit and score < 40:
        risk = "low"
    elif score >= 80: risk = "critical"
    elif score >= 50: risk = "high"
    elif score >= 25: risk = "medium"
    else: risk = "low"
    return {"risk": risk, "score": score, "reasons": reasons,
            "explicit_policy_violation": explicit, "independent_rule_engine": True,
            "decision": "pending_approval" if explicit or risk in {"high", "critical"} else ("monitoring" if risk == "medium" else "allowed")}
