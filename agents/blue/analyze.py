def analyze(event):
    if not event.get("is_demo"):
        raise ValueError("only demo events are accepted")
    high_signal = {"auth_failure_burst", "new_destination", "file_change_burst", "iot_config_anomaly"}
    suspicious = event.get("event_type") in high_signal
    return {
        "event_id": event["event_id"], "detected": suspicious,
        "reason": "허용된 합성 시나리오의 이상 징후" if suspicious else "기준선 관찰",
        "policy_candidate": {"policy_id": "dry-run-" + event["event_id"], "scope": event["device_id"],
                             "match": {"event_type": event["event_type"]}, "action": "block_dry_run" if suspicious else "observe",
                             "reason": "독립 검증 및 관리자 승인 필요", "rollback": {"mode": "automatic"}, "approval_required": True}
    }

def analyze_simulator_observation(observation, step):
    """Summarize an abstract simulator observation without interpreting it as a command."""
    if isinstance(observation, dict):
        fields = sorted(str(key) for key in observation.keys())[:32]
        shape = {"type": "dict", "field_count": len(observation), "fields": fields}
    else:
        shape = {"type": type(observation).__name__, "field_count": None, "fields": []}
    return {"step": step, "source": "CyberBattleSim", "classification": "abstract_observation", "detected": None, "observation_shape": shape, "response": "observe_only", "policy_mode": "dry-run", "approval_required": True,
            "policy_candidate": {"policy_id": "cyberbattle-observe-only", "scope": "simulator-observation", "match": {"source": "CyberBattleSim"}, "action": "observe", "reason": "독립 평가 및 관리자 승인 필요", "rollback": {"mode": "automatic"}, "approval_required": True}}
