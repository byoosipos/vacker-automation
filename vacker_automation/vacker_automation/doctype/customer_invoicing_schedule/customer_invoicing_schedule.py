import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, add_months
from frappe import _

class CustomerInvoicingSchedule(Document):
    def validate(self):
        """Validate customer invoicing schedule data"""
        self.validate_due_date()
        self.validate_amount()
        self.update_status()
        self.auto_fetch_property()
    
    def validate_due_date(self):
        """Validate due date"""
        if self.due_date:
            due_date = getdate(self.due_date)
            today_date = getdate(today())
            if due_date < today_date:
                if self.status == "Pending":
                    self.status = "Overdue"
    
    def validate_amount(self):
        """Validate payment amount"""
        if self.amount and self.amount <= 0:
            frappe.throw(_("Payment amount must be greater than zero"))
    
    def update_status(self):
        """Update payment status based on due date and payment date"""
        if self.payment_date:
            self.status = "Paid"
        elif self.due_date:
            due_date = getdate(self.due_date)
            today_date = getdate(today())
            if due_date < today_date and self.status == "Pending":
                self.status = "Overdue"
    
    def auto_fetch_property(self):
        """Auto-fetch property from media installation"""
        if self.media_installation and not self.property:
            property_name = frappe.db.get_value("Media Installation", self.media_installation, "property")
            if property_name:
                self.property = property_name
    
    def get_project_from_media_installation(self):
        """Get project name from media installation"""
        if self.media_installation:
            project_name = frappe.db.get_value("Media Installation", self.media_installation, "project")
            return project_name
        return None
    
    def on_update(self):
        """Actions to perform after customer invoicing schedule is updated"""
        self.send_payment_reminders()
        self.create_sales_invoice()
    
    def send_payment_reminders(self):
        """Send payment reminders"""
        if self.status == "Overdue":
            self.send_overdue_reminder()
        elif self.status == "Pending" and self.due_date:
            days_until_due = (getdate(self.due_date) - getdate(today())).days
            if 0 <= days_until_due <= 7:
                self.send_due_reminder(days_until_due)
    
    def send_overdue_reminder(self):
        """Send overdue payment reminder"""
        customer_email = frappe.db.get_value("Customer", self.customer, "email_id")
        if customer_email:
            subject = f"Payment Overdue - Media Installation: {self.media_installation}"
            message = f"""
            Dear Customer,
            
            Your payment for media installation is overdue.
            
            Media Installation: {self.media_installation}
            Property: {self.property}
            Due Date: {self.due_date}
            Amount: {self.amount}
            
            Please make the payment as soon as possible to avoid any service interruptions.
            
            Best regards,
            Vacker Outdoor Advertising Team
            """
            
            frappe.sendmail(
                recipients=[customer_email],
                subject=subject,
                message=message
            )
    
    def send_due_reminder(self, days_until_due):
        """Send payment due reminder"""
        customer_email = frappe.db.get_value("Customer", self.customer, "email_id")
        if customer_email:
            subject = f"Payment Due in {days_until_due} days - Media Installation: {self.media_installation}"
            message = f"""
            Dear Customer,
            
            This is a reminder that your payment is due in {days_until_due} days.
            
            Media Installation: {self.media_installation}
            Property: {self.property}
            Due Date: {self.due_date}
            Amount: {self.amount}
            
            Please ensure timely payment to avoid any late fees.
            
            Best regards,
            Vacker Outdoor Advertising Team
            """
            
            frappe.sendmail(
                recipients=[customer_email],
                subject=subject,
                message=message
            )
    
    def get_or_create_sales_order(self):
        """Get or create a Sales Order for this rental"""
        # Get project from media installation
        project_name = self.get_project_from_media_installation()
        
        # Get rental start date from media installation for delivery date
        rental_start_date = None
        if self.media_installation:
            rental_start_date = frappe.db.get_value("Media Installation", self.media_installation, "rental_start_date")
        
        # Try to find an existing Sales Order for this customer, project, and media installation
        filters = {
            "customer": self.customer,
            "docstatus": ["<", 2],
        }
        
        # Add project filter only if project exists
        if project_name:
            filters["project"] = project_name
            
        sales_orders = frappe.get_all("Sales Order", filters=filters, fields=["name"])
        if sales_orders:
            return sales_orders[0]["name"]
        
        # Create a new Sales Order
        so = frappe.new_doc("Sales Order")
        so.customer = self.customer
        
        # Set project if available
        if project_name:
            so.project = project_name
            
        # Set delivery date to rental start date (same as posting date)
        if rental_start_date:
            so.delivery_date = rental_start_date
            so.transaction_date = rental_start_date
        else:
            # Fallback to today's date if no rental start date
            so.delivery_date = today()
            so.transaction_date = today()
            
        so.append("items", {
            "item_code": "Media Rental",
            "qty": 1,
            "rate": self.amount,
            "amount": self.amount,
            "description": f"Media rental for installation {self.media_installation} - Property: {self.property}",
            "delivery_date": rental_start_date or today()
        })
        
        so.insert(ignore_permissions=True)
        frappe.msgprint(f"Sales Order {so.name} created for customer {self.customer} and project {project_name or 'N/A'}")
        return so.name

    def create_sales_invoice(self):
        """Automatically create sales invoice for this customer invoicing schedule"""
        if self.status == "Pending" and not self.sales_invoice:
            try:
                # ADVANCE INVOICING LOGIC: Create invoice 1 month before due date
                due_date = getdate(self.due_date)
                today_date = getdate(today())
                invoice_creation_date = add_months(due_date, -1)
                should_create_invoice = False
                reason = ""
                if due_date < today_date:
                    should_create_invoice = True
                    reason = "overdue"
                elif today_date >= invoice_creation_date:
                    should_create_invoice = True
                    reason = "advance_invoicing"
                if should_create_invoice:
                    # Get or create Sales Order
                    sales_order = self.get_or_create_sales_order()
                    
                    # Get project from media installation
                    project_name = self.get_project_from_media_installation()
                    
                    # Create sales invoice
                    si = frappe.new_doc("Sales Invoice")
                    si.customer = self.customer
                    
                    # Set project if available
                    if project_name:
                        si.project = project_name
                        
                    si.sales_order = sales_order
                    
                    if reason == "overdue":
                        si.posting_date = today_date
                    else:
                        si.posting_date = invoice_creation_date
                        
                    si.due_date = self.due_date
                    si.company = frappe.defaults.get_global_default("company")
                    
                    # Add item for media rental
                    si.append("items", {
                        "item_code": "Media Rental",
                        "qty": 1,
                        "rate": self.amount,
                        "amount": self.amount,
                        "description": f"Media rental for installation {self.media_installation} - Property: {self.property}",
                        "sales_order": sales_order
                    })
                    
                    si.insert(ignore_permissions=True)
                    
                    # Update customer invoicing schedule
                    self.sales_invoice = si.name
                    self.invoice_date = si.posting_date
                    self.status = "Invoice Created"
                    self.save(ignore_permissions=True)
                    
                    frappe.msgprint(f"Sales Invoice {si.name} created for customer invoicing schedule {self.name}")
            except Exception as e:
                frappe.log_error(f"Error creating sales invoice: {str(e)}")
                frappe.msgprint(f"Error creating sales invoice: {str(e)}", indicator="red")
    
    @frappe.whitelist()
    def mark_as_paid(self, payment_date=None, payment_reference=None):
        """Mark customer invoicing schedule as paid"""
        if not payment_date:
            payment_date = today()
        
        self.payment_date = payment_date
        self.payment_reference = payment_reference
        self.status = "Paid"
        self.save(ignore_permissions=True)
        
        return "Customer invoicing schedule marked as paid successfully"
    
    @frappe.whitelist()
    def get_payment_summary(self):
        """Get customer invoicing schedule summary"""
        days_overdue = 0
        if self.status == "Overdue" and self.due_date:
            days_overdue = (getdate(today()) - getdate(self.due_date)).days
        
        # Calculate days until invoice creation (1 month before due)
        days_until_invoice = 0
        if self.due_date and self.status == "Pending":
            invoice_creation_date = add_months(getdate(self.due_date), -1)
            days_until_invoice = (invoice_creation_date - getdate(today())).days
        
        return {
            "customer": self.customer,
            "media_installation": self.media_installation,
            "property": self.property,
            "due_date": self.due_date,
            "amount": self.amount,
            "status": self.status,
            "payment_date": self.payment_date,
            "payment_reference": self.payment_reference,
            "sales_invoice": self.sales_invoice,
            "is_overdue": self.status == "Overdue",
            "days_overdue": days_overdue,
            "days_until_invoice": days_until_invoice,
            "is_backdated": getdate(self.due_date) < getdate(today()) if self.due_date else False
        }
    
    @frappe.whitelist()
    def update_payment_status_from_invoice(self):
        """Update payment status based on the linked sales invoice"""
        try:
            if not self.sales_invoice:
                return {"success": False, "message": "No sales invoice linked to this customer invoicing schedule"}
            
            # Get the sales invoice
            invoice = frappe.get_doc("Sales Invoice", self.sales_invoice)
            
            if invoice.status == "Paid":
                # Update customer invoicing schedule with payment details
                self.status = "Paid"
                self.payment_date = invoice.modified
                self.payment_reference = invoice.name
                
                self.save(ignore_permissions=True)
                
                return {
                    "success": True,
                    "message": f"Customer invoicing schedule updated successfully. Payment date: {self.payment_date}"
                }
            else:
                return {
                    "success": False,
                    "message": f"Sales invoice is not paid yet. Current status: {invoice.status}"
                }
                
        except Exception as e:
            frappe.log_error(f"Error updating payment status for customer invoicing schedule {self.name}: {str(e)}")
            return {"success": False, "message": f"Error updating payment status: {str(e)}"}

@frappe.whitelist()
def mark_as_paid(customer_invoicing_schedule, payment_date=None, payment_reference=None):
    """Wrapper function to mark customer invoicing schedule as paid"""
    doc = frappe.get_doc("Customer Invoicing Schedule", customer_invoicing_schedule)
    return doc.mark_as_paid(payment_date, payment_reference)

@frappe.whitelist()
def update_payment_status_from_invoice(customer_invoicing_schedule):
    """Wrapper function to update payment status from invoice"""
    doc = frappe.get_doc("Customer Invoicing Schedule", customer_invoicing_schedule)
    return doc.update_payment_status_from_invoice() 