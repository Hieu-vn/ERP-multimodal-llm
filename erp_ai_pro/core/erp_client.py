# -*- coding: utf-8 -*-
"""
ERP Client Interface
This module provides a centralized client for interacting with the ERP system's API.
"""

import requests
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ERPClient:
    """
    A client for interacting with a live ERP system.
    This class centralizes all API calls to the ERP.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
        logger.info(f"ERPClient initialized for base URL: {base_url}")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Helper method to make requests to the ERP API."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling ERP API endpoint '{endpoint}': {e}")
            return {"error": str(e)}

    def get_product_stock_level(self, product_id: str) -> Dict[str, Any]:
        """Retrieves the stock level for a specific product."""
        return self._make_request("GET", f"products/{product_id}/stock")

    def get_customer_outstanding_balance(self, customer_id: str) -> Dict[str, Any]:
        """Retrieves the outstanding balance for a customer."""
        return self._make_request("GET", f"customers/{customer_id}/balance")

    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new sales order."""
        return self._make_request("POST", "orders", json=order_data)

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Retrieves the status of a specific order."""
        return self._make_request("GET", f"orders/{order_id}/status")
