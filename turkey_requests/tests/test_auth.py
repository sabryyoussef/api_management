import requests

url = "http://213.136.77.102:8069/web/session/authenticate"
headers = {"Content-Type": "application/json"}

payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "db": "turkishop",
        "login": "Islam.it@turkieshop.com",  # use your exact username
        "password": "123"                   # use your password here
    },
    "id": None
}

response = requests.post(url, json=payload, headers=headers)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())
