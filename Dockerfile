# Stage 1: Builder
# Sử dụng cùng base image để đảm bảo tương thích với các thư viện ML
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime AS builder

WORKDIR /app

# Tạo một môi trường ảo để cài đặt dependencies
ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Sao chép requirements.pro.txt và cài đặt dependencies vào môi trường ảo
COPY requirements.pro.txt .
RUN pip --timeout 1000 install --no-cache-dir -r requirements.pro.txt

# Stage 2: Runtime
# Sử dụng cùng base image cho runtime để đảm bảo môi trường nhất quán
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# Sao chép môi trường ảo đã cài đặt từ stage builder
COPY --from=builder /app/venv /app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Sao chép mã nguồn ứng dụng
COPY . .

# Mở cổng mà ứng dụng FastAPI sẽ lắng nghe
EXPOSE 8000

# Lệnh chạy ứng dụng khi container khởi động
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]