import os
import requests
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

ERP_API_BASE_URL = os.getenv("ERP_API_BASE_URL", "http://localhost:9000/api")
ERP_API_TOKEN = os.getenv("ERP_API_TOKEN", "demo-token")

HEADERS = {
    "Authorization": f"Bearer {ERP_API_TOKEN}",
    "Content-Type": "application/json"
}

# Định nghĩa Input và Output Schema cho GetRevenueReportTool
class GetRevenueReportInput(BaseModel):
    params: Dict[str, Any] = Field(description="Parameters for the revenue report (e.g., time range, channel).")

class GetRevenueReportOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The revenue report data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class GetRevenueReportTool:
    """Lấy báo cáo doanh thu theo tham số (thời gian, kênh, v.v.)."""
    input_schema = GetRevenueReportInput
    output_schema = GetRevenueReportOutput

    def run(self, params: Dict[str, Any]) -> GetRevenueReportOutput:
        url = f"{ERP_API_BASE_URL}/finance/revenue-report"
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
            resp.raise_for_status()
            return GetRevenueReportOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[FinanceAgent] Error get_revenue_report: {e}")
            return GetRevenueReportOutput(success=False, error=str(e))

class GetExpenseReportInput(BaseModel):
    params: Dict[str, Any] = Field(description="Parameters for the expense report.")

class GetExpenseReportOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The expense report data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class GetExpenseReportTool:
    """Lấy báo cáo chi phí theo tham số."""
    input_schema = GetExpenseReportInput
    output_schema = GetExpenseReportOutput

    def run(self, params: Dict[str, Any]) -> GetExpenseReportOutput:
        url = f"{ERP_API_BASE_URL}/finance/expense-report"
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
            resp.raise_for_status()
            return GetExpenseReportOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[FinanceAgent] Error get_expense_report: {e}")
            return GetExpenseReportOutput(success=False, error=str(e))

class GetCustomerDebtInput(BaseModel):
    customer_id: str = Field(description="The ID of the customer to check debt for.")

class GetCustomerDebtOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The customer debt data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class GetCustomerDebtTool:
    """Kiểm tra công nợ khách hàng."""
    input_schema = GetCustomerDebtInput
    output_schema = GetCustomerDebtOutput

    def run(self, customer_id: str) -> GetCustomerDebtOutput:
        url = f"{ERP_API_BASE_URL}/finance/customers/{customer_id}/debt"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            return GetCustomerDebtOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[FinanceAgent] Error get_customer_debt: {e}")
            return GetCustomerDebtOutput(success=False, error=str(e))

class CreateReceiptInput(BaseModel):
    receipt_data: Dict[str, Any] = Field(description="The data for the new receipt.")

class CreateReceiptOutput(BaseModel):
    success: bool = Field(description="True if the receipt was created successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The created receipt data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class CreateReceiptTool:
    """Lập phiếu thu."""
    input_schema = CreateReceiptInput
    output_schema = CreateReceiptOutput

    def run(self, receipt_data: Dict[str, Any]) -> CreateReceiptOutput:
        url = f"{ERP_API_BASE_URL}/finance/receipts"
        try:
            resp = requests.post(url, headers=HEADERS, json=receipt_data, timeout=15)
            resp.raise_for_status()
            return CreateReceiptOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[FinanceAgent] Error create_receipt: {e}")
            return CreateReceiptOutput(success=False, error=str(e))

class CreatePaymentInput(BaseModel):
    payment_data: Dict[str, Any] = Field(description="The data for the new payment.")

class CreatePaymentOutput(BaseModel):
    success: bool = Field(description="True if the payment was created successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The created payment data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class CreatePaymentTool:
    """Lập phiếu chi."""
    input_schema = CreatePaymentInput
    output_schema = CreatePaymentOutput

    def run(self, payment_data: Dict[str, Any]) -> CreatePaymentOutput:
        url = f"{ERP_API_BASE_URL}/finance/payments"
        try:
            resp = requests.post(url, headers=HEADERS, json=payment_data, timeout=15)
            resp.raise_for_status()
            return CreatePaymentOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[FinanceAgent] Error create_payment: {e}")
            return CreatePaymentOutput(success=False, error=str(e)) 