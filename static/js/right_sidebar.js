class RightSidebar {
    constructor() {
        this.sidebar = document.getElementById('rightSidebar');
        this.overlay = document.getElementById('rightSidebarOverlay');
        this.closeBtn = document.getElementById('closeRightSidebar');
        this.mainContent = document.getElementById('mainContent');
        this.currentPanel = null;
        this.middleSidebar = document.getElementById('middleSidebar');
        
        // Initialize the create watchlist modal
        const modalElement = document.getElementById('createWatchlistModal');
        if (modalElement) {
            this.createWatchlistModal = new bootstrap.Modal(modalElement);
            
            // Add event listener for modal hidden event
            modalElement.addEventListener('hidden.bs.modal', () => {
                if (window.watchlistManager) {
                    window.watchlistManager.resetForm();
                }
            });
        }

        if (!this.sidebar || !this.overlay || !this.closeBtn || !this.mainContent || !this.middleSidebar) {
            console.error('Required elements not found for RightSidebar');
            return;
        }

        this.init();
    }

    init() {
        // Initialize event listeners
        this.closeBtn.addEventListener('click', () => this.close());
        
        // Ensure overlay click handler is properly bound
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.close();
        });

        // Initialize panel triggers
        this.initializePanelTriggers();
        this.initializeActionButtons();
        this.initializeCreateWatchlistButton();
    }

    initializePanelTriggers() {
        // Portfolio trigger
        document.querySelector('.portfolio-trigger').addEventListener('click', () => {
            this.openPortfolio();
        });

        // Market trigger
        document.querySelector('.market-trigger').addEventListener('click', () => {
            this.openMarket();
        });

        // Risk trigger
        document.querySelector('.risk-trigger').addEventListener('click', () => {
            this.openRisk();
        });

        // Reports trigger
        document.querySelector('.reports-trigger').addEventListener('click', () => {
            this.openReports();
        });

        // Watchlist trigger
        document.querySelector('.watchlist-trigger').addEventListener('click', () => {
            this.openWatchlist();
        });

        // User profile trigger
        document.querySelector('.user-toggle').addEventListener('click', (e) => {
            e.preventDefault();
            this.openUserProfile();
        });
    }

    initializeActionButtons() {
        // Handle watchlist creation button
        document.querySelector('[data-action="create-watchlist"]')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.loadCreateWatchlistForm();
            this.close(); // Close the sidebar after clicking
        });

        // Handle other action buttons similarly
        document.querySelector('[data-action="buy-stock"]')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.loadBuyStockForm();
            this.close();
        });

        document.querySelector('[data-action="sell-stock"]')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.loadSellStockForm();
            this.close();
        });
    }

    initializeCreateWatchlistButton() {
        // Add click handler for all Create New Watchlist buttons
        document.querySelectorAll('.create-watchlist-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                if (this.createWatchlistModal) {
                    this.createWatchlistModal.show();
                }
            });
        });
    }

    resetCreateWatchlistForm() {
        const form = document.getElementById('createWatchlistForm');
        if (form) {
            form.reset();
            // Reset any other form elements
            const selectedStocksList = document.getElementById('selectedStocksList');
            if (selectedStocksList) {
                selectedStocksList.innerHTML = '';
            }
            const selectedCount = document.getElementById('selectedCount');
            if (selectedCount) {
                selectedCount.textContent = '0';
            }
        }
    }

    loadCreateWatchlistForm() {
        const formHTML = `
            <div class="card">
                <div class="card-header">
                    <h4>Create New Watchlist</h4>
                </div>
                <div class="card-body">
                    <form id="createWatchlistForm" class="needs-validation" novalidate>
                        <div class="mb-3">
                            <label for="watchlistName" class="form-label">Watchlist Name</label>
                            <input type="text" class="form-control" id="watchlistName" required>
                        </div>
                        <div class="mb-3">
                            <label for="watchlistDescription" class="form-label">Description</label>
                            <textarea class="form-control" id="watchlistDescription" rows="3"></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Visibility</label>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="visibility" id="private" value="private" checked>
                                <label class="form-check-label" for="private">Private</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="visibility" id="public" value="public">
                                <label class="form-check-label" for="public">Public</label>
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary">Create Watchlist</button>
                        <button type="button" class="btn btn-secondary" onclick="window.history.back()">Cancel</button>
                    </form>
                </div>
            </div>
        `;
        
        this.mainContent.innerHTML = formHTML;
        this.initializeCreateWatchlistForm();
    }

    loadBuyStockForm() {
        const formHTML = `
            <div class="card">
                <div class="card-header">
                    <h4>Buy Stock</h4>
                </div>
                <div class="card-body">
                    <form id="buyStockForm" class="needs-validation" novalidate>
                        <div class="mb-3">
                            <label for="stockSymbol" class="form-label">Stock Symbol</label>
                            <input type="text" class="form-control" id="stockSymbol" required>
                        </div>
                        <div class="mb-3">
                            <label for="quantity" class="form-label">Quantity</label>
                            <input type="number" class="form-control" id="quantity" required min="1">
                        </div>
                        <div class="mb-3">
                            <label for="price" class="form-label">Price per Share</label>
                            <input type="number" class="form-control" id="price" required step="0.01">
                        </div>
                        <button type="submit" class="btn btn-success">Place Buy Order</button>
                        <button type="button" class="btn btn-secondary" onclick="window.history.back()">Cancel</button>
                    </form>
                </div>
            </div>
        `;
        
        this.mainContent.innerHTML = formHTML;
        this.initializeBuyStockForm();
    }

    loadSellStockForm() {
        const formHTML = `
            <div class="card">
                <div class="card-header">
                    <h4>Sell Stock</h4>
                </div>
                <div class="card-body">
                    <form id="sellStockForm" class="needs-validation" novalidate>
                        <div class="mb-3">
                            <label for="stockSymbol" class="form-label">Stock Symbol</label>
                            <input type="text" class="form-control" id="stockSymbol" required>
                        </div>
                        <div class="mb-3">
                            <label for="quantity" class="form-label">Quantity</label>
                            <input type="number" class="form-control" id="quantity" required min="1">
                        </div>
                        <div class="mb-3">
                            <label for="price" class="form-label">Price per Share</label>
                            <input type="number" class="form-control" id="price" required step="0.01">
                        </div>
                        <button type="submit" class="btn btn-danger">Place Sell Order</button>
                        <button type="button" class="btn btn-secondary" onclick="window.history.back()">Cancel</button>
                    </form>
                </div>
            </div>
        `;
        
        this.mainContent.innerHTML = formHTML;
        this.initializeSellStockForm();
    }

    initializeCreateWatchlistForm() {
        const form = document.getElementById('createWatchlistForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                if (form.checkValidity()) {
                    // Use the WatchlistManager's createWatchlist method
                    if (window.watchlistManager) {
                        window.watchlistManager.createWatchlist();
                    } else {
                        console.error('WatchlistManager not initialized');
                    }
                }
                form.classList.add('was-validated');
            });
        }
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }

    open(panelType, config) {
        // Hide all panels
        document.querySelectorAll('.panel-content').forEach(panel => {
            panel.style.display = 'none';
        });

        // Show selected panel
        const panel = document.getElementById(`${panelType}Panel`);
        if (panel) {
            panel.style.display = 'block';
        }

        // Update header
        this.updateHeader(config);

        // Show sidebar
        this.sidebar.classList.add('active');
        this.overlay.classList.add('active');
        document.body.style.overflow = 'hidden';

        this.currentPanel = panelType;
    }

    close() {
        this.sidebar.classList.remove('active');
        this.overlay.classList.remove('active');
        document.body.style.overflow = '';
        this.currentPanel = null;
    }

    updateHeader(config) {
        const icon = this.sidebar.querySelector('.panel-icon');
        const title = this.sidebar.querySelector('.panel-title');
        const subtitle = this.sidebar.querySelector('.panel-subtitle');

        icon.className = `panel-icon fas ${config.icon}`;
        title.textContent = config.title;
        subtitle.textContent = config.subtitle;
    }

    async loadWatchlists() {
        try {
            console.log('Loading watchlists...');
            const response = await fetch('/api/watchlists/');
            console.log('Watchlist API response:', response);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Watchlist data:', data);
            
            // Update personal watchlists
            const personalWatchlistsContainer = document.querySelector('.row');
            if (personalWatchlistsContainer && data.personal) {
                if (data.personal.length === 0) {
                    personalWatchlistsContainer.innerHTML = `
                        <div class="col-12">
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle me-2"></i>
                                You haven't created any watchlists yet. Click the "Create New Watchlist" button to get started!
                            </div>
                        </div>
                    `;
                } else {
                    personalWatchlistsContainer.innerHTML = data.personal.map(watchlist => `
                        <div class="col-md-6 col-lg-4 mb-3">
                            <div class="card bg-dark border-light h-100">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between align-items-start mb-2">
                                        <h6 class="card-title text-light mb-0">
                                            <i class="fas fa-list text-primary me-2"></i>
                                            ${watchlist.name}
                                        </h6>
                                        <span class="badge bg-primary">${watchlist.stocks.length} stocks</span>
                                    </div>
                                    ${watchlist.description ? `<p class="card-text text-muted small mb-3">${watchlist.description}</p>` : ''}
                                    <div class="d-flex justify-content-between align-items-center mt-auto">
                                        <small class="text-muted">Last updated: ${new Date(watchlist.updated_at).toLocaleDateString()}</small>
                                        <div class="btn-group">
                                            <a href="/watchlist/${watchlist.id}/" class="btn btn-sm btn-outline-light" title="View">
                                                <i class="fas fa-eye"></i>
                                            </a>
                                            <button class="btn btn-sm btn-outline-light" onclick="watchlistManager.editWatchlist(${watchlist.id})" title="Edit">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger" onclick="watchlistManager.deleteWatchlist(${watchlist.id})" title="Delete">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('');
                }
                console.log('Updated personal watchlists');
            } else {
                console.warn('Personal watchlists container not found or no data');
            }

            // Update global watchlists
            const globalWatchlistsContainer = document.getElementById('globalWatchlists');
            if (globalWatchlistsContainer && data.global) {
                if (data.global.length === 0) {
                    globalWatchlistsContainer.innerHTML = `
                        <li class="list-group-item bg-dark text-light">
                            <i class="fas fa-info-circle me-2"></i>
                            No global watchlists available.
                        </li>
                    `;
                } else {
                    globalWatchlistsContainer.innerHTML = data.global.map(watchlist => `
                        <li class="list-group-item bg-dark text-light">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <i class="fas fa-globe text-primary me-2"></i>
                                    ${watchlist.name}
                                </div>
                                <span class="badge bg-primary">${watchlist.stocks.length} stocks</span>
                            </div>
                        </li>
                    `).join('');
                }
                console.log('Updated global watchlists');
            } else {
                console.warn('Global watchlists container not found or no data');
            }
        } catch (error) {
            console.error('Error loading watchlists:', error);
            // Show error message to user
            const errorMessage = document.createElement('div');
            errorMessage.className = 'alert alert-danger';
            errorMessage.textContent = 'Failed to load watchlists. Please try again later.';
            
            const personalWatchlistsContainer = document.querySelector('.row');
            if (personalWatchlistsContainer) {
                personalWatchlistsContainer.innerHTML = '';
                personalWatchlistsContainer.appendChild(errorMessage);
            }
        }
    }

    async loadPortfolioData() {
        try {
            const response = await fetch('/api/portfolio/summary/');
            const data = await response.json();
            
            document.getElementById('portfolioValue').textContent = 
                new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })
                    .format(data.total_value);
            
            const changeElement = document.getElementById('todayChange');
            const change = data.today_change;
            const changePercent = data.today_change_percentage;
            
            changeElement.textContent = `${change >= 0 ? '+' : ''}${change} (${changePercent}%)`;
            changeElement.className = `value ${change >= 0 ? 'text-success' : 'text-danger'}`;
        } catch (error) {
            console.error('Error loading portfolio data:', error);
        }
    }

    async loadMarketData() {
        try {
            const response = await fetch('/api/market/overview/');
            const data = await response.json();
            
            // Update market indices
            const indicesContainer = document.querySelector('.market-indices');
            indicesContainer.innerHTML = data.indices.map(index => `
                <div class="summary-item">
                    <span class="label">${index.name}</span>
                    <span class="value ${index.change >= 0 ? 'text-success' : 'text-danger'}">
                        ${index.value} (${index.change}%)
                    </span>
                </div>
            `).join('');

            // Update news feed
            const newsFeed = document.querySelector('.news-feed');
            newsFeed.innerHTML = data.news.map(item => `
                <div class="news-item">
                    <div class="news-title">${item.title}</div>
                    <div class="news-meta">
                        ${item.source} • ${new Date(item.date).toLocaleDateString()}
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading market data:', error);
        }
    }

    openUserProfile() {
        // Hide all panels in middle sidebar
        document.querySelectorAll('.middle-sidebar-panel').forEach(panel => {
            panel.style.display = 'none';
        });

        // Show user profile panel
        const userProfilePanel = document.getElementById('userProfilePanel');
        if (userProfilePanel) {
            userProfilePanel.style.display = 'block';
        }

        // Update middle sidebar header
        const header = this.middleSidebar.querySelector('.middle-sidebar-header');
        if (header) {
            header.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="fas fa-user-circle me-2"></i>
                    <h4 class="mb-0">User Profile</h4>
                </div>
            `;
        }

        // Show middle sidebar
        this.middleSidebar.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Load user profile data
        this.loadUserProfileData();
    }

    async loadUserProfileData() {
        try {
            const response = await fetch('/api/user/profile/');
            const data = await response.json();
            
            const content = this.middleSidebar.querySelector('.middle-sidebar-content');
            if (content) {
                content.innerHTML = `
                    <div class="user-profile-content">
                        <div class="text-center mb-4">
                            <div class="avatar-large mb-3">
                                <i class="fas fa-user-circle fa-4x"></i>
                            </div>
                            <h5 class="mb-1">${data.username}</h5>
                            <p class="text-muted mb-0">${data.email}</p>
                        </div>
                        
                        <div class="profile-stats">
                            <div class="stats-item">
                                <i class="fas fa-briefcase"></i>
                                <div class="stats-info">
                                    <span class="stats-label">Portfolio Value</span>
                                    <span class="stats-value">${data.portfolio_value}</span>
                                </div>
                            </div>
                            <div class="stats-item">
                                <i class="fas fa-chart-line"></i>
                                <div class="stats-info">
                                    <span class="stats-label">Total Returns</span>
                                    <span class="stats-value ${data.total_returns >= 0 ? 'positive' : 'negative'}">
                                        ${data.total_returns}
                                    </span>
                                </div>
                            </div>
                            <div class="stats-item">
                                <i class="fas fa-list"></i>
                                <div class="stats-info">
                                    <span class="stats-label">Watchlists</span>
                                    <span class="stats-value">${data.watchlist_count}</span>
                                </div>
                            </div>
                        </div>

                        <div class="quick-actions mt-4">
                            <h5>Quick Actions</h5>
                            <button class="btn btn-outline-light w-100 mb-2" onclick="window.location.href='/settings/'">
                                <i class="fas fa-cog"></i> Settings
                            </button>
                            <button class="btn btn-outline-light w-100 mb-2" onclick="window.location.href='/profile/'">
                                <i class="fas fa-user-edit"></i> Edit Profile
                            </button>
                            <button class="btn btn-outline-danger w-100" onclick="window.location.href='/logout/'">
                                <i class="fas fa-sign-out-alt"></i> Logout
                            </button>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading user profile:', error);
        }
    }

    openWatchlist() {
        // Hide all panels
        this.hideAllPanels();
        
        // Show watchlist panel
        const watchlistSection = document.querySelector('.watchlist-section');
        watchlistSection.style.display = 'block';
        
        // Update sidebar header
        const headerTitle = document.querySelector('.middle-sidebar-header h4');
        headerTitle.textContent = 'Watchlists';
        
        // Load watchlist data
        this.loadWatchlistData();
    }

    loadWatchlistData() {
        fetch('/api/watchlists/')
            .then(response => response.json())
            .then(data => {
                const personalWatchlists = document.querySelector('.watchlist-section .list-group');
                personalWatchlists.innerHTML = '';
                
                if (data.personal_watchlists.length === 0) {
                    personalWatchlists.innerHTML = '<div class="list-group-item text-muted">No watchlists created yet</div>';
                } else {
                    data.personal_watchlists.forEach(watchlist => {
                        const watchlistItem = `
                            <a href="#" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                                <div class="d-flex align-items-center">
                                    <div class="watchlist-icon me-2" style="background: rgba(241, 196, 15, 0.1); color: #f1c40f;">
                                        <i class="fas fa-star"></i>
                                    </div>
                                    <div>
                                        <div class="watchlist-name">${watchlist.name}</div>
                                        <div class="watchlist-meta">${watchlist.description || ''}</div>
                                    </div>
                                </div>
                                <span class="badge bg-primary rounded-pill">${watchlist.stocks.length}</span>
                            </a>
                        `;
                        personalWatchlists.innerHTML += watchlistItem;
                    });
                }
            })
            .catch(error => {
                console.error('Error loading watchlist data:', error);
            });
    }

    showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert alert before the form
        const form = document.getElementById('createWatchlistForm');
        if (form) {
            form.parentNode.insertBefore(alertDiv, form);
            
            // Auto dismiss after 5 seconds
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    }
}

// Initialize the right sidebar when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.rightSidebar = new RightSidebar();
}); 