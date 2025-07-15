// ===== ERP AI PRO API INTEGRATION =====

// ===== API CONFIGURATION =====
const API_BASE_URL = 'http://localhost:8000'; // Adjust based on your backend URL
const API_ENDPOINTS = {
    QUERY: '/query',
    HEALTH: '/health'
};

// ===== API CLIENT CLASS =====
class ERPAIClient {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }

    // ===== CORE HTTP METHODS =====
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            method: options.method || 'GET',
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        if (config.method !== 'GET' && options.body) {
            config.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async get(endpoint, options = {}) {
        return this.request(endpoint, { method: 'GET', ...options });
    }

    async post(endpoint, body, options = {}) {
        return this.request(endpoint, { method: 'POST', body, ...options });
    }

    async put(endpoint, body, options = {}) {
        return this.request(endpoint, { method: 'PUT', body, ...options });
    }

    async delete(endpoint, options = {}) {
        return this.request(endpoint, { method: 'DELETE', ...options });
    }

    // ===== ERP AI SPECIFIC METHODS =====
    async queryAI(role, question) {
        return this.post(API_ENDPOINTS.QUERY, {
            role: role,
            question: question
        });
    }

    async healthCheck() {
        return this.get(API_ENDPOINTS.HEALTH);
    }
}

// ===== INITIALIZE API CLIENT =====
const apiClient = new ERPAIClient();

// ===== AI CHAT FUNCTIONALITY =====
let chatHistory = [];
let isProcessing = false;

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const messagesContainer = document.getElementById('chat-messages');
    
    if (!input || !messagesContainer) return;
    
    const message = input.value.trim();
    if (!message || isProcessing) return;
    
    // Clear input
    input.value = '';
    
    // Add user message to chat
    addChatMessage('user', message);
    
    // Show loading indicator
    const loadingMessage = addChatMessage('ai', 'Đang xử lý...', true);
    
    // Set processing state
    isProcessing = true;
    
    try {
        // Send message to API
        const response = await apiClient.queryAI(currentUser.role, message);
        
        // Remove loading message
        if (loadingMessage) {
            loadingMessage.remove();
        }
        
        // Add AI response
        addChatMessage('ai', response.answer);
        
        // Store in chat history
        chatHistory.push({
            user: message,
            ai: response.answer,
            timestamp: new Date(),
            sourceDocuments: response.source_documents || []
        });
        
        // Show source documents if available
        if (response.source_documents && response.source_documents.length > 0) {
            addSourceDocuments(response.source_documents);
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        
        // Remove loading message
        if (loadingMessage) {
            loadingMessage.remove();
        }
        
        // Show error message
        addChatMessage('ai', 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.');
        
        // Show notification
        showNotification('Không thể kết nối với AI. Vui lòng kiểm tra kết nối mạng.', 'error');
    } finally {
        isProcessing = false;
    }
}

function addChatMessage(type, content, isLoading = false) {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) return null;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `vn-chat-message ${type}`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'vn-message-avatar';
    
    if (type === 'user') {
        avatarDiv.innerHTML = `<i class="fas fa-user"></i>`;
    } else {
        avatarDiv.innerHTML = `<i class="fas fa-robot"></i>`;
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'vn-message-content';
    
    if (isLoading) {
        contentDiv.innerHTML = `
            <div class="vn-loading-vn">
                <span>Đang xử lý...</span>
            </div>
        `;
    } else {
        contentDiv.innerHTML = formatMessageContent(content);
    }
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageDiv;
}

function formatMessageContent(content) {
    // Convert newlines to <br> tags
    content = content.replace(/\n/g, '<br>');
    
    // Format URLs as links
    content = content.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    
    // Format currency amounts
    content = content.replace(/(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:VND|₫|đồng)/gi, 
        '<span class="vn-currency">$1</span>');
    
    // Format product codes
    content = content.replace(/\b([A-Z]{2,3}\d{3,6})\b/g, '<code>$1</code>');
    
    return content;
}

function addSourceDocuments(documents) {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer || !documents.length) return;
    
    const sourceDiv = document.createElement('div');
    sourceDiv.className = 'vn-chat-message ai';
    sourceDiv.innerHTML = `
        <div class="vn-message-avatar">
            <i class="fas fa-file-alt"></i>
        </div>
        <div class="vn-message-content">
            <p><strong>Nguồn tham khảo:</strong></p>
            <ul>
                ${documents.map(doc => `<li>${doc.title || 'Tài liệu'}: ${doc.snippet || doc.content}</li>`).join('')}
            </ul>
        </div>
    `;
    
    messagesContainer.appendChild(sourceDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ===== DATA LOADING FUNCTIONS =====
async function loadOrdersTable() {
    const tbody = document.getElementById('orders-table');
    if (!tbody) return;
    
    // Sample data - in real app, this would come from API
    const orders = [
        {
            id: 'DH001',
            customer: 'Công ty TNHH ABC',
            total: 15600000,
            status: 'Đang xử lý',
            date: '2024-01-15',
            statusClass: 'warning'
        },
        {
            id: 'DH002',
            customer: 'Công ty CP XYZ',
            total: 28900000,
            status: 'Đã giao',
            date: '2024-01-14',
            statusClass: 'success'
        },
        {
            id: 'DH003',
            customer: 'Cửa hàng 123',
            total: 8750000,
            status: 'Đã hủy',
            date: '2024-01-13',
            statusClass: 'error'
        }
    ];
    
    tbody.innerHTML = orders.map(order => `
        <tr>
            <td><strong>${order.id}</strong></td>
            <td>${order.customer}</td>
            <td class="vn-text-right">${formatVietnameseCurrency(order.total)}</td>
            <td><span class="vn-status-badge ${order.statusClass}">${order.status}</span></td>
            <td>${formatVietnameseDate(order.date)}</td>
            <td>
                <button class="vn-btn outline" onclick="viewOrderDetails('${order.id}')">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

async function loadProductsTable() {
    const tbody = document.getElementById('products-table');
    if (!tbody) return;
    
    // Sample data - in real app, this would come from API
    const products = [
        {
            code: 'SP001',
            name: 'Sản phẩm A',
            quantity: 150,
            price: 250000,
            status: 'Còn hàng',
            statusClass: 'success'
        },
        {
            code: 'SP002',
            name: 'Sản phẩm B',
            quantity: 8,
            price: 180000,
            status: 'Sắp hết',
            statusClass: 'warning'
        },
        {
            code: 'SP003',
            name: 'Sản phẩm C',
            quantity: 0,
            price: 320000,
            status: 'Hết hàng',
            statusClass: 'error'
        }
    ];
    
    tbody.innerHTML = products.map(product => `
        <tr>
            <td><code>${product.code}</code></td>
            <td>${product.name}</td>
            <td class="vn-text-right">${formatVietnameseNumber(product.quantity)}</td>
            <td class="vn-text-right">${formatVietnameseCurrency(product.price)}</td>
            <td><span class="vn-status-badge ${product.statusClass}">${product.status}</span></td>
            <td>
                <button class="vn-btn outline" onclick="editProduct('${product.code}')">
                    <i class="fas fa-edit"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

async function loadTransactionsTable() {
    const tbody = document.getElementById('transactions-table');
    if (!tbody) return;
    
    // Sample data - in real app, this would come from API
    const transactions = [
        {
            id: 'GD001',
            type: 'Thu',
            amount: 15600000,
            description: 'Thanh toán đơn hàng DH001',
            date: '2024-01-15',
            typeClass: 'success'
        },
        {
            id: 'GD002',
            type: 'Chi',
            amount: -5200000,
            description: 'Mua hàng nhà cung cấp',
            date: '2024-01-14',
            typeClass: 'error'
        },
        {
            id: 'GD003',
            type: 'Thu',
            amount: 28900000,
            description: 'Thanh toán đơn hàng DH002',
            date: '2024-01-14',
            typeClass: 'success'
        }
    ];
    
    tbody.innerHTML = transactions.map(transaction => `
        <tr>
            <td><strong>${transaction.id}</strong></td>
            <td><span class="vn-status-badge ${transaction.typeClass}">${transaction.type}</span></td>
            <td class="vn-text-right ${transaction.amount > 0 ? 'vn-text-success' : 'vn-text-error'}">
                ${formatVietnameseCurrency(Math.abs(transaction.amount))}
            </td>
            <td>${transaction.description}</td>
            <td>${formatVietnameseDate(transaction.date)}</td>
            <td>
                <button class="vn-btn outline" onclick="viewTransactionDetails('${transaction.id}')">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// ===== DETAIL VIEW FUNCTIONS =====
function viewOrderDetails(orderId) {
    // In real app, this would fetch order details from API
    showModal('view-details', {
        title: `Chi tiết đơn hàng ${orderId}`,
        content: `
            <div class="vn-details-container">
                <h4>Thông tin đơn hàng</h4>
                <p><strong>Mã đơn hàng:</strong> ${orderId}</p>
                <p><strong>Khách hàng:</strong> Công ty TNHH ABC</p>
                <p><strong>Trạng thái:</strong> <span class="vn-status-badge warning">Đang xử lý</span></p>
                <p><strong>Ngày tạo:</strong> ${formatVietnameseDate('2024-01-15')}</p>
                <p><strong>Tổng tiền:</strong> ${formatVietnameseCurrency(15600000)}</p>
                
                <h4>Sản phẩm trong đơn hàng</h4>
                <div class="vn-order-items">
                    <div class="vn-item">SP001 - Sản phẩm A (x2) - ${formatVietnameseCurrency(500000)}</div>
                    <div class="vn-item">SP002 - Sản phẩm B (x1) - ${formatVietnameseCurrency(180000)}</div>
                </div>
            </div>
        `
    });
}

function editProduct(productCode) {
    // In real app, this would fetch product details and show edit form
    showNotification(`Chỉnh sửa sản phẩm ${productCode}`, 'info');
}

function viewTransactionDetails(transactionId) {
    // In real app, this would fetch transaction details from API
    showModal('view-details', {
        title: `Chi tiết giao dịch ${transactionId}`,
        content: `
            <div class="vn-details-container">
                <h4>Thông tin giao dịch</h4>
                <p><strong>Mã giao dịch:</strong> ${transactionId}</p>
                <p><strong>Loại:</strong> <span class="vn-status-badge success">Thu</span></p>
                <p><strong>Số tiền:</strong> ${formatVietnameseCurrency(15600000)}</p>
                <p><strong>Mô tả:</strong> Thanh toán đơn hàng DH001</p>
                <p><strong>Ngày giao dịch:</strong> ${formatVietnameseDate('2024-01-15')}</p>
            </div>
        `
    });
}

// ===== HEALTH CHECK =====
async function checkAPIHealth() {
    try {
        const health = await apiClient.healthCheck();
        console.log('API Health:', health);
        return health.status === 'ok';
    } catch (error) {
        console.error('API Health check failed:', error);
        return false;
    }
}

// ===== VIETNAMESE AI SUGGESTIONS =====
const vietnameseAISuggestions = [
    "Kiểm tra tồn kho sản phẩm SP001",
    "Tạo đơn hàng cho khách hàng ABC",
    "Xem báo cáo doanh thu tháng này",
    "Kiểm tra công nợ khách hàng XYZ",
    "Cập nhật giá sản phẩm SP002",
    "Xem danh sách đơn hàng chưa giao",
    "Thống kê sản phẩm bán chạy nhất",
    "Kiểm tra lượng hàng nhập tháng trước"
];

function setupAISuggestions() {
    const chatInput = document.getElementById('chat-input');
    if (!chatInput) return;
    
    // Add placeholder rotation
    let currentSuggestion = 0;
    setInterval(() => {
        chatInput.placeholder = vietnameseAISuggestions[currentSuggestion];
        currentSuggestion = (currentSuggestion + 1) % vietnameseAISuggestions.length;
    }, 3000);
}

// ===== INITIALIZE API FEATURES =====
document.addEventListener('DOMContentLoaded', function() {
    // Setup AI suggestions
    setupAISuggestions();
    
    // Check API health
    checkAPIHealth().then(isHealthy => {
        if (!isHealthy) {
            showNotification('Không thể kết nối với server AI. Một số tính năng có thể bị hạn chế.', 'warning');
        }
    });
    
    // Make sendMessage available globally
    window.sendMessage = sendMessage;
    
    // Make detail view functions available globally
    window.viewOrderDetails = viewOrderDetails;
    window.editProduct = editProduct;
    window.viewTransactionDetails = viewTransactionDetails;
});

// ===== EXPORT API CLIENT =====
window.apiClient = apiClient;
window.loadOrdersTable = loadOrdersTable;
window.loadProductsTable = loadProductsTable;
window.loadTransactionsTable = loadTransactionsTable;