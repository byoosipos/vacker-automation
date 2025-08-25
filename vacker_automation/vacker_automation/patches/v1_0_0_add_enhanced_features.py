# Copyright (c) 2025, Vacker and Contributors
# See license.txt

import frappe
from frappe.utils import getdate, today
import logging

# Configure logging
logger = logging.getLogger(__name__)

def execute():
    """Execute database migration for enhanced features"""
    try:
        logger.info("Starting Vacker Automation v1.0.0 migration...")
        
        # Add new fields to existing doctypes
        add_new_fields_to_landlord_property()
        add_new_fields_to_landlord_payment_schedule()
        add_new_fields_to_property()
        add_new_fields_to_maintenance_schedule()
        
        # Create new doctypes if they don't exist
        create_maintenance_history_doctype()
        create_ai_settings_doctype()
        
        # Update existing data
        update_existing_data()
        
        # Create indexes for performance
        create_database_indexes()
        
        logger.info("Vacker Automation v1.0.0 migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        frappe.throw(f"Migration failed: {str(e)}")

def add_new_fields_to_landlord_property():
    """Add new fields to Landlord Property child table"""
    try:
        logger.info("Adding new fields to Landlord Property...")
        
        # Check if fields already exist
        existing_fields = frappe.get_meta("Landlord Property").fields
        field_names = [f.fieldname for f in existing_fields]
        
        new_fields = [
            {
                "fieldname": "rental_percentage",
                "fieldtype": "Percent",
                "label": "Rental Percentage",
                "default": "100",
                "description": "Percentage of property being rented (100% = full property)"
            },
            {
                "fieldname": "escalation_clause",
                "fieldtype": "Text",
                "label": "Escalation Clause",
                "description": "e.g., 5% annually, 3% monthly"
            },
            {
                "fieldname": "escalation_percentage",
                "fieldtype": "Percent",
                "label": "Escalation Percentage",
                "read_only": 1
            },
            {
                "fieldname": "escalation_frequency",
                "fieldtype": "Select",
                "label": "Escalation Frequency",
                "options": "Monthly\nAnnually",
                "read_only": 1
            },
            {
                "fieldname": "escalated_rental_amount",
                "fieldtype": "Currency",
                "label": "Escalated Rental Amount",
                "precision": "2",
                "read_only": 1
            },
            {
                "fieldname": "rental_area",
                "fieldtype": "Float",
                "label": "Rental Area",
                "description": "Area being rented (in square units)"
            },
            {
                "fieldname": "rental_area_unit",
                "fieldtype": "Select",
                "label": "Area Unit",
                "options": "sq ft\nsq m\nacres\nhectares"
            }
        ]
        
        for field in new_fields:
            if field["fieldname"] not in field_names:
                frappe.db.sql(f"""
                    ALTER TABLE `tabLandlord Property` 
                    ADD COLUMN `{field['fieldname']}` {get_field_type_sql(field)}
                """)
                logger.info(f"Added field {field['fieldname']} to Landlord Property")
        
    except Exception as e:
        logger.error(f"Error adding fields to Landlord Property: {str(e)}")
        raise

def add_new_fields_to_landlord_payment_schedule():
    """Add new fields to Landlord Payment Schedule"""
    try:
        logger.info("Adding new fields to Landlord Payment Schedule...")
        
        # Check if fields already exist
        existing_fields = frappe.get_meta("Landlord Payment Schedule").fields
        field_names = [f.fieldname for f in existing_fields]
        
        new_fields = [
            {
                "fieldname": "partial_payment_amount",
                "fieldtype": "Currency",
                "label": "Partial Payment Amount",
                "precision": "2",
                "description": "Amount paid if not full payment"
            },
            {
                "fieldname": "remaining_balance",
                "fieldtype": "Currency",
                "label": "Remaining Balance",
                "precision": "2",
                "read_only": 1
            },
            {
                "fieldname": "notes",
                "fieldtype": "Text",
                "label": "Notes"
            }
        ]
        
        for field in new_fields:
            if field["fieldname"] not in field_names:
                frappe.db.sql(f"""
                    ALTER TABLE `tabLandlord Payment Schedule` 
                    ADD COLUMN `{field['fieldname']}` {get_field_type_sql(field)}
                """)
                logger.info(f"Added field {field['fieldname']} to Landlord Payment Schedule")
        
        # Update status options
        frappe.db.sql("""
            UPDATE `tabDocField` 
            SET options = 'Pending\nInvoice Created\nPaid\nPartially Paid\nOverdue\nCancelled'
            WHERE parent = 'Landlord Payment Schedule' AND fieldname = 'status'
        """)
        
    except Exception as e:
        logger.error(f"Error adding fields to Landlord Payment Schedule: {str(e)}")
        raise

def add_new_fields_to_property():
    """Add new fields to Property doctype"""
    try:
        logger.info("Adding new fields to Property...")
        
        # Check if fields already exist
        existing_fields = frappe.get_meta("Property").fields
        field_names = [f.fieldname for f in existing_fields]
        
        new_fields = [
            {
                "fieldname": "property_category",
                "fieldtype": "Select",
                "label": "Property Category",
                "options": "Billboard\nDigital Display\nTransit\nStreet Furniture\nBuilding Wrap\nOther"
            },
            {
                "fieldname": "compliance_status",
                "fieldtype": "Select",
                "label": "Compliance Status",
                "options": "Compliant\nNon-Compliant\nUnder Review\nPending Approval"
            },
            {
                "fieldname": "calculated_value",
                "fieldtype": "Currency",
                "label": "Calculated Value",
                "precision": "2",
                "read_only": 1
            },
            {
                "fieldname": "market_value",
                "fieldtype": "Currency",
                "label": "Market Value",
                "precision": "2"
            },
            {
                "fieldname": "last_valuation_date",
                "fieldtype": "Date",
                "label": "Last Valuation Date"
            },
            {
                "fieldname": "mapping_data",
                "fieldtype": "Code",
                "label": "Mapping Data",
                "read_only": 1,
                "hidden": 1
            }
        ]
        
        for field in new_fields:
            if field["fieldname"] not in field_names:
                frappe.db.sql(f"""
                    ALTER TABLE `tabProperty` 
                    ADD COLUMN `{field['fieldname']}` {get_field_type_sql(field)}
                """)
                logger.info(f"Added field {field['fieldname']} to Property")
        
    except Exception as e:
        logger.error(f"Error adding fields to Property: {str(e)}")
        raise

def add_new_fields_to_maintenance_schedule():
    """Add new fields to Maintenance Schedule"""
    try:
        logger.info("Adding new fields to Maintenance Schedule...")
        
        # Check if fields already exist
        existing_fields = frappe.get_meta("Maintenance Schedule").fields
        field_names = [f.fieldname for f in existing_fields]
        
        new_fields = [
            {
                "fieldname": "assigned_technician",
                "fieldtype": "Link",
                "label": "Assigned Technician",
                "options": "Employee"
            },
            {
                "fieldname": "technician_name",
                "fieldtype": "Data",
                "label": "Technician Name",
                "read_only": 1
            },
            {
                "fieldname": "estimated_cost",
                "fieldtype": "Currency",
                "label": "Estimated Cost",
                "precision": 2
            },
            {
                "fieldname": "reschedule_reason",
                "fieldtype": "Text",
                "label": "Reschedule Reason"
            },
            {
                "fieldname": "check_technician_availability",
                "fieldtype": "Check",
                "label": "Check Technician Availability",
                "default": 1
            }
        ]
        
        for field in new_fields:
            if field["fieldname"] not in field_names:
                frappe.db.sql(f"""
                    ALTER TABLE `tabMaintenance Schedule` 
                    ADD COLUMN `{field['fieldname']}` {get_field_type_sql(field)}
                """)
                logger.info(f"Added field {field['fieldname']} to Maintenance Schedule")
        
    except Exception as e:
        logger.error(f"Error adding fields to Maintenance Schedule: {str(e)}")
        raise

def create_maintenance_history_doctype():
    """Create Maintenance History doctype if it doesn't exist"""
    try:
        if not frappe.db.exists("DocType", "Maintenance History"):
            logger.info("Creating Maintenance History doctype...")
            
            # Create the doctype
            doctype = frappe.new_doc("DocType")
            doctype.name = "Maintenance History"
            doctype.module = "Vacker Automation"
            doctype.custom = 1
            doctype.istable = 0
            doctype.track_changes = 1
            doctype.track_views = 1
            
            # Add fields
            fields = [
                {
                    "fieldname": "maintenance_schedule",
                    "fieldtype": "Link",
                    "label": "Maintenance Schedule",
                    "options": "Maintenance Schedule",
                    "reqd": 1
                },
                {
                    "fieldname": "property",
                    "fieldtype": "Link",
                    "label": "Property",
                    "options": "Property",
                    "reqd": 1
                },
                {
                    "fieldname": "landlord",
                    "fieldtype": "Link",
                    "label": "Landlord",
                    "options": "Landlord",
                    "reqd": 1
                },
                {
                    "fieldname": "maintenance_type",
                    "fieldtype": "Select",
                    "label": "Maintenance Type",
                    "options": "Routine\nEmergency\nRepair\nUpgrade"
                },
                {
                    "fieldname": "completed_date",
                    "fieldtype": "Date",
                    "label": "Completed Date"
                },
                {
                    "fieldname": "actual_cost",
                    "fieldtype": "Currency",
                    "label": "Actual Cost",
                    "precision": "2"
                },
                {
                    "fieldname": "estimated_cost",
                    "fieldtype": "Currency",
                    "label": "Estimated Cost",
                    "precision": "2"
                },
                {
                    "fieldname": "technician",
                    "fieldtype": "Link",
                    "label": "Technician",
                    "options": "Employee"
                },
                {
                    "fieldname": "technician_notes",
                    "fieldtype": "Text",
                    "label": "Technician Notes"
                },
                {
                    "fieldname": "landlord_feedback",
                    "fieldtype": "Text",
                    "label": "Landlord Feedback"
                }
            ]
            
            for field_data in fields:
                field = doctype.append("fields")
                for key, value in field_data.items():
                    setattr(field, key, value)
            
            doctype.insert(ignore_permissions=True)
            logger.info("Maintenance History doctype created successfully")
        
    except Exception as e:
        logger.error(f"Error creating Maintenance History doctype: {str(e)}")
        raise

def create_ai_settings_doctype():
    """Create AI Settings doctype if it doesn't exist"""
    try:
        if not frappe.db.exists("DocType", "AI Settings"):
            logger.info("Creating AI Settings doctype...")
            
            # Create the doctype
            doctype = frappe.new_doc("DocType")
            doctype.name = "AI Settings"
            doctype.module = "Vacker Automation"
            doctype.custom = 1
            doctype.istable = 0
            doctype.track_changes = 1
            doctype.track_views = 1
            
            # Add fields
            fields = [
                {
                    "fieldname": "ai_provider",
                    "fieldtype": "Select",
                    "label": "AI Provider",
                    "options": "OpenAI\nAnthropic\nGoogle\nAzure\nCustom",
                    "reqd": 1
                },
                {
                    "fieldname": "api_key",
                    "fieldtype": "Password",
                    "label": "API Key",
                    "reqd": 1
                },
                {
                    "fieldname": "model_name",
                    "fieldtype": "Data",
                    "label": "Model Name",
                    "default": "gpt-4"
                },
                {
                    "fieldname": "max_tokens",
                    "fieldtype": "Int",
                    "label": "Max Tokens",
                    "default": "1000"
                },
                {
                    "fieldname": "temperature",
                    "fieldtype": "Float",
                    "label": "Temperature",
                    "default": "0.7"
                },
                {
                    "fieldname": "enabled_features",
                    "fieldtype": "MultiSelect",
                    "label": "Enabled Features",
                    "options": "Property Analysis\nRental Optimization\nMaintenance Prediction\nMarket Analysis\nContract Review"
                },
                {
                    "fieldname": "is_active",
                    "fieldtype": "Check",
                    "label": "Is Active",
                    "default": 1
                }
            ]
            
            for field_data in fields:
                field = doctype.append("fields")
                for key, value in field_data.items():
                    setattr(field, key, value)
            
            doctype.insert(ignore_permissions=True)
            logger.info("AI Settings doctype created successfully")
        
    except Exception as e:
        logger.error(f"Error creating AI Settings doctype: {str(e)}")
        raise

def update_existing_data():
    """Update existing data with new field values"""
    try:
        logger.info("Updating existing data...")
        
        # Update existing landlord properties with default rental percentage
        frappe.db.sql("""
            UPDATE `tabLandlord Property` 
            SET rental_percentage = 100 
            WHERE rental_percentage IS NULL
        """)
        
        # Update existing payment schedules with remaining balance
        frappe.db.sql("""
            UPDATE `tabLandlord Payment Schedule` 
            SET remaining_balance = amount 
            WHERE remaining_balance IS NULL
        """)
        
        # Update existing properties with calculated values
        properties = frappe.get_all("Property", fields=["name", "property_type", "city"])
        for prop in properties:
            try:
                property_doc = frappe.get_doc("Property", prop.name)
                property_doc.calculate_property_value()
                property_doc.save(ignore_permissions=True)
            except Exception as e:
                logger.warning(f"Could not update property {prop.name}: {str(e)}")
        
        logger.info("Existing data updated successfully")
        
    except Exception as e:
        logger.error(f"Error updating existing data: {str(e)}")
        raise

def create_database_indexes():
    """Create database indexes for better performance"""
    try:
        logger.info("Creating database indexes...")
        
        # Use frappe.db.commit() to handle implicit commits properly
        frappe.db.commit()
        
        # Indexes for Landlord Payment Schedule
        try:
            frappe.db.sql("""
                CREATE INDEX IF NOT EXISTS idx_landlord_payment_schedule_landlord 
                ON `tabLandlord Payment Schedule` (landlord)
            """)
            logger.info("Created index: idx_landlord_payment_schedule_landlord")
        except Exception as e:
            logger.warning(f"Could not create index idx_landlord_payment_schedule_landlord: {str(e)}")
        
        try:
            frappe.db.sql("""
                CREATE INDEX IF NOT EXISTS idx_landlord_payment_schedule_status 
                ON `tabLandlord Payment Schedule` (status)
            """)
            logger.info("Created index: idx_landlord_payment_schedule_status")
        except Exception as e:
            logger.warning(f"Could not create index idx_landlord_payment_schedule_status: {str(e)}")
        
        try:
            frappe.db.sql("""
                CREATE INDEX IF NOT EXISTS idx_landlord_payment_schedule_due_date 
                ON `tabLandlord Payment Schedule` (due_date)
            """)
            logger.info("Created index: idx_landlord_payment_schedule_due_date")
        except Exception as e:
            logger.warning(f"Could not create index idx_landlord_payment_schedule_due_date: {str(e)}")
        
        # Indexes for Maintenance Schedule
        try:
            frappe.db.sql("""
                CREATE INDEX IF NOT EXISTS idx_maintenance_schedule_landlord 
                ON `tabMaintenance Schedule` (landlord)
            """)
            logger.info("Created index: idx_maintenance_schedule_landlord")
        except Exception as e:
            logger.warning(f"Could not create index idx_maintenance_schedule_landlord: {str(e)}")
        
        try:
            frappe.db.sql("""
                CREATE INDEX IF NOT EXISTS idx_maintenance_schedule_status 
                ON `tabMaintenance Schedule` (status)
            """)
            logger.info("Created index: idx_maintenance_schedule_status")
        except Exception as e:
            logger.warning(f"Could not create index idx_maintenance_schedule_status: {str(e)}")
        
        try:
            frappe.db.sql("""
                CREATE INDEX IF NOT EXISTS idx_maintenance_schedule_scheduled_date 
                ON `tabMaintenance Schedule` (scheduled_date)
            """)
            logger.info("Created index: idx_maintenance_schedule_scheduled_date")
        except Exception as e:
            logger.warning(f"Could not create index idx_maintenance_schedule_scheduled_date: {str(e)}")
        
        # Indexes for Property
        try:
            frappe.db.sql("""
                CREATE INDEX IF NOT EXISTS idx_property_type 
                ON `tabProperty` (property_type)
            """)
            logger.info("Created index: idx_property_type")
        except Exception as e:
            logger.warning(f"Could not create index idx_property_type: {str(e)}")
        
        try:
            frappe.db.sql("""
                CREATE INDEX IF NOT EXISTS idx_property_status 
                ON `tabProperty` (property_status)
            """)
            logger.info("Created index: idx_property_status")
        except Exception as e:
            logger.warning(f"Could not create index idx_property_status: {str(e)}")
        
        # Indexes for Landlord Property
        try:
            frappe.db.sql("""
                CREATE INDEX IF NOT EXISTS idx_landlord_property_parent 
                ON `tabLandlord Property` (parent)
            """)
            logger.info("Created index: idx_landlord_property_parent")
        except Exception as e:
            logger.warning(f"Could not create index idx_landlord_property_parent: {str(e)}")
        
        try:
            frappe.db.sql("""
                CREATE INDEX IF NOT EXISTS idx_landlord_property_status 
                ON `tabLandlord Property` (status)
            """)
            logger.info("Created index: idx_landlord_property_status")
        except Exception as e:
            logger.warning(f"Could not create index idx_landlord_property_status: {str(e)}")
        
        frappe.db.commit()
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating database indexes: {str(e)}")
        frappe.db.rollback()
        # Don't raise the exception, just log it as indexes are optional

def get_field_type_sql(field):
    """Convert Frappe field type to SQL type"""
    field_type_mapping = {
        "Data": "VARCHAR(255)",
        "Text": "TEXT",
        "Link": "VARCHAR(255)",
        "Select": "VARCHAR(255)",
        "MultiSelect": "TEXT",
        "Check": "INT(1)",
        "Int": "INT",
        "Float": "DECIMAL(18,6)",
        "Currency": "DECIMAL(18,6)",
        "Percent": "DECIMAL(5,2)",
        "Date": "DATE",
        "Datetime": "DATETIME",
        "Time": "TIME",
        "Password": "VARCHAR(255)",
        "Code": "TEXT"
    }
    
    sql_type = field_type_mapping.get(field["fieldtype"], "VARCHAR(255)")
    
    # Add precision for numeric fields
    if field["fieldtype"] in ["Currency", "Float"] and "precision" in field:
        precision = field["precision"]
        if field["fieldtype"] == "Currency":
            sql_type = f"DECIMAL(18,{precision})"
        else:
            sql_type = f"DECIMAL(18,{precision})"
    
    return sql_type 