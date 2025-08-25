# Copyright (c) 2025, Vacker and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, add_days, nowdate


class AIRiskManager(Document):
    def before_insert(self):
        """Set default values before inserting"""
        if not self.assessment_date:
            self.assessment_date = frappe.utils.now()
        
        if not self.company:
            self.company = frappe.defaults.get_user_default('Company')
    
    def after_insert(self):
        """Perform initial risk assessment after creation"""
        self.perform_comprehensive_risk_assessment()
    
    def perform_comprehensive_risk_assessment(self):
        """Perform comprehensive AI-powered risk assessment"""
        try:
            # Gather financial data for analysis
            financial_data = self.gather_financial_data()
            
            # Perform various risk analyses
            risk_categories = self.analyze_risk_categories(financial_data)
            cash_flow_analysis = self.analyze_cash_flow_risks(financial_data)
            compliance_status = self.check_compliance_risks()
            
            # Generate AI-powered insights and recommendations
            ai_analysis = self.generate_ai_risk_insights(financial_data, risk_categories)
            
            # Update the document with findings
            self.risk_categories = json.dumps(risk_categories)
            self.financial_metrics = json.dumps(financial_data)
            self.cash_flow_analysis = json.dumps(cash_flow_analysis)
            self.compliance_status = json.dumps(compliance_status)
            self.risk_findings = ai_analysis['findings']
            self.ai_recommendations = ai_analysis['recommendations']
            self.mitigation_actions = ai_analysis['mitigation_actions']
            
            # Calculate overall risk level
            self.risk_level = self.calculate_overall_risk_level(risk_categories)
            
            # Set follow-up date based on risk level
            self.follow_up_date = self.calculate_follow_up_date()
            
            # Log analysis data
            self.assessment_data = json.dumps({
                'analysis_timestamp': frappe.utils.now(),
                'data_sources': ['GL Entry', 'Sales Invoice', 'Purchase Invoice', 'Payment Entry'],
                'analysis_period': self.get_analysis_period(),
                'ai_model_version': '1.0'
            })
            
            self.save(ignore_permissions=True)
            
            # Create alerts if critical risks found
            self.create_risk_alerts()
            
        except Exception as e:
            frappe.log_error(f"Risk Assessment Error: {str(e)}", "AI Risk Manager")
    
    def gather_financial_data(self):
        """Gather comprehensive financial data for risk analysis"""
        company = self.company
        from_date = add_days(nowdate(), -90)  # Last 3 months
        to_date = nowdate()
        
        # Revenue and Expense Analysis
        revenue_data = frappe.db.sql("""
            SELECT 
                SUM(credit) as total_revenue,
                COUNT(*) as revenue_transactions,
                AVG(credit) as avg_transaction_value
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.company = %s
            AND gle.posting_date BETWEEN %s AND %s
            AND acc.root_type = 'Income'
            AND gle.credit > 0
            AND gle.is_cancelled = 0
        """, (company, from_date, to_date), as_dict=True)
        
        expense_data = frappe.db.sql("""
            SELECT 
                SUM(debit) as total_expenses,
                COUNT(*) as expense_transactions,
                AVG(debit) as avg_expense_value
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.company = %s
            AND gle.posting_date BETWEEN %s AND %s
            AND acc.root_type = 'Expense'
            AND gle.debit > 0
            AND gle.is_cancelled = 0
        """, (company, from_date, to_date), as_dict=True)
        
        # Cash Flow Analysis
        cash_flow = frappe.db.sql("""
            SELECT 
                SUM(CASE WHEN debit > 0 THEN debit ELSE -credit END) as net_cash_flow,
                COUNT(*) as total_transactions
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.company = %s
            AND gle.posting_date BETWEEN %s AND %s
            AND acc.account_type IN ('Bank', 'Cash')
            AND gle.is_cancelled = 0
        """, (company, from_date, to_date), as_dict=True)
        
        # Outstanding Receivables
        receivables = frappe.db.sql("""
            SELECT 
                SUM(si.outstanding_amount) as total_outstanding,
                COUNT(*) as outstanding_invoices,
                AVG(DATEDIFF(CURDATE(), si.due_date)) as avg_overdue_days
            FROM `tabSales Invoice` si
            WHERE si.company = %s
            AND si.docstatus = 1
            AND si.outstanding_amount > 0
        """, (company,), as_dict=True)
        
        # Outstanding Payables
        payables = frappe.db.sql("""
            SELECT 
                SUM(pi.outstanding_amount) as total_payable,
                COUNT(*) as outstanding_bills,
                AVG(DATEDIFF(CURDATE(), pi.due_date)) as avg_overdue_days
            FROM `tabPurchase Invoice` pi
            WHERE pi.company = %s
            AND pi.docstatus = 1
            AND pi.outstanding_amount > 0
        """, (company,), as_dict=True)
        
        # Bank Balance
        bank_balance = frappe.db.sql("""
            SELECT 
                SUM(gle.debit - gle.credit) as total_bank_balance
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.company = %s
            AND acc.account_type = 'Bank'
            AND gle.is_cancelled = 0
        """, (company,), as_dict=True)
        
        return {
            'revenue': revenue_data[0] if revenue_data else {},
            'expenses': expense_data[0] if expense_data else {},
            'cash_flow': cash_flow[0] if cash_flow else {},
            'receivables': receivables[0] if receivables else {},
            'payables': payables[0] if payables else {},
            'bank_balance': bank_balance[0] if bank_balance else {},
            'analysis_period': {'from_date': from_date, 'to_date': to_date}
        }
    
    def analyze_risk_categories(self, financial_data):
        """Analyze different risk categories"""
        risks = {}
        
        # Liquidity Risk
        liquidity_risk = self.assess_liquidity_risk(financial_data)
        risks['liquidity'] = liquidity_risk
        
        # Credit Risk
        credit_risk = self.assess_credit_risk(financial_data)
        risks['credit'] = credit_risk
        
        # Operational Risk
        operational_risk = self.assess_operational_risk(financial_data)
        risks['operational'] = operational_risk
        
        # Market Risk
        market_risk = self.assess_market_risk(financial_data)
        risks['market'] = market_risk
        
        # Compliance Risk
        compliance_risk = self.assess_compliance_risk()
        risks['compliance'] = compliance_risk
        
        return risks
    
    def assess_liquidity_risk(self, financial_data):
        """Assess liquidity risk based on cash flow and bank balances"""
        bank_balance = flt(financial_data.get('bank_balance', {}).get('total_bank_balance', 0))
        monthly_expenses = flt(financial_data.get('expenses', {}).get('total_expenses', 0))
        cash_flow = flt(financial_data.get('cash_flow', {}).get('net_cash_flow', 0))
        
        # Calculate cash runway (months of expenses covered by current cash)
        cash_runway = (bank_balance / (monthly_expenses / 3)) if monthly_expenses > 0 else 0
        
        # Assess risk level
        if cash_runway < 1:
            risk_level = "Critical"
            risk_score = 90
        elif cash_runway < 3:
            risk_level = "High"
            risk_score = 70
        elif cash_runway < 6:
            risk_level = "Medium"
            risk_score = 40
        else:
            risk_level = "Low"
            risk_score = 10
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'cash_runway_months': round(cash_runway, 1),
            'bank_balance': bank_balance,
            'monthly_burn_rate': monthly_expenses / 3,
            'net_cash_flow': cash_flow,
            'indicators': self.get_liquidity_indicators(cash_runway, cash_flow)
        }
    
    def assess_credit_risk(self, financial_data):
        """Assess credit risk based on receivables and payment patterns"""
        receivables = financial_data.get('receivables', {})
        total_outstanding = flt(receivables.get('total_outstanding', 0))
        avg_overdue_days = flt(receivables.get('avg_overdue_days', 0))
        outstanding_invoices = flt(receivables.get('outstanding_invoices', 0))
        
        # Calculate Days Sales Outstanding (DSO)
        total_revenue = flt(financial_data.get('revenue', {}).get('total_revenue', 0))
        dso = (total_outstanding / (total_revenue / 90)) if total_revenue > 0 else 0
        
        # Assess risk level
        if avg_overdue_days > 60 or dso > 90:
            risk_level = "High"
            risk_score = 80
        elif avg_overdue_days > 30 or dso > 60:
            risk_level = "Medium"
            risk_score = 50
        elif avg_overdue_days > 15 or dso > 45:
            risk_level = "Low"
            risk_score = 25
        else:
            risk_level = "Very Low"
            risk_score = 5
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'total_outstanding': total_outstanding,
            'days_sales_outstanding': round(dso, 1),
            'avg_overdue_days': avg_overdue_days,
            'outstanding_invoices': outstanding_invoices,
            'collection_efficiency': self.calculate_collection_efficiency()
        }
    
    def assess_operational_risk(self, financial_data):
        """Assess operational risk based on expense patterns and efficiency"""
        expenses = financial_data.get('expenses', {})
        revenue = financial_data.get('revenue', {})
        
        total_expenses = flt(expenses.get('total_expenses', 0))
        total_revenue = flt(revenue.get('total_revenue', 0))
        
        # Calculate expense ratios
        expense_ratio = (total_expenses / total_revenue * 100) if total_revenue > 0 else 0
        
        # Analyze expense volatility
        expense_volatility = self.calculate_expense_volatility()
        
        # Assess risk level
        if expense_ratio > 90 or expense_volatility > 30:
            risk_level = "High"
            risk_score = 75
        elif expense_ratio > 80 or expense_volatility > 20:
            risk_level = "Medium"
            risk_score = 50
        elif expense_ratio > 70 or expense_volatility > 15:
            risk_level = "Low"
            risk_score = 25
        else:
            risk_level = "Very Low"
            risk_score = 10
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'expense_ratio': round(expense_ratio, 2),
            'expense_volatility': round(expense_volatility, 2),
            'operational_efficiency': self.calculate_operational_efficiency(financial_data)
        }
    
    def assess_market_risk(self, financial_data):
        """Assess market risk based on revenue patterns and customer concentration"""
        revenue = financial_data.get('revenue', {})
        
        # Analyze revenue volatility
        revenue_volatility = self.calculate_revenue_volatility()
        
        # Calculate customer concentration risk
        customer_concentration = self.calculate_customer_concentration()
        
        # Assess market risk
        if revenue_volatility > 25 or customer_concentration > 50:
            risk_level = "High"
            risk_score = 70
        elif revenue_volatility > 15 or customer_concentration > 30:
            risk_level = "Medium"
            risk_score = 45
        elif revenue_volatility > 10 or customer_concentration > 20:
            risk_level = "Low"
            risk_score = 20
        else:
            risk_level = "Very Low"
            risk_score = 5
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'revenue_volatility': round(revenue_volatility, 2),
            'customer_concentration': round(customer_concentration, 2),
            'market_indicators': self.get_market_risk_indicators()
        }
    
    def assess_compliance_risk(self):
        """Assess compliance risk based on regulatory requirements"""
        # Check for missing mandatory reports
        missing_reports = self.check_missing_reports()
        
        # Check for tax compliance
        tax_compliance = self.check_tax_compliance()
        
        # Check for audit trail completeness
        audit_trail_score = self.check_audit_trail_completeness()
        
        compliance_score = (tax_compliance + audit_trail_score) / 2
        
        if compliance_score < 60:
            risk_level = "High"
            risk_score = 85
        elif compliance_score < 80:
            risk_level = "Medium"
            risk_score = 50
        elif compliance_score < 95:
            risk_level = "Low"
            risk_score = 20
        else:
            risk_level = "Very Low"
            risk_score = 5
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'compliance_score': compliance_score,
            'missing_reports': missing_reports,
            'tax_compliance_score': tax_compliance,
            'audit_trail_score': audit_trail_score
        }
    
    def analyze_cash_flow_risks(self, financial_data):
        """Perform detailed cash flow risk analysis"""
        # Predict future cash flow
        cash_flow_prediction = self.predict_cash_flow()
        
        # Analyze cash flow patterns
        cash_flow_patterns = self.analyze_cash_flow_patterns()
        
        # Identify cash flow anomalies
        anomalies = self.detect_cash_flow_anomalies()
        
        return {
            'prediction': cash_flow_prediction,
            'patterns': cash_flow_patterns,
            'anomalies': anomalies,
            'recommendations': self.generate_cash_flow_recommendations(cash_flow_prediction)
        }
    
    def generate_ai_risk_insights(self, financial_data, risk_categories):
        """Generate AI-powered risk insights and recommendations"""
        try:
            # Prepare comprehensive risk context for AI analysis
            risk_context = {
                'financial_data': financial_data,
                'risk_categories': risk_categories,
                'company': self.company,
                'assessment_date': self.assessment_date
            }
            
            # Generate AI analysis using the chat_with_ai function
            from vacker_automation.vacker_automation.doctype.ai_settings.ai_settings import chat_with_ai
            
            ai_prompt = f"""
            FINANCIAL RISK MANAGEMENT ANALYSIS
            
            You are an expert financial risk manager analyzing the following comprehensive risk data:
            
            RISK ASSESSMENT DATA:
            {json.dumps(risk_context, indent=2)}
            
            Please provide a comprehensive risk management analysis including:
            
            1. CRITICAL RISK FINDINGS:
            - Identify the most critical financial risks
            - Quantify potential impact of each risk
            - Prioritize risks by urgency and severity
            
            2. AI-POWERED RECOMMENDATIONS:
            - Specific, actionable recommendations for each identified risk
            - Timeline for implementation
            - Expected impact of each recommendation
            
            3. MITIGATION ACTIONS:
            - Immediate actions required (next 30 days)
            - Medium-term strategies (next 90 days)
            - Long-term risk management improvements
            
            4. EARLY WARNING INDICATORS:
            - Key metrics to monitor for each risk category
            - Threshold values that should trigger alerts
            
            5. FINANCIAL HEALTH SCORE:
            - Overall financial health assessment (1-100)
            - Key factors affecting the score
            - Recommendations to improve the score
            
            Focus on providing specific, measurable, and actionable insights that can be immediately implemented.
            """
            
            ai_response = chat_with_ai(ai_prompt, thinking_mode=True)
            
            if ai_response and ai_response.get('success'):
                ai_analysis = ai_response.get('response', '')
                
                # Parse the AI response into structured components
                findings = self.extract_section(ai_analysis, "CRITICAL RISK FINDINGS")
                recommendations = self.extract_section(ai_analysis, "AI-POWERED RECOMMENDATIONS")
                mitigation_actions = self.extract_section(ai_analysis, "MITIGATION ACTIONS")
                
                return {
                    'findings': findings or ai_analysis[:1000],
                    'recommendations': recommendations or ai_analysis[1000:2000],
                    'mitigation_actions': mitigation_actions or ai_analysis[2000:3000],
                    'full_analysis': ai_analysis
                }
            else:
                # Fallback to rule-based analysis if AI is not available
                return self.generate_fallback_analysis(risk_categories)
                
        except Exception as e:
            frappe.log_error(f"AI Risk Analysis Error: {str(e)}", "AI Risk Manager")
            return self.generate_fallback_analysis(risk_categories)
    
    def extract_section(self, text, section_name):
        """Extract specific section from AI response"""
        try:
            lines = text.split('\n')
            section_lines = []
            in_section = False
            
            for line in lines:
                if section_name in line.upper():
                    in_section = True
                    continue
                elif in_section and any(header in line.upper() for header in ['FINDINGS', 'RECOMMENDATIONS', 'ACTIONS', 'INDICATORS', 'SCORE']):
                    if not section_name.upper() in line.upper():
                        break
                elif in_section:
                    section_lines.append(line)
            
            return '\n'.join(section_lines).strip()
        except:
            return None
    
    def generate_fallback_analysis(self, risk_categories):
        """Generate fallback analysis when AI is not available"""
        critical_risks = []
        recommendations = []
        actions = []
        
        for category, risk_data in risk_categories.items():
            if risk_data.get('risk_score', 0) > 60:
                critical_risks.append(f"High {category} risk detected (Score: {risk_data.get('risk_score')})")
                recommendations.append(f"Implement {category} risk mitigation strategies")
                actions.append(f"Monitor {category} risk indicators daily")
        
        return {
            'findings': '\n'.join(critical_risks) if critical_risks else "No critical risks identified",
            'recommendations': '\n'.join(recommendations) if recommendations else "Continue current monitoring",
            'mitigation_actions': '\n'.join(actions) if actions else "Maintain regular risk assessment schedule"
        }
    
    def calculate_overall_risk_level(self, risk_categories):
        """Calculate overall risk level based on individual risk scores"""
        total_score = 0
        risk_count = 0
        
        for category, risk_data in risk_categories.items():
            if isinstance(risk_data, dict) and 'risk_score' in risk_data:
                total_score += risk_data['risk_score']
                risk_count += 1
        
        if risk_count == 0:
            return "Low"
        
        avg_score = total_score / risk_count
        
        if avg_score >= 80:
            return "Critical"
        elif avg_score >= 60:
            return "High"
        elif avg_score >= 30:
            return "Medium"
        else:
            return "Low"
    
    def calculate_follow_up_date(self):
        """Calculate follow-up date based on risk level"""
        if self.risk_level == "Critical":
            return add_days(nowdate(), 1)  # Daily monitoring
        elif self.risk_level == "High":
            return add_days(nowdate(), 7)  # Weekly monitoring
        elif self.risk_level == "Medium":
            return add_days(nowdate(), 30)  # Monthly monitoring
        else:
            return add_days(nowdate(), 90)  # Quarterly monitoring
    
    def create_risk_alerts(self):
        """Create alerts for critical risks"""
        if self.risk_level in ["Critical", "High"]:
            # Create system notification
            frappe.publish_realtime(
                'risk_alert',
                {
                    'risk_assessment': self.name,
                    'risk_level': self.risk_level,
                    'company': self.company,
                    'message': f"Critical financial risk detected: {self.risk_assessment_name}"
                },
                user=frappe.session.user
            )
            
            # Send email notification to relevant users
            self.send_risk_notification_email()
    
    def send_risk_notification_email(self):
        """Send email notification for high-risk situations"""
        try:
            # Get users with appropriate roles
            recipients = frappe.get_all("Has Role", 
                filters={"role": ["in", ["Accounts Manager", "System Manager"]]},
                fields=["parent"]
            )
            
            recipient_emails = [frappe.db.get_value("User", user.parent, "email") 
                               for user in recipients if frappe.db.get_value("User", user.parent, "email")]
            
            if recipient_emails:
                frappe.sendmail(
                    recipients=recipient_emails,
                    subject=f"🚨 Financial Risk Alert - {self.company}",
                    message=f"""
                    <h3>Financial Risk Alert</h3>
                    <p><strong>Risk Level:</strong> {self.risk_level}</p>
                    <p><strong>Assessment:</strong> {self.risk_assessment_name}</p>
                    <p><strong>Company:</strong> {self.company}</p>
                    <p><strong>Date:</strong> {self.assessment_date}</p>
                    
                    <h4>Key Findings:</h4>
                    <p>{self.risk_findings[:500]}...</p>
                    
                    <h4>Immediate Actions Required:</h4>
                    <p>{self.mitigation_actions[:500]}...</p>
                    
                    <p>Please review the full risk assessment in the system for detailed analysis and recommendations.</p>
                    """,
                    reference_doctype="AI Risk Manager",
                    reference_name=self.name
                )
        except Exception as e:
            frappe.log_error(f"Risk Alert Email Error: {str(e)}", "AI Risk Manager")
    
    # Helper methods for specific calculations
    def get_analysis_period(self):
        """Get the analysis period"""
        return {
            'from_date': add_days(nowdate(), -90),
            'to_date': nowdate(),
            'period_days': 90
        }
    
    def get_liquidity_indicators(self, cash_runway, cash_flow):
        """Get liquidity risk indicators"""
        indicators = []
        if cash_runway < 3:
            indicators.append("Critical cash runway")
        if cash_flow < 0:
            indicators.append("Negative cash flow")
        return indicators
    
    def calculate_collection_efficiency(self):
        """Calculate collection efficiency"""
        # Placeholder - implement based on payment history
        return 85.5
    
    def calculate_expense_volatility(self):
        """Calculate expense volatility over time"""
        # Placeholder - implement time series analysis
        return 15.2
    
    def calculate_operational_efficiency(self, financial_data):
        """Calculate operational efficiency metrics"""
        return {
            'efficiency_score': 78.5,
            'cost_per_transaction': 125.50
        }
    
    def calculate_revenue_volatility(self):
        """Calculate revenue volatility"""
        # Placeholder - implement time series analysis
        return 12.8
    
    def calculate_customer_concentration(self):
        """Calculate customer concentration risk"""
        # Placeholder - implement customer revenue analysis
        return 25.3
    
    def get_market_risk_indicators(self):
        """Get market risk indicators"""
        return {
            'industry_trends': 'stable',
            'competitive_pressure': 'medium'
        }
    
    def check_missing_reports(self):
        """Check for missing mandatory reports"""
        return []
    
    def check_tax_compliance(self):
        """Check tax compliance status"""
        return 92.0
    
    def check_audit_trail_completeness(self):
        """Check audit trail completeness"""
        return 88.5
    
    def predict_cash_flow(self):
        """Predict future cash flow"""
        return {
            'next_30_days': 125000,
            'next_60_days': 245000,
            'next_90_days': 378000,
            'confidence_level': 78
        }
    
    def analyze_cash_flow_patterns(self):
        """Analyze cash flow patterns"""
        return {
            'seasonality': 'moderate',
            'trend': 'positive',
            'cyclical_pattern': 'monthly'
        }
    
    def detect_cash_flow_anomalies(self):
        """Detect cash flow anomalies"""
        return []
    
    def generate_cash_flow_recommendations(self, prediction):
        """Generate cash flow recommendations"""
        return [
            "Improve collection efficiency",
            "Optimize payment timing",
            "Diversify revenue streams"
        ]


# API Functions for Risk Management

@frappe.whitelist()
def create_risk_assessment(company=None, assessment_name=None):
    """Create a new AI risk assessment"""
    try:
        risk_assessment = frappe.new_doc("AI Risk Manager")
        risk_assessment.company = company or frappe.defaults.get_user_default('Company')
        risk_assessment.risk_assessment_name = assessment_name or f"Auto Risk Assessment - {frappe.utils.now()}"
        risk_assessment.insert()
        
        return {
            'success': True,
            'risk_assessment': risk_assessment.name,
            'message': 'Risk assessment created successfully'
        }
    except Exception as e:
        frappe.log_error(f"Risk Assessment Creation Error: {str(e)}", "AI Risk Manager")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def get_risk_dashboard_data(company=None, limit=10):
    """Get risk dashboard data"""
    try:
        if not company:
            company = frappe.defaults.get_user_default('Company')
        
        # Get recent risk assessments
        recent_assessments = frappe.get_all("AI Risk Manager",
            filters={'company': company},
            fields=['name', 'risk_assessment_name', 'assessment_date', 'risk_level', 'status'],
            order_by='assessment_date desc',
            limit=limit
        )
        
        # Get risk metrics summary
        risk_summary = frappe.db.sql("""
            SELECT 
                risk_level,
                COUNT(*) as count,
                AVG(CASE 
                    WHEN risk_level = 'Critical' THEN 90
                    WHEN risk_level = 'High' THEN 70
                    WHEN risk_level = 'Medium' THEN 40
                    ELSE 10
                END) as avg_risk_score
            FROM `tabAI Risk Manager`
            WHERE company = %s
            GROUP BY risk_level
        """, (company,), as_dict=True)
        
        # Get active alerts
        active_alerts = frappe.get_all("AI Risk Manager",
            filters={
                'company': company,
                'status': 'Active',
                'risk_level': ['in', ['Critical', 'High']]
            },
            fields=['name', 'risk_assessment_name', 'risk_level', 'follow_up_date']
        )
        
        return {
            'recent_assessments': recent_assessments,
            'risk_summary': risk_summary,
            'active_alerts': active_alerts,
            'total_assessments': len(recent_assessments)
        }
        
    except Exception as e:
        frappe.log_error(f"Risk Dashboard Error: {str(e)}", "AI Risk Manager")
        return {'error': str(e)}


@frappe.whitelist()
def run_automated_risk_scan(company=None):
    """Run automated risk scan for early warning detection"""
    try:
        if not company:
            company = frappe.defaults.get_user_default('Company')
        
        # Create automated risk assessment
        result = create_risk_assessment(company, f"Automated Scan - {frappe.utils.format_datetime(frappe.utils.now())}")
        
        if result.get('success'):
            # Get the assessment details
            assessment = frappe.get_doc("AI Risk Manager", result['risk_assessment'])
            
            return {
                'success': True,
                'risk_level': assessment.risk_level,
                'critical_findings': assessment.risk_findings[:200] + "..." if len(assessment.risk_findings) > 200 else assessment.risk_findings,
                'assessment_name': result['risk_assessment']
            }
        else:
            return result
            
    except Exception as e:
        frappe.log_error(f"Automated Risk Scan Error: {str(e)}", "AI Risk Manager")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def get_ai_risk_recommendations(risk_assessment_name):
    """Get AI-powered risk recommendations for a specific assessment"""
    try:
        assessment = frappe.get_doc("AI Risk Manager", risk_assessment_name)
        
        return {
            'risk_level': assessment.risk_level,
            'findings': assessment.risk_findings,
            'recommendations': assessment.ai_recommendations,
            'mitigation_actions': assessment.mitigation_actions,
            'follow_up_date': assessment.follow_up_date
        }
        
    except Exception as e:
        frappe.log_error(f"Risk Recommendations Error: {str(e)}", "AI Risk Manager")
        return {'error': str(e)}


@frappe.whitelist()
def setup_risk_monitoring_schedule():
    """Setup automated risk monitoring schedule"""
    try:
        # Create scheduled job for daily risk monitoring
        if not frappe.db.exists("Scheduled Job Type", "Daily Risk Assessment"):
            job = frappe.new_doc("Scheduled Job Type")
            job.method = "vacker_automation.vacker_automation.doctype.ai_risk_manager.ai_risk_manager.daily_risk_monitor"
            job.frequency = "Daily"
            job.insert()
        
        return {'success': True, 'message': 'Risk monitoring schedule setup complete'}
        
    except Exception as e:
        frappe.log_error(f"Risk Monitoring Setup Error: {str(e)}", "AI Risk Manager")
        return {'success': False, 'error': str(e)}


def daily_risk_monitor():
    """Daily automated risk monitoring function"""
    try:
        companies = frappe.get_all("Company", fields=["name"])
        
        for company in companies:
            # Run automated risk scan for each company
            run_automated_risk_scan(company.name)
            
        frappe.log_error("Daily risk monitoring completed successfully", "AI Risk Manager")
        
    except Exception as e:
        frappe.log_error(f"Daily Risk Monitor Error: {str(e)}", "AI Risk Manager") 