# Intelligent Validation Engine for Advanced AI Risk Assessment
# Copyright (c) 2025, Vacker and contributors

import frappe
import json
import re
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, add_days, nowdate, cstr
from difflib import SequenceMatcher
import requests
from PIL import Image
import pytesseract
import io
import base64


class IntelligentValidationEngine:
    """
    Advanced AI Risk Assessment and Mitigation System
    Acts as an experienced professional providing intelligent guidance
    """
    
    def __init__(self, user=None, company=None):
        self.user = user or frappe.session.user
        self.company = company or frappe.defaults.get_user_default('Company')
        self.user_context = self.get_user_context()
        
    def get_user_context(self):
        """Get comprehensive user context for personalized interactions"""
        user_doc = frappe.get_doc('User', self.user)
        roles = frappe.get_roles(self.user)
        
        return {
            'user': self.user,
            'full_name': user_doc.full_name,
            'roles': roles,
            'experience_level': self.determine_experience_level(roles),
            'department': user_doc.get('department'),
            'recent_activity': self.get_recent_user_activity()
        }
    
    def determine_experience_level(self, roles):
        """Determine user experience level based on roles"""
        if any(role in roles for role in ['System Manager', 'Administrator']):
            return 'expert'
        elif any(role in roles for role in ['Accounts Manager', 'HR Manager', 'Projects Manager']):
            return 'experienced'
        elif any(role in roles for role in ['Accounts User', 'HR User', 'Projects User']):
            return 'intermediate'
        else:
            return 'beginner'
    
    def get_recent_user_activity(self):
        """Get user's recent activity for context"""
        recent_docs = frappe.get_all('Version', 
            filters={'owner': self.user, 'creation': ['>', add_days(nowdate(), -30)]},
            fields=['docname', 'ref_doctype', 'creation'],
            order_by='creation desc',
            limit=50
        )
        return recent_docs


class ItemCreationIntelligence(IntelligentValidationEngine):
    """Intelligent Item Creation Validation with Conversational AI"""
    
    def validate_item_creation(self, item_doc):
        """
        Act as an experienced inventory manager (15+ years experience)
        Provide intelligent guidance during item creation
        """
        validation_results = {
            'allow_save': True,
            'warnings': [],
            'recommendations': [],
            'required_actions': [],
            'personality_response': '',
            'confidence_level': 0.95
        }
        
        # 1. Intelligent Duplicate Prevention
        duplicate_analysis = self.detect_intelligent_duplicates(item_doc)
        if duplicate_analysis['potential_duplicates']:
            validation_results['allow_save'] = False
            validation_results['personality_response'] = self.generate_duplicate_prevention_dialog(
                item_doc, duplicate_analysis
            )
            return validation_results
        
        # 2. Stock Maintenance Decision Guidance
        stock_guidance = self.guide_stock_maintenance_decision(item_doc)
        if stock_guidance['needs_clarification']:
            validation_results['required_actions'].append(stock_guidance)
        
        # 3. Item Group Classification Intelligence
        classification_guidance = self.intelligent_item_classification(item_doc)
        if classification_guidance['suggestion_confidence'] < 0.8:
            validation_results['recommendations'].append(classification_guidance)
        
        # 4. Chart of Accounts Mapping
        account_mapping = self.intelligent_account_mapping(item_doc)
        validation_results['recommendations'].append(account_mapping)
        
        # 5. Specification Completeness Check
        completeness_check = self.validate_specification_completeness(item_doc)
        if completeness_check['completeness_score'] < 0.7:
            validation_results['warnings'].append(completeness_check)
        
        # Generate personality response
        validation_results['personality_response'] = self.generate_experienced_manager_response(
            item_doc, validation_results
        )
        
        return validation_results
    
    def detect_intelligent_duplicates(self, item_doc):
        """Advanced duplicate detection using fuzzy matching and semantic analysis"""
        
        # Get existing items with similar characteristics
        search_filters = []
        if item_doc.item_group:
            search_filters.append(['item_group', '=', item_doc.item_group])
        
        existing_items = frappe.get_all('Item',
            filters=search_filters,
            fields=['name', 'item_name', 'description', 'item_code', 
                   'last_purchase_rate', 'stock_uom', 'creation'],
            limit=1000
        )
        
        potential_duplicates = []
        
        for existing_item in existing_items:
            similarity_score = self.calculate_item_similarity(item_doc, existing_item)
            
            if similarity_score > 0.7:  # 70% similarity threshold
                # Get additional context
                item_context = self.get_item_usage_context(existing_item.name)
                
                potential_duplicates.append({
                    'item': existing_item,
                    'similarity_score': similarity_score,
                    'similarity_reasons': self.explain_similarity(item_doc, existing_item),
                    'usage_context': item_context
                })
        
        # Sort by similarity score
        potential_duplicates.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return {
            'potential_duplicates': potential_duplicates[:5],  # Top 5 matches
            'total_similar_items': len(potential_duplicates)
        }
    
    def calculate_item_similarity(self, new_item, existing_item):
        """Calculate similarity between items using multiple factors"""
        similarity_factors = []
        
        # Name similarity
        name_similarity = SequenceMatcher(None, 
            cstr(new_item.item_name).lower(), 
            cstr(existing_item.item_name).lower()
        ).ratio()
        similarity_factors.append(('name', name_similarity, 0.4))
        
        # Description similarity
        if new_item.description and existing_item.description:
            desc_similarity = SequenceMatcher(None,
                cstr(new_item.description).lower(),
                cstr(existing_item.description).lower()
            ).ratio()
            similarity_factors.append(('description', desc_similarity, 0.3))
        
        # Item code similarity (if patterns exist)
        if new_item.item_code and existing_item.item_code:
            code_similarity = SequenceMatcher(None,
                cstr(new_item.item_code).lower(),
                cstr(existing_item.item_code).lower()
            ).ratio()
            similarity_factors.append(('code', code_similarity, 0.2))
        
        # UOM similarity
        if new_item.stock_uom and existing_item.stock_uom:
            uom_match = 1.0 if new_item.stock_uom == existing_item.stock_uom else 0.0
            similarity_factors.append(('uom', uom_match, 0.1))
        
        # Calculate weighted average
        total_weight = sum(weight for _, _, weight in similarity_factors)
        weighted_score = sum(score * weight for _, score, weight in similarity_factors) / total_weight
        
        return weighted_score
    
    def explain_similarity(self, new_item, existing_item):
        """Explain why items are considered similar"""
        reasons = []
        
        # Check name similarity
        name_sim = SequenceMatcher(None, 
            cstr(new_item.item_name).lower(), 
            cstr(existing_item.item_name).lower()
        ).ratio()
        
        if name_sim > 0.6:
            reasons.append(f"Very similar names: '{new_item.item_name}' vs '{existing_item.item_name}'")
        
        # Check common words
        new_words = set(cstr(new_item.item_name).lower().split())
        existing_words = set(cstr(existing_item.item_name).lower().split())
        common_words = new_words.intersection(existing_words)
        
        if len(common_words) >= 2:
            reasons.append(f"Common keywords: {', '.join(common_words)}")
        
        if new_item.stock_uom == existing_item.stock_uom:
            reasons.append(f"Same unit of measure: {new_item.stock_uom}")
        
        return reasons
    
    def get_item_usage_context(self, item_code):
        """Get usage context for existing item"""
        # Recent purchase history
        recent_purchases = frappe.db.sql("""
            SELECT pi.posting_date, pi.supplier, pii.rate, pii.qty
            FROM `tabPurchase Invoice Item` pii
            JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
            WHERE pii.item_code = %s
            AND pi.docstatus = 1
            ORDER BY pi.posting_date DESC
            LIMIT 5
        """, (item_code,), as_dict=True)
        
        # Current stock levels
        stock_levels = frappe.db.sql("""
            SELECT warehouse, actual_qty, stock_value
            FROM `tabBin`
            WHERE item_code = %s
            AND actual_qty > 0
        """, (item_code,), as_dict=True)
        
        # Recent material requests
        recent_requests = frappe.db.sql("""
            SELECT mr.transaction_date, mr.material_request_type, mri.qty
            FROM `tabMaterial Request Item` mri
            JOIN `tabMaterial Request` mr ON mri.parent = mr.name
            WHERE mri.item_code = %s
            AND mr.docstatus = 1
            ORDER BY mr.transaction_date DESC
            LIMIT 3
        """, (item_code,), as_dict=True)
        
        return {
            'recent_purchases': recent_purchases,
            'current_stock': stock_levels,
            'recent_requests': recent_requests,
            'last_used': recent_purchases[0].posting_date if recent_purchases else None
        }
    
    def generate_duplicate_prevention_dialog(self, new_item, duplicate_analysis):
        """Generate conversational duplicate prevention dialog"""
        
        duplicates = duplicate_analysis['potential_duplicates']
        if not duplicates:
            return ""
        
        dialog = f"""
        🤔 **Hold on! I think we might already have something similar...**
        
        I've been managing inventory for 15+ years, and I've learned that duplicates cause major headaches down the road. 
        Let me show you what I found that looks very similar to "{new_item.item_name}":
        
        """
        
        for i, dup in enumerate(duplicates[:3], 1):
            item = dup['item']
            context = dup['usage_context']
            
            dialog += f"""
        **{i}. {item.item_name}** (Code: {item.item_code})
        - Similarity: {dup['similarity_score']:.0%}
        - Why similar: {', '.join(dup['similarity_reasons'])}
        - Last purchased: {context['last_used'] or 'Never'}
        - Current stock: {len(context['current_stock'])} warehouse(s)
        """
            
            if context['recent_purchases']:
                latest_purchase = context['recent_purchases'][0]
                dialog += f"- Recent price: {latest_purchase['rate']} from {latest_purchase['supplier']}\n"
        
        dialog += f"""
        
        **🎯 My Recommendation:**
        Before creating a new item, please verify this isn't the same as what we already have. 
        If it's genuinely different, help me understand:
        
        1. **What makes this item unique?** (specifications, brand, size, etc.)
        2. **Why can't we use the existing similar items?**
        3. **Should we update the existing item description instead?**
        
        This extra step now will save hours of confusion and inventory mix-ups later!
        """
        
        return dialog
    
    def guide_stock_maintenance_decision(self, item_doc):
        """Guide user through stock maintenance decision"""
        
        # Analyze item characteristics to suggest stock maintenance
        stock_indicators = self.analyze_stock_indicators(item_doc)
        
        guidance = {
            'needs_clarification': False,
            'recommendation': '',
            'confidence': 0.8,
            'reasoning': []
        }
        
        # Check if maintain_stock is not set or unclear
        if item_doc.maintain_stock is None or not hasattr(item_doc, 'maintain_stock'):
            guidance['needs_clarification'] = True
            guidance['recommendation'] = self.generate_stock_maintenance_dialog(item_doc, stock_indicators)
        
        return guidance
    
    def analyze_stock_indicators(self, item_doc):
        """Analyze item characteristics to determine stock maintenance needs"""
        indicators = {
            'likely_stock_item': False,
            'reasons': []
        }
        
        # Analyze item name and description for keywords
        item_text = f"{item_doc.item_name} {item_doc.description or ''}".lower()
        
        stock_keywords = ['material', 'equipment', 'tool', 'spare', 'part', 'component', 'raw']
        non_stock_keywords = ['service', 'consultation', 'labor', 'delivery', 'installation']
        
        stock_matches = sum(1 for keyword in stock_keywords if keyword in item_text)
        non_stock_matches = sum(1 for keyword in non_stock_keywords if keyword in item_text)
        
        if stock_matches > non_stock_matches:
            indicators['likely_stock_item'] = True
            indicators['reasons'].append(f"Contains stock-related keywords: {stock_matches} matches")
        elif non_stock_matches > stock_matches:
            indicators['reasons'].append(f"Contains service-related keywords: {non_stock_matches} matches")
        
        # Check item group patterns
        if item_doc.item_group:
            stock_groups = ['Raw Materials', 'Components', 'Finished Goods', 'Tools', 'Equipment']
            non_stock_groups = ['Services', 'Consumables']
            
            if item_doc.item_group in stock_groups:
                indicators['likely_stock_item'] = True
                indicators['reasons'].append(f"Item group '{item_doc.item_group}' typically requires stock tracking")
            elif item_doc.item_group in non_stock_groups:
                indicators['reasons'].append(f"Item group '{item_doc.item_group}' typically doesn't require stock tracking")
        
        return indicators
    
    def generate_stock_maintenance_dialog(self, item_doc, indicators):
        """Generate dialog for stock maintenance decision"""
        
        dialog = f"""
        📦 **Let's decide on stock management for "{item_doc.item_name}"**
        
        As your inventory manager, I need to understand how this item works in your business:
        
        **Key Questions:**
        1. **Physical Storage**: Will you physically store this item in your warehouse?
        2. **Quantity Tracking**: Do you need to track how many you have on hand?
        3. **Receiving Process**: Will you receive deliveries of this item from suppliers?
        4. **Issue Tracking**: Do you need to track when and how much is used/sold?
        
        """
        
        if indicators['likely_stock_item']:
            dialog += f"""
        **💡 Based on my analysis, this looks like a STOCK ITEM because:**
        {chr(10).join(f"- {reason}" for reason in indicators['reasons'])}
        
        **Stock items are good for:**
        - Physical materials and components
        - Items you store in warehouses
        - Things you receive from suppliers
        - Items where quantity matters
        """
        else:
            dialog += f"""
        **💡 Based on my analysis, this might be a NON-STOCK ITEM because:**
        {chr(10).join(f"- {reason}" for reason in indicators['reasons'])}
        
        **Non-stock items are good for:**
        - Services and consultations
        - One-time expenses
        - Items consumed immediately
        - Things you don't physically store
        """
        
        dialog += """
        
        **Please confirm:** Should this item maintain stock levels? (Yes/No)
        """
        
        return dialog
    
    def intelligent_item_classification(self, item_doc):
        """Provide intelligent item group classification suggestions"""
        
        # Analyze existing item groups and their usage patterns
        existing_groups = self.analyze_existing_item_groups()
        
        # Generate suggestions based on item characteristics
        suggestions = self.generate_classification_suggestions(item_doc, existing_groups)
        
        return {
            'suggested_group': suggestions['top_suggestion'],
            'suggestion_confidence': suggestions['confidence'],
            'reasoning': suggestions['reasoning'],
            'alternative_suggestions': suggestions['alternatives']
        }
    
    def analyze_existing_item_groups(self):
        """Analyze existing item group patterns and usage"""
        
        groups_analysis = frappe.db.sql("""
            SELECT 
                ig.name,
                ig.item_group_name,
                COUNT(i.name) as item_count,
                AVG(CASE WHEN i.maintain_stock = 1 THEN 1 ELSE 0 END) as stock_ratio,
                GROUP_CONCAT(DISTINCT i.stock_uom) as common_uoms
            FROM `tabItem Group` ig
            LEFT JOIN `tabItem` i ON i.item_group = ig.name
            GROUP BY ig.name
            HAVING item_count > 0
            ORDER BY item_count DESC
        """, as_dict=True)
        
        return groups_analysis
    
    def generate_classification_suggestions(self, item_doc, existing_groups):
        """Generate item group suggestions based on analysis"""
        
        item_text = f"{item_doc.item_name} {item_doc.description or ''}".lower()
        
        # Score each group based on text similarity and usage patterns
        group_scores = []
        
        for group in existing_groups:
            score = 0
            reasoning = []
            
            # Text similarity with group name
            name_similarity = SequenceMatcher(None, 
                item_text, 
                group.item_group_name.lower()
            ).ratio()
            score += name_similarity * 40
            
            if name_similarity > 0.3:
                reasoning.append(f"Name similarity with '{group.item_group_name}'")
            
            # Check for keyword matches
            group_keywords = group.item_group_name.lower().split()
            keyword_matches = sum(1 for keyword in group_keywords if keyword in item_text)
            if keyword_matches > 0:
                score += keyword_matches * 20
                reasoning.append(f"Keyword matches: {keyword_matches}")
            
            # UOM compatibility
            if item_doc.stock_uom and group.common_uoms:
                if item_doc.stock_uom in group.common_uoms:
                    score += 15
                    reasoning.append(f"Compatible UOM: {item_doc.stock_uom}")
            
            # Group usage frequency (popular groups get slight boost)
            if group.item_count > 10:
                score += 10
                reasoning.append(f"Well-established group ({group.item_count} items)")
            
            group_scores.append({
                'group': group,
                'score': score,
                'reasoning': reasoning
            })
        
        # Sort by score
        group_scores.sort(key=lambda x: x['score'], reverse=True)
        
        top_suggestion = group_scores[0] if group_scores else None
        
        return {
            'top_suggestion': top_suggestion['group'].name if top_suggestion else None,
            'confidence': min(top_suggestion['score'] / 100, 1.0) if top_suggestion else 0,
            'reasoning': top_suggestion['reasoning'] if top_suggestion else [],
            'alternatives': [gs['group'].name for gs in group_scores[1:4]]
        }
    
    def intelligent_account_mapping(self, item_doc):
        """Suggest intelligent chart of accounts mapping"""
        
        # Analyze existing item account mappings
        account_patterns = self.analyze_account_usage_patterns(item_doc)
        
        suggestions = {
            'expense_account': account_patterns['common_expense_account'],
            'income_account': account_patterns['common_income_account'],
            'confidence': account_patterns['confidence'],
            'reasoning': account_patterns['reasoning']
        }
        
        return suggestions
    
    def analyze_account_usage_patterns(self, item_doc):
        """Analyze how similar items use accounts"""
        
        # Find similar items in the same group
        similar_items_accounts = frappe.db.sql("""
            SELECT 
                i.expense_account,
                i.income_account,
                COUNT(*) as usage_count
            FROM `tabItem` i
            WHERE i.item_group = %s
            AND i.expense_account IS NOT NULL
            GROUP BY i.expense_account, i.income_account
            ORDER BY usage_count DESC
            LIMIT 5
        """, (item_doc.item_group,), as_dict=True) if item_doc.item_group else []
        
        if similar_items_accounts:
            top_pattern = similar_items_accounts[0]
            return {
                'common_expense_account': top_pattern.expense_account,
                'common_income_account': top_pattern.income_account,
                'confidence': min(top_pattern.usage_count / 10, 1.0),
                'reasoning': [f"Used by {top_pattern.usage_count} similar items in {item_doc.item_group}"]
            }
        
        # Fallback to company defaults
        company_defaults = self.get_company_default_accounts()
        return {
            'common_expense_account': company_defaults.get('expense_account'),
            'common_income_account': company_defaults.get('income_account'),
            'confidence': 0.5,
            'reasoning': ['Using company default accounts']
        }
    
    def get_company_default_accounts(self):
        """Get company default accounts"""
        company_doc = frappe.get_doc('Company', self.company)
        return {
            'expense_account': company_doc.get('default_expense_account'),
            'income_account': company_doc.get('default_income_account')
        }
    
    def validate_specification_completeness(self, item_doc):
        """Validate completeness of item specifications"""
        
        completeness_factors = []
        
        # Essential fields
        if item_doc.item_name and len(item_doc.item_name.strip()) > 5:
            completeness_factors.append(('name', 1.0, 0.2))
        else:
            completeness_factors.append(('name', 0.5, 0.2))
        
        if item_doc.description and len(item_doc.description.strip()) > 20:
            completeness_factors.append(('description', 1.0, 0.3))
        else:
            completeness_factors.append(('description', 0.3, 0.3))
        
        if item_doc.stock_uom:
            completeness_factors.append(('uom', 1.0, 0.1))
        else:
            completeness_factors.append(('uom', 0.0, 0.1))
        
        if item_doc.item_group:
            completeness_factors.append(('group', 1.0, 0.2))
        else:
            completeness_factors.append(('group', 0.0, 0.2))
        
        # Calculate weighted completeness score
        total_weight = sum(weight for _, _, weight in completeness_factors)
        completeness_score = sum(score * weight for _, score, weight in completeness_factors) / total_weight
        
        missing_elements = [name for name, score, _ in completeness_factors if score < 0.8]
        
        return {
            'completeness_score': completeness_score,
            'missing_elements': missing_elements,
            'recommendations': self.generate_completeness_recommendations(missing_elements)
        }
    
    def generate_completeness_recommendations(self, missing_elements):
        """Generate recommendations for improving completeness"""
        recommendations = []
        
        if 'description' in missing_elements:
            recommendations.append("Add a detailed description including specifications, brand, model, size, etc.")
        
        if 'uom' in missing_elements:
            recommendations.append("Specify the unit of measure (e.g., Nos, Kg, Meters, Liters)")
        
        if 'group' in missing_elements:
            recommendations.append("Select an appropriate item group for better organization")
        
        return recommendations
    
    def generate_experienced_manager_response(self, item_doc, validation_results):
        """Generate response as an experienced inventory manager"""
        
        user_name = self.user_context.get('full_name', 'there')
        experience_level = self.user_context.get('experience_level', 'intermediate')
        
        # Adjust tone based on user experience
        if experience_level == 'beginner':
            tone = "friendly and educational"
            opening = f"Hi {user_name}! Let me help you set up this item correctly."
        elif experience_level == 'experienced':
            tone = "professional and collaborative"
            opening = f"Good to see you again, {user_name}. I have some suggestions for this item."
        else:
            tone = "professional and efficient"
            opening = f"Hello {user_name}, I've analyzed your item and here's what I found:"
        
        response = f"👨‍💼 **{opening}**\n\n"
        
        # Add warnings if any
        if validation_results['warnings']:
            response += "⚠️ **Areas that need attention:**\n"
            for warning in validation_results['warnings']:
                response += f"- {warning.get('message', 'Completeness needs improvement')}\n"
            response += "\n"
        
        # Add recommendations
        if validation_results['recommendations']:
            response += "💡 **My recommendations:**\n"
            for rec in validation_results['recommendations']:
                if isinstance(rec, dict) and 'suggested_group' in rec:
                    response += f"- Consider using item group: **{rec['suggested_group']}**\n"
                elif isinstance(rec, dict) and 'expense_account' in rec:
                    response += f"- Use expense account: **{rec['expense_account']}**\n"
                else:
                    response += f"- {rec}\n"
            response += "\n"
        
        # Add confidence indicator
        confidence = validation_results.get('confidence_level', 0.8)
        if confidence > 0.9:
            response += "✅ **This looks great! Ready to proceed.**"
        elif confidence > 0.7:
            response += "👍 **Good setup with minor suggestions above.**"
        else:
            response += "🔍 **Please address the points above before proceeding.**"
        
        return response


# Frappe whitelisted methods

@frappe.whitelist()
def validate_item_creation(item_doc_json):
    """API method for intelligent item creation validation"""
    try:
        item_doc = frappe._dict(json.loads(item_doc_json))
        validator = ItemCreationIntelligence()
        return validator.validate_item_creation(item_doc)
    except Exception as e:
        frappe.log_error(f"Item Creation Validation Error: {str(e)}", "Intelligent Validation")
        return {'error': str(e)}

@frappe.whitelist()
def get_duplicate_analysis(item_name, item_group=None):
    """API method for duplicate detection analysis"""
    try:
        validator = ItemCreationIntelligence()
        mock_item = frappe._dict({
            'item_name': item_name,
            'item_group': item_group
        })
        return validator.detect_intelligent_duplicates(mock_item)
    except Exception as e:
        frappe.log_error(f"Duplicate Analysis Error: {str(e)}", "Intelligent Validation")
        return {'error': str(e)} 