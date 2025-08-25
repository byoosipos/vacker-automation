# Sales Invoice Intelligence for Advanced AI Risk Assessment
# Copyright (c) 2025, Vacker and contributors

import frappe
import json
import re
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, add_days, nowdate, cstr
from .document_risk_assessment import DocumentRiskAssessmentEngine


class SalesInvoiceIntelligence(DocumentRiskAssessmentEngine):
    """
    Act as experienced sales controller ensuring revenue integrity
    Comprehensive risk assessment for sales invoices
    """
    
    def assess_sales_invoice(self, doc, trigger_point):
        """Comprehensive Sales Invoice Risk Assessment"""
        
        assessment = {
            'risk_level': 'low',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'warnings': [],
            'compliance_status': 'compliant',
            'personality_response': '',
            'revenue_insights': []
        }
        
        risk_factors = []
        
        # 1. Customer Credit Limit Validation
        credit_risk = self.validate_customer_credit_limit(doc)
        if credit_risk['risk_score'] > 0:
            risk_factors.append(credit_risk)
        
        # 2. Pricing Strategy Alignment
        pricing_risk = self.check_pricing_strategy_alignment(doc)
        if pricing_risk['risk_score'] > 0:
            risk_factors.append(pricing_risk)
        
        # 3. Revenue Recognition Compliance
        revenue_compliance = self.assess_revenue_recognition_compliance(doc)
        if revenue_compliance['risk_score'] > 0:
            risk_factors.append(revenue_compliance)
        
        # 4. Profit Margin Analysis
        margin_analysis = self.analyze_profit_margin_variance(doc)
        if margin_analysis['risk_score'] > 0:
            risk_factors.append(margin_analysis)
        
        # 5. Tax Calculation Validation
        tax_validation = self.validate_tax_calculations(doc)
        if tax_validation['risk_score'] > 0:
            risk_factors.append(tax_validation)
        
        # 6. Delivery Confirmation Check
        delivery_check = self.check_delivery_confirmation(doc)
        if delivery_check['risk_score'] > 0:
            risk_factors.append(delivery_check)
        
        # 7. Customer Payment Behavior Analysis
        payment_behavior = self.analyze_customer_payment_behavior(doc)
        assessment['revenue_insights'] = payment_behavior
        
        # Calculate overall risk
        assessment = self.calculate_overall_risk(assessment, risk_factors)
        
        # Generate personality response
        assessment['personality_response'] = self.generate_sales_controller_response(
            doc, assessment, risk_factors
        )
        
        return assessment
    
    def validate_customer_credit_limit(self, doc):
        """Validate customer credit limit and exposure"""
        
        risk_assessment = {
            'category': 'credit_limit_validation',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        # Import the proper function for getting credit limit
        from erpnext.selling.doctype.customer.customer import get_credit_limit
        
        # Get current outstanding
        outstanding_amount = frappe.db.sql("""
            SELECT SUM(si.outstanding_amount)
            FROM `tabSales Invoice` si
            WHERE si.customer = %s
            AND si.docstatus = 1
            AND si.outstanding_amount > 0
        """, (doc.customer,))[0][0] or 0
        
        # Add current invoice amount
        total_exposure = outstanding_amount + doc.grand_total
        
        # Check credit limit using proper ERPNext function
        credit_limit = get_credit_limit(doc.customer, doc.company)
        if credit_limit and credit_limit > 0:
            utilization_percent = (total_exposure / credit_limit) * 100
            
            if utilization_percent > 100:
                risk_assessment['risk_score'] = 85
                risk_assessment['findings'].append(
                    f"Credit limit exceeded: {utilization_percent:.1f}% utilization"
                )
                risk_assessment['recommendations'].append(
                    "Require immediate payment or management approval"
                )
            elif utilization_percent > 80:
                risk_assessment['risk_score'] = 50
                risk_assessment['findings'].append(
                    f"High credit utilization: {utilization_percent:.1f}%"
                )
                risk_assessment['recommendations'].append(
                    "Monitor payment closely and consider payment terms adjustment"
                )
        else:
            risk_assessment['risk_score'] = 30
            risk_assessment['findings'].append("No credit limit set for customer")
            risk_assessment['recommendations'].append("Establish formal credit limit")
        
        # Check payment history
        if outstanding_amount > 0:
            overdue_invoices = frappe.db.sql("""
                SELECT COUNT(*), MAX(DATEDIFF(NOW(), si.due_date))
                FROM `tabSales Invoice` si
                WHERE si.customer = %s
                AND si.docstatus = 1
                AND si.outstanding_amount > 0
                AND si.due_date < CURDATE()
            """, (doc.customer,))[0]
            
            if overdue_invoices[0] > 0:
                risk_assessment['risk_score'] += 25
                risk_assessment['findings'].append(
                    f"{overdue_invoices[0]} overdue invoices, max {overdue_invoices[1]} days"
                )
        
        return risk_assessment
    
    def check_pricing_strategy_alignment(self, doc):
        """Check if pricing aligns with company strategy"""
        
        risk_assessment = {
            'category': 'pricing_strategy',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        significant_discounts = []
        below_cost_items = []
        
        for item in doc.items:
            # Get item's last purchase rate
            last_purchase_rate = frappe.db.sql("""
                SELECT rate
                FROM `tabPurchase Invoice Item` pii
                JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
                WHERE pii.item_code = %s
                AND pi.docstatus = 1
                ORDER BY pi.posting_date DESC
                LIMIT 1
            """, (item.item_code,))
            
            if last_purchase_rate:
                cost_rate = last_purchase_rate[0][0]
                margin_percent = ((item.rate - cost_rate) / cost_rate) * 100
                
                if margin_percent < 10:  # Less than 10% margin
                    below_cost_items.append({
                        'item_code': item.item_code,
                        'selling_rate': item.rate,
                        'cost_rate': cost_rate,
                        'margin_percent': margin_percent
                    })
            
            # Check for significant discounts
            if hasattr(item, 'discount_percentage') and item.discount_percentage > 20:
                significant_discounts.append({
                    'item_code': item.item_code,
                    'discount_percent': item.discount_percentage,
                    'amount_impact': item.price_list_rate - item.rate
                })
        
        if below_cost_items:
            risk_assessment['risk_score'] = 60
            risk_assessment['findings'].append(
                f"{len(below_cost_items)} items selling below 10% margin"
            )
            risk_assessment['recommendations'].append(
                "Review pricing strategy for low-margin items"
            )
        
        if significant_discounts:
            risk_assessment['risk_score'] += 30
            risk_assessment['findings'].append(
                f"{len(significant_discounts)} items with >20% discount"
            )
            risk_assessment['recommendations'].append(
                "Verify discount approval and impact on profitability"
            )
        
        return risk_assessment
    
    def assess_revenue_recognition_compliance(self, doc):
        """Assess revenue recognition compliance"""
        
        risk_assessment = {
            'category': 'revenue_recognition',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        compliance_issues = []
        
        # Check if delivery is confirmed for goods
        goods_items = [item for item in doc.items if item.item_code and 
                      frappe.db.get_value('Item', item.item_code, 'is_stock_item')]
        
        if goods_items:
            # Check for delivery note
            delivery_confirmed = any(item.delivery_note for item in goods_items)
            
            if not delivery_confirmed:
                compliance_issues.append("Revenue recognized without delivery confirmation")
                risk_assessment['risk_score'] = 70
        
        # Check for service completion documentation
        service_items = [item for item in doc.items if item.item_code and 
                        not frappe.db.get_value('Item', item.item_code, 'is_stock_item')]
        
        # Since Sales Invoice doesn't have service_completion_certificate field,
        # check if service end dates are properly set for service items
        if service_items:
            items_without_service_dates = [item for item in service_items 
                                         if not item.get('service_end_date')]
            if items_without_service_dates:
                compliance_issues.append("Service revenue without service completion dates")
                risk_assessment['risk_score'] += 40
        
        # Check posting date vs delivery date
        if doc.get('delivery_date') and doc.posting_date < getdate(doc.delivery_date):
            compliance_issues.append("Revenue recognized before delivery date")
            risk_assessment['risk_score'] += 30
        
        if compliance_issues:
            risk_assessment['findings'] = compliance_issues
            risk_assessment['recommendations'].append(
                "Ensure revenue recognition follows accounting standards"
            )
        
        return risk_assessment
    
    def analyze_profit_margin_variance(self, doc):
        """Analyze profit margin variance against targets"""
        
        risk_assessment = {
            'category': 'profit_margin',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        # Calculate overall margin
        total_cost = 0
        total_revenue = doc.grand_total
        
        for item in doc.items:
            # Get standard cost or last purchase rate
            item_cost = frappe.db.get_value('Item', item.item_code, 'last_purchase_rate') or 0
            total_cost += item_cost * item.qty
        
        if total_cost > 0:
            margin_percent = ((total_revenue - total_cost) / total_revenue) * 100
            
            # Use a default target margin since Selling Settings doesn't have target_margin_percent
            target_margin = 25  # Default 25% margin target
            
            variance = margin_percent - target_margin
            
            if variance < -10:  # 10% below target
                risk_assessment['risk_score'] = 60
                risk_assessment['findings'].append(
                    f"Margin {margin_percent:.1f}% is {abs(variance):.1f}% below target"
                )
                risk_assessment['recommendations'].append(
                    "Review pricing strategy to improve profitability"
                )
            elif variance < -5:  # 5% below target
                risk_assessment['risk_score'] = 30
                risk_assessment['findings'].append(
                    f"Margin {margin_percent:.1f}% slightly below target"
                )
        
        return risk_assessment
    
    def validate_tax_calculations(self, doc):
        """Validate tax calculations and compliance"""
        
        risk_assessment = {
            'category': 'tax_validation',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        tax_issues = []
        
        # Check if tax template is applied
        if not doc.taxes_and_charges:
            tax_issues.append("No tax template applied")
            risk_assessment['risk_score'] = 40
        
        # Validate tax amounts
        if doc.taxes:
            for tax in doc.taxes:
                if not tax.account_head:
                    tax_issues.append(f"Missing account head for {tax.description}")
                    risk_assessment['risk_score'] += 20
                
                # Check tax rate reasonableness
                if tax.rate and (tax.rate < 0 or tax.rate > 50):
                    tax_issues.append(f"Unusual tax rate: {tax.rate}%")
                    risk_assessment['risk_score'] += 15
        
        # Check if customer has tax withholding category but still has taxes applied
        customer_doc = frappe.get_doc('Customer', doc.customer)
        if customer_doc.get('tax_withholding_category') and doc.total_taxes_and_charges > 0:
            # This might be normal, so lower the risk score
            tax_issues.append("Customer has tax withholding category - verify tax application")
            risk_assessment['risk_score'] += 20
        
        if tax_issues:
            risk_assessment['findings'] = tax_issues
            risk_assessment['recommendations'].append(
                "Verify tax calculations and customer tax status"
            )
        
        return risk_assessment
    
    def check_delivery_confirmation(self, doc):
        """Check delivery confirmation for goods"""
        
        risk_assessment = {
            'category': 'delivery_confirmation',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        # Check for stock items without delivery confirmation
        undelivered_items = []
        
        for item in doc.items:
            if item.item_code:
                is_stock_item = frappe.db.get_value('Item', item.item_code, 'is_stock_item')
                
                if is_stock_item and not item.delivery_note:
                    undelivered_items.append(item.item_code)
        
        if undelivered_items:
            risk_assessment['risk_score'] = 50
            risk_assessment['findings'].append(
                f"{len(undelivered_items)} stock items without delivery confirmation"
            )
            risk_assessment['recommendations'].append(
                "Confirm delivery before recognizing revenue"
            )
        
        return risk_assessment
    
    def analyze_customer_payment_behavior(self, doc):
        """Analyze customer payment behavior and predict payment date"""
        
        # Get customer payment history
        payment_history = frappe.db.sql("""
            SELECT 
                DATEDIFF(pe.posting_date, si.due_date) as days_to_pay,
                si.grand_total,
                si.due_date,
                pe.posting_date
            FROM `tabSales Invoice` si
            JOIN `tabPayment Entry Reference` per ON per.reference_name = si.name
            JOIN `tabPayment Entry` pe ON pe.name = per.parent
            WHERE si.customer = %s
            AND si.docstatus = 1
            AND pe.docstatus = 1
            ORDER BY si.posting_date DESC
            LIMIT 10
        """, (doc.customer,), as_dict=True)
        
        insights = {
            'avg_payment_days': 0,
            'payment_trend': 'on_time',
            'predicted_payment_date': doc.due_date,
            'confidence_level': 0.8
        }
        
        if payment_history:
            avg_days = sum(p['days_to_pay'] for p in payment_history) / len(payment_history)
            insights['avg_payment_days'] = round(avg_days, 1)
            
            if avg_days > 7:
                insights['payment_trend'] = 'late'
            elif avg_days < -2:
                insights['payment_trend'] = 'early'
            
            # Predict payment date
            predicted_date = add_days(doc.due_date, int(avg_days))
            insights['predicted_payment_date'] = predicted_date
        
        return insights
    
    def generate_sales_controller_response(self, doc, assessment, risk_factors):
        """Generate response as a diligent sales controller"""
        
        user_name = frappe.db.get_value('User', self.user, 'full_name') or 'there'
        
        response = f"💼 **Sales Controller Review for Invoice {doc.name or 'New'}**\n\n"
        response += f"Hello {user_name}, I've analyzed this {doc.grand_total:.2f} invoice for {doc.customer}.\n\n"
        
        # Risk level indicator
        if assessment['risk_score'] > 70:
            response += "🚨 **REVENUE RISK DETECTED** - Critical issues need resolution\n\n"
        elif assessment['risk_score'] > 40:
            response += "⚠️ **MODERATE RISK** - Review required before processing\n\n"
        else:
            response += "✅ **LOW RISK** - Revenue recognition approved\n\n"
        
        # Customer insights
        if assessment.get('revenue_insights'):
            insights = assessment['revenue_insights']
            response += f"**👤 Customer Payment Profile:**\n"
            response += f"• Average payment time: {insights['avg_payment_days']} days\n"
            response += f"• Payment trend: {insights['payment_trend']}\n"
            response += f"• Predicted payment: {insights['predicted_payment_date']}\n\n"
        
        # Detailed findings
        if risk_factors:
            response += "**📋 Revenue Integrity Findings:**\n"
            for factor in risk_factors:
                for finding in factor['findings']:
                    response += f"• {finding}\n"
            response += "\n"
        
        # Recommendations
        all_recommendations = []
        for factor in risk_factors:
            all_recommendations.extend(factor['recommendations'])
        
        if all_recommendations:
            response += "**💡 My Professional Recommendations:**\n"
            for rec in all_recommendations:
                response += f"• {rec}\n"
            response += "\n"
        
        # Approval decision
        if assessment['risk_score'] > 70:
            response += "**❌ HOLD FOR MANAGEMENT REVIEW** - Significant revenue risks identified."
        elif assessment['risk_score'] > 40:
            response += "**⚠️ PROCEED WITH CONDITIONS** - Address identified risks."
        else:
            response += "**✅ APPROVED FOR REVENUE RECOGNITION** - Compliance verified."
        
        return response


# Frappe whitelisted methods

@frappe.whitelist()
def assess_sales_invoice_risk(doc_name, trigger_point="on_save"):
    """API method for sales invoice risk assessment"""
    try:
        doc = frappe.get_doc('Sales Invoice', doc_name)
        assessor = SalesInvoiceIntelligence()
        return assessor.assess_sales_invoice(doc, trigger_point)
    except Exception as e:
        frappe.log_error(f"Sales Invoice Risk Assessment Error: {str(e)}", "Sales Intelligence")
        return {'error': str(e)}

@frappe.whitelist()
def get_customer_payment_prediction(customer):
    """API method for customer payment behavior prediction"""
    try:
        assessor = SalesInvoiceIntelligence()
        mock_doc = frappe._dict({'customer': customer, 'due_date': add_days(nowdate(), 30)})
        return assessor.analyze_customer_payment_behavior(mock_doc)
    except Exception as e:
        frappe.log_error(f"Customer Payment Prediction Error: {str(e)}", "Sales Intelligence")
        return {'error': str(e)} 