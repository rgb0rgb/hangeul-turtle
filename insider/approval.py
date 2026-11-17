"""Fail-closed approval state machine with a local notification queue."""
import time
from dataclasses import dataclass, field

STATES = {"allowed", "monitoring", "pending_approval", "approved", "rejected", "expired", "failed"}

@dataclass
class ApprovalEngine:
    ttl_seconds: int = 300
    queue: list = field(default_factory=list)
    records: dict = field(default_factory=dict)

    def submit(self, request, analysis, now=None):
        now = time.time() if now is None else now
        rid = request.get("request_id")
        if not rid or request.get("requester_id") is None:
            raise ValueError("request identity required")
        state = analysis["decision"] if analysis["decision"] in {"allowed", "monitoring"} else "pending_approval"
        record = {"request_id": rid, "requester_id": request["requester_id"], "state": state,
                  "created_at": now, "expires_at": now + self.ttl_seconds,
                  "approver_role": "security_officer", "notification": "not_required"}
        if state == "pending_approval":
            record["notification"] = "queued"
            self.queue.append({"request_id": rid, "recipient_role": "security_officer", "status": "queued"})
        self.records[rid] = record
        return dict(record)

    def _live(self, rid, now):
        record = self.records[rid]
        if record["state"] == "pending_approval" and now >= record["expires_at"]:
            record["state"] = "expired"
        return record

    def decide(self, rid, approver_id, approver_role, approve, now=None):
        now = time.time() if now is None else now
        if rid not in self.records: raise KeyError(rid)
        record = self._live(rid, now)
        if record["state"] != "pending_approval": raise ValueError("request is not pending")
        if approver_role != "security_officer": raise PermissionError("independent security approver required")
        if approver_id == record["requester_id"]: raise PermissionError("self-approval forbidden")
        record.update({"state": "approved" if approve else "rejected", "approver_id": approver_id, "decided_at": now})
        return dict(record)

    def notification_failed(self, rid):
        if rid not in self.records: raise KeyError(rid)
        record = self.records[rid]
        if record["state"] == "pending_approval": record["notification"] = "failed"
        return dict(record)
