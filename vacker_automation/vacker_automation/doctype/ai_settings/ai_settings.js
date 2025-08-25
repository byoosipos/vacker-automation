// Copyright (c) 2025, Vacker and contributors
// For license information, please see license.txt

frappe.ui.form.on('AI settings', {
    refresh: function(frm) {
        frm.add_custom_button(__('Test AI Connection'), function() {
            test_ai_connection(frm);
        });
        
        frm.add_custom_button(__('View Dashboard'), function() {
            frappe.set_route('comprehensive-executive-dashboard');
        });
        
        // Show current status
        show_ai_status(frm);
    },
    
    enable_openrouter: function(frm) {
        toggle_openrouter_fields(frm);
    },
    
    enable_azure: function(frm) {
        toggle_azure_fields(frm);
    },
    
    default_ai_provider: function(frm) {
        validate_provider_selection(frm);
    }
});

function toggle_openrouter_fields(frm) {
    const is_enabled = frm.doc.enable_openrouter;
    frm.toggle_reqd('openrouter_api_key', is_enabled);
    frm.toggle_display('openrouter_api_key', is_enabled);
    frm.toggle_display('openrouter_model', is_enabled);
    frm.toggle_display('openrouter_base_url', is_enabled);
    frm.toggle_display('openrouter_temperature', is_enabled);
    frm.toggle_display('openrouter_max_tokens', is_enabled);
    frm.toggle_display('openrouter_top_p', is_enabled);
}

function toggle_azure_fields(frm) {
    const is_enabled = frm.doc.enable_azure;
    frm.toggle_reqd('azure_api_key', is_enabled);
    frm.toggle_reqd('azure_endpoint', is_enabled);
    frm.toggle_reqd('azure_deployment_name', is_enabled);
    frm.toggle_display('azure_api_key', is_enabled);
    frm.toggle_display('azure_endpoint', is_enabled);
    frm.toggle_display('azure_deployment_name', is_enabled);
    frm.toggle_display('azure_api_version', is_enabled);
    frm.toggle_display('azure_temperature', is_enabled);
    frm.toggle_display('azure_max_tokens', is_enabled);
}

function validate_provider_selection(frm) {
    if (frm.doc.default_ai_provider === 'openrouter' && !frm.doc.enable_openrouter) {
        frappe.msgprint(__('Please enable Open Router AI first'));
        frm.set_value('default_ai_provider', '');
    }
    
    if (frm.doc.default_ai_provider === 'azure' && !frm.doc.enable_azure) {
        frappe.msgprint(__('Please enable Azure OpenAI first'));
        frm.set_value('default_ai_provider', '');
    }
}

function test_ai_connection(frm) {
    if (!frm.doc.enable_openrouter && !frm.doc.enable_azure) {
        frappe.msgprint(__('Please enable at least one AI provider first'));
        return;
    }
    
    frappe.call({
        method: 'vacker_automation.vacker_automation.doctype.ai_settings.ai_settings.chat_with_ai',
        args: {
            message: 'Test connection - please respond with "Connection successful"'
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.msgprint({
                    title: __('AI Connection Test'),
                    message: __('AI connection successful! Response: ') + r.message.response,
                    indicator: 'green'
                });
            } else {
                frappe.msgprint({
                    title: __('AI Connection Test'),
                    message: __('AI connection failed: ') + (r.message?.error || 'Unknown error'),
                    indicator: 'red'
                });
            }
        }
    });
}

function show_ai_status(frm) {
    let status_html = '<div style="margin-top: 10px;">';
    
    if (frm.doc.enable_openrouter) {
        status_html += '<span class="indicator green">Open Router AI Enabled</span><br>';
    }
    
    if (frm.doc.enable_azure) {
        status_html += '<span class="indicator green">Azure OpenAI Enabled</span><br>';
    }
    
    if (!frm.doc.enable_openrouter && !frm.doc.enable_azure) {
        status_html += '<span class="indicator red">No AI Provider Enabled</span><br>';
    }
    
    if (frm.doc.default_ai_provider) {
        status_html += '<span class="indicator blue">Default Provider: ' + frm.doc.default_ai_provider.toUpperCase() + '</span>';
    }
    
    status_html += '</div>';
    
    frm.dashboard.add_comment(status_html, 'blue', true);
}
