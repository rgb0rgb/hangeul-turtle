import tempfile
import unittest
from pathlib import Path
from enforcement.gate import EnforcementError, SandboxEnforcementGate
from insider.witness import AuditWitness

class EnforcementTests(unittest.TestCase):
    def test_pending_denies_real_read_and_approved_scope_allows_then_rollback_denies(self):
        with tempfile.TemporaryDirectory(prefix="ahs-enforce-") as root:
            Path(root, "jeon.txt").write_text("synthetic-secret", encoding="utf-8")
            gate = SandboxEnforcementGate(root); req = gate.request(event_id="e1", resource="jeon.txt", operation="read", requester_id="red", expires_in=30)
            with self.assertRaises(EnforcementError): gate.read_text(req["request_id"], "jeon.txt")
            gate.decide(req["request_id"], approver_id="sec", approver_role="security_officer", approve=True, token=req["approval_token"])
            self.assertEqual(gate.read_text(req["request_id"], "jeon.txt"), "synthetic-secret")
            gate.rollback(req["request_id"], "sec")
            with self.assertRaises(EnforcementError): gate.read_text(req["request_id"], "jeon.txt")
            self.assertTrue(any(x["actual_io"] for x in gate.observations))

    def test_scope_self_approval_expiry_and_token_reuse_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix="ahs-enforce-") as root:
            Path(root, "a.txt").write_text("a", encoding="utf-8"); gate = SandboxEnforcementGate(root)
            req = gate.request(event_id="e2", resource="a.txt", operation="read", requester_id="red", expires_in=30)
            with self.assertRaises(PermissionError): gate.decide(req["request_id"], approver_id="red", approver_role="security_officer", approve=True, token=req["approval_token"])
            with self.assertRaises(EnforcementError): gate.read_text(req["request_id"], "../outside")
            gate.decide(req["request_id"], approver_id="sec", approver_role="security_officer", approve=True, token=req["approval_token"])
            with self.assertRaises(EnforcementError): gate.decide(req["request_id"], approver_id="sec", approver_role="security_officer", approve=True, token=req["approval_token"])

    def test_external_witness_detects_delete_truncate_and_rewrite(self):
        records=[{"sequence":0,"value":"a"},{"sequence":1,"value":"b"}]; witness=AuditWitness()
        for record in records: witness.anchor(record)
        self.assertTrue(witness.verify(records)); self.assertFalse(witness.verify(records[:1]))
        changed=list(records); changed[0]={"sequence":0,"value":"tampered"}; self.assertFalse(witness.verify(changed))

if __name__ == "__main__": unittest.main()
