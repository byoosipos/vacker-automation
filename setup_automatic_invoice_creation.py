#!/usr/bin/env python3
"""
Setup script for automatic invoice creation based on payment schedules
"""

import frappe
from frappe.utils import getdate, today, add_days

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
        
        # Create a server script for manual execution
        create_server_script()
        
        print("\n🎉 Automatic invoice creation setup completed!")
        print("\n📋 Summary:")
        print("• Scheduled job runs daily at 9 AM")
        print("• Creates invoices for payment schedules due within 7 days")
        print("• Manual execution available via 'Create Invoices for Due Payments' button")
        print("• Individual schedule invoices can be created manually")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up automatic invoice creation: {str(e)}")
        return False

def create_server_script():
    """Create a server script for manual invoice creation"""
    try:
        script_name = "Create Invoices for Due Payments"
        
        if not frappe.db.exists("Server Script", script_name):
            script = frappe.new_doc("Server Script")
            script.name = script_name
            script.script_type = "API"
            script.api_method = "vacker_automation.vacker_automation.custom_api.work_flow.create_invoices_for_due_payments"
            script.insert()
            print(f"✅ Created server script: {script.name}")
        else:
            print(f"✅ Server script already exists: {script_name}")
            
    except Exception as e:
        print(f"❌ Error creating server script: {str(e)}")

def test_invoice_creation():
    """Test the invoice creation functionality"""
    try:
        print("\n🧪 Testing invoice creation...")
        
        # Get payment schedules that are due
        from frappe.utils import getdate, today, add_days
        
        due_schedules = frappe.get_all("Landlord Payment Schedule", 
            filters={
                "status": "Pending",
                "purchase_invoice": ["is", "null"],
                "due_date": ["<=", add_days(today(), 7)]
            },
            fields=["name", "landlord", "property", "due_date", "amount"]
        )
        
        print(f"Found {len(due_schedules)} payment schedules due within 7 days:")
        
        for schedule in due_schedules:
            days_until_due = (getdate(schedule.due_date) - getdate(today())).days
            status = "Overdue" if days_until_due < 0 else f"Due in {days_until_due} days"
            print(f"  • {schedule.name} - {schedule.property} - {schedule.amount} - {status}")
        
        if due_schedules:
            print("\n💡 To create invoices for these schedules:")
            print("1. Use the 'Create Invoices for Due Payments' button on any Landlord form")
            print("2. Or run the scheduled job manually")
            print("3. Or create invoices individually from each payment schedule")
        else:
            print("✅ No payment schedules are currently due for invoice creation")
            
    except Exception as e:
        print(f"❌ Error testing invoice creation: {str(e)}")

def main():
    """Main setup function"""
    print("🚀 Setting up Automatic Invoice Creation for Payment Schedules")
    print("=" * 60)
    
    # Setup the scheduled job
    if setup_automatic_invoice_creation():
        # Test the functionality
        test_invoice_creation()
        
        print("\n✅ Setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. The system will automatically create invoices for payment schedules due within 7 days")
        print("2. You can manually trigger invoice creation using the button on Landlord forms")
        print("3. Individual payment schedules can have invoices created manually")
        print("4. Check the scheduled job logs for any errors")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 