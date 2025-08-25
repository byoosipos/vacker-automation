// Copyright (c) 2025, Vacker and contributors
// For license information, please see license.txt

frappe.ui.form.on('Print Order Job Detail', {
    qty: function(frm, cdt, cdn) {
        calculate_row_total(frm, cdt, cdn);
    },
    sqmts: function(frm, cdt, cdn) {
        calculate_row_total(frm, cdt, cdn);
    },
    job_details_table_remove: function(frm) {
        calculate_parent_total(frm);
    },
    job_details_table_add: function(frm) {
        calculate_parent_total(frm);
    }
});

frappe.ui.form.on('Print Order', {
    refresh: function(frm) {
        calculate_parent_total(frm);
        // Set up dynamic filters for Sales Order
        frm.set_query('sales_order', function() {
            return {
                filters: {
                    'customer': frm.doc.customer || ''
                }
            };
        });
        
        // Set up role-based filters for approval fields
        frm.set_query('production_manager', function() {
            return {
                filters: {
                    'user_type': 'System User',
                    'enabled': 1
                },
                query: 'frappe.core.doctype.user.user.user_query',
                filters: {
                    'role': 'Production Manager'
                }
            };
        });
        
        frm.set_query('finance_manager', function() {
            return {
                filters: {
                    'user_type': 'System User',
                    'enabled': 1
                },
                query: 'frappe.core.doctype.user.user.user_query',
                filters: {
                    'role': 'Finance Manager'
                }
            };
        });
        
        frm.set_query('sales_marketing', function() {
            return {
                filters: {
                    'user_type': 'System User',
                    'enabled': 1
                },
                query: 'frappe.core.doctype.user.user.user_query',
                filters: {
                    'role': 'Sales & Marketing'
                }
            };
        });
        
        frm.set_query('managing_director', function() {
            return {
                filters: {
                    'user_type': 'System User',
                    'enabled': 1
                },
                query: 'frappe.core.doctype.user.user.user_query',
                filters: {
                    'role': 'Managing Director'
                }
            };
        });
        
        // Control submit button visibility based on approval status
        check_approval_status(frm);
    },
    job_details_table_on_form_rendered: function(frm) {
        calculate_parent_total(frm);
    },
    customer: function(frm) {
        // Clear sales_order when customer changes
        frm.set_value('sales_order', '');
        frm.refresh_field('sales_order');
    },
    sales_order: function(frm) {
        if (frm.doc.sales_order) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Sales Order',
                    name: frm.doc.sales_order
                },
                callback: function(r) {
                    if (r.message) {
                        // Auto-fill LPO No. from Sales Order's po_no
                        if (r.message.po_no) {
                            frm.set_value('lpo_no', r.message.po_no);
                        }
                        
                        // Populate job details table with items
                        if (r.message.items) {
                            // Optionally confirm with user if table is not empty
                            if (frm.doc.job_details_table && frm.doc.job_details_table.length > 0) {
                                frappe.confirm('Job Details table is not empty. Do you want to overwrite it with items from the Sales Order?', () => {
                                    set_items_from_sales_order(frm, r.message.items);
                                });
                            } else {
                                set_items_from_sales_order(frm, r.message.items);
                            }
                        }
                    }
                }
            });
        }
    },
    production_manager: function(frm) {
        check_approval_status(frm);
    },
    finance_manager: function(frm) {
        check_approval_status(frm);
    },
    sales_marketing: function(frm) {
        check_approval_status(frm);
    },
    managing_director: function(frm) {
        check_approval_status(frm);
    }
});

function calculate_row_total(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    row.total_sqmts = (row.qty || 0) * (row.sqmts || 0);
    frm.refresh_field('job_details_table');
    calculate_parent_total(frm);
}

function calculate_parent_total(frm) {
    let total = 0;
    (frm.doc.job_details_table || []).forEach(row => {
        total += row.total_sqmts || 0;
    });
    frm.set_value('total_sqmts', total);
}

function set_items_from_sales_order(frm, items) {
    frm.clear_table('job_details_table');
    (items || []).forEach(item => {
        let row = frm.add_child('job_details_table');
        row.job_details = item.item_name || item.description || '';
        row.print_sizes = '';
        row.orientation = '';
        row.material = '';
        row.qty = item.qty || 0;
        row.sqmts = 0;
        row.total_sqmts = 0;
    });
    frm.refresh_field('job_details_table');
    calculate_parent_total(frm);
}

function check_approval_status(frm) {
    const required_approvals = [
        'production_manager',
        'finance_manager', 
        'sales_marketing',
        'managing_director'
    ];
    
    const all_approved = required_approvals.every(field => frm.doc[field]);
    
    if (all_approved) {
        frm.enable_save();
        frm.page.show_inner_button('Submit', true);
    } else {
        frm.page.show_inner_button('Submit', false);
    }
}
