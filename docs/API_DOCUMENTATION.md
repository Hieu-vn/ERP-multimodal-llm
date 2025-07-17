# 🛠️ ERP AI Pro Version - API Documentation

## 📑 Table of Contents
1. [📝 Overview](#overview)
2. [🌐 Base Information](#base-information)
3. [🔗 Endpoints Overview](#endpoints-overview)
4. [🚦 Core Endpoints](#core-endpoints)
5. [🧑‍💼 Role & Tool Mapping](#role-tool-mapping)
6. [🤖 Agent Functions & Business Features](#agent-functions-business-features)
7. [🔐 Authentication & Authorization](#authentication-authorization)
8. [🚨 Error Handling](#error-handling)
9. [📦 Data Models](#data-models)
10. [🛠️ Tools and Utilities](#tools-and-utilities)
11. [⚙️ Configuration](#configuration)
12. [📈 Deployment & Monitoring](#deployment-monitoring)
13. [🚀 Advanced Features & Extensions](#advanced-features-extensions)
14. [💡 Examples](#examples)

---

## 📝 1. Overview
ERP AI Pro Version cung cấp RESTful API xây dựng với FastAPI, hỗ trợ async, real-time, truy vấn ERP bằng ngôn ngữ tự nhiên, phân quyền theo vai trò, tích hợp multi-agent, vector search, knowledge graph, và các công cụ nghiệp vụ chuyên biệt.

---

## 🌐 2. Base Information
- **Base URL**: `http://localhost:8000`
- **API Version**: v1.0.0
- **Content-Type**: `application/json`
- **Authentication**: Bearer Token
- **Rate Limiting**: 100 requests/minute per user

---

## 🔗 3. Endpoints Overview
| Method | Endpoint   | Description                        | Auth Required |
|--------|------------|------------------------------------|---------------|
| POST   | /query     | Xử lý truy vấn ngôn ngữ tự nhiên   | ✅            |
| GET    | /health    | Health check                      | ❌            |
| GET    | /docs      | Interactive API documentation      | ❌            |
| GET    | /redoc     | Alternative API documentation      | ❌            |

---

## 🚦 4. Core Endpoints

### 4.1 🗣️ Query Endpoint
**POST /query**
- Xử lý truy vấn ngôn ngữ tự nhiên, trả về kết quả AI-powered, phân quyền theo vai trò.

**Request Body:**
```json
{
  "role": "string",
  "question": "string"
}
```
- `role`: Vai trò người dùng (xem bảng role bên dưới)
- `question`: Câu hỏi tự nhiên (tiếng Việt hoặc Anh)

**Response Body:**
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

**Ví dụ request:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-token" \
  -d '{
    "role": "warehouse_manager",
    "question": "Làm thế nào để kiểm tra tồn kho hiện tại?"
  }'
```

**Ví dụ response:**
```json
{
  "answer": "Để kiểm tra tồn kho hiện tại, bạn có thể truy cập module 'Quản lý tồn kho'...",
  "source_documents": [
    {
      "page_content": "...",
      "metadata": {
        "source": "ERP_User_Manual_Inventory",
        "document_type": "user_manual",
        "authorized_roles": ["warehouse_manager", "inventory_clerk"]
      }
    }
  ],
  "thought_process": [
    "Thought: User hỏi về kiểm tra tồn kho",
    "Action: vector_search",
    "Action Input: kiểm tra tồn kho",
    "Observation: Tìm thấy thông tin trong user manual..."
  ]
}
```

### 4.2 ❤️‍🩹 Health Check Endpoint
**GET /health**
- Kiểm tra trạng thái API, pipeline, model.

**Response:**
```json
{
  "status": "ok",
  "message": "ERP AI Pro Version API is running.",
  "pipeline_ready": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 🧑‍💼 5. Role & Tool Mapping

### Supported Roles
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

### Mapping Role với Tool/Agent
| 🧑‍💼 Role           | 🛠️ Tools/Agents (ví dụ)                          |
|--------------------|------------------------------------------------------|
| admin              | all_tools                                            |
| finance_manager    | get_revenue_report, get_expense_report, ...          |
| sales_rep          | get_order_status, get_customer_outstanding_balance   |
| warehouse_manager  | get_inventory_overview, get_low_stock_alerts, ...    |
| analyst            | reporting_tools, calculation_tools                   |

---

## 🤖 6. Agent Functions & Business Features

### 6.1 📈 Agent Sales
- `get_product_stock_level()`: Kiểm tra tồn kho sản phẩm
- `create_order()`: Tạo đơn hàng
- `get_order_status()`: Trạng thái đơn hàng
- `get_customer_outstanding_balance()`: Công nợ khách hàng

### 6.2 📦 Agent Inventory
- `get_inventory_overview()`: Tổng quan kho
- `stock_in()`, `stock_out()`: Nhập/xuất kho
- `inventory_check()`: Kiểm kê
- `get_low_stock_alerts()`: Cảnh báo tồn kho thấp

### 6.3 💰 Agent Finance
- `get_revenue_report()`: Báo cáo doanh thu
- `get_expense_report()`: Báo cáo chi phí
- `get_customer_debt()`: Công nợ khách hàng
- `create_receipt()`, `create_payment()`: Thu/chi

### 6.4 🏢 Project, 👥 HRM, 🤝 CRM, ⚙️ Workflow, 🖥️ Computer Use
- Quản lý dự án, nhân sự, khách hàng, tự động hóa quy trình, tự động hóa thao tác UI, ...

---

## 🔐 7. Authentication & Authorization
- **Bearer Token Authentication**: `Authorization: Bearer your-api-token`
- **RBAC**: Phân quyền theo vai trò, mapping tool/agent

---

## 🚨 8. Error Handling
- **401 Unauthorized**: Sai token
- **403 Forbidden**: Không đủ quyền
- **422 Validation Error**: Thiếu trường bắt buộc
- **500**: Lỗi server

**Response mẫu:**
```json
{
  "detail": "Invalid authentication credentials"
}
```

---

## 📦 9. Data Models
- `QueryRequest`, `QueryResponse`, `SourceDocument`, ...
- Định nghĩa chi tiết trong schema (xem code hoặc tài liệu chi tiết)

---

## 🛠️ 10. Tools and Utilities
- `vector_search`, `graph_erp_lookup`, `get_current_date`, ...
- Các công cụ hỗ trợ truy vấn, phân tích, kết nối API ERP, ...

---

## ⚙️ 11. Configuration
- Cấu hình qua file `.env`, `rag_config.py`, ...
- Tham số: model, database, API, performance, ...

---

## 📈 12. Deployment & Monitoring
- Hỗ trợ Docker, Kubernetes, Terraform, CI/CD
- Health check, logging, performance tracking

---

## 🚀 13. Advanced Features & Extensions
- Fine-tuning, multi-language, plugin architecture, BI, analytics, webhook, SDK, ...

---

## 💡 14. Examples
### 14.1 Role-Specific Query
```json
{
  "role": "finance_manager",
  "question": "Báo cáo doanh thu quý 1 năm 2024"
}
```
### 14.2 Tool Usage
```python
from erp_ai_pro.core.tools import vector_search
results = vector_search(query="kiểm tra tồn kho", role="warehouse_manager")
```

---

## 📚 Tham khảo thêm
- [🏗️ ARCHITECTURE.md](ARCHITECTURE.md)
- [📋 README.md](README.md)
- [🤝 CONTRIBUTING.md](CONTRIBUTING.md)