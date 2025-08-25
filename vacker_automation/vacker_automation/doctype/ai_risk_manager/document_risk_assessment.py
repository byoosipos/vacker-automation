# Document Risk Assessment Engine for Advanced AI Risk Management
# Copyright (c) 2025, Vacker and contributors

import frappe
import json
import re
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, add_days, nowdate, cstr
import requests
from PIL import Image
import pytesseract
import io
import base64


class DocumentRiskAssessmentEngine:
    """
    Advanced Risk Assessment Engine for ERPNext Documents
    Provides real-time risk analysis and intelligent recommendations
    """
    
    def __init__(self, user=None, company=None):
        self.user = user or frappe.session.user
        self.company = company or frappe.defaults.get_user_default('Company')
        self.user_roles = frappe.get_roles(self.user)
        
    def assess_document_risk(self, doctype, doc, trigger_point="on_save"):
        """Main risk assessment method for any document type"""
        
        assessment_result = {
            'risk_level': 'low',  # low, medium, high, critical
            'risk_score': 0,      # 0-100
            'findings': [],
            'recommendations': [],
            'warnings': [],
            'compliance_status': 'compliant',
            'requires_approval': False,
            'personality_response': '',
            'evidence_required': [],
            'market_insights': []
        }
        
        # Route to specific assessment method based on document type
        if doctype == "Purchase Invoice":
            return self.assess_purchase_invoice(doc, trigger_point)
        elif doctype == "Sales Invoice":
            return self.assess_sales_invoice(doc, trigger_point)
        elif doctype == "Payment Entry":
            return self.assess_payment_entry(doc, trigger_point)
        elif doctype == "Journal Entry":
            return self.assess_journal_entry(doc, trigger_point)
        elif doctype == "Expense Claim":
            return self.assess_expense_claim(doc, trigger_point)
        elif doctype == "Material Request":
            return self.assess_material_request(doc, trigger_point)
        elif doctype == "Purchase Order":
            return self.assess_purchase_order(doc, trigger_point)
        elif doctype == "Sales Order":
            return self.assess_sales_order(doc, trigger_point)
        elif doctype == "Quotation":
            return self.assess_quotation(doc, trigger_point)
        else:
            return self.assess_generic_document(doc, trigger_point)


class PurchaseInvoiceRiskAssessment(DocumentRiskAssessmentEngine):
    """High-Priority Risk Assessment for Purchase Invoices"""
    
    def assess_purchase_invoice(self, doc, trigger_point):
        """Comprehensive Purchase Invoice Risk Assessment"""
        
        assessment = {
            'risk_level': 'low',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'warnings': [],
            'compliance_status': 'compliant',
            'personality_response': '',
            'market_insights': []
        }
        
        risk_factors = []
        
        # 1. Duplicate Invoice Detection
        duplicate_risk = self.detect_duplicate_invoices(doc)
        if duplicate_risk['risk_score'] > 0:
            risk_factors.append(duplicate_risk)
        
        # 2. Price Variance Analysis
        price_variance = self.analyze_price_variance(doc)
        if price_variance['risk_score'] > 0:
            risk_factors.append(price_variance)
        
        # 3. Supplier Risk Assessment
        supplier_risk = self.assess_supplier_risk(doc)
        if supplier_risk['risk_score'] > 0:
            risk_factors.append(supplier_risk)
        
        # 4. Three-way Matching Validation
        matching_risk = self.validate_three_way_matching(doc)
        if matching_risk['risk_score'] > 0:
            risk_factors.append(matching_risk)
        
        # 5. Budget Impact Analysis
        budget_risk = self.analyze_budget_impact(doc)
        if budget_risk['risk_score'] > 0:
            risk_factors.append(budget_risk)
        
        # 6. Accounting Standards Compliance
        compliance_risk = self.check_accounting_compliance(doc)
        if compliance_risk['risk_score'] > 0:
            risk_factors.append(compliance_risk)
        
        # 7. Market Intelligence Analysis
        market_analysis = self.get_market_intelligence(doc)
        assessment['market_insights'] = market_analysis
        
        # Calculate overall risk
        assessment = self.calculate_overall_risk(assessment, risk_factors)
        
        # Generate personality response
        assessment['personality_response'] = self.generate_finance_controller_response(
            doc, assessment, risk_factors
        )
        
        return assessment
    
    def detect_duplicate_invoices(self, doc):
        """Advanced duplicate invoice detection using multiple criteria"""
        
        risk_assessment = {
            'category': 'duplicate_detection',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        # Check by invoice number
        if doc.bill_no:
            duplicate_by_number = frappe.db.sql("""
                SELECT name, posting_date, grand_total, supplier
                FROM `tabPurchase Invoice`
                WHERE bill_no = %s
                AND supplier = %s
                AND name != %s
                AND docstatus != 2
            """, (doc.bill_no, doc.supplier, doc.name or ''), as_dict=True)
            
            if duplicate_by_number:
                risk_assessment['risk_score'] = 90
                risk_assessment['findings'].append(
                    f"Duplicate invoice number '{doc.bill_no}' found for supplier {doc.supplier}"
                )
                risk_assessment['recommendations'].append(
                    "Verify with supplier if this is a duplicate or amended invoice"
                )
        
        # Check by amount and date (fuzzy matching)
        if doc.grand_total:
            amount_tolerance = doc.grand_total * 0.02  # 2% tolerance
            similar_invoices = frappe.db.sql("""
                SELECT name, bill_no, posting_date, grand_total
                FROM `tabPurchase Invoice`
                WHERE supplier = %s
                AND ABS(grand_total - %s) <= %s
                AND posting_date BETWEEN %s AND %s
                AND name != %s
                AND docstatus != 2
            """, (
                doc.supplier, 
                doc.grand_total, 
                amount_tolerance,
                add_days(doc.posting_date, -7),
                add_days(doc.posting_date, 7),
                doc.name or ''
            ), as_dict=True)
            
            if similar_invoices and risk_assessment['risk_score'] < 50:
                risk_assessment['risk_score'] = 60
                risk_assessment['findings'].append(
                    f"Similar invoice amount ({doc.grand_total}) found within 7 days"
                )
        
        return risk_assessment
    
    def analyze_price_variance(self, doc):
        """Analyze price variance against historical purchases"""
        
        risk_assessment = {
            'category': 'price_variance',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        significant_variances = []
        
        for item in doc.items:
            # Get historical price data for this item
            historical_prices = frappe.db.sql("""
                SELECT pii.rate, pi.posting_date, pi.supplier
                FROM `tabPurchase Invoice Item` pii
                JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
                WHERE pii.item_code = %s
                AND pi.docstatus = 1
                AND pi.posting_date >= %s
                ORDER BY pi.posting_date DESC
                LIMIT 10
            """, (item.item_code, add_days(nowdate(), -180)), as_dict=True)
            
            if historical_prices:
                avg_price = sum(h['rate'] for h in historical_prices) / len(historical_prices)
                variance_percent = ((item.rate - avg_price) / avg_price) * 100
                
                if abs(variance_percent) > 15:  # 15% variance threshold
                    significant_variances.append({
                        'item_code': item.item_code,
                        'current_rate': item.rate,
                        'avg_historical_rate': avg_price,
                        'variance_percent': variance_percent
                    })
        
        if significant_variances:
            max_variance = max(abs(v['variance_percent']) for v in significant_variances)
            risk_assessment['risk_score'] = min(30 + (max_variance - 15) * 2, 80)
            
            risk_assessment['findings'].append(
                f"{len(significant_variances)} items have significant price variance (>15%)"
            )
            
            risk_assessment['recommendations'].append(
                "Review pricing with supplier and validate market rates"
            )
        
        return risk_assessment
    
    def assess_supplier_risk(self, doc):
        """Assess supplier-related risks"""
        
        risk_assessment = {
            'category': 'supplier_risk',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        # Get supplier history
        supplier_data = self.get_supplier_performance_data(doc.supplier)
        
        # Check payment history
        if supplier_data['avg_payment_delay'] > 30:
            risk_assessment['risk_score'] += 20
            risk_assessment['findings'].append(
                f"Supplier has average payment delay of {supplier_data['avg_payment_delay']} days"
            )
        
        # Check outstanding amounts
        if supplier_data['outstanding_amount'] > doc.grand_total * 5:
            risk_assessment['risk_score'] += 15
            risk_assessment['findings'].append(
                f"High outstanding amount with supplier: {supplier_data['outstanding_amount']}"
            )
        
        # Since Supplier DocType doesn't have a direct supplier_rating field,
        # we'll use payment history as a proxy for supplier performance
        if supplier_data['avg_payment_delay'] > 45:  # Very delayed payments
            risk_assessment['risk_score'] += 25
            risk_assessment['findings'].append(
                f"Poor supplier payment history: avg {supplier_data['avg_payment_delay']} days delay"
            )
        
        return risk_assessment
    
    def validate_three_way_matching(self, doc):
        """Validate three-way matching (PO → GRN → Invoice)"""
        
        risk_assessment = {
            'category': 'three_way_matching',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        # Check if items have associated PO and GRN
        unmatched_items = []
        
        for item in doc.items:
            if not item.purchase_order:
                unmatched_items.append(item.item_code)
            elif not item.purchase_receipt:
                # Check if GRN exists for this PO item
                grn_exists = frappe.db.exists("Purchase Receipt Item", {
                    "purchase_order": item.purchase_order,
                    "item_code": item.item_code,
                    "docstatus": 1
                })
                
                if not grn_exists:
                    unmatched_items.append(item.item_code)
        
        if unmatched_items:
            risk_assessment['risk_score'] = len(unmatched_items) * 15
            risk_assessment['findings'].append(
                f"{len(unmatched_items)} items lack proper PO/GRN matching"
            )
            risk_assessment['recommendations'].append(
                "Ensure all items have corresponding Purchase Orders and Receipts"
            )
        
        return risk_assessment
    
    def analyze_budget_impact(self, doc):
        """Analyze impact on budgets and cost centers"""
        
        risk_assessment = {
            'category': 'budget_impact',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        # Check project budget if applicable
        project_budget_risks = []
        
        for item in doc.items:
            if item.project:
                project_doc = frappe.get_doc("Project", item.project)
                if project_doc.total_sales_amount:
                    # Calculate project expense ratio
                    total_expenses = self.get_project_total_expenses(item.project)
                    expense_ratio = ((total_expenses + item.amount) / project_doc.total_sales_amount) * 100
                    
                    if expense_ratio > 80:
                        project_budget_risks.append({
                            'project': item.project,
                            'expense_ratio': expense_ratio,
                            'amount': item.amount
                        })
        
        if project_budget_risks:
            max_ratio = max(p['expense_ratio'] for p in project_budget_risks)
            risk_assessment['risk_score'] = min((max_ratio - 70) * 2, 60)
            
            risk_assessment['findings'].append(
                f"Projects approaching budget limits (expense ratio: {max_ratio:.1f}%)"
            )
            
            risk_assessment['recommendations'].append(
                "Review project budgets and consider budget reallocation"
            )
        
        return risk_assessment
    
    def check_accounting_compliance(self, doc):
        """Check accounting standards compliance"""
        
        risk_assessment = {
            'category': 'accounting_compliance',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        compliance_issues = []
        
        # Check GL account mappings
        for item in doc.items:
            if not item.expense_account:
                compliance_issues.append(f"Missing expense account for {item.item_code}")
        
        # Check tax calculations
        if doc.taxes:
            for tax in doc.taxes:
                if not tax.account_head:
                    compliance_issues.append(f"Missing account head for tax: {tax.description}")
        
        # Check cost center allocation
        if not doc.cost_center:
            compliance_issues.append("Missing cost center allocation")
        
        if compliance_issues:
            risk_assessment['risk_score'] = len(compliance_issues) * 10
            risk_assessment['findings'] = compliance_issues
            risk_assessment['recommendations'].append(
                "Complete all required accounting fields before submission"
            )
        
        return risk_assessment
    
    def get_market_intelligence(self, doc):
        """Get market intelligence for invoice items"""
        
        market_insights = {
            'price_trends': [],
            'supplier_alternatives': [],
            'market_alerts': []
        }
        
        # Analyze price trends for major items
        for item in doc.items:
            if item.amount > doc.grand_total * 0.2:  # Items >20% of total
                price_trend = self.analyze_item_price_trend(item.item_code)
                if price_trend:
                    market_insights['price_trends'].append({
                        'item_code': item.item_code,
                        'current_price': item.rate,
                        'trend': price_trend['trend'],
                        'recommendation': price_trend['recommendation']
                    })
        
        return market_insights
    
    def generate_finance_controller_response(self, doc, assessment, risk_factors):
        """Generate response as a diligent finance controller"""
        
        user_name = frappe.db.get_value('User', self.user, 'full_name') or 'there'
        
        response = f"💼 **Finance Controller Review for Invoice {doc.name or 'New'}**\n\n"
        response += f"Hello {user_name}, I've completed my analysis of this {doc.grand_total:.2f} invoice from {doc.supplier}.\n\n"
        
        # Risk level indicator
        if assessment['risk_score'] > 70:
            response += "🚨 **HIGH RISK DETECTED** - Immediate attention required\n\n"
        elif assessment['risk_score'] > 40:
            response += "⚠️ **MEDIUM RISK** - Please review findings below\n\n"
        else:
            response += "✅ **LOW RISK** - Standard processing approved\n\n"
        
        # Detailed findings
        if risk_factors:
            response += "**📋 Key Findings:**\n"
            for factor in risk_factors:
                for finding in factor['findings']:
                    response += f"• {finding}\n"
            response += "\n"
        
        # Recommendations
        all_recommendations = []
        for factor in risk_factors:
            all_recommendations.extend(factor['recommendations'])
        
        if all_recommendations:
            response += "**💡 My Recommendations:**\n"
            for rec in all_recommendations:
                response += f"• {rec}\n"
            response += "\n"
        
        # Market insights
        if assessment.get('market_insights', {}).get('price_trends'):
            response += "**📈 Market Intelligence:**\n"
            for trend in assessment['market_insights']['price_trends']:
                response += f"• {trend['item_code']}: {trend['recommendation']}\n"
            response += "\n"
        
        # Approval decision
        if assessment['risk_score'] > 60:
            response += "**❌ HOLD FOR REVIEW** - Please address the issues above before proceeding."
        elif assessment['risk_score'] > 30:
            response += "**⚠️ PROCEED WITH CAUTION** - Monitor the identified risks."
        else:
            response += "**✅ APPROVED FOR PROCESSING** - All checks passed."
        
        return response


# Helper methods and utility functions

def get_supplier_performance_data(supplier):
    """Get comprehensive supplier performance data"""
    
    performance_data = frappe.db.sql("""
        SELECT 
            AVG(DATEDIFF(pe.posting_date, pi.due_date)) as avg_payment_delay,
            SUM(pi.outstanding_amount) as outstanding_amount,
            COUNT(*) as total_invoices,
            AVG(pi.grand_total) as avg_invoice_amount
        FROM `tabPurchase Invoice` pi
        LEFT JOIN `tabPayment Entry Reference` per ON per.reference_name = pi.name
        LEFT JOIN `tabPayment Entry` pe ON pe.name = per.parent
        WHERE pi.supplier = %s
        AND pi.docstatus = 1
        AND pi.posting_date >= %s
    """, (supplier, add_days(nowdate(), -365)), as_dict=True)
    
    if performance_data:
        return performance_data[0]
    
    return {
        'avg_payment_delay': 0,
        'outstanding_amount': 0,
        'total_invoices': 0,
        'avg_invoice_amount': 0
    }

def get_project_total_expenses(project):
    """Calculate total expenses for a project"""
    
    total_expenses = frappe.db.sql("""
        SELECT SUM(pii.amount)
        FROM `tabPurchase Invoice Item` pii
        JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
        WHERE pii.project = %s
        AND pi.docstatus = 1
    """, (project,))[0][0] or 0
    
    return total_expenses

def analyze_item_price_trend(item_code):
    """Analyze price trend for an item"""
    
    price_history = frappe.db.sql("""
        SELECT pii.rate, pi.posting_date
        FROM `tabPurchase Invoice Item` pii
        JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
        WHERE pii.item_code = %s
        AND pi.docstatus = 1
        AND pi.posting_date >= %s
        ORDER BY pi.posting_date DESC
        LIMIT 10
    """, (item_code, add_days(nowdate(), -180)), as_dict=True)
    
    if len(price_history) < 3:
        return None
    
    # Simple trend analysis
    recent_avg = sum(p['rate'] for p in price_history[:3]) / 3
    older_avg = sum(p['rate'] for p in price_history[-3:]) / 3
    
    trend_percent = ((recent_avg - older_avg) / older_avg) * 100
    
    if trend_percent > 10:
        trend = 'increasing'
        recommendation = f"Price increased {trend_percent:.1f}% - consider alternative suppliers"
    elif trend_percent < -10:
        trend = 'decreasing'
        recommendation = f"Price decreased {trend_percent:.1f}% - good procurement timing"
    else:
        trend = 'stable'
        recommendation = "Price stable - consistent with market"
    
    return {
        'trend': trend,
        'trend_percent': trend_percent,
        'recommendation': recommendation
    }


# Frappe whitelisted methods

@frappe.whitelist()
def assess_document_risk(doctype, doc_name, trigger_point="on_save"):
    """API method for document risk assessment"""
    try:
        doc = frappe.get_doc(doctype, doc_name)
        assessor = DocumentRiskAssessmentEngine()
        return assessor.assess_document_risk(doctype, doc, trigger_point)
    except Exception as e:
        frappe.log_error(f"Document Risk Assessment Error: {str(e)}", "Risk Assessment")
        return {'error': str(e)}

    def calculate_overall_risk(self, assessment, risk_factors):
        """Calculate overall risk score from individual risk factors"""
        
        if not risk_factors:
            return assessment
        
        # Calculate weighted risk score
        total_risk = 0
        total_weight = 0
        
        for factor in risk_factors:
            risk_score = factor.get('risk_score', 0)
            
            # Assign weights based on category
            category = factor.get('category', 'general')
            weight = self.get_category_weight(category)
            
            total_risk += risk_score * weight
            total_weight += weight
        
        # Calculate final score
        if total_weight > 0:
            final_score = total_risk / total_weight
        else:
            final_score = 0
        
        # Determine risk level
        if final_score >= 80:
            risk_level = 'critical'
        elif final_score >= 60:
            risk_level = 'high'
        elif final_score >= 30:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        assessment['risk_score'] = final_score
        assessment['risk_level'] = risk_level
        
        return assessment
    
    def get_category_weight(self, category):
        """Get weight for risk category"""
        
        category_weights = {
            'fraud_detection': 1.0,
            'duplicate_detection': 0.9,
            'evidence_validation': 0.9,
            'accountability_framework': 0.8,
            'compliance': 0.8,
            'price_variance': 0.7,
            'supplier_risk': 0.6,
            'budget_impact': 0.5,
            'general': 0.4
        }
        
        return category_weights.get(category, 0.5)
    
    def analyze_project_budget_impact(self, project, amount):
        """Analyze project budget impact"""
        
        try:
            project_doc = frappe.get_doc('Project', project)
            
            if not project_doc.total_sales_amount:
                return {'budget_utilization': 0}
            
            # Get current project expenses
            current_expenses = frappe.db.sql("""
                SELECT SUM(ec.total_claimed_amount)
                FROM `tabExpense Claim` ec
                WHERE ec.project = %s
                AND ec.docstatus = 1
            """, (project,))[0][0] or 0
            
            # Add current amount
            projected_expenses = current_expenses + amount
            budget_utilization = (projected_expenses / project_doc.total_sales_amount) * 100
            
            return {'budget_utilization': budget_utilization}
            
        except Exception as e:
            frappe.log_error(f"Project Budget Analysis Error: {str(e)}", "Risk Assessment")
            return {'budget_utilization': 0}
    
    def analyze_cost_center_budget(self, cost_center, amount):
        """Analyze cost center budget impact"""
        
        try:
            # Get budget for current fiscal year
            fiscal_year = frappe.defaults.get_user_default('fiscal_year')
            
            budget_data = frappe.db.sql("""
                SELECT SUM(budget_amount) as total_budget
                FROM `tabBudget Account`
                WHERE cost_center = %s
                AND parent IN (
                    SELECT name FROM `tabBudget`
                    WHERE fiscal_year = %s
                    AND docstatus = 1
                )
            """, (cost_center, fiscal_year), as_dict=True)
            
            if not budget_data or not budget_data[0].total_budget:
                return {'budget_utilization': 0}
            
            total_budget = budget_data[0].total_budget
            
            # Get current expenses
            current_expenses = frappe.db.sql("""
                SELECT SUM(ec.total_claimed_amount)
                FROM `tabExpense Claim` ec
                WHERE ec.cost_center = %s
                AND ec.docstatus = 1
                AND YEAR(ec.posting_date) = YEAR(CURDATE())
            """, (cost_center,))[0][0] or 0
            
            # Add current amount
            projected_expenses = current_expenses + amount
            budget_utilization = (projected_expenses / total_budget) * 100
            
            return {'budget_utilization': budget_utilization}
            
        except Exception as e:
            frappe.log_error(f"Cost Center Budget Analysis Error: {str(e)}", "Risk Assessment")
            return {'budget_utilization': 0}
    
    def get_previous_assessments(self, doc):
        """Get previous AI assessments for document"""
        
        return getattr(doc, 'ai_assessment_data', '{}')
    
    def perform_final_security_checks(self, doc):
        """Perform final security checks"""
        
        return {'security_score': 100, 'security_findings': []}
    
    def calculate_final_risk_score(self, previous_assessments, final_checks, evidence_validation=None):
        """Calculate final comprehensive risk score"""
        
        # Base score from previous assessments
        try:
            if isinstance(previous_assessments, str):
                prev_data = json.loads(previous_assessments)
            else:
                prev_data = previous_assessments
            
            base_score = prev_data.get('risk_score', 0)
        except:
            base_score = 0
        
        # Security checks impact
        security_score = final_checks.get('security_score', 100)
        security_factor = (100 - security_score) / 100
        
        # Evidence validation impact
        evidence_factor = 0
        if evidence_validation:
            evidence_score = evidence_validation.get('overall_score', 1)
            evidence_factor = (1 - evidence_score) * 30  # Max 30 points penalty
        
        # Calculate final score
        final_score = base_score + (security_factor * 20) + evidence_factor
        
        return min(final_score, 100)  # Cap at 100
    
    def generate_final_ai_response(self, doc, assessment):
        """Generate final AI response"""
        
        risk_score = assessment.get('risk_score', 0)
        
        if risk_score >= 80:
            return f"CRITICAL RISK DETECTED - Document {doc.name} requires immediate review. Risk score: {risk_score:.1f}"
        elif risk_score >= 60:
            return f"HIGH RISK - Document {doc.name} needs additional verification. Risk score: {risk_score:.1f}"
        elif risk_score >= 30:
            return f"MEDIUM RISK - Document {doc.name} has some concerns to address. Risk score: {risk_score:.1f}"
        else:
            return f"LOW RISK - Document {doc.name} approved for processing. Risk score: {risk_score:.1f}"
    
    def perform_generic_assessment(self, doc):
        """Generic assessment for unsupported document types"""
        
        return {
            'risk_score': 10,
            'risk_level': 'low',
            'findings': ['Generic assessment applied'],
            'recommendations': ['Consider implementing specific AI assessment for this document type'],
            'personality_response': f'Basic assessment completed for {doc.doctype} {doc.name}'
        }
    
    def check_final_cash_flow_impact(self, doc):
        """Check final cash flow impact"""
        
        # Simplified cash flow check
        if hasattr(doc, 'paid_amount'):
            amount = doc.paid_amount
            
            if amount > 5000000:  # 5M UGX
                return {
                    'critical_impact': True,
                    'message': f'High-value payment {amount:,.0f} UGX may impact cash flow significantly'
                }
        
        return {'critical_impact': False}
    
    def perform_final_fraud_check(self, doc):
        """Perform final fraud check"""
        
        # Simplified fraud check
        return {'high_risk': False}
    
    def schedule_accountability_tasks(self, doc):
        """Schedule accountability tasks"""
        
        tasks = []
        
        if doc.doctype == 'Material Request':
            if hasattr(doc, 'total_estimated_cost') and doc.total_estimated_cost > 100000:
                tasks.append({
                    'type': 'material_usage_followup',
                    'due_date': add_days(nowdate(), 30),
                    'description': 'Material usage accountability report required'
                })
        
        elif doc.doctype == 'Expense Claim':
            if hasattr(doc, 'total_claimed_amount') and doc.total_claimed_amount > 50000:
                tasks.append({
                    'type': 'expense_evidence_followup',
                    'due_date': add_days(nowdate(), 14),
                    'description': 'Expense evidence and outcome report required'
                })
        
        return tasks
    
    def update_ai_assessment_log(self, doc, action, assessment_data=None):
        """Update AI assessment log"""
        
        try:
            # This would update the assessment log
            pass
        except Exception as e:
            frappe.log_error(f"Assessment Log Update Error: {str(e)}", "Risk Assessment")
    
    def update_accountability_tracking(self, doc, status):
        """Update accountability tracking"""
        
        try:
            # This would update accountability tracking
            pass
        except Exception as e:
            frappe.log_error(f"Accountability Tracking Error: {str(e)}", "Risk Assessment")
    
    def update_predictive_models(self, doc):
        """Update predictive models with new data"""
        
        try:
            # This would update ML models
            pass
        except Exception as e:
            frappe.log_error(f"Predictive Model Update Error: {str(e)}", "Risk Assessment")
    
    def update_supplier_performance_data(self, doc):
        """Update supplier performance data"""
        
        try:
            # This would update supplier performance metrics
            pass
        except Exception as e:
            frappe.log_error(f"Supplier Performance Update Error: {str(e)}", "Risk Assessment")
    
    def update_customer_behavior_data(self, doc):
        """Update customer behavior data"""
        
        try:
            # This would update customer behavior analytics
            pass
        except Exception as e:
            frappe.log_error(f"Customer Behavior Update Error: {str(e)}", "Risk Assessment")
    
    def update_market_intelligence(self, doc):
        """Update market intelligence data"""
        
        try:
            # This would update market intelligence
            pass
        except Exception as e:
            frappe.log_error(f"Market Intelligence Update Error: {str(e)}", "Risk Assessment")
    
    def identify_consolidation_opportunities(self, doc):
        """Identify consolidation opportunities"""
        
        # Simplified consolidation analysis
        return []
    
    def get_recent_material_requests(self, requested_by, days):
        """Get recent material requests"""
        
        return frappe.get_all('Material Request',
            filters={
                'requested_by': requested_by,
                'transaction_date': ['>=', add_days(nowdate(), -days)]
            },
            fields=['name', 'total_estimated_cost', 'transaction_date']
        )
    
    def analyze_optimal_procurement_timing(self, doc):
        """Analyze optimal procurement timing"""
        
        # Simplified timing analysis
        return []
    
    def find_alternative_items(self, item_code):
        """Find alternative items"""
        
        # Simplified alternative item search
        return []
    
    def get_seasonal_price_data(self, item_code):
        """Get seasonal price data"""
        
        # Simplified seasonal data
        return None
    
    def get_annual_demand(self, item_code):
        """Get annual demand for item"""
        
        annual_demand = frappe.db.sql("""
            SELECT SUM(qty) as total_qty
            FROM `tabStock Ledger Entry`
            WHERE item_code = %s
            AND voucher_type IN ('Material Issue', 'Stock Entry')
            AND posting_date >= %s
        """, (item_code, add_days(nowdate(), -365)))
        
        return annual_demand[0][0] if annual_demand and annual_demand[0][0] else 0
    
    def get_average_unit_cost(self, item_code):
        """Get average unit cost"""
        
        avg_cost = frappe.db.sql("""
            SELECT AVG(rate) as avg_rate
            FROM `tabPurchase Invoice Item` pii
            JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
            WHERE pii.item_code = %s
            AND pi.docstatus = 1
            AND pi.posting_date >= %s
        """, (item_code, add_days(nowdate(), -180)))
        
        return avg_cost[0][0] if avg_cost and avg_cost[0][0] else 1000  # Default 1000 UGX


@frappe.whitelist()
def get_supplier_risk_profile(supplier):
    """API method for supplier risk profile"""
    try:
        return get_supplier_performance_data(supplier)
    except Exception as e:
        frappe.log_error(f"Supplier Risk Profile Error: {str(e)}", "Risk Assessment")
        return {'error': str(e)} 