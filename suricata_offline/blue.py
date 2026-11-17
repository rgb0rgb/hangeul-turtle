"""Conservative Blue boundary for Suricata offline events."""
def analyze(event):
    suspicious = event.get("event_type") == "alert" or bool(event.get("signature"))
    return {"event_id": event["event_id"], "detected": suspicious,
            "reason":"Suricata offline alert evidence" if suspicious else "non-alert observation",
            "policy_mode":"dry-run", "approval_required":True,
            "policy_candidate": {"action":"observe" if not suspicious else "block_dry_run",
                "scope":event.get("dst_ip"), "reason":"administrator approval required",
                "approval_required":True}}
