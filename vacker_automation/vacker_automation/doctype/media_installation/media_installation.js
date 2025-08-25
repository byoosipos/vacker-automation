// Copyright (c) 2025, Vacker and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Media Installation", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Media Installation', {
    refresh: function(frm) {
        // Add custom buttons
        frm.add_custom_button(__('Generate Customer Invoicing Schedules'), function() {
            generate_customer_invoicing_schedules(frm);
        });
        
        frm.add_custom_button(__('View Customer Invoicing Schedules'), function() {
            view_customer_invoicing_schedules(frm);
        }, __('Actions'));
        
        frm.add_custom_button(__('View Property Rental History'), function() {
            view_property_rental_history(frm);
        }, __('Actions'));
        
        frm.add_custom_button(__('View Sales Invoices'), function() {
            view_sales_invoices(frm);
        }, __('Actions'));
        
        frm.add_custom_button(__('Schedule Maintenance'), function() {
            schedule_maintenance(frm);
        }, __('Actions'));
        
        // Add buttons for project and customer management
        if (frm.doc.project) {
            frm.add_custom_button(__('View Project'), function() {
                frappe.set_route('Form', 'Project', frm.doc.project);
            }, __('Project'));
        }
        
        if (frm.doc.customer) {
            frm.add_custom_button(__('View Customer'), function() {
                frappe.set_route('Form', 'Customer', frm.doc.customer);
            }, __('Customer'));
        }
        
        if (frm.doc.landlord) {
            frm.add_custom_button(__('View Landlord'), function() {
                frappe.set_route('Form', 'Landlord', frm.doc.landlord);
            }, __('Landlord'));
        }
        
        if (frm.doc.property) {
            frm.add_custom_button(__('View Property'), function() {
                frappe.set_route('Form', 'Property', frm.doc.property);
            }, __('Property'));
        }
        
        // Update customer invoicing schedules info
        update_customer_invoicing_schedules_info(frm);
    },
    
    project: function(frm) {
        // Auto-fetch project name when project is selected
        if (frm.doc.project) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Project',
                    name: frm.doc.project
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('project_name', r.message.project_name);
                    }
                }
            });
        } else {
            frm.set_value('project_name', '');
        }
    },
    
    customer: function(frm) {
        // Auto-fetch customer name when customer is selected
        if (frm.doc.customer) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Customer',
                    name: frm.doc.customer
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('customer_name', r.message.customer_name);
                    }
                }
            });
        } else {
            frm.set_value('customer_name', '');
        }
    },
    
    rental_start_date: function(frm) {
        validate_rental_dates(frm);
    },
    
    rental_end_date: function(frm) {
        validate_rental_dates(frm);
    },
    
    rental_amount: function(frm) {
        calculate_total_revenue(frm);
    },
    
    rental_frequency: function(frm) {
        calculate_total_revenue(frm);
    }
});

function generate_customer_invoicing_schedules(frm) {
    if (!frm.doc.customer || !frm.doc.rental_start_date || !frm.doc.rental_end_date || !frm.doc.rental_amount) {
        frappe.msgprint({
            title: __('Missing Information'),
            message: __('Please fill in customer, rental dates, and rental amount before generating invoicing schedules.'),
            indicator: 'red'
        });
        return;
    }
    
    frappe.call({
        method: 'vacker_automation.vacker_automation.doctype.media_installation.media_installation.generate_customer_invoicing_schedule',
        args: {
            media_installation: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                frappe.msgprint({
                    title: __('Success'),
                    message: __('Customer invoicing schedules generated successfully.'),
                    indicator: 'green'
                });
                frm.refresh();
            }
        }
    });
}

function view_customer_invoicing_schedules(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Customer Invoicing Schedule',
            filters: {
                'media_installation': frm.doc.name
            },
            fields: ['name', 'customer', 'due_date', 'amount', 'status', 'sales_invoice']
        },
        callback: function(r) {
            if (r.message) {
                show_customer_invoicing_schedules(r.message, frm);
            }
        }
    });
}

function show_customer_invoicing_schedules(schedules, frm) {
    let content = `
        <div class="customer-invoicing-schedules">
            <h4>Customer Invoicing Schedules for Installation: ${frm.doc.installation_id}</h4>
            <p><strong>Note:</strong> Sales invoices are automatically created 1 month before the due date (advance invoicing).</p>
            <table class="table table-bordered">
                <tr>
                    <td><strong>Total Schedules:</strong></td>
                    <td>${schedules.length}</td>
                </tr>
                <tr>
                    <td><strong>Pending Schedules:</strong></td>
                    <td>${schedules.filter(s => s.status === 'Pending').length}</td>
                </tr>
                <tr>
                    <td><strong>Invoice Created:</strong></td>
                    <td>${schedules.filter(s => s.status === 'Invoice Created').length}</td>
                </tr>
                <tr>
                    <td><strong>Paid Schedules:</strong></td>
                    <td>${schedules.filter(s => s.status === 'Paid').length}</td>
                </tr>
                <tr>
                    <td><strong>Overdue Schedules:</strong></td>
                    <td>${schedules.filter(s => s.status === 'Overdue').length}</td>
                </tr>
            </table>
        </div>
    `;
    
    if (schedules.length > 0) {
        content += `
            <h5>Recent Customer Invoicing Schedules</h5>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Schedule</th>
                        <th>Customer</th>
                        <th>Due Date</th>
                        <th>Amount</th>
                        <th>Status</th>
                        <th>Sales Invoice</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        schedules.slice(0, 10).forEach(schedule => {
            let invoiceLink = schedule.sales_invoice ? 
                `<a href="/app/sales-invoice/${schedule.sales_invoice}" target="_blank">${schedule.sales_invoice}</a>` : 
                '-';
            
            content += `
                <tr>
                    <td><a href="/app/customer-invoicing-schedule/${schedule.name}" target="_blank">${schedule.name}</a></td>
                    <td>${schedule.customer || '-'}</td>
                    <td>${frappe.format(schedule.due_date, {fieldtype: 'Date'})}</td>
                    <td>${frappe.format(schedule.amount, {fieldtype: 'Currency'})}</td>
                    <td><span class="label label-${get_schedule_status_color(schedule.status)}">${schedule.status}</span></td>
                    <td>${invoiceLink}</td>
                </tr>
            `;
        });
        
        content += `
                </tbody>
            </table>
        `;
    }
    
    let d = new frappe.ui.Dialog({
        title: __('Customer Invoicing Schedules'),
        size: 'large',
        fields: [{
            fieldtype: 'HTML',
            options: content
        }]
    });
    
    d.show();
}

function view_property_rental_history(frm) {
    frappe.call({
        method: 'vacker_automation.vacker_automation.doctype.media_installation.media_installation.get_property_rental_history',
        args: {
            media_installation: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                show_property_rental_history(r.message, frm);
            }
        }
    });
}

function show_property_rental_history(history, frm) {
    let content = `
        <div class="property-rental-history">
            <h4>Property Rental History: ${frm.doc.property}</h4>
            <table class="table table-bordered">
                <tr>
                    <td><strong>Total Rentals:</strong></td>
                    <td>${history.total_rentals}</td>
                </tr>
                <tr>
                    <td><strong>Property:</strong></td>
                    <td>${history.property}</td>
                </tr>
            </table>
        </div>
    `;
    
    if (history.rental_history && history.rental_history.length > 0) {
        content += `
            <h5>Rental History</h5>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Installation</th>
                        <th>Customer</th>
                        <th>Rental Period</th>
                        <th>Amount</th>
                        <th>Frequency</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        history.rental_history.forEach(rental => {
            content += `
                <tr>
                    <td><a href="/app/media-installation/${rental.installation}" target="_blank">${rental.installation}</a></td>
                    <td>${rental.customer_name || rental.customer}</td>
                    <td>${frappe.format(rental.rental_start_date, {fieldtype: 'Date'})} to ${frappe.format(rental.rental_end_date, {fieldtype: 'Date'})}</td>
                    <td>${frappe.format(rental.rental_amount, {fieldtype: 'Currency'})}</td>
                    <td>${rental.rental_frequency}</td>
                    <td><span class="label label-${get_rental_status_color(rental.rental_status)}">${rental.rental_status}</span></td>
                </tr>
            `;
        });
        
        content += `
                </tbody>
            </table>
        `;
    }
    
    let d = new frappe.ui.Dialog({
        title: __('Property Rental History'),
        size: 'large',
        fields: [{
            fieldtype: 'HTML',
            options: content
        }]
    });
    
    d.show();
}

function view_sales_invoices(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Sales Invoice',
            filters: {
                'media_installation': frm.doc.name
            },
            fields: ['name', 'posting_date', 'due_date', 'grand_total', 'status']
        },
        callback: function(r) {
            if (r.message) {
                show_sales_invoices(r.message, frm);
            }
        }
    });
}

function show_sales_invoices(invoices, frm) {
    let content = `
        <div class="sales-invoices">
            <h4>Sales Invoices for Installation: ${frm.doc.installation_id}</h4>
            <table class="table table-bordered">
                <tr>
                    <td><strong>Total Invoices:</strong></td>
                    <td>${invoices.length}</td>
                </tr>
                <tr>
                    <td><strong>Draft Invoices:</strong></td>
                    <td>${invoices.filter(i => i.status === 'Draft').length}</td>
                </tr>
                <tr>
                    <td><strong>Submitted Invoices:</strong></td>
                    <td>${invoices.filter(i => i.status === 'Submitted').length}</td>
                </tr>
                <tr>
                    <td><strong>Paid Invoices:</strong></td>
                    <td>${invoices.filter(i => i.status === 'Paid').length}</td>
                </tr>
                <tr>
                    <td><strong>Total Amount:</strong></td>
                    <td>${frappe.format(invoices.reduce((sum, inv) => sum + (inv.grand_total || 0), 0), {fieldtype: 'Currency'})}</td>
                </tr>
            </table>
        </div>
    `;
    
    if (invoices.length > 0) {
        content += `
            <h5>Recent Sales Invoices</h5>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Invoice</th>
                        <th>Posting Date</th>
                        <th>Due Date</th>
                        <th>Amount</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        invoices.slice(0, 10).forEach(invoice => {
            content += `
                <tr>
                    <td><a href="/app/sales-invoice/${invoice.name}" target="_blank">${invoice.name}</a></td>
                    <td>${frappe.format(invoice.posting_date, {fieldtype: 'Date'})}</td>
                    <td>${frappe.format(invoice.due_date, {fieldtype: 'Date'})}</td>
                    <td>${frappe.format(invoice.grand_total, {fieldtype: 'Currency'})}</td>
                    <td><span class="label label-${get_invoice_status_color(invoice.status)}">${invoice.status}</span></td>
                </tr>
            `;
        });
        
        content += `
                </tbody>
            </table>
        `;
    }
    
    let d = new frappe.ui.Dialog({
        title: __('Sales Invoices'),
        size: 'large',
        fields: [{
            fieldtype: 'HTML',
            options: content
        }]
    });
    
    d.show();
}

function schedule_maintenance(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Schedule Maintenance'),
        fields: [
            {
                fieldtype: 'Date',
                fieldname: 'maintenance_date',
                label: __('Maintenance Date'),
                reqd: 1
            },
            {
                fieldtype: 'Select',
                fieldname: 'maintenance_type',
                label: __('Maintenance Type'),
                options: 'Routine\nEmergency\nRepair\nUpgrade',
                default: 'Routine'
            }
        ],
        primary_action_label: __('Schedule'),
        primary_action: function(values) {
            frappe.call({
                method: 'vacker_automation.vacker_automation.doctype.media_installation.media_installation.schedule_maintenance',
                args: {
                    media_installation: frm.doc.name,
                    maintenance_date: values.maintenance_date,
                    maintenance_type: values.maintenance_type
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('Success'),
                            message: __('Maintenance scheduled successfully.'),
                            indicator: 'green'
                        });
                        d.hide();
                    }
                }
            });
        }
    });
    d.show();
}

function validate_rental_dates(frm) {
    if (frm.doc.rental_start_date && frm.doc.rental_end_date) {
        let start_date = new Date(frm.doc.rental_start_date);
        let end_date = new Date(frm.doc.rental_end_date);
        
        if (end_date <= start_date) {
            frappe.msgprint({
                title: __('Invalid Dates'),
                message: __('Rental end date must be after start date.'),
                indicator: 'red'
            });
        }
    }
}

function calculate_total_revenue(frm) {
    if (frm.doc.rental_start_date && frm.doc.rental_end_date && frm.doc.rental_amount && frm.doc.rental_frequency) {
        let start_date = new Date(frm.doc.rental_start_date);
        let end_date = new Date(frm.doc.rental_end_date);
        let months = (end_date.getFullYear() - start_date.getFullYear()) * 12 + (end_date.getMonth() - start_date.getMonth());
        
        let total_revenue = 0;
        if (frm.doc.rental_frequency === 'Monthly') {
            total_revenue = frm.doc.rental_amount * Math.max(1, months);
        } else if (frm.doc.rental_frequency === 'Quarterly') {
            total_revenue = frm.doc.rental_amount * Math.max(1, Math.floor(months / 3));
        } else if (frm.doc.rental_frequency === 'Annually') {
            total_revenue = frm.doc.rental_amount * Math.max(1, Math.floor(months / 12));
        } else { // One-time
            total_revenue = frm.doc.rental_amount;
        }
        
        // You can display this in a custom field or show it in a message
        frappe.show_alert(`Estimated total revenue: ${frappe.format(total_revenue, {fieldtype: 'Currency'})}`, 'blue');
    }
}

function get_schedule_status_color(status) {
    switch(status) {
        case 'Pending': return 'default';
        case 'Invoice Created': return 'info';
        case 'Paid': return 'success';
        case 'Overdue': return 'danger';
        default: return 'default';
    }
}

function get_rental_status_color(status) {
    switch(status) {
        case 'Active': return 'success';
        case 'Completed': return 'info';
        case 'Terminated': return 'danger';
        case 'Suspended': return 'warning';
        default: return 'default';
    }
}

function get_invoice_status_color(status) {
    switch(status) {
        case 'Draft': return 'default';
        case 'Submitted': return 'warning';
        case 'Paid': return 'success';
        default: return 'default';
    }
}

function update_customer_invoicing_schedules_info(frm) {
    if (!frm.doc.name) return; // Document not saved yet
    
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Customer Invoicing Schedule',
            filters: {
                'media_installation': frm.doc.name
            },
            fields: ['name', 'due_date', 'amount', 'status', 'sales_invoice', 'payment_date'],
            order_by: 'due_date'
        },
        callback: function(r) {
            if (r.message) {
                let html_content = '';
                
                if (r.message.length === 0) {
                    html_content = `
                        <div class="alert alert-info">
                            <strong>No Customer Invoicing Schedules Found</strong><br>
                            Customer invoicing schedules will be automatically generated when the installation is completed.
                        </div>
                    `;
                } else {
                    html_content = `
                        <div class="customer-invoicing-schedules">
                            <h5>Customer Invoicing Schedules (${r.message.length} total)</h5>
                            <div class="table-responsive">
                                <table class="table table-bordered table-striped">
                                    <thead>
                                        <tr>
                                            <th>Schedule</th>
                                            <th>Due Date</th>
                                            <th>Amount</th>
                                            <th>Status</th>
                                            <th>Sales Invoice</th>
                                            <th>Payment Date</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                    `;
                    
                    r.message.forEach(schedule => {
                        const status_color = get_schedule_status_color(schedule.status);
                        const invoice_link = schedule.sales_invoice ? 
                            `<a href="/app/sales-invoice/${schedule.sales_invoice}" target="_blank">${schedule.sales_invoice}</a>` : 
                            '-';
                        const payment_date = schedule.payment_date || '-';
                        
                        html_content += `
                            <tr>
                                <td><a href="/app/customer-invoicing-schedule/${schedule.name}" target="_blank">${schedule.name}</a></td>
                                <td>${frappe.format(schedule.due_date, {fieldtype: 'Date'})}</td>
                                <td>${frappe.format(schedule.amount, {fieldtype: 'Currency'})}</td>
                                <td><span class="label label-${status_color}">${schedule.status}</span></td>
                                <td>${invoice_link}</td>
                                <td>${payment_date}</td>
                            </tr>
                        `;
                    });
                    
                    html_content += `
                                    </tbody>
                                </table>
                            </div>
                            <div class="mt-3">
                                <small class="text-muted">
                                    <strong>Note:</strong> Sales invoices are automatically created 1 month before the due date (advance invoicing).
                                </small>
                            </div>
                        </div>
                    `;
                }
                
                // Update the HTML field
                if (frm.get_field('customer_invoicing_schedules_info')) {
                    frm.set_value('customer_invoicing_schedules_info', html_content);
                }
            }
        }
    });
}
