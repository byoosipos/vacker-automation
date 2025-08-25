/**
 * Operations Management Module
 * Handles production operations, inventory management, workflow optimization, and performance monitoring
 */

class OperationsModule {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.charts = {};
        this.currentFilters = {
            facility: 'all',
            department: 'all',
            shift: 'all',
            period: '30'
        };
    }

    render() {
        return `
            <div class="operations-module">
                <div class="module-header">
                    <h2><i class="fas fa-cogs"></i> Operations Management</h2>
                    <div class="module-actions">
                        <button class="btn-primary" onclick="operationsModule.startProduction()">
                            <i class="fas fa-play"></i> Start Production
                        </button>
                        <button class="btn-secondary" onclick="operationsModule.scheduleShift()">
                            <i class="fas fa-calendar"></i> Schedule Shift
                        </button>
                        <button class="btn-secondary" onclick="operationsModule.exportOperationsReport()">
                            <i class="fas fa-download"></i> Export Report
                        </button>
                    </div>
                </div>

                <!-- KPIs Row -->
                <div class="kpi-row">
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-percentage"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="overallEfficiency">87.5%</div>
                            <div class="kpi-label">Overall Efficiency</div>
                            <div class="kpi-change positive">+2.3%</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="dailyOutput">2,450</div>
                            <div class="kpi-label">Daily Output (units)</div>
                            <div class="kpi-change positive">+8.2%</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="cycleTime">4.2</div>
                            <div class="kpi-label">Cycle Time (hrs)</div>
                            <div class="kpi-change negative">+0.3</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="defectRate">1.8%</div>
                            <div class="kpi-label">Defect Rate</div>
                            <div class="kpi-change positive">-0.5%</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-tools"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="equipmentUptime">94.7%</div>
                            <div class="kpi-label">Equipment Uptime</div>
                            <div class="kpi-change positive">+1.2%</div>
                        </div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">
                            <i class="fas fa-users"></i>
                        </div>
                        <div class="kpi-content">
                            <div class="kpi-value" id="workerUtilization">92.3%</div>
                            <div class="kpi-label">Worker Utilization</div>
                            <div class="kpi-change positive">+0.8%</div>
                        </div>
                    </div>
                </div>

                <!-- Charts Row -->
                <div class="charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Production Performance</h3>
                            <div class="chart-actions">
                                <select onchange="operationsModule.updateProductionChart(this.value)">
                                    <option value="daily">Daily</option>
                                    <option value="weekly">Weekly</option>
                                    <option value="monthly">Monthly</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="productionPerformanceChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Equipment Status</h3>
                            <div class="chart-actions">
                                <button onclick="operationsModule.refreshEquipmentStatus()">
                                    <i class="fas fa-sync-alt"></i>
                                </button>
                            </div>
                        </div>
                        <canvas id="equipmentStatusChart"></canvas>
                    </div>
                </div>

                <div class="charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Quality Metrics</h3>
                            <div class="chart-actions">
                                <select onchange="operationsModule.updateQualityChart(this.value)">
                                    <option value="defects">Defect Rate</option>
                                    <option value="rework">Rework Rate</option>
                                    <option value="customer">Customer Complaints</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="qualityMetricsChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Capacity Utilization</h3>
                            <div class="chart-actions">
                                <select onchange="operationsModule.updateCapacityChart(this.value)">
                                    <option value="department">By Department</option>
                                    <option value="shift">By Shift</option>
                                    <option value="equipment">By Equipment</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="capacityUtilizationChart"></canvas>
                    </div>
                </div>

                <!-- Tabs Section -->
                <div class="tab-container">
                    <div class="tab-buttons">
                        <button class="tab-button active" onclick="operationsModule.switchTab('production')">
                            <i class="fas fa-industry"></i> Production
                        </button>
                        <button class="tab-button" onclick="operationsModule.switchTab('equipment')">
                            <i class="fas fa-tools"></i> Equipment
                        </button>
                        <button class="tab-button" onclick="operationsModule.switchTab('workflow')">
                            <i class="fas fa-project-diagram"></i> Workflow
                        </button>
                        <button class="tab-button" onclick="operationsModule.switchTab('quality')">
                            <i class="fas fa-award"></i> Quality Control
                        </button>
                        <button class="tab-button" onclick="operationsModule.switchTab('performance')">
                            <i class="fas fa-chart-bar"></i> Performance
                        </button>
                    </div>

                    <div class="tab-content">
                        <!-- Production Tab -->
                        <div id="productionTab" class="tab-pane active">
                            <div class="tab-controls">
                                <div class="production-summary">
                                    <div class="summary-card">
                                        <h4>Active Production Lines</h4>
                                        <div class="summary-value">8/10</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Current Shift</h4>
                                        <div class="summary-value">Day Shift</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Target Output</h4>
                                        <div class="summary-value">2,500 units</div>
                                    </div>
                                    <div class="summary-card">
                                        <h4>Actual Output</h4>
                                        <div class="summary-value">2,450 units</div>
                                    </div>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="operationsModule.scheduleProduction()">
                                        <i class="fas fa-calendar-plus"></i> Schedule Production
                                    </button>
                                    <button onclick="operationsModule.adjustTargets()">
                                        <i class="fas fa-bullseye"></i> Adjust Targets
                                    </button>
                                </div>
                            </div>
                            <div class="production-lines" id="productionLines">
                                <!-- Production lines will be populated here -->
                            </div>
                        </div>

                        <!-- Equipment Tab -->
                        <div id="equipmentTab" class="tab-pane">
                            <div class="tab-controls">
                                <div class="equipment-metrics">
                                    <div class="metric-card">
                                        <h4>Total Equipment</h4>
                                        <div class="metric-value">45</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Operational</h4>
                                        <div class="metric-value">42</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Under Maintenance</h4>
                                        <div class="metric-value">2</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Out of Service</h4>
                                        <div class="metric-value">1</div>
                                    </div>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="operationsModule.scheduleMaintenace()">
                                        <i class="fas fa-wrench"></i> Schedule Maintenance
                                    </button>
                                    <button onclick="operationsModule.equipmentDiagnostics()">
                                        <i class="fas fa-stethoscope"></i> Diagnostics
                                    </button>
                                </div>
                            </div>
                            <div class="equipment-grid" id="equipmentGrid">
                                <!-- Equipment will be populated here -->
                            </div>
                        </div>

                        <!-- Workflow Tab -->
                        <div id="workflowTab" class="tab-pane">
                            <div class="tab-controls">
                                <div class="workflow-metrics">
                                    <div class="metric-card">
                                        <h4>Active Workflows</h4>
                                        <div class="metric-value">12</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Bottlenecks</h4>
                                        <div class="metric-value">3</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Optimization Score</h4>
                                        <div class="metric-value">85%</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Cycle Efficiency</h4>
                                        <div class="metric-value">92%</div>
                                    </div>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="operationsModule.optimizeWorkflow()">
                                        <i class="fas fa-magic"></i> Optimize
                                    </button>
                                    <button onclick="operationsModule.analyzeBottlenecks()">
                                        <i class="fas fa-search"></i> Analyze Bottlenecks
                                    </button>
                                </div>
                            </div>
                            <div class="workflow-diagram" id="workflowDiagram">
                                <!-- Workflow diagram will be populated here -->
                            </div>
                        </div>

                        <!-- Quality Control Tab -->
                        <div id="qualityTab" class="tab-pane">
                            <div class="tab-controls">
                                <div class="quality-metrics">
                                    <div class="metric-card">
                                        <h4>First Pass Yield</h4>
                                        <div class="metric-value">97.2%</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Customer Returns</h4>
                                        <div class="metric-value">0.8%</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Quality Score</h4>
                                        <div class="metric-value">4.6/5</div>
                                    </div>
                                    <div class="metric-card">
                                        <h4>Inspection Rate</h4>
                                        <div class="metric-value">15%</div>
                                    </div>
                                </div>
                                <div class="action-buttons">
                                    <button onclick="operationsModule.qualityAudit()">
                                        <i class="fas fa-clipboard-check"></i> Quality Audit
                                    </button>
                                    <button onclick="operationsModule.correctiveActions()">
                                        <i class="fas fa-tools"></i> Corrective Actions
                                    </button>
                                </div>
                            </div>
                            <div class="quality-dashboard" id="qualityDashboard">
                                <!-- Quality dashboard will be populated here -->
                            </div>
                        </div>

                        <!-- Performance Tab -->
                        <div id="performanceTab" class="tab-pane">
                            <div class="performance-analytics">
                                <div class="analytics-chart">
                                    <h4>OEE Trends</h4>
                                    <canvas id="oeeTrendsChart"></canvas>
                                </div>
                                <div class="analytics-chart">
                                    <h4>Productivity Analysis</h4>
                                    <canvas id="productivityChart"></canvas>
                                </div>
                                <div class="analytics-chart">
                                    <h4>Cost per Unit</h4>
                                    <canvas id="costPerUnitChart"></canvas>
                                </div>
                                <div class="analytics-insights">
                                    <h4>Performance Insights</h4>
                                    <div class="insights-list" id="performanceInsights">
                                        <!-- Performance insights will be populated here -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderOperationsCharts() {
        this.renderProductionPerformanceChart();
        this.renderEquipmentStatusChart();
        this.renderQualityMetricsChart();
        this.renderCapacityUtilizationChart();
        this.renderPerformanceCharts();
    }

    renderProductionPerformanceChart() {
        const ctx = document.getElementById('productionPerformanceChart').getContext('2d');
        
        const days = Array.from({length: 30}, (_, i) => {
            const date = new Date();
            date.setDate(date.getDate() - 29 + i);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });

        this.charts.productionPerformance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: days,
                datasets: [{
                    label: 'Target Output',
                    data: Array.from({length: 30}, () => 2500),
                    borderColor: '#95a5a6',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    tension: 0
                }, {
                    label: 'Actual Output',
                    data: Array.from({length: 30}, () => Math.floor(Math.random() * 500) + 2200),
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Efficiency %',
                    data: Array.from({length: 30}, () => Math.floor(Math.random() * 20) + 80),
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Output (units)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Efficiency %'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                        min: 0,
                        max: 100
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

    renderEquipmentStatusChart() {
        const ctx = document.getElementById('equipmentStatusChart').getContext('2d');
        
        this.charts.equipmentStatus = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Operational', 'Under Maintenance', 'Out of Service', 'Standby'],
                datasets: [{
                    data: [42, 2, 1, 0],
                    backgroundColor: [
                        '#2ecc71',
                        '#f39c12',
                        '#e74c3c',
                        '#95a5a6'
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
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                            }
                        }
                    }
                }
            }
        });
    }

    renderQualityMetricsChart() {
        const ctx = document.getElementById('qualityMetricsChart').getContext('2d');
        
        const weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];

        this.charts.qualityMetrics = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: weeks,
                datasets: [{
                    label: 'Defect Rate (%)',
                    data: [2.1, 1.8, 1.9, 1.6],
                    backgroundColor: '#e74c3c',
                    yAxisID: 'y'
                }, {
                    label: 'First Pass Yield (%)',
                    data: [96.5, 97.2, 96.8, 97.5],
                    backgroundColor: '#2ecc71',
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
                            text: 'Defect Rate %'
                        },
                        min: 0,
                        max: 5
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'First Pass Yield %'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                        min: 90,
                        max: 100
                    }
                }
            }
        });
    }

    renderCapacityUtilizationChart() {
        const ctx = document.getElementById('capacityUtilizationChart').getContext('2d');
        
        this.charts.capacityUtilization = new Chart(ctx, {
            type: 'horizontalBar',
            data: {
                labels: ['Assembly Line 1', 'Assembly Line 2', 'Welding Station', 'Paint Shop', 'Quality Control'],
                datasets: [{
                    label: 'Capacity Utilization %',
                    data: [92, 88, 95, 78, 85],
                    backgroundColor: [
                        '#3498db',
                        '#2ecc71',
                        '#f39c12',
                        '#e74c3c',
                        '#9b59b6'
                    ]
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Utilization %'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    renderPerformanceCharts() {
        // OEE Trends Chart
        const oeeCtx = document.getElementById('oeeTrendsChart')?.getContext('2d');
        if (oeeCtx) {
            this.charts.oeeTrends = new Chart(oeeCtx, {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{
                        label: 'Availability',
                        data: [94, 96, 94, 95],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)'
                    }, {
                        label: 'Performance',
                        data: [88, 90, 89, 91],
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)'
                    }, {
                        label: 'Quality',
                        data: [97, 98, 97, 98],
                        borderColor: '#f39c12',
                        backgroundColor: 'rgba(243, 156, 18, 0.1)'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Percentage (%)'
                            }
                        }
                    }
                }
            });
        }

        // Productivity Chart
        const productivityCtx = document.getElementById('productivityChart')?.getContext('2d');
        if (productivityCtx) {
            this.charts.productivity = new Chart(productivityCtx, {
                type: 'bar',
                data: {
                    labels: ['Day Shift', 'Evening Shift', 'Night Shift'],
                    datasets: [{
                        label: 'Units per Hour',
                        data: [102, 98, 95],
                        backgroundColor: '#3498db'
                    }, {
                        label: 'Target',
                        data: [100, 100, 100],
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
                                text: 'Units per Hour'
                            }
                        }
                    }
                }
            });
        }

        // Cost per Unit Chart
        const costCtx = document.getElementById('costPerUnitChart')?.getContext('2d');
        if (costCtx) {
            this.charts.costPerUnit = new Chart(costCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Actual Cost',
                        data: [45.2, 44.8, 46.1, 45.5, 44.9, 45.3],
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Target Cost',
                        data: [45, 45, 45, 45, 45, 45],
                        borderColor: '#95a5a6',
                        backgroundColor: 'transparent',
                        borderDash: [5, 5]
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: 'Cost per Unit ($)'
                            }
                        }
                    }
                }
            });
        }
    }

    populateOperationsTables() {
        this.populateProductionLines();
        this.populateEquipmentGrid();
        this.populateWorkflowDiagram();
        this.populateQualityDashboard();
        this.populatePerformanceInsights();
    }

    populateProductionLines() {
        const productionLines = document.getElementById('productionLines');
        if (!productionLines) return;

        const lines = [
            {
                id: 'LINE001',
                name: 'Assembly Line 1',
                status: 'running',
                currentOrder: 'ORD-2024-001',
                targetOutput: 300,
                actualOutput: 285,
                efficiency: 95,
                shift: 'Day Shift',
                supervisor: 'John Smith',
                nextMaintenance: '2024-06-01'
            },
            {
                id: 'LINE002',
                name: 'Assembly Line 2',
                status: 'running',
                currentOrder: 'ORD-2024-002',
                targetOutput: 280,
                actualOutput: 275,
                efficiency: 98.2,
                shift: 'Day Shift',
                supervisor: 'Sarah Johnson',
                nextMaintenance: '2024-06-03'
            },
            {
                id: 'LINE003',
                name: 'Welding Station',
                status: 'maintenance',
                currentOrder: null,
                targetOutput: 150,
                actualOutput: 0,
                efficiency: 0,
                shift: 'Day Shift',
                supervisor: 'Mike Wilson',
                nextMaintenance: '2024-05-29'
            }
        ];

        productionLines.innerHTML = lines.map(line => `
            <div class="production-line-card ${line.status}">
                <div class="line-header">
                    <h4>${line.name}</h4>
                    <span class="status-badge ${line.status}">${line.status}</span>
                </div>
                <div class="line-details">
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="label">Current Order:</span>
                            <span class="value">${line.currentOrder || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Target Output:</span>
                            <span class="value">${line.targetOutput} units</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Actual Output:</span>
                            <span class="value">${line.actualOutput} units</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Efficiency:</span>
                            <span class="value">${line.efficiency}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Shift:</span>
                            <span class="value">${line.shift}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Supervisor:</span>
                            <span class="value">${line.supervisor}</span>
                        </div>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${(line.actualOutput / line.targetOutput) * 100}%"></div>
                </div>
                <div class="line-actions">
                    <button onclick="operationsModule.viewLineDetails('${line.id}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="operationsModule.controlLine('${line.id}')" title="Control">
                        <i class="fas fa-cog"></i>
                    </button>
                    <button onclick="operationsModule.maintainLine('${line.id}')" title="Maintenance">
                        <i class="fas fa-wrench"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    populateEquipmentGrid() {
        const equipmentGrid = document.getElementById('equipmentGrid');
        if (!equipmentGrid) return;

        const equipment = [
            {
                id: 'EQ001',
                name: 'CNC Machine #1',
                type: 'CNC',
                status: 'operational',
                utilization: 92,
                lastMaintenance: '2024-05-15',
                nextMaintenance: '2024-06-15',
                efficiency: 95,
                location: 'Workshop A',
                operator: 'Tom Brown'
            },
            {
                id: 'EQ002',
                name: 'Hydraulic Press',
                type: 'Press',
                status: 'operational',
                utilization: 78,
                lastMaintenance: '2024-05-10',
                nextMaintenance: '2024-06-10',
                efficiency: 88,
                location: 'Workshop B',
                operator: 'Lisa Chen'
            },
            {
                id: 'EQ003',
                name: 'Paint Booth #1',
                type: 'Paint',
                status: 'maintenance',
                utilization: 0,
                lastMaintenance: '2024-05-28',
                nextMaintenance: '2024-06-28',
                efficiency: 0,
                location: 'Paint Shop',
                operator: null
            }
        ];

        equipmentGrid.innerHTML = equipment.map(eq => `
            <div class="equipment-card ${eq.status}">
                <div class="equipment-header">
                    <h4>${eq.name}</h4>
                    <span class="status-badge ${eq.status}">${eq.status}</span>
                </div>
                <div class="equipment-details">
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="label">Type:</span>
                            <span class="value">${eq.type}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Utilization:</span>
                            <span class="value">${eq.utilization}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Efficiency:</span>
                            <span class="value">${eq.efficiency}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Location:</span>
                            <span class="value">${eq.location}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Operator:</span>
                            <span class="value">${eq.operator || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Next Maintenance:</span>
                            <span class="value">${eq.nextMaintenance}</span>
                        </div>
                    </div>
                </div>
                <div class="utilization-bar">
                    <div class="utilization-fill" style="width: ${eq.utilization}%"></div>
                </div>
                <div class="equipment-actions">
                    <button onclick="operationsModule.viewEquipmentHistory('${eq.id}')" title="History">
                        <i class="fas fa-history"></i>
                    </button>
                    <button onclick="operationsModule.scheduleMaintenance('${eq.id}')" title="Schedule Maintenance">
                        <i class="fas fa-calendar-plus"></i>
                    </button>
                    <button onclick="operationsModule.equipmentDiagnostic('${eq.id}')" title="Diagnostics">
                        <i class="fas fa-stethoscope"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    populateWorkflowDiagram() {
        const workflowDiagram = document.getElementById('workflowDiagram');
        if (!workflowDiagram) return;

        workflowDiagram.innerHTML = `
            <div class="workflow-visualization">
                <div class="workflow-stage">
                    <div class="stage-box">
                        <h5>Raw Materials</h5>
                        <div class="stage-metrics">
                            <span>Buffer: 85%</span>
                            <span>Rate: 120/hr</span>
                        </div>
                    </div>
                    <div class="stage-connector">→</div>
                </div>
                <div class="workflow-stage">
                    <div class="stage-box bottleneck">
                        <h5>Machining</h5>
                        <div class="stage-metrics">
                            <span>Buffer: 45%</span>
                            <span>Rate: 95/hr</span>
                        </div>
                        <div class="bottleneck-indicator">Bottleneck</div>
                    </div>
                    <div class="stage-connector">→</div>
                </div>
                <div class="workflow-stage">
                    <div class="stage-box">
                        <h5>Assembly</h5>
                        <div class="stage-metrics">
                            <span>Buffer: 92%</span>
                            <span>Rate: 110/hr</span>
                        </div>
                    </div>
                    <div class="stage-connector">→</div>
                </div>
                <div class="workflow-stage">
                    <div class="stage-box">
                        <h5>Quality Control</h5>
                        <div class="stage-metrics">
                            <span>Buffer: 78%</span>
                            <span>Rate: 105/hr</span>
                        </div>
                    </div>
                    <div class="stage-connector">→</div>
                </div>
                <div class="workflow-stage">
                    <div class="stage-box">
                        <h5>Finished Goods</h5>
                        <div class="stage-metrics">
                            <span>Inventory: 1,250</span>
                            <span>Rate: 98/hr</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="workflow-recommendations">
                <h5>Optimization Recommendations:</h5>
                <ul>
                    <li>Increase machining capacity by 15% to eliminate bottleneck</li>
                    <li>Redistribute workers from assembly to machining during peak hours</li>
                    <li>Schedule maintenance during low-demand periods</li>
                </ul>
            </div>
        `;
    }

    populateQualityDashboard() {
        const qualityDashboard = document.getElementById('qualityDashboard');
        if (!qualityDashboard) return;

        qualityDashboard.innerHTML = `
            <div class="quality-metrics-grid">
                <div class="quality-card">
                    <h5>Defect Analysis</h5>
                    <div class="defect-types">
                        <div class="defect-item">
                            <span>Surface Defects</span>
                            <span>45%</span>
                        </div>
                        <div class="defect-item">
                            <span>Dimensional Issues</span>
                            <span>30%</span>
                        </div>
                        <div class="defect-item">
                            <span>Material Defects</span>
                            <span>25%</span>
                        </div>
                    </div>
                </div>
                <div class="quality-card">
                    <h5>Recent Inspections</h5>
                    <div class="inspection-list">
                        <div class="inspection-item">
                            <span>Batch #B001</span>
                            <span class="status passed">Passed</span>
                        </div>
                        <div class="inspection-item">
                            <span>Batch #B002</span>
                            <span class="status failed">Failed</span>
                        </div>
                        <div class="inspection-item">
                            <span>Batch #B003</span>
                            <span class="status pending">Pending</span>
                        </div>
                    </div>
                </div>
                <div class="quality-card">
                    <h5>Corrective Actions</h5>
                    <div class="actions-list">
                        <div class="action-item">
                            <span>Adjust welding parameters</span>
                            <span class="priority high">High</span>
                        </div>
                        <div class="action-item">
                            <span>Replace worn cutting tools</span>
                            <span class="priority medium">Medium</span>
                        </div>
                        <div class="action-item">
                            <span>Update work instructions</span>
                            <span class="priority low">Low</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    populatePerformanceInsights() {
        const performanceInsights = document.getElementById('performanceInsights');
        if (!performanceInsights) return;

        const insights = [
            {
                type: 'success',
                title: 'Efficiency Improvement',
                description: 'Overall equipment efficiency increased by 2.3% this month',
                action: 'Document best practices',
                priority: 'medium'
            },
            {
                type: 'warning',
                title: 'Bottleneck Alert',
                description: 'Machining station is limiting overall throughput',
                action: 'Consider capacity expansion',
                priority: 'high'
            },
            {
                type: 'info',
                title: 'Maintenance Optimization',
                description: 'Predictive maintenance reduced unplanned downtime by 18%',
                action: 'Expand predictive maintenance program',
                priority: 'low'
            }
        ];

        performanceInsights.innerHTML = insights.map(insight => `
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
        if (tabName === 'performance') {
            setTimeout(() => this.renderPerformanceCharts(), 100);
        }
    }

    // Chart update methods
    updateProductionChart(period) {
        console.log('Updating production chart:', period);
    }

    updateQualityChart(metric) {
        console.log('Updating quality chart:', metric);
    }

    updateCapacityChart(view) {
        console.log('Updating capacity chart:', view);
    }

    refreshEquipmentStatus() {
        console.log('Refreshing equipment status');
    }

    // Action methods
    startProduction() {
        console.log('Starting production');
    }

    scheduleShift() {
        console.log('Scheduling shift');
    }

    exportOperationsReport() {
        console.log('Exporting operations report');
    }

    scheduleProduction() {
        console.log('Scheduling production');
    }

    adjustTargets() {
        console.log('Adjusting production targets');
    }

    viewLineDetails(lineId) {
        console.log('Viewing line details:', lineId);
    }

    controlLine(lineId) {
        console.log('Controlling line:', lineId);
    }

    maintainLine(lineId) {
        console.log('Maintaining line:', lineId);
    }

    scheduleMaintenace() {
        console.log('Scheduling maintenance');
    }

    equipmentDiagnostics() {
        console.log('Running equipment diagnostics');
    }

    viewEquipmentHistory(equipmentId) {
        console.log('Viewing equipment history:', equipmentId);
    }

    scheduleMaintenance(equipmentId) {
        console.log('Scheduling maintenance for:', equipmentId);
    }

    equipmentDiagnostic(equipmentId) {
        console.log('Running diagnostic for:', equipmentId);
    }

    optimizeWorkflow() {
        console.log('Optimizing workflow');
    }

    analyzeBottlenecks() {
        console.log('Analyzing bottlenecks');
    }

    qualityAudit() {
        console.log('Starting quality audit');
    }

    correctiveActions() {
        console.log('Managing corrective actions');
    }

    // Update methods for real-time data
    updateKPIs(data) {
        if (data.overallEfficiency) {
            document.getElementById('overallEfficiency').textContent = `${data.overallEfficiency.toFixed(1)}%`;
        }
        if (data.dailyOutput) {
            document.getElementById('dailyOutput').textContent = data.dailyOutput.toLocaleString();
        }
        if (data.cycleTime) {
            document.getElementById('cycleTime').textContent = data.cycleTime.toFixed(1);
        }
        if (data.defectRate) {
            document.getElementById('defectRate').textContent = `${data.defectRate.toFixed(1)}%`;
        }
        if (data.equipmentUptime) {
            document.getElementById('equipmentUptime').textContent = `${data.equipmentUptime.toFixed(1)}%`;
        }
        if (data.workerUtilization) {
            document.getElementById('workerUtilization').textContent = `${data.workerUtilization.toFixed(1)}%`;
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

// Initialize operations module when DOM is loaded
let operationsModule;

document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.dashboard !== 'undefined') {
        operationsModule = new OperationsModule(window.dashboard);
    }
});
