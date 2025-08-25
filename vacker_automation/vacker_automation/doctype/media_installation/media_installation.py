import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, add_months, add_days
from frappe import _

class MediaInstallation(Document):
    def autoname(self):
        """Auto-generate installation ID based on naming series"""
        if not self.installation_id:
            self.installation_id = frappe.model.naming.make_autoname("INST-.YYYY.-.#####")
    
    def validate(self):
        """Validate installation data"""
        self.validate_installation_date()
        self.validate_landlord_property_consistency()
        self.validate_maintenance_schedule()
        self.fetch_media_type_from_landlord()
        self.auto_fetch_names()
        self.validate_rental_dates()
        self.calculate_total_revenue()
        self.update_customer_invoicing_schedules_info()
    
    def validate_installation_date(self):
        """Validate installation date"""
        if self.installation_date:
            installation_date = getdate(self.installation_date)
            today_date = getdate(today())
            if installation_date < today_date:
                frappe.msgprint(_("⚠️ Installation date is in the past. This is allowed for retroactive installations."), indicator="orange")
    
    def validate_landlord_property_consistency(self):
        """Validate that landlord and property are consistent"""
        if self.landlord and self.property:
            # Check if the landlord has an active contract for this property in the child table
            landlord_property_exists = frappe.db.exists("Landlord Property", {
                "parent": self.landlord,
                "property": self.property,
                "status": "Active"
            })
            
            if not landlord_property_exists:
                frappe.throw(_("Selected landlord does not have an active contract for this property. Please ensure the landlord has an active property contract."))
    
    def validate_rental_dates(self):
        """Validate rental start and end dates"""
        if self.rental_start_date and self.rental_end_date:
            if getdate(self.rental_end_date) <= getdate(self.rental_start_date):
                frappe.throw(_("Rental end date must be after start date"))
    
    def auto_fetch_names(self):
        """Auto-fetch project and customer names"""
        if self.project and not self.project_name:
            project_name = frappe.db.get_value("Project", self.project, "project_name")
            if project_name:
                self.project_name = project_name
        
        if self.customer and not self.customer_name:
            customer_name = frappe.db.get_value("Customer", self.customer, "customer_name")
            if customer_name:
                self.customer_name = customer_name
    
    def update_customer_invoicing_schedules_info(self):
        """Update the HTML field with customer invoicing schedules information"""
        if not self.name:  # Document not saved yet
            return
            
        # Get customer invoicing schedules for this installation
        schedules = frappe.get_all("Customer Invoicing Schedule", 
            filters={"media_installation": self.name},
            fields=["name", "due_date", "amount", "status", "sales_invoice", "payment_date"],
            order_by="due_date"
        )
        
        if not schedules:
            self.customer_invoicing_schedules_info = """
                <div class="alert alert-info">
                    <strong>No Customer Invoicing Schedules Found</strong><br>
                    Customer invoicing schedules will be automatically generated when the installation is completed.
                </div>
            """
            return
        
        # Create HTML table with schedules
        html_content = f"""
            <div class="customer-invoicing-schedules">
                <h5>Customer Invoicing Schedules ({len(schedules)} total)</h5>
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
        """
        
        for schedule in schedules:
            status_color = self._get_schedule_status_color(schedule.status)
            invoice_link = f'<a href="/app/sales-invoice/{schedule.sales_invoice}" target="_blank">{schedule.sales_invoice}</a>' if schedule.sales_invoice else '-'
            payment_date = schedule.payment_date or '-'
            
            html_content += f"""
                <tr>
                    <td><a href="/app/customer-invoicing-schedule/{schedule.name}" target="_blank">{schedule.name}</a></td>
                    <td>{schedule.due_date}</td>
                    <td>{frappe.format(schedule.amount, {'fieldtype': 'Currency'})}</td>
                    <td><span class="label label-{status_color}">{schedule.status}</span></td>
                    <td>{invoice_link}</td>
                    <td>{payment_date}</td>
                </tr>
            """
        
        html_content += """
                        </tbody>
                    </table>
                </div>
                <div class="mt-3">
                    <small class="text-muted">
                        <strong>Note:</strong> Sales invoices are automatically created 1 month before the due date (advance invoicing).
                    </small>
                </div>
            </div>
        """
        
        self.customer_invoicing_schedules_info = html_content
    
    def _get_schedule_status_color(self, status):
        """Get Bootstrap color class for schedule status"""
        status_colors = {
            'Pending': 'default',
            'Invoice Created': 'info',
            'Paid': 'success',
            'Overdue': 'danger',
            'Cancelled': 'warning'
        }
        return status_colors.get(status, 'default')
    
    def calculate_total_revenue(self):
        """Calculate total revenue for rental history entries"""
        if self.rental_history:
            total_revenue = 0
            for rental in self.rental_history:
                if rental.total_revenue:
                    total_revenue += rental.total_revenue
                else:
                    # Calculate revenue based on rental period and amount
                    if rental.rental_start_date and rental.rental_end_date and rental.rental_amount:
                        start_date = getdate(rental.rental_start_date)
                        end_date = getdate(rental.rental_end_date)
                        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                        if rental.rental_frequency == "Monthly":
                            rental.total_revenue = rental.rental_amount * max(1, months)
                        elif rental.rental_frequency == "Quarterly":
                            rental.total_revenue = rental.rental_amount * max(1, months // 3)
                        elif rental.rental_frequency == "Annually":
                            rental.total_revenue = rental.rental_amount * max(1, months // 12)
                        else:  # One-time
                            rental.total_revenue = rental.rental_amount
                        total_revenue += rental.total_revenue
    
    def validate_maintenance_schedule(self):
        """Validate maintenance schedule and calculate next maintenance date"""
        if self.installation_date and self.maintenance_schedule:
            if self.maintenance_schedule == "Monthly":
                self.next_maintenance_date = add_months(getdate(self.installation_date), 1)
            elif self.maintenance_schedule == "Quarterly":
                self.next_maintenance_date = add_months(getdate(self.installation_date), 3)
            elif self.maintenance_schedule == "Bi-annually":
                self.next_maintenance_date = add_months(getdate(self.installation_date), 6)
            elif self.maintenance_schedule == "As Needed":
                self.next_maintenance_date = None
    
    def fetch_media_type_from_landlord(self):
        """Fetch media type from landlord property record"""
        if self.landlord and self.property and not self.media_type:
            # Get media type from the specific property in the landlord's child table
            media_type = frappe.db.get_value("Landlord Property", {
                "parent": self.landlord,
                "property": self.property
            }, "media_type")
            
            if media_type:
                self.media_type = media_type
    
    def on_update(self):
        """Actions to perform after installation is updated"""
        # Check if this update is triggered by a maintenance schedule to prevent circular dependency
        if frappe.flags.in_maintenance_update:
            return
            
        self.update_installation_status()
        self.create_maintenance_schedule()
        self.create_customer_invoicing_schedule()
        self.update_rental_history()
        self.send_notifications()
    
    def update_installation_status(self):
        """Update installation status and related records"""
        if self.installation_status == "Completed":
            # Update property status if needed
            if self.property:
                property_doc = frappe.get_doc("Property", self.property)
                if property_doc.property_status == "Under Maintenance":
                    property_doc.property_status = "Occupied"
                    property_doc.save(ignore_permissions=True)
        
        elif self.installation_status == "Maintenance Required":
            # Update property status to under maintenance
            if self.property:
                property_doc = frappe.get_doc("Property", self.property)
                property_doc.property_status = "Under Maintenance"
                property_doc.save(ignore_permissions=True)
    
    def create_customer_invoicing_schedule(self):
        """Create customer invoicing schedule for this installation"""
        # Prevent creating customer invoicing schedules if:
        # 1. This is triggered by a maintenance update (circular dependency)
        # 2. Installation is not completed
        # 3. Required fields are missing
        if (frappe.flags.in_maintenance_update or
            self.installation_status != "Completed" or
            not self.customer or 
            not self.rental_start_date or 
            not self.rental_end_date or 
            not self.rental_amount or 
            not self.rental_frequency):
            return
            
        # Delete existing customer invoicing schedules
        frappe.db.delete("Customer Invoicing Schedule", {
            "media_installation": self.name,
            "docstatus": 0
        })
        
        # Generate customer invoicing schedule
        self._generate_customer_invoicing_schedule()
    
    def _generate_customer_invoicing_schedule(self):
        """Internal method to generate customer invoicing schedule entries"""
        if not self.rental_start_date or not self.rental_end_date or not self.rental_amount:
            return
        
        start_date = getdate(self.rental_start_date)
        end_date = getdate(self.rental_end_date)
        current_date = start_date
        today_date = getdate(today())
        
        retroactive_invoices = 0
        future_invoices = 0
        
        while current_date <= end_date:
            # Create customer invoicing schedule entry
            customer_schedule = frappe.new_doc("Customer Invoicing Schedule")
            customer_schedule.customer = self.customer
            customer_schedule.media_installation = self.name
            customer_schedule.property = self.property
            customer_schedule.due_date = current_date
            customer_schedule.amount = self.rental_amount
            customer_schedule.status = "Pending"
            
            # Handle backdated rentals - mark past invoices as overdue
            if current_date < today_date:
                customer_schedule.status = "Overdue"
                retroactive_invoices += 1
            else:
                future_invoices += 1
            
            customer_schedule.insert(ignore_permissions=True)
            
            # Calculate next invoicing date
            if self.rental_frequency == "Monthly":
                current_date = add_months(current_date, 1)
            elif self.rental_frequency == "Quarterly":
                current_date = add_months(current_date, 3)
            elif self.rental_frequency == "Annually":
                current_date = add_months(current_date, 12)
            elif self.rental_frequency == "One-time":
                break  # Only one invoice for one-time rentals
        
        # Show summary of generated invoices
        if retroactive_invoices > 0:
            frappe.msgprint(
                f"Generated {retroactive_invoices} retroactive customer invoices (overdue) and {future_invoices} future invoices for installation {self.installation_id}",
                indicator="orange"
            )
        else:
            frappe.msgprint(
                f"Generated {future_invoices} future customer invoices for installation {self.installation_id}",
                indicator="green"
            )
    
    def update_rental_history(self):
        """Update rental history for this installation"""
        # Prevent updating rental history if:
        # 1. This is triggered by a maintenance update (circular dependency)
        # 2. Required fields are missing
        if (frappe.flags.in_maintenance_update or
            not self.customer or 
            not self.rental_start_date or 
            not self.rental_end_date or 
            not self.rental_amount):
            return
            
        # Check if this rental already exists in history
        existing_rental = None
        if self.rental_history:
            for rental in self.rental_history:
                if (rental.customer == self.customer and 
                    rental.rental_start_date == self.rental_start_date and
                    rental.rental_end_date == self.rental_end_date):
                    existing_rental = rental
                    break
        
        if not existing_rental:
            # Add new rental to history
            new_rental = self.append("rental_history")
            new_rental.customer = self.customer
            new_rental.customer_name = self.customer_name
            new_rental.rental_start_date = self.rental_start_date
            new_rental.rental_end_date = self.rental_end_date
            new_rental.rental_amount = self.rental_amount
            new_rental.rental_frequency = self.rental_frequency
            new_rental.rental_status = self.rental_status
            
            # Calculate total revenue
            start_date = getdate(self.rental_start_date)
            end_date = getdate(self.rental_end_date)
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            
            if self.rental_frequency == "Monthly":
                new_rental.total_revenue = self.rental_amount * max(1, months)
            elif self.rental_frequency == "Quarterly":
                new_rental.total_revenue = self.rental_amount * max(1, months // 3)
            elif self.rental_frequency == "Annually":
                new_rental.total_revenue = self.rental_amount * max(1, months // 12)
            else:  # One-time
                new_rental.total_revenue = self.rental_amount
    
    def create_maintenance_schedule(self):
        """Create maintenance schedule entries"""
        # Prevent creating maintenance schedules if:
        # 1. This is triggered by a maintenance update (circular dependency)
        # 2. Installation is not completed
        # 3. Maintenance schedule is "As Needed"
        if (frappe.flags.in_maintenance_update or 
            self.installation_status != "Completed" or 
            self.maintenance_schedule == "As Needed"):
            return
            
        # Delete existing maintenance schedules for this installation
        frappe.db.delete("Maintenance Schedule", {
            "media_installation": self.name,
            "docstatus": 0
        })
        
        # Create new maintenance schedule
        self.generate_maintenance_schedule()
    
    def generate_maintenance_schedule(self):
        """Generate maintenance schedule entries"""
        if not self.installation_date or not self.maintenance_schedule:
            return
        
        start_date = getdate(self.installation_date)
        current_date = start_date
        
        # Generate maintenance schedule for 2 years
        for i in range(24):  # 24 months
            if self.maintenance_schedule == "Monthly":
                current_date = add_months(start_date, i + 1)
            elif self.maintenance_schedule == "Quarterly":
                if (i + 1) % 3 == 0:
                    current_date = add_months(start_date, i + 1)
                else:
                    continue
            elif self.maintenance_schedule == "Bi-annually":
                if (i + 1) % 6 == 0:
                    current_date = add_months(start_date, i + 1)
                else:
                    continue
            
            # Create maintenance schedule entry
            maintenance_schedule = frappe.new_doc("Maintenance Schedule")
            maintenance_schedule.media_installation = self.name
            maintenance_schedule.landlord = self.landlord
            maintenance_schedule.property = self.property
            maintenance_schedule.scheduled_date = current_date
            maintenance_schedule.maintenance_type = "Routine"
            maintenance_schedule.status = "Scheduled"
            maintenance_schedule.insert(ignore_permissions=True)
    
    def send_notifications(self):
        """Send notifications based on installation status"""
        if self.installation_status == "Completed":
            self.send_completion_notification()
        elif self.installation_status == "Maintenance Required":
            self.send_maintenance_notification()
    
    def send_completion_notification(self):
        """Send installation completion notification"""
        if self.landlord:
            landlord_email = frappe.db.get_value("Landlord", self.landlord, "email_address")
            if landlord_email:
                subject = f"Media Installation Completed - Installation ID: {self.installation_id}"
                message = f"""
                Dear Landlord,
                
                The media installation at your property has been completed successfully.
                
                Installation ID: {self.installation_id}
                Property: {self.property}
                Installation Date: {self.installation_date}
                Media Type: {self.media_type}
                Customer: {self.customer_name}
                Project: {self.project_name}
                
                Thank you for your cooperation.
                
                Best regards,
                Vacker Outdoor Advertising Team
                """
                
                frappe.sendmail(
                    recipients=[landlord_email],
                    subject=subject,
                    message=message
                )
        
        # Send notification to customer
        if self.customer:
            customer_email = frappe.db.get_value("Customer", self.customer, "email_id")
            if customer_email:
                subject = f"Media Installation Completed - Installation ID: {self.installation_id}"
                message = f"""
                Dear Customer,
                
                Your media installation has been completed successfully.
                
                Installation ID: {self.installation_id}
                Property: {self.property}
                Installation Date: {self.installation_date}
                Media Type: {self.media_type}
                Project: {self.project_name}
                Rental Period: {self.rental_start_date} to {self.rental_end_date}
                Rental Amount: {self.rental_amount}
                
                Your advertising campaign is now live!
                
                Best regards,
                Vacker Outdoor Advertising Team
                """
                
                frappe.sendmail(
                    recipients=[customer_email],
                    subject=subject,
                    message=message
                )
    
    def send_maintenance_notification(self):
        """Send maintenance required notification"""
        if self.landlord:
            landlord_email = frappe.db.get_value("Landlord", self.landlord, "email_address")
            if landlord_email:
                subject = f"Maintenance Required - Installation ID: {self.installation_id}"
                message = f"""
                Dear Landlord,
                
                Maintenance is required for the media installation at your property.
                
                Installation ID: {self.installation_id}
                Property: {self.property}
                Issue: {self.installation_notes or 'Maintenance required'}
                
                Our team will contact you shortly to schedule the maintenance.
                
                Best regards,
                Vacker Outdoor Advertising Team
                """
                
                frappe.sendmail(
                    recipients=[landlord_email],
                    subject=subject,
                    message=message
                )
    
    @frappe.whitelist()
    def get_installation_summary(self):
        """Get comprehensive installation summary"""
        return {
            "installation_id": self.installation_id,
            "landlord": self.landlord,
            "property": self.property,
            "media_type": self.media_type,
            "installation_date": self.installation_date,
            "status": self.installation_status,
            "cost": self.installation_cost,
            "maintenance_schedule": self.maintenance_schedule,
            "next_maintenance_date": self.next_maintenance_date,
            "notes": self.installation_notes,
            "project": self.project,
            "project_name": self.project_name,
            "customer": self.customer,
            "customer_name": self.customer_name,
            "rental_period": {
                "start_date": self.rental_start_date,
                "end_date": self.rental_end_date,
                "amount": self.rental_amount,
                "frequency": self.rental_frequency,
                "status": self.rental_status
            }
        }
    
    @frappe.whitelist()
    def get_property_rental_history(self):
        """Get rental history for this property across all installations"""
        installations = frappe.get_all("Media Installation", 
            filters={"property": self.property},
            fields=["name", "customer", "customer_name", "rental_start_date", "rental_end_date", "rental_amount", "rental_frequency", "rental_status"]
        )
        
        rental_history = []
        for installation in installations:
            rental_history.append({
                "installation": installation.name,
                "customer": installation.customer,
                "customer_name": installation.customer_name,
                "rental_start_date": installation.rental_start_date,
                "rental_end_date": installation.rental_end_date,
                "rental_amount": installation.rental_amount,
                "rental_frequency": installation.rental_frequency,
                "rental_status": installation.rental_status
            })
        
        return {
            "property": self.property,
            "total_rentals": len(rental_history),
            "rental_history": rental_history
        }
    
    @frappe.whitelist()
    def schedule_maintenance(self, maintenance_date, maintenance_type="Routine"):
        """Schedule maintenance for this installation"""
        if not maintenance_date:
            frappe.throw(_("Maintenance date is required"))
        
        maintenance_schedule = frappe.new_doc("Maintenance Schedule")
        maintenance_schedule.media_installation = self.name
        maintenance_schedule.landlord = self.landlord
        maintenance_schedule.property = self.property
        maintenance_schedule.scheduled_date = maintenance_date
        maintenance_schedule.maintenance_type = maintenance_type
        maintenance_schedule.status = "Scheduled"
        maintenance_schedule.insert(ignore_permissions=True)
        
        return maintenance_schedule.name
    
    def generate_customer_invoicing_schedule(self):
        """Generate customer invoicing schedule for this installation"""
        try:
            if not self.customer or not self.rental_start_date or not self.rental_end_date or not self.rental_amount:
                return {
                    "success": False,
                    "message": "Missing required information: customer, rental dates, or rental amount"
                }
            # Delete existing customer invoicing schedules
            frappe.db.delete("Customer Invoicing Schedule", {
                "media_installation": self.name,
                "docstatus": 0
            })
            # Generate new customer invoicing schedule
            self._generate_customer_invoicing_schedule()
            return {
                "success": True,
                "message": "Customer invoicing schedules generated successfully"
            }
        except Exception as e:
            frappe.logger().error(f"Error generating customer invoicing schedule: {str(e)}")
            return {
                "success": False,
                "message": f"Error generating customer invoicing schedule: {str(e)}"
            }

@frappe.whitelist()
def generate_customer_invoicing_schedule(media_installation):
    doc = frappe.get_doc("Media Installation", media_installation)
    return doc.generate_customer_invoicing_schedule() 