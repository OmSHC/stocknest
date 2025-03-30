class WatchlistManager {
    constructor() {
        console.log('WatchlistManager constructor called');
        
        // Initialize properties first
        this.initializeProperties();
        
        // Bind events only if elements exist
        this.bindEvents();
        
        // Initialize modal event listener
        this.initializeModalListener();
        
        // Ensure selected stocks list is visible
        if (this.selectedStocksList) {
            this.selectedStocksList.style.display = 'flex';
            this.selectedStocksList.style.flexWrap = 'wrap';
            this.selectedStocksList.style.gap = '0.5rem';
            console.log('Selected stocks list initialized with styles:', {
                display: this.selectedStocksList.style.display,
                flexWrap: this.selectedStocksList.style.flexWrap,
                gap: this.selectedStocksList.style.gap
            });
        }
        
        // Debug log
        console.log('WatchlistManager initialized with elements:', {
            stockSearch: this.stockSearch,
            stockItems: this.stockItems?.length,
            selectedStocksList: this.selectedStocksList,
            selectedCount: this.selectedCount,
            noResults: this.noResults
        });
    }

    initializeProperties() {
        // DOM Elements - with existence checks
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
        this.createWatchlistModal = document.getElementById('createWatchlistModal');

        // Initialize Bootstrap modal if it exists
        if (this.createWatchlistModal) {
            this.modal = new bootstrap.Modal(this.createWatchlistModal);
        }

        // Log which elements were found and which weren't
        console.log('Elements found:', {
            stockSearch: !!this.stockSearch,
            stockItems: this.stockItems.length,
            selectedStocksList: !!this.selectedStocksList,
            selectedCount: !!this.selectedCount,
            stockListContainer: !!this.stockListContainer,
            noResults: !!this.noResults,
            addStockBtn: !!this.addStockBtn,
            createWatchlistForm: !!this.createWatchlistForm,
            createWatchlistModal: !!this.createWatchlistModal
        });

        // State
        this.selectedStocks = new Set();
        this.currentWatchlistId = null;
    }

    initializeModalListener() {
        if (this.createWatchlistModal) {
            this.createWatchlistModal.addEventListener('shown.bs.modal', () => {
                console.log('Create Watchlist modal shown, reinitializing search');
                this.initializeProperties();
                this.bindEvents();
            });
        }
    }

    bindEvents() {
        // Stock search input
        if (this.stockSearch) {
            console.log('Binding search input event');
            // Remove any existing event listeners
            this.stockSearch.removeEventListener('input', this.handleSearchInput);
            // Add the event listener with onclick
            this.stockSearch.oninput = (e) => {
                console.log('Search input event triggered:', e.target.value);
                this.handleSearchInput();
            };
        } else {
            console.warn('Stock search input element not found');
        }

        // Add stock button
        if (this.addStockBtn) {
            this.addStockBtn.onclick = () => this.handleAddStock();
        }

        // Stock item clicks
        if (this.stockItems && this.stockItems.length > 0) {
            console.log(`Binding click events to ${this.stockItems.length} stock items`);
            this.stockItems.forEach(item => {
                item.onclick = (e) => this.handleStockItemClick(e, item);
            });
        } else {
            console.warn('No stock items found to bind events to');
        }

        // Stock checkboxes
        const checkboxes = document.querySelectorAll('.stock-checkbox');
        console.log(`Found ${checkboxes.length} stock checkboxes`);
        checkboxes.forEach(checkbox => {
            checkbox.onchange = () => this.handleStockSelection();
        });

        // Create watchlist form submission
        if (this.createWatchlistForm) {
            this.createWatchlistForm.onsubmit = (e) => {
                e.preventDefault();
                this.createWatchlist();
            };
        }

        // Watchlist name clicks
        const watchlistNames = document.querySelectorAll('.watchlist-name');
        if (watchlistNames.length > 0) {
            console.log('Binding click events to', watchlistNames.length, 'watchlist names');
            watchlistNames.forEach(name => {
                name.onclick = (e) => {
                    e.preventDefault();
                    const watchlistId = name.getAttribute('data-watchlist-id');
                    console.log('Watchlist name clicked:', name.textContent.trim(), 'ID:', watchlistId);
                    this.loadWatchlistDetails(watchlistId);
                };
            });
        }
    }

    handleSearchInput() {
        // Get the search input value directly from the event
        const searchInput = document.getElementById('stockSearch');
        if (!searchInput) {
            console.error('Search input element not found');
            return;
        }

        const searchText = searchInput.value.toLowerCase().trim();
        let visibleCount = 0;

        // Log the search attempt
        console.log('Raw search input value:', searchInput.value);
        console.log('Search text after trim:', searchText);

        // Get all stock items again to ensure we have the latest
        this.stockItems = document.querySelectorAll('.stock-item');
        console.log('Total stock items:', this.stockItems.length);

        // Hide all stocks first
        this.stockItems.forEach(item => {
            item.style.cssText = 'background: transparent; border: none; padding: 8px; cursor: pointer; display: none;';
        });

        // If search text is less than 3 characters, show message and return
        if (searchText.length < 3) {
            if (this.noResults) {
                this.noResults.textContent = 'Type at least 3 characters to search...';
                this.noResults.style.display = 'block';
            }
            return;
        }

        // Filter stocks based on search text
        this.stockItems.forEach(item => {
            const symbol = item.querySelector('strong')?.textContent?.trim() || '';
            const name = item.querySelector('small')?.textContent?.trim() || '';
            
            // Convert to lowercase for comparison
            const symbolLower = symbol.toLowerCase();
            const nameLower = name.toLowerCase();
            
            // Check for matches
            const matchesSymbol = symbolLower.includes(searchText);
            const matchesName = nameLower.includes(searchText);
            
            // Show matching items
            if (matchesSymbol || matchesName) {
                // Force display block and ensure other styles are preserved
                item.style.cssText = 'background: transparent; border: none; padding: 8px; cursor: pointer; display: block !important;';
                visibleCount++;
                console.log('Match found:', symbol, 'Setting display to block');
                
                // Double check the display style
                const computedStyle = window.getComputedStyle(item);
                console.log('Computed display style:', computedStyle.display);
            }
        });

        // Update no results message
        if (this.noResults) {
            if (visibleCount === 0) {
                this.noResults.textContent = 'No stocks found matching your search.';
                this.noResults.style.display = 'block';
            } else {
                this.noResults.style.display = 'none';
            }
        }

        // Log search results and verify visibility
        console.log(`Found ${visibleCount} matches for "${searchText}"`);
        if (visibleCount > 0) {
            const visibleItems = Array.from(this.stockItems).filter(item => window.getComputedStyle(item).display !== 'none');
            console.log('Actually visible items:', visibleItems.length);
        }
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
        if (e.target.tagName !== 'INPUT') {
            const checkbox = item.querySelector('.stock-checkbox');
            checkbox.checked = !checkbox.checked;
            this.handleStockSelection();
        }
    }

    handleStockSelection() {
        // Get all checked checkboxes
        const selectedCheckboxes = document.querySelectorAll('.stock-checkbox:checked');
        console.log('Selected checkboxes:', selectedCheckboxes.length);
        
        // Update selected count
        if (this.selectedCount) {
            this.selectedCount.textContent = selectedCheckboxes.length;
        }

        // Update selected stocks list
        const selectedStocksList = document.getElementById('selectedStocksList');
        console.log('Selected stocks list element:', selectedStocksList);
        
        if (selectedStocksList) {
            // Clear existing content
            selectedStocksList.innerHTML = '';
            
            // Add each selected stock
            selectedCheckboxes.forEach(checkbox => {
                const stockItem = checkbox.closest('.stock-item');
                if (!stockItem) {
                    console.warn('Stock item not found for checkbox:', checkbox.id);
                    return;
                }

                const symbol = stockItem.querySelector('strong')?.textContent?.trim() || '';
                
                console.log('Creating badge for:', { symbol });
                
                // Create badge for selected stock with improved styling
                const badge = document.createElement('div');
                badge.className = 'selected-stock-badge';
                badge.style.cssText = `
                    display: inline-flex !important;
                    align-items: center !important;
                    background-color: rgba(13, 110, 253, 0.1) !important;
                    border: 1px solid rgba(13, 110, 253, 0.3) !important;
                    color: #0d6efd !important;
                    padding: 6px 10px !important;
                    border-radius: 20px !important;
                    margin: 4px !important;
                    font-size: 0.9em !important;
                    font-weight: 500 !important;
                    visibility: visible !important;
                    position: relative !important;
                    z-index: 1001 !important;
                    transition: all 0.2s ease-in-out !important;
                    cursor: default !important;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
                `;
                
                // Set badge content with improved layout
                badge.innerHTML = `
                    <span class="stock-symbol" style="margin-right: 6px;">${symbol}</span>
                    <button type="button" class="btn-close" 
                            style="font-size: 0.7em; 
                                   padding: 0px;
                                   width: 16px;
                                   height: 16px;
                                   border-radius: 50%;
                                   display: inline-flex !important;
                                   align-items: center;
                                   justify-content: center;
                                   background: rgba(13, 110, 253, 0.2);
                                   opacity: 0.8;
                                   cursor: pointer;
                                   transition: all 0.2s ease;"
                            aria-label="Remove ${symbol}"
                            onmouseover="this.style.opacity='1'; this.style.background='rgba(13, 110, 253, 0.3)'"
                            onmouseout="this.style.opacity='0.8'; this.style.background='rgba(13, 110, 253, 0.2)'"
                            onclick="event.preventDefault(); event.stopPropagation(); window.watchlistManager.removeStock('${checkbox.id}')"></button>
                `;
                
                // Add hover effect to the badge
                badge.addEventListener('mouseover', () => {
                    badge.style.backgroundColor = 'rgba(13, 110, 253, 0.15)';
                    badge.style.borderColor = 'rgba(13, 110, 253, 0.4)';
                });
                
                badge.addEventListener('mouseout', () => {
                    badge.style.backgroundColor = 'rgba(13, 110, 253, 0.1)';
                    badge.style.borderColor = 'rgba(13, 110, 253, 0.3)';
                });
                
                // Add badge to selected stocks list
                selectedStocksList.appendChild(badge);
                
                // Log for debugging
                console.log('Added badge to container:', {
                    badge: badge.outerHTML,
                    containerChildren: selectedStocksList.children.length,
                    badgeDisplay: window.getComputedStyle(badge).display,
                    badgeVisibility: window.getComputedStyle(badge).visibility
                });
            });
        } else {
            console.warn('Selected stocks list container not found');
        }
    }

    removeStock(checkboxId) {
        console.log('Removing stock with checkbox ID:', checkboxId);
        const checkbox = document.getElementById(checkboxId);
        if (checkbox) {
            checkbox.checked = false;
            this.handleStockSelection();
            
            // Hide the stock item if it doesn't match the current search
            const stockItem = checkbox.closest('.stock-item');
            if (stockItem && this.stockSearch) {
                const searchText = this.stockSearch.value.toLowerCase().trim();
                if (searchText.length >= 3) {
                    const symbol = stockItem.querySelector('strong')?.textContent?.trim() || '';
                    const name = stockItem.querySelector('small')?.textContent?.trim() || '';
                    const matches = symbol.toLowerCase().includes(searchText) || 
                                  name.toLowerCase().includes(searchText);
                    stockItem.style.display = matches ? 'block' : 'none';
                } else {
                    stockItem.style.display = 'none';
                }
            }
            
            console.log('Stock removed successfully');
        } else {
            console.warn('Checkbox not found:', checkboxId);
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
        const form = document.getElementById('createWatchlistForm');
        const name = document.getElementById('watchlistName').value;
        const description = document.getElementById('watchlistDescription').value;
        const visibility = document.getElementById('watchlistVisibility')?.value || 'private';
        
        if (!name) {
            this.showAlert('danger', 'Watchlist name is required');
            return;
        }
        
        // Show loading state on the submit button
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating...';
        
        try {
            // Create FormData object
            const formData = new FormData(form);
            
            // Add selected stocks
            const selectedStocks = Array.from(document.querySelectorAll('.stock-checkbox:checked')).map(cb => cb.value);
            formData.delete('stocks'); // Remove any existing stocks field
            selectedStocks.forEach(stockId => formData.append('stocks', stockId));
            
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            const data = await response.json();
            
            if (response.ok) {
                // Hide the modal
                const modal = document.getElementById('createWatchlistModal');
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
                
                // Show success message
                this.showAlert('success', data.message);
                
                // Reset form
                this.resetForm();
                
                // Redirect if URL provided
                if (data.redirect) {
                    window.location.href = data.redirect;
                }
            } else {
                this.showAlert('danger', data.error || 'Error creating watchlist');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showAlert('danger', 'Error creating watchlist');
        } finally {
            // Restore button state
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
        if (this.stockSearch) {
            this.stockSearch.value = '';
        }
        if (this.stockItems) {
            this.stockItems.forEach(item => {
                item.style.display = 'none';
            });
        }
        if (this.noResults) {
            this.noResults.textContent = 'Type to search for stocks...';
            this.noResults.style.display = 'block';
        }
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
        console.log('Showing watchlist:', watchlistId);
        
        // Get the elements we need
        const detailsContainer = document.getElementById('watchlistDetails');
        const nameElement = document.getElementById('watchlistDetailsName');
        const contentElement = document.getElementById('watchlistDetailsContent');
        
        // Log which elements were found
        console.log('Elements found:', {
            detailsContainer: !!detailsContainer,
            nameElement: !!nameElement,
            contentElement: !!contentElement
        });
        
        // Only proceed if we have all required elements
        if (!detailsContainer || !nameElement || !contentElement) {
            console.warn('Required elements not found for showing watchlist');
            return;
        }
        
        // Show the details container
        detailsContainer.style.display = 'block';
        
        // Update the name (safely)
        try {
            nameElement.textContent = 'Loading...';
        } catch (error) {
            console.error('Error updating name element:', error);
        }
        
        // Load the watchlist details
        this.loadWatchlistDetails(watchlistId);
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
        try {
            window.watchlistManager = new WatchlistManager();
        } catch (error) {
            console.error('Error initializing WatchlistManager:', error);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing WatchlistManager');
    window.watchlistManager = new WatchlistManager();
}); 