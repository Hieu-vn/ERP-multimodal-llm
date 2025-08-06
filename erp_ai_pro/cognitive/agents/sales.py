import os
import requests
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# Đọc URL và token API ERP từ biến môi trường
ERP_API_BASE_URL = os.getenv("ERP_API_BASE_URL", "http://localhost:9000/api")
ERP_API_TOKEN = os.getenv("ERP_API_TOKEN", "demo-token")

HEADERS = {
    "Authorization": f"Bearer {ERP_API_TOKEN}",
    "Content-Type": "application/json"
}

# Định nghĩa Input và Output Schema cho GetProductStockLevelTool
class GetProductStockLevelInput(BaseModel):
    product_id: str = Field(description="The ID of the product to check stock for.")

class GetProductStockLevelOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The stock data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class GetProductStockLevelTool:
    """Kiểm tra tồn kho sản phẩm theo product_id."""
    input_schema = GetProductStockLevelInput
    output_schema = GetProductStockLevelOutput

    def run(self, product_id: str) -> GetProductStockLevelOutput:
        url = f"{ERP_API_BASE_URL}/inventory/stock/{product_id}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            return GetProductStockLevelOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[SalesAgent] Error get_product_stock_level: {e}")
            return GetProductStockLevelOutput(success=False, error=str(e))

class CreateOrderInput(BaseModel):
    order_data: Dict[str, Any] = Field(description="The data for the new order.")

class CreateOrderOutput(BaseModel):
    success: bool = Field(description="True if the order was created successfully, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The created order data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class CreateOrderTool:
    """Tạo đơn hàng mới."""
    input_schema = CreateOrderInput
    output_schema = CreateOrderOutput

    def run(self, order_data: Dict[str, Any]) -> CreateOrderOutput:
        url = f"{ERP_API_BASE_URL}/sales/orders"
        try:
            resp = requests.post(url, headers=HEADERS, json=order_data, timeout=15)
            resp.raise_for_status()
            return CreateOrderOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[SalesAgent] Error create_order: {e}")
            return CreateOrderOutput(success=False, error=str(e))

class GetOrderStatusInput(BaseModel):
    order_id: str = Field(description="The ID of the order to check status for.")

class GetOrderStatusOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The order status data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class GetOrderStatusTool:
    """Kiểm tra trạng thái đơn hàng."""
    input_schema = GetOrderStatusInput
    output_schema = GetOrderStatusOutput

    def run(self, order_id: str) -> GetOrderStatusOutput:
        url = f"{ERP_API_BASE_URL}/sales/orders/{order_id}/status"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            return GetOrderStatusOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[SalesAgent] Error get_order_status: {e}")
            return GetOrderStatusOutput(success=False, error=str(e))

class GetCustomerOutstandingBalanceInput(BaseModel):
    customer_id: str = Field(description="The ID of the customer to check outstanding balance for.")

class GetCustomerOutstandingBalanceOutput(BaseModel):
    success: bool = Field(description="True if the operation was successful, False otherwise.")
    data: Optional[Dict[str, Any]] = Field(None, description="The outstanding balance data if successful.")
    error: Optional[str] = Field(None, description="Error message if the operation failed.")

class GetCustomerOutstandingBalanceTool:
    """Kiểm tra công nợ khách hàng."""
    input_schema = GetCustomerOutstandingBalanceInput
    output_schema = GetCustomerOutstandingBalanceOutput

    def run(self, customer_id: str) -> GetCustomerOutstandingBalanceOutput:
        url = f"{ERP_API_BASE_URL}/finance/customers/{customer_id}/outstanding"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            return GetCustomerOutstandingBalanceOutput(success=True, data=resp.json())
        except Exception as e:
            print(f"[SalesAgent] Error get_customer_outstanding_balance: {e}")
            return GetCustomerOutstandingBalanceOutput(success=False, error=str(e)) 