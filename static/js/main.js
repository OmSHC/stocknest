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
    document.querySelectorAll('a[href*="create_watchlist"]').forEach(link => {
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

    // Handle refresh button clicks
    document.addEventListener('click', function(e) {
        const refreshButton = e.target.closest('.btn-refresh');
        if (refreshButton) {
            e.preventDefault();
            
            // Get the current page URL without any parameters
            const currentPath = window.location.pathname;
            
            // If we're on the create watchlist page, don't refresh
            if (currentPath.includes('create_watchlist')) {
                return;
            }
            
            // Otherwise refresh the current page content
            fetch(currentPath, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                document.getElementById('mainContentWrapper').innerHTML = html;
            })
            .catch(error => {
                console.error('Error refreshing content:', error);
            });
        }
    });
}); 