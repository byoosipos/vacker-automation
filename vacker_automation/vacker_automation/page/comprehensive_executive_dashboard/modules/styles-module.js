/**
 * Styles Module - All CSS styles for the Comprehensive Executive Dashboard
 * Separated from main file for better maintainability
 */
class StylesModule {
    constructor() {
        this.inject_styles();
        console.log('🎨 StylesModule initialized and styles injected');
    }

    inject_styles() {
        try {
            if (document.getElementById('comprehensive-dashboard-styles')) {
                console.log('Styles already injected, skipping');
                return; // Styles already injected
            }

            const style = document.createElement('style');
            style.id = 'comprehensive-dashboard-styles';
            style.type = 'text/css';
            
            // Safely set styles content
            const stylesContent = this.get_all_styles();
            if (stylesContent && typeof stylesContent === 'string') {
                style.textContent = stylesContent;
                document.head.appendChild(style);
                
                // Add a global flag to confirm styles were injected
                window.DASHBOARD_STYLES_INJECTED = true;
                console.log('✅ Dashboard styles injected successfully');
                
                // Force re-render to ensure styles are applied
                setTimeout(() => {
                    if (frappe.comprehensive_dashboard) {
                        console.log('Refreshing dashboard display...');
                        $('.dashboard-content').css('visibility', 'visible');
                    }
                }, 500);
            } else {
                console.error('Failed to get styles content');
            }
        } catch (error) {
            console.error('Error injecting styles:', error);
        }
    }

    get_all_styles() {
        return `
            /* =====================================
               COMPREHENSIVE EXECUTIVE DASHBOARD STYLES
               ===================================== */

            /* Base Dashboard Styles */
            .chatgpt-dashboard {
                width: 100%;
                height: 100vh;
                display: flex;
                flex-direction: column;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #ffffff;
                color: #374151;
                overflow: hidden;
            }

            /* Mobile Header */
            .mobile-header {
                display: none;
                justify-content: space-between;
                align-items: center;
                padding: 12px 16px;
                background: #ffffff;
                border-bottom: 1px solid #e5e7eb;
                position: relative;
                z-index: 100;
            }

            .mobile-menu-btn, .mobile-chat-btn {
                background: none;
                border: none;
                padding: 8px;
                border-radius: 6px;
                color: #374151;
                cursor: pointer;
                transition: background-color 0.2s;
            }

            .mobile-menu-btn:hover, .mobile-chat-btn:hover {
                background: #f3f4f6;
            }

            .mobile-title {
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 600;
                color: #10b981;
            }

            /* Desktop Header */
            .desktop-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 16px 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                background-size: 200% 200%;
                animation: gradient-shift 8s ease infinite;
                color: white;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                position: relative;
                overflow: hidden;
            }

            .desktop-header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.05)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.03)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.04)"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grain)"/></svg>');
                pointer-events: none;
            }

            @keyframes gradient-shift {
                0%, 100% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
            }

            .header-left {
                display: flex;
                align-items: center;
                gap: 24px;
            }

            .sidebar-toggle {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 14px;
            }

            .sidebar-toggle:hover {
                background: rgba(255, 255, 255, 0.25);
                transform: translateY(-1px);
            }

            .header-center h1 {
                margin: 0;
                font-size: 24px;
                font-weight: 700;
                display: flex;
                align-items: center;
                gap: 12px;
                position: relative;
                z-index: 1;
            }

            .header-right {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .control-btn, .chat-history-toggle {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                border-radius: 6px;
                padding: 8px 12px;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 13px;
            }

            .control-btn:hover, .chat-history-toggle:hover {
                background: rgba(255, 255, 255, 0.25);
                transform: translateY(-1px);
            }

            /* Main Content Area */
            .dashboard-main-content {
                flex: 1;
                display: flex;
                overflow: hidden;
                padding-top: 0;
            }

            /* Modules Sidebar */
            .modules-sidebar {
                width: 280px;
                background: #ffffff;
                border-right: 1px solid #e5e7eb;
                display: flex;
                flex-direction: column;
                transition: transform 0.3s ease;
                overflow-y: auto;
                box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
            }

            .sidebar-header {
                padding: 20px;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            }

            .sidebar-header h3 {
                margin: 0;
                color: #1f2937;
                font-size: 18px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .sidebar-close {
                background: none;
                border: none;
                color: #6b7280;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: all 0.2s;
            }

            .sidebar-close:hover {
                background: #f3f4f6;
                color: #374151;
            }

            /* Modules Menu */
            .modules-menu {
                flex: 1;
                padding: 16px;
            }

            .priority-modules {
                margin-bottom: 24px;
            }

            .priority-modules h4 {
                margin: 0 0 12px;
                color: #6b7280;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .other-modules h4 {
                margin: 0 0 12px;
                color: #6b7280;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .module-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s;
                margin-bottom: 4px;
                border: 1px solid transparent;
            }

            .module-item:hover {
                background: #f9fafb;
                border-color: #e5e7eb;
                transform: translateX(2px);
            }

            .module-item.active {
                background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                border-color: #10b981;
                color: #065f46;
                font-weight: 500;
            }

            .module-item.priority {
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                border-color: #f59e0b;
                color: #92400e;
                font-weight: 500;
            }

            .module-item i {
                width: 20px;
                text-align: center;
                font-size: 16px;
            }

            /* Central Content */
            .central-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                margin-left: 0;
                margin-right: 0;
                transition: margin 0.3s ease;
            }

            .dashboard-content {
                flex: 1;
                overflow-y: auto;
                padding: 24px;
                background: #ffffff;
                scroll-behavior: smooth;
            }

            /* Chat History Sidebar */
            .chat-history-sidebar {
                width: 320px;
                background: #ffffff;
                border-left: 1px solid #e5e7eb;
                display: flex;
                flex-direction: column;
                transition: transform 0.3s ease;
                overflow-y: auto;
                box-shadow: -2px 0 8px rgba(0, 0, 0, 0.05);
            }

            .chat-history-header {
                padding: 20px;
                border-bottom: 1px solid #e5e7eb;
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            }

            .chat-history-header h3 {
                margin: 0;
                color: #1f2937;
                font-size: 16px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .chat-sessions {
                flex: 1;
                padding: 16px;
            }

            .chat-session-item {
                padding: 12px;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s;
                margin-bottom: 8px;
                border: 1px solid transparent;
            }

            .chat-session-item:hover {
                background: #f9fafb;
                border-color: #e5e7eb;
            }

            .chat-session-item.active {
                background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                border-color: #10b981;
            }

            .session-title {
                font-weight: 500;
                color: #1f2937;
                font-size: 14px;
                margin-bottom: 4px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 200px;
            }

            .session-time {
                color: #6b7280;
                font-size: 12px;
            }

            .session-preview {
                color: #9ca3af;
                font-size: 12px;
                margin-top: 4px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            /* AI Chat Interface Styles */
            .ai-chat-interface {
                height: 100%;
                display: flex;
                flex-direction: column;
                max-width: 800px;
                margin: 0 auto;
                background: #1f2937;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            }

            /* Fullscreen Chat Styles */
            .ai-chat-fullscreen {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                max-width: none !important;
                margin: 0 !important;
                border-radius: 0 !important;
                z-index: 9999 !important;
            }

            body.chat-fullscreen-mode {
                overflow: hidden;
            }

            body.chat-fullscreen-mode .desktop-header,
            body.chat-fullscreen-mode .mobile-header,
            body.chat-fullscreen-mode .modules-sidebar,
            body.chat-fullscreen-mode .chat-history-sidebar {
                display: none !important;
            }

            /* Chat Header */
            .chat-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 16px 24px;
                background: #374151;
                border-bottom: 1px solid #4b5563;
                color: #f9fafb;
            }

            .ai-status {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .ai-avatar-mini {
                width: 32px;
                height: 32px;
                background: linear-gradient(135deg, #10b981, #34d399);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 14px;
            }

            .ai-info {
                display: flex;
                flex-direction: column;
            }

            .ai-name {
                font-weight: 600;
                font-size: 14px;
                color: #f9fafb;
            }

            .ai-status-text {
                font-size: 12px;
                color: #10b981;
            }

            .chat-header-right {
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .header-btn {
                background: #4b5563;
                border: 1px solid #6b7280;
                color: #d1d5db;
                border-radius: 6px;
                padding: 8px;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 32px;
                height: 32px;
            }

            .header-btn:hover {
                background: #6b7280;
                color: #f9fafb;
            }

            /* Chat Container */
            .chat-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }

            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 24px;
                scroll-behavior: smooth;
                background: #1f2937;
                color: #f9fafb;
            }

            .chat-messages::-webkit-scrollbar {
                width: 4px;
            }

            .chat-messages::-webkit-scrollbar-track {
                background: #374151;
            }

            .chat-messages::-webkit-scrollbar-thumb {
                background: #6b7280;
                border-radius: 2px;
            }

            /* Welcome Container */
            .welcome-container {
                text-align: center;
                max-width: 600px;
                margin: 40px auto;
                padding: 0 20px;
            }

            .ai-avatar {
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, #10b981, #34d399);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 24px;
                color: white;
                font-size: 32px;
            }

            .welcome-content h2 {
                margin: 0 0 16px;
                color: #f9fafb;
                font-size: 28px;
                font-weight: 600;
            }

            .welcome-content p {
                color: #d1d5db;
                font-size: 16px;
                line-height: 1.6;
                margin: 0 0 24px;
            }

            .capabilities-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                gap: 16px;
                margin: 24px 0;
            }

            .capability {
                padding: 16px;
                background: #374151;
                border-radius: 8px;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
                text-align: center;
                border: 1px solid #4b5563;
                transition: all 0.2s;
            }

            .capability:hover {
                background: #4b5563;
                border-color: #10b981;
                transform: translateY(-2px);
            }

            .capability i {
                color: #10b981;
                font-size: 24px;
            }

            .capability span {
                color: #f9fafb;
                font-size: 14px;
                font-weight: 500;
            }

            /* Example Prompts */
            .example-prompts {
                margin-top: 32px;
                text-align: left;
            }

            .example-prompts h4 {
                color: #f9fafb;
                font-size: 16px;
                margin-bottom: 16px;
                text-align: center;
            }

            .prompt-examples {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .prompt {
                background: #374151;
                border: 1px solid #4b5563;
                border-radius: 8px;
                padding: 12px 16px;
                color: #d1d5db;
                cursor: pointer;
                transition: all 0.2s;
                font-style: italic;
            }

            .prompt:hover {
                background: #4b5563;
                border-color: #10b981;
                color: #f9fafb;
            }

            /* Chat Messages */
            .chat-message {
                display: flex;
                margin-bottom: 24px;
                animation: fadeInUp 0.3s ease-out;
            }

            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(12px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .user-message {
                flex-direction: row-reverse;
            }

            .message-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                margin: 0 12px;
                font-size: 16px;
                color: white;
            }

            .ai-message .message-avatar {
                background: linear-gradient(135deg, #10b981, #34d399);
            }

            .user-message .message-avatar {
                background: linear-gradient(135deg, #3b82f6, #60a5fa);
            }

            .message-content {
                max-width: 70%;
                background: #374151;
                padding: 12px 16px;
                border-radius: 16px;
                position: relative;
                color: #f9fafb;
            }

            .user-message .message-content {
                background: #3b82f6;
                color: white;
            }

            .message-text {
                line-height: 1.5;
                font-size: 14px;
                margin-bottom: 6px;
                word-wrap: break-word;
            }

            .message-text code {
                background: rgba(0, 0, 0, 0.3);
                padding: 2px 4px;
                border-radius: 4px;
                font-family: 'Monaco', 'Consolas', monospace;
                font-size: 13px;
            }

            .message-text pre {
                background: rgba(0, 0, 0, 0.3);
                padding: 12px;
                border-radius: 6px;
                overflow-x: auto;
                margin: 8px 0;
            }

            .message-text strong {
                font-weight: 600;
            }

            .message-text em {
                font-style: italic;
            }

            .message-time {
                color: #9ca3af;
                font-size: 11px;
                opacity: 0.7;
            }

            .user-message .message-time {
                color: rgba(255, 255, 255, 0.7);
            }

            /* Typing Indicator */
            .typing-indicator .message-content {
                background: #4b5563;
                padding: 16px;
                color: #f9fafb;
            }

            .typing-animation {
                display: flex;
                gap: 4px;
                align-items: center;
            }

            .typing-animation span {
                width: 8px;
                height: 8px;
                background: #10b981;
                border-radius: 50%;
                animation: typing 1.4s infinite ease-in-out;
            }

            .typing-animation span:nth-child(1) { animation-delay: 0s; }
            .typing-animation span:nth-child(2) { animation-delay: 0.2s; }
            .typing-animation span:nth-child(3) { animation-delay: 0.4s; }

            @keyframes typing {
                0%, 80%, 100% {
                    transform: scale(0.8);
                    opacity: 0.5;
                }
                40% {
                    transform: scale(1.2);
                    opacity: 1;
                }
            }

            /* Chat Input Area */
            .chat-input-area {
                border-top: 1px solid #4b5563;
                background: #374151;
                padding: 16px 24px;
            }

            .chat-features {
                display: flex;
                gap: 8px;
                margin-bottom: 12px;
                flex-wrap: wrap;
            }

            .feature-btn {
                background: #4b5563;
                border: 1px solid #6b7280;
                color: #d1d5db;
                border-radius: 6px;
                padding: 6px 10px;
                cursor: pointer;
                transition: all 0.2s;
                font-size: 13px;
                display: flex;
                align-items: center;
                gap: 6px;
            }

            .feature-btn:hover {
                background: #6b7280;
                color: #f9fafb;
            }

            .feature-btn.active {
                background: #10b981;
                border-color: #10b981;
                color: #ffffff;
            }

            .input-container {
                display: flex;
                gap: 12px;
                align-items: flex-end;
                margin-bottom: 12px;
            }

            #chat-input {
                flex: 1;
                border: 1px solid #6b7280;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                line-height: 1.5;
                resize: none;
                min-height: 20px;
                max-height: 120px;
                font-family: inherit;
                background: #4b5563;
                color: #f9fafb;
                transition: border-color 0.2s, box-shadow 0.2s;
            }

            #chat-input:focus {
                outline: none;
                border-color: #10b981;
                box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
            }

            #chat-input::placeholder {
                color: #9ca3af;
            }

            .send-btn {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 10px;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: background-color 0.2s;
                flex-shrink: 0;
            }

            .send-btn:hover {
                background: #059669;
            }

            .send-btn:disabled {
                background: #6b7280;
                cursor: not-allowed;
            }

            .quick-actions {
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                justify-content: center;
            }

            .quick-btn {
                background: #4b5563;
                border: 1px solid #6b7280;
                color: #d1d5db;
                border-radius: 20px;
                padding: 6px 12px;
                cursor: pointer;
                transition: all 0.2s;
                font-size: 13px;
            }

            .quick-btn:hover {
                background: #6b7280;
                border-color: #10b981;
                color: #10b981;
            }

            /* Dashboard Content Styles */
            .loading-state {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 60px;
                color: #374151;
                font-size: 16px;
                gap: 12px;
                background: #ffffff;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                border: 1px solid #f3f4f6;
            }

            .executive-overview, .financial-dashboard, .projects-dashboard,
            .hr-dashboard, .sales-dashboard, .materials-dashboard,
            .bank-cash-dashboard, .purchase-orders-dashboard,
            .operations-dashboard, .risk-management-dashboard {
                padding: 0;
                max-width: 1200px;
                margin: 0 auto;
            }

            .dashboard-header {
                text-align: center;
                margin-bottom: 32px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 32px;
                border-radius: 12px;
                color: white;
                position: relative;
                overflow: hidden;
            }

            .dashboard-header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.05)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.03)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.04)"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grain)"/></svg>');
                pointer-events: none;
            }

            .dashboard-header h1 {
                margin: 0 0 12px;
                font-size: 32px;
                font-weight: 700;
                position: relative;
                z-index: 1;
            }

            .dashboard-header p {
                margin: 0;
                font-size: 16px;
                opacity: 0.9;
                position: relative;
                z-index: 1;
            }

            /* KPI Cards and Metrics */
            .kpi-cards, .financial-metrics, .project-metrics,
            .hr-metrics, .sales-metrics, .material-metrics,
            .cash-metrics, .po-metrics, .operations-metrics,
            .risk-metrics {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 32px;
            }

            .kpi-card, .metric-card {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 24px;
                text-align: center;
                transition: all 0.3s ease;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                position: relative;
                overflow: hidden;
            }

            .kpi-card:hover, .metric-card:hover {
                border-color: #10b981;
                transform: translateY(-4px);
                box-shadow: 0 8px 24px rgba(16, 185, 129, 0.15);
            }

            .kpi-card::before, .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #10b981, #34d399);
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .kpi-card:hover::before, .metric-card:hover::before {
                opacity: 1;
            }

            .metric-icon {
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #10b981, #34d399);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 16px;
                color: white;
                font-size: 24px;
            }

            .metric-value {
                font-size: 28px;
                font-weight: 700;
                color: #1f2937;
                margin-bottom: 8px;
            }

            .metric-label {
                color: #6b7280;
                font-size: 14px;
                font-weight: 500;
            }

            .metric-change {
                display: inline-flex;
                align-items: center;
                gap: 4px;
                font-size: 12px;
                font-weight: 500;
                margin-top: 8px;
                padding: 2px 8px;
                border-radius: 12px;
            }

            .metric-change.positive {
                color: #065f46;
                background: #d1fae5;
            }

            .metric-change.negative {
                color: #991b1b;
                background: #fee2e2;
            }

            /* Chart Sections */
            .chart-section, .sales-chart-section, .cashflow-chart-section,
            .po-status-section, .operations-chart-section, .risk-chart-section {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 24px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }

            .chart-section h3, .sales-chart-section h3, .cashflow-chart-section h3,
            .po-status-section h3, .operations-chart-section h3, .risk-chart-section h3 {
                margin: 0 0 20px;
                color: #1f2937;
                font-size: 18px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
                padding-bottom: 12px;
                border-bottom: 2px solid #f3f4f6;
            }

            .chart-container, .status-charts {
                position: relative;
                height: 300px;
                margin-top: 16px;
            }

            .chart-container canvas, .status-charts canvas {
                max-width: 100%;
                height: auto;
            }

            /* Tables */
            .activity-table, .projects-table, .employees-table,
            .customers-table, .inventory-table, .accounts-table,
            .po-table, .work-orders-table, .incidents-table {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }

            .table-header {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 16px;
                padding: 16px 20px;
                background: #f9fafb;
                border-bottom: 1px solid #e5e7eb;
                font-weight: 600;
                color: #374151;
                font-size: 14px;
            }

            .table-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 16px;
                padding: 16px 20px;
                border-bottom: 1px solid #f3f4f6;
                transition: background-color 0.2s;
                align-items: center;
                font-size: 14px;
            }

            .table-row:hover {
                background: #f9fafb;
            }

            .table-row:last-child {
                border-bottom: none;
            }

            /* Status Indicators */
            .status {
                display: inline-flex;
                align-items: center;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
            }

            .status.active, .status.on-track, .status.completed {
                color: #065f46;
                background: #d1fae5;
            }

            .status.pending, .status.at-risk {
                color: #92400e;
                background: #fef3c7;
            }

            .status.overdue, .status.delayed {
                color: #991b1b;
                background: #fee2e2;
            }

            .priority {
                display: inline-flex;
                align-items: center;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
            }

            .priority.high {
                color: #991b1b;
                background: #fee2e2;
            }

            .priority.medium {
                color: #92400e;
                background: #fef3c7;
            }

            .priority.low {
                color: #065f46;
                background: #d1fae5;
            }

            /* Balance indicators */
            .balance.positive {
                color: #065f46;
                font-weight: 600;
            }

            .balance.negative {
                color: #991b1b;
                font-weight: 600;
            }

            /* No data states */
            .no-data {
                text-align: center;
                padding: 40px;
                color: #6b7280;
                font-style: italic;
            }

            /* Mobile Responsive Styles */
            @media (max-width: 768px) {
                .mobile-header {
                    display: flex;
                }

                .desktop-header {
                    display: none;
                }

                .dashboard-main-content {
                    padding-top: 0;
                }

                .modules-sidebar,
                .chat-history-sidebar {
                    position: fixed;
                    top: 0;
                    height: 100vh;
                    z-index: 1000;
                    width: 280px;
                }

                .modules-sidebar {
                    left: -280px;
                    transform: none;
                }

                .chat-history-sidebar {
                    right: -320px;
                    width: 320px;
                }

                .chatgpt-dashboard.modules-open .modules-sidebar {
                    left: 0;
                }

                .chatgpt-dashboard.chat-open .chat-history-sidebar {
                    right: 0;
                }

                .central-content {
                    margin: 0 !important;
                }

                .mobile-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                    background: rgba(0, 0, 0, 0.6);
                    opacity: 0;
                    visibility: hidden;
                    transition: all 0.3s ease;
                    z-index: 990;
                    backdrop-filter: blur(4px);
                }

                .mobile-overlay.active {
                    opacity: 1;
                    visibility: visible;
                }

                .ai-chat-interface {
                    margin: 0;
                    border-radius: 0;
                    height: calc(100vh - 60px);
                }

                .dashboard-content {
                    padding: 16px;
                }

                .chat-input-area {
                    padding: 12px 16px;
                }

                .capabilities-grid {
                    grid-template-columns: 1fr 1fr;
                }

                .quick-actions {
                    justify-content: center;
                }

                .chat-message {
                    margin-bottom: 16px;
                }

                .message-content {
                    max-width: 85%;
                }

                .message-avatar {
                    width: 32px;
                    height: 32px;
                    margin: 0 8px;
                    font-size: 14px;
                }

                .kpi-cards, .financial-metrics, .project-metrics,
                .hr-metrics, .sales-metrics, .material-metrics,
                .cash-metrics, .po-metrics, .operations-metrics,
                .risk-metrics {
                    grid-template-columns: 1fr 1fr;
                    gap: 12px;
                }

                .session-title {
                    max-width: 140px;
                }

                .table-header, .table-row {
                    font-size: 12px;
                    padding: 12px 16px;
                }

                .dashboard-header {
                    padding: 24px 16px;
                }

                .dashboard-header h1 {
                    font-size: 24px;
                }

                .chart-container, .status-charts {
                    height: 250px;
                }
            }

            /* Focus states for accessibility */
            .module-item:focus,
            .chat-session-item:focus,
            .feature-btn:focus,
            .quick-btn:focus,
            .send-btn:focus,
            .header-btn:focus {
                outline: 2px solid #10b981;
                outline-offset: 2px;
            }

            /* Animations */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes slideInFromLeft {
                from { transform: translateX(-100%); }
                to { transform: translateX(0); }
            }

            @keyframes slideInFromRight {
                from { transform: translateX(100%); }
                to { transform: translateX(0); }
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }

            /* Utility Classes */
            .fade-in {
                animation: fadeIn 0.3s ease-out;
            }

            .slide-in-left {
                animation: slideInFromLeft 0.3s ease-out;
            }

            .slide-in-right {
                animation: slideInFromRight 0.3s ease-out;
            }

            .pulse {
                animation: pulse 2s infinite;
            }

            /* Hidden utility */
            .hidden {
                display: none !important;
            }

            /* Print styles */
            @media print {
                .mobile-header,
                .desktop-header,
                .modules-sidebar,
                .chat-history-sidebar,
                .chat-input-area {
                    display: none !important;
                }

                .dashboard-content {
                    padding: 0 !important;
                }

                .ai-chat-interface {
                    background: white !important;
                    color: black !important;
                }

                .chat-messages {
                    background: white !important;
                    color: black !important;
                }
            }
        `;
    }
}

// Auto-inject styles when module is loaded
if (typeof window !== 'undefined') {
    window.StylesModule = StylesModule;
    new StylesModule();
}

// Export for use in main dashboard
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StylesModule;
}
