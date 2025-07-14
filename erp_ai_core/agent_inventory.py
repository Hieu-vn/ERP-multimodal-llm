import os
import requests
from typing import Dict, Any

ERP_API_BASE_URL = os.getenv("ERP_API_BASE_URL", "http://localhost:9000/api")
ERP_API_TOKEN = os.getenv("ERP_API_TOKEN", "demo-token")

HEADERS = {
    "Authorization": f"Bearer {ERP_API_TOKEN}",
    "Content-Type": "application/json"
}

def get_inventory_overview() -> Dict[str, Any]:
    """Lấy tổng quan tồn kho."""
    url = f"{ERP_API_BASE_URL}/inventory/overview"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[InventoryAgent] Error get_inventory_overview: {e}")
        return {"success": False, "error": str(e)}

def stock_in(stock_data: Dict[str, Any]) -> Dict[str, Any]:
    """Nhập kho."""
    url = f"{ERP_API_BASE_URL}/inventory/stock-in"
    try:
        resp = requests.post(url, headers=HEADERS, json=stock_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[InventoryAgent] Error stock_in: {e}")
        return {"success": False, "error": str(e)}

def stock_out(stock_data: Dict[str, Any]) -> Dict[str, Any]:
    """Xuất kho."""
    url = f"{ERP_API_BASE_URL}/inventory/stock-out"
    try:
        resp = requests.post(url, headers=HEADERS, json=stock_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[InventoryAgent] Error stock_out: {e}")
        return {"success": False, "error": str(e)}

def inventory_check() -> Dict[str, Any]:
    """Kiểm kê kho."""
    url = f"{ERP_API_BASE_URL}/inventory/check"
    try:
        resp = requests.post(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[InventoryAgent] Error inventory_check: {e}")
        return {"success": False, "error": str(e)}

def get_low_stock_alerts() -> Dict[str, Any]:
    """Cảnh báo tồn kho tối thiểu."""
    url = f"{ERP_API_BASE_URL}/inventory/low-stock-alerts"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[InventoryAgent] Error get_low_stock_alerts: {e}")
        return {"success": False, "error": str(e)} 