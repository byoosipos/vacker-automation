# Copyright (c) 2025, Vacker and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import requests
import json


class AIsettings(Document):
	def validate(self):
		"""Validate AI settings configuration"""
		if self.enable_openrouter and not self.openrouter_api_key:
			frappe.throw("Open Router API Key is required when Open Router AI is enabled")
		
		if self.enable_azure and not all([self.azure_api_key, self.azure_endpoint, self.azure_deployment_name]):
			frappe.throw("Azure API Key, Endpoint, and Deployment Name are required when Azure OpenAI is enabled")
		
		# Validate at least one provider is enabled
		if not (self.enable_openrouter or self.enable_azure):
			frappe.throw("At least one AI provider must be enabled")
		
		# Test API connection on save
		self.test_ai_connection()
	
	def test_ai_connection(self):
		"""Test connection to AI provider"""
		try:
			if self.default_ai_provider == "openrouter" and self.enable_openrouter:
				self.test_openrouter_connection()
			elif self.default_ai_provider == "azure" and self.enable_azure:
				self.test_azure_connection()
		except Exception as e:
			frappe.log_error(f"AI Connection Test Failed: {str(e)}", "AI Settings")
			frappe.msgprint(f"Warning: AI connection test failed - {str(e)}", alert=True)
	
	def test_openrouter_connection(self):
		"""Test Open Router API connection"""
		# Decrypt the API key
		api_key = self.get_password("openrouter_api_key")
		if not api_key:
			raise Exception("Open Router API key not found or not set")
		
		headers = {
			"Authorization": f"Bearer {api_key}",
			"Content-Type": "application/json"
		}
		
		test_payload = {
			"model": self.openrouter_model,
			"messages": [{"role": "user", "content": "Test connection"}],
			"max_tokens": 5
		}
		
		response = requests.post(
			f"{self.openrouter_base_url}/chat/completions",
			headers=headers,
			json=test_payload,
			timeout=30
		)
		
		if response.status_code != 200:
			raise Exception(f"Open Router API connection failed: {response.text}")
	
	def test_azure_connection(self):
		"""Test Azure OpenAI API connection"""
		# Decrypt the API key
		api_key = self.get_password("azure_api_key")
		if not api_key:
			raise Exception("Azure API key not found or not set")
		
		headers = {
			"api-key": api_key,
			"Content-Type": "application/json"
		}
		
		test_payload = {
			"messages": [{"role": "user", "content": "Test connection"}],
			"max_tokens": 5
		}
		
		url = f"{self.azure_endpoint}openai/deployments/{self.azure_deployment_name}/chat/completions?api-version={self.azure_api_version}"
		
		response = requests.post(
			url,
			headers=headers,
			json=test_payload,
			timeout=30
		)
		
		if response.status_code != 200:
			raise Exception(f"Azure OpenAI API connection failed: {response.text}")


@frappe.whitelist()
def get_ai_settings():
	"""Get AI settings for the application"""
	settings = frappe.get_single("AI settings")
	return {
		"enabled": settings.enable_openrouter or settings.enable_azure,
		"default_provider": settings.default_ai_provider,
		"data_summarization": settings.enable_data_summarization,
		"report_generation": settings.enable_report_generation,
		"privacy_mode": settings.data_privacy_mode,
		"chat_history_limit": settings.ai_chat_history_limit
	}


@frappe.whitelist()
def get_comprehensive_ai_context(filters=None):
    """Get comprehensive business context for AI including all financial, user, and company data"""
    try:
        if not filters:
            filters = {}
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        # Get company information
        company = filters.get('company') or frappe.defaults.get_user_default('Company')
        if not company:
            company = frappe.db.get_value('Company', {}, 'name')
        
        company_info = frappe.get_doc('Company', company) if company else {}
        
        # Determine AI access level based on user roles
        ai_access_level = determine_ai_access_level(frappe.session.user)
        
        # Get comprehensive context data based on access level
        context = {
            # Company Information
            'company_info': {
                'name': company_info.get('company_name') if company_info else '',
                'country': company_info.get('country') if company_info else '',
                'domain': company_info.get('domain') if company_info else '',
                'default_currency': company_info.get('default_currency') if company_info else '',
                'founded': company_info.get('date_of_establishment') if company_info else ''
            },
            
            # Current User Context
            'user_context': {
                'user': frappe.session.user,
                'full_name': frappe.db.get_value('User', frappe.session.user, 'full_name'),
                'role_profile': frappe.db.get_value('User', frappe.session.user, 'role_profile_name'),
                'roles': frappe.get_roles(frappe.session.user),
                'ai_access_level': ai_access_level
            },
            
            # Risk Management Context
            'risk_overview': get_risk_management_context() if ai_access_level >= 2 else None,
            
            # Financial Summary (Level 2+ access)
            'financial_overview': get_financial_summary_safe(filters) if ai_access_level >= 2 else None,
            'gl_summary': get_gl_overview_safe(filters) if ai_access_level >= 2 else None,
            'cashflow_summary': get_cashflow_data_safe(filters) if ai_access_level >= 2 else None,
            
            # Business Operations (Level 1+ access)
            'projects_summary': get_project_overview_safe(filters) if ai_access_level >= 1 else None,
            'sales_summary': get_sales_overview_safe(filters) if ai_access_level >= 1 else None,
            'procurement_summary': get_procurement_summary_safe(filters) if ai_access_level >= 1 else None,
            'inventory_summary': get_inventory_overview_safe(filters) if ai_access_level >= 1 else None,
            
            # HR & Workforce (Level 2+ access)
            'hr_summary': get_hr_summary_safe(filters) if ai_access_level >= 2 else None,
            'workforce_summary': get_workforce_analytics(filters) if ai_access_level >= 2 else None,
            
            # System Information (Level 3+ access)
            'system_info': {
                'total_users': frappe.db.count('User', {'enabled': 1}) if ai_access_level >= 3 else None,
                'active_users_today': frappe.db.count('User', {'last_login': ['>', frappe.utils.add_days(frappe.utils.nowdate(), -1)]}) if ai_access_level >= 3 else None,
                'total_customers': frappe.db.count('Customer') if ai_access_level >= 1 else None,
                'total_suppliers': frappe.db.count('Supplier') if ai_access_level >= 1 else None,
                'total_items': frappe.db.count('Item') if ai_access_level >= 1 else None
            },
            
            # Permissions and Access
            'user_permissions': {
                'ai_access_level': ai_access_level,
                'can_read_financial': 'Accounts Manager' in frappe.get_roles(frappe.session.user) or 'System Manager' in frappe.get_roles(frappe.session.user),
                'can_read_hr': 'HR Manager' in frappe.get_roles(frappe.session.user) or 'System Manager' in frappe.get_roles(frappe.session.user),
                'can_read_projects': 'Projects Manager' in frappe.get_roles(frappe.session.user) or 'System Manager' in frappe.get_roles(frappe.session.user),
                'can_manage_risks': 'Accounts Manager' in frappe.get_roles(frappe.session.user) or 'System Manager' in frappe.get_roles(frappe.session.user),
                'is_system_manager': 'System Manager' in frappe.get_roles(frappe.session.user)
            }
        }
        
        return context
        
    except Exception as e:
        frappe.log_error(f"AI Context Error: {str(e)}", "AI Context")
        return {}


def determine_ai_access_level(user):
    """Determine AI access level based on user roles and permissions"""
    user_roles = frappe.get_roles(user)
    
    # Level 3: Full Administrative Access
    if any(role in user_roles for role in ['System Manager', 'Administrator']):
        return 3
    
    # Level 2: Manager Access
    if any(role in user_roles for role in ['Accounts Manager', 'HR Manager', 'Projects Manager', 'Sales Manager']):
        return 2
    
    # Level 1: User Access
    if any(role in user_roles for role in ['Accounts User', 'HR User', 'Projects User', 'Sales User']):
        return 1
    
    # Level 0: Minimal Access
    return 0


def get_financial_summary_safe(filters):
    """Safe wrapper for get_financial_summary function"""
    try:
        from vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard import get_financial_summary
        return get_financial_summary(filters)
    except Exception as e:
        frappe.log_error(f"Financial Summary Error: {str(e)}", "AI Context")
        return None

def get_gl_overview_safe(filters):
    """Safe wrapper for get_gl_overview function"""
    try:
        from vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard import get_gl_overview
        return get_gl_overview(filters)
    except Exception as e:
        frappe.log_error(f"GL Overview Error: {str(e)}", "AI Context")
        return None

def get_cashflow_data_safe(filters):
    """Safe wrapper for get_cashflow_data function"""
    try:
        from vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard import get_cashflow_data
        return get_cashflow_data(filters)
    except Exception as e:
        frappe.log_error(f"Cashflow Data Error: {str(e)}", "AI Context")
        return None

def get_project_overview_safe(filters):
    """Safe wrapper for get_project_overview function"""
    try:
        from vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard import get_project_overview
        return get_project_overview(filters)
    except Exception as e:
        frappe.log_error(f"Project Overview Error: {str(e)}", "AI Context")
        return None

def get_sales_overview_safe(filters):
    """Safe wrapper for get_sales_overview function"""
    try:
        from vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard import get_sales_overview
        return get_sales_overview(filters)
    except Exception as e:
        frappe.log_error(f"Sales Overview Error: {str(e)}", "AI Context")
        return None

def get_procurement_summary_safe(filters):
    """Safe wrapper for get_procurement_summary function"""
    try:
        from vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard import get_procurement_summary
        return get_procurement_summary(filters)
    except Exception as e:
        frappe.log_error(f"Procurement Summary Error: {str(e)}", "AI Context")
        return None

def get_inventory_overview_safe(filters):
    """Safe wrapper for get_inventory_overview function"""
    try:
        from vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard import get_inventory_overview
        return get_inventory_overview(filters)
    except Exception as e:
        frappe.log_error(f"Inventory Overview Error: {str(e)}", "AI Context")
        return None

def get_hr_summary_safe(filters):
    """Safe wrapper for get_hr_summary function"""
    try:
        from vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard import get_hr_summary
        return get_hr_summary(filters)
    except Exception as e:
        frappe.log_error(f"HR Summary Error: {str(e)}", "AI Context")
        return None

def get_risk_management_context():
    """Get risk management context for AI analysis"""
    try:
        from vacker_automation.vacker_automation.doctype.ai_risk_manager.ai_risk_manager import get_risk_dashboard_data
        
        risk_data = get_risk_dashboard_data()
        
        return {
            'recent_risk_assessments': risk_data.get('recent_assessments', []),
            'active_risk_alerts': risk_data.get('active_alerts', []),
            'risk_summary': risk_data.get('risk_summary', []),
            'risk_monitoring_enabled': True
        }
    except Exception as e:
        frappe.log_error(f"Risk Context Error: {str(e)}", "AI Risk Context")
        return None


@frappe.whitelist()
def chat_with_ai(message, context_data=None, chat_session=None, thinking_mode=False, enable_web_search=False, date_range=None):
    """Send message to AI and get response with enhanced capabilities and comprehensive business context"""
    import time
    start_time = time.time()
    
    try:
        settings = frappe.get_single("AI settings")
        
        if not (settings.enable_openrouter or settings.enable_azure):
            return {"error": "AI is not enabled. Please configure AI settings first."}
        
        # Create or get chat session
        if not chat_session:
            from vacker_automation.vacker_automation.doctype.chat_session.chat_session import create_new_session
            chat_session = create_new_session()
        
        # Save user message
        from vacker_automation.vacker_automation.doctype.chat_message.chat_message import save_message
        save_message(
            chat_session=chat_session,
            content=message,
            message_type="User",
            thinking_mode=thinking_mode,
            web_search_enabled=enable_web_search
        )
        
        # Get comprehensive business context
        filters = {}
        if date_range:
            if isinstance(date_range, str):
                date_range = json.loads(date_range)
            filters.update(date_range)
        
        comprehensive_context = get_comprehensive_ai_context(filters)
        
        # Prepare enhanced context with comprehensive business data
        context_str = f"\nCOMPREHENSIVE BUSINESS CONTEXT:\n{json.dumps(comprehensive_context, indent=2)}"
        
        # Add dashboard context if provided
        if context_data:
            if isinstance(context_data, str):
                context_data = json.loads(context_data)
            context_str += f"\n\nDASHBOARD DATA: {json.dumps(context_data, indent=2)}"
        
        # Add date range context if provided
        if date_range:
            context_str += f"\nANALYSIS PERIOD: {date_range.get('from_date', '')} to {date_range.get('to_date', '')}"
        
        # Enhanced system prompt for thinking mode
        enhanced_prompt = settings.system_prompt
        if thinking_mode:
            enhanced_prompt += "\n\nYou are in THINKING MODE. Before providing your final answer, show your reasoning process step by step. Use the format: 🧠 **Thinking Process:** [your reasoning] followed by 📝 **Answer:** [your response]."
        
        if enable_web_search:
            enhanced_prompt += "\n\nYou have access to web search capabilities. When asked about current trends, market data, or recent information, provide comprehensive insights based on your knowledge and reasoning."
        
        # Get recent messages from this session for context
        from vacker_automation.vacker_automation.doctype.chat_message.chat_message import get_session_messages
        recent_messages = get_session_messages(chat_session, limit=settings.ai_chat_history_limit)
        
        # Build message history
        messages = [{"role": "system", "content": enhanced_prompt + context_str}]
        
        # Add recent session messages
        for msg in recent_messages[:-1]:  # Exclude the just-added user message
            role = "user" if msg.message_type == "User" else "assistant"
            messages.append({"role": role, "content": msg.content})
        
        messages.append({"role": "user", "content": message})
        
        # Get AI response
        ai_model = ""
        temperature = 0
        
        if settings.default_ai_provider == "openrouter" and settings.enable_openrouter:
            response = get_openrouter_response(settings, messages)
            ai_model = settings.openrouter_model
            temperature = settings.openrouter_temperature
        elif settings.default_ai_provider == "azure" and settings.enable_azure:
            response = get_azure_response(settings, messages)
            ai_model = settings.azure_deployment_name
            temperature = settings.azure_temperature
        else:
            return {"error": "No valid AI provider configured"}
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Parse thinking mode response if enabled
        thinking_content = ""
        final_response = response
        
        if thinking_mode and "🧠 **Thinking Process:**" in response:
            parts = response.split("📝 **Answer:**")
            if len(parts) == 2:
                thinking_content = parts[0].replace("🧠 **Thinking Process:**", "").strip()
                final_response = parts[1].strip()
        
        # Save AI response
        save_message(
            chat_session=chat_session,
            content=final_response,
            message_type="AI",
            thinking_mode=thinking_mode,
            thinking_content=thinking_content,
            web_search_enabled=enable_web_search,
            ai_model=ai_model,
            temperature=temperature,
            response_time=response_time
        )
        
        return {
            "response": final_response,
            "thinking": thinking_content if thinking_mode else None,
            "chat_session": chat_session,
            "response_time": response_time,
            "success": True
        }
        
    except Exception as e:
        frappe.log_error(f"AI Chat Error: {str(e)}", "AI Chat")
        return {"error": f"AI service error: {str(e)}"}


def get_openrouter_response(settings, messages, stream=False):
    """Get response from Open Router AI with optional streaming"""
    # Decrypt the API key
    api_key = settings.get_password("openrouter_api_key")
    if not api_key:
        raise Exception("Open Router API key not found or not set")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.openrouter_model,
        "messages": messages,
        "max_tokens": settings.openrouter_max_tokens,
        "temperature": settings.openrouter_temperature,
        "top_p": settings.openrouter_top_p,
        "stream": stream
    }
    
    if stream:
        # For streaming responses
        response = requests.post(
            f"{settings.openrouter_base_url}/chat/completions",
            headers=headers,
            json=payload,
            stream=True,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"Open Router API error: {response.text}")
        
        return response  # Return the streaming response object
    else:
        # For regular responses
        response = requests.post(
            f"{settings.openrouter_base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Open Router API error: {response.text}")
        
        return response.json()["choices"][0]["message"]["content"]


def get_azure_response(settings, messages, stream=False):
    """Get response from Azure OpenAI with optional streaming"""
    # Decrypt the API key
    api_key = settings.get_password("azure_api_key")
    if not api_key:
        raise Exception("Azure API key not found or not set")
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": messages,
        "max_tokens": settings.azure_max_tokens,
        "temperature": settings.azure_temperature,
        "stream": stream
    }
    
    url = f"{settings.azure_endpoint}openai/deployments/{settings.azure_deployment_name}/chat/completions?api-version={settings.azure_api_version}"
    
    if stream:
        # For streaming responses
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            stream=True,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"Azure OpenAI API error: {response.text}")
        
        return response  # Return the streaming response object
    else:
        # For regular responses
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Azure OpenAI API error: {response.text}")
        
        return response.json()["choices"][0]["message"]["content"]


@frappe.whitelist()
def generate_data_summary(dashboard_data, filters=None):
	"""Generate AI summary of dashboard data"""
	try:
		settings = frappe.get_single("AI settings")
		
		if not settings.enable_data_summarization:
			return {"error": "Data summarization is not enabled"}
		
		# Prepare data for AI analysis
		if isinstance(dashboard_data, str):
			dashboard_data = json.loads(dashboard_data)
		
		summary_prompt = f"""
		Please provide a comprehensive business summary of the following dashboard data:
		
		Dashboard Data: {json.dumps(dashboard_data, indent=2)}
		
		Filters Applied: {json.dumps(filters) if filters else 'None'}
		
		Please provide:
		1. Key insights and trends
		2. Areas of concern or opportunity
		3. Recommended actions
		4. Performance highlights
		
		Keep the summary business-focused and actionable.
		"""
		
		response = chat_with_ai(summary_prompt, dashboard_data)
		return response
		
	except Exception as e:
		frappe.log_error(f"Data Summary Error: {str(e)}", "AI Data Summary")
		return {"error": f"Failed to generate summary: {str(e)}"}


@frappe.whitelist()
def generate_comprehensive_report(module_name, data, filters=None):
	"""Generate comprehensive AI report for specific module"""
	try:
		settings = frappe.get_single("AI settings")
		
		if not settings.enable_report_generation:
			return {"error": "Report generation is not enabled"}
		
		if isinstance(data, str):
			data = json.loads(data)
		
		report_prompt = f"""
		Generate a comprehensive business report for the {module_name} module with the following data:
		
		Data: {json.dumps(data, indent=2)}
		Filters: {json.dumps(filters) if filters else 'None'}
		
		Please structure the report with:
		1. Executive Summary
		2. Key Performance Indicators
		3. Detailed Analysis
		4. Trends and Patterns
		5. Risk Assessment
		6. Recommendations
		7. Action Items
		
		Format the response in a professional business report style.
		"""
		
		response = chat_with_ai(report_prompt, data)
		return response
		
	except Exception as e:
		frappe.log_error(f"Report Generation Error: {str(e)}", "AI Report Generation")
		return {"error": f"Failed to generate report: {str(e)}"}


@frappe.whitelist()
def perform_web_search(query, context_data=None):
	"""Perform web search and provide AI insights"""
	try:
		settings = frappe.get_single("AI settings")
		
		if not (settings.enable_openrouter or settings.enable_azure):
			return {"error": "AI is not enabled. Please configure AI settings first."}
		
		if isinstance(context_data, str):
			context_data = json.loads(context_data)
		
		# Enhanced search prompt with web research capabilities
		search_prompt = f"""
		Please research the following query using your knowledge and provide comprehensive insights:
		
		Search Query: {query}
		
		Business Context: {json.dumps(context_data, indent=2) if context_data else 'No specific context provided'}
		
		Please provide:
		1. Current Market Trends and Analysis
		2. Industry Benchmarks and Best Practices
		3. Competitive Landscape Insights
		4. Strategic Recommendations
		5. Actionable Business Insights
		6. Risk Factors and Opportunities
		
		Focus on providing factual, business-relevant information that can help in decision-making.
		Include specific data points, statistics, and trends where applicable.
		"""
		
		response = chat_with_ai(search_prompt, context_data)
		return response
		
	except Exception as e:
		frappe.log_error(f"Web Search Error: {str(e)}", "AI Web Search")
		return {"error": f"Failed to perform web search: {str(e)}"}


@frappe.whitelist()
def chat_with_ai_stream(message, context_data=None, chat_history=None, thinking_mode=False, enable_web_search=False, date_range=None):
	"""Stream AI response in real-time"""
	import json as json_module
	
	try:
		settings = frappe.get_single("AI settings")
		
		if not (settings.enable_openrouter or settings.enable_azure):
			yield json_module.dumps({"error": "AI is not enabled. Please configure AI settings first."})
			return
		
		# Prepare enhanced context (same as regular chat)
		context_str = ""
		if context_data:
			if isinstance(context_data, str):
				context_data = json.loads(context_data)
			context_str = f"\nContext Data: {json.dumps(context_data, indent=2)}"
		
		if date_range:
			if isinstance(date_range, str):
				date_range = json.loads(date_range)
			context_str += f"\nAnalysis Period: {date_range.get('from_date', '')} to {date_range.get('to_date', '')}"
		
		# Enhanced system prompt
		enhanced_prompt = settings.system_prompt
		if thinking_mode:
			enhanced_prompt += "\n\nYou are in THINKING MODE. Show your reasoning process clearly."
		
		if enable_web_search:
			enhanced_prompt += "\n\nProvide comprehensive insights based on your knowledge and reasoning."
		
		# Build message history
		messages = [{"role": "system", "content": enhanced_prompt + context_str}]
		
		if chat_history:
			if isinstance(chat_history, str):
				chat_history = json.loads(chat_history)
			messages.extend(chat_history[-settings.ai_chat_history_limit:])
		
		messages.append({"role": "user", "content": message})
		
		# Get streaming response
		if settings.default_ai_provider == "openrouter" and settings.enable_openrouter:
			stream_response = get_openrouter_response(settings, messages, stream=True)
		elif settings.default_ai_provider == "azure" and settings.enable_azure:
			stream_response = get_azure_response(settings, messages, stream=True)
		else:
			yield json_module.dumps({"error": "No valid AI provider configured"})
			return
		
		# Process streaming response
		full_content = ""
		for line in stream_response.iter_lines():
			if line:
				line = line.decode('utf-8')
				if line.startswith('data: '):
					data = line[6:]  # Remove 'data: ' prefix
					if data.strip() == '[DONE]':
						break
					
					try:
						chunk = json_module.loads(data)
						if 'choices' in chunk and len(chunk['choices']) > 0:
							delta = chunk['choices'][0].get('delta', {})
							if 'content' in delta:
								content = delta['content']
								full_content += content
								yield json_module.dumps({
									"content": content,
									"full_content": full_content,
									"success": True
								})
					except json_module.JSONDecodeError:
						continue
		
		# Send final response
		yield json_module.dumps({
			"content": "",
			"full_content": full_content,
			"finished": True,
			"success": True
		})
		
	except Exception as e:
		frappe.log_error(f"AI Stream Error: {str(e)}", "AI Stream")
		yield json_module.dumps({"error": f"AI streaming error: {str(e)}"})


@frappe.whitelist()
def test_ai_connection():
	"""Test AI connection endpoint"""
	try:
		settings = frappe.get_single("AI settings")
		settings.test_ai_connection()
		return {"success": True, "message": "AI connection test successful!"}
	except Exception as e:
		frappe.log_error(f"AI Connection Test Error: {str(e)}", "AI Connection Test")
		return {"success": False, "error": str(e)}
