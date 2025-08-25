# Quotation Intelligence for Advanced AI Risk Assessment
# Copyright (c) 2025, Vacker and contributors

import frappe
import json
import re
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, add_days, nowdate, cstr, fmt_money
from .document_risk_assessment import DocumentRiskAssessmentEngine


class QuotationIntelligence(DocumentRiskAssessmentEngine):
    """
    Act as experienced sales manager ensuring competitive pricing and risk mitigation
    Comprehensive risk assessment for quotations
    """
    
    def assess_quotation(self, doc, trigger_point):
        """Comprehensive Quotation Risk Assessment"""
        
        assessment = {
            'risk_level': 'low',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'warnings': [],
            'compliance_status': 'compliant',
            'personality_response': '',
            'pricing_insights': [],
            'competitive_analysis': {}
        }
        
        risk_factors = []
        
        # 1. Pricing Strategy Analysis
        pricing_risk = self.analyze_pricing_strategy(doc)
        if pricing_risk['risk_score'] > 0:
            risk_factors.append(pricing_risk)
        
        # 2. Profit Margin Validation
        margin_risk = self.validate_profit_margins(doc)
        if margin_risk['risk_score'] > 0:
            risk_factors.append(margin_risk)
        
        # 3. Customer Credit Assessment
        customer_risk = self.assess_customer_creditworthiness(doc)
        if customer_risk['risk_score'] > 0:
            risk_factors.append(customer_risk)
        
        # 4. Competitive Pricing Analysis
        competitive_risk = self.analyze_competitive_pricing(doc)
        assessment['competitive_analysis'] = competitive_risk
        if competitive_risk['risk_score'] > 0:
            risk_factors.append(competitive_risk)
        
        # 5. Validity Period Assessment
        validity_risk = self.assess_validity_period(doc)
        if validity_risk['risk_score'] > 0:
            risk_factors.append(validity_risk)
        
        # 6. Terms and Conditions Review
        terms_risk = self.review_terms_conditions(doc)
        if terms_risk['risk_score'] > 0:
            risk_factors.append(terms_risk)
        
        # 7. Market Intelligence Integration
        market_analysis = self.integrate_market_intelligence(doc)
        assessment['pricing_insights'] = market_analysis
        
        # 8. Capacity and Delivery Assessment
        capacity_risk = self.assess_delivery_capacity(doc)
        if capacity_risk['risk_score'] > 0:
            risk_factors.append(capacity_risk)
        
        # Calculate overall risk
        assessment = self.calculate_overall_risk(assessment, risk_factors)
        
        # Generate personality response
        assessment['personality_response'] = self.generate_sales_manager_response(
            doc, assessment, risk_factors
        )
        
        return assessment
    
    def analyze_pricing_strategy(self, doc):
        """Analyze pricing strategy and identify risks"""
        
        risk_assessment = {
            'category': 'pricing_strategy',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        total_margin = 0
        low_margin_items = []
        high_discount_items = []
        
        for item in doc.items:
            # Get item cost
            item_cost = frappe.db.get_value('Item', item.item_code, 'last_purchase_rate') or 0
            
            if item_cost > 0:
                # Calculate margin
                margin_percent = ((item.rate - item_cost) / item.rate) * 100
                total_margin += margin_percent
                
                # Check for low margins
                if margin_percent < 15:  # Less than 15% margin
                    low_margin_items.append({
                        'item_code': item.item_code,
                        'margin_percent': margin_percent,
                        'selling_rate': item.rate,
                        'cost_rate': item_cost
                    })
            
            # Check for high discounts
            if hasattr(item, 'discount_percentage') and item.discount_percentage > 25:
                high_discount_items.append({
                    'item_code': item.item_code,
                    'discount_percent': item.discount_percentage,
                    'original_rate': item.price_list_rate,
                    'discounted_rate': item.rate
                })
        
        # Assess risks
        if low_margin_items:
            risk_assessment['risk_score'] = len(low_margin_items) * 20
            risk_assessment['findings'].append(
                f"{len(low_margin_items)} items with margins below 15%"
            )
            risk_assessment['recommendations'].append(
                "Review pricing for low-margin items to ensure profitability"
            )
        
        if high_discount_items:
            risk_assessment['risk_score'] += len(high_discount_items) * 15
            risk_assessment['findings'].append(
                f"{len(high_discount_items)} items with discounts above 25%"
            )
            risk_assessment['recommendations'].append(
                "Verify authorization for high discount percentages"
            )
        
        return risk_assessment
    
    def validate_profit_margins(self, doc):
        """Validate overall profit margins"""
        
        risk_assessment = {
            'category': 'profit_margin_validation',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        total_cost = 0
        total_revenue = doc.grand_total
        
        for item in doc.items:
            item_cost = frappe.db.get_value('Item', item.item_code, 'last_purchase_rate') or 0
            total_cost += item_cost * item.qty
        
        if total_cost > 0 and total_revenue > 0:
            overall_margin = ((total_revenue - total_cost) / total_revenue) * 100
            
            # Use a default target margin since Selling Settings doesn't have target_margin_percent
            target_margin = 25  # Default 25% margin target
            
            if overall_margin < target_margin - 10:  # 10% below target
                risk_assessment['risk_score'] = 70
                risk_assessment['findings'].append(
                    f"Overall margin {overall_margin:.1f}% significantly below target {target_margin}%"
                )
                risk_assessment['recommendations'].append(
                    "Revise pricing to meet company margin targets"
                )
            elif overall_margin < target_margin:
                risk_assessment['risk_score'] = 30
                risk_assessment['findings'].append(
                    f"Overall margin {overall_margin:.1f}% below target {target_margin}%"
                )
                risk_assessment['recommendations'].append(
                    "Consider minor pricing adjustments to improve margins"
                )
        
        return risk_assessment
    
    def assess_customer_creditworthiness(self, doc):
        """Assess customer credit risk"""
        
        risk_assessment = {
            'category': 'customer_credit_risk',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        if not doc.quotation_to or doc.quotation_to != 'Customer':
            return risk_assessment
        
        customer = doc.party_name
        
        # Get customer payment history
        payment_history = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_invoices,
                SUM(si.outstanding_amount) as total_outstanding,
                AVG(DATEDIFF(pe.posting_date, si.due_date)) as avg_payment_delay
            FROM `tabSales Invoice` si
            LEFT JOIN `tabPayment Entry Reference` per ON per.reference_name = si.name
            LEFT JOIN `tabPayment Entry` pe ON pe.name = per.parent
            WHERE si.customer = %s
            AND si.docstatus = 1
        """, (customer,), as_dict=True)
        
        if payment_history and payment_history[0]:
            history = payment_history[0]
            
            # Check outstanding amounts
            if history.total_outstanding and history.total_outstanding > doc.grand_total * 2:
                risk_assessment['risk_score'] = 60
                risk_assessment['findings'].append(
                    f"High outstanding amount: {fmt_money(history.total_outstanding)}"
                )
                risk_assessment['recommendations'].append(
                    "Consider requiring advance payment or bank guarantee"
                )
            
            # Check payment delays
            if history.avg_payment_delay and history.avg_payment_delay > 15:
                risk_assessment['risk_score'] += 30
                risk_assessment['findings'].append(
                    f"Customer averages {history.avg_payment_delay:.0f} days payment delay"
                )
                risk_assessment['recommendations'].append(
                    "Consider stricter payment terms or credit insurance"
                )
        
        # Check customer credit limit using proper ERPNext function
        from erpnext.selling.doctype.customer.customer import get_credit_limit
        
        # Get company from quotation doc (assuming it's available in context)
        company = getattr(doc, 'company', frappe.defaults.get_user_default('Company'))
        credit_limit = get_credit_limit(customer, company)
        
        if credit_limit and credit_limit > 0:
            credit_utilization = (history.total_outstanding or 0) / credit_limit
            if credit_utilization > 0.8:  # 80% utilization
                risk_assessment['risk_score'] += 40
                risk_assessment['findings'].append(
                    f"Customer credit utilization at {credit_utilization*100:.1f}%"
                )
        
        return risk_assessment
    
    def analyze_competitive_pricing(self, doc):
        """Analyze competitive pricing and market position"""
        
        competitive_analysis = {
            'category': 'competitive_analysis',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'market_position': 'unknown',
            'price_competitiveness': 'average'
        }
        
        # Get recent quotations for similar items
        similar_quotations = []
        
        for item in doc.items:
            recent_quotes = frappe.db.sql("""
                SELECT 
                    qi.rate,
                    q.transaction_date,
                    q.party_name as customer
                FROM `tabQuotation Item` qi
                JOIN `tabQuotation` q ON qi.parent = q.name
                WHERE qi.item_code = %s
                AND q.docstatus = 1
                AND q.transaction_date >= %s
                AND q.name != %s
                ORDER BY q.transaction_date DESC
                LIMIT 10
            """, (item.item_code, add_days(nowdate(), -90), doc.name or ''), as_dict=True)
            
            if recent_quotes:
                avg_market_rate = sum(q.rate for q in recent_quotes) / len(recent_quotes)
                price_variance = ((item.rate - avg_market_rate) / avg_market_rate) * 100
                
                if price_variance > 20:  # 20% above market
                    competitive_analysis['risk_score'] += 25
                    competitive_analysis['findings'].append(
                        f"{item.item_code}: {price_variance:.1f}% above market average"
                    )
                    competitive_analysis['recommendations'].append(
                        f"Consider competitive pricing for {item.item_code}"
                    )
                    competitive_analysis['price_competitiveness'] = 'high_risk'
                
                elif price_variance < -15:  # 15% below market
                    competitive_analysis['findings'].append(
                        f"{item.item_code}: {abs(price_variance):.1f}% below market (competitive advantage)"
                    )
                    competitive_analysis['price_competitiveness'] = 'competitive'
        
        return competitive_analysis
    
    def assess_validity_period(self, doc):
        """Assess quotation validity period risks"""
        
        risk_assessment = {
            'category': 'validity_period',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        if doc.valid_till:
            validity_days = (getdate(doc.valid_till) - getdate(nowdate())).days
            
            if validity_days > 90:  # More than 3 months
                risk_assessment['risk_score'] = 40
                risk_assessment['findings'].append(
                    f"Long validity period: {validity_days} days"
                )
                risk_assessment['recommendations'].append(
                    "Consider shorter validity period due to market volatility"
                )
            elif validity_days < 7:  # Less than a week
                risk_assessment['risk_score'] = 20
                risk_assessment['findings'].append(
                    f"Very short validity period: {validity_days} days"
                )
                risk_assessment['recommendations'].append(
                    "Ensure customer has adequate time for decision making"
                )
        else:
            risk_assessment['risk_score'] = 30
            risk_assessment['findings'].append("No validity period specified")
            risk_assessment['recommendations'].append("Set appropriate validity period for quotation")
        
        return risk_assessment
    
    def review_terms_conditions(self, doc):
        """Review terms and conditions for risks"""
        
        risk_assessment = {
            'category': 'terms_conditions',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        # Check payment terms
        if not doc.payment_terms_template:
            risk_assessment['risk_score'] = 25
            risk_assessment['findings'].append("No payment terms template specified")
            risk_assessment['recommendations'].append("Add standard payment terms to protect cash flow")
        
        # Check delivery terms
        if hasattr(doc, 'delivery_date') and doc.delivery_date:
            delivery_days = (getdate(doc.delivery_date) - getdate(nowdate())).days
            
            if delivery_days > 180:  # More than 6 months
                risk_assessment['risk_score'] += 20
                risk_assessment['findings'].append(
                    f"Long delivery period: {delivery_days} days"
                )
                risk_assessment['recommendations'].append(
                    "Verify capacity for extended delivery timeline"
                )
        
        return risk_assessment
    
    def integrate_market_intelligence(self, doc):
        """Integrate market intelligence for pricing insights"""
        
        pricing_insights = []
        
        for item in doc.items:
            # Get market intelligence if available
            try:
                from .material_request_intelligence import MaterialRequestIntelligence
                market_intelligence = MaterialRequestIntelligence()
                market_data = market_intelligence.get_uganda_market_data(item.item_code)
                
                if market_data and market_data.get('average_market_price'):
                    market_price = market_data['average_market_price']
                    price_difference = ((item.rate - market_price) / market_price) * 100
                    
                    pricing_insights.append({
                        'item_code': item.item_code,
                        'quoted_price': item.rate,
                        'market_price': market_price,
                        'price_difference_percent': price_difference,
                        'market_trend': market_data.get('seasonal_trend', 'stable')
                    })
            except:
                pass  # Market intelligence not available
        
        return pricing_insights
    
    def assess_delivery_capacity(self, doc):
        """Assess company's capacity to deliver on quotation"""
        
        risk_assessment = {
            'category': 'delivery_capacity',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        # Check inventory availability for stock items
        unavailable_items = []
        
        for item in doc.items:
            if frappe.db.get_value('Item', item.item_code, 'is_stock_item'):
                available_qty = frappe.db.sql("""
                    SELECT SUM(actual_qty)
                    FROM `tabBin`
                    WHERE item_code = %s
                    AND actual_qty > 0
                """, (item.item_code,))[0][0] or 0
                
                if available_qty < item.qty:
                    unavailable_items.append({
                        'item_code': item.item_code,
                        'required_qty': item.qty,
                        'available_qty': available_qty,
                        'shortage': item.qty - available_qty
                    })
        
        if unavailable_items:
            risk_assessment['risk_score'] = len(unavailable_items) * 15
            risk_assessment['findings'].append(
                f"{len(unavailable_items)} items have insufficient stock"
            )
            risk_assessment['recommendations'].append(
                "Verify procurement timeline for stock items or adjust delivery dates"
            )
        
        return risk_assessment
    
    def generate_sales_manager_response(self, doc, assessment, risk_factors):
        """Generate response as experienced sales manager"""
        
        user_name = frappe.db.get_value('User', self.user, 'full_name') or 'there'
        customer_name = doc.party_name or 'prospect'
        
        response = f"🎯 **Sales Manager Review - Quotation {doc.name or 'New'}**\n\n"
        response += f"Hello {user_name}, I've analyzed this {fmt_money(doc.grand_total)} quotation for {customer_name}.\n\n"
        
        # Risk level indicator
        if assessment['risk_score'] > 70:
            response += "🚨 **HIGH RISK QUOTATION** - Critical issues require resolution\n\n"
        elif assessment['risk_score'] > 40:
            response += "⚠️ **MEDIUM RISK** - Review and adjust before sending\n\n"
        else:
            response += "✅ **LOW RISK** - Quotation approved for customer presentation\n\n"
        
        # Competitive analysis
        if assessment.get('competitive_analysis', {}).get('price_competitiveness'):
            competitiveness = assessment['competitive_analysis']['price_competitiveness']
            if competitiveness == 'high_risk':
                response += "💰 **PRICING ALERT**: Above market rates - risk of losing to competitors\n\n"
            elif competitiveness == 'competitive':
                response += "💰 **COMPETITIVE PRICING**: Well positioned against market rates\n\n"
        
        # Market insights
        if assessment.get('pricing_insights'):
            response += "📊 **Market Intelligence Insights:**\n"
            for insight in assessment['pricing_insights'][:3]:  # Show top 3
                response += f"• {insight['item_code']}: {insight['price_difference_percent']:+.1f}% vs market\n"
            response += "\n"
        
        # Detailed findings
        if risk_factors:
            response += "**📋 Sales Risk Analysis:**\n"
            for factor in risk_factors:
                for finding in factor['findings']:
                    response += f"• {finding}\n"
            response += "\n"
        
        # Recommendations
        all_recommendations = []
        for factor in risk_factors:
            all_recommendations.extend(factor['recommendations'])
        
        if all_recommendations:
            response += "**💡 Strategic Recommendations:**\n"
            for rec in all_recommendations:
                response += f"• {rec}\n"
            response += "\n"
        
        # Final decision
        if assessment['risk_score'] > 70:
            response += "**❌ HOLD QUOTATION** - Address critical risks before customer presentation."
        elif assessment['risk_score'] > 40:
            response += "**⚠️ PROCEED WITH CAUTION** - Implement recommendations to strengthen position."
        else:
            response += "**✅ APPROVED FOR CUSTOMER PRESENTATION** - Competitive and profitable quotation."
        
        return response


# Frappe whitelisted methods

@frappe.whitelist()
def assess_quotation_risk(doc_name, trigger_point="on_save"):
    """API method for quotation risk assessment"""
    try:
        doc = frappe.get_doc('Quotation', doc_name)
        assessor = QuotationIntelligence()
        return assessor.assess_quotation(doc, trigger_point)
    except Exception as e:
        frappe.log_error(f"Quotation Risk Assessment Error: {str(e)}", "Quotation Intelligence")
        return {'error': str(e)}

@frappe.whitelist()
def get_competitive_analysis(customer, items_json):
    """API method for competitive pricing analysis"""
    try:
        assessor = QuotationIntelligence()
        items = frappe.parse_json(items_json)
        mock_doc = frappe._dict({
            'party_name': customer,
            'items': items,
            'grand_total': sum(item.get('amount', 0) for item in items)
        })
        return assessor.analyze_competitive_pricing(mock_doc)
    except Exception as e:
        frappe.log_error(f"Competitive Analysis Error: {str(e)}", "Quotation Intelligence")
        return {'error': str(e)} 