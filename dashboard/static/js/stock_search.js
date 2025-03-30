// Stock search functionality
console.log('Stock search script starting to load...');

// Global variables
let selectedStocks = new Set();
let searchTimeout = null;

// Define searchStocks function and make it globally available immediately
function searchStocks(query) {
    console.log('searchStocks function called with query:', query);
    
    // Clear previous timeout if exists
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }

    // Set new timeout to prevent too many API calls
    searchTimeout = setTimeout(() => {
        console.log('Executing search with query:', query);
        const searchResults = document.getElementById('stockSearchResults');
        const searchLoading = document.getElementById('searchLoading');
        const noResults = document.getElementById('noResults');

        if (!searchResults || !searchLoading || !noResults) {
            console.error('Required elements not found:', {
                searchResults: !!searchResults,
                searchLoading: !!searchLoading,
                noResults: !!noResults
            });
            return;
        }

        if (query.length < 3) {
            searchResults.innerHTML = '';
            searchLoading.style.display = 'none';
            noResults.style.display = 'none';
            return;
        }

        // Show loading spinner
        searchLoading.style.display = 'block';
        noResults.style.display = 'none';
        searchResults.innerHTML = '';

        // Make API request
        const url = `/dashboard/api/search-stocks/?q=${encodeURIComponent(query)}`;
        console.log('Making API request to:', url);
        
        fetch(url)
            .then(response => {
                console.log('API response status:', response.status);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Received data:', data);
                if (!data.results || data.results.length === 0) {
                    noResults.style.display = 'block';
                    return;
                }

                data.results.forEach(stock => {
                    const div = document.createElement('div');
                    div.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center bg-dark text-light';
                    div.innerHTML = `
                        <div>
                            <strong>${stock.symbol}</strong> - ${stock.name}
                        </div>
                        <div class="form-check">
                            <input class="form-check-input stock-checkbox" type="checkbox" value="${stock.symbol}" id="stock-${stock.symbol}">
                        </div>
                    `;

                    div.onclick = function(e) {
                        if (e.target !== this.querySelector('.stock-checkbox')) {
                            const checkbox = this.querySelector('.stock-checkbox');
                            checkbox.checked = !checkbox.checked;
                            handleStockSelection(stock);
                        }
                    };

                    searchResults.appendChild(div);
                });
            })
            .catch(error => {
                console.error('Error:', error);
                searchResults.innerHTML = 
                    '<div class="alert alert-danger">Error searching stocks</div>';
            })
            .finally(() => {
                searchLoading.style.display = 'none';
            });
    }, 300); // 300ms delay to prevent too many API calls
}

// Function to handle stock selection
function handleStockSelection(stock) {
    if (selectedStocks.has(stock.symbol)) {
        selectedStocks.delete(stock.symbol);
    } else {
        selectedStocks.add(stock.symbol);
    }
    updateSelectedCount();
    updateSelectedStocksList();
}

// Function to update selected count
function updateSelectedCount() {
    const countElement = document.getElementById('selectedCount');
    if (countElement) {
        countElement.textContent = selectedStocks.size;
    }
}

// Function to update selected stocks list
function updateSelectedStocksList() {
    const selectedStocksList = document.getElementById('selectedStocksList');
    const selectedStocksInput = document.getElementById('selectedStocksInput');
    
    if (!selectedStocksList || !selectedStocksInput) {
        console.error('Required elements not found for updating selected stocks');
        return;
    }
    
    selectedStocksList.innerHTML = '';
    selectedStocks.forEach(symbol => {
        const stockTag = document.createElement('div');
        stockTag.className = 'badge bg-primary d-flex align-items-center gap-2';
        stockTag.innerHTML = `
            ${symbol}
            <button type="button" class="btn-close btn-close-white" onclick="removeStock('${symbol}')"></button>
        `;
        selectedStocksList.appendChild(stockTag);
    });

    selectedStocksInput.value = Array.from(selectedStocks).join(',');
}

// Function to remove a stock
function removeStock(symbol) {
    selectedStocks.delete(symbol);
    updateSelectedCount();
    updateSelectedStocksList();
}

// Make functions globally available
window.searchStocks = searchStocks;
window.handleStockSelection = handleStockSelection;
window.removeStock = removeStock;

// Function to load all stocks
function loadAllStocks() {
    console.log('Loading all stocks...');
    searchStocks(''); // Empty query to get all stocks
}

// Initialize when DOM is loaded
function initializeStockSearch() {
    console.log('Initializing stock search...');
    const stockSearch = document.getElementById('stockSearch');
    if (stockSearch) {
        console.log('Stock search input found, adding event listener');
        // Add input event listener
        stockSearch.addEventListener('input', function(e) {
            console.log('Input event triggered with value:', e.target.value);
            searchStocks(e.target.value);
        });
        
        // Load all stocks initially
        loadAllStocks();
    } else {
        console.error('Stock search input not found');
    }
}

// Initialize immediately
console.log('Initializing stock search immediately');
initializeStockSearch();

// Log when script finishes loading
console.log('Stock search script finished loading'); 