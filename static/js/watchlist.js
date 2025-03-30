class WatchlistManager {
    constructor() {
        console.log('WatchlistManager constructor called');
        
        // DOM Elements
        this.stockSearch = document.getElementById('stockSearch');
        this.stockItems = document.querySelectorAll('.stock-item');
        this.selectedStocksList = document.getElementById('selectedStocksList');
        this.selectedCount = document.getElementById('selectedCount');
        this.stockListContainer = document.querySelector('.stock-list-container');
        this.noResults = document.getElementById('noResults');
        this.searchLoading = document.getElementById('searchLoading');
        this.addStockBtn = document.getElementById('addStock');
        this.createWatchlistForm = document.getElementById('createWatchlistForm');
        this.watchlistDetailsContainer = document.getElementById('watchlistDetails');
        this.watchlistDetailsContent = document.getElementById('watchlistDetailsContent');
        this.watchlistDetailsName = document.getElementById('watchlistDetailsName');
        this.watchlistDetailsLoading = document.getElementById('watchlistDetailsLoading');
        this.watchlistsContainer = document.getElementById('watchlistsContainer');
        this.createWatchlistFormContainer = document.getElementById('createWatchlistFormContainer');

        // State
        this.selectedStocks = new Set();
        this.currentWatchlistId = null;

        // Bind event handlers
        this.bindEvents();
        
        // Debug log
        console.log('WatchlistManager initialized');
        console.log('Watchlist details container found:', !!this.watchlistDetailsContainer);
        console.log('Found watchlist names:', document.querySelectorAll('.watchlist-name').length);
    }

    bindEvents() {
        // Stock search input
        if (this.stockSearch) {
            this.stockSearch.addEventListener('input', () => this.handleSearchInput());
        }

        // Add stock button
        if (this.addStockBtn) {
            this.addStockBtn.addEventListener('click', () => this.handleAddStock());
        }

        // Stock item clicks
        if (this.stockItems) {
            this.stockItems.forEach(item => {
                item.addEventListener('click', (e) => this.handleStockItemClick(e, item));
            });
        }

        // Keyboard navigation
        if (this.stockSearch) {
            this.stockSearch.addEventListener('keydown', (e) => this.handleKeyboardNavigation(e));
        }

        // Create watchlist form submission - allow normal form submission
        if (this.createWatchlistForm && this.createWatchlistForm.classList.contains('ajax-form')) {
            this.createWatchlistForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createWatchlist();
            });
        }

        // Watchlist name clicks
        const watchlistNames = document.querySelectorAll('.watchlist-name');
        console.log('Binding click events to', watchlistNames.length, 'watchlist names');
        
        watchlistNames.forEach(name => {
            name.addEventListener('click', (e) => {
                e.preventDefault();
                const watchlistId = name.getAttribute('data-watchlist-id');
                console.log('Watchlist name clicked:', name.textContent.trim(), 'ID:', watchlistId);
                this.loadWatchlistDetails(watchlistId);
            });
        });
    }

    handleSearchInput() {
        const searchText = this.stockSearch.value.toLowerCase();
        let visibleCount = 0;

        this.stockItems.forEach(item => {
            const symbol = item.querySelector('strong').textContent.toLowerCase();
            const name = item.querySelector('small').textContent.toLowerCase();
            const matches = symbol.includes(searchText) || name.includes(searchText);
            
            item.style.display = matches ? 'block' : 'none';
            if (matches) visibleCount++;
        });

        // Show/hide container and messages
        this.stockListContainer.style.display = searchText ? 'block' : 'none';
        this.noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }

    handleAddStock() {
        const searchText = this.stockSearch.value.toLowerCase();
        const visibleItems = Array.from(this.stockItems).filter(item => 
            item.style.display !== 'none' && 
            !item.querySelector('.stock-checkbox').checked
        );
        
        if (visibleItems.length > 0) {
            this.handleStockSelection(visibleItems[0]);
        }
    }

    handleStockItemClick(e, item) {
        if (e.target !== item.querySelector('.stock-checkbox')) {
            this.handleStockSelection(item);
        }
    }

    handleKeyboardNavigation(e) {
        if (e.key === 'Enter' && this.stockSearch.value) {
            e.preventDefault();
            this.handleAddStock();
        }
    }

    handleStockSelection(item) {
        const checkbox = item.querySelector('.stock-checkbox');
        const stockId = checkbox.value;
        const symbol = item.querySelector('strong').textContent;
        const name = item.querySelector('small').textContent;

        if (checkbox.checked) {
            this.selectedStocks.add(stockId);
        } else {
            this.selectedStocks.delete(stockId);
        }

        this.updateSelectedCount();
        this.updateSelectedStocksList();
    }

    updateSelectedCount() {
        this.selectedCount.textContent = this.selectedStocks.size;
    }

    updateSelectedStocksList() {
        this.selectedStocksList.innerHTML = Array.from(this.selectedStocks).map(stockId => {
            const item = Array.from(this.stockItems).find(item => 
                item.querySelector('.stock-checkbox').value === stockId
            );
            const symbol = item.querySelector('strong').textContent;
            return `
                <span class="badge bg-primary">
                    ${symbol}
                    <button type="button" class="btn-close btn-close-white ms-1" 
                            onclick="watchlistManager.removeStock('${stockId}')"></button>
                </span>
            `;
        }).join('');
    }

    removeStock(stockId) {
        const item = Array.from(this.stockItems).find(item => 
            item.querySelector('.stock-checkbox').value === stockId
        );
        if (item) {
            item.querySelector('.stock-checkbox').checked = false;
            this.selectedStocks.delete(stockId);
            this.updateSelectedCount();
            this.updateSelectedStocksList();
        }
    }

    showCreateWatchlistForm() {
        // Allow default navigation behavior by not manipulating the display
        return true;
    }

    hideCreateWatchlistForm() {
        if (this.createWatchlistFormContainer) {
            this.createWatchlistFormContainer.style.display = 'none';
            if (this.watchlistsContainer) {
                this.watchlistsContainer.style.display = 'block';
            }
        }
    }

    hideWatchlistDetails() {
        if (this.watchlistDetailsContainer) {
            this.watchlistDetailsContainer.style.display = 'none';
            if (this.watchlistsContainer) {
                this.watchlistsContainer.style.display = 'block';
            }
        }
    }

    async createWatchlist() {
        const name = document.getElementById('watchlistName').value;
        const description = document.getElementById('watchlistDescription').value;
        const visibility = document.getElementById('watchlistVisibility').value;
        
        if (!name) {
            this.showAlert('danger', 'Watchlist name is required');
            return;
        }
        
        // Show loading state on the submit button
        const submitButton = document.querySelector('#createWatchlistForm button[type="submit"]');
        const originalText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating...';
        
        try {
            // Create FormData object
            const formData = new FormData();
            formData.append('name', name);
            formData.append('description', description);
            formData.append('visibility', visibility);
            
            const response = await fetch('/dashboard/watchlist/create/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: formData
            });

            if (response.ok) {
                // Reset form
                this.resetForm();
                
                // Show success message
                this.showAlert('success', 'Watchlist created successfully');
                
                // Hide the form and show the watchlists
                this.hideCreateWatchlistForm();
                
                // Reload the page to show the new watchlist
                window.location.reload();
            } else {
                const data = await response.json();
                this.showAlert('danger', data.error || 'Error creating watchlist');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showAlert('danger', 'Error creating watchlist');
        } finally {
            // Reset button state
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        }
    }

    resetForm() {
        if (this.createWatchlistForm) {
            this.createWatchlistForm.reset();
        }
        this.selectedStocks.clear();
        this.updateSelectedCount();
        this.updateSelectedStocksList();
        this.stockSearch.value = '';
        this.stockListContainer.style.display = 'none';
        this.noResults.style.display = 'none';
    }

    showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    }

    // Additional methods for watchlist management
    async editWatchlist(watchlistId) {
        // TODO: Implement edit functionality
        console.log('Edit watchlist:', watchlistId);
    }

    async deleteWatchlist(watchlistId) {
        if (confirm('Are you sure you want to delete this watchlist?')) {
            try {
                const response = await fetch(`/api/watchlists/${watchlistId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });

                if (response.ok) {
                    this.showAlert('success', 'Watchlist deleted successfully');
                    location.reload();
                } else {
                    this.showAlert('danger', 'Error deleting watchlist');
                }
            } catch (error) {
                console.error('Error:', error);
                this.showAlert('danger', 'Error deleting watchlist');
            }
        }
    }

    async viewWatchlist(watchlistId) {
        // TODO: Implement view functionality
        console.log('View watchlist:', watchlistId);
    }

    async loadWatchlistDetails(watchlistId) {
        console.log('Loading watchlist details for ID:', watchlistId);
        
        // Save the current watchlist ID
        this.currentWatchlistId = watchlistId;
        
        // Show the details container
        if (this.watchlistDetailsContainer) {
            console.log('Watchlist details container found');
            this.watchlistDetailsContainer.style.display = 'block';
            this.watchlistDetailsLoading.style.display = 'block';
            this.watchlistDetailsContent.innerHTML = '';
            this.watchlistDetailsName.textContent = 'Loading...';
            
            try {
                // Scroll to the details container
                this.watchlistDetailsContainer.scrollIntoView({ behavior: 'smooth' });
                
                // Fetch watchlist details
                console.log('Fetching from URL:', `/dashboard/watchlist/${watchlistId}/`);
                const response = await fetch(`/dashboard/watchlist/${watchlistId}/`, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                console.log('Response status:', response.status);
                
                // Check if the response is HTML
                const contentType = response.headers.get('content-type');
                console.log('Content type:', contentType);
                
                if (contentType && contentType.includes('text/html')) {
                    // For HTML response, we'll extract the main content
                    const html = await response.text();
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    
                    // Get the watchlist name
                    const nameElement = doc.querySelector('.card-header h4');
                    if (nameElement) {
                        this.watchlistDetailsName.innerHTML = nameElement.innerHTML;
                    }
                    
                    // Get the content
                    const contentElement = doc.querySelector('.card-body');
                    if (contentElement) {
                        this.watchlistDetailsContent.innerHTML = contentElement.innerHTML;
                    }
                } else {
                    // For JSON response
                    const data = await response.json();
                    console.log('Response data:', data);
                    
                    if (response.ok) {
                        this.watchlistDetailsName.textContent = data.name;
                        
                        // Create content for the watchlist
                        let content = '';
                        
                        if (data.description) {
                            content += `<p class="text-muted">${data.description}</p>`;
                        }
                        
                        content += `
                            <div class="row mt-4">
                                <div class="col-12">
                                    <h5 class="text-light mb-3">Stocks in Watchlist</h5>
                                    <div class="table-responsive">
                                        <table class="table table-dark table-hover">
                                            <thead>
                                                <tr>
                                                    <th>Symbol</th>
                                                    <th>Name</th>
                                                    <th>Current Price</th>
                                                    <th>Change</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                        `;
                        
                        if (data.stocks && data.stocks.length > 0) {
                            data.stocks.forEach(stock => {
                                content += `
                                    <tr>
                                        <td>${stock.symbol}</td>
                                        <td>${stock.name}</td>
                                        <td>${stock.current_price || 'N/A'}</td>
                                        <td>
                                            <span class="${stock.change >= 0 ? 'text-success' : 'text-danger'}">
                                                ${stock.change_percentage ? stock.change_percentage.toFixed(2) + '%' : 'N/A'}
                                            </span>
                                        </td>
                                        <td>
                                            <button class="btn btn-sm btn-outline-light" onclick="watchlistManager.viewStockDetails('${stock.symbol}')">
                                                <i class="fas fa-chart-line"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger" onclick="watchlistManager.removeStockFromWatchlist(${watchlistId}, '${stock.symbol}')">
                                                <i class="fas fa-times"></i>
                                            </button>
                                        </td>
                                    </tr>
                                `;
                            });
                        } else {
                            content += `
                                <tr>
                                    <td colspan="5" class="text-center">No stocks in this watchlist yet.</td>
                                </tr>
                            `;
                        }
                        
                        content += `
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        `;
                        
                        this.watchlistDetailsContent.innerHTML = content;
                    } else {
                        this.watchlistDetailsContent.innerHTML = `
                            <div class="alert alert-danger">
                                Error loading watchlist details: ${data.error || 'Unknown error'}
                            </div>
                        `;
                    }
                }
            } catch (error) {
                console.error('Error loading watchlist details:', error);
                this.watchlistDetailsContent.innerHTML = `
                    <div class="alert alert-danger">
                        Error loading watchlist details. Please try again later.
                    </div>
                `;
            } finally {
                // Hide loading indicator
                this.watchlistDetailsLoading.style.display = 'none';
            }
        } else {
            console.error('Watchlist details container not found');
        }
    }

    async viewStockDetails(symbol) {
        console.log('View stock details:', symbol);
        // TODO: Implement stock details view
    }

    async removeStockFromWatchlist(watchlistId, symbol) {
        console.log('Remove stock from watchlist:', watchlistId, symbol);
        // TODO: Implement remove stock functionality
    }

    // Initialize the watchlist manager
    static init() {
        console.log('DOM fully loaded, initializing WatchlistManager');
        window.watchlistManager = new WatchlistManager();
    }
}

// Make sure we initialize only when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    WatchlistManager.init();
}); 