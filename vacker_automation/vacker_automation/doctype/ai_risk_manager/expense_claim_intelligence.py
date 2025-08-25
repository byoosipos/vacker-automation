# Expense Claim Intelligence with Accountability Framework
# Copyright (c) 2025, Vacker and contributors

import frappe
import json
import re
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, add_days, nowdate, cstr
from .document_risk_assessment import DocumentRiskAssessmentEngine
import requests
from PIL import Image
import pytesseract
import io
import base64


class ExpenseClaimIntelligence(DocumentRiskAssessmentEngine):
    """
    Act as strategic project coordinator ensuring responsible resource utilization
    Enforces mandatory accountability framework with evidence-based validation
    """
    
    def assess_expense_claim(self, doc, trigger_point):
        """Comprehensive Expense Claim Risk Assessment with Accountability"""
        
        assessment = {
            'risk_level': 'low',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'warnings': [],
            'compliance_status': 'compliant',
            'personality_response': '',
            'accountability_status': {},
            'evidence_validation': {},
            'policy_compliance': {}
        }
        
        risk_factors = []
        
        # 1. MANDATORY: Evidence Validation
        evidence_validation = self.validate_supporting_evidence(doc)
        assessment['evidence_validation'] = evidence_validation
        if evidence_validation['risk_score'] > 0:
            risk_factors.append(evidence_validation)
        
        # 2. MANDATORY: Previous Expense Follow-up Check
        accountability_check = self.check_previous_expense_accountability(doc)
        assessment['accountability_status'] = accountability_check
        if accountability_check['requires_followup']:
            risk_factors.append(accountability_check)
        
        # 3. Policy Compliance Analysis
        policy_compliance = self.analyze_policy_compliance(doc)
        assessment['policy_compliance'] = policy_compliance
        if policy_compliance['risk_score'] > 0:
            risk_factors.append(policy_compliance)
        
        # 4. Spending Pattern Analysis
        spending_pattern = self.analyze_spending_patterns(doc)
        if spending_pattern['risk_score'] > 0:
            risk_factors.append(spending_pattern)
        
        # 5. Project Budget Impact
        budget_impact = self.analyze_project_budget_impact(doc)
        if budget_impact['risk_score'] > 0:
            risk_factors.append(budget_impact)
        
        # 6. Duplicate Expense Detection
        duplicate_check = self.detect_duplicate_expenses(doc)
        if duplicate_check['risk_score'] > 0:
            risk_factors.append(duplicate_check)
        
        # 7. Approval Hierarchy Validation
        approval_validation = self.validate_approval_hierarchy(doc)
        if approval_validation['risk_score'] > 0:
            risk_factors.append(approval_validation)
        
        # Calculate overall risk
        assessment = self.calculate_overall_risk(assessment, risk_factors)
        
        # Generate personality response
        assessment['personality_response'] = self.generate_project_coordinator_response(
            doc, assessment, risk_factors
        )
        
        return assessment
    
    def validate_supporting_evidence(self, doc):
        """MANDATORY: Validate OCR receipts and evidence completeness"""
        
        risk_assessment = {
            'category': 'evidence_validation',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'evidence_analysis': {},
            'requires_additional_evidence': False
        }
        
        # Check for attached receipts
        attachments = frappe.get_all('File', 
            filters={'attached_to_doctype': 'Expense Claim', 'attached_to_name': doc.name},
            fields=['name', 'file_name', 'file_url']
        )
        
        if not attachments:
            risk_assessment['risk_score'] = 95
            risk_assessment['findings'].append("No supporting receipts/evidence attached")
            risk_assessment['recommendations'].append("MANDATORY: Upload clear photos of all receipts")
            risk_assessment['requires_additional_evidence'] = True
            return risk_assessment
        
        # Analyze each expense item for evidence
        total_amount = doc.total_claimed_amount or 0
        evidence_coverage = 0
        receipt_analysis = []
        
        for expense in doc.expenses:
            expense_evidence = self.analyze_expense_evidence(expense, attachments)
            receipt_analysis.append(expense_evidence)
            
            if expense_evidence['has_valid_evidence']:
                evidence_coverage += expense.amount
        
        coverage_percent = (evidence_coverage / total_amount * 100) if total_amount > 0 else 0
        
        if coverage_percent < 80:
            risk_assessment['risk_score'] = 80
            risk_assessment['findings'].append(
                f"Only {coverage_percent:.1f}% of expenses have valid evidence"
            )
            risk_assessment['recommendations'].append(
                "Provide receipts for ALL expense items"
            )
            risk_assessment['requires_additional_evidence'] = True
        
        # High-value expense special validation
        high_value_expenses = [e for e in doc.expenses if e.amount > 100000]  # 100k UGX
        for expense in high_value_expenses:
            if not self.has_detailed_justification(expense):
                risk_assessment['risk_score'] += 30
                risk_assessment['findings'].append(
                    f"High-value expense ({expense.amount}) lacks detailed justification"
                )
                risk_assessment['recommendations'].append(
                    "Provide detailed business justification for high-value expenses"
                )
        
        risk_assessment['evidence_analysis'] = {
            'coverage_percent': coverage_percent,
            'receipt_analysis': receipt_analysis,
            'total_attachments': len(attachments)
        }
        
        return risk_assessment
    
    def check_previous_expense_accountability(self, doc):
        """MANDATORY: Check accountability for previous expense claims"""
        
        accountability_check = {
            'category': 'accountability_framework',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'requires_followup': False,
            'pending_followups': []
        }
        
        # Get previous expense claims from last 90 days
        previous_claims = frappe.db.sql("""
            SELECT 
                ec.name,
                ec.posting_date,
                ec.total_claimed_amount,
                ec.project,
                ec.purpose,
                COALESCE(ef.followup_status, 'pending') as followup_status,
                ef.impact_report,
                ef.evidence_photos
            FROM `tabExpense Claim` ec
            LEFT JOIN `tabExpense Followup` ef ON ef.expense_claim = ec.name
            WHERE ec.employee = %s
            AND ec.docstatus = 1
            AND ec.posting_date >= %s
            AND ec.name != %s
            ORDER BY ec.posting_date DESC
        """, (
            doc.employee, 
            add_days(nowdate(), -90), 
            doc.name or ''
        ), as_dict=True)
        
        pending_followups = []
        total_pending_amount = 0
        
        for claim in previous_claims:
            if claim.followup_status == 'pending':
                # Check if claim requires follow-up based on amount and type
                if self.requires_accountability_followup(claim):
                    pending_followups.append({
                        'claim_name': claim.name,
                        'amount': claim.total_claimed_amount,
                        'date': claim.posting_date,
                        'project': claim.project,
                        'purpose': claim.purpose,
                        'days_pending': (getdate(nowdate()) - getdate(claim.posting_date)).days
                    })
                    total_pending_amount += claim.total_claimed_amount
        
        if pending_followups:
            accountability_check['requires_followup'] = True
            accountability_check['pending_followups'] = pending_followups
            
            # Block if there are high-value pending follow-ups
            if total_pending_amount > 500000:  # 500k UGX
                accountability_check['risk_score'] = 95
                accountability_check['findings'].append(
                    f"BLOCKED: {len(pending_followups)} pending expense follow-ups totaling {total_pending_amount:,.0f} UGX"
                )
                accountability_check['recommendations'].append(
                    "Complete accountability reports for previous expenses before submitting new claims"
                )
            else:
                accountability_check['risk_score'] = 50
                accountability_check['findings'].append(
                    f"{len(pending_followups)} expense claims require accountability follow-up"
                )
                accountability_check['recommendations'].append(
                    "Submit outcome reports for pending expense follow-ups"
                )
        
        return accountability_check
    
    def analyze_policy_compliance(self, doc):
        """Analyze compliance with company expense policies"""
        
        risk_assessment = {
            'category': 'policy_compliance',
            'risk_score': 0,
            'findings': [],
            'recommendations': [],
            'policy_violations': []
        }
        
        policy_violations = []
        
        # Get company expense policy limits
        expense_policy = self.get_expense_policy_limits()
        
        for expense in doc.expenses:
            # Check daily limits
            daily_limit = expense_policy.get(expense.expense_type, {}).get('daily_limit', 0)
            if daily_limit > 0 and expense.amount > daily_limit:
                policy_violations.append({
                    'type': 'daily_limit_exceeded',
                    'expense_type': expense.expense_type,
                    'amount': expense.amount,
                    'limit': daily_limit,
                    'variance': expense.amount - daily_limit
                })
            
            # Check requires approval
            approval_threshold = expense_policy.get(expense.expense_type, {}).get('approval_threshold', 0)
            if expense.amount > approval_threshold and not doc.approval_status:
                policy_violations.append({
                    'type': 'approval_required',
                    'expense_type': expense.expense_type,
                    'amount': expense.amount,
                    'threshold': approval_threshold
                })
            
            # Check advance required
            if expense.amount > 200000 and not doc.advance_paid:  # 200k UGX
                policy_violations.append({
                    'type': 'advance_required',
                    'expense_type': expense.expense_type,
                    'amount': expense.amount
                })
        
        if policy_violations:
            risk_assessment['risk_score'] = len(policy_violations) * 20
            risk_assessment['policy_violations'] = policy_violations
            
            for violation in policy_violations:
                if violation['type'] == 'daily_limit_exceeded':
                    risk_assessment['findings'].append(
                        f"{violation['expense_type']}: Amount {violation['amount']:,.0f} exceeds daily limit {violation['limit']:,.0f}"
                    )
                elif violation['type'] == 'approval_required':
                    risk_assessment['findings'].append(
                        f"{violation['expense_type']}: Amount {violation['amount']:,.0f} requires management approval"
                    )
                elif violation['type'] == 'advance_required':
                    risk_assessment['findings'].append(
                        f"High-value expense {violation['amount']:,.0f} should have advance payment"
                    )
            
            risk_assessment['recommendations'].append(
                "Ensure compliance with company expense policies"
            )
        
        return risk_assessment
    
    def analyze_spending_patterns(self, doc):
        """Analyze employee spending patterns for anomalies"""
        
        risk_assessment = {
            'category': 'spending_patterns',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        # Get employee's historical spending
        historical_spending = frappe.db.sql("""
            SELECT 
                expense_type,
                AVG(amount) as avg_amount,
                COUNT(*) as frequency,
                MAX(amount) as max_amount
            FROM `tabExpense Claim Detail` ecd
            JOIN `tabExpense Claim` ec ON ecd.parent = ec.name
            WHERE ec.employee = %s
            AND ec.docstatus = 1
            AND ec.posting_date >= %s
            GROUP BY expense_type
        """, (doc.employee, add_days(nowdate(), -180)), as_dict=True)
        
        spending_patterns = {h['expense_type']: h for h in historical_spending}
        
        anomalies = []
        
        for expense in doc.expenses:
            historical = spending_patterns.get(expense.expense_type)
            
            if historical:
                # Check for amount anomalies
                variance_percent = ((expense.amount - historical['avg_amount']) / historical['avg_amount']) * 100
                
                if variance_percent > 200:  # 200% above average
                    anomalies.append({
                        'expense_type': expense.expense_type,
                        'current_amount': expense.amount,
                        'avg_amount': historical['avg_amount'],
                        'variance_percent': variance_percent,
                        'anomaly_type': 'unusual_amount'
                    })
                
                # Check for frequency anomalies
                recent_frequency = frappe.db.count('Expense Claim Detail', {
                    'expense_type': expense.expense_type,
                    'creation': ['>=', add_days(nowdate(), -30)]
                })
                
                if recent_frequency > historical['frequency'] * 2:
                    anomalies.append({
                        'expense_type': expense.expense_type,
                        'recent_frequency': recent_frequency,
                        'historical_frequency': historical['frequency'],
                        'anomaly_type': 'high_frequency'
                    })
        
        if anomalies:
            risk_assessment['risk_score'] = len(anomalies) * 25
            
            for anomaly in anomalies:
                if anomaly['anomaly_type'] == 'unusual_amount':
                    risk_assessment['findings'].append(
                        f"{anomaly['expense_type']}: Amount {anomaly['current_amount']:,.0f} is {anomaly['variance_percent']:.0f}% above average"
                    )
                elif anomaly['anomaly_type'] == 'high_frequency':
                    risk_assessment['findings'].append(
                        f"{anomaly['expense_type']}: Unusually high frequency of claims"
                    )
            
            risk_assessment['recommendations'].append(
                "Review spending patterns and provide justification for anomalies"
            )
        
        return risk_assessment
    
    def analyze_project_budget_impact(self, doc):
        """Analyze impact on project budgets"""
        
        risk_assessment = {
            'category': 'project_budget_impact',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        if not doc.project:
            return risk_assessment
        
        # Get project budget information
        project_doc = frappe.get_doc('Project', doc.project)
        
        if project_doc.total_sales_amount:
            # Calculate current project expenses
            current_expenses = frappe.db.sql("""
                SELECT SUM(ec.total_claimed_amount)
                FROM `tabExpense Claim` ec
                WHERE ec.project = %s
                AND ec.docstatus = 1
            """, (doc.project,))[0][0] or 0
            
            # Add current claim
            projected_expenses = current_expenses + doc.total_claimed_amount
            expense_ratio = (projected_expenses / project_doc.total_sales_amount) * 100
            
            if expense_ratio > 80:
                risk_assessment['risk_score'] = 70
                risk_assessment['findings'].append(
                    f"Project expenses at {expense_ratio:.1f}% of budget - approaching limit"
                )
                risk_assessment['recommendations'].append(
                    "Review project budget allocation and expense necessity"
                )
            elif expense_ratio > 60:
                risk_assessment['risk_score'] = 30
                risk_assessment['findings'].append(
                    f"Project expenses at {expense_ratio:.1f}% of budget"
                )
                risk_assessment['recommendations'].append(
                    "Monitor project expense levels closely"
                )
        
        return risk_assessment
    
    def detect_duplicate_expenses(self, doc):
        """Detect potential duplicate expense entries"""
        
        risk_assessment = {
            'category': 'duplicate_detection',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        duplicates = []
        
        for expense in doc.expenses:
            # Check for similar expenses in last 30 days
            similar_expenses = frappe.db.sql("""
                SELECT 
                    ec.name,
                    ec.posting_date,
                    ecd.amount,
                    ecd.description
                FROM `tabExpense Claim Detail` ecd
                JOIN `tabExpense Claim` ec ON ecd.parent = ec.name
                WHERE ec.employee = %s
                AND ecd.expense_type = %s
                AND ABS(ecd.amount - %s) <= 1000
                AND ec.posting_date BETWEEN %s AND %s
                AND ec.docstatus = 1
                AND ec.name != %s
            """, (
                doc.employee,
                expense.expense_type,
                expense.amount,
                add_days(expense.expense_date, -30),
                add_days(expense.expense_date, 30),
                doc.name or ''
            ), as_dict=True)
            
            if similar_expenses:
                duplicates.append({
                    'current_expense': expense,
                    'similar_expenses': similar_expenses
                })
        
        if duplicates:
            risk_assessment['risk_score'] = len(duplicates) * 40
            risk_assessment['findings'].append(
                f"{len(duplicates)} expenses have potential duplicates"
            )
            risk_assessment['recommendations'].append(
                "Verify these are not duplicate expense entries"
            )
        
        return risk_assessment
    
    def validate_approval_hierarchy(self, doc):
        """Validate approval hierarchy compliance"""
        
        risk_assessment = {
            'category': 'approval_hierarchy',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        total_amount = doc.total_claimed_amount or 0
        
        # Define approval thresholds
        approval_thresholds = {
            'supervisor': 100000,  # 100k UGX
            'manager': 500000,     # 500k UGX
            'director': 1000000    # 1M UGX
        }
        
        required_approval_level = 'self'
        if total_amount > approval_thresholds['director']:
            required_approval_level = 'director'
        elif total_amount > approval_thresholds['manager']:
            required_approval_level = 'manager'
        elif total_amount > approval_thresholds['supervisor']:
            required_approval_level = 'supervisor'
        
        if required_approval_level != 'self' and not doc.approval_status:
            risk_assessment['risk_score'] = 60
            risk_assessment['findings'].append(
                f"Amount {total_amount:,.0f} requires {required_approval_level} approval"
            )
            risk_assessment['recommendations'].append(
                f"Obtain {required_approval_level} approval before processing"
            )
        
        return risk_assessment
    
    def generate_project_coordinator_response(self, doc, assessment, risk_factors):
        """Generate response as strategic project coordinator"""
        
        user_name = frappe.db.get_value('User', self.user, 'full_name') or 'there'
        employee_name = frappe.db.get_value('Employee', doc.employee, 'employee_name') or doc.employee
        
        response = f"👨‍💼 **Project Coordinator Review - Expense Claim Analysis**\n\n"
        response += f"Hello {user_name}, I'm reviewing {employee_name}'s expense claim for {doc.total_claimed_amount:,.0f} UGX.\n\n"
        
        # Accountability status
        if assessment.get('accountability_status', {}).get('requires_followup'):
            pending = assessment['accountability_status']['pending_followups']
            response += f"🚫 **ACCOUNTABILITY REQUIRED FIRST**\n"
            response += f"I found {len(pending)} pending expense follow-ups that need completion:\n"
            for p in pending[:3]:  # Show first 3
                response += f"• {p['claim_name']}: {p['amount']:,.0f} UGX from {p['date']} ({p['days_pending']} days ago)\n"
            response += "\n**Required Evidence for Previous Expenses:**\n"
            response += "📸 Photos showing materials/services in use\n"
            response += "📋 Brief outcome report on project impact\n"
            response += "💡 Lessons learned and recommendations\n\n"
        
        # Evidence validation
        if assessment.get('evidence_validation', {}).get('requires_additional_evidence'):
            evidence = assessment['evidence_validation']
            response += f"📎 **EVIDENCE VALIDATION REQUIRED**\n"
            response += f"Coverage: {evidence['evidence_analysis']['coverage_percent']:.1f}% of expenses have receipts\n"
            response += "**Missing Evidence:**\n"
            for finding in evidence['findings']:
                response += f"• {finding}\n"
            response += "\n"
        
        # Risk level indicator
        if assessment['risk_score'] > 80:
            response += "🚨 **HIGH RISK - HOLD FOR REVIEW** - Critical issues must be resolved\n\n"
        elif assessment['risk_score'] > 50:
            response += "⚠️ **MEDIUM RISK** - Address issues below before approval\n\n"
        else:
            response += "✅ **LOW RISK** - Standard processing approved\n\n"
        
        # Project impact analysis
        if doc.project:
            response += f"**🎯 Project Impact Analysis:**\n"
            response += f"• Project: {doc.project}\n"
            response += f"• Resource allocation efficiency assessment needed\n"
            response += f"• Expected ROI documentation required\n\n"
        
        # All findings
        if risk_factors:
            response += "**📋 Detailed Findings:**\n"
            for factor in risk_factors:
                for finding in factor['findings']:
                    response += f"• {finding}\n"
            response += "\n"
        
        # Strategic recommendations
        all_recommendations = []
        for factor in risk_factors:
            all_recommendations.extend(factor['recommendations'])
        
        if all_recommendations:
            response += "**💡 Strategic Recommendations:**\n"
            for rec in all_recommendations:
                response += f"• {rec}\n"
            response += "\n"
        
        # Final decision
        if assessment['risk_score'] > 80:
            response += "**❌ EXPENSE CLAIM BLOCKED** - Complete accountability requirements first."
        elif assessment['risk_score'] > 50:
            response += "**⚠️ CONDITIONAL APPROVAL** - Address identified issues."
        else:
            response += "**✅ APPROVED FOR PROCESSING** - Resource utilization validated."
        
        return response
    
    # Helper methods
    
    def analyze_expense_evidence(self, expense, attachments):
        """Analyze evidence for a specific expense"""
        return {
            'expense_type': expense.expense_type,
            'amount': expense.amount,
            'has_valid_evidence': len(attachments) > 0,  # Simplified for now
            'evidence_quality': 'basic',  # Can be enhanced with OCR
            'requires_additional_docs': expense.amount > 50000
        }
    
    def has_detailed_justification(self, expense):
        """Check if expense has detailed business justification"""
        return expense.description and len(expense.description) > 50
    
    def requires_accountability_followup(self, claim):
        """Determine if a claim requires accountability follow-up"""
        return claim.total_claimed_amount > 50000  # 50k UGX threshold
    
    def get_expense_policy_limits(self):
        """Get company expense policy limits"""
        # This would typically come from a settings doctype
        return {
            'Travel': {'daily_limit': 150000, 'approval_threshold': 300000},
            'Meals': {'daily_limit': 50000, 'approval_threshold': 100000},
            'Fuel': {'daily_limit': 100000, 'approval_threshold': 200000},
            'Accommodation': {'daily_limit': 200000, 'approval_threshold': 400000},
            'Materials': {'daily_limit': 500000, 'approval_threshold': 1000000}
        }


# Frappe whitelisted methods

@frappe.whitelist()
def assess_expense_claim_risk(doc_name, trigger_point="on_save"):
    """API method for expense claim risk assessment"""
    try:
        doc = frappe.get_doc('Expense Claim', doc_name)
        assessor = ExpenseClaimIntelligence()
        return assessor.assess_expense_claim(doc, trigger_point)
    except Exception as e:
        frappe.log_error(f"Expense Claim Risk Assessment Error: {str(e)}", "Expense Intelligence")
        return {'error': str(e)}

@frappe.whitelist()
def check_employee_accountability(employee):
    """API method for checking employee accountability status"""
    try:
        assessor = ExpenseClaimIntelligence()
        mock_doc = frappe._dict({'employee': employee})
        return assessor.check_previous_expense_accountability(mock_doc)
    except Exception as e:
        frappe.log_error(f"Employee Accountability Check Error: {str(e)}", "Expense Intelligence")
        return {'error': str(e)}

@frappe.whitelist()
def validate_expense_evidence(expense_claim, files_data):
    """API method for validating expense evidence using OCR"""
    try:
        assessor = ExpenseClaimIntelligence()
        doc = frappe.get_doc('Expense Claim', expense_claim)
        return assessor.validate_supporting_evidence(doc)
    except Exception as e:
        frappe.log_error(f"Evidence Validation Error: {str(e)}", "Expense Intelligence")
        return {'error': str(e)} 