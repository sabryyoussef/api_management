import requests

# ----------------------
# 1) AUTHENTICATION
# ----------------------
auth_url = "http://213.136.77.102:8069/web/session/authenticate"
headers = {"Content-Type": "application/json"}

auth_payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "db": "turkishop",
        "login": "Islam.it@turkieshop.com",   # or the correct username
        "password": "123"                    # or the correct password or API key
    },
    "id": None
}

# Send authentication request
auth_response = requests.post(auth_url, json=auth_payload, headers=headers)
auth_data = auth_response.json()

if auth_response.status_code == 200 and "result" in auth_data:
    print("Successfully authenticated!")
    # Capture the session cookie
    session_cookies = auth_response.cookies
else:
    print("Authentication failed!")
    print(auth_response.status_code, auth_data)
    exit(1)

# ----------------------
# 2) GET stock.picking
# ----------------------
call_url = "http://213.136.77.102:8069/web/dataset/call_kw"

# We’ll read the first 10 records for demonstration, with a few sample fields
picking_payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "stock.picking",
        "method": "search_read",
        "args": [],
        "kwargs": {
            # Optionally apply a domain if you want to filter (e.g., only 'done' pickings)
            # "domain": [["state", "=", "done"]],
            
            "fields": [
                "name",
                "state",
                "scheduled_date",
                "origin",
                "partner_id"
            ],
            "limit": 10
        }
    },
    "id": None
}

picking_response = requests.post(
    call_url, 
    json=picking_payload, 
    headers=headers, 
    cookies=session_cookies  # Pass the authenticated session cookie
)

if picking_response.status_code == 200:
    picking_data = picking_response.json()
    if "result" in picking_data:
        records = picking_data["result"]
        print("Number of records returned:", len(records))
        for rec in records:
            print(rec)
    else:
        print("Error in response:", picking_data)
else:
    print("HTTP Error:", picking_response.status_code, picking_response.text)
