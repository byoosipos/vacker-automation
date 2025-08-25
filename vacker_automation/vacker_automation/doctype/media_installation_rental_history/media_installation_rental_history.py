import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today
from frappe import _

class MediaInstallationRentalHistory(Document):
    def validate(self):
        """Validate rental history data"""
        self.validate_rental_dates()
        self.auto_fetch_customer_name()
        self.calculate_total_revenue()
    
    def validate_rental_dates(self):
        """Validate rental start and end dates"""
        if self.rental_start_date and self.rental_end_date:
            if getdate(self.rental_end_date) <= getdate(self.rental_start_date):
                frappe.throw(_("Rental end date must be after start date"))
    
    def auto_fetch_customer_name(self):
        """Auto-fetch customer name when customer is selected"""
        if self.customer and not self.customer_name:
            customer_name = frappe.db.get_value("Customer", self.customer, "customer_name")
            if customer_name:
                self.customer_name = customer_name
    
    def calculate_total_revenue(self):
        """Calculate total revenue based on rental period and frequency"""
        if (self.rental_start_date and 
            self.rental_end_date and 
            self.rental_amount and 
            self.rental_frequency):
            
            start_date = getdate(self.rental_start_date)
            end_date = getdate(self.rental_end_date)
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            
            if self.rental_frequency == "Monthly":
                self.total_revenue = self.rental_amount * max(1, months)
            elif self.rental_frequency == "Quarterly":
                self.total_revenue = self.rental_amount * max(1, months // 3)
            elif self.rental_frequency == "Annually":
                self.total_revenue = self.rental_amount * max(1, months // 12)
            else:  # One-time
                self.total_revenue = self.rental_amount
    
    def on_update(self):
        """Actions to perform after rental history is updated"""
        self.update_rental_status()
    
    def update_rental_status(self):
        """Update rental status based on dates"""
        if self.rental_start_date and self.rental_end_date:
            today_date = getdate(today())
            start_date = getdate(self.rental_start_date)
            end_date = getdate(self.rental_end_date)
            
            if today_date < start_date:
                self.rental_status = "Scheduled"
            elif start_date <= today_date <= end_date:
                self.rental_status = "Active"
            else:
                self.rental_status = "Completed"
    
    @frappe.whitelist()
    def get_rental_summary(self):
        """Get rental summary for this entry"""
        return {
            "customer": self.customer,
            "customer_name": self.customer_name,
            "rental_period": {
                "start_date": self.rental_start_date,
                "end_date": self.rental_end_date,
                "duration_months": self._calculate_duration_months()
            },
            "financial": {
                "rental_amount": self.rental_amount,
                "rental_frequency": self.rental_frequency,
                "total_revenue": self.total_revenue
            },
            "status": self.rental_status
        }
    
    def _calculate_duration_months(self):
        """Calculate rental duration in months"""
        if self.rental_start_date and self.rental_end_date:
            start_date = getdate(self.rental_start_date)
            end_date = getdate(self.rental_end_date)
            return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        return 0 