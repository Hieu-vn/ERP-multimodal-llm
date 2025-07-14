# ERP AI Pro Version

## Giới thiệu dự án

**ERP AI Pro Version** là một trợ lý AI mạnh mẽ được thiết kế để tích hợp với các hệ thống ERP (Enterprise Resource Planning), tận dụng công nghệ Retrieval-Augmented Generation (RAG) và các mô hình ngôn ngữ lớn (LLM). Mục tiêu của dự án là cung cấp một giao diện API RESTful cho phép người dùng truy vấn dữ liệu ERP bằng ngôn ngữ tự nhiên và nhận được câu trả lời chính xác, có nguồn gốc từ dữ liệu doanh nghiệp.

Dự án này giúp chuyển đổi cách tương tác với dữ liệu ERP phức tạp, biến nó thành một nguồn thông tin dễ dàng truy cập và phân tích thông qua các câu hỏi thông thường, loại bỏ nhu cầu truy vấn cơ sở dữ liệu trực tiếp hoặc tìm kiếm thủ công.

## Tính năng chính

*   **Truy vấn ngôn ngữ tự nhiên:** Cho phép người dùng đặt câu hỏi về dữ liệu ERP bằng ngôn ngữ tự nhiên.
*   **Retrieval-Augmented Generation (RAG):** Kết hợp khả năng truy xuất thông tin từ cơ sở dữ liệu vector (ChromaDB) với khả năng tạo văn bản của LLM để cung cấp câu trả lời chính xác và có ngữ cảnh.
*   **API RESTful:** Cung cấp một API dễ sử dụng được xây dựng với FastAPI để tích hợp liền mạch với các ứng dụng khác.
*   **Khả năng mở rộng:** Kiến trúc module cho phép dễ dàng mở rộng và tích hợp các mô hình, nguồn dữ liệu mới.
*   **Tối ưu hóa LLM:** Hỗ trợ các thư viện cho việc tinh chỉnh và tối ưu hóa hiệu suất LLM.

## Cấu trúc dự án

```
.
├── config/                     # Cấu hình cho các module khác nhau
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

## Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng fork repository, tạo một nhánh mới cho các thay đổi của bạn và gửi Pull Request.

## Liên hệ

Nếu có bất kỳ câu hỏi hoặc vấn đề nào, vui lòng mở một issue trên GitHub hoặc liên hệ với chúng tôi.

```