import jwt
import json
import sys

def create_token(scopes):
    payload = {
        "scope": " ".join(scopes),
        "realm_access": {
            "roles": scopes
        }
    }
    return jwt.encode(payload, "secret", algorithm="HS256")

# Test 1: Authorized tool call (read_file)
token_valid = create_token(["tool:read_file"])
req_valid = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "read_file",
        "arguments": {"path": "test.txt"},
        "metadata": {"token": token_valid}
    }
}

# Test 2: Unauthorized tool call (write_file with only read_file scope)
req_unauthorized = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "write_file",
        "arguments": {"path": "test.txt", "content": "hello"},
        "metadata": {"token": token_valid}
    }
}

# Test 3: System call (list_tools) - should be routed to all/default
req_list = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/list",
    "params": {}
}

print(json.dumps(req_valid))
print(json.dumps(req_unauthorized))
print(json.dumps(req_list))
