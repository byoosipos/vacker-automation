/**
 * Chart Utilities Module for Comprehensive Executive Dashboard
 * Centralized Chart.js utilities and common chart configurations
 * @class ChartUtils
 */
class ChartUtils {
    constructor() {
        this.charts = new Map();
        this.defaultColors = [
            '#3b82f6', // Blue
            '#10b981', // Green
            '#f59e0b', // Yellow
            '#ef4444', // Red
            '#8b5cf6', // Purple
            '#06b6d4', // Cyan
            '#84cc16', // Lime
            '#f97316', // Orange
            '#ec4899', // Pink
            '#6b7280'  // Gray
        ];
    }

    /**
     * Initialize Chart.js with global defaults
     */
    init() {
        if (typeof Chart !== 'undefined') {
            Chart.defaults.font.family = "'Inter', 'Segoe UI', 'Roboto', sans-serif";
            Chart.defaults.font.size = 12;
            Chart.defaults.color = '#374151';
            Chart.defaults.borderColor = '#e5e7eb';
            Chart.defaults.backgroundColor = 'rgba(59, 130, 246, 0.1)';
            
            // Set responsive defaults
            Chart.defaults.responsive = true;
            Chart.defaults.maintainAspectRatio = false;
        }
    }

    /**
     * Create a line chart
     */
    createLineChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const defaultOptions = {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: this.processDatasets(data.datasets || [], 'line')
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#374151',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(156, 163, 175, 0.2)'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                ...options
            }
        };

        const chart = new Chart(canvas, defaultOptions);
        this.charts.set(canvasId, chart);
        return chart;
    }

    /**
     * Create a bar chart
     */
    createBarChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const defaultOptions = {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: this.processDatasets(data.datasets || [], 'bar')
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(156, 163, 175, 0.2)'
                        }
                    }
                },
                ...options
            }
        };

        const chart = new Chart(canvas, defaultOptions);
        this.charts.set(canvasId, chart);
        return chart;
    }

    /**
     * Create a doughnut chart
     */
    createDoughnutChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const defaultOptions = {
            type: 'doughnut',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.values || [],
                    backgroundColor: data.colors || this.getColors(data.values?.length || 5),
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff'
                    }
                },
                cutout: '60%',
                ...options
            }
        };

        const chart = new Chart(canvas, defaultOptions);
        this.charts.set(canvasId, chart);
        return chart;
    }

    /**
     * Create a pie chart
     */
    createPieChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const defaultOptions = {
            type: 'pie',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.values || [],
                    backgroundColor: data.colors || this.getColors(data.values?.length || 5),
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff'
                    }
                },
                ...options
            }
        };

        const chart = new Chart(canvas, defaultOptions);
        this.charts.set(canvasId, chart);
        return chart;
    }

    /**
     * Create an area chart
     */
    createAreaChart(canvasId, data, options = {}) {
        const areaData = {
            ...data,
            datasets: (data.datasets || []).map(dataset => ({
                ...dataset,
                fill: true,
                backgroundColor: dataset.backgroundColor || this.addAlpha(dataset.borderColor || this.defaultColors[0], 0.2),
                tension: 0.4
            }))
        };

        return this.createLineChart(canvasId, areaData, options);
    }

    /**
     * Create a multi-axis chart
     */
    createMultiAxisChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const defaultOptions = {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: this.processDatasets(data.datasets || [], 'line')
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
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: {
                            color: 'rgba(156, 163, 175, 0.2)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false,
                        }
                    }
                },
                ...options
            }
        };

        const chart = new Chart(canvas, defaultOptions);
        this.charts.set(canvasId, chart);
        return chart;
    }

    /**
     * Process datasets with default styling
     */
    processDatasets(datasets, chartType) {
        return datasets.map((dataset, index) => {
            const color = dataset.borderColor || dataset.backgroundColor || this.defaultColors[index % this.defaultColors.length];
            
            const processedDataset = {
                ...dataset,
                borderColor: color,
                pointBackgroundColor: color,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: chartType === 'line' ? 4 : 0,
                pointHoverRadius: chartType === 'line' ? 6 : 0
            };

            // Set background color based on chart type
            if (chartType === 'line') {
                processedDataset.backgroundColor = dataset.fill ? this.addAlpha(color, 0.1) : 'transparent';
            } else if (chartType === 'bar') {
                processedDataset.backgroundColor = this.addAlpha(color, 0.8);
                processedDataset.borderRadius = 4;
                processedDataset.borderSkipped = false;
            }

            return processedDataset;
        });
    }

    /**
     * Get color palette
     */
    getColors(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(this.defaultColors[i % this.defaultColors.length]);
        }
        return colors;
    }

    /**
     * Add alpha transparency to a color
     */
    addAlpha(color, alpha) {
        if (color.startsWith('#')) {
            const hex = color.slice(1);
            const r = parseInt(hex.substr(0, 2), 16);
            const g = parseInt(hex.substr(2, 2), 16);
            const b = parseInt(hex.substr(4, 2), 16);
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        }
        return color;
    }

    /**
     * Format currency for chart labels
     */
    formatCurrency(value, options = {}) {
        const { 
            currency = 'USD', 
            minimumFractionDigits = 0, 
            maximumFractionDigits = 0,
            compact = false 
        } = options;

        if (compact && Math.abs(value) >= 1000) {
            if (Math.abs(value) >= 1000000) {
                return '$' + (value / 1000000).toFixed(1) + 'M';
            } else {
                return '$' + (value / 1000).toFixed(0) + 'K';
            }
        }

        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency,
            minimumFractionDigits,
            maximumFractionDigits
        }).format(value);
    }

    /**
     * Format percentage for chart labels
     */
    formatPercentage(value, decimals = 1) {
        return `${value.toFixed(decimals)}%`;
    }

    /**
     * Format number with K/M suffix
     */
    formatNumber(value) {
        if (Math.abs(value) >= 1000000) {
            return (value / 1000000).toFixed(1) + 'M';
        } else if (Math.abs(value) >= 1000) {
            return (value / 1000).toFixed(0) + 'K';
        }
        return value.toString();
    }

    /**
     * Update chart data
     */
    updateChart(canvasId, newData) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }

    /**
     * Destroy a specific chart
     */
    destroyChart(canvasId) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.destroy();
            this.charts.delete(canvasId);
        }
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        this.charts.forEach((chart, canvasId) => {
            chart.destroy();
        });
        this.charts.clear();
    }

    /**
     * Resize all charts
     */
    resizeAllCharts() {
        this.charts.forEach(chart => {
            chart.resize();
        });
    }

    /**
     * Get chart by canvas ID
     */
    getChart(canvasId) {
        return this.charts.get(canvasId);
    }

    /**
     * Common chart options for financial data
     */
    getFinancialChartOptions() {
        return {
            scales: {
                y: {
                    ticks: {
                        callback: (value) => this.formatCurrency(value, { compact: true })
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            return `${context.dataset.label}: ${this.formatCurrency(context.parsed.y)}`;
                        }
                    }
                }
            }
        };
    }

    /**
     * Common chart options for percentage data
     */
    getPercentageChartOptions() {
        return {
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    ticks: {
                        callback: (value) => this.formatPercentage(value)
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            return `${context.dataset.label}: ${this.formatPercentage(context.parsed.y)}`;
                        }
                    }
                }
            }
        };
    }

    /**
     * Create a metric card with chart
     */
    createMetricCard(container, metric) {
        const { title, value, change, chartData, chartType = 'line' } = metric;
        
        const cardHtml = `
            <div class="metric-card-with-chart">
                <div class="metric-header">
                    <h4>${title}</h4>
                </div>
                <div class="metric-value">${value}</div>
                <div class="metric-change ${change >= 0 ? 'positive' : 'negative'}">
                    <i class="fa fa-${change >= 0 ? 'arrow-up' : 'arrow-down'}"></i>
                    ${Math.abs(change)}%
                </div>
                <div class="metric-chart">
                    <canvas id="${metric.id}-chart" width="200" height="100"></canvas>
                </div>
            </div>
        `;

        container.append(cardHtml);

        // Create mini chart
        if (chartData) {
            setTimeout(() => {
                this.createMiniChart(`${metric.id}-chart`, chartData, chartType);
            }, 100);
        }
    }

    /**
     * Create a mini chart for metric cards
     */
    createMiniChart(canvasId, data, type = 'line') {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            scales: {
                x: { display: false },
                y: { display: false }
            },
            elements: {
                point: { radius: 0 }
            }
        };

        let chartConfig;
        if (type === 'line') {
            chartConfig = {
                type: 'line',
                data: {
                    labels: data.labels || [],
                    datasets: [{
                        data: data.values || [],
                        borderColor: data.color || this.defaultColors[0],
                        backgroundColor: this.addAlpha(data.color || this.defaultColors[0], 0.1),
                        fill: true,
                        tension: 0.4,
                        borderWidth: 2
                    }]
                },
                options: chartOptions
            };
        } else if (type === 'bar') {
            chartConfig = {
                type: 'bar',
                data: {
                    labels: data.labels || [],
                    datasets: [{
                        data: data.values || [],
                        backgroundColor: this.addAlpha(data.color || this.defaultColors[0], 0.8),
                        borderColor: data.color || this.defaultColors[0],
                        borderWidth: 1
                    }]
                },
                options: chartOptions
            };
        }

        if (chartConfig) {
            const chart = new Chart(canvas, chartConfig);
            this.charts.set(canvasId, chart);
            return chart;
        }

        return null;
    }
}

// Export the utility
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartUtils;
} else {
    window.ChartUtils = ChartUtils;
}
