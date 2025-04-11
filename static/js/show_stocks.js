// Show Stocks functionality
console.log('show_stocks.js is being loaded');

// Function to load and display all stocks
function loadAllStocks() {
    console.log('Loading all stocks');
    
    // Get the stock list element
    const stockList = document.getElementById('stockList');
    if (!stockList) {
        console.error('Stock list element not found');
        return;
    }
    
    // Show loading indicator
    stockList.innerHTML = `
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
        stockList.innerHTML = html;
    })
    .catch(error => {
        console.error('Error loading watchlist detail content:', error);
        
        // Show error message
        stockList.innerHTML = `
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

// Add event listener to the Show Stocks link
document.addEventListener('DOMContentLoaded', function() {
    const showStocksLink = document.querySelector('a[onclick*="loadStocks"]');
    if (showStocksLink) {
        showStocksLink.onclick = function(e) {
            e.preventDefault();
            loadAllStocks();
        };
    }
}); 