"""Hash-chained, redacted audit records for synthetic experiments."""
import hashlib
import json

class AuditLog:
    def __init__(self): self.records = []
    def append(self, record):
        safe = {k: v for k, v in record.items() if k not in {"token", "password", "customer_raw"}}
        safe["previous_hash"] = self.records[-1]["hash"] if self.records else "0" * 64
        payload = json.dumps(safe, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        safe["hash"] = hashlib.sha256(payload.encode()).hexdigest()
        self.records.append(safe)
        return dict(safe)
    def verify(self):
        previous = "0" * 64
        for item in self.records:
            check = dict(item); actual = check.pop("hash")
            if check.get("previous_hash") != previous: return False
            expected = hashlib.sha256(json.dumps(check, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if expected != actual: return False
            previous = actual
        return True
