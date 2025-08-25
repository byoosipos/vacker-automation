import frappe
from frappe import _

def before_install():
    """Setup before installing the app"""
    pass

def after_install():
    """Setup after installing the app"""
    create_dashboard_permissions()
    create_custom_roles()
    frappe.db.commit()

def create_dashboard_permissions():
    """Create necessary permissions for dashboard access"""
    
    # Define roles that should have access to the comprehensive dashboard
    dashboard_roles = [
        "System Manager",
        "CEO", 
        "Directors",
        "General Manager",
        "Accounts Manager",
        "Projects Manager"
    ]
    
    # Create roles if they don't exist
    for role_name in dashboard_roles:
        if not frappe.db.exists("Role", role_name):
            role = frappe.new_doc("Role")
            role.role_name = role_name
            role.description = f"Role for {role_name} with dashboard access"
            role.save(ignore_permissions=True)

def create_custom_roles():
    """Create custom roles specific to Vacker Automation"""
    
    custom_roles = [
        {
            "role_name": "Executive Dashboard User",
            "description": "Users who can access the comprehensive executive dashboard"
        },
        {
            "role_name": "Financial Analyst",
            "description": "Users who can access financial analytics and reports"
        },
        {
            "role_name": "Operations Manager",
            "description": "Users who can access operational analytics and reports"
        }
    ]
    
    for role_data in custom_roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.new_doc("Role")
            role.role_name = role_data["role_name"]
            role.description = role_data["description"]
            role.save(ignore_permissions=True)

def setup_default_permissions():
    """Setup default permissions for dashboard-related doctypes"""
    
    # Define permission mappings
    permission_maps = [
        {
            "doctype": "Material Request",
            "roles": ["Executive Dashboard User", "Operations Manager"],
            "permissions": ["read"]
        },
        {
            "doctype": "Project",
            "roles": ["Executive Dashboard User", "Projects Manager"],
            "permissions": ["read"]
        },
        {
            "doctype": "GL Entry",
            "roles": ["Executive Dashboard User", "Financial Analyst"],
            "permissions": ["read"]
        }
    ]
    
    for perm_map in permission_maps:
        for role in perm_map["roles"]:
            if frappe.db.exists("Role", role):
                for permission in perm_map["permissions"]:
                    # Check if permission already exists
                    existing_perm = frappe.db.exists("Custom DocPerm", {
                        "parent": perm_map["doctype"],
                        "role": role,
                        permission: 1
                    })
                    
                    if not existing_perm:
                        # Create new permission
                        doc_perm = frappe.new_doc("Custom DocPerm")
                        doc_perm.parent = perm_map["doctype"]
                        doc_perm.role = role
                        doc_perm.read = 1 if permission == "read" else 0
                        doc_perm.write = 1 if permission == "write" else 0
                        doc_perm.create = 1 if permission == "create" else 0
                        doc_perm.delete = 1 if permission == "delete" else 0
                        doc_perm.save(ignore_permissions=True)

def install_required_packages():
    """Install required Python packages for dashboard functionality"""
    
    import subprocess
    import sys
    
    required_packages = [
        "pandas",
        "openpyxl", 
        "xlsxwriter"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            frappe.msgprint(f"Installing required package: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def create_dashboard_workspace():
    """Create a workspace for executive dashboard access"""
    
    workspace_name = "Executive Dashboard"
    
    if not frappe.db.exists("Workspace", workspace_name):
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

def setup_dashboard_settings():
    """Setup dashboard-specific settings and configurations"""
    
    # Create dashboard settings doctype if needed
    settings_name = "Executive Dashboard Settings"
    
    if not frappe.db.exists("Singles", settings_name):
        # Create basic settings document
        settings = frappe.new_doc("DocType")
        settings.name = settings_name
        settings.module = "Vacker Automation"
        settings.issingle = 1
        settings.description = "Settings for Executive Dashboard configuration"
        
        # Add basic fields
        settings.append("fields", {
            "fieldname": "default_company",
            "fieldtype": "Link",
            "options": "Company",
            "label": "Default Company"
        })
        
        settings.append("fields", {
            "fieldname": "refresh_interval",
            "fieldtype": "Int",
            "label": "Auto Refresh Interval (seconds)",
            "default": 300
        })
        
        settings.append("fields", {
            "fieldname": "enable_notifications",
            "fieldtype": "Check",
            "label": "Enable Critical Alerts",
            "default": 1
        })
        
        settings.save(ignore_permissions=True)

def clear_cache_and_rebuild():
    """Clear cache and rebuild to ensure changes take effect"""
    
    frappe.clear_cache()
    frappe.reload_doc("core", "doctype", "page")
    
    # Rebuild website if needed
    try:
        from frappe.website.utils import clear_cache
        clear_cache()
    except ImportError:
        pass 