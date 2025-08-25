/**
 * Overview Module for Comprehensive Executive Dashboard
 * Provides executive-level overview and summary metrics
 * @class OverviewModule
 */
class OverviewModule {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.charts = {};
    }

    render(content) {
        if (!this.dashboard.data) {
            content.html('<div class="loading-state"><i class="fa fa-spinner fa-spin"></i> Loading overview data...</div>');
            return;
        }

        const data = this.dashboard.data;
        const financial = data.financial_summary || {};
        const sales = data.sales_overview?.sales_summary || {};
        const hr = data.hr_summary?.employee_summary?.[0] || {};
        const projects = data.projects_overview || {};

        content.html(`
            <div class="overview-dashboard">
                <div class="dashboard-header">
                    <h1><i class="fa fa-tachometer"></i> Executive Overview</h1>
                    <p>High-level business metrics and key performance indicators</p>
                </div>

                <!-- Key Performance Indicators -->
                <div class="kpi-grid">
                    <div class="kpi-card revenue">
                        <div class="kpi-icon"><i class="fa fa-money"></i></div>
                        <div class="kpi-content">
                            <h3>Total Revenue</h3>
                            <div class="kpi-value">$${this.formatCurrency(financial.total_revenue || 0)}</div>
                            <div class="kpi-change positive">+12.5% from last month</div>
                        </div>
                    </div>

                    <div class="kpi-card profit">
                        <div class="kpi-icon"><i class="fa fa-line-chart"></i></div>
                        <div class="kpi-content">
                            <h3>Net Profit</h3>
                            <div class="kpi-value">$${this.formatCurrency(financial.total_profit || 0)}</div>
                            <div class="kpi-change ${(financial.profit_margin || 0) > 0 ? 'positive' : 'negative'}">
                                ${(financial.profit_margin || 0).toFixed(1)}% margin
                            </div>
                        </div>
                    </div>

                    <div class="kpi-card customers">
                        <div class="kpi-icon"><i class="fa fa-users"></i></div>
                        <div class="kpi-content">
                            <h3>Active Customers</h3>
                            <div class="kpi-value">${sales.unique_customers || 0}</div>
                            <div class="kpi-change positive">+8.3% growth</div>
                        </div>
                    </div>

                    <div class="kpi-card employees">
                        <div class="kpi-icon"><i class="fa fa-user-tie"></i></div>
                        <div class="kpi-content">
                            <h3>Total Employees</h3>
                            <div class="kpi-value">${hr.total_employees || 0}</div>
                            <div class="kpi-change neutral">${hr.active_employees || 0} active</div>
                        </div>
                    </div>
                </div>

                <!-- Business Health Dashboard -->
                <div class="business-health-section">
                    <h3><i class="fa fa-heartbeat"></i> Business Health Dashboard</h3>
                    <div class="health-indicators">
                        <div class="health-indicator">
                            <span class="indicator-label">Financial Health</span>
                            <div class="health-bar">
                                <div class="health-fill" style="width: ${this.calculateFinancialHealth(financial)}%"></div>
                            </div>
                            <span class="health-score">${this.calculateFinancialHealth(financial)}/100</span>
                        </div>

                        <div class="health-indicator">
                            <span class="indicator-label">Sales Performance</span>
                            <div class="health-bar">
                                <div class="health-fill" style="width: ${this.calculateSalesHealth(sales)}%"></div>
                            </div>
                            <span class="health-score">${this.calculateSalesHealth(sales)}/100</span>
                        </div>

                        <div class="health-indicator">
                            <span class="indicator-label">Operational Efficiency</span>
                            <div class="health-bar">
                                <div class="health-fill" style="width: 78%"></div>
                            </div>
                            <span class="health-score">78/100</span>
                        </div>

                        <div class="health-indicator">
                            <span class="indicator-label">Employee Satisfaction</span>
                            <div class="health-bar">
                                <div class="health-fill" style="width: 85%"></div>
                            </div>
                            <span class="health-score">85/100</span>
                        </div>
                    </div>
                </div>

                <!-- Quick Stats Grid -->
                <div class="quick-stats-grid">
                    <div class="stats-section financial-stats">
                        <h4><i class="fa fa-chart-pie"></i> Financial Overview</h4>
                        <div class="stats-list">
                            <div class="stat-item">
                                <span class="stat-label">Gross Revenue</span>
                                <span class="stat-value">$${this.formatCurrency(financial.gross_revenue || 0)}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Operating Expenses</span>
                                <span class="stat-value">$${this.formatCurrency(financial.total_expenses || 0)}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Cash Flow</span>
                                <span class="stat-value ${(financial.net_cash_flow || 0) >= 0 ? 'positive' : 'negative'}">
                                    $${this.formatCurrency(Math.abs(financial.net_cash_flow || 0))}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div class="stats-section sales-stats">
                        <h4><i class="fa fa-shopping-cart"></i> Sales Performance</h4>
                        <div class="stats-list">
                            <div class="stat-item">
                                <span class="stat-label">Total Orders</span>
                                <span class="stat-value">${sales.total_orders || 0}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Average Order Value</span>
                                <span class="stat-value">$${this.formatCurrency(sales.avg_order_value || 0)}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Conversion Rate</span>
                                <span class="stat-value">3.2%</span>
                            </div>
                        </div>
                    </div>

                    <div class="stats-section projects-stats">
                        <h4><i class="fa fa-tasks"></i> Project Status</h4>
                        <div class="stats-list">
                            <div class="stat-item">
                                <span class="stat-label">Active Projects</span>
                                <span class="stat-value">${projects.active_projects || 0}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Completed This Month</span>
                                <span class="stat-value">${projects.completed_projects || 0}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">On Track</span>
                                <span class="stat-value">${projects.on_track_projects || 0}</span>
                            </div>
                        </div>
                    </div>

                    <div class="stats-section operations-stats">
                        <h4><i class="fa fa-cogs"></i> Operations</h4>
                        <div class="stats-list">
                            <div class="stat-item">
                                <span class="stat-label">Inventory Turnover</span>
                                <span class="stat-value">4.2x</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Quality Score</span>
                                <span class="stat-value">96.8%</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Customer Satisfaction</span>
                                <span class="stat-value">4.7/5.0</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Executive Summary Charts -->
                <div class="executive-charts-section">
                    <h3><i class="fa fa-chart-line"></i> Executive Summary Charts</h3>
                    <div class="charts-grid">
                        <div class="chart-container">
                            <h4>Revenue Trend (Last 6 Months)</h4>
                            <canvas id="revenue-trend-chart" width="400" height="250"></canvas>
                        </div>

                        <div class="chart-container">
                            <h4>Department Performance</h4>
                            <canvas id="department-performance-chart" width="400" height="250"></canvas>
                        </div>

                        <div class="chart-container">
                            <h4>Customer Acquisition</h4>
                            <canvas id="customer-acquisition-chart" width="400" height="250"></canvas>
                        </div>

                        <div class="chart-container">
                            <h4>Expense Breakdown</h4>
                            <canvas id="expense-breakdown-chart" width="400" height="250"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Recent Activity Feed -->
                <div class="activity-feed-section">
                    <h3><i class="fa fa-clock-o"></i> Recent Business Activity</h3>
                    <div class="activity-feed">
                        <div class="activity-item">
                            <div class="activity-icon sales"><i class="fa fa-shopping-cart"></i></div>
                            <div class="activity-content">
                                <div class="activity-title">Large order received from ABC Corp</div>
                                <div class="activity-meta">$45,000 • 2 hours ago</div>
                            </div>
                        </div>

                        <div class="activity-item">
                            <div class="activity-icon hr"><i class="fa fa-user-plus"></i></div>
                            <div class="activity-content">
                                <div class="activity-title">3 new employees onboarded</div>
                                <div class="activity-meta">Engineering Department • 4 hours ago</div>
                            </div>
                        </div>

                        <div class="activity-item">
                            <div class="activity-icon projects"><i class="fa fa-check-circle"></i></div>
                            <div class="activity-content">
                                <div class="activity-title">Project Alpha completed successfully</div>
                                <div class="activity-meta">2 days ahead of schedule • 6 hours ago</div>
                            </div>
                        </div>

                        <div class="activity-item">
                            <div class="activity-icon financial"><i class="fa fa-money"></i></div>
                            <div class="activity-content">
                                <div class="activity-title">Monthly financial report generated</div>
                                <div class="activity-meta">Revenue up 12% YoY • 8 hours ago</div>
                            </div>
                        </div>

                        <div class="activity-item">
                            <div class="activity-icon alert"><i class="fa fa-exclamation-triangle"></i></div>
                            <div class="activity-content">
                                <div class="activity-title">Inventory low for Product X</div>
                                <div class="activity-meta">Reorder recommended • 1 day ago</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `);

        // Render charts
        this.renderExecutiveCharts(data);
    }

    renderExecutiveCharts(data) {
        setTimeout(() => {
            this.renderRevenueTrendChart();
            this.renderDepartmentPerformanceChart();
            this.renderCustomerAcquisitionChart();
            this.renderExpenseBreakdownChart();
        }, 100);
    }

    renderRevenueTrendChart() {
        const ctx = document.getElementById('revenue-trend-chart');
        if (!ctx) return;

        // Sample data - replace with actual data
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        const revenue = [120000, 135000, 118000, 165000, 178000, 195000];

        this.charts.revenueTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Revenue ($)',
                    data: revenue,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + (value / 1000) + 'K';
                            }
                        }
                    }
                }
            }
        });
    }

    renderDepartmentPerformanceChart() {
        const ctx = document.getElementById('department-performance-chart');
        if (!ctx) return;

        this.charts.departmentPerformance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Sales', 'Engineering', 'Marketing', 'Operations', 'HR'],
                datasets: [{
                    label: 'Performance Score',
                    data: [92, 88, 85, 90, 87],
                    backgroundColor: [
                        '#10b981',
                        '#3b82f6',
                        '#f59e0b',
                        '#8b5cf6',
                        '#ef4444'
                    ],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    renderCustomerAcquisitionChart() {
        const ctx = document.getElementById('customer-acquisition-chart');
        if (!ctx) return;

        this.charts.customerAcquisition = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Organic', 'Referral', 'Marketing', 'Social Media'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: [
                        '#10b981',
                        '#3b82f6',
                        '#f59e0b',
                        '#8b5cf6'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    renderExpenseBreakdownChart() {
        const ctx = document.getElementById('expense-breakdown-chart');
        if (!ctx) return;

        this.charts.expenseBreakdown = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Salaries', 'Marketing', 'Operations', 'Technology', 'Other'],
                datasets: [{
                    data: [60, 15, 12, 8, 5],
                    backgroundColor: [
                        '#ef4444',
                        '#f59e0b',
                        '#10b981',
                        '#3b82f6',
                        '#8b5cf6'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    calculateFinancialHealth(financial) {
        // Simple calculation based on profit margin and cash flow
        const profitMargin = financial.profit_margin || 0;
        const cashFlow = financial.net_cash_flow || 0;
        
        let score = 50; // Base score
        if (profitMargin > 0) score += Math.min(profitMargin * 2, 30);
        if (cashFlow > 0) score += 20;
        
        return Math.min(Math.max(score, 0), 100);
    }

    calculateSalesHealth(sales) {
        // Simple calculation based on growth indicators
        const orders = sales.total_orders || 0;
        const customers = sales.unique_customers || 0;
        
        let score = 60; // Base score
        if (orders > 100) score += 20;
        if (customers > 50) score += 20;
        
        return Math.min(Math.max(score, 0), 100);
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }

    destroy() {
        // Clean up charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }
}

// Export the module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OverviewModule;
} else {
    window.OverviewModule = OverviewModule;
}
