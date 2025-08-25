import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, add_months, nowdate, get_first_day, get_last_day
import json
import logging

@frappe.whitelist()
def get_dashboard_data(filters=None):
    """Main method to get comprehensive project profitability data"""
    
    if not filters:
        filters = {}
    
    # Parse filters if it's a JSON string
    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except (json.JSONDecodeError, ValueError):
            filters = {}
    
    # Set default filters
    if not filters.get('company'):
        filters['company'] = frappe.defaults.get_user_default('Company')
    
    if not filters.get('from_date'):
        filters['from_date'] = get_first_day(add_months(nowdate(), -12))
    
    if not filters.get('to_date'):
        filters['to_date'] = get_last_day(nowdate())
    
    data = {
        'summary': get_profitability_summary(filters),
        'projects': get_project_profitability_data(filters),
        'trends': get_profitability_trends(filters),
        'cost_breakdown': get_cost_breakdown_analysis(filters),
        'performance_metrics': get_performance_metrics(filters)
    }
    
    return data

@frappe.whitelist()
def get_profitability_summary(filters):
    """Get high-level profitability summary for executive dashboard"""
    
    # Parse filters if it's a JSON string
    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except (json.JSONDecodeError, ValueError):
            filters = {}
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Total Contract Value
    total_contract_value = frappe.db.sql("""
        SELECT SUM(p.total_sales_amount)
        FROM `tabProject` p
        WHERE p.company = %(company)s
        AND p.expected_start_date >= %(from_date)s
        AND p.expected_start_date <= %(to_date)s
        AND p.status != 'Cancelled'
    """, {'company': company, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
    
    # Total Revenue Recognized (from Sales Invoices)
    total_revenue = frappe.db.sql("""
        SELECT SUM(si.base_grand_total)
        FROM `tabSales Invoice` si
        WHERE si.company = %(company)s
        AND si.project IS NOT NULL
        AND si.posting_date >= %(from_date)s
        AND si.posting_date <= %(to_date)s
        AND si.docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
    
    # Total Costs (Material + Labor + Other)
    total_costs = get_total_project_costs(filters)
    
    # Calculate metrics
    gross_profit = flt(total_revenue) - flt(total_costs)
    profit_margin = (flt(gross_profit) / flt(total_revenue) * 100) if total_revenue else 0
    
    # Active Projects Count
    active_projects = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabProject` p
        WHERE p.company = %(company)s
        AND p.status IN ('Open', 'In Progress')
        AND p.expected_start_date >= %(from_date)s
        AND p.expected_start_date <= %(to_date)s
    """, {'company': company, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
    
    return {
        'total_contract_value': flt(total_contract_value, 2),
        'total_revenue': flt(total_revenue, 2),
        'total_costs': flt(total_costs, 2),
        'gross_profit': flt(gross_profit, 2),
        'profit_margin': flt(profit_margin, 2),
        'active_projects': cint(active_projects),
        'avg_project_value': flt(total_contract_value / active_projects, 2) if active_projects else 0
    }

def get_total_project_costs(filters):
    """Calculate total project costs from various sources"""
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Material Costs (from Purchase Invoices)
    material_costs = frappe.db.sql("""
        SELECT SUM(pi.base_grand_total)
        FROM `tabPurchase Invoice` pi
        WHERE pi.company = %(company)s
        AND pi.project IS NOT NULL
        AND pi.posting_date >= %(from_date)s
        AND pi.posting_date <= %(to_date)s
        AND pi.docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
    
    # Labor Costs (from Timesheets)
    labor_costs = frappe.db.sql("""
        SELECT SUM(td.base_costing_amount)
        FROM `tabTimesheet Detail` td
        JOIN `tabTimesheet` t ON td.parent = t.name
        WHERE t.company = %(company)s
        AND td.project IS NOT NULL
        AND t.start_date >= %(from_date)s
        AND t.start_date <= %(to_date)s
        AND t.docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
    
    # Other Expenses (from Expense Claims)
    other_expenses = frappe.db.sql("""
        SELECT SUM(ec.grand_total)
        FROM `tabExpense Claim` ec
        WHERE ec.company = %(company)s
        AND ec.project IS NOT NULL
        AND ec.posting_date >= %(from_date)s
        AND ec.posting_date <= %(to_date)s
        AND ec.docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
    
    return flt(material_costs) + flt(labor_costs) + flt(other_expenses)

@frappe.whitelist()
def get_project_profitability_data(filters):
    """Get detailed profitability data for each project
    - Includes projects that are active or have financial activity in the date range.
    - If 'all_projects' is set, includes all projects for the company.
    - Adds error handling and audit logging for data access.
    """
    try:
        # Parse filters if it's a JSON string
        if isinstance(filters, str):
            try:
                filters = json.loads(filters)
            except (json.JSONDecodeError, ValueError):
                filters = {}
        
        company = filters.get('company')
        from_date = filters.get('from_date')
        to_date = filters.get('to_date')
        project_filter = filters.get('project')
        all_projects = filters.get('all_projects', False)
        
        # Build project selection logic
        conditions = ["p.company = %(company)s", "p.status != 'Cancelled'"]
        values = {'company': company, 'from_date': from_date, 'to_date': to_date}
        
        if project_filter:
            conditions.append("p.name = %(project)s")
            values['project'] = project_filter
        
        if not all_projects:
            # Include projects that are:
            # - Active (Open, In Progress), or
            # - Have activity in the date range
            conditions.append("(" \
                "p.status IN ('Open', 'In Progress') "
                "OR EXISTS (SELECT 1 FROM `tabSales Invoice` si WHERE si.project = p.name AND si.docstatus = 1 AND si.posting_date >= %(from_date)s AND si.posting_date <= %(to_date)s) "
                "OR EXISTS (SELECT 1 FROM `tabPurchase Invoice` pi WHERE pi.project = p.name AND pi.docstatus = 1 AND pi.posting_date >= %(from_date)s AND pi.posting_date <= %(to_date)s) "
                "OR EXISTS (SELECT 1 FROM `tabTimesheet Detail` td JOIN `tabTimesheet` t ON td.parent = t.name WHERE td.project = p.name AND t.docstatus = 1 AND t.start_date >= %(from_date)s AND t.start_date <= %(to_date)s) "
                "OR EXISTS (SELECT 1 FROM `tabExpense Claim` ec WHERE ec.project = p.name AND ec.docstatus = 1 AND ec.posting_date >= %(from_date)s AND ec.posting_date <= %(to_date)s) "
            ")")
        # else: show all projects for the company
        
        where_clause = " AND ".join(conditions)
        
        # --- DB Index Recommendation ---
        # For performance, add indexes on:
        #   tabProject(company, status, expected_start_date)
        #   tabSales Invoice(project, posting_date, docstatus)
        #   tabPurchase Invoice(project, posting_date, docstatus)
        #   tabTimesheet Detail(project)
        #   tabExpense Claim(project, posting_date, docstatus)
        # -------------------------------
        
        projects = frappe.db.sql(f"""
            SELECT 
                p.name,
                p.project_name,
                p.customer,
                p.status,
                p.percent_complete,
                p.expected_start_date,
                p.expected_end_date,
                p.total_sales_amount as contract_value,
                p.estimated_costing as estimated_cost,
                p.priority
            FROM `tabProject` p
            WHERE {where_clause}
            ORDER BY p.expected_start_date DESC
        """, values, as_dict=True)
        
        # Enrich with financial data
        for project in projects:
            project.update(get_project_financial_details(project.name, filters))
            # Calculate derived metrics
            project['gross_profit'] = flt(project.get('total_revenue', 0)) - flt(project.get('total_costs', 0))
            project['profit_margin'] = (flt(project['gross_profit']) / flt(project.get('total_revenue', 0)) * 100) if project.get('total_revenue') else 0
            project['cost_variance'] = flt(project.get('total_costs', 0)) - flt(project.get('estimated_cost', 0))
            project['cost_variance_percent'] = (flt(project['cost_variance']) / flt(project.get('estimated_cost', 0)) * 100) if project.get('estimated_cost') else 0
            # Project health indicator
            project['health_indicator'] = get_project_health_indicator(project)
        
        # Audit log for dashboard access
        frappe.logger().info(f"User {frappe.session.user} accessed project profitability dashboard with filters: {filters}")
        return projects
    except Exception as e:
        logging.exception("Error in get_project_profitability_data")
        frappe.log_error(f"Dashboard error: {str(e)}", "Project Profitability Dashboard")
        frappe.throw(_(f"Error loading project profitability data: {str(e)}"))

def get_project_financial_details(project_name, filters):
    """Get detailed financial information for a specific project"""
    
    # Revenue from Sales Invoices
    revenue_data = frappe.db.sql("""
        SELECT 
            SUM(si.base_grand_total) as total_revenue,
            COUNT(si.name) as invoice_count
        FROM `tabSales Invoice` si
        WHERE si.project = %(project)s
        AND si.docstatus = 1
        AND si.posting_date >= %(from_date)s
        AND si.posting_date <= %(to_date)s
    """, {'project': project_name, 'from_date': filters.get('from_date'), 'to_date': filters.get('to_date')}, as_dict=True)
    
    # Costs breakdown
    costs_data = get_project_costs_breakdown(project_name, filters)
    
    # Combine data
    financial_data = {
        'total_revenue': revenue_data[0].get('total_revenue', 0) if revenue_data else 0,
        'invoice_count': revenue_data[0].get('invoice_count', 0) if revenue_data else 0,
        'total_costs': sum(costs_data.values()),
        'material_costs': costs_data.get('material_costs', 0),
        'labor_costs': costs_data.get('labor_costs', 0),
        'other_expenses': costs_data.get('other_expenses', 0)
    }
    
    return financial_data

def get_project_costs_breakdown(project_name, filters):
    """Get detailed cost breakdown for a project"""
    
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Material costs
    material_costs = frappe.db.sql("""
        SELECT SUM(pi.base_grand_total)
        FROM `tabPurchase Invoice` pi
        WHERE pi.project = %(project)s
        AND pi.docstatus = 1
        AND pi.posting_date >= %(from_date)s
        AND pi.posting_date <= %(to_date)s
    """, {'project': project_name, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
    
    # Labor costs
    labor_costs = frappe.db.sql("""
        SELECT SUM(td.base_costing_amount)
        FROM `tabTimesheet Detail` td
        JOIN `tabTimesheet` t ON td.parent = t.name
        WHERE td.project = %(project)s
        AND t.docstatus = 1
        AND t.start_date >= %(from_date)s
        AND t.start_date <= %(to_date)s
    """, {'project': project_name, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
    
    # Other expenses
    other_expenses = frappe.db.sql("""
        SELECT SUM(ec.grand_total)
        FROM `tabExpense Claim` ec
        WHERE ec.project = %(project)s
        AND ec.docstatus = 1
        AND ec.posting_date >= %(from_date)s
        AND ec.posting_date <= %(to_date)s
    """, {'project': project_name, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
    
    return {
        'material_costs': flt(material_costs),
        'labor_costs': flt(labor_costs),
        'other_expenses': flt(other_expenses)
    }

def get_project_health_indicator(project):
    """Calculate project health indicator based on multiple factors"""
    
    score = 0
    
    # Profit margin factor (40% weight)
    profit_margin = project.get('profit_margin', 0)
    if profit_margin > 20:
        score += 40
    elif profit_margin > 10:
        score += 30
    elif profit_margin > 0:
        score += 20
    else:
        score += 0
    
    # Progress vs timeline factor (30% weight)
    percent_complete = project.get('percent_complete', 0)
    if percent_complete >= 90:
        score += 30
    elif percent_complete >= 70:
        score += 25
    elif percent_complete >= 50:
        score += 20
    elif percent_complete >= 25:
        score += 15
    else:
        score += 10
    
    # Cost variance factor (30% weight)
    cost_variance_percent = abs(project.get('cost_variance_percent', 0))
    if cost_variance_percent <= 5:
        score += 30
    elif cost_variance_percent <= 10:
        score += 25
    elif cost_variance_percent <= 20:
        score += 15
    else:
        score += 5
    
    # Return health status
    if score >= 85:
        return {'status': 'Excellent', 'color': 'green', 'score': score}
    elif score >= 70:
        return {'status': 'Good', 'color': 'blue', 'score': score}
    elif score >= 50:
        return {'status': 'Fair', 'color': 'yellow', 'score': score}
    else:
        return {'status': 'Poor', 'color': 'red', 'score': score}

@frappe.whitelist()
def get_profitability_trends(filters):
    """Get profitability trends over time for charting"""
    
    # Parse filters if it's a JSON string
    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except (json.JSONDecodeError, ValueError):
            filters = {}
    
    company = filters.get('company')
    from_date = getdate(filters.get('from_date'))
    to_date = getdate(filters.get('to_date'))
    
    # Generate monthly data points
    trends = []
    current_date = from_date
    
    while current_date <= to_date:
        month_start = get_first_day(current_date)
        month_end = get_last_day(current_date)
        
        # Get revenue for the month
        monthly_revenue = frappe.db.sql("""
            SELECT SUM(si.base_grand_total)
            FROM `tabSales Invoice` si
            WHERE si.company = %(company)s
            AND si.project IS NOT NULL
            AND si.posting_date >= %(month_start)s
            AND si.posting_date <= %(month_end)s
            AND si.docstatus = 1
        """, {'company': company, 'month_start': month_start, 'month_end': month_end})[0][0] or 0
        
        # Get costs for the month
        monthly_costs = get_total_project_costs({
            'company': company,
            'from_date': month_start,
            'to_date': month_end
        })
        
        trends.append({
            'period': current_date.strftime('%Y-%m'),
            'revenue': flt(monthly_revenue),
            'costs': flt(monthly_costs),
            'profit': flt(monthly_revenue) - flt(monthly_costs),
            'margin': (flt(monthly_revenue - monthly_costs) / flt(monthly_revenue) * 100) if monthly_revenue else 0
        })
        
        current_date = add_months(current_date, 1)
    
    return trends

@frappe.whitelist()
def get_cost_breakdown_analysis(filters):
    """Get detailed cost breakdown analysis across all projects"""
    
    # Parse filters if it's a JSON string
    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except (json.JSONDecodeError, ValueError):
            filters = {}
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Material costs by category
    material_breakdown = frappe.db.sql("""
        SELECT 
            ig.name as item_group,
            SUM(pii.base_amount) as amount
        FROM `tabPurchase Invoice Item` pii
        JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
        JOIN `tabItem` i ON pii.item_code = i.name
        JOIN `tabItem Group` ig ON i.item_group = ig.name
        WHERE pi.company = %(company)s
        AND pi.project IS NOT NULL
        AND pi.posting_date >= %(from_date)s
        AND pi.posting_date <= %(to_date)s
        AND pi.docstatus = 1
        GROUP BY ig.name
        ORDER BY amount DESC
        LIMIT 10
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Labor costs by employee type/designation
    labor_breakdown = frappe.db.sql("""
        SELECT 
            e.designation,
            SUM(td.base_costing_amount) as amount
        FROM `tabTimesheet Detail` td
        JOIN `tabTimesheet` t ON td.parent = t.name
        JOIN `tabEmployee` e ON t.employee = e.name
        WHERE t.company = %(company)s
        AND td.project IS NOT NULL
        AND t.start_date >= %(from_date)s
        AND t.start_date <= %(to_date)s
        AND t.docstatus = 1
        GROUP BY e.designation
        ORDER BY amount DESC
        LIMIT 10
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return {
        'material_breakdown': material_breakdown,
        'labor_breakdown': labor_breakdown
    }

@frappe.whitelist()
def get_performance_metrics(filters):
    """Get key performance metrics for the dashboard"""
    
    # Parse filters if it's a JSON string
    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except (json.JSONDecodeError, ValueError):
            filters = {}
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Project completion metrics
    completion_metrics = frappe.db.sql("""
        SELECT 
            AVG(percent_complete) as avg_completion,
            COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_projects,
            COUNT(CASE WHEN status IN ('Open', 'In Progress') THEN 1 END) as active_projects,
            COUNT(CASE WHEN expected_end_date < CURDATE() AND status != 'Completed' THEN 1 END) as overdue_projects
        FROM `tabProject`
        WHERE company = %(company)s
        AND expected_start_date >= %(from_date)s
        AND expected_start_date <= %(to_date)s
        AND status != 'Cancelled'
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Financial performance
    financial_metrics = get_profitability_summary(filters)
    
    return {
        'completion_metrics': completion_metrics[0] if completion_metrics else {},
        'financial_metrics': financial_metrics
    }

@frappe.whitelist()
def export_dashboard_data(filters, data):
    """Export dashboard data to Excel format"""
    
    import pandas as pd
    from io import BytesIO
    import base64
    
    try:
        # Create Excel writer object
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Executive Summary
            summary_df = pd.DataFrame([data['summary']])
            summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
            
            # Project Details
            projects_df = pd.DataFrame(data['projects'])
            if not projects_df.empty:
                # Flatten health_indicator column
                projects_df['health_status'] = projects_df['health_indicator'].apply(lambda x: x.get('status', ''))
                projects_df['health_score'] = projects_df['health_indicator'].apply(lambda x: x.get('score', 0))
                projects_df = projects_df.drop('health_indicator', axis=1)
                
                projects_df.to_excel(writer, sheet_name='Project Details', index=False)
            
            # Profitability Trends
            trends_df = pd.DataFrame(data['trends'])
            if not trends_df.empty:
                trends_df.to_excel(writer, sheet_name='Profitability Trends', index=False)
            
            # Cost Breakdown
            if data['cost_breakdown']['material_breakdown']:
                material_df = pd.DataFrame(data['cost_breakdown']['material_breakdown'])
                material_df.to_excel(writer, sheet_name='Material Costs', index=False)
            
            if data['cost_breakdown']['labor_breakdown']:
                labor_df = pd.DataFrame(data['cost_breakdown']['labor_breakdown'])
                labor_df.to_excel(writer, sheet_name='Labor Costs', index=False)
        
        # Save to file
        file_name = f"project_profitability_dashboard_{frappe.utils.now_datetime().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = f"/tmp/{file_name}"
        
        with open(file_path, 'wb') as f:
            f.write(output.getvalue())
        
        # Create file doc
        file_doc = frappe.get_doc({
            'doctype': 'File',
            'file_name': file_name,
            'file_url': f'/files/{file_name}',
            'is_private': 1
        })
        
        with open(file_path, 'rb') as f:
            file_doc.content = f.read()
        
        file_doc.save()
        
        return {
            'file_url': file_doc.file_url,
            'file_name': file_name
        }
        
    except Exception as e:
        frappe.log_error(f"Export error: {str(e)}", "Dashboard Export")
        frappe.throw(_("Error exporting data: {0}").format(str(e)))

@frappe.whitelist()
def get_project_comparison_data(project_names):
    """Get comparison data for multiple projects"""
    
    if isinstance(project_names, str):
        project_names = json.loads(project_names)
    
    comparison_data = []
    
    for project_name in project_names:
        project_data = frappe.db.get_value('Project', project_name, [
            'name', 'project_name', 'total_sales_amount', 'estimated_costing',
            'percent_complete', 'status', 'customer'
        ], as_dict=True)
        
        if project_data:
            # Get financial details
            financial_data = get_project_financial_details(project_name, {
                'from_date': get_first_day(add_months(nowdate(), -12)),
                'to_date': get_last_day(nowdate())
            })
            
            project_data.update(financial_data)
            project_data['gross_profit'] = flt(project_data.get('total_revenue', 0)) - flt(project_data.get('total_costs', 0))
            project_data['profit_margin'] = (flt(project_data['gross_profit']) / flt(project_data.get('total_revenue', 0)) * 100) if project_data.get('total_revenue') else 0
            
            comparison_data.append(project_data)
    
    return comparison_data

@frappe.whitelist()
def get_budget_vs_actual_analysis(filters):
    """Get budget vs actual analysis for projects"""
    
    # Parse filters if it's a JSON string
    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except (json.JSONDecodeError, ValueError):
            filters = {}
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    projects = frappe.db.sql("""
        SELECT 
            p.name,
            p.project_name,
            p.estimated_costing as budgeted_cost,
            p.total_sales_amount as budgeted_revenue
        FROM `tabProject` p
        WHERE p.company = %(company)s
        AND p.expected_start_date >= %(from_date)s
        AND p.expected_start_date <= %(to_date)s
        AND p.status != 'Cancelled'
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    for project in projects:
        # Get actual costs and revenue
        actual_data = get_project_financial_details(project.name, filters)
        
        project.update({
            'actual_revenue': actual_data.get('total_revenue', 0),
            'actual_costs': actual_data.get('total_costs', 0),
            'revenue_variance': flt(actual_data.get('total_revenue', 0)) - flt(project.get('budgeted_revenue', 0)),
            'cost_variance': flt(actual_data.get('total_costs', 0)) - flt(project.get('budgeted_cost', 0))
        })
        
        # Calculate variance percentages
        project['revenue_variance_percent'] = (project['revenue_variance'] / flt(project.get('budgeted_revenue', 0)) * 100) if project.get('budgeted_revenue') else 0
        project['cost_variance_percent'] = (project['cost_variance'] / flt(project.get('budgeted_cost', 0)) * 100) if project.get('budgeted_cost') else 0
    
    return projects

@frappe.whitelist()
def get_customer_profitability_analysis(filters):
    """Get profitability analysis by customer"""
    
    # Parse filters if it's a JSON string
    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except (json.JSONDecodeError, ValueError):
            filters = {}
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    customer_data = frappe.db.sql("""
        SELECT 
            p.customer,
            COUNT(p.name) as project_count,
            SUM(p.total_sales_amount) as total_contract_value,
            AVG(p.percent_complete) as avg_completion
        FROM `tabProject` p
        WHERE p.company = %(company)s
        AND p.expected_start_date >= %(from_date)s
        AND p.expected_start_date <= %(to_date)s
        AND p.status != 'Cancelled'
        AND p.customer IS NOT NULL
        GROUP BY p.customer
        ORDER BY total_contract_value DESC
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    for customer in customer_data:
        # Get actual revenue and costs for this customer
        revenue = frappe.db.sql("""
            SELECT SUM(si.base_grand_total)
            FROM `tabSales Invoice` si
            JOIN `tabProject` p ON si.project = p.name
            WHERE si.customer = %(customer)s
            AND si.company = %(company)s
            AND si.posting_date >= %(from_date)s
            AND si.posting_date <= %(to_date)s
            AND si.docstatus = 1
        """, {'customer': customer.customer, 'company': company, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
        
        costs = frappe.db.sql("""
            SELECT SUM(pi.base_grand_total)
            FROM `tabPurchase Invoice` pi
            JOIN `tabProject` p ON pi.project = p.name
            WHERE p.customer = %(customer)s
            AND pi.company = %(company)s
            AND pi.posting_date >= %(from_date)s
            AND pi.posting_date <= %(to_date)s
            AND pi.docstatus = 1
        """, {'customer': customer.customer, 'company': company, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
        
        customer.update({
            'total_revenue': flt(revenue),
            'total_costs': flt(costs),
            'gross_profit': flt(revenue) - flt(costs),
            'profit_margin': (flt(revenue - costs) / flt(revenue) * 100) if revenue else 0
        })
    
    return customer_data

def get_project_risk_indicators(project):
    """Calculate risk indicators for a project"""
    
    risk_score = 0
    risk_factors = []
    
    # Timeline risk
    if project.get('expected_end_date'):
        end_date = getdate(project['expected_end_date'])
        if end_date < getdate(nowdate()) and project.get('status') != 'Completed':
            risk_score += 30
            risk_factors.append('Project overdue')
    
    # Budget overrun risk
    cost_variance_percent = abs(project.get('cost_variance_percent', 0))
    if cost_variance_percent > 20:
        risk_score += 25
        risk_factors.append('Significant cost overrun')
    elif cost_variance_percent > 10:
        risk_score += 15
        risk_factors.append('Moderate cost overrun')
    
    # Low progress risk
    percent_complete = project.get('percent_complete', 0)
    if percent_complete < 25 and project.get('status') == 'In Progress':
        risk_score += 20
        risk_factors.append('Low progress for active project')
    
    # Profitability risk
    profit_margin = project.get('profit_margin', 0)
    if profit_margin < 0:
        risk_score += 25
        risk_factors.append('Negative profit margin')
    elif profit_margin < 5:
        risk_score += 15
        risk_factors.append('Low profit margin')
    
    # Determine risk level
    if risk_score >= 60:
        risk_level = 'High'
        risk_color = 'red'
    elif risk_score >= 30:
        risk_level = 'Medium'
        risk_color = 'yellow'
    else:
        risk_level = 'Low'
        risk_color = 'green'
    
    return {
        'risk_level': risk_level,
        'risk_score': risk_score,
        'risk_color': risk_color,
        'risk_factors': risk_factors
    }

@frappe.whitelist()
def get_profitability_forecast(filters):
    """Forecast future profitability using simple linear regression on monthly profit."""
    import numpy as np
    try:
        # Get historical trends
        trends = get_profitability_trends(filters)
        if not trends or len(trends) < 2:
            return {'forecast': [], 'message': 'Not enough data for forecast'}
        # Prepare data
        y = np.array([t['profit'] for t in trends])
        X = np.arange(len(y)).reshape(-1, 1)
        # Linear regression
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X, y)
        # Forecast next 6 months
        future_X = np.arange(len(y), len(y) + 6).reshape(-1, 1)
        forecast = model.predict(future_X)
        forecast_periods = []
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        last_period = trends[-1]['period'] + '-01'
        last_date = datetime.strptime(last_period, '%Y-%m-%d')
        for i, value in enumerate(forecast):
            period = (last_date + relativedelta(months=i+1)).strftime('%Y-%m')
            forecast_periods.append({'period': period, 'forecast_profit': float(value)})
        return {'forecast': forecast_periods}
    except Exception as e:
        frappe.log_error(f"Forecast error: {str(e)}", "Profitability Forecast")
        return {'forecast': [], 'message': str(e)}

@frappe.whitelist()
def get_project_risk_summary(filters):
    """Return a summary of top at-risk projects for dashboard display."""
    try:
        projects = get_project_profitability_data(filters)
        risks = []
        for project in projects:
            risk = get_project_risk_indicators(project)
            if risk['risk_level'] == 'High':
                risks.append({
                    'name': project['name'],
                    'project_name': project['project_name'],
                    'customer': project['customer'],
                    'risk_score': risk['risk_score'],
                    'risk_factors': risk['risk_factors'],
                    'profit_margin': project.get('profit_margin', 0),
                    'status': project.get('status', '')
                })
        # Sort by risk score descending
        risks = sorted(risks, key=lambda x: x['risk_score'], reverse=True)
        return {'top_risks': risks[:5]}
    except Exception as e:
        frappe.log_error(f"Risk summary error: {str(e)}", "Project Risk Summary")
        return {'top_risks': [], 'message': str(e)}

@frappe.whitelist()
def get_monthly_performance_summary(filters):
    """Get monthly performance summary for the dashboard"""
    
    # Parse filters if it's a JSON string
    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except (json.JSONDecodeError, ValueError):
            filters = {}
    
    company = filters.get('company')
    from_date = getdate(filters.get('from_date'))
    to_date = getdate(filters.get('to_date'))
    
    monthly_data = []
    current_date = from_date
    
    while current_date <= to_date:
        month_start = get_first_day(current_date)
        month_end = get_last_day(current_date)
        
        # Revenue for the month
        monthly_revenue = frappe.db.sql("""
            SELECT SUM(si.base_grand_total)
            FROM `tabSales Invoice` si
            WHERE si.company = %(company)s
            AND si.project IS NOT NULL
            AND si.posting_date >= %(month_start)s
            AND si.posting_date <= %(month_end)s
            AND si.docstatus = 1
        """, {'company': company, 'month_start': month_start, 'month_end': month_end})[0][0] or 0
        
        # Projects started this month
        projects_started = frappe.db.sql("""
            SELECT COUNT(*)
            FROM `tabProject`
            WHERE company = %(company)s
            AND expected_start_date >= %(month_start)s
            AND expected_start_date <= %(month_end)s
            AND status != 'Cancelled'
        """, {'company': company, 'month_start': month_start, 'month_end': month_end})[0][0] or 0
        
        # Projects completed this month
        projects_completed = frappe.db.sql("""
            SELECT COUNT(*)
            FROM `tabProject`
            WHERE company = %(company)s
            AND status = 'Completed'
            AND modified >= %(month_start)s
            AND modified <= %(month_end)s
        """, {'company': company, 'month_start': month_start, 'month_end': month_end})[0][0] or 0
        
        monthly_data.append({
            'period': current_date.strftime('%Y-%m'),
            'month_name': current_date.strftime('%B %Y'),
            'revenue': flt(monthly_revenue),
            'projects_started': cint(projects_started),
            'projects_completed': cint(projects_completed)
        })
        
        current_date = add_months(current_date, 1)
    
    return monthly_data 