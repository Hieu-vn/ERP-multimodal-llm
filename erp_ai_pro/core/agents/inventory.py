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

# Định nghĩa Input và Output Schema cho GetInventoryOverviewTool
class GetInventoryOverviewInput(BaseModel):
    pass # Không có input

class GetInventoryOverviewOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The inventory overview data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class GetInventoryOverviewTool:
    """Lấy tổng quan tồn kho."""
    input_schema = GetInventoryOverviewInput
    output_schema = GetInventoryOverviewOutput

    def run(self) -> GetInventoryOverviewOutput:
        url = f"{ERP_API_BASE_URL}/inventory/overview"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            return GetInventoryOverviewOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[InventoryAgent] Error get_inventory_overview: {e}")
            return GetInventoryOverviewOutput(success=False, error=str(e))

class StockInInput(BaseModel):
    stock_data: Dict[str, Any] = Field(description="The data for the stock-in operation.")

class StockInOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The stock-in data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class StockInTool:
    """Nhập kho."""
    input_schema = StockInInput
    output_schema = StockInOutput

    def run(self, stock_data: Dict[str, Any]) -> StockInOutput:
        url = f"{ERP_API_BASE_URL}/inventory/stock-in"
        try:
            resp = requests.post(url, headers=HEADERS, json=stock_data, timeout=15)
            resp.raise_for_status()
            return StockInOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[InventoryAgent] Error stock_in: {e}")
            return StockInOutput(success=False, error=str(e))

class StockOutInput(BaseModel):
    stock_data: Dict[str, Any] = Field(description="The data for the stock-out operation.")

class StockOutOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The stock-out data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class StockOutTool:
    """Xuất kho."""
    input_schema = StockOutInput
    output_schema = StockOutOutput

    def run(self, stock_data: Dict[str, Any]) -> StockOutOutput:
        url = f"{ERP_API_BASE_URL}/inventory/stock-out"
        try:
            resp = requests.post(url, headers=HEADERS, json=stock_data, timeout=15)
            resp.raise_for_status()
            return StockOutOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[InventoryAgent] Error stock_out: {e}")
            return StockOutOutput(success=False, error=str(e))

class InventoryCheckInput(BaseModel):
    pass # Không có input

class InventoryCheckOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The inventory check data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class InventoryCheckTool:
    """Kiểm kê kho."""
    input_schema = InventoryCheckInput
    output_schema = InventoryCheckOutput

    def run(self) -> InventoryCheckOutput:
        url = f"{ERP_API_BASE_URL}/inventory/check"
        try:
            resp = requests.post(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            return InventoryCheckOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[InventoryAgent] Error inventory_check: {e}")
            return InventoryCheckOutput(success=False, error=str(e))

class GetLowStockAlertsInput(BaseModel):
    pass # Không có input

class GetLowStockAlertsOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The low stock alerts data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class GetLowStockAlertsTool:
    """Cảnh báo tồn kho tối thiểu."""
    input_schema = GetLowStockAlertsInput
    output_schema = GetLowStockAlertsOutput

    def run(self) -> GetLowStockAlertsOutput:
        url = f"{ERP_API_BASE_URL}/inventory/low-stock-alerts"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            return GetLowStockAlertsOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[InventoryAgent] Error get_low_stock_alerts: {e}")
            return GetLowStockAlertsOutput(success=False, error=str(e)) 