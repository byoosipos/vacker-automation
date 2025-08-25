# Copyright (c) 2025, Vacker and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe.utils import nowdate, cstr


class AIRiskAssessmentLog(Document):
    def before_insert(self):
        """Set default values before inserting"""
        if not self.assessment_timestamp:
            self.assessment_timestamp = nowdate()
        
        if not self.user:
            self.user = frappe.session.user
        
        if not self.company:
            self.company = frappe.defaults.get_user_default('Company')
        
        if not self.status:
            self.status = 'completed'
    
    def validate(self):
        """Validate the assessment log entry"""
        # Ensure risk score is within valid range
        if self.risk_score and (self.risk_score < 0 or self.risk_score > 100):
            frappe.throw("Risk Score must be between 0 and 100")
        
        # Set risk level based on risk score if not provided
        if self.risk_score and not self.risk_level:
            if self.risk_score >= 85:
                self.risk_level = 'critical'
            elif self.risk_score >= 60:
                self.risk_level = 'high'
            elif self.risk_score >= 30:
                self.risk_level = 'medium'
            else:
                self.risk_level = 'low'
        
        # Validate assessment_data is valid JSON if provided
        if self.assessment_data:
            try:
                json.loads(self.assessment_data)
            except (json.JSONDecodeError, ValueError):
                frappe.throw("Assessment Data must be valid JSON")
    
    def get_assessment_summary(self):
        """Get a summary of the assessment"""
        summary = {
            'document': f"{self.document_type} - {self.document_name}",
            'action': self.action,
            'risk_score': self.risk_score or 0,
            'risk_level': self.risk_level or 'unknown',
            'timestamp': self.assessment_timestamp,
            'user': self.user,
            'status': self.status
        }
        
        # Parse assessment data if available
        if self.assessment_data:
            try:
                assessment_details = json.loads(self.assessment_data)
                summary['details'] = assessment_details
            except (json.JSONDecodeError, ValueError):
                summary['details'] = {}
        
        return summary


@frappe.whitelist()
def get_assessment_history(document_type, document_name, limit=10):
    """Get assessment history for a document"""
    try:
        assessments = frappe.get_all('AI Risk Assessment Log',
            filters={
                'document_type': document_type,
                'document_name': document_name
            },
            fields=[
                'name', 'action', 'assessment_timestamp', 'risk_score', 
                'risk_level', 'status', 'user', 'assessment_data'
            ],
            order_by='assessment_timestamp desc',
            limit=limit
        )
        
        # Parse assessment data for each entry
        for assessment in assessments:
            if assessment.get('assessment_data'):
                try:
                    assessment['parsed_data'] = json.loads(assessment['assessment_data'])
                except (json.JSONDecodeError, ValueError):
                    assessment['parsed_data'] = {}
        
        return assessments
        
    except Exception as e:
        frappe.log_error(f"Assessment History Error: {str(e)}", "AI Assessment Log")
        return []


@frappe.whitelist()
def get_risk_analytics(company=None, from_date=None, to_date=None):
    """Get risk analytics from assessment logs"""
    try:
        filters = {}
        if company:
            filters['company'] = company
        if from_date and to_date:
            filters['assessment_timestamp'] = ['between', [from_date, to_date]]
        
        # Risk level distribution
        risk_distribution = frappe.db.sql("""
            SELECT 
                risk_level,
                COUNT(*) as count,
                AVG(risk_score) as avg_score
            FROM `tabAI Risk Assessment Log`
            WHERE company = %(company)s
            AND assessment_timestamp BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY risk_level
            ORDER BY avg_score DESC
        """, {
            'company': company or frappe.defaults.get_user_default('Company'),
            'from_date': from_date or frappe.utils.add_days(nowdate(), -30),
            'to_date': to_date or nowdate()
        }, as_dict=True)
        
        # Document type risk analysis
        document_risk_analysis = frappe.db.sql("""
            SELECT 
                document_type,
                COUNT(*) as total_assessments,
                AVG(risk_score) as avg_risk_score,
                MAX(risk_score) as max_risk_score,
                COUNT(CASE WHEN risk_level IN ('high', 'critical') THEN 1 END) as high_risk_count
            FROM `tabAI Risk Assessment Log`
            WHERE company = %(company)s
            AND assessment_timestamp BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY document_type
            ORDER BY avg_risk_score DESC
        """, {
            'company': company or frappe.defaults.get_user_default('Company'),
            'from_date': from_date or frappe.utils.add_days(nowdate(), -30),
            'to_date': to_date or nowdate()
        }, as_dict=True)
        
        # User activity analysis
        user_activity = frappe.db.sql("""
            SELECT 
                user,
                COUNT(*) as assessment_count,
                AVG(risk_score) as avg_risk_triggered,
                COUNT(CASE WHEN risk_level IN ('high', 'critical') THEN 1 END) as high_risk_triggers
            FROM `tabAI Risk Assessment Log`
            WHERE company = %(company)s
            AND assessment_timestamp BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY user
            ORDER BY high_risk_triggers DESC, avg_risk_triggered DESC
            LIMIT 10
        """, {
            'company': company or frappe.defaults.get_user_default('Company'),
            'from_date': from_date or frappe.utils.add_days(nowdate(), -30),
            'to_date': to_date or nowdate()
        }, as_dict=True)
        
        return {
            'risk_distribution': risk_distribution,
            'document_analysis': document_risk_analysis,
            'user_activity': user_activity,
            'summary': {
                'total_assessments': sum([d['count'] for d in risk_distribution]),
                'avg_risk_score': sum([d['avg_score'] * d['count'] for d in risk_distribution]) / sum([d['count'] for d in risk_distribution]) if risk_distribution else 0,
                'high_risk_percentage': (sum([d['count'] for d in risk_distribution if d['risk_level'] in ['high', 'critical']]) / sum([d['count'] for d in risk_distribution]) * 100) if risk_distribution else 0
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Risk Analytics Error: {str(e)}", "AI Assessment Log")
        return {'error': str(e)}


@frappe.whitelist()
def create_manual_assessment(document_type, document_name, notes=None):
    """Create a manual AI assessment log entry"""
    try:
        # Get the document
        doc = frappe.get_doc(document_type, document_name)
        
        # Create assessment log
        assessment_log = frappe.get_doc({
            'doctype': 'AI Risk Assessment Log',
            'document_type': document_type,
            'document_name': document_name,
            'action': 'manual_assessment',
            'assessment_timestamp': nowdate(),
            'user': frappe.session.user,
            'company': getattr(doc, 'company', frappe.defaults.get_user_default('Company')),
            'risk_score': getattr(doc, 'ai_risk_score', 0),
            'risk_level': getattr(doc, 'ai_risk_level', 'low'),
            'assessment_data': getattr(doc, 'ai_assessment_data', '{}'),
            'status': 'completed',
            'notes': notes or 'Manual assessment triggered by user'
        })
        
        assessment_log.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {'success': True, 'assessment_log': assessment_log.name}
        
    except Exception as e:
        frappe.log_error(f"Manual Assessment Error: {str(e)}", "AI Assessment Log")
        return {'error': str(e)} 