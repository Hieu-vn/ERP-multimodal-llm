# 📡 API Documentation

## Tổng quan API

ERP AI Pro Version cung cấp RESTful API được xây dựng với FastAPI, hỗ trợ async processing và real-time interaction với hệ thống ERP thông qua natural language queries.

## 🌐 Base Information

- **Base URL**: `http://localhost:8000` (development)
- **API Version**: v1.0.0
- **Content-Type**: `application/json`
- **Authentication**: Bearer Token
- **Rate Limiting**: 100 requests/minute per user

## 📋 Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/query` | Process natural language query | ✅ |
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/docs` | Interactive API documentation | ❌ |
| `GET` | `/redoc` | Alternative API documentation | ❌ |

## 🔥 Core Endpoints

### 1. Query Endpoint

**Xử lý truy vấn ngôn ngữ tự nhiên và trả về kết quả AI-powered**

```http
POST /query
```

#### Request Body

```json
{
  "role": "string",
  "question": "string"
}
```

#### Parameters

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `role` | string | ✅ | User role trong hệ thống ERP | `"finance_manager"` |
| `question` | string | ✅ | Câu hỏi bằng tiếng Việt tự nhiên | `"Doanh thu tháng này như thế nào?"` |

#### Supported Roles

```json
[
  "admin",
  "finance_manager", 
  "sales_manager",
  "sales_rep",
  "warehouse_manager",
  "inventory_clerk",
  "customer_service",
  "analyst"
]
```

#### Response Format

```json
{
  "answer": "string",
  "source_documents": [
    {
      "page_content": "string",
      "metadata": {
        "source": "string",
        "document_type": "string",
        "authorized_roles": ["string"]
      }
    }
  ],
  "thought_process": ["string"]
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Câu trả lời được tạo bởi AI |
| `source_documents` | array | Danh sách tài liệu nguồn được sử dụng |
| `thought_process` | array | Quá trình suy luận của agent (optional) |

#### Example Request

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-token" \
  -d '{
    "role": "warehouse_manager",
    "question": "Làm thế nào để kiểm tra tồn kho hiện tại?"
  }'
```

#### Example Response

```json
{
  "answer": "Để kiểm tra tồn kho hiện tại, bạn có thể truy cập module 'Quản lý tồn kho' trong hệ thống ERP, chọn 'Báo cáo tồn kho' và nhập mã sản phẩm hoặc tên sản phẩm. Hệ thống sẽ hiển thị số lượng tồn kho theo từng kho và vị trí.",
  "source_documents": [
    {
      "page_content": "Để kiểm tra tồn kho hiện tại, truy cập module 'Quản lý tồn kho'...",
      "metadata": {
        "source": "ERP_User_Manual_Inventory",
        "document_type": "user_manual",
        "authorized_roles": ["warehouse_manager", "inventory_clerk"]
      }
    }
  ],
  "thought_process": [
    "Thought: User đang hỏi về cách kiểm tra tồn kho",
    "Action: vector_search",
    "Action Input: kiểm tra tồn kho",
    "Observation: Tìm thấy thông tin trong user manual..."
  ]
}
```

### 2. Health Check Endpoint

**Kiểm tra trạng thái hoạt động của API**

```http
GET /health
```

#### Response

```json
{
  "status": "ok",
  "message": "ERP AI Pro Version API is running.",
  "pipeline_ready": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🎯 Role-Specific Query Examples

### Finance Manager

```json
{
  "role": "finance_manager",
  "question": "Báo cáo doanh thu quý 1 năm 2024"
}
```

**Available Tools:**
- `get_revenue_report`
- `get_expense_report`
- `get_customer_debt`
- `create_receipt`
- `create_payment`

### Sales Representative

```json
{
  "role": "sales_rep",
  "question": "Khách hàng ABC Company có đơn hàng nào đang pending không?"
}
```

**Available Tools:**
- `get_order_status`
- `get_customer_outstanding_balance`
- `vector_search`

### Warehouse Manager

```json
{
  "role": "warehouse_manager",
  "question": "Sản phẩm nào sắp hết hàng?"
}
```

**Available Tools:**
- `get_inventory_overview`
- `get_low_stock_alerts`
- `stock_in`
- `stock_out`

## 🔒 Authentication & Authorization

### Bearer Token Authentication

```http
Authorization: Bearer your-api-token
```

### Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

#### 403 Forbidden
```json
{
  "detail": "Insufficient permissions for requested operation"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "role"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 📊 Error Handling

### Standard HTTP Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| `200` | OK | Request thành công |
| `400` | Bad Request | Request không hợp lệ |
| `401` | Unauthorized | Không có quyền truy cập |
| `403` | Forbidden | Không đủ quyền thực hiện |
| `422` | Validation Error | Dữ liệu đầu vào không hợp lệ |
| `500` | Internal Server Error | Lỗi server nội bộ |
| `503` | Service Unavailable | Service tạm thời không khả dụng |

### Error Response Format

```json
{
  "detail": "string",
  "error_code": "string",
  "timestamp": "string",
  "correlation_id": "string"
}
```

## 🚀 Performance & Rate Limiting

### Rate Limits

| User Type | Requests per Minute | Burst Limit |
|-----------|-------------------|-------------|
| Free Tier | 10 | 20 |
| Professional | 100 | 200 |
| Enterprise | 1000 | 2000 |

### Response Times

| Operation Type | Expected Response Time |
|---------------|----------------------|
| Simple Query | < 2 seconds |
| Complex Query | < 5 seconds |
| Heavy Analytics | < 10 seconds |

## 📝 Interactive Documentation

### Swagger UI

Truy cập `http://localhost:8000/docs` để sử dụng interactive API documentation với:
- ✅ Try-it-out functionality
- 📋 Schema validation
- 🔧 Request/response examples
- 📚 Comprehensive documentation

### ReDoc

Truy cập `http://localhost:8000/redoc` để xem alternative documentation với:
- 📖 Clean, readable format
- 🏗️ Three-column layout
- 🔍 Search functionality
- 📱 Mobile-responsive design

## 🧪 Testing

### Using cURL

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Query với authentication
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"role": "admin", "question": "Hệ thống hoạt động như thế nào?"}'
```

### Using Python requests

```python
import requests

# Configuration
BASE_URL = "http://localhost:8000"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-api-token"
}

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Query
payload = {
    "role": "finance_manager",
    "question": "Doanh thu tháng này như thế nào?"
}
response = requests.post(f"{BASE_URL}/query", json=payload, headers=headers)
print(response.json())
```

### Using JavaScript/Fetch

```javascript
const baseUrl = 'http://localhost:8000';
const headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer your-api-token'
};

// Query function
async function queryERP(role, question) {
  const response = await fetch(`${baseUrl}/query`, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({ role, question })
  });
  
  return await response.json();
}

// Usage
queryERP('warehouse_manager', 'Tồn kho hiện tại như thế nào?')
  .then(result => console.log(result))
  .catch(error => console.error(error));
```

## 🔧 SDK & Client Libraries

### Official Python SDK

```python
from erp_ai_client import ERPAIClient

client = ERPAIClient(
    base_url="http://localhost:8000",
    api_token="your-api-token"
)

# Simple query
result = client.query(
    role="finance_manager",
    question="Doanh thu quý này như thế nào?"
)

print(result.answer)
```

### Community Libraries

- **JavaScript/TypeScript**: `erp-ai-js`
- **Go**: `erp-ai-go`
- **Java**: `erp-ai-java`
- **C#**: `ERPAIClient.NET`

## 📈 Monitoring & Analytics

### Request Metrics

Tất cả requests được tracked với:
- Response time
- Success/failure rates
- User role distribution
- Query complexity scores
- Resource utilization

### Business Intelligence

- 📊 Query patterns analysis
- 👥 User behavior insights
- 🎯 Performance optimization recommendations
- 📈 Usage trends và forecasting