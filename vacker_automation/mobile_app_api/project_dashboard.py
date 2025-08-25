# File: vacker_automation/mobile_app_api/project_dashboard.py

import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_project_dashboard():
    # Fetch all projects with relevant fields
    projects = frappe.get_all(
        "Project",
        fields=[
            "name",
            "project_name",
            "status",
            "customer",
            "expected_end_date",
            "percent_complete",
            "priority",
            "modified"
        ],
        order_by="modified desc"
    )

    # Get all material requests linked to projects
    material_requests = frappe.get_all(
        "Material Request",
        fields=["name", "project"]
    )

    # Count material requests per project
    mr_count_map = {}
    for mr in material_requests:
        project = mr.get("project")
        if project:
            mr_count_map[project] = mr_count_map.get(project, 0) + 1

    # Add material request count to each project
    for project in projects:
        project["material_request_count"] = mr_count_map.get(project["name"], 0)

    return {
        "status": "success",
        "data": projects
    }