// ===== VIETNAMESE ERP AI PRO - MAIN JAVASCRIPT =====

// ===== GLOBAL VARIABLES =====
let currentSection = 'dashboard';
let currentUser = {
    name: 'Phạm Khách Hiếu',
    role: 'admin',
    avatar: 'PKH'
};

// ===== INITIALIZE APPLICATION =====
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    updateCurrentDate();
    loadDashboardData();
    
    // Update date every minute
    setInterval(updateCurrentDate, 60000);
});

// ===== INITIALIZE APP =====
function initializeApp() {
    console.log('🚀 Khởi tạo ERP AI Pro...');
    
    // Setup navigation
    setupNavigation();
    
    // Setup modal handlers
    setupModalHandlers();
    
    // Setup Vietnamese formatting
    setupVietnameseFormatting();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    console.log('✅ Khởi tạo hoàn tất!');
}

// ===== NAVIGATION SYSTEM =====
function setupNavigation() {
    const navLinks = document.querySelectorAll('.vn-nav-link, .vn-mobile-nav-item');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetSection = this.getAttribute('href').substring(1);
            navigateToSection(targetSection);
        });
    });
}

function navigateToSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.vn-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        targetSection.classList.add('vn-animate-fade-in');
        
        // Remove animation class after animation completes
        setTimeout(() => {
            targetSection.classList.remove('vn-animate-fade-in');
        }, 300);
    }
    
    // Update navigation active state
    updateNavigationActive(sectionId);
    
    // Update current section
    currentSection = sectionId;
    
    // Load section-specific data
    loadSectionData(sectionId);
}

function updateNavigationActive(sectionId) {
    // Remove active class from all nav links
    const navLinks = document.querySelectorAll('.vn-nav-link, .vn-mobile-nav-item');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to current nav links
    const activeLinks = document.querySelectorAll(`[href="#${sectionId}"]`);
    activeLinks.forEach(link => {
        link.classList.add('active');
    });
}

// ===== DATE AND TIME FORMATTING =====
function updateCurrentDate() {
    const now = new Date();
    const dateElement = document.getElementById('current-date');
    
    if (dateElement) {
        // Vietnamese date format
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            timeZone: 'Asia/Ho_Chi_Minh'
        };
        
        const vietnameseDate = now.toLocaleDateString('vi-VN', options);
        dateElement.textContent = vietnameseDate;
    }
}

// ===== VIETNAMESE FORMATTING =====
function setupVietnameseFormatting() {
    // Setup currency formatting
    setupCurrencyFormatting();
    
    // Setup number formatting
    setupNumberFormatting();
    
    // Setup date formatting
    setupDateFormatting();
}

function formatVietnameseCurrency(amount) {
    if (typeof amount !== 'number') {
        amount = parseFloat(amount) || 0;
    }
    
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatVietnameseNumber(number) {
    if (typeof number !== 'number') {
        number = parseFloat(number) || 0;
    }
    
    return new Intl.NumberFormat('vi-VN').format(number);
}

function formatVietnameseDate(date) {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    
    return date.toLocaleDateString('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

function setupCurrencyFormatting() {
    const currencyElements = document.querySelectorAll('.vn-currency');
    currencyElements.forEach(element => {
        const amount = parseFloat(element.textContent.replace(/[^\d.-]/g, ''));
        element.textContent = formatVietnameseCurrency(amount);
    });
}

function setupNumberFormatting() {
    const numberElements = document.querySelectorAll('.vn-number');
    numberElements.forEach(element => {
        const number = parseFloat(element.textContent.replace(/[^\d.-]/g, ''));
        element.textContent = formatVietnameseNumber(number);
    });
}

function setupDateFormatting() {
    const dateElements = document.querySelectorAll('.vn-date');
    dateElements.forEach(element => {
        const date = new Date(element.textContent);
        element.textContent = formatVietnameseDate(date);
    });
}

// ===== MODAL SYSTEM =====
function setupModalHandlers() {
    const modalOverlay = document.getElementById('modal-overlay');
    
    // Close modal when clicking overlay
    modalOverlay.addEventListener('click', function(e) {
        if (e.target === modalOverlay) {
            closeModal();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
            closeModal();
        }
    });
}

function showModal(type, data = {}) {
    const modalOverlay = document.getElementById('modal-overlay');
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');
    
    let title = '';
    let content = '';
    
    switch (type) {
        case 'create-order':
            title = 'Tạo đơn hàng mới';
            content = createOrderModalContent();
            break;
        case 'add-product':
            title = 'Thêm sản phẩm';
            content = addProductModalContent();
            break;
        case 'create-invoice':
            title = 'Tạo hóa đơn';
            content = createInvoiceModalContent();
            break;
        case 'view-details':
            title = data.title || 'Chi tiết';
            content = data.content || '';
            break;
        default:
            title = 'Thông báo';
            content = '<p>Chức năng đang được phát triển...</p>';
    }
    
    modalTitle.textContent = title;
    modalContent.innerHTML = content;
    
    modalOverlay.classList.add('active');
    
    // Setup form handlers if needed
    setupModalFormHandlers(type);
}

function closeModal() {
    const modalOverlay = document.getElementById('modal-overlay');
    modalOverlay.classList.remove('active');
}

// ===== MODAL CONTENT GENERATORS =====
function createOrderModalContent() {
    return `
        <form class="vn-form-vn" onsubmit="handleCreateOrder(event)">
            <div class="vn-form-group">
                <label class="vn-form-label">Khách hàng <span class="vn-form-required">*</span></label>
                <select class="vn-form-input" required>
                    <option value="">Chọn khách hàng</option>
                    <option value="KH001">Công ty TNHH ABC</option>
                    <option value="KH002">Công ty CP XYZ</option>
                    <option value="KH003">Cửa hàng 123</option>
                </select>
            </div>
            
            <div class="vn-form-group">
                <label class="vn-form-label">Sản phẩm</label>
                <div id="order-products">
                    <div class="vn-product-row">
                        <select class="vn-form-input" style="width: 40%;">
                            <option value="">Chọn sản phẩm</option>
                            <option value="SP001">Sản phẩm A</option>
                            <option value="SP002">Sản phẩm B</option>
                        </select>
                        <input type="number" class="vn-form-input" placeholder="Số lượng" style="width: 20%;">
                        <input type="text" class="vn-form-input" placeholder="Đơn giá" style="width: 25%;">
                        <button type="button" class="vn-btn secondary" onclick="removeProductRow(this)">Xóa</button>
                    </div>
                </div>
                <button type="button" class="vn-btn outline" onclick="addProductRow()">
                    <i class="fas fa-plus"></i> Thêm sản phẩm
                </button>
            </div>
            
            <div class="vn-form-group">
                <label class="vn-form-label">Ghi chú</label>
                <textarea class="vn-form-input" rows="3" placeholder="Nhập ghi chú đơn hàng..."></textarea>
            </div>
            
            <div class="vn-form-group">
                <button type="submit" class="vn-btn primary">
                    <i class="fas fa-save"></i> Tạo đơn hàng
                </button>
                <button type="button" class="vn-btn secondary" onclick="closeModal()">Hủy</button>
            </div>
        </form>
    `;
}

function addProductModalContent() {
    return `
        <form class="vn-form-vn" onsubmit="handleAddProduct(event)">
            <div class="vn-form-group">
                <label class="vn-form-label">Mã sản phẩm <span class="vn-form-required">*</span></label>
                <input type="text" class="vn-form-input" placeholder="Nhập mã sản phẩm" required>
            </div>
            
            <div class="vn-form-group">
                <label class="vn-form-label">Tên sản phẩm <span class="vn-form-required">*</span></label>
                <input type="text" class="vn-form-input" placeholder="Nhập tên sản phẩm" required>
            </div>
            
            <div class="vn-form-group">
                <label class="vn-form-label">Danh mục</label>
                <select class="vn-form-input">
                    <option value="">Chọn danh mục</option>
                    <option value="DM001">Điện tử</option>
                    <option value="DM002">Thời trang</option>
                    <option value="DM003">Gia dụng</option>
                </select>
            </div>
            
            <div class="vn-form-group">
                <label class="vn-form-label">Giá bán <span class="vn-form-required">*</span></label>
                <input type="number" class="vn-form-input" placeholder="Nhập giá bán" required>
            </div>
            
            <div class="vn-form-group">
                <label class="vn-form-label">Số lượng ban đầu</label>
                <input type="number" class="vn-form-input" placeholder="Nhập số lượng" value="0">
            </div>
            
            <div class="vn-form-group">
                <label class="vn-form-label">Mô tả</label>
                <textarea class="vn-form-input" rows="3" placeholder="Nhập mô tả sản phẩm..."></textarea>
            </div>
            
            <div class="vn-form-group">
                <button type="submit" class="vn-btn primary">
                    <i class="fas fa-save"></i> Thêm sản phẩm
                </button>
                <button type="button" class="vn-btn secondary" onclick="closeModal()">Hủy</button>
            </div>
        </form>
    `;
}

function createInvoiceModalContent() {
    return `
        <form class="vn-form-vn" onsubmit="handleCreateInvoice(event)">
            <div class="vn-form-group">
                <label class="vn-form-label">Đơn hàng <span class="vn-form-required">*</span></label>
                <select class="vn-form-input" required>
                    <option value="">Chọn đơn hàng</option>
                    <option value="DH001">DH001 - Công ty TNHH ABC</option>
                    <option value="DH002">DH002 - Công ty CP XYZ</option>
                </select>
            </div>
            
            <div class="vn-form-group">
                <label class="vn-form-label">Loại hóa đơn</label>
                <select class="vn-form-input">
                    <option value="VAT">Hóa đơn VAT</option>
                    <option value="NORMAL">Hóa đơn thường</option>
                </select>
            </div>
            
            <div class="vn-form-group">
                <label class="vn-form-label">Ngày xuất hóa đơn</label>
                <input type="date" class="vn-form-input" value="${new Date().toISOString().split('T')[0]}">
            </div>
            
            <div class="vn-form-group">
                <label class="vn-form-label">Ghi chú</label>
                <textarea class="vn-form-input" rows="3" placeholder="Nhập ghi chú hóa đơn..."></textarea>
            </div>
            
            <div class="vn-form-group">
                <button type="submit" class="vn-btn primary">
                    <i class="fas fa-file-invoice"></i> Tạo hóa đơn
                </button>
                <button type="button" class="vn-btn secondary" onclick="closeModal()">Hủy</button>
            </div>
        </form>
    `;
}

// ===== FORM HANDLERS =====
function setupModalFormHandlers(type) {
    // Setup any specific form handlers based on modal type
    if (type === 'create-order') {
        setupOrderFormHandlers();
    }
}

function setupOrderFormHandlers() {
    // This would setup dynamic product row management
    window.addProductRow = function() {
        const container = document.getElementById('order-products');
        const newRow = document.createElement('div');
        newRow.className = 'vn-product-row';
        newRow.innerHTML = `
            <select class="vn-form-input" style="width: 40%;">
                <option value="">Chọn sản phẩm</option>
                <option value="SP001">Sản phẩm A</option>
                <option value="SP002">Sản phẩm B</option>
            </select>
            <input type="number" class="vn-form-input" placeholder="Số lượng" style="width: 20%;">
            <input type="text" class="vn-form-input" placeholder="Đơn giá" style="width: 25%;">
            <button type="button" class="vn-btn secondary" onclick="removeProductRow(this)">Xóa</button>
        `;
        container.appendChild(newRow);
    };
    
    window.removeProductRow = function(button) {
        const row = button.closest('.vn-product-row');
        const container = document.getElementById('order-products');
        if (container.children.length > 1) {
            row.remove();
        }
    };
}

// ===== FORM SUBMISSION HANDLERS =====
function handleCreateOrder(event) {
    event.preventDefault();
    showNotification('Đơn hàng đã được tạo thành công!', 'success');
    closeModal();
    // Here you would typically send data to the API
}

function handleAddProduct(event) {
    event.preventDefault();
    showNotification('Sản phẩm đã được thêm thành công!', 'success');
    closeModal();
    // Here you would typically send data to the API
}

function handleCreateInvoice(event) {
    event.preventDefault();
    showNotification('Hóa đơn đã được tạo thành công!', 'success');
    closeModal();
    // Here you would typically send data to the API
}

// ===== NOTIFICATION SYSTEM =====
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `vn-notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Hide notification after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// ===== KEYBOARD SHORTCUTS =====
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for AI chat
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            openAIChat();
        }
        
        // Ctrl/Cmd + N for new order
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            showModal('create-order');
        }
        
        // Ctrl/Cmd + D for dashboard
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            navigateToSection('dashboard');
        }
    });
}

// ===== SECTION DATA LOADING =====
function loadSectionData(sectionId) {
    switch (sectionId) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'sales':
            loadSalesData();
            break;
        case 'inventory':
            loadInventoryData();
            break;
        case 'finance':
            loadFinanceData();
            break;
        case 'ai-chat':
            // AI chat is handled separately
            break;
    }
}

function loadDashboardData() {
    // Load dashboard KPIs, charts, etc.
    updateKPICards();
    loadRevenueChart();
    loadTopProducts();
}

function loadSalesData() {
    // Load sales data
    loadOrdersTable();
}

function loadInventoryData() {
    // Load inventory data
    loadProductsTable();
}

function loadFinanceData() {
    // Load finance data
    loadTransactionsTable();
}

// ===== DATA UPDATE FUNCTIONS =====
function updateKPICards() {
    // This would typically fetch real data from the API
    const kpis = [
        { selector: '.vn-kpi-card:nth-child(1) .vn-kpi-value', value: '45,600,000' },
        { selector: '.vn-kpi-card:nth-child(2) .vn-kpi-value', value: '24' },
        { selector: '.vn-kpi-card:nth-child(3) .vn-kpi-value', value: '1,247' },
        { selector: '.vn-kpi-card:nth-child(4) .vn-kpi-value', value: '128,500,000' }
    ];
    
    kpis.forEach(kpi => {
        const element = document.querySelector(kpi.selector);
        if (element) {
            element.textContent = kpi.value;
        }
    });
}

function loadRevenueChart() {
    const canvas = document.getElementById('revenue-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Sample data - in real app, this would come from API
    const data = {
        labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
        datasets: [{
            label: 'Doanh thu (triệu đồng)',
            data: [45, 52, 38, 65, 48, 72, 41],
            borderColor: '#D32F2F',
            backgroundColor: 'rgba(211, 47, 47, 0.1)',
            tension: 0.4
        }]
    };
    
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function loadTopProducts() {
    const container = document.getElementById('top-products');
    if (!container) return;
    
    // Sample data
    const products = [
        { name: 'Sản phẩm A', sales: 156 },
        { name: 'Sản phẩm B', sales: 142 },
        { name: 'Sản phẩm C', sales: 128 },
        { name: 'Sản phẩm D', sales: 95 },
        { name: 'Sản phẩm E', sales: 87 }
    ];
    
    container.innerHTML = products.map(product => `
        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">
            <span>${product.name}</span>
            <span class="vn-font-semibold">${product.sales}</span>
        </div>
    `).join('');
}

// ===== UTILITY FUNCTIONS =====
function openAIChat() {
    navigateToSection('ai-chat');
    
    // Focus on chat input
    setTimeout(() => {
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.focus();
        }
    }, 300);
}

function setupEventListeners() {
    // Setup any additional event listeners
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
}

// ===== EXPORT FUNCTIONS FOR GLOBAL USE =====
window.showModal = showModal;
window.closeModal = closeModal;
window.navigateToSection = navigateToSection;
window.openAIChat = openAIChat;
window.showNotification = showNotification;
window.formatVietnameseCurrency = formatVietnameseCurrency;
window.formatVietnameseNumber = formatVietnameseNumber;
window.formatVietnameseDate = formatVietnameseDate;