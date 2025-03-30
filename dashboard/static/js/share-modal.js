// Share modal functionality
function initializeShareModal() {
    const shareModal = document.getElementById('shareModal');
    const shareButtons = document.querySelectorAll('[data-share]');
    
    if (!shareModal || !shareButtons.length) {
        return; // Exit if elements don't exist
    }

    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const shareType = this.getAttribute('data-share');
            // Handle share functionality
            console.log('Sharing:', shareType);
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeShareModal);

// Also try to initialize immediately in case DOM is already loaded
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    initializeShareModal();
} 