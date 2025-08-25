# Copyright (c) 2025, Vacker and Contributors
# See license.txt

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, today, add_months
import logging

# Configure logging for tests
logger = logging.getLogger(__name__)

class TestLandlord(FrappeTestCase):
    """Comprehensive test suite for Landlord doctype"""
    
    def setUp(self):
        """Set up test data"""
        self.create_test_data()
    
    def tearDown(self):
        """Clean up test data"""
        self.cleanup_test_data()
    
    def create_test_data(self):
        """Create test data for all tests"""
        try:
            # Create test property
            if not frappe.db.exists("Property", "TEST-PROP-001"):
                self.test_property = frappe.new_doc("Property")
                self.test_property.property_id = "TEST-PROP-001"
                self.test_property.property_name = "Test Billboard"
                self.test_property.full_address = "123 Test Street, Kampala"
                self.test_property.city = "Kampala"
                self.test_property.state_province = "Central"
                self.test_property.property_type = "Commercial"
                self.test_property.property_status = "Available"
                self.test_property.insert(ignore_permissions=True)
            else:
                self.test_property = frappe.get_doc("Property", "TEST-PROP-001")
            
            # Create test landlord
            if not frappe.db.exists("Landlord", "TEST-LAND-001"):
                self.test_landlord = frappe.new_doc("Landlord")
                self.test_landlord.landlord_id = "TEST-LAND-001"
                self.test_landlord.full_legal_name = "Test Landlord Company"
                self.test_landlord.primary_phone = "1234567890"
                self.test_landlord.email_address = "test@landlord.com"
                self.test_landlord.physical_address = "456 Landlord Street, Kampala"
                self.test_landlord.tax_identification_number = "TIN123456"
                self.test_landlord.date_of_onboarding = today()
                self.test_landlord.insert(ignore_permissions=True)
            else:
                self.test_landlord = frappe.get_doc("Landlord", "TEST-LAND-001")
                
        except Exception as e:
            logger.error(f"Error creating test data: {str(e)}")
            raise
    
    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            # Clean up test documents
            test_docs = [
                ("Landlord", "TEST-LAND-001"),
                ("Property", "TEST-PROP-001"),
                ("Landlord Payment Schedule", {"landlord": "TEST-LAND-001"}),
                ("Maintenance Schedule", {"landlord": "TEST-LAND-001"})
            ]
            
            for doctype, filters in test_docs:
                if isinstance(filters, dict):
                    frappe.db.delete(doctype, filters)
                else:
                    if frappe.db.exists(doctype, filters):
                        frappe.delete_doc(doctype, filters, ignore_permissions=True)
                        
        except Exception as e:
            logger.error(f"Error cleaning up test data: {str(e)}")
    
    def test_landlord_creation(self):
        """Test basic landlord creation"""
        try:
            landlord = frappe.new_doc("Landlord")
            landlord.landlord_id = "TEST-CREATE-001"
            landlord.full_legal_name = "Test Creation Landlord"
            landlord.primary_phone = "9876543210"
            landlord.email_address = "create@test.com"
            landlord.physical_address = "789 Create Street"
            landlord.tax_identification_number = "TIN789"
            landlord.date_of_onboarding = today()
            
            landlord.insert(ignore_permissions=True)
            
            # Verify creation
            self.assertTrue(frappe.db.exists("Landlord", landlord.name))
            self.assertEqual(landlord.full_legal_name, "Test Creation Landlord")
            
            # Clean up
            frappe.delete_doc("Landlord", landlord.name, ignore_permissions=True)
            
        except Exception as e:
            self.fail(f"Landlord creation test failed: {str(e)}")
    
    def test_landlord_validation(self):
        """Test landlord validation rules"""
        try:
            # Test missing required fields
            landlord = frappe.new_doc("Landlord")
            landlord.landlord_id = "TEST-VALIDATE-001"
            
            with self.assertRaises(frappe.ValidationError):
                landlord.insert(ignore_permissions=True)
            
            # Test invalid email format
            landlord.full_legal_name = "Test Validation"
            landlord.primary_phone = "1234567890"
            landlord.email_address = "invalid-email"
            landlord.physical_address = "Test Address"
            landlord.tax_identification_number = "TIN123"
            landlord.date_of_onboarding = today()
            
            with self.assertRaises(frappe.ValidationError):
                landlord.insert(ignore_permissions=True)
                
        except Exception as e:
            self.fail(f"Landlord validation test failed: {str(e)}")
    
    def test_property_addition(self):
        """Test adding properties to landlord"""
        try:
            # Add property to landlord
            child = self.test_landlord.append("properties")
            child.property = self.test_property.name
            child.contract_start_date = today()
            child.contract_end_date = add_months(today(), 12)
            child.rental_amount = 1000
            child.payment_frequency = "Monthly"
            child.status = "Active"
            
            self.test_landlord.save(ignore_permissions=True)
            
            # Verify property was added
            self.assertEqual(len(self.test_landlord.properties), 1)
            self.assertEqual(self.test_landlord.properties[0].rental_amount, 1000)
            
            # Test rental amount calculation
            self.test_landlord.calculate_total_rental_amount()
            self.assertEqual(self.test_landlord.rental_amount, 1000)
            
        except Exception as e:
            self.fail(f"Property addition test failed: {str(e)}")
    
    def test_payment_schedule_generation(self):
        """Test payment schedule generation"""
        try:
            # Add property first
            child = self.test_landlord.append("properties")
            child.property = self.test_property.name
            child.contract_start_date = today()
            child.contract_end_date = add_months(today(), 12)
            child.rental_amount = 1000
            child.payment_frequency = "Monthly"
            child.status = "Active"
            
            self.test_landlord.save(ignore_permissions=True)
            
            # Generate payment schedules
            result = self.test_landlord.generate_invoicing_schedules()
            
            # Verify schedules were created
            schedules = frappe.get_all("Landlord Payment Schedule", {
                "landlord": self.test_landlord.name
            })
            
            self.assertGreater(len(schedules), 0)
            
            # Verify schedule details
            schedule = frappe.get_doc("Landlord Payment Schedule", schedules[0].name)
            self.assertEqual(schedule.landlord, self.test_landlord.name)
            self.assertEqual(schedule.property, self.test_property.name)
            self.assertEqual(schedule.amount, 1000)
            
        except Exception as e:
            self.fail(f"Payment schedule generation test failed: {str(e)}")
    
    def test_overlapping_contracts(self):
        """Test overlapping contract validation"""
        try:
            # Add first property
            child1 = self.test_landlord.append("properties")
            child1.property = self.test_property.name
            child1.contract_start_date = today()
            child1.contract_end_date = add_months(today(), 6)
            child1.rental_amount = 1000
            child1.payment_frequency = "Monthly"
            child1.status = "Active"
            
            self.test_landlord.save(ignore_permissions=True)
            
            # Try to add overlapping contract
            child2 = self.test_landlord.append("properties")
            child2.property = self.test_property.name
            child2.contract_start_date = add_months(today(), 3)  # Overlaps
            child2.contract_end_date = add_months(today(), 9)
            child2.rental_amount = 1200
            child2.payment_frequency = "Monthly"
            child2.status = "Active"
            
            # This should raise a validation error
            with self.assertRaises(frappe.ValidationError):
                self.test_landlord.save(ignore_permissions=True)
                
        except Exception as e:
            self.fail(f"Overlapping contracts test failed: {str(e)}")
    
    def test_partial_payment_support(self):
        """Test partial payment functionality"""
        try:
            # Create payment schedule
            schedule = frappe.new_doc("Landlord Payment Schedule")
            schedule.landlord = self.test_landlord.name
            schedule.property = self.test_property.name
            schedule.due_date = today()
            schedule.amount = 1000
            schedule.payment_frequency = "Monthly"
            schedule.status = "Pending"
            schedule.insert(ignore_permissions=True)
            
            # Test partial payment
            result = schedule.mark_as_paid(payment_date=today(), partial_amount=600)
            
            self.assertTrue(result.success)
            self.assertEqual(schedule.status, "Partially Paid")
            self.assertEqual(schedule.remaining_balance, 400)
            
        except Exception as e:
            self.fail(f"Partial payment test failed: {str(e)}")
    
    def test_escalation_clause(self):
        """Test escalation clause functionality"""
        try:
            # Add property with escalation clause
            child = self.test_landlord.append("properties")
            child.property = self.test_property.name
            child.contract_start_date = today()
            child.contract_end_date = add_months(today(), 12)
            child.rental_amount = 1000
            child.payment_frequency = "Monthly"
            child.status = "Active"
            child.escalation_clause = "5% annually"
            
            self.test_landlord.save(ignore_permissions=True)
            
            # Verify escalation calculation
            self.assertEqual(child.escalation_percentage, 5)
            self.assertEqual(child.escalation_frequency, "Annually")
            self.assertEqual(child.escalated_rental_amount, 1050)
            
        except Exception as e:
            self.fail(f"Escalation clause test failed: {str(e)}")
    
    def test_maintenance_integration(self):
        """Test maintenance schedule integration"""
        try:
            # Create maintenance schedule
            maintenance = frappe.new_doc("Maintenance Schedule")
            maintenance.media_installation = "TEST-INST-001"  # Would need to create this
            maintenance.landlord = self.test_landlord.name
            maintenance.property = self.test_property.name
            maintenance.scheduled_date = add_months(today(), 1)
            maintenance.maintenance_type = "Routine"
            maintenance.status = "Scheduled"
            maintenance.insert(ignore_permissions=True)
            
            # Test maintenance completion
            result = maintenance.mark_as_completed(
                completed_date=today(),
                technician_notes="Test maintenance completed",
                maintenance_cost=500
            )
            
            self.assertTrue(result.success)
            self.assertEqual(maintenance.status, "Completed")
            
        except Exception as e:
            self.fail(f"Maintenance integration test failed: {str(e)}")
    
    def test_property_valuation(self):
        """Test property valuation calculation"""
        try:
            # Test property value calculation
            self.test_property.calculate_property_value()
            
            self.assertIsNotNone(self.test_property.calculated_value)
            self.assertGreater(self.test_property.calculated_value, 0)
            
            # Test valuation update
            result = self.test_property.update_valuation(150000, today())
            
            self.assertTrue(result.success)
            self.assertEqual(self.test_property.market_value, 150000)
            
        except Exception as e:
            self.fail(f"Property valuation test failed: {str(e)}")
    
    def test_audit_logging(self):
        """Test audit logging functionality"""
        try:
            # Create a test landlord and verify logging
            landlord = frappe.new_doc("Landlord")
            landlord.landlord_id = "TEST-AUDIT-001"
            landlord.full_legal_name = "Test Audit Landlord"
            landlord.primary_phone = "1111111111"
            landlord.email_address = "audit@test.com"
            landlord.physical_address = "Audit Street"
            landlord.tax_identification_number = "TIN111"
            landlord.date_of_onboarding = today()
            
            landlord.insert(ignore_permissions=True)
            
            # Check if audit log was created (implementation dependent)
            # This would depend on how audit logging is implemented
            
            # Clean up
            frappe.delete_doc("Landlord", landlord.name, ignore_permissions=True)
            
        except Exception as e:
            self.fail(f"Audit logging test failed: {str(e)}")
    
    def test_performance_large_dataset(self):
        """Test performance with large datasets"""
        try:
            # Create multiple properties and landlords
            landlords = []
            properties = []
            
            for i in range(10):
                # Create property
                prop = frappe.new_doc("Property")
                prop.property_id = f"PERF-PROP-{i:03d}"
                prop.property_name = f"Performance Property {i}"
                prop.full_address = f"Performance Street {i}"
                prop.city = "Kampala"
                prop.state_province = "Central"
                prop.property_type = "Commercial"
                prop.insert(ignore_permissions=True)
                properties.append(prop)
                
                # Create landlord
                landlord = frappe.new_doc("Landlord")
                landlord.landlord_id = f"PERF-LAND-{i:03d}"
                landlord.full_legal_name = f"Performance Landlord {i}"
                landlord.primary_phone = f"123456789{i}"
                landlord.email_address = f"perf{i}@test.com"
                landlord.physical_address = f"Performance Address {i}"
                landlord.tax_identification_number = f"TIN{i:03d}"
                landlord.date_of_onboarding = today()
                landlord.insert(ignore_permissions=True)
                landlords.append(landlord)
                
                # Add property to landlord
                child = landlord.append("properties")
                child.property = prop.name
                child.contract_start_date = today()
                child.contract_end_date = add_months(today(), 12)
                child.rental_amount = 1000 + (i * 100)
                child.payment_frequency = "Monthly"
                child.status = "Active"
                landlord.save(ignore_permissions=True)
            
            # Test bulk operations
            start_time = frappe.utils.now()
            
            # Generate payment schedules for all landlords
            for landlord in landlords:
                landlord.generate_invoicing_schedules()
            
            end_time = frappe.utils.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Performance assertion (should complete within reasonable time)
            self.assertLess(processing_time, 30)  # 30 seconds max
            
            # Clean up
            for landlord in landlords:
                frappe.delete_doc("Landlord", landlord.name, ignore_permissions=True)
            for prop in properties:
                frappe.delete_doc("Property", prop.name, ignore_permissions=True)
                
        except Exception as e:
            self.fail(f"Performance test failed: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling and recovery"""
        try:
            # Test invalid data handling
            landlord = frappe.new_doc("Landlord")
            landlord.landlord_id = "TEST-ERROR-001"
            landlord.full_legal_name = "Test Error Landlord"
            landlord.primary_phone = "invalid-phone"  # Invalid phone
            landlord.email_address = "invalid-email"  # Invalid email
            landlord.physical_address = "Test Address"
            landlord.tax_identification_number = "TIN123"
            landlord.date_of_onboarding = today()
            
            # Should raise validation error
            with self.assertRaises(frappe.ValidationError):
                landlord.insert(ignore_permissions=True)
            
            # Test recovery - fix the data and try again
            landlord.primary_phone = "1234567890"
            landlord.email_address = "valid@email.com"
            
            # Should work now
            landlord.insert(ignore_permissions=True)
            
            # Clean up
            frappe.delete_doc("Landlord", landlord.name, ignore_permissions=True)
            
        except Exception as e:
            self.fail(f"Error handling test failed: {str(e)}")
    
    def test_integration_with_erpnext(self):
        """Test integration with ERPNext modules"""
        try:
            # Test supplier creation
            self.test_landlord.create_or_update_supplier()
            
            # Verify supplier was created
            self.assertIsNotNone(self.test_landlord.supplier)
            self.assertTrue(frappe.db.exists("Supplier", self.test_landlord.supplier))
            
            # Test purchase invoice creation
            # This would require more setup with items and accounts
            
        except Exception as e:
            self.fail(f"ERPNext integration test failed: {str(e)}")
    
    def test_api_endpoints(self):
        """Test API endpoints and whitelist methods"""
        try:
            # Test get_landlord_summary
            summary = self.test_landlord.get_landlord_summary()
            self.assertIsInstance(summary, dict)
            self.assertIn('landlord_id', summary)
            
            # Test calculate_annual_revenue
            revenue = self.test_landlord.calculate_annual_revenue()
            self.assertIsInstance(revenue, (int, float))
            
        except Exception as e:
            self.fail(f"API endpoints test failed: {str(e)}")

class TestLandlordProperty(FrappeTestCase):
    """Test suite for Landlord Property child table"""
    
    def setUp(self):
        """Set up test data"""
        self.create_test_data()
    
    def tearDown(self):
        """Clean up test data"""
        self.cleanup_test_data()
    
    def create_test_data(self):
        """Create test data"""
        # Create test property and landlord (similar to main test)
        pass
    
    def test_property_validation(self):
        """Test property validation rules"""
        pass
    
    def test_escalation_calculation(self):
        """Test escalation calculation logic"""
        pass

class TestLandlordPaymentSchedule(FrappeTestCase):
    """Test suite for Landlord Payment Schedule"""
    
    def setUp(self):
        """Set up test data"""
        self.create_test_data()
    
    def tearDown(self):
        """Clean up test data"""
        self.cleanup_test_data()
    
    def create_test_data(self):
        """Create test data"""
        pass
    
    def test_payment_schedule_creation(self):
        """Test payment schedule creation"""
        pass
    
    def test_partial_payment_handling(self):
        """Test partial payment functionality"""
        pass
    
    def test_invoice_generation(self):
        """Test automatic invoice generation"""
        pass

class TestProperty(FrappeTestCase):
    """Test suite for Property doctype"""
    
    def setUp(self):
        """Set up test data"""
        self.create_test_data()
    
    def tearDown(self):
        """Clean up test data"""
        self.cleanup_test_data()
    
    def create_test_data(self):
        """Create test data"""
        pass
    
    def test_property_creation(self):
        """Test property creation and validation"""
        pass
    
    def test_valuation_calculation(self):
        """Test property valuation calculation"""
        pass
    
    def test_mapping_integration(self):
        """Test mapping service integration"""
        pass

class TestMaintenanceSchedule(FrappeTestCase):
    """Test suite for Maintenance Schedule"""
    
    def setUp(self):
        """Set up test data"""
        self.create_test_data()
    
    def tearDown(self):
        """Clean up test data"""
        self.cleanup_test_data()
    
    def create_test_data(self):
        """Create test data"""
        pass
    
    def test_maintenance_creation(self):
        """Test maintenance schedule creation"""
        pass
    
    def test_technician_assignment(self):
        """Test technician assignment logic"""
        pass
    
    def test_cost_calculation(self):
        """Test maintenance cost calculation"""
        pass

if __name__ == '__main__':
    unittest.main()
