# ERP AI Pro Version 🚀

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0+-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.0+-purple)](https://langchain.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Giới thiệu dự án

**ERP AI Pro Version** là một hệ thống trợ lý AI enterprise-grade được thiết kế để revolutionize cách tương tác với các hệ thống ERP (Enterprise Resource Planning). Sử dụng công nghệ tiên tiến RAG (Retrieval-Augmented Generation) kết hợp với các mô hình ngôn ngữ lớn (LLM), hệ thống cung cấp khả năng truy vấn dữ liệu ERP bằng ngôn ngữ tự nhiên thông qua API RESTful.

### 🎯 Tầm nhìn
Democratize việc truy cập dữ liệu ERP, biến những truy vấn phức tạp thành các cuộc hội thoại đơn giản bằng tiếng Việt tự nhiên, loại bỏ rào cản kỹ thuật giữa người dùng và dữ liệu doanh nghiệp.

### 🎁 Giá trị cốt lõi
- **Accessibility**: Dễ dàng tiếp cận dữ liệu ERP cho mọi người dùng
- **Intelligence**: AI-powered insights từ dữ liệu doanh nghiệp
- **Security**: Role-based access control với bảo mật cao
- **Scalability**: Kiến trúc microservices có thể mở rộng

## ✨ Tính năng chính

### 🔥 Core Features
- **🗣️ Natural Language Processing**: Truy vấn dữ liệu ERP bằng tiếng Việt tự nhiên
- **🧠 Advanced Agentic RAG**: Kết hợp vector search (ChromaDB) + knowledge graph (Neo4j) + LLM với multi-agent reasoning
- **🔒 Role-Based Access Control (RBAC)**: Phân quyền chi tiết cho 10+ vai trò người dùng
- **⚡ Multi-Agent Architecture**: 8 specialized agents cho mọi module ERP
- **🔄 Real-time Data Integration**: Kết nối trực tiếp với ERP APIs và UI automation

### 📊 ERP Modules Coverage
- **💰 Finance & Accounting**: Doanh thu, chi phí, công nợ, thanh toán, báo cáo tài chính
- **📦 Inventory Management**: Quản lý kho, tồn kho, nhập/xuất kho, cảnh báo
- **🛒 Sales & Orders**: Đơn hàng, khách hàng, sản phẩm, doanh số
- **🎯 Project Management**: Dự án, task, milestone, resource allocation, risk management
- **👥 Human Resources (HRM)**: Nhân viên, lương, nghỉ phép, tuyển dụng, đánh giá hiệu suất
- **🤝 Customer Relationship (CRM)**: Lead, opportunity, khách hàng, support tickets
- **⚙️ Workflow Automation**: Quy trình tự động, phê duyệt, workflow engine
- **🖥️ Computer Use Automation**: Tự động hóa UI, data entry, report generation

### 🛠️ Technical Features
- **🏗️ Production-Ready API**: FastAPI với async processing
- **📊 Hybrid Data Sources**: Structured (Neo4j) + Unstructured (Vector Store) + Live APIs
- **🎯 Fine-tuning Support**: Unsloth integration cho model optimization
- **📈 Query Enhancement**: Query rewriting, expansion và re-ranking
- **🔧 Retry Mechanisms**: Robust error handling với exponential backoff

### 🌟 Enterprise Features
- **📋 Comprehensive Logging**: Detailed monitoring và debugging
- **🏥 Health Checks**: Application health monitoring
- **🐳 Docker Support**: Containerized deployment
- **☁️ Infrastructure as Code**: Terraform configs cho cloud deployment

## 🏗️ Architecture Overview

### 🤖 AI Agents Ecosystem

**ERP AI Pro** sử dụng kiến trúc multi-agent với 8 specialized agents:

#### 🔍 **Core Agents**
- **RAG Pipeline Agent**: Agentic RAG với vector search + knowledge graph
- **Computer Use Agent**: UI automation với computer vision và browser control

#### 📊 **Business Domain Agents**
- **Sales Agent**: Đơn hàng, sản phẩm, khách hàng, doanh số
- **Inventory Agent**: Quản lý kho, tồn kho, nhập/xuất, kiểm kê
- **Finance Agent**: Tài chính, kế toán, thanh toán, báo cáo
- **Project Management Agent**: Dự án, task, resource, milestone tracking
- **HRM Agent**: Nhân sự, lương, nghỉ phép, tuyển dụng, đánh giá
- **CRM Agent**: Lead, opportunity, customer service, marketing

#### ⚙️ **Automation Agents**
- **Workflow Automation Agent**: Quy trình tự động, approval workflows

### 🔄 Agent Orchestration Flow

1. **Query Analysis**: Xác định domain và business context
2. **Agent Selection**: Chọn agent phù hợp nhất dựa trên RBAC
3. **Multi-Agent Reasoning**: Kết hợp nhiều agents nếu cần
4. **Response Synthesis**: Tổng hợp kết quả từ các agents

## 📁 Cấu trúc dự án

```
.
├── config/                     # Cấu hình cho các module khác nhau
│   ├── rag_config.py          # RBAC và tool mapping
│   └── neo4j_config.py        # Graph database config
├── erp_ai_core/               # Core AI agents và logic
│   ├── agent_sales.py         # Sales domain agent
│   ├── agent_inventory.py     # Inventory management agent
│   ├── agent_finance.py       # Finance & accounting agent
│   ├── agent_project_management.py # Project management agent
│   ├── agent_hrm.py           # Human resources agent
│   ├── agent_crm.py           # Customer relationship agent
│   ├── agent_workflow_automation.py # Workflow automation
│   ├── agent_computer_use.py  # UI automation agent
│   ├── rag_pipeline.py        # Main RAG orchestrator
│   ├── vector_search_tool.py  # Vector search tool
│   ├── graph_erp_tool.py      # Graph database tool
│   └── data_analysis_tool.py  # Analysis & calculation tool
├── data_ingestion/             # Scripts để trích xuất và tải dữ liệu ERP
├── data_preparation/           # Scripts để tiền xử lý và chuẩn bị dữ liệu
├── deployment/                 # Các script và cấu hình liên quan đến triển khai
├── erp_ai_core/                # Logic cốt lõi của pipeline RAG và các mô hình
├── evaluation/                 # Các công cụ và script để đánh giá mô hình
├── finetuning/                 # Các script và cấu hình cho việc tinh chỉnh LLM
├── infrastructure/             # Cấu hình hạ tầng (ví dụ: Terraform)
├── notebooks/                  # Jupyter notebooks cho thử nghiệm và khám phá dữ liệu
├── tests/                      # Unit và integration tests
├── .env.example                # Mẫu file cấu hình biến môi trường
├── .gitignore                  # Các file/thư mục bị bỏ qua bởi Git
├── Dockerfile                  # Định nghĩa Docker image cho ứng dụng
├── .dockerignore               # Các file/thư mục bị bỏ qua khi build Docker image
├── main.py                     # Điểm khởi đầu của ứng dụng FastAPI
├── requirements.pro.txt        # Danh sách các thư viện Python cần thiết
├── run_api_server.bat          # Script chạy API server (Windows)
├── run_create_vector_store.bat # Script tạo vector store (Windows)
├── run_create_vector_store.py  # Script Python để tạo vector store
├── run_etl.bat                 # Script chạy ETL (Windows)
└── test_functional_query.py    # Script kiểm tra chức năng truy vấn
```

## Cài đặt

Để cài đặt và chạy dự án, bạn cần có Python 3.10+ và `pip`.

1.  **Clone repository:**
    ```bash
    git clone https://github.com/Hieu-vn/ERP-multimodel-llm.git
    cd ERP-multimodel-llm
    ```

2.  **Tạo và kích hoạt môi trường ảo (khuyến nghị):**
    ```bash
    python -m venv venv
    # Trên Windows
    .\venv\Scripts\activate
    # Trên macOS/Linux
    source venv/bin/activate
    ```

3.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install -r requirements.pro.txt
    ```

4.  **Cấu hình biến môi trường:**
    *   Tạo một tệp `.env` trong thư mục gốc của dự án bằng cách sao chép `.env.example`.
    *   Chỉnh sửa tệp `.env` với các giá trị cấu hình cần thiết (ví dụ: khóa API, đường dẫn dữ liệu).

    ```bash
    copy .env.example .env  # Trên Windows
    cp .env.example .env    # Trên macOS/Linux
    ```

## Cách chạy

### Chạy API Server

Sau khi cài đặt, bạn có thể chạy API server:

```bash
# Trên Windows
.\run_api_server.bat

# Hoặc thủ công
uvicorn main:app --host 0.0.0.0 --port 8000
```

API sẽ chạy trên `http://0.0.0.0:8000`. Bạn có thể truy cập tài liệu API tại `http://0.0.0.0:8000/docs` hoặc `http://0.0.0.0:8000/redoc`.

### Chạy ETL và tạo Vector Store

Trước khi truy vấn, bạn cần chạy quá trình ETL để nạp dữ liệu vào vector store.

```bash
# Trên Windows
.\run_etl.bat
.\run_create_vector_store.bat

# Hoặc thủ công
python data_ingestion/etl_erp_data.py
python run_create_vector_store.py
```

Quá trình này sẽ xử lý dữ liệu ERP của bạn và tạo các embedding, sau đó lưu trữ chúng vào ChromaDB.

## Sử dụng API

Sau khi API server đang chạy và vector store đã được tạo, bạn có thể gửi các truy vấn đến endpoint `/query`.

**Endpoint:** `POST /query`

**Request Body (JSON):**

```json
{
  "role": "finance_manager",
  "question": "Doanh thu quý 1 năm 2024 là bao nhiêu?"
}
```

**Response Body (JSON):**

```json
{
  "answer": "Dựa trên dữ liệu, doanh thu quý 1 năm 2024 là X triệu USD.",
  "source_documents": [
    {
      "page_content": "...",
      "metadata": {
        "source": "...",
        "page": "..."
      }
    }
  ]
}
```

Bạn cũng có thể kiểm tra trạng thái API tại `GET /health`.

## 📚 Documentation

Để hiểu sâu hơn về dự án, vui lòng tham khảo các tài liệu chi tiết:

- **[🏗️ Architecture Guide](ARCHITECTURE.md)** - Kiến trúc hệ thống và thiết kế chi tiết
- **[📡 API Documentation](API.md)** - Tài liệu API đầy đủ với examples
- **[🚀 Deployment Guide](DEPLOYMENT.md)** - Hướng dẫn triển khai production
- **[🤝 Contributing Guide](CONTRIBUTING.md)** - Hướng dẫn đóng góp cho dự án
- **[📝 Changelog](CHANGELOG.md)** - Lịch sử thay đổi và phiên bản

## 🤝 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp từ cộng đồng! 

### Cách bắt đầu:
1. 📖 Đọc [Contributing Guide](CONTRIBUTING.md)
2. 🍴 Fork repository
3. 🌿 Tạo feature branch
4. 🔧 Implement changes
5. 🧪 Add tests
6. 📝 Update documentation
7. 🚀 Submit Pull Request

### Lĩnh vực cần đóng góp:
- 🎯 **Model Optimization**: Fine-tuning và performance
- 🌍 **Multi-language Support**: English, Chinese support
- 📊 **Advanced Analytics**: ML-powered insights
- 📱 **Mobile SDK**: React Native/Flutter integration
- 📚 **Documentation**: Tutorials và examples

## 🌟 Community & Support

### 💬 Kênh giao tiếp
- **GitHub Issues**: Bug reports và feature requests
- **GitHub Discussions**: Q&A và thảo luận
- **Discord**: Real-time community support
- **Email**: [maintainers@erp-ai-pro.com]

### 🎯 Roadmap
- **v1.1.0**: Multi-language support
- **v1.2.0**: Advanced analytics dashboard  
- **v1.3.0**: Mobile SDK
- **v2.0.0**: Distributed architecture

## 📄 License

Dự án này được cấp phép theo [MIT License](LICENSE) - xem file LICENSE để biết chi tiết.

## 🙏 Acknowledgments

### Core Team
- **AI/ML Engineering**: Model development và optimization
- **Backend Development**: API và infrastructure
- **DevOps**: Deployment và monitoring
- **Documentation**: Technical writing và examples

### Community
Cảm ơn tất cả contributors đã giúp dự án phát triển:
- 🐛 Bug reporters
- 💡 Feature suggesters  
- 🔧 Code contributors
- 📚 Documentation improvers
- 🧪 Testers và feedback providers

### Technology Stack
- **LangChain**: RAG framework foundation
- **FastAPI**: Modern web framework
- **ChromaDB**: Vector database innovation
- **Neo4j**: Graph database excellence
- **Unsloth**: Efficient fine-tuning
- **HuggingFace**: Model ecosystem

---

<div align="center">

**Made with ❤️ for the Enterprise AI Community**

⭐ **Star this repository if you find it helpful!** ⭐

[🚀 Get Started](DEPLOYMENT.md) | [🏗️ Architecture](ARCHITECTURE.md) | [📡 API Docs](API.md) | [🤝 Contributing](CONTRIBUTING.md)

</div>

```