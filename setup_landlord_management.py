#!/usr/bin/env python3
"""
Landlord Management System Setup Script for Vacker Outdoor Advertising
This script installs and configures the complete landlord management system.
"""

import frappe
import os
import sys
from frappe.utils import today, getdate

def setup_landlord_management():
    """Main setup function for the landlord management system"""
    print("🚀 Setting up Landlord Management System for Vacker Outdoor Advertising...")
    
    try:
        # Step 1: Create Outdoor Advertising module
        create_outdoor_advertising_module()
        
        # Step 2: Create DocTypes
        create_doctypes()
        
        # Step 3: Create Dashboard Page
        create_dashboard_page()
        
        # Step 4: Set up permissions and roles
        setup_permissions()
        
        # Step 5: Create sample data (optional)
        create_sample_data()
        
        # Step 6: Configure workflows
        setup_workflows()
        
        print("✅ Landlord Management System setup completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Access the dashboard at: /app/landlord-management-dashboard")
        print("2. Create your first Property record")
        print("3. Add Landlord records")
        print("4. Configure payment schedules")
        print("5. Set up maintenance schedules")
        
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        frappe.log_error(f"Landlord Management Setup Error: {str(e)}")

def create_outdoor_advertising_module():
    """Create the Outdoor Advertising module"""
    print("📦 Creating Outdoor Advertising module...")
    
    if not frappe.db.exists("Module Def", "Outdoor Advertising"):
        module = frappe.new_doc("Module Def")
        module.module_name = "Outdoor Advertising"
        module.app_name = "vacker_automation"
        module.custom = 1
        module.package = "Vacker Automation"
        module.insert(ignore_permissions=True)
        print("✅ Outdoor Advertising module created")
    else:
        print("ℹ️  Outdoor Advertising module already exists")

def create_doctypes():
    """Create all required DocTypes"""
    print("🏗️  Creating DocTypes...")
    
    doctypes = [
        "Property",
        "Landlord", 
        "Media Installation",
        "Landlord Payment Schedule",
        "Maintenance Schedule"
    ]
    
    for doctype_name in doctypes:
        create_doctype(doctype_name)

def create_doctype(doctype_name):
    """Create a specific DocType"""
    try:
        if not frappe.db.exists("DocType", doctype_name):
            # Load DocType from JSON file
            json_file = f"vacker_automation/vacker_automation/doctype/{doctype_name.lower().replace(' ', '_')}/{doctype_name.lower().replace(' ', '_')}.json"
            
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    doctype_data = frappe.parse_json(f.read())
                
                # Create DocType
                doctype = frappe.new_doc("DocType")
                for key, value in doctype_data.items():
                    if key != "name":  # Skip the name field
                        setattr(doctype, key, value)
                
                doctype.insert(ignore_permissions=True)
                print(f"✅ Created DocType: {doctype_name}")
            else:
                print(f"⚠️  JSON file not found for DocType: {doctype_name}")
        else:
            print(f"ℹ️  DocType {doctype_name} already exists")
            
    except Exception as e:
        print(f"❌ Error creating DocType {doctype_name}: {str(e)}")

def create_dashboard_page():
    """Create the Landlord Management Dashboard page"""
    print("📊 Creating Landlord Management Dashboard...")
    
    try:
        if not frappe.db.exists("Page", "landlord-management-dashboard"):
            page = frappe.new_doc("Page")
            page.title = "Landlord Management Dashboard"
            page.page_name = "landlord-management-dashboard"
            page.module = "Outdoor Advertising"
            page.standard = "No"
            page.insert(ignore_permissions=True)
            print("✅ Landlord Management Dashboard page created")
        else:
            print("ℹ️  Landlord Management Dashboard page already exists")
            
    except Exception as e:
        print(f"❌ Error creating dashboard page: {str(e)}")

def setup_permissions():
    """Set up permissions and roles"""
    print("🔐 Setting up permissions and roles...")
    
    # Create roles if they don't exist
    roles = [
        "Landlord Manager",
        "Property Coordinator", 
        "Accounts Executive",
        "Field Executive"
    ]
    
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            role = frappe.new_doc("Role")
            role.role_name = role_name
            role.desk_access = 1
            role.insert(ignore_permissions=True)
            print(f"✅ Created role: {role_name}")
        else:
            print(f"ℹ️  Role {role_name} already exists")

def create_sample_data():
    """Create sample data for testing"""
    print("📝 Creating sample data...")
    
    # Create sample properties
    create_sample_properties()
    
    # Create sample landlords
    create_sample_landlords()
    
    print("✅ Sample data created")

def create_sample_properties():
    """Create sample property records"""
    sample_properties = [
        {
            "property_name": "Downtown Billboard - Main Street",
            "full_address": "123 Main Street, Downtown, City Center",
            "city": "Mumbai",
            "state_province": "Maharashtra",
            "property_type": "Commercial",
            "property_size": "14x48 feet",
            "property_status": "Available"
        },
        {
            "property_name": "Highway Digital Display - NH48",
            "full_address": "Highway NH48, Kilometer 25, Suburban Area",
            "city": "Pune",
            "state_province": "Maharashtra", 
            "property_type": "Roadside",
            "property_size": "20x60 feet",
            "property_status": "Available"
        },
        {
            "property_name": "Mall Transit Advertisement - Phoenix Mall",
            "full_address": "Phoenix Mall, Lower Parel, Mumbai",
            "city": "Mumbai",
            "state_province": "Maharashtra",
            "property_type": "Commercial",
            "property_size": "10x30 feet",
            "property_status": "Available"
        }
    ]
    
    for prop_data in sample_properties:
        if not frappe.db.exists("Property", {"property_name": prop_data["property_name"]}):
            property_doc = frappe.new_doc("Property")
            for key, value in prop_data.items():
                setattr(property_doc, key, value)
            property_doc.insert(ignore_permissions=True)
            print(f"✅ Created sample property: {prop_data['property_name']}")

def create_sample_landlords():
    """Create sample landlord records"""
    # Get existing properties
    properties = frappe.get_all("Property", fields=["name", "property_name"])
    
    if not properties:
        print("⚠️  No properties found. Please create properties first.")
        return
    
    sample_landlords = [
        {
            "full_legal_name": "ABC Properties Ltd",
            "contact_person": "Mr. Rajesh Kumar",
            "company_entity_name": "ABC Properties Ltd",
            "landlord_type": "Corporate",
            "primary_phone": "+91-9876543210",
            "email_address": "rajesh@abcproperties.com",
            "physical_address": "456 Business Park, Andheri, Mumbai",
            "media_type": "Billboard",
            "contract_start_date": today(),
            "contract_end_date": getdate(today()).replace(year=getdate(today()).year + 2),
            "payment_frequency": "Monthly",
            "rental_amount": 50000,
            "tax_identification_number": "ABCD123456789"
        },
        {
            "full_legal_name": "Mrs. Priya Sharma",
            "contact_person": "Mrs. Priya Sharma",
            "landlord_type": "Individual",
            "primary_phone": "+91-8765432109",
            "email_address": "priya.sharma@email.com",
            "physical_address": "789 Residential Complex, Bandra, Mumbai",
            "media_type": "Digital Display",
            "contract_start_date": today(),
            "contract_end_date": getdate(today()).replace(year=getdate(today()).year + 1),
            "payment_frequency": "Quarterly",
            "rental_amount": 75000,
            "tax_identification_number": "PRIYA987654321"
        }
    ]
    
    for i, landlord_data in enumerate(sample_landlords):
        if i < len(properties):
            landlord_data["property"] = properties[i]["name"]
            
            if not frappe.db.exists("Landlord", {"full_legal_name": landlord_data["full_legal_name"]}):
                landlord_doc = frappe.new_doc("Landlord")
                for key, value in landlord_data.items():
                    setattr(landlord_doc, key, value)
                landlord_doc.insert(ignore_permissions=True)
                print(f"✅ Created sample landlord: {landlord_data['full_legal_name']}")

def setup_workflows():
    """Set up workflows for landlord management"""
    print("⚙️  Setting up workflows...")
    
    # Create landlord onboarding workflow
    create_landlord_workflow()
    
    print("✅ Workflows configured")

def create_landlord_workflow():
    """Create workflow for landlord onboarding"""
    workflow_name = "Landlord Onboarding"
    
    if not frappe.db.exists("Workflow", workflow_name):
        workflow = frappe.new_doc("Workflow")
        workflow.workflow_name = workflow_name
        workflow.document_type = "Landlord"
        workflow.is_active = 1
        workflow.send_email_alert = 1
        
        # Add states
        states = [
            {"state": "Draft", "style": "gray"},
            {"state": "Pending Verification", "style": "orange"},
            {"state": "Approved", "style": "green"},
            {"state": "Active", "style": "blue"}
        ]
        
        for state_data in states:
            workflow.append("states", state_data)
        
        # Add transitions
        transitions = [
            {
                "state": "Draft",
                "action": "Submit for Verification",
                "next_state": "Pending Verification",
                "allowed": "Landlord Manager"
            },
            {
                "state": "Pending Verification", 
                "action": "Approve",
                "next_state": "Approved",
                "allowed": "System Manager"
            },
            {
                "state": "Approved",
                "action": "Activate",
                "next_state": "Active", 
                "allowed": "Landlord Manager"
            }
        ]
        
        for transition_data in transitions:
            workflow.append("transitions", transition_data)
        
        workflow.insert(ignore_permissions=True)
        print(f"✅ Created workflow: {workflow_name}")
    else:
        print(f"ℹ️  Workflow {workflow_name} already exists")

def verify_setup():
    """Verify that the setup was successful"""
    print("\n🔍 Verifying setup...")
    
    # Check if DocTypes exist
    doctypes = ["Property", "Landlord", "Media Installation"]
    for doctype in doctypes:
        if frappe.db.exists("DocType", doctype):
            print(f"✅ {doctype} DocType exists")
        else:
            print(f"❌ {doctype} DocType missing")
    
    # Check if dashboard page exists
    if frappe.db.exists("Page", "landlord-management-dashboard"):
        print("✅ Dashboard page exists")
    else:
        print("❌ Dashboard page missing")
    
    # Check if module exists
    if frappe.db.exists("Module Def", "Outdoor Advertising"):
        print("✅ Outdoor Advertising module exists")
    else:
        print("❌ Outdoor Advertising module missing")

if __name__ == "__main__":
    # This script should be run from the Frappe bench environment
    setup_landlord_management()
    verify_setup() 