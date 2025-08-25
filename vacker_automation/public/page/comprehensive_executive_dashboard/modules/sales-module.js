class SalesModule {
    constructor() {
        this.chartInstances = new Map();
        this.salesData = [];
        this.leads = [];
        this.opportunities = [];
        this.customers = [];
        this.salesTeam = [];
        this.products = [];
        this.regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East & Africa'];
        this.salesStages = ['Lead', 'Qualified', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost'];
    }

    async render() {
        const container = document.getElementById('sales-content');
        if (!container) return;

        container.innerHTML = `
            <div class="sales-module">
                <!-- Sales KPIs -->
                <div class="sales-kpis">
                    <div class="kpi-grid">
                        <div class="kpi-card">
                            <div class="kpi-icon">💰</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="total-revenue">$0</div>
                                <div class="kpi-label">Total Revenue</div>
                                <div class="kpi-change positive">+15% from last quarter</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">📊</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="monthly-recurring-revenue">$0</div>
                                <div class="kpi-label">Monthly Recurring Revenue</div>
                                <div class="kpi-change positive">+8% MoM growth</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">🎯</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="sales-target-achievement">0%</div>
                                <div class="kpi-label">Target Achievement</div>
                                <div class="kpi-change positive">Quarterly target</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">🔄</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="conversion-rate">0%</div>
                                <div class="kpi-label">Lead Conversion Rate</div>
                                <div class="kpi-change positive">+2.3% improvement</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">⏱️</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="sales-cycle-length">0 days</div>
                                <div class="kpi-label">Avg Sales Cycle</div>
                                <div class="kpi-change negative">-5 days improvement</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">👥</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="new-customers">0</div>
                                <div class="kpi-label">New Customers</div>
                                <div class="kpi-change positive">This month</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Sales Charts Row -->
                <div class="sales-charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Revenue Trend</h3>
                            <div class="chart-controls">
                                <select id="revenue-period">
                                    <option value="monthly">Monthly</option>
                                    <option value="quarterly">Quarterly</option>
                                    <option value="yearly">Yearly</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="revenue-trend-chart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Sales Pipeline</h3>
                            <div class="chart-controls">
                                <select id="pipeline-view">
                                    <option value="stage">By Stage</option>
                                    <option value="value">By Value</option>
                                    <option value="probability">By Probability</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="sales-pipeline-chart"></canvas>
                    </div>
                </div>

                <div class="sales-charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Sales by Region</h3>
                            <div class="chart-controls">
                                <select id="region-metric">
                                    <option value="revenue">Revenue</option>
                                    <option value="deals">Number of Deals</option>
                                    <option value="customers">Customers</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="sales-by-region-chart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Product Performance</h3>
                            <div class="chart-controls">
                                <select id="product-metric">
                                    <option value="revenue">Revenue</option>
                                    <option value="units">Units Sold</option>
                                    <option value="margin">Profit Margin</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="product-performance-chart"></canvas>
                    </div>
                </div>

                <!-- Sales Details Section -->
                <div class="sales-details">
                    <div class="section-tabs">
                        <button class="tab-btn active" data-tab="sales-pipeline">Pipeline</button>
                        <button class="tab-btn" data-tab="leads-management">Leads</button>
                        <button class="tab-btn" data-tab="customer-analysis">Customers</button>
                        <button class="tab-btn" data-tab="team-performance">Team Performance</button>
                        <button class="tab-btn" data-tab="forecasting">Forecasting</button>
                    </div>

                    <div class="tab-content active" id="sales-pipeline">
                        <div class="pipeline-section">
                            <div class="pipeline-overview">
                                <div class="pipeline-stats">
                                    <div class="stat-card">
                                        <h4>Total Pipeline Value</h4>
                                        <div class="stat-value">$2.4M</div>
                                        <div class="stat-description">Across all stages</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Weighted Pipeline</h4>
                                        <div class="stat-value">$1.2M</div>
                                        <div class="stat-description">Probability adjusted</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Deals in Progress</h4>
                                        <div class="stat-value">45</div>
                                        <div class="stat-description">Active opportunities</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Expected Close</h4>
                                        <div class="stat-value">$850K</div>
                                        <div class="stat-description">This quarter</div>
                                    </div>
                                </div>
                            </div>
                            <div class="pipeline-visual">
                                <div class="pipeline-stages">
                                    <div class="stage-column" data-stage="lead">
                                        <div class="stage-header">
                                            <h4>Lead</h4>
                                            <span class="stage-count">25</span>
                                            <span class="stage-value">$650K</span>
                                        </div>
                                        <div class="stage-deals" id="lead-deals">
                                            <!-- Dynamic content -->
                                        </div>
                                    </div>
                                    <div class="stage-column" data-stage="qualified">
                                        <div class="stage-header">
                                            <h4>Qualified</h4>
                                            <span class="stage-count">18</span>
                                            <span class="stage-value">$540K</span>
                                        </div>
                                        <div class="stage-deals" id="qualified-deals">
                                            <!-- Dynamic content -->
                                        </div>
                                    </div>
                                    <div class="stage-column" data-stage="proposal">
                                        <div class="stage-header">
                                            <h4>Proposal</h4>
                                            <span class="stage-count">12</span>
                                            <span class="stage-value">$420K</span>
                                        </div>
                                        <div class="stage-deals" id="proposal-deals">
                                            <!-- Dynamic content -->
                                        </div>
                                    </div>
                                    <div class="stage-column" data-stage="negotiation">
                                        <div class="stage-header">
                                            <h4>Negotiation</h4>
                                            <span class="stage-count">8</span>
                                            <span class="stage-value">$320K</span>
                                        </div>
                                        <div class="stage-deals" id="negotiation-deals">
                                            <!-- Dynamic content -->
                                        </div>
                                    </div>
                                    <div class="stage-column" data-stage="closed">
                                        <div class="stage-header">
                                            <h4>Closed Won</h4>
                                            <span class="stage-count">15</span>
                                            <span class="stage-value">$980K</span>
                                        </div>
                                        <div class="stage-deals" id="closed-deals">
                                            <!-- Dynamic content -->
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="tab-content" id="leads-management">
                        <div class="leads-section">
                            <div class="leads-header">
                                <h3>Lead Management</h3>
                                <div class="leads-controls">
                                    <input type="text" id="leads-search" placeholder="Search leads...">
                                    <select id="lead-source-filter">
                                        <option value="all">All Sources</option>
                                        <option value="website">Website</option>
                                        <option value="referral">Referral</option>
                                        <option value="social-media">Social Media</option>
                                        <option value="email-campaign">Email Campaign</option>
                                        <option value="trade-show">Trade Show</option>
                                    </select>
                                    <select id="lead-status-filter">
                                        <option value="all">All Statuses</option>
                                        <option value="new">New</option>
                                        <option value="contacted">Contacted</option>
                                        <option value="qualified">Qualified</option>
                                        <option value="unqualified">Unqualified</option>
                                    </select>
                                </div>
                            </div>
                            <div class="leads-stats">
                                <div class="stat-row">
                                    <div class="stat-item">
                                        <span class="stat-label">Total Leads</span>
                                        <span class="stat-value">1,245</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">New This Week</span>
                                        <span class="stat-value">87</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">Qualified</span>
                                        <span class="stat-value">342</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">Conversion Rate</span>
                                        <span class="stat-value">27.5%</span>
                                    </div>
                                </div>
                            </div>
                            <div class="leads-table-container">
                                <div class="table-responsive">
                                    <table class="leads-table">
                                        <thead>
                                            <tr>
                                                <th>Lead Name</th>
                                                <th>Company</th>
                                                <th>Source</th>
                                                <th>Status</th>
                                                <th>Score</th>
                                                <th>Assigned To</th>
                                                <th>Last Contact</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody id="leads-table-body">
                                            <!-- Dynamic content -->
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="tab-content" id="customer-analysis">
                        <div class="customer-section">
                            <div class="customer-overview">
                                <div class="customer-stats">
                                    <div class="stat-card">
                                        <h4>Total Customers</h4>
                                        <div class="stat-value">2,847</div>
                                        <div class="stat-description">Active customer base</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Customer Lifetime Value</h4>
                                        <div class="stat-value">$45K</div>
                                        <div class="stat-description">Average CLV</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Customer Retention</h4>
                                        <div class="stat-value">94%</div>
                                        <div class="stat-description">Annual retention rate</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Churn Rate</h4>
                                        <div class="stat-value">6%</div>
                                        <div class="stat-description">Monthly churn</div>
                                    </div>
                                </div>
                            </div>
                            <div class="customer-segmentation">
                                <h4>Customer Segmentation</h4>
                                <div class="segmentation-charts">
                                    <div class="chart-container">
                                        <canvas id="customer-segment-chart"></canvas>
                                    </div>
                                    <div class="chart-container">
                                        <canvas id="customer-value-distribution-chart"></canvas>
                                    </div>
                                </div>
                            </div>
                            <div class="top-customers">
                                <h4>Top Customers by Revenue</h4>
                                <div class="customers-list" id="top-customers-list">
                                    <!-- Dynamic content -->
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="tab-content" id="team-performance">
                        <div class="team-performance-section">
                            <div class="team-overview">
                                <div class="team-stats">
                                    <div class="stat-card">
                                        <h4>Sales Team Size</h4>
                                        <div class="stat-value">24</div>
                                        <div class="stat-description">Active sales reps</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Avg Performance</h4>
                                        <div class="stat-value">112%</div>
                                        <div class="stat-description">Of quota achievement</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Top Performer</h4>
                                        <div class="stat-value">Sarah Kim</div>
                                        <div class="stat-description">145% quota achievement</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Team Revenue</h4>
                                        <div class="stat-value">$8.4M</div>
                                        <div class="stat-description">This quarter</div>
                                    </div>
                                </div>
                            </div>
                            <div class="team-charts">
                                <div class="chart-container">
                                    <h4>Individual Performance</h4>
                                    <canvas id="individual-performance-chart"></canvas>
                                </div>
                                <div class="chart-container">
                                    <h4>Activity Metrics</h4>
                                    <canvas id="activity-metrics-chart"></canvas>
                                </div>
                            </div>
                            <div class="team-leaderboard">
                                <h4>Sales Leaderboard</h4>
                                <div class="table-responsive">
                                    <table class="leaderboard-table">
                                        <thead>
                                            <tr>
                                                <th>Rank</th>
                                                <th>Sales Rep</th>
                                                <th>Revenue</th>
                                                <th>Deals Closed</th>
                                                <th>Quota Achievement</th>
                                                <th>Activity Score</th>
                                                <th>Trend</th>
                                            </tr>
                                        </thead>
                                        <tbody id="leaderboard-table-body">
                                            <!-- Dynamic content -->
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="tab-content" id="forecasting">
                        <div class="forecasting-section">
                            <div class="forecast-overview">
                                <div class="forecast-stats">
                                    <div class="stat-card">
                                        <h4>Q1 Forecast</h4>
                                        <div class="stat-value">$2.8M</div>
                                        <div class="stat-description">Projected revenue</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Forecast Accuracy</h4>
                                        <div class="stat-value">87%</div>
                                        <div class="stat-description">Historical accuracy</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Best Case</h4>
                                        <div class="stat-value">$3.2M</div>
                                        <div class="stat-description">Optimistic scenario</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Worst Case</h4>
                                        <div class="stat-value">$2.1M</div>
                                        <div class="stat-description">Conservative scenario</div>
                                    </div>
                                </div>
                            </div>
                            <div class="forecast-charts">
                                <div class="chart-container">
                                    <h4>Revenue Forecast</h4>
                                    <canvas id="revenue-forecast-chart"></canvas>
                                </div>
                                <div class="chart-container">
                                    <h4>Pipeline Progression</h4>
                                    <canvas id="pipeline-progression-chart"></canvas>
                                </div>
                            </div>
                            <div class="forecast-breakdown">
                                <h4>Forecast Breakdown</h4>
                                <div class="breakdown-table-container">
                                    <div class="table-responsive">
                                        <table class="forecast-table">
                                            <thead>
                                                <tr>
                                                    <th>Month</th>
                                                    <th>Conservative</th>
                                                    <th>Most Likely</th>
                                                    <th>Optimistic</th>
                                                    <th>Actual</th>
                                                    <th>Variance</th>
                                                </tr>
                                            </thead>
                                            <tbody id="forecast-table-body">
                                                <!-- Dynamic content -->
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        await this.initializeSalesData();
        this.renderSalesCharts();
        this.setupEventListeners();
        this.populateSalesTables();
    }

    async initializeSalesData() {
        // Generate sample sales data
        this.opportunities = [
            {
                id: 1,
                name: 'Enterprise Software License',
                company: 'Tech Corp Inc',
                value: 125000,
                stage: 'Proposal',
                probability: 75,
                closeDate: '2025-07-15',
                assignedTo: 'Sarah Kim',
                source: 'Referral'
            },
            {
                id: 2,
                name: 'Cloud Migration Services',
                company: 'Global Industries',
                value: 85000,
                stage: 'Negotiation',
                probability: 60,
                closeDate: '2025-06-30',
                assignedTo: 'Mike Chen',
                source: 'Website'
            },
            {
                id: 3,
                name: 'Consulting Package',
                company: 'StartUp LLC',
                value: 45000,
                stage: 'Qualified',
                probability: 40,
                closeDate: '2025-08-20',
                assignedTo: 'Lisa Johnson',
                source: 'Trade Show'
            }
        ];

        this.leads = [
            {
                id: 1,
                name: 'John Anderson',
                company: 'Anderson Enterprises',
                email: 'john@anderson.com',
                phone: '+1-555-0123',
                source: 'Website',
                status: 'New',
                score: 85,
                assignedTo: 'Sarah Kim',
                lastContact: '2025-05-15'
            },
            {
                id: 2,
                name: 'Maria Rodriguez',
                company: 'Rodriguez Solutions',
                email: 'maria@rodriguez.com',
                phone: '+1-555-0124',
                source: 'Referral',
                status: 'Contacted',
                score: 92,
                assignedTo: 'Mike Chen',
                lastContact: '2025-05-14'
            }
        ];

        this.salesTeam = [
            {
                id: 1,
                name: 'Sarah Kim',
                role: 'Senior Sales Rep',
                revenue: 485000,
                quota: 400000,
                deals: 15,
                activities: 125,
                performance: 121
            },
            {
                id: 2,
                name: 'Mike Chen',
                role: 'Sales Rep',
                revenue: 325000,
                quota: 300000,
                deals: 12,
                activities: 98,
                performance: 108
            },
            {
                id: 3,
                name: 'Lisa Johnson',
                role: 'Sales Rep',
                revenue: 285000,
                quota: 300000,
                deals: 10,
                activities: 87,
                performance: 95
            }
        ];

        this.products = [
            { name: 'Enterprise Suite', revenue: 1250000, units: 45, margin: 65 },
            { name: 'Professional Plan', revenue: 850000, units: 120, margin: 55 },
            { name: 'Starter Package', revenue: 425000, units: 280, margin: 45 },
            { name: 'Consulting Services', revenue: 675000, units: 35, margin: 70 }
        ];

        this.updateSalesKPIs();
    }

    updateSalesKPIs() {
        const totalRevenue = 3200000; // Placeholder
        const mrr = 450000; // Placeholder
        const targetAchievement = 108; // Placeholder
        const conversionRate = 27.5; // Placeholder
        const salesCycle = 42; // Placeholder
        const newCustomers = 28; // Placeholder

        document.getElementById('total-revenue').textContent = `$${(totalRevenue / 1000000).toFixed(1)}M`;
        document.getElementById('monthly-recurring-revenue').textContent = `$${(mrr / 1000).toFixed(0)}K`;
        document.getElementById('sales-target-achievement').textContent = `${targetAchievement}%`;
        document.getElementById('conversion-rate').textContent = `${conversionRate}%`;
        document.getElementById('sales-cycle-length').textContent = `${salesCycle} days`;
        document.getElementById('new-customers').textContent = newCustomers;
    }

    renderSalesCharts() {
        this.renderRevenueTrendChart();
        this.renderSalesPipelineChart();
        this.renderSalesByRegionChart();
        this.renderProductPerformanceChart();
        this.renderCustomerSegmentChart();
        this.renderCustomerValueDistributionChart();
        this.renderIndividualPerformanceChart();
        this.renderActivityMetricsChart();
        this.renderRevenueForecastChart();
        this.renderPipelineProgressionChart();
    }

    renderRevenueTrendChart() {
        const ctx = document.getElementById('revenue-trend-chart');
        if (!ctx) return;

        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const actualRevenue = [280, 320, 285, 340, 375, 420, 395, 450, 485, 520, 0, 0];
        const targetRevenue = [300, 300, 300, 350, 350, 400, 400, 450, 450, 500, 500, 550];

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'Actual Revenue',
                        data: actualRevenue,
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Target Revenue',
                        data: targetRevenue,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderDash: [5, 5],
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Revenue ($K)'
                        }
                    }
                }
            }
        });

        this.chartInstances.set('revenue-trend-chart', chart);
    }

    renderSalesPipelineChart() {
        const ctx = document.getElementById('sales-pipeline-chart');
        if (!ctx) return;

        const stageValues = [650, 540, 420, 320, 250]; // Values in thousands

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Lead', 'Qualified', 'Proposal', 'Negotiation', 'Closing'],
                datasets: [{
                    label: 'Pipeline Value ($K)',
                    data: stageValues,
                    backgroundColor: [
                        '#3498db',
                        '#2ecc71',
                        '#f39c12',
                        '#e67e22',
                        '#e74c3c'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Value ($K)'
                        }
                    }
                }
            }
        });

        this.chartInstances.set('sales-pipeline-chart', chart);
    }

    renderSalesByRegionChart() {
        const ctx = document.getElementById('sales-by-region-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: this.regions,
                datasets: [{
                    data: [1200, 850, 650, 320, 180], // Revenue in thousands
                    backgroundColor: [
                        '#3498db',
                        '#2ecc71',
                        '#f39c12',
                        '#e74c3c',
                        '#9b59b6'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const percentage = ((context.raw / context.dataset.data.reduce((a, b) => a + b, 0)) * 100).toFixed(1);
                                return `${context.label}: $${context.raw}K (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });

        this.chartInstances.set('sales-by-region-chart', chart);
    }

    renderProductPerformanceChart() {
        const ctx = document.getElementById('product-performance-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.products.map(p => p.name),
                datasets: [{
                    label: 'Revenue ($K)',
                    data: this.products.map(p => p.revenue / 1000),
                    backgroundColor: '#2ecc71',
                    yAxisID: 'y'
                }, {
                    label: 'Profit Margin (%)',
                    data: this.products.map(p => p.margin),
                    backgroundColor: '#e74c3c',
                    yAxisID: 'y1',
                    type: 'line'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Revenue ($K)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Margin (%)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });

        this.chartInstances.set('product-performance-chart', chart);
    }

    renderCustomerSegmentChart() {
        const ctx = document.getElementById('customer-segment-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Enterprise', 'Mid-Market', 'Small Business', 'Startup'],
                datasets: [{
                    data: [450, 850, 1200, 347],
                    backgroundColor: [
                        '#3498db',
                        '#2ecc71',
                        '#f39c12',
                        '#e74c3c'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        this.chartInstances.set('customer-segment-chart', chart);
    }

    renderCustomerValueDistributionChart() {
        const ctx = document.getElementById('customer-value-distribution-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['$0-10K', '$10K-50K', '$50K-100K', '$100K-500K', '$500K+'],
                datasets: [{
                    label: 'Number of Customers',
                    data: [1200, 850, 450, 280, 67],
                    backgroundColor: '#3498db'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Customers'
                        }
                    }
                }
            }
        });

        this.chartInstances.set('customer-value-distribution-chart', chart);
    }

    renderIndividualPerformanceChart() {
        const ctx = document.getElementById('individual-performance-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.salesTeam.map(rep => rep.name),
                datasets: [
                    {
                        label: 'Actual Revenue ($K)',
                        data: this.salesTeam.map(rep => rep.revenue / 1000),
                        backgroundColor: '#2ecc71'
                    },
                    {
                        label: 'Quota ($K)',
                        data: this.salesTeam.map(rep => rep.quota / 1000),
                        backgroundColor: '#3498db'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Revenue ($K)'
                        }
                    }
                }
            }
        });

        this.chartInstances.set('individual-performance-chart', chart);
    }

    renderActivityMetricsChart() {
        const ctx = document.getElementById('activity-metrics-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Calls', 'Emails', 'Meetings', 'Demos', 'Proposals', 'Follow-ups'],
                datasets: [{
                    label: 'Team Average',
                    data: [85, 92, 78, 65, 45, 88],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    pointBackgroundColor: '#3498db'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });

        this.chartInstances.set('activity-metrics-chart', chart);
    }

    renderRevenueForecastChart() {
        const ctx = document.getElementById('revenue-forecast-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [
                    {
                        label: 'Actual',
                        data: [280, 320, 285, 340, 0, 0],
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)'
                    },
                    {
                        label: 'Conservative',
                        data: [280, 320, 285, 340, 365, 380],
                        borderColor: '#e74c3c',
                        borderDash: [5, 5]
                    },
                    {
                        label: 'Most Likely',
                        data: [280, 320, 285, 340, 385, 410],
                        borderColor: '#f39c12',
                        borderDash: [5, 5]
                    },
                    {
                        label: 'Optimistic',
                        data: [280, 320, 285, 340, 420, 450],
                        borderColor: '#3498db',
                        borderDash: [5, 5]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Revenue ($K)'
                        }
                    }
                }
            }
        });

        this.chartInstances.set('revenue-forecast-chart', chart);
    }

    renderPipelineProgressionChart() {
        const ctx = document.getElementById('pipeline-progression-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [
                    {
                        label: 'New Opportunities',
                        data: [12, 15, 8, 18],
                        borderColor: '#2ecc71',
                        tension: 0.4
                    },
                    {
                        label: 'Qualified Leads',
                        data: [8, 12, 6, 14],
                        borderColor: '#3498db',
                        tension: 0.4
                    },
                    {
                        label: 'Closed Won',
                        data: [3, 5, 2, 7],
                        borderColor: '#f39c12',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Deals'
                        }
                    }
                }
            }
        });

        this.chartInstances.set('pipeline-progression-chart', chart);
    }

    populateSalesTables() {
        this.populatePipelineDeals();
        this.populateLeadsTable();
        this.populateTopCustomers();
        this.populateLeaderboard();
        this.populateForecastTable();
    }

    populatePipelineDeals() {
        // Populate pipeline visual with deals
        const stages = ['lead', 'qualified', 'proposal', 'negotiation', 'closed'];
        const sampleDeals = {
            lead: [
                { name: 'New Software License', company: 'Tech Corp', value: '$45K', probability: '20%' },
                { name: 'Consulting Project', company: 'Global Inc', value: '$65K', probability: '15%' }
            ],
            qualified: [
                { name: 'Cloud Migration', company: 'Enterprise Ltd', value: '$125K', probability: '40%' },
                { name: 'Training Package', company: 'StartUp Co', value: '$35K', probability: '45%' }
            ],
            proposal: [
                { name: 'System Integration', company: 'Big Corp', value: '$180K', probability: '75%' },
                { name: 'Support Contract', company: 'Medium Biz', value: '$55K', probability: '70%' }
            ],
            negotiation: [
                { name: 'Enterprise Suite', company: 'Large Corp', value: '$250K', probability: '85%' }
            ],
            closed: [
                { name: 'Completed Project', company: 'Happy Client', value: '$95K', probability: '100%' }
            ]
        };

        stages.forEach(stage => {
            const container = document.getElementById(`${stage}-deals`);
            if (container && sampleDeals[stage]) {
                container.innerHTML = sampleDeals[stage].map(deal => `
                    <div class="deal-card">
                        <div class="deal-name">${deal.name}</div>
                        <div class="deal-company">${deal.company}</div>
                        <div class="deal-value">${deal.value}</div>
                        <div class="deal-probability">${deal.probability}</div>
                    </div>
                `).join('');
            }
        });
    }

    populateLeadsTable() {
        const tbody = document.getElementById('leads-table-body');
        if (!tbody) return;

        tbody.innerHTML = this.leads.map(lead => `
            <tr>
                <td>
                    <div class="lead-info">
                        <strong>${lead.name}</strong>
                        <small>${lead.email}</small>
                    </div>
                </td>
                <td>${lead.company}</td>
                <td>
                    <span class="source-badge ${lead.source.toLowerCase().replace(' ', '-')}">${lead.source}</span>
                </td>
                <td>
                    <span class="status-badge ${lead.status.toLowerCase()}">${lead.status}</span>
                </td>
                <td>
                    <div class="score-container">
                        <span class="score-value">${lead.score}</span>
                        <div class="score-bar">
                            <div class="score-fill ${lead.score > 80 ? 'high' : lead.score > 60 ? 'medium' : 'low'}" style="width: ${lead.score}%"></div>
                        </div>
                    </div>
                </td>
                <td>${lead.assignedTo}</td>
                <td>${new Date(lead.lastContact).toLocaleDateString()}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-sm btn-primary" onclick="contactLead(${lead.id})">Contact</button>
                        <button class="btn-sm btn-secondary" onclick="qualifyLead(${lead.id})">Qualify</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    populateTopCustomers() {
        const container = document.getElementById('top-customers-list');
        if (!container) return;

        const topCustomers = [
            { name: 'Enterprise Solutions Inc', revenue: 285000, tier: 'Platinum', satisfaction: 95 },
            { name: 'Global Tech Corp', revenue: 235000, tier: 'Gold', satisfaction: 92 },
            { name: 'Innovation Labs', revenue: 195000, tier: 'Gold', satisfaction: 88 },
            { name: 'Digital Dynamics', revenue: 165000, tier: 'Silver', satisfaction: 90 },
            { name: 'Future Systems', revenue: 145000, tier: 'Silver', satisfaction: 87 }
        ];

        container.innerHTML = topCustomers.map((customer, index) => `
            <div class="customer-item">
                <div class="customer-rank">#${index + 1}</div>
                <div class="customer-info">
                    <div class="customer-name">${customer.name}</div>
                    <div class="customer-tier">
                        <span class="tier-badge ${customer.tier.toLowerCase()}">${customer.tier}</span>
                    </div>
                </div>
                <div class="customer-metrics">
                    <div class="metric">
                        <span class="metric-label">Revenue</span>
                        <span class="metric-value">$${(customer.revenue / 1000).toFixed(0)}K</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Satisfaction</span>
                        <span class="metric-value">${customer.satisfaction}%</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    populateLeaderboard() {
        const tbody = document.getElementById('leaderboard-table-body');
        if (!tbody) return;

        const sortedTeam = [...this.salesTeam].sort((a, b) => b.performance - a.performance);

        tbody.innerHTML = sortedTeam.map((rep, index) => `
            <tr>
                <td>
                    <div class="rank-badge rank-${index + 1}">#${index + 1}</div>
                </td>
                <td>
                    <div class="rep-info">
                        <strong>${rep.name}</strong>
                        <small>${rep.role}</small>
                    </div>
                </td>
                <td>$${(rep.revenue / 1000).toFixed(0)}K</td>
                <td>${rep.deals}</td>
                <td>
                    <div class="quota-achievement">
                        <span class="achievement-value">${rep.performance}%</span>
                        <div class="achievement-bar">
                            <div class="achievement-fill ${rep.performance > 100 ? 'exceeded' : 'progress'}" style="width: ${Math.min(rep.performance, 150)}%"></div>
                        </div>
                    </div>
                </td>
                <td>${rep.activities}</td>
                <td>
                    <div class="trend-indicator ${rep.performance > 100 ? 'up' : 'down'}">
                        ${rep.performance > 100 ? '↗' : '↘'}
                    </div>
                </td>
            </tr>
        `).join('');
    }

    populateForecastTable() {
        const tbody = document.getElementById('forecast-table-body');
        if (!tbody) return;

        const forecastData = [
            { month: 'January', conservative: 280, likely: 320, optimistic: 365, actual: 285, variance: 5 },
            { month: 'February', conservative: 290, likely: 335, optimistic: 380, actual: 340, variance: 5 },
            { month: 'March', conservative: 310, likely: 350, optimistic: 395, actual: 345, variance: -5 },
            { month: 'April', conservative: 320, likely: 365, optimistic: 410, actual: null, variance: null },
            { month: 'May', conservative: 335, likely: 380, optimistic: 425, actual: null, variance: null },
            { month: 'June', conservative: 350, likely: 395, optimistic: 440, actual: null, variance: null }
        ];

        tbody.innerHTML = forecastData.map(data => `
            <tr>
                <td>${data.month}</td>
                <td>$${data.conservative}K</td>
                <td>$${data.likely}K</td>
                <td>$${data.optimistic}K</td>
                <td>${data.actual ? `$${data.actual}K` : '-'}</td>
                <td>
                    ${data.variance !== null ? 
                        `<span class="variance ${data.variance >= 0 ? 'positive' : 'negative'}">${data.variance > 0 ? '+' : ''}${data.variance}%</span>` : 
                        '-'
                    }
                </td>
            </tr>
        `).join('');
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const targetTab = e.target.getAttribute('data-tab');
                this.switchTab(targetTab);
            });
        });

        // Search and filter functionality
        const leadsSearch = document.getElementById('leads-search');
        if (leadsSearch) {
            leadsSearch.addEventListener('input', (e) => {
                this.filterLeads(e.target.value);
            });
        }

        // Chart control listeners
        document.getElementById('revenue-period')?.addEventListener('change', () => {
            this.updateRevenueChart();
        });

        document.getElementById('pipeline-view')?.addEventListener('change', () => {
            this.updatePipelineChart();
        });

        document.getElementById('region-metric')?.addEventListener('change', () => {
            this.updateRegionChart();
        });

        document.getElementById('product-metric')?.addEventListener('change', () => {
            this.updateProductChart();
        });
    }

    switchTab(tabName) {
        // Remove active class from all tabs and content
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

        // Add active class to selected tab and content
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(tabName).classList.add('active');
    }

    filterLeads(searchTerm) {
        const rows = document.querySelectorAll('.leads-table tbody tr');
        rows.forEach(row => {
            const name = row.cells[0].textContent.toLowerCase();
            const company = row.cells[1].textContent.toLowerCase();
            if (name.includes(searchTerm.toLowerCase()) || company.includes(searchTerm.toLowerCase())) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    updateRevenueChart() {
        console.log('Updating revenue chart');
        // Implement chart update logic
    }

    updatePipelineChart() {
        console.log('Updating pipeline chart');
        // Implement chart update logic
    }

    updateRegionChart() {
        console.log('Updating region chart');
        // Implement chart update logic
    }

    updateProductChart() {
        console.log('Updating product chart');
        // Implement chart update logic
    }

    destroy() {
        // Clean up chart instances
        this.chartInstances.forEach(chart => {
            chart.destroy();
        });
        this.chartInstances.clear();
    }
}

// Global functions for table actions
window.contactLead = function(leadId) {
    console.log('Contacting lead:', leadId);
    // Implement lead contact logic
};

window.qualifyLead = function(leadId) {
    console.log('Qualifying lead:', leadId);
    // Implement lead qualification logic
};

// Export the module
window.SalesModule = SalesModule;
