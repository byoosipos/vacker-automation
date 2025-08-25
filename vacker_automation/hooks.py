app_name = "vacker_automation"
app_title = "Vacker Automation"
app_publisher = "Vacker"
app_description = "Vacker Automation and Customizations"
app_email = "info@vacker.com"
app_license = "MIT"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/vacker_automation/css/vacker_automation.css"
app_include_js = [
    "/assets/vacker_automation/js/ai_dashboard_enhancements.js"
]

# include js, css files in header of web template
# web_include_css = "/assets/vacker_automation/css/vacker_automation.css"
# web_include_js = "/assets/vacker_automation/js/vacker_automation.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "vacker_automation/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# Note: These files are located in public/page/comprehensive_executive_dashboard/modules/
# and are loaded automatically when the comprehensive-executive-dashboard page is accessed
page_js = {
    "comprehensive-executive-dashboard": [
        "page/comprehensive_executive_dashboard/modules/styles-module.js",
        "page/comprehensive_executive_dashboard/modules/ai-chat-module.js",
        "page/comprehensive_executive_dashboard/modules/dashboard-core.js",
        "page/comprehensive_executive_dashboard/modules/overview-module.js",
        "page/comprehensive_executive_dashboard/modules/financial-module.js",
        "page/comprehensive_executive_dashboard/modules/chart-utils.js",
        "page/comprehensive_executive_dashboard/modules/operations-module.js",
        "page/comprehensive_executive_dashboard/modules/purchase-orders-module.js",
        "page/comprehensive_executive_dashboard/modules/bank-cash-module.js",
        "page/comprehensive_executive_dashboard/modules/hr-module.js",
        "page/comprehensive_executive_dashboard/modules/materials-module.js",
        "page/comprehensive_executive_dashboard/modules/projects-module.js",
        "page/comprehensive_executive_dashboard/modules/sales-module.js"
    ]
}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "vacker_automation/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "vacker_automation.utils.jinja_methods",
# 	"filters": "vacker_automation.utils.jinja_filters"
# }

# Installation
# ------------

before_install = "vacker_automation.install.before_install"
after_install = "vacker_automation.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "vacker_automation.uninstall.before_uninstall"
# after_uninstall = "vacker_automation.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "vacker_automation.utils.before_app_install"
# after_app_install = "vacker_automation.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "vacker_automation.utils.before_app_uninstall"
# after_app_uninstall = "vacker_automation.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "vacker_automation.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    # AI Risk Assessment Hooks for all enabled doctypes
    "*": {
        "before_insert": "vacker_automation.vacker_automation.doctype.ai_risk_manager.hooks_configuration.ai_before_insert",
        "validate": "vacker_automation.vacker_automation.doctype.ai_risk_manager.hooks_configuration.ai_validate",
        "before_save": "vacker_automation.vacker_automation.doctype.ai_risk_manager.hooks_configuration.ai_before_save",
        "after_insert": "vacker_automation.vacker_automation.doctype.ai_risk_manager.hooks_configuration.ai_after_insert",
        "on_submit": "vacker_automation.vacker_automation.doctype.ai_risk_manager.hooks_configuration.ai_on_submit",
        "on_cancel": "vacker_automation.vacker_automation.doctype.ai_risk_manager.hooks_configuration.ai_on_cancel"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"vacker_automation.tasks.all"
# 	],
# 	"daily": [
# 		"vacker_automation.tasks.daily"
# 	],
# 	"hourly": [
# 		"vacker_automation.tasks.hourly"
# 	],
# 	"weekly": [
# 		"vacker_automation.tasks.weekly"
# 	],
# 	"monthly": [
# 		"vacker_automation.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "vacker_automation.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "vacker_automation.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "vacker_automation.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["vacker_automation.utils.before_request"]
# after_request = ["vacker_automation.utils.after_request"]

# Job Events
# ----------
# before_job = ["vacker_automation.utils.before_job"]
# after_job = ["vacker_automation.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------
# Minimal fixtures for pages only (avoid custom field conflicts)
fixtures = [
    {"dt": "Page", "filters": [["module", "=", "Vacker Automation"]]},
]
# auth_hooks = [
# 	"vacker_automation.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Hooks for Vacker Automation

# Auto-update payment schedules when purchase invoices are paid
on_update_after_submit = [
    "vacker_automation.vacker_automation.hooks.update_payment_schedule_on_invoice_payment"
]

# Update payment schedules when invoices are paid
def update_payment_schedule_on_invoice_payment(doc, method):
    """Update payment schedule when purchase invoice is paid"""
    if doc.doctype == "Purchase Invoice" and doc.status == "Paid":
        try:
            # Check if this invoice is linked to a payment schedule
            if hasattr(doc, 'landlord_payment_schedule') and doc.landlord_payment_schedule:
                payment_schedule = frappe.get_doc("Landlord Payment Schedule", doc.landlord_payment_schedule)
                payment_schedule.update_payment_status_from_invoice()
                frappe.msgprint(f"Payment schedule {payment_schedule.name} updated with payment details")
        except Exception as e:
            frappe.log_error(f"Error updating payment schedule for invoice {doc.name}: {str(e)}")

# In vacker_automation/hooks.py

override_whitelisted_methods = {
    # ... other overrides
}

# Add this line to expose your endpoint
doc_events = {
    # ... other doc events
}

# Add this line to expose your endpoint
app_include_js = []
app_include_css = []

# Add this to expose the endpoint
override_whitelisted_methods.update({
    "vacker_automation.mobile_app_api.project_dashboard.get_project_dashboard": "vacker_automation.mobile_app_api.project_dashboard.get_project_dashboard"
})