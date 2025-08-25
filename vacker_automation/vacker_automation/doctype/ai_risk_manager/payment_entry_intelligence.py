# Payment Entry Intelligence for Advanced AI Risk Assessment
# Copyright (c) 2025, Vacker and contributors

import frappe
import json
import re
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, add_days, nowdate, cstr, fmt_money
from .document_risk_assessment import DocumentRiskAssessmentEngine


class PaymentEntryIntelligence(DocumentRiskAssessmentEngine):
    """
    Act as diligent finance controller ensuring payment integrity
    Advanced fraud detection and cash flow impact analysis
    """
    
    def assess_payment_entry(self, doc, trigger_point):
        """Comprehensive Payment Entry Risk Assessment"""
        
        assessment = {
            'risk_level': 'low',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'warnings': [],
            'compliance_status': 'compliant',
            'personality_response': '',
            'fraud_indicators': {},
            'cash_flow_impact': {},
            'reconciliation_status': {}
        }
        
        risk_factors = []
        
        # 1. CRITICAL: Fraud Detection Analysis
        fraud_analysis = self.detect_fraud_patterns(doc)
        assessment['fraud_indicators'] = fraud_analysis
        if fraud_analysis['risk_score'] > 0:
            risk_factors.append(fraud_analysis)
        
        # 2. Bank Account Validation
        bank_validation = self.validate_bank_account_details(doc)
        if bank_validation['risk_score'] > 0:
            risk_factors.append(bank_validation)
        
        # 3. Amount Variance Analysis
        amount_variance = self.analyze_amount_variances(doc)
        if amount_variance['risk_score'] > 0:
            risk_factors.append(amount_variance)
        
        # 4. Payment Authorization Check
        authorization_check = self.validate_payment_authorization(doc)
        if authorization_check['risk_score'] > 0:
            risk_factors.append(authorization_check)
        
        # 5. Cash Flow Impact Assessment
        cash_flow_impact = self.assess_cash_flow_impact(doc)
        assessment['cash_flow_impact'] = cash_flow_impact
        if cash_flow_impact['risk_score'] > 0:
            risk_factors.append(cash_flow_impact)
        
        # 6. Foreign Exchange Validation
        if doc.paid_from_account_currency != doc.paid_to_account_currency:
            fx_validation = self.validate_foreign_exchange(doc)
            if fx_validation['risk_score'] > 0:
                risk_factors.append(fx_validation)
        
        # 7. Bank Reconciliation Status
        reconciliation_status = self.check_bank_reconciliation_status(doc)
        assessment['reconciliation_status'] = reconciliation_status
        if reconciliation_status['risk_score'] > 0:
            risk_factors.append(reconciliation_status)
        
        # 8. Duplicate Payment Detection
        duplicate_check = self.detect_duplicate_payments(doc)
        if duplicate_check['risk_score'] > 0:
            risk_factors.append(duplicate_check)
        
        # Calculate overall risk
        assessment = self.calculate_overall_risk(assessment, risk_factors)
        
        # Generate personality response
        assessment['personality_response'] = self.generate_finance_controller_response(
            doc, assessment, risk_factors
        )
        
        return assessment
    
    def detect_fraud_patterns(self, doc):
        """Advanced fraud pattern detection"""
        
        risk_assessment = {
            'category': 'fraud_detection',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'fraud_indicators': [],
            'risk_level': 'low'
        }
        
        fraud_indicators = []
        
        # 1. Suspicious Amount Patterns
        amount_analysis = self.analyze_suspicious_amounts(doc)
        if amount_analysis['suspicious']:
            fraud_indicators.extend(amount_analysis['indicators'])
        
        # 2. Timing Analysis
        timing_analysis = self.analyze_payment_timing(doc)
        if timing_analysis['suspicious']:
            fraud_indicators.extend(timing_analysis['indicators'])
        
        # 3. Party Analysis
        party_analysis = self.analyze_party_patterns(doc)
        if party_analysis['suspicious']:
            fraud_indicators.extend(party_analysis['indicators'])
        
        # 4. Account Pattern Analysis
        account_analysis = self.analyze_account_patterns(doc)
        if account_analysis['suspicious']:
            fraud_indicators.extend(account_analysis['indicators'])
        
        # 5. Reference Document Validation
        reference_validation = self.validate_reference_documents(doc)
        if reference_validation['suspicious']:
            fraud_indicators.extend(reference_validation['indicators'])
        
        if fraud_indicators:
            high_risk_indicators = [fi for fi in fraud_indicators if fi['severity'] == 'high']
            medium_risk_indicators = [fi for fi in fraud_indicators if fi['severity'] == 'medium']
            
            if high_risk_indicators:
                risk_assessment['risk_score'] = 90
                risk_assessment['risk_level'] = 'critical'
                risk_assessment['findings'].append("CRITICAL: High-risk fraud indicators detected")
                risk_assessment['recommendations'].append("HOLD PAYMENT - Immediate investigation required")
            elif len(medium_risk_indicators) >= 2:
                risk_assessment['risk_score'] = 70
                risk_assessment['risk_level'] = 'high'
                risk_assessment['findings'].append("Multiple fraud risk indicators detected")
                risk_assessment['recommendations'].append("Enhanced verification required before processing")
            else:
                risk_assessment['risk_score'] = 40
                risk_assessment['risk_level'] = 'medium'
                risk_assessment['findings'].append("Potential fraud indicators require review")
        
        risk_assessment['fraud_indicators'] = fraud_indicators
        return risk_assessment
    
    def analyze_suspicious_amounts(self, doc):
        """Analyze payment amounts for suspicious patterns"""
        
        analysis = {'suspicious': False, 'indicators': []}
        
        amount = doc.paid_amount or 0
        
        # Round number amounts (potential fraud indicator)
        if amount > 10000 and amount % 10000 == 0:
            analysis['suspicious'] = True
            analysis['indicators'].append({
                'type': 'round_amount',
                'severity': 'medium',
                'description': f"Round number amount: {fmt_money(amount)}",
                'recommendation': "Verify business justification for round amount"
            })
        
        # Unusually high amounts
        if amount > 5000000:  # 5M UGX
            recent_payments = frappe.db.sql("""
                SELECT AVG(paid_amount) as avg_amount
                FROM `tabPayment Entry`
                WHERE company = %s
                AND docstatus = 1
                AND posting_date >= %s
                AND payment_type = %s
            """, (doc.company, add_days(nowdate(), -90), doc.payment_type), as_dict=True)
            
            if recent_payments and recent_payments[0].avg_amount:
                avg_amount = recent_payments[0].avg_amount
                variance = ((amount - avg_amount) / avg_amount) * 100
                
                if variance > 500:  # 500% above average
                    analysis['suspicious'] = True
                    analysis['indicators'].append({
                        'type': 'unusual_amount',
                        'severity': 'high',
                        'description': f"Amount {variance:.0f}% above average payment",
                        'recommendation': "Verify business necessity and authorization"
                    })
        
        # Just below authorization limits
        authorization_limits = self.get_authorization_limits()
        for limit_name, limit_amount in authorization_limits.items():
            if limit_amount - 50000 <= amount < limit_amount:
                analysis['suspicious'] = True
                analysis['indicators'].append({
                    'type': 'below_authorization_limit',
                    'severity': 'medium',
                    'description': f"Amount just below {limit_name} limit ({fmt_money(limit_amount)})",
                    'recommendation': "Verify not structured to avoid authorization"
                })
        
        return analysis
    
    def analyze_payment_timing(self, doc):
        """Analyze payment timing for suspicious patterns"""
        
        analysis = {'suspicious': False, 'indicators': []}
        
        posting_time = doc.get('posting_time') or '00:00:00'
        posting_date = getdate(doc.posting_date)
        
        # Late night payments
        if posting_time > '22:00:00' or posting_time < '06:00:00':
            analysis['suspicious'] = True
            analysis['indicators'].append({
                'type': 'unusual_timing',
                'severity': 'medium',
                'description': f"Payment created at {posting_time} (outside business hours)",
                'recommendation': "Verify business necessity for off-hours payment"
            })
        
        # Weekend payments
        if posting_date.weekday() >= 5:  # Saturday or Sunday
            analysis['suspicious'] = True
            analysis['indicators'].append({
                'type': 'weekend_payment',
                'severity': 'medium',
                'description': "Payment created on weekend",
                'recommendation': "Verify business urgency for weekend payment"
            })
        
        # Holiday payments
        if self.is_company_holiday(posting_date):
            analysis['suspicious'] = True
            analysis['indicators'].append({
                'type': 'holiday_payment',
                'severity': 'medium',
                'description': "Payment created on company holiday",
                'recommendation': "Verify business urgency for holiday payment"
            })
        
        # Rapid sequence payments to same party
        if doc.party_type and doc.party:
            recent_payments = frappe.db.count('Payment Entry', {
                'party_type': doc.party_type,
                'party': doc.party,
                'posting_date': ['>=', add_days(posting_date, -3)],
                'docstatus': 1,
                'name': ['!=', doc.name or '']
            })
            
            if recent_payments >= 3:
                analysis['suspicious'] = True
                analysis['indicators'].append({
                    'type': 'rapid_sequence',
                    'severity': 'high',
                    'description': f"{recent_payments} payments to same party in 3 days",
                    'recommendation': "Investigate potential structured payments or fraud"
                })
        
        return analysis
    
    def analyze_party_patterns(self, doc):
        """Analyze party-related fraud patterns"""
        
        analysis = {'suspicious': False, 'indicators': []}
        
        if not doc.party_type or not doc.party:
            return analysis
        
        # New party with high-value payment
        party_doc = frappe.get_doc(doc.party_type, doc.party)
        days_since_creation = (getdate(nowdate()) - getdate(party_doc.creation)).days
        
        if days_since_creation <= 7 and doc.paid_amount > 1000000:  # New party, 1M+ UGX
            analysis['suspicious'] = True
            analysis['indicators'].append({
                'type': 'new_party_high_value',
                'severity': 'high',
                'description': f"High-value payment to party created {days_since_creation} days ago",
                'recommendation': "Enhanced due diligence required for new high-value party"
            })
        
        # Check for similar party names (potential duplicate parties)
        similar_parties = self.find_similar_party_names(doc.party_type, doc.party)
        if similar_parties:
            analysis['suspicious'] = True
            analysis['indicators'].append({
                'type': 'similar_party_names',
                'severity': 'medium',
                'description': f"Found {len(similar_parties)} parties with similar names",
                'recommendation': "Verify not duplicate or related parties"
            })
        
        # Inactive party suddenly receiving payments
        if doc.party_type == 'Supplier':
            last_transaction = frappe.db.sql("""
                SELECT MAX(posting_date) as last_date
                FROM `tabPurchase Invoice`
                WHERE supplier = %s
                AND docstatus = 1
                AND posting_date < %s
            """, (doc.party, doc.posting_date), as_dict=True)
            
            if last_transaction and last_transaction[0].last_date:
                days_inactive = (getdate(doc.posting_date) - getdate(last_transaction[0].last_date)).days
                if days_inactive > 180:  # 6 months inactive
                    analysis['suspicious'] = True
                    analysis['indicators'].append({
                        'type': 'inactive_party_payment',
                        'severity': 'medium',
                        'description': f"Payment to supplier inactive for {days_inactive} days",
                        'recommendation': "Verify business relationship and payment necessity"
                    })
        
        return analysis
    
    def analyze_account_patterns(self, doc):
        """Analyze account usage patterns"""
        
        analysis = {'suspicious': False, 'indicators': []}
        
        # Unusual account combinations
        if doc.paid_from and doc.paid_to:
            # Check if this account combination is unusual
            usage_count = frappe.db.count('Payment Entry', {
                'paid_from': doc.paid_from,
                'paid_to': doc.paid_to,
                'docstatus': 1
            })
            
            if usage_count == 0:  # First time using this combination
                analysis['suspicious'] = True
                analysis['indicators'].append({
                    'type': 'unusual_account_combination',
                    'severity': 'medium',
                    'description': "First payment between these accounts",
                    'recommendation': "Verify account combination is appropriate"
                })
        
        # High-risk account types
        high_risk_accounts = ['Cash', 'Petty Cash', 'Temporary']
        
        if doc.paid_from:
            from_account_type = frappe.db.get_value('Account', doc.paid_from, 'account_type')
            if any(risk_type in (doc.paid_from or '') for risk_type in high_risk_accounts):
                if doc.paid_amount > 500000:  # 500k UGX
                    analysis['suspicious'] = True
                    analysis['indicators'].append({
                        'type': 'high_risk_account',
                        'severity': 'medium',
                        'description': f"High-value payment from {from_account_type} account",
                        'recommendation': "Verify authorization for cash-based high-value payment"
                    })
        
        return analysis
    
    def validate_reference_documents(self, doc):
        """Validate reference documents"""
        
        analysis = {'suspicious': False, 'indicators': []}
        
        if not doc.references:
            if doc.payment_type == 'Pay' and doc.paid_amount > 100000:
                analysis['suspicious'] = True
                analysis['indicators'].append({
                    'type': 'no_reference_document',
                    'severity': 'high',
                    'description': "High-value payment without reference document",
                    'recommendation': "Mandatory reference document required for payments >100k"
                })
        else:
            # Validate reference documents exist and are valid
            for ref in doc.references:
                if ref.reference_doctype and ref.reference_name:
                    if not frappe.db.exists(ref.reference_doctype, ref.reference_name):
                        analysis['suspicious'] = True
                        analysis['indicators'].append({
                            'type': 'invalid_reference',
                            'severity': 'high',
                            'description': f"Reference {ref.reference_doctype} {ref.reference_name} not found",
                            'recommendation': "Verify reference document validity"
                        })
        
        return analysis
    
    def validate_bank_account_details(self, doc):
        """Validate bank account details and patterns"""
        
        risk_assessment = {
            'category': 'bank_account_validation',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        # Validate bank account exists and is active
        if doc.paid_from:
            from_account = frappe.get_doc('Account', doc.paid_from)
            if from_account.is_group:
                risk_assessment['risk_score'] = 80
                risk_assessment['findings'].append("Payment from group account not allowed")
                risk_assessment['recommendations'].append("Select specific bank account")
        
        # Check for bank account mismatches
        if hasattr(doc, 'bank_account') and doc.bank_account:
            bank_account_doc = frappe.get_doc('Bank Account', doc.bank_account)
            if bank_account_doc.account != doc.paid_from:
                risk_assessment['risk_score'] += 40
                risk_assessment['findings'].append("Bank account mismatch with payment account")
                risk_assessment['recommendations'].append("Verify correct bank account selection")
        
        # Check account balance sufficiency
        if doc.payment_type == 'Pay':
            account_balance = self.get_account_balance(doc.paid_from, doc.posting_date)
            if account_balance < doc.paid_amount:
                risk_assessment['risk_score'] += 70
                risk_assessment['findings'].append(
                    f"Insufficient balance: {fmt_money(account_balance)} available, {fmt_money(doc.paid_amount)} required"
                )
                risk_assessment['recommendations'].append("Verify sufficient funds before processing")
        
        return risk_assessment
    
    def analyze_amount_variances(self, doc):
        """Analyze amount variances and allocations"""
        
        risk_assessment = {
            'category': 'amount_variance',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        if doc.references:
            total_allocated = sum(ref.allocated_amount for ref in doc.references)
            variance = abs(doc.paid_amount - total_allocated)
            
            if variance > 1000:  # 1k UGX tolerance
                variance_percent = (variance / doc.paid_amount) * 100
                
                if variance_percent > 5:  # 5% variance
                    risk_assessment['risk_score'] = 50
                    risk_assessment['findings'].append(
                        f"Amount variance: {fmt_money(variance)} ({variance_percent:.1f}%)"
                    )
                    risk_assessment['recommendations'].append("Verify allocation accuracy")
        
        # Check for over-allocation
        if doc.references:
            for ref in doc.references:
                if ref.reference_doctype and ref.reference_name:
                    outstanding = frappe.db.get_value(
                        ref.reference_doctype, 
                        ref.reference_name, 
                        'outstanding_amount'
                    ) or 0
                    
                    if ref.allocated_amount > outstanding + 1000:  # 1k tolerance
                        risk_assessment['risk_score'] += 60
                        risk_assessment['findings'].append(
                            f"Over-allocation: {fmt_money(ref.allocated_amount)} > {fmt_money(outstanding)} outstanding"
                        )
                        risk_assessment['recommendations'].append("Verify allocation does not exceed outstanding")
        
        return risk_assessment
    
    def validate_payment_authorization(self, doc):
        """Validate payment authorization levels"""
        
        risk_assessment = {
            'category': 'payment_authorization',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        amount = doc.paid_amount or 0
        
        # Define authorization requirements
        auth_levels = {
            'manager': 1000000,     # 1M UGX
            'director': 5000000,    # 5M UGX
            'board': 20000000       # 20M UGX
        }
        
        required_auth = 'none'
        if amount >= auth_levels['board']:
            required_auth = 'board'
        elif amount >= auth_levels['director']:
            required_auth = 'director'
        elif amount >= auth_levels['manager']:
            required_auth = 'manager'
        
        if required_auth != 'none':
            # Check if proper authorization exists
            auth_exists = self.check_payment_authorization_exists(doc, required_auth)
            
            if not auth_exists:
                risk_assessment['risk_score'] = 80
                risk_assessment['findings'].append(
                    f"Payment requires {required_auth} authorization (Amount: {fmt_money(amount)})"
                )
                risk_assessment['recommendations'].append(f"Obtain {required_auth} approval before processing")
        
        return risk_assessment
    
    def assess_cash_flow_impact(self, doc):
        """Assess impact on company cash flow"""
        
        impact_assessment = {
            'category': 'cash_flow_impact',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'projected_balance': 0,
            'impact_severity': 'low'
        }
        
        if doc.payment_type == 'Pay':
            # Get current cash position
            current_balance = self.get_current_cash_position(doc.company)
            projected_balance = current_balance - doc.paid_amount
            
            impact_assessment['projected_balance'] = projected_balance
            
            # Assess impact severity
            if projected_balance < 0:
                impact_assessment['risk_score'] = 90
                impact_assessment['impact_severity'] = 'critical'
                impact_assessment['findings'].append(
                    f"Payment would create negative cash position: {fmt_money(projected_balance)}"
                )
                impact_assessment['recommendations'].append("Defer payment or arrange funding")
            elif projected_balance < 1000000:  # 1M UGX minimum
                impact_assessment['risk_score'] = 60
                impact_assessment['impact_severity'] = 'high'
                impact_assessment['findings'].append(
                    f"Payment reduces cash to critically low level: {fmt_money(projected_balance)}"
                )
                impact_assessment['recommendations'].append("Monitor cash flow closely")
            elif projected_balance < current_balance * 0.2:  # Below 20% of current
                impact_assessment['risk_score'] = 30
                impact_assessment['impact_severity'] = 'medium'
                impact_assessment['findings'].append(
                    f"Payment significantly impacts cash position: {fmt_money(projected_balance)}"
                )
                impact_assessment['recommendations'].append("Consider payment timing optimization")
        
        return impact_assessment
    
    def validate_foreign_exchange(self, doc):
        """Validate foreign exchange rates and calculations"""
        
        risk_assessment = {
            'category': 'foreign_exchange',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        if doc.source_exchange_rate:
            # Get market rate
            market_rate = self.get_market_exchange_rate(
                doc.paid_from_account_currency,
                doc.paid_to_account_currency,
                doc.posting_date
            )
            
            if market_rate:
                variance_percent = abs((doc.source_exchange_rate - market_rate) / market_rate) * 100
                
                if variance_percent > 5:  # 5% variance threshold
                    risk_assessment['risk_score'] = 50
                    risk_assessment['findings'].append(
                        f"Exchange rate variance: {variance_percent:.1f}% from market rate"
                    )
                    risk_assessment['recommendations'].append("Verify exchange rate is current and accurate")
        
        return risk_assessment
    
    def check_bank_reconciliation_status(self, doc):
        """Check bank reconciliation requirements"""
        
        recon_assessment = {
            'category': 'bank_reconciliation',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'requires_reconciliation': False
        }
        
        # High-value payments require bank statement reconciliation
        if doc.paid_amount > 1000000:  # 1M UGX
            recon_assessment['requires_reconciliation'] = True
            recon_assessment['risk_score'] = 30
            recon_assessment['findings'].append("High-value payment requires bank reconciliation")
            recon_assessment['recommendations'].append("Ensure bank statement reconciliation within 24 hours")
        
        return recon_assessment
    
    def detect_duplicate_payments(self, doc):
        """Detect potential duplicate payments"""
        
        risk_assessment = {
            'category': 'duplicate_detection',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        # Check for similar payments in last 7 days
        if doc.party_type and doc.party:
            similar_payments = frappe.db.sql("""
                SELECT name, posting_date, paid_amount, reference_no
                FROM `tabPayment Entry`
                WHERE party_type = %s
                AND party = %s
                AND ABS(paid_amount - %s) <= 1000
                AND posting_date BETWEEN %s AND %s
                AND docstatus = 1
                AND name != %s
            """, (
                doc.party_type,
                doc.party,
                doc.paid_amount,
                add_days(doc.posting_date, -7),
                add_days(doc.posting_date, 7),
                doc.name or ''
            ), as_dict=True)
            
            if similar_payments:
                risk_assessment['risk_score'] = 70
                risk_assessment['findings'].append(
                    f"Found {len(similar_payments)} similar payments in last 7 days"
                )
                risk_assessment['recommendations'].append("Verify not duplicate payment")
        
        return risk_assessment
    
    def generate_finance_controller_response(self, doc, assessment, risk_factors):
        """Generate response as diligent finance controller"""
        
        user_name = frappe.db.get_value('User', self.user, 'full_name') or 'there'
        party_name = doc.party or 'Unknown'
        
        response = f"💼 **Finance Controller Review - Payment Entry Analysis**\n\n"
        response += f"Hello {user_name}, I'm reviewing payment of {fmt_money(doc.paid_amount)} to {party_name}.\n\n"
        
        # Fraud indicators
        if assessment.get('fraud_indicators', {}).get('fraud_indicators'):
            fraud_count = len(assessment['fraud_indicators']['fraud_indicators'])
            response += f"🚨 **FRAUD ALERT** - {fraud_count} suspicious indicators detected\n"
            response += "**Critical Security Review Required**\n\n"
        
        # Cash flow impact
        if assessment.get('cash_flow_impact', {}).get('impact_severity') in ['high', 'critical']:
            impact = assessment['cash_flow_impact']
            response += f"💰 **CASH FLOW IMPACT**: {impact['impact_severity'].upper()}\n"
            response += f"Projected balance after payment: {fmt_money(impact['projected_balance'])}\n\n"
        
        # Risk level indicator
        if assessment['risk_score'] > 80:
            response += "🚨 **CRITICAL RISK - PAYMENT BLOCKED** - Immediate review required\n\n"
        elif assessment['risk_score'] > 60:
            response += "⚠️ **HIGH RISK** - Enhanced verification needed\n\n"
        elif assessment['risk_score'] > 30:
            response += "⚠️ **MEDIUM RISK** - Standard review process\n\n"
        else:
            response += "✅ **LOW RISK** - Payment approved for processing\n\n"
        
        # Detailed findings
        if risk_factors:
            response += "**📋 Financial Control Findings:**\n"
            for factor in risk_factors:
                for finding in factor['findings']:
                    response += f"• {finding}\n"
            response += "\n"
        
        # Recommendations
        all_recommendations = []
        for factor in risk_factors:
            all_recommendations.extend(factor['recommendations'])
        
        if all_recommendations:
            response += "**💡 Control Recommendations:**\n"
            for rec in all_recommendations:
                response += f"• {rec}\n"
            response += "\n"
        
        # Final authorization decision
        if assessment['risk_score'] > 80:
            response += "**❌ PAYMENT BLOCKED** - Critical risks must be resolved before processing."
        elif assessment['risk_score'] > 60:
            response += "**⚠️ ENHANCED VERIFICATION REQUIRED** - Additional approvals needed."
        elif assessment['risk_score'] > 30:
            response += "**⚠️ PROCEED WITH CAUTION** - Standard verification completed."
        else:
            response += "**✅ PAYMENT AUTHORIZED** - All financial controls satisfied."
        
        return response
    
    # Helper methods
    
    def get_authorization_limits(self):
        """Get payment authorization limits"""
        return {
            'supervisor': 500000,   # 500k UGX
            'manager': 1000000,     # 1M UGX  
            'director': 5000000,    # 5M UGX
            'board': 20000000       # 20M UGX
        }
    
    def is_company_holiday(self, date):
        """Check if date is a company holiday"""
        # Simplified - would check against Holiday List
        return frappe.db.exists('Holiday', {
            'holiday_date': date,
            'parent': frappe.defaults.get_user_default('Holiday List')
        })
    
    def find_similar_party_names(self, party_type, party_name):
        """Find parties with similar names"""
        # Simplified similarity check
        similar = frappe.db.sql(f"""
            SELECT name
            FROM `tab{party_type}`
            WHERE name != %s
            AND SOUNDEX(name) = SOUNDEX(%s)
            LIMIT 5
        """, (party_name, party_name), as_dict=True)
        
        return similar
    
    def get_account_balance(self, account, date):
        """Get account balance on specific date"""
        from erpnext.accounts.utils import get_balance_on
        return get_balance_on(account, date)
    
    def get_current_cash_position(self, company):
        """Get current cash position"""
        cash_accounts = frappe.get_all('Account', 
            filters={
                'company': company,
                'account_type': ['in', ['Cash', 'Bank']], 
                'is_group': 0
            },
            fields=['name']
        )
        
        total_cash = 0
        for account in cash_accounts:
            balance = self.get_account_balance(account.name, nowdate())
            total_cash += balance
        
        return total_cash
    
    def check_payment_authorization_exists(self, doc, required_level):
        """Check if payment authorization exists"""
        # Simplified - would check against approval workflow
        return doc.get(f'{required_level}_approved') == 1
    
    def get_market_exchange_rate(self, from_currency, to_currency, date):
        """Get market exchange rate"""
        # Would integrate with external API or exchange rate service
        return frappe.db.get_value('Currency Exchange', {
            'from_currency': from_currency,
            'to_currency': to_currency
        }, 'exchange_rate')


# Frappe whitelisted methods

@frappe.whitelist()
def assess_payment_entry_risk(doc_name, trigger_point="on_save"):
    """API method for payment entry risk assessment"""
    try:
        doc = frappe.get_doc('Payment Entry', doc_name)
        assessor = PaymentEntryIntelligence()
        return assessor.assess_payment_entry(doc, trigger_point)
    except Exception as e:
        frappe.log_error(f"Payment Entry Risk Assessment Error: {str(e)}", "Payment Intelligence")
        return {'error': str(e)}

@frappe.whitelist()
def check_cash_flow_impact(company, amount, payment_date):
    """API method for checking cash flow impact"""
    try:
        assessor = PaymentEntryIntelligence()
        mock_doc = frappe._dict({
            'company': company,
            'paid_amount': flt(amount),
            'posting_date': payment_date,
            'payment_type': 'Pay'
        })
        return assessor.assess_cash_flow_impact(mock_doc)
    except Exception as e:
        frappe.log_error(f"Cash Flow Impact Check Error: {str(e)}", "Payment Intelligence")
        return {'error': str(e)}

@frappe.whitelist()
def detect_payment_fraud_patterns(party_type, party, amount, date):
    """API method for fraud pattern detection"""
    try:
        assessor = PaymentEntryIntelligence()
        mock_doc = frappe._dict({
            'party_type': party_type,
            'party': party,
            'paid_amount': flt(amount),
            'posting_date': date
        })
        return assessor.detect_fraud_patterns(mock_doc)
    except Exception as e:
        frappe.log_error(f"Fraud Pattern Detection Error: {str(e)}", "Payment Intelligence")
        return {'error': str(e)} 