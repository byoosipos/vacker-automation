// Initialize the dashboard when page loads
frappe.pages['comprehensive-executive-dashboard'].on_page_load = function(wrapper) {
    // Debug: Check which modules are available
    console.log('🔍 Checking available modules:');
    console.log('- AIChatModule:', typeof window.AIChatModule !== 'undefined');
    console.log('- StylesModule:', typeof window.StylesModule !== 'undefined');
    console.log('- OverviewModule:', typeof window.OverviewModule !== 'undefined');
    console.log('- FinancialManagementModule:', typeof window.FinancialManagementModule !== 'undefined');
    console.log('- ChartUtils:', typeof window.ChartUtils !== 'undefined');
    
    // Ensure styles are loaded first
    if (typeof window.StylesModule !== 'undefined') {
        new window.StylesModule();
    }
        
        var page = frappe.ui.make_app_page({
            parent: wrapper,
            title: 'AI Business Intelligence',
            single_column: true
        });
        
    
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'AI Business Intelligence',
        single_column: true
    });
    
    try {
        frappe.comprehensive_dashboard = new ComprehensiveExecutiveDashboard(page);
        console.log('✅ Dashboard instance created successfully');
    } catch (error) {
        console.error('❌ Error creating dashboard instance:', error);
        
        // Show error in page
        page.main.html(`
            <div style="display: flex; justify-content: center; align-items: center; min-height: 60vh; padding: 20px;">
                <div style="text-align: center; max-width: 500px; padding: 30px; border: 1px solid #e74c3c; border-radius: 8px; background: #fff;">
                    <h2 style="color: #e74c3c; margin-bottom: 20px;"><i class="fa fa-exclamation-triangle"></i> Initialization Error</h2>
                    <p style="margin-bottom: 25px; color: #666;">Failed to initialize the dashboard. Please check the console for details.</p>
                    <button class="btn btn-primary" onclick="location.reload()" style="margin-bottom: 20px;">
                        <i class="fa fa-refresh"></i> Refresh Page
                    </button>
                    <details style="margin-top: 20px; text-align: left;">
                        <summary style="cursor: pointer; color: #666;">Error Details</summary>
                        <pre style="margin-top: 10px; padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; overflow-x: auto; font-size: 12px;">${error.message}</pre>
                    </details>
                </div>
            </div>
        `);
    }
};

class ComprehensiveExecutiveDashboard {
    constructor(page) {
        this.page = page;
        this.filters = {};
        this.data = {};
        this.charts = {};
        this.current_view = 'ai_assistant';
        this.current_session = null;
        this.chat_sessions = [];
        this.is_mobile = window.innerWidth <= 768;
        this.modules = {}; // Store loaded module instances
        this.loaded_modules = new Set(); // Track which modules have been loaded
        this.loading_modules = new Set(); // Track modules currently being loaded
        this.cache = new Map(); // Client-side cache for module data
        this.cache_timeout = 300000; // 5 minutes in milliseconds
        
        // User Experience enhancements
        this.user_preferences = {};
        this.user_role = null;
        this.accessible_modules = new Set();
        this.is_first_time_user = false;
        this.tour_active = false;
        this.layout_mode = 'default'; // default, compact, expanded
        this.theme_mode = 'light'; // light, dark, auto
        
        this.load_user_preferences();
        this.check_user_permissions();
        this.make_page();
        this.setup_filters();
        this.setup_mobile_handlers();
        this.load_chat_sessions();
        
        // Initialize based on user preferences
        this.initialize_dashboard();
    }
    
    /**
     * Load user preferences and settings
     */
    async load_user_preferences() {
        try {
            const response = await frappe.call({
                method: 'vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard.get_user_preferences',
                no_spinner: true
            });
            
            if (response.message) {
                this.user_preferences = response.message.preferences || {};
                this.user_role = response.message.role || 'Guest';
                this.is_first_time_user = response.message.is_first_time || false;
                
                // Apply saved preferences
                this.layout_mode = this.user_preferences.layout_mode || 'default';
                this.theme_mode = this.user_preferences.theme_mode || 'light';
                this.current_view = this.user_preferences.default_view || 'ai_assistant';
                
                this.apply_theme();
                this.apply_layout_mode();
            }
        } catch (error) {
            console.error('Error loading user preferences:', error);
        }
    }
    
    /**
     * Check user permissions and accessible modules
     */
    async check_user_permissions() {
        try {
            const response = await frappe.call({
                method: 'vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard.get_user_permissions',
                no_spinner: true
            });
            
            if (response.message) {
                this.accessible_modules = new Set(response.message.accessible_modules || []);
                this.user_role = response.message.role || 'Guest';
            }
        } catch (error) {
            console.error('Error checking user permissions:', error);
            // Default to basic access
            this.accessible_modules = new Set(['ai_assistant', 'overview']);
        }
    }
    
    /**
     * Initialize dashboard based on user state
     */
    async initialize_dashboard() {
        if (this.is_first_time_user) {
            this.show_onboarding();
        } else {
            this.load_data();
        }
    }
    
    /**
     * Show onboarding tour for new users
     */
    show_onboarding() {
        this.tour_active = true;
        
        const onboarding_content = `
            <div class="onboarding-overlay">
                <div class="onboarding-modal">
                    <div class="onboarding-header">
                        <h2><i class="fa fa-rocket"></i> Welcome to AI Business Intelligence!</h2>
                        <p>Let's take a quick tour to help you get started</p>
                    </div>
                    <div class="onboarding-content">
                        <div class="onboarding-step active" data-step="1">
                            <div class="step-icon"><i class="fa fa-dashboard"></i></div>
                            <h3>Dashboard Overview</h3>
                            <p>Your AI-powered business intelligence dashboard provides comprehensive insights across all business functions.</p>
                            <ul>
                                <li>Real-time financial analytics</li>
                                <li>Project performance tracking</li>
                                <li>HR and operational insights</li>
                                <li>AI-powered chat assistant</li>
                            </ul>
                        </div>
                        
                        <div class="onboarding-step" data-step="2">
                            <div class="step-icon"><i class="fa fa-comments"></i></div>
                            <h3>AI Assistant</h3>
                            <p>Your intelligent business companion can help you:</p>
                            <ul>
                                <li>Analyze your business data</li>
                                <li>Generate reports and insights</li>
                                <li>Answer questions about performance</li>
                                <li>Provide recommendations</li>
                            </ul>
                        </div>
                        
                        <div class="onboarding-step" data-step="3">
                            <div class="step-icon"><i class="fa fa-cogs"></i></div>
                            <h3>Customization</h3>
                            <p>Personalize your experience:</p>
                            <ul>
                                <li>Choose your preferred layout</li>
                                <li>Set default dashboard view</li>
                                <li>Configure data refresh intervals</li>
                                <li>Access role-based modules</li>
                            </ul>
                        </div>
                        
                        <div class="onboarding-step" data-step="4">
                            <div class="step-icon"><i class="fa fa-shield"></i></div>
                            <h3>Your Access Level</h3>
                            <p>Based on your role: <strong>${this.user_role}</strong></p>
                            <p>You have access to:</p>
                            <ul>
                                ${Array.from(this.accessible_modules).map(module => 
                                    `<li>${this.get_module_display_name(module)}</li>`
                                ).join('')}
                            </ul>
                        </div>
                    </div>
                    <div class="onboarding-footer">
                        <div class="step-indicators">
                            <span class="step-indicator active" data-step="1"></span>
                            <span class="step-indicator" data-step="2"></span>
                            <span class="step-indicator" data-step="3"></span>
                            <span class="step-indicator" data-step="4"></span>
                        </div>
                        <div class="onboarding-actions">
                            <button class="btn btn-default" id="skip-tour">Skip Tour</button>
                            <button class="btn btn-primary" id="next-step">Next</button>
                            <button class="btn btn-success" id="finish-tour" style="display: none;">Get Started</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('body').append(onboarding_content);
        this.setup_onboarding_events();
    }
    
    /**
     * Setup onboarding event handlers
     */
    setup_onboarding_events() {
        let current_step = 1;
        const total_steps = 4;
        
        $('#next-step').on('click', () => {
            if (current_step < total_steps) {
                current_step++;
                this.show_onboarding_step(current_step);
                
                if (current_step === total_steps) {
                    $('#next-step').hide();
                    $('#finish-tour').show();
                }
            }
        });
        
        $('#skip-tour, #finish-tour').on('click', () => {
            this.finish_onboarding();
        });
        
        $('.step-indicator').on('click', (e) => {
            const step = parseInt($(e.target).data('step'));
            current_step = step;
            this.show_onboarding_step(step);
        });
    }
    
    /**
     * Show specific onboarding step
     */
    show_onboarding_step(step) {
        $('.onboarding-step').removeClass('active');
        $(`.onboarding-step[data-step="${step}"]`).addClass('active');
        
        $('.step-indicator').removeClass('active');
        $(`.step-indicator[data-step="${step}"]`).addClass('active');
    }
    
    /**
     * Finish onboarding and start using dashboard
     */
    async finish_onboarding() {
        this.tour_active = false;
        $('.onboarding-overlay').remove();
        
        // Save that user has completed onboarding
        try {
            await frappe.call({
                method: 'vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard.complete_onboarding',
                no_spinner: true
            });
        } catch (error) {
            console.error('Error saving onboarding completion:', error);
        }
        
        // Show welcome message and start dashboard
        frappe.show_alert({
            message: 'Welcome! Your dashboard is loading...',
            indicator: 'green'
        }, 3);
        
        this.load_data();
    }
    
    /**
     * Apply theme based on user preference
     */
    apply_theme() {
        const body = $('body');
        body.removeClass('theme-light theme-dark');
        
        if (this.theme_mode === 'auto') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            body.addClass(prefersDark ? 'theme-dark' : 'theme-light');
        } else {
            body.addClass(`theme-${this.theme_mode}`);
        }
    }
    
    /**
     * Apply layout mode
     */
    apply_layout_mode() {
        const dashboard = $('.chatgpt-dashboard');
        dashboard.removeClass('layout-default layout-compact layout-expanded');
        dashboard.addClass(`layout-${this.layout_mode}`);
    }
    
    /**
     * Save user preferences
     */
    async save_user_preferences() {
        try {
            await frappe.call({
                method: 'vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard.save_user_preferences',
                args: {
                    preferences: {
                        layout_mode: this.layout_mode,
                        theme_mode: this.theme_mode,
                        default_view: this.current_view,
                        ...this.user_preferences
                    }
                },
                no_spinner: true
            });
        } catch (error) {
            console.error('Error saving user preferences:', error);
        }
    }
    
    /**
     * Show user preferences modal
     */
    show_preferences_modal() {
        const modal_content = `
            <div class="modal fade" id="preferences-modal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h4 class="modal-title"><i class="fa fa-cogs"></i> Dashboard Preferences</h4>
                            <button type="button" class="close" data-dismiss="modal">
                                <span>&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <div class="preferences-tabs">
                                <ul class="nav nav-tabs">
                                    <li class="active"><a href="#appearance-tab" data-toggle="tab">Appearance</a></li>
                                    <li><a href="#layout-tab" data-toggle="tab">Layout</a></li>
                                    <li><a href="#modules-tab" data-toggle="tab">Modules</a></li>
                                    <li><a href="#notifications-tab" data-toggle="tab">Notifications</a></li>
                                </ul>
                                <div class="tab-content">
                                    <div class="tab-pane active" id="appearance-tab">
                                        ${this.render_appearance_preferences()}
                                    </div>
                                    <div class="tab-pane" id="layout-tab">
                                        ${this.render_layout_preferences()}
                                    </div>
                                    <div class="tab-pane" id="modules-tab">
                                        ${this.render_modules_preferences()}
                                    </div>
                                    <div class="tab-pane" id="notifications-tab">
                                        ${this.render_notifications_preferences()}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="save-preferences">Save Changes</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('body').append(modal_content);
        $('#preferences-modal').modal('show');
        this.setup_preferences_events();
    }
    
    /**
     * Render appearance preferences
     */
    render_appearance_preferences() {
        return `
            <div class="preference-section">
                <h5><i class="fa fa-paint-brush"></i> Theme</h5>
                <div class="theme-options">
                    <label class="theme-option ${this.theme_mode === 'light' ? 'active' : ''}">
                        <input type="radio" name="theme" value="light" ${this.theme_mode === 'light' ? 'checked' : ''}>
                        <div class="theme-preview light">
                            <div class="theme-header"></div>
                            <div class="theme-sidebar"></div>
                            <div class="theme-content"></div>
                        </div>
                        <span>Light</span>
                    </label>
                    <label class="theme-option ${this.theme_mode === 'dark' ? 'active' : ''}">
                        <input type="radio" name="theme" value="dark" ${this.theme_mode === 'dark' ? 'checked' : ''}>
                        <div class="theme-preview dark">
                            <div class="theme-header"></div>
                            <div class="theme-sidebar"></div>
                            <div class="theme-content"></div>
                        </div>
                        <span>Dark</span>
                    </label>
                    <label class="theme-option ${this.theme_mode === 'auto' ? 'active' : ''}">
                        <input type="radio" name="theme" value="auto" ${this.theme_mode === 'auto' ? 'checked' : ''}>
                        <div class="theme-preview auto">
                            <div class="theme-header"></div>
                            <div class="theme-sidebar"></div>
                            <div class="theme-content"></div>
                        </div>
                        <span>Auto</span>
                    </label>
                </div>
            </div>
            
            <div class="preference-section">
                <h5><i class="fa fa-home"></i> Default View</h5>
                <select class="form-control" id="default-view">
                    ${Array.from(this.accessible_modules).map(module => 
                        `<option value="${module}" ${this.current_view === module ? 'selected' : ''}>
                            ${this.get_module_display_name(module)}
                        </option>`
                    ).join('')}
                </select>
            </div>
        `;
    }
    
    /**
     * Render layout preferences
     */
    render_layout_preferences() {
        return `
            <div class="preference-section">
                <h5><i class="fa fa-layout"></i> Layout Mode</h5>
                <div class="layout-options">
                    <label class="layout-option ${this.layout_mode === 'default' ? 'active' : ''}">
                        <input type="radio" name="layout" value="default" ${this.layout_mode === 'default' ? 'checked' : ''}>
                        <div class="layout-preview default">
                            <div class="layout-sidebar"></div>
                            <div class="layout-content"></div>
                            <div class="layout-chat"></div>
                        </div>
                        <span>Default</span>
                    </label>
                    <label class="layout-option ${this.layout_mode === 'compact' ? 'active' : ''}">
                        <input type="radio" name="layout" value="compact" ${this.layout_mode === 'compact' ? 'checked' : ''}>
                        <div class="layout-preview compact">
                            <div class="layout-sidebar"></div>
                            <div class="layout-content"></div>
                        </div>
                        <span>Compact</span>
                    </label>
                    <label class="layout-option ${this.layout_mode === 'expanded' ? 'active' : ''}">
                        <input type="radio" name="layout" value="expanded" ${this.layout_mode === 'expanded' ? 'checked' : ''}>
                        <div class="layout-preview expanded">
                            <div class="layout-content"></div>
                        </div>
                        <span>Expanded</span>
                    </label>
                </div>
            </div>
            
            <div class="preference-section">
                <h5><i class="fa fa-refresh"></i> Data Refresh</h5>
                <div class="form-group">
                    <label>Auto-refresh interval (minutes)</label>
                    <select class="form-control" id="refresh-interval">
                        <option value="0">Manual only</option>
                        <option value="5" ${this.user_preferences.refresh_interval === 5 ? 'selected' : ''}>5 minutes</option>
                        <option value="10" ${this.user_preferences.refresh_interval === 10 ? 'selected' : ''}>10 minutes</option>
                        <option value="15" ${this.user_preferences.refresh_interval === 15 ? 'selected' : ''}>15 minutes</option>
                        <option value="30" ${this.user_preferences.refresh_interval === 30 ? 'selected' : ''}>30 minutes</option>
                    </select>
                </div>
            </div>
        `;
    }
    
    /**
     * Check if user has access to a module
     */
    has_module_access(module_name) {
        return this.accessible_modules.has(module_name);
    }
    
    /**
     * Filter modules menu based on user permissions
     */


    make_page() {
        try {
            console.log('🚀 Initializing Comprehensive Executive Dashboard');
            
            // Clear any existing error states
            localStorage.removeItem('dashboard_error');
            
            // Hide default page elements
            this.page.$title_area.hide();
            this.page.$sub_title_area.hide();
            this.hide_frappe_elements();
        
        this.page.main.html(`
            <div class="chatgpt-dashboard">
                <!-- Mobile Header -->
                <div class="mobile-header">
                    <button class="mobile-menu-btn" id="mobile-menu-toggle">
                        <i class="fa fa-bars"></i>
                    </button>
                    <div class="mobile-title">
                        <i class="fa fa-robot"></i>
                        <span>AI Dashboard</span>
                    </div>
                    <button class="mobile-chat-btn" id="mobile-chat-toggle">
                        <i class="fa fa-comments"></i>
                    </button>
                </div>

                <!-- Desktop Header -->
                <div class="desktop-header">
                    <div class="header-left">
                        <button class="sidebar-toggle" id="modules-sidebar-toggle">
                            <i class="fa fa-th-large"></i>
                            <span>Modules</span>
                        </button>
                        <div class="dashboard-filters"></div>
                    </div>
                    <div class="header-center">
                        <h1><i class="fa fa-robot"></i> AI Business Intelligence</h1>
                    </div>
                    <div class="header-right">
                        <button class="control-btn" onclick="frappe.set_route('/')">
                            <i class="fa fa-home"></i>
                            <span>Desk</span>
                        </button>
                        <button class="control-btn" onclick="frappe.app.logout()">
                            <i class="fa fa-sign-out"></i>
                            <span>Logout</span>
                        </button>
                        <button class="chat-history-toggle" id="chat-history-toggle">
                            <i class="fa fa-history"></i>
                            <span>Chat History</span>
                        </button>
                    </div>
                </div>

                <!-- Main Content Area -->
                <div class="dashboard-main-content">
                    <!-- Modules Sidebar -->
                    <div class="modules-sidebar" id="modules-sidebar">
                        <div class="sidebar-header">
                            <h3><i class="fa fa-rocket"></i> Modules</h3>
                            <button class="sidebar-close" id="modules-close">
                                <i class="fa fa-times"></i>
                            </button>
                        </div>
                        <div class="modules-menu"></div>
                    </div>

                    <!-- Central Content -->
                    <div class="central-content">
                        <div class="dashboard-content"></div>
                    </div>

                    <!-- Chat History Sidebar -->
                    <div class="chat-history-sidebar" id="chat-history-sidebar">
                        <div class="chat-sidebar-header">
                            <h3><i class="fa fa-comments"></i> Chat History</h3>
                            <div class="chat-header-actions">
                                <button class="btn-new-chat" id="new-chat-btn" title="New Chat">
                                    <i class="fa fa-plus"></i>
                                </button>
                                <button class="sidebar-close" id="chat-history-close">
                                    <i class="fa fa-times"></i>
                                </button>
                            </div>
                        </div>
                        
                        <div class="chat-sessions-container">
                            <div class="session-filters">
                                <select id="session-type-filter" class="form-control">
                                    <option value="">All Types</option>
                                    <option value="General Chat">General Chat</option>
                                    <option value="Data Analysis">Data Analysis</option>
                                    <option value="Report Generation">Report Generation</option>
                                    <option value="Web Research">Web Research</option>
                                    <option value="Document Analysis">Document Analysis</option>
                                </select>
                            </div>
                            
                            <div class="chat-sessions-list" id="chat-sessions-list">
                                <!-- Chat sessions will be loaded here -->
                            </div>
                            
                            <div class="chat-stats" id="chat-stats">
                                <!-- Chat statistics will be shown here -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Overlay for mobile -->
                <div class="mobile-overlay" id="mobile-overlay"></div>
            </div>
        `);

            this.add_chatgpt_styles();
            this.setup_sidebar_controls();
            
            console.log('✅ Dashboard page initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing dashboard page:', error);
            
            // Store error for debugging
            localStorage.setItem('dashboard_error', JSON.stringify({
                error: error.message,
                stack: error.stack,
                timestamp: new Date().toISOString()
            }));
            
            // Show error fallback
            this.page.main.html(`
                <div class="dashboard-error" style="display: flex; justify-content: center; align-items: center; min-height: 60vh; padding: 20px;">
                    <div class="error-container" style="text-align: center; max-width: 500px; padding: 30px; border: 1px solid #e74c3c; border-radius: 8px; background: #fff;">
                        <h2 style="color: #e74c3c; margin-bottom: 20px;"><i class="fa fa-exclamation-triangle"></i> Dashboard Error</h2>
                        <p style="margin-bottom: 25px; color: #666;">There was an error loading the dashboard. Please try refreshing the page.</p>
                        <button class="btn btn-primary" onclick="location.reload()" style="margin-bottom: 20px;">
                            <i class="fa fa-refresh"></i> Refresh Page
                        </button>
                        <details style="margin-top: 20px; text-align: left;">
                            <summary style="cursor: pointer; color: #666;">Error Details</summary>
                            <pre style="margin-top: 10px; padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; overflow-x: auto; font-size: 12px;">${error.message}</pre>
                        </details>
                    </div>
                </div>
            `);
        }
    }

    hide_frappe_elements() {
        $('.navbar, .page-head, .breadcrumb-area').hide();
        $('body, .layout-main, .layout-main-section, .container-page, .page-wrapper').css({
            'margin': '0',
            'padding': '0',
            'max-width': 'none',
            'width': '100%',
            'overflow': 'hidden'
        });
    }

    setup_mobile_handlers() {
        // Mobile menu toggles
        $('#mobile-menu-toggle').on('click', () => {
            this.toggle_mobile_sidebar('modules');
        });

        $('#mobile-chat-toggle').on('click', () => {
            this.toggle_mobile_sidebar('chat');
        });

        // Mobile overlay
        $('#mobile-overlay').on('click', () => {
            this.close_mobile_sidebars();
        });

        // Window resize handler
        $(window).on('resize', () => {
            const was_mobile = this.is_mobile;
            this.is_mobile = window.innerWidth <= 768;
            
            if (was_mobile !== this.is_mobile) {
                this.close_mobile_sidebars();
            }
        });
    }

    toggle_mobile_sidebar(type) {
        if (type === 'modules') {
            $('.chatgpt-dashboard').toggleClass('modules-open');
            $('.chatgpt-dashboard').removeClass('chat-open');
        } else {
            $('.chatgpt-dashboard').toggleClass('chat-open');
            $('.chatgpt-dashboard').removeClass('modules-open');
        }

        if ($('.chatgpt-dashboard').hasClass('modules-open') || $('.chatgpt-dashboard').hasClass('chat-open')) {
            $('#mobile-overlay').addClass('active');
        } else {
            $('#mobile-overlay').removeClass('active');
        }
    }

    // Module loading and management methods
    async loadModule(moduleName, moduleClass) {
        try {
            // Check if module is already loaded
            if (this.modules[moduleName]) {
                return this.modules[moduleName];
            }

            // Create new module instance
            const module = new moduleClass(this);
            this.modules[moduleName] = module;
            
            return module;
        } catch (error) {
            console.error(`Error loading module ${moduleName}:`, error);
            return null;
        }
    }

    destroyModule(moduleName) {
        if (this.modules[moduleName]) {
            if (typeof this.modules[moduleName].destroy === 'function') {
                this.modules[moduleName].destroy();
            }
            delete this.modules[moduleName];
        }
    }

    destroyAllModules() {
        Object.keys(this.modules).forEach(moduleName => {
            this.destroyModule(moduleName);
        });
    }

    // ...existing code...

    close_mobile_sidebars() {
        $('.chatgpt-dashboard').removeClass('modules-open chat-open');
        $('#mobile-overlay').removeClass('active');
    }

    add_chatgpt_styles() {
        // Inject comprehensive dashboard styles if not already present
        if (!document.getElementById('comprehensive-dashboard-styles')) {
            const style = document.createElement('style');
            style.id = 'comprehensive-dashboard-styles';
            style.textContent = `
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
                
                /* Ensure proper styling for all dashboard elements */
                .dashboard-sidebar, .main-content, .chat-sidebar {
                    transition: all 0.3s ease;
                }
            `;
            document.head.appendChild(style);
        }
    }

    setup_sidebar_controls() {
        // Desktop sidebar toggles
        $('#modules-sidebar-toggle').on('click', () => {
            $('.chatgpt-dashboard').toggleClass('modules-sidebar-open');
        });

        $('#chat-history-toggle').on('click', () => {
            $('.chatgpt-dashboard').toggleClass('chat-sidebar-open');
        });

        // Sidebar close buttons
        $('#modules-close').on('click', () => {
            $('.chatgpt-dashboard').removeClass('modules-sidebar-open modules-open');
        });

        $('#chat-history-close').on('click', () => {
            $('.chatgpt-dashboard').removeClass('chat-sidebar-open chat-open');
        });

        // New chat button
        $('#new-chat-btn').on('click', () => {
            this.create_new_chat_session();
        });

        // Session type filter
        $('#session-type-filter').on('change', () => {
            this.filter_chat_sessions();
        });
    }

    setup_filters() {
        const filter_wrapper = this.page.main.find('.dashboard-filters');
        
        this.company_filter = frappe.ui.form.make_control({
            parent: filter_wrapper,
            df: {
                fieldtype: 'Link',
                options: 'Company',
                label: 'Company',
                fieldname: 'company',
                default: frappe.defaults.get_user_default('Company')
            },
            render_input: true
        });

        this.from_date_filter = frappe.ui.form.make_control({
            parent: filter_wrapper,
            df: {
                fieldtype: 'Date',
                label: 'From Date',
                fieldname: 'from_date',
                default: frappe.datetime.add_months(frappe.datetime.get_today(), -12)
            },
            render_input: true
        });

        this.to_date_filter = frappe.ui.form.make_control({
            parent: filter_wrapper,
            df: {
                fieldtype: 'Date',
                label: 'To Date',
                fieldname: 'to_date',
                default: frappe.datetime.get_today()
            },
            render_input: true
        });

        filter_wrapper.append(`
            <button class="btn btn-primary btn-sm refresh-btn">
                <i class="fa fa-refresh"></i> Refresh
            </button>
        `);

        this.setup_filter_events();
    }

    setup_filter_events() {
        $('.refresh-btn').on('click', () => {
            this.get_filters();
            this.load_data();
        });

        [this.company_filter, this.from_date_filter, this.to_date_filter].forEach(filter => {
            filter.$input.on('change', () => {
                this.get_filters();
                this.load_data();
            });
        });
    }

    setup_modules_menu() {
        const menu_items = [
            { id: 'ai_assistant', icon: 'fa-comments', label: 'AI Assistant', priority: true },
            { id: 'risk_management', icon: 'fa-shield', label: 'AI Risk Manager', priority: true },
            { id: 'overview', icon: 'fa-dashboard', label: 'Executive Overview' },
            { id: 'financial', icon: 'fa-money', label: 'Financial Analytics' },
            { id: 'bank_cash', icon: 'fa-university', label: 'Bank & Cash' },
            { id: 'projects', icon: 'fa-tasks', label: 'Projects Dashboard' },
            { id: 'materials', icon: 'fa-cubes', label: 'Material Requests' },
            { id: 'purchase_orders', icon: 'fa-shopping-cart', label: 'Purchase Orders' },
            { id: 'sales', icon: 'fa-line-chart', label: 'Sales & CRM' },
            { id: 'hr', icon: 'fa-users', label: 'HR & Workforce' },
            { id: 'operations', icon: 'fa-cogs', label: 'Operations' }
        ];

        const modules_menu = this.page.main.find('.modules-menu');
        
        menu_items.forEach(item => {
            const priorityClass = item.priority ? 'priority-item' : '';
            modules_menu.append(`
                <div class="module-item ${item.id === 'ai_assistant' ? 'active' : ''} ${priorityClass}" data-view="${item.id}">
                    <i class="fa ${item.icon}"></i>
                    <span>${item.label}</span>
                </div>
            `);
        });

        $('.module-item').on('click', (e) => {
            const view = $(e.currentTarget).data('view');
            this.switch_view(view);
            
            // Close mobile sidebar after selection
            if (this.is_mobile) {
                this.close_mobile_sidebars();
            }
        });
    }

    switch_view(view) {
        $('.module-item').removeClass('active');
        $(`.module-item[data-view="${view}"]`).addClass('active');
        
        // Destroy all modules when switching views to free up resources
        this.destroyAllModules();
        
        // Use lazy loading for better performance
        this.switch_view_with_loading(view);
    }

    load_chat_sessions() {
        frappe.call({
            method: 'vacker_automation.vacker_automation.doctype.chat_session.chat_session.get_user_sessions',
            args: { limit: 50 },
            callback: (r) => {
                if (r.message) {
                    this.chat_sessions = r.message;
                    this.render_chat_sessions();
                    this.update_chat_stats();
                }
            }
        });
    }

    render_chat_sessions() {
        const sessions_list = $('#chat-sessions-list');
        sessions_list.empty();

        if (!this.chat_sessions.length) {
            sessions_list.html(`
                <div class="empty-state">
                    <i class="fa fa-comments-o"></i>
                    <h4>No Chat Sessions</h4>
                    <p>Start your first conversation with the AI assistant</p>
                    <button class="btn btn-primary btn-sm" id="start-chatting-btn">
                        <i class="fa fa-plus"></i> Start Chatting
                    </button>
                </div>
            `);
            
            // Add event listener for start chatting button
            $('#start-chatting-btn').on('click', () => {
                this.switch_view('ai_assistant');
            });
            
            return;
        }

        this.chat_sessions.forEach(session => {
            const isActive = session.name === this.current_session;
            const timeAgo = this.format_time_ago(session.last_message_at);
            
            // Safely escape HTML content to prevent syntax errors
            const safeName = (session.name || '').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/`/g, '&#96;');
            const safeTitle = (session.title || 'Untitled Chat').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/`/g, '&#96;');
            const safeSessionType = (session.session_type || 'General').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
            const safeLatestMessage = (session.latest_message || 'No messages yet').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/`/g, '&#96;');
            const safeTotalMessages = session.total_messages || 0;
            
            // Create session element using DOM methods to avoid syntax issues
            const sessionElement = $(`
                <div class="chat-session-item ${isActive ? 'active' : ''}" data-session="${safeName}">
                    <div class="session-header">
                        <div class="session-title" title="${safeTitle}">
                            ${safeTitle}
                        </div>
                        <div class="session-actions">
                            <button class="btn-edit-session" data-session="${safeName}" title="Rename">
                                <i class="fa fa-edit"></i>
                            </button>
                            <button class="btn-delete-session" data-session="${safeName}" title="Delete">
                                <i class="fa fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="session-meta">
                        <span class="session-type">${safeSessionType}</span>
                        <span class="session-time">${timeAgo || ''}</span>
                    </div>
                    <div class="session-preview">
                        ${safeLatestMessage}
                    </div>
                    <div class="session-stats">
                        <span><i class="fa fa-comments"></i> ${safeTotalMessages}</span>
                    </div>
                </div>
            `);
            
            sessions_list.append(sessionElement);
        });

        this.setup_session_events();
    }

    setup_session_events() {
        // Session selection
        $('.chat-session-item').on('click', (e) => {
            if ($(e.target).closest('.session-actions').length) return;
            
            const session_name = $(e.currentTarget).data('session');
            this.load_chat_session(session_name);
        });

        // Edit session
        $('.btn-edit-session').on('click', (e) => {
            e.stopPropagation();
            const session_name = $(e.currentTarget).data('session');
            this.edit_session_title(session_name);
        });

        // Delete session
        $('.btn-delete-session').on('click', (e) => {
            e.stopPropagation();
            const session_name = $(e.currentTarget).data('session');
            this.delete_session(session_name);
        });
    }

    create_new_chat_session() {
        frappe.call({
            method: 'vacker_automation.vacker_automation.doctype.chat_session.chat_session.create_new_session',
            args: { session_type: 'General Chat' },
            callback: (r) => {
                if (r.message) {
                    this.current_session = r.message;
                    this.load_chat_sessions();
                    this.switch_view('ai_assistant');
                    frappe.show_alert('New chat session created!', 3);
                }
            }
        });
    }

    load_chat_session(session_name) {
        this.current_session = session_name;
        $('.chat-session-item').removeClass('active');
        
        // Safely escape the session name for jQuery selector
        const safe_session_name = (session_name || '').replace(/"/g, '\\"').replace(/'/g, "\\'");
        $(`.chat-session-item[data-session="${safe_session_name}"]`).addClass('active');
        
        // Load messages for this session
        frappe.call({
            method: 'vacker_automation.vacker_automation.doctype.chat_message.chat_message.get_session_messages',
            args: { chat_session: session_name },
            callback: (r) => {
                if (r.message) {
                    this.load_session_messages(r.message);
                    this.switch_view('ai_assistant');
                }
            }
        });
    }

    load_session_messages(messages) {
        const chat_messages = $('#chat-messages');
        if (!chat_messages.length) return;
        
        chat_messages.empty();
        
        messages.forEach(message => {
            this.add_message_to_ui(
                message.message_type.toLowerCase() === 'user' ? 'user' : 'ai',
                message.content,
                message.timestamp,
                message.thinking_content
            );
        });
        
        chat_messages.scrollTop(chat_messages[0].scrollHeight);
    }

    filter_chat_sessions() {
        const filter_type = $('#session-type-filter').val();
        
        $('.chat-session-item').each(function() {
            const session_type = $(this).find('.session-type').text();
            if (!filter_type || session_type === filter_type) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    }

    edit_session_title(session_name) {
        const session = this.chat_sessions.find(s => s.name === session_name);
        if (!session) return;

        frappe.prompt([
            {
                fieldtype: 'Data',
                label: 'Session Title',
                fieldname: 'title',
                reqd: 1,
                default: session.title
            }
        ], (values) => {
            frappe.call({
                method: 'vacker_automation.vacker_automation.doctype.chat_session.chat_session.update_session_title',
                args: {
                    session_name: session_name,
                    new_title: values.title
                },
                callback: (r) => {
                    if (r.message && r.message.success) {
                        this.load_chat_sessions();
                        frappe.show_alert('Session title updated!', 3);
                    }
                }
            });
        }, 'Rename Chat Session', 'Update');
    }

    delete_session(session_name) {
        frappe.confirm(
            'Are you sure you want to delete this chat session? This action cannot be undone.',
            () => {
                frappe.call({
                    method: 'vacker_automation.vacker_automation.doctype.chat_session.chat_session.delete_session',
                    args: { session_name: session_name },
                    callback: (r) => {
                        if (r.message && r.message.success) {
                            if (this.current_session === session_name) {
                                this.current_session = null;
                            }
                            this.load_chat_sessions();
                            frappe.show_alert('Session deleted!', 3);
                        }
                    }
                });
            }
        );
    }

    update_chat_stats() {
        frappe.call({
            method: 'vacker_automation.vacker_automation.doctype.chat_message.chat_message.get_message_stats',
            callback: (r) => {
                if (r.message) {
                    const stats = r.message;
                    $('#chat-stats').html(`
                        <div class="stats-header">
                            <h4><i class="fa fa-bar-chart"></i> Your Chat Statistics</h4>
                        </div>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <span class="stat-value">${stats.total_messages}</span>
                                <span class="stat-label">Total Messages</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">${stats.ai_messages}</span>
                                <span class="stat-label">AI Responses</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">${(stats.avg_response_time || 0).toFixed(1)}s</span>
                                <span class="stat-label">Avg Response</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">${stats.total_tokens}</span>
                                <span class="stat-label">Tokens Used</span>
                            </div>
                        </div>
                    `);
                }
            }
        });
    }

    get_filters() {
        this.filters = {
            company: this.company_filter.get_value(),
            from_date: this.from_date_filter.get_value(),
            to_date: this.to_date_filter.get_value()
        };
    }

    load_data() {
        this.get_filters();
        
        // Show loading indicator
        const content = this.page.main.find('.dashboard-content');
        content.html('<div class="loading-state"><i class="fa fa-spinner fa-spin"></i> Loading dashboard data...</div>');
        
        frappe.call({
            method: 'vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard.get_comprehensive_dashboard_data',
            args: { 
                filters: this.filters,
                lazy_load: true  // Enable lazy loading for performance
            },
            callback: (r) => {
                try {
                    if (r && r.message) {
                        const data = r.message;
                        
                        // Check if the response contains an error
                        if (data.error) {
                            throw new Error(data.message || 'Unknown error occurred');
                        }
                        
                        this.data = data;
                        // Cache core data
                        this.cache_data('core', this.data);
                        this.setup_modules_menu();
                        this.render_view();
                        
                        // Initialize AI enhancements after dashboard is ready
                        this.initialize_ai_enhancements();
                        
                        // Trigger data updated event for AI enhancements
                        $(document).trigger('dashboard_data_updated');
                        
                        console.log('Dashboard data loaded successfully');
                    } else {
                        throw new Error('No data received from server');
                    }
                } catch (error) {
                    console.error('Error processing dashboard data:', error);
                    this.show_error_state(content, 'Failed to process dashboard data', error.message);
                    this.log_client_error('load_data_callback', error, { response: r });
                }
            },
            error: (r) => {
                console.error('Dashboard loading error:', r);
                this.show_error_state(content, 'Error loading dashboard data', this.get_error_message(r));
                this.log_client_error('load_data_request', new Error('Request failed'), { response: r });
            }
        });
    }
    
    // Client-side caching methods
    cache_data(key, data) {
        if (!this.cache) this.cache = new Map();
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }
    
    format_time_ago(datetime) {
        if (!datetime) return '';
        return moment(datetime).fromNow();
    }
    
    get_cached_data(key) {
        if (!this.cache) return null;
        const cached = this.cache.get(key);
        if (cached && (Date.now() - cached.timestamp) < this.cache_timeout) {
            return cached.data;
        }
        return null;
    }
    
    clear_cache() {
        if (this.cache) this.cache.clear();
    }
    
    // Enhanced lazy loading for specific modules with comprehensive error handling
    async load_module_data(module_name, force_refresh = false) {
        // Input validation
        if (!module_name || typeof module_name !== 'string') {
            console.error('Invalid module name provided:', module_name);
            this.show_error_message('Invalid module name provided');
            return null;
        }
        
        // Check if already loading
        if (!this.loading_modules) this.loading_modules = new Set();
        if (this.loading_modules.has(module_name)) {
            console.log(`Module ${module_name} is already loading`);
            return;
        }
        
        // Check cache first
        const cache_key = `module_${module_name}`;
        if (!force_refresh) {
            const cached_data = this.get_cached_data(cache_key);
            if (cached_data) {
                this.data = {...this.data, ...cached_data};
                if (!this.loaded_modules) this.loaded_modules = new Set();
                this.loaded_modules.add(module_name);
                return cached_data;
            }
        }
        
        this.loading_modules.add(module_name);
        
        try {
            // Show loading indicator
            this.show_module_loading(module_name);
            
            const response = await frappe.call({
                method: 'vacker_automation.vacker_automation.page.comprehensive_executive_dashboard.comprehensive_executive_dashboard.get_module_data',
                args: {
                    module_name: module_name,
                    filters: this.filters || {}
                },
                timeout: 30000  // 30 second timeout
            });
            
            if (response && response.message) {
                const module_data = response.message;
                
                // Check if the response contains an error
                if (module_data.error) {
                    throw new Error(module_data.message || `Failed to load ${module_name} module`);
                }
                
                this.data = {...this.data, ...module_data};
                this.cache_data(cache_key, module_data);
                if (!this.loaded_modules) this.loaded_modules = new Set();
                this.loaded_modules.add(module_name);
                
                console.log(`Successfully loaded module: ${module_name}`);
                return module_data;
            } else {
                throw new Error(`No data received for module: ${module_name}`);
            }
        } catch (error) {
            console.error(`Error loading module ${module_name}:`, error);
            
            // Log to server for debugging
            this.log_client_error('load_module_data', error, {
                module_name: module_name,
                filters: this.filters
            });
            
            // Show user-friendly error message
            this.show_error_alert(`Failed to load ${this.get_module_display_name(module_name)} module`, error.message);
            
            // Return empty data structure to prevent further errors
            return this.get_empty_module_data(module_name);
        } finally {
            this.loading_modules.delete(module_name);
            this.hide_module_loading(module_name);
        }
    }
    
    // Enhanced error handling helpers
    show_error_message(message, duration = 5000) {
        frappe.show_alert({
            message: message,
            indicator: 'red'
        }, duration);
    }
    
    show_error_alert(title, message) {
        frappe.msgprint({
            title: title,
            message: message,
            indicator: 'red'
        });
    }
    
    show_module_loading(module_name) {
        const display_name = this.get_module_display_name(module_name);
        const content = this.page.main.find('.dashboard-content');
        content.html(`
            <div class="loading-state">
                <i class="fa fa-spinner fa-spin"></i> 
                Loading ${display_name} module...
                <div class="loading-progress">
                    <div class="progress">
                        <div class="progress-bar progress-bar-striped active" style="width: 100%"></div>
                    </div>
                </div>
            </div>
        `);
    }
    
    hide_module_loading(module_name) {
        // Loading will be hidden when content is rendered
    }
    
    get_module_display_name(module_name) {
        const display_names = {
            'financial': 'Financial Analytics',
            'projects': 'Project Management',
            'materials': 'Materials Management',
            'sales': 'Sales & CRM',
            'hr': 'Human Resources',
            'purchase': 'Purchase Management',
            'operations': 'Operations',
            'system': 'System Analytics',
            'trends': 'Trend Analysis'
        };
        return display_names[module_name] || module_name;
    }
    
    get_empty_module_data(module_name) {
        // Return empty data structure based on module type
        const empty_structures = {
            'financial': { gl_overview: {}, cashflow_data: {}, bank_cash_analysis: {} },
            'projects': { project_profitability: {} },
            'materials': { material_requests: {}, procurement_summary: {}, inventory_overview: {} },
            'sales': { sales_overview: {}, sales_invoices_detailed: {}, customer_analytics: {} },
            'hr': { hr_summary: {}, workforce_analytics: {}, payroll_detailed: {}, expense_claims_overview: {} },
            'purchase': { purchase_orders_overview: {}, purchase_invoices_overview: {} },
            'operations': { manufacturing_overview: {}, items_analysis: {}, item_groups_analysis: {} },
            'system': { users_analysis: {}, payments_detailed: {} },
            'trends': { trend_analysis: {} }
        };
        return empty_structures[module_name] || {};
    }
    
    log_client_error(method, error, context = {}) {
        try {
            frappe.call({
                method: 'frappe.log_error',
                args: {
                    title: `Dashboard Client Error - ${method}`,
                    message: `Error: ${error.message}\\nStack: ${error.stack}\\nContext: ${JSON.stringify(context)}`
                },
                no_spinner: true
            });
        } catch (log_error) {
            console.error('Failed to log error to server:', log_error);
        }
    }
    
    show_error_state(content, title, message) {
        content.html(`
            <div class="error-state-enhanced">
                <div class="error-icon">
                    <i class="fa fa-exclamation-triangle"></i>
                </div>
                <h3>${title}</h3>
                <p>${message}</p>
                <div class="error-actions">
                    <button class="btn btn-primary" id="reload-page-btn">
                        <i class="fa fa-refresh"></i> Reload Page
                    </button>
                    <button class="btn btn-default" id="go-to-desk-btn">
                        <i class="fa fa-home"></i> Go to Desk
                    </button>
                </div>
                <div class="error-details">
                    <small>If the problem persists, please contact your system administrator.</small>
                </div>
            </div>
        `);
        
        // Add event listeners for error action buttons
        $('#reload-page-btn').on('click', () => {
            location.reload();
        });
        
        $('#go-to-desk-btn').on('click', () => {
            frappe.set_route('/');
        });
    }
    
    get_error_message(response) {
        if (response && response.message) {
            return response.message;
        } else if (response && response.exc) {
            return 'Server error occurred. Please check the logs.';
        } else {
            return 'Network or server connection error.';
        }
    }
    
    // Enhanced module switching with lazy loading
    async switch_view_with_loading(view) {
        const module_map = {
            'financial': ['financial'],
            'projects': ['projects'],
            'materials': ['materials'],
            'sales': ['sales'],
            'hr': ['hr'],
            'bank_cash': ['purchase'],
            'purchase_orders': ['purchase'],
            'operations': ['operations'],
            'risk_management': ['system']
        };
        
        const required_modules = module_map[view];
        
        if (required_modules && (!this.loaded_modules || !this.loaded_modules.has(required_modules[0]))) {
            const content = this.page.main.find('.dashboard-content');
            content.html(`<div class="loading-state"><i class="fa fa-spinner fa-spin"></i> Loading ${view} module...</div>`);
            
            try {
                await Promise.all(required_modules.map(module => this.load_module_data(module)));
            } catch (error) {
                console.error(`Error loading modules for ${view}:`, error);
                content.html(`<div class="error-state"><i class="fa fa-times-circle"></i> Failed to load ${view} module</div>`);
                return;
            }
        }
        
        this.current_view = view;
        this.render_view();
    }

    render_view() {
        const content = this.page.main.find('.dashboard-content');
        
        switch(this.current_view) {
            case 'ai_assistant':
                this.render_ai_assistant(content);
                break;
            case 'risk_management':
                this.render_risk_management_dashboard(content);
                break;
            case 'overview':
                this.render_overview(content);
                break;
            case 'financial':
                this.render_financial_dashboard(content);
                break;
            case 'projects':
                this.render_projects_dashboard(content);
                break;
            case 'sales':
                this.render_sales_dashboard(content);
                break;
            case 'materials':
                this.render_materials_modular(content);
                break;
            case 'hr':
                this.render_hr_dashboard(content);
                break;
            case 'bank_cash':
                this.render_bank_cash_modular(content);
                break;
            case 'purchase_orders':
                this.render_purchase_orders_modular(content);
                break;
            case 'operations':
                this.render_operations_modular(content);
                break;
            default:
                this.render_coming_soon(content);
        }
    }

    // Helper method for currency formatting
    formatCurrency(amount) {
        if (amount === null || amount === undefined || isNaN(amount)) {
            return '0.00';
        }
        return parseFloat(amount).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    // Chart rendering methods
    render_cashflow_chart() {
        // Implementation for cashflow chart
        setTimeout(() => {
            const ctx = document.getElementById('cashflow-chart');
            if (ctx && typeof Chart !== 'undefined') {
                // Chart implementation here
            }
        }, 100);
    }

    render_po_charts() {
        // Implementation for purchase order charts
        setTimeout(() => {
            const ctx = document.getElementById('po-status-chart');
            if (ctx && typeof Chart !== 'undefined') {
                // Chart implementation here
            }
        }, 100);
    }

    render_hr_charts(summary, departments) {
        // Implementation for HR charts
        setTimeout(() => {
            const genderCtx = document.getElementById('gender-chart');
            const deptCtx = document.getElementById('department-chart');
            if (genderCtx && deptCtx && typeof Chart !== 'undefined') {
                // Chart implementation here
            }
        }, 100);
    }

    // Risk management methods
    view_risk_details(assessment_name) {
        frappe.set_route('Form', 'Risk Assessment', assessment_name);
    }

    create_new_risk_assessment() {
        frappe.new_doc('Risk Assessment');
    }

    // Cleanup method
    destroy() {
        this.destroyAllModules();
        if (this.cache) {
            this.cache.clear();
        }
    }

    initialize_ai_enhancements() {
        // Placeholder for AI enhancements
    }

    render_ai_assistant(content) {
        try {
            if (typeof window.AIChatModule !== 'undefined' && window.AIChatModule) {
                const chatModule = new window.AIChatModule(this);
                chatModule.render(content);
            } else {
                // Fallback to basic chat interface
                console.warn('AIChatModule not available, loading fallback');
                this.render_fallback_chat(content);
            }
        } catch (error) {
            console.error('Error rendering AI assistant:', error);
            this.render_fallback_chat(content);
        }
    }

    render_fallback_chat(content) {
        content.html(`
            <div class="ai-chat-fallback">
                <div class="chat-header">
                    <h3><i class="fa fa-comments"></i> AI Business Intelligence</h3>
                    <p>Loading chat interface...</p>
                </div>
                <div class="chat-messages" id="chat-messages" style="height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
                    <div class="welcome-message">
                        <p><strong>Welcome to AI Business Intelligence!</strong></p>
                        <p>The chat interface is loading. Please wait a moment...</p>
                    </div>
                </div>
                <div class="chat-input-area">
                    <div class="input-group">
                        <input type="text" class="form-control" id="chat-input" placeholder="Type your message here..." disabled>
                        <div class="input-group-btn">
                            <button class="btn btn-primary" id="send-message" disabled>
                                <i class="fa fa-send"></i> Send
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `);
        
        // Try to load the module again after a delay
        setTimeout(() => {
            if (typeof window.AIChatModule !== 'undefined' && window.AIChatModule) {
                console.log('AIChatModule now available, reloading...');
                this.render_ai_assistant(content);
            }
        }, 2000);
    }
}
