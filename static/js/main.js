// Common utility functions
const AppManager = {
    // Initialize the application
    init() {
        this.initializeEventListeners();
        this.initializeSidebarState();
    },

    // Initialize event listeners
    initializeEventListeners() {
        // Handle sidebar navigation
        document.querySelectorAll('.sidebar .nav-link').forEach(link => {
            // Skip user-toggle and dataupdate links
            if (!link.classList.contains('user-toggle') && !link.getAttribute('href').includes('dataupdate')) {
                link.addEventListener('click', (e) => this.handleSidebarNavigation(e));
            }
        });

        // Handle refresh button clicks
        document.addEventListener('click', (e) => this.handleRefreshClick(e));
    },

    // Initialize sidebar state
    initializeSidebarState() {
        const activePanelId = localStorage.getItem('activePanelId');
        if (activePanelId) {
            this.showPanel(activePanelId);
        }
    },

    // Handle sidebar navigation
    handleSidebarNavigation(e) {
        const panel = e.currentTarget.getAttribute('data-panel');
        if (!panel) {
            // If no data-panel attribute, let the browser handle the navigation
            return;
        }
        
        e.preventDefault();
        switch(panel) {
            case 'watchlist':
                this.showWatchlist();
                break;
            case 'portfolio':
                this.showPortfolio();
                break;
            case 'market-insights':
                this.showMarket();
                break;
            case 'risk-analysis':
                this.showRisk();
                break;
            case 'reports':
                this.showReports();
                break;
            default:
                this.showDashboard();
        }
    },

    // Handle refresh button clicks
    handleRefreshClick(e) {
        const refreshButton = e.target.closest('.btn-refresh');
        if (refreshButton) {
            e.preventDefault();
            const currentPath = window.location.pathname;
            
            if (currentPath.includes('watchlist:create')) {
                return;
            }
            
            this.loadContent(currentPath);
        }
    },

    // Show different panels
    showPanel(panelId) {
        // Hide all panels first
        document.querySelectorAll('.middle-sidebar-panel, .watchlist-section, .portfolio-section, .market-section, .risk-section, .reports-section').forEach(panel => {
            panel.style.display = 'none';
        });

        // Show the requested panel
        const panel = document.getElementById(panelId) || document.querySelector(`.${panelId}`);
        if (panel) {
            panel.style.display = 'block';
            this.updateHeaderTitle(panelId);
        }
    },

    // Update header title based on panel
    updateHeaderTitle(panelId) {
        // Remove header title update since we removed the header
        return;
    },

    // Show different sections
    showDashboard() {
        this.hideAllSections();
        document.getElementById('dashboardStats').style.display = 'block';
        document.querySelector('.dashboard-content').style.display = 'block';
        this.updateHeaderTitle('dashboardPanel');
    },

    showWatchlist() {
        this.hideAllSections();
        document.getElementById('watchlistStats').style.display = 'block';
        document.querySelector('.watchlist-section').style.display = 'block';
        document.querySelector('.watchlist-content').style.display = 'block';
        this.updateHeaderTitle('watchlistPanel');
    },

    showPortfolio() {
        this.hideAllSections();
        document.getElementById('portfolioStats').style.display = 'block';
        document.querySelector('.portfolio-section').style.display = 'block';
        document.querySelector('.portfolio-content').style.display = 'block';
        this.updateHeaderTitle('portfolioPanel');
    },

    showMarket() {
        this.hideAllSections();
        document.getElementById('marketStats').style.display = 'block';
        document.querySelector('.market-section').style.display = 'block';
        document.querySelector('.market-content').style.display = 'block';
        this.updateHeaderTitle('marketPanel');
    },

    showRisk() {
        this.hideAllSections();
        document.getElementById('riskStats').style.display = 'block';
        document.querySelector('.risk-section').style.display = 'block';
        document.querySelector('.risk-content').style.display = 'block';
        this.updateHeaderTitle('riskPanel');
    },

    showReports() {
        this.hideAllSections();
        document.getElementById('reportsStats').style.display = 'block';
        document.querySelector('.reports-section').style.display = 'block';
        document.querySelector('.reports-content').style.display = 'block';
        this.updateHeaderTitle('reportsPanel');
    },

    // Hide all sections
    hideAllSections() {
        document.querySelectorAll('.section-stats-card').forEach(card => card.style.display = 'none');
        document.querySelectorAll('.watchlist-section, .portfolio-section, .market-section, .risk-section, .reports-section').forEach(section => section.style.display = 'none');
    },

    // Load content via AJAX
    loadContent(url) {
        const mainContent = document.getElementById('mainContentWrapper');
        
        // Show loading indicator
        mainContent.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            mainContent.innerHTML = html;
            history.pushState({}, '', url);
            
            // Reinitialize any necessary scripts
            if (typeof initializeScripts === 'function') {
                initializeScripts();
            }
        })
        .catch(error => {
            console.error('Error loading content:', error);
            mainContent.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    An error occurred while loading the content. Please try again.
                </div>
            `;
        });
    },

    // Show alert message
    showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const mainContent = document.getElementById('mainContentWrapper');
        mainContent.insertBefore(alertDiv, mainContent.firstChild);
        
        setTimeout(() => alertDiv.remove(), 5000);
    }
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    AppManager.init();
});

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            mainContent.classList.toggle('expanded');
        });
    }

    // Theme Toggle
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('light-theme');
            const icon = this.querySelector('i');
            if (document.body.classList.contains('light-theme')) {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }
        });
    }

    // Timeframe Selector
    const timeframeButtons = document.querySelectorAll('.timeframe-selector .btn');
    timeframeButtons.forEach(button => {
        button.addEventListener('click', function() {
            timeframeButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            // Here you would typically make an API call to update the chart data
            updateChartData(this.textContent.trim());
        });
    });

    // Search Functionality
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value;
            if (query.length >= 2) {
                searchStocks(query);
            }
        }, 300));
    }

    // Notification Toggle
    const notifications = document.querySelector('.notifications');
    if (notifications) {
        notifications.addEventListener('click', function() {
            // Here you would typically show a notification panel
            console.log('Show notifications');
        });
    }

    // Chart Data Update Function
    function updateChartData(timeframe) {
        // This is a placeholder for the actual API call
        console.log(`Updating chart data for timeframe: ${timeframe}`);
        // You would typically make an API call here to get new data
        // and then update the chart using Chart.js
    }

    // Stock Search Function
    function searchStocks(query) {
        // This is a placeholder for the actual API call
        console.log(`Searching for stocks: ${query}`);
        // You would typically make an API call here to search for stocks
    }

    // Debounce Function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Initialize Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle Responsive Tables
    const tables = document.querySelectorAll('.table-responsive');
    tables.forEach(table => {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });

    // Add Loading States for non-login forms
    document.querySelectorAll('button[type="submit"]:not(#loginButton):not(#signupButton)').forEach(button => {
        button.addEventListener('click', function() {
            if (this.form && this.form.checkValidity()) {
                this.disabled = true;
                this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            }
        });
    });

    // Handle create watchlist links
    document.querySelectorAll('a[href*="watchlist:create"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the URL from the clicked element
            const url = e.currentTarget.getAttribute('href');
            
            // Load content via AJAX
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                // Update main content
                document.getElementById('mainContentWrapper').innerHTML = html;
            })
            .catch(error => {
                console.error('Error loading create watchlist form:', error);
            });
            
            return false; // Prevent any default navigation
        });
    });

    // Function to show create watchlist form
    function showCreateWatchlistForm() {
        loadContent('{% url "dashboard:watchlist:create_content" %}');
    }

    // Add click handler to create watchlist button
    const createWatchlistBtn = document.querySelector('[data-action="create-watchlist"]');
    if (createWatchlistBtn) {
        createWatchlistBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showCreateWatchlistForm();
        });
    }

    // Initialize other functionality
    console.log('Main.js loaded');
}); 