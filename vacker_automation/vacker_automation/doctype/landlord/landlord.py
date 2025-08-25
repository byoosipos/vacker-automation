import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, add_days, add_months, add_years
from frappe import _
import re

class Landlord(Document):
    def autoname(self):
        """Auto-generate landlord ID based on naming series"""
        if not self.landlord_id:
            self.landlord_id = frappe.model.naming.make_autoname("LAND-.YYYY.-.#####")
    
    def validate(self):
        """Validate landlord data"""
        self.validate_contact_information()
        self.validate_payment_information()
        self.validate_email_format()
        self.validate_phone_numbers()
        self.calculate_total_rental_amount()
    
    def validate_contact_information(self):
        """Validate that at least one contact method is provided"""
        if not self.primary_phone and not self.email_address:
            frappe.throw(_("Either primary phone or email address is required"))
    
    def validate_payment_information(self):
        """Validate payment method and banking details"""
        if self.payment_method == "Bank Transfer":
            if not self.bank_name or not self.account_number:
                frappe.throw(_("Bank name and account number are required for bank transfer"))
    
    def validate_email_format(self):
        """Validate email format"""
        if self.email_address:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.email_address):
                frappe.throw(_("Please enter a valid email address"))
    
    def validate_phone_numbers(self):
        """Validate phone number formats"""
        if self.primary_phone:
            # Remove spaces, dashes, parentheses, and plus signs for validation
            phone_clean = re.sub(r'[\s\-\(\)\+]', '', self.primary_phone)
            if not phone_clean.isdigit() or len(phone_clean) < 8:
                frappe.throw(_("Please enter a valid primary phone number (minimum 8 digits)"))
        
        if self.secondary_phone:
            # Remove spaces, dashes, parentheses, and plus signs for validation
            phone_clean = re.sub(r'[\s\-\(\)\+]', '', self.secondary_phone)
            if not phone_clean.isdigit() or len(phone_clean) < 8:
                frappe.throw(_("Please enter a valid secondary phone number (minimum 8 digits)"))
    
    def calculate_total_rental_amount(self):
        """Calculate total rental amount from all properties"""
        total_amount = 0
        if self.properties:
            for property_item in self.properties:
                if property_item.rental_amount and property_item.status == "Active":
                    total_amount += property_item.rental_amount
        self.rental_amount = total_amount
    
    def on_update(self):
        """Actions to perform after landlord is updated"""
        # Only update property status if not already in a property update cycle
        if not frappe.local.flags.get('updating_property_status'):
            frappe.local.flags.updating_property_status = True
            try:
                self.update_property_status()
            finally:
                frappe.local.flags.updating_property_status = False
        
        # Create supplier if it doesn't exist and has required fields
        if not self.supplier and self.landlord_id and self.full_legal_name:
            self.create_or_update_supplier()
        
        self.create_payment_schedule()
        self.send_notifications()
    
    def update_property_status(self):
        """Update property status based on landlord status"""
        if self.properties:
            for property_item in self.properties:
                try:
                    property_doc = frappe.get_doc("Property", property_item.property)
                    if self.docstatus == 1:  # Submitted
                        property_doc.property_status = "Occupied"
                    else:
                        property_doc.property_status = "Available"
                    property_doc.save(ignore_permissions=True)
                except Exception as e:
                    frappe.log_error(f"Error updating property {property_item.property}: {str(e)}")
    
    def create_payment_schedule(self):
        """Create invoicing schedule based on payment frequency"""
        if self.docstatus == 1 and self.properties:
            # Delete existing invoicing schedules
            frappe.db.delete("Landlord Payment Schedule", {
                "landlord": self.name,
                "docstatus": 0
            })
            
            # Create new invoicing schedules for all properties
            for property_item in self.properties:
                if property_item.status == "Active":
                    self._generate_invoicing_schedule_for_property(property_item)
    
    def _generate_payment_schedule(self):
        """Internal method to generate payment schedule entries - DEPRECATED"""
        # This method is deprecated - use _generate_invoicing_schedule_for_property instead
        frappe.throw("This method is deprecated. Use generate_invoicing_schedules() instead.")
    
    @frappe.whitelist()
    def generate_payment_schedule(self):
        """Generate invoicing schedule entries - Frontend accessible method"""
        try:
            return self.generate_invoicing_schedules()
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def send_notifications(self):
        """Send notifications based on landlord status"""
        if self.docstatus == 1:
            # Send welcome notification
            self.send_welcome_notification()
            
            # Send contract expiry reminders for all properties
            if self.properties:
                for property_item in self.properties:
                    if property_item.contract_end_date:
                        days_until_expiry = (getdate(property_item.contract_end_date) - getdate(today())).days
                        if 0 <= days_until_expiry <= 90:
                            self.send_contract_expiry_reminder(property_item, days_until_expiry)
    
    @frappe.whitelist()
    def send_welcome_notification(self):
        """Send welcome notification to landlord"""
        if self.email_address:
            subject = f"Welcome to Vacker Outdoor Advertising - Landlord ID: {self.landlord_id}"
            
            # Build property list
            property_list = ""
            if self.properties:
                for property_item in self.properties:
                    property_list += f"\n- {property_item.property}: {property_item.rental_amount}"
            
            message = f"""
            Dear {self.full_legal_name},
            
            Welcome to Vacker Outdoor Advertising! Your landlord account has been successfully created.
            
            Landlord ID: {self.landlord_id}
            Properties: {property_list}
            Total Rental Amount: {self.rental_amount}
            
            We look forward to a successful partnership.
            
            Best regards,
            Vacker Outdoor Advertising Team
            """
            
            frappe.sendmail(
                recipients=[self.email_address],
                subject=subject,
                message=message
            )
    
    @frappe.whitelist()
    def send_contract_expiry_reminder(self, property_item, days_until_expiry):
        """Send contract expiry reminder for specific property"""
        if self.email_address:
            subject = f"Contract Expiry Reminder - {property_item.property} - {days_until_expiry} days remaining"
            message = f"""
            Dear {self.full_legal_name},
            
            This is a reminder that your contract for property {property_item.property} will expire in {days_until_expiry} days.
            
            Landlord ID: {self.landlord_id}
            Property: {property_item.property}
            Contract End Date: {property_item.contract_end_date}
            
            Please contact us to discuss contract renewal options.
            
            Best regards,
            Vacker Outdoor Advertising Team
            """
            
            frappe.sendmail(
                recipients=[self.email_address],
                subject=subject,
                message=message
            )
    
    @frappe.whitelist()
    def get_landlord_summary(self):
        """Get comprehensive landlord summary for dashboard"""
        properties_summary = []
        if self.properties:
            for property_item in self.properties:
                properties_summary.append({
                    "property": property_item.property,
                    "property_address": property_item.property_address,
                    "media_type": property_item.media_type,
                    "rental_amount": property_item.rental_amount,
                    "status": property_item.status,
                    "contract_end_date": property_item.contract_end_date
                })
        
        return {
            "landlord_id": self.landlord_id,
            "full_legal_name": self.full_legal_name,
            "landlord_type": self.landlord_type,
            "properties": properties_summary,
            "financial": {
                "total_rental_amount": self.rental_amount,
                "commission_percentage": self.commission_percentage
            },
            "contact": {
                "primary_phone": self.primary_phone,
                "email_address": self.email_address,
                "preferred_communication": self.preferred_communication
            },
            "status": self.docstatus,
            "total_properties": len(properties_summary) if properties_summary else 0,
            "active_properties": len([p for p in properties_summary if p.get("status") == "Active"]) if properties_summary else 0
        }
    
    @frappe.whitelist()
    def calculate_annual_revenue(self):
        """Calculate annual revenue for this landlord from all properties"""
        total_annual_revenue = 0
        
        if self.properties:
            for property_item in self.properties:
                if property_item.rental_amount and property_item.status == "Active":
                    if property_item.payment_frequency == "Monthly":
                        total_annual_revenue += property_item.rental_amount * 12
                    elif property_item.payment_frequency == "Quarterly":
                        total_annual_revenue += property_item.rental_amount * 4
                    elif property_item.payment_frequency == "Annually":
                        total_annual_revenue += property_item.rental_amount
        
        return total_annual_revenue
    
    @frappe.whitelist()
    def generate_invoicing_schedules(self):
        """Generate invoicing schedules for all properties with advance invoicing logic"""
        try:
            if not self.properties:
                return {"success": False, "message": "No properties found for this landlord"}
            
            generated_count = 0
            errors = []
            retroactive_count = 0
            
            for property_item in self.properties:
                try:
                    if property_item.status == "Active":
                        # Check if invoicing schedules already exist for this property
                        existing_schedules = frappe.db.count("Landlord Payment Schedule", {
                            "landlord": self.name,
                            "property": property_item.property,
                            "docstatus": 0
                        })
                        
                        if existing_schedules > 0:
                            # Delete existing schedules first
                            frappe.db.delete("Landlord Payment Schedule", {
                                "landlord": self.name,
                                "property": property_item.property,
                                "docstatus": 0
                            })
                        
                        # Validate required fields
                        if not property_item.contract_start_date:
                            errors.append(f"Property {property_item.property}: Contract start date is required")
                            continue
                        if not property_item.contract_end_date:
                            errors.append(f"Property {property_item.property}: Contract end date is required")
                            continue
                        if not property_item.rental_amount:
                            errors.append(f"Property {property_item.property}: Rental amount is required")
                            continue
                        if not property_item.payment_frequency:
                            errors.append(f"Property {property_item.property}: Payment frequency is required")
                            continue
                        
                        # Create invoicing schedule for this property
                        result = self._generate_invoicing_schedule_for_property(property_item)
                        generated_count += result.get("generated", 0)
                        retroactive_count += result.get("retroactive", 0)
                    else:
                        errors.append(f"Property {property_item.property}: Skipped (status is not Active)")
                        
                except Exception as e:
                    error_msg = f"Property {property_item.property}: {str(e)}"
                    errors.append(error_msg)
                    frappe.log_error(str(e)[:120], f"Error generating invoicing schedule for property {property_item.property}")
            
            if generated_count > 0:
                message = f"Successfully generated {generated_count} invoicing schedules"
                if retroactive_count > 0:
                    message += f" ({retroactive_count} retroactive invoices for backdated contracts)"
                if errors:
                    message += f". Errors: {'; '.join(errors)}"
                return {"success": True, "message": message}
            else:
                return {"success": False, "message": f"No invoicing schedules generated. Errors: {'; '.join(errors)}"}
                
        except Exception as e:
            frappe.log_error(str(e)[:120], f"Error in generate_invoicing_schedules for landlord {self.name}")
            return {"success": False, "message": f"Failed to generate invoicing schedules: {str(e)}"}
    
    @frappe.whitelist()
    def get_payment_schedule_summary(self):
        """Get invoicing schedule summary for this landlord"""
        try:
            from frappe.utils import getdate, today
            
            # Get invoicing schedules for this landlord
            schedules = frappe.get_all("Landlord Payment Schedule",
                filters={"landlord": self.name},
                fields=["name", "property", "due_date", "amount", "status", "purchase_invoice"]
            )
            
            total_schedules = len(schedules)
            pending_schedules = len([s for s in schedules if s.status == "Pending"])
            invoice_created_schedules = len([s for s in schedules if s.status == "Invoice Created"])
            paid_schedules = len([s for s in schedules if s.status == "Paid"])
            
            # Calculate overdue schedules
            today_date = getdate(today())
            overdue_schedules = len([s for s in schedules if s.due_date and getdate(s.due_date) < today_date and s.status != "Paid"])
            
            # Get recent schedules (last 10)
            recent_schedules = schedules[:10] if len(schedules) > 10 else schedules
            
            return {
                "success": True,
                "total_schedules": total_schedules,
                "pending_schedules": pending_schedules,
                "invoice_created_schedules": invoice_created_schedules,
                "paid_schedules": paid_schedules,
                "overdue_schedules": overdue_schedules,
                "recent_schedules": recent_schedules
            }
            
        except Exception as e:
            frappe.log_error(f"Error getting invoicing schedule summary for landlord {self.name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_invoicing_schedule_for_property(self, property_item):
        """Generate invoicing schedule entries for a specific property with advance invoicing"""
        try:
            # Validate required fields
            if not property_item.contract_start_date:
                frappe.throw(f"Contract start date is required for property {property_item.property}")
            if not property_item.contract_end_date:
                frappe.throw(f"Contract end date is required for property {property_item.property}")
            if not property_item.rental_amount:
                frappe.throw(f"Rental amount is required for property {property_item.property}")
            if not property_item.payment_frequency:
                frappe.throw(f"Payment frequency is required for property {property_item.property}")
            
            # Delete existing invoicing schedules for this property
            frappe.db.delete("Landlord Payment Schedule", {
                "landlord": self.name,
                "property": property_item.property,
                "docstatus": 0
            })
            
            # Calculate invoicing dates with advance invoicing logic
            start_date = getdate(property_item.contract_start_date)
            end_date = getdate(property_item.contract_end_date)
            current_date = start_date
            today_date = getdate(today())
            schedule_count = 0
            retroactive_count = 0
            
            while current_date <= end_date:
                # Create invoicing schedule entry
                invoicing_schedule = frappe.new_doc("Landlord Payment Schedule")
                invoicing_schedule.landlord = self.name
                invoicing_schedule.property = property_item.property
                invoicing_schedule.due_date = current_date
                invoicing_schedule.amount = property_item.rental_amount
                invoicing_schedule.payment_frequency = property_item.payment_frequency
                invoicing_schedule.status = "Pending"
                
                # Handle backdated contracts - mark past invoices as overdue
                if current_date < today_date:
                    invoicing_schedule.status = "Overdue"
                    retroactive_count += 1
                
                invoicing_schedule.insert(ignore_permissions=True)
                schedule_count += 1
                
                # Calculate next invoicing date
                if property_item.payment_frequency == "Monthly":
                    current_date = add_months(current_date, 1)
                elif property_item.payment_frequency == "Quarterly":
                    current_date = add_months(current_date, 3)
                elif property_item.payment_frequency == "Annually":
                    current_date = add_months(current_date, 12)
            
            if retroactive_count > 0:
                frappe.msgprint(f"Generated {schedule_count} invoicing schedules for property {property_item.property} ({retroactive_count} retroactive invoices for backdated contract)")
            else:
                frappe.msgprint(f"Generated {schedule_count} invoicing schedules for property {property_item.property}")
            
            return {"generated": schedule_count, "retroactive": retroactive_count}
            
        except Exception as e:
            frappe.log_error(f"Error generating invoicing schedule for property {property_item.property}: {str(e)}")
            frappe.throw(f"Error generating invoicing schedule for property {property_item.property}: {str(e)}")
    
    def create_or_update_supplier(self):
        """Create or update supplier record for this landlord"""
        try:
            # Validate required fields
            if not self.landlord_id:
                print("❌ Landlord ID is required to create supplier")
                return
            
            if not self.full_legal_name:
                print("❌ Full legal name is required to create supplier")
                return
            
            # Check if supplier already exists using full legal name
            supplier_name = self.full_legal_name
            existing_supplier = frappe.db.exists("Supplier", {"supplier_name": supplier_name})
            
            if existing_supplier:
                # Update existing supplier
                supplier = frappe.get_doc("Supplier", existing_supplier)
                print(f"Updating existing supplier: {supplier.name}")
            else:
                # Create new supplier
                supplier = frappe.new_doc("Supplier")
                supplier.supplier_name = supplier_name
                supplier.supplier_type = "Individual"  # Use Individual instead of Landlord
                print(f"Creating new supplier: {supplier_name}")
            
            # Update supplier details
            supplier.supplier_group = "Landlord"
            supplier.country = "Uganda"  # Set default country
            supplier.supplier_details = f"Landlord ID: {self.landlord_id}\nFull Name: {self.full_legal_name}"
            
            # Set contact details
            if self.primary_phone:
                supplier.mobile_no = self.primary_phone
            if self.email_address:
                supplier.email_id = self.email_address
            
            # Set address
            if self.physical_address:
                supplier.address = self.physical_address
            
            # Set company details if available
            if hasattr(self, 'company_entity_name') and self.company_entity_name:
                supplier.supplier_name = self.company_entity_name
                supplier.supplier_type = "Company"  # Change to Company if company name is provided
                supplier.supplier_details = f"Landlord ID: {self.landlord_id}\nCompany: {self.company_entity_name}\nContact: {self.full_legal_name}"
            
            supplier.save(ignore_permissions=True)
            
            # Store supplier reference in landlord
            if not self.supplier:
                self.supplier = supplier.name
                self.save(ignore_permissions=True)
                print(f"Supplier reference updated in landlord: {supplier.name}")
            
            print(f"✅ Supplier {supplier.name} created/updated successfully for landlord {self.landlord_id}")
            
        except Exception as e:
            print(f"❌ Error creating supplier for landlord {self.name}: {str(e)}")
            frappe.log_error(f"Error creating supplier for landlord {self.name}: {str(e)}")
            raise e
    
    @frappe.whitelist()
    def create_purchase_invoices_from_schedules(self):
        """Create purchase invoices from pending payment schedules"""
        try:
            if not self.supplier:
                return {"success": False, "message": "No supplier found for this landlord. Please ensure the landlord is submitted first."}
            
            # Get pending payment schedules
            pending_schedules = frappe.get_all("Landlord Payment Schedule", 
                filters={
                    "landlord": self.name,
                    "status": "Pending",
                    "docstatus": 0
                },
                fields=["name", "property", "due_date", "amount", "payment_frequency"]
            )
            
            if not pending_schedules:
                return {"success": False, "message": "No pending payment schedules found for this landlord."}
            
            created_invoices = []
            errors = []
            
            for schedule in pending_schedules:
                try:
                    # Create purchase invoice
                    pi = frappe.new_doc("Purchase Invoice")
                    pi.supplier = self.supplier
                    pi.posting_date = schedule.due_date
                    pi.due_date = schedule.due_date
                    pi.company = frappe.defaults.get_global_default("company")
                    
                    # Add item for rental payment
                    pi.append("items", {
                        "item_code": "Rental Payment",  # You may need to create this item
                        "qty": 1,
                        "rate": schedule.amount,
                        "amount": schedule.amount,
                        "description": f"Rental payment for property {schedule.property} - {schedule.payment_frequency} payment"
                    })
                    
                    # Set reference to payment schedule
                    pi.landlord_payment_schedule = schedule.name
                    pi.landlord = self.name
                    pi.property = schedule.property
                    
                    pi.insert(ignore_permissions=True)
                    created_invoices.append(pi.name)
                    
                    # Update payment schedule status
                    schedule_doc = frappe.get_doc("Landlord Payment Schedule", schedule.name)
                    schedule_doc.status = "Invoice Created"
                    schedule_doc.purchase_invoice = pi.name
                    schedule_doc.save(ignore_permissions=True)
                    
                except Exception as e:
                    error_msg = f"Error creating invoice for schedule {schedule.name}: {str(e)}"
                    errors.append(error_msg)
                    frappe.log_error(error_msg)
            
            if created_invoices:
                message = f"Successfully created {len(created_invoices)} purchase invoice(s): {', '.join(created_invoices)}"
                if errors:
                    message += f"\nErrors: {'; '.join(errors)}"
                return {"success": True, "message": message, "invoices": created_invoices}
            else:
                return {"success": False, "message": f"No invoices created. Errors: {'; '.join(errors)}"}
                
        except Exception as e:
            frappe.log_error(f"Error in create_purchase_invoices_from_schedules for landlord {self.name}: {str(e)}")
            return {"success": False, "message": f"Failed to create purchase invoices: {str(e)}"}
    
    @frappe.whitelist()
    def get_purchase_invoice_summary(self):
        """Get summary of purchase invoices for this landlord"""
        try:
            invoices = frappe.get_all("Purchase Invoice", 
                filters={"landlord": self.name},
                fields=["name", "posting_date", "due_date", "grand_total", "status", "property"],
                order_by="posting_date desc"
            )
            
            summary = {
                "total_invoices": len(invoices),
                "draft_invoices": len([i for i in invoices if i.status == "Draft"]),
                "submitted_invoices": len([i for i in invoices if i.status == "Submitted"]),
                "paid_invoices": len([i for i in invoices if i.status == "Paid"]),
                "total_amount": sum(i.grand_total for i in invoices),
                "recent_invoices": invoices[:5]  # Last 5 invoices
            }
            
            return summary
            
        except Exception as e:
            frappe.log_error(f"Error getting purchase invoice summary for landlord {self.name}: {str(e)}")
            return {"error": str(e)}
    
    @frappe.whitelist()
    def create_supplier_manually(self):
        """Manually create supplier for this landlord"""
        try:
            if self.supplier:
                return {"success": False, "message": f"Supplier already exists: {self.supplier}"}
            
            self.create_or_update_supplier()
            
            return {
                "success": True,
                "message": f"Supplier created successfully: {self.supplier}"
            }
            
        except Exception as e:
            frappe.log_error(f"Error creating supplier manually for landlord {self.name}: {str(e)}")
            return {
                "success": False,
                "message": f"Error creating supplier: {str(e)}"
            }
    
    @frappe.whitelist()
    def update_all_payment_schedules(self):
        """Update all payment schedules for this landlord based on invoice status"""
        try:
            # Get all payment schedules for this landlord that have invoices
            schedules = frappe.get_all("Landlord Payment Schedule",
                filters={
                    "landlord": self.name,
                    "purchase_invoice": ["is", "not null"],
                    "status": ["!=", "Paid"]
                },
                fields=["name", "purchase_invoice", "status"]
            )
            
            updated_count = 0
            errors = []
            
            for schedule in schedules:
                try:
                    schedule_doc = frappe.get_doc("Landlord Payment Schedule", schedule.name)
                    result = schedule_doc.update_payment_status_from_invoice()
                    
                    if result.get("success"):
                        updated_count += 1
                    else:
                        errors.append(f"Schedule {schedule.name}: {result.get('message')}")
                        
                except Exception as e:
                    error_msg = f"Error updating schedule {schedule.name}: {str(e)}"
                    errors.append(error_msg)
                    frappe.log_error(error_msg)
            
            message = f"Updated {updated_count} payment schedules"
            if errors:
                message += f". Errors: {len(errors)}"
            
            return {
                "success": True,
                "updated_count": updated_count,
                "errors": len(errors),
                "message": message
            }
            
        except Exception as e:
            frappe.log_error(f"Error updating payment schedules for landlord {self.name}: {str(e)}")
            return {
                "success": False,
                "message": f"Error updating payment schedules: {str(e)}"
            } 