// Copyright (c) 2025, Vacker and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Landlord Payment Schedule", {
// 	refresh(frm) {

// 	},
// });

// Landlord Payment Schedule Form JavaScript
frappe.ui.form.on('Landlord Payment Schedule', {
    refresh: function(frm) {
        // Add custom buttons
        if (frm.doc.status === "Pending" && !frm.doc.purchase_invoice) {
            frm.add_custom_button(__('Create Purchase Invoice'), function() {
                create_purchase_invoice(frm);
            }, __('Actions'));
        }
        
        // Add button to view purchase invoice if it exists
        if (frm.doc.purchase_invoice) {
            frm.add_custom_button(__('View Purchase Invoice'), function() {
                frappe.set_route('Form', 'Purchase Invoice', frm.doc.purchase_invoice);
            }, __('Invoice'));
            
            // Add button to update payment status if invoice is paid
            if (frm.doc.status !== "Paid") {
                frm.add_custom_button(__('Mark as Paid'), function() {
                    update_payment_status(frm);
                }, __('Actions'));
                
                // Add button to update from invoice if invoice exists
                if (frm.doc.purchase_invoice) {
                    frm.add_custom_button(__('Update from Invoice'), function() {
                        update_from_invoice(frm);
                    }, __('Actions'));
                }
            }
        }
        
        // Add button to view landlord
        if (frm.doc.landlord) {
            frm.add_custom_button(__('View Landlord'), function() {
                frappe.set_route('Form', 'Landlord', frm.doc.landlord);
            }, __('Landlord'));
        }
        
        // Add button to view property
        if (frm.doc.property) {
            frm.add_custom_button(__('View Property'), function() {
                frappe.set_route('Form', 'Property', frm.doc.property);
            }, __('Property'));
        }
    },
    
    onload: function(frm) {
        // Show due date information
        if (frm.doc.due_date) {
            show_due_date_info(frm);
        }
    }
});

function create_purchase_invoice(frm) {
    frappe.call({
        method: 'vacker_automation.vacker_automation.custom_api.work_flow.create_invoice_for_specific_schedule',
        args: {
            schedule_name: frm.doc.name
        },
        callback: function(r) {
            if (r.message.success) {
                frappe.msgprint({
                    title: __('Success'),
                    message: r.message.message,
                    indicator: 'green'
                });
                frm.refresh();
            } else {
                frappe.msgprint({
                    title: __('Error'),
                    message: r.message.message,
                    indicator: 'red'
                });
            }
        }
    });
}

function update_payment_status(frm) {
    frappe.call({
        method: 'vacker_automation.vacker_automation.doctype.landlord_payment_schedule.landlord_payment_schedule.mark_as_paid',
        args: {
            landlord_payment_schedule: frm.doc.name,
            payment_date: frappe.datetime.nowdate(),
            payment_reference: frm.doc.purchase_invoice || 'Manual Payment'
        },
        callback: function(r) {
            if (r.message) {
                frappe.msgprint({
                    title: __('Success'),
                    message: r.message,
                    indicator: 'green'
                });
                frm.refresh();
            } else {
                frappe.msgprint({
                    title: __('Error'),
                    message: 'Error updating payment status.',
                    indicator: 'red'
                });
            }
        },
        error: function(err) {
            frappe.msgprint({
                title: __('Error'),
                message: 'Failed to update payment status. Please try again.',
                indicator: 'red'
            });
        }
    });
}

function update_from_invoice(frm) {
    frappe.call({
        method: 'vacker_automation.vacker_automation.doctype.landlord_payment_schedule.landlord_payment_schedule.update_payment_status_from_invoice',
        args: {
            landlord_payment_schedule: frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.msgprint({
                    title: __('Success'),
                    message: r.message.message,
                    indicator: 'green'
                });
                frm.refresh();
            } else {
                let errorMsg = r.message && r.message.message ? r.message.message : 'Error updating from invoice.';
                frappe.msgprint({
                    title: __('Error'),
                    message: errorMsg,
                    indicator: 'red'
                });
            }
        },
        error: function(err) {
            frappe.msgprint({
                title: __('Error'),
                message: 'Failed to update from invoice. Please try again.',
                indicator: 'red'
            });
        }
    });
}

function show_due_date_info(frm) {
    if (frm.doc.due_date) {
        const due_date = new Date(frm.doc.due_date);
        const today = new Date();
        const diff_time = due_date - today;
        const diff_days = Math.ceil(diff_time / (1000 * 60 * 60 * 24));
        
        let status_text = '';
        let indicator = 'blue';
        
        if (diff_days < 0) {
            status_text = `Overdue by ${Math.abs(diff_days)} days`;
            indicator = 'red';
        } else if (diff_days === 0) {
            status_text = 'Due today';
            indicator = 'orange';
        } else if (diff_days <= 7) {
            status_text = `Due in ${diff_days} days`;
            indicator = 'yellow';
        } else {
            status_text = `Due in ${diff_days} days`;
            indicator = 'green';
        }
        
        frappe.show_alert(status_text, indicator);
    }
}
