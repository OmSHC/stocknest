class ShareModalManager {
    constructor() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }

    initialize() {
        try {
            // Get modal elements
            this.modal = document.getElementById('shareModal');
            this.shareButton = document.getElementById('shareButton');
            this.copyButton = document.getElementById('copyShareLink');
            this.shareLink = document.getElementById('shareLink');

            // Log initialization status
            console.log('ShareModalManager elements found:', {
                modal: !!this.modal,
                shareButton: !!this.shareButton,
                copyButton: !!this.copyButton,
                shareLink: !!this.shareLink
            });

            // Only bind events if elements exist
            if (this.modal && this.shareButton) {
                this.bindEvents();
            }
        } catch (error) {
            console.error('Error initializing ShareModalManager:', error);
        }
    }

    bindEvents() {
        try {
            // Share button click
            if (this.shareButton) {
                this.shareButton.addEventListener('click', () => this.showModal());
            }

            // Copy button click
            if (this.copyButton) {
                this.copyButton.addEventListener('click', () => this.copyShareLink());
            }

            // Close button click
            const closeButtons = this.modal.querySelectorAll('[data-bs-dismiss="modal"]');
            closeButtons.forEach(button => {
                button.addEventListener('click', () => this.hideModal());
            });
        } catch (error) {
            console.error('Error binding ShareModalManager events:', error);
        }
    }

    showModal() {
        try {
            if (this.modal) {
                const modalInstance = new bootstrap.Modal(this.modal);
                modalInstance.show();
            }
        } catch (error) {
            console.error('Error showing share modal:', error);
        }
    }

    hideModal() {
        try {
            if (this.modal) {
                const modalInstance = bootstrap.Modal.getInstance(this.modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        } catch (error) {
            console.error('Error hiding share modal:', error);
        }
    }

    copyShareLink() {
        try {
            if (this.shareLink) {
                this.shareLink.select();
                document.execCommand('copy');
                
                // Show success message
                const tooltip = bootstrap.Tooltip.getInstance(this.copyButton);
                if (tooltip) {
                    this.copyButton.setAttribute('data-bs-original-title', 'Copied!');
                    tooltip.show();
                    
                    setTimeout(() => {
                        this.copyButton.setAttribute('data-bs-original-title', 'Copy to clipboard');
                        tooltip.hide();
                    }, 2000);
                }
            }
        } catch (error) {
            console.error('Error copying share link:', error);
        }
    }
}

// Initialize the share modal manager
window.shareModalManager = new ShareModalManager(); 