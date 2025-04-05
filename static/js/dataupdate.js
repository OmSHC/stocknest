// Only declare the class if it hasn't been declared yet
console.log('dataupdate.js is being loaded');
if (typeof DataUpdateManager === 'undefined') {
    class DataUpdateManager {
        constructor() {
            console.log('DataUpdateManager constructor called');
            this.initializeElements();
            this.initializeProperties();
            this.initializeModalListener();
            this.init();
            this.handleDirectUrlAccess();
            console.log('DataUpdateManager initialized');
        }

        initializeElements() {
            console.log('Initializing DataUpdateManager elements');
            try {
                // Initialize core elements
                this.mainContent = document.getElementById('mainContent');
                this.createWatchlistForm = document.getElementById('createWatchlistForm');
                this.watchlistsContainer = document.getElementById('watchlistsContainer');
                
                // Initialize Data Update specific elements
                this.updateStockQuotesBtn = document.querySelector('.dataupdate-section button[onclick*="updateStockQuotes"]');
                this.updateHistoricalDataBtn = document.querySelector('.dataupdate-section a[onclick*="updateHistoricalData"]');
                this.updateStockInfoBtn = document.querySelector('.dataupdate-section a[onclick*="updateStockInfo"]');
                this.stockList = document.getElementById('stockList');
                this.lastHistoricalUpdate = document.getElementById('lastHistoricalUpdate');
                this.lastInfoUpdate = document.getElementById('lastInfoUpdate');
                this.historicalUpdateStatus = document.getElementById('historicalUpdateStatus');
                this.infoUpdateStatus = document.getElementById('infoUpdateStatus');
                this.notification = document.getElementById('notification');
                this.stockDetailsModal = document.getElementById('stockDetailsModal');

                // Log initialization status
                console.log('DataUpdateManager elements initialized:', {
                    mainContent: !!this.mainContent,
                    createWatchlistForm: !!this.createWatchlistForm,
                    watchlistsContainer: !!this.watchlistsContainer,
                    updateStockQuotesBtn: !!this.updateStockQuotesBtn,
                    updateHistoricalDataBtn: !!this.updateHistoricalDataBtn,
                    updateStockInfoBtn: !!this.updateStockInfoBtn,
                    stockList: !!this.stockList,
                    lastHistoricalUpdate: !!this.lastHistoricalUpdate,
                    lastInfoUpdate: !!this.lastInfoUpdate,
                    historicalUpdateStatus: !!this.historicalUpdateStatus,
                    infoUpdateStatus: !!this.infoUpdateStatus,
                    notification: !!this.notification,
                    stockDetailsModal: !!this.stockDetailsModal
                });

                // Only show warnings if we're on the watchlist page
                if (window.location.pathname.includes('/watchlist/')) {
                    if (!this.mainContent) {
                        console.warn('Main content container not found - this is expected if not on watchlist page');
                    }
                    if (!this.createWatchlistForm) {
                        console.warn('Create watchlist form not found - this is expected if not on watchlist page');
                    }
                    if (!this.watchlistsContainer) {
                        console.warn('Watchlists container not found - this is expected if not on watchlist page');
                    }
                }
            } catch (error) {
                console.error('Error in initializeElements:', error);
            }
        }

        initializeProperties() {
            console.log('Initializing DataUpdateManager properties');
            try {
                // DOM Elements
                this.stockSearch = document.getElementById('stockSearch');
                this.stockItems = document.querySelectorAll('.stock-item');
                this.selectedStocksList = document.getElementById('selectedStocksList');
                this.selectedCount = document.getElementById('selectedCount');
                this.stockListContainer = document.querySelector('.stock-list-container');
                this.noResults = document.getElementById('noResults');
                this.searchLoading = document.getElementById('searchLoading');
                this.addStockBtn = document.getElementById('addStock');
                this.watchlistDetailsContainer = document.getElementById('watchlistDetails');
                this.watchlistDetailsContent = document.getElementById('watchlistDetailsContent');
                this.watchlistDetailsName = document.getElementById('watchlistDetailsName');
                this.watchlistDetailsLoading = document.getElementById('watchlistDetailsLoading');
                this.createWatchlistFormContainer = document.getElementById('createWatchlistFormContainer');
                this.createWatchlistModal = document.getElementById('createWatchlistModal');
                this.showCreateWatchlistBtn = document.getElementById('showCreateWatchlistBtn');
                this.closeCreateWatchlistBtn = document.getElementById('closeCreateWatchlistBtn');
                this.cancelCreateWatchlistBtn = document.getElementById('cancelCreateWatchlistBtn');

                // Initialize Bootstrap modal if it exists
                if (this.createWatchlistModal) {
                    this.modal = new bootstrap.Modal(this.createWatchlistModal);
                }

                // State
                this.selectedStocks = new Set();
                this.currentWatchlistId = null;
                this.isFormVisible = false;
            } catch (error) {
                console.error('Error in initializeProperties:', error);
            }
        }

        initializeModalListener() {
            if (this.createWatchlistModal) {
                this.createWatchlistModal.addEventListener('shown.bs.modal', () => {
                    console.log('Create Watchlist modal shown, reinitializing search');
                    this.initializeProperties();
                });
            }
        }

        init() {
            console.log('DataUpdateManager.init() called');
            
            // Check if we're on the dataupdate page and show the section
            if (window.location.pathname.includes('/dataupdate/')) {
                console.log('On dataupdate page, showing dataupdate section');
                const dataupdateSection = document.querySelector('.dataupdate-section');
                if (dataupdateSection) {
                    dataupdateSection.style.display = 'block';
                    console.log('Data update section is now visible');
                } else {
                    console.error('dataupdate section not found in DOM');
                }
            }
            
            // Log DOM elements we need
            console.log('Checking required DOM elements:', {
                updateStockQuotes: !!this.updateStockQuotesBtn,
                updateHistoricalData: !!this.updateHistoricalDataBtn,
                updateStockInfo: !!this.updateStockInfoBtn,
                stockList: !!this.stockList,
                notification: !!this.notification,
                stockDetailsModal: !!this.stockDetailsModal
            });

            this.bindEvents();
            this.loadStocks();
        }

        bindEvents() {
            console.log('Binding DataUpdateManager events');
            
            if (this.updateStockQuotesBtn) {
                console.log('Binding click event to updateStockQuotes button');
                this.updateStockQuotesBtn.addEventListener('click', () => {
                    console.log('updateStockQuotes button clicked');
                    this.updateStockQuotes();
                });
            } else {
                console.error('updateStockQuotes button not found in DOM');
            }

            if (this.updateHistoricalDataBtn) {
                console.log('Binding click event to updateHistoricalData button');
                this.updateHistoricalDataBtn.addEventListener('click', () => {
                    console.log('updateHistoricalData button clicked');
                    this.updateHistoricalData();
                });
            } else {
                console.error('updateHistoricalData button not found in DOM');
            }

            if (this.updateStockInfoBtn) {
                console.log('Binding click event to updateStockInfo button');
                this.updateStockInfoBtn.addEventListener('click', () => {
                    console.log('updateStockInfo button clicked');
                    this.updateStockInfo();
                });
            } else {
                console.error('updateStockInfo button not found in DOM');
            }
        }

        setupStockSearch() {
            const searchInput = document.getElementById('stockSearch');
            const stockItems = document.querySelectorAll('.stock-item');
            const noResults = document.getElementById('noResults');
            const searchLoading = document.getElementById('searchLoading');
            let searchTimeout;

            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    const searchText = e.target.value.toLowerCase().trim();
                    
                    // Show loading indicator
                    if (searchLoading) searchLoading.style.display = 'block';
                    if (noResults) noResults.style.display = 'none';

                    // Clear previous timeout
                    clearTimeout(searchTimeout);

                    // Set new timeout to prevent too many updates
                    searchTimeout = setTimeout(() => {
                        let matchFound = false;

                        stockItems.forEach(item => {
                            const symbol = item.querySelector('.stock-symbol').textContent.toLowerCase();
                            const name = item.querySelector('.stock-name').textContent.toLowerCase();

                            if (searchText === '') {
                                item.style.display = 'none';
                            } else if (symbol.includes(searchText) || name.includes(searchText)) {
                                item.style.display = 'block';
                                matchFound = true;
                            } else {
                                item.style.display = 'none';
                            }
                        });

                        // Hide loading indicator
                        if (searchLoading) searchLoading.style.display = 'none';

                        // Show/hide no results message
                        if (noResults) {
                            noResults.style.display = searchText && !matchFound ? 'block' : 'none';
                        }
                    }, 300);
                });
            }
        }

        setupStockSelection() {
            const stockCheckboxes = document.querySelectorAll('.stock-checkbox');
            const selectedStocksList = document.getElementById('selectedStocksList');
            const selectedCount = document.getElementById('selectedCount');

            stockCheckboxes.forEach(checkbox => {
                checkbox.addEventListener('change', () => {
                    this.updateSelectedStocks();
                });
            });
        }

        updateSelectedStocks() {
            const selectedStocksList = document.getElementById('selectedStocksList');
            const selectedCount = document.getElementById('selectedCount');
            const checkedBoxes = document.querySelectorAll('.stock-checkbox:checked');

            if (selectedStocksList && selectedCount) {
                selectedCount.textContent = checkedBoxes.length;
                selectedStocksList.innerHTML = '';

                checkedBoxes.forEach(checkbox => {
                    const stockItem = checkbox.closest('.stock-item');
                    const symbol = stockItem.querySelector('strong').textContent.trim();

                    const stockTag = document.createElement('div');
                    stockTag.className = 'selected-stock-tag';
                    stockTag.innerHTML = `
                        ${symbol}
                        <button type="button" class="btn-remove-stock" onclick="window.dataUpdateManager.removeStock('${checkbox.id}')">
                            <i class="fas fa-times"></i>
                        </button>
                    `;
                    selectedStocksList.appendChild(stockTag);
                });
            }
        }

        removeStock(checkboxId) {
            const checkbox = document.getElementById(checkboxId);
            if (checkbox) {
                checkbox.checked = false;
                this.updateSelectedStocks();
            }
        }

        hideCreateWatchlistForm() {
            // Add any cleanup or reset logic here
            const form = document.getElementById('createWatchlistForm');
            if (form) {
                form.reset();
                this.updateSelectedStocks();
            }
            // Trigger the event to hide the form
            const event = new CustomEvent('hideWatchlistForm');
            document.dispatchEvent(event);
        }

        // Stock search and selection
        handleStockSearch() {
            try {
                const searchInput = document.getElementById('stockSearch');
                const stockItems = document.querySelectorAll('.stock-item');
                const noResults = document.getElementById('noResults');
                const addStockBtn = document.getElementById('addStock');
                
                if (!searchInput || !stockItems) return;
                
                const searchText = searchInput.value.toLowerCase().trim();
                let visibleCount = 0;

                stockItems.forEach(item => {
                    const stockNameEl = item.querySelector('.stock-name');
                    const stockSymbolEl = item.querySelector('.stock-symbol');
                    
                    if (!stockNameEl || !stockSymbolEl) return;
                    
                    const stockName = stockNameEl.textContent.toLowerCase();
                    const stockSymbol = stockSymbolEl.textContent.toLowerCase();
                    const isVisible = searchText === '' ? false : 
                                    stockName.includes(searchText) || 
                                    stockSymbol.includes(searchText);
                    
                    item.style.display = isVisible ? 'block' : 'none';
                    if (isVisible) visibleCount++;
                });

                // Update UI elements
                if (noResults) {
                    noResults.style.display = searchText && visibleCount === 0 ? 'block' : 'none';
                }
                if (addStockBtn) {
                    addStockBtn.disabled = visibleCount === 0;
                }
            } catch (error) {
                console.error('Error in handleStockSearch:', error);
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

        handleStockSelection() {
            const selectedCheckboxes = document.querySelectorAll('.stock-checkbox:checked');
            console.log('Selected checkboxes:', selectedCheckboxes.length);
            
            if (this.selectedCount) {
                this.selectedCount.textContent = selectedCheckboxes.length;
            }

            const selectedStocksList = document.getElementById('selectedStocksList');
            if (selectedStocksList) {
                selectedStocksList.innerHTML = '';
                selectedCheckboxes.forEach(checkbox => {
                    const stockItem = checkbox.closest('.stock-item');
                    const stockSymbol = stockItem.querySelector('strong').textContent.trim();
                    const stockId = checkbox.value;

                    selectedStocksList.innerHTML += `
                        <div class="selected-stock-tag" data-stock-id="${stockId}">
                            ${stockSymbol}
                            <button type="button" class="btn-remove-stock" onclick="dataUpdateManager.removeSelectedStock('${stockId}')">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    `;
                });
            }
        }

        removeSelectedStock(stockId) {
            const checkbox = document.querySelector(`.stock-checkbox[value="${stockId}"]`);
            if (checkbox) {
                checkbox.checked = false;
                this.handleStockSelection();
            }
        }

        // Watchlist creation
        initializeCreateWatchlistForm() {
            const form = document.getElementById('createWatchlistForm');
            if (form) {
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const formData = new FormData(form);
                    // Get all checked stock checkboxes
                    const selectedStocks = Array.from(document.querySelectorAll('.stock-checkbox:checked')).map(cb => cb.value);
                    
                    // Debug print
                    console.log('Selected stocks:', selectedStocks);
                    
                    // Clear any existing stocks field
                    formData.delete('stocks');
                    // Add each selected stock ID
                    selectedStocks.forEach(stockId => {
                        formData.append('stocks', stockId);
                    });

                    // Debug print form data
                    for (let pair of formData.entries()) {
                        console.log(pair[0] + ': ' + pair[1]);
                    }

                    try {
                        const response = await fetch(form.action, {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                                'X-Requested-With': 'XMLHttpRequest'
                            },
                            body: formData
                        });

                        const result = await response.json();
                        
                        if (result.success) {
                            // Show success message
                            this.showAlert('success', 'Watchlist created successfully!');
                            // Load the watchlist details in the main content area
                            const mainContent = document.getElementById('mainContent');
                            if (mainContent) {
                                mainContent.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
                                
                                // Fetch the watchlist details
                                const watchlistResponse = await fetch(result.redirect_url, {
                                    headers: {
                                        'X-Requested-With': 'XMLHttpRequest'
                                    }
                                });
                                
                                if (watchlistResponse.ok) {
                                    const html = await watchlistResponse.text();
                                    mainContent.innerHTML = html;
                                } else {
                                    mainContent.innerHTML = '<div class="alert alert-danger">Error loading watchlist details</div>';
                                }
                            }
                        } else {
                            this.showAlert('error', result.message || 'Failed to create watchlist');
                        }
                    } catch (error) {
                        console.error('Error creating watchlist:', error);
                        this.showAlert('error', 'An error occurred while creating the watchlist');
                    }
                });
            }
        }

        showAlert(type, message) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            const cardBody = document.querySelector('.card-body');
            if (cardBody) {
                cardBody.insertBefore(alertDiv, cardBody.firstChild);
                
                // Auto dismiss after 5 seconds
                setTimeout(() => {
                    alertDiv.remove();
                }, 5000);
            }
        }

        // Watchlist viewing and management
        async viewWatchlist(watchlistId) {
            console.log('Showing watchlist:', watchlistId);
            
            const detailsContainer = document.getElementById('watchlistDetails');
            const nameElement = document.getElementById('watchlistDetailsName');
            const contentElement = document.getElementById('watchlistDetailsContent');
            
            if (!detailsContainer || !nameElement || !contentElement) {
                console.warn('Required elements not found for showing watchlist');
                return;
            }
            
            detailsContainer.style.display = 'block';
            nameElement.textContent = 'Loading...';
            
            this.loadWatchlistDetails(watchlistId);
        }

        handleDirectUrlAccess() {
            // Check if we're on a watchlist detail page
            const path = window.location.pathname;
            const match = path.match(/\/watchlist\/(\d+)\//);
            if (match) {
                const watchlistId = match[1];
                console.log('Direct URL access detected for watchlist:', watchlistId);
                this.loadWatchlistDetails(watchlistId);
            }
        }

        async loadWatchlistDetails(watchlistId) {
            try {
                const response = await fetch(`/watchlist/${watchlistId}/`);
                if (!response.ok) {
                    throw new Error('Failed to fetch watchlist details');
                }
                const content = await response.text();
                
                // Update the dashboard content area
                const dashboardContent = document.querySelector('.dashboard-content');
                if (dashboardContent) {
                    // Create a temporary container to parse the HTML
                    const tempContainer = document.createElement('div');
                    tempContainer.innerHTML = content;
                    
                    // Find the mainContentWrapper div in the response
                    const mainContentWrapper = tempContainer.querySelector('#mainContentWrapper');
                    if (mainContentWrapper) {
                        // Find the card-body within mainContentWrapper
                        const cardBody = mainContentWrapper.querySelector('.card-body');
                        if (cardBody) {
                            // Update only the card-body content
                            const existingCardBody = dashboardContent.querySelector('.card-body');
                            if (existingCardBody) {
                                existingCardBody.innerHTML = cardBody.innerHTML;
                            }
                        }
                        // Update URL without page reload
                        window.history.pushState({}, '', `/watchlist/${watchlistId}/`);
                    } else {
                        console.error('Main content wrapper not found in response');
                    }
                } else {
                    console.error('Dashboard content area not found');
                }
            } catch (error) {
                console.error('Error loading watchlist details:', error);
                // Show error message to user
                alert('Failed to load watchlist details. Please try again.');
            }
        }

        renderWatchlistDetails(data) {
            this.watchlistDetailsName.textContent = data.name;
            
            let content = '';
            if (data.description) {
                content += `<p class="text-muted">${data.description}</p>`;
            }
            
            content += `
                <div class="row mt-4">
                    <div class="col-12">
                        <div class="table-responsive">
                            <table class="table table-dark table-hover">
                                <thead>
                                    <tr>
                                        <th>Symbol <i class="fas fa-tag ms-1"></i></th>
                                        <th>Price <i class="fas fa-dollar-sign ms-1"></i></th>
                                        <th>Change <i class="fas fa-chart-line ms-1"></i></th>
                                        <th>Volume <i class="fas fa-chart-bar ms-1"></i></th>
                                        <th>Actions <i class="fas fa-cog ms-1"></i></th>
                                    </tr>
                                </thead>
                                <tbody>
            `;
            
            if (data.stocks && data.stocks.length > 0) {
                data.stocks.forEach(stock => {
                    content += `
                        <tr>
                            <td>${stock.symbol}</td>
                            <td>$${stock.current_price || '0.00'}</td>
                            <td>
                                <span class="${stock.change >= 0 ? 'text-success' : 'text-danger'}">
                                    ${stock.change_percentage ? stock.change_percentage.toFixed(2) + '%' : '0.00%'}
                                </span>
                            </td>
                            <td>${stock.volume || '0'}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-light me-2" onclick="dataUpdateManager.viewStockDetails('${stock.symbol}')">
                                    <i class="fas fa-chart-line"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="dataUpdateManager.removeStockFromWatchlist(${this.currentWatchlistId}, '${stock.symbol}')">
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
        }

        // Add new methods for edit and delete functionality
        async editWatchlist(watchlistId) {
            try {
                // Fetch watchlist details
                const response = await fetch(`/dashboard/watchlist/${watchlistId}/edit/`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch watchlist details');
                }

                const html = await response.text();
                
                // Create and show the modal with matching styles
                const modalHtml = `
                    <div class="modal fade" id="editWatchlistModal" tabindex="-1" aria-labelledby="editWatchlistModalLabel" aria-hidden="true">
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content bg-dark text-light">
                                <div class="modal-header border-secondary">
                                    <h5 class="modal-title" id="editWatchlistModalLabel">
                                        <i class="fas fa-edit me-2"></i>Edit Watchlist
                                    </h5>
                                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="card bg-dark border-secondary">
                                        <div class="card-body">
                                            <div class="row">
                                                <div class="col-12">
                                                    <div class="d-flex justify-content-between align-items-center mb-4">
                                                        <h4 class="mb-0">
                                                            <i class="fas fa-star text-warning me-2"></i>
                                                            Edit Watchlist
                                                        </h4>
                                                    </div>
                                                    ${html}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-footer border-secondary">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                    <button type="button" class="btn btn-primary" onclick="dataUpdateManager.updateWatchlist(${watchlistId})">
                                        <i class="fas fa-save me-2"></i>Update Watchlist
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                // Remove existing modal if any
                const existingModal = document.getElementById('editWatchlistModal');
                if (existingModal) {
                    existingModal.remove();
                }

                // Add new modal to body
                document.body.insertAdjacentHTML('beforeend', modalHtml);

                // Initialize the modal
                const modal = new bootstrap.Modal(document.getElementById('editWatchlistModal'));
                modal.show();

                // Initialize stock search functionality for the edit modal
                const editModal = document.getElementById('editWatchlistModal');
                const searchInput = editModal.querySelector('#stockSearch');
                const stockItems = editModal.querySelectorAll('.stock-item');
                const noResults = editModal.querySelector('#noResults');
                const searchLoading = editModal.querySelector('#searchLoading');
                const selectedStocksList = editModal.querySelector('#selectedStocksList');
                const selectedCount = editModal.querySelector('#selectedCount');

                console.log('Edit Modal Elements:', {
                    searchInput: !!searchInput,
                    stockItems: stockItems.length,
                    noResults: !!noResults,
                    searchLoading: !!searchLoading,
                    selectedStocksList: !!selectedStocksList,
                    selectedCount: !!selectedCount
                });

                // Hide all stocks by default
                stockItems.forEach(item => {
                    item.style.display = 'none';
                });

                if (searchInput) {
                    let searchTimeout;
                    searchInput.addEventListener('input', (e) => {
                        const searchText = e.target.value.toLowerCase().trim();
                        console.log('Search Text:', searchText);
                        
                        // Show loading indicator
                        if (searchLoading) searchLoading.style.display = 'block';
                        if (noResults) noResults.style.display = 'none';

                        // Clear previous timeout
                        clearTimeout(searchTimeout);

                        // Set new timeout to prevent too many updates
                        searchTimeout = setTimeout(() => {
                            let matchFound = false;
                            console.log('Processing search with timeout');

                            // Hide all items if search text is less than 3 characters
                            if (searchText.length < 3) {
                                stockItems.forEach(item => {
                                    item.style.display = 'none';
                                });
                                if (searchLoading) searchLoading.style.display = 'none';
                                if (noResults) noResults.style.display = 'none';
                                return;
                            }

                            stockItems.forEach((item, index) => {
                                // Get the stock name and symbol from the label text
                                const label = item.querySelector('.form-check-label');
                                if (!label) {
                                    console.log(`Stock ${index + 1} missing label element`);
                                    return;
                                }

                                const labelText = label.textContent.toLowerCase();
                                console.log(`Stock ${index + 1} label text:`, labelText);
                                
                                if (labelText.includes(searchText)) {
                                    item.style.display = 'block';
                                    matchFound = true;
                                    console.log(`Stock ${index + 1} shown (matched search)`);
                                } else {
                                    item.style.display = 'none';
                                    console.log(`Stock ${index + 1} hidden (no match)`);
                                }
                            });

                            // Hide loading indicator
                            if (searchLoading) searchLoading.style.display = 'none';

                            // Show/hide no results message
                            if (noResults) {
                                const shouldShowNoResults = searchText.length >= 3 && !matchFound;
                                noResults.style.display = shouldShowNoResults ? 'block' : 'none';
                                console.log('No Results Display:', shouldShowNoResults);
                            }

                            console.log('Search Complete:', {
                                matchFound,
                                searchText,
                                visibleItems: Array.from(stockItems).filter(item => item.style.display !== 'none').length
                            });
                        }, 300);
                    });
                } else {
                    console.error('Search input element not found in edit modal');
                }

                // Initialize stock selection functionality
                const stockCheckboxes = editModal.querySelectorAll('.stock-checkbox');

                // Set initial checked state based on existing selected stocks
                stockCheckboxes.forEach(checkbox => {
                    const stockId = checkbox.value;
                    const existingStock = selectedStocksList.querySelector(`.selected-stock-tag[data-stock-id="${stockId}"]`);
                    if (existingStock) {
                        checkbox.checked = true;
                    }
                });

                // Update selected count initially
                if (selectedCount) {
                    const checkedBoxes = editModal.querySelectorAll('.stock-checkbox:checked');
                    selectedCount.textContent = checkedBoxes.length;
                }

                stockCheckboxes.forEach(checkbox => {
                    checkbox.addEventListener('change', () => {
                        const checkedBoxes = editModal.querySelectorAll('.stock-checkbox:checked');
                        if (selectedCount) {
                            selectedCount.textContent = checkedBoxes.length;
                        }
                        if (selectedStocksList) {
                            if (checkbox.checked) {
                                // Only add the new stock if it's checked and not already in the list
                                const stockId = checkbox.value;
                                const existingTag = selectedStocksList.querySelector(`.selected-stock-tag[data-stock-id="${stockId}"]`);
                                if (!existingTag) {
                                    const stockItem = checkbox.closest('.stock-item');
                                    const stockSymbol = stockItem.querySelector('strong').textContent.trim();
                                    const stockTag = `
                                        <div class="selected-stock-tag" data-stock-id="${stockId}">
                                            ${stockSymbol}
                                            <button type="button" class="btn-remove-stock" onclick="dataUpdateManager.removeSelectedStock('${stockId}')">
                                                <i class="fas fa-times"></i>
                                            </button>
                                        </div>
                                    `;
                                    selectedStocksList.insertAdjacentHTML('beforeend', stockTag);
                                }
                            } else {
                                // Remove the stock tag if unchecked
                                const stockId = checkbox.value;
                                const stockTag = selectedStocksList.querySelector(`.selected-stock-tag[data-stock-id="${stockId}"]`);
                                if (stockTag) {
                                    stockTag.remove();
                                }
                            }
                        }
                    });
                });

                // Initialize remove stock functionality
                const removeStockButtons = editModal.querySelectorAll('.btn-remove-stock');
                removeStockButtons.forEach(button => {
                    button.addEventListener('click', (e) => {
                        e.preventDefault();
                        const stockId = button.closest('.selected-stock-tag').dataset.stockId;
                        const checkbox = editModal.querySelector(`.stock-checkbox[value="${stockId}"]`);
                        if (checkbox) {
                            checkbox.checked = false;
                            const event = new Event('change');
                            checkbox.dispatchEvent(event);
                        }
                    });
                });

                // Add custom styles to match watchlist details
                const style = document.createElement('style');
                style.textContent = `
                    .modal-content {
                        background-color: #1a1a1a !important;
                        border-color: #2d2d2d !important;
                    }
                    .modal-header {
                        border-bottom-color: #2d2d2d !important;
                    }
                    .modal-footer {
                        border-top-color: #2d2d2d !important;
                    }
                    .card {
                        background-color: #1a1a1a !important;
                        border-color: #2d2d2d !important;
                    }
                    .card-body {
                        padding: 1.5rem;
                    }
                    .form-control, .form-select {
                        background-color: #2d2d2d !important;
                        border-color: #3d3d3d !important;
                        color: #ffffff !important;
                        padding: 0.75rem 1rem;
                    }
                    .form-control:focus, .form-select:focus {
                        background-color: #2d2d2d !important;
                        border-color: #0d6efd !important;
                        color: #ffffff !important;
                        box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
                    }
                    .form-label {
                        color: #ffffff !important;
                        font-weight: 500;
                        margin-bottom: 0.5rem;
                    }
                    .stock-list-container {
                        background-color: #2d2d2d !important;
                        border: 1px solid #3d3d3d !important;
                        border-radius: 0.375rem;
                        max-height: 300px;
                        overflow-y: auto;
                    }
                    .stock-item {
                        border-bottom: 1px solid #3d3d3d !important;
                        padding: 0.75rem 1rem;
                    }
                    .stock-item:last-child {
                        border-bottom: none !important;
                    }
                    .stock-item:hover {
                        background-color: #363636 !important;
                    }
                    .selected-stock-tag {
                        background-color: #2d2d2d !important;
                        border: 1px solid #3d3d3d !important;
                        color: #ffffff !important;
                        padding: 0.25rem 0.5rem !important;
                        margin: 0.25rem;
                        border-radius: 0.25rem;
                        display: inline-flex;
                        align-items: center;
                        gap: 0.25rem;
                        font-size: 0.875rem;
                    }
                    .stock-info {
                        font-weight: 500;
                    }
                    .btn-remove-stock {
                        color: #dc3545 !important;
                        padding: 0 0.25rem !important;
                        border: none;
                        background: none;
                        cursor: pointer;
                        display: inline-flex;
                        align-items: center;
                    }
                    .btn-remove-stock:hover {
                        color: #ff6b6b !important;
                    }
                    .stock-symbol {
                        font-weight: 600;
                        color: #ffffff;
                    }
                    .stock-name {
                        color: #adb5bd;
                        font-size: 0.875rem;
                    }
                    .form-check {
                        margin: 0;
                    }
                    .form-check-input {
                        background-color: #3d3d3d !important;
                        border-color: #4d4d4d !important;
                    }
                    .form-check-input:checked {
                        background-color: #0d6efd !important;
                        border-color: #0d6efd !important;
                    }
                    .form-check-label {
                        color: #ffffff !important;
                        margin-left: 0.5rem;
                    }
                    .btn-primary {
                        background-color: #0d6efd !important;
                        border-color: #0d6efd !important;
                    }
                    .btn-primary:hover {
                        background-color: #0b5ed7 !important;
                        border-color: #0a58ca !important;
                    }
                    .btn-secondary {
                        background-color: #6c757d !important;
                        border-color: #6c757d !important;
                    }
                    .btn-secondary:hover {
                        background-color: #5c636a !important;
                        border-color: #565e64 !important;
                    }
                `;
                document.head.appendChild(style);
            } catch (error) {
                console.error('Error loading edit form:', error);
                this.showAlert('error', 'Failed to load edit form');
            }
        }

        async updateWatchlist(watchlistId) {
            const form = document.getElementById('editWatchlistForm');
            if (!form) {
                this.showAlert('error', 'Edit form not found');
                return;
            }

            const formData = new FormData(form);
            
            // Get all checked stock checkboxes
            const selectedStocks = Array.from(document.querySelectorAll('.stock-checkbox:checked')).map(cb => cb.value);
            formData.delete('stocks'); // Remove the original stocks field
            selectedStocks.forEach(stockId => formData.append('stocks', stockId));

            try {
                const response = await fetch(`/dashboard/watchlist/${watchlistId}/edit/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                const result = await response.json();
                
                if (result.success) {
                    // Show success message
                    this.showAlert('success', 'Watchlist updated successfully!');
                    
                    // Close the modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editWatchlistModal'));
                    if (modal) {
                        modal.hide();
                    }
                    
                    // Reload the page to show updated data
                    window.location.reload();
                } else {
                    this.showAlert('error', result.message || 'Failed to update watchlist');
                }
            } catch (error) {
                console.error('Error updating watchlist:', error);
                this.showAlert('error', 'An error occurred while updating the watchlist');
            }
        }

        async deleteWatchlist(watchlistId) {
            if (!confirm('Are you sure you want to delete this watchlist? This action cannot be undone.')) {
                return;
            }

            try {
                const response = await fetch(`/dashboard/watchlist/${watchlistId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                const result = await response.json();
                
                if (result.success) {
                    // Show success message
                    this.showAlert('success', 'Watchlist deleted successfully!');
                    
                    // Remove the watchlist from the UI
                    const watchlistElement = document.querySelector(`[data-watchlist-id="${watchlistId}"]`);
                    if (watchlistElement) {
                        watchlistElement.remove();
                    }
                    
                    // If we're on the watchlist detail page, redirect to the list
                    if (window.location.pathname.includes(`/watchlist/${watchlistId}/`)) {
                        window.location.href = '/dashboard/watchlist/';
                    }
                } else {
                    this.showAlert('error', result.message || 'Failed to delete watchlist');
                }
            } catch (error) {
                console.error('Error deleting watchlist:', error);
                this.showAlert('error', 'An error occurred while deleting the watchlist');
            }
        }

        // Form management
        showCreateWatchlistForm() {
            AppManager.loadContent('/watchlist/create/');
        }

        resetForm() {
            if (this.createWatchlistForm) {
                this.createWatchlistForm.reset();
                if (this.selectedStocksList) {
                    this.selectedStocksList.innerHTML = '';
                }
                if (this.selectedCount) {
                    this.selectedCount.textContent = '0';
                }
                this.selectedStocks.clear();
            }
        }

        // Stock management
        viewStockDetails(symbol) {
            // Format the symbol for TradingView (add NSE suffix for Indian stocks)
            const tradingViewSymbol = `NSE:${symbol}`;
            
            // Open TradingView chart in a new tab
            window.open(`https://www.tradingview.com/chart/?symbol=${tradingViewSymbol}`, '_blank');
        }

        async removeStockFromWatchlist(watchlistId, symbol) {
            if (!confirm(`Are you sure you want to remove ${symbol} from this watchlist?`)) {
                return;
            }

            try {
                const response = await fetch(`/dashboard/watchlist/${watchlistId}/remove-stock/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ symbol: symbol })
                });

                const result = await response.json();
                
                if (result.success) {
                    // Show success message
                    this.showAlert('success', `${symbol} removed from watchlist successfully!`);
                    
                    // Remove the stock row from the table
                    const stockRow = document.querySelector(`tr[data-stock-symbol="${symbol}"]`);
                    if (stockRow) {
                        stockRow.remove();
                    }
                    
                    // Update the empty state if no stocks remain
                    const tbody = document.querySelector('.table tbody');
                    if (tbody && tbody.children.length === 0) {
                        tbody.innerHTML = `
                            <tr>
                                <td colspan="5" class="text-center py-4">
                                    <div class="text-muted">
                                        <i class="fas fa-inbox fa-2x mb-2"></i>
                                        <p class="mb-0">No stocks in this watchlist yet.</p>
                                    </div>
                                </td>
                            </tr>
                        `;
                    }
                } else {
                    this.showAlert('error', result.message || 'Failed to remove stock from watchlist');
                }
            } catch (error) {
                console.error('Error removing stock from watchlist:', error);
                this.showAlert('error', 'An error occurred while removing the stock');
            }
        }

        setupWatchlistClickHandlers() {
            const watchlistLinks = document.querySelectorAll('.watchlist-link');
            watchlistLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const watchlistId = link.dataset.watchlistId;
                    if (watchlistId) {
                        this.loadWatchlistDetails(watchlistId);
                    }
                });
            });
        }

        loadStocks() {
            console.log('Loading all stocks');
            
            // Show loading indicator
            this.stockList.innerHTML = `
                <div class="text-center text-muted p-4">
                    <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                    <p>Loading stocks...</p>
                </div>
            `;
            
            // Update the status badge
            const statusBadge = document.getElementById('historicalUpdateStatus');
            if (statusBadge) {
                statusBadge.textContent = 'Loading...';
                statusBadge.className = 'badge bg-info rounded-pill';
            }
            
            // Fetch the watchlist_detail_content.html template
            fetch('/dataupdate/watchlist_detail_content.html', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(html => {
                console.log('Watchlist detail content loaded');
                
                // Update the last update time
                const lastUpdateSpan = document.getElementById('lastHistoricalUpdate');
                if (lastUpdateSpan) {
                    lastUpdateSpan.textContent = new Date().toLocaleString();
                }
                
                // Update the status badge
                if (statusBadge) {
                    statusBadge.textContent = 'Loaded';
                    statusBadge.className = 'badge bg-success rounded-pill';
                }
                
                // Update the stock list with the template content
                this.stockList.innerHTML = html;
            })
            .catch(error => {
                console.error('Error loading watchlist detail content:', error);
                
                // Show error message
                this.stockList.innerHTML = `
                    <div class="alert alert-danger m-3" role="alert">
                        <i class="fas fa-exclamation-circle me-2"></i>Error loading stocks: ${error.message}
                    </div>
                `;
                
                // Update the status badge
                if (statusBadge) {
                    statusBadge.textContent = 'Error';
                    statusBadge.className = 'badge bg-danger rounded-pill';
                }
            });
        }
        
        renderStocks(stocks) {
            if (!stocks || stocks.length === 0) {
                this.stockList.innerHTML = `
                    <div class="text-center text-muted p-4">
                        <i class="fas fa-inbox fa-2x mb-3"></i>
                        <p>No stocks found.</p>
                    </div>
                `;
                return;
            }
            
            // Create a table to display the stocks
            let html = `
                <div class="table-responsive">
                    <table class="table table-dark table-hover">
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Name</th>
                                <th class="text-end">Price</th>
                                <th class="text-end">Change</th>
                                <th class="text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            // Add each stock to the table
            stocks.forEach(stock => {
                const changeClass = stock.change > 0 ? 'text-success' : stock.change < 0 ? 'text-danger' : '';
                html += `
                    <tr>
                        <td><strong>${stock.symbol}</strong></td>
                        <td>${stock.name}</td>
                        <td class="text-end">$${parseFloat(stock.price).toFixed(2)}</td>
                        <td class="text-end ${changeClass}">
                            ${parseFloat(stock.change).toFixed(2)} (${parseFloat(stock.change_percentage).toFixed(2)}%)
                        </td>
                        <td class="text-center">
                            <div class="btn-group">
                                <button class="btn btn-sm btn-outline-info" onclick="window.dataUpdateManager.viewStockDetails('${stock.symbol}')" title="View Details">
                                    <i class="fas fa-chart-line"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-primary" onclick="window.dataUpdateManager.updateStockData('${stock.symbol}')" title="Update Data">
                                    <i class="fas fa-sync"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });
            
            // Close the table
            html += `
                        </tbody>
                    </table>
                </div>
            `;
            
            // Update the stock list
            this.stockList.innerHTML = html;
        }
        
        viewStockDetails(symbol) {
            console.log('Viewing details for stock:', symbol);
            // Implement stock details view logic here
            this.showNotification('info', `Viewing details for ${symbol}`);
        }
        
        updateStockData(symbol) {
            console.log('Updating data for stock:', symbol);
            // Implement stock data update logic here
            this.showNotification('info', `Updating data for ${symbol}`);
        }

        updateStockQuotes() {
            this.showNotification('Updating stock quotes...', 'info');
            fetch('/dashboard/dataupdate/api/update-stock-quotes/', { 
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.showNotification(data.message, 'success');
                        this.loadStocks();
                    } else {
                        this.showNotification(data.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error updating stock quotes:', error);
                    this.showNotification('Error updating stock quotes', 'error');
                });
        }

        updateHistoricalData() {
            this.showNotification('Updating historical data...', 'info');
            this.historicalUpdateStatus.textContent = 'Updating...';
            this.historicalUpdateStatus.className = 'badge bg-warning rounded-pill';
            
            fetch('/dashboard/dataupdate/api/update-historical-data/', { 
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.showNotification(data.message, 'success');
                        this.historicalUpdateStatus.textContent = 'Updated';
                        this.historicalUpdateStatus.className = 'badge bg-success rounded-pill';
                        this.lastHistoricalUpdate.textContent = this.formatDate(new Date());
                        this.loadStocks();
                    } else {
                        this.showNotification(data.message, 'error');
                        this.historicalUpdateStatus.textContent = 'Failed';
                        this.historicalUpdateStatus.className = 'badge bg-danger rounded-pill';
                    }
                })
                .catch(error => {
                    console.error('Error updating historical data:', error);
                    this.showNotification('Error updating historical data', 'error');
                    this.historicalUpdateStatus.textContent = 'Failed';
                    this.historicalUpdateStatus.className = 'badge bg-danger rounded-pill';
                });
        }

        updateStockInfo() {
            this.showNotification('Updating stock information...', 'info');
            this.infoUpdateStatus.textContent = 'Updating...';
            this.infoUpdateStatus.className = 'badge bg-warning rounded-pill';
            
            fetch('/dashboard/dataupdate/api/update-stock-info/', { 
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.showNotification(data.message, 'success');
                        this.infoUpdateStatus.textContent = 'Updated';
                        this.infoUpdateStatus.className = 'badge bg-success rounded-pill';
                        this.lastInfoUpdate.textContent = this.formatDate(new Date());
                        this.loadStocks();
                    } else {
                        this.showNotification(data.message, 'error');
                        this.infoUpdateStatus.textContent = 'Failed';
                        this.infoUpdateStatus.className = 'badge bg-danger rounded-pill';
                    }
                })
                .catch(error => {
                    console.error('Error updating stock information:', error);
                    this.showNotification('Error updating stock information', 'error');
                    this.infoUpdateStatus.textContent = 'Failed';
                    this.infoUpdateStatus.className = 'badge bg-danger rounded-pill';
                });
        }

        fetchStockDetails(symbol) {
            fetch(`/dashboard/dataupdate/api/get-stock-data/?symbol=${symbol}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.showStockDetails(data.stock);
                    } else {
                        this.showNotification(data.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error fetching stock details:', error);
                    this.showNotification('Error fetching stock details', 'error');
                });
        }

        deleteStock(symbol) {
            if (confirm(`Are you sure you want to delete ${symbol}?`)) {
                fetch('/dashboard/dataupdate/api/delete-stock/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                    body: JSON.stringify({ symbol: symbol })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.showNotification(data.message, 'success');
                        this.loadStocks();
                    } else {
                        this.showNotification(data.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error deleting stock:', error);
                    this.showNotification('Error deleting stock', 'error');
                });
            }
        }

        showStockDetails(stock) {
            if (!this.stockDetailsModal) {
                console.error('Stock details modal not found');
                return;
            }
            
            const content = document.getElementById('stockDetailsContent');
            if (!content) {
                console.error('Stock details content element not found');
                return;
            }
            
            content.innerHTML = `
                <div class="mb-4">
                    <h4>${stock.name} (${stock.symbol})</h4>
                    <div class="text-muted">${stock.sector} | ${stock.industry}</div>
                </div>
                
                <div class="mb-4">
                    <h5>Current Data</h5>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="data-card">
                                <div class="data-label">Price</div>
                                <div class="data-value">₹${stock.current_price.toFixed(2)}</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="data-card">
                                <div class="data-label">Change</div>
                                <div class="data-value ${stock.price_change >= 0 ? 'text-success' : 'text-danger'}">
                                    ${stock.price_change >= 0 ? '+' : ''}${stock.price_change.toFixed(2)}
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="data-card">
                                <div class="data-label">Change %</div>
                                <div class="data-value ${stock.price_change_percent >= 0 ? 'text-success' : 'text-danger'}">
                                    ${stock.price_change_percent >= 0 ? '+' : ''}${stock.price_change_percent.toFixed(2)}%
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="data-card">
                                <div class="data-label">Volume</div>
                                <div class="data-value">${this.formatNumber(stock.volume)}</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mb-4">
                    <h5>Description</h5>
                    <p>${stock.description || 'No description available.'}</p>
                </div>
                
                <div>
                    <h5>Last Updated</h5>
                    <p>${this.formatDate(stock.last_updated)}</p>
                </div>
            `;
            
            const bsModal = new bootstrap.Modal(this.stockDetailsModal);
            bsModal.show();
        }

        showNotification(message, type = 'info') {
            console.log('DataUpdateManager.showNotification() called:', {
                message: message,
                type: type
            });
            
            if (!this.notification) {
                console.error('notification element not found in DOM');
                return;
            }

            this.notification.textContent = message;
            this.notification.className = `notification ${type}`;
            this.notification.style.display = 'block';
            
            console.log('Notification shown, will hide in 3 seconds');
            setTimeout(() => {
                this.notification.style.display = 'none';
                console.log('Notification hidden');
            }, 3000);
        }

        formatDate(dateString) {
            console.log('DataUpdateManager.formatDate() called with:', dateString);
            if (!dateString) {
                console.log('No date string provided, returning "Never"');
                return 'Never';
            }
            const date = new Date(dateString);
            const formatted = date.toLocaleString();
            console.log('Formatted date:', formatted);
            return formatted;
        }

        formatNumber(number) {
            console.log('DataUpdateManager.formatNumber() called with:', number);
            const formatted = new Intl.NumberFormat().format(number);
            console.log('Formatted number:', formatted);
            return formatted;
        }

        initialize() {
            this.setupEventListeners();
            this.setupWatchlistClickHandlers();
        }
    }

    // Initialize DataUpdateManager only once
    (function() {
        console.log('Initializing DataUpdateManager');
        if (!window.dataUpdateManager) {
            window.dataUpdateManager = new DataUpdateManager();
        }
    })();
}

console.log('dataupdate.js loaded'); 