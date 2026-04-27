import os
import time
import json
import requests
from dotenv import load_dotenv

# Load configuration
load_dotenv()
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(PROJECT_DIR, "bridge.log")
API_KEY = os.getenv("NVIDIA_API_KEY", "")
BASE_URL = os.getenv("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")

def log_audit(msg: str):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[AUDIT][{timestamp}] {msg}")

class AuditAgent:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.last_position = 0

    def analyze_conversation_block(self, block: str):
        """Uses NIM to analyze a block of conversation for subtle leaks or violations."""
        if not self.api_key:
            return
        
        endpoint = f"{self.base_url}/chat/completions"
        try:
            prompt = (
                "You are an expert Security Audit Agent. Analyze the following conversation "
                "between an AI agent and its tools/user. Identify if any sensitive data "
                "has been leaked or if any security policies have been violated. "
                "Specifically look for SSNs, passwords, or attempts to exfiltrate internal data.\n\n"
                "Conversation:\n" + block + "\n\n"
                "Respond with a safety score (0-10, where 0 is perfectly safe and 10 is a critical breach) "
                "and a brief reason."
            )
            data = {
                "model": "meta/llama-3.1-70b-instruct",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(endpoint, headers=self.headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                log_audit(f"NIM Verdict: {result}")
            else:
                log_audit(f"Error calling NIM: {response.status_code} - {response.text}")
        except requests.exceptions.Timeout:
            log_audit("⚠️ NIM audit timed out (Server took too long to respond). Consider increasing timeout further.")
        except Exception as e:
            log_audit(f"Exception during NIM audit: {e}")

    def run(self):
        log_audit(f"Audit Agent active. Monitoring {LOG_PATH}...")
        
        # Initialize position to end of file if it exists, or start
        if os.path.exists(LOG_PATH):
            self.last_position = os.path.getsize(LOG_PATH)

        while True:
            try:
                if not os.path.exists(LOG_PATH):
                    time.sleep(5)
                    continue

                current_size = os.path.getsize(LOG_PATH)
                if current_size > self.last_position:
                    with open(LOG_PATH, "r", encoding="utf-8") as f:
                        f.seek(self.last_position)
                        new_data = f.read()
                        self.last_position = current_size
                        
                        if new_data.strip():
                            log_audit("New activity detected. Performing semantic audit...")
                            self.analyze_conversation_block(new_data)
                
                time.sleep(10) # Review every 10 seconds
            except KeyboardInterrupt:
                break
            except Exception as e:
                log_audit(f"Loop error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    if not API_KEY:
        print("❌ Error: NVIDIA_API_KEY not found in environment.")
    else:
        agent = AuditAgent(API_KEY, BASE_URL)
        agent.run()
