// Landlord Management Dashboard JavaScript
frappe.pages['landlord-management-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Landlord Management Dashboard'),
        single_column: true
    });

    // Initialize dashboard
    init_dashboard(page);
};

function init_dashboard(page) {
    // Create dashboard layout
    const dashboard = $(`
        <div class="landlord-dashboard">
            <div class="dashboard-header">
                <h1>Landlord Management Dashboard</h1>
                <div class="dashboard-actions">
                    <button class="btn btn-primary" onclick="refreshDashboard()">
                        <i class="fa fa-refresh"></i> Refresh
                    </button>
                    <button class="btn btn-success" onclick="exportDashboard()">
                        <i class="fa fa-download"></i> Export
                    </button>
                </div>
            </div>
            
            <div class="dashboard-summary">
                <div class="summary-card" id="total-landlords">
                    <div class="card-icon">
                        <i class="fa fa-users"></i>
                    </div>
                    <div class="card-content">
                        <h3>Total Landlords</h3>
                        <div class="card-value" id="total-landlords-value">-</div>
                    </div>
                </div>
                
                <div class="summary-card" id="active-landlords">
                    <div class="card-icon">
                        <i class="fa fa-user-check"></i>
                    </div>
                    <div class="card-content">
                        <h3>Active Landlords</h3>
                        <div class="card-value" id="active-landlords-value">-</div>
                    </div>
                </div>
                
                <div class="summary-card" id="monthly-income">
                    <div class="card-icon">
                        <i class="fa fa-money"></i>
                    </div>
                    <div class="card-content">
                        <h3>Monthly Income</h3>
                        <div class="card-value" id="monthly-income-value">-</div>
                    </div>
                </div>
                
                <div class="summary-card" id="overdue-payments">
                    <div class="card-icon">
                        <i class="fa fa-exclamation-triangle"></i>
                    </div>
                    <div class="card-content">
                        <h3>Overdue Payments</h3>
                        <div class="card-value" id="overdue-payments-value">-</div>
                    </div>
                </div>
            </div>
            
            <div class="dashboard-charts">
                <div class="chart-container">
                    <h3>Revenue by Landlord Type</h3>
                    <div id="revenue-by-type-chart"></div>
                </div>
                
                <div class="chart-container">
                    <h3>Revenue by Media Type</h3>
                    <div id="revenue-by-media-chart"></div>
                </div>
                
                <div class="chart-container">
                    <h3>Property Status Distribution</h3>
                    <div id="property-status-chart"></div>
                </div>
            </div>
            
            <div class="dashboard-details">
                <div class="detail-section">
                    <h3>Upcoming Payments</h3>
                    <div id="upcoming-payments-list"></div>
                </div>
                
                <div class="detail-section">
                    <h3>Contracts Expiring Soon</h3>
                    <div id="contract-expiries-list"></div>
                </div>
                
                <div class="detail-section">
                    <h3>Top Landlords by Revenue</h3>
                    <div id="top-landlords-list"></div>
                </div>
            </div>
        </div>
    `);

    page.main.append(dashboard);
    
    // Load dashboard data
    loadDashboardData();
    
    // Set up auto-refresh
    setInterval(loadDashboardData, 300000); // Refresh every 5 minutes
}

function loadDashboardData() {
    frappe.call({
        method: 'vacker_automation.vacker_automation.page.landlord_management_dashboard.landlord_management_dashboard.get_dashboard_stats',
        callback: function(r) {
            console.log('Dashboard data received:', r);
            if (r.message) {
                updateDashboard(r.message);
            } else {
                console.error('No dashboard data received');
                showError('Failed to load dashboard data');
            }
        },
        error: function(err) {
            console.error('Error loading dashboard data:', err);
            showError('Error loading dashboard data: ' + err.message);
        }
    });
}

function updateDashboard(data) {
    console.log('Updating dashboard with data:', data);
    
    // Update summary cards
    if (data.summary) {
        updateSummaryCards(data.summary);
    } else {
        console.warn('No summary data available');
    }
    
    // Update charts
    if (data.charts) {
        updateCharts(data.charts);
    } else {
        console.warn('No chart data available');
    }
    
    // Update detail sections
    updateDetailSections(data);
}

function updateSummaryCards(summary) {
    console.log('Updating summary cards with:', summary);
    
    $('#total-landlords-value').text(summary.total_landlords || 0);
    $('#active-landlords-value').text(summary.active_landlords || 0);
    $('#monthly-income-value').text(formatCurrency(summary.monthly_income || 0));
    $('#overdue-payments-value').text(summary.overdue_payments || 0);
}

function formatCurrency(amount) {
    if (amount === null || amount === undefined || isNaN(amount)) return '0.00';
    return parseFloat(amount).toFixed(2);
}

function updateCharts(charts) {
    console.log('Updating charts with:', charts);
    
    // Revenue by landlord type chart
    if (charts.revenue_by_type && charts.revenue_by_type.length > 0) {
        const chartData = charts.revenue_by_type.map(item => ({
            name: item.landlord_type || 'Unknown',
            value: parseFloat(item.annual_revenue || 0)
        }));
        
        renderPieChart('#revenue-by-type-chart', chartData, 'Revenue by Landlord Type');
    } else {
        console.warn('No revenue by type data available');
        $('#revenue-by-type-chart').html('<div class="no-data">No revenue data available</div>');
    }
    
    // Revenue by media type chart
    if (charts.revenue_by_media && charts.revenue_by_media.length > 0) {
        const chartData = charts.revenue_by_media.map(item => ({
            name: item.media_type || 'Unknown',
            value: parseFloat(item.annual_revenue || 0)
        }));
        
        renderPieChart('#revenue-by-media-chart', chartData, 'Revenue by Media Type');
    } else {
        console.warn('No revenue by media data available');
        $('#revenue-by-media-chart').html('<div class="no-data">No revenue data available</div>');
    }
    
    // Property status chart
    if (charts.property_status && charts.property_status.length > 0) {
        const chartData = charts.property_status.map(item => ({
            name: item.property_status || 'Unknown',
            value: parseInt(item.count || 0)
        }));
        
        renderPieChart('#property-status-chart', chartData, 'Property Status Distribution');
    } else {
        console.warn('No property status data available');
        $('#property-status-chart').html('<div class="no-data">No property data available</div>');
    }
}

function renderPieChart(container, data, title) {
    const chartContainer = $(container);
    chartContainer.empty();
    
    if (data.length === 0) {
        chartContainer.html('<div class="no-data">No data available</div>');
        return;
    }
    
    // Simple pie chart using HTML/CSS
    const total = data.reduce((sum, item) => sum + item.value, 0);
    let currentAngle = 0;
    
    const chart = $('<div class="pie-chart"></div>');
    
    data.forEach((item, index) => {
        const percentage = total > 0 ? (item.value / total) * 100 : 0;
        const angle = (percentage / 100) * 360;
        
        const slice = $(`
            <div class="pie-slice" style="
                transform: rotate(${currentAngle}deg);
                background: ${getChartColor(index)};
                clip-path: polygon(50% 50%, 50% 0%, ${50 + 50 * Math.cos(angle * Math.PI / 180)}% ${50 - 50 * Math.sin(angle * Math.PI / 180)}%);
            "></div>
        `);
        
        chart.append(slice);
        currentAngle += angle;
    });
    
    chartContainer.append(chart);
    
    // Add legend
    const legend = $('<div class="chart-legend"></div>');
    data.forEach((item, index) => {
        const legendItem = $(`
            <div class="legend-item">
                <span class="legend-color" style="background: ${getChartColor(index)}"></span>
                <span class="legend-label">${item.name}</span>
                <span class="legend-value">${formatCurrency(item.value)}</span>
            </div>
        `);
        legend.append(legendItem);
    });
    
    chartContainer.append(legend);
}

function getChartColor(index) {
    const colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
    ];
    return colors[index % colors.length];
}

function updateDetailSections(data) {
    // Update upcoming payments
    updateUpcomingPayments(data.upcoming_payments);
    
    // Update contract expiries
    updateContractExpiries(data.contract_expiries);
    
    // Update top landlords
    updateTopLandlords(data.top_landlords);
}

function updateUpcomingPayments(payments) {
    const container = $('#upcoming-payments-list');
    container.empty();
    
    if (!payments || payments.length === 0) {
        container.html('<div class="no-data">No upcoming payments</div>');
        return;
    }
    
    const table = $('<table class="table table-striped"></table>');
    table.append(`
        <thead>
            <tr>
                <th>Landlord</th>
                <th>Property</th>
                <th>Amount</th>
                <th>Due Date</th>
            </tr>
        </thead>
    `);
    
    const tbody = $('<tbody></tbody>');
    payments.forEach(payment => {
        const row = $(`
            <tr>
                <td>${payment.full_legal_name || payment.landlord}</td>
                <td>${payment.property}</td>
                <td>${formatCurrency(payment.amount)}</td>
                <td>${frappe.format(payment.due_date, {fieldtype: 'Date'})}</td>
            </tr>
        `);
        tbody.append(row);
    });
    
    table.append(tbody);
    container.append(table);
}

function updateContractExpiries(contracts) {
    const container = $('#contract-expiries-list');
    container.empty();
    
    if (!contracts || contracts.length === 0) {
        container.html('<div class="no-data">No contracts expiring soon</div>');
        return;
    }
    
    const table = $('<table class="table table-striped"></table>');
    table.append(`
        <thead>
            <tr>
                <th>Landlord</th>
                <th>Property</th>
                <th>End Date</th>
                <th>Rental Amount</th>
            </tr>
        </thead>
    `);
    
    const tbody = $('<tbody></tbody>');
    contracts.forEach(contract => {
        const row = $(`
            <tr>
                <td>${contract.full_legal_name}</td>
                <td>${contract.property}</td>
                <td>${frappe.format(contract.contract_end_date, {fieldtype: 'Date'})}</td>
                <td>${formatCurrency(contract.rental_amount)}</td>
            </tr>
        `);
        tbody.append(row);
    });
    
    table.append(tbody);
    container.append(table);
}

function updateTopLandlords(landlords) {
    const container = $('#top-landlords-list');
    container.empty();
    
    if (!landlords || landlords.length === 0) {
        container.html('<div class="no-data">No landlord data available</div>');
        return;
    }
    
    const table = $('<table class="table table-striped"></table>');
    table.append(`
        <thead>
            <tr>
                <th>Landlord</th>
                <th>Property</th>
                <th>Annual Revenue</th>
                <th>Payment Frequency</th>
            </tr>
        </thead>
    `);
    
    const tbody = $('<tbody></tbody>');
    landlords.forEach(landlord => {
        const row = $(`
            <tr>
                <td>${landlord.full_legal_name}</td>
                <td>${landlord.property}</td>
                <td>${formatCurrency(landlord.annual_revenue)}</td>
                <td>${landlord.payment_frequency}</td>
            </tr>
        `);
        tbody.append(row);
    });
    
    table.append(tbody);
    container.append(table);
}

function refreshDashboard() {
    loadDashboardData();
    frappe.show_alert('Dashboard refreshed successfully', 3);
}

function exportDashboard() {
    frappe.call({
        method: 'vacker_automation.vacker_automation.page.landlord_management_dashboard.landlord_management_dashboard.get_dashboard_stats',
        callback: function(r) {
            if (r.message) {
                // Create CSV export
                const csv = convertToCSV(r.message);
                downloadCSV(csv, 'landlord-dashboard-export.csv');
            }
        }
    });
}

function convertToCSV(data) {
    // Implementation for CSV conversion
    // This is a simplified version - you might want to use a proper CSV library
    let csv = 'Landlord Management Dashboard Export\n\n';
    
    // Summary data
    csv += 'Summary Statistics\n';
    csv += 'Total Landlords,' + data.summary.total_landlords + '\n';
    csv += 'Active Landlords,' + data.summary.active_landlords + '\n';
    csv += 'Monthly Income,' + data.summary.monthly_income + '\n';
    csv += 'Overdue Payments,' + data.summary.overdue_payments + '\n\n';
    
    return csv;
}

function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

function showError(message) {
    // Show error message on dashboard
    const errorDiv = $('<div class="alert alert-danger">' + message + '</div>');
    $('.landlord-dashboard').prepend(errorDiv);
    
    // Remove error after 5 seconds
    setTimeout(() => {
        errorDiv.fadeOut();
    }, 5000);
} 