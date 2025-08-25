import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, add_months, add_days
from frappe import _
import logging

# Configure logging
logger = logging.getLogger(__name__)

class LandlordProperty(Document):
    def validate(self):
        """Validate landlord property data with enhanced checks"""
        try:
            self.validate_contract_dates()
            self.validate_rental_amount()
            self.validate_overlapping_contracts()
            self.validate_partial_rental()
            self.auto_fetch_property_address()
            self.update_status()
            self.calculate_escalation_amount()
        except Exception as e:
            logger.error(f"Validation error in LandlordProperty {self.name}: {str(e)}")
            frappe.throw(_(f"Validation failed: {str(e)}"))
    
    def validate_contract_dates(self):
        """Validate contract start and end dates"""
        if self.contract_start_date and self.contract_end_date:
            if getdate(self.contract_end_date) <= getdate(self.contract_start_date):
                frappe.throw(_("Contract end date must be after start date"))
            
            # Add warning for backdated contracts but don't block them
            if getdate(self.contract_start_date) < getdate(today()):
                frappe.msgprint(
                    _("⚠️ Backdated contract detected. Retroactive invoicing will be generated for past periods."),
                    indicator="orange"
                )
    
    def validate_rental_amount(self):
        """Validate rental amount"""
        if self.rental_amount and self.rental_amount <= 0:
            frappe.throw(_("Rental amount must be greater than zero"))
    
    def validate_overlapping_contracts(self):
        """Validate that contracts don't overlap for the same property"""
        if not self.property or not self.contract_start_date or not self.contract_end_date:
            return
        
        # Get parent landlord
        parent_landlord = self.get_parent_landlord()
        if not parent_landlord:
            return
        
        # Check for overlapping contracts
        overlapping_contracts = frappe.db.sql("""
            SELECT lp.name, lp.contract_start_date, lp.contract_end_date
            FROM `tabLandlord Property` lp
            WHERE lp.parent = %s 
            AND lp.property = %s 
            AND lp.name != %s
            AND (
                (lp.contract_start_date <= %s AND lp.contract_end_date >= %s) OR
                (lp.contract_start_date <= %s AND lp.contract_end_date >= %s) OR
                (lp.contract_start_date >= %s AND lp.contract_end_date <= %s)
            )
        """, (
            parent_landlord, self.property, self.name or "NEW",
            self.contract_start_date, self.contract_start_date,
            self.contract_end_date, self.contract_end_date,
            self.contract_start_date, self.contract_end_date
        ))
        
        if overlapping_contracts:
            frappe.throw(_(
                "Contract overlaps with existing contract(s) for this property. "
                "Please adjust the contract dates or terminate existing contracts first."
            ))
    
    def validate_partial_rental(self):
        """Validate partial property rental settings"""
        if hasattr(self, 'rental_percentage') and self.rental_percentage:
            if self.rental_percentage <= 0 or self.rental_percentage > 100:
                frappe.throw(_("Rental percentage must be between 0 and 100"))
            
            # Adjust rental amount based on percentage
            if self.rental_amount and self.rental_percentage != 100:
                self.rental_amount = (self.rental_amount * self.rental_percentage) / 100
    
    def get_parent_landlord(self):
        """Get the parent landlord name"""
        for field in self.parent_fields:
            if field.fieldname == "parent":
                return self.get(field.fieldname)
        return None
    
    def auto_fetch_property_address(self):
        """Auto-fetch property address when property is selected"""
        if self.property and not self.property_address:
            try:
                property_doc = frappe.get_doc("Property", self.property)
                if property_doc.full_address:
                    self.property_address = property_doc.full_address
            except Exception as e:
                logger.error(f"Error fetching property address: {str(e)}")
    
    def update_status(self):
        """Update status based on contract dates"""
        if self.contract_end_date:
            end_date = getdate(self.contract_end_date)
            today_date = getdate(today())
            
            if end_date < today_date:
                self.status = "Expired"
            elif end_date == today_date:
                self.status = "Expired"
            else:
                self.status = "Active"
    
    def calculate_escalation_amount(self):
        """Calculate escalation amount based on escalation clause"""
        if hasattr(self, 'escalation_clause') and self.escalation_clause:
            try:
                # Parse escalation clause (example: "5% annually")
                if "annually" in self.escalation_clause.lower():
                    percentage = float(self.escalation_clause.split('%')[0])
                    self.escalation_percentage = percentage
                    self.escalation_frequency = "Annually"
                elif "monthly" in self.escalation_clause.lower():
                    percentage = float(self.escalation_clause.split('%')[0])
                    self.escalation_percentage = percentage
                    self.escalation_frequency = "Monthly"
                
                # Calculate escalated amount
                if hasattr(self, 'escalation_percentage') and self.escalation_percentage:
                    self.escalated_rental_amount = self.rental_amount * (1 + self.escalation_percentage / 100)
            except Exception as e:
                logger.error(f"Error calculating escalation: {str(e)}")
    
    def on_update(self):
        """Actions to perform after landlord property is updated"""
        try:
            self.update_property_status()
            self.create_invoicing_schedule()
            self.log_property_changes()
        except Exception as e:
            logger.error(f"Error in on_update for LandlordProperty {self.name}: {str(e)}")
    
    def update_property_status(self):
        """Update property status based on landlord property status"""
        if self.property:
            try:
                property_doc = frappe.get_doc("Property", self.property)
                if self.status == "Active":
                    property_doc.property_status = "Occupied"
                else:
                    property_doc.property_status = "Available"
                property_doc.save(ignore_permissions=True)
            except Exception as e:
                logger.error(f"Error updating property status: {str(e)}")
    
    def create_invoicing_schedule(self):
        """Create invoicing schedule for this property with enhanced logic"""
        if self.status == "Active" and self.rental_amount and self.payment_frequency:
            try:
                # Delete existing invoicing schedules for this property
                frappe.db.delete("Landlord Payment Schedule", {
                    "property": self.property,
                    "docstatus": 0
                })
                
                # Create new invoicing schedule
                self.generate_invoicing_schedule()
            except Exception as e:
                logger.error(f"Error creating invoicing schedule: {str(e)}")
    
    def generate_invoicing_schedule(self):
        """Generate invoicing schedule entries for this property with escalation support"""
        from frappe.utils import add_months, add_years
        
        start_date = getdate(self.contract_start_date)
        end_date = getdate(self.contract_end_date)
        current_date = start_date
        today_date = getdate(today())
        
        # Get the parent landlord
        parent_landlord = self.get_parent_landlord()
        
        retroactive_invoices = 0
        future_invoices = 0
        escalation_counter = 0
        
        while current_date <= end_date:
            # Calculate escalated amount if applicable
            current_amount = self.rental_amount
            if hasattr(self, 'escalation_percentage') and self.escalation_percentage:
                if self.escalation_frequency == "Annually":
                    years_elapsed = (current_date - start_date).days / 365
                    if years_elapsed >= escalation_counter + 1:
                        current_amount *= (1 + self.escalation_percentage / 100) ** (escalation_counter + 1)
                        escalation_counter += 1
                elif self.escalation_frequency == "Monthly":
                    months_elapsed = (current_date - start_date).days / 30
                    if months_elapsed >= escalation_counter + 1:
                        current_amount *= (1 + self.escalation_percentage / 100) ** (escalation_counter + 1)
                        escalation_counter += 1
            
            # Create invoicing schedule entry
            invoicing_schedule = frappe.new_doc("Landlord Payment Schedule")
            invoicing_schedule.landlord = parent_landlord
            invoicing_schedule.property = self.property
            invoicing_schedule.due_date = current_date
            invoicing_schedule.amount = current_amount
            invoicing_schedule.payment_frequency = self.payment_frequency
            invoicing_schedule.status = "Pending"
            
            # Handle backdated contracts - mark past invoices as overdue
            if current_date < today_date:
                invoicing_schedule.status = "Overdue"
                retroactive_invoices += 1
            else:
                future_invoices += 1
            
            invoicing_schedule.insert(ignore_permissions=True)
            
            # Calculate next invoicing date
            if self.payment_frequency == "Monthly":
                current_date = add_months(current_date, 1)
            elif self.payment_frequency == "Quarterly":
                current_date = add_months(current_date, 3)
            elif self.payment_frequency == "Annually":
                current_date = add_years(current_date, 1)
        
        # Show summary of generated invoices
        if retroactive_invoices > 0:
            frappe.msgprint(
                f"Generated {retroactive_invoices} retroactive invoices (overdue) and {future_invoices} future invoices for property {self.property}",
                indicator="orange"
            )
        else:
            frappe.msgprint(
                f"Generated {future_invoices} future invoices for property {self.property}",
                indicator="green"
            )
    
    def log_property_changes(self):
        """Log changes to property for audit trail"""
        try:
            if self.is_new():
                frappe.logger().info(f"New landlord property created: {self.name} for property {self.property}")
            else:
                frappe.logger().info(f"Landlord property updated: {self.name} for property {self.property}")
        except Exception as e:
            logger.error(f"Error logging property changes: {str(e)}")
    
    @frappe.whitelist()
    def get_property_summary(self):
        """Get comprehensive property summary for dashboard"""
        try:
            return {
                "property": self.property,
                "property_address": self.property_address,
                "media_type": self.media_type,
                "contract_period": {
                    "start_date": self.contract_start_date,
                    "end_date": self.contract_end_date
                },
                "financial": {
                    "rental_amount": self.rental_amount,
                    "payment_frequency": self.payment_frequency,
                    "escalated_amount": getattr(self, 'escalated_rental_amount', None),
                    "rental_percentage": getattr(self, 'rental_percentage', 100)
                },
                "status": self.status,
                "days_until_expiry": (getdate(self.contract_end_date) - getdate(today())).days if self.contract_end_date else None,
                "is_backdated": getdate(self.contract_start_date) < getdate(today()) if self.contract_start_date else False,
                "escalation_info": {
                    "clause": getattr(self, 'escalation_clause', None),
                    "percentage": getattr(self, 'escalation_percentage', None),
                    "frequency": getattr(self, 'escalation_frequency', None)
                }
            }
        except Exception as e:
            logger.error(f"Error getting property summary: {str(e)}")
            return {} 