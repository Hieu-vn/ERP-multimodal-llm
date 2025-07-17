// ===== VIETNAMESE LOCALIZATION & CULTURAL FEATURES =====

// ===== VIETNAMESE LANGUAGE CONSTANTS =====
const VIETNAMESE_MESSAGES = {
    // General UI Messages
    LOADING: 'Đang tải...',
    SAVING: 'Đang lưu...',
    SUCCESS: 'Thành công',
    ERROR: 'Có lỗi xảy ra',
    CONFIRM: 'Xác nhận',
    CANCEL: 'Hủy',
    SAVE: 'Lưu',
    EDIT: 'Chỉnh sửa',
    DELETE: 'Xóa',
    ADD: 'Thêm',
    SEARCH: 'Tìm kiếm',
    FILTER: 'Lọc',
    EXPORT: 'Xuất',
    IMPORT: 'Nhập',
    PRINT: 'In',
    
    // Business Messages
    ORDER_CREATED: 'Đơn hàng đã được tạo thành công',
    PRODUCT_ADDED: 'Sản phẩm đã được thêm thành công',
    INVOICE_GENERATED: 'Hóa đơn đã được tạo thành công',
    PAYMENT_PROCESSED: 'Thanh toán đã được xử lý',
    STOCK_UPDATED: 'Tồn kho đã được cập nhật',
    
    // Error Messages
    NETWORK_ERROR: 'Lỗi kết nối mạng. Vui lòng thử lại.',
    VALIDATION_ERROR: 'Dữ liệu nhập không hợp lệ',
    PERMISSION_DENIED: 'Bạn không có quyền thực hiện thao tác này',
    SESSION_EXPIRED: 'Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.',
    
    // Status Messages
    PROCESSING: 'Đang xử lý',
    COMPLETED: 'Hoàn thành',
    PENDING: 'Chờ xử lý',
    CANCELLED: 'Đã hủy',
    IN_STOCK: 'Còn hàng',
    OUT_OF_STOCK: 'Hết hàng',
    LOW_STOCK: 'Sắp hết hàng'
};

// ===== VIETNAMESE DATE AND TIME =====
const VIETNAMESE_DATE = {
    DAYS: ['Chủ nhật', 'Thứ hai', 'Thứ ba', 'Thứ tư', 'Thứ năm', 'Thứ sáu', 'Thứ bảy'],
    DAYS_SHORT: ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'],
    MONTHS: [
        'Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
        'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'
    ],
    MONTHS_SHORT: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12']
};

// ===== VIETNAMESE BUSINESS TERMS =====
const VIETNAMESE_BUSINESS = {
    CUSTOMER: 'Khách hàng',
    SUPPLIER: 'Nhà cung cấp',
    PRODUCT: 'Sản phẩm',
    ORDER: 'Đơn hàng',
    INVOICE: 'Hóa đơn',
    PAYMENT: 'Thanh toán',
    RECEIPT: 'Phiếu thu',
    EXPENSE: 'Chi phí',
    REVENUE: 'Doanh thu',
    PROFIT: 'Lợi nhuận',
    INVENTORY: 'Tồn kho',
    WAREHOUSE: 'Kho hàng',
    CATEGORY: 'Danh mục',
    UNIT: 'Đơn vị',
    QUANTITY: 'Số lượng',
    PRICE: 'Giá',
    TOTAL: 'Tổng cộng',
    DISCOUNT: 'Giảm giá',
    TAX: 'Thuế',
    VAT: 'Thuế GTGT',
    SUBTOTAL: 'Tạm tính',
    DEBT: 'Công nợ',
    BALANCE: 'Số dư',
    TRANSACTION: 'Giao dịch'
};

// ===== VIETNAMESE CURRENCY FORMATTING =====
class VietnameseCurrency {
    static format(amount, options = {}) {
        const {
            showSymbol = true,
            useShortForm = false,
            precision = 0
        } = options;
        
        if (typeof amount !== 'number') {
            amount = parseFloat(amount) || 0;
        }
        
        // Convert to Vietnamese number format
        const formatted = new Intl.NumberFormat('vi-VN', {
            minimumFractionDigits: precision,
            maximumFractionDigits: precision
        }).format(amount);
        
        if (!showSymbol) {
            return formatted;
        }
        
        // Use short form for large amounts
        if (useShortForm && amount >= 1000000) {
            if (amount >= 1000000000) {
                return `${(amount / 1000000000).toFixed(1)} tỷ`;
            } else if (amount >= 1000000) {
                return `${(amount / 1000000).toFixed(1)} triệu`;
            }
        }
        
        return `${formatted} ₫`;
    }
    
    static parse(currencyString) {
        // Remove currency symbols and convert to number
        const cleaned = currencyString.replace(/[^\d,.-]/g, '');
        return parseFloat(cleaned.replace(/,/g, '')) || 0;
    }
    
    static convertToWords(amount) {
        // Vietnamese number to words converter
        const ones = ['', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín'];
        const tens = ['', '', 'hai mươi', 'ba mươi', 'bốn mươi', 'năm mươi', 'sáu mươi', 'bảy mươi', 'tám mươi', 'chín mươi'];
        const scales = ['', 'nghìn', 'triệu', 'tỷ'];
        
        // This is a simplified version - full implementation would be more complex
        if (amount === 0) return 'không đồng';
        
        // For demo purposes, return a simple format
        return `${VietnameseCurrency.format(amount, { showSymbol: false })} đồng`;
    }
}

// ===== VIETNAMESE ADDRESS FORMATTING =====
class VietnameseAddress {
    static format(address) {
        const {
            street = '',
            ward = '',
            district = '',
            city = '',
            country = 'Việt Nam'
        } = address;
        
        const parts = [street, ward, district, city, country].filter(Boolean);
        return parts.join(', ');
    }
    
    static parseAddress(addressString) {
        // Basic address parsing for Vietnamese format
        const parts = addressString.split(',').map(part => part.trim());
        
        return {
            street: parts[0] || '',
            ward: parts[1] || '',
            district: parts[2] || '',
            city: parts[3] || '',
            country: parts[4] || 'Việt Nam'
        };
    }
}

// ===== VIETNAMESE TAX CALCULATIONS =====
class VietnameseTax {
    static calculateVAT(amount, rate = 0.1) {
        return amount * rate;
    }
    
    static calculateTotal(amount, vatRate = 0.1) {
        const vat = this.calculateVAT(amount, vatRate);
        return amount + vat;
    }
    
    static formatTaxCode(taxCode) {
        // Vietnamese tax code format: XXXX-XXX-XXX
        const cleaned = taxCode.replace(/[^\d]/g, '');
        if (cleaned.length === 10) {
            return `${cleaned.slice(0, 4)}-${cleaned.slice(4, 7)}-${cleaned.slice(7, 10)}`;
        }
        return taxCode;
    }
}

// ===== VIETNAMESE BUSINESS CALENDAR =====
class VietnameseBusinessCalendar {
    static holidays = {
        // Fixed holidays
        '01-01': 'Tết Dương lịch',
        '04-30': 'Ngày Giải phóng miền Nam',
        '05-01': 'Ngày Quốc tế Lao động',
        '09-02': 'Ngày Quốc khánh',
        
        // Lunar holidays (approximate dates)
        '02-14': 'Tết Nguyên đán', // This would need proper lunar calendar calculation
        '04-15': 'Giỗ Tổ Hùng Vương',
        '08-15': 'Tết Trung thu'
    };
    
    static isHoliday(date) {
        if (!(date instanceof Date)) {
            date = new Date(date);
        }
        
        const monthDay = String(date.getMonth() + 1).padStart(2, '0') + '-' + 
                         String(date.getDate()).padStart(2, '0');
        
        return this.holidays[monthDay] || null;
    }
    
    static isWorkingDay(date) {
        if (!(date instanceof Date)) {
            date = new Date(date);
        }
        
        const dayOfWeek = date.getDay();
        const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
        const isHoliday = this.isHoliday(date);
        
        return !isWeekend && !isHoliday;
    }
    
    static getWorkingDays(startDate, endDate) {
        const days = [];
        const current = new Date(startDate);
        
        while (current <= endDate) {
            if (this.isWorkingDay(current)) {
                days.push(new Date(current));
            }
            current.setDate(current.getDate() + 1);
        }
        
        return days;
    }
}

// ===== VIETNAMESE PHONE NUMBER FORMATTING =====
class VietnamesePhone {
    static format(phoneNumber) {
        const cleaned = phoneNumber.replace(/[^\d]/g, '');
        
        // Vietnamese mobile numbers
        if (cleaned.length === 10 && cleaned.startsWith('0')) {
            return `${cleaned.slice(0, 4)} ${cleaned.slice(4, 7)} ${cleaned.slice(7, 10)}`;
        }
        
        // Vietnamese landline numbers
        if (cleaned.length === 11 && cleaned.startsWith('0')) {
            return `${cleaned.slice(0, 3)} ${cleaned.slice(3, 6)} ${cleaned.slice(6, 10)}`;
        }
        
        return phoneNumber;
    }
    
    static validate(phoneNumber) {
        const cleaned = phoneNumber.replace(/[^\d]/g, '');
        
        // Check Vietnamese mobile patterns
        const mobilePattern = /^(03|05|07|08|09)\d{8}$/;
        const landlinePattern = /^(024|028|0\d{2})\d{7}$/;
        
        return mobilePattern.test(cleaned) || landlinePattern.test(cleaned);
    }
}

// ===== VIETNAMESE INPUT VALIDATION =====
class VietnameseValidation {
    static validateTaxCode(taxCode) {
        const cleaned = taxCode.replace(/[^\d]/g, '');
        return cleaned.length === 10 || cleaned.length === 13;
    }
    
    static validateEmail(email) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailPattern.test(email);
    }
    
    static validateVietnameseText(text) {
        // Allow Vietnamese characters, numbers, and common punctuation
        const vietnamesePattern = /^[a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀẾỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴÝỶỸ\s\d.,;:!?()-]*$/;
        return vietnamesePattern.test(text);
    }
}

// ===== VIETNAMESE SORTING AND SEARCHING =====
class VietnameseUtils {
    static removeAccents(str) {
        return str.normalize('NFD')
                 .replace(/[\u0300-\u036f]/g, '')
                 .replace(/đ/g, 'd')
                 .replace(/Đ/g, 'D');
    }
    
    static searchVietnamese(items, query, field = 'name') {
        const normalizedQuery = this.removeAccents(query.toLowerCase());
        
        return items.filter(item => {
            const text = field ? item[field] : item;
            const normalizedText = this.removeAccents(text.toLowerCase());
            return normalizedText.includes(normalizedQuery);
        });
    }
    
    static sortVietnamese(items, field = 'name', ascending = true) {
        return items.sort((a, b) => {
            const textA = this.removeAccents((field ? a[field] : a).toLowerCase());
            const textB = this.removeAccents((field ? b[field] : b).toLowerCase());
            
            if (ascending) {
                return textA.localeCompare(textB);
            } else {
                return textB.localeCompare(textA);
            }
        });
    }
}

// ===== VIETNAMESE BUSINESS LOGIC =====
class VietnameseBusinessLogic {
    static calculateBusinessDays(startDate, endDate) {
        return VietnameseBusinessCalendar.getWorkingDays(startDate, endDate).length;
    }
    
    static calculateLateFee(amount, daysLate, dailyRate = 0.0005) {
        // 0.05% per day is common in Vietnamese business
        return amount * daysLate * dailyRate;
    }
    
    static generateInvoiceNumber(prefix = 'HD', date = new Date()) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
        
        return `${prefix}${year}${month}${day}${random}`;
    }
    
    static calculateDiscount(amount, discountRate) {
        return amount * (discountRate / 100);
    }
    
    static formatBusinessHours(openTime, closeTime, lunchStart, lunchEnd) {
        return `${openTime} - ${lunchStart}, ${lunchEnd} - ${closeTime}`;
    }
}

// ===== VIETNAMESE UI ENHANCEMENTS =====
class VietnameseUI {
    static initializeVietnameseComponents() {
        // Initialize Vietnamese-specific UI components
        this.setupVietnameseInputs();
        this.setupVietnameseDatePickers();
        this.setupVietnameseNumberInputs();
        this.setupVietnameseSearch();
    }
    
    static setupVietnameseInputs() {
        // Setup IME support for Vietnamese input
        const textInputs = document.querySelectorAll('input[type="text"], textarea');
        textInputs.forEach(input => {
            input.setAttribute('lang', 'vi');
            input.setAttribute('spellcheck', 'true');
        });
    }
    
    static setupVietnameseDatePickers() {
        // Setup date pickers with Vietnamese locale
        const dateInputs = document.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => {
            input.setAttribute('lang', 'vi-VN');
        });
    }
    
    static setupVietnameseNumberInputs() {
        // Setup number inputs with Vietnamese formatting
        const numberInputs = document.querySelectorAll('input[type="number"], .vn-currency-input');
        numberInputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.value) {
                    const number = parseFloat(this.value);
                    if (!isNaN(number)) {
                        this.value = VietnameseCurrency.format(number, { showSymbol: false });
                    }
                }
            });
        });
    }
    
    static setupVietnameseSearch() {
        // Setup search with Vietnamese text support
        const searchInputs = document.querySelectorAll('.vn-search-input');
        searchInputs.forEach(input => {
            input.addEventListener('input', function() {
                const query = this.value;
                if (query.length > 0) {
                    // Trigger Vietnamese search
                    this.dispatchEvent(new CustomEvent('vietnameseSearch', {
                        detail: { query: query }
                    }));
                }
            });
        });
    }
}

// ===== VIETNAMESE NOTIFICATIONS =====
class VietnameseNotifications {
    static showSuccess(message) {
        showNotification(message, 'success');
    }
    
    static showError(message) {
        showNotification(message, 'error');
    }
    
    static showWarning(message) {
        showNotification(message, 'warning');
    }
    
    static showInfo(message) {
        showNotification(message, 'info');
    }
    
    static showBusinessSuccess(action) {
        const messages = {
            'order_created': 'Đơn hàng đã được tạo thành công',
            'product_added': 'Sản phẩm đã được thêm thành công',
            'invoice_generated': 'Hóa đơn đã được tạo thành công',
            'payment_processed': 'Thanh toán đã được xử lý thành công',
            'data_saved': 'Dữ liệu đã được lưu thành công'
        };
        
        this.showSuccess(messages[action] || 'Thao tác thành công');
    }
    
    static showBusinessError(error) {
        const messages = {
            'network_error': 'Lỗi kết nối mạng. Vui lòng thử lại.',
            'validation_error': 'Dữ liệu nhập không hợp lệ. Vui lòng kiểm tra lại.',
            'permission_denied': 'Bạn không có quyền thực hiện thao tác này.',
            'session_expired': 'Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.',
            'server_error': 'Lỗi máy chủ. Vui lòng liên hệ bộ phận hỗ trợ.'
        };
        
        this.showError(messages[error] || 'Đã có lỗi xảy ra. Vui lòng thử lại.');
    }
}

// ===== VIETNAMESE KEYBOARD SHORTCUTS =====
class VietnameseKeyboardShortcuts {
    static setup() {
        document.addEventListener('keydown', (e) => {
            // Vietnamese-specific shortcuts
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                openAIChat();
            }
            
            if (e.ctrlKey && e.key === 'n') {
                e.preventDefault();
                showModal('create-order');
            }
            
            if (e.ctrlKey && e.key === 't') {
                e.preventDefault();
                navigateToSection('dashboard');
            }
            
            if (e.ctrlKey && e.key === 'b') {
                e.preventDefault();
                navigateToSection('sales');
            }
            
            if (e.ctrlKey && e.key === 'h') {
                e.preventDefault();
                navigateToSection('inventory');
            }
            
            if (e.ctrlKey && e.key === 'i') {
                e.preventDefault();
                navigateToSection('finance');
            }
        });
    }
}

// ===== INITIALIZE VIETNAMESE FEATURES =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Vietnamese UI components
    VietnameseUI.initializeVietnameseComponents();
    
    // Setup Vietnamese keyboard shortcuts
    VietnameseKeyboardShortcuts.setup();
    
    // Apply Vietnamese formatting to existing elements
    applyVietnameseFormatting();
    
    console.log('🇻🇳 Vietnamese features initialized');
});

function applyVietnameseFormatting() {
    // Apply Vietnamese formatting to currency elements
    const currencyElements = document.querySelectorAll('.vn-currency-format');
    currencyElements.forEach(element => {
        const amount = parseFloat(element.textContent.replace(/[^\d.-]/g, ''));
        element.textContent = VietnameseCurrency.format(amount);
    });
    
    // Apply Vietnamese formatting to phone elements
    const phoneElements = document.querySelectorAll('.vn-phone-format');
    phoneElements.forEach(element => {
        element.textContent = VietnamesePhone.format(element.textContent);
    });
    
    // Apply Vietnamese formatting to tax code elements
    const taxCodeElements = document.querySelectorAll('.vn-tax-code-format');
    taxCodeElements.forEach(element => {
        element.textContent = VietnameseTax.formatTaxCode(element.textContent);
    });
}

// ===== EXPORT CLASSES AND FUNCTIONS =====
window.VietnameseCurrency = VietnameseCurrency;
window.VietnameseAddress = VietnameseAddress;
window.VietnameseTax = VietnameseTax;
window.VietnameseBusinessCalendar = VietnameseBusinessCalendar;
window.VietnamesePhone = VietnamesePhone;
window.VietnameseValidation = VietnameseValidation;
window.VietnameseUtils = VietnameseUtils;
window.VietnameseBusinessLogic = VietnameseBusinessLogic;
window.VietnameseNotifications = VietnameseNotifications;
window.VIETNAMESE_MESSAGES = VIETNAMESE_MESSAGES;
window.VIETNAMESE_BUSINESS = VIETNAMESE_BUSINESS;