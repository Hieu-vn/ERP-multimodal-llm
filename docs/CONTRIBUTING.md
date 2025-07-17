# 🤝 CONTRIBUTING.md

Cảm ơn bạn đã quan tâm đến việc đóng góp cho **ERP AI Pro Version**! Chúng tôi hoan nghênh mọi đóng góp từ cộng đồng để cùng nhau xây dựng hệ thống AI ERP tốt nhất.

## 📋 Mục lục
- [🤝 Quy tắc ứng xử](#quy-tắc-ứng-xử)
- [🚀 Bắt đầu nhanh](#bắt-đầu-nhanh)
- [💻 Thiết lập môi trường phát triển](#thiết-lập-môi-trường-phát-triển)
- [🔀 Quy trình phát triển & Git workflow](#quy-trình-phát-triển--git-workflow)
- [🧪 Coding Standards & Testing](#coding-standards--testing)
- [🚢 Hướng dẫn triển khai (Deployment)](#hướng-dẫn-triển-khai-deployment)
- [🔄 CI/CD & Production](#cicd--production)
- [📥 Pull Request & Issue Guidelines](#pull-request--issue-guidelines)
- [🌐 Cộng đồng & Liên hệ](#cộng-đồng--liên-hệ)

---

## 🤝 Quy tắc ứng xử
Dự án này tuân theo [Contributor Covenant](https://www.contributor-covenant.org/). Hãy luôn tôn trọng, xây dựng, chuyên nghiệp và chào đón mọi background.

---

## 🚀 Bắt đầu nhanh
- [x] **Fork repository**
- [x] **Clone về máy**
  ```bash
  git clone https://github.com/yourusername/ERP-multimodel-llm.git
  cd ERP-multimodel-llm
  ```
- [x] **Tạo branch mới**
  ```bash
  git checkout -b feature/your-feature-name
  ```

---

## 💻 Thiết lập môi trường phát triển
### 🛠️ Yêu cầu hệ thống
- 🐍 Python 3.10+
- 🐙 Git
- 🐳 Docker & Docker Compose
- 🕸️ Neo4j (local hoặc Docker)
- ⚡ GPU (tùy chọn, cho development)

### ⚙️ Cài đặt môi trường
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.pro.txt
pip install -r requirements-dev.txt  # Dev dependencies
cp .env.example .env
# Chỉnh sửa .env nếu cần
```

### 🗄️ Khởi tạo database & vector store
```bash
# Chạy Neo4j, Redis bằng Docker Compose (nếu cần)
docker-compose -f docker-compose.dev.yml up -d neo4j redis
# ETL & vector store
python data_ingestion/etl_erp_data.py
python run_create_vector_store.py
```

### 🚦 Chạy server phát triển
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔀 Quy trình phát triển & Git workflow
- Sử dụng **Git Flow**: feature/..., fix/..., docs/..., refactor/..., test/..., chore/...
- Commit theo [Conventional Commits](https://conventionalcommits.org/)
- Luôn tạo Pull Request từ branch riêng biệt
- Thường xuyên cập nhật từ main branch

**Ví dụ:**
```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature
# ... code ...
git add .
git commit -m "feat(agent): add new HRM agent"
git push origin feature/your-feature
```

---

## 🧪 Coding Standards & Testing
- Tuân thủ **PEP8** (Python)
- Sử dụng type hint, docstring, comment rõ ràng
- Chạy lint, type check, format trước khi commit:
  ```bash
  flake8 erp_ai_pro/core/ --max-line-length=100
  mypy erp_ai_pro/core/
  black erp_ai_pro/core/ --line-length=100
  isort erp_ai_pro/core/ --profile black
  bandit -r erp_ai_pro/core/
  ```
- Viết unit test, integration test, functional test:
  ```bash
  python -m pytest tests/
  ```
- Sử dụng pre-commit hooks:
  ```bash
  pre-commit install
  ```

---

## 🚢 Hướng dẫn triển khai (Deployment)
### 🐳 Docker
- Build image:
  ```bash
  docker build -t erp-ai-pro:latest .
  ```
- Run container:
  ```bash
  docker run -d --name erp-ai-pro -p 8000:8000 -v $(pwd)/data:/app/data -v $(pwd)/.env:/app/.env --restart unless-stopped erp-ai-pro:latest
  ```

### 🐳 Docker Compose
- Sử dụng file `docker-compose.yml` hoặc `docker-compose.enhanced.yml`:
  ```bash
  docker-compose up -d
  docker-compose logs -f erp-ai-api
  docker-compose ps
  ```

### ☸️ Kubernetes (production)
- Sử dụng các manifest trong thư mục `infrastructure/` hoặc tự tạo manifest phù hợp
- Triển khai với Helm, Terraform nếu cần

### ☁️ Cloud & CI/CD
- Hỗ trợ triển khai trên AWS, GCP, Azure (tham khảo file Terraform)
- CI/CD với GitHub Actions, tự động build, test, deploy

---

## 🔄 CI/CD & Production
- Đảm bảo cấu hình `.env` production, secrets, resource limit
- Health check, logging, monitoring, alerting
- Backup, recovery, scaling, security best practices

---

## 📥 Pull Request & Issue Guidelines
- [x] Mô tả rõ ràng, chi tiết, có checklist review
- [x] Đính kèm issue liên quan (nếu có)
- [x] Đảm bảo pass toàn bộ test, lint, type check trước khi tạo PR
- [x] Tham gia review, phản hồi tích cực

---

## 🌐 Cộng đồng & Liên hệ
- 📧 Email: phamkhachieuforwork1001@gmail.com
- 🐙 Github: https://github.com/Hieu-vn/ERP-multimodel-llm
- 💬 Đóng góp ý kiến, báo lỗi, đề xuất tính năng qua GitHub Issues hoặc Discussions

---

**🎉 Chúng tôi đánh giá cao mọi đóng góp để dự án ngày càng hoàn thiện!**