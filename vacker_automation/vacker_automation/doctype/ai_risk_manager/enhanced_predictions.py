# Enhanced Predictive Analytics for AI Risk Manager
# Copyright (c) 2025, Vacker and contributors

import frappe
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, add_days, nowdate
import json


class EnhancedPredictiveAnalytics:
    """Advanced predictive analytics for financial risk management"""
    
    def __init__(self, company=None):
        self.company = company or frappe.defaults.get_user_default('Company')
    
    def predict_cash_flow_advanced(self, forecast_days=90):
        """Enhanced cash flow prediction using multiple models"""
        try:
            # Get historical cash flow data
            historical_data = self.get_historical_cash_flow_data()
            
            # Multiple prediction models
            predictions = {
                'trend_based': self.trend_based_prediction(historical_data, forecast_days),
                'seasonal': self.seasonal_prediction(historical_data, forecast_days),
                'ml_enhanced': self.ml_cash_flow_prediction(historical_data, forecast_days),
                'ensemble': None  # Will be calculated from above
            }
            
            # Ensemble prediction (weighted average)
            predictions['ensemble'] = self.create_ensemble_prediction(predictions)
            
            # Add confidence intervals
            confidence_intervals = self.calculate_confidence_intervals(predictions['ensemble'])
            
            return {
                'predictions': predictions,
                'confidence_intervals': confidence_intervals,
                'recommendation': self.generate_cash_flow_recommendations(predictions['ensemble']),
                'risk_alerts': self.identify_cash_flow_risks(predictions['ensemble'])
            }
            
        except Exception as e:
            frappe.log_error(f"Enhanced Cash Flow Prediction Error: {str(e)}", "Enhanced Predictions")
            return None
    
    def predict_customer_payment_behavior(self, customer=None):
        """Predict customer payment patterns and identify at-risk accounts"""
        try:
            # Get customer payment history
            payment_history = self.get_customer_payment_history(customer)
            
            # Calculate payment metrics
            payment_metrics = {}
            for cust, data in payment_history.items():
                metrics = {
                    'avg_payment_days': np.mean([d['days_to_pay'] for d in data]),
                    'payment_consistency': self.calculate_payment_consistency(data),
                    'late_payment_trend': self.calculate_late_payment_trend(data),
                    'payment_amount_variance': self.calculate_payment_variance(data),
                    'risk_score': 0
                }
                
                # Calculate risk score
                metrics['risk_score'] = self.calculate_customer_risk_score(metrics)
                payment_metrics[cust] = metrics
            
            return {
                'customer_metrics': payment_metrics,
                'high_risk_customers': self.identify_high_risk_customers(payment_metrics),
                'collection_recommendations': self.generate_collection_strategy(payment_metrics)
            }
            
        except Exception as e:
            frappe.log_error(f"Customer Payment Prediction Error: {str(e)}", "Enhanced Predictions")
            return None
    
    def predict_project_completion_probability(self, project=None):
        """Predict project completion probability based on current progress"""
        try:
            if project:
                projects = [project]
            else:
                # Get all active projects
                projects = frappe.get_all('Project', 
                    filters={'company': self.company, 'status': ['in', ['Open', 'In Progress']]},
                    fields=['name', 'project_name', 'expected_end_date', 'percent_complete']
                )
            
            predictions = {}
            for proj in projects:
                project_name = proj.name if isinstance(proj, dict) else proj
                
                # Get project data
                project_data = self.get_project_analysis_data(project_name)
                
                # Calculate completion probability
                completion_prob = self.calculate_completion_probability(project_data)
                
                # Identify risk factors
                risk_factors = self.identify_project_risk_factors(project_data)
                
                # Generate recommendations
                recommendations = self.generate_project_recommendations(project_data, completion_prob)
                
                predictions[project_name] = {
                    'completion_probability': completion_prob,
                    'risk_factors': risk_factors,
                    'recommendations': recommendations,
                    'expected_completion_variance': self.calculate_completion_variance(project_data)
                }
            
            return predictions
            
        except Exception as e:
            frappe.log_error(f"Project Completion Prediction Error: {str(e)}", "Enhanced Predictions")
            return None
    
    def detect_financial_anomalies(self):
        """Real-time detection of financial anomalies"""
        try:
            anomalies = {
                'transaction_anomalies': self.detect_transaction_anomalies(),
                'expense_anomalies': self.detect_expense_anomalies(),
                'revenue_anomalies': self.detect_revenue_anomalies(),
                'cash_flow_anomalies': self.detect_cash_flow_anomalies()
            }
            
            # Prioritize anomalies by severity
            prioritized_anomalies = self.prioritize_anomalies(anomalies)
            
            return {
                'anomalies': anomalies,
                'priority_alerts': prioritized_anomalies,
                'investigation_steps': self.generate_investigation_steps(prioritized_anomalies)
            }
            
        except Exception as e:
            frappe.log_error(f"Anomaly Detection Error: {str(e)}", "Enhanced Predictions")
            return None
    
    # Helper Methods
    
    def get_historical_cash_flow_data(self, months=12):
        """Get historical cash flow data for analysis"""
        from_date = add_days(nowdate(), -30 * months)
        
        data = frappe.db.sql("""
            SELECT 
                DATE(posting_date) as date,
                SUM(CASE WHEN debit > 0 THEN debit ELSE -credit END) as daily_cash_flow
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.company = %s
            AND gle.posting_date >= %s
            AND acc.account_type IN ('Bank', 'Cash')
            AND gle.is_cancelled = 0
            GROUP BY DATE(posting_date)
            ORDER BY posting_date
        """, (self.company, from_date), as_dict=True)
        
        return data
    
    def trend_based_prediction(self, historical_data, forecast_days):
        """Simple trend-based prediction"""
        if not historical_data or len(historical_data) < 7:
            return []
        
        # Calculate trend
        values = [d['daily_cash_flow'] for d in historical_data[-30:]]  # Last 30 days
        trend = np.polyfit(range(len(values)), values, 1)[0]  # Linear trend
        
        # Generate predictions
        last_value = values[-1]
        predictions = []
        for i in range(1, forecast_days + 1):
            predicted_value = last_value + (trend * i)
            predictions.append({
                'date': add_days(nowdate(), i),
                'predicted_cash_flow': predicted_value,
                'model': 'trend_based'
            })
        
        return predictions
    
    def seasonal_prediction(self, historical_data, forecast_days):
        """Seasonal pattern-based prediction"""
        if not historical_data or len(historical_data) < 30:
            return []
        
        # Calculate weekly seasonality
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.dayofweek
        
        # Average by day of week
        seasonal_patterns = df.groupby('day_of_week')['daily_cash_flow'].mean().to_dict()
        
        # Generate predictions
        predictions = []
        for i in range(1, forecast_days + 1):
            future_date = add_days(nowdate(), i)
            day_of_week = getdate(future_date).weekday()
            predicted_value = seasonal_patterns.get(day_of_week, 0)
            
            predictions.append({
                'date': future_date,
                'predicted_cash_flow': predicted_value,
                'model': 'seasonal'
            })
        
        return predictions
    
    def ml_cash_flow_prediction(self, historical_data, forecast_days):
        """Machine learning enhanced prediction (placeholder for advanced ML)"""
        # This would implement actual ML models like ARIMA, LSTM, etc.
        # For now, return a simple moving average
        
        if not historical_data or len(historical_data) < 7:
            return []
        
        # Simple moving average for demonstration
        window_size = min(7, len(historical_data))
        recent_values = [d['daily_cash_flow'] for d in historical_data[-window_size:]]
        avg_value = np.mean(recent_values)
        
        predictions = []
        for i in range(1, forecast_days + 1):
            predictions.append({
                'date': add_days(nowdate(), i),
                'predicted_cash_flow': avg_value,
                'model': 'ml_enhanced'
            })
        
        return predictions
    
    def create_ensemble_prediction(self, predictions):
        """Create ensemble prediction from multiple models"""
        models = ['trend_based', 'seasonal', 'ml_enhanced']
        weights = {'trend_based': 0.3, 'seasonal': 0.3, 'ml_enhanced': 0.4}
        
        ensemble_predictions = []
        max_length = max(len(predictions[model]) for model in models if predictions[model])
        
        for i in range(max_length):
            weighted_sum = 0
            total_weight = 0
            date = None
            
            for model in models:
                if predictions[model] and i < len(predictions[model]):
                    value = predictions[model][i]['predicted_cash_flow']
                    weight = weights[model]
                    weighted_sum += value * weight
                    total_weight += weight
                    if not date:
                        date = predictions[model][i]['date']
            
            if total_weight > 0:
                ensemble_predictions.append({
                    'date': date,
                    'predicted_cash_flow': weighted_sum / total_weight,
                    'model': 'ensemble'
                })
        
        return ensemble_predictions
    
    def calculate_confidence_intervals(self, predictions, confidence=0.95):
        """Calculate confidence intervals for predictions"""
        if not predictions:
            return []
        
        # Simple confidence interval calculation
        # In practice, this would use historical prediction errors
        confidence_intervals = []
        for pred in predictions:
            value = pred['predicted_cash_flow']
            # Assume 10% standard error for demonstration
            std_error = abs(value * 0.1)
            margin = std_error * 1.96  # 95% confidence interval
            
            confidence_intervals.append({
                'date': pred['date'],
                'lower_bound': value - margin,
                'upper_bound': value + margin,
                'confidence_level': confidence
            })
        
        return confidence_intervals
    
    def generate_cash_flow_recommendations(self, predictions):
        """Generate actionable recommendations based on predictions"""
        if not predictions:
            return []
        
        recommendations = []
        
        # Check for negative cash flow periods
        negative_days = [p for p in predictions if p['predicted_cash_flow'] < 0]
        if negative_days:
            recommendations.append({
                'type': 'warning',
                'message': f"Predicted negative cash flow for {len(negative_days)} days",
                'action': "Consider accelerating receivables collection or delaying payments"
            })
        
        # Check for low cash flow periods
        low_cash_days = [p for p in predictions if 0 < p['predicted_cash_flow'] < 10000]
        if low_cash_days:
            recommendations.append({
                'type': 'caution',
                'message': f"Low cash flow predicted for {len(low_cash_days)} days",
                'action': "Monitor cash position closely and prepare contingency plans"
            })
        
        return recommendations
    
    def identify_cash_flow_risks(self, predictions):
        """Identify specific cash flow risks"""
        if not predictions:
            return []
        
        risks = []
        
        # Consecutive negative days
        negative_streak = 0
        max_negative_streak = 0
        
        for pred in predictions:
            if pred['predicted_cash_flow'] < 0:
                negative_streak += 1
                max_negative_streak = max(max_negative_streak, negative_streak)
            else:
                negative_streak = 0
        
        if max_negative_streak > 5:
            risks.append({
                'type': 'critical',
                'risk': 'Extended negative cash flow period',
                'duration': f"{max_negative_streak} days",
                'impact': 'High liquidity risk'
            })
        
        return risks


# Frappe whitelisted methods for API access

@frappe.whitelist()
def get_enhanced_cash_flow_prediction(company=None, forecast_days=90):
    """API method for enhanced cash flow prediction"""
    analytics = EnhancedPredictiveAnalytics(company)
    return analytics.predict_cash_flow_advanced(int(forecast_days))

@frappe.whitelist()
def get_customer_payment_predictions(customer=None, company=None):
    """API method for customer payment behavior prediction"""
    analytics = EnhancedPredictiveAnalytics(company)
    return analytics.predict_customer_payment_behavior(customer)

@frappe.whitelist()
def get_project_completion_predictions(project=None, company=None):
    """API method for project completion probability prediction"""
    analytics = EnhancedPredictiveAnalytics(company)
    return analytics.predict_project_completion_probability(project)

@frappe.whitelist()
def detect_financial_anomalies(company=None):
    """API method for financial anomaly detection"""
    analytics = EnhancedPredictiveAnalytics(company)
    return analytics.detect_financial_anomalies() 