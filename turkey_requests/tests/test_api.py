import requests
import json

# -------------------------------------------------------------------
# Step 1: Authenticate to get session cookies
# -------------------------------------------------------------------
login_url = "http://213.136.77.102:8069/web/session/authenticate"
headers = {"Content-Type": "application/json"}

# Update these with your own credentials
auth_payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "db": "turkishop",
        "login": "Islam.it@turkieshop.com",  # or your own username
        "password": "123"                   # or your own password / API key
    },
    "id": None
}

session_resp = requests.post(login_url, json=auth_payload, headers=headers)
session_data = session_resp.json()

if session_resp.status_code == 200 and "result" in session_data:
    print("Authenticated successfully!")
    session_cookies = session_resp.cookies
else:
    print("Authentication failed.")
    print(session_resp.text)
    exit(1)

# -------------------------------------------------------------------
# Step 2: Make a GET request to our custom endpoint /api/test
# -------------------------------------------------------------------
test_url = "http://213.136.77.102:8069/api/test"

response = requests.get(test_url, cookies=session_cookies)
print("Response status code:", response.status_code)

try:
    print("Response JSON:", response.json())
except json.JSONDecodeError:
    print("Non-JSON response:", response.text)
