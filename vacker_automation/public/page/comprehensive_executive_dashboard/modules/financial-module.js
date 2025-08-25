/**
 * Enhanced Financial Management Module
 * Handles all financial analytics, GL overview, cash flow, and bank analysis
 */
class FinancialManagementModule {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.charts = {};
        this.data = {};
        this.loading = false;
        this.error_state = false;
        
        // Configuration
        this.config = {
            refresh_interval: 300000, // 5 minutes
            chart_colors: {
                primary: '#1f77b4',
                secondary: '#ff7f0e',
                success: '#2ca02c',
                danger: '#d62728',
                warning: '#ff7f0e',
                info: '#17a2b8'
            },
            animation_duration: 750
        };
    }

    /**
     * Render the financial dashboard with enhanced error handling
     */
    render(content) {
        try {
            this.content = content;
            this.show_loading();
            
            // Load financial data if not already available
            if (!this.has_financial_data()) {
                this.load_financial_data();
            } else {
                this.render_dashboard();
            }
        } catch (error) {
            this.handle_error('render', error);
        }
    }

    /**
     * Check if financial data is available
     */
    has_financial_data() {
        const data = this.dashboard.data;
        return data && (
            data.financial_summary ||
            data.gl_overview ||
            data.cashflow_data ||
            data.bank_cash_analysis
        );
    }

    /**
     * Load financial data with error handling
     */
    async load_financial_data() {
        try {
            this.loading = true;
            
            // Load financial module data
            const financial_data = await this.dashboard.load_module_data('financial');
            
            if (financial_data && !financial_data.error) {
                this.data = financial_data;
                this.render_dashboard();
            } else {
                throw new Error(financial_data?.message || 'Failed to load financial data');
            }
        } catch (error) {
            this.handle_error('load_financial_data', error);
        } finally {
            this.loading = false;
        }
    }

    /**
     * Render the complete financial dashboard
     */
    render_dashboard() {
        try {
            const data = this.get_financial_data();
            
            this.content.html(`
                <div class="financial-dashboard-enhanced">
                    ${this.render_header()}
                    ${this.render_summary_cards(data.financial_summary)}
                    <div class="row mt-4">
                        <div class="col-md-8">
                            ${this.render_financial_charts_section(data)}
                        </div>
                        <div class="col-md-4">
                            ${this.render_kpi_section(data)}
                        </div>
                    </div>
                    <div class="row mt-4">
                        <div class="col-md-6">
                            ${this.render_gl_overview_section(data.gl_overview)}
                        </div>
                        <div class="col-md-6">
                            ${this.render_cashflow_section(data.cashflow_data)}
                        </div>
                    </div>
                    ${this.render_bank_accounts_section(data.bank_cash_analysis)}
                </div>
            `);

            // Initialize charts after DOM is ready
            setTimeout(() => {
                this.initialize_charts(data);
                this.setup_event_handlers();
            }, 100);

        } catch (error) {
            this.handle_error('render_dashboard', error);
        }
    }

    /**
     * Get consolidated financial data
     */
    get_financial_data() {
        const dashboard_data = this.dashboard.data || {};
        const module_data = this.data || {};
        
        return {
            financial_summary: dashboard_data.financial_summary || module_data.financial_summary || this.get_empty_financial_summary(),
            gl_overview: dashboard_data.gl_overview || module_data.gl_overview || {},
            cashflow_data: dashboard_data.cashflow_data || module_data.cashflow_data || {},
            bank_cash_analysis: dashboard_data.bank_cash_analysis || module_data.bank_cash_analysis || {}
        };
    }

    /**
     * Render dashboard header
     */
    render_header() {
        return `
            <div class="financial-header">
                <div class="header-content">
                    <h1><i class="fa fa-line-chart"></i> Financial Analytics Dashboard</h1>
                    <p>Comprehensive financial insights and performance metrics</p>
                </div>
                <div class="header-actions">
                    <button class="btn btn-primary btn-sm" onclick="this.refresh_data()" title="Refresh Data">
                        <i class="fa fa-refresh"></i>
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="this.export_data()" title="Export Data">
                        <i class="fa fa-download"></i>
                    </button>
                    <button class="btn btn-info btn-sm" onclick="this.toggle_advanced_view()" title="Advanced View">
                        <i class="fa fa-cogs"></i>
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Render financial summary cards with enhanced styling
     */
    render_summary_cards(financial_summary) {
        if (!financial_summary) {
            return '<div class="alert alert-warning">Financial summary data not available</div>';
        }

        const cards = [
            {
                title: 'Total Revenue',
                value: this.format_currency(financial_summary.total_revenue || 0),
                icon: 'fa-arrow-up',
                color: 'success',
                change: this.calculate_change(financial_summary.total_revenue, financial_summary.prev_revenue),
                transactions: financial_summary.revenue_transactions || 0
            },
            {
                title: 'Total Expenses',
                value: this.format_currency(financial_summary.total_expenses || 0),
                icon: 'fa-arrow-down',
                color: 'danger',
                change: this.calculate_change(financial_summary.total_expenses, financial_summary.prev_expenses),
                transactions: financial_summary.expense_transactions || 0
            },
            {
                title: 'Net Profit',
                value: this.format_currency(financial_summary.net_profit || 0),
                icon: 'fa-dollar',
                color: financial_summary.net_profit >= 0 ? 'success' : 'danger',
                change: this.calculate_change(financial_summary.net_profit, financial_summary.prev_profit)
            },
            {
                title: 'Profit Margin',
                value: `${(financial_summary.profit_margin || 0).toFixed(1)}%`,
                icon: 'fa-percent',
                color: financial_summary.profit_margin >= 20 ? 'success' : financial_summary.profit_margin >= 10 ? 'warning' : 'danger',
                change: this.calculate_change(financial_summary.profit_margin, financial_summary.prev_margin)
            }
        ];

        return `
            <div class="financial-summary-cards">
                <div class="row">
                    ${cards.map(card => `
                        <div class="col-md-3 col-sm-6">
                            <div class="metric-card ${card.color}">
                                <div class="card-header">
                                    <div class="card-icon">
                                        <i class="fa ${card.icon}"></i>
                                    </div>
                                    <div class="card-title">${card.title}</div>
                                </div>
                                <div class="card-body">
                                    <div class="metric-value">${card.value}</div>
                                    ${card.change ? `<div class="metric-change ${card.change.direction}">${card.change.text}</div>` : ''}
                                    ${card.transactions ? `<div class="metric-meta">${card.transactions} transactions</div>` : ''}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Render financial charts section
     */
    render_financial_charts_section(data) {
        return `
            <div class="financial-charts-section">
                <div class="section-header">
                    <h3><i class="fa fa-bar-chart"></i> Financial Performance</h3>
                    <div class="chart-controls">
                        <select id="chart-period" class="form-control form-control-sm">
                            <option value="monthly">Monthly</option>
                            <option value="quarterly">Quarterly</option>
                            <option value="yearly">Yearly</option>
                        </select>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="financial-performance-chart" width="800" height="400"></canvas>
                </div>
            </div>
        `;
    }

    /**
     * Render KPI section
     */
    render_kpi_section(data) {
        const financial_summary = data.financial_summary || {};
        
        const kpis = [
            {
                label: 'Revenue Growth',
                value: this.calculate_growth_rate(financial_summary.total_revenue, financial_summary.prev_revenue),
                target: 15,
                format: 'percentage'
            },
            {
                label: 'Expense Ratio',
                value: financial_summary.total_revenue ? (financial_summary.total_expenses / financial_summary.total_revenue * 100) : 0,
                target: 80,
                format: 'percentage',
                inverted: true
            },
            {
                label: 'Asset Turnover',
                value: financial_summary.total_assets ? (financial_summary.total_revenue / financial_summary.total_assets) : 0,
                target: 1.2,
                format: 'decimal'
            },
            {
                label: 'ROA',
                value: financial_summary.total_assets ? (financial_summary.net_profit / financial_summary.total_assets * 100) : 0,
                target: 10,
                format: 'percentage'
            }
        ];

        return `
            <div class="financial-kpi-section">
                <div class="section-header">
                    <h3><i class="fa fa-tachometer"></i> Key Performance Indicators</h3>
                </div>
                <div class="kpi-container">
                    ${kpis.map(kpi => `
                        <div class="kpi-item">
                            <div class="kpi-label">${kpi.label}</div>
                            <div class="kpi-value">${this.format_kpi_value(kpi.value, kpi.format)}</div>
                            <div class="kpi-progress">
                                <div class="progress">
                                    <div class="progress-bar ${this.get_kpi_color(kpi.value, kpi.target, kpi.inverted)}" 
                                         style="width: ${this.get_kpi_percentage(kpi.value, kpi.target)}%"></div>
                                </div>
                            </div>
                            <div class="kpi-target">Target: ${this.format_kpi_value(kpi.target, kpi.format)}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Render GL overview section
     */
    render_gl_overview_section(gl_data) {
        if (!gl_data || Object.keys(gl_data).length === 0) {
            return `
                <div class="gl-overview-section">
                    <h3><i class="fa fa-book"></i> General Ledger Overview</h3>
                    <div class="alert alert-info">No GL data available</div>
                </div>
            `;
        }

        return `
            <div class="gl-overview-section">
                <div class="section-header">
                    <h3><i class="fa fa-book"></i> General Ledger Overview</h3>
                </div>
                <div class="gl-content">
                    <div class="account-summary">
                        ${this.render_account_breakdown(gl_data)}
                    </div>
                    <div class="chart-container mt-3">
                        <canvas id="gl-breakdown-chart" width="400" height="300"></canvas>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render cashflow section
     */
    render_cashflow_section(cashflow_data) {
        if (!cashflow_data || Object.keys(cashflow_data).length === 0) {
            return `
                <div class="cashflow-section">
                    <h3><i class="fa fa-exchange"></i> Cash Flow Analysis</h3>
                    <div class="alert alert-info">No cash flow data available</div>
                </div>
            `;
        }

        return `
            <div class="cashflow-section">
                <div class="section-header">
                    <h3><i class="fa fa-exchange"></i> Cash Flow Analysis</h3>
                </div>
                <div class="cashflow-content">
                    <div class="cashflow-summary">
                        ${this.render_cashflow_summary(cashflow_data)}
                    </div>
                    <div class="chart-container mt-3">
                        <canvas id="cashflow-trend-chart" width="400" height="300"></canvas>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render bank accounts section
     */
    render_bank_accounts_section(bank_data) {
        if (!bank_data || !bank_data.bank_accounts) {
            return `
                <div class="row mt-4">
                    <div class="col-md-12">
                        <div class="bank-accounts-section">
                            <h3><i class="fa fa-university"></i> Bank Accounts</h3>
                            <div class="alert alert-info">No bank account data available</div>
                        </div>
                    </div>
                </div>
            `;
        }

        return `
            <div class="row mt-4">
                <div class="col-md-12">
                    <div class="bank-accounts-section">
                        <div class="section-header">
                            <h3><i class="fa fa-university"></i> Bank Accounts Overview</h3>
                            <div class="total-balance">
                                Total Balance: <strong>${this.format_currency(bank_data.total_cash || 0)}</strong>
                            </div>
                        </div>
                        <div class="bank-accounts-table">
                            ${this.render_bank_accounts_table(bank_data.bank_accounts)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Initialize all charts
     */
    initialize_charts(data) {
        try {
            this.create_financial_performance_chart(data);
            this.create_gl_breakdown_chart(data.gl_overview);
            this.create_cashflow_trend_chart(data.cashflow_data);
        } catch (error) {
            console.error('Error initializing charts:', error);
        }
    }

    /**
     * Create financial performance chart
     */
    create_financial_performance_chart(data) {
        const ctx = document.getElementById('financial-performance-chart');
        if (!ctx) return;

        const financial_summary = data.financial_summary || {};
        
        // Sample data - in real implementation, this would come from the server
        const chartData = {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [
                {
                    label: 'Revenue',
                    data: this.generate_sample_data(financial_summary.total_revenue, 6),
                    borderColor: this.config.chart_colors.success,
                    backgroundColor: this.config.chart_colors.success + '20',
                    tension: 0.4
                },
                {
                    label: 'Expenses',
                    data: this.generate_sample_data(financial_summary.total_expenses, 6),
                    borderColor: this.config.chart_colors.danger,
                    backgroundColor: this.config.chart_colors.danger + '20',
                    tension: 0.4
                }
            ]
        };

        this.charts.performance = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: this.config.animation_duration
                },
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => this.format_currency(value)
                        }
                    }
                }
            }
        });
    }

    // ... rest of the methods will continue ...

    /**
     * Utility methods
     */
    format_currency(value) {
        if (!value && value !== 0) return '$0';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }

    calculate_change(current, previous) {
        if (!previous || previous === 0) return null;
        
        const change = ((current - previous) / previous) * 100;
        const direction = change >= 0 ? 'positive' : 'negative';
        const text = `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`;
        
        return { direction, text, value: change };
    }

    calculate_growth_rate(current, previous) {
        if (!previous || previous === 0) return 0;
        return ((current - previous) / previous) * 100;
    }

    format_kpi_value(value, format) {
        switch (format) {
            case 'percentage':
                return `${value.toFixed(1)}%`;
            case 'decimal':
                return value.toFixed(2);
            case 'currency':
                return this.format_currency(value);
            default:
                return value.toString();
        }
    }

    get_kpi_color(value, target, inverted = false) {
        const ratio = value / target;
        const good = inverted ? ratio <= 1 : ratio >= 1;
        
        if (good) return 'progress-bar-success';
        else if (ratio >= 0.8) return 'progress-bar-warning';
        else return 'progress-bar-danger';
    }

    get_kpi_percentage(value, target) {
        return Math.min((value / target) * 100, 100);
    }

    generate_sample_data(base_value, count) {
        const data = [];
        for (let i = 0; i < count; i++) {
            const variation = (Math.random() - 0.5) * 0.3; // ±15% variation
            data.push(base_value * (1 + variation));
        }
        return data;
    }

    get_empty_financial_summary() {
        return {
            total_revenue: 0,
            total_expenses: 0,
            net_profit: 0,
            profit_margin: 0,
            total_assets: 0,
            total_liabilities: 0,
            total_equity: 0,
            revenue_transactions: 0,
            expense_transactions: 0
        };
    }

    show_loading() {
        this.content.html(`
            <div class="loading-state">
                <i class="fa fa-spinner fa-spin"></i> 
                Loading Financial Analytics...
            </div>
        `);
    }

    handle_error(method, error) {
        console.error(`Financial Module Error in ${method}:`, error);
        this.error_state = true;
        
        this.content.html(`
            <div class="error-state">
                <i class="fa fa-exclamation-triangle"></i>
                <h3>Error Loading Financial Data</h3>
                <p>${error.message || 'An unexpected error occurred'}</p>
                <button class="btn btn-primary" onclick="this.retry()">
                    <i class="fa fa-refresh"></i> Retry
                </button>
            </div>
        `);
    }

    retry() {
        this.error_state = false;
        this.render(this.content);
    }

    destroy() {
        // Cleanup charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }
}

// Export for use in main dashboard
window.FinancialManagementModule = FinancialManagementModule;
