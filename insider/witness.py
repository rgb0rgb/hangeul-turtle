"""Independent witness anchors for deletion/truncation detection."""
import hashlib
import json

class AuditWitness:
    def __init__(self): self.anchors = []
    def anchor(self, audit_record):
        payload = json.dumps(audit_record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(payload.encode()).hexdigest()
        self.anchors.append({"sequence":len(self.anchors), "hash":digest})
        return self.anchors[-1].copy()
    def verify(self, audit_records):
        if len(audit_records) != len(self.anchors): return False
        for anchor, record in zip(self.anchors, audit_records):
            payload = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            if anchor["hash"] != hashlib.sha256(payload.encode()).hexdigest(): return False
        return True
