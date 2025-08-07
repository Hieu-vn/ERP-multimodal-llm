# Kế hoạch Phát triển Chiến lược cho ERP AI Pro

## Tầm nhìn: Hệ thống Đa Agent Phân cấp (Hierarchical Multi-Agent System)
Mục tiêu của chúng ta là xây dựng một "tổ chức" gồm các trợ lý AI chuyên môn, thay vì một AI "biết tuốt". Mỗi nhân viên sẽ tương tác với một "Tổng Quản" AI, và AI này sẽ tự động điều phối công việc đến các "Chuyên gia" AI tương ứng trong các lĩnh vực khác nhau, dựa trên quyền hạn và yêu cầu của người dùng.

---

## Mô hình Phát triển: "Lõi Sạch & Lát Cắt Dọc" (Clean Core & Vertical Slices)
Chúng ta sẽ từ bỏ cách làm chắp vá và áp dụng một mô hình phát triển bài bản:
1.  **Lõi Sạch (Clean Core):** Tái cấu trúc để có một nền tảng kiến trúc rõ ràng, tách bạch và dễ bảo trì.
2.  **Lát Cắt Dọc (Vertical Slices):** Phát triển từng tính năng hoàn chỉnh từ đầu đến cuối (Data -> Logic -> AI -> API), mang lại giá trị sử dụng ngay lập tức.

---

## Kiến trúc & Công nghệ

### Chiến lược Mô hình Lai (Hybrid Model Strategy)
Để tối ưu và tối đa hóa hiệu năng, dự án sẽ áp dụng chiến lược "Mô hình Lai", sử dụng đúng model cho đúng vai trò:
- **"Tổng Quản" AI (OrchestratorAgent):** Sử dụng một model API thương mại hàng đầu (**Gemini 1.5 Pro** hoặc tương đương) để tận dụng khả năng suy luận (reasoning) và gọi hàm (function calling) vượt trội. Model này được "dạy" qua Prompt Engineering, không cần fine-tune.
- **"Chuyên gia" AI (Specialist Agents):** Sử dụng một model nền mã nguồn mở mạnh mẽ (**Llama 3 8B** hoặc tương đương) làm gốc. Các kỹ năng chuyên môn sẽ được huấn luyện bằng phương pháp **QLoRA (Quantized Low-Rank Adaptation)** để tạo ra các "adapter" nhỏ gọn, hiệu suất cao và tiết kiệm chi phí.

### Công nghệ Nền tảng
- **Kiến trúc Logic:** Hệ thống Đa Agent Phân cấp 3 lớp.
- **Framework Backend:** FastAPI.
- **Ngôn ngữ:** Python.
- **CSDL:** SQLite (Giao dịch), Neo4j (Graph), Qdrant (Vector).
- **Framework AI:** LangChain / LlamaIndex.
- **Hạ tầng:** Docker & Docker Compose.

### Sơ đồ Kiến trúc Đích
```
[Người dùng (với vai trò & quyền hạn)]
        |
        V
[Lớp 1: "Tổng Quản" AI (OrchestratorAgent - Chief of Staff)]
   (Sử dụng Model Gemini Pro/Ultra mạnh nhất để suy luận và điều phối)
        |
        +------------------+------------------+------------------+
        |                  |                  |                  |
        V                  V                  V                  V
[Lớp 2: "Chuyên gia" AI (Specialist Agents - Các Trưởng phòng)]
   (Sử dụng các model được fine-tune chuyên biệt bằng QLoRA)
   - SalesAgent       - HRAgent          - BIAgent          - FinanceAgent
        |                  |                  |                  |
        V                  V                  V                  V
[Lớp 3: "Công cụ & Dữ liệu" (Tools & Data Sources)]
   (API, Databases, Knowledge Base...)
```

---

## Lộ trình Phát triển Chi tiết

### **Giai đoạn 0: Tái Cấu trúc Nền tảng (The Great Refactoring)**
**Mục tiêu:** Sửa chữa những sai lầm kiến trúc cốt lõi. Giai đoạn này không tạo ra tính năng mới, nhưng nó là bắt buộc để các giai đoạn sau có thể thành công.

*   **[ ] 1. Định nghĩa Kiến trúc 3 Lớp "Canonical":**
    *   **Hành động:** Chính thức hóa cấu trúc thư mục và quy tắc cho 3 lớp:
        1.  **`erp_ai_pro/presentation`**: Lớp API (FastAPI).
        2.  **`erp_ai_pro/cognitive`**: Lớp AI/Agent (Orchestrator, Specialists).
        3.  **`erp_ai_pro/tools`**: Lớp Công cụ & Dữ liệu (DB connections, ERP clients, Tools).
    *   **Mục tiêu:** Tách biệt rõ ràng, mỗi lớp có một nhiệm vụ duy nhất.

*   **[ ] 2. Thiết lập Môi trường & Testing:**
    *   **Hành động:**
        1.  Tạo một file `requirements.txt` duy nhất và sạch sẽ.
        2.  Thiết lập `pytest` làm framework testing chính thức.
        3.  Viết các unit test cơ bản cho các hàm trong lớp `tools`.

*   **[ ] 3. Xây dựng Cơ chế RBAC (Role-Based Access Control) Lõi:**
    *   **Hành động:**
        1.  Thiết kế cơ chế xác thực người dùng và lấy `user_id`, `role` tại lớp API.
        2.  Xây dựng chức năng **Tải "Công cụ" Động (Dynamic Tool Loading)**: Dựa vào `role`, `OrchestratorAgent` sẽ chỉ cung cấp các tool được phép cho các agent con.
    *   **Mục tiêu:** Đảm bảo AI không thể truy cập hay thậm chí "biết" đến các chức năng mà người dùng không có quyền.

### **Giai đoạn 1: Xây dựng "Lát cắt Dọc" Đầu tiên - Quản lý Phê duyệt**
**Mục tiêu:** Xây dựng một tính năng hoàn chỉnh từ đầu đến cuối để chứng minh kiến trúc mới hoạt động hiệu quả.

*   **[ ] 1. Lớp Tools & Data:**
    *   **Hành động:**
        1.  Thiết kế và tạo bảng `approval_requests` trong CSDL.
        2.  Trong `erp_ai_pro/tools/erp_client.py`, viết các hàm: `create_request_in_db`, `get_request_from_db`, `update_request_status_in_db`.
        3.  Trong `erp_ai_pro/tools/approval_tools.py`, tạo các tool `CreateApprovalRequestTool`, `ApproveRequestTool` gọi đến `erp_client`.

*   **[ ] 2. Lớp Cognitive (AI):**
    *   **Hành động:** Cập nhật `OrchestratorAgent` để nó nhận biết và biết khi nào cần sử dụng các tool phê duyệt mới.

*   **[ ] 3. Lớp Presentation (API):**
    *   **Hành động:** Đảm bảo API có thể nhận các câu lệnh như "tạo yêu cầu nghỉ phép" và chuyển nó cho `OrchestratorAgent`.

*   **[ ] 4. Testing:**
    *   **Hành động:** Viết một **integration test** để kiểm tra toàn bộ luồng từ API -> Orchestrator -> Tool -> CSDL.

### **Giai đoạn 2: Fine-tune "Chuyên gia" AI Đầu tiên với QLoRA**
**Mục tiêu:** Tạo ra một agent chuyên môn đầu tiên, chứng minh tính hiệu quả của QLoRA.

*   **[ ] 1. Lựa chọn Chuyên gia & Chuẩn bị Dữ liệu:**
    *   **Hành động:**
        1.  Chọn `BIAgent` (Business Intelligence Agent) làm chuyên gia đầu tiên.
        2.  Tạo một tập dữ liệu chất lượng cao gồm các cặp: `("câu hỏi nghiệp vụ bằng ngôn ngữ tự nhiên", "truy vấn Cypher/SQL chính xác tương ứng")`.

*   **[ ] 2. Fine-tune bằng QLoRA:**
    *   **Hành động:**
        1.  Sử dụng thư viện `transformers`, `bitsandbytes`, `peft`.
        2.  Tải một model nền (ví dụ: Llama 3 8B, Mixtral) với cấu hình lượng tử hóa 4-bit.
        3.  Huấn luyện model trên tập dữ liệu đã chuẩn bị để tạo ra một "adapter" LoRA chuyên về dịch ngôn ngữ sang truy vấn CSDL.
        4.  Lưu lại file adapter đã huấn luyện.

*   **[ ] 3. Tích hợp Chuyên gia vào Hệ thống:**
    *   **Hành động:** Cập nhật `OrchestratorAgent` để khi gặp các câu hỏi phân tích, nó sẽ gọi đến `BIAgent` (đã được tải cùng với adapter LoRA tương ứng).

### **Giai đoạn 3: Mở rộng theo Chiều dọc & Hoàn thiện**
**Mục tiêu:** Lần lượt xây dựng các tính năng nghiệp vụ khác và tăng cường trí thông minh cho hệ thống.

*   **[ ] 1. Xây dựng các "Lát cắt dọc" tiếp theo:**
    *   **Hành động:** Lặp lại quy trình của Giai đoạn 1 và 2 cho các nghiệp vụ khác:
        *   Quản lý Khách hàng (CRM)
        *   Quản lý Nhân sự (HRM)
        *   Xử lý Hóa đơn (Multimodal)

*   **[ ] 2. Nâng cấp Trí nhớ (Memory):**
    *   **Hành động:** Tích hợp cơ chế lưu trữ và truy xuất ngữ cảnh hội thoại để AI có thể hiểu các câu hỏi nối tiếp.

*   **[ ] 3. Giám sát & Ghi log (Observability):**
    *   **Hành động:** Tích hợp các công cụ logging (ví dụ: `structlog`) để theo dõi và gỡ lỗi các chuỗi suy luận của AI, giúp việc tinh chỉnh prompt và gỡ lỗi dễ dàng hơn.