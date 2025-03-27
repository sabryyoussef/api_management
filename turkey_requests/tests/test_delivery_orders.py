import requests
import json

# -----------------------------------------------------------------
# STEP 1: Authenticate
# -----------------------------------------------------------------
login_url = "http://213.136.77.102:8069/web/session/authenticate"
headers = {"Content-Type": "application/json"}

auth_payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "db": "turkishop",
        "login": "Islam.it@turkieshop.com",  # or the correct username
        "password": "123"                   # or the correct password/API key
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
    print("Status code:", session_resp.status_code)
    print("Response:", session_resp.text)
    exit(1)

# -----------------------------------------------------------------
# STEP 2: Call the custom route /api/delivery_orders
# -----------------------------------------------------------------
test_url = "http://213.136.77.102:8069/api/delivery_orders"

response = requests.get(test_url, cookies=session_cookies)
print("Response status code:", response.status_code)

try:
    response_json = response.json()
    print("Response JSON:", json.dumps(response_json, indent=2, ensure_ascii=False))
except json.JSONDecodeError:
    print("Non-JSON response:", response.text)
