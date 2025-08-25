// Enhanced Landlord DocType Client Script with better error handling and modularization
frappe.ui.form.on('Landlord', {
    refresh: function(frm) {
        // Add custom buttons with enhanced error handling
        addCustomButtons(frm);
        
        // Add supplier information section
        if (frm.doc.supplier) {
            frm.add_custom_button(__('Open Supplier'), function() {
                frappe.set_route('Form', 'Supplier', frm.doc.supplier);
            }, __('Supplier'));
        }
    },
    
    // Calculate total rental amount when properties change
    properties: function(frm) {
        calculateTotalRentalAmount(frm);
    },
    
    // Auto-fetch property address when property is selected
    property: function(frm) {
        autoFetchPropertyAddress(frm);
    },
    
    // Validate contract dates
    contract_end_date: function(frm) {
        validateContractDates(frm);
    },
    
    // Validate rental amount
    rental_amount: function(frm) {
        validateRentalAmount(frm);
    },
    
    // Validate commission percentage
    commission_percentage: function(frm) {
        validateCommissionPercentage(frm);
    },
    
    // Show/hide bank fields based on payment method
    payment_method: function(frm) {
        toggleBankFields(frm);
    },
    
    // Validate email format
    email_address: function(frm) {
        validateEmailFormat(frm);
    },
    
    // Validate phone numbers
    primary_phone: function(frm) {
        validatePhoneNumber(frm, 'primary_phone');
    },
    
    secondary_phone: function(frm) {
        validatePhoneNumber(frm, 'secondary_phone');
    },
    
    // Calculate annual revenue
    rental_amount: function(frm) {
        calculateAnnualRevenue(frm);
    },
    
    // Auto-calculate next payment date
    payment_frequency: function(frm) {
        calculateNextPaymentDate(frm);
    }
});

// Modular functions for better organization and error handling

function addCustomButtons(frm) {
    try {
        // Generate Invoicing Schedules button
        frm.add_custom_button(__('Generate Invoicing Schedules'), function() {
            generateInvoicingSchedules(frm);
        });
        
        // View Invoicing Schedules button
        frm.add_custom_button(__('View Invoicing Schedules'), function() {
            viewInvoicingSchedules(frm);
        }, __('Actions'));
        
        // Send Welcome Email button
        frm.add_custom_button(__('Send Welcome Email'), function() {
            sendWelcomeEmail(frm);
        });
        
        // View Dashboard button
        frm.add_custom_button(__('View Dashboard'), function() {
            frappe.set_route('page', 'landlord-management-dashboard');
        });
        
        // Add Property button
        frm.add_custom_button(__('Add Property'), function() {
            addPropertyToLandlord(frm);
        });
        
        // Show additional buttons only when submitted
        if (frm.doc.docstatus === 1) {
            addSubmittedButtons(frm);
        }
    } catch (error) {
        console.error('Error adding custom buttons:', error);
        frappe.msgprint(__('Error setting up form buttons. Please refresh the page.'));
    }
}

function addSubmittedButtons(frm) {
    try {
        // View Supplier button
        frm.add_custom_button(__('View Supplier'), function() {
            viewSupplier(frm);
        }, __('Actions'));
        
        // View Purchase Invoices button
        frm.add_custom_button(__('View Purchase Invoices'), function() {
            viewPurchaseInvoices(frm);
        }, __('Actions'));
        
        // Create Invoices for Due Payments button
        frm.add_custom_button(__('Create Invoices for Due Payments'), function() {
            createInvoicesForDuePayments(frm);
        }, __('Actions'));
        
        // Update All Invoicing Schedules button
        frm.add_custom_button(__('Update All Invoicing Schedules'), function() {
            updateAllInvoicingSchedules(frm);
        }, __('Actions'));
        
        // Create Supplier button (if supplier doesn't exist)
        if (!frm.doc.supplier) {
            frm.add_custom_button(__('Create Supplier'), function() {
                createSupplier(frm);
            }, __('Actions'));
        }
    } catch (error) {
        console.error('Error adding submitted buttons:', error);
    }
}

function generateInvoicingSchedules(frm) {
    showLoadingState(frm, 'Generating invoicing schedules...');
    
    frm.call({
        method: 'generate_invoicing_schedules',
        doc: frm.doc,
        callback: function(r) {
            hideLoadingState(frm);
            
            if (r.message && r.message.success) {
                frappe.msgprint({
                    title: __('Success'),
                    message: r.message.message || __('Invoicing schedules generated successfully'),
                    indicator: 'green'
                });
                frm.reload_doc();
            } else {
                frappe.msgprint({
                    title: __('Error'),
                    message: r.message ? r.message.message : __('Failed to generate invoicing schedules'),
                    indicator: 'red'
                });
            }
        },
        error: function(err) {
            hideLoadingState(frm);
            handleApiError(err, 'Failed to generate invoicing schedules');
        }
    });
}

function viewInvoicingSchedules(frm) {
    try {
        frappe.call({
            method: 'vacker_automation.vacker_automation.doctype.landlord.landlord.get_payment_schedule_summary',
            args: {
                landlord: frm.doc.name
            },
            callback: function(r) {
                if (r.message) {
                    showInvoicingScheduleSummary(r.message);
                }
            },
            error: function(err) {
                handleApiError(err, 'Failed to load invoicing schedules');
            }
        });
    } catch (error) {
        console.error('Error viewing invoicing schedules:', error);
        frappe.msgprint(__('Error loading invoicing schedules. Please try again.'));
    }
}

function sendWelcomeEmail(frm) {
    showLoadingState(frm, 'Sending welcome email...');
    
    frm.call({
        method: 'send_welcome_notification',
        doc: frm.doc,
        callback: function(r) {
            hideLoadingState(frm);
            if (r.message) {
                frappe.msgprint(__('Welcome email sent successfully'));
            }
        },
        error: function(err) {
            hideLoadingState(frm);
            handleApiError(err, 'Failed to send welcome email');
        }
    });
}

function addPropertyToLandlord(frm) {
    try {
        // Create a dialog to add property
        let d = new frappe.ui.Dialog({
            title: __('Add Property'),
            fields: [
                {
                    fieldtype: 'Link',
                    fieldname: 'property',
                    label: __('Property'),
                    options: 'Property',
                    reqd: 1
                },
                {
                    fieldtype: 'Date',
                    fieldname: 'contract_start_date',
                    label: __('Contract Start Date'),
                    reqd: 1
                },
                {
                    fieldtype: 'Date',
                    fieldname: 'contract_end_date',
                    label: __('Contract End Date'),
                    reqd: 1
                },
                {
                    fieldtype: 'Currency',
                    fieldname: 'rental_amount',
                    label: __('Rental Amount'),
                    reqd: 1
                },
                {
                    fieldtype: 'Select',
                    fieldname: 'payment_frequency',
                    label: __('Payment Frequency'),
                    options: 'Monthly\nQuarterly\nAnnually',
                    reqd: 1
                }
            ],
            primary_action_label: __('Add Property'),
            primary_action: function(values) {
                addPropertyToChildTable(frm, values);
                d.hide();
            }
        });
        d.show();
    } catch (error) {
        console.error('Error creating add property dialog:', error);
        frappe.msgprint(__('Error creating property dialog. Please try again.'));
    }
}

function addPropertyToChildTable(frm, values) {
    try {
        let child = frm.add_child('properties');
        child.property = values.property;
        child.contract_start_date = values.contract_start_date;
        child.contract_end_date = values.contract_end_date;
        child.rental_amount = values.rental_amount;
        child.payment_frequency = values.payment_frequency;
        child.status = 'Active';
        
        frm.refresh_field('properties');
        calculateTotalRentalAmount(frm);
        
        frappe.msgprint(__('Property added successfully'));
    } catch (error) {
        console.error('Error adding property to child table:', error);
        frappe.msgprint(__('Error adding property. Please try again.'));
    }
}

function calculateTotalRentalAmount(frm) {
    try {
        let total = 0;
        if (frm.doc.properties) {
            frm.doc.properties.forEach(function(property) {
                if (property.rental_amount && property.status === 'Active') {
                    total += property.rental_amount;
                }
            });
        }
        frm.set_value('rental_amount', total);
    } catch (error) {
        console.error('Error calculating total rental amount:', error);
    }
}

function autoFetchPropertyAddress(frm) {
    try {
        if (frm.doc.property) {
            frappe.db.get_value('Property', frm.doc.property, 'full_address')
                .then(r => {
                    if (r.message) {
                        frm.set_value('property_address', r.message.full_address);
                    }
                })
                .catch(err => {
                    console.error('Error fetching property address:', err);
                });
        } else {
            frm.set_value('property_address', '');
        }
    } catch (error) {
        console.error('Error in autoFetchPropertyAddress:', error);
    }
}

function validateContractDates(frm) {
    try {
        if (frm.doc.contract_start_date && frm.doc.contract_end_date) {
            if (frm.doc.contract_end_date <= frm.doc.contract_start_date) {
                frappe.msgprint(__('Contract end date must be after start date'));
                frm.set_value('contract_end_date', '');
            }
        }
    } catch (error) {
        console.error('Error validating contract dates:', error);
    }
}

function validateRentalAmount(frm) {
    try {
        if (frm.doc.rental_amount && frm.doc.rental_amount <= 0) {
            frappe.msgprint(__('Rental amount must be greater than zero'));
            frm.set_value('rental_amount', '');
        }
    } catch (error) {
        console.error('Error validating rental amount:', error);
    }
}

function validateCommissionPercentage(frm) {
    try {
        if (frm.doc.commission_percentage && 
            (frm.doc.commission_percentage < 0 || frm.doc.commission_percentage > 100)) {
            frappe.msgprint(__('Commission percentage must be between 0 and 100'));
            frm.set_value('commission_percentage', 0);
        }
    } catch (error) {
        console.error('Error validating commission percentage:', error);
    }
}

function toggleBankFields(frm) {
    try {
        if (frm.doc.payment_method === 'Bank Transfer') {
            frm.set_df_property('bank_name', 'hidden', 0);
            frm.set_df_property('account_number', 'hidden', 0);
        } else {
            frm.set_df_property('bank_name', 'hidden', 1);
            frm.set_df_property('account_number', 'hidden', 1);
        }
    } catch (error) {
        console.error('Error toggling bank fields:', error);
    }
}

function validateEmailFormat(frm) {
    try {
        if (frm.doc.email_address) {
            const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailPattern.test(frm.doc.email_address)) {
                frappe.msgprint(__('Please enter a valid email address'));
            }
        }
    } catch (error) {
        console.error('Error validating email format:', error);
    }
}

function validatePhoneNumber(frm, fieldname) {
    try {
        if (frm.doc[fieldname]) {
            const phoneClean = frm.doc[fieldname].replace(/[\s\-\(\)\+]/g, '');
            if (!phoneClean.match(/^\d{8,}$/)) {
                frappe.msgprint(__(`Please enter a valid ${fieldname.replace('_', ' ')} (minimum 8 digits)`));
            }
        }
    } catch (error) {
        console.error('Error validating phone number:', error);
    }
}

function calculateAnnualRevenue(frm) {
    try {
        if (frm.doc.rental_amount && frm.doc.payment_frequency) {
            let annualRevenue = 0;
            if (frm.doc.payment_frequency === 'Monthly') {
                annualRevenue = frm.doc.rental_amount * 12;
            } else if (frm.doc.payment_frequency === 'Quarterly') {
                annualRevenue = frm.doc.rental_amount * 4;
            } else if (frm.doc.payment_frequency === 'Annually') {
                annualRevenue = frm.doc.rental_amount;
            }
            
            if (annualRevenue > 0) {
                frappe.show_alert(__('Annual Revenue: ') + frappe.format(annualRevenue, {fieldtype: 'Currency'}), 3);
            }
        }
    } catch (error) {
        console.error('Error calculating annual revenue:', error);
    }
}

function calculateNextPaymentDate(frm) {
    try {
        if (frm.doc.contract_start_date && frm.doc.payment_frequency) {
            let nextPaymentDate = frappe.datetime.add_months(frm.doc.contract_start_date, 1);
            
            if (frm.doc.payment_frequency === 'Quarterly') {
                nextPaymentDate = frappe.datetime.add_months(frm.doc.contract_start_date, 3);
            } else if (frm.doc.payment_frequency === 'Annually') {
                nextPaymentDate = frappe.datetime.add_years(frm.doc.contract_start_date, 1);
            }
            
            frappe.show_alert(__('Next Payment Date: ') + frappe.format(nextPaymentDate, {fieldtype: 'Date'}), 3);
        }
    } catch (error) {
        console.error('Error calculating next payment date:', error);
    }
}

// Utility functions for better error handling and user experience

function showLoadingState(frm, message) {
    try {
        frm.dashboard.add_indicator(message, 'blue');
        frm.disable_save();
    } catch (error) {
        console.error('Error showing loading state:', error);
    }
}

function hideLoadingState(frm) {
    try {
        frm.dashboard.clear_indicator();
        frm.enable_save();
    } catch (error) {
        console.error('Error hiding loading state:', error);
    }
}

function handleApiError(err, defaultMessage) {
    console.error('API Error:', err);
    let message = defaultMessage;
    
    if (err && err.message) {
        message = err.message;
    } else if (err && err.responseJSON && err.responseJSON.message) {
        message = err.responseJSON.message;
    }
    
    frappe.msgprint({
        title: __('Error'),
        message: message,
        indicator: 'red'
    });
}

function viewSupplier(frm) {
    try {
        if (frm.doc.supplier) {
            frappe.set_route('Form', 'Supplier', frm.doc.supplier);
        } else {
            frappe.msgprint(__('No supplier associated with this landlord'));
        }
    } catch (error) {
        console.error('Error viewing supplier:', error);
        frappe.msgprint(__('Error opening supplier. Please try again.'));
    }
}

function viewPurchaseInvoices(frm) {
    try {
        frappe.call({
            method: 'vacker_automation.vacker_automation.doctype.landlord.landlord.get_purchase_invoice_summary',
            args: {
                landlord: frm.doc.name
            },
            callback: function(r) {
                if (r.message) {
                    showPurchaseInvoiceSummary(r.message);
                }
            },
            error: function(err) {
                handleApiError(err, 'Failed to load purchase invoices');
            }
        });
    } catch (error) {
        console.error('Error viewing purchase invoices:', error);
        frappe.msgprint(__('Error loading purchase invoices. Please try again.'));
    }
}

function createInvoicesForDuePayments(frm) {
    showLoadingState(frm, 'Creating invoices for due payments...');
    
    frm.call({
        method: 'create_purchase_invoices_from_schedules',
        doc: frm.doc,
        callback: function(r) {
            hideLoadingState(frm);
            if (r.message && r.message.success) {
                frappe.msgprint({
                    title: __('Success'),
                    message: r.message.message || __('Invoices created successfully'),
                    indicator: 'green'
                });
            } else {
                frappe.msgprint({
                    title: __('Error'),
                    message: r.message ? r.message.message : __('Failed to create invoices'),
                    indicator: 'red'
                });
            }
        },
        error: function(err) {
            hideLoadingState(frm);
            handleApiError(err, 'Failed to create invoices');
        }
    });
}

function updateAllInvoicingSchedules(frm) {
    showLoadingState(frm, 'Updating all invoicing schedules...');
    
    frm.call({
        method: 'update_all_payment_schedules',
        doc: frm.doc,
        callback: function(r) {
            hideLoadingState(frm);
            if (r.message && r.message.success) {
                frappe.msgprint({
                    title: __('Success'),
                    message: r.message.message || __('Invoicing schedules updated successfully'),
                    indicator: 'green'
                });
            } else {
                frappe.msgprint({
                    title: __('Error'),
                    message: r.message ? r.message.message : __('Failed to update invoicing schedules'),
                    indicator: 'red'
                });
            }
        },
        error: function(err) {
            hideLoadingState(frm);
            handleApiError(err, 'Failed to update invoicing schedules');
        }
    });
}

function createSupplier(frm) {
    showLoadingState(frm, 'Creating supplier...');
    
    frm.call({
        method: 'create_supplier_manually',
        doc: frm.doc,
        callback: function(r) {
            hideLoadingState(frm);
            if (r.message && r.message.success) {
                frappe.msgprint({
                    title: __('Success'),
                    message: r.message.message || __('Supplier created successfully'),
                    indicator: 'green'
                });
                frm.reload_doc();
            } else {
                frappe.msgprint({
                    title: __('Error'),
                    message: r.message ? r.message.message : __('Failed to create supplier'),
                    indicator: 'red'
                });
            }
        },
        error: function(err) {
            hideLoadingState(frm);
            handleApiError(err, 'Failed to create supplier');
        }
    });
}

// Enhanced display functions with better error handling

function showInvoicingScheduleSummary(summary) {
    try {
        let content = '<div class="invoicing-schedule-summary">';
        content += '<h4>Invoicing Schedule Summary</h4>';
        content += '<table class="table table-bordered">';
        content += '<thead><tr><th>Property</th><th>Due Date</th><th>Amount</th><th>Status</th></tr></thead>';
        content += '<tbody>';
        
        if (summary.schedules && summary.schedules.length > 0) {
            summary.schedules.forEach(function(schedule) {
                content += `<tr>
                    <td>${schedule.property}</td>
                    <td>${schedule.due_date}</td>
                    <td>${frappe.format(schedule.amount, {fieldtype: 'Currency'})}</td>
                    <td><span class="label label-${getStatusColor(schedule.status)}">${schedule.status}</span></td>
                </tr>`;
            });
        } else {
            content += '<tr><td colspan="4" class="text-center">No invoicing schedules found</td></tr>';
        }
        
        content += '</tbody></table>';
        content += '</div>';
        
        let d = new frappe.ui.Dialog({
            title: __('Invoicing Schedule Summary'),
            width: 'large',
            fields: [{
                fieldtype: 'HTML',
                fieldname: 'summary',
                options: content
            }]
        });
        d.show();
    } catch (error) {
        console.error('Error showing invoicing schedule summary:', error);
        frappe.msgprint(__('Error displaying invoicing schedule summary. Please try again.'));
    }
}

function showPurchaseInvoiceSummary(summary) {
    try {
        let content = '<div class="purchase-invoice-summary">';
        content += '<h4>Purchase Invoice Summary</h4>';
        content += '<table class="table table-bordered">';
        content += '<thead><tr><th>Invoice</th><th>Date</th><th>Amount</th><th>Status</th></tr></thead>';
        content += '<tbody>';
        
        if (summary.invoices && summary.invoices.length > 0) {
            summary.invoices.forEach(function(invoice) {
                content += `<tr>
                    <td>${invoice.name}</td>
                    <td>${invoice.posting_date}</td>
                    <td>${frappe.format(invoice.grand_total, {fieldtype: 'Currency'})}</td>
                    <td><span class="label label-${getStatusColor(invoice.status)}">${invoice.status}</span></td>
                </tr>`;
            });
        } else {
            content += '<tr><td colspan="4" class="text-center">No purchase invoices found</td></tr>';
        }
        
        content += '</tbody></table>';
        content += '</div>';
        
        let d = new frappe.ui.Dialog({
            title: __('Purchase Invoice Summary'),
            width: 'large',
            fields: [{
                fieldtype: 'HTML',
                fieldname: 'summary',
                options: content
            }]
        });
        d.show();
    } catch (error) {
        console.error('Error showing purchase invoice summary:', error);
        frappe.msgprint(__('Error displaying purchase invoice summary. Please try again.'));
    }
}

function getStatusColor(status) {
    const statusColors = {
        'Pending': 'warning',
        'Paid': 'success',
        'Overdue': 'danger',
        'Partially Paid': 'info',
        'Cancelled': 'default'
    };
    return statusColors[status] || 'default';
} 