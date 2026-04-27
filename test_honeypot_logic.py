import os
import json
import unittest
from unittest.mock import MagicMock, patch
from bridge import FraudDetectionEngine

class TestHoneypotLogic(unittest.TestCase):
    def setUp(self):
        # Initialize engine with learning_mode=False to ensure enforcements trigger
        self.engine = FraudDetectionEngine(learning_mode=False)
        self.spiffe_id = "spiffe://runtime-shield/agent-alpha"

    def test_honeypot_quarantine(self):
        print(f"🕵️ Testing Honeypot Quarantine for {self.spiffe_id}...")
        
        # Mock a decision that originated from the honeypot rule
        mock_decision = MagicMock()
        mock_decision.action.value = "deny"
        mock_decision.name = "block-honeypots"
        mock_decision.reason = "Honeypot Triggered"
        mock_decision.severity.value = "critical"

        # First attempt: should trigger penalty
        blocked, action, reason, severity = self.engine.analyze(
            agent=self.spiffe_id,
            decision=mock_decision,
            tool_name="get_system_config",
            tool_args={"component": "kernel"}
        )

        print(f"Score after one hit: {self.engine.agent_risk_scores[self.spiffe_id]}")
        
        self.assertTrue(blocked)
        self.assertEqual(action, "deny")
        self.assertIn("QUARANTINE", reason)
        self.assertEqual(self.engine.agent_risk_scores[self.spiffe_id], 100)
        print("✅ Quarantine successful: Risk score reached 100 instantly.")

    def test_identity_isolation(self):
        print("🧪 Testing Identity Isolation between multiple agents...")
        
        agent_a = "spiffe://runtime-shield/agent-a"
        agent_b = "spiffe://runtime-shield/agent-b"

        # Agent A hits a honeypot
        mock_decision = MagicMock()
        mock_decision.action.value = "deny"
        mock_decision.name = "block-honeypots"
        
        self.engine.analyze(agent=agent_a, decision=mock_decision, tool_name="fetch_internal_db")
        
        # Verify Agent A is blocked
        self.assertEqual(self.engine.agent_risk_scores[agent_a], 100)
        
        # Verify Agent B risk is still 0
        self.assertEqual(self.engine.agent_risk_scores.get(agent_b, 0), 0)
        print("✅ Identity Isolation successful: Only the malicious agent was blacklisted.")

if __name__ == "__main__":
    unittest.main()
