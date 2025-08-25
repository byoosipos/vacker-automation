#!/usr/bin/env python3
"""
Test script to check landlord method accessibility
"""

import frappe

def test_landlord_method():
    """Test if the get_payment_schedule_summary method exists"""
    try:
        # Get the first landlord
        landlords = frappe.get_all("Landlord", limit=1)
        if not landlords:
            print("No landlords found in the system")
            return
        
        landlord_name = landlords[0].name
        print(f"Testing with landlord: {landlord_name}")
        
        # Get the landlord document
        landlord = frappe.get_doc("Landlord", landlord_name)
        print(f"Landlord loaded: {landlord.name}")
        
        # Check if method exists
        if hasattr(landlord, 'get_payment_schedule_summary'):
            print("✅ Method get_payment_schedule_summary exists")
            
            # Try to call the method
            try:
                result = landlord.get_payment_schedule_summary()
                print(f"✅ Method call successful: {result}")
            except Exception as e:
                print(f"❌ Method call failed: {str(e)}")
        else:
            print("❌ Method get_payment_schedule_summary does not exist")
            
            # List all methods
            methods = [method for method in dir(landlord) if not method.startswith('_')]
            print(f"Available methods: {methods}")
            
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")

if __name__ == "__main__":
    test_landlord_method() 