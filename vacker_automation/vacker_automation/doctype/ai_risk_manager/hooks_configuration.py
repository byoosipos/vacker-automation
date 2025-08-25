# Hooks Configuration for Advanced AI Risk Assessment Integration
# Copyright (c) 2025, Vacker and contributors

import frappe
import json
from frappe.utils import nowdate, add_days, cstr
from .intelligent_validation_engine import ItemCreationIntelligence
from .document_risk_assessment import PurchaseInvoiceRiskAssessment
from .sales_invoice_intelligence import SalesInvoiceIntelligence
from .expense_claim_intelligence import ExpenseClaimIntelligence
from .payment_entry_intelligence import PaymentEntryIntelligence
from .material_request_intelligence import MaterialRequestIntelligence
from .quotation_intelligence import QuotationIntelligence
from .evidence_validation_system import EvidenceValidationSystem


class AIRiskAssessmentHooks:
    """
    Central hooks configuration for AI Risk Assessment integration
    Coordinates all AI intelligence modules with ERPNext document lifecycle
    """
    
    def __init__(self):
        self.enabled_doctypes = [
            'Item', 'Purchase Invoice', 'Sales Invoice', 'Payment Entry',
            'Expense Claim', 'Material Request', 'Purchase Order', 'Sales Order', 'Quotation'
        ]
        
        self.risk_thresholds = {
            'block_submission': 85,    # Block if risk score >= 85
            'require_approval': 60,    # Require additional approval if >= 60
            'warning_only': 30         # Show warning if >= 30
        }
    
    def before_insert(self, doc, method):
        """Hook: Before document insertion"""
        try:
            if doc.doctype in self.enabled_doctypes:
                # Pre-insertion risk assessment
                risk_assessment = self.assess_pre_insertion_risk(doc)
                
                if risk_assessment.get('block_creation'):
                    frappe.throw(
                        title="AI Risk Assessment Block",
                        msg=risk_assessment.get('message', 'Document creation blocked by AI risk assessment')
                    )
                
                # Store initial assessment in doc
                if hasattr(doc, 'set'):
                    doc.set('ai_risk_initial_assessment', json.dumps(risk_assessment))
                    
        except Exception as e:
            self.log_ai_error("before_insert", doc.doctype, doc.name, str(e))
    
    def validate(self, doc, method):
        """Hook: Document validation"""
        try:
            if doc.doctype in self.enabled_doctypes:
                # Comprehensive validation with AI
                validation_result = self.perform_ai_validation(doc)
                
                # Handle validation results
                self.handle_validation_results(doc, validation_result)
                
        except Exception as e:
            self.log_ai_error("validate", doc.doctype, doc.name, str(e))
    
    def before_save(self, doc, method):
        """Hook: Before document save"""
        try:
            if doc.doctype in self.enabled_doctypes:
                # Final risk assessment before save
                final_assessment = self.perform_final_risk_assessment(doc)
                
                # Store assessment results
                self.store_risk_assessment(doc, final_assessment)
                
                # Check if save should be blocked
                if final_assessment.get('risk_score', 0) >= self.risk_thresholds['block_submission']:
                    if not final_assessment.get('override_approved'):
                        frappe.throw(
                            title="High Risk Document Blocked",
                            msg=final_assessment.get('personality_response', 'Document blocked due to high risk score')
                        )
                
        except Exception as e:
            self.log_ai_error("before_save", doc.doctype, doc.name, str(e))
    
    def after_insert(self, doc, method):
        """Hook: After document insertion"""
        try:
            if doc.doctype in self.enabled_doctypes:
                # Create AI assessment log entry
                self.create_ai_assessment_log(doc, 'insert')
                
                # Schedule follow-up tasks if needed
                self.schedule_ai_followup_tasks(doc)
                
        except Exception as e:
            self.log_ai_error("after_insert", doc.doctype, doc.name, str(e))
    
    def on_submit(self, doc, method):
        """Hook: On document submission"""
        try:
            if doc.doctype in self.enabled_doctypes:
                # Final submission risk check
                submission_assessment = self.assess_submission_risk(doc)
                
                if submission_assessment.get('block_submission'):
                    frappe.throw(
                        title="Submission Blocked by AI",
                        msg=submission_assessment.get('message', 'Submission blocked by AI risk assessment')
                    )
                
                # Update risk assessment log
                self.update_ai_assessment_log(doc, 'submit', submission_assessment)
                
                # Trigger post-submission AI processes
                self.trigger_post_submission_processes(doc)
                
        except Exception as e:
            self.log_ai_error("on_submit", doc.doctype, doc.name, str(e))
    
    def on_cancel(self, doc, method):
        """Hook: On document cancellation"""
        try:
            if doc.doctype in self.enabled_doctypes:
                # Log cancellation in AI assessment
                self.update_ai_assessment_log(doc, 'cancel')
                
                # Update related accountability tracking
                self.update_accountability_tracking(doc, 'cancelled')
                
        except Exception as e:
            self.log_ai_error("on_cancel", doc.doctype, doc.name, str(e))
    
    def assess_pre_insertion_risk(self, doc):
        """Assess risk before document insertion"""
        
        assessment = {
            'risk_score': 0,
            'block_creation': False,
            'warnings': [],
            'recommendations': []
        }
        
        # Item-specific pre-insertion checks
        if doc.doctype == 'Item':
            # Check for accountability requirements
            if hasattr(doc, 'requested_by'):
                accountability_check = self.check_user_accountability(doc.requested_by)
                if accountability_check.get('requires_followup'):
                    assessment['block_creation'] = True
                    assessment['message'] = (
                        "Complete pending accountability requirements before creating new items. "
                        f"You have {len(accountability_check.get('pending_followups', []))} pending follow-ups."
                    )
        
        # Material Request pre-insertion checks
        elif doc.doctype == 'Material Request':
            if hasattr(doc, 'requested_by'):
                material_accountability = self.check_material_accountability(doc.requested_by)
                if material_accountability.get('requires_followup'):
                    pending = material_accountability.get('pending_followups', [])
                    total_value = sum(p.get('value', 0) for p in pending)
                    
                    if total_value > 2000000:  # 2M UGX block threshold
                        assessment['block_creation'] = True
                        assessment['message'] = (
                            f"Complete accountability for {len(pending)} pending material requests "
                            f"totaling {total_value:,.0f} UGX before submitting new requests."
                        )
        
        # Expense Claim pre-insertion checks
        elif doc.doctype == 'Expense Claim':
            if hasattr(doc, 'employee'):
                expense_accountability = self.check_expense_accountability(doc.employee)
                if expense_accountability.get('requires_followup'):
                    pending = expense_accountability.get('pending_followups', [])
                    total_value = sum(p.get('amount', 0) for p in pending)
                    
                    if total_value > 500000:  # 500k UGX block threshold
                        assessment['block_creation'] = True
                        assessment['message'] = (
                            f"Complete evidence submission for {len(pending)} pending expense claims "
                            f"totaling {total_value:,.0f} UGX before submitting new claims."
                        )
        
        return assessment
    
    def perform_ai_validation(self, doc):
        """Perform comprehensive AI validation"""
        
        validation_result = {
            'risk_score': 0,
            'validation_status': 'approved',
            'findings': [],
            'recommendations': [],
            'personality_response': '',
            'detailed_analysis': {}
        }
        
        try:
            # Route to appropriate AI intelligence module
            if doc.doctype == 'Item':
                intelligence = ItemCreationIntelligence()
                analysis = intelligence.validate_item_creation(doc)
                
            elif doc.doctype == 'Purchase Invoice':
                intelligence = PurchaseInvoiceRiskAssessment()
                analysis = intelligence.assess_purchase_invoice(doc, 'validate')
                
            elif doc.doctype == 'Sales Invoice':
                intelligence = SalesInvoiceIntelligence()
                analysis = intelligence.assess_sales_invoice(doc, 'validate')
                
            elif doc.doctype == 'Payment Entry':
                intelligence = PaymentEntryIntelligence()
                analysis = intelligence.assess_payment_entry(doc, 'validate')
                
            elif doc.doctype == 'Expense Claim':
                intelligence = ExpenseClaimIntelligence()
                analysis = intelligence.assess_expense_claim(doc, 'validate')
                
            elif doc.doctype == 'Material Request':
                intelligence = MaterialRequestIntelligence()
                analysis = intelligence.assess_material_request(doc, 'validate')
                
            elif doc.doctype == 'Quotation':
                intelligence = QuotationIntelligence()
                analysis = intelligence.assess_quotation(doc, 'validate')
                
            else:
                # Generic document assessment
                analysis = self.perform_generic_assessment(doc)
            
            # Consolidate results
            validation_result.update(analysis)
            
        except Exception as e:
            self.log_ai_error("ai_validation", doc.doctype, doc.name, str(e))
            validation_result['error'] = str(e)
        
        return validation_result
    
    def handle_validation_results(self, doc, validation_result):
        """Handle AI validation results and apply actions"""
        
        risk_score = validation_result.get('risk_score', 0)
        
        # Block high-risk submissions
        if risk_score >= self.risk_thresholds['block_submission']:
            if not self.check_override_permission(doc, risk_score):
                frappe.throw(
                    title="AI Risk Assessment Block",
                    msg=validation_result.get('personality_response', f'Document blocked due to high risk score: {risk_score}')
                )
        
        # Require additional approval for medium-risk
        elif risk_score >= self.risk_thresholds['require_approval']:
            self.set_approval_requirement(doc, validation_result)
        
        # Show warnings for low-risk
        elif risk_score >= self.risk_thresholds['warning_only']:
            self.add_ai_warnings(doc, validation_result)
        
        # Store AI insights for user display
        self.store_ai_insights(doc, validation_result)
    
    def perform_final_risk_assessment(self, doc):
        """Perform final comprehensive risk assessment"""
        
        final_assessment = {
            'risk_score': 0,
            'final_status': 'approved',
            'critical_findings': [],
            'final_recommendations': [],
            'compliance_status': 'compliant'
        }
        
        # Combine all previous assessments
        previous_assessments = self.get_previous_assessments(doc)
        
        # Perform final checks
        final_checks = self.perform_final_security_checks(doc)
        
        # Evidence validation (if applicable)
        if doc.doctype in ['Expense Claim', 'Material Request']:
            evidence_validation = self.validate_attached_evidence(doc)
            final_assessment['evidence_validation'] = evidence_validation
        
        # Calculate final risk score
        final_assessment['risk_score'] = self.calculate_final_risk_score(
            previous_assessments, final_checks, final_assessment.get('evidence_validation')
        )
        
        # Generate final personality response
        final_assessment['personality_response'] = self.generate_final_ai_response(
            doc, final_assessment
        )
        
        return final_assessment
    
    def assess_submission_risk(self, doc):
        """Final risk assessment at submission"""
        
        submission_assessment = {
            'block_submission': False,
            'require_additional_approval': False,
            'submission_warnings': [],
            'post_submission_tasks': []
        }
        
        # Check for last-minute risk factors
        if doc.doctype == 'Payment Entry':
            # Cash flow impact check
            cash_flow_check = self.check_final_cash_flow_impact(doc)
            if cash_flow_check.get('critical_impact'):
                submission_assessment['block_submission'] = True
                submission_assessment['message'] = cash_flow_check.get('message')
        
        elif doc.doctype == 'Purchase Invoice':
            # Final fraud check
            fraud_check = self.perform_final_fraud_check(doc)
            if fraud_check.get('high_risk'):
                submission_assessment['block_submission'] = True
                submission_assessment['message'] = fraud_check.get('message')
        
        # Schedule post-submission accountability tasks
        if doc.doctype in ['Expense Claim', 'Material Request']:
            submission_assessment['post_submission_tasks'] = self.schedule_accountability_tasks(doc)
        
        return submission_assessment
    
    def create_ai_assessment_log(self, doc, action):
        """Create AI assessment log entry"""
        
        try:
            ai_log = frappe.get_doc({
                'doctype': 'AI Risk Assessment Log',
                'document_type': doc.doctype,
                'document_name': doc.name,
                'action': action,
                'assessment_timestamp': nowdate(),
                'user': frappe.session.user,
                'company': getattr(doc, 'company', frappe.defaults.get_user_default('Company')),
                'risk_score': getattr(doc, 'ai_risk_score', 0),
                'assessment_data': getattr(doc, 'ai_assessment_data', '{}'),
                'status': 'completed'
            })
            
            ai_log.insert(ignore_permissions=True)
            frappe.db.commit()
            
        except Exception as e:
            self.log_ai_error("create_assessment_log", doc.doctype, doc.name, str(e))
    
    def schedule_ai_followup_tasks(self, doc):
        """Schedule AI-driven follow-up tasks"""
        
        # Material Request follow-up
        if doc.doctype == 'Material Request':
            # Schedule usage follow-up based on material value
            total_value = getattr(doc, 'total_estimated_cost', 0)
            
            if total_value > 100000:  # 100k UGX threshold
                followup_date = add_days(nowdate(), 30)  # 30 days follow-up
                
                self.create_followup_task({
                    'task_type': 'material_usage_followup',
                    'reference_doctype': doc.doctype,
                    'reference_name': doc.name,
                    'assigned_to': getattr(doc, 'requested_by', frappe.session.user),
                    'due_date': followup_date,
                    'description': f'Provide usage report for material request {doc.name} worth {total_value:,.0f} UGX'
                })
        
        # Expense Claim follow-up
        elif doc.doctype == 'Expense Claim':
            total_amount = getattr(doc, 'total_claimed_amount', 0)
            
            if total_amount > 50000:  # 50k UGX threshold
                followup_date = add_days(nowdate(), 14)  # 14 days follow-up
                
                self.create_followup_task({
                    'task_type': 'expense_evidence_followup',
                    'reference_doctype': doc.doctype,
                    'reference_name': doc.name,
                    'assigned_to': getattr(doc, 'employee', frappe.session.user),
                    'due_date': followup_date,
                    'description': f'Submit evidence/outcome report for expense claim {doc.name} worth {total_amount:,.0f} UGX'
                })
    
    def trigger_post_submission_processes(self, doc):
        """Trigger AI processes after successful submission"""
        
        # Update predictive models with new data
        if doc.doctype in ['Purchase Invoice', 'Sales Invoice']:
            self.update_predictive_models(doc)
        
        # Update supplier performance data
        if doc.doctype == 'Purchase Invoice':
            self.update_supplier_performance_data(doc)
        
        # Update customer payment behavior data
        if doc.doctype == 'Sales Invoice':
            self.update_customer_behavior_data(doc)
        
        # Update market intelligence
        if doc.doctype in ['Purchase Invoice', 'Material Request']:
            self.update_market_intelligence(doc)
    
    def store_risk_assessment(self, doc, assessment):
        """Store risk assessment data in document"""
        
        if hasattr(doc, 'set'):
            doc.set('ai_risk_score', assessment.get('risk_score', 0))
            doc.set('ai_risk_level', assessment.get('risk_level', 'low'))
            doc.set('ai_assessment_data', json.dumps(assessment, default=str))
            doc.set('ai_assessment_timestamp', nowdate())
    
    def validate_attached_evidence(self, doc):
        """Validate attached evidence using AI"""
        
        evidence_validation = {
            'validation_status': 'pending',
            'evidence_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        try:
            # Get attached files
            attachments = frappe.get_all('File',
                filters={
                    'attached_to_doctype': doc.doctype,
                    'attached_to_name': doc.name
                },
                fields=['name', 'file_name', 'file_url']
            )
            
            if attachments:
                # Prepare evidence files for validation
                evidence_files = []
                for attachment in attachments:
                    evidence_files.append({
                        'file_name': attachment.file_name,
                        'file_url': attachment.file_url
                    })
                
                # Validate evidence using AI
                validator = EvidenceValidationSystem()
                validation_result = validator.validate_evidence_submission(
                    doc.doctype, doc.name, evidence_files
                )
                
                evidence_validation.update(validation_result)
            else:
                # No evidence attached
                if doc.doctype == 'Expense Claim':
                    total_amount = getattr(doc, 'total_claimed_amount', 0)
                    if total_amount > 50000:  # 50k UGX requires evidence
                        evidence_validation['validation_status'] = 'rejected'
                        evidence_validation['findings'].append('No supporting evidence attached for high-value expense claim')
                
        except Exception as e:
            self.log_ai_error("evidence_validation", doc.doctype, doc.name, str(e))
            evidence_validation['error'] = str(e)
        
        return evidence_validation
    
    # Helper methods
    
    def check_user_accountability(self, user):
        """Check user accountability status"""
        # This would integrate with accountability tracking
        return {'requires_followup': False, 'pending_followups': []}
    
    def check_material_accountability(self, requested_by):
        """Check material request accountability"""
        intelligence = MaterialRequestIntelligence()
        mock_doc = frappe._dict({'requested_by': requested_by})
        return intelligence.check_material_accountability(mock_doc)
    
    def check_expense_accountability(self, employee):
        """Check expense claim accountability"""
        intelligence = ExpenseClaimIntelligence()
        mock_doc = frappe._dict({'employee': employee})
        return intelligence.check_previous_expense_accountability(mock_doc)
    
    def check_override_permission(self, doc, risk_score):
        """Check if user has permission to override AI blocks"""
        user_roles = frappe.get_roles(frappe.session.user)
        
        # High-level roles can override AI blocks
        override_roles = ['System Manager', 'AI Risk Override', 'Administrator']
        return any(role in user_roles for role in override_roles)
    
    def set_approval_requirement(self, doc, validation_result):
        """Set additional approval requirements"""
        if hasattr(doc, 'set'):
            doc.set('requires_ai_approval', 1)
            doc.set('ai_approval_reason', validation_result.get('personality_response', 'Additional approval required due to AI risk assessment'))
    
    def add_ai_warnings(self, doc, validation_result):
        """Add AI warnings to document"""
        warnings = validation_result.get('warnings', [])
        if warnings and hasattr(doc, 'set'):
            doc.set('ai_warnings', json.dumps(warnings))
    
    def store_ai_insights(self, doc, validation_result):
        """Store AI insights for user display"""
        if hasattr(doc, 'set'):
            insights = {
                'recommendations': validation_result.get('recommendations', []),
                'findings': validation_result.get('findings', []),
                'personality_response': validation_result.get('personality_response', ''),
                'market_insights': validation_result.get('market_insights', {})
            }
            doc.set('ai_insights', json.dumps(insights, default=str))
    
    def log_ai_error(self, hook_point, doctype, docname, error_message):
        """Log AI-related errors"""
        frappe.log_error(
            title=f"AI Hook Error - {hook_point}",
            message=f"Doctype: {doctype}\nDocument: {docname}\nError: {error_message}",
            reference_doctype=doctype,
            reference_name=docname
        )
    
    def create_followup_task(self, task_data):
        """Create accountability follow-up task"""
        try:
            task = frappe.get_doc({
                'doctype': 'AI Followup Task',
                'task_type': task_data['task_type'],
                'reference_doctype': task_data['reference_doctype'],
                'reference_name': task_data['reference_name'],
                'assigned_to': task_data['assigned_to'],
                'due_date': task_data['due_date'],
                'description': task_data['description'],
                'status': 'Open',
                'priority': 'Medium'
            })
            
            task.insert(ignore_permissions=True)
            frappe.db.commit()
            
        except Exception as e:
            frappe.log_error(f"Followup Task Creation Error: {str(e)}", "AI Hooks")

    def get_previous_assessments(self, doc):
        """Get previous AI assessments for the document"""
        try:
            # Get assessment data stored in the document
            assessment_data = getattr(doc, 'ai_assessment_data', '{}')
            
            if isinstance(assessment_data, str):
                try:
                    assessment_data = json.loads(assessment_data)
                except (json.JSONDecodeError, ValueError):
                    assessment_data = {}
            
            # Get historical assessments from AI Assessment Log if it exists
            historical_assessments = []
            try:
                historical_assessments = frappe.get_all('AI Risk Assessment Log',
                    filters={
                        'document_type': doc.doctype,
                        'document_name': doc.name
                    },
                    fields=['name', 'assessment_timestamp', 'risk_score', 'assessment_data', 'action'],
                    order_by='assessment_timestamp desc',
                    limit=5
                )
            except frappe.DoesNotExistError:
                # AI Risk Assessment Log DocType doesn't exist yet
                pass
            
            return {
                'current_assessment': assessment_data,
                'historical_assessments': historical_assessments,
                'assessment_count': len(historical_assessments)
            }
            
        except Exception as e:
            frappe.log_error(f"Get Previous Assessments Error: {str(e)}", "AI Hooks")
            return {'current_assessment': {}, 'historical_assessments': [], 'assessment_count': 0}

    def update_ai_assessment_log(self, doc, action, assessment_data=None):
        """Update AI assessment log with new assessment data"""
        try:
            # Prepare assessment data
            if not assessment_data:
                assessment_data = {
                    'risk_score': getattr(doc, 'ai_risk_score', 0),
                    'risk_level': getattr(doc, 'ai_risk_level', 'low'),
                    'action': action,
                    'timestamp': nowdate()
                }
            
            # Try to create log entry in AI Risk Assessment Log
            try:
                ai_log = frappe.get_doc({
                    'doctype': 'AI Risk Assessment Log',
                    'document_type': doc.doctype,
                    'document_name': doc.name,
                    'action': action,
                    'assessment_timestamp': nowdate(),
                    'user': frappe.session.user,
                    'company': getattr(doc, 'company', frappe.defaults.get_user_default('Company')),
                    'risk_score': assessment_data.get('risk_score', 0),
                    'assessment_data': json.dumps(assessment_data, default=str),
                    'status': 'completed'
                })
                
                ai_log.insert(ignore_permissions=True)
                frappe.db.commit()
                
            except frappe.DoesNotExistError:
                # AI Risk Assessment Log DocType doesn't exist, log to Error Log instead
                frappe.log_error(
                    title=f"AI Assessment Update - {action}",
                    message=f"Document: {doc.doctype} - {doc.name}\nAction: {action}\nAssessment: {json.dumps(assessment_data, default=str)}",
                    reference_doctype=doc.doctype,
                    reference_name=doc.name
                )
            
            # Update document with latest assessment
            if hasattr(doc, 'set'):
                doc.set('ai_last_assessment_action', action)
                doc.set('ai_last_assessment_timestamp', nowdate())
                
        except Exception as e:
            frappe.log_error(f"Update AI Assessment Log Error: {str(e)}", "AI Hooks")

    def perform_final_security_checks(self, doc):
        """Perform final security checks before saving/submitting"""
        security_checks = {
            'security_score': 0,
            'security_status': 'passed',
            'security_findings': [],
            'recommendations': []
        }
        
        try:
            # Check for unusual amounts
            if hasattr(doc, 'grand_total') and doc.grand_total:
                if doc.grand_total > 10000000:  # 10M UGX threshold
                    security_checks['security_score'] += 30
                    security_checks['security_findings'].append('High value transaction requiring additional scrutiny')
            
            # Check for weekend/off-hours submissions
            import datetime
            now = datetime.datetime.now()
            if now.weekday() >= 5 or now.hour < 8 or now.hour > 18:  # Weekend or off-hours
                security_checks['security_score'] += 10
                security_checks['security_findings'].append('Document submitted outside normal business hours')
            
            # Check user permissions and roles
            user_roles = frappe.get_roles(frappe.session.user)
            if not any(role in user_roles for role in ['System Manager', 'Accounts Manager', 'Sales Manager']):
                if hasattr(doc, 'grand_total') and doc.grand_total and doc.grand_total > 1000000:  # 1M UGX
                    security_checks['security_score'] += 20
                    security_checks['security_findings'].append('High value transaction by non-manager user')
            
            # Set final security status
            if security_checks['security_score'] >= 50:
                security_checks['security_status'] = 'failed'
            elif security_checks['security_score'] >= 30:
                security_checks['security_status'] = 'warning'
            
        except Exception as e:
            frappe.log_error(f"Security Checks Error: {str(e)}", "AI Security")
            security_checks['error'] = str(e)
        
        return security_checks

    def calculate_final_risk_score(self, previous_assessments, final_checks, evidence_validation=None):
        """Calculate final risk score based on all assessments"""
        try:
            base_risk = 0
            
            # Previous assessments risk
            if previous_assessments and previous_assessments.get('current_assessment'):
                base_risk = previous_assessments['current_assessment'].get('risk_score', 0)
            
            # Security checks risk
            if final_checks:
                base_risk += final_checks.get('security_score', 0)
            
            # Evidence validation risk
            if evidence_validation:
                evidence_score = evidence_validation.get('evidence_score', 0)
                if evidence_score < 50:  # Poor evidence quality
                    base_risk += 25
            
            # Cap at 100
            return min(base_risk, 100)
            
        except Exception as e:
            frappe.log_error(f"Risk Score Calculation Error: {str(e)}", "AI Risk")
            return 0

    def generate_final_ai_response(self, doc, final_assessment):
        """Generate final AI personality response"""
        try:
            risk_score = final_assessment.get('risk_score', 0)
            
            if risk_score >= 85:
                return f"⚠️ CRITICAL RISK DETECTED: This {doc.doctype} has a very high risk score of {risk_score}. Immediate review required before proceeding."
            elif risk_score >= 60:
                return f"🔍 HIGH RISK: This {doc.doctype} requires additional approval (Risk Score: {risk_score}). Please review carefully."
            elif risk_score >= 30:
                return f"⚡ MEDIUM RISK: This {doc.doctype} shows some risk indicators (Risk Score: {risk_score}). Consider review."
            else:
                return f"✅ LOW RISK: This {doc.doctype} appears normal (Risk Score: {risk_score}). Proceed with confidence."
                
        except Exception as e:
            frappe.log_error(f"AI Response Generation Error: {str(e)}", "AI Response")
            return "AI assessment completed with no specific recommendations."

    def check_final_cash_flow_impact(self, doc):
        """Check final cash flow impact for payment entries"""
        impact_check = {
            'critical_impact': False,
            'impact_level': 'low',
            'message': ''
        }
        
        try:
            if doc.doctype == 'Payment Entry' and hasattr(doc, 'paid_amount'):
                # Get current bank balance
                if hasattr(doc, 'paid_from') and doc.paid_from:
                    balance = frappe.db.sql("""
                        SELECT SUM(debit - credit) as balance
                        FROM `tabGL Entry`
                        WHERE account = %s
                        AND is_cancelled = 0
                        AND docstatus = 1
                    """, (doc.paid_from,))[0][0] or 0
                    
                    # Check if payment would cause overdraft
                    if balance - doc.paid_amount < 0:
                        impact_check['critical_impact'] = True
                        impact_check['impact_level'] = 'critical'
                        impact_check['message'] = f"Payment would cause overdraft. Current balance: {balance:,.0f}, Payment: {doc.paid_amount:,.0f}"
                    elif balance - doc.paid_amount < 100000:  # 100k UGX minimum
                        impact_check['impact_level'] = 'high'
                        impact_check['message'] = f"Payment would leave very low balance: {balance - doc.paid_amount:,.0f}"
                        
        except Exception as e:
            frappe.log_error(f"Cash Flow Impact Check Error: {str(e)}", "AI Cash Flow")
        
        return impact_check

    def perform_final_fraud_check(self, doc):
        """Perform final fraud detection checks"""
        fraud_check = {
            'high_risk': False,
            'fraud_score': 0,
            'indicators': [],
            'message': ''
        }
        
        try:
            if doc.doctype == 'Purchase Invoice':
                # Check for duplicate suppliers
                if hasattr(doc, 'supplier') and doc.supplier:
                    recent_invoices = frappe.db.count('Purchase Invoice', {
                        'supplier': doc.supplier,
                        'posting_date': ['>=', add_days(nowdate(), -7)],
                        'docstatus': 1
                    })
                    
                    if recent_invoices > 5:  # More than 5 invoices in a week
                        fraud_check['fraud_score'] += 30
                        fraud_check['indicators'].append('Unusual frequency of invoices from supplier')
                
                # Check for round numbers (potential fraud indicator)
                if hasattr(doc, 'grand_total') and doc.grand_total:
                    if doc.grand_total % 100000 == 0:  # Exact multiples of 100k
                        fraud_check['fraud_score'] += 15
                        fraud_check['indicators'].append('Round number amounts can indicate fraud')
            
            # Set final fraud status
            if fraud_check['fraud_score'] >= 50:
                fraud_check['high_risk'] = True
                fraud_check['message'] = f"High fraud risk detected (Score: {fraud_check['fraud_score']}). Manual review required."
                
        except Exception as e:
            frappe.log_error(f"Fraud Check Error: {str(e)}", "AI Fraud")
        
        return fraud_check

    def schedule_accountability_tasks(self, doc):
        """Schedule accountability tasks based on document type and value"""
        tasks = []
        
        try:
            if doc.doctype == 'Material Request':
                if hasattr(doc, 'total_estimated_cost') and doc.total_estimated_cost > 100000:
                    tasks.append({
                        'type': 'material_usage_followup',
                        'due_date': add_days(nowdate(), 30),
                        'description': f'Material usage accountability report required for {doc.name}'
                    })
            
            elif doc.doctype == 'Expense Claim':
                if hasattr(doc, 'total_claimed_amount') and doc.total_claimed_amount > 50000:
                    tasks.append({
                        'type': 'expense_evidence_followup',
                        'due_date': add_days(nowdate(), 14),
                        'description': f'Expense evidence and outcome report required for {doc.name}'
                    })
            
            elif doc.doctype == 'Purchase Invoice':
                if hasattr(doc, 'grand_total') and doc.grand_total > 500000:
                    tasks.append({
                        'type': 'purchase_verification_followup',
                        'due_date': add_days(nowdate(), 21),
                        'description': f'Purchase verification and delivery confirmation required for {doc.name}'
                    })
                    
        except Exception as e:
            frappe.log_error(f"Accountability Tasks Error: {str(e)}", "AI Accountability")
        
        return tasks

    def perform_generic_assessment(self, doc):
        """Perform generic AI assessment for documents without specific intelligence modules"""
        assessment = {
            'risk_score': 0,
            'validation_status': 'approved',
            'findings': [],
            'recommendations': [],
            'personality_response': '',
            'detailed_analysis': {}
        }
        
        try:
            # Basic risk assessment based on common fields
            if hasattr(doc, 'grand_total') and doc.grand_total:
                if doc.grand_total > 5000000:  # 5M UGX
                    assessment['risk_score'] += 25
                    assessment['findings'].append('High value transaction')
                    assessment['recommendations'].append('Consider additional approval workflow')
            
            # Check for required fields completion
            required_fields = ['company']
            if doc.doctype in ['Sales Invoice', 'Purchase Invoice']:
                required_fields.extend(['customer' if doc.doctype == 'Sales Invoice' else 'supplier'])
            
            missing_fields = [field for field in required_fields if not getattr(doc, field, None)]
            if missing_fields:
                assessment['risk_score'] += 10
                assessment['findings'].append(f'Missing required fields: {", ".join(missing_fields)}')
            
            # Generate personality response
            if assessment['risk_score'] >= 30:
                assessment['personality_response'] = f"This {doc.doctype} requires attention due to risk indicators."
            else:
                assessment['personality_response'] = f"This {doc.doctype} appears to be in good order."
                
        except Exception as e:
            frappe.log_error(f"Generic Assessment Error: {str(e)}", "AI Generic")
            assessment['error'] = str(e)
        
        return assessment

    def update_accountability_tracking(self, doc, status):
        """Update accountability tracking"""
        try:
            # This would update accountability tracking systems
            frappe.log_error(
                title="Accountability Update",
                message=f"Document: {doc.doctype} - {doc.name}\nStatus: {status}",
                reference_doctype=doc.doctype,
                reference_name=doc.name
            )
        except Exception as e:
            frappe.log_error(f"Accountability Tracking Error: {str(e)}", "AI Accountability")

    def update_predictive_models(self, doc):
        """Update predictive models with new data"""
        try:
            # This would update ML models with new transaction data
            pass
        except Exception as e:
            frappe.log_error(f"Predictive Model Update Error: {str(e)}", "AI Predictive")

    def update_supplier_performance_data(self, doc):
        """Update supplier performance data"""
        try:
            # This would update supplier performance metrics
            pass
        except Exception as e:
            frappe.log_error(f"Supplier Performance Update Error: {str(e)}", "AI Supplier")

    def update_customer_behavior_data(self, doc):
        """Update customer behavior data"""
        try:
            # This would update customer behavior analytics
            pass
        except Exception as e:
            frappe.log_error(f"Customer Behavior Update Error: {str(e)}", "AI Customer")

    def update_market_intelligence(self, doc):
        """Update market intelligence data"""
        try:
            # This would update market intelligence systems
            pass
        except Exception as e:
            frappe.log_error(f"Market Intelligence Update Error: {str(e)}", "AI Market")


# Global hook wrapper functions for frappe document events

def ai_before_insert(doc, method):
    """Global before_insert hook wrapper"""
    try:
        hooks = AIRiskAssessmentHooks()
        hooks.before_insert(doc, method)
    except Exception as e:
        frappe.log_error(f"AI Before Insert Hook Error: {str(e)}", "AI Hooks")

def ai_validate(doc, method):
    """Global validate hook wrapper"""
    try:
        hooks = AIRiskAssessmentHooks()
        hooks.validate(doc, method)
    except Exception as e:
        frappe.log_error(f"AI Validate Hook Error: {str(e)}", "AI Hooks")

def ai_before_save(doc, method):
    """Global before_save hook wrapper"""
    try:
        hooks = AIRiskAssessmentHooks()
        hooks.before_save(doc, method)
    except Exception as e:
        frappe.log_error(f"AI Before Save Hook Error: {str(e)}", "AI Hooks")

def ai_after_insert(doc, method):
    """Global after_insert hook wrapper"""
    try:
        hooks = AIRiskAssessmentHooks()
        hooks.after_insert(doc, method)
    except Exception as e:
        frappe.log_error(f"AI After Insert Hook Error: {str(e)}", "AI Hooks")

def ai_on_submit(doc, method):
    """Global on_submit hook wrapper"""
    try:
        hooks = AIRiskAssessmentHooks()
        hooks.on_submit(doc, method)
    except Exception as e:
        frappe.log_error(f"AI On Submit Hook Error: {str(e)}", "AI Hooks")

def ai_on_cancel(doc, method):
    """Global on_cancel hook wrapper"""
    try:
        hooks = AIRiskAssessmentHooks()
        hooks.on_cancel(doc, method)
    except Exception as e:
        frappe.log_error(f"AI On Cancel Hook Error: {str(e)}", "AI Hooks")


# Frappe whitelisted methods for manual AI assessment

@frappe.whitelist()
def trigger_manual_ai_assessment(doctype, doc_name):
    """Manually trigger AI assessment for a document"""
    try:
        doc = frappe.get_doc(doctype, doc_name)
        hooks = AIRiskAssessmentHooks()
        
        assessment = hooks.perform_ai_validation(doc)
        
        # Store assessment results
        hooks.store_risk_assessment(doc, assessment)
        doc.save(ignore_permissions=True)
        
        return assessment
        
    except Exception as e:
        frappe.log_error(f"Manual AI Assessment Error: {str(e)}", "AI Hooks")
        return {'error': str(e)}

@frappe.whitelist()
def get_ai_insights(doctype, doc_name):
    """Get AI insights for a document"""
    try:
        doc = frappe.get_doc(doctype, doc_name)
        
        insights = {
            'risk_score': getattr(doc, 'ai_risk_score', 0),
            'risk_level': getattr(doc, 'ai_risk_level', 'unknown'),
            'assessment_data': getattr(doc, 'ai_assessment_data', '{}'),
            'insights': getattr(doc, 'ai_insights', '{}'),
            'warnings': getattr(doc, 'ai_warnings', '[]')
        }
        
        # Parse JSON fields
        for field in ['assessment_data', 'insights', 'warnings']:
            if insights[field]:
                try:
                    insights[field] = json.loads(insights[field])
                except:
                    pass
        
        return insights
        
    except Exception as e:
        frappe.log_error(f"Get AI Insights Error: {str(e)}", "AI Hooks")
        return {'error': str(e)}

@frappe.whitelist()
def override_ai_block(doctype, doc_name, override_reason):
    """Override AI block with proper authorization"""
    try:
        # Check override permissions
        hooks = AIRiskAssessmentHooks()
        if not hooks.check_override_permission(None, 100):  # Max risk score for permission check
            frappe.throw("You don't have permission to override AI blocks")
        
        doc = frappe.get_doc(doctype, doc_name)
        
        # Log override action
        override_log = frappe.get_doc({
            'doctype': 'AI Override Log',
            'document_type': doctype,
            'document_name': doc_name,
            'override_user': frappe.session.user,
            'override_reason': override_reason,
            'override_timestamp': nowdate(),
            'original_risk_score': getattr(doc, 'ai_risk_score', 0)
        })
        
        override_log.insert(ignore_permissions=True)
        
        # Set override flag
        doc.set('ai_override_approved', 1)
        doc.set('ai_override_user', frappe.session.user)
        doc.set('ai_override_reason', override_reason)
        doc.save(ignore_permissions=True)
        
        return {'success': True, 'message': 'AI block override approved'}
        
    except Exception as e:
        frappe.log_error(f"AI Override Error: {str(e)}", "AI Hooks")
        return {'error': str(e)} 