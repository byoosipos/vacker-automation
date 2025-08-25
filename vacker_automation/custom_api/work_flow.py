import frappe
from frappe import _

@frappe.whitelist()
def fetch_workflow_actions(docname, doctype):
    # Fetch workflow actions directly from the database using SQL
    workflow_actions = frappe.db.sql("""
        SELECT 
            workflow_state,
            status,
            completed_by,
            completed_by_role
          
        FROM 
            `tabWorkflow Action`
        WHERE 
            reference_name = %s AND reference_doctype = %s
    """, (docname, doctype), as_dict=True)

    # Return the list of workflow actions
    return workflow_actions

