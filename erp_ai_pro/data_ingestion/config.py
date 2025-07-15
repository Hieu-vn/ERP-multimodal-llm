# config.py
import os

# Đường dẫn đến các tệp CSV mẫu
BASE_DIR = "C:/Users/phamk/" # Thay đổi nếu các file CSV ở thư mục khác

CUSTOMER_CSV = os.path.join(BASE_DIR, "customers.csv")
PRODUCT_CSV = os.path.join(BASE_DIR, "products.csv")
ORDER_CSV = os.path.join(BASE_DIR, "orders.csv")
EMPLOYEE_CSV = os.path.join(BASE_DIR, "employees.csv")