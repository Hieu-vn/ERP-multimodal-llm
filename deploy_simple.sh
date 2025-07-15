#!/bin/bash

# Simple Deployment Script for Modern ERP AI Pro
# No bloat, just essentials

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}=================================${NC}"
    echo -e "${BLUE}   Modern ERP AI Pro v2.0${NC}"
    echo -e "${BLUE}   Simple Deployment${NC}"
    echo -e "${BLUE}=================================${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

check_python() {
    print_step "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    if [[ "$python_version" < "3.8" ]]; then
        print_error "Python 3.8+ is required. Found: $python_version"
        exit 1
    fi
    
    print_info "✓ Python $python_version found"
}

install_dependencies() {
    print_step "Installing dependencies..."
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install essential packages only
    pip install \
        fastapi==0.108.0 \
        uvicorn==0.26.0 \
        torch==2.1.0 \
        transformers==4.40.0 \
        sentence-transformers==2.6.0 \
        qdrant-client==1.7.0 \
        redis==5.0.0 \
        pillow==10.2.0 \
        easyocr==1.7.0 \
        pandas==2.2.0 \
        scikit-learn==1.4.0 \
        prophet==1.1.0 \
        numpy==1.26.0 \
        pydantic==2.6.0 \
        python-multipart==0.0.6
    
    print_info "✓ Dependencies installed"
}

setup_services() {
    print_step "Setting up services..."
    
    # Check if Redis is running
    if ! pgrep redis-server > /dev/null; then
        print_info "Starting Redis server..."
        if command -v redis-server &> /dev/null; then
            redis-server --daemonize yes
        else
            print_error "Redis not found. Please install Redis: sudo apt-get install redis-server"
            exit 1
        fi
    fi
    
    # Check if we can run Qdrant via Docker
    if command -v docker &> /dev/null; then
        print_info "Starting Qdrant vector database..."
        docker run -d \
            --name qdrant \
            -p 6333:6333 \
            -p 6334:6334 \
            -v $(pwd)/qdrant_data:/qdrant/storage \
            qdrant/qdrant:latest
    else
        print_error "Docker not found. Please install Docker for Qdrant."
        print_info "Or install Qdrant directly: pip install qdrant-client"
    fi
    
    print_info "✓ Services configured"
}

create_config() {
    print_step "Creating configuration..."
    
    cat > .env << EOF
# Modern ERP AI Pro Configuration
BASE_MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=erp_knowledge
MAX_TOKENS=4096
TEMPERATURE=0.7
TOP_P=0.9
RETRIEVAL_K=5
USE_VLLM=false
EOF
    
    print_info "✓ Configuration created"
}

create_directories() {
    print_step "Creating directories..."
    
    mkdir -p uploads
    mkdir -p logs
    mkdir -p qdrant_data
    
    print_info "✓ Directories created"
}

create_sample_data() {
    print_step "Creating sample data..."
    
    cat > sample_data.py << 'EOF'
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from erp_ai_pro.core.modern_rag_pipeline import modern_rag_pipeline

async def add_sample_data():
    # Initialize pipeline
    await modern_rag_pipeline.setup()
    
    # Sample ERP documents
    documents = [
        {
            "content": "ERP là viết tắt của Enterprise Resource Planning - Hệ thống hoạch định tài nguyên doanh nghiệp. Đây là phần mềm quản lý tích hợp các quy trình kinh doanh cốt lõi của một tổ chức.",
            "metadata": {"category": "definition", "topic": "erp"}
        },
        {
            "content": "Quản lý kho bao gồm các chức năng: nhập kho, xuất kho, kiểm kê, theo dõi tồn kho. Hệ thống cần cảnh báo khi hàng tồn kho thấp.",
            "metadata": {"category": "inventory", "topic": "warehouse"}
        },
        {
            "content": "Báo cáo tài chính bao gồm: báo cáo doanh thu, báo cáo chi phí, báo cáo lãi lỗ, bảng cân đối kế toán. Các báo cáo này cần được cập nhật theo thời gian thực.",
            "metadata": {"category": "finance", "topic": "reporting"}
        },
        {
            "content": "Quy trình bán hàng: tạo đơn hàng → xác nhận → xuất kho → giao hàng → thanh toán → hậu mãi. Mỗi bước cần có thông báo và theo dõi.",
            "metadata": {"category": "sales", "topic": "process"}
        },
        {
            "content": "Quản lý nhân sự bao gồm: quản lý thông tin nhân viên, chấm công, tính lương, đánh giá hiệu suất, quản lý nghỉ phép.",
            "metadata": {"category": "hr", "topic": "management"}
        }
    ]
    
    # Add documents to knowledge base
    for doc in documents:
        await modern_rag_pipeline.add_document(doc["content"], doc["metadata"])
    
    print("Sample data added successfully!")

if __name__ == "__main__":
    asyncio.run(add_sample_data())
EOF
    
    print_info "✓ Sample data script created"
}

start_application() {
    print_step "Starting application..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Add sample data
    print_info "Adding sample data..."
    python sample_data.py
    
    # Start the application
    print_info "Starting Modern ERP AI Pro API..."
    python main_modern.py &
    
    # Wait for startup
    sleep 5
    
    # Test the API
    if curl -s http://localhost:8000/health > /dev/null; then
        print_info "✓ API started successfully"
    else
        print_error "API failed to start"
        exit 1
    fi
}

display_summary() {
    print_step "Deployment completed!"
    
    echo -e "\n${GREEN}🎉 Modern ERP AI Pro v2.0 is running!${NC}\n"
    
    echo -e "${BLUE}📊 Access Points:${NC}"
    echo -e "  • API: ${GREEN}http://localhost:8000${NC}"
    echo -e "  • Documentation: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "  • Health Check: ${GREEN}http://localhost:8000/health${NC}"
    
    echo -e "\n${BLUE}🚀 Key Features:${NC}"
    echo -e "  • Llama-3.1 8B Language Model"
    echo -e "  • Multimodal Support (Images)"
    echo -e "  • Streaming Responses"
    echo -e "  • Redis Caching"
    echo -e "  • Qdrant Vector Database"
    echo -e "  • Business Intelligence"
    
    echo -e "\n${BLUE}🔧 Quick Tests:${NC}"
    echo -e "  • Query: ${GREEN}curl -X POST http://localhost:8000/query -H 'Content-Type: application/json' -d '{\"role\": \"admin\", \"question\": \"ERP là gì?\"}'${NC}"
    echo -e "  • Metrics: ${GREEN}curl http://localhost:8000/metrics${NC}"
    echo -e "  • Stream: ${GREEN}curl -X POST http://localhost:8000/query/stream -H 'Content-Type: application/json' -d '{\"role\": \"admin\", \"question\": \"Quản lý kho như thế nào?\", \"stream\": true}'${NC}"
    
    echo -e "\n${BLUE}🔧 Management:${NC}"
    echo -e "  • Stop: ${GREEN}pkill -f main_modern.py${NC}"
    echo -e "  • Logs: ${GREEN}tail -f logs/app.log${NC}"
    echo -e "  • Restart: ${GREEN}./deploy_simple.sh${NC}"
}

main() {
    print_header
    
    check_python
    install_dependencies
    setup_services
    create_config
    create_directories
    create_sample_data
    start_application
    display_summary
    
    echo -e "\n${GREEN}✅ Deployment completed successfully!${NC}"
}

# Check if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi