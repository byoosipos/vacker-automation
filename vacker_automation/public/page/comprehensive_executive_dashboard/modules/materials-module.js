/**
 * Materials Management Module
 * Handles materials, inventory, procurement, and supplier management
 */

class MaterialsModule {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.charts = {};
        this.currentFilters = {
            category: 'all',
            supplier: 'all',
            status: 'all',
            location: 'all'
        };
    }

    render() {
        return `
            <div class="materials-module">
                <div class="module-header">
                    <h2><i class="fas fa-boxes"></i> Materials Management</h2>
                    <div class="module-actions">
                        <button class="btn-primary" onclick="materialsModule.openAddMaterialModal()">
                            <i class="fas fa-plus"></i> Add Material
                        </button>
                        <button class="btn-secondary" onclick="materialsModule.exportMaterialsReport()">
                            <i class="fas fa-download"></i> Export Report
                        </button>
                    </div>
                </div>

                <!-- KPIs Row -->
                <div class="kpi-row">
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-warehouse"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="totalMaterials">2,847</div>
                            <div class="kpi-label">Total Materials</div>
                            <div class="kpi-change positive">+5.2%</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-dollar-sign"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="inventoryValue">$1.2M</div>
                            <div class="kpi-label">Inventory Value</div>
                            <div class="kpi-change positive">+8.1%</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="lowStockItems">47</div>
                            <div class="kpi-label">Low Stock Items</div>
                            <div class="kpi-change negative">+12</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-truck"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="activeSuppliers">156</div>
                            <div class="kpi-label">Active Suppliers</div>
                            <div class="kpi-change positive">+3</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="avgLeadTime">12.5</div>
                            <div class="kpi-label">Avg Lead Time (days)</div>
                            <div class="kpi-change negative">+1.2</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-percentage"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="stockAccuracy">97.8%</div>
                            <div class="kpi-label">Stock Accuracy</div>
                            <div class="kpi-change positive">+0.5%</div>
                        </div>
                    </div>
                </div>

                <!-- Charts Row -->
                <div class="charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Inventory Levels by Category</h3>
                            <div class="chart-actions">
                                <select onchange="materialsModule.updateInventoryChart(this.value)">
                                    <option value="category">By Category</option>
                                    <option value="location">By Location</option>
                                    <option value="value">By Value</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="inventoryLevelsChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Stock Movement Trends</h3>
                            <div class="chart-actions">
                                <select onchange="materialsModule.updateStockMovementChart(this.value)">
                                    <option value="30">Last 30 Days</option>
                                    <option value="90">Last 90 Days</option>
                                    <option value="365">Last Year</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="stockMovementChart"></canvas>
                    </div>
                </div>

                <div class="charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Supplier Performance</h3>
                            <div class="chart-actions">
                                <button onclick="materialsModule.refreshSupplierData()">
                                    <i class="fas fa-sync-alt"></i>
                                </button>
                            </div>
                        </div>
                        <canvas id="supplierPerformanceChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>ABC Analysis</h3>
                            <div class="chart-actions">
                                <select onchange="materialsModule.updateABCChart(this.value)">
                                    <option value="value">By Value</option>
                                    <option value="quantity">By Quantity</option>
                                    <option value="frequency">By Frequency</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="abcAnalysisChart"></canvas>
                    </div>
                </div>

                <!-- Tabs Section -->
                <div class="tab-container">
                    <div class="tab-buttons">
                        <button class="tab-button active" onclick="materialsModule.switchTab('inventory')">
                            <i class="fas fa-boxes"></i> Inventory
                        </button>
                        <button class="tab-button" onclick="materialsModule.switchTab('procurement')">
                            <i class="fas fa-shopping-cart"></i> Procurement
                        </button>
                        <button class="tab-button" onclick="materialsModule.switchTab('suppliers')">
                            <i class="fas fa-truck"></i> Suppliers
                        </button>
                        <button class="tab-button" onclick="materialsModule.switchTab('quality')">
                            <i class="fas fa-award"></i> Quality Control
                        </button>
                        <button class="tab-button" onclick="materialsModule.switchTab('analytics')">
                            <i class="fas fa-chart-line"></i> Analytics
                        </button>
                    </div>

                    <div class="tab-content">
                        <!-- Inventory Tab -->
                        <div id="inventoryTab" class="tab-pane active">
                            <div class="tab-controls">
                                <div class="search-filters">
                                    <input type="text" placeholder="Search materials..." id="materialSearch">
                                    <select id="categoryFilter" onchange="materialsModule.applyFilters()">
                                        <option value="all">All Categories</option>
                                        <option value="raw-materials">Raw Materials</option>
                                        <option value="components">Components</option>
                                        <option value="packaging">Packaging</option>
                                        <option value="consumables">Consumables</option>
                                    </select>
                                    <select id="statusFilter" onchange="materialsModule.applyFilters()">
                                        <option value="all">All Status</option>
                                        <option value="in-stock">In Stock</option>
                                        <option value="low-stock">Low Stock</option>
                                        <option value="out-of-stock">Out of Stock</option>
                                    </select>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="materialsModule.performStockCount()">
                                        <i class="fas fa-clipboard-check"></i> Stock Count
                                    </button>
                                    <button onclick="materialsModule.generateReorderReport()">
                                        <i class="fas fa-exclamation-circle"></i> Reorder Report
                                    </button>
                                </div>
                            </div>
                            <div class="materials-grid" id="materialsGrid">
                                <!-- Materials will be populated here -->
                            </div>
                        </div>

                        <!-- Procurement Tab -->
                        <div id="procurementTab" class="tab-pane">
                            <div class="tab-controls">
                                <div class="procurement-summary">
                                    <div class="summary-card">
                                        <h4>Pending Requests</h4>
                                        <div class="summary-value">23</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>In Process</h4>
                                        <div class="summary-value">15</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Completed This Month</h4>
                                        <div class="summary-value">187</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Total Value</h4>
                                        <div class="summary-value">$487K</div>
                                    </div>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="materialsModule.createProcurementRequest()">
                                        <i class="fas fa-plus"></i> New Request
                                    </button>
                                    <button onclick="materialsModule.bulkApproval()">
                                        <i class="fas fa-check-double"></i> Bulk Approval
                                    </button>
                                </div>
                            </div>
                            <div class="procurement-table" id="procurementTable">
                                <!-- Procurement requests will be populated here -->
                            </div>
                        </div>

                        <!-- Suppliers Tab -->
                        <div id="suppliersTab" class="tab-pane">
                            <div class="tab-controls">
                                <div class="supplier-metrics">
                                    <div class="metric-card">
                                        <h4>On-Time Delivery</h4>
                                        <div class="metric-value">94.2%</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Quality Score</h4>
                                        <div class="metric-value">97.8%</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Cost Variance</h4>
                                        <div class="metric-value">-2.1%</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Avg Response Time</h4>
                                        <div class="metric-value">4.2h</div>
                                    </div>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="materialsModule.addSupplier()">
                                        <i class="fas fa-plus"></i> Add Supplier
                                    </button>
                                    <button onclick="materialsModule.evaluateSuppliers()">
                                        <i class="fas fa-star"></i> Evaluate Performance
                                    </button>
                                </div>
                            </div>
                            <div class="suppliers-list" id="suppliersList">
                                <!-- Suppliers will be populated here -->
                            </div>
                        </div>

                        <!-- Quality Control Tab -->
                        <div id="qualityTab" class="tab-pane">
                            <div class="tab-controls">
                                <div class="quality-metrics">
                                    <div class="metric-card">
                                        <h4>Inspection Rate</h4>
                                        <div class="metric-value">15.2%</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Pass Rate</h4>
                                        <div class="metric-value">97.5%</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Defect Rate</h4>
                                        <div class="metric-value">2.1%</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Rework Cost</h4>
                                        <div class="metric-value">$12.5K</div>
                                    </div>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="materialsModule.scheduleInspection()">
                                        <i class="fas fa-search"></i> Schedule Inspection
                                    </button>
                                    <button onclick="materialsModule.generateQualityReport()">
                                        <i class="fas fa-clipboard-list"></i> Quality Report
                                    </button>
                                </div>
                            </div>
                            <div class="quality-inspections" id="qualityInspections">
                                <!-- Quality inspections will be populated here -->
                            </div>
                        </div>

                        <!-- Analytics Tab -->
                        <div id="analyticsTab" class="tab-pane">
                            <div class="analytics-dashboard">
                                <div class="analytics-chart">
                                    <h4>Inventory Turnover Analysis</h4>
                                    <canvas id="inventoryTurnoverChart"></canvas>
                                </div>
                                <div class="analytics-chart">
                                    <h4>Cost Trend Analysis</h4>
                                    <canvas id="costTrendChart"></canvas>
                                </div>
                                <div class="analytics-chart">
                                    <h4>Demand Forecasting</h4>
                                    <canvas id="demandForecastChart"></canvas>
                                </div>
                                <div class="analytics-insights">
                                    <h4>AI Insights</h4>
                                    <div class="insights-list" id="materialsInsights">
                                        <!-- AI insights will be populated here -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderMaterialsCharts() {
        this.renderInventoryLevelsChart();
        this.renderStockMovementChart();
        this.renderSupplierPerformanceChart();
        this.renderABCAnalysisChart();
        this.renderAnalyticsCharts();
    }

    renderInventoryLevelsChart() {
        const ctx = document.getElementById('inventoryLevelsChart').getContext('2d');
        
        this.charts.inventoryLevels = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Raw Materials', 'Components', 'Packaging', 'Consumables', 'Finished Goods'],
                datasets: [{
                    data: [35, 25, 15, 10, 15],
                    backgroundColor: [
                        '#3498db',
                        '#2ecc71',
                        '#f39c12',
                        '#e74c3c',
                        '#9b59b6'
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

    renderStockMovementChart() {
        const ctx = document.getElementById('stockMovementChart').getContext('2d');
        
        const days = Array.from({length: 30}, (_, i) => {
            const date = new Date();
            date.setDate(date.getDate() - 29 + i);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });

        this.charts.stockMovement = new Chart(ctx, {
            type: 'line',
            data: {
                labels: days,
                datasets: [{
                    label: 'Stock In',
                    data: Array.from({length: 30}, () => Math.floor(Math.random() * 100) + 50),
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Stock Out',
                    data: Array.from({length: 30}, () => Math.floor(Math.random() * 80) + 30),
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
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

    renderSupplierPerformanceChart() {
        const ctx = document.getElementById('supplierPerformanceChart').getContext('2d');
        
        this.charts.supplierPerformance = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Quality', 'Delivery', 'Cost', 'Service', 'Innovation', 'Compliance'],
                datasets: [{
                    label: 'Supplier A',
                    data: [9, 8, 7, 9, 6, 8],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.2)'
                }, {
                    label: 'Supplier B',
                    data: [8, 9, 8, 7, 7, 9],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.2)'
                }, {
                    label: 'Supplier C',
                    data: [7, 7, 9, 8, 8, 7],
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

    renderABCAnalysisChart() {
        const ctx = document.getElementById('abcAnalysisChart').getContext('2d');
        
        this.charts.abcAnalysis = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['A Items', 'B Items', 'C Items'],
                datasets: [{
                    label: 'Value (%)',
                    data: [80, 15, 5],
                    backgroundColor: ['#e74c3c', '#f39c12', '#2ecc71'],
                    borderWidth: 1
                }, {
                    label: 'Quantity (%)',
                    data: [20, 30, 50],
                    backgroundColor: ['rgba(231, 76, 60, 0.5)', 'rgba(243, 156, 18, 0.5)', 'rgba(46, 204, 113, 0.5)'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    renderAnalyticsCharts() {
        // Inventory Turnover Chart
        const turnoverCtx = document.getElementById('inventoryTurnoverChart')?.getContext('2d');
        if (turnoverCtx) {
            this.charts.inventoryTurnover = new Chart(turnoverCtx, {
                type: 'bar',
                data: {
                    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                    datasets: [{
                        label: 'Inventory Turnover',
                        data: [4.2, 4.8, 5.1, 4.9],
                        backgroundColor: '#3498db'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Cost Trend Chart
        const costCtx = document.getElementById('costTrendChart')?.getContext('2d');
        if (costCtx) {
            this.charts.costTrend = new Chart(costCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Material Cost Index',
                        data: [100, 102, 98, 105, 103, 107],
                        borderColor: '#e74c3c',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: false
                        }
                    }
                }
            });
        }

        // Demand Forecast Chart
        const forecastCtx = document.getElementById('demandForecastChart')?.getContext('2d');
        if (forecastCtx) {
            this.charts.demandForecast = new Chart(forecastCtx, {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{
                        label: 'Actual Demand',
                        data: [1200, 1350, 1180, 1420],
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)'
                    }, {
                        label: 'Forecasted Demand',
                        data: [1250, 1300, 1200, 1400],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderDash: [5, 5]
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }

    populateMaterialsTables() {
        this.populateInventoryGrid();
        this.populateProcurementTable();
        this.populateSuppliersList();
        this.populateQualityInspections();
        this.populateMaterialsInsights();
    }

    populateInventoryGrid() {
        const materialsGrid = document.getElementById('materialsGrid');
        if (!materialsGrid) return;

        const materials = [
            {
                id: 'MAT001',
                name: 'Steel Rods (10mm)',
                category: 'Raw Materials',
                currentStock: 500,
                minStock: 100,
                maxStock: 1000,
                unitPrice: 25.50,
                supplier: 'Steel Corp Ltd',
                location: 'Warehouse A',
                status: 'in-stock'
            },
            {
                id: 'MAT002',
                name: 'Hydraulic Pump',
                category: 'Components',
                currentStock: 15,
                minStock: 20,
                maxStock: 50,
                unitPrice: 1250.00,
                supplier: 'Hydraulics Inc',
                location: 'Warehouse B',
                status: 'low-stock'
            },
            {
                id: 'MAT003',
                name: 'Packaging Boxes',
                category: 'Packaging',
                currentStock: 0,
                minStock: 50,
                maxStock: 500,
                unitPrice: 2.50,
                supplier: 'Pack Solutions',
                location: 'Warehouse C',
                status: 'out-of-stock'
            }
        ];

        materialsGrid.innerHTML = materials.map(material => `
            <div class="material-card ${material.status}">
                <div class="material-header">
                    <h4>${material.name}</h4>
                    <span class="material-id">${material.id}</span>
                </div>
                <div class="material-details">
                    <div class="detail-row">
                        <span>Category:</span>
                        <span>${material.category}</span>
                    </div>
                    <div class="detail-row">
                        <span>Current Stock:</span>
                        <span class="stock-level ${material.status}">${material.currentStock}</span>
                    </div>
                    <div class="detail-row">
                        <span>Unit Price:</span>
                        <span>$${material.unitPrice.toFixed(2)}</span>
                    </div>
                    <div class="detail-row">
                        <span>Supplier:</span>
                        <span>${material.supplier}</span>
                    </div>
                </div>
                <div class="material-actions">
                    <button onclick="materialsModule.adjustStock('${material.id}')" title="Adjust Stock">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="materialsModule.viewHistory('${material.id}')" title="View History">
                        <i class="fas fa-history"></i>
                    </button>
                    <button onclick="materialsModule.reorderMaterial('${material.id}')" title="Reorder">
                        <i class="fas fa-shopping-cart"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    populateProcurementTable() {
        const procurementTable = document.getElementById('procurementTable');
        if (!procurementTable) return;

        const requests = [
            {
                id: 'PR001',
                material: 'Steel Rods (10mm)',
                quantity: 500,
                requestedBy: 'John Smith',
                requestDate: '2024-05-28',
                expectedDate: '2024-06-05',
                status: 'pending',
                priority: 'high',
                supplier: 'Steel Corp Ltd',
                estimatedCost: 12750
            },
            {
                id: 'PR002',
                material: 'Hydraulic Pump',
                quantity: 10,
                requestedBy: 'Sarah Johnson',
                requestDate: '2024-05-27',
                expectedDate: '2024-06-10',
                status: 'approved',
                priority: 'medium',
                supplier: 'Hydraulics Inc',
                estimatedCost: 12500
            }
        ];

        procurementTable.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Request ID</th>
                        <th>Material</th>
                        <th>Quantity</th>
                        <th>Requested By</th>
                        <th>Request Date</th>
                        <th>Expected Date</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Estimated Cost</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${requests.map(request => `
                        <tr>
                            <td>${request.id}</td>
                            <td>${request.material}</td>
                            <td>${request.quantity}</td>
                            <td>${request.requestedBy}</td>
                            <td>${request.requestDate}</td>
                            <td>${request.expectedDate}</td>
                            <td><span class="status-badge ${request.status}">${request.status}</span></td>
                            <td><span class="priority-badge ${request.priority}">${request.priority}</span></td>
                            <td>$${request.estimatedCost.toLocaleString()}</td>
                            <td>
                                <button onclick="materialsModule.viewRequest('${request.id}')" title="View">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button onclick="materialsModule.approveRequest('${request.id}')" title="Approve">
                                    <i class="fas fa-check"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    populateSuppliersList() {
        const suppliersList = document.getElementById('suppliersList');
        if (!suppliersList) return;

        const suppliers = [
            {
                id: 'SUP001',
                name: 'Steel Corp Ltd',
                category: 'Raw Materials',
                rating: 4.8,
                onTimeDelivery: 95,
                qualityScore: 98,
                totalOrders: 145,
                totalValue: 485000,
                contact: 'contact@steelcorp.com',
                phone: '+1 234-567-8901'
            },
            {
                id: 'SUP002',
                name: 'Hydraulics Inc',
                category: 'Components',
                rating: 4.6,
                onTimeDelivery: 92,
                qualityScore: 96,
                totalOrders: 78,
                totalValue: 325000,
                contact: 'sales@hydraulics.com',
                phone: '+1 234-567-8902'
            }
        ];

        suppliersList.innerHTML = suppliers.map(supplier => `
            <div class="supplier-card">
                <div class="supplier-header">
                    <h4>${supplier.name}</h4>
                    <div class="supplier-rating">
                        ${Array.from({length: 5}, (_, i) => 
                            `<i class="fas fa-star ${i < Math.floor(supplier.rating) ? 'active' : ''}"></i>`
                        ).join('')}
                        <span>${supplier.rating}</span>
                    </div>
                </div>
                <div class="supplier-details">
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="label">Category:</span>
                            <span class="value">${supplier.category}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">On-Time Delivery:</span>
                            <span class="value">${supplier.onTimeDelivery}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Quality Score:</span>
                            <span class="value">${supplier.qualityScore}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Total Orders:</span>
                            <span class="value">${supplier.totalOrders}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Total Value:</span>
                            <span class="value">$${supplier.totalValue.toLocaleString()}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Contact:</span>
                            <span class="value">${supplier.contact}</span>
                        </div>
                    </div>
                </div>
                <div class="supplier-actions">
                    <button onclick="materialsModule.contactSupplier('${supplier.id}')">
                        <i class="fas fa-envelope"></i> Contact
                    </button>
                    <button onclick="materialsModule.viewSupplierDetails('${supplier.id}')">
                        <i class="fas fa-info-circle"></i> Details
                    </button>
                    <button onclick="materialsModule.evaluateSupplier('${supplier.id}')">
                        <i class="fas fa-star"></i> Evaluate
                    </button>
                </div>
            </div>
        `).join('');
    }

    populateQualityInspections() {
        const qualityInspections = document.getElementById('qualityInspections');
        if (!qualityInspections) return;

        const inspections = [
            {
                id: 'QI001',
                material: 'Steel Rods (10mm)',
                batchNumber: 'BT20240528001',
                inspectionDate: '2024-05-28',
                inspector: 'Mike Wilson',
                status: 'passed',
                defects: 0,
                sampleSize: 50,
                notes: 'All samples within specification'
            },
            {
                id: 'QI002',
                material: 'Hydraulic Pump',
                batchNumber: 'BT20240527001',
                inspectionDate: '2024-05-27',
                inspector: 'Lisa Chen',
                status: 'failed',
                defects: 2,
                sampleSize: 5,
                notes: 'Pressure test failure on 2 units'
            }
        ];

        qualityInspections.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Inspection ID</th>
                        <th>Material</th>
                        <th>Batch Number</th>
                        <th>Date</th>
                        <th>Inspector</th>
                        <th>Status</th>
                        <th>Defects</th>
                        <th>Sample Size</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${inspections.map(inspection => `
                        <tr>
                            <td>${inspection.id}</td>
                            <td>${inspection.material}</td>
                            <td>${inspection.batchNumber}</td>
                            <td>${inspection.inspectionDate}</td>
                            <td>${inspection.inspector}</td>
                            <td><span class="status-badge ${inspection.status}">${inspection.status}</span></td>
                            <td>${inspection.defects}</td>
                            <td>${inspection.sampleSize}</td>
                            <td>
                                <button onclick="materialsModule.viewInspectionReport('${inspection.id}')" title="View Report">
                                    <i class="fas fa-file-alt"></i>
                                </button>
                                <button onclick="materialsModule.retestBatch('${inspection.batchNumber}')" title="Retest">
                                    <i class="fas fa-redo"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    populateMaterialsInsights() {
        const materialsInsights = document.getElementById('materialsInsights');
        if (!materialsInsights) return;

        const insights = [
            {
                type: 'warning',
                title: 'Low Stock Alert',
                description: '47 materials are below minimum stock levels',
                action: 'Generate reorder recommendations',
                priority: 'high'
            },
            {
                type: 'info',
                title: 'Cost Optimization',
                description: 'Switch to Supplier B for steel rods to save 8%',
                action: 'Review supplier contracts',
                priority: 'medium'
            },
            {
                type: 'success',
                title: 'Quality Improvement',
                description: 'Defect rate decreased by 15% this month',
                action: 'Document best practices',
                priority: 'low'
            }
        ];

        materialsInsights.innerHTML = insights.map(insight => `
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
        const category = document.getElementById('categoryFilter').value;
        const status = document.getElementById('statusFilter').value;
        const search = document.getElementById('materialSearch').value.toLowerCase();

        this.currentFilters = { category, status, search };
        this.populateInventoryGrid();
    }

    // Chart update methods
    updateInventoryChart(type) {
        // Update inventory levels chart based on type
        console.log('Updating inventory chart:', type);
    }

    updateStockMovementChart(period) {
        // Update stock movement chart for period
        console.log('Updating stock movement chart:', period);
    }

    updateABCChart(analysis) {
        // Update ABC analysis chart
        console.log('Updating ABC chart:', analysis);
    }

    // Action methods
    openAddMaterialModal() {
        console.log('Opening add material modal');
    }

    exportMaterialsReport() {
        console.log('Exporting materials report');
    }

    adjustStock(materialId) {
        console.log('Adjusting stock for:', materialId);
    }

    viewHistory(materialId) {
        console.log('Viewing history for:', materialId);
    }

    reorderMaterial(materialId) {
        console.log('Reordering material:', materialId);
    }

    performStockCount() {
        console.log('Performing stock count');
    }

    generateReorderReport() {
        console.log('Generating reorder report');
    }

    createProcurementRequest() {
        console.log('Creating procurement request');
    }

    bulkApproval() {
        console.log('Performing bulk approval');
    }

    viewRequest(requestId) {
        console.log('Viewing request:', requestId);
    }

    approveRequest(requestId) {
        console.log('Approving request:', requestId);
    }

    addSupplier() {
        console.log('Adding new supplier');
    }

    evaluateSuppliers() {
        console.log('Evaluating suppliers');
    }

    contactSupplier(supplierId) {
        console.log('Contacting supplier:', supplierId);
    }

    viewSupplierDetails(supplierId) {
        console.log('Viewing supplier details:', supplierId);
    }

    evaluateSupplier(supplierId) {
        console.log('Evaluating supplier:', supplierId);
    }

    scheduleInspection() {
        console.log('Scheduling inspection');
    }

    generateQualityReport() {
        console.log('Generating quality report');
    }

    viewInspectionReport(inspectionId) {
        console.log('Viewing inspection report:', inspectionId);
    }

    retestBatch(batchNumber) {
        console.log('Retesting batch:', batchNumber);
    }

    refreshSupplierData() {
        console.log('Refreshing supplier data');
    }

    // Update methods for real-time data
    updateKPIs(data) {
        if (data.totalMaterials) {
            document.getElementById('totalMaterials').textContent = data.totalMaterials.toLocaleString();
        }
        if (data.inventoryValue) {
            document.getElementById('inventoryValue').textContent = `$${(data.inventoryValue / 1000000).toFixed(1)}M`;
        }
        if (data.lowStockItems) {
            document.getElementById('lowStockItems').textContent = data.lowStockItems;
        }
        if (data.activeSuppliers) {
            document.getElementById('activeSuppliers').textContent = data.activeSuppliers;
        }
        if (data.avgLeadTime) {
            document.getElementById('avgLeadTime').textContent = data.avgLeadTime.toFixed(1);
        }
        if (data.stockAccuracy) {
            document.getElementById('stockAccuracy').textContent = `${data.stockAccuracy.toFixed(1)}%`;
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

// Initialize materials module when DOM is loaded
let materialsModule;

document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.dashboard !== 'undefined') {
        materialsModule = new MaterialsModule(window.dashboard);
    }
});
