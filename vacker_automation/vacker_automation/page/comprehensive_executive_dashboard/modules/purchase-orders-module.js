/**
 * Purchase Orders Management Module
 * Handles purchase order creation, tracking, approval workflows, and vendor management
 */

class PurchaseOrdersModule {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.charts = {};
        this.currentFilters = {
            status: 'all',
            vendor: 'all',
            department: 'all',
            priority: 'all',
            dateRange: '30'
        };
    }

    render() {
        return `
            <div class="purchase-orders-module">
                <div class="module-header">
                    <h2><i class="fas fa-shopping-cart"></i> Purchase Orders</h2>
                    <div class="module-actions">
                        <button class="btn-primary" onclick="purchaseOrdersModule.createPurchaseOrder()">
                            <i class="fas fa-plus"></i> Create PO
                        </button>
                        <button class="btn-secondary" onclick="purchaseOrdersModule.bulkApproval()">
                            <i class="fas fa-check-double"></i> Bulk Approve
                        </button>
                        <button class="btn-secondary" onclick="purchaseOrdersModule.exportPOReport()">
                            <i class="fas fa-download"></i> Export Report
                        </button>
                    </div>
                </div>

                <!-- KPIs Row -->
                <div class="kpi-row">
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-file-invoice"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="totalPOs">1,247</div>
                            <div class="kpi-label">Total POs</div>
                            <div class="kpi-change positive">+18</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-dollar-sign"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="totalPOValue">$2.8M</div>
                            <div class="kpi-label">Total PO Value</div>
                            <div class="kpi-change positive">+12.5%</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="pendingPOs">43</div>
                            <div class="kpi-label">Pending Approval</div>
                            <div class="kpi-change negative">+8</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="overduePOs">7</div>
                            <div class="kpi-label">Overdue Deliveries</div>
                            <div class="kpi-change negative">+2</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-truck"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="activeVendors">89</div>
                            <div class="kpi-label">Active Vendors</div>
                            <div class="kpi-change positive">+3</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-percentage"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="onTimeDelivery">94.2%</div>
                            <div class="kpi-label">On-Time Delivery</div>
                            <div class="kpi-change positive">+1.8%</div>
                        </div>
                    </div>
                </div>

                <!-- Charts Row -->
                <div class="charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>PO Status Distribution</h3>
                            <div class="chart-actions">
                                <select onchange="purchaseOrdersModule.updateStatusChart(this.value)">
                                    <option value="current">Current Month</option>
                                    <option value="quarter">This Quarter</option>
                                    <option value="year">This Year</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="poStatusChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Purchase Trends</h3>
                            <div class="chart-actions">
                                <select onchange="purchaseOrdersModule.updateTrendsChart(this.value)">
                                    <option value="value">By Value</option>
                                    <option value="quantity">By Quantity</option>
                                    <option value="count">By Count</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="purchaseTrendsChart"></canvas>
                    </div>
                </div>

                <div class="charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Vendor Performance</h3>
                            <div class="chart-actions">
                                <button onclick="purchaseOrdersModule.refreshVendorData()">
                                    <i class="fas fa-sync-alt"></i>
                                </button>
                            </div>
                        </div>
                        <canvas id="vendorPerformanceChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Category Spending</h3>
                            <div class="chart-actions">
                                <select onchange="purchaseOrdersModule.updateCategoryChart(this.value)">
                                    <option value="monthly">Monthly</option>
                                    <option value="quarterly">Quarterly</option>
                                    <option value="yearly">Yearly</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="categorySpendingChart"></canvas>
                    </div>
                </div>

                <!-- Tabs Section -->
                <div class="tab-container">
                    <div class="tab-buttons">
                        <button class="tab-button active" onclick="purchaseOrdersModule.switchTab('orders')">
                            <i class="fas fa-file-invoice"></i> Purchase Orders
                        </button>
                        <button class="tab-button" onclick="purchaseOrdersModule.switchTab('approval')">
                            <i class="fas fa-clipboard-check"></i> Approval Workflow
                        </button>
                        <button class="tab-button" onclick="purchaseOrdersModule.switchTab('vendors')">
                            <i class="fas fa-truck"></i> Vendor Management
                        </button>
                        <button class="tab-button" onclick="purchaseOrdersModule.switchTab('receiving')">
                            <i class="fas fa-boxes"></i> Receiving
                        </button>
                        <button class="tab-button" onclick="purchaseOrdersModule.switchTab('analytics')">
                            <i class="fas fa-chart-bar"></i> Analytics
                        </button>
                    </div>

                    <div class="tab-content">
                        <!-- Purchase Orders Tab -->
                        <div id="ordersTab" class="tab-pane active">
                            <div class="tab-controls">
                                <div class="po-filters">
                                    <input type="text" placeholder="Search POs..." id="poSearch">
                                    <select id="statusFilter" onchange="purchaseOrdersModule.applyFilters()">
                                        <option value="all">All Status</option>
                                        <option value="draft">Draft</option>
                                        <option value="pending">Pending Approval</option>
                                        <option value="approved">Approved</option>
                                        <option value="sent">Sent to Vendor</option>
                                        <option value="received">Received</option>
                                        <option value="completed">Completed</option>
                                        <option value="cancelled">Cancelled</option>
                                    </select>
                                    <select id="vendorFilter" onchange="purchaseOrdersModule.applyFilters()">
                                        <option value="all">All Vendors</option>
                                        <option value="vendor1">Steel Corp Ltd</option>
                                        <option value="vendor2">Tech Solutions Inc</option>
                                        <option value="vendor3">Office Supplies Co</option>
                                    </select>
                                    <select id="priorityFilter" onchange="purchaseOrdersModule.applyFilters()">
                                        <option value="all">All Priorities</option>
                                        <option value="urgent">Urgent</option>
                                        <option value="high">High</option>
                                        <option value="normal">Normal</option>
                                        <option value="low">Low</option>
                                    </select>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="purchaseOrdersModule.quickPO()">
                                        <i class="fas fa-bolt"></i> Quick PO
                                    </button>
                                    <button onclick="purchaseOrdersModule.duplicatePO()">
                                        <i class="fas fa-copy"></i> Duplicate
                                    </button>
                                    <button onclick="purchaseOrdersModule.bulkActions()">
                                        <i class="fas fa-tasks"></i> Bulk Actions
                                    </button>
                                </div>
                            </div>
                            <div class="purchase-orders-table" id="purchaseOrdersTable">
                                <!-- Purchase orders will be populated here -->
                            </div>
                        </div>

                        <!-- Approval Workflow Tab -->
                        <div id="approvalTab" class="tab-pane">
                            <div class="tab-controls">
                                <div class="approval-summary">
                                    <div class="summary-card">
                                        <h4>Pending My Approval</h4>
                                        <div class="summary-value">8</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Pending Finance Approval</h4>
                                        <div class="summary-value">15</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Pending Manager Approval</h4>
                                        <div class="summary-value">20</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Average Approval Time</h4>
                                        <div class="summary-value">2.3 days</div>
                                    </div>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="purchaseOrdersModule.configureWorkflow()">
                                        <i class="fas fa-cog"></i> Configure Workflow
                                    </button>
                                    <button onclick="purchaseOrdersModule.approvalHistory()">
                                        <i class="fas fa-history"></i> Approval History
                                    </button>
                                </div>
                            </div>
                            <div class="approval-queue" id="approvalQueue">
                                <!-- Approval queue will be populated here -->
                            </div>
                        </div>

                        <!-- Vendor Management Tab -->
                        <div id="vendorsTab" class="tab-pane">
                            <div class="tab-controls">
                                <div class="vendor-metrics">
                                    <div class="metric-card">
                                        <h4>Vendor Rating</h4>
                                        <div class="metric-value">4.2/5</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Quality Score</h4>
                                        <div class="metric-value">96.5%</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Cost Savings</h4>
                                        <div class="metric-value">$125K</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Contract Renewals</h4>
                                        <div class="metric-value">12</div>
                                    </div>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="purchaseOrdersModule.addVendor()">
                                        <i class="fas fa-plus"></i> Add Vendor
                                    </button>
                                    <button onclick="purchaseOrdersModule.vendorEvaluation()">
                                        <i class="fas fa-star"></i> Vendor Evaluation
                                    </button>
                                    <button onclick="purchaseOrdersModule.contractManagement()">
                                        <i class="fas fa-file-contract"></i> Contracts
                                    </button>
                                </div>
                            </div>
                            <div class="vendors-grid" id="vendorsGrid">
                                <!-- Vendors will be populated here -->
                            </div>
                        </div>

                        <!-- Receiving Tab -->
                        <div id="receivingTab" class="tab-pane">
                            <div class="tab-controls">
                                <div class="receiving-summary">
                                    <div class="summary-card">
                                        <h4>Expected Today</h4>
                                        <div class="summary-value">12</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Partially Received</h4>
                                        <div class="summary-value">5</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Quality Issues</h4>
                                        <div class="summary-value">2</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>On-Time Rate</h4>
                                        <div class="summary-value">94.2%</div>
                                    </div>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="purchaseOrdersModule.scheduleReceiving()">
                                        <i class="fas fa-calendar"></i> Schedule
                                    </button>
                                    <button onclick="purchaseOrdersModule.qualityInspection()">
                                        <i class="fas fa-search"></i> Quality Check
                                    </button>
                                </div>
                            </div>
                            <div class="receiving-schedule" id="receivingSchedule">
                                <!-- Receiving schedule will be populated here -->
                            </div>
                        </div>

                        <!-- Analytics Tab -->
                        <div id="analyticsTab" class="tab-pane">
                            <div class="analytics-dashboard">
                                <div class="analytics-chart">
                                    <h4>Spend Analysis</h4>
                                    <canvas id="spendAnalysisChart"></canvas>
                                </div>
                                <div class="analytics-chart">
                                    <h4>Vendor Concentration</h4>
                                    <canvas id="vendorConcentrationChart"></canvas>
                                </div>
                                <div class="analytics-chart">
                                    <h4>Procurement Cycle Time</h4>
                                    <canvas id="procurementCycleChart"></canvas>
                                </div>
                                <div class="analytics-insights">
                                    <h4>Key Insights</h4>
                                    <div class="insights-list" id="procurementInsights">
                                        <!-- Insights will be populated here -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderPOCharts() {
        this.renderPOStatusChart();
        this.renderPurchaseTrendsChart();
        this.renderVendorPerformanceChart();
        this.renderCategorySpendingChart();
        this.renderAnalyticsCharts();
    }

    renderPOStatusChart() {
        const ctx = document.getElementById('poStatusChart').getContext('2d');
        
        this.charts.poStatus = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Approved', 'Pending Approval', 'Sent to Vendor', 'Received', 'Completed', 'Cancelled'],
                datasets: [{
                    data: [35, 15, 20, 18, 10, 2],
                    backgroundColor: [
                        '#2ecc71',
                        '#f39c12',
                        '#3498db',
                        '#9b59b6',
                        '#1abc9c',
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
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    renderPurchaseTrendsChart() {
        const ctx = document.getElementById('purchaseTrendsChart').getContext('2d');
        
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];

        this.charts.purchaseTrends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'PO Value ($K)',
                    data: [420, 380, 450, 520, 480, 510],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y'
                }, {
                    label: 'PO Count',
                    data: [185, 167, 198, 215, 202, 208],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Value ($K)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Count'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
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

    renderVendorPerformanceChart() {
        const ctx = document.getElementById('vendorPerformanceChart').getContext('2d');
        
        this.charts.vendorPerformance = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Quality', 'Delivery', 'Price', 'Service', 'Innovation', 'Compliance'],
                datasets: [{
                    label: 'Steel Corp Ltd',
                    data: [9, 8, 7, 9, 6, 8],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.2)'
                }, {
                    label: 'Tech Solutions Inc',
                    data: [8, 9, 8, 7, 9, 9],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.2)'
                }, {
                    label: 'Office Supplies Co',
                    data: [7, 7, 9, 8, 5, 7],
                    borderColor: '#f39c12',
                    backgroundColor: 'rgba(243, 156, 18, 0.2)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 10
                    }
                }
            }
        });
    }

    renderCategorySpendingChart() {
        const ctx = document.getElementById('categorySpendingChart').getContext('2d');
        
        this.charts.categorySpending = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Raw Materials', 'Equipment', 'Services', 'Office Supplies', 'IT Hardware', 'Maintenance'],
                datasets: [{
                    label: 'Current Month',
                    data: [850, 320, 180, 45, 125, 90],
                    backgroundColor: '#3498db'
                }, {
                    label: 'Previous Month',
                    data: [780, 350, 165, 52, 110, 85],
                    backgroundColor: '#95a5a6'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Amount ($K)'
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

    renderAnalyticsCharts() {
        // Spend Analysis Chart
        const spendCtx = document.getElementById('spendAnalysisChart')?.getContext('2d');
        if (spendCtx) {
            this.charts.spendAnalysis = new Chart(spendCtx, {
                type: 'line',
                data: {
                    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                    datasets: [{
                        label: 'Total Spend',
                        data: [1200, 1350, 1180, 1420],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Budgeted',
                        data: [1250, 1300, 1200, 1400],
                        borderColor: '#2ecc71',
                        backgroundColor: 'transparent',
                        borderDash: [5, 5]
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Amount ($K)'
                            }
                        }
                    }
                }
            });
        }

        // Vendor Concentration Chart
        const concentrationCtx = document.getElementById('vendorConcentrationChart')?.getContext('2d');
        if (concentrationCtx) {
            this.charts.vendorConcentration = new Chart(concentrationCtx, {
                type: 'pie',
                data: {
                    labels: ['Top 5 Vendors', 'Next 10 Vendors', 'Other Vendors'],
                    datasets: [{
                        data: [65, 25, 10],
                        backgroundColor: ['#e74c3c', '#f39c12', '#2ecc71']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }

        // Procurement Cycle Time Chart
        const cycleCtx = document.getElementById('procurementCycleChart')?.getContext('2d');
        if (cycleCtx) {
            this.charts.procurementCycle = new Chart(cycleCtx, {
                type: 'bar',
                data: {
                    labels: ['Request', 'Approval', 'Sourcing', 'PO Creation', 'Delivery'],
                    datasets: [{
                        label: 'Average Days',
                        data: [2, 3, 5, 1, 8],
                        backgroundColor: '#3498db'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Days'
                            }
                        }
                    }
                }
            });
        }
    }

    populatePOTables() {
        this.populatePurchaseOrdersTable();
        this.populateApprovalQueue();
        this.populateVendorsGrid();
        this.populateReceivingSchedule();
        this.populateProcurementInsights();
    }

    populatePurchaseOrdersTable() {
        const poTable = document.getElementById('purchaseOrdersTable');
        if (!poTable) return;

        const purchaseOrders = [
            {
                id: 'PO-2024-001',
                vendor: 'Steel Corp Ltd',
                department: 'Manufacturing',
                requestedBy: 'John Smith',
                date: '2024-05-28',
                deliveryDate: '2024-06-05',
                status: 'approved',
                priority: 'high',
                totalAmount: 125000,
                currency: 'USD',
                items: 5
            },
            {
                id: 'PO-2024-002',
                vendor: 'Tech Solutions Inc',
                department: 'IT',
                requestedBy: 'Sarah Johnson',
                date: '2024-05-27',
                deliveryDate: '2024-06-10',
                status: 'pending',
                priority: 'medium',
                totalAmount: 45000,
                currency: 'USD',
                items: 3
            },
            {
                id: 'PO-2024-003',
                vendor: 'Office Supplies Co',
                department: 'Administration',
                requestedBy: 'Mike Wilson',
                date: '2024-05-26',
                deliveryDate: '2024-06-01',
                status: 'sent',
                priority: 'low',
                totalAmount: 1200,
                currency: 'USD',
                items: 12
            }
        ];

        poTable.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>PO Number</th>
                        <th>Vendor</th>
                        <th>Department</th>
                        <th>Requested By</th>
                        <th>Date</th>
                        <th>Delivery Date</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Amount</th>
                        <th>Items</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${purchaseOrders.map(po => `
                        <tr>
                            <td><strong>${po.id}</strong></td>
                            <td>${po.vendor}</td>
                            <td>${po.department}</td>
                            <td>${po.requestedBy}</td>
                            <td>${po.date}</td>
                            <td>${po.deliveryDate}</td>
                            <td><span class="status-badge ${po.status}">${po.status}</span></td>
                            <td><span class="priority-badge ${po.priority}">${po.priority}</span></td>
                            <td>$${po.totalAmount.toLocaleString()}</td>
                            <td>${po.items}</td>
                            <td>
                                <button onclick="purchaseOrdersModule.viewPO('${po.id}')" title="View">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button onclick="purchaseOrdersModule.editPO('${po.id}')" title="Edit">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button onclick="purchaseOrdersModule.printPO('${po.id}')" title="Print">
                                    <i class="fas fa-print"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    populateApprovalQueue() {
        const approvalQueue = document.getElementById('approvalQueue');
        if (!approvalQueue) return;

        const approvals = [
            {
                poId: 'PO-2024-004',
                vendor: 'Equipment Supplies Ltd',
                amount: 85000,
                requestedBy: 'Lisa Chen',
                submittedDate: '2024-05-28',
                approvalLevel: 'Finance Manager',
                daysWaiting: 1,
                priority: 'high',
                notes: 'Urgent equipment replacement required'
            },
            {
                poId: 'PO-2024-005',
                vendor: 'Software Solutions Inc',
                amount: 25000,
                requestedBy: 'David Brown',
                submittedDate: '2024-05-27',
                approvalLevel: 'Department Manager',
                daysWaiting: 2,
                priority: 'medium',
                notes: 'Annual software license renewal'
            }
        ];

        approvalQueue.innerHTML = `
            <div class="approval-cards">
                ${approvals.map(approval => `
                    <div class="approval-card ${approval.priority}">
                        <div class="approval-header">
                            <h4>${approval.poId}</h4>
                            <span class="priority-badge ${approval.priority}">${approval.priority}</span>
                        </div>
                        <div class="approval-details">
                            <div class="detail-row">
                                <span class="label">Vendor:</span>
                                <span class="value">${approval.vendor}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Amount:</span>
                                <span class="value">$${approval.amount.toLocaleString()}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Requested By:</span>
                                <span class="value">${approval.requestedBy}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Approval Level:</span>
                                <span class="value">${approval.approvalLevel}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Days Waiting:</span>
                                <span class="value">${approval.daysWaiting}</span>
                            </div>
                        </div>
                        <div class="approval-notes">
                            <p>${approval.notes}</p>
                        </div>
                        <div class="approval-actions">
                            <button class="btn-approve" onclick="purchaseOrdersModule.approvePO('${approval.poId}')">
                                <i class="fas fa-check"></i> Approve
                            </button>
                            <button class="btn-reject" onclick="purchaseOrdersModule.rejectPO('${approval.poId}')">
                                <i class="fas fa-times"></i> Reject
                            </button>
                            <button class="btn-review" onclick="purchaseOrdersModule.reviewPO('${approval.poId}')">
                                <i class="fas fa-eye"></i> Review
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    populateVendorsGrid() {
        const vendorsGrid = document.getElementById('vendorsGrid');
        if (!vendorsGrid) return;

        const vendors = [
            {
                id: 'VEN001',
                name: 'Steel Corp Ltd',
                category: 'Raw Materials',
                rating: 4.8,
                totalOrders: 145,
                totalValue: 2850000,
                onTimeDelivery: 95,
                qualityScore: 98,
                contact: 'john.doe@steelcorp.com',
                phone: '+1 234-567-8901',
                status: 'active'
            },
            {
                id: 'VEN002',
                name: 'Tech Solutions Inc',
                category: 'IT Equipment',
                rating: 4.6,
                totalOrders: 78,
                totalValue: 1250000,
                onTimeDelivery: 92,
                qualityScore: 96,
                contact: 'sales@techsolutions.com',
                phone: '+1 234-567-8902',
                status: 'active'
            }
        ];

        vendorsGrid.innerHTML = vendors.map(vendor => `
            <div class="vendor-card">
                <div class="vendor-header">
                    <h4>${vendor.name}</h4>
                    <div class="vendor-rating">
                        ${Array.from({length: 5}, (_, i) => 
                            `<i class="fas fa-star ${i < Math.floor(vendor.rating) ? 'active' : ''}"></i>`
                        ).join('')}
                        <span>${vendor.rating}</span>
                    </div>
                </div>
                <div class="vendor-details">
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="label">Category:</span>
                            <span class="value">${vendor.category}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Total Orders:</span>
                            <span class="value">${vendor.totalOrders}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Total Value:</span>
                            <span class="value">$${(vendor.totalValue / 1000000).toFixed(1)}M</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">On-Time Delivery:</span>
                            <span class="value">${vendor.onTimeDelivery}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Quality Score:</span>
                            <span class="value">${vendor.qualityScore}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Contact:</span>
                            <span class="value">${vendor.contact}</span>
                        </div>
                    </div>
                </div>
                <div class="vendor-actions">
                    <button onclick="purchaseOrdersModule.createPOForVendor('${vendor.id}')">
                        <i class="fas fa-plus"></i> New PO
                    </button>
                    <button onclick="purchaseOrdersModule.viewVendorDetails('${vendor.id}')">
                        <i class="fas fa-info-circle"></i> Details
                    </button>
                    <button onclick="purchaseOrdersModule.evaluateVendor('${vendor.id}')">
                        <i class="fas fa-star"></i> Evaluate
                    </button>
                </div>
            </div>
        `).join('');
    }

    populateReceivingSchedule() {
        const receivingSchedule = document.getElementById('receivingSchedule');
        if (!receivingSchedule) return;

        const deliveries = [
            {
                poId: 'PO-2024-001',
                vendor: 'Steel Corp Ltd',
                expectedDate: '2024-06-05',
                items: 'Steel Rods, Plates',
                quantity: '500 units',
                status: 'scheduled',
                dock: 'Dock A',
                inspector: 'Mike Wilson'
            },
            {
                poId: 'PO-2024-003',
                vendor: 'Office Supplies Co',
                expectedDate: '2024-06-01',
                items: 'Office Chairs, Desks',
                quantity: '12 items',
                status: 'in-transit',
                dock: 'Dock B',
                inspector: 'Sarah Johnson'
            }
        ];

        receivingSchedule.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>PO Number</th>
                        <th>Vendor</th>
                        <th>Expected Date</th>
                        <th>Items</th>
                        <th>Quantity</th>
                        <th>Status</th>
                        <th>Dock</th>
                        <th>Inspector</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${deliveries.map(delivery => `
                        <tr>
                            <td>${delivery.poId}</td>
                            <td>${delivery.vendor}</td>
                            <td>${delivery.expectedDate}</td>
                            <td>${delivery.items}</td>
                            <td>${delivery.quantity}</td>
                            <td><span class="status-badge ${delivery.status}">${delivery.status}</span></td>
                            <td>${delivery.dock}</td>
                            <td>${delivery.inspector}</td>
                            <td>
                                <button onclick="purchaseOrdersModule.receiveShipment('${delivery.poId}')" title="Receive">
                                    <i class="fas fa-check"></i>
                                </button>
                                <button onclick="purchaseOrdersModule.inspectShipment('${delivery.poId}')" title="Inspect">
                                    <i class="fas fa-search"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    populateProcurementInsights() {
        const procurementInsights = document.getElementById('procurementInsights');
        if (!procurementInsights) return;

        const insights = [
            {
                type: 'warning',
                title: 'Budget Variance',
                description: 'Raw materials spending is 15% over budget this quarter',
                action: 'Review pricing with suppliers',
                priority: 'high'
            },
            {
                type: 'success',
                title: 'Cost Savings Opportunity',
                description: 'Consolidating IT purchases could save $25K annually',
                action: 'Negotiate volume discounts',
                priority: 'medium'
            },
            {
                type: 'info',
                title: 'Vendor Performance',
                description: 'Steel Corp Ltd consistently exceeds delivery expectations',
                action: 'Consider preferred vendor status',
                priority: 'low'
            }
        ];

        procurementInsights.innerHTML = insights.map(insight => `
            <div class="insight-card ${insight.type}">
                <div class="insight-header">
                    <h5>${insight.title}</h5>
                    <span class="priority-badge ${insight.priority}">${insight.priority}</span>
                </div>
                <p>${insight.description}</p>
                <button class="insight-action">${insight.action}</button>
            </div>
        `).join('');
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
        if (tabName === 'analytics') {
            setTimeout(() => this.renderAnalyticsCharts(), 100);
        }
    }

    applyFilters() {
        const status = document.getElementById('statusFilter').value;
        const vendor = document.getElementById('vendorFilter').value;
        const priority = document.getElementById('priorityFilter').value;
        const search = document.getElementById('poSearch').value.toLowerCase();

        this.currentFilters = { status, vendor, priority, search };
        this.populatePurchaseOrdersTable();
    }

    // Chart update methods
    updateStatusChart(period) {
        console.log('Updating status chart:', period);
    }

    updateTrendsChart(type) {
        console.log('Updating trends chart:', type);
    }

    updateCategoryChart(period) {
        console.log('Updating category chart:', period);
    }

    refreshVendorData() {
        console.log('Refreshing vendor data');
    }

    // Action methods
    createPurchaseOrder() {
        console.log('Creating new purchase order');
    }

    bulkApproval() {
        console.log('Performing bulk approval');
    }

    exportPOReport() {
        console.log('Exporting PO report');
    }

    quickPO() {
        console.log('Creating quick PO');
    }

    duplicatePO() {
        console.log('Duplicating PO');
    }

    bulkActions() {
        console.log('Performing bulk actions');
    }

    viewPO(poId) {
        console.log('Viewing PO:', poId);
    }

    editPO(poId) {
        console.log('Editing PO:', poId);
    }

    printPO(poId) {
        console.log('Printing PO:', poId);
    }

    approvePO(poId) {
        console.log('Approving PO:', poId);
    }

    rejectPO(poId) {
        console.log('Rejecting PO:', poId);
    }

    reviewPO(poId) {
        console.log('Reviewing PO:', poId);
    }

    configureWorkflow() {
        console.log('Configuring approval workflow');
    }

    approvalHistory() {
        console.log('Viewing approval history');
    }

    addVendor() {
        console.log('Adding new vendor');
    }

    vendorEvaluation() {
        console.log('Starting vendor evaluation');
    }

    contractManagement() {
        console.log('Opening contract management');
    }

    createPOForVendor(vendorId) {
        console.log('Creating PO for vendor:', vendorId);
    }

    viewVendorDetails(vendorId) {
        console.log('Viewing vendor details:', vendorId);
    }

    evaluateVendor(vendorId) {
        console.log('Evaluating vendor:', vendorId);
    }

    scheduleReceiving() {
        console.log('Scheduling receiving');
    }

    qualityInspection() {
        console.log('Starting quality inspection');
    }

    receiveShipment(poId) {
        console.log('Receiving shipment for PO:', poId);
    }

    inspectShipment(poId) {
        console.log('Inspecting shipment for PO:', poId);
    }

    // Update methods for real-time data
    updateKPIs(data) {
        if (data.totalPOs) {
            document.getElementById('totalPOs').textContent = data.totalPOs.toLocaleString();
        }
        if (data.totalPOValue) {
            document.getElementById('totalPOValue').textContent = `$${(data.totalPOValue / 1000000).toFixed(1)}M`;
        }
        if (data.pendingPOs) {
            document.getElementById('pendingPOs').textContent = data.pendingPOs;
        }
        if (data.overduePOs) {
            document.getElementById('overduePOs').textContent = data.overduePOs;
        }
        if (data.activeVendors) {
            document.getElementById('activeVendors').textContent = data.activeVendors;
        }
        if (data.onTimeDelivery) {
            document.getElementById('onTimeDelivery').textContent = `${data.onTimeDelivery.toFixed(1)}%`;
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

// Initialize purchase orders module when DOM is loaded
let purchaseOrdersModule;

document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.dashboard !== 'undefined') {
        purchaseOrdersModule = new PurchaseOrdersModule(window.dashboard);
    }
});
