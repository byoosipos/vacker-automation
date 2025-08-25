# Copyright (c) 2025, Vacker and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import time


class ChatMessage(Document):
	def before_insert(self):
		"""Set default values before inserting"""
		if not self.user:
			self.user = frappe.session.user
		
		if not self.timestamp:
			self.timestamp = frappe.utils.now()
	
	def after_insert(self):
		"""Update chat session after message is inserted"""
		if self.chat_session:
			session = frappe.get_doc("Chat Session", self.chat_session)
			session.increment_message_count()


@frappe.whitelist()
def save_message(chat_session, content, message_type, thinking_mode=False, thinking_content=None, 
				web_search_enabled=False, attachments=None, ai_model=None, temperature=None, 
				tokens_used=None, response_time=None, metadata=None):
	"""Save a chat message to the database"""
	
	message = frappe.new_doc("Chat Message")
	message.chat_session = chat_session
	message.user = frappe.session.user
	message.content = content
	message.message_type = message_type
	message.timestamp = frappe.utils.now()
	
	# AI-specific fields
	if thinking_mode:
		message.thinking_mode = 1
		message.thinking_content = thinking_content
	
	if web_search_enabled:
		message.web_search_enabled = 1
	
	if attachments:
		message.attachments = json.dumps(attachments) if isinstance(attachments, (list, dict)) else attachments
	
	if ai_model:
		message.ai_model = ai_model
	
	if temperature:
		message.temperature = float(temperature)
	
	if tokens_used:
		message.tokens_used = int(tokens_used)
	
	if response_time:
		message.response_time = float(response_time)
	
	if metadata:
		message.metadata = json.dumps(metadata) if isinstance(metadata, (list, dict)) else metadata
	
	message.insert(ignore_permissions=True)
	
	return message.name


@frappe.whitelist()
def get_session_messages(chat_session, limit=100, offset=0):
	"""Get messages for a chat session"""
	messages = frappe.get_all("Chat Message",
		filters={"chat_session": chat_session},
		fields=[
			"name", "content", "message_type", "timestamp", "thinking_mode", 
			"thinking_content", "web_search_enabled", "attachments", "ai_model",
			"tokens_used", "response_time"
		],
		order_by="timestamp asc",
		limit=limit,
		start=offset
	)
	
	# Parse JSON fields
	for message in messages:
		if message.attachments:
			try:
				message.attachments = json.loads(message.attachments)
			except:
				message.attachments = []
	
	return messages


@frappe.whitelist()
def delete_message(message_name):
	"""Delete a chat message"""
	message = frappe.get_doc("Chat Message", message_name)
	
	# Check if user owns the message or the session
	session = frappe.get_doc("Chat Session", message.chat_session)
	if session.user != frappe.session.user:
		frappe.throw("You can only delete messages from your own sessions")
	
	frappe.delete_doc("Chat Message", message_name)
	
	# Update session message count
	session.total_messages = max(0, (session.total_messages or 1) - 1)
	session.save(ignore_permissions=True)
	
	return {"success": True, "message": "Message deleted"}


@frappe.whitelist()
def get_message_stats(chat_session=None, user=None, from_date=None, to_date=None):
	"""Get statistics for messages"""
	filters = {}
	
	if chat_session:
		filters["chat_session"] = chat_session
	
	if user:
		filters["user"] = user
	elif not chat_session:  # If no specific session, filter by current user
		filters["user"] = frappe.session.user
	
	if from_date:
		if not to_date:
			to_date = frappe.utils.now()
		filters["timestamp"] = ["between", [from_date, to_date]]
	
	messages = frappe.get_all("Chat Message",
		filters=filters,
		fields=["message_type", "tokens_used", "response_time", "ai_model"]
	)
	
	stats = {
		"total_messages": len(messages),
		"user_messages": len([m for m in messages if m.message_type == "User"]),
		"ai_messages": len([m for m in messages if m.message_type == "AI"]),
		"system_messages": len([m for m in messages if m.message_type == "System"]),
		"total_tokens": sum([m.tokens_used or 0 for m in messages]),
		"avg_response_time": 0,
		"models_used": {}
	}
	
	# Calculate average response time for AI messages
	ai_response_times = [m.response_time for m in messages if m.message_type == "AI" and m.response_time]
	if ai_response_times:
		stats["avg_response_time"] = sum(ai_response_times) / len(ai_response_times)
	
	# Count models used
	for message in messages:
		if message.ai_model:
			stats["models_used"][message.ai_model] = stats["models_used"].get(message.ai_model, 0) + 1
	
	return stats 