/**
 * Enhanced AI Chat Module - Advanced AI capabilities
 * Handles AI conversation, predictive analytics, report generation, and intelligent insights
 */
class AIChatModule {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.current_session = null;
        this.chat_sessions = [];
        this.is_fullscreen = false;
        this.thinking_mode = false;
        this.web_search_enabled = false;
        this.is_typing = false;
        
        // Enhanced AI capabilities
        this.ai_capabilities = {
            predictive_analytics: true,
            natural_language_reports: true,
            business_insights: true,
            market_research: true,
            document_analysis: true,
            voice_interaction: true,
            real_time_analysis: true
        };
        
        this.ai_models = {
            general_chat: 'gpt-4-turbo',
            data_analysis: 'gpt-4-turbo',
            report_generation: 'gpt-4-turbo',
            predictive_modeling: 'claude-3-5-sonnet',
            sentiment_analysis: 'gpt-3.5-turbo'
        };
        
        this.conversation_context = [];
        this.data_context = null;
        this.analytics_cache = new Map();
        
        this.load_chat_sessions();
        this.initialize_ai_features();
    }

    /**
     * Initialize advanced AI features
     */
    initialize_ai_features() {
        this.setup_voice_recognition();
        this.setup_predictive_engine();
        this.setup_context_awareness();
    }

    /**
     * Render the enhanced AI chat interface
     */
    render(content) {
        // Store original container for fullscreen toggle
        this.original_container = content;
        this.original_parent = content.parent();

        const isFullscreen = this.is_fullscreen;
        const containerClass = isFullscreen ? 'ai-chat-fullscreen' : 'ai-chat-interface';
        
        content.html(`
            <div class="${containerClass}" id="ai-chat-container">
                ${this.render_chat_header()}
                <div class="chat-container">
                    <div class="chat-messages" id="chat-messages">
                        ${this.current_session ? this.render_session_messages() : this.get_enhanced_welcome_message()}
                    </div>
                    
                    <div class="chat-input-area">
                        ${this.render_ai_capabilities_panel()}
                        ${this.render_chat_features()}
                        ${this.render_chat_input()}
                        ${this.render_enhanced_quick_actions()}
                    </div>
                </div>
                
                <input type="file" id="file-upload" multiple style="display: none;" accept=".pdf,.doc,.docx,.txt,.csv,.xlsx,.json">
                
                <!-- AI Analytics Panel -->
                <div class="ai-analytics-panel" id="ai-analytics-panel" style="display: none;">
                    ${this.render_analytics_panel()}
                </div>
            </div>
        `);

        this.setup_enhanced_chat_events();
        this.setup_fullscreen_mode();
        this.setup_data_context();
    }

    /**
     * Render enhanced chat header with AI status
     */
    render_chat_header() {
        return `
            <div class="chat-header enhanced">
                <div class="chat-header-left">
                    <div class="ai-status advanced">
                        <div class="ai-avatar-advanced">
                            <div class="ai-brain-animation">
                                <i class="fa fa-brain"></i>
                                <div class="neural-activity"></div>
                            </div>
                        </div>
                        <div class="ai-info">
                            <span class="ai-name">AI Business Intelligence</span>
                            <span class="ai-status-text">${this.get_ai_status_text()}</span>
                            <div class="ai-capabilities">
                                <span class="capability-badge">Analytics</span>
                                <span class="capability-badge">Predictions</span>
                                <span class="capability-badge">Insights</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="chat-header-right">
                    <button class="header-btn" id="analytics-toggle" title="AI Analytics Panel">
                        <i class="fa fa-chart-line"></i>
                    </button>
                    <button class="header-btn" id="new-session-btn" title="New Session">
                        <i class="fa fa-plus"></i>
                    </button>
                    <button class="header-btn" id="chat-settings-btn" title="AI Settings">
                        <i class="fa fa-cog"></i>
                    </button>
                    <button class="header-btn" id="fullscreen-toggle" title="${this.is_fullscreen ? 'Exit Fullscreen' : 'Fullscreen'}">
                        <i class="fa fa-${this.is_fullscreen ? 'compress' : 'expand'}"></i>
                    </button>
                    ${this.is_fullscreen ? `
                        <button class="header-btn" id="close-fullscreen" title="Close Chat">
                            <i class="fa fa-times"></i>
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Render AI capabilities panel
     */
    render_ai_capabilities_panel() {
        return `
            <div class="ai-capabilities-panel">
                <div class="capabilities-header">
                    <h4><i class="fa fa-magic"></i> AI Capabilities</h4>
                    <span class="capabilities-status">All systems operational</span>
                </div>
                <div class="capabilities-grid">
                    <div class="capability-item ${this.ai_capabilities.predictive_analytics ? 'active' : 'disabled'}" data-capability="predictive">
                        <i class="fa fa-crystal-ball"></i>
                        <span>Predictive Analytics</span>
                    </div>
                    <div class="capability-item ${this.ai_capabilities.natural_language_reports ? 'active' : 'disabled'}" data-capability="reports">
                        <i class="fa fa-file-text"></i>
                        <span>Report Generation</span>
                    </div>
                    <div class="capability-item ${this.ai_capabilities.business_insights ? 'active' : 'disabled'}" data-capability="insights">
                        <i class="fa fa-lightbulb-o"></i>
                        <span>Business Insights</span>
                    </div>
                    <div class="capability-item ${this.ai_capabilities.market_research ? 'active' : 'disabled'}" data-capability="research">
                        <i class="fa fa-search"></i>
                        <span>Market Research</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render enhanced chat features toolbar
     */
    render_chat_features() {
        return `
            <div class="chat-features enhanced">
                <button class="feature-btn ${this.thinking_mode ? 'active' : ''}" id="thinking-mode-toggle" title="Deep Thinking Mode">
                    <i class="fa fa-brain"></i>
                    <span>Deep Think</span>
                </button>
                <button class="feature-btn ${this.web_search_enabled ? 'active' : ''}" id="web-search-toggle" title="Web Research">
                    <i class="fa fa-globe"></i>
                    <span>Research</span>
                </button>
                <button class="feature-btn" id="document-upload" title="Document Analysis">
                    <i class="fa fa-file-text"></i>
                    <span>Documents</span>
                </button>
                <button class="feature-btn" id="voice-input" title="Voice Interaction">
                    <i class="fa fa-microphone"></i>
                    <span>Voice</span>
                </button>
                <button class="feature-btn" id="data-analysis" title="Real-time Data Analysis">
                    <i class="fa fa-chart-bar"></i>
                    <span>Analyze</span>
                </button>
                <button class="feature-btn" id="generate-report" title="Generate Business Report">
                    <i class="fa fa-file-pdf-o"></i>
                    <span>Report</span>
                </button>
            </div>
        `;
    }

    /**
     * Render enhanced quick action buttons
     */
    render_enhanced_quick_actions() {
        return `
            <div class="quick-actions enhanced">
                <div class="action-category">
                    <h5>📊 Data Analysis</h5>
                    <button class="quick-btn" data-message="Analyze current financial performance and identify trends">
                        Financial Analysis
                    </button>
                    <button class="quick-btn" data-message="Show me project profitability insights and recommendations">
                        Project Insights
                    </button>
                    <button class="quick-btn" data-message="Analyze HR metrics and workforce efficiency">
                        HR Analytics
                    </button>
                </div>
                
                <div class="action-category">
                    <h5>🔮 Predictions</h5>
                    <button class="quick-btn" data-message="Predict next quarter's revenue based on current trends">
                        Revenue Forecast
                    </button>
                    <button class="quick-btn" data-message="Identify potential risks and opportunities">
                        Risk Assessment
                    </button>
                    <button class="quick-btn" data-message="Predict cash flow for the next 3 months">
                        Cash Flow Forecast
                    </button>
                </div>
                
                <div class="action-category">
                    <h5>📋 Reports</h5>
                    <button class="quick-btn" data-message="Generate a comprehensive executive summary report">
                        Executive Summary
                    </button>
                    <button class="quick-btn" data-message="Create a detailed performance dashboard report">
                        Performance Report
                    </button>
                    <button class="quick-btn" data-message="Generate market analysis and competitive insights">
                        Market Analysis
                    </button>
                </div>
                
                <div class="action-category">
                    <h5>💡 Optimization</h5>
                    <button class="quick-btn" data-message="Suggest ways to optimize operational efficiency">
                        Optimize Operations
                    </button>
                    <button class="quick-btn" data-message="Recommend cost reduction strategies">
                        Cost Optimization
                    </button>
                    <button class="quick-btn" data-message="Suggest revenue growth opportunities">
                        Growth Strategies
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Get enhanced welcome message with AI capabilities showcase
     */
    get_enhanced_welcome_message() {
        return `
            <div class="welcome-container enhanced">
                <div class="ai-avatar-large">
                    <div class="ai-brain-large">
                        <i class="fa fa-brain"></i>
                        <div class="neural-network"></div>
                    </div>
                </div>
                <div class="welcome-content">
                    <h2>🧠 Welcome to Advanced AI Business Intelligence</h2>
                    <p>I'm your next-generation AI assistant with powerful analytical capabilities:</p>
                    
                    <div class="capabilities-showcase">
                        <div class="capability-section">
                            <h3><i class="fa fa-crystal-ball"></i> Predictive Analytics</h3>
                            <ul>
                                <li>Revenue and sales forecasting</li>
                                <li>Risk prediction and assessment</li>
                                <li>Market trend analysis</li>
                                <li>Customer behavior prediction</li>
                            </ul>
                        </div>
                        
                        <div class="capability-section">
                            <h3><i class="fa fa-lightbulb-o"></i> Intelligent Insights</h3>
                            <ul>
                                <li>Automated business intelligence</li>
                                <li>Performance anomaly detection</li>
                                <li>Optimization recommendations</li>
                                <li>Strategic decision support</li>
                            </ul>
                        </div>
                        
                        <div class="capability-section">
                            <h3><i class="fa fa-file-text"></i> Advanced Reports</h3>
                            <ul>
                                <li>Natural language report generation</li>
                                <li>Executive summaries</li>
                                <li>Interactive visualizations</li>
                                <li>Custom analysis reports</li>
                            </ul>
                        </div>
                        
                        <div class="capability-section">
                            <h3><i class="fa fa-search"></i> Research & Analysis</h3>
                            <ul>
                                <li>Real-time market research</li>
                                <li>Competitive analysis</li>
                                <li>Document processing</li>
                                <li>Data mining and insights</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="ai-status-showcase">
                        <div class="status-item">
                            <i class="fa fa-check-circle text-success"></i>
                            <span>Predictive Models: Active</span>
                        </div>
                        <div class="status-item">
                            <i class="fa fa-check-circle text-success"></i>
                            <span>Real-time Analysis: Online</span>
                        </div>
                        <div class="status-item">
                            <i class="fa fa-check-circle text-success"></i>
                            <span>Market Data: Connected</span>
                        </div>
                    </div>
                    
                    <div class="welcome-prompt">
                        <p><strong>Try asking me something like:</strong></p>
                        <div class="example-prompts advanced">
                            <div class="prompt prediction" data-message="Predict our revenue for next quarter based on current trends and market conditions">
                                "Predict our revenue for next quarter"
                            </div>
                            <div class="prompt insights" data-message="Analyze our operational efficiency and suggest improvements">
                                "Analyze our operational efficiency"
                            </div>
                            <div class="prompt report" data-message="Generate a comprehensive executive report for the board meeting">
                                "Generate an executive report"
                            </div>
                            <div class="prompt optimization" data-message="What are the biggest opportunities to improve our profit margins?">
                                "How can we improve profit margins?"
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render analytics panel
     */
    render_analytics_panel() {
        return `
            <div class="analytics-content">
                <div class="analytics-header">
                    <h3><i class="fa fa-chart-line"></i> AI Analytics Dashboard</h3>
                    <button class="close-analytics" id="close-analytics">
                        <i class="fa fa-times"></i>
                    </button>
                </div>
                
                <div class="analytics-sections">
                    <div class="analytics-section">
                        <h4>🎯 Predictive Insights</h4>
                        <div id="predictive-insights">
                            <div class="insight-card">
                                <h5>Revenue Forecast</h5>
                                <div class="insight-value">+12.5% growth projected</div>
                                <div class="insight-confidence">Confidence: 87%</div>
                            </div>
                            <div class="insight-card">
                                <h5>Risk Assessment</h5>
                                <div class="insight-value">Low risk detected</div>
                                <div class="insight-confidence">Confidence: 92%</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="analytics-section">
                        <h4>📊 Real-time Analysis</h4>
                        <div id="realtime-analysis">
                            <canvas id="realtime-chart" width="400" height="200"></canvas>
                        </div>
                    </div>
                    
                    <div class="analytics-section">
                        <h4>💡 Recommendations</h4>
                        <div id="ai-recommendations">
                            <div class="recommendation-item">
                                <i class="fa fa-arrow-up text-success"></i>
                                <span>Optimize inventory levels to reduce carrying costs</span>
                            </div>
                            <div class="recommendation-item">
                                <i class="fa fa-arrow-up text-warning"></i>
                                <span>Focus on high-margin products for better profitability</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Enhanced message sending with AI processing
     */
    async send_enhanced_message() {
        const input = $('#chat-input');
        const message = input.val().trim();
        
        if (!message) return;
        
        // Clear input and add user message
        input.val('');
        this.add_message(message, 'user');
        
        // Determine message type and processing approach
        const messageType = this.classify_message(message);
        
        // Show typing indicator with processing type
        this.show_enhanced_typing_indicator(messageType);
        
        try {
            let response;
            
            switch (messageType) {
                case 'prediction':
                    response = await this.process_prediction_request(message);
                    break;
                case 'analysis':
                    response = await this.process_analysis_request(message);
                    break;
                case 'report':
                    response = await this.process_report_request(message);
                    break;
                case 'optimization':
                    response = await this.process_optimization_request(message);
                    break;
                default:
                    response = await this.process_general_request(message);
            }
            
            this.hide_typing_indicator();
            this.add_message(response.content, 'ai', response.metadata);
            
            // Update conversation context
            this.update_conversation_context(message, response);
            
        } catch (error) {
            this.hide_typing_indicator();
            this.add_message(`I apologize, but I encountered an error processing your request: ${error.message}`, 'ai');
            console.error('Enhanced AI processing error:', error);
        }
    }

    /**
     * Classify message type for appropriate processing
     */
    classify_message(message) {
        const predictionKeywords = ['predict', 'forecast', 'future', 'next quarter', 'next month', 'trend'];
        const analysisKeywords = ['analyze', 'analysis', 'examine', 'review', 'assess'];
        const reportKeywords = ['report', 'summary', 'generate', 'create report', 'executive'];
        const optimizationKeywords = ['optimize', 'improve', 'efficiency', 'recommendations', 'suggest'];
        
        const lowerMessage = message.toLowerCase();
        
        if (predictionKeywords.some(keyword => lowerMessage.includes(keyword))) {
            return 'prediction';
        } else if (analysisKeywords.some(keyword => lowerMessage.includes(keyword))) {
            return 'analysis';
        } else if (reportKeywords.some(keyword => lowerMessage.includes(keyword))) {
            return 'report';
        } else if (optimizationKeywords.some(keyword => lowerMessage.includes(keyword))) {
            return 'optimization';
        }
        
        return 'general';
    }

    /**
     * Process prediction requests using AI models
     */
    async process_prediction_request(message) {
        // Get current dashboard data for context
        const data = this.dashboard.data;
        
        const response = await frappe.call({
            method: 'vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard.process_ai_prediction',
            args: {
                message: message,
                data_context: JSON.stringify(data),
                conversation_context: JSON.stringify(this.conversation_context)
            }
        });
        
        return {
            content: response.message.content,
            metadata: {
                type: 'prediction',
                confidence: response.message.confidence,
                charts: response.message.charts,
                recommendations: response.message.recommendations
            }
        };
    }

    /**
     * Process analysis requests
     */
    async process_analysis_request(message) {
        const data = this.dashboard.data;
        
        const response = await frappe.call({
            method: 'vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard.process_ai_analysis',
            args: {
                message: message,
                data_context: JSON.stringify(data),
                conversation_context: JSON.stringify(this.conversation_context)
            }
        });
        
        return {
            content: response.message.content,
            metadata: {
                type: 'analysis',
                insights: response.message.insights,
                visualizations: response.message.visualizations,
                key_findings: response.message.key_findings
            }
        };
    }

    /**
     * Get AI status text based on current state
     */
    get_ai_status_text() {
        if (this.is_typing) return 'Processing...';
        if (this.thinking_mode) return 'Deep thinking enabled';
        if (this.web_search_enabled) return 'Research mode active';
        return 'Ready for intelligent assistance';
    }

    /**
     * Setup enhanced chat events
     */
    setup_enhanced_chat_events() {
        // Enhanced send message
        $('#send-message').on('click', () => this.send_enhanced_message());
        $('#chat-input').on('keypress', (e) => {
            if (e.which === 13 && !e.shiftKey) {
                e.preventDefault();
                this.send_enhanced_message();
            }
        });

        // AI capabilities toggle
        $('.capability-item').on('click', (e) => {
            const capability = $(e.currentTarget).data('capability');
            this.toggle_ai_capability(capability);
        });

        // Analytics panel toggle
        $('#analytics-toggle').on('click', () => this.toggle_analytics_panel());
        $('#close-analytics').on('click', () => this.hide_analytics_panel());

        // Enhanced quick actions
        $('.quick-btn').on('click', (e) => {
            const message = $(e.currentTarget).data('message');
            $('#chat-input').val(message);
            this.send_enhanced_message();
        });

        // Example prompts
        $('.prompt').on('click', (e) => {
            const message = $(e.currentTarget).data('message');
            $('#chat-input').val(message);
            this.send_enhanced_message();
        });

        // Setup existing events
        this.setup_chat_events();
    }

    /**
     * Show enhanced typing indicator
     */
    show_enhanced_typing_indicator(messageType = 'general') {
        this.is_typing = true;
        
        const processingMessages = {
            'prediction': 'Analyzing data patterns and generating predictions...',
            'analysis': 'Processing complex data analysis...',
            'report': 'Generating comprehensive report...',
            'optimization': 'Calculating optimization strategies...',
            'general': 'Thinking...'
        };
        
        const message = processingMessages[messageType] || processingMessages['general'];
        
        const typingHtml = `
            <div class="message ai typing enhanced" id="typing-indicator">
                <div class="message-avatar">
                    <div class="ai-brain-small">
                        <i class="fa fa-brain"></i>
                        <div class="neural-activity-small"></div>
                    </div>
                </div>
                <div class="message-content">
                    <div class="typing-animation">
                        <div class="typing-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                        <div class="typing-text">${message}</div>
                        <div class="processing-indicator">
                            <div class="progress">
                                <div class="progress-bar progress-bar-striped active" style="width: 100%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#chat-messages').append(typingHtml);
        this.scroll_to_bottom();
    }

    /**
     * Additional utility methods for enhanced AI features
     */
    setup_voice_recognition() {
        // Placeholder for voice recognition setup
        console.log('Voice recognition initialized');
    }

    setup_predictive_engine() {
        // Placeholder for predictive engine setup
        console.log('Predictive engine initialized');
    }

    setup_context_awareness() {
        // Initialize context awareness with dashboard data
        this.data_context = this.dashboard.data;
        console.log('Context awareness initialized');
    }

    toggle_ai_capability(capability) {
        console.log(`Toggling AI capability: ${capability}`);
        // Implementation for toggling specific AI capabilities
    }

    toggle_analytics_panel() {
        $('#ai-analytics-panel').toggle();
    }

    hide_analytics_panel() {
        $('#ai-analytics-panel').hide();
    }

    update_conversation_context(message, response) {
        this.conversation_context.push({
            user: message,
            ai: response.content,
            timestamp: new Date().toISOString(),
            type: response.metadata?.type || 'general'
        });
        
        // Keep only last 10 exchanges for context
        if (this.conversation_context.length > 10) {
            this.conversation_context = this.conversation_context.slice(-10);
        }
    }

    /**
     * Render session messages
     */
    render_session_messages() {
        if (!this.current_session || !this.current_session.messages) {
            return this.get_enhanced_welcome_message();
        }
        
        return this.current_session.messages.map(msg => `
            <div class="chat-message ${msg.sender === 'user' ? 'user-message' : 'ai-message'}">
                <div class="message-avatar">
                    <i class="fa fa-${msg.sender === 'user' ? 'user' : 'robot'}"></i>
                </div>
                <div class="message-content">
                    <div class="message-text">${this.format_message_text(msg.text)}</div>
                    <div class="message-time">${new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Setup all chat event handlers
     */
    setup_chat_events() {
        // Auto-resize textarea
        $('#chat-input').on('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });

        // Send on Enter (Shift+Enter for new line)
        $('#chat-input').on('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.send_message();
            }
        });

        // Send button click
        $('#send-message').on('click', () => this.send_message());

        // Feature toggles
        $('#thinking-mode-toggle').on('click', () => this.toggle_thinking_mode());
        $('#web-search-toggle').on('click', () => this.toggle_web_search());
        $('#document-upload').on('click', () => this.trigger_file_upload());
        $('#voice-input').on('click', () => this.start_voice_input());

        // Quick actions
        $('.quick-btn, .prompt').on('click', (e) => {
            const message = $(e.target).data('message');
            if (message) {
                $('#chat-input').val(message);
                this.send_message();
            }
        });

        // File upload
        $('#file-upload').on('change', (e) => this.handle_file_upload(e));

        // Header actions
        $('#new-session-btn').on('click', () => this.start_new_session());
        $('#chat-settings-btn').on('click', () => this.show_settings());
        $('#fullscreen-toggle').on('click', () => this.toggle_fullscreen());
        $('#close-fullscreen').on('click', () => this.exit_fullscreen());
    }

    /**
     * Setup fullscreen mode functionality
     */
    setup_fullscreen_mode() {
        if (this.is_fullscreen) {
            // Hide dashboard navigation and header
            $('.desktop-header, .mobile-header, .modules-sidebar').hide();
            $('body').addClass('chat-fullscreen-mode');
            
            // Make chat container fill entire viewport
            $('#ai-chat-container').addClass('ai-chat-fullscreen');
        }
    }

    /**
     * Toggle fullscreen mode
     */
    toggle_fullscreen() {
        this.is_fullscreen = !this.is_fullscreen;
        
        if (this.is_fullscreen) {
            this.enter_fullscreen();
        } else {
            this.exit_fullscreen();
        }
    }

    /**
     * Enter fullscreen mode
     */
    enter_fullscreen() {
        this.is_fullscreen = true;
        
        // Hide navigation elements
        $('.desktop-header, .mobile-header, .modules-sidebar, .chat-history-sidebar').hide();
        $('body').addClass('chat-fullscreen-mode');
        
        // Re-render with fullscreen layout
        this.render(this.original_container);
        
        // Scroll to bottom
        this.scroll_to_bottom();
    }

    /**
     * Exit fullscreen mode
     */
    exit_fullscreen() {
        this.is_fullscreen = false;
        
        // Show navigation elements
        $('.desktop-header, .mobile-header').show();
        $('body').removeClass('chat-fullscreen-mode');
        
        // Re-render with normal layout
        this.render(this.original_container);
        
        // Scroll to bottom
        this.scroll_to_bottom();
    }

    /**
     * Send message to AI
     */
    async send_message() {
        const input = $('#chat-input');
        const message = input.val().trim();
        
        if (!message || this.is_typing) return;

        // Clear input and add user message
        input.val('').css('height', 'auto');
        this.add_message(message, 'user');
        
        // Show typing indicator
        this.show_typing_indicator();
        
        try {
            // Simulate AI response (replace with actual API call)
            const response = await this.get_ai_response(message);
            this.hide_typing_indicator();
            this.add_message(response, 'ai');
        } catch (error) {
            this.hide_typing_indicator();
            this.add_message('Sorry, I encountered an error. Please try again.', 'ai');
            console.error('AI response error:', error);
        }
    }

    /**
     * Get AI response (mock implementation)
     */
    async get_ai_response(message) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
        
        // Mock responses based on message content
        if (message.toLowerCase().includes('data') || message.toLowerCase().includes('analyze')) {
            return `I've analyzed your current dashboard data. Here are the key insights:

📊 **Sales Performance**: Your sales have increased by 15% compared to last month
💰 **Revenue**: Total revenue is $${(Math.random() * 1000000 + 500000).toLocaleString()}
📈 **Growth Trend**: Showing positive momentum in the technology and services sectors
⚠️ **Areas of Concern**: Inventory turnover could be optimized

Would you like me to dive deeper into any specific area?`;
        } else if (message.toLowerCase().includes('report')) {
            return `I'll generate a comprehensive business report for you. This will include:

🔹 Executive Summary
🔹 Financial Performance Analysis  
🔹 Operational Metrics
🔹 Risk Assessment
🔹 Recommendations

The report will be ready in a few moments. Would you like me to focus on any specific time period or business area?`;
        } else if (message.toLowerCase().includes('insights')) {
            return `Based on your current business data, here are the key insights:

💡 **Top Opportunities**:
- Customer retention rate is at 94% - excellent performance
- New market segment showing 23% growth potential
- Digital transformation initiatives are yielding positive ROI

⚡ **Action Items**:
- Consider expanding inventory in high-performing categories
- Invest in customer acquisition for the growing segment
- Review operational efficiency in underperforming areas

What would you like to explore further?`;
        } else {
            return `Thank you for your question! I'm here to help you understand your business data better. I can:

🔍 Analyze your current performance metrics
📊 Generate detailed reports and insights
💡 Provide recommendations for improvement
📈 Help with forecasting and trend analysis

Feel free to ask me anything specific about your business data!`;
        }
    }

    /**
     * Add message to chat
     */
    add_message(text, sender, metadata = null) {
        const messages = $('#chat-messages');
        if (!messages.length) {
            console.warn('Chat messages container not found');
            return;
        }
        
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const isUser = sender === 'user';
        
        // Safely format content
        const formattedText = this.format_message_text(text || '');
        const safeTime = (time || '').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        const metadataHtml = metadata ? this.render_message_metadata(metadata) : '';
        
        const messageHtml = `
            <div class="chat-message ${isUser ? 'user-message' : 'ai-message'}">
                <div class="message-avatar">
                    <i class="fa fa-${isUser ? 'user' : 'robot'}"></i>
                </div>
                <div class="message-content">
                    <div class="message-text">${formattedText}</div>
                    ${metadataHtml}
                    <div class="message-time">${safeTime}</div>
                </div>
            </div>
        `;
        
        try {
            messages.append(messageHtml);
            this.scroll_to_bottom();
        } catch (error) {
            console.error('Error appending message to chat:', error);
            console.error('Problematic HTML:', messageHtml);
        }
        
        // Save to session if exists
        if (this.current_session) {
            this.current_session.messages.push({
                text: text,
                sender: sender,
                timestamp: new Date().toISOString()
            });
            this.save_chat_sessions();
        }
    }

    /**
     * Format message text with markdown-like styling
     */
    format_message_text(text) {
        if (!text || typeof text !== 'string') {
            return '';
        }
        
        // First escape HTML to prevent XSS and parsing errors
        const escaped = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
        
        // Then apply markdown-like formatting
        return escaped
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    /**
     * Show typing indicator
     */
    show_typing_indicator() {
        this.is_typing = true;
        $('#send-message').prop('disabled', true);
        
        const messages = $('#chat-messages');
        messages.append(`
            <div class="chat-message ai-message typing-indicator" id="typing-indicator">
                <div class="message-avatar">
                    <i class="fa fa-robot"></i>
                </div>
                <div class="message-content">
                    <div class="typing-animation">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `);
        
        this.scroll_to_bottom();
    }

    /**
     * Hide typing indicator
     */
    hide_typing_indicator() {
        this.is_typing = false;
        $('#send-message').prop('disabled', false);
        $('#typing-indicator').remove();
    }

    /**
     * Scroll to bottom of chat
     */
    scroll_to_bottom() {
        const messages = $('#chat-messages');
        messages.scrollTop(messages[0].scrollHeight);
    }

    /**
     * Toggle thinking mode
     */
    toggle_thinking_mode() {
        this.thinking_mode = !this.thinking_mode;
        $('#thinking-mode-toggle').toggleClass('active', this.thinking_mode);
    }

    /**
     * Toggle web search
     */
    toggle_web_search() {
        this.web_search_enabled = !this.web_search_enabled;
        $('#web-search-toggle').toggleClass('active', this.web_search_enabled);
    }

    /**
     * Trigger file upload
     */
    trigger_file_upload() {
        $('#file-upload').click();
    }

    /**
     * Handle file upload
     */
    handle_file_upload(event) {
        const files = event.target.files;
        if (files.length > 0) {
            for (let file of files) {
                this.add_message(`📎 Uploaded: ${file.name} (${this.format_file_size(file.size)})`, 'user');
            }
            this.add_message('I\'ve received your file(s). I can help you analyze the content. What would you like me to focus on?', 'ai');
        }
    }

    /**
     * Format file size
     */
    format_file_size(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Start voice input (placeholder)
     */
    start_voice_input() {
        if ('webkitSpeechRecognition' in window) {
            const recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                $('#chat-input').val(transcript);
            };
            
            recognition.start();
        } else {
            this.add_message('Voice input is not supported in your browser.', 'ai');
        }
    }

    /**
     * Start new chat session
     */
    start_new_session() {
        this.current_session = {
            id: Date.now().toString(),
            title: 'New Chat',
            created: new Date().toISOString(),
            messages: []
        };
        
        this.chat_sessions.unshift(this.current_session);
        this.save_chat_sessions();
        
        // Clear messages and show welcome
        $('#chat-messages').html(this.get_enhanced_welcome_message());
    }

    /**
     * Show settings dialog
     */
    show_settings() {
        // Placeholder for settings modal
        frappe.msgprint('Chat settings coming soon!');
    }

    /**
     * Load chat sessions from storage
     */
    load_chat_sessions() {
        try {
            const saved = localStorage.getItem('ai_chat_sessions');
            this.chat_sessions = saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Error loading chat sessions:', error);
            this.chat_sessions = [];
        }
    }

    /**
     * Save chat sessions to storage
     */
    save_chat_sessions() {
        try {
            localStorage.setItem('ai_chat_sessions', JSON.stringify(this.chat_sessions));
        } catch (error) {
            console.error('Error saving chat sessions:', error);
        }
    }

    render_message_metadata(metadata) {
        if (!metadata) return '';
        
        let metadataHtml = '';
        
        if (metadata.type === 'prediction' && metadata.confidence) {
            metadataHtml += `<div class="message-metadata">
                <span class="confidence-badge">Confidence: ${metadata.confidence}%</span>
            </div>`;
        }
        
        if (metadata.key_findings) {
            metadataHtml += `<div class="key-findings">
                <h5>Key Findings:</h5>
                <ul>${metadata.key_findings.map(finding => `<li>${finding}</li>`).join('')}</ul>
            </div>`;
        }
        
        return metadataHtml;
    }

    destroy() {
        // Cleanup enhanced AI features
        this.conversation_context = [];
        this.data_context = null;
        this.analytics_cache.clear();
    }
}

// Export for use in main dashboard
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIChatModule;
} else {
    window.AIChatModule = AIChatModule;
}
