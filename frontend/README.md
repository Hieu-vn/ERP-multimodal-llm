# ERP AI Pro - Vietnamese UI/UX System 🇻🇳

## Tổng quan

Hệ thống giao diện người dùng ERP AI Pro được thiết kế đặc biệt cho thị trường Việt Nam, tối ưu hóa trải nghiệm người dùng trên các thiết bị Android phổ biến tại Việt Nam và tích hợp sâu với văn hóa kinh doanh Việt Nam.

## ✨ Tính năng chính

### 🎨 Thiết kế phù hợp văn hóa VN
- **Màu sắc**: Sử dụng màu đỏ và vàng truyền thống Việt Nam
- **Typography**: Tối ưu hiển thị tiếng Việt với font Inter
- **Layout**: Bố cục phù hợp thói quen sử dụng của người Việt
- **Icons**: Biểu tượng dễ hiểu cho người dùng Việt Nam

### 📱 Tối ưu mobile Android VN
- **Responsive Design**: Hoạt động tốt trên các thiết bị Android phổ biến
- **Touch Target**: Kích thước nút bấm tối ưu cho ngón tay
- **Performance**: Tối ưu tốc độ trên thiết bị Android cấp thấp
- **Navigation**: Bottom navigation quen thuộc với người dùng Android

### 🧩 Component Library tiếng Việt
- **Forms**: Biểu mẫu với validation tiếng Việt
- **Tables**: Bảng dữ liệu với format số và tiền tệ VN
- **Cards**: Thẻ thông tin với layout phù hợp
- **Modals**: Hộp thoại với ngôn ngữ thân thiện

### 📊 Data Visualization cho business VN
- **Charts**: Biểu đồ với nhãn tiếng Việt
- **KPIs**: Chỉ số hiệu suất theo chuẩn VN
- **Currency**: Định dạng tiền tệ VND chuẩn
- **Dates**: Hiển thị ngày tháng theo format Việt Nam

### ⚡ UX tối ưu cho ERP workflow VN
- **AI Chat**: Trợ lý AI hiểu tiếng Việt
- **Quick Actions**: Thao tác nhanh cho nghiệp vụ VN
- **Notifications**: Thông báo bằng tiếng Việt
- **Keyboard Shortcuts**: Phím tắt tiện lợi

## 🏗️ Cấu trúc thư mục

```
frontend/
├── index.html              # Trang chính
├── styles/
│   ├── main.css            # Styles chính
│   ├── components.css      # Component styles
│   └── vietnamese.css      # Styles đặc trưng VN
├── js/
│   ├── main.js             # Logic chính
│   ├── api.js              # Tích hợp API
│   ├── components.js       # Component logic
│   └── vietnamese.js       # Tính năng VN
└── README.md               # Tài liệu này
```

## 🚀 Cách sử dụng

### 1. Cài đặt

```bash
# Clone repository
git clone <repository-url>

# Navigate to frontend directory
cd frontend

# Start a local server (example with Python)
python -m http.server 8080

# Or with Node.js
npx http-server -p 8080
```

### 2. Mở trình duyệt

```
http://localhost:8080
```

### 3. Kết nối với Backend

Cập nhật URL backend trong `js/api.js`:

```javascript
const API_BASE_URL = 'http://your-backend-url:8000';
```

## 🎨 Design System

### Màu sắc (Colors)

```css
/* Vietnamese Brand Colors */
--vn-primary: #D32F2F;           /* Đỏ Việt Nam */
--vn-secondary: #FFC107;         /* Vàng sao */
--vn-success: #4CAF50;           /* Xanh thành công */
--vn-warning: #FF9800;           /* Cam cảnh báo */
--vn-error: #F44336;             /* Đỏ lỗi */
--vn-info: #2196F3;              /* Xanh thông tin */
```

### Typography

```css
/* Vietnamese Text Optimization */
font-family: 'Inter', 'Segoe UI', Tahoma, sans-serif;
font-feature-settings: "liga" 1;
text-rendering: optimizeLegibility;
```

### Spacing

```css
/* Consistent Spacing */
--vn-spacing-xs: 0.25rem;       /* 4px */
--vn-spacing-sm: 0.5rem;        /* 8px */
--vn-spacing-md: 1rem;          /* 16px */
--vn-spacing-lg: 1.5rem;        /* 24px */
--vn-spacing-xl: 2rem;          /* 32px */
```

## 📱 Responsive Breakpoints

```css
/* Mobile First Approach */
@media (max-width: 768px) { /* Mobile */ }
@media (min-width: 769px) and (max-width: 1024px) { /* Tablet */ }
@media (min-width: 1025px) { /* Desktop */ }

/* Vietnamese Android Specific */
@media (max-width: 360px) { /* Android Low-end */ }
@media (min-width: 361px) and (max-width: 414px) { /* Android Mid-range */ }
```

## 🧩 Components

### KPI Cards

```html
<div class="vn-kpi-card">
    <div class="vn-kpi-icon sales">
        <i class="fas fa-chart-line"></i>
    </div>
    <div class="vn-kpi-content">
        <h3>Doanh thu hôm nay</h3>
        <p class="vn-kpi-value">45,600,000 ₫</p>
        <span class="vn-kpi-change positive">+12.5%</span>
    </div>
</div>
```

### Vietnamese Forms

```html
<form class="vn-form-vn">
    <div class="vn-form-group">
        <label class="vn-form-label">Tên khách hàng <span class="vn-form-required">*</span></label>
        <input type="text" class="vn-form-input" required>
    </div>
</form>
```

### Data Tables

```html
<div class="vn-data-table">
    <div class="vn-table-header">
        <h3>Danh sách đơn hàng</h3>
        <div class="vn-table-search">
            <input type="text" placeholder="Tìm kiếm...">
        </div>
    </div>
    <div class="vn-table-responsive">
        <table class="vn-table">
            <!-- Table content -->
        </table>
    </div>
</div>
```

### Status Badges

```html
<span class="vn-status-badge success">Hoàn thành</span>
<span class="vn-status-badge warning">Đang xử lý</span>
<span class="vn-status-badge error">Đã hủy</span>
```

## 🔧 JavaScript API

### Vietnamese Currency

```javascript
// Format currency
VietnameseCurrency.format(1500000); // "1,500,000 ₫"

// Parse currency
VietnameseCurrency.parse("1,500,000 ₫"); // 1500000

// Convert to words
VietnameseCurrency.convertToWords(1500000); // "1,500,000 đồng"
```

### Vietnamese Validation

```javascript
// Validate tax code
VietnameseValidation.validateTaxCode("0123456789"); // true

// Validate phone number
VietnamesePhone.validate("0901234567"); // true

// Format phone number
VietnamesePhone.format("0901234567"); // "0901 234 567"
```

### Vietnamese Date & Time

```javascript
// Check if working day
VietnameseBusinessCalendar.isWorkingDay(new Date()); // true/false

// Get working days between dates
VietnameseBusinessCalendar.getWorkingDays(startDate, endDate);

// Check holiday
VietnameseBusinessCalendar.isHoliday(new Date()); // null or holiday name
```

### Vietnamese Search

```javascript
// Search with Vietnamese text
VietnameseUtils.searchVietnamese(items, "tim kiem", "name");

// Sort Vietnamese text
VietnameseUtils.sortVietnamese(items, "name", true);

// Remove accents
VietnameseUtils.removeAccents("tiếng việt"); // "tieng viet"
```

## 🎯 AI Chat Integration

### Sử dụng AI Chat

```javascript
// Send message to AI
sendMessage(); // Tự động lấy từ input

// Custom message
apiClient.queryAI("admin", "Kiểm tra tồn kho SP001");
```

### AI Suggestions

```javascript
const suggestions = [
    "Kiểm tra tồn kho sản phẩm SP001",
    "Tạo đơn hàng cho khách hàng ABC",
    "Xem báo cáo doanh thu tháng này"
];
```

## 🎨 Tùy chỉnh giao diện

### Thay đổi màu sắc

```css
:root {
    --vn-primary: #your-color;
    --vn-secondary: #your-color;
}
```

### Thay đổi font

```css
:root {
    --vn-font-family: 'Your Font', sans-serif;
}
```

### Thêm theme mới

```css
.vn-custom-theme {
    --vn-primary: #custom-primary;
    --vn-secondary: #custom-secondary;
}
```

## 📱 Mobile Optimization

### Touch Targets

```css
.vn-mobile-touch {
    min-height: 48px;
    min-width: 48px;
}
```

### Android Specific

```css
/* Android Low-end */
@media (max-width: 360px) {
    .vn-android-low {
        font-size: 14px;
        line-height: 1.8;
    }
}

/* Android Mid-range */
@media (min-width: 361px) and (max-width: 414px) {
    .vn-android-mid {
        font-size: 16px;
        line-height: 1.6;
    }
}
```

## 🔍 Accessibility

### High Contrast Mode

```css
.vn-high-contrast {
    --vn-primary: #000000;
    --vn-white: #FFFFFF;
}
```

### Large Text

```css
.vn-large-text {
    font-size: calc(var(--vn-font-size-base) * 1.5);
    line-height: 1.8;
}
```

### Focus Indicators

```css
.vn-focus-visible {
    outline: 3px solid var(--vn-primary);
    outline-offset: 2px;
}
```

## ⌨️ Keyboard Shortcuts

| Phím tắt | Chức năng |
|----------|-----------|
| Ctrl+K | Mở AI Chat |
| Ctrl+N | Tạo đơn hàng mới |
| Ctrl+D | Về Dashboard |
| Ctrl+B | Bán hàng |
| Ctrl+H | Kho hàng |
| Ctrl+I | Tài chính |

## 🌍 Localization

### Ngôn ngữ

```javascript
// Vietnamese messages
VIETNAMESE_MESSAGES = {
    LOADING: 'Đang tải...',
    SUCCESS: 'Thành công',
    ERROR: 'Có lỗi xảy ra',
    // ...
};
```

### Business Terms

```javascript
// Vietnamese business terms
VIETNAMESE_BUSINESS = {
    CUSTOMER: 'Khách hàng',
    ORDER: 'Đơn hàng',
    INVOICE: 'Hóa đơn',
    // ...
};
```

## 📊 Performance

### Optimization Tips

1. **Lazy Loading**: Load components khi cần
2. **Image Optimization**: Tối ưu hình ảnh cho mobile
3. **Caching**: Cache dữ liệu để giảm tải
4. **Minification**: Nén CSS/JS cho production

### Bundle Size

```bash
# Kiểm tra kích thước bundle
du -sh frontend/

# Tối ưu images
# Sử dụng WebP format cho hình ảnh
```

## 🔒 Security

### Input Validation

```javascript
// Validate Vietnamese input
VietnameseValidation.validateVietnameseText(userInput);

// Sanitize data
function sanitizeInput(input) {
    return input.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
}
```

### XSS Protection

```javascript
// Escape HTML
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
```

## 🚀 Deployment

### Production Build

```bash
# Minify CSS
npx clean-css-cli -o styles/main.min.css styles/main.css

# Minify JS
npx terser js/main.js -o js/main.min.js

# Optimize images
npx imagemin frontend/images/* --out-dir=frontend/images/optimized
```

### Environment Variables

```javascript
// Development
const API_BASE_URL = 'http://localhost:8000';

// Production
const API_BASE_URL = 'https://your-api.com';
```

## 🧪 Testing

### Unit Tests

```javascript
// Test Vietnamese currency formatting
describe('VietnameseCurrency', () => {
    test('format currency correctly', () => {
        expect(VietnameseCurrency.format(1500000)).toBe('1,500,000 ₫');
    });
});
```

### E2E Tests

```javascript
// Test user workflows
describe('Vietnamese ERP Workflow', () => {
    test('create order in Vietnamese', () => {
        // Test order creation flow
    });
});
```

## 🔄 Updates & Maintenance

### Regular Updates

1. **Dependencies**: Cập nhật thư viện định kỳ
2. **Security**: Patch lỗ hổng bảo mật
3. **Performance**: Tối ưu hiệu suất
4. **Features**: Thêm tính năng mới

### Monitoring

```javascript
// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', () => {
        const perfData = performance.getEntriesByType('navigation')[0];
        console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart);
    });
}
```

## 🤝 Contributing

### Quy tắc đóng góp

1. **Code Style**: Tuân thủ coding standards
2. **Comments**: Viết comment bằng tiếng Việt
3. **Testing**: Thêm tests cho tính năng mới
4. **Documentation**: Cập nhật documentation

### Pull Request Process

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Create pull request
5. Code review
6. Merge

## 📚 Resources

### Vietnamese Business

- [Quy định hóa đơn điện tử](https://thuvienphapluat.vn)
- [Chuẩn kế toán Việt Nam](https://mof.gov.vn)
- [Luật doanh nghiệp](https://mica.gov.vn)

### Design Resources

- [Vietnamese UI Patterns](https://ui-patterns.com)
- [Material Design](https://material.io)
- [Vietnamese Typography](https://fonts.google.com)

### Development Tools

- [Vietnamese Input Methods](https://github.com/lamquangminh/vietnamese-input)
- [Vietnamese Date Libraries](https://github.com/lamquangminh/vietnamese-date)
- [Vietnamese Validation](https://github.com/lamquangminh/vietnamese-validation)

## 📞 Support

### Liên hệ hỗ trợ

- **Email**: support@erp-ai-pro.com
- **Discord**: [ERP AI Pro Community](https://discord.gg/erp-ai-pro)
- **GitHub Issues**: [Report Issues](https://github.com/your-repo/issues)

### FAQ

**Q: Làm sao để thay đổi ngôn ngữ?**
A: Hiện tại chỉ hỗ trợ tiếng Việt. Tính năng đa ngôn ngữ sẽ được thêm trong phiên bản tiếp theo.

**Q: Hỗ trợ những trình duyệt nào?**
A: Chrome, Firefox, Safari, Edge (phiên bản mới nhất)

**Q: Làm sao để tích hợp với hệ thống ERP có sẵn?**
A: Xem tài liệu API integration trong `/docs/api.md`

## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

---

**Made with ❤️ for Vietnamese businesses**

**Được phát triển với tình yêu dành cho doanh nghiệp Việt Nam** 🇻🇳