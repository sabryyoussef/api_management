import requests
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OdooConfig:
    base_url: str
    db: str
    username: str
    password: str

class OdooClient:
    def __init__(self, config: OdooConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.cookies = None

    def authenticate(self) -> bool:
        """Authenticate with Odoo server and store session cookies."""
        auth_url = f"{self.config.base_url}/web/session/authenticate"
        auth_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": self.config.db,
                "login": self.config.username,
                "password": self.config.password
            },
            "id": None
        }

        try:
            response = self.session.post(auth_url, json=auth_payload)
            response.raise_for_status()
            self.cookies = response.cookies
            logger.info("Authentication successful")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False

    def call_kw(self, model: str, method: str, args: list = None, kwargs: Dict[str, Any] = None) -> Optional[Dict]:
        """Make a call to Odoo's call_kw endpoint."""
        if not self.cookies:
            if not self.authenticate():
                return None

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
            response = self.session.post(endpoint, json=payload, cookies=self.cookies)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API call failed: {str(e)}")
            return None

def main():
    # Configuration
    config = OdooConfig(
        base_url="http://213.136.77.102:8069",
        db="turkishop",
        username="Islam.it@turkieshop.com",
        password="123"
    )

    # Create client
    client = OdooClient(config)

    # Example: search_read on res.partner
    result = client.call_kw(
        model="res.partner",
        method="search_read",
        kwargs={
            "fields": ["name", "email"],
            "limit": 5
        }
    )

    if result:
        logger.info("Search Read Result: %s", result)
    else:
        logger.error("Failed to get results")

if __name__ == "__main__":
    main()
