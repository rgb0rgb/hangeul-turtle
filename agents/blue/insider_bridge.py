"""Adapter from redacted insider events to the existing Blue collaboration path."""
from agents.blue.collaborative import run_collaboration

def collaboration_observation(event, analysis):
    """Do not pass raw customer data or secrets to models."""
    return {"source":"synthetic-insider-event", "role":event["role"], "action":event["action"],
            "hour":event["hour"], "records":event["records"], "sensitivity":event["sensitivity"],
            "risk":analysis["risk"], "detected":analysis["decision"] == "pending_approval"}

def assist(event, analysis, timeout_seconds=45.0):
    return run_collaboration(collaboration_observation(event, analysis), timeout_seconds)
