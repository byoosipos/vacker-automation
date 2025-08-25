# Copyright (c) 2025, Vacker and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import frappe

class PrintOrder(Document):
    def validate(self):
        self.calculate_total_sqmts()
        self.validate_required_fields()
        self.validate_quantities()
        self.validate_approval_permissions()

    def calculate_total_sqmts(self):
        total = 0
        for d in self.job_details_table:
            d.total_sqmts = (d.qty or 0) * (d.sqmts or 0)
            total += d.total_sqmts or 0
        self.total_sqmts = total

    def validate_required_fields(self):
        required_fields = [
            ('client_name', 'Client Name'),
            ('account_holder', 'Account Holder'),
            ('lpo_no', 'LPO No.'),
            ('date', 'Date'),
        ]
        for field, label in required_fields:
            if not self.get(field):
                frappe.throw(f"{label} is required.")
        if not self.job_details_table:
            frappe.throw("At least one Job Detail is required.")

    def validate_quantities(self):
        for d in self.job_details_table:
            if (d.qty or 0) <= 0:
                frappe.throw(f"Qty must be positive for job: {d.job_details}")
            if (d.sqmts or 0) <= 0:
                frappe.throw(f"SQMTS must be positive for job: {d.job_details}")

    def validate_approval_permissions(self):
        current_user = frappe.session.user
        user_roles = frappe.get_roles(current_user)
        
        # Check if user is trying to set approval fields
        if self.has_value_changed('production_manager') and self.production_manager:
            if 'Production Manager' not in user_roles:
                frappe.throw("Only users with 'Production Manager' role can set Production Manager field.")
        
        if self.has_value_changed('finance_manager') and self.finance_manager:
            if 'Finance Manager' not in user_roles:
                frappe.throw("Only users with 'Finance Manager' role can set Finance Manager field.")
        
        if self.has_value_changed('sales_marketing') and self.sales_marketing:
            if 'Sales & Marketing' not in user_roles:
                frappe.throw("Only users with 'Sales & Marketing' role can set Sales & Marketing field.")
        
        if self.has_value_changed('managing_director') and self.managing_director:
            if 'Managing Director' not in user_roles:
                frappe.throw("Only users with 'Managing Director' role can set Managing Director field.")
