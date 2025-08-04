# Gemini Instructions for ERP AI Pro Project

This file serves as a persistent context for Gemini, outlining the project's current state, objectives, and detailed checklist of tasks to be completed.

## Project Overview
The ERP AI Pro is a next-generation AI assistant for enterprise resource planning, built on a multi-agent architecture with multimodal capabilities, deep integration with ERP modules, and support for Vietnamese.

## Core Objectives
- To build a robust, production-grade AI agent system.
- To ensure every user query is handled intelligently: either resolved, clarified with specific questions, or gracefully declined with clear reasons and alternatives.
- To fully leverage ERP Phase 1 capabilities as outlined in `[Chatbot]_ General.md`.
- To ensure the system is scalable, maintainable, and secure.

## General Guidelines for Gemini
- **Project Structure Awareness:** Always read and remember the project structure before coding to avoid redundant actions or creating files that already exist or have existing system handling.
- **Prioritize Completeness:** For each component, ensure it's fully implemented and testable before moving to the next. Avoid placeholders unless explicitly agreed upon.
- **Context Awareness:** Always refer to this `GEMINI.md` for the current checklist and project context.
- **Transparency:** Clearly state what you are doing and why.
- **Error Handling:** Implement robust error handling at every layer.
- **Logging:** Use structured logging (`structlog`) consistently.
- **User Experience:** Focus on clear, helpful, and actionable responses for the end-user, especially in fallback scenarios.
- **ERP Phase 1 Focus:** All new implementations should directly support the functionalities described in `[Chatbot]_ General.md`.

---

##  Detailed Project Checklist: Phase 1 Development Tasks

This checklist outlines the remaining development tasks to bring the ERP AI Pro system to a fully functional and robust state, focusing on detailed implementation and integration.

### **I. Database & Data Ingestion (Hoàn thiện Cơ sở dữ liệu & Nạp dữ liệu)**

*   **1. Hoàn thiện Kết nối Database (`erp_ai_pro/core/db_connections.py`)**
    *   [ ] **Mục tiêu:** Đảm bảo các hàm `init_vector_db` (Qdrant) và `init_graph_db` (Neo4j) không chỉ kết nối mà còn có thể thực hiện các thao tác cơ bản (ví dụ: kiểm tra kết nối, tạo collection/database nếu chưa có).
    *   [ ] **Hành động:** Review code hiện tại, thêm logic kiểm tra kết nối mạnh mẽ hơn và xử lý lỗi kết nối một cách rõ ràng.

*   **2. Hoàn thiện Nạp dữ liệu cho Vector DB (`scripts/run_create_vector_store.py`)**
    *   [ ] **Mục tiêu:** Đảm bảo script này có thể đọc các file tài liệu mẫu trong `knowledge_base` và nạp chúng vào Qdrant một cách thành công và có thể kiểm tra được.
    *   [ ] **Hành động:** Chạy thử script này, xác minh dữ liệu được nạp vào Qdrant (có thể dùng Qdrant UI hoặc client API để kiểm tra).

*   **3. Hoàn thiện Nạp dữ liệu cho Graph DB (`scripts/run_create_graph_data.py`)**
    *   [ ] **Mục tiêu:** Đảm bảo script này có thể nạp dữ liệu mẫu vào Neo4j một cách thành công và có thể kiểm tra được, phản ánh schema mở rộng trong `BusinessIntelligenceAgent`.
    *   [ ] **Hành động:** Chạy thử script này, xác minh dữ liệu được nạp vào Neo4j (có thể dùng Neo4j Browser để kiểm tra).

### **II. Agent Enhancements & Integration (Nâng cấp Agent & Tích hợp)**

*   **4. Hoàn thiện các Tools trong `LiveERPAgent` (`erp_ai_pro/core/tools.py`)**
    *   [ ] **Mục tiêu:** Thay thế các hàm mock đơn giản bằng các hàm giả lập hành vi của ERP một cách phức tạp hơn, bao gồm cả việc kiểm tra quyền, trả về lỗi nghiệp vụ, hoặc yêu cầu thêm thông tin nếu cần. Mỗi tool phải có logic giả lập đủ để kiểm tra.
    *   [ ] **Hành động:**
        *   `get_newsfeed_updates`: Giả lập dữ liệu động hơn, có thể lọc theo thời gian.
        *   `create_new_task`: Giả lập kiểm tra `assignee_name` có tồn tại không.
        *   `update_task_status`: Giả lập kiểm tra `task_id` có tồn tại không, trạng thái chuyển đổi hợp lệ.
        *   `get_tasks_by_assignee`: Giả lập trả về các task thực tế hơn.
        *   `create_approval_request`: Giả lập kiểm tra `request_type` hợp lệ, có thể yêu cầu `amount` cho một số loại.
        *   `get_my_approval_requests`: Giả lập trả về các request của người dùng hiện tại.
        *   `approve_request`/`reject_request`: Giả lập kiểm tra `request_id` tồn tại, quyền phê duyệt.
        *   `get_report`: Giả lập dữ liệu báo cáo phức tạp hơn, có thể trả về lỗi nếu `report_type` không hợp lệ.
        *   `get_employee_details`: Giả lập trả về chi tiết nhân viên đầy đủ hơn, có thể trả về lỗi nếu không tìm thấy.
        *   `get_okr_status`: Giả lập trả về trạng thái OKR chi tiết hơn.
        *   `get_invoice_details`/`get_contract_status`: Giả lập trả về chi tiết hóa đơn/hợp đồng.
        *   `get_product_stock_level`: Giả lập trả về tồn kho theo nhiều kho, có thể trả về lỗi nếu sản phẩm không tồn tại.
        *   `get_customer_order_history`: Giả lập trả về lịch sử đơn hàng chi tiết hơn.
        *   `create_support_ticket`: Giả lập tạo ticket và trả về ID.

*   **5. Hoàn thiện `BusinessIntelligenceAgent` (`erp_ai_pro/core/agents/bi_agent.py`)**
    *   [ ] **Mục tiêu:** Đảm bảo `TEXT_TO_CYPHER_PROMPT` đủ thông minh để tạo ra các truy vấn Cypher phức tạp hơn, và `_summarize_results` có thể xử lý các kết quả đa dạng từ Neo4j.
    *   [ ] **Hành động:**
        *   Tạo các ví dụ truy vấn phức tạp (ví dụ: "Doanh số theo khu vực", "Sản phẩm bán chạy nhất", "Mối quan hệ giữa khách hàng và dự án") và kiểm tra khả năng của BI Agent.
        *   Đảm bảo `_summarize_results` có thể biến các kết quả dạng bảng/đồ thị thành văn bản tự nhiên.

*   **6. Hoàn thiện `MultimodalAgent` (`erp_ai_pro/core/agents/multimodal_agent.py`)**
    *   [ ] **Mục tiêu:** Đảm bảo các model xử lý hình ảnh được tải đúng cách và có thể trích xuất thông tin hữu ích, và LLM có thể tổng hợp thông tin này với câu hỏi của người dùng.
    *   [ ] **Hành động:**
        *   Cung cấp các hình ảnh mẫu (biểu đồ, hóa đơn, ảnh sản phẩm) vào thư mục `uploads` (hoặc một thư mục test riêng).
        *   Kiểm tra khả năng của Multimodal Agent trong việc tạo caption, OCR và tổng hợp thông tin.

*   **7. Cập nhật `OrchestratorAgent` (`erp_ai_pro/core/agents/orchestrator.py`)**
    *   [ ] **Mục tiêu:** Đảm bảo `ORCHESTRATOR_SYSTEM_PROMPT` phản ánh chính xác và đầy đủ các khả năng mới của `LiveERPAgent` và `BusinessIntelligenceAgent` (với các ví dụ cụ thể hơn).
    *   [ ] **Hành động:** Review lại prompt, thêm các ví dụ mới cho các công cụ và truy vấn BI đã được mở rộng.

---
# Checklist khắc phục và hoàn thiện dự án ERP AI Pro

### **Giai đoạn 1: Ưu tiên Cao nhất (Critical - Lỗi nghiêm trọng & Lỗ hổng bảo mật)**

*Mục tiêu của giai đoạn này là vá các lỗ hổng bảo mật, sửa các lỗi khiến dự án không thể build hoặc chạy, và đảm bảo tính nhất quán cơ bản của kiến trúc.*

---

#### **✅ 1. Khắc phục Lỗi Hard-coded đường dẫn file trong Data Ingestion**

*   **Vấn đề:** Script ETL không thể chạy trên bất kỳ môi trường nào ngoài máy của nhà phát triển ban đầu do đường dẫn file tuyệt đối (`C:/Users/phamk/`).
*   **Giải pháp:** Sử dụng đường dẫn tương đối từ gốc dự án để đảm bảo script có thể chạy ở mọi nơi.
*   **Các bước thực hiện:**
    1.  Mở file `erp_ai_pro/data_ingestion/config.py`.
    2.  Thay đổi `BASE_DIR` để nó tự động xác định đường dẫn gốc của dự án. Sử dụng thư viện `pathlib` để có giải pháp an toàn và đa nền tảng.
    3.  Đảm bảo các file CSV mẫu được di chuyển vào thư mục `data_source` ở gốc dự án để phù hợp với cấu trúc mới.
*   **Xác minh:** Chạy lệnh `python erp_ai_pro/data_ingestion/etl_erp_data.py` từ thư mục gốc của dự án. Script phải chạy thành công mà không có lỗi `FileNotFoundError`.

---

#### **✅ 2. Vá lỗ hổng bảo mật Remote Code Execution (RCE) trong `PerformCalculationTool`**

*   **Vấn đề:** Việc sử dụng `eval()` trên đầu vào của người dùng tạo ra một lỗ hổng bảo mật nghiêm trọng, cho phép thực thi mã độc.
*   **Giải pháp:** Thay thế `eval()` bằng một phương pháp phân tích cú pháp biểu thức an toàn.
*   **Các bước thực hiện:**
    1.  Mở file `erp_ai_pro/core/tools.py`.
    2.  Trong class `PerformCalculationTool`, thay thế phương thức `run` bằng một logic an toàn hơn. Sử dụng thư viện `ast.literal_eval` cho các phép tính đơn giản hoặc một thư viện phân tích toán học an toàn như `numexpr`.
    3.  Thêm `numexpr` vào file `requirements.pro.txt`.
*   **Xác minh:**
    1.  Viết unit test cho `PerformCalculationTool` trong `erp_ai_pro/tests/test_tools.py`.
    2.  Test case 1: Truyền một biểu thức hợp lệ (`"2 * (3 + 5)"`) và xác minh kết quả đúng.
    3.  Test case 2: Truyền một chuỗi mã độc (`"__import__('os').system('ls')"`) và xác minh rằng hàm ném ra một lỗi `ValueError` hoặc tương tự, thay vì thực thi lệnh.

---

### **Giai đoạn 2: Ưu tiên Trung bình (Architectural Integrity & Core Functionality)**

*Mục tiêu của giai đoạn này là làm cho các thành phần cốt lõi của dự án hoạt động đúng như thiết kế kiến trúc, loại bỏ sự mơ hồ và hoàn thiện các luồng chức năng chính.*

---

#### **✅ 3. Hợp nhất các API Entrypoint không nhất quán**

*   **Vấn đề:** Tồn tại hai file API (`main.py` và `enhanced_main.py`) gây nhầm lẫn và khó bảo trì.
*   **Giải pháp:** Hợp nhất thành một entry point duy nhất và xóa file không cần thiết.
*   **Các bước thực hiện:**
    1.  Xóa file `erp_ai_pro/api/main.py` (phiên bản cũ).
    2.  Đổi tên `erp_ai_pro/api/enhanced_main.py` thành `erp_ai_pro/api/main.py`.
    3.  Mở file `Dockerfile.enhanced` và cập nhật lệnh `CMD` để trỏ đến file mới.
*   **Xác minh:** Build và chạy ứng dụng bằng `docker-compose -f docker-compose.enhanced.yml up`. Ứng dụng phải khởi động thành công và endpoint `/health` phải hoạt động.

---

#### **✅ 4. Sửa chữa Pipeline Dữ liệu bị đứt gãy (ETL -> Neo4j)**

*   **Vấn đề:** Script `load_to_neo4j.py` đang sử dụng dữ liệu giả lập thay vì dữ liệu đã được xử lý từ `etl_erp_data.py`.
*   **Giải pháp:** Kết nối hai script lại với nhau để tạo thành một pipeline dữ liệu hoàn chỉnh.
*   **Các bước thực hiện:**
    1.  Mở file `erp_ai_pro/data_ingestion/load_to_neo4j.py`.
    2.  Import hàm `run_etl` từ `etl_erp_data.py`.
    3.  Trong khối `if __name__ == "__main__":`, gọi `nodes, relationships = run_etl()` để lấy dữ liệu thực tế.
    4.  Xóa các biến `simulated_nodes` và `simulated_relationships`.
    5.  Truyền `nodes` và `relationships` thực tế vào các hàm `loader.load_nodes()` và `loader.load_relationships()`.
*   **Xác minh:** Chạy `python erp_ai_pro/data_ingestion/load_to_neo4j.py`. Sau khi script hoàn tất, sử dụng Neo4j Browser để truy vấn và xác nhận rằng dữ liệu từ các file CSV (ví dụ: tên khách hàng, sản phẩm) đã thực sự được nạp vào cơ sở dữ liệu.

---

#### **✅ 5. Hoàn thiện Tích hợp cho các Agent Cốt lõi**

*   **Vấn đề:** Các agent quan trọng như `BusinessIntelligenceAgent` và `LiveERPAgent` chưa được tích hợp đầy đủ trong `main_system.py`.
*   **Giải pháp:** Implement logic gọi và truyền dữ liệu thực tế cho các agent này.
*   **Các bước thực hiện:**
    1.  Mở file `erp_ai_pro/core/main_system.py`.
    2.  Trong phương thức `query`, tại khối `if/elif` chọn agent, thay thế các logic placeholder.
*   **Xác minh:** Viết các integration test mới trong thư mục `tests/` để kiểm tra các luồng này.

---

### **Giai đoạn 3: Ưu tiên Thấp (Code Quality & Refactoring)**

*Mục tiêu của giai đoạn này là dọn dẹp mã nguồn, tái cấu trúc để tăng tính dễ đọc, dễ bảo trì và loại bỏ các thành phần không cần thiết.*

---

#### **✅ 6. Tái cấu trúc Logic RBAC và loại bỏ `rag_pipeline.py`**

*   **Vấn đề:** Logic RBAC (lọc công cụ theo vai trò) đang nằm trong file `rag_pipeline.py` của kiến trúc cũ, gây khó hiểu.
*   **Giải pháp:** Di chuyển logic này đến nơi phù hợp hơn trong kiến trúc mới và loại bỏ file cũ.
*   **Các bước thực hiện:**
    1.  Di chuyển logic lọc `tools` dựa trên `role` từ `rag_pipeline.py` vào phương thức `query` của `main_system.py`.
    2.  Sau khi di chuyển, nếu `rag_pipeline.py` không còn chức năng nào khác, hãy xóa file này.
*   **Xác minh:** Viết unit test cho chức năng RBAC.

---

#### **✅ 7. Thay thế Logic nghiệp vụ giả lập (Mock) bằng một Client Interface rõ ràng**

*   **Vấn đề:** Các công cụ nghiệp vụ đang gọi đến các API giả lập, không có cấu trúc rõ ràng cho việc tích hợp thật.
*   **Giải pháp:** Tạo một lớp `ERPClient` tập trung, đóng vai trò là một interface (giao diện) để tương tác với hệ thống ERP thực tế.
*   **Các bước thực hiện:**
    1.  Tạo một file mới, ví dụ `erp_ai_pro/core/erp_client.py`.
    2.  Trong file này, định nghĩa một class `ERPClient` với các phương thức tương ứng với các nghiệp vụ.
    3.  Trong các file tool (`sales.py`, `hrm.py`, ...), thay vì dùng `requests.post/get`, hãy gọi đến các phương thức của `ERPClient`.
*   **Xác minh:** Tất cả các unit test hiện có cho các tool vẫn phải pass.

---

#### **✅ 8. Dọn dẹp các file không cần thiết và làm rõ cấu trúc dự án**

*   **Vấn đề:** Tồn tại các file và thư mục thừa, gây nhiễu.
*   **Giải pháp:** Xóa các file không dùng và thêm file README để giải thích mục đích của các thư mục trống.
*   **Các bước thực hiện:**
    1.  Xóa file `Dockerfile` (chỉ giữ lại `Dockerfile.enhanced`).
    2.  Đối với các thư mục trống như `evaluation`, `notebooks`, `finetuning`, tạo một file `README.md` bên trong mỗi thư mục với nội dung giải thích mục đích của nó.
*   **Xác minh:** Dự án vẫn build và chạy bình thường.
