"""Fail-closed I/O gate for a temporary sandbox resource.

This is deliberately not a host firewall or OS-wide access-control adapter.
The constructor requires a temporary-directory root and all operations are
path-confined. Independent observers record the actual open/write result.
"""
import hashlib
import hmac
import secrets
import time
from pathlib import Path

class EnforcementError(Exception): pass

class SandboxEnforcementGate:
    def __init__(self, sandbox_root, policy_version="enforce-v1", clock=None):
        self.root = Path(sandbox_root).resolve()
        if not self.root.is_dir() or not str(self.root).startswith("/tmp/"):
            raise ValueError("enforcement is restricted to a temporary directory")
        self.policy_version = policy_version
        self.clock = clock or time.time
        self.requests = {}
        self.observations = []

    def _inside(self, relative_path):
        target = (self.root / relative_path).resolve()
        if target != self.root and self.root not in target.parents:
            raise EnforcementError("resource path outside sandbox")
        return target

    def request(self, *, event_id, resource, operation, requester_id, expires_in=300):
        if operation not in {"read", "write"} or not resource or not event_id or not requester_id:
            raise ValueError("invalid enforcement request")
        target = self._inside(resource)
        if expires_in <= 0 or expires_in > 3600: raise ValueError("invalid expiry")
        token = secrets.token_urlsafe(24)
        request_id = "enf-" + secrets.token_hex(12)
        self.requests[request_id] = {"event_id":event_id, "resource":str(target), "operation":operation,
            "requester_id":requester_id, "state":"pending_approval", "expires_at":self.clock()+expires_in,
            "token_hash":hashlib.sha256(token.encode()).hexdigest(), "token_used":False,
            "policy_version":self.policy_version, "rollback":False}
        return {"request_id":request_id, "state":"pending_approval", "expires_at":self.requests[request_id]["expires_at"],
                "approval_token":token, "resource":resource, "operation":operation}

    def decide(self, request_id, *, approver_id, approver_role, approve, token):
        record = self.requests[request_id]
        if self.clock() >= record["expires_at"]: record["state"] = "expired"
        if record["state"] != "pending_approval": raise EnforcementError("request is not pending")
        if approver_role != "security_officer" or approver_id == record["requester_id"]:
            raise PermissionError("independent approval required")
        if record["token_used"] or not hmac.compare_digest(record["token_hash"], hashlib.sha256(token.encode()).hexdigest()):
            raise PermissionError("invalid or reused approval token")
        record["token_used"] = True
        record["state"] = "approved" if approve else "rejected"
        record["approver_id"] = approver_id
        return {"request_id":request_id, "state":record["state"], "policy_version":record["policy_version"]}

    def rollback(self, request_id, actor_id):
        record = self.requests[request_id]
        record["rollback"] = True; record["state"] = "rejected"; record["rollback_actor"] = actor_id
        return {"request_id":request_id, "state":"rejected", "rollback":True}

    def _authorize(self, request_id, relative_path, operation):
        record = self.requests[request_id]
        target = self._inside(relative_path)
        if self.clock() >= record["expires_at"] and record["state"] == "approved": record["state"] = "expired"
        allowed = record["state"] == "approved" and not record["rollback"] and record["operation"] == operation and target == Path(record["resource"])
        self.observations.append({"request_id":request_id, "event_id":record["event_id"], "operation":operation,
                                  "resource":relative_path, "state":record["state"], "allowed":allowed,
                                  "actual_io":False, "policy_version":record["policy_version"]})
        if not allowed: raise EnforcementError("I/O denied by independent enforcement gate")
        return target

    def read_text(self, request_id, relative_path):
        target = self._authorize(request_id, relative_path, "read")
        value = target.read_text(encoding="utf-8")
        self.observations[-1].update(actual_io=True, result="read_success")
        return value

    def write_text(self, request_id, relative_path, value):
        if not isinstance(value, str) or len(value) > 4096: raise ValueError("bounded synthetic write only")
        target = self._authorize(request_id, relative_path, "write")
        target.write_text(value, encoding="utf-8")
        self.observations[-1].update(actual_io=True, result="write_success")
        return {"written":True, "content_recorded":False}
