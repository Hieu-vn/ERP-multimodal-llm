import os
import requests
from typing import Dict, Any

ERP_API_BASE_URL = os.getenv("ERP_API_BASE_URL", "http://localhost:9000/api")
ERP_API_TOKEN = os.getenv("ERP_API_TOKEN", "demo-token")

HEADERS = {
    "Authorization": f"Bearer {ERP_API_TOKEN}",
    "Content-Type": "application/json"
}

def get_revenue_report(params: Dict[str, Any]) -> Dict[str, Any]:
    """Lấy báo cáo doanh thu theo tham số (thời gian, kênh, v.v.)."""
    url = f"{ERP_API_BASE_URL}/finance/revenue-report"
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[FinanceAgent] Error get_revenue_report: {e}")
        return {"success": False, "error": str(e)}

def get_expense_report(params: Dict[str, Any]) -> Dict[str, Any]:
    """Lấy báo cáo chi phí theo tham số."""
    url = f"{ERP_API_BASE_URL}/finance/expense-report"
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[FinanceAgent] Error get_expense_report: {e}")
        return {"success": False, "error": str(e)}

def get_customer_debt(customer_id: str) -> Dict[str, Any]:
    """Kiểm tra công nợ khách hàng."""
    url = f"{ERP_API_BASE_URL}/finance/customers/{customer_id}/debt"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[FinanceAgent] Error get_customer_debt: {e}")
        return {"success": False, "error": str(e)}

def create_receipt(receipt_data: Dict[str, Any]) -> Dict[str, Any]:
    """Lập phiếu thu."""
    url = f"{ERP_API_BASE_URL}/finance/receipts"
    try:
        resp = requests.post(url, headers=HEADERS, json=receipt_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[FinanceAgent] Error create_receipt: {e}")
        return {"success": False, "error": str(e)}

def create_payment(payment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Lập phiếu chi."""
    url = f"{ERP_API_BASE_URL}/finance/payments"
    try:
        resp = requests.post(url, headers=HEADERS, json=payment_data, timeout=15)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        print(f"[FinanceAgent] Error create_payment: {e}")
        return {"success": False, "error": str(e)} 