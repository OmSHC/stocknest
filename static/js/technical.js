// technical.js - Handles technical analysis functionality

// Initialize technical analysis module
document.addEventListener('DOMContentLoaded', function() {
    // Initialize technical analysis components
    initializeTechnicalAnalysis();
    
    // Initialize screener if on screener page
    if (document.getElementById('screener-container')) {
        initializeScreener();
    }
});

function initializeTechnicalAnalysis() {
    // Add event listeners for technical analysis menu items
    setupTechnicalMenu();
    
    // Initialize technical indicators
    initializeIndicators();
}

function initializeScreener() {
    // Add event listeners for screener functionality
    setupScreenerForm();
    
    // Load saved screeners if any
    loadSavedScreeners();
}

function setupTechnicalMenu() {
    // Get all technical menu items
    const technicalMenuItems = document.querySelectorAll('.technical-menu-item');
    
    technicalMenuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const indicatorType = this.getAttribute('data-indicator');
            loadTechnicalIndicator(indicatorType);
        });
    });
}

function loadTechnicalIndicator(indicatorType) {
    // Clear previous indicator content
    const indicatorContainer = document.getElementById('technical-indicator-container');
    indicatorContainer.innerHTML = '';
    
    // Show loading state
    indicatorContainer.innerHTML = '<div class="loading">Loading indicator...</div>';
    
    // Fetch data and render indicator based on type
    switch(indicatorType) {
        case 'moving-average':
            loadMovingAverage();
            break;
        case 'rsi':
            loadRSI();
            break;
        case 'macd':
            loadMACD();
            break;
        case 'bollinger-bands':
            loadBollingerBands();
            break;
        default:
            console.error('Unknown indicator type:', indicatorType);
    }
}

function loadMovingAverage() {
    // Implementation for Moving Average indicator
    const container = document.getElementById('technical-indicator-container');
    
    // Create form for MA parameters
    const form = document.createElement('form');
    form.className = 'ma-parameters';
    form.innerHTML = `
        <div class="form-group">
            <label for="ma-period">Period:</label>
            <input type="number" id="ma-period" value="20" min="1" max="200">
        </div>
        <div class="form-group">
            <label for="ma-type">Type:</label>
            <select id="ma-type">
                <option value="sma">Simple MA</option>
                <option value="ema">Exponential MA</option>
            </select>
        </div>
        <button type="submit">Apply</button>
    `;
    
    container.innerHTML = '';
    container.appendChild(form);
    
    // Add event listener for form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const period = document.getElementById('ma-period').value;
        const type = document.getElementById('ma-type').value;
        calculateMovingAverage(period, type);
    });
}

function loadRSI() {
    // Implementation for RSI indicator
    const container = document.getElementById('technical-indicator-container');
    
    // Create form for RSI parameters
    const form = document.createElement('form');
    form.className = 'rsi-parameters';
    form.innerHTML = `
        <div class="form-group">
            <label for="rsi-period">Period:</label>
            <input type="number" id="rsi-period" value="14" min="1" max="100">
        </div>
        <button type="submit">Apply</button>
    `;
    
    container.innerHTML = '';
    container.appendChild(form);
    
    // Add event listener for form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const period = document.getElementById('rsi-period').value;
        calculateRSI(period);
    });
}

function loadMACD() {
    // Implementation for MACD indicator
    const container = document.getElementById('technical-indicator-container');
    
    // Create form for MACD parameters
    const form = document.createElement('form');
    form.className = 'macd-parameters';
    form.innerHTML = `
        <div class="form-group">
            <label for="macd-fast">Fast Period:</label>
            <input type="number" id="macd-fast" value="12" min="1" max="100">
        </div>
        <div class="form-group">
            <label for="macd-slow">Slow Period:</label>
            <input type="number" id="macd-slow" value="26" min="1" max="100">
        </div>
        <div class="form-group">
            <label for="macd-signal">Signal Period:</label>
            <input type="number" id="macd-signal" value="9" min="1" max="100">
        </div>
        <button type="submit">Apply</button>
    `;
    
    container.innerHTML = '';
    container.appendChild(form);
    
    // Add event listener for form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const fast = document.getElementById('macd-fast').value;
        const slow = document.getElementById('macd-slow').value;
        const signal = document.getElementById('macd-signal').value;
        calculateMACD(fast, slow, signal);
    });
}

function loadBollingerBands() {
    // Implementation for Bollinger Bands indicator
    const container = document.getElementById('technical-indicator-container');
    
    // Create form for Bollinger Bands parameters
    const form = document.createElement('form');
    form.className = 'bb-parameters';
    form.innerHTML = `
        <div class="form-group">
            <label for="bb-period">Period:</label>
            <input type="number" id="bb-period" value="20" min="1" max="100">
        </div>
        <div class="form-group">
            <label for="bb-deviations">Standard Deviations:</label>
            <input type="number" id="bb-deviations" value="2" min="0.1" max="5" step="0.1">
        </div>
        <button type="submit">Apply</button>
    `;
    
    container.innerHTML = '';
    container.appendChild(form);
    
    // Add event listener for form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const period = document.getElementById('bb-period').value;
        const deviations = document.getElementById('bb-deviations').value;
        calculateBollingerBands(period, deviations);
    });
}

// Technical indicator calculation functions
function calculateMovingAverage(period, type) {
    // Implementation for calculating moving average
    console.log(`Calculating ${type} Moving Average with period ${period}`);
    // Add your moving average calculation logic here
}

function calculateRSI(period) {
    // Implementation for calculating RSI
    console.log(`Calculating RSI with period ${period}`);
    // Add your RSI calculation logic here
}

function calculateMACD(fast, slow, signal) {
    // Implementation for calculating MACD
    console.log(`Calculating MACD with fast=${fast}, slow=${slow}, signal=${signal}`);
    // Add your MACD calculation logic here
}

function calculateBollingerBands(period, deviations) {
    // Implementation for calculating Bollinger Bands
    console.log(`Calculating Bollinger Bands with period=${period}, deviations=${deviations}`);
    // Add your Bollinger Bands calculation logic here
}

function setupScreenerForm() {
    const form = document.getElementById('screener-form');
    if (!form) return;
    
    // Add condition button
    const addConditionBtn = document.getElementById('add-condition');
    if (addConditionBtn) {
        addConditionBtn.addEventListener('click', addCondition);
    }
    
    // Remove condition buttons
    document.querySelectorAll('.remove-condition').forEach(btn => {
        btn.addEventListener('click', removeCondition);
    });
    
    // Form submission
    form.addEventListener('submit', handleScreenerSubmit);
}

function addCondition() {
    const conditionsContainer = document.getElementById('conditions-container');
    const conditionTemplate = document.getElementById('condition-template');
    if (!conditionsContainer || !conditionTemplate) return;
    const newCondition = conditionTemplate.content.cloneNode(true);
    conditionsContainer.appendChild(newCondition);
    const condElem = conditionsContainer.lastElementChild;
    // Initialize expression builder
    const exprBuilder = condElem.querySelector('.expression-builder');
    const exprInput = condElem.querySelector('.expression-json');
    initializeExpressionBuilder(exprBuilder, exprInput);
    // Remove button
    const removeBtn = condElem.querySelector('.remove-condition');
    if (removeBtn) removeBtn.addEventListener('click', removeCondition);
    // Add-row button
    const addRowBtn = condElem.querySelector('.add-row-btn');
    if (addRowBtn) addRowBtn.addEventListener('click', addCondition);
}

function removeCondition(event) {
    const conditionElement = event.target.closest('.condition');
    if (conditionElement) {
        conditionElement.remove();
    }
}

function handleScreenerSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    // Collect conditions
    const conditions = [];
    document.querySelectorAll('.condition').forEach(condition => {
        const timeframe = condition.querySelector('.timeframe').value;
        const operator = condition.querySelector('.operator').value;
        const value = condition.querySelector('.value').value;
        const exprJson = condition.querySelector('.expression-json').value;
        if (exprJson && operator && value) {
            conditions.push({
                timeframe,
                operator,
                value: parseFloat(value),
                expression: JSON.parse(exprJson)
            });
        }
    });
    // Prepare data for API
    const data = {
        name: formData.get('name'),
        description: formData.get('description'),
        visibility: formData.get('visibility'),
        conditions
    };
    // Send to API
    fetch('/dashboard/technical/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = `/dashboard/technical/${data.screener.id}/`;
        } else {
            alert(data.message || 'Error creating screener');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error creating screener');
    });
}

function loadSavedScreeners() {
    // Implementation for loading saved screeners
    // This will be called when the page loads to display existing screeners
}

function runScreener(screenerId) {
    // Show loading state
    const resultsContainer = document.getElementById('screener-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = '<div class="loading">Running screener...</div>';
    }
    
    // Call API to run screener
    fetch(`/dashboard/technical/${screenerId}/run/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayScreenerResults(data.results);
            } else {
                alert(data.message || 'Error running screener');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error running screener');
        });
}

function displayScreenerResults(results) {
    const resultsContainer = document.getElementById('screener-results');
    if (!resultsContainer) return;
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="no-results">No stocks match the criteria</div>';
        return;
    }
    
    // Create table
    const table = document.createElement('table');
    table.className = 'table table-striped table-hover';
    
    // Create header
    const thead = document.createElement('thead');
    thead.innerHTML = `
        <tr>
            <th>Symbol</th>
            <th>Name</th>
            <th>Sector</th>
            <th>Open</th>
            <th>High</th>
            <th>Low</th>
            <th>Close</th>
            <th>Volume</th>
            <th>Date</th>
        </tr>
    `;
    
    // Create body
    const tbody = document.createElement('tbody');
    results.forEach(result => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${result.symbol}</td>
            <td>${result.name}</td>
            <td>${result.sector}</td>
            <td>${result.open}</td>
            <td>${result.high}</td>
            <td>${result.low}</td>
            <td>${result.close}</td>
            <td>${result.volume}</td>
            <td>${result.date}</td>
        `;
        tbody.appendChild(tr);
    });
    
    // Assemble table
    table.appendChild(thead);
    table.appendChild(tbody);
    
    // Clear and update container
    resultsContainer.innerHTML = '';
    resultsContainer.appendChild(table);
}

// Helper function to get CSRF token
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

// Export functions for use in other modules
window.technicalAnalysis = {
    initializeTechnicalAnalysis,
    initializeScreener,
    addCondition,
    removeCondition,
    runScreener
};

// --- Expression Builder ---
const MENU_OPTIONS = [
    { category: 'Math Functions', options: [
        { label: 'Max', type: 'func', args: 1 },
        { label: 'Min', type: 'func', args: 1 },
        { label: 'Abs', type: 'func', args: 1 },
    ]},
    { category: 'Comparators', options: [
        { label: '>', type: 'comparator', args: 2 },
        { label: '<', type: 'comparator', args: 2 },
        { label: '>=', type: 'comparator', args: 2 },
        { label: '<=', type: 'comparator', args: 2 },
        { label: '=', type: 'comparator', args: 2 },
    ]},
    { category: 'Operator', options: [
        { label: '+', type: 'operator', args: 2 },
        { label: '-', type: 'operator', args: 2 },
        { label: '*', type: 'operator', args: 2 },
        { label: '/', type: 'operator', args: 2 },
    ]},
    { category: 'Attributes', options: [
        { label: 'High', type: 'var' },
        { label: 'Low', type: 'var' },
        { label: 'Close', type: 'var' },
        { label: 'Open', type: 'var' },
        { label: 'Volume', type: 'var' },
        { label: 'Number', type: 'number' },
    ]},
];

function initializeExpressionBuilder(container, hiddenInput) {
    container.innerHTML = '';
    buildExprNode(container, null, hiddenInput);
}

function buildExprNode(parent, expr, hiddenInput) {
    // expr: {type, label, args: [expr,...]} or null
    if (!expr) {
        // Show plus button
        const plus = document.createElement('button');
        plus.type = 'button';
        plus.className = 'expr-plus-btn';
        plus.textContent = '+';
        plus.onclick = function(e) {
            e.stopPropagation();
            showExprMenu(plus, (option) => {
                parent.removeChild(plus);
                const node = createExprNode(option, hiddenInput);
                parent.appendChild(node);
                // Always add another plus after
                buildExprNode(parent, null, hiddenInput);
                updateHiddenExpr(parent, hiddenInput);
            });
        };
        parent.appendChild(plus);
    } else {
        // Render expr node (not used in this version)
    }
}

function createExprNode(option, hiddenInput) {
    const node = document.createElement('span');
    node.className = 'expr-node';
    node.style.display = 'inline-flex';
    node.style.alignItems = 'center';
    node.style.marginRight = '6px';
    node.style.background = '#f3eaff';
    node.style.borderRadius = '16px';
    node.style.padding = '2px 8px';
    node.style.fontWeight = '600';
    node.style.color = '#6c47ff';
    // Remove/edit icon
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.textContent = '×';
    removeBtn.className = 'expr-remove-btn';
    removeBtn.style.marginLeft = '4px';
    removeBtn.style.background = 'none';
    removeBtn.style.border = 'none';
    removeBtn.style.color = '#b800b8';
    removeBtn.style.fontWeight = 'bold';
    removeBtn.onclick = function(e) {
        e.stopPropagation();
        node.remove();
        updateHiddenExpr(node.parentNode, hiddenInput);
    };
    if (option.type === 'number') {
        const input = document.createElement('input');
        input.type = 'number';
        input.value = '';
        input.placeholder = 'Number';
        input.className = 'expr-number-input';
        input.style.width = '70px';
        input.style.margin = '0 4px';
        input.style.border = '1px solid #d0d3e0';
        input.style.borderRadius = '8px';
        input.style.fontWeight = '600';
        input.style.fontSize = '1em';
        input.style.background = '#fff';
        input.style.color = '#3a3a6a';
        input.oninput = function() {
            node.numberValue = input.value;
            updateHiddenExpr(node.parentNode, hiddenInput);
        };
        node.appendChild(input);
        node.getExpr = function() {
            return { type: 'number', value: input.value };
        };
    } else {
        // Label
        const label = document.createElement('span');
        label.textContent = option.label;
        node.appendChild(label);
        // If function, add args as plus buttons with brackets
        if (option.type === 'func') {
            node.appendChild(document.createTextNode('('));
            for (let i = 0; i < option.args; i++) {
                const argSpan = document.createElement('span');
                argSpan.className = 'expr-arg';
                argSpan.style.margin = '0 2px';
                buildExprNode(argSpan, null, hiddenInput); // Always just a plus button
                node.appendChild(argSpan);
                if (i < option.args - 1) node.appendChild(document.createTextNode(', '));
            }
            node.appendChild(document.createTextNode(')'));
        }
        // If operator or comparator, add args as plus buttons without brackets
        else if (option.type === 'operator' || option.type === 'comparator') {
            for (let i = 0; i < option.args; i++) {
                const argSpan = document.createElement('span');
                argSpan.className = 'expr-arg';
                argSpan.style.margin = '0 2px';
                buildExprNode(argSpan, null, hiddenInput); // Always just a plus button
                node.appendChild(argSpan);
                if (i < option.args - 1) node.appendChild(document.createTextNode(' ' + option.label + ' '));
            }
        }
        node.getExpr = function() {
            if (option.type === 'var') return { type: 'var', label: option.label };
            if (option.type === 'func' || option.type === 'operator' || option.type === 'comparator') {
                const args = Array.from(node.querySelectorAll(':scope > .expr-arg')).map(arg => {
                    const plus = arg.querySelector('.expr-plus-btn');
                    if (plus) return null;
                    const child = arg.querySelector('.expr-node');
                    return child && child.getExpr ? child.getExpr() : null;
                });
                return { type: option.type, label: option.label, args };
            }
        };
    }
    node.appendChild(removeBtn);
    node.option = option;
    return node;
}

function showExprMenu(anchor, onSelect) {
    // Remove any existing menu
    document.querySelectorAll('.expr-menu').forEach(m => m.remove());
    const menu = document.createElement('div');
    menu.className = 'expr-menu';
    menu.style.position = 'absolute';
    menu.style.zIndex = 1000;
    menu.style.background = '#fff';
    menu.style.border = '1px solid #e0e3ea';
    menu.style.borderRadius = '10px';
    menu.style.boxShadow = '0 4px 16px rgba(80,80,120,0.10)';
    menu.style.padding = '8px 0';
    menu.style.minWidth = '220px';
    menu.style.maxHeight = '320px';
    menu.style.overflowY = 'auto';
    // Tabs
    const tabBar = document.createElement('div');
    tabBar.style.display = 'flex';
    tabBar.style.gap = '8px';
    tabBar.style.padding = '0 12px 8px 12px';
    let activeTab = 0;
    MENU_OPTIONS.forEach((cat, i) => {
        const tab = document.createElement('button');
        tab.textContent = cat.category;
        tab.className = 'expr-menu-tab';
        tab.style.background = i === 0 ? '#6c47ff' : '#f8f9fb';
        tab.style.color = i === 0 ? '#fff' : '#6c47ff';
        tab.style.border = 'none';
        tab.style.borderRadius = '12px';
        tab.style.padding = '2px 12px';
        tab.style.fontWeight = '600';
        tab.onclick = () => {
            activeTab = i;
            renderOptions();
            tabBar.querySelectorAll('button').forEach((b, j) => {
                b.style.background = j === i ? '#6c47ff' : '#f8f9fb';
                b.style.color = j === i ? '#fff' : '#6c47ff';
            });
        };
        tabBar.appendChild(tab);
    });
    menu.appendChild(tabBar);
    // Options
    const optionsDiv = document.createElement('div');
    menu.appendChild(optionsDiv);
    function renderOptions() {
        optionsDiv.innerHTML = '';
        MENU_OPTIONS[activeTab].options.forEach(opt => {
            const optBtn = document.createElement('div');
            optBtn.textContent = opt.label;
            optBtn.className = 'expr-menu-option';
            optBtn.style.padding = '6px 18px';
            optBtn.style.cursor = 'pointer';
            optBtn.style.fontWeight = '500';
            optBtn.onmouseenter = () => optBtn.style.background = '#f3eaff';
            optBtn.onmouseleave = () => optBtn.style.background = '';
            optBtn.onclick = () => {
                menu.remove();
                onSelect(opt);
            };
            optionsDiv.appendChild(optBtn);
        });
    }
    renderOptions();
    document.body.appendChild(menu);
    // Position
    const rect = anchor.getBoundingClientRect();
    menu.style.left = (rect.left + window.scrollX) + 'px';
    menu.style.top = (rect.bottom + window.scrollY + 2) + 'px';
    // Remove on click outside
    setTimeout(() => {
        document.addEventListener('mousedown', function handler(e) {
            if (!menu.contains(e.target)) {
                menu.remove();
                document.removeEventListener('mousedown', handler);
            }
        });
    }, 10);
}

function updateHiddenExpr(container, hiddenInput) {
    // Find the first expr-node in container
    const node = container.querySelector(':scope > .expr-node');
    if (node && node.getExpr) {
        hiddenInput.value = JSON.stringify(node.getExpr());
    } else {
        hiddenInput.value = '';
    }
} 