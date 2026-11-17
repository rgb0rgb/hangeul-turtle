import unittest
from insider.behavior import analyze
from insider.approval import ApprovalEngine
from insider.audit import AuditLog
from insider.red_scenarios import generate
from evaluator.insider_evaluation import evaluate_holdout

class InsiderControlsTests(unittest.TestCase):
    def test_super_admin_has_no_exception_and_self_approval_fails(self):
        event = generate("insider-admin-export", 11)
        decision = analyze(event)
        self.assertEqual(decision["decision"], "pending_approval")
        engine = ApprovalEngine(); record = engine.submit({"request_id":"r1","requester_id":event["user_id"]}, decision, 1000)
        with self.assertRaises(PermissionError): engine.decide("r1", event["user_id"], "security_officer", True, 1001)
        self.assertEqual(record["state"], "pending_approval")

    def test_notification_failure_and_expiry_fail_closed(self):
        event = generate("insider-exfil", 12); decision = analyze(event); engine = ApprovalEngine(ttl_seconds=5)
        engine.submit({"request_id":"r2","requester_id":event["user_id"]}, decision, 1000)
        engine.notification_failed("r2")
        self.assertEqual(engine.records["r2"]["state"], "pending_approval")
        with self.assertRaises(ValueError): engine.decide("r2", "sec-1", "security_officer", True, 1006)
        self.assertEqual(engine.records["r2"]["state"], "expired")

    def test_audit_chain_detects_tampering_without_secrets(self):
        audit = AuditLog(); audit.append({"request_id":"r3","token":"never-store","state":"pending_approval"})
        self.assertNotIn("token", audit.records[0]); self.assertTrue(audit.verify())
        audit.records[0]["state"] = "approved"
        self.assertFalse(audit.verify())

    def test_holdout_is_separate_and_normal_batch_is_not_false_positive(self):
        result = evaluate_holdout(100)
        self.assertTrue(result["development"]["audit_complete"])
        self.assertTrue(result["holdout"]["audit_complete"])
        self.assertEqual(result["holdout"]["false_positive_rate"], 0.0)
        self.assertEqual(result["holdout"]["detection_rate"], 1.0)
        self.assertFalse(result["policy_promotion"]["promoted"])

if __name__ == "__main__": unittest.main()
