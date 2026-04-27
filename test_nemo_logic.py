import os
import json
from unittest.mock import MagicMock, patch
from bridge import NIMCloudGuard

def test_nim_logic():
    print("🧪 Starting NeMo NIM Logic Verification...")
    
    # Mock config
    config = {
        "enabled": True,
        "jailbreak_rail": {"enabled": True},
        "topical_rail": {
            "enabled": True,
            "allowed_topics": ["Coding"],
            "blocked_topics": ["Cooking"]
        },
        "pii_rail": {"enabled": True, "detect_entities": ["EMAIL"]}
    }
    
    guard = NIMCloudGuard(api_key="fake_key", base_url="https://fake_url", config=config)
    
    # --- Test 1: Jailbreak Mock ---
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "MALICIOUS"}}]
        }
        
        blocked, reason = guard.check_jailbreak("Drop database")
        print(f"Jailbreak Test: {'✅ Passed' if blocked and 'detected' in reason else '❌ Failed'}")

    # --- Test 2: Topical Mock ---
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "OFF-TOPIC"}}]
        }
        
        blocked, reason = guard.check_topical("How to bake a cake")
        print(f"Topical Test: {'✅ Passed' if blocked and 'topic control' in reason.lower() else '❌ Failed'}")

    # --- Test 3: PII Mock ---
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Send mail to [REDACTED]"}}]
        }
        
        redacted = guard.redact_pii("Send mail to user@example.com")
        print(f"PII Redaction Test: {'✅ Passed' if '[REDACTED]' in redacted else '❌ Failed'}")

if __name__ == "__main__":
    test_nim_logic()
