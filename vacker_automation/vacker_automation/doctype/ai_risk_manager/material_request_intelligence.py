# Material Request Intelligence with Market Integration
# Copyright (c) 2025, Vacker and contributors

import frappe
import json
import re
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, add_days, nowdate, cstr, fmt_money
from .document_risk_assessment import DocumentRiskAssessmentEngine
import requests


class MaterialRequestIntelligence(DocumentRiskAssessmentEngine):
    """
    Act as experienced procurement manager with Uganda market intelligence
    Provides intelligent supplier recommendations and material usage accountability
    """
    
    def assess_material_request(self, doc, trigger_point):
        """Comprehensive Material Request Risk Assessment with Market Intelligence"""
        
        assessment = {
            'risk_level': 'low',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'warnings': [],
            'compliance_status': 'compliant',
            'personality_response': '',
            'market_intelligence': {},
            'supplier_recommendations': [],
            'accountability_status': {},
            'procurement_insights': {}
        }
        
        risk_factors = []
        
        # 1. MANDATORY: Previous Material Request Follow-up
        accountability_check = self.check_material_accountability(doc)
        assessment['accountability_status'] = accountability_check
        if accountability_check['requires_followup']:
            risk_factors.append(accountability_check)
        
        # 2. Market Intelligence Analysis
        market_analysis = self.analyze_market_intelligence(doc)
        assessment['market_intelligence'] = market_analysis
        if market_analysis['risk_score'] > 0:
            risk_factors.append(market_analysis)
        
        # 3. Supplier Performance Analysis
        supplier_analysis = self.analyze_supplier_performance(doc)
        assessment['supplier_recommendations'] = supplier_analysis
        if supplier_analysis['risk_score'] > 0:
            risk_factors.append(supplier_analysis)
        
        # 4. Budget Impact Assessment
        budget_impact = self.assess_budget_impact(doc)
        if budget_impact['risk_score'] > 0:
            risk_factors.append(budget_impact)
        
        # 5. Inventory Optimization Analysis
        inventory_analysis = self.analyze_inventory_optimization(doc)
        if inventory_analysis['risk_score'] > 0:
            risk_factors.append(inventory_analysis)
        
        # 6. Procurement Efficiency Analysis
        efficiency_analysis = self.analyze_procurement_efficiency(doc)
        assessment['procurement_insights'] = efficiency_analysis
        if efficiency_analysis['risk_score'] > 0:
            risk_factors.append(efficiency_analysis)
        
        # 7. Alternative Item Suggestions
        alternative_analysis = self.suggest_alternative_items(doc)
        if alternative_analysis['suggestions']:
            assessment['alternative_suggestions'] = alternative_analysis['suggestions']
        
        # 8. Seasonal/Market Timing Analysis
        timing_analysis = self.analyze_procurement_timing(doc)
        if timing_analysis['risk_score'] > 0:
            risk_factors.append(timing_analysis)
        
        # Calculate overall risk
        assessment = self.calculate_overall_risk(assessment, risk_factors)
        
        # Generate personality response
        assessment['personality_response'] = self.generate_procurement_manager_response(
            doc, assessment, risk_factors
        )
        
        return assessment
    
    def check_material_accountability(self, doc):
        """MANDATORY: Check accountability for previous material requests"""
        
        accountability_check = {
            'category': 'material_accountability',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'requires_followup': False,
            'pending_followups': [],
            'usage_efficiency': 0
        }
        
        if not doc.requested_by:
            return accountability_check
        
        # Get previous material requests from last 6 months
        previous_requests = frappe.db.sql("""
            SELECT 
                mr.name,
                mr.transaction_date,
                mr.total_estimated_cost,
                mr.project,
                mr.purpose,
                COALESCE(mf.followup_status, 'pending') as followup_status,
                mf.usage_report,
                mf.efficiency_rating,
                mf.wastage_report
            FROM `tabMaterial Request` mr
            LEFT JOIN `tabMaterial Followup` mf ON mf.material_request = mr.name
            WHERE mr.requested_by = %s
            AND mr.docstatus = 1
            AND mr.transaction_date >= %s
            AND mr.name != %s
            ORDER BY mr.transaction_date DESC
        """, (
            doc.requested_by, 
            add_days(nowdate(), -180), 
            doc.name or ''
        ), as_dict=True)
        
        pending_followups = []
        total_pending_value = 0
        
        for request in previous_requests:
            if request.followup_status == 'pending':
                # Check if request requires follow-up based on value and type
                if self.requires_material_followup(request):
                    pending_followups.append({
                        'request_name': request.name,
                        'value': request.total_estimated_cost,
                        'date': request.transaction_date,
                        'project': request.project,
                        'purpose': request.purpose,
                        'days_pending': (getdate(nowdate()) - getdate(request.transaction_date)).days
                    })
                    total_pending_value += request.total_estimated_cost or 0
        
        if pending_followups:
            accountability_check['requires_followup'] = True
            accountability_check['pending_followups'] = pending_followups
            
            # Block if there are high-value pending follow-ups
            if total_pending_value > 2000000:  # 2M UGX
                accountability_check['risk_score'] = 95
                accountability_check['findings'].append(
                    f"BLOCKED: {len(pending_followups)} pending material follow-ups totaling {total_pending_value:,.0f} UGX"
                )
                accountability_check['recommendations'].append(
                    "Complete usage reports for previous material requests before submitting new requests"
                )
            else:
                accountability_check['risk_score'] = 60
                accountability_check['findings'].append(
                    f"{len(pending_followups)} material requests require usage documentation"
                )
                accountability_check['recommendations'].append(
                    "Submit usage reports for pending material follow-ups"
                )
        
        # Calculate usage efficiency from completed follow-ups
        completed_followups = [r for r in previous_requests if r.followup_status == 'completed']
        if completed_followups:
            avg_efficiency = sum(r.efficiency_rating or 0 for r in completed_followups) / len(completed_followups)
            accountability_check['usage_efficiency'] = avg_efficiency
            
            if avg_efficiency < 60:  # Below 60% efficiency
                accountability_check['risk_score'] += 30
                accountability_check['findings'].append(
                    f"Historical material usage efficiency: {avg_efficiency:.1f}% (below standards)"
                )
                accountability_check['recommendations'].append(
                    "Improve material usage efficiency through better planning"
                )
        
        return accountability_check
    
    def analyze_market_intelligence(self, doc):
        """Analyze Uganda market intelligence for requested items"""
        
        market_analysis = {
            'category': 'market_intelligence',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'price_insights': [],
            'availability_insights': [],
            'market_trends': []
        }
        
        total_savings_potential = 0
        high_risk_items = []
        
        for item in doc.items:
            # Get market intelligence for each item
            item_market_data = self.get_uganda_market_data(item.item_code)
            
            if item_market_data:
                # Price variance analysis
                if item.rate and item_market_data.get('average_market_price'):
                    market_price = item_market_data['average_market_price']
                    variance_percent = ((item.rate - market_price) / market_price) * 100
                    
                    if variance_percent > 20:  # 20% above market
                        market_analysis['risk_score'] += 30
                        market_analysis['findings'].append(
                            f"{item.item_code}: {variance_percent:.1f}% above market price"
                        )
                        market_analysis['recommendations'].append(
                            f"Negotiate better price for {item.item_code} - potential savings: {(item.rate - market_price) * item.qty:,.0f} UGX"
                        )
                        total_savings_potential += (item.rate - market_price) * item.qty
                    elif variance_percent < -10:  # 10% below market (suspicious)
                        market_analysis['findings'].append(
                            f"{item.item_code}: Price {abs(variance_percent):.1f}% below market - verify quality"
                        )
                
                # Availability analysis
                if item_market_data.get('availability_status') == 'scarce':
                    high_risk_items.append(item.item_code)
                    market_analysis['findings'].append(
                        f"{item.item_code}: Limited market availability - consider alternatives"
                    )
                
                # Seasonal trends
                if item_market_data.get('seasonal_trend'):
                    trend = item_market_data['seasonal_trend']
                    if trend == 'peak_season':
                        market_analysis['findings'].append(
                            f"{item.item_code}: Peak season pricing - consider timing adjustment"
                        )
                    elif trend == 'off_season':
                        market_analysis['recommendations'].append(
                            f"{item.item_code}: Off-season opportunity - good procurement timing"
                        )
                
                market_analysis['price_insights'].append({
                    'item_code': item.item_code,
                    'current_rate': item.rate,
                    'market_price': item_market_data.get('average_market_price'),
                    'variance_percent': variance_percent if item.rate and item_market_data.get('average_market_price') else 0,
                    'savings_potential': (item.rate - item_market_data.get('average_market_price', 0)) * item.qty if item.rate else 0
                })
        
        if total_savings_potential > 500000:  # 500k UGX potential savings
            market_analysis['risk_score'] += 20
            market_analysis['findings'].append(
                f"Total potential savings: {total_savings_potential:,.0f} UGX through better negotiations"
            )
        
        if high_risk_items:
            market_analysis['risk_score'] += len(high_risk_items) * 15
            market_analysis['recommendations'].append(
                f"Source alternatives for {len(high_risk_items)} scarce items"
            )
        
        return market_analysis
    
    def analyze_supplier_performance(self, doc):
        """Analyze supplier performance and provide recommendations"""
        
        supplier_analysis = {
            'category': 'supplier_performance',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'suggested_suppliers': []
        }
        
        for item in doc.items:
            # Get supplier performance data for this item
            supplier_performance = self.get_item_supplier_performance(item.item_code)
            
            if supplier_performance:
                # Rank suppliers by performance
                ranked_suppliers = sorted(
                    supplier_performance, 
                    key=lambda x: (x['performance_score'], -x['average_price']), 
                    reverse=True
                )
                
                top_suppliers = ranked_suppliers[:3]  # Top 3 suppliers
                
                supplier_analysis['suggested_suppliers'].append({
                    'item_code': item.item_code,
                    'suppliers': top_suppliers,
                    'current_supplier': doc.supplier if hasattr(doc, 'supplier') else None
                })
                
                # Check if current supplier is not optimal
                if hasattr(doc, 'supplier') and doc.supplier:
                    current_supplier_performance = next(
                        (s for s in supplier_performance if s['supplier'] == doc.supplier), 
                        None
                    )
                    
                    if current_supplier_performance:
                        best_supplier = ranked_suppliers[0]
                        
                        if current_supplier_performance['performance_score'] < best_supplier['performance_score'] - 10:
                            supplier_analysis['risk_score'] += 25
                            supplier_analysis['findings'].append(
                                f"{item.item_code}: Current supplier performance below optimal"
                            )
                            supplier_analysis['recommendations'].append(
                                f"Consider {best_supplier['supplier']} for {item.item_code} (Performance: {best_supplier['performance_score']:.1f}%)"
                            )
        
        return supplier_analysis
    
    def assess_budget_impact(self, doc):
        """Assess impact on project/department budgets"""
        
        budget_assessment = {
            'category': 'budget_impact',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        total_estimated_cost = doc.total_estimated_cost or 0
        
        # Project budget analysis
        if doc.project:
            project_budget_analysis = self.analyze_project_budget_impact(doc.project, total_estimated_cost)
            
            if project_budget_analysis['budget_utilization'] > 80:
                budget_assessment['risk_score'] = 70
                budget_assessment['findings'].append(
                    f"Project budget utilization: {project_budget_analysis['budget_utilization']:.1f}%"
                )
                budget_assessment['recommendations'].append(
                    "Review project budget allocation - approaching limits"
                )
            elif project_budget_analysis['budget_utilization'] > 60:
                budget_assessment['risk_score'] = 30
                budget_assessment['findings'].append(
                    f"Project budget utilization: {project_budget_analysis['budget_utilization']:.1f}%"
                )
                budget_assessment['recommendations'].append(
                    "Monitor project expenses closely"
                )
        
        # Cost center budget analysis
        if doc.cost_center:
            cc_budget_analysis = self.analyze_cost_center_budget(doc.cost_center, total_estimated_cost)
            
            if cc_budget_analysis['budget_utilization'] > 85:
                budget_assessment['risk_score'] += 60
                budget_assessment['findings'].append(
                    f"Cost center budget utilization: {cc_budget_analysis['budget_utilization']:.1f}%"
                )
                budget_assessment['recommendations'].append(
                    "Cost center approaching budget limits"
                )
        
        return budget_assessment
    
    def analyze_inventory_optimization(self, doc):
        """Analyze inventory optimization opportunities"""
        
        inventory_analysis = {
            'category': 'inventory_optimization',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        for item in doc.items:
            # Get current stock levels
            current_stock = self.get_current_stock_levels(item.item_code)
            
            # Get usage patterns
            usage_pattern = self.get_item_usage_pattern(item.item_code)
            
            # Check for overstocking
            if current_stock['total_stock'] > 0:
                months_of_stock = current_stock['total_stock'] / (usage_pattern['monthly_avg_usage'] or 1)
                
                if months_of_stock > 6:  # More than 6 months stock
                    inventory_analysis['risk_score'] += 20
                    inventory_analysis['findings'].append(
                        f"{item.item_code}: {months_of_stock:.1f} months stock available"
                    )
                    inventory_analysis['recommendations'].append(
                        f"Defer procurement of {item.item_code} - sufficient stock available"
                    )
                elif months_of_stock > 3:  # More than 3 months stock
                    inventory_analysis['findings'].append(
                        f"{item.item_code}: {months_of_stock:.1f} months stock - monitor usage"
                    )
            
            # Check for slow-moving items
            if usage_pattern['velocity_category'] == 'slow':
                inventory_analysis['risk_score'] += 15
                inventory_analysis['findings'].append(
                    f"{item.item_code}: Slow-moving item - verify necessity"
                )
                inventory_analysis['recommendations'].append(
                    f"Review necessity of {item.item_code} - slow usage pattern"
                )
            
            # Economic Order Quantity analysis
            eoq_analysis = self.calculate_eoq(item.item_code, item.qty)
            if eoq_analysis['variance_percent'] > 30:
                inventory_analysis['findings'].append(
                    f"{item.item_code}: Quantity {eoq_analysis['variance_percent']:.1f}% from optimal EOQ"
                )
                inventory_analysis['recommendations'].append(
                    f"Consider EOQ of {eoq_analysis['eoq']:.0f} units for {item.item_code}"
                )
        
        return inventory_analysis
    
    def analyze_procurement_efficiency(self, doc):
        """Analyze procurement process efficiency"""
        
        efficiency_analysis = {
            'category': 'procurement_efficiency',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'consolidation_opportunities': [],
            'timing_optimization': []
        }
        
        # Check for consolidation opportunities
        consolidation_opportunities = self.identify_consolidation_opportunities(doc)
        if consolidation_opportunities:
            efficiency_analysis['consolidation_opportunities'] = consolidation_opportunities
            efficiency_analysis['findings'].append(
                f"Found {len(consolidation_opportunities)} consolidation opportunities"
            )
            efficiency_analysis['recommendations'].append(
                "Consider consolidating similar items for better pricing"
            )
        
        # Check for frequent small orders
        recent_requests = self.get_recent_material_requests(doc.requested_by, 30)
        if len(recent_requests) >= 5:  # 5+ requests in 30 days
            avg_value = sum(r.get('total_estimated_cost', 0) for r in recent_requests) / len(recent_requests)
            
            if avg_value < 200000:  # Average below 200k UGX
                efficiency_analysis['risk_score'] = 40
                efficiency_analysis['findings'].append(
                    f"{len(recent_requests)} small requests in 30 days (avg: {avg_value:,.0f} UGX)"
                )
                efficiency_analysis['recommendations'].append(
                    "Consider batch ordering to improve procurement efficiency"
                )
        
        # Timing optimization
        timing_suggestions = self.analyze_optimal_procurement_timing(doc)
        if timing_suggestions:
            efficiency_analysis['timing_optimization'] = timing_suggestions
            
        return efficiency_analysis
    
    def suggest_alternative_items(self, doc):
        """Suggest alternative items based on functionality and cost"""
        
        alternative_analysis = {
            'suggestions': [],
            'potential_savings': 0
        }
        
        for item in doc.items:
            alternatives = self.find_alternative_items(item.item_code)
            
            if alternatives:
                cost_effective_alternatives = [
                    alt for alt in alternatives 
                    if alt['cost_difference'] < 0  # Lower cost
                ]
                
                if cost_effective_alternatives:
                    best_alternative = min(cost_effective_alternatives, key=lambda x: x['total_cost'])
                    
                    alternative_analysis['suggestions'].append({
                        'original_item': item.item_code,
                        'alternative_item': best_alternative['item_code'],
                        'cost_savings': abs(best_alternative['cost_difference']) * item.qty,
                        'functionality_match': best_alternative['functionality_match'],
                        'quality_rating': best_alternative['quality_rating']
                    })
                    
                    alternative_analysis['potential_savings'] += abs(best_alternative['cost_difference']) * item.qty
        
        return alternative_analysis
    
    def analyze_procurement_timing(self, doc):
        """Analyze procurement timing for market optimization"""
        
        timing_analysis = {
            'category': 'procurement_timing',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        current_date = getdate(doc.transaction_date)
        
        for item in doc.items:
            # Check seasonal price patterns
            seasonal_data = self.get_seasonal_price_data(item.item_code)
            
            if seasonal_data:
                current_season_factor = seasonal_data.get('current_factor', 1.0)
                optimal_season_factor = seasonal_data.get('optimal_factor', 1.0)
                
                if current_season_factor > optimal_season_factor * 1.15:  # 15% above optimal
                    timing_analysis['risk_score'] += 25
                    timing_analysis['findings'].append(
                        f"{item.item_code}: Purchasing in high-price season ({current_season_factor:.1f}x factor)"
                    )
                    timing_analysis['recommendations'].append(
                        f"Consider delaying {item.item_code} purchase until {seasonal_data.get('optimal_month', 'optimal season')}"
                    )
        
        # Check for end-of-month/quarter purchasing (potential budget clearing)
        if current_date.day >= 25 or (current_date.month in [3, 6, 9, 12] and current_date.day >= 20):
            timing_analysis['findings'].append(
                "End-of-period procurement - verify necessity vs budget clearing"
            )
        
        return timing_analysis
    
    def generate_procurement_manager_response(self, doc, assessment, risk_factors):
        """Generate response as experienced procurement manager"""
        
        user_name = frappe.db.get_value('User', self.user, 'full_name') or 'there'
        requester_name = frappe.db.get_value('User', doc.requested_by, 'full_name') or doc.requested_by
        
        response = f"🛒 **Procurement Manager Review - Material Request Analysis**\n\n"
        response += f"Hello {user_name}, I'm reviewing {requester_name}'s material request for {doc.total_estimated_cost:,.0f} UGX.\n\n"
        
        # Accountability status
        if assessment.get('accountability_status', {}).get('requires_followup'):
            pending = assessment['accountability_status']['pending_followups']
            response += f"🚫 **ACCOUNTABILITY CHECKPOINT**\n"
            response += f"Found {len(pending)} pending material follow-ups requiring completion:\n"
            for p in pending[:3]:  # Show first 3
                response += f"• {p['request_name']}: {p['value']:,.0f} UGX from {p['date']} ({p['days_pending']} days ago)\n"
            response += "\n**Required Documentation:**\n"
            response += "📋 Material usage report with efficiency metrics\n"
            response += "📸 Photos of materials in actual use\n"
            response += "💡 Lessons learned and wastage analysis\n\n"
        
        # Market intelligence insights
        if assessment.get('market_intelligence', {}).get('price_insights'):
            market_data = assessment['market_intelligence']
            total_savings = sum(p['savings_potential'] for p in market_data['price_insights'] if p['savings_potential'] > 0)
            
            if total_savings > 100000:  # 100k+ UGX savings potential
                response += f"💰 **MARKET INTELLIGENCE ALERT**\n"
                response += f"Potential cost savings identified: {total_savings:,.0f} UGX\n"
                response += "Market analysis shows opportunities for better pricing.\n\n"
        
        # Supplier recommendations
        if assessment.get('supplier_recommendations', {}).get('suggested_suppliers'):
            response += f"🤝 **SUPPLIER OPTIMIZATION OPPORTUNITIES**\n"
            supplier_data = assessment['supplier_recommendations']['suggested_suppliers']
            response += f"Alternative suppliers identified for {len(supplier_data)} items\n"
            response += "Consider supplier performance optimization.\n\n"
        
        # Risk level indicator
        if assessment['risk_score'] > 80:
            response += "🚨 **HIGH RISK - HOLD FOR REVIEW** - Critical issues require resolution\n\n"
        elif assessment['risk_score'] > 50:
            response += "⚠️ **MEDIUM RISK** - Address procurement inefficiencies\n\n"
        else:
            response += "✅ **PROCUREMENT APPROVED** - Efficient resource allocation\n\n"
        
        # Uganda market context
        if doc.company:
            response += f"**🇺🇬 Uganda Market Context:**\n"
            response += f"• Current market conditions analyzed\n"
            response += f"• Local supplier performance considered\n"
            response += f"• Seasonal pricing factors evaluated\n\n"
        
        # Detailed findings
        if risk_factors:
            response += "**📋 Procurement Analysis:**\n"
            for factor in risk_factors:
                for finding in factor['findings']:
                    response += f"• {finding}\n"
            response += "\n"
        
        # Professional recommendations
        all_recommendations = []
        for factor in risk_factors:
            all_recommendations.extend(factor['recommendations'])
        
        if all_recommendations:
            response += "**💡 Procurement Optimization:**\n"
            for rec in all_recommendations:
                response += f"• {rec}\n"
            response += "\n"
        
        # Alternative suggestions
        if assessment.get('alternative_suggestions'):
            alternatives = assessment['alternative_suggestions']
            total_alt_savings = sum(alt['cost_savings'] for alt in alternatives)
            
            if total_alt_savings > 50000:  # 50k+ savings
                response += f"**🔄 ALTERNATIVE ITEMS AVAILABLE**\n"
                response += f"Cost-effective alternatives identified: {total_alt_savings:,.0f} UGX potential savings\n\n"
        
        # Final decision
        if assessment['risk_score'] > 80:
            response += "**❌ MATERIAL REQUEST BLOCKED** - Complete accountability requirements and address issues."
        elif assessment['risk_score'] > 50:
            response += "**⚠️ CONDITIONAL APPROVAL** - Optimize procurement approach as recommended."
        else:
            response += "**✅ PROCUREMENT AUTHORIZED** - Efficient resource allocation validated."
        
        response += f"\n\n*Serving Uganda's procurement needs with 15+ years of market expertise.*"
        
        return response
    
    # Helper methods for market intelligence and analysis
    
    def requires_material_followup(self, request):
        """Determine if a material request requires follow-up"""
        return (request.total_estimated_cost or 0) > 100000  # 100k UGX threshold
    
    def get_uganda_market_data(self, item_code):
        """Get Uganda market intelligence for item"""
        # This would integrate with local market data sources
        # Simplified mock data structure
        return {
            'average_market_price': self.get_average_market_price(item_code),
            'availability_status': self.get_availability_status(item_code),
            'seasonal_trend': self.get_seasonal_trend(item_code),
            'price_trend': 'stable',  # stable, increasing, decreasing
            'lead_time_days': 7
        }
    
    def get_item_supplier_performance(self, item_code):
        """Get supplier performance data for item"""
        suppliers = frappe.db.sql("""
            SELECT 
                pi.supplier,
                AVG(pii.rate) as average_price,
                COUNT(*) as transaction_count,
                AVG(DATEDIFF(pi.posting_date, po.transaction_date)) as avg_delivery_days,
                AVG(CASE WHEN pi.posting_date <= po.schedule_date THEN 100 ELSE 80 END) as delivery_performance,
                AVG(95) as quality_rating  -- Simplified
            FROM `tabPurchase Invoice Item` pii
            JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
            LEFT JOIN `tabPurchase Order` po ON pi.purchase_order = po.name
            WHERE pii.item_code = %s
            AND pi.docstatus = 1
            AND pi.posting_date >= %s
            GROUP BY pi.supplier
            HAVING transaction_count >= 2
            ORDER BY delivery_performance DESC, average_price ASC
        """, (item_code, add_days(nowdate(), -365)), as_dict=True)
        
        # Calculate performance score
        for supplier in suppliers:
            score = (
                (supplier.delivery_performance or 80) * 0.4 +
                (supplier.quality_rating or 85) * 0.3 +
                (100 - min((supplier.avg_delivery_days or 10) * 5, 50)) * 0.3
            )
            supplier['performance_score'] = score
        
        return suppliers
    
    def get_current_stock_levels(self, item_code):
        """Get current stock levels across warehouses"""
        stock_data = frappe.db.sql("""
            SELECT 
                SUM(actual_qty) as total_stock,
                SUM(stock_value) as total_value,
                COUNT(DISTINCT warehouse) as warehouse_count
            FROM `tabBin`
            WHERE item_code = %s
            AND actual_qty > 0
        """, (item_code,), as_dict=True)
        
        return stock_data[0] if stock_data else {'total_stock': 0, 'total_value': 0, 'warehouse_count': 0}
    
    def get_item_usage_pattern(self, item_code):
        """Get item usage pattern and velocity"""
        usage_data = frappe.db.sql("""
            SELECT 
                AVG(qty) as monthly_avg_usage,
                STDDEV(qty) as usage_variability,
                COUNT(*) as transaction_frequency
            FROM (
                SELECT 
                    YEAR(posting_date) as year,
                    MONTH(posting_date) as month,
                    SUM(qty) as qty
                FROM `tabStock Ledger Entry`
                WHERE item_code = %s
                AND voucher_type IN ('Material Issue', 'Stock Entry')
                AND posting_date >= %s
                GROUP BY YEAR(posting_date), MONTH(posting_date)
            ) monthly_usage
        """, (item_code, add_days(nowdate(), -180)), as_dict=True)
        
        result = usage_data[0] if usage_data else {'monthly_avg_usage': 0, 'usage_variability': 0, 'transaction_frequency': 0}
        
        # Classify velocity
        if result['transaction_frequency'] >= 4:  # 4+ months of activity
            if result['monthly_avg_usage'] >= 100:
                result['velocity_category'] = 'fast'
            elif result['monthly_avg_usage'] >= 20:
                result['velocity_category'] = 'medium'
            else:
                result['velocity_category'] = 'slow'
        else:
            result['velocity_category'] = 'new'
        
        return result
    
    def calculate_eoq(self, item_code, requested_qty):
        """Calculate Economic Order Quantity"""
        # Simplified EOQ calculation
        annual_demand = self.get_annual_demand(item_code)
        holding_cost_percent = 0.15  # 15% holding cost
        ordering_cost = 5000  # 5k UGX per order (simplified)
        
        if annual_demand > 0:
            eoq = (2 * annual_demand * ordering_cost / (holding_cost_percent * self.get_average_unit_cost(item_code))) ** 0.5
            variance_percent = abs((requested_qty - eoq) / eoq) * 100
        else:
            eoq = requested_qty
            variance_percent = 0
        
        return {
            'eoq': eoq,
            'variance_percent': variance_percent,
            'recommended_action': 'optimize_quantity' if variance_percent > 30 else 'quantity_acceptable'
        }
    
    def get_average_market_price(self, item_code):
        """Get average market price for item"""
        # This would integrate with market price APIs
        recent_purchases = frappe.db.sql("""
            SELECT AVG(rate) as avg_rate
            FROM `tabPurchase Invoice Item` pii
            JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
            WHERE pii.item_code = %s
            AND pi.docstatus = 1
            AND pi.posting_date >= %s
        """, (item_code, add_days(nowdate(), -90)), as_dict=True)
        
        return recent_purchases[0]['avg_rate'] if recent_purchases and recent_purchases[0]['avg_rate'] else 0
    
    def get_availability_status(self, item_code):
        """Get market availability status"""
        # Simplified availability check
        recent_orders = frappe.db.count('Purchase Order Item', {
            'item_code': item_code,
            'creation': ['>=', add_days(nowdate(), -30)]
        })
        
        if recent_orders > 5:
            return 'abundant'
        elif recent_orders > 2:
            return 'normal'
        else:
            return 'scarce'
    
    def get_seasonal_trend(self, item_code):
        """Get seasonal pricing trend"""
        current_month = getdate(nowdate()).month
        
        # Simplified seasonal analysis
        construction_materials = ['cement', 'steel', 'brick', 'sand']
        agricultural_items = ['fertilizer', 'seed', 'pesticide']
        
        item_name = frappe.db.get_value('Item', item_code, 'item_name') or ''
        item_name_lower = item_name.lower()
        
        if any(material in item_name_lower for material in construction_materials):
            # Construction materials peak during dry seasons (Dec-Mar, Jun-Aug)
            if current_month in [12, 1, 2, 3, 6, 7, 8]:
                return 'peak_season'
            else:
                return 'off_season'
        elif any(agri in item_name_lower for agri in agricultural_items):
            # Agricultural items peak during planting seasons (Mar-May, Sep-Nov)
            if current_month in [3, 4, 5, 9, 10, 11]:
                return 'peak_season'
            else:
                return 'off_season'
        
        return 'stable'


# Frappe whitelisted methods

@frappe.whitelist()
def assess_material_request_risk(doc_name, trigger_point="on_save"):
    """API method for material request risk assessment"""
    try:
        doc = frappe.get_doc('Material Request', doc_name)
        assessor = MaterialRequestIntelligence()
        return assessor.assess_material_request(doc, trigger_point)
    except Exception as e:
        frappe.log_error(f"Material Request Risk Assessment Error: {str(e)}", "Material Intelligence")
        return {'error': str(e)}

@frappe.whitelist()
def get_uganda_market_intelligence(item_code):
    """API method for Uganda market intelligence"""
    try:
        assessor = MaterialRequestIntelligence()
        return assessor.get_uganda_market_data(item_code)
    except Exception as e:
        frappe.log_error(f"Market Intelligence Error: {str(e)}", "Material Intelligence")
        return {'error': str(e)}

@frappe.whitelist()
def get_supplier_recommendations(item_code):
    """API method for supplier performance recommendations"""
    try:
        assessor = MaterialRequestIntelligence()
        return assessor.get_item_supplier_performance(item_code)
    except Exception as e:
        frappe.log_error(f"Supplier Recommendations Error: {str(e)}", "Material Intelligence")
        return {'error': str(e)}

@frappe.whitelist()
def check_material_accountability(requested_by):
    """API method for checking material accountability status"""
    try:
        assessor = MaterialRequestIntelligence()
        mock_doc = frappe._dict({'requested_by': requested_by})
        return assessor.check_material_accountability(mock_doc)
    except Exception as e:
        frappe.log_error(f"Material Accountability Check Error: {str(e)}", "Material Intelligence")
        return {'error': str(e)} 