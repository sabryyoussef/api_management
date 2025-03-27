import requests

# ----------------------
# Step 1) AUTHENTICATION
# ----------------------
auth_url = "http://213.136.77.102:8069/web/session/authenticate"
headers = {"Content-Type": "application/json"}

auth_payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "db": "turkishop",
        "login": "Islam.it@turkieshop.com",  # or correct username
        "password": "123"                   # or correct password / API key
    },
    "id": None
}

auth_response = requests.post(auth_url, json=auth_payload, headers=headers)
auth_data = auth_response.json()

if auth_response.status_code == 200 and "result" in auth_data:
    print("Successfully authenticated!")
    session_cookies = auth_response.cookies
else:
    print("Authentication failed!")
    print(auth_response.status_code, auth_data)
    exit(1)

# ------------------------------------------------
# Step 2) READ THE 'stock.picking' RECORD WITH ID 59
# ------------------------------------------------
call_url = "http://213.136.77.102:8069/web/dataset/call_kw"

# We'll use the "read" method to fetch all details of a single record.
picking_id = 59

read_payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "stock.picking",
        "method": "read",
        "args": [[picking_id]],
        "kwargs": {
            # optional "fields": ["field1", "field2"] 
            # If you omit fields, Odoo usually returns ALL fields,
            # which can be quite a lot. 
            # If you only want certain fields, uncomment and specify them:
            #
            # "fields": [
            #     "name",
            #     "state",
            #     "origin",
            #     "picking_type_id",
            #     "move_lines",
            #     "partner_id",
            #     "scheduled_date",
            #     "location_id",
            #     "location_dest_id"
            # ]
        }
    },
    "id": None
}

read_response = requests.post(call_url, json=read_payload, headers=headers, cookies=session_cookies)
read_data = read_response.json()

if read_response.status_code == 200 and "result" in read_data:
    picking_records = read_data["result"]
    if picking_records:
        picking_record = picking_records[0]  # read() returns a list; we requested only one ID
        print("Details for stock.picking ID =", picking_id, ":")
        for field_name, field_value in picking_record.items():
            print(f"{field_name}: {field_value}")
    else:
        print(f"No picking record found with ID {picking_id}")
else:
    print("Error retrieving picking record:")
    print(read_response.status_code, read_data)
