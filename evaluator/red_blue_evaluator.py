"""Independent Red/Blue result classifier.

It consumes execution evidence and Blue output, but never trusts Blue's own
success claim. Abstract CyberBattleSim observations cannot prove blocking.
"""
def evaluate(red_request, execution, blue_events):
    if execution.get("execution_status") != "actual":
        return {"detection_status": "unknown", "blocking_status": "unknown", "overall_status": "unknown", "reason": "no actual simulator execution"}
    truth = red_request.get("_truth", "unknown")
    detected = [bool(item.get("detected")) for item in blue_events if isinstance(item, dict) and "detected" in item]
    detection_status = "detected" if truth == "attack" and any(detected) else ("not_detected" if truth == "attack" and detected else "unknown")
    return {"detection_status": detection_status, "blocking_status": "unknown",
            "overall_status": detection_status if detection_status == "not_detected" else "unknown",
            "reason": "CyberBattleSim abstract state provides no blocking evidence", "blue_claims_ignored": True}
