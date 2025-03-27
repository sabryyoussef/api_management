import logging
import requests
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# Configure logger
logger = logging.getLogger("test_update_delivery_orders")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class DeliveryState(Enum):
    DRAFT = "draft"
    WAITING = "waiting"
    CONFIRMED = "confirmed"
    ASSIGNED = "assigned"
    DONE = "done"
    CANCEL = "cancel"

@dataclass
class OdooConfig:
    base_url: str = "http://213.136.77.102:8069"
    database: str = "turkishop"
    username: str = "Islam.it@turkieshop.com"
    password: str = "123"

class OdooApiError(Exception):
    """Custom exception for Odoo API errors"""
    def __init__(self, message: str, response: Optional[requests.Response] = None):
        self.message = message
        self.response = response
        super().__init__(self.message)

class OdooClient:
    def __init__(self, config: OdooConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Odoo server"""
        login_url = f"{self.config.base_url}/web/session/authenticate"
        auth_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": self.config.database,
                "login": self.config.username,
                "password": self.config.password
            },
            "id": None
        }

        try:
            logger.info("Authenticating to Odoo at %s", login_url)
            response = self.session.post(login_url, json=auth_payload)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("result"):
                raise OdooApiError("Authentication failed", response)
            
            logger.info("Authentication successful")
            
        except requests.exceptions.RequestException as e:
            raise OdooApiError(f"Connection error during authentication: {str(e)}")
        except json.JSONDecodeError as e:
            raise OdooApiError(f"Invalid JSON response during authentication: {str(e)}", response)

    def _call_kw(self, model: str, method: str, args: List = None, kwargs: Dict = None) -> Dict:
        """Make a call to Odoo's call_kw endpoint"""
        endpoint = f"{self.config.base_url}/web/dataset/call_kw"
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

        try:
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                raise OdooApiError(f"API error: {data['error']}", response)
            
            return data
        except requests.exceptions.RequestException as e:
            raise OdooApiError(f"Connection error in API call: {str(e)}")
        except json.JSONDecodeError as e:
            raise OdooApiError(f"Invalid JSON response in API call: {str(e)}", response)

    def validate_delivery_orders(self, order_ids: List[int]) -> bool:
        """Validate if delivery orders exist and are accessible"""
        try:
            data = self._call_kw(
                "stock.picking",
                "search_read",
                kwargs={
                    "domain": [("id", "in", order_ids)],
                    "fields": ["id", "name", "state"]
                }
            )
            
            found_orders = data.get("result", [])
            if len(found_orders) != len(order_ids):
                missing_ids = set(order_ids) - {order["id"] for order in found_orders}
                logger.warning("Some delivery orders not found: %s", missing_ids)
                return False
                
            return True
            
        except Exception as e:
            logger.error("Error validating delivery orders: %s", str(e))
            return False

    def update_delivery_orders(self, order_ids: List[int], state: DeliveryState) -> Dict[str, Any]:
        """Update delivery orders using standard Odoo API"""
        if not order_ids:
            raise ValueError("No delivery order IDs provided")
        
        if not isinstance(state, DeliveryState):
            raise ValueError(f"Invalid state. Must be one of: {[s.value for s in DeliveryState]}")

        # Validate orders exist
        if not self.validate_delivery_orders(order_ids):
            raise OdooApiError("Some delivery orders do not exist or are not accessible")

        try:
            logger.info("Updating delivery orders: %s to state: %s", order_ids, state.value)
            
            # First, check if we need to do any specific actions based on the target state
            if state == DeliveryState.DONE:
                # For 'done' state, we need to validate the transfer
                result = self._call_kw(
                    "stock.picking",
                    "button_validate",
                    args=[order_ids]
                )
            elif state == DeliveryState.CANCEL:
                # For 'cancel' state, we need to cancel the transfer
                result = self._call_kw(
                    "stock.picking",
                    "action_cancel",
                    args=[order_ids]
                )
            else:
                # For other states, we can write directly to the state field
                result = self._call_kw(
                    "stock.picking",
                    "write",
                    args=[order_ids, {"state": state.value}]
                )
            
            # Verify the update
            updated_orders = self._call_kw(
                "stock.picking",
                "search_read",
                kwargs={
                    "domain": [("id", "in", order_ids)],
                    "fields": ["id", "name", "state"]
                }
            )
            
            logger.info("Successfully updated delivery orders")
            return updated_orders
            
        except OdooApiError as e:
            if "UserError" in str(e):
                logger.error("User error while updating orders: %s", str(e))
            raise

def main():
    try:
        # Initialize client with config
        config = OdooConfig()
        client = OdooClient(config)

        # Example delivery order IDs to update
        delivery_order_ids = [66, 67, 70]  # Replace with real IDs
        
        # Update to 'done' state
        result = client.update_delivery_orders(
            order_ids=delivery_order_ids,
            state=DeliveryState.DONE
        )
        
        logger.info("Update result: %s", json.dumps(result, indent=2, ensure_ascii=False))
        
    except OdooApiError as e:
        logger.error("Odoo API Error: %s", e.message)
        if e.response:
            logger.debug("Response details: %s", e.response.text)
    except ValueError as e:
        logger.error("Validation Error: %s", str(e))
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))

if __name__ == "__main__":
    main()
