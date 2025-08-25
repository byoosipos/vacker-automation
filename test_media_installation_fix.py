#!/usr/bin/env python3
"""
Test script to verify Media Installation functionality after fixes
"""

import frappe
import sys
import os

# Add the vacker directory to Python path
sys.path.append('/home/byoosi/vacker')

def test_media_installation_creation():
    """Test creating a Media Installation record"""
    try:
        # Create a test Media Installation
        media_installation = frappe.new_doc("Media Installation")
        media_installation.installation_id = "TEST-001"
        media_installation.landlord = "Test Landlord"
        media_installation.property = "Test Property"
        media_installation.project = "Test Project"
        media_installation.customer = "Test Customer"
        media_installation.rental_start_date = "2025-01-01"
        media_installation.rental_end_date = "2025-12-31"
        media_installation.rental_amount = 1000.00
        media_installation.rental_frequency = "Monthly"
        media_installation.installation_date = "2025-01-01"
        media_installation.installation_status = "Completed"
        
        # Save the document
        media_installation.save()
        
        print("✅ Media Installation created successfully!")
        print(f"   Installation ID: {media_installation.installation_id}")
        print(f"   Name: {media_installation.name}")
        
        # Check if customer invoicing schedules were created
        customer_schedules = frappe.get_all("Customer Invoicing Schedule", 
                                          filters={"media_installation": media_installation.name},
                                          fields=["name", "due_date", "amount", "status"])
        
        print(f"✅ Created {len(customer_schedules)} customer invoicing schedules")
        
        # Check if rental history was updated
        if media_installation.rental_history:
            print(f"✅ Rental history updated with {len(media_installation.rental_history)} entries")
        
        # Clean up - delete the test record
        frappe.delete_doc("Media Installation", media_installation.name)
        print("✅ Test record cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating Media Installation: {str(e)}")
        return False

def test_customer_invoicing_schedule_standalone():
    """Test creating a standalone Customer Invoicing Schedule"""
    try:
        # Create a standalone Customer Invoicing Schedule
        customer_schedule = frappe.new_doc("Customer Invoicing Schedule")
        customer_schedule.customer = "Test Customer"
        customer_schedule.media_installation = "TEST-MEDIA-001"
        customer_schedule.property = "Test Property"
        customer_schedule.due_date = "2025-01-01"
        customer_schedule.amount = 1000.00
        customer_schedule.status = "Pending"
        
        # Save the document
        customer_schedule.save()
        
        print("✅ Standalone Customer Invoicing Schedule created successfully!")
        print(f"   Name: {customer_schedule.name}")
        
        # Clean up
        frappe.delete_doc("Customer Invoicing Schedule", customer_schedule.name)
        print("✅ Test record cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating Customer Invoicing Schedule: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Media Installation functionality after fixes...")
    print("=" * 60)
    
    # Test 1: Media Installation creation
    print("\n1. Testing Media Installation creation:")
    test1_result = test_media_installation_creation()
    
    # Test 2: Standalone Customer Invoicing Schedule
    print("\n2. Testing standalone Customer Invoicing Schedule:")
    test2_result = test_customer_invoicing_schedule_standalone()
    
    print("\n" + "=" * 60)
    if test1_result and test2_result:
        print("🎉 All tests passed! The fixes are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.") 