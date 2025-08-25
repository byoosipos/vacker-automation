class ProjectsModule {
    constructor() {
        this.chartInstances = new Map();
        this.projects = [];
        this.milestones = [];
        this.tasks = [];
        this.resources = [];
        this.projectTypes = ['Development', 'Implementation', 'Research', 'Marketing', 'Operations'];
        this.statusTypes = ['Planning', 'In Progress', 'On Hold', 'Completed', 'Cancelled'];
        this.priorityLevels = ['Low', 'Medium', 'High', 'Critical'];
    }

    async render() {
        const container = document.getElementById('projects-content');
        if (!container) return;

        container.innerHTML = `
            <div class="projects-module">
                <!-- Projects KPIs -->
                <div class="projects-kpis">
                    <div class="kpi-grid">
                        <div class="kpi-card">
                            <div class="kpi-icon">📊</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="total-projects">0</div>
                                <div class="kpi-label">Total Projects</div>
                                <div class="kpi-change positive">+5 this month</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">🚀</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="active-projects">0</div>
                                <div class="kpi-label">Active Projects</div>
                                <div class="kpi-change positive">85% completion rate</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">⏰</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="overdue-projects">0</div>
                                <div class="kpi-label">Overdue Projects</div>
                                <div class="kpi-change negative">Need attention</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">💰</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="project-budget">$0</div>
                                <div class="kpi-label">Total Budget</div>
                                <div class="kpi-change neutral">Allocated funds</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">👥</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="team-members">0</div>
                                <div class="kpi-label">Team Members</div>
                                <div class="kpi-change positive">Across all projects</div>
                            </div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-icon">✅</div>
                            <div class="kpi-content">
                                <div class="kpi-value" id="completion-rate">0%</div>
                                <div class="kpi-label">Avg Completion</div>
                                <div class="kpi-change positive">On track</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Project Charts Row -->
                <div class="projects-charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Project Status Distribution</h3>
                            <div class="chart-controls">
                                <select id="project-status-period">
                                    <option value="current">Current</option>
                                    <option value="last-month">Last Month</option>
                                    <option value="last-quarter">Last Quarter</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="project-status-chart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Project Timeline Progress</h3>
                            <div class="chart-controls">
                                <select id="timeline-view">
                                    <option value="weekly">Weekly</option>
                                    <option value="monthly">Monthly</option>
                                    <option value="quarterly">Quarterly</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="project-timeline-chart"></canvas>
                    </div>
                </div>

                <div class="projects-charts-row">
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Budget vs Actual Spending</h3>
                            <div class="chart-controls">
                                <select id="budget-project">
                                    <option value="all">All Projects</option>
                                    <option value="active">Active Only</option>
                                    <option value="completed">Completed</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="project-budget-chart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-header">
                            <h3>Resource Allocation</h3>
                            <div class="chart-controls">
                                <select id="resource-type">
                                    <option value="teams">Teams</option>
                                    <option value="hours">Hours</option>
                                    <option value="budget">Budget</option>
                                </select>
                            </div>
                        </div>
                        <canvas id="resource-allocation-chart"></canvas>
                    </div>
                </div>

                <!-- Project Details Section -->
                <div class="projects-details">
                    <div class="section-tabs">
                        <button class="tab-btn active" data-tab="active-projects">Active Projects</button>
                        <button class="tab-btn" data-tab="project-milestones">Milestones</button>
                        <button class="tab-btn" data-tab="team-performance">Team Performance</button>
                        <button class="tab-btn" data-tab="risk-analysis">Risk Analysis</button>
                    </div>

                    <div class="tab-content active" id="active-projects">
                        <div class="projects-table-container">
                            <div class="table-header">
                                <h3>Active Projects Overview</h3>
                                <div class="table-controls">
                                    <input type="text" id="project-search" placeholder="Search projects...">
                                    <select id="project-filter">
                                        <option value="all">All Projects</option>
                                        <option value="high-priority">High Priority</option>
                                        <option value="overdue">Overdue</option>
                                        <option value="at-risk">At Risk</option>
                                    </select>
                                </div>
                            </div>
                            <div class="table-responsive">
                                <table class="projects-table">
                                    <thead>
                                        <tr>
                                            <th>Project Name</th>
                                            <th>Type</th>
                                            <th>Status</th>
                                            <th>Priority</th>
                                            <th>Progress</th>
                                            <th>Team Lead</th>
                                            <th>Budget</th>
                                            <th>Deadline</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody id="projects-table-body">
                                        <!-- Dynamic content -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    <div class="tab-content" id="project-milestones">
                        <div class="milestones-section">
                            <div class="milestones-header">
                                <h3>Project Milestones</h3>
                                <div class="milestone-filters">
                                    <select id="milestone-project">
                                        <option value="all">All Projects</option>
                                    </select>
                                    <select id="milestone-status">
                                        <option value="all">All Statuses</option>
                                        <option value="upcoming">Upcoming</option>
                                        <option value="completed">Completed</option>
                                        <option value="overdue">Overdue</option>
                                    </select>
                                </div>
                            </div>
                            <div class="milestones-timeline" id="milestones-timeline">
                                <!-- Dynamic milestone timeline -->
                            </div>
                        </div>
                    </div>

                    <div class="tab-content" id="team-performance">
                        <div class="team-performance-section">
                            <div class="performance-grid">
                                <div class="performance-card">
                                    <h4>Team Productivity</h4>
                                    <canvas id="team-productivity-chart"></canvas>
                                </div>
                                <div class="performance-card">
                                    <h4>Task Completion Rate</h4>
                                    <canvas id="task-completion-chart"></canvas>
                                </div>
                                <div class="performance-card">
                                    <h4>Team Workload</h4>
                                    <canvas id="team-workload-chart"></canvas>
                                </div>
                                <div class="performance-card">
                                    <h4>Skills Distribution</h4>
                                    <canvas id="skills-distribution-chart"></canvas>
                                </div>
                            </div>
                            <div class="team-members-list">
                                <h4>Team Members Performance</h4>
                                <div class="team-table-responsive">
                                    <table class="team-table">
                                        <thead>
                                            <tr>
                                                <th>Team Member</th>
                                                <th>Role</th>
                                                <th>Active Projects</th>
                                                <th>Tasks Completed</th>
                                                <th>Performance Score</th>
                                                <th>Workload</th>
                                                <th>Availability</th>
                                            </tr>
                                        </thead>
                                        <tbody id="team-performance-body">
                                            <!-- Dynamic content -->
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="tab-content" id="risk-analysis">
                        <div class="risk-analysis-section">
                            <div class="risk-overview">
                                <div class="risk-summary-cards">
                                    <div class="risk-card high-risk">
                                        <div class="risk-level">High Risk</div>
                                        <div class="risk-count" id="high-risk-count">0</div>
                                        <div class="risk-description">Projects requiring immediate attention</div>
                                    </div>
                                    <div class="risk-card medium-risk">
                                        <div class="risk-level">Medium Risk</div>
                                        <div class="risk-count" id="medium-risk-count">0</div>
                                        <div class="risk-description">Projects to monitor closely</div>
                                    </div>
                                    <div class="risk-card low-risk">
                                        <div class="risk-level">Low Risk</div>
                                        <div class="risk-count" id="low-risk-count">0</div>
                                        <div class="risk-description">Projects on track</div>
                                    </div>
                                </div>
                            </div>
                            <div class="risk-details">
                                <div class="risk-chart-container">
                                    <canvas id="risk-analysis-chart"></canvas>
                                </div>
                                <div class="risk-factors">
                                    <h4>Risk Factors Analysis</h4>
                                    <div class="risk-factors-list" id="risk-factors-list">
                                        <!-- Dynamic risk factors -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        await this.initializeProjectsData();
        this.renderProjectCharts();
        this.setupEventListeners();
        this.populateProjectTables();
    }

    async initializeProjectsData() {
        // Generate sample project data
        this.projects = [
            {
                id: 1,
                name: 'ERP System Enhancement',
                type: 'Development',
                status: 'In Progress',
                priority: 'High',
                progress: 75,
                teamLead: 'John Smith',
                budget: 150000,
                spent: 112500,
                deadline: '2025-07-15',
                startDate: '2025-01-15',
                teamSize: 8,
                riskLevel: 'Medium'
            },
            {
                id: 2,
                name: 'Customer Portal Implementation',
                type: 'Implementation',
                status: 'Planning',
                priority: 'Medium',
                progress: 25,
                teamLead: 'Sarah Johnson',
                budget: 80000,
                spent: 20000,
                deadline: '2025-09-30',
                startDate: '2025-03-01',
                teamSize: 5,
                riskLevel: 'Low'
            },
            {
                id: 3,
                name: 'Market Research Analysis',
                type: 'Research',
                status: 'Completed',
                priority: 'Medium',
                progress: 100,
                teamLead: 'Mike Davis',
                budget: 45000,
                spent: 43500,
                deadline: '2025-04-30',
                startDate: '2025-02-01',
                teamSize: 3,
                riskLevel: 'Low'
            },
            {
                id: 4,
                name: 'Digital Marketing Campaign',
                type: 'Marketing',
                status: 'In Progress',
                priority: 'High',
                progress: 60,
                teamLead: 'Lisa Wilson',
                budget: 120000,
                spent: 95000,
                deadline: '2025-06-30',
                startDate: '2025-01-01',
                teamSize: 6,
                riskLevel: 'High'
            },
            {
                id: 5,
                name: 'Infrastructure Upgrade',
                type: 'Operations',
                status: 'On Hold',
                priority: 'Critical',
                progress: 40,
                teamLead: 'Tom Brown',
                budget: 200000,
                spent: 75000,
                deadline: '2025-08-15',
                startDate: '2025-02-15',
                teamSize: 10,
                riskLevel: 'High'
            }
        ];

        this.updateProjectKPIs();
    }

    updateProjectKPIs() {
        const totalProjects = this.projects.length;
        const activeProjects = this.projects.filter(p => p.status === 'In Progress').length;
        const overdueProjects = this.projects.filter(p => new Date(p.deadline) < new Date() && p.status !== 'Completed').length;
        const totalBudget = this.projects.reduce((sum, p) => sum + p.budget, 0);
        const totalTeamMembers = this.projects.reduce((sum, p) => sum + p.teamSize, 0);
        const avgCompletion = this.projects.reduce((sum, p) => sum + p.progress, 0) / totalProjects;

        document.getElementById('total-projects').textContent = totalProjects;
        document.getElementById('active-projects').textContent = activeProjects;
        document.getElementById('overdue-projects').textContent = overdueProjects;
        document.getElementById('project-budget').textContent = `$${(totalBudget / 1000).toFixed(0)}K`;
        document.getElementById('team-members').textContent = totalTeamMembers;
        document.getElementById('completion-rate').textContent = `${avgCompletion.toFixed(1)}%`;
    }

    renderProjectCharts() {
        this.renderProjectStatusChart();
        this.renderProjectTimelineChart();
        this.renderProjectBudgetChart();
        this.renderResourceAllocationChart();
        this.renderTeamPerformanceCharts();
        this.renderRiskAnalysisChart();
    }

    renderProjectStatusChart() {
        const ctx = document.getElementById('project-status-chart');
        if (!ctx) return;

        const statusCounts = this.statusTypes.map(status => 
            this.projects.filter(p => p.status === status).length
        );

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: this.statusTypes,
                datasets: [{
                    data: statusCounts,
                    backgroundColor: [
                        '#3498db',  // Planning
                        '#2ecc71',  // In Progress
                        '#f39c12',  // On Hold
                        '#27ae60',  // Completed
                        '#e74c3c'   // Cancelled
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
                                return `${context.label}: ${context.raw} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });

        this.chartInstances.set('project-status-chart', chart);
    }

    renderProjectTimelineChart() {
        const ctx = document.getElementById('project-timeline-chart');
        if (!ctx) return;

        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const plannedData = months.map(() => Math.floor(Math.random() * 10) + 5);
        const actualData = months.map((month, index) => {
            if (index <= 4) return plannedData[index] + Math.floor(Math.random() * 3) - 1;
            return null;
        });

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'Planned Progress',
                        data: plannedData,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Actual Progress',
                        data: actualData,
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
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
                            text: 'Progress (%)'
                        }
                    }
                }
            }
        });

        this.chartInstances.set('project-timeline-chart', chart);
    }

    renderProjectBudgetChart() {
        const ctx = document.getElementById('project-budget-chart');
        if (!ctx) return;

        const projectNames = this.projects.map(p => p.name.length > 15 ? p.name.substring(0, 15) + '...' : p.name);
        const budgetData = this.projects.map(p => p.budget / 1000);
        const spentData = this.projects.map(p => p.spent / 1000);

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: projectNames,
                datasets: [
                    {
                        label: 'Budget (K)',
                        data: budgetData,
                        backgroundColor: 'rgba(52, 152, 219, 0.7)',
                        borderColor: '#3498db',
                        borderWidth: 1
                    },
                    {
                        label: 'Spent (K)',
                        data: spentData,
                        backgroundColor: 'rgba(231, 76, 60, 0.7)',
                        borderColor: '#e74c3c',
                        borderWidth: 1
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
                            text: 'Amount ($K)'
                        }
                    }
                }
            }
        });

        this.chartInstances.set('project-budget-chart', chart);
    }

    renderResourceAllocationChart() {
        const ctx = document.getElementById('resource-allocation-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: this.projectTypes,
                datasets: [{
                    data: this.projectTypes.map(type => 
                        this.projects.filter(p => p.type === type).length
                    ),
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

        this.chartInstances.set('resource-allocation-chart', chart);
    }

    renderTeamPerformanceCharts() {
        // Team Productivity Chart
        const productivityCtx = document.getElementById('team-productivity-chart');
        if (productivityCtx) {
            const chart = new Chart(productivityCtx, {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{
                        label: 'Tasks Completed',
                        data: [12, 19, 15, 22],
                        borderColor: '#2ecc71',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
            this.chartInstances.set('team-productivity-chart', chart);
        }

        // Task Completion Chart
        const completionCtx = document.getElementById('task-completion-chart');
        if (completionCtx) {
            const chart = new Chart(completionCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Completed', 'In Progress', 'Pending'],
                    datasets: [{
                        data: [65, 25, 10],
                        backgroundColor: ['#2ecc71', '#f39c12', '#e74c3c']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
            this.chartInstances.set('task-completion-chart', chart);
        }
    }

    renderRiskAnalysisChart() {
        const ctx = document.getElementById('risk-analysis-chart');
        if (!ctx) return;

        const riskData = {
            'Low': this.projects.filter(p => p.riskLevel === 'Low').length,
            'Medium': this.projects.filter(p => p.riskLevel === 'Medium').length,
            'High': this.projects.filter(p => p.riskLevel === 'High').length
        };

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(riskData),
                datasets: [{
                    label: 'Number of Projects',
                    data: Object.values(riskData),
                    backgroundColor: [
                        '#2ecc71',  // Low
                        '#f39c12',  // Medium
                        '#e74c3c'   // High
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        stepSize: 1
                    }
                }
            }
        });

        this.chartInstances.set('risk-analysis-chart', chart);

        // Update risk counts
        document.getElementById('high-risk-count').textContent = riskData.High || 0;
        document.getElementById('medium-risk-count').textContent = riskData.Medium || 0;
        document.getElementById('low-risk-count').textContent = riskData.Low || 0;
    }

    populateProjectTables() {
        this.populateActiveProjectsTable();
        this.populateTeamPerformanceTable();
        this.populateMilestoneTimeline();
        this.populateRiskFactors();
    }

    populateActiveProjectsTable() {
        const tbody = document.getElementById('projects-table-body');
        if (!tbody) return;

        tbody.innerHTML = this.projects.map(project => `
            <tr class="project-row ${project.status.toLowerCase().replace(' ', '-')}">
                <td>
                    <div class="project-name">
                        <strong>${project.name}</strong>
                        <small>ID: ${project.id}</small>
                    </div>
                </td>
                <td>
                    <span class="project-type ${project.type.toLowerCase()}">${project.type}</span>
                </td>
                <td>
                    <span class="status-badge ${project.status.toLowerCase().replace(' ', '-')}">${project.status}</span>
                </td>
                <td>
                    <span class="priority-badge ${project.priority.toLowerCase()}">${project.priority}</span>
                </td>
                <td>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${project.progress}%"></div>
                        </div>
                        <span class="progress-text">${project.progress}%</span>
                    </div>
                </td>
                <td>${project.teamLead}</td>
                <td>
                    <div class="budget-info">
                        <div>$${(project.budget / 1000).toFixed(0)}K</div>
                        <small>Spent: $${(project.spent / 1000).toFixed(0)}K</small>
                    </div>
                </td>
                <td>
                    <div class="deadline-info ${new Date(project.deadline) < new Date() ? 'overdue' : ''}">
                        ${new Date(project.deadline).toLocaleDateString()}
                    </div>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-sm btn-primary" onclick="viewProject(${project.id})">View</button>
                        <button class="btn-sm btn-secondary" onclick="editProject(${project.id})">Edit</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    populateTeamPerformanceTable() {
        const tbody = document.getElementById('team-performance-body');
        if (!tbody) return;

        const teamMembers = [
            { name: 'John Smith', role: 'Project Manager', projects: 2, tasks: 45, score: 92, workload: 85, availability: 'Available' },
            { name: 'Sarah Johnson', role: 'Developer', projects: 3, tasks: 38, score: 88, workload: 75, availability: 'Busy' },
            { name: 'Mike Davis', role: 'Analyst', projects: 1, tasks: 22, score: 95, workload: 60, availability: 'Available' },
            { name: 'Lisa Wilson', role: 'Designer', projects: 2, tasks: 31, score: 87, workload: 80, availability: 'Available' },
            { name: 'Tom Brown', role: 'DevOps', projects: 2, tasks: 28, score: 90, workload: 70, availability: 'On Leave' }
        ];

        tbody.innerHTML = teamMembers.map(member => `
            <tr>
                <td>
                    <div class="member-info">
                        <strong>${member.name}</strong>
                    </div>
                </td>
                <td>${member.role}</td>
                <td>${member.projects}</td>
                <td>${member.tasks}</td>
                <td>
                    <div class="score-container">
                        <span class="score-value">${member.score}</span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${member.score}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="workload-container">
                        <span class="workload-value">${member.workload}%</span>
                        <div class="workload-bar">
                            <div class="workload-fill ${member.workload > 80 ? 'high' : member.workload > 60 ? 'medium' : 'low'}" style="width: ${member.workload}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="availability-badge ${member.availability.toLowerCase().replace(' ', '-')}">${member.availability}</span>
                </td>
            </tr>
        `).join('');
    }

    populateMilestoneTimeline() {
        const container = document.getElementById('milestones-timeline');
        if (!container) return;

        const milestones = [
            { id: 1, projectId: 1, name: 'Requirements Analysis Complete', date: '2025-02-15', status: 'completed' },
            { id: 2, projectId: 1, name: 'Design Phase Complete', date: '2025-03-30', status: 'completed' },
            { id: 3, projectId: 1, name: 'Development Phase 1', date: '2025-05-15', status: 'upcoming' },
            { id: 4, projectId: 2, name: 'Technical Specifications', date: '2025-04-01', status: 'completed' },
            { id: 5, projectId: 2, name: 'Prototype Development', date: '2025-06-15', status: 'upcoming' }
        ];

        container.innerHTML = `
            <div class="timeline">
                ${milestones.map(milestone => `
                    <div class="timeline-item ${milestone.status}">
                        <div class="timeline-marker"></div>
                        <div class="timeline-content">
                            <div class="milestone-header">
                                <h4>${milestone.name}</h4>
                                <span class="milestone-date">${new Date(milestone.date).toLocaleDateString()}</span>
                            </div>
                            <div class="milestone-project">
                                Project: ${this.projects.find(p => p.id === milestone.projectId)?.name || 'Unknown'}
                            </div>
                            <div class="milestone-status">
                                <span class="status-badge ${milestone.status}">${milestone.status.charAt(0).toUpperCase() + milestone.status.slice(1)}</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    populateRiskFactors() {
        const container = document.getElementById('risk-factors-list');
        if (!container) return;

        const riskFactors = [
            { factor: 'Budget Overrun', impact: 'High', probability: 'Medium', projects: ['ERP System Enhancement', 'Infrastructure Upgrade'] },
            { factor: 'Resource Availability', impact: 'Medium', probability: 'High', projects: ['Digital Marketing Campaign'] },
            { factor: 'Technical Complexity', impact: 'High', probability: 'Low', projects: ['Customer Portal Implementation'] },
            { factor: 'Timeline Delays', impact: 'Medium', probability: 'Medium', projects: ['ERP System Enhancement', 'Digital Marketing Campaign'] }
        ];

        container.innerHTML = riskFactors.map(risk => `
            <div class="risk-factor-item">
                <div class="risk-factor-header">
                    <h5>${risk.factor}</h5>
                    <div class="risk-indicators">
                        <span class="risk-indicator impact ${risk.impact.toLowerCase()}">Impact: ${risk.impact}</span>
                        <span class="risk-indicator probability ${risk.probability.toLowerCase()}">Probability: ${risk.probability}</span>
                    </div>
                </div>
                <div class="risk-affected-projects">
                    <strong>Affected Projects:</strong> ${risk.projects.join(', ')}
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
        const searchInput = document.getElementById('project-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterProjects(e.target.value);
            });
        }

        const filterSelect = document.getElementById('project-filter');
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                this.filterProjectsByStatus(e.target.value);
            });
        }

        // Chart control listeners
        document.getElementById('project-status-period')?.addEventListener('change', () => {
            this.updateProjectStatusChart();
        });

        document.getElementById('timeline-view')?.addEventListener('change', () => {
            this.updateTimelineChart();
        });

        document.getElementById('budget-project')?.addEventListener('change', () => {
            this.updateBudgetChart();
        });

        document.getElementById('resource-type')?.addEventListener('change', () => {
            this.updateResourceChart();
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

    filterProjects(searchTerm) {
        const rows = document.querySelectorAll('.project-row');
        rows.forEach(row => {
            const projectName = row.querySelector('.project-name strong').textContent.toLowerCase();
            const teamLead = row.cells[5].textContent.toLowerCase();
            if (projectName.includes(searchTerm.toLowerCase()) || teamLead.includes(searchTerm.toLowerCase())) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    filterProjectsByStatus(filterValue) {
        const rows = document.querySelectorAll('.project-row');
        rows.forEach(row => {
            const shouldShow = filterValue === 'all' || row.classList.contains(filterValue.replace('-', ''));
            row.style.display = shouldShow ? '' : 'none';
        });
    }

    updateProjectStatusChart() {
        // Implement chart update logic based on selected period
        console.log('Updating project status chart');
    }

    updateTimelineChart() {
        // Implement timeline chart update logic
        console.log('Updating timeline chart');
    }

    updateBudgetChart() {
        // Implement budget chart update logic
        console.log('Updating budget chart');
    }

    updateResourceChart() {
        // Implement resource chart update logic
        console.log('Updating resource chart');
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
window.viewProject = function(projectId) {
    console.log('Viewing project:', projectId);
    // Implement project view logic
};

window.editProject = function(projectId) {
    console.log('Editing project:', projectId);
    // Implement project edit logic
};

// Export the module
window.ProjectsModule = ProjectsModule;
