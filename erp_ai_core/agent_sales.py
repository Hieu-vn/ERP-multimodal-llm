import os
import requests
from typing import Dict, Any, Optional

# Đọc URL và token API ERP từ biến môi trường
ERP_API_BASE_URL = os.getenv("ERP_API_BASE_URL", "http://localhost:9000/api")
ERP_API_TOKEN = os.getenv("ERP_API_TOKEN", "demo-token")

HEADERS = {
    "Authorization": f"Bearer {ERP_API_TOKEN}",
    "Content-Type": "application/json"
}

def get_product_stock_level(product_id: str) -> Dict[str, Any]:
    """Kiểm tra tồn kho sản phẩm theo product_id."""
    url = f"{ERP_API_BASE_URL}/inventory/stock/{product_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[SalesAgent] Error get_product_stock_level: {e}")
        return {"success": False, "error": str(e)}

def create_order(order_data: Dict[str, Any]) -> Dict[str, Any]:
    """Tạo đơn hàng mới."""
    url = f"{ERP_API_BASE_URL}/sales/orders"
    try:
        resp = requests.post(url, headers=HEADERS, json=order_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[SalesAgent] Error create_order: {e}")
        return {"success": False, "error": str(e)}

def get_order_status(order_id: str) -> Dict[str, Any]:
    """Kiểm tra trạng thái đơn hàng."""
    url = f"{ERP_API_BASE_URL}/sales/orders/{order_id}/status"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[SalesAgent] Error get_order_status: {e}")
        return {"success": False, "error": str(e)}

def get_customer_outstanding_balance(customer_id: str) -> Dict[str, Any]:
    """Kiểm tra công nợ khách hàng."""
    url = f"{ERP_API_BASE_URL}/finance/customers/{customer_id}/outstanding"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[SalesAgent] Error get_customer_outstanding_balance: {e}")
        return {"success": False, "error": str(e)} 