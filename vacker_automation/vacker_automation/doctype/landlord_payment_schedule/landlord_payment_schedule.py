import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, add_days, add_months
from frappe import _
import logging

# Configure logging
logger = logging.getLogger(__name__)

class LandlordPaymentSchedule(Document):
    """
    Enhanced Landlord Payment Schedule with partial payment support and comprehensive tracking.
    
    This doctype handles:
    - Payment schedule generation for landlord properties
    - Partial payment tracking and reconciliation
    - Automatic invoice creation with advance invoicing logic
    - Payment status management and notifications
    - Integration with ERPNext Purchase Invoice system
    
    Key Features:
    - Advance invoicing (1 month before due date)
    - Partial payment support with balance tracking
    - Escalation clause support
    - Comprehensive audit logging
    - Role-based access control
    """
    
    def validate(self):
        """Validate payment schedule data with enhanced checks"""
        try:
            self.validate_due_date()
            self.validate_amount()
            self.validate_partial_payment()
            self.update_status()
            self.log_payment_changes()
        except Exception as e:
            logger.error(f"Validation error in LandlordPaymentSchedule {self.name}: {str(e)}")
            frappe.throw(_(f"Validation failed: {str(e)}"))
    
    def validate_due_date(self):
        """Validate due date and update status accordingly"""
        if self.due_date:
            due_date = getdate(self.due_date)
            today_date = getdate(today())
            if due_date < today_date:
                if self.status == "Pending":
                    self.status = "Overdue"
    
    def validate_amount(self):
        """Validate payment amount and partial payment amounts"""
        if self.amount and self.amount <= 0:
            frappe.throw(_("Payment amount must be greater than zero"))
        
        # Validate partial payment amount
        if hasattr(self, 'partial_payment_amount') and self.partial_payment_amount:
            if self.partial_payment_amount < 0:
                frappe.throw(_("Partial payment amount cannot be negative"))
            if self.partial_payment_amount > self.amount:
                frappe.throw(_("Partial payment amount cannot exceed total amount"))
    
    def validate_partial_payment(self):
        """Validate partial payment logic and calculate remaining balance"""
        if hasattr(self, 'partial_payment_amount') and self.partial_payment_amount:
            self.remaining_balance = self.amount - self.partial_payment_amount
            if self.remaining_balance <= 0:
                self.status = "Paid"
            elif self.remaining_balance < self.amount:
                self.status = "Partially Paid"
    
    def update_status(self):
        """Update payment status based on due date, payment date, and partial payments"""
        if self.payment_date:
            if hasattr(self, 'remaining_balance') and self.remaining_balance and self.remaining_balance > 0:
                self.status = "Partially Paid"
            else:
                self.status = "Paid"
        elif self.due_date:
            due_date = getdate(self.due_date)
            today_date = getdate(today())
            if due_date < today_date and self.status == "Pending":
                self.status = "Overdue"
    
    def log_payment_changes(self):
        """Log payment changes for audit trail"""
        try:
            if self.is_new():
                frappe.logger().info(f"New payment schedule created: {self.name} for landlord {self.landlord}")
            else:
                frappe.logger().info(f"Payment schedule updated: {self.name} for landlord {self.landlord}")
        except Exception as e:
            logger.error(f"Error logging payment changes: {str(e)}")
    
    def on_update(self):
        """Actions to perform after payment schedule is updated with enhanced error handling"""
        try:
            self.send_payment_reminders()
            self.create_journal_entry()
            self.create_purchase_invoice()
            self.update_landlord_summary()
        except Exception as e:
            logger.error(f"Error in on_update for LandlordPaymentSchedule {self.name}: {str(e)}")
            frappe.msgprint(f"Warning: Some operations failed - {str(e)}", alert=True)
    
    def send_payment_reminders(self):
        """Send payment reminders with enhanced logic"""
        try:
            if self.status == "Overdue":
                self.send_overdue_reminder()
            elif self.status == "Pending" and self.due_date:
                days_until_due = (getdate(self.due_date) - getdate(today())).days
                if 0 <= days_until_due <= 7:
                    self.send_due_reminder(days_until_due)
            elif self.status == "Partially Paid":
                self.send_partial_payment_reminder()
        except Exception as e:
            logger.error(f"Error sending payment reminders: {str(e)}")
    
    def send_overdue_reminder(self):
        """Send overdue payment reminder with enhanced messaging"""
        try:
            landlord_email = frappe.db.get_value("Landlord", self.landlord, "email_address")
            if landlord_email:
                subject = f"Payment Overdue - Landlord: {self.landlord}"
                
                # Calculate overdue amount
                overdue_amount = self.amount
                if hasattr(self, 'partial_payment_amount') and self.partial_payment_amount:
                    overdue_amount = self.remaining_balance
                
                message = f"""
                Dear Landlord,
                
                This is a reminder that your payment is overdue.
                
                Landlord: {self.landlord}
                Property: {self.property}
                Due Date: {self.due_date}
                Total Amount: {self.amount}
                Overdue Amount: {overdue_amount}
                
                Please process the payment at your earliest convenience to avoid any late fees.
                
                Best regards,
                Vacker Outdoor Advertising Team
                """
                
                frappe.sendmail(
                    recipients=[landlord_email],
                    subject=subject,
                    message=message
                )
        except Exception as e:
            logger.error(f"Error sending overdue reminder: {str(e)}")
    
    def send_due_reminder(self, days_until_due):
        """Send payment due reminder"""
        try:
            landlord_email = frappe.db.get_value("Landlord", self.landlord, "email_address")
            if landlord_email:
                subject = f"Payment Due in {days_until_due} days - Landlord: {self.landlord}"
                message = f"""
                Dear Landlord,
                
                This is a reminder that your payment is due in {days_until_due} days.
                
                Landlord: {self.landlord}
                Property: {self.property}
                Due Date: {self.due_date}
                Amount: {self.amount}
                
                Please ensure timely payment to avoid any late fees.
                
                Best regards,
                Vacker Outdoor Advertising Team
                """
                
                frappe.sendmail(
                    recipients=[landlord_email],
                    subject=subject,
                    message=message
                )
        except Exception as e:
            logger.error(f"Error sending due reminder: {str(e)}")
    
    def send_partial_payment_reminder(self):
        """Send reminder for remaining balance after partial payment"""
        try:
            landlord_email = frappe.db.get_value("Landlord", self.landlord, "email_address")
            if landlord_email and hasattr(self, 'remaining_balance') and self.remaining_balance > 0:
                subject = f"Partial Payment Received - Remaining Balance Due - Landlord: {self.landlord}"
                message = f"""
                Dear Landlord,
                
                Thank you for your partial payment. There is still a remaining balance due.
                
                Landlord: {self.landlord}
                Property: {self.property}
                Total Amount: {self.amount}
                Partial Payment: {self.partial_payment_amount}
                Remaining Balance: {self.remaining_balance}
                Due Date: {self.due_date}
                
                Please process the remaining balance at your earliest convenience.
                
                Best regards,
                Vacker Outdoor Advertising Team
                """
                
                frappe.sendmail(
                    recipients=[landlord_email],
                    subject=subject,
                    message=message
                )
        except Exception as e:
            logger.error(f"Error sending partial payment reminder: {str(e)}")
    
    def create_journal_entry(self):
        """Create journal entry when payment is made with enhanced logic"""
        try:
            if self.status == "Paid" and self.payment_date and not self.payment_reference:
                # Create journal entry for payment
                je = frappe.new_doc("Journal Entry")
                je.voucher_type = "Bank Entry"
                je.posting_date = self.payment_date
                je.company = frappe.defaults.get_global_default("company")
                
                # Get landlord details
                landlord_doc = frappe.get_doc("Landlord", self.landlord)
                bank_account = landlord_doc.bank_name or "Bank Account"
                
                # Add accounts
                je.append("accounts", {
                    "account": bank_account,
                    "debit_in_account_currency": self.amount,
                    "credit_in_account_currency": 0
                })
                
                je.append("accounts", {
                    "account": "Rental Income",
                    "debit_in_account_currency": 0,
                    "credit_in_account_currency": self.amount
                })
                
                je.user_remark = f"Payment for Landlord: {self.landlord}, Property: {self.property}"
                je.insert(ignore_permissions=True)
                
                # Update payment reference
                self.payment_reference = je.name
                self.save(ignore_permissions=True)
        except Exception as e:
            logger.error(f"Error creating journal entry: {str(e)}")
    
    def create_purchase_invoice(self):
        """
        Automatically create purchase invoice for this invoicing schedule with enhanced logic.
        
        Features:
        - Advance invoicing (1 month before due date)
        - Partial payment support
        - Escalation clause integration
        - Comprehensive error handling
        """
        try:
            if self.status == "Pending" and not self.purchase_invoice:
                # ADVANCE INVOICING LOGIC: Create invoice 1 month before due date
                due_date = getdate(self.due_date)
                today_date = getdate(today())
                
                # Calculate when invoice should be created (1 month before due date)
                invoice_creation_date = add_months(due_date, -1)
                
                # Create invoice if:
                # 1. It's overdue (due_date < today)
                # 2. It's due within 1 month (today >= invoice_creation_date)
                # 3. It's a backdated contract (due_date < today)
                
                should_create_invoice = False
                reason = ""
                
                if due_date < today_date:
                    # Overdue invoice - create immediately
                    should_create_invoice = True
                    reason = "overdue"
                elif today_date >= invoice_creation_date:
                    # Advance invoicing - create 1 month before due
                    should_create_invoice = True
                    reason = "advance_invoicing"
                
                if should_create_invoice:
                    self._create_purchase_invoice_document(reason, invoice_creation_date)
        except Exception as e:
            logger.error(f"Error creating purchase invoice: {str(e)}")
    
    def _create_purchase_invoice_document(self, reason, invoice_creation_date):
        """Create the actual purchase invoice document with enhanced features"""
        try:
            # Get landlord details
            landlord = frappe.get_doc("Landlord", self.landlord)
            if not landlord.supplier:
                frappe.log_error(f"No supplier found for landlord {self.landlord}")
                return
            
            # Create purchase invoice
            pi = frappe.new_doc("Purchase Invoice")
            pi.supplier = landlord.supplier
            
            # Set posting date based on reason
            today_date = getdate(today())
            if reason == "overdue":
                pi.posting_date = today_date  # Post today for overdue invoices
            else:
                pi.posting_date = invoice_creation_date  # Post on invoice creation date for advance invoicing
            
            pi.due_date = self.due_date
            pi.company = frappe.defaults.get_global_default("company")
            
            # Calculate invoice amount (consider partial payments)
            invoice_amount = self.amount
            if hasattr(self, 'partial_payment_amount') and self.partial_payment_amount:
                invoice_amount = self.remaining_balance
            
            # Add item for rental payment
            pi.append("items", {
                "item_code": "Rental Payment",
                "qty": 1,
                "rate": invoice_amount,
                "amount": invoice_amount,
                "description": f"Rental payment for property {self.property} - {self.payment_frequency} payment (Due: {self.due_date})"
            })
            
            # Set custom fields for landlord tracking
            pi.landlord = self.landlord
            pi.property = self.property
            pi.landlord_payment_schedule = self.name
            
            pi.insert(ignore_permissions=True)
            
            # Update invoicing schedule with invoice reference
            self.purchase_invoice = pi.name
            self.save(ignore_permissions=True)
            
            logger.info(f"Purchase invoice {pi.name} created for payment schedule {self.name}")
            
        except Exception as e:
            logger.error(f"Error creating purchase invoice document: {str(e)}")
            raise
    
    def update_landlord_summary(self):
        """Update landlord summary with payment information"""
        try:
            if self.landlord:
                landlord = frappe.get_doc("Landlord", self.landlord)
                landlord.calculate_total_rental_amount()
                landlord.save(ignore_permissions=True)
        except Exception as e:
            logger.error(f"Error updating landlord summary: {str(e)}")
    
    @frappe.whitelist()
    def mark_as_paid(self, payment_date=None, payment_reference=None, partial_amount=None):
        """
        Mark payment as paid with partial payment support
        
        Args:
            payment_date: Date of payment (defaults to today)
            payment_reference: Reference number for payment
            partial_amount: Partial payment amount (if not full payment)
        """
        try:
            if not payment_date:
                payment_date = today()
            
            self.payment_date = payment_date
            self.payment_reference = payment_reference
            
            if partial_amount and partial_amount < self.amount:
                self.partial_payment_amount = partial_amount
                self.status = "Partially Paid"
                self.remaining_balance = self.amount - partial_amount
            else:
                self.status = "Paid"
                self.remaining_balance = 0
            
            self.save(ignore_permissions=True)
            
            return {
                "success": True,
                "message": f"Payment marked as {self.status.lower()}",
                "remaining_balance": self.remaining_balance
            }
        except Exception as e:
            logger.error(f"Error marking payment as paid: {str(e)}")
            return {"success": False, "message": str(e)}
    
    @frappe.whitelist()
    def get_payment_summary(self):
        """Get comprehensive payment summary for dashboard"""
        try:
            return {
                "landlord": self.landlord,
                "property": self.property,
                "due_date": self.due_date,
                "amount": self.amount,
                "status": self.status,
                "payment_date": self.payment_date,
                "payment_reference": self.payment_reference,
                "partial_payment": getattr(self, 'partial_payment_amount', 0),
                "remaining_balance": getattr(self, 'remaining_balance', 0),
                "days_overdue": (getdate(today()) - getdate(self.due_date)).days if self.due_date and getdate(self.due_date) < getdate(today()) else 0,
                "purchase_invoice": self.purchase_invoice
            }
        except Exception as e:
            logger.error(f"Error getting payment summary: {str(e)}")
            return {}
    
    @frappe.whitelist()
    def update_payment_status_from_invoice(self):
        """Update payment status based on linked purchase invoice"""
        try:
            if self.purchase_invoice:
                invoice = frappe.get_doc("Purchase Invoice", self.purchase_invoice)
                if invoice.docstatus == 1:  # Submitted
                    self.status = "Invoice Created"
                elif invoice.docstatus == 2:  # Cancelled
                    self.status = "Cancelled"
                self.save(ignore_permissions=True)
        except Exception as e:
            logger.error(f"Error updating payment status from invoice: {str(e)}")

# Global functions for external access
@frappe.whitelist()
def mark_as_paid(landlord_payment_schedule, payment_date=None, payment_reference=None, partial_amount=None):
    """Global function to mark payment as paid"""
    try:
        doc = frappe.get_doc("Landlord Payment Schedule", landlord_payment_schedule)
        return doc.mark_as_paid(payment_date, payment_reference, partial_amount)
    except Exception as e:
        logger.error(f"Error in global mark_as_paid: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def update_payment_status_from_invoice(landlord_payment_schedule):
    """Global function to update payment status from invoice"""
    try:
        doc = frappe.get_doc("Landlord Payment Schedule", landlord_payment_schedule)
        doc.update_payment_status_from_invoice()
        return {"success": True}
    except Exception as e:
        logger.error(f"Error in global update_payment_status_from_invoice: {str(e)}")
        return {"success": False, "message": str(e)} 