frappe.pages['project-profitability-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Project Profitability Dashboard',
		single_column: true
	});

	// Load Chart.js from CDN if not already loaded
	if (typeof Chart === 'undefined') {
		// Add Chart.js script to head
		let script = document.createElement('script');
		script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js';
		script.onload = function() {
			// Initialize dashboard after Chart.js is loaded
			let dashboard = new ProjectProfitabilityDashboard(page);
			dashboard.show();
		};
		document.head.appendChild(script);
	} else {
		// Initialize dashboard
		let dashboard = new ProjectProfitabilityDashboard(page);
		dashboard.show();
	}
};

class ProjectProfitabilityDashboard {
	constructor(page) {
		this.page = page;
		this.filters = {};
		this.dashboard_data = {};
		this.charts = {};
		
		// Set default filters
		this.filters = {
			company: frappe.defaults.get_user_default('Company'),
			from_date: frappe.datetime.add_months(frappe.datetime.get_today(), -12),
			to_date: frappe.datetime.get_today(),
			project: null,
			all_projects: false // Default to false (By Date Range)
		};
	}

	show() {
		// Clean up any existing dashboard first
		this.cleanup();
		
		this.make_filters();
		this.make_dashboard();
		this.refresh_data();
		// Add new UI sections for forecast and risks
		this.add_forecast_and_risk_sections();
	}

	add_forecast_and_risk_sections() {
		// Add Profitability Forecast chart section
		$(this.page.body).prepend(`
			<div class="row mt-4">
				<div class="col-md-8">
					<div class="dashboard-section">
						<h4 class="section-title">Profitability Forecast (Next 6 Months)</h4>
						<div class="chart-container">
							<canvas id="profitability-forecast-chart" height="200"></canvas>
						</div>
					</div>
				</div>
				<div class="col-md-4">
					<div class="dashboard-section">
						<h4 class="section-title">Top Risks</h4>
						<ul id="top-risks-list" class="list-group"></ul>
					</div>
				</div>
			</div>
		`);
		// Add search and status tabs above the table
		$(this.page.body).find('.dashboard-section:contains("Project Profitability Analysis")').prepend(`
			<div class="row mb-2">
				<div class="col-md-6">
					<input type="text" id="project-search" class="form-control" placeholder="Search by project or customer...">
				</div>
				<div class="col-md-6 text-end">
					<ul class="nav nav-pills justify-content-end" id="status-tabs">
						<li class="nav-item"><a class="nav-link active" data-status="All" href="#">All</a></li>
						<li class="nav-item"><a class="nav-link" data-status="Open" href="#">Open</a></li>
						<li class="nav-item"><a class="nav-link" data-status="In Progress" href="#">In Progress</a></li>
						<li class="nav-item"><a class="nav-link" data-status="Completed" href="#">Completed</a></li>
						<li class="nav-item"><a class="nav-link" data-status="At Risk" href="#">At Risk</a></li>
					</ul>
				</div>
			</div>
		`);
		// Wire up search and tabs
		this.setup_project_search_and_tabs();
	}

	setup_project_search_and_tabs() {
		// Search box
		$(document).on('input', '#project-search', () => {
			this.populate_projects_table();
		});
		// Status tabs
		$(document).on('click', '#status-tabs .nav-link', (e) => {
			e.preventDefault();
			$('#status-tabs .nav-link').removeClass('active');
			$(e.target).addClass('active');
			this.populate_projects_table();
		});
	}

	cleanup() {
		// Destroy existing charts
		this.destroy_existing_charts();
		
		// Remove loading indicator if it exists
		$('#loading-overlay').remove();
		
		// Clear dashboard container
		$(this.page.body).empty();
	}

	make_filters() {
		// Create filter area
		this.page.add_field({
			fieldname: 'company',
			label: __('Company'),
			fieldtype: 'Link',
			options: 'Company',
			default: this.filters.company,
			change: () => {
				this.filters.company = this.page.fields_dict.company.get_value();
				this.refresh_data();
			}
		});

		this.page.add_field({
			fieldname: 'from_date',
			label: __('From Date'),
			fieldtype: 'Date',
			default: this.filters.from_date,
			change: () => {
				this.filters.from_date = this.page.fields_dict.from_date.get_value();
				this.refresh_data();
			}
		});

		this.page.add_field({
			fieldname: 'to_date',
			label: __('To Date'),
			fieldtype: 'Date',
			default: this.filters.to_date,
			change: () => {
				this.filters.to_date = this.page.fields_dict.to_date.get_value();
				this.refresh_data();
			}
		});

		this.page.add_field({
			fieldname: 'project',
			label: __('Project'),
			fieldtype: 'Link',
			options: 'Project',
			change: () => {
				this.filters.project = this.page.fields_dict.project.get_value();
				this.refresh_data();
			}
		});

		// Add All Projects toggle
		this.page.add_field({
			fieldname: 'all_projects',
			label: __('All Projects'),
			fieldtype: 'Check',
			default: 0,
			change: () => {
				this.filters.all_projects = this.page.fields_dict.all_projects.get_value() ? 1 : 0;
				this.refresh_data();
			}
		});

		// Add refresh button
		this.page.add_action_item(__('Refresh'), () => {
			this.refresh_data();
		});

		// Add export button
		this.page.add_action_item(__('Export'), () => {
			this.export_data();
		});
	}

	make_dashboard() {
		// Clear existing content
		$(this.page.body).empty();

		// Create main dashboard container
		this.dashboard_container = $(`
			<div class="dashboard-container">
				<div class="row">
					<!-- Executive Summary Cards -->
					<div class="col-md-12">
						<div class="dashboard-section">
							<h4 class="section-title">Executive Summary</h4>
							<div class="row summary-cards" id="summary-cards">
								<!-- Summary cards will be populated here -->
							</div>
						</div>
					</div>
				</div>

				<div class="row mt-4">
					<!-- Profitability Trends Chart -->
					<div class="col-md-8">
						<div class="dashboard-section">
							<h4 class="section-title">Profitability Trends</h4>
							<div class="chart-container">
								<canvas id="profitability-trends-chart" height="300"></canvas>
							</div>
						</div>
					</div>

					<!-- Key Performance Indicators -->
					<div class="col-md-4">
						<div class="dashboard-section">
							<h4 class="section-title">Key Performance Indicators</h4>
							<div id="kpi-container">
								<!-- KPI cards will be populated here -->
							</div>
						</div>
					</div>
				</div>

				<div class="row mt-4">
					<!-- Cost Breakdown Charts -->
					<div class="col-md-6">
						<div class="dashboard-section">
							<h4 class="section-title">Material Cost Breakdown</h4>
							<div class="chart-container">
								<canvas id="material-breakdown-chart" height="250"></canvas>
							</div>
						</div>
					</div>

					<div class="col-md-6">
						<div class="dashboard-section">
							<h4 class="section-title">Labor Cost Breakdown</h4>
							<div class="chart-container">
								<canvas id="labor-breakdown-chart" height="250"></canvas>
							</div>
						</div>
					</div>
				</div>

				<div class="row mt-4">
					<!-- Project Profitability Table -->
					<div class="col-md-12">
						<div class="dashboard-section">
							<h4 class="section-title">Project Profitability Analysis</h4>
							<div class="table-responsive">
								<table class="table table-striped table-hover" id="projects-table">
									<thead class="table-dark">
										<tr>
											<th>Project</th>
											<th>Customer</th>
											<th>Status</th>
											<th>Progress</th>
											<th>Contract Value</th>
											<th>Revenue</th>
											<th>Costs</th>
											<th>Profit</th>
											<th>Margin %</th>
											<th>Health</th>
											<th>Actions</th>
										</tr>
									</thead>
									<tbody id="projects-table-body">
										<!-- Project data will be populated here -->
									</tbody>
								</table>
							</div>
						</div>
					</div>
				</div>
			</div>
		`).appendTo(this.page.body);

		// Add custom CSS
		this.add_dashboard_styles();
	}

	add_dashboard_styles() {
		$(`
			<style>
				.dashboard-container {
					padding: 20px;
				}

				.dashboard-section {
					background: white;
					border-radius: 8px;
					padding: 20px;
					margin-bottom: 20px;
					box-shadow: 0 2px 8px rgba(0,0,0,0.1);
				}

				.section-title {
					margin-bottom: 20px;
					color: #333;
					font-weight: 600;
					border-bottom: 2px solid #007bff;
					padding-bottom: 10px;
				}

				.summary-card {
					background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
					color: white;
					border-radius: 10px;
					padding: 20px;
					margin-bottom: 15px;
					text-align: center;
					transition: transform 0.3s ease;
				}

				.summary-card:hover {
					transform: translateY(-5px);
				}

				.summary-card.positive {
					background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
				}

				.summary-card.negative {
					background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%);
				}

				.summary-card h3 {
					font-size: 2.5rem;
					margin-bottom: 5px;
					font-weight: bold;
				}

				.summary-card p {
					margin: 0;
					font-size: 0.9rem;
					opacity: 0.9;
				}

				.kpi-item {
					padding: 15px;
					margin-bottom: 10px;
					border-left: 4px solid #007bff;
					background: #f8f9fa;
					border-radius: 5px;
				}

				.kpi-value {
					font-size: 1.5rem;
					font-weight: bold;
					color: #333;
				}

				.kpi-label {
					font-size: 0.9rem;
					color: #666;
					margin-top: 5px;
				}

				.health-indicator {
					padding: 5px 12px;
					border-radius: 15px;
					font-size: 0.8rem;
					font-weight: bold;
					text-transform: uppercase;
				}

				.health-excellent {
					background: #d4edda;
					color: #155724;
				}

				.health-good {
					background: #cce5ff;
					color: #004085;
				}

				.health-fair {
					background: #fff3cd;
					color: #856404;
				}

				.health-poor {
					background: #f8d7da;
					color: #721c24;
				}

				.progress-bar-custom {
					height: 20px;
					border-radius: 10px;
					background: #e9ecef;
					overflow: hidden;
				}

				.progress-fill {
					height: 100%;
					background: linear-gradient(45deg, #007bff, #28a745);
					transition: width 0.3s ease;
				}

				.chart-container {
					position: relative;
					height: 300px;
					margin: 20px 0;
				}

				.table th {
					font-weight: 600;
					font-size: 0.9rem;
				}

				.table td {
					vertical-align: middle;
					font-size: 0.9rem;
				}

				.btn-action {
					padding: 5px 10px;
					font-size: 0.8rem;
					border-radius: 4px;
					margin-right: 5px;
				}

				@media (max-width: 768px) {
					.dashboard-container {
						padding: 10px;
					}
					
					.summary-card h3 {
						font-size: 1.8rem;
					}
				}
			</style>
		`).appendTo('head');
	}

	refresh_data() {
		// Show loading indicator
		this.show_loading();

		// Ensure all_projects is boolean
		this.filters.all_projects = !!this.page.fields_dict.all_projects.get_value();

		// Fetch dashboard data
		frappe.call({
			method: 'vacker_automation.vacker_automation.page.project_profitability_dashboard.project_profitability_dashboard.get_dashboard_data',
			args: {
				filters: this.filters
			},
			callback: (r) => {
				try {
					if (r.message) {
						this.dashboard_data = r.message;
						this.populate_dashboard();
						this.load_forecast_and_risks();
					}
				} catch (error) {
					console.error('Error populating dashboard:', error);
					frappe.msgprint(__('Error displaying dashboard data: {0}', [error.message]));
				} finally {
					this.hide_loading();
				}
			},
			error: (error) => {
				console.error('Error fetching dashboard data:', error);
				this.hide_loading();
				frappe.msgprint(__('Error loading dashboard data'));
			}
		});
	}

	load_forecast_and_risks() {
		// Profitability Forecast
		frappe.call({
			method: 'vacker_automation.vacker_automation.page.project_profitability_dashboard.project_profitability_dashboard.get_profitability_forecast',
			args: { filters: this.filters },
			callback: (r) => {
				if (r.message && r.message.forecast) {
					this.create_forecast_chart(r.message.forecast);
				}
			}
		});
		// Top Risks
		frappe.call({
			method: 'vacker_automation.vacker_automation.page.project_profitability_dashboard.project_profitability_dashboard.get_project_risk_summary',
			args: { filters: this.filters },
			callback: (r) => {
				if (r.message && r.message.top_risks) {
					this.populate_top_risks(r.message.top_risks);
				}
			}
		});
	}

	create_forecast_chart(forecast) {
		const ctx = document.getElementById('profitability-forecast-chart').getContext('2d');
		if (this.charts.forecast) {
			this.charts.forecast.destroy();
		}
		const labels = forecast.map(f => f.period);
		const data = forecast.map(f => f.forecast_profit);
		this.charts.forecast = new Chart(ctx, {
			type: 'line',
			data: {
				labels: labels,
				datasets: [{
					label: 'Forecast Profit',
					data: data,
					borderColor: '#ff9800',
					backgroundColor: 'rgba(255, 152, 0, 0.1)',
					fill: true,
					tension: 0.4
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				scales: {
					y: {
						beginAtZero: true,
						ticks: {
							callback: function(value) {
								return frappe.format(value, {fieldtype: 'Currency'});
							}
						}
					}
				},
				plugins: {
					legend: { position: 'top' },
					tooltip: {
						callbacks: {
							label: function(context) {
								return context.dataset.label + ': ' + frappe.format(context.parsed.y, {fieldtype: 'Currency'});
							}
						}
					}
				}
			}
		});
	}

	populate_top_risks(risks) {
		const $list = $('#top-risks-list');
		$list.empty();
		if (!risks.length) {
			$list.append('<li class="list-group-item">No high-risk projects.</li>');
			return;
		}
		risks.forEach(risk => {
			$list.append(`
				<li class="list-group-item">
					<strong>${risk.project_name}</strong> (${risk.customer || '-'})<br>
					<span class="badge bg-danger me-1">Risk Score: ${risk.risk_score}</span>
					<ul class="mb-0 ps-3">
						${risk.risk_factors.map(f => `<li>${f}</li>`).join('')}
					</ul>
				</li>
			`);
		});
	}

	show_loading() {
		$('.dashboard-container').append(`
			<div id="loading-overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
				 background: rgba(255,255,255,0.8); z-index: 9999; display: flex; align-items: center; 
				 justify-content: center;">
				<div class="text-center">
					<div class="spinner-border text-primary" role="status">
						<span class="sr-only">Loading...</span>
					</div>
					<p class="mt-2">Loading dashboard data...</p>
				</div>
			</div>
		`);
	}

	hide_loading() {
		$('#loading-overlay').remove();
	}

	populate_dashboard() {
		this.populate_summary_cards();
		this.populate_charts();
		this.populate_kpi_section();
		this.populate_projects_table();
	}

	populate_summary_cards() {
		const summary = this.dashboard_data.summary;
		const cards_html = `
			<div class="col-md-2">
				<div class="summary-card">
					<h3>${this.format_currency(summary.total_contract_value)}</h3>
					<p>Total Contract Value</p>
				</div>
			</div>
			<div class="col-md-2">
				<div class="summary-card">
					<h3>${this.format_currency(summary.total_revenue)}</h3>
					<p>Revenue Recognized</p>
				</div>
			</div>
			<div class="col-md-2">
				<div class="summary-card">
					<h3>${this.format_currency(summary.total_costs)}</h3>
					<p>Total Costs</p>
				</div>
			</div>
			<div class="col-md-2">
				<div class="summary-card ${summary.gross_profit >= 0 ? 'positive' : 'negative'}">
					<h3>${this.format_currency(summary.gross_profit)}</h3>
					<p>Gross Profit</p>
				</div>
			</div>
			<div class="col-md-2">
				<div class="summary-card ${summary.profit_margin >= 0 ? 'positive' : 'negative'}">
					<h3>${summary.profit_margin.toFixed(1)}%</h3>
					<p>Profit Margin</p>
				</div>
			</div>
			<div class="col-md-2">
				<div class="summary-card">
					<h3>${summary.active_projects}</h3>
					<p>Active Projects</p>
				</div>
			</div>
		`;
		
		$('#summary-cards').html(cards_html);
	}

	populate_charts() {
		// Destroy existing charts first
		this.destroy_existing_charts();
		
		// Profitability trends chart
		this.create_profitability_trends_chart();
		
		// Cost breakdown charts
		this.create_cost_breakdown_charts();
	}

	destroy_existing_charts() {
		// Destroy existing charts to prevent canvas reuse errors
		if (this.charts.trends) {
			this.charts.trends.destroy();
			this.charts.trends = null;
		}
		if (this.charts.material) {
			this.charts.material.destroy();
			this.charts.material = null;
		}
		if (this.charts.labor) {
			this.charts.labor.destroy();
			this.charts.labor = null;
		}
		if (this.charts.forecast) {
			this.charts.forecast.destroy();
			this.charts.forecast = null;
		}
	}

	create_profitability_trends_chart() {
		try {
			const ctx = document.getElementById('profitability-trends-chart').getContext('2d');
			const trends = this.dashboard_data.trends;
			
			if (!trends || trends.length === 0) {
				return;
			}
			
			const labels = trends.map(t => t.period);
			const revenue_data = trends.map(t => t.revenue);
			const cost_data = trends.map(t => t.costs);
			const profit_data = trends.map(t => t.profit);

			this.charts.trends = new Chart(ctx, {
			type: 'line',
			data: {
				labels: labels,
				datasets: [
					{
						label: 'Revenue',
						data: revenue_data,
						borderColor: '#28a745',
						backgroundColor: 'rgba(40, 167, 69, 0.1)',
						fill: true,
						tension: 0.4
					},
					{
						label: 'Costs',
						data: cost_data,
						borderColor: '#dc3545',
						backgroundColor: 'rgba(220, 53, 69, 0.1)',
						fill: true,
						tension: 0.4
					},
					{
						label: 'Profit',
						data: profit_data,
						borderColor: '#007bff',
						backgroundColor: 'rgba(0, 123, 255, 0.1)',
						fill: true,
						tension: 0.4
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				scales: {
					y: {
						beginAtZero: true,
						ticks: {
							callback: function(value) {
								return frappe.format(value, {fieldtype: 'Currency'});
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
								return context.dataset.label + ': ' + 
									   frappe.format(context.parsed.y, {fieldtype: 'Currency'});
							}
						}
					}
				}
			}
		});
		} catch (error) {
			console.error('Error creating profitability trends chart:', error);
		}
	}

	create_cost_breakdown_charts() {
		try {
			// Material breakdown chart
			const material_ctx = document.getElementById('material-breakdown-chart').getContext('2d');
			const material_data = this.dashboard_data.cost_breakdown.material_breakdown;
		
		if (material_data && material_data.length > 0) {
			this.charts.material = new Chart(material_ctx, {
				type: 'doughnut',
				data: {
					labels: material_data.map(d => d.item_group),
					datasets: [{
						data: material_data.map(d => d.amount),
						backgroundColor: [
							'#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
							'#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
						]
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
									return context.label + ': ' + 
										   frappe.format(context.parsed, {fieldtype: 'Currency'});
								}
							}
						}
					}
				}
			});
		}

		// Labor breakdown chart
		const labor_ctx = document.getElementById('labor-breakdown-chart').getContext('2d');
		const labor_data = this.dashboard_data.cost_breakdown.labor_breakdown;
		
		if (labor_data && labor_data.length > 0) {
			this.charts.labor = new Chart(labor_ctx, {
				type: 'bar',
				data: {
					labels: labor_data.map(d => d.designation || 'Unknown'),
					datasets: [{
						label: 'Labor Cost',
						data: labor_data.map(d => d.amount),
						backgroundColor: '#36A2EB',
						borderColor: '#36A2EB',
						borderWidth: 1
					}]
				},
				options: {
					responsive: true,
					maintainAspectRatio: false,
					scales: {
						y: {
							beginAtZero: true,
							ticks: {
								callback: function(value) {
									return frappe.format(value, {fieldtype: 'Currency'});
								}
							}
						}
					},
					plugins: {
						legend: {
							display: false
						},
						tooltip: {
							callbacks: {
								label: function(context) {
									return 'Cost: ' + frappe.format(context.parsed.y, {fieldtype: 'Currency'});
								}
							}
						}
					}
				}
			});
		}
		} catch (error) {
			console.error('Error creating cost breakdown charts:', error);
		}
	}

	populate_kpi_section() {
		const metrics = this.dashboard_data.performance_metrics;
		const completion = metrics.completion_metrics;
		
		const kpi_html = `
			<div class="kpi-item">
				<div class="kpi-value">${(completion.avg_completion || 0).toFixed(1)}%</div>
				<div class="kpi-label">Average Project Completion</div>
			</div>
			<div class="kpi-item">
				<div class="kpi-value">${completion.completed_projects || 0}</div>
				<div class="kpi-label">Completed Projects</div>
			</div>
			<div class="kpi-item">
				<div class="kpi-value">${completion.active_projects || 0}</div>
				<div class="kpi-label">Active Projects</div>
			</div>
			<div class="kpi-item">
				<div class="kpi-value">${completion.overdue_projects || 0}</div>
				<div class="kpi-label">Overdue Projects</div>
			</div>
		`;
		
		$('#kpi-container').html(kpi_html);
	}

	populate_projects_table() {
		let projects = this.dashboard_data.projects;
		// Filter by search
		const search = ($('#project-search').val() || '').toLowerCase();
		if (search) {
			projects = projects.filter(p =>
				(p.project_name && p.project_name.toLowerCase().includes(search)) ||
				(p.customer && p.customer.toLowerCase().includes(search))
			);
		}
		// Filter by status tab
		const status = $('#status-tabs .nav-link.active').data('status');
		if (status && status !== 'All') {
			if (status === 'At Risk') {
				// At Risk: risk_level == 'High'
				projects = projects.filter(p => {
					const risk = p.health_indicator && p.health_indicator.status;
					return risk && risk.toLowerCase() === 'poor';
				});
			} else {
				projects = projects.filter(p => p.status === status);
			}
		}
		let table_html = '';
		
		projects.forEach(project => {
			const health = project.health_indicator;
			table_html += `
				<tr>
					<td>
						<strong>${project.project_name}</strong><br>
						<small class="text-muted">${project.name}</small>
					</td>
					<td>${project.customer || '-'}</td>
					<td>
						<span class="badge badge-${this.get_status_color(project.status)}">${project.status}</span>
					</td>
					<td>
						<div class="progress-bar-custom">
							<div class="progress-fill" style="width: ${project.percent_complete || 0}%"></div>
						</div>
						<small>${(project.percent_complete || 0).toFixed(1)}%</small>
					</td>
					<td>${this.format_currency(project.contract_value)}</td>
					<td>${this.format_currency(project.total_revenue)}</td>
					<td>${this.format_currency(project.total_costs)}</td>
					<td class="${project.gross_profit >= 0 ? 'text-success' : 'text-danger'}">
						${this.format_currency(project.gross_profit)}
					</td>
					<td class="${project.profit_margin >= 0 ? 'text-success' : 'text-danger'}">
						${(project.profit_margin || 0).toFixed(1)}%
					</td>
					<td>
						<span class="health-indicator health-${health.status.toLowerCase()}">
							${health.status}
						</span>
					</td>
					<td>
						<button class="btn btn-sm btn-primary btn-action" onclick="frappe.set_route('Form', 'Project', '${project.name}')">
							<i class="fa fa-external-link"></i> View
						</button>
						<button class="btn btn-sm btn-info btn-action" onclick="window.dashboard.view_project_details('${project.name}')">
							<i class="fa fa-chart-line"></i> Details
						</button>
					</td>
				</tr>
			`;
		});
		
		$('#projects-table-body').html(table_html);
		
		// Store reference for global access
		window.dashboard = this;
	}

	view_project_details(project_name) {
		// Create detailed project analysis modal
		const project = this.dashboard_data.projects.find(p => p.name === project_name);
		
		const dialog = new frappe.ui.Dialog({
			title: `Project Analysis - ${project.project_name}`,
			size: 'large',
			fields: [
				{
					fieldtype: 'HTML',
					fieldname: 'project_details',
					options: this.get_project_details_html(project)
				}
			]
		});
		
		dialog.show();
	}

	get_project_details_html(project) {
		return `
			<div class="project-details">
				<div class="row">
					<div class="col-md-6">
						<h5>Financial Summary</h5>
						<table class="table table-sm">
							<tr><td><strong>Contract Value:</strong></td><td>${this.format_currency(project.contract_value)}</td></tr>
							<tr><td><strong>Revenue:</strong></td><td>${this.format_currency(project.total_revenue)}</td></tr>
							<tr><td><strong>Total Costs:</strong></td><td>${this.format_currency(project.total_costs)}</td></tr>
							<tr><td><strong>Material Costs:</strong></td><td>${this.format_currency(project.material_costs)}</td></tr>
							<tr><td><strong>Labor Costs:</strong></td><td>${this.format_currency(project.labor_costs)}</td></tr>
							<tr><td><strong>Other Expenses:</strong></td><td>${this.format_currency(project.other_expenses)}</td></tr>
							<tr class="${project.gross_profit >= 0 ? 'table-success' : 'table-danger'}">
								<td><strong>Gross Profit:</strong></td><td><strong>${this.format_currency(project.gross_profit)}</strong></td>
							</tr>
						</table>
					</div>
					<div class="col-md-6">
						<h5>Project Information</h5>
						<table class="table table-sm">
							<tr><td><strong>Customer:</strong></td><td>${project.customer || '-'}</td></tr>
							<tr><td><strong>Status:</strong></td><td>${project.status}</td></tr>
							<tr><td><strong>Progress:</strong></td><td>${(project.percent_complete || 0).toFixed(1)}%</td></tr>
							<tr><td><strong>Start Date:</strong></td><td>${project.expected_start_date || '-'}</td></tr>
							<tr><td><strong>End Date:</strong></td><td>${project.expected_end_date || '-'}</td></tr>
							<tr><td><strong>Priority:</strong></td><td>${project.priority || '-'}</td></tr>
							<tr><td><strong>Health Score:</strong></td><td>${project.health_indicator.score}/100</td></tr>
						</table>
					</div>
				</div>
			</div>
		`;
	}

	format_currency(value) {
		return frappe.format(value || 0, {fieldtype: 'Currency'});
	}

	get_status_color(status) {
		const status_colors = {
			'Open': 'primary',
			'In Progress': 'info',
			'Completed': 'success',
			'Cancelled': 'danger',
			'On Hold': 'warning'
		};
		return status_colors[status] || 'secondary';
	}

	export_data() {
		// Export dashboard data to Excel
		frappe.call({
			method: 'vacker_automation.vacker_automation.page.project_profitability_dashboard.project_profitability_dashboard.export_dashboard_data',
			args: {
				filters: this.filters,
				data: this.dashboard_data
			},
			callback: (r) => {
				if (r.message) {
					window.open(r.message.file_url);
				}
			}
		});
	}
} 