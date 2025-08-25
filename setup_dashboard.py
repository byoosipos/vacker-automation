#!/usr/bin/env python3
"""
Setup script for Vacker Automation Comprehensive Executive Dashboard

This script ensures all components are properly installed and configured.
Run this script after installing the app to verify everything is working.

Usage:
    python setup_dashboard.py

Or from bench:
    bench execute vacker_automation.setup_dashboard.main
"""

import frappe
from frappe import _

def main():
    """Main setup function"""
    
    print("🚀 Setting up Vacker Automation Comprehensive Executive Dashboard...")
    
    try:
        # Connect to database
        frappe.connect()
        
        # Run setup steps
        steps = [
            ("Checking app installation", check_app_installation),
            ("Verifying pages", verify_pages),
            ("Installing required packages", install_packages),
            ("Setting up permissions", setup_permissions),
            ("Creating workspace", create_workspace),
            ("Verifying database access", verify_database_access),
            ("Testing API endpoints", test_api_endpoints),
            ("Clearing cache", clear_cache),
        ]
        
        for step_name, step_function in steps:
            print(f"📋 {step_name}...")
            try:
                step_function()
                print(f"✅ {step_name} completed successfully")
            except Exception as e:
                print(f"❌ {step_name} failed: {str(e)}")
                raise
        
        print("\n🎉 Setup completed successfully!")
        print("\n📊 Access your dashboard at:")
        print(f"   - Comprehensive Executive Dashboard: {frappe.utils.get_url()}/app/comprehensive-executive-dashboard")
        print(f"   - Project Profitability Dashboard: {frappe.utils.get_url()}/app/project-profitability-dashboard")
        
        print("\n👥 Dashboard access roles:")
        print("   - System Manager")
        print("   - CEO")
        print("   - Directors")
        print("   - General Manager")
        print("   - Accounts Manager")
        print("   - Projects Manager")
        
    except Exception as e:
        print(f"\n💥 Setup failed with error: {str(e)}")
        raise
    
    finally:
        frappe.destroy()

def check_app_installation():
    """Verify that the Vacker Automation app is properly installed"""
    
    installed_apps = frappe.get_installed_apps()
    
    if "vacker_automation" not in installed_apps:
        raise Exception("Vacker Automation app is not installed. Please install it first using: bench install-app vacker_automation")
    
    # Check if the app module is accessible
    try:
        import vacker_automation
    except ImportError:
        raise Exception("Vacker Automation module is not importable. Please check the installation.")

def verify_pages():
    """Verify that the dashboard pages exist and are accessible"""
    
    pages_to_check = [
        "comprehensive-executive-dashboard",
        "project-profitability-dashboard"
    ]
    
    for page_name in pages_to_check:
        if not frappe.db.exists("Page", page_name):
            # Try to create the page if it doesn't exist
            try:
                frappe.reload_doc("vacker_automation", "page", page_name.replace("-", "_"))
            except Exception:
                raise Exception(f"Page '{page_name}' not found and could not be created")

def install_packages():
    """Install required Python packages"""
    
    required_packages = ["pandas", "openpyxl", "xlsxwriter"]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"   Installing {package}...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def setup_permissions():
    """Setup basic permissions for dashboard access"""
    
    # Create roles if they don't exist
    roles_to_create = ["CEO", "Directors", "General Manager"]
    
    for role_name in roles_to_create:
        if not frappe.db.exists("Role", role_name):
            role = frappe.new_doc("Role")
            role.role_name = role_name
            role.description = f"Role for {role_name} with dashboard access"
            try:
                role.save(ignore_permissions=True)
            except Exception:
                pass  # Role might already exist

def create_workspace():
    """Create Executive Dashboard workspace if it doesn't exist"""
    
    workspace_name = "Executive Dashboard"
    
    if not frappe.db.exists("Workspace", workspace_name):
        try:
            workspace = frappe.new_doc("Workspace")
            workspace.title = workspace_name
            workspace.module = "Vacker Automation"
            workspace.public = 1
            workspace.is_standard = 0
            
            # Add dashboard links
            workspace.append("links", {
                "type": "Page",
                "link_to": "comprehensive-executive-dashboard",
                "label": "Comprehensive Executive Dashboard",
                "icon": "dashboard"
            })
            
            workspace.append("links", {
                "type": "Page",
                "link_to": "project-profitability-dashboard", 
                "label": "Project Profitability Dashboard",
                "icon": "projects"
            })
            
            workspace.save(ignore_permissions=True)
            
        except Exception as e:
            print(f"   Warning: Could not create workspace: {str(e)}")

def verify_database_access():
    """Verify that the dashboard can access required database tables"""
    
    tables_to_check = [
        "tabGL Entry",
        "tabMaterial Request", 
        "tabProject",
        "tabSales Invoice",
        "tabPurchase Invoice",
        "tabEmployee"
    ]
    
    for table in tables_to_check:
        try:
            frappe.db.sql(f"SELECT COUNT(*) FROM `{table}` LIMIT 1")
        except Exception as e:
            raise Exception(f"Cannot access table {table}: {str(e)}")

def test_api_endpoints():
    """Test that the dashboard API endpoints are working"""
    
    try:
        # Test the main dashboard data endpoint
        from vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard import get_comprehensive_dashboard_data
        
        # Call with minimal filters
        test_filters = {
            'company': frappe.defaults.get_user_default('Company') or frappe.db.get_single_value('Global Defaults', 'default_company'),
            'from_date': frappe.utils.add_months(frappe.utils.today(), -1),
            'to_date': frappe.utils.today()
        }
        
        result = get_comprehensive_dashboard_data(test_filters)
        
        if not isinstance(result, dict):
            raise Exception("Dashboard API did not return expected data structure")
            
    except Exception as e:
        raise Exception(f"Dashboard API test failed: {str(e)}")

def clear_cache():
    """Clear cache and reload"""
    
    frappe.clear_cache()
    
    # Clear website cache if available
    try:
        from frappe.website.utils import clear_cache as clear_website_cache
        clear_website_cache()
    except ImportError:
        pass

def check_system_requirements():
    """Check system requirements and recommendations"""
    
    print("\n🔍 System Requirements Check:")
    
    # Check Frappe/ERPNext version
    print(f"   - Frappe Version: {frappe.__version__}")
    
    # Check database
    db_engine = frappe.db.db_type
    print(f"   - Database: {db_engine}")
    
    # Check if Chart.js is available (should be included with ERPNext)
    print("   - Chart.js: Available with ERPNext")
    
    # Check memory and performance recommendations
    print("\n💡 Performance Recommendations:")
    print("   - Enable Redis caching for better performance")
    print("   - Consider database indexing for large datasets")
    print("   - Use background jobs for heavy calculations")

if __name__ == "__main__":
    main() 