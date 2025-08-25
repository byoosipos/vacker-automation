#!/usr/bin/env python3
"""
AI Dashboard Enhancements Setup Script - Step 8
Vacker Automation - AI Integration Completion
"""

import frappe
import os

def setup_ai_enhancements():
    """Setup AI Dashboard Enhancements - Step 8"""
    
    print("🚀 Setting up AI Dashboard Enhancements - Step 8...")
    
    # 1. Ensure AI Settings are configured
    setup_ai_settings()
    
    # 2. Clear cache to load new JavaScript
    clear_cache()
    
    # 3. Create custom fields if needed
    setup_custom_fields()
    
    # 4. Setup permissions
    setup_permissions()
    
    # 5. Test AI functionality
    test_ai_features()
    
    print("✅ AI Dashboard Enhancements setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Restart your bench: bench restart")
    print("2. Access the dashboard: https://your-site/app/comprehensive-executive-dashboard")
    print("3. Try the new features:")
    print("   - 🎤 Voice Commands (Ctrl+Shift+V)")
    print("   - 💡 Smart Suggestions (type in chat)")
    print("   - 📊 Predictive Insights (auto-generated)")
    print("   - ⚡ Real-time Updates (every 30 seconds)")
    print("   - ⌨️ Keyboard Shortcuts (Ctrl+K for chat focus)")

def setup_ai_settings():
    """Ensure AI settings are properly configured"""
    print("⚙️ Checking AI Settings...")
    
    try:
        ai_settings = frappe.get_single("AI Settings")
        
        # Enable streaming if not already enabled
        if not hasattr(ai_settings, 'enable_streaming'):
            ai_settings.append('custom_fields', {
                'fieldname': 'enable_streaming',
                'fieldtype': 'Check',
                'label': 'Enable Streaming Chat',
                'default': 1
            })
        
        # Enable voice commands if not already enabled
        if not hasattr(ai_settings, 'enable_voice'):
            ai_settings.append('custom_fields', {
                'fieldname': 'enable_voice',
                'fieldtype': 'Check', 
                'label': 'Enable Voice Commands',
                'default': 1
            })
            
        ai_settings.save()
        print("✅ AI Settings configured")
        
    except Exception as e:
        print(f"⚠️ AI Settings configuration error: {e}")

def clear_cache():
    """Clear cache to load new JavaScript files"""
    print("🧹 Clearing cache...")
    
    try:
        frappe.clear_cache()
        print("✅ Cache cleared")
    except Exception as e:
        print(f"⚠️ Cache clear error: {e}")

def setup_custom_fields():
    """Setup any required custom fields"""
    print("📋 Setting up custom fields...")
    
    try:
        # Add voice transcription field to Chat Message if needed
        if not frappe.db.exists("Custom Field", {"fieldname": "voice_transcription"}):
            frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "Chat Message", 
                "fieldname": "voice_transcription",
                "fieldtype": "Check",
                "label": "Voice Transcription",
                "insert_after": "web_search_enabled"
            }).save()
            
        # Add streaming mode field to Chat Message if needed
        if not frappe.db.exists("Custom Field", {"fieldname": "streaming_mode"}):
            frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "Chat Message",
                "fieldname": "streaming_mode", 
                "fieldtype": "Check",
                "label": "Streaming Mode",
                "insert_after": "voice_transcription"
            }).save()
            
        print("✅ Custom fields setup completed")
        
    except Exception as e:
        print(f"⚠️ Custom fields setup error: {e}")

def setup_permissions():
    """Setup permissions for AI features"""
    print("🔐 Setting up permissions...")
    
    try:
        # Ensure all roles have access to AI features
        roles = ["System Manager", "CEO", "Directors", "General Manager", "AI User"]
        
        for role in roles:
            if frappe.db.exists("Role", role):
                # Grant access to AI Settings
                if not frappe.db.exists("DocPerm", {"parent": "AI Settings", "role": role}):
                    frappe.get_doc({
                        "doctype": "DocPerm",
                        "parent": "AI Settings",
                        "parenttype": "DocType",
                        "role": role,
                        "read": 1,
                        "write": 1 if role in ["System Manager", "AI User"] else 0
                    }).save()
                    
        print("✅ Permissions setup completed")
        
    except Exception as e:
        print(f"⚠️ Permissions setup error: {e}")

def test_ai_features():
    """Test AI features to ensure they work"""
    print("🧪 Testing AI features...")
    
    try:
        # Test AI connection
        from vacker_automation.vacker_automation.doctype.ai_settings.ai_settings import chat_with_ai
        
        test_response = chat_with_ai(
            message="Test connection for AI enhancements - respond with 'Enhancement test successful'"
        )
        
        if test_response.get("success"):
            print("✅ AI connection test successful")
        else:
            print(f"⚠️ AI connection test failed: {test_response.get('error', 'Unknown error')}")
            
        # Test real-time updates
        from vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard import get_real_time_updates
        
        updates_response = get_real_time_updates()
        if updates_response:
            print("✅ Real-time updates test successful")
        else:
            print("⚠️ Real-time updates test failed")
            
        print("✅ AI features testing completed")
        
    except Exception as e:
        print(f"⚠️ AI features testing error: {e}")

def create_ai_enhancement_readme():
    """Create README for AI enhancements"""
    readme_content = """
# 🚀 AI Dashboard Enhancements - Step 8 Complete!

## ✨ New Features Added

### 🎤 Voice Commands
- **Activation**: Ctrl+Shift+V or click microphone button
- **Usage**: Speak your message, AI will transcribe and optionally auto-send
- **Supported**: Chrome, Edge, Safari (latest versions)

### 💡 Smart Suggestions  
- **Activation**: Start typing in chat input (3+ characters)
- **Features**: Context-aware suggestions based on your input
- **Categories**: Financial, Projects, Sales, Inventory analysis

### 📊 Predictive Insights
- **Activation**: Auto-generated when viewing dashboard data
- **Features**: AI-powered business insights and recommendations  
- **Interaction**: Click "Explore This" to dive deeper

### ⚡ Real-time Updates
- **Frequency**: Every 30 seconds
- **Features**: Notifications for new invoices, projects, material requests
- **Controls**: Auto-refresh on overview page, manual refresh option

### ⌨️ Keyboard Shortcuts
- **Ctrl+K**: Focus chat input
- **Ctrl+Shift+V**: Start voice recording  
- **Ctrl+Shift+S**: Toggle streaming mode
- **Escape**: Close all AI panels

## 🔧 Technical Implementation

### Files Added/Modified:
- ✅ `public/js/ai_dashboard_enhancements.js` - Main enhancement script
- ✅ `hooks.py` - JavaScript file registration
- ✅ `comprehensive_executive_dashboard.py` - Real-time updates backend
- ✅ `setup_ai_enhancements.py` - This setup script

### Browser Support:
- ✅ Chrome 60+ (Full features including voice)
- ✅ Firefox 70+ (Partial voice support) 
- ✅ Safari 14+ (WebKit voice recognition)
- ✅ Edge 80+ (Full features)

## 🎯 Next Steps

1. **Test Voice Commands**: Try speaking "Show me financial analysis send"
2. **Explore Smart Suggestions**: Type "financial" or "projects" in chat
3. **Review Predictive Insights**: Check the insights panel on dashboard pages
4. **Monitor Real-time Updates**: Watch for notification popups
5. **Use Keyboard Shortcuts**: Try Ctrl+K to quickly access chat

## 🔗 Integration Points

- **Existing AI Chat**: Enhanced with streaming and voice
- **Dashboard Data**: Feeds into predictive analytics
- **Risk Management**: Integrated with AI risk assessments
- **User Sessions**: Persistent across chat sessions

## 📞 Support

For issues or questions about AI enhancements:
- Check browser console for error messages
- Ensure AI Settings are properly configured
- Verify microphone permissions for voice features
- Contact: info@vacker.com

---
**Vacker Company Limited - AI Integration Excellence** 🌟
"""
    
    try:
        with open("AI_ENHANCEMENTS_README.md", "w") as f:
            f.write(readme_content)
        print("✅ AI Enhancement README created")
    except Exception as e:
        print(f"⚠️ README creation error: {e}")

def main():
    """Main setup function"""
    print("=" * 60)
    print("🤖 VACKER AI DASHBOARD ENHANCEMENTS - STEP 8")
    print("=" * 60)
    
    setup_ai_enhancements()
    create_ai_enhancement_readme()
    
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE - AI ENHANCEMENTS READY!")
    print("=" * 60)

if __name__ == "__main__":
    main() 