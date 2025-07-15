// ===== VIETNAMESE ERP COMPONENTS =====

// ===== COMPONENT REGISTRY =====
const ComponentRegistry = {
    components: new Map(),
    
    register(name, component) {
        this.components.set(name, component);
    },
    
    get(name) {
        return this.components.get(name);
    },
    
    create(name, props = {}) {
        const Component = this.get(name);
        if (Component) {
            return new Component(props);
        }
        throw new Error(`Component ${name} not found`);
    }
};

// ===== BASE COMPONENT CLASS =====
class BaseComponent {
    constructor(props = {}) {
        this.props = props;
        this.element = null;
        this.state = {};
        this.listeners = [];
    }
    
    render() {
        throw new Error('render() method must be implemented');
    }
    
    mount(container) {
        this.element = this.render();
        container.appendChild(this.element);
        this.afterMount();
        return this;
    }
    
    afterMount() {
        // Override in subclasses
    }
    
    unmount() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
        this.cleanup();
    }
    
    cleanup() {
        // Remove event listeners
        this.listeners.forEach(({ element, event, handler }) => {
            element.removeEventListener(event, handler);
        });
        this.listeners = [];
    }
    
    addEventListener(element, event, handler) {
        element.addEventListener(event, handler);
        this.listeners.push({ element, event, handler });
    }
    
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.update();
    }
    
    update() {
        if (this.element) {
            const newElement = this.render();
            this.element.parentNode.replaceChild(newElement, this.element);
            this.element = newElement;
        }
    }
    
    createElement(tag, props = {}, ...children) {
        const element = document.createElement(tag);
        
        // Set attributes
        Object.entries(props).forEach(([key, value]) => {
            if (key === 'className') {
                element.className = value;
            } else if (key === 'style') {
                Object.assign(element.style, value);
            } else if (key.startsWith('on')) {
                const event = key.slice(2).toLowerCase();
                this.addEventListener(element, event, value);
            } else {
                element.setAttribute(key, value);
            }
        });
        
        // Add children
        children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else if (child instanceof Node) {
                element.appendChild(child);
            }
        });
        
        return element;
    }
}

// ===== VIETNAMESE KPI CARD COMPONENT =====
class VnKPICard extends BaseComponent {
    constructor(props) {
        super(props);
        this.state = {
            value: props.value || 0,
            title: props.title || '',
            change: props.change || 0,
            icon: props.icon || 'fas fa-chart-line',
            type: props.type || 'default'
        };
    }
    
    render() {
        const { value, title, change, icon, type } = this.state;
        const changeClass = change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral';
        
        return this.createElement('div', { className: 'vn-kpi-card' },
            this.createElement('div', { className: `vn-kpi-icon ${type}` },
                this.createElement('i', { className: icon })
            ),
            this.createElement('div', { className: 'vn-kpi-content' },
                this.createElement('h3', {}, title),
                this.createElement('p', { className: 'vn-kpi-value' }, 
                    typeof value === 'number' ? formatVietnameseNumber(value) : value
                ),
                this.createElement('span', { className: `vn-kpi-change ${changeClass}` },
                    change > 0 ? `+${change}%` : `${change}%`
                )
            )
        );
    }
}

// ===== VIETNAMESE DATA TABLE COMPONENT =====
class VnDataTable extends BaseComponent {
    constructor(props) {
        super(props);
        this.state = {
            columns: props.columns || [],
            data: props.data || [],
            searchTerm: '',
            sortColumn: null,
            sortDirection: 'asc',
            currentPage: 1,
            pageSize: props.pageSize || 10
        };
    }
    
    render() {
        const { columns, data, searchTerm } = this.state;
        
        // Filter data based on search
        const filteredData = this.filterData(data, searchTerm);
        
        // Sort data
        const sortedData = this.sortData(filteredData);
        
        // Paginate data
        const paginatedData = this.paginateData(sortedData);
        
        return this.createElement('div', { className: 'vn-data-table' },
            this.renderTableHeader(),
            this.renderTable(paginatedData),
            this.renderPagination(filteredData.length)
        );
    }
    
    renderTableHeader() {
        return this.createElement('div', { className: 'vn-table-header' },
            this.createElement('h3', {}, this.props.title || 'Bảng dữ liệu'),
            this.createElement('div', { className: 'vn-table-search' },
                this.createElement('input', {
                    type: 'text',
                    placeholder: 'Tìm kiếm...',
                    value: this.state.searchTerm,
                    onInput: (e) => this.handleSearch(e.target.value)
                }),
                this.createElement('i', { className: 'fas fa-search' })
            )
        );
    }
    
    renderTable(data) {
        return this.createElement('div', { className: 'vn-table-responsive' },
            this.createElement('table', { className: 'vn-table' },
                this.renderTableHead(),
                this.renderTableBody(data)
            )
        );
    }
    
    renderTableHead() {
        return this.createElement('thead', {},
            this.createElement('tr', {},
                ...this.state.columns.map(column => 
                    this.createElement('th', {
                        onClick: () => this.handleSort(column.key)
                    }, column.title)
                )
            )
        );
    }
    
    renderTableBody(data) {
        return this.createElement('tbody', {},
            ...data.map(row => 
                this.createElement('tr', {},
                    ...this.state.columns.map(column => 
                        this.createElement('td', {}, this.formatCellValue(row[column.key], column))
                    )
                )
            )
        );
    }
    
    renderPagination(totalItems) {
        const totalPages = Math.ceil(totalItems / this.state.pageSize);
        
        if (totalPages <= 1) return null;
        
        return this.createElement('div', { className: 'vn-pagination' },
            this.createElement('button', {
                className: 'vn-btn outline',
                disabled: this.state.currentPage === 1,
                onClick: () => this.goToPage(this.state.currentPage - 1)
            }, 'Trước'),
            this.createElement('span', { className: 'vn-pagination-info' },
                `Trang ${this.state.currentPage} / ${totalPages}`
            ),
            this.createElement('button', {
                className: 'vn-btn outline',
                disabled: this.state.currentPage === totalPages,
                onClick: () => this.goToPage(this.state.currentPage + 1)
            }, 'Sau')
        );
    }
    
    filterData(data, searchTerm) {
        if (!searchTerm) return data;
        
        return data.filter(row => 
            Object.values(row).some(value => 
                String(value).toLowerCase().includes(searchTerm.toLowerCase())
            )
        );
    }
    
    sortData(data) {
        if (!this.state.sortColumn) return data;
        
        return [...data].sort((a, b) => {
            const aVal = a[this.state.sortColumn];
            const bVal = b[this.state.sortColumn];
            
            if (this.state.sortDirection === 'asc') {
                return aVal > bVal ? 1 : -1;
            } else {
                return aVal < bVal ? 1 : -1;
            }
        });
    }
    
    paginateData(data) {
        const startIndex = (this.state.currentPage - 1) * this.state.pageSize;
        return data.slice(startIndex, startIndex + this.state.pageSize);
    }
    
    formatCellValue(value, column) {
        if (column.type === 'currency') {
            return formatVietnameseCurrency(value);
        } else if (column.type === 'date') {
            return formatVietnameseDate(value);
        } else if (column.type === 'number') {
            return formatVietnameseNumber(value);
        }
        return value;
    }
    
    handleSearch(searchTerm) {
        this.setState({ searchTerm, currentPage: 1 });
    }
    
    handleSort(columnKey) {
        const { sortColumn, sortDirection } = this.state;
        
        if (sortColumn === columnKey) {
            this.setState({
                sortDirection: sortDirection === 'asc' ? 'desc' : 'asc'
            });
        } else {
            this.setState({
                sortColumn: columnKey,
                sortDirection: 'asc'
            });
        }
    }
    
    goToPage(page) {
        this.setState({ currentPage: page });
    }
}

// ===== VIETNAMESE MODAL COMPONENT =====
class VnModal extends BaseComponent {
    constructor(props) {
        super(props);
        this.state = {
            isOpen: props.isOpen || false,
            title: props.title || 'Tiêu đề',
            content: props.content || '',
            onClose: props.onClose || (() => {})
        };
    }
    
    render() {
        if (!this.state.isOpen) return this.createElement('div', { style: { display: 'none' } });
        
        return this.createElement('div', { className: 'vn-modal-overlay active' },
            this.createElement('div', { className: 'vn-modal' },
                this.createElement('div', { className: 'vn-modal-header' },
                    this.createElement('h3', {}, this.state.title),
                    this.createElement('button', {
                        className: 'vn-modal-close',
                        onClick: () => this.close()
                    }, this.createElement('i', { className: 'fas fa-times' }))
                ),
                this.createElement('div', { className: 'vn-modal-content' },
                    typeof this.state.content === 'string' 
                        ? this.createElement('div', { innerHTML: this.state.content })
                        : this.state.content
                )
            )
        );
    }
    
    open() {
        this.setState({ isOpen: true });
        document.body.style.overflow = 'hidden';
    }
    
    close() {
        this.setState({ isOpen: false });
        document.body.style.overflow = '';
        this.state.onClose();
    }
    
    afterMount() {
        // Close modal when clicking outside
        this.addEventListener(this.element, 'click', (e) => {
            if (e.target === this.element) {
                this.close();
            }
        });
        
        // Close modal with Escape key
        this.addEventListener(document, 'keydown', (e) => {
            if (e.key === 'Escape' && this.state.isOpen) {
                this.close();
            }
        });
    }
}

// ===== VIETNAMESE FORM COMPONENT =====
class VnForm extends BaseComponent {
    constructor(props) {
        super(props);
        this.state = {
            fields: props.fields || [],
            values: props.values || {},
            errors: {},
            isSubmitting: false,
            onSubmit: props.onSubmit || (() => {})
        };
    }
    
    render() {
        return this.createElement('form', {
            className: 'vn-form-vn',
            onSubmit: (e) => this.handleSubmit(e)
        },
            ...this.state.fields.map(field => this.renderField(field)),
            this.renderSubmitButton()
        );
    }
    
    renderField(field) {
        const { name, label, type, required, options, placeholder } = field;
        const value = this.state.values[name] || '';
        const error = this.state.errors[name];
        
        return this.createElement('div', { className: 'vn-form-group' },
            this.createElement('label', { className: 'vn-form-label' },
                label,
                required && this.createElement('span', { className: 'vn-form-required' }, ' *')
            ),
            this.renderInput(field, value),
            error && this.createElement('span', { className: 'vn-form-error' }, error)
        );
    }
    
    renderInput(field, value) {
        const { name, type, options, placeholder } = field;
        
        if (type === 'select') {
            return this.createElement('select', {
                className: 'vn-form-input',
                value: value,
                onChange: (e) => this.handleInputChange(name, e.target.value)
            },
                this.createElement('option', { value: '' }, 'Chọn...'),
                ...options.map(option => 
                    this.createElement('option', { value: option.value }, option.label)
                )
            );
        } else if (type === 'textarea') {
            return this.createElement('textarea', {
                className: 'vn-form-input',
                value: value,
                placeholder: placeholder,
                onChange: (e) => this.handleInputChange(name, e.target.value)
            });
        } else {
            return this.createElement('input', {
                type: type || 'text',
                className: 'vn-form-input',
                value: value,
                placeholder: placeholder,
                onChange: (e) => this.handleInputChange(name, e.target.value)
            });
        }
    }
    
    renderSubmitButton() {
        return this.createElement('div', { className: 'vn-form-group' },
            this.createElement('button', {
                type: 'submit',
                className: 'vn-btn primary',
                disabled: this.state.isSubmitting
            },
                this.createElement('i', { className: 'fas fa-save' }),
                this.state.isSubmitting ? ' Đang lưu...' : ' Lưu'
            )
        );
    }
    
    handleInputChange(name, value) {
        this.setState({
            values: { ...this.state.values, [name]: value },
            errors: { ...this.state.errors, [name]: null }
        });
    }
    
    handleSubmit(e) {
        e.preventDefault();
        
        const errors = this.validateForm();
        if (Object.keys(errors).length > 0) {
            this.setState({ errors });
            return;
        }
        
        this.setState({ isSubmitting: true });
        this.state.onSubmit(this.state.values)
            .finally(() => {
                this.setState({ isSubmitting: false });
            });
    }
    
    validateForm() {
        const errors = {};
        
        this.state.fields.forEach(field => {
            const { name, required, type } = field;
            const value = this.state.values[name];
            
            if (required && (!value || value.trim() === '')) {
                errors[name] = 'Trường này là bắt buộc';
            } else if (type === 'email' && value && !VietnameseValidation.validateEmail(value)) {
                errors[name] = 'Email không hợp lệ';
            } else if (type === 'phone' && value && !VietnamesePhone.validate(value)) {
                errors[name] = 'Số điện thoại không hợp lệ';
            } else if (type === 'tax-code' && value && !VietnameseValidation.validateTaxCode(value)) {
                errors[name] = 'Mã số thuế không hợp lệ';
            }
        });
        
        return errors;
    }
}

// ===== VIETNAMESE CHART COMPONENT =====
class VnChart extends BaseComponent {
    constructor(props) {
        super(props);
        this.state = {
            type: props.type || 'line',
            data: props.data || {},
            options: props.options || {},
            title: props.title || ''
        };
        this.chartInstance = null;
    }
    
    render() {
        return this.createElement('div', { className: 'vn-chart-card' },
            this.createElement('h3', {}, this.state.title),
            this.createElement('canvas', { id: this.getCanvasId() })
        );
    }
    
    afterMount() {
        this.renderChart();
    }
    
    renderChart() {
        const canvas = this.element.querySelector('canvas');
        const ctx = canvas.getContext('2d');
        
        // Default Vietnamese chart options
        const defaultOptions = {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        usePointStyle: true,
                        font: {
                            family: 'Inter, sans-serif'
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: (value) => {
                            if (this.state.type === 'currency') {
                                return formatVietnameseCurrency(value);
                            }
                            return formatVietnameseNumber(value);
                        }
                    }
                }
            }
        };
        
        const options = { ...defaultOptions, ...this.state.options };
        
        this.chartInstance = new Chart(ctx, {
            type: this.state.type,
            data: this.state.data,
            options: options
        });
    }
    
    getCanvasId() {
        return `chart-${Math.random().toString(36).substr(2, 9)}`;
    }
    
    updateChart(newData) {
        if (this.chartInstance) {
            this.chartInstance.data = newData;
            this.chartInstance.update();
        }
    }
    
    cleanup() {
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }
        super.cleanup();
    }
}

// ===== VIETNAMESE NOTIFICATION COMPONENT =====
class VnNotification extends BaseComponent {
    constructor(props) {
        super(props);
        this.state = {
            message: props.message || '',
            type: props.type || 'info',
            duration: props.duration || 3000,
            isVisible: false
        };
    }
    
    render() {
        const { message, type, isVisible } = this.state;
        
        return this.createElement('div', {
            className: `vn-notification ${type} ${isVisible ? 'show' : ''}`,
            style: {
                position: 'fixed',
                top: '5rem',
                right: '1rem',
                zIndex: 1500,
                transform: isVisible ? 'translateX(0)' : 'translateX(100%)',
                transition: 'transform 0.3s ease-out'
            }
        }, message);
    }
    
    show() {
        this.setState({ isVisible: true });
        
        setTimeout(() => {
            this.hide();
        }, this.state.duration);
    }
    
    hide() {
        this.setState({ isVisible: false });
        
        setTimeout(() => {
            this.unmount();
        }, 300);
    }
}

// ===== VIETNAMESE LOADING COMPONENT =====
class VnLoading extends BaseComponent {
    constructor(props) {
        super(props);
        this.state = {
            message: props.message || 'Đang tải...',
            size: props.size || 'medium'
        };
    }
    
    render() {
        return this.createElement('div', { className: 'vn-loading' },
            this.createElement('div', { className: `vn-loading-spinner ${this.state.size}` }),
            this.createElement('span', {}, this.state.message)
        );
    }
}

// ===== REGISTER COMPONENTS =====
ComponentRegistry.register('VnKPICard', VnKPICard);
ComponentRegistry.register('VnDataTable', VnDataTable);
ComponentRegistry.register('VnModal', VnModal);
ComponentRegistry.register('VnForm', VnForm);
ComponentRegistry.register('VnChart', VnChart);
ComponentRegistry.register('VnNotification', VnNotification);
ComponentRegistry.register('VnLoading', VnLoading);

// ===== UTILITY FUNCTIONS =====
function createComponent(name, props) {
    return ComponentRegistry.create(name, props);
}

function mountComponent(name, props, container) {
    const component = createComponent(name, props);
    return component.mount(container);
}

// ===== VIETNAMESE COMPONENT HELPERS =====
const VnComponents = {
    // Create KPI Card
    createKPICard(props) {
        return createComponent('VnKPICard', props);
    },
    
    // Create Data Table
    createDataTable(props) {
        return createComponent('VnDataTable', props);
    },
    
    // Create Modal
    createModal(props) {
        return createComponent('VnModal', props);
    },
    
    // Create Form
    createForm(props) {
        return createComponent('VnForm', props);
    },
    
    // Create Chart
    createChart(props) {
        return createComponent('VnChart', props);
    },
    
    // Show notification
    showNotification(message, type = 'info', duration = 3000) {
        const notification = createComponent('VnNotification', {
            message,
            type,
            duration
        });
        
        notification.mount(document.body);
        notification.show();
        
        return notification;
    },
    
    // Show loading
    showLoading(message = 'Đang tải...', container = document.body) {
        const loading = createComponent('VnLoading', { message });
        return loading.mount(container);
    }
};

// ===== EXPORT FOR GLOBAL USE =====
window.ComponentRegistry = ComponentRegistry;
window.VnComponents = VnComponents;
window.BaseComponent = BaseComponent;
window.createComponent = createComponent;
window.mountComponent = mountComponent;

// ===== VIETNAMESE FORM FIELD DEFINITIONS =====
const VnFormFields = {
    // Customer form fields
    customerFields: [
        {
            name: 'name',
            label: 'Tên khách hàng',
            type: 'text',
            required: true,
            placeholder: 'Nhập tên khách hàng'
        },
        {
            name: 'email',
            label: 'Email',
            type: 'email',
            placeholder: 'Nhập email'
        },
        {
            name: 'phone',
            label: 'Số điện thoại',
            type: 'phone',
            placeholder: 'Nhập số điện thoại'
        },
        {
            name: 'address',
            label: 'Địa chỉ',
            type: 'textarea',
            placeholder: 'Nhập địa chỉ'
        },
        {
            name: 'taxCode',
            label: 'Mã số thuế',
            type: 'tax-code',
            placeholder: 'Nhập mã số thuế'
        }
    ],
    
    // Product form fields
    productFields: [
        {
            name: 'code',
            label: 'Mã sản phẩm',
            type: 'text',
            required: true,
            placeholder: 'Nhập mã sản phẩm'
        },
        {
            name: 'name',
            label: 'Tên sản phẩm',
            type: 'text',
            required: true,
            placeholder: 'Nhập tên sản phẩm'
        },
        {
            name: 'category',
            label: 'Danh mục',
            type: 'select',
            options: [
                { value: 'electronics', label: 'Điện tử' },
                { value: 'clothing', label: 'Thời trang' },
                { value: 'home', label: 'Gia dụng' }
            ]
        },
        {
            name: 'price',
            label: 'Giá bán',
            type: 'number',
            required: true,
            placeholder: 'Nhập giá bán'
        },
        {
            name: 'quantity',
            label: 'Số lượng',
            type: 'number',
            placeholder: 'Nhập số lượng'
        },
        {
            name: 'description',
            label: 'Mô tả',
            type: 'textarea',
            placeholder: 'Nhập mô tả sản phẩm'
        }
    ],
    
    // Order form fields
    orderFields: [
        {
            name: 'customer',
            label: 'Khách hàng',
            type: 'select',
            required: true,
            options: [] // Will be populated dynamically
        },
        {
            name: 'orderDate',
            label: 'Ngày đặt hàng',
            type: 'date',
            required: true
        },
        {
            name: 'deliveryDate',
            label: 'Ngày giao hàng',
            type: 'date'
        },
        {
            name: 'notes',
            label: 'Ghi chú',
            type: 'textarea',
            placeholder: 'Nhập ghi chú đơn hàng'
        }
    ]
};

// Export form fields
window.VnFormFields = VnFormFields;

// ===== INITIALIZE COMPONENTS =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('🧩 Vietnamese components initialized');
});