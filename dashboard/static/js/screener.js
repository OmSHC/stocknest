// screener.js

if (typeof ScreenerManager === 'undefined') {
    class ScreenerManager {
        constructor() {
            this.init();
        }

        init() {
            // Attach event to button
            const btn = document.getElementById('saveScreenerBtn');
            if (btn) {
                btn.addEventListener('click', () => this.submitCreateScreener());
            }
        }

        async submitCreateScreener() {
            const name = document.getElementById('screenerName').value;
            const description = document.getElementById('screenerDescription').value;
            const visibility = document.getElementById('screenerVisibility').value;
            const conditions = getConditionsFromUI();

            if (!name) {
                this.showAlert('error', 'Screener name is required.');
                return;
            }
            if (!conditions.length) {
                this.showAlert('error', 'At least one condition is required.');
                return;
            }

            const payload = { name, description, visibility, conditions };

            try {
                const response = await fetch('/dashboard/technical/api/create/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();
                if (data.success) {
                    this.showAlert('success', 'Screener saved successfully!');
                    // Optionally redirect or update UI
                } else {
                    this.showAlert('error', data.message || data.error || 'Failed to save screener');
                }
            } catch (error) {
                this.showAlert('error', 'Error saving screener: ' + error);
            }
        }

        showAlert(type, message) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            const container = document.querySelector('.modal-body') || document.body;
            container.insertBefore(alertDiv, container.firstChild);
            setTimeout(() => alertDiv.remove(), 5000);
        }
    }

    // Initialize ScreenerManager only once
    document.addEventListener('DOMContentLoaded', function() {
        if (!window.screenerManager) {
            window.screenerManager = new ScreenerManager();
        }
    });
}

// Helper to get CSRF token (Django requirement)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Example stub for getting conditions from UI
function getConditionsFromUI() {
    // TODO: Implement this to collect conditions from your UI
    // Example static data:
    return [
        {
            condition: {
                indicator: "RSI",
                operator: ">",
                value: 70
            },
            order: 0
        },
        {
            condition: {
                indicator: "MACD",
                operator: "<",
                value: 0
            },
            order: 1
        }
    ];
}

// Example: Attach to a button in your HTML
// <button id="saveScreenerBtn" onclick="saveScreener()">Save Screener</button> 