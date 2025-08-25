// AI Chat Dashboard Class and Main Logic
// Note: This is a separate AI-focused dashboard, renamed to avoid conflicts
frappe.pages['ai-chat-dashboard'].on_page_load = function(wrapper) {
    new AIChatDashboard(wrapper);
};

class AIChatDashboard {
    constructor(wrapper) {
        this.page = frappe.ui.make_app_page({
            parent: wrapper,
            title: 'AI Business Intelligence Dashboard',
            single_column: true
        });
        
        this.page.main.addClass('chatgpt-dashboard-wrapper');
        this.wrapper = $(wrapper);
        this.data = null;
        this.current_module = 'ai_chat';
        this.chat_sessions = [];
        this.current_session = null;
        this.sidebar_visible = true;
        this.chat_history_visible = false;
        
        this.initialize();
    }

    initialize() {
        this.setup_page();
        this.load_data();
        this.add_chatgpt_styles();
        this.render_interface();
        this.setup_event_listeners();
    }

    setup_page() {
        this.page.set_title('AI Business Intelligence Dashboard');
        this.page.clear_inner_toolbar();
        this.page.wrapper.find('.layout-main-section-wrapper').css({
            'padding': '0',
            'margin': '0'
        });
    }

    async load_data() {
        try {
            const response = await frappe.call({
                method: 'vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard.get_dashboard_data'
            });
            this.data = response.message;
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            frappe.msgprint({
                title: 'Error',
                message: 'Failed to load dashboard data. Please refresh the page.',
                indicator: 'red'
            });
        }
    }

    render_interface() {
        this.page.main.html(this.get_main_template());
        this.setup_sidebar();
        this.setup_chat_interface();
        this.render_current_module();
    }

    get_main_template() {
        return `
            <div class="modern-dashboard-container">
                <!-- Enhanced Sidebar -->
                <div class="enhanced-sidebar ${this.sidebar_visible ? 'visible' : ''}">
                    <div class="sidebar-content">
                        <!-- Company & Filters Section -->
                        <div class="company-filters-section">
                            <div class="company-selector">
                                <label>Company</label>
                                <select id="company-filter" class="form-control">
                                    <option value="">Select Company</option>
                                </select>
                            </div>
                            <div class="date-range-selector">
                                <label>Date Range</label>
                                <input type="date" id="from-date" class="form-control">
                                <input type="date" id="to-date" class="form-control">
                            </div>
                        </div>

                        <!-- Navigation Modules -->
                        <div class="navigation-modules">
                            <div class="nav-header">
                                <h3><i class="fa fa-dashboard"></i> Business Intelligence</h3>
                            </div>
                            <div class="nav-items">
                                ${this.get_navigation_items()}
                            </div>
                        </div>

                        <!-- User Actions -->
                        <div class="user-actions-section">
                            <div class="action-buttons">
                                <button class="action-btn chat-history-btn" data-action="toggle-chat-history">
                                    <i class="fa fa-history"></i> Chat History
                                </button>
                                <button class="action-btn desk-btn" data-action="go-to-desk">
                                    <i class="fa fa-home"></i> Desk
                                </button>
                                <button class="action-btn logout-btn" data-action="logout">
                                    <i class="fa fa-sign-out"></i> Logout
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Main Content Area -->
                <div class="main-content-area ${this.current_module === 'ai_chat' ? 'fullscreen-chat' : ''}">
                    <div class="content-container">
                        <div class="dashboard-content" id="dashboard-content">
                            <!-- Dynamic content will be loaded here -->
                        </div>
                    </div>
                </div>

                <!-- Chat History Sidebar -->
                <div class="chat-history-panel ${this.chat_history_visible ? 'visible' : ''}">
                    <div class="chat-history-content">
                        <div class="history-header">
                            <h3><i class="fa fa-comments"></i> Chat Sessions</h3>
                            <button class="btn-new-chat" onclick="dashboard.create_new_chat_session()">
                                <i class="fa fa-plus"></i>
                            </button>
                        </div>
                        <div class="chat-sessions-list" id="chat-sessions-list">
                            <!-- Chat sessions will be loaded here -->
                        </div>
                    </div>
                </div>

                <!-- Sidebar Toggle -->
                <button class="sidebar-toggle-btn ${this.sidebar_visible ? 'active' : ''}" onclick="dashboard.toggle_sidebar()">
                    <i class="fa fa-bars"></i>
                </button>
            </div>
        `;
    }

    get_navigation_items() {
        const modules = [
            { id: 'ai_chat', icon: 'fa-comments', label: 'AI Business Assistant', priority: true },
            { id: 'overview', icon: 'fa-dashboard', label: 'Executive Overview' },
            { id: 'financial', icon: 'fa-line-chart', label: 'Financial Analytics' },
            { id: 'projects', icon: 'fa-tasks', label: 'Project Management' },
            { id: 'hr', icon: 'fa-users', label: 'HR Analytics' },
            { id: 'sales', icon: 'fa-shopping-cart', label: 'Sales Intelligence' },
            { id: 'materials', icon: 'fa-cubes', label: 'Materials Management' },
            { id: 'bank_cash', icon: 'fa-university', label: 'Bank & Cash Flow' },
            { id: 'purchase_orders', icon: 'fa-shopping-bag', label: 'Purchase Orders' },
            { id: 'operations', icon: 'fa-cogs', label: 'Operations' },
            { id: 'risk_management', icon: 'fa-shield', label: 'Risk Management' }
        ];

        return modules.map(module => `
            <div class="nav-item ${module.priority ? 'priority-item' : ''} ${this.current_module === module.id ? 'active' : ''}" 
                 data-module="${module.id}" onclick="dashboard.switch_module('${module.id}')">
                <i class="fa ${module.icon}"></i>
                <span>${module.label}</span>
            </div>
        `).join('');
    }

    setup_sidebar() {
        // Load companies for filter
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Company',
                fields: ['name', 'company_name']
            },
            callback: (r) => {
                if (r.message) {
                    const companySelect = this.page.main.find('#company-filter');
                    r.message.forEach(company => {
                        companySelect.append(`<option value="${company.name}">${company.company_name || company.name}</option>`);
                    });
                }
            }
        });

        // Set default date range
        const today = frappe.datetime.get_today();
        const monthAgo = frappe.datetime.add_months(today, -1);
        this.page.main.find('#from-date').val(monthAgo);
        this.page.main.find('#to-date').val(today);
    }

    setup_chat_interface() {
        if (this.current_module === 'ai_chat') {
            this.render_ai_chat_interface();
        }
    }

    switch_module(module_id) {
        this.current_module = module_id;
        
        // Update navigation
        this.page.main.find('.nav-item').removeClass('active');
        this.page.main.find(`[data-module="${module_id}"]`).addClass('active');
        
        // Update main content area
        const mainContent = this.page.main.find('.main-content-area');
        if (module_id === 'ai_chat') {
            mainContent.addClass('fullscreen-chat');
        } else {
            mainContent.removeClass('fullscreen-chat');
        }
        
        this.render_current_module();
    }

    render_current_module() {
        const content = this.page.main.find('#dashboard-content');
        
        switch (this.current_module) {
            case 'ai_chat':
                this.render_ai_chat_interface();
                break;
            case 'overview':
                this.render_overview_dashboard(content);
                break;
            case 'financial':
                this.render_financial_dashboard(content);
                break;
            case 'projects':
                this.render_projects_dashboard(content);
                break;
            case 'hr':
                this.render_hr_dashboard(content);
                break;
            case 'sales':
                this.render_sales_dashboard(content);
                break;
            case 'materials':
                this.render_materials_dashboard(content);
                break;
            case 'bank_cash':
                this.render_bank_cash_dashboard(content);
                break;
            case 'purchase_orders':
                this.render_purchase_orders_dashboard(content);
                break;
            case 'operations':
                this.render_operations_dashboard(content);
                break;
            case 'risk_management':
                this.render_risk_management_dashboard(content);
                break;
            default:
                content.html('<div class="loading-state">Module not found</div>');
        }
    }

    toggle_sidebar() {
        this.sidebar_visible = !this.sidebar_visible;
        const sidebar = this.page.main.find('.enhanced-sidebar');
        const toggleBtn = this.page.main.find('.sidebar-toggle-btn');
        
        if (this.sidebar_visible) {
            sidebar.addClass('visible');
            toggleBtn.addClass('active');
        } else {
            sidebar.removeClass('visible');
            toggleBtn.removeClass('active');
        }
    }

    toggle_chat_history() {
        this.chat_history_visible = !this.chat_history_visible;
        const panel = this.page.main.find('.chat-history-panel');
        
        if (this.chat_history_visible) {
            panel.addClass('visible');
            this.load_chat_sessions();
        } else {
            panel.removeClass('visible');
        }
    }

    setup_event_listeners() {
        // Action button handlers
        this.page.main.on('click', '[data-action]', (e) => {
            const action = $(e.currentTarget).data('action');
            
            switch (action) {
                case 'toggle-chat-history':
                    this.toggle_chat_history();
                    break;
                case 'go-to-desk':
                    frappe.set_route('');
                    break;
                case 'logout':
                    frappe.app.logout();
                    break;
            }
        });

        // Filter change handlers
        this.page.main.on('change', '#company-filter, #from-date, #to-date', () => {
            this.load_data();
        });
    }

    // Placeholder methods for dashboard rendering (to be implemented in separate modules)
    render_ai_chat_interface() {
        // This will be implemented in ai-chat-module.js
        if (window.AIChatModule) {
            window.AIChatModule.render(this.page.main.find('#dashboard-content'));
        }
    }

    render_overview_dashboard(content) {
        // This will be implemented in overview-module.js
        if (window.OverviewModule) {
            window.OverviewModule.render(content, this.data);
        }
    }

    render_financial_dashboard(content) {
        // This will be implemented in financial-module.js
        if (window.FinancialModule) {
            window.FinancialModule.render(content, this.data);
        }
    }

    render_projects_dashboard(content) {
        // This will be implemented in projects-module.js
        if (window.ProjectsModule) {
            window.ProjectsModule.render(content, this.data);
        }
    }

    render_hr_dashboard(content) {
        // This will be implemented in hr-module.js
        if (window.HRModule) {
            window.HRModule.render(content, this.data);
        }
    }

    render_sales_dashboard(content) {
        // This will be implemented in sales-module.js
        if (window.SalesModule) {
            window.SalesModule.render(content, this.data);
        }
    }

    render_materials_dashboard(content) {
        // This will be implemented in materials-module.js
        if (window.MaterialsModule) {
            window.MaterialsModule.render(content, this.data);
        }
    }

    render_bank_cash_dashboard(content) {
        // This will be implemented in bank-cash-module.js
        if (window.BankCashModule) {
            window.BankCashModule.render(content, this.data);
        }
    }

    render_purchase_orders_dashboard(content) {
        // This will be implemented in purchase-orders-module.js
        if (window.PurchaseOrdersModule) {
            window.PurchaseOrdersModule.render(content, this.data);
        }
    }

    render_operations_dashboard(content) {
        // This will be implemented in operations-module.js
        if (window.OperationsModule) {
            window.OperationsModule.render(content, this.data);
        }
    }

    render_risk_management_dashboard(content) {
        // This will be implemented in risk-management-module.js
        if (window.RiskManagementModule) {
            window.RiskManagementModule.render(content, this.data);
        }
    }

    formatCurrency(amount) {
        if (!amount && amount !== 0) return '0';
        return parseFloat(amount).toLocaleString('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });
    }

    create_new_chat_session() {
        const sessionId = 'session_' + Date.now();
        const newSession = {
            id: sessionId,
            title: 'New Business Query',
            created: new Date(),
            messages: [],
            type: 'business_intelligence'
        };
        
        this.chat_sessions.push(newSession);
        this.current_session = newSession;
        this.load_chat_sessions();
        
        if (this.current_module === 'ai_chat' && window.AIChatModule) {
            window.AIChatModule.switch_session(sessionId);
        }
    }

    load_chat_sessions() {
        const sessionsList = this.page.main.find('#chat-sessions-list');
        if (this.chat_sessions.length === 0) {
            sessionsList.html(`
                <div class="empty-chat-state">
                    <i class="fa fa-comments"></i>
                    <h4>No Chat Sessions</h4>
                    <p>Start a new conversation with your AI Business Assistant</p>
                </div>
            `);
        } else {
            const sessionsHtml = this.chat_sessions.map(session => `
                <div class="chat-session-item ${this.current_session?.id === session.id ? 'active' : ''}" 
                     data-session-id="${session.id}">
                    <div class="session-header">
                        <span class="session-title">${session.title}</span>
                        <div class="session-actions">
                            <button class="btn-edit-session" onclick="dashboard.edit_session('${session.id}')">
                                <i class="fa fa-edit"></i>
                            </button>
                            <button class="btn-delete-session" onclick="dashboard.delete_session('${session.id}')">
                                <i class="fa fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="session-meta">
                        <span class="session-type">${session.type}</span>
                        <span class="session-time">${moment(session.created).fromNow()}</span>
                    </div>
                    <div class="session-stats">
                        <span><i class="fa fa-comment"></i> ${session.messages.length}</span>
                    </div>
                </div>
            `).join('');
            sessionsList.html(sessionsHtml);
        }
    }

    add_chatgpt_styles() {
        // This will be implemented in styles-module.js
        if (window.StylesModule) {
            window.StylesModule.addStyles();
        }
    }
}

// Export for use in main dashboard
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIChatDashboard;
} else {
    window.AIChatDashboard = AIChatDashboard;
}

// Make dashboard globally accessible
window.dashboard = null;

// Initialize when page loads
$(document).ready(function() {
    if (frappe.get_route()[0] === 'comprehensive-executive-dashboard') {
        setTimeout(() => {
            if (window.dashboard) {
                window.dashboard = new AIChatDashboard($('.layout-main-section-wrapper'));
            }
        }, 100);
    }
});
