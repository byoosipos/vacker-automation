class HRModule {
    constructor() {
        this.chartInstances = new Map();
        this.employees = [];
        this.departments = [];
        this.positions = [];
        this.performanceData = [];
        this.attendanceData = [];
        this.leaveRequests = [];
        this.recruitmentData = [];
    }

    async render() {
        const container = document.getElementById('hr-content');
        if (!container) return;

        container.innerHTML = `
            <div class="hr-module">
                <!-- HR KPIs -->
                <div class="hr-kpis">
                    <div class="kpi-grid">
                        <div class="kpi-card">
                            <div class="kpi-icon">👥</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="total-employees">0</div>
                                <div class="kpi-label">Total Employees</div>
                                <div class="kpi-change positive">+12 this quarter</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">📈</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="employee-satisfaction">0%</div>
                                <div class="kpi-label">Employee Satisfaction</div>
                                <div class="kpi-change positive">+3% from last survey</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">🔄</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="turnover-rate">0%</div>
                                <div class="kpi-label">Turnover Rate</div>
                                <div class="kpi-change negative">Annual rate</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">🎯</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="recruitment-efficiency">0%</div>
                                <div class="kpi-label">Recruitment Efficiency</div>
                                <div class="kpi-change positive">Time to hire improvement</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">📚</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="training-completion">0%</div>
                                <div class="kpi-label">Training Completion</div>
                                <div class="kpi-change positive">This quarter</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">⏰</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="average-attendance">0%</div>
                                <div class="kpi-label">Attendance Rate</div>
                                <div class="kpi-change neutral">Monthly average</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- HR Charts Row -->
                <div class="hr-charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Department Distribution</h3>
                            <div class="chart-controls">
                                <select id="department-view">
                                    <option value="headcount">Headcount</option>
                                    <option value="budget">Budget Allocation</option>
                                    <option value="performance">Performance</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="department-distribution-chart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Employee Growth Trend</h3>
                            <div class="chart-controls">
                                <select id="growth-period">
                                    <option value="monthly">Monthly</option>
                                    <option value="quarterly">Quarterly</option>
                                    <option value="yearly">Yearly</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="employee-growth-chart"></canvas>
                    </div>
                </div>

                <div class="hr-charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Performance Distribution</h3>
                            <div class="chart-controls">
                                <select id="performance-period">
                                    <option value="current">Current Period</option>
                                    <option value="last-quarter">Last Quarter</option>
                                    <option value="yearly">Yearly</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="performance-distribution-chart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Attendance & Leave Analysis</h3>
                            <div class="chart-controls">
                                <select id="attendance-view">
                                    <option value="monthly">Monthly</option>
                                    <option value="quarterly">Quarterly</option>
                                    <option value="department">By Department</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="attendance-chart"></canvas>
                    </div>
                </div>

                <!-- HR Details Section -->
                <div class="hr-details">
                    <div class="section-tabs">
                        <button class="tab-btn active" data-tab="employee-directory">Employee Directory</button>
                        <button class="tab-btn" data-tab="performance-management">Performance</button>
                        <button class="tab-btn" data-tab="recruitment-pipeline">Recruitment</button>
                        <button class="tab-btn" data-tab="training-development">Training</button>
                        <button class="tab-btn" data-tab="compensation-benefits">Compensation</button>
                    </div>

                    <div class="tab-content active" id="employee-directory">
                        <div class="employee-directory-section">
                            <div class="directory-header">
                                <h3>Employee Directory</h3>
                                <div class="directory-controls">
                                    <input type="text" id="employee-search" placeholder="Search employees...">
                                    <select id="department-filter">
                                        <option value="all">All Departments</option>
                                        <option value="engineering">Engineering</option>
                                        <option value="sales">Sales</option>
                                        <option value="marketing">Marketing</option>
                                        <option value="hr">Human Resources</option>
                                        <option value="finance">Finance</option>
                                    </select>
                                    <select id="position-filter">
                                        <option value="all">All Positions</option>
                                        <option value="manager">Manager</option>
                                        <option value="senior">Senior</option>
                                        <option value="junior">Junior</option>
                                        <option value="intern">Intern</option>
                                    </select>
                                </div>
                            </div>
                            <div class="employees-grid" id="employees-grid">
                                <!-- Dynamic employee cards -->
                            </div>
                        </div>
                    </div>

                    <div class="tab-content" id="performance-management">
                        <div class="performance-section">
                            <div class="performance-overview">
                                <div class="performance-stats">
                                    <div class="stat-card">
                                        <h4>Top Performers</h4>
                                        <div class="stat-value">15</div>
                                        <div class="stat-description">Employees with 90%+ rating</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Reviews Pending</h4>
                                        <div class="stat-value">8</div>
                                        <div class="stat-description">Performance reviews due</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Goal Achievement</h4>
                                        <div class="stat-value">87%</div>
                                        <div class="stat-description">Average goal completion</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Career Development</h4>
                                        <div class="stat-value">23</div>
                                        <div class="stat-description">Employees in development programs</div>
                                    </div>
                                </div>
                            </div>
                            <div class="performance-charts">
                                <div class="chart-container">
                                    <h4>Performance Ratings by Department</h4>
                                    <canvas id="department-performance-chart"></canvas>
                                </div>
                                <div class="chart-container">
                                    <h4>Goal Achievement Trends</h4>
                                    <canvas id="goal-achievement-chart"></canvas>
                                </div>
                            </div>
                            <div class="performance-table-container">
                                <h4>Employee Performance Summary</h4>
                                <div class="table-responsive">
                                    <table class="performance-table">
                                        <thead>
                                            <tr>
                                                <th>Employee</th>
                                                <th>Department</th>
                                                <th>Position</th>
                                                <th>Performance Rating</th>
                                                <th>Goals Achieved</th>
                                                <th>Last Review</th>
                                                <th>Next Review</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody id="performance-table-body">
                                            <!-- Dynamic content -->
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="tab-content" id="recruitment-pipeline">
                        <div class="recruitment-section">
                            <div class="recruitment-overview">
                                <div class="recruitment-stats">
                                    <div class="stat-card">
                                        <h4>Open Positions</h4>
                                        <div class="stat-value">12</div>
                                        <div class="stat-description">Across all departments</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Applications</h4>
                                        <div class="stat-value">156</div>
                                        <div class="stat-description">This month</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Interviews Scheduled</h4>
                                        <div class="stat-value">24</div>
                                        <div class="stat-description">Next 2 weeks</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Time to Hire</h4>
                                        <div class="stat-value">18 days</div>
                                        <div class="stat-description">Average duration</div>
                                    </div>
                                </div>
                            </div>
                            <div class="recruitment-pipeline-visual">
                                <div class="pipeline-stage">
                                    <div class="stage-header">Application</div>
                                    <div class="stage-count">156</div>
                                    <div class="stage-bar" style="width: 100%; background: #3498db;"></div>
                                </div>
                                <div class="pipeline-stage">
                                    <div class="stage-header">Screening</div>
                                    <div class="stage-count">89</div>
                                    <div class="stage-bar" style="width: 57%; background: #2ecc71;"></div>
                                </div>
                                <div class="pipeline-stage">
                                    <div class="stage-header">Interview</div>
                                    <div class="stage-count">45</div>
                                    <div class="stage-bar" style="width: 29%; background: #f39c12;"></div>
                                </div>
                                <div class="pipeline-stage">
                                    <div class="stage-header">Final Review</div>
                                    <div class="stage-count">18</div>
                                    <div class="stage-bar" style="width: 12%; background: #e74c3c;"></div>
                                </div>
                                <div class="pipeline-stage">
                                    <div class="stage-header">Offer</div>
                                    <div class="stage-count">8</div>
                                    <div class="stage-bar" style="width: 5%; background: #9b59b6;"></div>
                                </div>
                            </div>
                            <div class="open-positions-table">
                                <h4>Open Positions</h4>
                                <div class="table-responsive">
                                    <table class="positions-table">
                                        <thead>
                                            <tr>
                                                <th>Position</th>
                                                <th>Department</th>
                                                <th>Level</th>
                                                <th>Applications</th>
                                                <th>Posted Date</th>
                                                <th>Priority</th>
                                                <th>Status</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody id="positions-table-body">
                                            <!-- Dynamic content -->
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="tab-content" id="training-development">
                        <div class="training-section">
                            <div class="training-overview">
                                <div class="training-stats">
                                    <div class="stat-card">
                                        <h4>Active Programs</h4>
                                        <div class="stat-value">8</div>
                                        <div class="stat-description">Training programs running</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Enrolled Employees</h4>
                                        <div class="stat-value">145</div>
                                        <div class="stat-description">In various programs</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Completion Rate</h4>
                                        <div class="stat-value">92%</div>
                                        <div class="stat-description">This quarter</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Training Budget</h4>
                                        <div class="stat-value">$85K</div>
                                        <div class="stat-description">Spent this year</div>
                                    </div>
                                </div>
                            </div>
                            <div class="training-charts">
                                <div class="chart-container">
                                    <h4>Training Completion by Department</h4>
                                    <canvas id="training-completion-chart"></canvas>
                                </div>
                                <div class="chart-container">
                                    <h4>Skill Development Progress</h4>
                                    <canvas id="skill-development-chart"></canvas>
                                </div>
                            </div>
                            <div class="training-programs">
                                <h4>Current Training Programs</h4>
                                <div class="programs-grid" id="training-programs-grid">
                                    <!-- Dynamic training program cards -->
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="tab-content" id="compensation-benefits">
                        <div class="compensation-section">
                            <div class="compensation-overview">
                                <div class="compensation-stats">
                                    <div class="stat-card">
                                        <h4>Average Salary</h4>
                                        <div class="stat-value">$75K</div>
                                        <div class="stat-description">Company-wide average</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Salary Increase</h4>
                                        <div class="stat-value">4.2%</div>
                                        <div class="stat-description">Average this year</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Benefits Enrollment</h4>
                                        <div class="stat-value">98%</div>
                                        <div class="stat-description">Employee participation</div>
                                    </div>
                                    <div class="stat-card">
                                        <h4>Total Compensation</h4>
                                        <div class="stat-value">$12.5M</div>
                                        <div class="stat-description">Annual budget</div>
                                    </div>
                                </div>
                            </div>
                            <div class="compensation-charts">
                                <div class="chart-container">
                                    <h4>Salary Distribution by Department</h4>
                                    <canvas id="salary-distribution-chart"></canvas>
                                </div>
                                <div class="chart-container">
                                    <h4>Benefits Utilization</h4>
                                    <canvas id="benefits-utilization-chart"></canvas>
                                </div>
                            </div>
                            <div class="compensation-analysis">
                                <div class="analysis-section">
                                    <h4>Compensation Analysis</h4>
                                    <div class="analysis-grid">
                                        <div class="analysis-card">
                                            <h5>Market Comparison</h5>
                                            <div class="comparison-data">
                                                <div class="comparison-item">
                                                    <span>vs Market Average:</span>
                                                    <span class="positive">+8%</span>
                                                </div>
                                                <div class="comparison-item">
                                                    <span>vs Industry Median:</span>
                                                    <span class="positive">+12%</span>
                                                </div>
                                                <div class="comparison-item">
                                                    <span>Competitiveness Score:</span>
                                                    <span class="neutral">85/100</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="analysis-card">
                                            <h5>Pay Equity</h5>
                                            <div class="equity-data">
                                                <div class="equity-item">
                                                    <span>Gender Pay Gap:</span>
                                                    <span class="positive">2.1%</span>
                                                </div>
                                                <div class="equity-item">
                                                    <span>Experience Adjustment:</span>
                                                    <span class="neutral">Fair</span>
                                                </div>
                                                <div class="equity-item">
                                                    <span>Performance Correlation:</span>
                                                    <span class="positive">Strong</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        await this.initializeHRData();
        this.renderHRCharts();
        this.setupEventListeners();
        this.populateHRTables();
    }

    async initializeHRData() {
        // Generate sample employee data
        this.employees = [
            {
                id: 1,
                name: 'John Smith',
                department: 'Engineering',
                position: 'Senior Developer',
                level: 'Senior',
                hireDate: '2022-03-15',
                salary: 95000,
                performanceRating: 4.5,
                attendance: 96,
                email: 'john.smith@company.com',
                phone: '+1 234-567-8901',
                manager: 'Alice Johnson'
            },
            {
                id: 2,
                name: 'Sarah Johnson',
                department: 'Marketing',
                position: 'Marketing Manager',
                level: 'Manager',
                hireDate: '2021-08-20',
                salary: 78000,
                performanceRating: 4.2,
                attendance: 94,
                email: 'sarah.johnson@company.com',
                phone: '+1 234-567-8902',
                manager: 'David Wilson'
            },
            {
                id: 3,
                name: 'Mike Davis',
                department: 'Sales',
                position: 'Sales Representative',
                level: 'Junior',
                hireDate: '2023-01-10',
                salary: 55000,
                performanceRating: 4.0,
                attendance: 92,
                email: 'mike.davis@company.com',
                phone: '+1 234-567-8903',
                manager: 'Lisa Brown'
            },
            {
                id: 4,
                name: 'Lisa Wilson',
                department: 'HR',
                position: 'HR Specialist',
                level: 'Senior',
                hireDate: '2020-05-12',
                salary: 65000,
                performanceRating: 4.8,
                attendance: 98,
                email: 'lisa.wilson@company.com',
                phone: '+1 234-567-8904',
                manager: 'Tom Anderson'
            },
            {
                id: 5,
                name: 'Tom Brown',
                department: 'Finance',
                position: 'Financial Analyst',
                level: 'Junior',
                hireDate: '2022-11-01',
                salary: 58000,
                performanceRating: 3.8,
                attendance: 89,
                email: 'tom.brown@company.com',
                phone: '+1 234-567-8905',
                manager: 'Emily Clark'
            }
        ];

        this.departments = [
            { name: 'Engineering', headcount: 45, budget: 4200000 },
            { name: 'Sales', headcount: 32, budget: 2800000 },
            { name: 'Marketing', headcount: 18, budget: 1500000 },
            { name: 'HR', headcount: 12, budget: 900000 },
            { name: 'Finance', headcount: 15, budget: 1200000 },
            { name: 'Operations', headcount: 25, budget: 1800000 }
        ];

        this.updateHRKPIs();
    }

    updateHRKPIs() {
        const totalEmployees = this.employees.length;
        const satisfaction = 87; // Placeholder
        const turnoverRate = 8.5; // Placeholder
        const recruitmentEfficiency = 92; // Placeholder
        const trainingCompletion = 85; // Placeholder
        const avgAttendance = this.employees.reduce((sum, emp) => sum + emp.attendance, 0) / totalEmployees;

        document.getElementById('total-employees').textContent = totalEmployees;
        document.getElementById('employee-satisfaction').textContent = `${satisfaction}%`;
        document.getElementById('turnover-rate').textContent = `${turnoverRate}%`;
        document.getElementById('recruitment-efficiency').textContent = `${recruitmentEfficiency}%`;
        document.getElementById('training-completion').textContent = `${trainingCompletion}%`;
        document.getElementById('average-attendance').textContent = `${avgAttendance.toFixed(1)}%`;
    }

    renderHRCharts() {
        this.renderDepartmentDistributionChart();
        this.renderEmployeeGrowthChart();
        this.renderPerformanceDistributionChart();
        this.renderAttendanceChart();
        this.renderDepartmentPerformanceChart();
        this.renderGoalAchievementChart();
        this.renderTrainingCompletionChart();
        this.renderSkillDevelopmentChart();
        this.renderSalaryDistributionChart();
        this.renderBenefitsUtilizationChart();
    }

    renderDepartmentDistributionChart() {
        const ctx = document.getElementById('department-distribution-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: this.departments.map(d => d.name),
                datasets: [{
                    data: this.departments.map(d => d.headcount),
                    backgroundColor: [
                        '#3498db',
                        '#2ecc71',
                        '#f39c12',
                        '#e74c3c',
                        '#9b59b6',
                        '#1abc9c'
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
                                return `${context.label}: ${context.raw} employees (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });

        this.chartInstances.set('department-distribution-chart', chart);
    }

    renderEmployeeGrowthChart() {
        const ctx = document.getElementById('employee-growth-chart');
        if (!ctx) return;

        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const employeeGrowth = [140, 142, 145, 148, 152, 155, 158, 162, 165, 168, 172, 175];

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Total Employees',
                    data: employeeGrowth,
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
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
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Number of Employees'
                        }
                    }
                }
            }
        });

        this.chartInstances.set('employee-growth-chart', chart);
    }

    renderPerformanceDistributionChart() {
        const ctx = document.getElementById('performance-distribution-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Excellent (4.5-5.0)', 'Good (4.0-4.4)', 'Satisfactory (3.5-3.9)', 'Needs Improvement (3.0-3.4)', 'Poor (<3.0)'],
                datasets: [{
                    label: 'Number of Employees',
                    data: [25, 45, 35, 12, 3],
                    backgroundColor: [
                        '#27ae60',
                        '#2ecc71',
                        '#f39c12',
                        '#e67e22',
                        '#e74c3c'
                    ]
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
                            text: 'Number of Employees'
                        }
                    }
                }
            }
        });

        this.chartInstances.set('performance-distribution-chart', chart);
    }

    renderAttendanceChart() {
        const ctx = document.getElementById('attendance-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [
                    {
                        label: 'Attendance Rate',
                        data: [94, 96, 93, 95, 97, 94],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Leave Requests',
                        data: [8, 12, 15, 18, 10, 14],
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1'
                    }
                ]
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
                            text: 'Attendance Rate (%)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Leave Requests'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });

        this.chartInstances.set('attendance-chart', chart);
    }

    renderDepartmentPerformanceChart() {
        const ctx = document.getElementById('department-performance-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: this.departments.map(d => d.name),
                datasets: [{
                    label: 'Average Performance Rating',
                    data: [4.2, 4.0, 4.3, 4.5, 3.9, 4.1],
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
                        max: 5,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });

        this.chartInstances.set('department-performance-chart', chart);
    }

    renderGoalAchievementChart() {
        const ctx = document.getElementById('goal-achievement-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                datasets: [{
                    label: 'Goal Achievement Rate',
                    data: [82, 85, 87, 89],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Achievement Rate (%)'
                        }
                    }
                }
            }
        });

        this.chartInstances.set('goal-achievement-chart', chart);
    }

    renderTrainingCompletionChart() {
        const ctx = document.getElementById('training-completion-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.departments.map(d => d.name),
                datasets: [{
                    label: 'Completion Rate (%)',
                    data: [92, 88, 95, 90, 85, 89],
                    backgroundColor: '#3498db'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Completion Rate (%)'
                        }
                    }
                }
            }
        });

        this.chartInstances.set('training-completion-chart', chart);
    }

    renderSkillDevelopmentChart() {
        const ctx = document.getElementById('skill-development-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Technical Skills', 'Leadership', 'Communication', 'Project Management', 'Other'],
                datasets: [{
                    data: [35, 20, 25, 15, 5],
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
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        this.chartInstances.set('skill-development-chart', chart);
    }

    renderSalaryDistributionChart() {
        const ctx = document.getElementById('salary-distribution-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.departments.map(d => d.name),
                datasets: [{
                    label: 'Average Salary ($K)',
                    data: [85, 65, 70, 60, 75, 68],
                    backgroundColor: '#2ecc71'
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
                            text: 'Salary ($K)'
                        }
                    }
                }
            }
        });

        this.chartInstances.set('salary-distribution-chart', chart);
    }

    renderBenefitsUtilizationChart() {
        const ctx = document.getElementById('benefits-utilization-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Health Insurance', 'Dental', 'Vision', '401k', 'PTO', 'Training Budget'],
                datasets: [{
                    label: 'Utilization Rate (%)',
                    data: [98, 85, 72, 89, 95, 67],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.2)',
                    pointBackgroundColor: '#e74c3c'
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

        this.chartInstances.set('benefits-utilization-chart', chart);
    }

    populateHRTables() {
        this.populateEmployeeDirectory();
        this.populatePerformanceTable();
        this.populatePositionsTable();
        this.populateTrainingPrograms();
    }

    populateEmployeeDirectory() {
        const container = document.getElementById('employees-grid');
        if (!container) return;

        container.innerHTML = this.employees.map(employee => `
            <div class="employee-card">
                <div class="employee-avatar">
                    <div class="avatar-placeholder">${employee.name.split(' ').map(n => n[0]).join('')}</div>
                </div>
                <div class="employee-info">
                    <h4>${employee.name}</h4>
                    <div class="employee-title">${employee.position}</div>
                    <div class="employee-department">${employee.department}</div>
                    <div class="employee-details">
                        <div class="detail-item">
                            <span class="label">Email:</span>
                            <span class="value">${employee.email}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Phone:</span>
                            <span class="value">${employee.phone}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Hire Date:</span>
                            <span class="value">${new Date(employee.hireDate).toLocaleDateString()}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Manager:</span>
                            <span class="value">${employee.manager}</span>
                        </div>
                    </div>
                    <div class="employee-stats">
                        <div class="stat">
                            <span class="stat-label">Performance</span>
                            <span class="stat-value">${employee.performanceRating}/5</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Attendance</span>
                            <span class="stat-value">${employee.attendance}%</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    populatePerformanceTable() {
        const tbody = document.getElementById('performance-table-body');
        if (!tbody) return;

        tbody.innerHTML = this.employees.map(employee => `
            <tr>
                <td>
                    <div class="employee-info">
                        <strong>${employee.name}</strong>
                        <small>ID: ${employee.id}</small>
                    </div>
                </td>
                <td>${employee.department}</td>
                <td>${employee.position}</td>
                <td>
                    <div class="rating-container">
                        <span class="rating-value">${employee.performanceRating}/5</span>
                        <div class="rating-stars">
                            ${'★'.repeat(Math.floor(employee.performanceRating))}${'☆'.repeat(5 - Math.floor(employee.performanceRating))}
                        </div>
                    </div>
                </td>
                <td>
                    <div class="goals-progress">
                        <span>${Math.floor(Math.random() * 3) + 6}/8</span>
                        <div class="progress-bar small">
                            <div class="progress-fill" style="width: ${75 + Math.random() * 25}%"></div>
                        </div>
                    </div>
                </td>
                <td>${new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toLocaleDateString()}</td>
                <td>${new Date(Date.now() + Math.random() * 90 * 24 * 60 * 60 * 1000).toLocaleDateString()}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-sm btn-primary" onclick="viewPerformance(${employee.id})">View</button>
                        <button class="btn-sm btn-secondary" onclick="scheduleReview(${employee.id})">Review</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    populatePositionsTable() {
        const tbody = document.getElementById('positions-table-body');
        if (!tbody) return;

        const openPositions = [
            { title: 'Senior Frontend Developer', department: 'Engineering', level: 'Senior', applications: 45, posted: '2025-05-15', priority: 'High', status: 'Active' },
            { title: 'Marketing Coordinator', department: 'Marketing', level: 'Junior', applications: 32, posted: '2025-05-10', priority: 'Medium', status: 'Active' },
            { title: 'Sales Manager', department: 'Sales', level: 'Manager', applications: 28, posted: '2025-05-08', priority: 'High', status: 'Interviewing' },
            { title: 'Data Analyst', department: 'Finance', level: 'Junior', applications: 51, posted: '2025-05-01', priority: 'Medium', status: 'Active' }
        ];

        tbody.innerHTML = openPositions.map(position => `
            <tr>
                <td><strong>${position.title}</strong></td>
                <td>${position.department}</td>
                <td>
                    <span class="level-badge ${position.level.toLowerCase()}">${position.level}</span>
                </td>
                <td>${position.applications}</td>
                <td>${new Date(position.posted).toLocaleDateString()}</td>
                <td>
                    <span class="priority-badge ${position.priority.toLowerCase()}">${position.priority}</span>
                </td>
                <td>
                    <span class="status-badge ${position.status.toLowerCase()}">${position.status}</span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-sm btn-primary" onclick="viewApplications('${position.title}')">View</button>
                        <button class="btn-sm btn-secondary" onclick="editPosition('${position.title}')">Edit</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    populateTrainingPrograms() {
        const container = document.getElementById('training-programs-grid');
        if (!container) return;

        const programs = [
            { name: 'Leadership Development', participants: 25, duration: '8 weeks', completion: 92, status: 'Active' },
            { name: 'Technical Skills Bootcamp', participants: 40, duration: '12 weeks', completion: 78, status: 'Active' },
            { name: 'Communication Workshop', participants: 60, duration: '4 weeks', completion: 95, status: 'Completed' },
            { name: 'Project Management Certification', participants: 18, duration: '16 weeks', completion: 65, status: 'Active' }
        ];

        container.innerHTML = programs.map(program => `
            <div class="training-program-card">
                <div class="program-header">
                    <h5>${program.name}</h5>
                    <span class="program-status ${program.status.toLowerCase()}">${program.status}</span>
                </div>
                <div class="program-details">
                    <div class="detail-row">
                        <span>Participants:</span>
                        <span>${program.participants}</span>
                    </div>
                    <div class="detail-row">
                        <span>Duration:</span>
                        <span>${program.duration}</span>
                    </div>
                    <div class="detail-row">
                        <span>Completion:</span>
                        <span>${program.completion}%</span>
                    </div>
                </div>
                <div class="program-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${program.completion}%"></div>
                    </div>
                </div>
            </div>
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
        const searchInput = document.getElementById('employee-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterEmployees(e.target.value);
            });
        }

        const departmentFilter = document.getElementById('department-filter');
        if (departmentFilter) {
            departmentFilter.addEventListener('change', (e) => {
                this.filterEmployeesByDepartment(e.target.value);
            });
        }

        const positionFilter = document.getElementById('position-filter');
        if (positionFilter) {
            positionFilter.addEventListener('change', (e) => {
                this.filterEmployeesByPosition(e.target.value);
            });
        }

        // Chart control listeners
        document.getElementById('department-view')?.addEventListener('change', () => {
            this.updateDepartmentChart();
        });

        document.getElementById('growth-period')?.addEventListener('change', () => {
            this.updateGrowthChart();
        });

        document.getElementById('performance-period')?.addEventListener('change', () => {
            this.updatePerformanceChart();
        });

        document.getElementById('attendance-view')?.addEventListener('change', () => {
            this.updateAttendanceChart();
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

    filterEmployees(searchTerm) {
        const cards = document.querySelectorAll('.employee-card');
        cards.forEach(card => {
            const name = card.querySelector('h4').textContent.toLowerCase();
            const position = card.querySelector('.employee-title').textContent.toLowerCase();
            const department = card.querySelector('.employee-department').textContent.toLowerCase();
            
            if (name.includes(searchTerm.toLowerCase()) || 
                position.includes(searchTerm.toLowerCase()) || 
                department.includes(searchTerm.toLowerCase())) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    filterEmployeesByDepartment(department) {
        const cards = document.querySelectorAll('.employee-card');
        cards.forEach(card => {
            const empDepartment = card.querySelector('.employee-department').textContent;
            if (department === 'all' || empDepartment.toLowerCase() === department.toLowerCase()) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    filterEmployeesByPosition(position) {
        const cards = document.querySelectorAll('.employee-card');
        cards.forEach(card => {
            const empPosition = card.querySelector('.employee-title').textContent.toLowerCase();
            if (position === 'all' || empPosition.includes(position.toLowerCase())) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    updateDepartmentChart() {
        console.log('Updating department chart');
        // Implement chart update logic
    }

    updateGrowthChart() {
        console.log('Updating growth chart');
        // Implement chart update logic
    }

    updatePerformanceChart() {
        console.log('Updating performance chart');
        // Implement chart update logic
    }

    updateAttendanceChart() {
        console.log('Updating attendance chart');
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
window.viewPerformance = function(employeeId) {
    console.log('Viewing performance for employee:', employeeId);
    // Implement performance view logic
};

window.scheduleReview = function(employeeId) {
    console.log('Scheduling review for employee:', employeeId);
    // Implement review scheduling logic
};

window.viewApplications = function(position) {
    console.log('Viewing applications for position:', position);
    // Implement applications view logic
};

window.editPosition = function(position) {
    console.log('Editing position:', position);
    // Implement position edit logic
};

// Export the module
window.HRModule = HRModule;
