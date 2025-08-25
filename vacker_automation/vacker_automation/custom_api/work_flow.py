import frappe
from frappe import _

def setup_purchase_invoice_custom_fields():
    """Setup custom fields for Purchase Invoice to link with landlord payment schedules"""
    try:
        # Check if custom field already exists
        if not frappe.db.exists("Custom Field", "Purchase Invoice-landlord"):
            custom_field = frappe.new_doc("Custom Field")
            custom_field.dt = "Purchase Invoice"
            custom_field.fieldname = "landlord"
            custom_field.label = "Landlord"
            custom_field.fieldtype = "Link"
            custom_field.options = "Landlord"
            custom_field.insert(ignore_permissions=True)
        
        if not frappe.db.exists("Custom Field", "Purchase Invoice-property"):
            custom_field = frappe.new_doc("Custom Field")
            custom_field.dt = "Purchase Invoice"
            custom_field.fieldname = "property"
            custom_field.label = "Property"
            custom_field.fieldtype = "Link"
            custom_field.options = "Property"
            custom_field.insert(ignore_permissions=True)
        
        if not frappe.db.exists("Custom Field", "Purchase Invoice-landlord_payment_schedule"):
            custom_field = frappe.new_doc("Custom Field")
            custom_field.dt = "Purchase Invoice"
            custom_field.fieldname = "landlord_payment_schedule"
            custom_field.label = "Landlord Payment Schedule"
            custom_field.fieldtype = "Link"
            custom_field.options = "Landlord Payment Schedule"
            custom_field.read_only = 1
            custom_field.insert(ignore_permissions=True)
        
        frappe.msgprint("Purchase Invoice custom fields setup completed successfully!")
        
    except Exception as e:
        frappe.log_error(f"Error setting up Purchase Invoice custom fields: {str(e)}")
        frappe.throw(f"Error setting up custom fields: {str(e)}")

def setup_supplier_group():
    """Setup Landlord supplier group if it doesn't exist"""
    try:
        if not frappe.db.exists("Supplier Group", "Landlord"):
            supplier_group = frappe.new_doc("Supplier Group")
            supplier_group.supplier_group_name = "Landlord"
            supplier_group.parent_supplier_group = "All Supplier Groups"
            supplier_group.insert(ignore_permissions=True)
            frappe.msgprint("Landlord supplier group created successfully!")
        else:
            frappe.msgprint("Landlord supplier group already exists!")
            
    except Exception as e:
        frappe.log_error(f"Error setting up supplier group: {str(e)}")
        frappe.throw(f"Error setting up supplier group: {str(e)}")

def ensure_rental_payment_item():
    """Ensure the Rental Payment item exists"""
    try:
        if not frappe.db.exists("Item", "Rental Payment"):
            # Create the Rental Payment item
            item = frappe.new_doc("Item")
            item.item_code = "Rental Payment"
            item.item_name = "Rental Payment"
            item.item_group = "Services"
            item.stock_uom = "Nos"
            item.is_stock_item = 0
            item.is_purchase_item = 1
            item.is_sales_item = 0
            item.description = "Rental payment for outdoor advertising properties"
            item.insert(ignore_permissions=True)
            print(f"✅ Created Rental Payment item: {item.name}")
        else:
            print(f"✅ Rental Payment item already exists")
            
    except Exception as e:
        print(f"❌ Error creating Rental Payment item: {str(e)}")

@frappe.whitelist()
def setup_landlord_integration():
    """Setup all landlord integration components"""
    try:
        setup_supplier_group()
        ensure_rental_payment_item()
        setup_purchase_invoice_custom_fields()
        
        return {
            "success": True,
            "message": "Landlord integration setup completed successfully!"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error in setup: {str(e)}"
        }

@frappe.whitelist()
def create_invoices_for_due_payments():
    """Scheduled job to create purchase invoices for invoicing schedules with advance invoicing logic"""
    try:
        from frappe.utils import getdate, today, add_days, add_months
        
        # Get invoicing schedules that need invoices created
        # 1. Overdue schedules (due_date < today)
        # 2. Schedules due within 1 month (advance invoicing)
        # 3. Don't have invoices yet
        
        today_date = getdate(today())
        one_month_from_now = add_months(today_date, 1)
        
        due_schedules = frappe.get_all("Landlord Payment Schedule", 
            filters={
                "status": "Pending",
                "purchase_invoice": ["is", "null"],
                "due_date": ["<=", one_month_from_now]  # Due within 1 month or overdue
            },
            fields=["name", "landlord", "property", "due_date", "amount", "payment_frequency"]
        )
        
        created_invoices = []
        errors = []
        advance_invoices = 0
        overdue_invoices = 0
        
        for schedule in due_schedules:
            try:
                # Get the invoicing schedule document
                schedule_doc = frappe.get_doc("Landlord Payment Schedule", schedule.name)
                
                # Check if it should create an invoice
                due_date = getdate(schedule.due_date)
                invoice_creation_date = add_months(due_date, -1)
                
                should_create = False
                invoice_type = ""
                
                if due_date < today_date:
                    # Overdue - create immediately
                    should_create = True
                    invoice_type = "overdue"
                elif today_date >= invoice_creation_date:
                    # Advance invoicing - create 1 month before due
                    should_create = True
                    invoice_type = "advance"
                
                if should_create:
                    # Trigger invoice creation
                    schedule_doc.create_purchase_invoice()
                    created_invoices.append(schedule.name)
                    
                    if invoice_type == "overdue":
                        overdue_invoices += 1
                    else:
                        advance_invoices += 1
                    
            except Exception as e:
                error_msg = f"Error creating invoice for schedule {schedule.name}: {str(e)}"
                errors.append(error_msg)
                frappe.log_error(error_msg)
        
        # Log the results
        if created_invoices:
            frappe.logger().info(f"Created {len(created_invoices)} purchase invoices: {advance_invoices} advance invoices, {overdue_invoices} overdue invoices")
        
        if errors:
            frappe.logger().error(f"Errors in invoice creation: {errors}")
        
        return {
            "success": True,
            "created_invoices": len(created_invoices),
            "advance_invoices": advance_invoices,
            "overdue_invoices": overdue_invoices,
            "errors": len(errors),
            "message": f"Processed {len(due_schedules)} invoicing schedules. Created {len(created_invoices)} invoices ({advance_invoices} advance, {overdue_invoices} overdue) with {len(errors)} errors."
        }
        
    except Exception as e:
        frappe.log_error(f"Error in create_invoices_for_due_payments: {str(e)}")
        return {
            "success": False,
            "message": f"Error in scheduled job: {str(e)}"
        }

@frappe.whitelist()
def create_invoice_for_specific_schedule(schedule_name):
    """Manually create invoice for a specific invoicing schedule"""
    try:
        schedule_doc = frappe.get_doc("Landlord Payment Schedule", schedule_name)
        
        if schedule_doc.status != "Pending":
            return {"success": False, "message": "Invoicing schedule is not in Pending status"}
        
        if schedule_doc.purchase_invoice:
            return {"success": False, "message": "Purchase invoice already exists for this schedule"}
        
        # Create the invoice
        schedule_doc.create_purchase_invoice()
        
        return {
            "success": True,
            "message": f"Purchase invoice created successfully for invoicing schedule {schedule_name}"
        }
        
    except Exception as e:
        frappe.log_error(f"Error creating invoice for schedule {schedule_name}: {str(e)}")
        return {
            "success": False,
            "message": f"Error creating invoice: {str(e)}"
        }

@frappe.whitelist()
def handle_backdated_contracts():
    """Special function to handle backdated contracts and create retroactive invoices"""
    try:
        from frappe.utils import getdate, today
        
        # Find landlords with backdated contracts
        backdated_landlords = frappe.db.sql("""
            SELECT DISTINCT l.name, l.full_legal_name
            FROM `tabLandlord` l
            JOIN `tabLandlord Property` lp ON l.name = lp.parent
            WHERE l.docstatus = 1
            AND lp.contract_start_date < %s
            AND lp.status = 'Active'
        """, today(), as_dict=1)
        
        processed_landlords = 0
        total_retroactive_invoices = 0
        
        for landlord in backdated_landlords:
            try:
                landlord_doc = frappe.get_doc("Landlord", landlord.name)
                
                # Generate invoicing schedules for backdated contracts
                result = landlord_doc.generate_invoicing_schedules()
                
                if result.get("success"):
                    processed_landlords += 1
                    # Count retroactive invoices
                    retroactive_count = result.get("retroactive_count", 0)
                    total_retroactive_invoices += retroactive_count
                    
            except Exception as e:
                frappe.log_error(f"Error processing backdated contract for landlord {landlord.name}: {str(e)}")
        
        return {
            "success": True,
            "processed_landlords": processed_landlords,
            "total_retroactive_invoices": total_retroactive_invoices,
            "message": f"Processed {processed_landlords} landlords with backdated contracts. Created {total_retroactive_invoices} retroactive invoices."
        }
        
    except Exception as e:
        frappe.log_error(f"Error in handle_backdated_contracts: {str(e)}")
        return {
            "success": False,
            "message": f"Error processing backdated contracts: {str(e)}"
        }

@frappe.whitelist()
def setup_automatic_invoice_creation():
    """Setup scheduled job for automatic invoice creation"""
    try:
        # Check if the scheduled job already exists
        existing_job = frappe.db.exists("Scheduled Job Type", "vacker_automation.vacker_automation.custom_api.work_flow.create_invoices_for_due_payments")
        
        if not existing_job:
            # Create the scheduled job
            job = frappe.new_doc("Scheduled Job Type")
            job.method = "vacker_automation.vacker_automation.custom_api.work_flow.create_invoices_for_due_payments"
            job.frequency = "Daily"  # Run daily to check for due payments
            job.cron_format = "0 9 * * *"  # Run at 9 AM daily
            job.insert()
            print(f"✅ Created scheduled job: {job.name}")
        else:
            print(f"✅ Scheduled job already exists: {existing_job}")
        
        print("🎉 Automatic invoice creation setup completed!")
        print("📋 Summary:")
        print("• Scheduled job runs daily at 9 AM")
        print("• Creates invoices for payment schedules due within 3 days")
        print("• Posting date is set to the due date")
        print("• Manual execution available via 'Create Invoices for Due Payments' button")
        print("• Individual schedule invoices can be created manually")
        
        return {
            "success": True,
            "message": "Automatic invoice creation setup completed successfully!"
        }
        
    except Exception as e:
        frappe.log_error(f"Error setting up automatic invoice creation: {str(e)}")
        return {
            "success": False,
            "message": f"Error in setup: {str(e)}"
        }

@frappe.whitelist()
def create_suppliers_for_all_landlords():
    """Create suppliers for all landlords that don't have one"""
    try:
        # Get all submitted landlords without suppliers
        landlords = frappe.get_all("Landlord", 
            filters={
                "docstatus": 1,
                "supplier": ["is", "null"]
            },
            fields=["name", "landlord_id", "full_legal_name"]
        )
        
        created_suppliers = []
        errors = []
        
        for landlord in landlords:
            try:
                landlord_doc = frappe.get_doc("Landlord", landlord.name)
                landlord_doc.create_or_update_supplier()
                created_suppliers.append(landlord.name)
                print(f"✅ Created supplier for landlord: {landlord.landlord_id}")
                
            except Exception as e:
                error_msg = f"Error creating supplier for landlord {landlord.name}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
                frappe.log_error(error_msg)
        
        message = f"Created suppliers for {len(created_suppliers)} landlords"
        if errors:
            message += f". Errors: {len(errors)}"
        
        return {
            "success": True,
            "created_suppliers": len(created_suppliers),
            "errors": len(errors),
            "message": message
        }
        
    except Exception as e:
        frappe.log_error(f"Error in create_suppliers_for_all_landlords: {str(e)}")
        return {
            "success": False,
            "message": f"Error in bulk supplier creation: {str(e)}"
        }

@frappe.whitelist()
def create_customer_invoices_for_due_payments():
    """Scheduled job to create sales invoices for customer invoicing schedules with advance invoicing logic"""
    try:
        from frappe.utils import getdate, today, add_days, add_months
        
        # Get customer invoicing schedules that need invoices created
        # 1. Overdue schedules (due_date < today)
        # 2. Schedules due within 1 month (advance invoicing)
        # 3. Don't have invoices yet
        
        today_date = getdate(today())
        one_month_from_now = add_months(today_date, 1)
        
        due_schedules = frappe.get_all("Customer Invoicing Schedule", 
            filters={
                "status": ["in", ["Pending", "Overdue"]],
                "sales_invoice": ["is", "null"]
            },
            fields=["name", "customer", "media_installation", "property", "due_date", "amount"]
        )
        
        invoices_created = 0
        overdue_invoices = 0
        advance_invoices = 0
        
        for schedule in due_schedules:
            try:
                due_date = getdate(schedule.due_date)
                
                # Calculate when invoice should be created (1 month before due date)
                invoice_creation_date = add_months(due_date, -1)
                
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
                    # Get customer details
                    customer = frappe.get_doc("Customer", schedule.customer)
                    
                    # Create sales invoice
                    si = frappe.new_doc("Sales Invoice")
                    si.customer = schedule.customer
                    
                    # Set posting date based on reason
                    if reason == "overdue":
                        si.posting_date = today_date  # Post today for overdue invoices
                    else:
                        si.posting_date = invoice_creation_date  # Post on invoice creation date for advance invoicing
                    
                    si.due_date = schedule.due_date
                    si.company = frappe.defaults.get_global_default("company")
                    
                    # Add item for media rental
                    si.append("items", {
                        "item_code": "Media Rental",
                        "qty": 1,
                        "rate": schedule.amount,
                        "amount": schedule.amount,
                        "description": f"Media rental for installation {schedule.media_installation} - Property: {schedule.property} (Due: {schedule.due_date})"
                    })
                    
                    # Set custom fields for tracking
                    si.media_installation = schedule.media_installation
                    si.property = schedule.property
                    si.customer_invoicing_schedule = schedule.name
                    
                    si.insert(ignore_permissions=True)
                    
                    # Update customer invoicing schedule with invoice reference
                    customer_schedule = frappe.get_doc("Customer Invoicing Schedule", schedule.name)
                    customer_schedule.sales_invoice = si.name
                    customer_schedule.invoice_date = si.posting_date
                    customer_schedule.status = "Invoice Created"
                    customer_schedule.save(ignore_permissions=True)
                    
                    invoices_created += 1
                    
                    if reason == "overdue":
                        overdue_invoices += 1
                    else:
                        advance_invoices += 1
                    
                    frappe.logger().info(f"Created sales invoice {si.name} for customer invoicing schedule {schedule.name} ({reason})")
                
            except Exception as e:
                frappe.logger().error(f"Error creating sales invoice for customer invoicing schedule {schedule.name}: {str(e)}")
                continue
        
        # Log summary
        if invoices_created > 0:
            frappe.logger().info(f"Customer invoicing job completed: {invoices_created} invoices created ({overdue_invoices} overdue, {advance_invoices} advance)")
        
        return {
            "success": True,
            "message": f"Customer invoicing job completed successfully. {invoices_created} invoices created ({overdue_invoices} overdue, {advance_invoices} advance)",
            "invoices_created": invoices_created,
            "overdue_invoices": overdue_invoices,
            "advance_invoices": advance_invoices
        }
        
    except Exception as e:
        frappe.logger().error(f"Error in customer invoicing job: {str(e)}")
        return {
            "success": False,
            "message": f"Error in customer invoicing job: {str(e)}"
        }

@frappe.whitelist()
def get_media_installation_summary():
    """Get comprehensive summary of media installations with project and customer information"""
    try:
        # Get all media installations
        installations = frappe.get_all("Media Installation",
            fields=["name", "installation_id", "landlord", "property", "customer", "customer_name", 
                   "project", "project_name", "rental_start_date", "rental_end_date", "rental_amount", 
                   "rental_frequency", "rental_status", "installation_status"]
        )
        
        # Get customer invoicing schedules
        customer_schedules = frappe.get_all("Customer Invoicing Schedule",
            fields=["media_installation", "status", "amount"]
        )
        
        # Get sales invoices
        sales_invoices = frappe.get_all("Sales Invoice",
            filters={"media_installation": ["is", "set"]},
            fields=["media_installation", "grand_total", "status"]
        )
        
        # Calculate statistics
        total_installations = len(installations)
        active_rentals = len([i for i in installations if i.rental_status == "Active"])
        completed_installations = len([i for i in installations if i.installation_status == "Completed"])
        
        # Calculate total revenue
        total_revenue = sum([inv.grand_total or 0 for inv in sales_invoices])
        
        # Group by project
        projects = {}
        for installation in installations:
            if installation.project:
                if installation.project not in projects:
                    projects[installation.project] = {
                        "project_name": installation.project_name,
                        "installations": [],
                        "total_revenue": 0
                    }
                projects[installation.project]["installations"].append(installation)
        
        # Group by customer
        customers = {}
        for installation in installations:
            if installation.customer:
                if installation.customer not in customers:
                    customers[installation.customer] = {
                        "customer_name": installation.customer_name,
                        "installations": [],
                        "total_revenue": 0
                    }
                customers[installation.customer]["installations"].append(installation)
        
        return {
            "success": True,
            "summary": {
                "total_installations": total_installations,
                "active_rentals": active_rentals,
                "completed_installations": completed_installations,
                "total_revenue": total_revenue,
                "projects": projects,
                "customers": customers
            }
        }
        
    except Exception as e:
        frappe.logger().error(f"Error getting media installation summary: {str(e)}")
        return {
            "success": False,
            "message": f"Error getting media installation summary: {str(e)}"
        }

@frappe.whitelist()
def get_property_rental_analytics(property_name=None):
    """Get rental analytics for properties"""
    try:
        filters = {}
        if property_name:
            filters["property"] = property_name
        
        # Get all media installations for the property
        installations = frappe.get_all("Media Installation",
            filters=filters,
            fields=["name", "property", "customer", "customer_name", "rental_start_date", 
                   "rental_end_date", "rental_amount", "rental_frequency", "rental_status"]
        )
        
        # Calculate analytics
        total_rentals = len(installations)
        active_rentals = len([i for i in installations if i.rental_status == "Active"])
        completed_rentals = len([i for i in installations if i.rental_status == "Completed"])
        
        # Calculate total revenue
        total_revenue = 0
        for installation in installations:
            if installation.rental_amount:
                start_date = getdate(installation.rental_start_date) if installation.rental_start_date else None
                end_date = getdate(installation.rental_end_date) if installation.rental_end_date else None
                
                if start_date and end_date:
                    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                    
                    if installation.rental_frequency == "Monthly":
                        total_revenue += installation.rental_amount * max(1, months)
                    elif installation.rental_frequency == "Quarterly":
                        total_revenue += installation.rental_amount * max(1, months // 3)
                    elif installation.rental_frequency == "Annually":
                        total_revenue += installation.rental_amount * max(1, months // 12)
                    else:  # One-time
                        total_revenue += installation.rental_amount
        
        # Get unique customers
        unique_customers = len(set([i.customer for i in installations if i.customer]))
        
        return {
            "success": True,
            "analytics": {
                "property": property_name or "All Properties",
                "total_rentals": total_rentals,
                "active_rentals": active_rentals,
                "completed_rentals": completed_rentals,
                "total_revenue": total_revenue,
                "unique_customers": unique_customers,
                "installations": installations
            }
        }
        
    except Exception as e:
        frappe.logger().error(f"Error getting property rental analytics: {str(e)}")
        return {
            "success": False,
            "message": f"Error getting property rental analytics: {str(e)}"
        } 