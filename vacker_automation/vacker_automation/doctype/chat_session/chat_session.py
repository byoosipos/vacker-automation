# Copyright (c) 2025, Vacker and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class ChatSession(Document):
	def before_insert(self):
		"""Set default values before inserting"""
		if not self.user:
			self.user = frappe.session.user
		
		if not self.creation_date:
			self.creation_date = frappe.utils.now()
		
		if not self.last_message_at:
			self.last_message_at = frappe.utils.now()
		
		if not self.title:
			self.title = f"Chat Session {frappe.utils.format_datetime(self.creation_date, 'dd/MM/yyyy HH:mm')}"
	
	def update_session(self, title=None, session_type=None, tags=None):
		"""Update session metadata"""
		if title:
			self.title = title
		if session_type:
			self.session_type = session_type
		if tags:
			self.tags = tags
		
		self.last_message_at = frappe.utils.now()
		self.save(ignore_permissions=True)
	
	def increment_message_count(self):
		"""Increment the message count and update last message time"""
		self.total_messages = (self.total_messages or 0) + 1
		self.last_message_at = frappe.utils.now()
		self.save(ignore_permissions=True)
	
	def archive_session(self):
		"""Archive the session"""
		self.status = "Archived"
		self.save(ignore_permissions=True)
	
	def get_session_stats(self):
		"""Get session statistics"""
		messages = frappe.get_all("Chat Message", 
			filters={"chat_session": self.name},
			fields=["name", "message_type", "creation", "tokens_used"]
		)
		
		user_messages = len([m for m in messages if m.message_type == "User"])
		ai_messages = len([m for m in messages if m.message_type == "AI"])
		total_tokens = sum([m.tokens_used or 0 for m in messages])
		
		return {
			"total_messages": len(messages),
			"user_messages": user_messages,
			"ai_messages": ai_messages,
			"total_tokens": total_tokens,
			"session_duration": self.get_session_duration()
		}
	
	def get_session_duration(self):
		"""Calculate session duration"""
		if not self.creation_date or not self.last_message_at:
			return 0
		
		from frappe.utils import time_diff_in_seconds
		return time_diff_in_seconds(self.last_message_at, self.creation_date)


@frappe.whitelist()
def create_new_session(title=None, session_type="General Chat"):
	"""Create a new chat session"""
	session = frappe.new_doc("Chat Session")
	session.user = frappe.session.user
	session.title = title or f"New Chat {frappe.utils.format_datetime(frappe.utils.now(), 'dd/MM HH:mm')}"
	session.session_type = session_type
	session.insert(ignore_permissions=True)
	
	return session.name


@frappe.whitelist()
def get_user_sessions(limit=20, status="Active"):
	"""Get user's chat sessions"""
	sessions = frappe.get_all("Chat Session",
		filters={
			"user": frappe.session.user,
			"status": status
		},
		fields=[
			"name", "title", "creation_date", "last_message_at", 
			"total_messages", "session_type", "status", "tags"
		],
		order_by="last_message_at desc",
		limit=limit
	)
	
	# Add latest message preview for each session
	for session in sessions:
		latest_message = frappe.get_all("Chat Message",
			filters={"chat_session": session.name},
			fields=["content", "message_type"],
			order_by="creation desc",
			limit=1
		)
		
		if latest_message:
			session["latest_message"] = latest_message[0].content[:100] + "..." if len(latest_message[0].content) > 100 else latest_message[0].content
			session["latest_message_type"] = latest_message[0].message_type
		else:
			session["latest_message"] = "No messages yet"
			session["latest_message_type"] = None
	
	return sessions


@frappe.whitelist()
def update_session_title(session_name, new_title):
	"""Update session title"""
	session = frappe.get_doc("Chat Session", session_name)
	if session.user != frappe.session.user:
		frappe.throw("You can only update your own sessions")
	
	session.title = new_title
	session.save(ignore_permissions=True)
	
	return {"success": True, "message": "Session title updated"}


@frappe.whitelist()
def archive_session(session_name):
	"""Archive a chat session"""
	session = frappe.get_doc("Chat Session", session_name)
	if session.user != frappe.session.user:
		frappe.throw("You can only archive your own sessions")
	
	session.archive_session()
	
	return {"success": True, "message": "Session archived"}


@frappe.whitelist()
def delete_session(session_name):
	"""Delete a chat session and all its messages"""
	session = frappe.get_doc("Chat Session", session_name)
	if session.user != frappe.session.user:
		frappe.throw("You can only delete your own sessions")
	
	# Delete all messages in the session
	messages = frappe.get_all("Chat Message", filters={"chat_session": session_name})
	for message in messages:
		frappe.delete_doc("Chat Message", message.name)
	
	# Delete the session
	frappe.delete_doc("Chat Session", session_name)
	
	return {"success": True, "message": "Session deleted"} 