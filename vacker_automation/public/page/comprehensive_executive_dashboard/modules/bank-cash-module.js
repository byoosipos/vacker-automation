/**
 * Bank & Cash Flow Management Module
 * Handles banking operations, cash flow analysis, and financial liquidity management
 */

class BankCashModule {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.charts = {};
        this.currentFilters = {
            period: '30',
            account: 'all',
            category: 'all',
            currency: 'all'
        };
    }

    render() {
        return `
            <div class="bank-cash-module">
                <div class="module-header">
                    <h2><i class="fas fa-university"></i> Bank & Cash Management</h2>
                    <div class="module-actions">
                        <button class="btn-primary" onclick="bankCashModule.initiateTransfer()">
                            <i class="fas fa-exchange-alt"></i> Transfer Funds
                        </button>
                        <button class="btn-secondary" onclick="bankCashModule.reconcileAccounts()">
                            <i class="fas fa-balance-scale"></i> Reconcile
                        </button>
                        <button class="btn-secondary" onclick="bankCashModule.exportCashFlowReport()">
                            <i class="fas fa-download"></i> Export Report
                        </button>
                    </div>
                </div>

                <!-- KPIs Row -->
                <div class="kpi-row">
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-wallet"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="totalCashBalance">$2.4M</div>
                            <div class="kpi-label">Total Cash Balance</div>
                            <div class="kpi-change positive">+12.3%</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="monthlyInflow">$487K</div>
                            <div class="kpi-label">Monthly Inflow</div>
                            <div class="kpi-change positive">+8.7%</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-chart-line-down"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="monthlyOutflow">$312K</div>
                            <div class="kpi-label">Monthly Outflow</div>
                            <div class="kpi-change negative">+15.2%</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-piggy-bank"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="netCashFlow">$175K</div>
                            <div class="kpi-label">Net Cash Flow</div>
                            <div class="kpi-change positive">+$42K</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-calendar-day"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="burnRate">45</div>
                            <div class="kpi-label">Days Cash on Hand</div>
                            <div class="kpi-change positive">+12 days</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-percentage"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="liquidityRatio">2.8</div>
                            <div class="kpi-label">Current Ratio</div>
                            <div class="kpi-change positive">+0.3</div>
                        </div>
                    </div>
                </div>

                <!-- Charts Row -->
                <div class="charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Cash Flow Trend</h3>
                            <div class="chart-actions">
                                <select onchange="bankCashModule.updateCashFlowPeriod(this.value)">
                                    <option value="7">Last 7 Days</option>
                                    <option value="30" selected>Last 30 Days</option>
                                    <option value="90">Last 90 Days</option>
                                    <option value="365">Last Year</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="cashFlowChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Account Balances</h3>
                            <div class="chart-actions">
                                <button onclick="bankCashModule.refreshAccountBalances()">
                                    <i class="fas fa-sync-alt"></i>
                                </button>
                            </div>
                        </div>
                        <canvas id="accountBalancesChart"></canvas>
                    </div>
                </div>

                <div class="charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Cash Flow Categories</h3>
                            <div class="chart-actions">
                                <select onchange="bankCashModule.updateCategoryChart(this.value)">
                                    <option value="inflow">Inflow</option>
                                    <option value="outflow">Outflow</option>
                                    <option value="both">Both</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="cashFlowCategoriesChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Liquidity Forecast</h3>
                            <div class="chart-actions">
                                <select onchange="bankCashModule.updateForecastPeriod(this.value)">
                                    <option value="30">Next 30 Days</option>
                                    <option value="90">Next 90 Days</option>
                                    <option value="365">Next Year</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="liquidityForecastChart"></canvas>
                    </div>
                </div>

                <!-- Tabs Section -->
                <div class="tab-container">
                    <div class="tab-buttons">
                        <button class="tab-button active" onclick="bankCashModule.switchTab('accounts')">
                            <i class="fas fa-university"></i> Bank Accounts
                        </button>
                        <button class="tab-button" onclick="bankCashModule.switchTab('transactions')">
                            <i class="fas fa-exchange-alt"></i> Transactions
                        </button>
                        <button class="tab-button" onclick="bankCashModule.switchTab('cashflow')">
                            <i class="fas fa-chart-line"></i> Cash Flow Analysis
                        </button>
                        <button class="tab-button" onclick="bankCashModule.switchTab('forecasting')">
                            <i class="fas fa-crystal-ball"></i> Forecasting
                        </button>
                        <button class="tab-button" onclick="bankCashModule.switchTab('reconciliation')">
                            <i class="fas fa-balance-scale"></i> Reconciliation
                        </button>
                    </div>

                    <div class="tab-content">
                        <!-- Bank Accounts Tab -->
                        <div id="accountsTab" class="tab-pane active">
                            <div class="tab-controls">
                                <div class="account-summary">
                                    <div class="summary-card">
                                        <h4>Operating Accounts</h4>
                                        <div class="summary-value">$1.8M</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Savings Accounts</h4>
                                        <div class="summary-value">$450K</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Investment Accounts</h4>
                                        <div class="summary-value">$150K</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Total Interest Earned</h4>
                                        <div class="summary-value">$2.1K</div>
                                    </div>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="bankCashModule.addBankAccount()">
                                        <i class="fas fa-plus"></i> Add Account
                                    </button>
                                    <button onclick="bankCashModule.syncAllAccounts()">
                                        <i class="fas fa-sync"></i> Sync All
                                    </button>
                                </div>
                            </div>
                            <div class="accounts-grid" id="accountsGrid">
                                <!-- Bank accounts will be populated here -->
                            </div>
                        </div>

                        <!-- Transactions Tab -->
                        <div id="transactionsTab" class="tab-pane">
                            <div class="tab-controls">
                                <div class="transaction-filters">
                                    <input type="date" id="startDate" onchange="bankCashModule.applyTransactionFilters()">
                                    <input type="date" id="endDate" onchange="bankCashModule.applyTransactionFilters()">
                                    <select id="accountFilter" onchange="bankCashModule.applyTransactionFilters()">
                                        <option value="all">All Accounts</option>
                                        <option value="operating">Operating</option>
                                        <option value="savings">Savings</option>
                                        <option value="investment">Investment</option>
                                    </select>
                                    <select id="categoryFilter" onchange="bankCashModule.applyTransactionFilters()">
                                        <option value="all">All Categories</option>
                                        <option value="revenue">Revenue</option>
                                        <option value="expenses">Expenses</option>
                                        <option value="transfers">Transfers</option>
                                    </select>
                                    <input type="text" placeholder="Search transactions..." id="transactionSearch">
                                </div>
                                <div class="action-buttons">
                                    <button onclick="bankCashModule.addTransaction()">
                                        <i class="fas fa-plus"></i> Add Transaction
                                    </button>
                                    <button onclick="bankCashModule.importTransactions()">
                                        <i class="fas fa-upload"></i> Import
                                    </button>
                                    <button onclick="bankCashModule.exportTransactions()">
                                        <i class="fas fa-download"></i> Export
                                    </button>
                                </div>
                            </div>
                            <div class="transactions-table" id="transactionsTable">
                                <!-- Transactions will be populated here -->
                            </div>
                        </div>

                        <!-- Cash Flow Analysis Tab -->
                        <div id="cashflowTab" class="tab-pane">
                            <div class="cashflow-dashboard">
                                <div class="cashflow-metrics">
                                    <div class="metric-card">
                                        <h4>Operating Cash Flow</h4>
                                        <div class="metric-value positive">$234K</div>
                                        <div class="metric-change">+18.5%</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Investing Cash Flow</h4>
                                        <div class="metric-value negative">-$45K</div>
                                        <div class="metric-change">-12.3%</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Financing Cash Flow</h4>
                                        <div class="metric-value negative">-$14K</div>
                                        <div class="metric-change">+5.2%</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Free Cash Flow</h4>
                                        <div class="metric-value positive">$189K</div>
                                        <div class="metric-change">+22.1%</div>
                                    </div>
                                </div>
                                <div class="cashflow-analysis">
                                    <div class="analysis-chart">
                                        <h4>Cash Flow Statement</h4>
                                        <canvas id="cashFlowStatementChart"></canvas>
                                    </div>
                                    <div class="analysis-chart">
                                        <h4>Working Capital Trend</h4>
                                        <canvas id="workingCapitalChart"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Forecasting Tab -->
                        <div id="forecastingTab" class="tab-pane">
                            <div class="tab-controls">
                                <div class="forecast-settings">
                                    <label>Forecast Period:</label>
                                    <select id="forecastPeriod" onchange="bankCashModule.updateForecast()">
                                        <option value="30">30 Days</option>
                                        <option value="90">90 Days</option>
                                        <option value="180">6 Months</option>
                                        <option value="365">1 Year</option>
                                    </select>
                                    <label>Confidence Level:</label>
                                    <select id="confidenceLevel" onchange="bankCashModule.updateForecast()">
                                        <option value="80">80%</option>
                                        <option value="90">90%</option>
                                        <option value="95">95%</option>
                                    </select>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="bankCashModule.runForecast()">
                                        <i class="fas fa-play"></i> Run Forecast
                                    </button>
                                    <button onclick="bankCashModule.saveForecastScenario()">
                                        <i class="fas fa-save"></i> Save Scenario
                                    </button>
                                </div>
                            </div>
                            <div class="forecast-results">
                                <div class="forecast-chart">
                                    <h4>Cash Flow Projection</h4>
                                    <canvas id="cashFlowProjectionChart"></canvas>
                                </div>
                                <div class="forecast-scenarios" id="forecastScenarios">
                                    <!-- Forecast scenarios will be populated here -->
                                </div>
                            </div>
                        </div>

                        <!-- Reconciliation Tab -->
                        <div id="reconciliationTab" class="tab-pane">
                            <div class="tab-controls">
                                <div class="reconciliation-summary">
                                    <div class="summary-card">
                                        <h4>Pending Reconciliations</h4>
                                        <div class="summary-value">5</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Unmatched Transactions</h4>
                                        <div class="summary-value">12</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Discrepancy Amount</h4>
                                        <div class="summary-value">$1,247</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Last Reconciliation</h4>
                                        <div class="summary-value">2 days ago</div>
                                    </div>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="bankCashModule.startReconciliation()">
                                        <i class="fas fa-play"></i> Start Reconciliation
                                    </button>
                                    <button onclick="bankCashModule.autoMatch()">
                                        <i class="fas fa-magic"></i> Auto Match
                                    </button>
                                </div>
                            </div>
                            <div class="reconciliation-workspace" id="reconciliationWorkspace">
                                <!-- Reconciliation workspace will be populated here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderBankCashCharts() {
        this.renderCashFlowChart();
        this.renderAccountBalancesChart();
        this.renderCashFlowCategoriesChart();
        this.renderLiquidityForecastChart();
        this.renderAnalysisCharts();
    }

    renderCashFlowChart() {
        const ctx = document.getElementById('cashFlowChart').getContext('2d');
        
        const days = Array.from({length: 30}, (_, i) => {
            const date = new Date();
            date.setDate(date.getDate() - 29 + i);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });

        this.charts.cashFlow = new Chart(ctx, {
            type: 'line',
            data: {
                labels: days,
                datasets: [{
                    label: 'Cash Inflow',
                    data: Array.from({length: 30}, () => Math.floor(Math.random() * 50000) + 10000),
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Cash Outflow',
                    data: Array.from({length: 30}, () => -(Math.floor(Math.random() * 40000) + 8000)),
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Net Cash Flow',
                    data: Array.from({length: 30}, () => Math.floor(Math.random() * 20000) - 5000),
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    fill: false,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + (value / 1000).toFixed(0) + 'K';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': $' + 
                                       Math.abs(context.parsed.y).toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    renderAccountBalancesChart() {
        const ctx = document.getElementById('accountBalancesChart').getContext('2d');
        
        this.charts.accountBalances = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Operating Account', 'Savings Account', 'Investment Account', 'Petty Cash'],
                datasets: [{
                    data: [1800000, 450000, 150000, 5000],
                    backgroundColor: [
                        '#3498db',
                        '#2ecc71',
                        '#f39c12',
                        '#e74c3c'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed;
                                return context.label + ': $' + (value / 1000).toFixed(0) + 'K';
                            }
                        }
                    }
                }
            }
        });
    }

    renderCashFlowCategoriesChart() {
        const ctx = document.getElementById('cashFlowCategoriesChart').getContext('2d');
        
        this.charts.cashFlowCategories = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Revenue', 'Operating Expenses', 'Capital Expenditure', 'Loan Payments', 'Investments'],
                datasets: [{
                    label: 'Inflow',
                    data: [450000, 0, 0, 0, 25000],
                    backgroundColor: '#2ecc71'
                }, {
                    label: 'Outflow',
                    data: [0, -180000, -45000, -25000, -15000],
                    backgroundColor: '#e74c3c'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + (Math.abs(value) / 1000).toFixed(0) + 'K';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }

    renderLiquidityForecastChart() {
        const ctx = document.getElementById('liquidityForecastChart').getContext('2d');
        
        const forecastDays = Array.from({length: 30}, (_, i) => {
            const date = new Date();
            date.setDate(date.getDate() + i);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });

        this.charts.liquidityForecast = new Chart(ctx, {
            type: 'line',
            data: {
                labels: forecastDays,
                datasets: [{
                    label: 'Projected Cash Balance',
                    data: Array.from({length: 30}, (_, i) => 2400000 + (i * 5000) + (Math.random() * 100000)),
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Minimum Required Balance',
                    data: Array.from({length: 30}, () => 500000),
                    borderColor: '#e74c3c',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    tension: 0
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + (value / 1000000).toFixed(1) + 'M';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }

    renderAnalysisCharts() {
        // Cash Flow Statement Chart
        const statementCtx = document.getElementById('cashFlowStatementChart')?.getContext('2d');
        if (statementCtx) {
            this.charts.cashFlowStatement = new Chart(statementCtx, {
                type: 'bar',
                data: {
                    labels: ['Operating Activities', 'Investing Activities', 'Financing Activities'],
                    datasets: [{
                        label: 'Cash Flow',
                        data: [234000, -45000, -14000],
                        backgroundColor: ['#2ecc71', '#e74c3c', '#f39c12']
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + (value / 1000).toFixed(0) + 'K';
                                }
                            }
                        }
                    }
                }
            });
        }

        // Working Capital Chart
        const workingCapitalCtx = document.getElementById('workingCapitalChart')?.getContext('2d');
        if (workingCapitalCtx) {
            this.charts.workingCapital = new Chart(workingCapitalCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Working Capital',
                        data: [1200000, 1350000, 1180000, 1420000, 1380000, 1450000],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: function(value) {
                                    return '$' + (value / 1000000).toFixed(1) + 'M';
                                }
                            }
                        }
                    }
                }
            });
        }

        // Cash Flow Projection Chart
        const projectionCtx = document.getElementById('cashFlowProjectionChart')?.getContext('2d');
        if (projectionCtx) {
            const projectionLabels = Array.from({length: 12}, (_, i) => {
                const date = new Date();
                date.setMonth(date.getMonth() + i);
                return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
            });

            this.charts.cashFlowProjection = new Chart(projectionCtx, {
                type: 'line',
                data: {
                    labels: projectionLabels,
                    datasets: [{
                        label: 'Conservative Scenario',
                        data: Array.from({length: 12}, (_, i) => 2400000 + (i * 50000) - (Math.random() * 200000)),
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Most Likely Scenario',
                        data: Array.from({length: 12}, (_, i) => 2400000 + (i * 80000) + (Math.random() * 100000)),
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Optimistic Scenario',
                        data: Array.from({length: 12}, (_, i) => 2400000 + (i * 120000) + (Math.random() * 300000)),
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: function(value) {
                                    return '$' + (value / 1000000).toFixed(1) + 'M';
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    }
                }
            });
        }
    }

    populateBankCashTables() {
        this.populateAccountsGrid();
        this.populateTransactionsTable();
        this.populateForecastScenarios();
        this.populateReconciliationWorkspace();
    }

    populateAccountsGrid() {
        const accountsGrid = document.getElementById('accountsGrid');
        if (!accountsGrid) return;

        const accounts = [
            {
                id: 'ACC001',
                name: 'Main Operating Account',
                bank: 'First National Bank',
                accountNumber: '****1234',
                type: 'Checking',
                balance: 1800000,
                currency: 'USD',
                interestRate: 0.5,
                lastSync: '2024-05-28 10:30',
                status: 'active'
            },
            {
                id: 'ACC002',
                name: 'High Yield Savings',
                bank: 'Capital Bank',
                accountNumber: '****5678',
                type: 'Savings',
                balance: 450000,
                currency: 'USD',
                interestRate: 2.5,
                lastSync: '2024-05-28 10:25',
                status: 'active'
            },
            {
                id: 'ACC003',
                name: 'Investment Account',
                bank: 'Investment Trust',
                accountNumber: '****9012',
                type: 'Investment',
                balance: 150000,
                currency: 'USD',
                interestRate: 5.2,
                lastSync: '2024-05-28 09:45',
                status: 'active'
            }
        ];

        accountsGrid.innerHTML = accounts.map(account => `
            <div class="account-card">
                <div class="account-header">
                    <h4>${account.name}</h4>
                    <span class="account-status ${account.status}">${account.status}</span>
                </div>
                <div class="account-details">
                    <div class="detail-row">
                        <span class="label">Bank:</span>
                        <span class="value">${account.bank}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Account:</span>
                        <span class="value">${account.accountNumber}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Type:</span>
                        <span class="value">${account.type}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Balance:</span>
                        <span class="value balance">$${account.balance.toLocaleString()}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Interest Rate:</span>
                        <span class="value">${account.interestRate}%</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Last Sync:</span>
                        <span class="value">${account.lastSync}</span>
                    </div>
                </div>
                <div class="account-actions">
                    <button onclick="bankCashModule.viewAccountDetails('${account.id}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="bankCashModule.syncAccount('${account.id}')" title="Sync">
                        <i class="fas fa-sync"></i>
                    </button>
                    <button onclick="bankCashModule.transferFrom('${account.id}')" title="Transfer">
                        <i class="fas fa-exchange-alt"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    populateTransactionsTable() {
        const transactionsTable = document.getElementById('transactionsTable');
        if (!transactionsTable) return;

        const transactions = [
            {
                id: 'TXN001',
                date: '2024-05-28',
                description: 'Customer Payment - Invoice #12345',
                account: 'Main Operating Account',
                category: 'Revenue',
                amount: 25000,
                type: 'credit',
                status: 'completed',
                reference: 'INV12345'
            },
            {
                id: 'TXN002',
                date: '2024-05-28',
                description: 'Office Rent Payment',
                account: 'Main Operating Account',
                category: 'Operating Expenses',
                amount: -8500,
                type: 'debit',
                status: 'completed',
                reference: 'RENT-MAY24'
            },
            {
                id: 'TXN003',
                date: '2024-05-27',
                description: 'Supplier Payment - Steel Corp',
                account: 'Main Operating Account',
                category: 'Materials',
                amount: -15750,
                type: 'debit',
                status: 'pending',
                reference: 'PO-5678'
            }
        ];

        transactionsTable.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Account</th>
                        <th>Category</th>
                        <th>Amount</th>
                        <th>Status</th>
                        <th>Reference</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${transactions.map(transaction => `
                        <tr>
                            <td>${transaction.date}</td>
                            <td>${transaction.description}</td>
                            <td>${transaction.account}</td>
                            <td>${transaction.category}</td>
                            <td class="amount ${transaction.type}">
                                ${transaction.amount > 0 ? '+' : ''}$${Math.abs(transaction.amount).toLocaleString()}
                            </td>
                            <td><span class="status-badge ${transaction.status}">${transaction.status}</span></td>
                            <td>${transaction.reference}</td>
                            <td>
                                <button onclick="bankCashModule.viewTransaction('${transaction.id}')" title="View">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button onclick="bankCashModule.editTransaction('${transaction.id}')" title="Edit">
                                    <i class="fas fa-edit"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    populateForecastScenarios() {
        const forecastScenarios = document.getElementById('forecastScenarios');
        if (!forecastScenarios) return;

        const scenarios = [
            {
                name: 'Conservative Growth',
                description: 'Assumes 5% annual growth with current expense levels',
                probability: 30,
                cashPosition30Days: 2650000,
                cashPosition90Days: 2850000,
                cashPosition365Days: 3200000,
                risks: ['Economic downturn', 'Delayed payments'],
                opportunities: ['Cost optimization', 'Efficiency gains']
            },
            {
                name: 'Expected Performance',
                description: 'Based on historical trends and current pipeline',
                probability: 50,
                cashPosition30Days: 2750000,
                cashPosition90Days: 3100000,
                cashPosition365Days: 3800000,
                risks: ['Market volatility', 'Competition'],
                opportunities: ['New contracts', 'Market expansion']
            },
            {
                name: 'Optimistic Growth',
                description: 'Assumes new contracts and market expansion',
                probability: 20,
                cashPosition30Days: 2900000,
                cashPosition90Days: 3400000,
                cashPosition365Days: 4500000,
                risks: ['Over-expansion', 'Resource constraints'],
                opportunities: ['Major contracts', 'Strategic partnerships']
            }
        ];

        forecastScenarios.innerHTML = scenarios.map(scenario => `
            <div class="scenario-card">
                <div class="scenario-header">
                    <h4>${scenario.name}</h4>
                    <span class="probability">${scenario.probability}% probability</span>
                </div>
                <p class="scenario-description">${scenario.description}</p>
                <div class="scenario-projections">
                    <div class="projection">
                        <span class="label">30 Days:</span>
                        <span class="value">$${(scenario.cashPosition30Days / 1000000).toFixed(1)}M</span>
                    </div>
                    <div class="projection">
                        <span class="label">90 Days:</span>
                        <span class="value">$${(scenario.cashPosition90Days / 1000000).toFixed(1)}M</span>
                    </div>
                    <div class="projection">
                        <span class="label">1 Year:</span>
                        <span class="value">$${(scenario.cashPosition365Days / 1000000).toFixed(1)}M</span>
                    </div>
                </div>
                <div class="scenario-details">
                    <div class="risks">
                        <h5>Key Risks:</h5>
                        <ul>
                            ${scenario.risks.map(risk => `<li>${risk}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="opportunities">
                        <h5>Opportunities:</h5>
                        <ul>
                            ${scenario.opportunities.map(opp => `<li>${opp}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `).join('');
    }

    populateReconciliationWorkspace() {
        const reconciliationWorkspace = document.getElementById('reconciliationWorkspace');
        if (!reconciliationWorkspace) return;

        reconciliationWorkspace.innerHTML = `
            <div class="reconciliation-panels">
                <div class="panel">
                    <h4>Bank Statement</h4>
                    <div class="statement-transactions">
                        <div class="transaction-item">
                            <span class="date">2024-05-28</span>
                            <span class="description">Customer Payment</span>
                            <span class="amount credit">+$25,000</span>
                            <span class="status unmatched">Unmatched</span>
                        </div>
                        <div class="transaction-item">
                            <span class="date">2024-05-28</span>
                            <span class="description">Office Rent</span>
                            <span class="amount debit">-$8,500</span>
                            <span class="status matched">Matched</span>
                        </div>
                    </div>
                </div>
                <div class="panel">
                    <h4>System Transactions</h4>
                    <div class="system-transactions">
                        <div class="transaction-item">
                            <span class="date">2024-05-28</span>
                            <span class="description">Invoice #12345 Payment</span>
                            <span class="amount credit">+$25,000</span>
                            <span class="status unmatched">Unmatched</span>
                        </div>
                        <div class="transaction-item">
                            <span class="date">2024-05-28</span>
                            <span class="description">Rent Payment - May</span>
                            <span class="amount debit">-$8,500</span>
                            <span class="status matched">Matched</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="reconciliation-actions">
                <button onclick="bankCashModule.matchTransactions()">
                    <i class="fas fa-link"></i> Match Selected
                </button>
                <button onclick="bankCashModule.markAsReconciled()">
                    <i class="fas fa-check"></i> Mark as Reconciled
                </button>
                <button onclick="bankCashModule.addAdjustment()">
                    <i class="fas fa-plus"></i> Add Adjustment
                </button>
            </div>
        `;
    }

    // Event Handlers
    switchTab(tabName) {
        // Hide all tab panes
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        // Remove active class from all tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });
        
        // Show selected tab pane
        document.getElementById(tabName + 'Tab').classList.add('active');
        
        // Add active class to selected tab button
        event.target.classList.add('active');

        // Render charts if needed
        if (tabName === 'cashflow' || tabName === 'forecasting') {
            setTimeout(() => this.renderAnalysisCharts(), 100);
        }
    }

    // Chart update methods
    updateCashFlowPeriod(period) {
        console.log('Updating cash flow period:', period);
    }

    updateCategoryChart(type) {
        console.log('Updating category chart:', type);
    }

    updateForecastPeriod(period) {
        console.log('Updating forecast period:', period);
    }

    updateForecast() {
        const period = document.getElementById('forecastPeriod').value;
        const confidence = document.getElementById('confidenceLevel').value;
        console.log('Updating forecast:', period, confidence);
    }

    // Action methods
    initiateTransfer() {
        console.log('Initiating fund transfer');
    }

    reconcileAccounts() {
        console.log('Starting account reconciliation');
    }

    exportCashFlowReport() {
        console.log('Exporting cash flow report');
    }

    refreshAccountBalances() {
        console.log('Refreshing account balances');
    }

    addBankAccount() {
        console.log('Adding new bank account');
    }

    syncAllAccounts() {
        console.log('Syncing all accounts');
    }

    viewAccountDetails(accountId) {
        console.log('Viewing account details:', accountId);
    }

    syncAccount(accountId) {
        console.log('Syncing account:', accountId);
    }

    transferFrom(accountId) {
        console.log('Initiating transfer from:', accountId);
    }

    applyTransactionFilters() {
        console.log('Applying transaction filters');
    }

    addTransaction() {
        console.log('Adding new transaction');
    }

    importTransactions() {
        console.log('Importing transactions');
    }

    exportTransactions() {
        console.log('Exporting transactions');
    }

    viewTransaction(transactionId) {
        console.log('Viewing transaction:', transactionId);
    }

    editTransaction(transactionId) {
        console.log('Editing transaction:', transactionId);
    }

    runForecast() {
        console.log('Running cash flow forecast');
    }

    saveForecastScenario() {
        console.log('Saving forecast scenario');
    }

    startReconciliation() {
        console.log('Starting reconciliation process');
    }

    autoMatch() {
        console.log('Auto-matching transactions');
    }

    matchTransactions() {
        console.log('Matching selected transactions');
    }

    markAsReconciled() {
        console.log('Marking as reconciled');
    }

    addAdjustment() {
        console.log('Adding reconciliation adjustment');
    }

    // Update methods for real-time data
    updateKPIs(data) {
        if (data.totalCashBalance) {
            document.getElementById('totalCashBalance').textContent = `$${(data.totalCashBalance / 1000000).toFixed(1)}M`;
        }
        if (data.monthlyInflow) {
            document.getElementById('monthlyInflow').textContent = `$${(data.monthlyInflow / 1000).toFixed(0)}K`;
        }
        if (data.monthlyOutflow) {
            document.getElementById('monthlyOutflow').textContent = `$${(data.monthlyOutflow / 1000).toFixed(0)}K`;
        }
        if (data.netCashFlow) {
            document.getElementById('netCashFlow').textContent = `$${(data.netCashFlow / 1000).toFixed(0)}K`;
        }
        if (data.burnRate) {
            document.getElementById('burnRate').textContent = data.burnRate;
        }
        if (data.liquidityRatio) {
            document.getElementById('liquidityRatio').textContent = data.liquidityRatio.toFixed(1);
        }
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

// Initialize bank cash module when DOM is loaded
let bankCashModule;

document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.dashboard !== 'undefined') {
        bankCashModule = new BankCashModule(window.dashboard);
    }
});
