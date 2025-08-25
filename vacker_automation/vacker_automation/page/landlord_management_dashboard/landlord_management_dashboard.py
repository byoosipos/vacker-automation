import frappe
from frappe import _
from frappe.utils import today, getdate, add_months, add_days
import json

def get_context(context):
    """Get context for the dashboard"""
    context.no_cache = 1
    context.title = _("Landlord Management Dashboard")
    
    # Get dashboard data
    context.dashboard_data = get_dashboard_data()

def get_dashboard_data():
    """Get comprehensive dashboard data"""
    return {
        "summary": get_summary_data(),
        "charts": get_chart_data(),
        "recent_activities": get_recent_activities(),
        "upcoming_payments": get_upcoming_payments(),
        "contract_expiries": get_contract_expiries(),
        "maintenance_schedules": get_maintenance_schedules(),
        "top_landlords": get_top_landlords()
    }

def get_summary_data():
    """Get summary statistics"""
    try:
        # Total landlords (submitted)
        total_landlords = frappe.db.count("Landlord", {"docstatus": 1})
        frappe.logger().info(f"Total landlords: {total_landlords}")
        
        # Active landlords (have active contracts)
        active_landlords = frappe.db.sql("""
            SELECT COUNT(DISTINCT l.name) 
            FROM `tabLandlord` l
            JOIN `tabLandlord Property` lp ON l.name = lp.parent
            WHERE l.docstatus = 1 
            AND lp.contract_end_date >= %s
            AND lp.status = 'Active'
        """, today())[0][0] or 0
        frappe.logger().info(f"Active landlords: {active_landlords}")
        
        total_properties = frappe.db.count("Property")
        occupied_properties = frappe.db.count("Property", {"property_status": "Occupied"})
        
        # Calculate monthly rental income from active contracts
        monthly_income = frappe.db.sql("""
            SELECT SUM(lp.rental_amount) 
            FROM `tabLandlord` l
            JOIN `tabLandlord Property` lp ON l.name = lp.parent
            WHERE l.docstatus = 1 
            AND lp.contract_end_date >= %s
            AND lp.status = 'Active'
            AND lp.payment_frequency = 'Monthly'
        """, today())[0][0] or 0
        frappe.logger().info(f"Monthly income: {monthly_income}")
        
        quarterly_income = frappe.db.sql("""
            SELECT SUM(lp.rental_amount) 
            FROM `tabLandlord` l
            JOIN `tabLandlord Property` lp ON l.name = lp.parent
            WHERE l.docstatus = 1 
            AND lp.contract_end_date >= %s
            AND lp.status = 'Active'
            AND lp.payment_frequency = 'Quarterly'
        """, today())[0][0] or 0
        frappe.logger().info(f"Quarterly income: {quarterly_income}")
        
        annual_income = frappe.db.sql("""
            SELECT SUM(lp.rental_amount) 
            FROM `tabLandlord` l
            JOIN `tabLandlord Property` lp ON l.name = lp.parent
            WHERE l.docstatus = 1 
            AND lp.contract_end_date >= %s
            AND lp.status = 'Active'
            AND lp.payment_frequency = 'Annually'
        """, today())[0][0] or 0
        frappe.logger().info(f"Annual income: {annual_income}")
        
        total_monthly_income = monthly_income + (quarterly_income / 3) + (annual_income / 12)
        frappe.logger().info(f"Total monthly income: {total_monthly_income}")
        
        # Get overdue payments
        overdue_payments = frappe.db.count("Landlord Payment Schedule", {
            "status": "Overdue"
        })
        frappe.logger().info(f"Overdue payments: {overdue_payments}")
        
        # Get contracts expiring this month
        contracts_expiring = frappe.db.sql("""
            SELECT COUNT(*) 
            FROM `tabLandlord` l
            JOIN `tabLandlord Property` lp ON l.name = lp.parent
            WHERE l.docstatus = 1
            AND lp.contract_end_date BETWEEN %s AND %s
            AND lp.status = 'Active'
        """, [today(), add_months(today(), 1)])[0][0] or 0
        frappe.logger().info(f"Contracts expiring: {contracts_expiring}")
        
        summary_data = {
            "total_landlords": total_landlords,
            "active_landlords": active_landlords,
            "total_properties": total_properties,
            "occupied_properties": occupied_properties,
            "monthly_income": total_monthly_income,
            "overdue_payments": overdue_payments,
            "contracts_expiring": contracts_expiring
        }
        
        frappe.logger().info(f"Summary data: {summary_data}")
        return summary_data
        
    except Exception as e:
        frappe.logger().error(f"Error in get_summary_data: {str(e)}")
        raise

def get_chart_data():
    """Get chart data for dashboard"""
    try:
        # Revenue by landlord type
        revenue_by_type = frappe.db.sql("""
            SELECT 
                l.landlord_type,
                SUM(CASE 
                    WHEN lp.payment_frequency = 'Monthly' THEN lp.rental_amount * 12
                    WHEN lp.payment_frequency = 'Quarterly' THEN lp.rental_amount * 4
                    WHEN lp.payment_frequency = 'Annually' THEN lp.rental_amount
                    ELSE 0
                END) as annual_revenue
            FROM `tabLandlord` l
            JOIN `tabLandlord Property` lp ON l.name = lp.parent
            WHERE l.docstatus = 1 
            AND lp.contract_end_date >= %s
            AND lp.status = 'Active'
            GROUP BY l.landlord_type
        """, today(), as_dict=1)
        frappe.logger().info(f"Revenue by type: {revenue_by_type}")
        
        # Revenue by media type
        revenue_by_media = frappe.db.sql("""
            SELECT 
                lp.media_type,
                SUM(CASE 
                    WHEN lp.payment_frequency = 'Monthly' THEN lp.rental_amount * 12
                    WHEN lp.payment_frequency = 'Quarterly' THEN lp.rental_amount * 4
                    WHEN lp.payment_frequency = 'Annually' THEN lp.rental_amount
                    ELSE 0
                END) as annual_revenue
            FROM `tabLandlord` l
            JOIN `tabLandlord Property` lp ON l.name = lp.parent
            WHERE l.docstatus = 1 
            AND lp.contract_end_date >= %s
            AND lp.status = 'Active'
            GROUP BY lp.media_type
        """, today(), as_dict=1)
        frappe.logger().info(f"Revenue by media: {revenue_by_media}")
        
        # Property status distribution
        property_status = frappe.db.sql("""
            SELECT property_status, COUNT(*) as count
            FROM `tabProperty`
            GROUP BY property_status
        """, as_dict=1)
        frappe.logger().info(f"Property status: {property_status}")
        
        chart_data = {
            "revenue_by_type": revenue_by_type,
            "revenue_by_media": revenue_by_media,
            "property_status": property_status
        }
        
        frappe.logger().info(f"Chart data: {chart_data}")
        return chart_data
        
    except Exception as e:
        frappe.logger().error(f"Error in get_chart_data: {str(e)}")
        raise

def get_recent_activities():
    """Get recent activities"""
    recent_landlords = frappe.db.sql("""
        SELECT name, full_legal_name, date_of_onboarding, landlord_type
        FROM `tabLandlord`
        WHERE docstatus = 1
        ORDER BY creation DESC
        LIMIT 5
    """, as_dict=1)
    
    recent_payments = frappe.db.sql("""
        SELECT lps.name, lps.landlord, lps.property, lps.amount, lps.payment_date
        FROM `tabLandlord Payment Schedule` lps
        WHERE lps.status = 'Paid'
        ORDER BY lps.payment_date DESC
        LIMIT 5
    """, as_dict=1)
    
    return {
        "recent_landlords": recent_landlords,
        "recent_payments": recent_payments
    }

def get_upcoming_payments():
    """Get upcoming payments"""
    upcoming_payments = frappe.db.sql("""
        SELECT 
            lps.name,
            lps.landlord,
            lps.property,
            lps.amount,
            lps.due_date,
            l.full_legal_name
        FROM `tabLandlord Payment Schedule` lps
        JOIN `tabLandlord` l ON lps.landlord = l.name
        WHERE lps.status = 'Pending'
        AND lps.due_date BETWEEN %s AND %s
        ORDER BY lps.due_date ASC
        LIMIT 10
    """, [today(), add_months(today(), 1)], as_dict=1)
    
    return upcoming_payments

def get_contract_expiries():
    """Get contracts expiring soon"""
    expiring_contracts = frappe.db.sql("""
        SELECT 
            l.name,
            l.full_legal_name,
            lp.property,
            lp.contract_end_date,
            lp.rental_amount,
            lp.media_type
        FROM `tabLandlord` l
        JOIN `tabLandlord Property` lp ON l.name = lp.parent
        WHERE l.docstatus = 1
        AND lp.contract_end_date BETWEEN %s AND %s
        AND lp.status = 'Active'
        ORDER BY lp.contract_end_date ASC
        LIMIT 10
    """, [today(), add_months(today(), 3)], as_dict=1)
    
    return expiring_contracts

def get_maintenance_schedules():
    """Get upcoming maintenance schedules"""
    maintenance_schedules = frappe.db.sql("""
        SELECT 
            ms.name,
            ms.landlord,
            ms.property,
            ms.scheduled_date,
            ms.maintenance_type,
            l.full_legal_name
        FROM `tabMaintenance Schedule` ms
        JOIN `tabLandlord` l ON ms.landlord = l.name
        WHERE ms.status = 'Scheduled'
        AND ms.scheduled_date BETWEEN %s AND %s
        ORDER BY ms.scheduled_date ASC
        LIMIT 10
    """, [today(), add_months(today(), 1)], as_dict=1)
    
    return maintenance_schedules

def get_top_landlords():
    """Get top landlords by revenue"""
    top_landlords = frappe.db.sql("""
        SELECT 
            l.name,
            l.full_legal_name,
            SUM(CASE 
                WHEN lp.payment_frequency = 'Monthly' THEN lp.rental_amount * 12
                WHEN lp.payment_frequency = 'Quarterly' THEN lp.rental_amount * 4
                WHEN lp.payment_frequency = 'Annually' THEN lp.rental_amount
                ELSE 0
            END) as annual_revenue,
            COUNT(lp.property) as property_count
        FROM `tabLandlord` l
        JOIN `tabLandlord Property` lp ON l.name = lp.parent
        WHERE l.docstatus = 1 
        AND lp.contract_end_date >= %s
        AND lp.status = 'Active'
        GROUP BY l.name, l.full_legal_name
        ORDER BY annual_revenue DESC
        LIMIT 10
    """, today(), as_dict=1)
    
    return top_landlords

@frappe.whitelist()
def get_dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        dashboard_data = get_dashboard_data()
        frappe.logger().info(f"Dashboard data: {dashboard_data}")
        return dashboard_data
    except Exception as e:
        frappe.logger().error(f"Error getting dashboard stats: {str(e)}")
        frappe.throw(f"Error getting dashboard stats: {str(e)}")

@frappe.whitelist()
def get_landlord_details(landlord_name):
    """Get detailed landlord information"""
    landlord = frappe.get_doc("Landlord", landlord_name)
    return landlord.get_landlord_summary()

@frappe.whitelist()
def get_property_details(property_name):
    """Get detailed property information"""
    property_doc = frappe.get_doc("Property", property_name)
    return property_doc.get_property_details() 