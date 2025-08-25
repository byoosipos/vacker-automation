import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, add_months, nowdate, get_first_day, get_last_day, today, formatdate
import json
from datetime import datetime, timedelta
import hashlib
import time
import traceback

# Cache configuration
CACHE_TIMEOUT = 300  # 5 minutes default
CACHE_PREFIX = "exec_dashboard"

# Logging configuration
def log_error(method_name, error, context=None):
    """Centralized error logging"""
    error_msg = f"Dashboard Error in {method_name}: {str(error)}"
    if context:
        error_msg += f" | Context: {json.dumps(context, default=str)}"
    
    frappe.log_error(
        title=f"Executive Dashboard - {method_name}",
        message=f"{error_msg}\n\nTraceback:\n{traceback.format_exc()}"
    )

def safe_db_query(query, values=None, as_dict=True, method_name="unknown"):
    """Safe database query with error handling"""
    try:
        return frappe.db.sql(query, values, as_dict=as_dict)
    except Exception as e:
        log_error(method_name, e, {"query": query[:200], "values": values})
        return [] if as_dict else [[]]

def validate_filters(filters):
    """Validate and sanitize filters"""
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        # Ensure filters is a dictionary
        if not isinstance(filters, dict):
            filters = {}
        
        # Validate company
        if filters.get('company'):
            company_exists = frappe.db.exists('Company', filters['company'])
            if not company_exists:
                filters.pop('company', None)
        
        # Validate dates
        for date_field in ['from_date', 'to_date']:
            if filters.get(date_field):
                try:
                    getdate(filters[date_field])
                except:
                    filters.pop(date_field, None)
        
        return filters
    except Exception as e:
        log_error("validate_filters", e, {"filters": str(filters)[:200]})
        return {}

def get_cache_key(filters, method_name):
    """Generate a cache key based on filters and method name"""
    try:
        filter_str = json.dumps(filters, sort_keys=True, default=str)
        key_data = f"{method_name}:{filter_str}"
        return f"{CACHE_PREFIX}:{hashlib.md5(key_data.encode()).hexdigest()}"
    except Exception as e:
        log_error("get_cache_key", e, {"method_name": method_name})
        return f"{CACHE_PREFIX}:fallback_{method_name}"

def get_cached_data(cache_key, timeout=CACHE_TIMEOUT):
    """Get data from cache"""
    try:
        if frappe.cache().exists(cache_key):
            cached_data = frappe.cache().get_value(cache_key)
            if cached_data and isinstance(cached_data, dict):
                cache_time = cached_data.get('timestamp', 0)
                if (time.time() - cache_time) < timeout:
                    return cached_data.get('data')
    except Exception as e:
        log_error("get_cached_data", e, {"cache_key": cache_key})
    return None

def set_cached_data(cache_key, data, timeout=CACHE_TIMEOUT):
    """Set data in cache"""
    try:
        cache_data = {
            'data': data,
            'timestamp': time.time()
        }
        frappe.cache().set_value(cache_key, cache_data, expires_in_sec=timeout)
    except Exception as e:
        log_error("set_cached_data", e, {"cache_key": cache_key})

def get_default_company():
    """Get default company with error handling"""
    try:
        company = frappe.defaults.get_user_default('Company')
        if not company:
            company = frappe.db.get_single_value('Global Defaults', 'default_company')
        if not company:
            first_company = frappe.db.get_value('Company', {}, 'name')
            if first_company:
                company = first_company
        return company
    except Exception as e:
        log_error("get_default_company", e)
        return None

@frappe.whitelist()
def get_comprehensive_dashboard_data(filters=None, lazy_load=True):
    """Main method to get comprehensive executive dashboard data across all modules with performance optimizations"""
    
    try:
        # Validate and sanitize filters
        filters = validate_filters(filters or {})
        
        # Set default filters
        if not filters.get('company'):
            filters['company'] = get_default_company()
        
        if not filters.get('from_date'):
            filters['from_date'] = get_first_day(add_months(nowdate(), -12))
        
        if not filters.get('to_date'):
            filters['to_date'] = get_last_day(nowdate())

        # Ensure we have a valid company
        if not filters.get('company'):
            return {
                "error": True,
                "message": "No company found. Please ensure at least one company exists in the system."
            }

        # Performance optimization: Check cache first
        cache_key = get_cache_key(filters, 'comprehensive_dashboard')
        cached_data = get_cached_data(cache_key)
        
        if cached_data and not filters.get('force_refresh'):
            return cached_data
        
        # Core data (always load for essential metrics)
        core_data = {}
        
        try:
            core_data['financial_summary'] = get_financial_summary(filters)
        except Exception as e:
            log_error("get_financial_summary", e, filters)
            core_data['financial_summary'] = get_empty_financial_summary()
        
        try:
            core_data['project_overview'] = get_project_overview(filters)
        except Exception as e:
            log_error("get_project_overview", e, filters)
            core_data['project_overview'] = get_empty_project_overview()
        
        try:
            core_data['kpi_dashboard'] = get_kpi_dashboard(filters)
        except Exception as e:
            log_error("get_kpi_dashboard", e, filters)
            core_data['kpi_dashboard'] = get_empty_kpi_dashboard()
        
        # Extended data (load based on lazy_load parameter)
        if not lazy_load or filters.get('load_all_modules'):
            extended_modules = [
                ('gl_overview', get_gl_overview),
                ('cashflow_data', get_cashflow_data),
                ('bank_cash_analysis', get_bank_cash_analysis),
                ('project_profitability', get_project_profitability_summary),
                ('material_requests', get_material_requests_overview),
                ('procurement_summary', get_procurement_summary),
                ('purchase_orders_overview', get_purchase_orders_overview),
                ('purchase_invoices_overview', get_purchase_invoices_overview),
                ('inventory_overview', get_inventory_overview),
                ('sales_overview', get_sales_overview),
                ('sales_invoices_detailed', get_sales_invoices_detailed),
                ('customer_analytics', get_customer_analytics),
                ('hr_summary', get_hr_summary),
                ('workforce_analytics', get_workforce_analytics),
                ('payroll_detailed', get_payroll_detailed),
                ('expense_claims_overview', get_expense_claims_overview),
                ('items_analysis', get_items_analysis),
                ('item_groups_analysis', get_item_groups_analysis),
                ('users_analysis', get_users_analysis),
                ('payments_detailed', get_payments_detailed),
                ('manufacturing_overview', get_manufacturing_overview),
                ('trend_analysis', get_trend_analysis)
            ]
            
            for module_name, module_func in extended_modules:
                try:
                    core_data[module_name] = module_func(filters)
                except Exception as e:
                    log_error(f"get_{module_name}", e, filters)
                    core_data[module_name] = {}
        
        # Cache the result
        set_cached_data(cache_key, core_data)
        
        return core_data
        
    except Exception as e:
        log_error("get_comprehensive_dashboard_data", e, filters)
        return {
            "error": True,
            "message": "An error occurred while loading dashboard data. Please try again or contact support."
        }

def get_empty_financial_summary():
    """Return empty financial summary structure"""
    return {
        'total_revenue': 0,
        'total_expenses': 0,
        'net_profit': 0,
        'profit_margin': 0,
        'total_assets': 0,
        'total_liabilities': 0,
        'total_equity': 0,
        'revenue_transactions': 0,
        'expense_transactions': 0
    }

def get_empty_project_overview():
    """Return empty project overview structure"""
    return {
        'total_projects': 0,
        'active_projects': 0,
        'completed_projects': 0,
        'on_hold_projects': 0,
        'total_project_value': 0,
        'avg_completion': 0
    }

def get_empty_kpi_dashboard():
    """Return empty KPI dashboard structure"""
    return {
        'revenue_growth': 0,
        'profit_margin': 0,
        'customer_satisfaction': 0,
        'employee_utilization': 0
    }

@frappe.whitelist()
def get_module_data(module_name, filters=None):
    """Get data for a specific module (for lazy loading) with error handling"""
    
    try:
        # Validate inputs
        if not module_name:
            return {"error": True, "message": "Module name is required"}
        
        # Validate and sanitize filters
        filters = validate_filters(filters or {})
        
        # Ensure we have a valid company
        if not filters.get('company'):
            filters['company'] = get_default_company()
        
        if not filters.get('company'):
            return {"error": True, "message": "No company found"}
        
        # Check cache first
        cache_key = get_cache_key(filters, f'module_{module_name}')
        cached_data = get_cached_data(cache_key)
        
        if cached_data and not filters.get('force_refresh'):
            return cached_data
        
        # Module-specific data loading with error handling
        module_data = {}
        
        module_functions = {
            'financial': [
                ('gl_overview', get_gl_overview),
                ('cashflow_data', get_cashflow_data),
                ('bank_cash_analysis', get_bank_cash_analysis),
            ],
            'projects': [
                ('project_profitability', get_project_profitability_summary),
            ],
            'materials': [
                ('material_requests', get_material_requests_overview),
                ('procurement_summary', get_procurement_summary),
                ('inventory_overview', get_inventory_overview),
            ],
            'sales': [
                ('sales_overview', get_sales_overview),
                ('sales_invoices_detailed', get_sales_invoices_detailed),
                ('customer_analytics', get_customer_analytics),
            ],
            'hr': [
                ('hr_summary', get_hr_summary),
                ('workforce_analytics', get_workforce_analytics),
                ('payroll_detailed', get_payroll_detailed),
                ('expense_claims_overview', get_expense_claims_overview),
            ],
            'purchase': [
                ('purchase_orders_overview', get_purchase_orders_overview),
                ('purchase_invoices_overview', get_purchase_invoices_overview),
            ],
            'operations': [
                ('manufacturing_overview', get_manufacturing_overview),
                ('items_analysis', get_items_analysis),
                ('item_groups_analysis', get_item_groups_analysis),
            ],
            'system': [
                ('users_analysis', get_users_analysis),
                ('payments_detailed', get_payments_detailed),
            ],
            'trends': [
                ('trend_analysis', get_trend_analysis),
            ]
        }
        
        if module_name not in module_functions:
            return {"error": True, "message": f"Unknown module: {module_name}"}
        
        # Load data for each function in the module
        for data_key, func in module_functions[module_name]:
            try:
                module_data[data_key] = func(filters)
            except Exception as e:
                log_error(f"get_module_data_{module_name}_{data_key}", e, filters)
                module_data[data_key] = {}
        
        # Cache the module data
        set_cached_data(cache_key, module_data)
        
        return module_data
        
    except Exception as e:
        log_error("get_module_data", e, {"module_name": module_name, "filters": filters})
        return {"error": True, "message": f"Failed to load {module_name} module data"}

@frappe.whitelist()
def clear_dashboard_cache(company=None):
    """Clear dashboard cache for a company or all companies"""
    try:
        if company:
            # Clear cache for specific company
            cache_pattern = f"{CACHE_PREFIX}:*{company}*"
        else:
            # Clear all dashboard cache
            cache_pattern = f"{CACHE_PREFIX}:*"
        
        # Note: This is a simplified cache clearing approach
        # In production, you might want to implement a more sophisticated cache invalidation strategy
        frappe.cache().delete_keys(cache_pattern)
        
        return {"status": "success", "message": "Cache cleared successfully"}
    except Exception as e:
        frappe.log_error(f"Cache clearing error: {str(e)}", "Dashboard Cache Error")
        return {"status": "error", "message": "Failed to clear cache"}

@frappe.whitelist()
def get_financial_summary(filters):
    """Get comprehensive financial summary from GL entries with optimized queries"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    # Check cache first
    cache_key = get_cache_key(filters, 'financial_summary')
    cached_data = get_cached_data(cache_key, timeout=180)  # 3 minutes cache for financial data
    
    if cached_data and not filters.get('force_refresh'):
        return cached_data
    
    company = filters.get('company')
    if not company:
        company = frappe.defaults.get_user_default('Company') or frappe.db.get_single_value('Global Defaults', 'default_company')
        if not company:
            first_company = frappe.db.get_value('Company', {}, 'name')
            if first_company:
                company = first_company
    
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Optimized single query for revenue and expense data
    financial_data = frappe.db.sql("""
        SELECT 
            acc.root_type,
            SUM(CASE WHEN gle.credit > 0 AND acc.root_type = 'Income' THEN gle.credit ELSE 0 END) as total_revenue,
            SUM(CASE WHEN gle.debit > 0 AND acc.root_type = 'Expense' THEN gle.debit ELSE 0 END) as total_expenses,
            COUNT(DISTINCT CASE WHEN acc.root_type = 'Income' AND gle.credit > 0 THEN gle.voucher_no END) as revenue_transactions,
            COUNT(DISTINCT CASE WHEN acc.root_type = 'Expense' AND gle.debit > 0 THEN gle.voucher_no END) as expense_transactions
        FROM `tabGL Entry` gle
        INNER JOIN `tabAccount` acc ON gle.account = acc.name
        WHERE gle.company = %(company)s
        AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND acc.root_type IN ('Income', 'Expense')
        AND gle.is_cancelled = 0
        AND gle.docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Optimized balance sheet query with index hints
    balance_sheet_data = frappe.db.sql("""
        SELECT 
            acc.root_type,
            SUM(gle.debit - gle.credit) as balance
        FROM `tabGL Entry` gle USE INDEX (posting_date)
        INNER JOIN `tabAccount` acc ON gle.account = acc.name
        WHERE gle.company = %(company)s
        AND gle.posting_date <= %(to_date)s
        AND acc.root_type IN ('Asset', 'Liability', 'Equity')
        AND gle.is_cancelled = 0
        AND gle.docstatus = 1
        GROUP BY acc.root_type
    """, {'company': company, 'to_date': to_date}, as_dict=True)
    
    # Process financial data
    revenue = 0
    expenses = 0
    revenue_transactions = 0
    expense_transactions = 0
    
    for row in financial_data:
        revenue += flt(row.get('total_revenue', 0))
        expenses += flt(row.get('total_expenses', 0))
        revenue_transactions += cint(row.get('revenue_transactions', 0))
        expense_transactions += cint(row.get('expense_transactions', 0))
    
    # Convert balance sheet data to dictionary
    balance_sheet = {}
    for row in balance_sheet_data:
        balance_sheet[row['root_type'].lower()] = flt(row['balance'])
    
    result = {
        'total_revenue': flt(revenue, 2),
        'total_expenses': flt(expenses, 2),
        'net_profit': flt(revenue - expenses, 2),
        'profit_margin': flt((revenue - expenses) / revenue * 100, 2) if revenue else 0,
        'total_assets': flt(balance_sheet.get('asset', 0), 2),
        'total_liabilities': flt(balance_sheet.get('liability', 0), 2),
        'total_equity': flt(balance_sheet.get('equity', 0), 2),
        'revenue_transactions': revenue_transactions,
        'expense_transactions': expense_transactions
    }
    
    # Cache the result
    set_cached_data(cache_key, result, timeout=180)
    
    return result

@frappe.whitelist()
def get_gl_overview(filters):
    """Get General Ledger overview with account-wise analysis"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Top Revenue Accounts
    top_revenue_accounts = frappe.db.sql("""
        SELECT 
            gle.account,
            acc.account_name,
            SUM(gle.credit) as total_credit,
            COUNT(*) as transaction_count
        FROM `tabGL Entry` gle
        JOIN `tabAccount` acc ON gle.account = acc.name
        WHERE gle.company = %(company)s
        AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND acc.root_type = 'Income'
        AND gle.credit > 0
        AND gle.is_cancelled = 0
        AND gle.docstatus = 1
        GROUP BY gle.account
        ORDER BY total_credit DESC
        LIMIT 10
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Top Expense Accounts
    top_expense_accounts = frappe.db.sql("""
        SELECT 
            gle.account,
            acc.account_name,
            SUM(gle.debit) as total_debit,
            COUNT(*) as transaction_count
        FROM `tabGL Entry` gle
        JOIN `tabAccount` acc ON gle.account = acc.name
        WHERE gle.company = %(company)s
        AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND acc.root_type = 'Expense'
        AND gle.debit > 0
        AND gle.is_cancelled = 0
        AND gle.docstatus = 1
        GROUP BY gle.account
        ORDER BY total_debit DESC
        LIMIT 10
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Monthly GL Trends
    monthly_trends = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(gle.posting_date, '%%Y-%%m') as period,
            acc.root_type,
            SUM(gle.debit) as total_debit,
            SUM(gle.credit) as total_credit
        FROM `tabGL Entry` gle
        JOIN `tabAccount` acc ON gle.account = acc.name
        WHERE gle.company = %(company)s
        AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND acc.root_type IN ('Income', 'Expense')
        AND gle.is_cancelled = 0
        AND gle.docstatus = 1
        GROUP BY period, acc.root_type
        ORDER BY period, acc.root_type
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return {
        'top_revenue_accounts': top_revenue_accounts,
        'top_expense_accounts': top_expense_accounts,
        'monthly_trends': monthly_trends
    }

@frappe.whitelist()
def get_material_requests_overview(filters):
    """Get comprehensive Material Request tracking and analytics"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Status-wise Material Request counts
    status_summary = frappe.db.sql("""
        SELECT 
            mr.status,
            COUNT(*) as count,
            SUM(CASE WHEN mri.amount THEN mri.amount ELSE mri.qty * mri.rate END) as total_value
        FROM `tabMaterial Request` mr
        LEFT JOIN `tabMaterial Request Item` mri ON mr.name = mri.parent
        WHERE mr.company = %(company)s
        AND mr.transaction_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY mr.status
        ORDER BY count DESC
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Recent Material Requests
    recent_requests = frappe.db.sql("""
        SELECT 
            mr.name,
            mr.transaction_date,
            mr.status,
            mr.material_request_type,
            mr.per_ordered,
            mr.per_received,
            COUNT(mri.name) as items_count,
            SUM(CASE WHEN mri.amount THEN mri.amount ELSE mri.qty * mri.rate END) as total_value
        FROM `tabMaterial Request` mr
        LEFT JOIN `tabMaterial Request Item` mri ON mr.name = mri.parent
        WHERE mr.company = %(company)s
        AND mr.transaction_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY mr.name
        ORDER BY mr.transaction_date DESC
        LIMIT 20
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Pending Actions Summary
    pending_actions = frappe.db.sql("""
        SELECT 
            'Draft' as category,
            COUNT(*) as count,
            SUM(CASE WHEN mri.amount THEN mri.amount ELSE mri.qty * mri.rate END) as value
        FROM `tabMaterial Request` mr
        LEFT JOIN `tabMaterial Request Item` mri ON mr.name = mri.parent
        WHERE mr.company = %(company)s
        AND mr.status = 'Draft'
        
        UNION ALL
        
        SELECT 
            'Pending Approval' as category,
            COUNT(*) as count,
            SUM(CASE WHEN mri.amount THEN mri.amount ELSE mri.qty * mri.rate END) as value
        FROM `tabMaterial Request` mr
        LEFT JOIN `tabMaterial Request Item` mri ON mr.name = mri.parent
        WHERE mr.company = %(company)s
        AND mr.status = 'Pending'
        
        UNION ALL
        
        SELECT 
            'Partially Ordered' as category,
            COUNT(*) as count,
            SUM(CASE WHEN mri.amount THEN mri.amount ELSE mri.qty * mri.rate END) as value
        FROM `tabMaterial Request` mr
        LEFT JOIN `tabMaterial Request Item` mri ON mr.name = mri.parent
        WHERE mr.company = %(company)s
        AND mr.status IN ('Partially Ordered', 'Partially Received')
    """, {'company': company}, as_dict=True)
    
    # Top Requested Items
    top_items = frappe.db.sql("""
        SELECT 
            mri.item_code,
            mri.item_name,
            SUM(mri.qty) as total_qty,
            COUNT(DISTINCT mr.name) as request_count,
            SUM(CASE WHEN mri.amount THEN mri.amount ELSE mri.qty * mri.rate END) as total_value
        FROM `tabMaterial Request Item` mri
        JOIN `tabMaterial Request` mr ON mri.parent = mr.name
        WHERE mr.company = %(company)s
        AND mr.transaction_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY mri.item_code
        ORDER BY total_value DESC
        LIMIT 15
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return {
        'status_summary': status_summary,
        'recent_requests': recent_requests,
        'pending_actions': pending_actions,
        'top_items': top_items
    }

@frappe.whitelist()
def get_project_overview(filters):
    """Get comprehensive project analytics"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Project Status Summary
    project_status = frappe.db.sql("""
        SELECT 
            p.status,
            COUNT(*) as count,
            SUM(p.total_sales_amount) as total_value,
            AVG(p.percent_complete) as avg_completion
        FROM `tabProject` p
        WHERE p.company = %(company)s
        AND (p.expected_start_date BETWEEN %(from_date)s AND %(to_date)s
             OR p.expected_end_date BETWEEN %(from_date)s AND %(to_date)s
             OR p.status IN ('Open', 'In Progress'))
        GROUP BY p.status
        ORDER BY count DESC
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Critical Projects (Overdue or High Risk)
    critical_projects = frappe.db.sql("""
        SELECT 
            p.name,
            p.project_name,
            p.customer,
            p.status,
            p.percent_complete,
            p.expected_end_date,
            p.total_sales_amount,
            DATEDIFF(CURDATE(), p.expected_end_date) as days_overdue
        FROM `tabProject` p
        WHERE p.company = %(company)s
        AND (
            (p.expected_end_date < CURDATE() AND p.status != 'Completed')
            OR (p.percent_complete < 50 AND DATEDIFF(p.expected_end_date, CURDATE()) < 30)
        )
        ORDER BY days_overdue DESC, p.expected_end_date ASC
        LIMIT 10
    """, {'company': company}, as_dict=True)
    
    # Project Performance Metrics
    performance_metrics = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_projects,
            AVG(percent_complete) as avg_completion,
            COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_projects,
            COUNT(CASE WHEN expected_end_date < CURDATE() AND status != 'Completed' THEN 1 END) as overdue_projects,
            SUM(total_sales_amount) as total_contract_value
        FROM `tabProject`
        WHERE company = %(company)s
        AND expected_start_date >= %(from_date)s
    """, {'company': company, 'from_date': from_date}, as_dict=True)
    
    return {
        'project_status': project_status,
        'critical_projects': critical_projects,
        'performance_metrics': performance_metrics[0] if performance_metrics else {}
    }

@frappe.whitelist()
def get_sales_overview(filters):
    """Get comprehensive sales analytics"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Sales Summary
    sales_summary = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_orders,
            SUM(base_grand_total) as total_sales,
            AVG(base_grand_total) as avg_order_value,
            COUNT(DISTINCT customer) as unique_customers
        FROM `tabSales Invoice`
        WHERE company = %(company)s
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Top Customers
    top_customers = frappe.db.sql("""
        SELECT 
            customer,
            customer_name,
            COUNT(*) as order_count,
            SUM(base_grand_total) as total_sales,
            AVG(base_grand_total) as avg_order_value
        FROM `tabSales Invoice`
        WHERE company = %(company)s
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND docstatus = 1
        GROUP BY customer
        ORDER BY total_sales DESC
        LIMIT 10
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Monthly Sales Trends
    monthly_sales = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(posting_date, '%%Y-%%m') as period,
            COUNT(*) as order_count,
            SUM(base_grand_total) as total_sales
        FROM `tabSales Invoice`
        WHERE company = %(company)s
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND docstatus = 1
        GROUP BY period
        ORDER BY period
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return {
        'sales_summary': sales_summary[0] if sales_summary else {},
        'top_customers': top_customers,
        'monthly_sales': monthly_sales
    }

@frappe.whitelist()
def get_hr_summary(filters):
    """Get HR and workforce analytics"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    
    # Employee Summary
    employee_summary = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_employees,
            COUNT(CASE WHEN status = 'Active' THEN 1 END) as active_employees,
            COUNT(CASE WHEN gender = 'Male' THEN 1 END) as male_employees,
            COUNT(CASE WHEN gender = 'Female' THEN 1 END) as female_employees
        FROM `tabEmployee`
        WHERE company = %(company)s
    """, {'company': company}, as_dict=True)
    
    # Department-wise Employee Count
    department_wise = frappe.db.sql("""
        SELECT 
            department,
            COUNT(*) as employee_count
        FROM `tabEmployee`
        WHERE company = %(company)s
        AND status = 'Active'
        GROUP BY department
        ORDER BY employee_count DESC
    """, {'company': company}, as_dict=True)
    
    # Recent Attendance Summary (Last 30 days)
    attendance_summary = frappe.db.sql("""
        SELECT 
            status,
            COUNT(*) as count
        FROM `tabAttendance`
        WHERE company = %(company)s
        AND attendance_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY status
    """, {'company': company}, as_dict=True)
    
    return {
        'employee_summary': employee_summary[0] if employee_summary else {},
        'department_wise': department_wise,
        'attendance_summary': attendance_summary
    }

@frappe.whitelist()
def get_kpi_dashboard(filters):
    """Get Key Performance Indicators dashboard"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Calculate previous period for comparison
    date_diff = getdate(to_date) - getdate(from_date)
    prev_to_date = getdate(from_date) - timedelta(days=1)
    prev_from_date = prev_to_date - date_diff
    
    # Revenue Growth
    current_revenue = frappe.db.sql("""
        SELECT SUM(base_grand_total)
        FROM `tabSales Invoice`
        WHERE company = %(company)s
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
    
    prev_revenue = frappe.db.sql("""
        SELECT SUM(base_grand_total)
        FROM `tabSales Invoice`
        WHERE company = %(company)s
        AND posting_date BETWEEN %(prev_from_date)s AND %(prev_to_date)s
        AND docstatus = 1
    """, {'company': company, 'prev_from_date': prev_from_date, 'prev_to_date': prev_to_date})[0][0] or 0
    
    revenue_growth = ((current_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue else 0
    
    # Project Completion Rate
    total_projects = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabProject`
        WHERE company = %(company)s
        AND expected_start_date >= %(from_date)s
    """, {'company': company, 'from_date': from_date})[0][0] or 0
    
    completed_projects = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabProject`
        WHERE company = %(company)s
        AND status = 'Completed'
        AND expected_start_date >= %(from_date)s
    """, {'company': company, 'from_date': from_date})[0][0] or 0
    
    project_completion_rate = (completed_projects / total_projects * 100) if total_projects else 0
    
    # Material Request Fulfillment Rate
    total_mr = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabMaterial Request`
        WHERE company = %(company)s
        AND transaction_date BETWEEN %(from_date)s AND %(to_date)s
        AND docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
    
    fulfilled_mr = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabMaterial Request`
        WHERE company = %(company)s
        AND transaction_date BETWEEN %(from_date)s AND %(to_date)s
        AND status IN ('Received', 'Transferred', 'Issued', 'Ordered')
        AND docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date})[0][0] or 0
    
    mr_fulfillment_rate = (fulfilled_mr / total_mr * 100) if total_mr else 0
    
    return {
        'revenue_growth': flt(revenue_growth, 2),
        'current_revenue': flt(current_revenue, 2),
        'prev_revenue': flt(prev_revenue, 2),
        'project_completion_rate': flt(project_completion_rate, 2),
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'mr_fulfillment_rate': flt(mr_fulfillment_rate, 2),
        'total_mr': total_mr,
        'fulfilled_mr': fulfilled_mr
    }

@frappe.whitelist()
def get_cashflow_data(filters):
    """Get cashflow analysis from GL entries"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Cash Inflows and Outflows
    cashflow_data = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(gle.posting_date, '%%Y-%%m') as period,
            SUM(CASE WHEN acc.account_type IN ('Cash', 'Bank') AND gle.debit > 0 THEN gle.debit ELSE 0 END) as cash_inflow,
            SUM(CASE WHEN acc.account_type IN ('Cash', 'Bank') AND gle.credit > 0 THEN gle.credit ELSE 0 END) as cash_outflow
        FROM `tabGL Entry` gle
        JOIN `tabAccount` acc ON gle.account = acc.name
        WHERE gle.company = %(company)s
        AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND acc.account_type IN ('Cash', 'Bank')
        AND gle.is_cancelled = 0
        AND gle.docstatus = 1
        GROUP BY period
        ORDER BY period
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Current Cash Position
    current_cash = frappe.db.sql("""
        SELECT 
            SUM(gle.debit - gle.credit) as cash_balance
        FROM `tabGL Entry` gle
        JOIN `tabAccount` acc ON gle.account = acc.name
        WHERE gle.company = %(company)s
        AND gle.posting_date <= %(to_date)s
        AND acc.account_type IN ('Cash', 'Bank')
        AND gle.is_cancelled = 0
        AND gle.docstatus = 1
    """, {'company': company, 'to_date': to_date})[0][0] or 0
    
    return {
        'cashflow_data': cashflow_data,
        'current_cash_balance': flt(current_cash, 2)
    }

# Additional helper methods for other modules
@frappe.whitelist()
def get_procurement_summary(filters):
    """Get procurement and purchase analytics"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Purchase Summary
    purchase_summary = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_purchases,
            SUM(base_grand_total) as total_purchase_value,
            AVG(base_grand_total) as avg_purchase_value,
            COUNT(DISTINCT supplier) as unique_suppliers
        FROM `tabPurchase Invoice`
        WHERE company = %(company)s
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return purchase_summary[0] if purchase_summary else {}

@frappe.whitelist()
def get_inventory_overview(filters):
    """Get inventory and stock analytics"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    
    # Current Stock Value
    stock_value = frappe.db.sql("""
        SELECT 
            SUM(stock_value) as total_stock_value,
            COUNT(DISTINCT item_code) as unique_items
        FROM `tabBin`
        WHERE IFNULL(actual_qty, 0) > 0
    """, as_dict=True)
    
    return stock_value[0] if stock_value else {}

@frappe.whitelist()
def get_customer_analytics(filters):
    """Get customer analytics and insights"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    
    # Customer Summary
    customer_summary = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_customers,
            COUNT(CASE WHEN disabled = 0 THEN 1 END) as active_customers
        FROM `tabCustomer`
    """, as_dict=True)
    
    return customer_summary[0] if customer_summary else {}

@frappe.whitelist()
def get_workforce_analytics(filters):
    """Get detailed workforce analytics"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    
    # Designation-wise employee count
    designation_wise = frappe.db.sql("""
        SELECT 
            designation,
            COUNT(*) as employee_count
        FROM `tabEmployee`
        WHERE company = %(company)s
        AND status = 'Active'
        GROUP BY designation
        ORDER BY employee_count DESC
        LIMIT 10
    """, {'company': company}, as_dict=True)
    
    return {'designation_wise': designation_wise}

@frappe.whitelist()
def get_manufacturing_overview(filters):
    """Get manufacturing analytics"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Work Order Summary
    work_order_summary = frappe.db.sql("""
        SELECT 
            status,
            COUNT(*) as count,
            SUM(qty) as total_qty
        FROM `tabWork Order`
        WHERE company = %(company)s
        AND creation BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY status
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return {'work_order_summary': work_order_summary}

@frappe.whitelist()
def get_trend_analysis(filters):
    """Get comprehensive trend analysis across modules"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Monthly trends for key metrics
    monthly_trends = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(posting_date, '%%Y-%%m') as period,
            'Sales' as metric_type,
            SUM(base_grand_total) as value
        FROM `tabSales Invoice`
        WHERE company = %(company)s
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND docstatus = 1
        GROUP BY period
        
        UNION ALL
        
        SELECT 
            DATE_FORMAT(posting_date, '%%Y-%%m') as period,
            'Purchase' as metric_type,
            SUM(base_grand_total) as value
        FROM `tabPurchase Invoice`
        WHERE company = %(company)s
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND docstatus = 1
        GROUP BY period
        
        ORDER BY period, metric_type
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return {'monthly_trends': monthly_trends}

@frappe.whitelist()
def get_project_profitability_summary(filters):
    """Get summarized project profitability data"""
    
    # Import from existing project dashboard
    from vacker_automation.vacker_automation.page.project_profitability_dashboard.project_profitability_dashboard import get_profitability_summary
    
    return get_profitability_summary(filters)

@frappe.whitelist()
def get_bank_cash_analysis(filters):
    """Get detailed bank and cash analysis"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Bank Accounts Summary
    bank_accounts = frappe.db.sql("""
        SELECT 
            acc.name as account,
            acc.account_name,
            acc.account_type,
            SUM(gle.debit - gle.credit) as balance,
            COUNT(*) as transaction_count
        FROM `tabAccount` acc
        LEFT JOIN `tabGL Entry` gle ON acc.name = gle.account
        WHERE acc.company = %(company)s
        AND acc.account_type IN ('Bank', 'Cash')
        AND (gle.posting_date <= %(to_date)s OR gle.posting_date IS NULL)
        AND (gle.is_cancelled = 0 OR gle.is_cancelled IS NULL)
        AND (gle.docstatus = 1 OR gle.docstatus IS NULL)
        GROUP BY acc.name
        ORDER BY balance DESC
    """, {'company': company, 'to_date': to_date}, as_dict=True)
    
    # Recent Bank Transactions
    recent_transactions = frappe.db.sql("""
        SELECT 
            gle.posting_date,
            gle.account,
            acc.account_name,
            gle.voucher_type,
            gle.voucher_no,
            gle.debit,
            gle.credit,
            gle.debit - gle.credit as net_amount,
            gle.remarks
        FROM `tabGL Entry` gle
        JOIN `tabAccount` acc ON gle.account = acc.name
        WHERE gle.company = %(company)s
        AND acc.account_type IN ('Bank', 'Cash')
        AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND gle.is_cancelled = 0
        AND gle.docstatus = 1
        ORDER BY gle.posting_date DESC, gle.creation DESC
        LIMIT 50
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Account Summary by Type
    account_summary = frappe.db.sql("""
        SELECT 
            acc.account_type,
            COUNT(*) as account_count,
            SUM(CASE WHEN gle.account IS NOT NULL THEN gle.debit - gle.credit ELSE 0 END) as total_balance
        FROM `tabAccount` acc
        LEFT JOIN `tabGL Entry` gle ON acc.name = gle.account 
            AND gle.posting_date <= %(to_date)s 
            AND gle.is_cancelled = 0 
            AND gle.docstatus = 1
        WHERE acc.company = %(company)s
        AND acc.account_type IN ('Bank', 'Cash')
        AND acc.disabled = 0
        GROUP BY acc.account_type
        ORDER BY total_balance DESC
    """, {'company': company, 'to_date': to_date}, as_dict=True)
    
    # Recent Payment Entries for cash flow insights
    payment_entries = frappe.db.sql("""
        SELECT 
            pe.name,
            pe.posting_date,
            pe.payment_type,
            pe.party_type,
            pe.party,
            pe.paid_amount,
            pe.received_amount,
            pe.paid_from,
            pe.paid_to
        FROM `tabPayment Entry` pe
        WHERE pe.company = %(company)s
        AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pe.docstatus = 1
        ORDER BY pe.posting_date DESC
        LIMIT 20
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return {
        'bank_accounts': bank_accounts,
        'recent_transactions': recent_transactions,
        'account_summary': account_summary,
        'payment_entries': payment_entries
    }

@frappe.whitelist()
def get_purchase_orders_overview(filters):
    """Get comprehensive purchase orders analysis"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Purchase Order Status Summary
    po_status_summary = frappe.db.sql("""
        SELECT 
            po.status,
            COUNT(*) as count,
            SUM(po.base_grand_total) as total_value,
            AVG(po.per_received) as avg_received,
            AVG(po.per_billed) as avg_billed
        FROM `tabPurchase Order` po
        WHERE po.company = %(company)s
        AND po.transaction_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY po.status
        ORDER BY count DESC
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Recent Purchase Orders
    recent_pos = frappe.db.sql("""
        SELECT 
            po.name,
            po.transaction_date,
            po.supplier,
            po.supplier_name,
            po.status,
            po.base_grand_total,
            po.per_received,
            po.per_billed,
            po.schedule_date,
            DATEDIFF(CURDATE(), po.schedule_date) as days_overdue
        FROM `tabPurchase Order` po
        WHERE po.company = %(company)s
        AND po.transaction_date BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY po.transaction_date DESC
        LIMIT 20
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Top Suppliers by PO Value
    top_suppliers = frappe.db.sql("""
        SELECT 
            po.supplier,
            po.supplier_name,
            COUNT(*) as po_count,
            SUM(po.base_grand_total) as total_value,
            AVG(po.base_grand_total) as avg_po_value
        FROM `tabPurchase Order` po
        WHERE po.company = %(company)s
        AND po.transaction_date BETWEEN %(from_date)s AND %(to_date)s
        AND po.docstatus = 1
        GROUP BY po.supplier
        ORDER BY total_value DESC
        LIMIT 10
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Overdue Purchase Orders
    overdue_pos = frappe.db.sql("""
        SELECT 
            po.name,
            po.supplier_name,
            po.base_grand_total,
            po.schedule_date,
            po.per_received,
            DATEDIFF(CURDATE(), po.schedule_date) as days_overdue
        FROM `tabPurchase Order` po
        WHERE po.company = %(company)s
        AND po.schedule_date < CURDATE()
        AND po.status NOT IN ('Closed', 'Cancelled')
        AND po.per_received < 100
        ORDER BY days_overdue DESC
        LIMIT 15
    """, {'company': company}, as_dict=True)
    
    return {
        'po_status_summary': po_status_summary,
        'recent_pos': recent_pos,
        'top_suppliers': top_suppliers,
        'overdue_pos': overdue_pos
    }

@frappe.whitelist()
def get_purchase_invoices_overview(filters):
    """Get comprehensive purchase invoices analysis"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Purchase Invoice Summary
    pi_summary = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_invoices,
            SUM(pi.base_grand_total) as total_value,
            AVG(pi.base_grand_total) as avg_invoice_value,
            COUNT(DISTINCT pi.supplier) as unique_suppliers,
            SUM(CASE WHEN pi.outstanding_amount > 0 THEN pi.outstanding_amount ELSE 0 END) as total_outstanding
        FROM `tabPurchase Invoice` pi
        WHERE pi.company = %(company)s
        AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pi.docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Monthly Purchase Trends
    monthly_purchases = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(pi.posting_date, '%%Y-%%m') as period,
            COUNT(*) as invoice_count,
            SUM(pi.base_grand_total) as total_value
        FROM `tabPurchase Invoice` pi
        WHERE pi.company = %(company)s
        AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pi.docstatus = 1
        GROUP BY period
        ORDER BY period
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Outstanding Purchase Invoices
    outstanding_invoices = frappe.db.sql("""
        SELECT 
            pi.name,
            pi.posting_date,
            pi.supplier_name,
            pi.base_grand_total,
            pi.outstanding_amount,
            pi.due_date,
            DATEDIFF(CURDATE(), pi.due_date) as days_overdue
        FROM `tabPurchase Invoice` pi
        WHERE pi.company = %(company)s
        AND pi.outstanding_amount > 0
        AND pi.docstatus = 1
        ORDER BY pi.due_date ASC
        LIMIT 20
    """, {'company': company}, as_dict=True)
    
    # Top Purchase Categories
    top_categories = frappe.db.sql("""
        SELECT 
            pii.expense_account as account,
            acc.account_name,
            COUNT(*) as invoice_count,
            SUM(pii.amount) as total_value
        FROM `tabPurchase Invoice Item` pii
        JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
        LEFT JOIN `tabAccount` acc ON pii.expense_account = acc.name
        WHERE pi.company = %(company)s
        AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pi.docstatus = 1
        GROUP BY pii.expense_account
        ORDER BY total_value DESC
        LIMIT 10
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return {
        'pi_summary': pi_summary[0] if pi_summary else {},
        'monthly_purchases': monthly_purchases,
        'outstanding_invoices': outstanding_invoices,
        'top_categories': top_categories
    }

@frappe.whitelist()
def get_sales_invoices_detailed(filters):
    """Get detailed sales invoices analysis"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Sales Invoice Summary
    si_summary = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_invoices,
            SUM(si.base_grand_total) as total_value,
            AVG(si.base_grand_total) as avg_invoice_value,
            COUNT(DISTINCT si.customer) as unique_customers,
            SUM(CASE WHEN si.outstanding_amount > 0 THEN si.outstanding_amount ELSE 0 END) as total_outstanding
        FROM `tabSales Invoice` si
        WHERE si.company = %(company)s
        AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND si.docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Outstanding Sales Invoices
    outstanding_invoices = frappe.db.sql("""
        SELECT 
            si.name,
            si.posting_date,
            si.customer_name,
            si.base_grand_total,
            si.outstanding_amount,
            si.due_date,
            DATEDIFF(CURDATE(), si.due_date) as days_overdue
        FROM `tabSales Invoice` si
        WHERE si.company = %(company)s
        AND si.outstanding_amount > 0
        AND si.docstatus = 1
        ORDER BY si.due_date ASC
        LIMIT 20
    """, {'company': company}, as_dict=True)
    
    # Sales by Territory
    sales_by_territory = frappe.db.sql("""
        SELECT 
            si.territory,
            COUNT(*) as invoice_count,
            SUM(si.base_grand_total) as total_sales
        FROM `tabSales Invoice` si
        WHERE si.company = %(company)s
        AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND si.docstatus = 1
        GROUP BY si.territory
        ORDER BY total_sales DESC
        LIMIT 10
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Top Selling Items
    top_items = frappe.db.sql("""
        SELECT 
            sii.item_code,
            sii.item_name,
            SUM(sii.qty) as total_qty,
            SUM(sii.amount) as total_value,
            COUNT(DISTINCT si.name) as invoice_count
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        WHERE si.company = %(company)s
        AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND si.docstatus = 1
        GROUP BY sii.item_code
        ORDER BY total_value DESC
        LIMIT 15
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return {
        'si_summary': si_summary[0] if si_summary else {},
        'outstanding_invoices': outstanding_invoices,
        'sales_by_territory': sales_by_territory,
        'top_items': top_items
    }

@frappe.whitelist()
def get_payroll_detailed(filters):
    """Get detailed payroll and employee analytics"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Payroll Summary
    payroll_summary = frappe.db.sql("""
        SELECT 
            COUNT(DISTINCT ss.employee) as employees_paid,
            SUM(ss.gross_pay) as total_gross_pay,
            SUM(ss.net_pay) as total_net_pay,
            AVG(ss.gross_pay) as avg_gross_pay,
            AVG(ss.net_pay) as avg_net_pay
        FROM `tabSalary Slip` ss
        WHERE ss.company = %(company)s
        AND ss.start_date >= %(from_date)s
        AND ss.end_date <= %(to_date)s
        AND ss.docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Department-wise Payroll
    dept_payroll = frappe.db.sql("""
        SELECT 
            e.department,
            COUNT(DISTINCT ss.employee) as employee_count,
            SUM(ss.gross_pay) as total_gross_pay,
            SUM(ss.net_pay) as total_net_pay,
            AVG(ss.gross_pay) as avg_gross_pay
        FROM `tabSalary Slip` ss
        JOIN `tabEmployee` e ON ss.employee = e.name
        WHERE ss.company = %(company)s
        AND ss.start_date >= %(from_date)s
        AND ss.end_date <= %(to_date)s
        AND ss.docstatus = 1
        GROUP BY e.department
        ORDER BY total_gross_pay DESC
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Monthly Payroll Trends
    monthly_payroll = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(ss.start_date, '%%Y-%%m') as period,
            COUNT(DISTINCT ss.employee) as employee_count,
            SUM(ss.gross_pay) as total_gross_pay,
            SUM(ss.net_pay) as total_net_pay
        FROM `tabSalary Slip` ss
        WHERE ss.company = %(company)s
        AND ss.start_date >= %(from_date)s
        AND ss.end_date <= %(to_date)s
        AND ss.docstatus = 1
        GROUP BY period
        ORDER BY period
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Employee Leave Summary
    leave_summary = frappe.db.sql("""
        SELECT 
            la.leave_type,
            COUNT(*) as applications,
            SUM(la.total_leave_days) as total_days,
            COUNT(CASE WHEN la.status = 'Approved' THEN 1 END) as approved_count
        FROM `tabLeave Application` la
        WHERE la.company = %(company)s
        AND la.from_date >= %(from_date)s
        AND la.to_date <= %(to_date)s
        GROUP BY la.leave_type
        ORDER BY total_days DESC
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return {
        'payroll_summary': payroll_summary[0] if payroll_summary else {},
        'dept_payroll': dept_payroll,
        'monthly_payroll': monthly_payroll,
        'leave_summary': leave_summary
    }

@frappe.whitelist()
def get_expense_claims_overview(filters):
    """Get comprehensive expense claims analysis"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Expense Claims Summary
    expense_summary = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_claims,
            SUM(ec.total_claimed_amount) as total_claimed,
            SUM(ec.total_sanctioned_amount) as total_sanctioned,
            COUNT(DISTINCT ec.employee) as unique_employees,
            AVG(ec.total_claimed_amount) as avg_claim_amount
        FROM `tabExpense Claim` ec
        WHERE ec.company = %(company)s
        AND ec.posting_date BETWEEN %(from_date)s AND %(to_date)s
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Status-wise Expense Claims
    status_summary = frappe.db.sql("""
        SELECT 
            ec.approval_status as status,
            COUNT(*) as count,
            SUM(ec.total_claimed_amount) as total_amount
        FROM `tabExpense Claim` ec
        WHERE ec.company = %(company)s
        AND ec.posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY ec.approval_status
        ORDER BY count DESC
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Top Expense Categories
    expense_categories = frappe.db.sql("""
        SELECT 
            ecd.expense_type,
            COUNT(*) as claim_count,
            SUM(ecd.amount) as total_amount,
            AVG(ecd.amount) as avg_amount
        FROM `tabExpense Claim Detail` ecd
        JOIN `tabExpense Claim` ec ON ecd.parent = ec.name
        WHERE ec.company = %(company)s
        AND ec.posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY ecd.expense_type
        ORDER BY total_amount DESC
        LIMIT 10
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Recent Expense Claims
    recent_claims = frappe.db.sql("""
        SELECT 
            ec.name,
            ec.posting_date,
            ec.employee_name,
            ec.total_claimed_amount,
            ec.total_sanctioned_amount,
            ec.approval_status
        FROM `tabExpense Claim` ec
        WHERE ec.company = %(company)s
        AND ec.posting_date BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY ec.posting_date DESC
        LIMIT 20
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Pending Approvals
    pending_approvals = frappe.db.sql("""
        SELECT 
            ec.name,
            ec.employee_name,
            ec.total_claimed_amount,
            ec.posting_date,
            DATEDIFF(CURDATE(), ec.posting_date) as days_pending
        FROM `tabExpense Claim` ec
        WHERE ec.company = %(company)s
        AND ec.approval_status IN ('Draft', 'Submitted')
        ORDER BY ec.posting_date ASC
        LIMIT 15
    """, {'company': company}, as_dict=True)
    
    return {
        'expense_summary': expense_summary[0] if expense_summary else {},
        'status_summary': status_summary,
        'expense_categories': expense_categories,
        'recent_claims': recent_claims,
        'pending_approvals': pending_approvals
    }

@frappe.whitelist()
def get_items_analysis(filters):
    """Get comprehensive items analysis"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Items Summary
    items_summary = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_items,
            COUNT(CASE WHEN i.disabled = 0 THEN 1 END) as active_items,
            COUNT(CASE WHEN i.is_stock_item = 1 THEN 1 END) as stock_items,
            COUNT(CASE WHEN i.is_sales_item = 1 THEN 1 END) as sales_items,
            COUNT(CASE WHEN i.is_purchase_item = 1 THEN 1 END) as purchase_items
        FROM `tabItem` i
    """, as_dict=True)
    
    # Top Selling Items by Value
    top_selling_items = frappe.db.sql("""
        SELECT 
            sii.item_code,
            sii.item_name,
            SUM(sii.qty) as total_qty_sold,
            SUM(sii.amount) as total_sales_value,
            COUNT(DISTINCT si.name) as invoice_count,
            AVG(sii.rate) as avg_selling_rate
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        WHERE si.company = %(company)s
        AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND si.docstatus = 1
        GROUP BY sii.item_code
        ORDER BY total_sales_value DESC
        LIMIT 20
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Top Purchased Items by Value
    top_purchase_items = frappe.db.sql("""
        SELECT 
            pii.item_code,
            pii.item_name,
            SUM(pii.qty) as total_qty_purchased,
            SUM(pii.amount) as total_purchase_value,
            COUNT(DISTINCT pi.name) as invoice_count,
            AVG(pii.rate) as avg_purchase_rate
        FROM `tabPurchase Invoice Item` pii
        JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
        WHERE pi.company = %(company)s
        AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pi.docstatus = 1
        GROUP BY pii.item_code
        ORDER BY total_purchase_value DESC
        LIMIT 20
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Current Stock Levels
    stock_levels = frappe.db.sql("""
        SELECT 
            b.item_code,
            i.item_name,
            i.item_group,
            SUM(b.actual_qty) as current_stock,
            SUM(b.stock_value) as stock_value,
            i.stock_uom
        FROM `tabBin` b
        JOIN `tabItem` i ON b.item_code = i.name
        WHERE b.actual_qty > 0
        GROUP BY b.item_code
        ORDER BY stock_value DESC
        LIMIT 20
    """, as_dict=True)
    
    # Items with Low Stock
    low_stock_items = frappe.db.sql("""
        SELECT 
            b.item_code,
            i.item_name,
            i.item_group,
            SUM(b.actual_qty) as current_stock,
            i.safety_stock,
            i.stock_uom
        FROM `tabBin` b
        JOIN `tabItem` i ON b.item_code = i.name
        WHERE b.actual_qty >= 0
        GROUP BY b.item_code, i.item_name, i.item_group, i.safety_stock, i.stock_uom
        HAVING SUM(b.actual_qty) <= COALESCE(MAX(i.safety_stock), 0)
        AND SUM(b.actual_qty) >= 0
        ORDER BY current_stock ASC
        LIMIT 15
    """, as_dict=True)
    
    # Item Price Trends
    price_trends = frappe.db.sql("""
        SELECT 
            ip.item_code,
            i.item_name,
            ip.price_list_rate,
            ip.currency,
            ip.valid_from,
            ip.price_list
        FROM `tabItem Price` ip
        JOIN `tabItem` i ON ip.item_code = i.name
        WHERE ip.valid_from BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY ip.valid_from DESC
        LIMIT 20
    """, {'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return {
        'items_summary': items_summary[0] if items_summary else {},
        'top_selling_items': top_selling_items,
        'top_purchase_items': top_purchase_items,
        'stock_levels': stock_levels,
        'low_stock_items': low_stock_items,
        'price_trends': price_trends
    }

@frappe.whitelist()
def get_item_groups_analysis(filters):
    """Get comprehensive item groups analysis"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Item Groups Summary
    groups_summary = frappe.db.sql("""
        SELECT 
            COUNT(DISTINCT ig.name) as total_groups,
            COUNT(DISTINCT i.name) as total_items
        FROM `tabItem Group` ig
        LEFT JOIN `tabItem` i ON i.item_group = ig.name
    """, as_dict=True)
    
    # Sales by Item Group
    sales_by_group = frappe.db.sql("""
        SELECT 
            i.item_group,
            COUNT(DISTINCT sii.item_code) as unique_items,
            SUM(sii.qty) as total_qty_sold,
            SUM(sii.amount) as total_sales_value,
            COUNT(DISTINCT si.name) as invoice_count,
            AVG(sii.rate) as avg_rate
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        JOIN `tabItem` i ON sii.item_code = i.name
        WHERE si.company = %(company)s
        AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND si.docstatus = 1
        GROUP BY i.item_group
        ORDER BY total_sales_value DESC
        LIMIT 15
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Purchases by Item Group
    purchases_by_group = frappe.db.sql("""
        SELECT 
            i.item_group,
            COUNT(DISTINCT pii.item_code) as unique_items,
            SUM(pii.qty) as total_qty_purchased,
            SUM(pii.amount) as total_purchase_value,
            COUNT(DISTINCT pi.name) as invoice_count,
            AVG(pii.rate) as avg_rate
        FROM `tabPurchase Invoice Item` pii
        JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
        JOIN `tabItem` i ON pii.item_code = i.name
        WHERE pi.company = %(company)s
        AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pi.docstatus = 1
        GROUP BY i.item_group
        ORDER BY total_purchase_value DESC
        LIMIT 15
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Stock Value by Item Group
    stock_by_group = frappe.db.sql("""
        SELECT 
            i.item_group,
            COUNT(DISTINCT b.item_code) as unique_items,
            SUM(b.actual_qty) as total_stock_qty,
            SUM(b.stock_value) as total_stock_value
        FROM `tabBin` b
        JOIN `tabItem` i ON b.item_code = i.name
        WHERE b.actual_qty > 0
        GROUP BY i.item_group
        ORDER BY total_stock_value DESC
        LIMIT 15
    """, as_dict=True)
    
    # Item Group Hierarchy
    group_hierarchy = frappe.db.sql("""
        SELECT 
            ig.name,
            ig.parent_item_group,
            ig.is_group,
            COUNT(i.name) as item_count
        FROM `tabItem Group` ig
        LEFT JOIN `tabItem` i ON i.item_group = ig.name
        GROUP BY ig.name
        ORDER BY ig.lft
    """, as_dict=True)
    
    return {
        'groups_summary': groups_summary[0] if groups_summary else {},
        'sales_by_group': sales_by_group,
        'purchases_by_group': purchases_by_group,
        'stock_by_group': stock_by_group,
        'group_hierarchy': group_hierarchy
    }

@frappe.whitelist()
def get_users_analysis(filters):
    """Get comprehensive users and system analysis"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Users Summary
    users_summary = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_users,
            COUNT(CASE WHEN u.enabled = 1 THEN 1 END) as active_users,
            COUNT(CASE WHEN u.user_type = 'System User' THEN 1 END) as system_users,
            COUNT(CASE WHEN u.user_type = 'Website User' THEN 1 END) as website_users
        FROM `tabUser` u
        WHERE u.name NOT IN ('Administrator', 'Guest')
    """, as_dict=True)
    
    # User Activity (Recent Logins)
    user_activity = frappe.db.sql("""
        SELECT 
            u.full_name,
            u.email,
            u.last_login,
            u.last_active,
            u.enabled,
            u.user_type
        FROM `tabUser` u
        WHERE u.name NOT IN ('Administrator', 'Guest')
        AND u.last_login IS NOT NULL
        ORDER BY u.last_login DESC
        LIMIT 20
    """, as_dict=True)
    
    # User Roles Distribution
    user_roles = frappe.db.sql("""
        SELECT 
            ur.role,
            COUNT(*) as user_count,
            COUNT(CASE WHEN u.enabled = 1 THEN 1 END) as active_user_count
        FROM `tabHas Role` ur
        JOIN `tabUser` u ON ur.parent = u.name
        WHERE u.name NOT IN ('Administrator', 'Guest')
        AND ur.role NOT IN ('All', 'Guest')
        GROUP BY ur.role
        ORDER BY user_count DESC
        LIMIT 15
    """, as_dict=True)
    
    # Document Creation by Users
    doc_creation = frappe.db.sql("""
        SELECT 
            'Sales Invoice' as doctype,
            owner as user,
            COUNT(*) as count
        FROM `tabSales Invoice`
        WHERE creation BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY owner
        
        UNION ALL
        
        SELECT 
            'Purchase Invoice' as doctype,
            owner as user,
            COUNT(*) as count
        FROM `tabPurchase Invoice`
        WHERE creation BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY owner
        
        UNION ALL
        
        SELECT 
            'Material Request' as doctype,
            owner as user,
            COUNT(*) as count
        FROM `tabMaterial Request`
        WHERE creation BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY owner
        
        ORDER BY count DESC
        LIMIT 20
    """, {'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # System Performance Metrics
    system_metrics = frappe.db.sql("""
        SELECT 
            COUNT(DISTINCT DATE(creation)) as active_days,
            COUNT(*) as total_transactions
        FROM `tabGL Entry`
        WHERE creation BETWEEN %(from_date)s AND %(to_date)s
    """, {'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return {
        'users_summary': users_summary[0] if users_summary else {},
        'user_activity': user_activity,
        'user_roles': user_roles,
        'doc_creation': doc_creation,
        'system_metrics': system_metrics[0] if system_metrics else {}
    }

@frappe.whitelist()
def get_payments_detailed(filters):
    """Get comprehensive payments analysis"""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    company = filters.get('company')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    
    # Payments Summary
    payments_summary = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_payments,
            SUM(pe.paid_amount) as total_paid_amount,
            SUM(pe.received_amount) as total_received_amount,
            AVG(pe.paid_amount) as avg_payment_amount,
            COUNT(DISTINCT pe.party) as unique_parties
        FROM `tabPayment Entry` pe
        WHERE pe.company = %(company)s
        AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pe.docstatus = 1
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Payments by Type
    payments_by_type = frappe.db.sql("""
        SELECT 
            pe.payment_type,
            COUNT(*) as count,
            SUM(pe.paid_amount) as total_amount
        FROM `tabPayment Entry` pe
        WHERE pe.company = %(company)s
        AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pe.docstatus = 1
        GROUP BY pe.payment_type
        ORDER BY total_amount DESC
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Payments by Mode
    payments_by_mode = frappe.db.sql("""
        SELECT 
            pe.mode_of_payment,
            COUNT(*) as count,
            SUM(pe.paid_amount) as total_amount
        FROM `tabPayment Entry` pe
        WHERE pe.company = %(company)s
        AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pe.docstatus = 1
        GROUP BY pe.mode_of_payment
        ORDER BY total_amount DESC
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Top Paying Customers
    top_paying_customers = frappe.db.sql("""
        SELECT 
            pe.party as customer,
            pe.party_name,
            COUNT(*) as payment_count,
            SUM(pe.paid_amount) as total_paid
        FROM `tabPayment Entry` pe
        WHERE pe.company = %(company)s
        AND pe.party_type = 'Customer'
        AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pe.docstatus = 1
        GROUP BY pe.party
        ORDER BY total_paid DESC
        LIMIT 15
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Payments to Suppliers
    payments_to_suppliers = frappe.db.sql("""
        SELECT 
            pe.party as supplier,
            pe.party_name,
            COUNT(*) as payment_count,
            SUM(pe.paid_amount) as total_paid
        FROM `tabPayment Entry` pe
        WHERE pe.company = %(company)s
        AND pe.party_type = 'Supplier'
        AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pe.docstatus = 1
        GROUP BY pe.party
        ORDER BY total_paid DESC
        LIMIT 15
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Monthly Payment Trends
    monthly_payments = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(pe.posting_date, '%%Y-%%m') as period,
            pe.payment_type,
            COUNT(*) as payment_count,
            SUM(pe.paid_amount) as total_amount
        FROM `tabPayment Entry` pe
        WHERE pe.company = %(company)s
        AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pe.docstatus = 1
        GROUP BY period, pe.payment_type
        ORDER BY period, pe.payment_type
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    # Recent Large Payments
    large_payments = frappe.db.sql("""
        SELECT 
            pe.name,
            pe.posting_date,
            pe.payment_type,
            pe.party_name,
            pe.paid_amount,
            pe.mode_of_payment,
            pe.reference_no
        FROM `tabPayment Entry` pe
        WHERE pe.company = %(company)s
        AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pe.paid_amount > 10000
        AND pe.docstatus = 1
        ORDER BY pe.paid_amount DESC
        LIMIT 20
    """, {'company': company, 'from_date': from_date, 'to_date': to_date}, as_dict=True)
    
    return {
        'payments_summary': payments_summary[0] if payments_summary else {},
        'payments_by_type': payments_by_type,
        'payments_by_mode': payments_by_mode,
        'top_paying_customers': top_paying_customers,
        'payments_to_suppliers': payments_to_suppliers,
        'monthly_payments': monthly_payments,
        'large_payments': large_payments
    }

@frappe.whitelist()
def export_executive_dashboard_data(filters):
    """Export comprehensive dashboard data to Excel"""
    
    try:
        import pandas as pd
        from io import BytesIO
        import base64
        
        # Get all dashboard data
        data = get_comprehensive_dashboard_data(filters)
        
        # Create Excel writer object
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Financial Summary
            if data.get('financial_summary'):
                financial_df = pd.DataFrame([data['financial_summary']])
                financial_df.to_excel(writer, sheet_name='Financial Summary', index=False)
            
            # Material Requests
            if data.get('material_requests', {}).get('recent_requests'):
                mr_df = pd.DataFrame(data['material_requests']['recent_requests'])
                mr_df.to_excel(writer, sheet_name='Material Requests', index=False)
            
            # Projects Overview
            if data.get('project_overview', {}).get('critical_projects'):
                projects_df = pd.DataFrame(data['project_overview']['critical_projects'])
                projects_df.to_excel(writer, sheet_name='Critical Projects', index=False)
            
            # Sales Overview
            if data.get('sales_overview', {}).get('top_customers'):
                sales_df = pd.DataFrame(data['sales_overview']['top_customers'])
                sales_df.to_excel(writer, sheet_name='Top Customers', index=False)
            
            # KPI Dashboard
            if data.get('kpi_dashboard'):
                kpi_df = pd.DataFrame([data['kpi_dashboard']])
                kpi_df.to_excel(writer, sheet_name='KPI Dashboard', index=False)
        
        # Return Excel file as base64
        output.seek(0)
        excel_data = output.read()
        
        return {
            'file_content': base64.b64encode(excel_data).decode('utf-8'),
            'filename': f'Executive_Dashboard_{frappe.utils.today()}.xlsx'
        }
        
    except ImportError:
        frappe.throw(_("pandas library is required for Excel export. Please install it using: bench pip install pandas openpyxl"))
    except Exception as e:
        frappe.log_error(f"Export error: {str(e)}", "Executive Dashboard Export")
        frappe.throw(_("Error generating Excel export: {0}").format(str(e)))

@frappe.whitelist()
def get_real_time_updates(last_update=None):
    """Get real-time updates for dashboard data"""
    import json
    from datetime import datetime, timedelta
    
    try:
        current_time = datetime.now()
        
        # If no last_update provided, assume 1 minute ago
        if not last_update:
            last_update_time = current_time - timedelta(minutes=1)
        else:
            last_update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
        
        # Check for recent changes in critical documents
        has_updates = False
        update_description = ""
        
        # Check for new sales invoices
        new_sales_invoices = frappe.db.count('Sales Invoice', {
            'creation': ['>', last_update_time],
            'docstatus': ['!=', 2]
        })
        
        # Check for new purchase invoices
        new_purchase_invoices = frappe.db.count('Purchase Invoice', {
            'creation': ['>', last_update_time],
            'docstatus': ['!=', 2]
        })
        
        # Check for new material requests
        new_material_requests = frappe.db.count('Material Request', {
            'creation': ['>', last_update_time],
            'docstatus': ['!=', 2]
        })
        
        # Check for new projects
        new_projects = frappe.db.count('Project', {
            'creation': ['>', last_update_time]
        })
        
        updates = []
        if new_sales_invoices > 0:
            updates.append(f"{new_sales_invoices} new sales invoice(s)")
            has_updates = True
            
        if new_purchase_invoices > 0:
            updates.append(f"{new_purchase_invoices} new purchase invoice(s)")
            has_updates = True
            
        if new_material_requests > 0:
            updates.append(f"{new_material_requests} new material request(s)")
            has_updates = True
            
        if new_projects > 0:
            updates.append(f"{new_projects} new project(s)")
            has_updates = True
        
        if has_updates:
            update_description = "Recent activity: " + ", ".join(updates)
        
        return {
            "has_updates": has_updates,
            "description": update_description,
            "timestamp": current_time.isoformat(),
            "new_sales_invoices": new_sales_invoices,
            "new_purchase_invoices": new_purchase_invoices,
            "new_material_requests": new_material_requests,
            "new_projects": new_projects
        }
        
    except Exception as e:
        frappe.log_error(f"Real-time updates error: {str(e)}", "Dashboard Real-time Updates")
        return {
            "has_updates": False,
            "description": "Error checking for updates",
            "error": str(e)
        } 

@frappe.whitelist()
def get_user_preferences():
    """Get user preferences and onboarding status"""
    try:
        user = frappe.session.user
        
        # Get user preferences from User document or custom settings
        user_doc = frappe.get_doc("User", user)
        
        # Check if user has completed onboarding (you may need to add this field to User doctype)
        onboarding_completed = False
        if hasattr(user_doc, 'dashboard_onboarding_completed'):
            onboarding_completed = user_doc.dashboard_onboarding_completed
        
        # Get saved preferences (you may need to add this field to User doctype)
        preferences = {}
        if hasattr(user_doc, 'dashboard_preferences') and user_doc.dashboard_preferences:
            try:
                preferences = json.loads(user_doc.dashboard_preferences)
            except:
                preferences = {}
        
        # Get user role for permissions
        user_roles = frappe.get_roles(user)
        primary_role = user_roles[0] if user_roles else "Guest"
        
        return {
            "preferences": preferences,
            "role": primary_role,
            "is_first_time": not onboarding_completed,
            "user_roles": user_roles
        }
        
    except Exception as e:
        log_error("get_user_preferences", e)
        return {
            "preferences": {},
            "role": "Guest",
            "is_first_time": True,
            "user_roles": ["Guest"]
        }

@frappe.whitelist()
def save_user_preferences(preferences):
    """Save user preferences"""
    try:
        user = frappe.session.user
        
        # Validate preferences
        if not isinstance(preferences, dict):
            if isinstance(preferences, str):
                preferences = json.loads(preferences)
            else:
                preferences = {}
        
        # Save preferences to User document (you may need to add this field to User doctype)
        user_doc = frappe.get_doc("User", user)
        if hasattr(user_doc, 'dashboard_preferences'):
            user_doc.dashboard_preferences = json.dumps(preferences)
            user_doc.save(ignore_permissions=True)
        
        return {"status": "success", "message": "Preferences saved successfully"}
        
    except Exception as e:
        log_error("save_user_preferences", e, {"preferences": preferences})
        return {"status": "error", "message": "Failed to save preferences"}

@frappe.whitelist()
def complete_onboarding():
    """Mark user onboarding as completed"""
    try:
        user = frappe.session.user
        
        # Update user document to mark onboarding as completed (you may need to add this field to User doctype)
        user_doc = frappe.get_doc("User", user)
        if hasattr(user_doc, 'dashboard_onboarding_completed'):
            user_doc.dashboard_onboarding_completed = 1
            user_doc.save(ignore_permissions=True)
        
        return {"status": "success", "message": "Onboarding completed"}
        
    except Exception as e:
        log_error("complete_onboarding", e)
        return {"status": "error", "message": "Failed to complete onboarding"}

@frappe.whitelist()
def get_user_permissions():
    """Get user permissions and accessible modules"""
    try:
        user = frappe.session.user
        user_roles = frappe.get_roles(user)
        
        # Define module access based on roles
        module_permissions = {
            "System Manager": ["ai_assistant", "overview", "financial", "projects", "hr", "sales", "materials", "bank_cash", "purchase_orders", "operations", "risk_management"],
            "CEO": ["ai_assistant", "overview", "financial", "projects", "hr", "sales", "risk_management"],
            "Directors": ["ai_assistant", "overview", "financial", "projects", "hr", "sales"],
            "General Manager": ["ai_assistant", "overview", "financial", "projects", "hr", "sales", "operations"],
            "Accounts Manager": ["ai_assistant", "overview", "financial", "bank_cash", "purchase_orders"],
            "Projects Manager": ["ai_assistant", "overview", "projects", "materials", "purchase_orders"],
            "HR Manager": ["ai_assistant", "overview", "hr"],
            "Sales Manager": ["ai_assistant", "overview", "sales"],
            "Purchase Manager": ["ai_assistant", "overview", "materials", "purchase_orders"],
            "Stock Manager": ["ai_assistant", "overview", "materials", "operations"],
            "Guest": ["ai_assistant", "overview"]
        }
        
        # Get accessible modules based on user roles
        accessible_modules = set()
        primary_role = "Guest"
        
        for role in user_roles:
            if role in module_permissions:
                accessible_modules.update(module_permissions[role])
                if role != "All" and primary_role == "Guest":
                    primary_role = role
        
        # Ensure basic access
        if not accessible_modules:
            accessible_modules = {"ai_assistant", "overview"}
        
        return {
            "accessible_modules": list(accessible_modules),
            "role": primary_role,
            "user_roles": user_roles
        }
        
    except Exception as e:
        log_error("get_user_permissions", e)
        return {
            "accessible_modules": ["ai_assistant", "overview"],
            "role": "Guest",
            "user_roles": ["Guest"]
        }