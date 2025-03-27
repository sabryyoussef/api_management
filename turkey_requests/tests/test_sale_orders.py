import logging
import requests
import json

# -------------------------------------------------------------------
# Configure the logger
# -------------------------------------------------------------------
logger = logging.getLogger("test_sale_orders")
logger.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Optional: Set a more detailed format for the logs
formatter = logging.Formatter(
    "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def call_kw(session, url, model, method, args=None, kwargs=None):
    """Helper function to make Odoo API calls"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": model,
            "method": method,
            "args": args or [],
            "kwargs": kwargs or {}
        },
        "id": None
    }
    
    response = session.post(url, json=payload, headers=headers)
    return response.json()

def main():
    # -------------------------------------------------------------------
    # STEP 1: Authenticate to get session cookies
    # -------------------------------------------------------------------
    base_url = "http://213.136.77.102:8069"
    login_url = f"{base_url}/web/session/authenticate"
    api_url = f"{base_url}/web/dataset/call_kw"
    
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})

    auth_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "db": "turkishop",
            "login": "Islam.it@turkieshop.com",
            "password": "123"
        },
        "id": None
    }

    logger.info("Authenticating to Odoo at %s", login_url)
    session_resp = session.post(login_url, json=auth_payload)
    logger.info("Received response from authentication endpoint with status code %s", session_resp.status_code)

    try:
        session_data = session_resp.json()
        if not session_data.get("result"):
            logger.error("Authentication failed. Response: %s", session_data)
            return
        logger.info("Authenticated successfully!")
    except json.JSONDecodeError:
        logger.error("Authentication response is not valid JSON. Response text: %s", session_resp.text)
        return

    # -------------------------------------------------------------------
    # STEP 2: Get a valid product and partner
    # -------------------------------------------------------------------
    logger.info("Fetching available products...")
    product_result = call_kw(
        session,
        api_url,
        "product.product",
        "search_read",
        kwargs={
            "fields": ["id", "name", "list_price"],
            "domain": [("sale_ok", "=", True)],
            "limit": 1
        }
    )

    if not product_result.get("result"):
        logger.error("Failed to fetch products: %s", product_result)
        return

    products = product_result["result"]
    if not products:
        logger.error("No products found!")
        return

    product = products[0]
    logger.info("Found product: %s", product)

    logger.info("Fetching available partners...")
    partner_result = call_kw(
        session,
        api_url,
        "res.partner",
        "search_read",
        kwargs={
            "fields": ["id", "name"],
            "domain": [("customer_rank", ">", 0)],
            "limit": 1
        }
    )

    if not partner_result.get("result"):
        logger.error("Failed to fetch partners: %s", partner_result)
        return

    partners = partner_result["result"]
    if not partners:
        logger.error("No partners found!")
        return

    partner = partners[0]
    logger.info("Found partner: %s", partner)

    # -------------------------------------------------------------------
    # STEP 3: Create sale order
    # -------------------------------------------------------------------
    logger.info("Creating sale order...")
    create_result = call_kw(
        session,
        api_url,
        "sale.order",
        "create",
        args=[{
            "partner_id": partner["id"],
            "order_line": [(0, 0, {
                "product_id": product["id"],
                "product_uom_qty": 1.0,
                "price_unit": product["list_price"]
            })]
        }]
    )

    if create_result.get("error"):
        logger.error("Failed to create sale order: %s", create_result["error"])
    else:
        logger.info("Sale order created successfully: %s", create_result["result"])

if __name__ == "__main__":
    main()
