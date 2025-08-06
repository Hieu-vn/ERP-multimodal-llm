# config.py
import os
from pathlib import Path

# Xác định thư mục gốc của dự án một cách đáng tin cậy.
# Giả định rằng thư mục gốc là thư mục cha của 'erp_ai_pro'.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Định nghĩa thư mục chứa dữ liệu nguồn
DATA_SOURCE_DIR = PROJECT_ROOT / "data_source"

# Tạo các đường dẫn đầy đủ đến các tệp CSV
CUSTOMER_CSV = DATA_SOURCE_DIR / "customers.csv"
PRODUCT_CSV = DATA_SOURCE_DIR / "products.csv"
ORDER_CSV = DATA_SOURCE_DIR / "orders.csv"
EMPLOYEE_CSV = DATA_SOURCE_DIR / "employees.csv"

# In ra để kiểm tra (tùy chọn, hữu ích cho việc gỡ lỗi)
print(f"Project Root: {PROJECT_ROOT}")
print(f"Data Source Directory: {DATA_SOURCE_DIR}")
