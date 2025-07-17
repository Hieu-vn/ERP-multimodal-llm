# ERP AI Pro Version 🚀

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0+-green)](https://fastapi.tiangolo.com/) [![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org) [![LangChain](https://img.shields.io/badge/LangChain-0.1.0+-purple)](https://langchain.com) [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Giới thiệu dự án

**ERP AI Pro Version** là hệ thống trợ lý AI enterprise-grade, ứng dụng công nghệ RAG (Retrieval-Augmented Generation) kết hợp LLM, multi-agent, hỗ trợ tiếng Việt, tích hợp sâu với mọi module ERP doanh nghiệp. Dự án hướng tới democratize truy cập dữ liệu ERP, biến truy vấn phức tạp thành hội thoại tự nhiên, loại bỏ rào cản kỹ thuật.

### 🎯 Mục tiêu & Giá trị cốt lõi
- 🗝️ **Democratize ERP Data Access**: Truy vấn ERP bằng ngôn ngữ tự nhiên
- 👤 **Role-based Intelligence**: Thông tin phù hợp vai trò, quyền hạn
- 🏗️ **Scalable Architecture**: Module hóa, dễ mở rộng, tích hợp
- 🛡️ **Production-ready**: Error handling, monitoring, security
- 🧑‍💻 **Accessibility**: Dễ tiếp cận cho mọi người dùng
- 🤖 **Intelligence**: AI-powered insights
- 🔐 **Security**: RBAC, bảo mật cao
- 💼 **Business Value**: Tăng hiệu quả vận hành, giảm thời gian truy xuất dữ liệu, hỗ trợ quyết định nhanh

---

## ✨ Tính năng nổi bật

### 🔥 Core Features
- 🗣️ **Natural Language Processing**: Truy vấn ERP bằng tiếng Việt tự nhiên
- 🧠 **Advanced Agentic RAG**: Vector search (ChromaDB) + knowledge graph (Neo4j) + LLM + multi-agent reasoning
- 🔒 **Role-Based Access Control (RBAC)**: Phân quyền chi tiết cho 10+ vai trò
- ⚡ **Multi-Agent Architecture**: 8+ specialized agents cho mọi module ERP
- 🔄 **Real-time Data Integration**: Kết nối trực tiếp ERP APIs, UI automation
- 📊 **Hybrid Data Sources**: Structured (Neo4j), Unstructured (Vector Store), Live APIs
- 🎯 **Fine-tuning Support**: Unsloth, PEFT
- 📈 **Query Enhancement**: Query rewriting, expansion, re-ranking
- 🔧 **Retry Mechanisms**: Robust error handling, exponential backoff
- 🏥 **Health Checks, Logging, Monitoring**
- 🐳 **Docker, Terraform, CI/CD ready**

### 📊 ERP Modules Coverage
- 💰 **Finance & Accounting**: Doanh thu, chi phí, công nợ, thanh toán, báo cáo tài chính
- 📦 **Inventory Management**: Quản lý kho, tồn kho, nhập/xuất kho, cảnh báo
- 🛒 **Sales & Orders**: Đơn hàng, khách hàng, sản phẩm, doanh số
- 🎯 **Project Management**: Dự án, task, milestone, resource allocation, risk management
- 👥 **Human Resources (HRM)**: Nhân viên, lương, nghỉ phép, tuyển dụng, đánh giá hiệu suất
- 🤝 **Customer Relationship (CRM)**: Lead, opportunity, khách hàng, support tickets
- ⚙️ **Workflow Automation**: Quy trình tự động, phê duyệt, workflow engine
- 🖥️ **Computer Use Automation**: Tự động hóa UI, data entry, report generation

---

## 🏆 Business Value & ROI

| 💡 Lợi ích | Mô tả |
|---|---|
| ⚡ **90%+ Query Resolution** | Tự động hóa truy vấn ERP |
| ⏱️ **60% Time Reduction** | Truy xuất dữ liệu, báo cáo nhanh hơn |
| 🕑 **24/7 Availability** | AI assistant luôn sẵn sàng |
| 👤 **Role-Based Experience** | Cá nhân hóa theo vai trò |
| 🧠 **Intelligent Suggestions** | Gợi ý thông minh, contextual |
| 📈 **Scalability & Security** | Microservices, RBAC, audit trail |
| 📋 **Compliance** | Audit, data governance |

---

## 🚀 Hướng dẫn cài đặt nhanh

### 🛠️ Yêu cầu
- 🐍 Python 3.10+
- 📦 pip

### 📝 Các bước cài đặt

1. **Clone repository:**
    ```bash
    git clone https://github.com/Hieu-vn/ERP-multimodel-llm.git
    cd ERP-multimodel-llm
    ```
2. **Tạo và kích hoạt môi trường ảo:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
3. **Cài đặt dependencies:**
    ```bash
    pip install -r requirements.pro.txt
    ```
4. **Cấu hình environment:**
    ```bash
    cp .env.example .env
    # Chỉnh sửa .env nếu cần
    ```
5. **Chạy ETL và tạo vector store:**
    ```bash
    python data_ingestion/etl_erp_data.py
    python run_create_vector_store.py
    ```
6. **Chạy API server:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

---

## 📚 Tài liệu chi tiết

- [🏗️ ARCHITECTURE.md](ARCHITECTURE.md): Kiến trúc hệ thống, phân tích chi tiết, technical deep-dive
- [🛠️ API_DOCUMENTATION.md](API_DOCUMENTATION.md): Tài liệu API, endpoint, ví dụ, mapping agent/tools
- [🤝 CONTRIBUTING.md](CONTRIBUTING.md): Hướng dẫn đóng góp, triển khai, quy trình phát triển
- [📝 CHANGELOG.md](CHANGELOG.md): Lịch sử thay đổi

---

## 🤝 Đóng góp
Chúng tôi hoan nghênh mọi đóng góp từ cộng đồng!

### 🚦 Quy trình đóng góp
- [x] Đọc [Contributing Guide](CONTRIBUTING.md)
- [x] Fork repository
- [x] Tạo feature branch
- [x] Implement changes
- [x] Add tests
- [x] Update documentation
- [x] Submit Pull Request

### 🌱 Lĩnh vực cần đóng góp:
- Model Optimization, Multi-language Support, Advanced Analytics, Mobile SDK, Documentation

---

## 📅 Roadmap & Future Enhancements
- 🌐 Multi-language support
- 📊 Advanced analytics dashboard
- 🔔 Real-time notifications
- 📱 Mobile API support
- 🏢 Distributed deployment
- 🧬 Model versioning system
- 🧪 A/B testing framework

---

## 🏢 Liên hệ
- 📧 Email: phamkhachieuforwork1001@gmail.com
- 🐙 Github: https://github.com/Hieu-vn/ERP-multimodel-llm
