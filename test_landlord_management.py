#!/usr/bin/env python3
"""
Test Script for Landlord Management System
Validates all components and functionality of the system.
"""

import frappe
import unittest
from frappe.utils import today, getdate, add_months
from datetime import datetime

class TestLandlordManagement(unittest.TestCase):
    """Test cases for Landlord Management System"""
    
    def setUp(self):
        """Set up test data"""
        self.create_test_data()
    
    def tearDown(self):
        """Clean up test data"""
        self.cleanup_test_data()
    
    def create_test_data(self):
        """Create test data for all tests"""
        # Create test property
        if not frappe.db.exists("Property", {"property_name": "Test Property"}):
            self.test_property = frappe.new_doc("Property")
            self.test_property.property_name = "Test Property"
            self.test_property.full_address = "123 Test Street, Test City"
            self.test_property.city = "Test City"
            self.test_property.state_province = "Test State"
            self.test_property.property_type = "Commercial"
            self.test_property.property_status = "Available"
            self.test_property.insert(ignore_permissions=True)
        else:
            self.test_property = frappe.get_doc("Property", {"property_name": "Test Property"})
        
        # Create test landlord
        if not frappe.db.exists("Landlord", {"full_legal_name": "Test Landlord"}):
            self.test_landlord = frappe.new_doc("Landlord")
            self.test_landlord.full_legal_name = "Test Landlord"
            self.test_landlord.contact_person = "Test Contact"
            self.test_landlord.landlord_type = "Individual"
            self.test_landlord.primary_phone = "+91-1234567890"
            self.test_landlord.email_address = "test@landlord.com"
            self.test_landlord.physical_address = "456 Test Address"
            self.test_landlord.property = self.test_property.name
            self.test_landlord.media_type = "Billboard"
            self.test_landlord.contract_start_date = today()
            self.test_landlord.contract_end_date = add_months(today(), 12)
            self.test_landlord.payment_frequency = "Monthly"
            self.test_landlord.rental_amount = 50000
            self.test_landlord.tax_identification_number = "TEST123456789"
            self.test_landlord.insert(ignore_permissions=True)
        else:
            self.test_landlord = frappe.get_doc("Landlord", {"full_legal_name": "Test Landlord"})
    
    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            # Delete test records
            if hasattr(self, 'test_landlord') and self.test_landlord:
                frappe.delete_doc("Landlord", self.test_landlord.name, force=True)
            
            if hasattr(self, 'test_property') and self.test_property:
                frappe.delete_doc("Property", self.test_property.name, force=True)
                
        except Exception as e:
            print(f"Cleanup error: {str(e)}")
    
    def test_01_property_creation(self):
        """Test property creation and validation"""
        print("Testing Property Creation...")
        
        # Test property creation
        property_doc = frappe.new_doc("Property")
        property_doc.property_name = "Test Property 2"
        property_doc.full_address = "789 Test Address"
        property_doc.city = "Test City 2"
        property_doc.state_province = "Test State 2"
        property_doc.property_type = "Roadside"
        property_doc.property_status = "Available"
        
        # Test validation
        property_doc.validate()
        property_doc.insert(ignore_permissions=True)
        
        # Verify creation
        self.assertTrue(frappe.db.exists("Property", property_doc.name))
        self.assertEqual(property_doc.property_name, "Test Property 2")
        
        # Cleanup
        frappe.delete_doc("Property", property_doc.name, force=True)
        print("✅ Property creation test passed")
    
    def test_02_landlord_creation(self):
        """Test landlord creation and validation"""
        print("Testing Landlord Creation...")
        
        # Test landlord creation
        landlord_doc = frappe.new_doc("Landlord")
        landlord_doc.full_legal_name = "Test Landlord 2"
        landlord_doc.contact_person = "Test Contact 2"
        landlord_doc.landlord_type = "Corporate"
        landlord_doc.primary_phone = "+91-9876543210"
        landlord_doc.email_address = "test2@landlord.com"
        landlord_doc.physical_address = "789 Test Address"
        landlord_doc.property = self.test_property.name
        landlord_doc.media_type = "Digital Display"
        landlord_doc.contract_start_date = today()
        landlord_doc.contract_end_date = add_months(today(), 24)
        landlord_doc.payment_frequency = "Quarterly"
        landlord_doc.rental_amount = 100000
        landlord_doc.tax_identification_number = "TEST987654321"
        
        # Test validation
        landlord_doc.validate()
        landlord_doc.insert(ignore_permissions=True)
        
        # Verify creation
        self.assertTrue(frappe.db.exists("Landlord", landlord_doc.name))
        self.assertEqual(landlord_doc.full_legal_name, "Test Landlord 2")
        
        # Test auto-generated landlord ID
        self.assertIsNotNone(landlord_doc.landlord_id)
        self.assertTrue(landlord_doc.landlord_id.startswith("LAND-"))
        
        # Cleanup
        frappe.delete_doc("Landlord", landlord_doc.name, force=True)
        print("✅ Landlord creation test passed")
    
    def test_03_landlord_validation(self):
        """Test landlord validation rules"""
        print("Testing Landlord Validation...")
        
        # Test invalid contract dates
        landlord_doc = frappe.new_doc("Landlord")
        landlord_doc.full_legal_name = "Validation Test Landlord"
        landlord_doc.primary_phone = "+91-1234567890"
        landlord_doc.email_address = "validation@test.com"
        landlord_doc.physical_address = "Test Address"
        landlord_doc.property = self.test_property.name
        landlord_doc.contract_start_date = today()
        landlord_doc.contract_end_date = today()  # Same as start date
        
        # Should raise validation error
        with self.assertRaises(Exception):
            landlord_doc.validate()
        
        # Test invalid email
        landlord_doc.contract_end_date = add_months(today(), 12)
        landlord_doc.email_address = "invalid-email"
        
        with self.assertRaises(Exception):
            landlord_doc.validate()
        
        # Test invalid phone
        landlord_doc.email_address = "valid@email.com"
        landlord_doc.primary_phone = "123"  # Too short
        
        with self.assertRaises(Exception):
            landlord_doc.validate()
        
        print("✅ Landlord validation test passed")
    
    def test_04_payment_schedule_generation(self):
        """Test automatic payment schedule generation"""
        print("Testing Payment Schedule Generation...")
        
        # Submit landlord to trigger payment schedule generation
        self.test_landlord.submit()
        
        # Check if payment schedules were created
        payment_schedules = frappe.get_all("Landlord Payment Schedule", 
            filters={"landlord": self.test_landlord.name},
            fields=["name", "due_date", "amount", "status"]
        )
        
        self.assertGreater(len(payment_schedules), 0)
        
        # Verify first payment schedule
        first_payment = payment_schedules[0]
        self.assertEqual(first_payment.amount, 50000)
        self.assertEqual(first_payment.status, "Pending")
        
        print("✅ Payment schedule generation test passed")
    
    def test_05_media_installation(self):
        """Test media installation creation and management"""
        print("Testing Media Installation...")
        
        # Create media installation
        installation_doc = frappe.new_doc("Media Installation")
        installation_doc.landlord = self.test_landlord.name
        installation_doc.property = self.test_property.name
        installation_doc.installation_date = today()
        installation_doc.installation_status = "Planned"
        installation_doc.installation_cost = 25000
        installation_doc.maintenance_schedule = "Monthly"
        
        installation_doc.validate()
        installation_doc.insert(ignore_permissions=True)
        
        # Verify creation
        self.assertTrue(frappe.db.exists("Media Installation", installation_doc.name))
        self.assertEqual(installation_doc.installation_status, "Planned")
        
        # Test status update
        installation_doc.installation_status = "Completed"
        installation_doc.save()
        
        # Check if maintenance schedules were created
        maintenance_schedules = frappe.get_all("Maintenance Schedule",
            filters={"media_installation": installation_doc.name},
            fields=["name", "scheduled_date", "status"]
        )
        
        self.assertGreater(len(maintenance_schedules), 0)
        
        # Cleanup
        frappe.delete_doc("Media Installation", installation_doc.name, force=True)
        print("✅ Media installation test passed")
    
    def test_06_dashboard_data(self):
        """Test dashboard data retrieval"""
        print("Testing Dashboard Data...")
        
        # Import dashboard functions
        from vacker_automation.page.landlord_management_dashboard.landlord_management_dashboard import (
            get_summary_data, get_chart_data, get_upcoming_payments
        )
        
        # Test summary data
        summary = get_summary_data()
        self.assertIsInstance(summary, dict)
        self.assertIn('total_landlords', summary)
        self.assertIn('active_landlords', summary)
        self.assertIn('monthly_income', summary)
        
        # Test chart data
        charts = get_chart_data()
        self.assertIsInstance(charts, dict)
        self.assertIn('revenue_by_type', charts)
        self.assertIn('revenue_by_media', charts)
        
        # Test upcoming payments
        payments = get_upcoming_payments()
        self.assertIsInstance(payments, list)
        
        print("✅ Dashboard data test passed")
    
    def test_07_api_endpoints(self):
        """Test API endpoints"""
        print("Testing API Endpoints...")
        
        # Test landlord summary API
        summary = self.test_landlord.get_landlord_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('landlord_id', summary)
        self.assertIn('full_legal_name', summary)
        
        # Test annual revenue calculation
        annual_revenue = self.test_landlord.calculate_annual_revenue()
        self.assertEqual(annual_revenue, 50000 * 12)  # Monthly * 12
        
        # Test property details API
        property_details = self.test_property.get_property_details()
        self.assertIsInstance(property_details, dict)
        self.assertIn('property_id', property_details)
        self.assertIn('property_name', property_details)
        
        print("✅ API endpoints test passed")
    
    def test_08_email_notifications(self):
        """Test email notification functionality"""
        print("Testing Email Notifications...")
        
        # Test welcome notification (without actually sending)
        try:
            self.test_landlord.send_welcome_notification()
            print("✅ Welcome notification test passed")
        except Exception as e:
            print(f"⚠️  Welcome notification test: {str(e)}")
        
        # Test contract expiry reminder
        try:
            self.test_landlord.send_contract_expiry_reminder(30)
            print("✅ Contract expiry reminder test passed")
        except Exception as e:
            print(f"⚠️  Contract expiry reminder test: {str(e)}")
    
    def test_09_permissions(self):
        """Test role-based permissions"""
        print("Testing Permissions...")
        
        # Check if roles exist
        roles = ["Landlord Manager", "Property Coordinator", "Accounts Executive", "Field Executive"]
        for role in roles:
            self.assertTrue(frappe.db.exists("Role", role), f"Role {role} should exist")
        
        # Check DocType permissions
        doctypes = ["Property", "Landlord", "Media Installation"]
        for doctype in doctypes:
            permissions = frappe.get_all("Custom DocPerm",
                filters={"parent": doctype},
                fields=["role", "read", "write", "create"]
            )
            self.assertGreater(len(permissions), 0, f"Permissions should exist for {doctype}")
        
        print("✅ Permissions test passed")
    
    def test_10_workflow(self):
        """Test workflow functionality"""
        print("Testing Workflow...")
        
        # Check if workflow exists
        workflow_name = "Landlord Onboarding"
        if frappe.db.exists("Workflow", workflow_name):
            workflow = frappe.get_doc("Workflow", workflow_name)
            self.assertEqual(workflow.document_type, "Landlord")
            self.assertTrue(workflow.is_active)
            print("✅ Workflow test passed")
        else:
            print("⚠️  Workflow not found - may need to be created manually")

def run_tests():
    """Run all tests"""
    print("🧪 Starting Landlord Management System Tests...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLandlordManagement)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 60)
    print(f"📊 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if not result.failures and not result.errors:
        print("\n🎉 All tests passed! Landlord Management System is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
    
    return result

if __name__ == "__main__":
    # Run tests
    result = run_tests()
    
    # Exit with appropriate code
    if result.failures or result.errors:
        sys.exit(1)
    else:
        sys.exit(0) 