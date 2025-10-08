// ====================================================
// CORESYNC CONCIERGE
// Extends DashboardAPI for consistency
// ====================================================

/**
 * Concierge API - extends base DashboardAPI class
 * Uses existing patterns from dashboard.js
 */
class CoreSyncConciergeAPI extends DashboardAPI {
    constructor() {
        super();
    }

    /**
     * Submit new concierge request
     * @param {Object} requestData - Request details
     * @returns {Promise<Object>}
     */
    async submitRequest(requestData) {
        return this.request('/api/concierge/requests/', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }

    /**
     * Get user's requests
     * @returns {Promise<Array>}
     */
    async getMyRequests() {
        return this.request('/api/concierge/requests/');
    }

    /**
     * Get requests grouped by status
     * @returns {Promise<Object>}
     */
    async getMyRequestsGrouped() {
        return this.request('/api/concierge/requests/my_requests/');
    }

    /**
     * Cancel request
     * @param {number} requestId - Request ID
     * @returns {Promise<Object>}
     */
    async cancelRequest(requestId) {
        return this.request(`/api/concierge/requests/${requestId}/cancel_request/`, {
            method: 'POST'
        });
    }
}

/**
 * Main Concierge class
 */
class CoreSyncConcierge {
    constructor() {
        this.api = new CoreSyncConciergeAPI();
        this.init();
    }

    /**
     * Initialize concierge
     */
    async init() {
        this.setupForm();
        this.setMinPickupDate();
        await this.loadMyRequests();
    }

    /**
     * Setup form submission
     */
    setupForm() {
        const form = document.getElementById('concierge-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.submitRequest();
        });
    }

    /**
     * Set minimum pickup date (3 days from now)
     */
    setMinPickupDate() {
        const dateInput = document.getElementById('pickup_date');
        if (dateInput) {
            const minDate = new Date();
            minDate.setDate(minDate.getDate() + 3);
            dateInput.min = minDate.toISOString().split('T')[0];
        }
    }

    /**
     * Submit concierge request
     */
    async submitRequest() {
        const budgetMin = parseFloat(document.getElementById('budget_min').value);
        const budgetMax = parseFloat(document.getElementById('budget_max').value);

        // Validate budget
        if (budgetMin > budgetMax) {
            this.showToast('Maximum budget must be greater than minimum', 'error');
            return;
        }

        const requestData = {
            request_type: document.getElementById('request_type').value,
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            product_link: document.getElementById('product_link').value,
            budget_min: budgetMin,
            budget_max: budgetMax,
            preferred_pickup_date: document.getElementById('pickup_date').value,
        };

        try {
            const submitBtn = document.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';

            await this.api.submitRequest(requestData);
            this.showToast('Request submitted successfully!', 'success');
            document.getElementById('concierge-form').reset();

            // Reload requests list
            await this.loadMyRequests();

            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Request';
        } catch (error) {
            console.error('Error:', error);
            this.showToast(error.message || 'Failed to submit request', 'error');

            const submitBtn = document.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Request';
        }
    }

    /**
     * Load user's requests
     */
    async loadMyRequests() {
        try {
            const requests = await this.api.getMyRequests();
            this.renderRequests(requests.results || requests);
        } catch (error) {
            console.error('Error loading requests:', error);
        }
    }

    /**
     * Render requests list
     * @param {Array} requests - Array of requests
     */
    renderRequests(requests) {
        const container = document.getElementById('requests-list');
        if (!container) return;

        if (requests.length === 0) {
            container.innerHTML = '<p style="color: rgba(255,255,255,0.5); text-align: center; padding: 2rem;">No requests yet.</p>';
            return;
        }

        container.innerHTML = requests.map(req => `
            <div class="request-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div style="flex: 1;">
                        <h3 style="margin-bottom: 0.5rem;">${req.title}</h3>
                        <p style="color: rgba(255,255,255,0.7); font-size: 0.875rem;">${req.request_type_display}</p>
                    </div>
                    <span class="status-badge status-${req.status}">${req.status_display}</span>
                </div>
                <div style="color: rgba(255,255,255,0.8); font-size: 0.875rem;">
                    <p style="margin-bottom: 0.5rem;">Budget: $${parseFloat(req.budget_min).toFixed(2)} - $${parseFloat(req.budget_max).toFixed(2)}</p>
                    ${req.actual_cost > 0 ? `
                        <p style="margin-bottom: 0.5rem;">Actual Cost: $${parseFloat(req.actual_cost).toFixed(2)}</p>
                    ` : ''}
                    <p style="margin-bottom: 0.5rem;">Pickup: ${new Date(req.preferred_pickup_date).toLocaleDateString()}</p>
                    <p>Submitted: ${new Date(req.submitted_at).toLocaleDateString()}</p>
                </div>
                ${req.can_cancel ? `
                    <button 
                        onclick="concierge.cancelRequest(${req.id})" 
                        class="btn-secondary btn-small"
                        style="margin-top: 1rem;"
                    >
                        Cancel Request
                    </button>
                ` : ''}
            </div>
        `).join('');
    }

    /**
     * Cancel request
     * @param {number} id - Request ID
     */
    async cancelRequest(id) {
        if (!confirm('Are you sure you want to cancel this request?')) return;

        try {
            await this.api.cancelRequest(id);
            this.showToast('Request cancelled', 'success');
            await this.loadMyRequests();
        } catch (error) {
            console.error('Error:', error);
            this.showToast('Failed to cancel request', 'error');
        }
    }

    /**
     * Show toast notification - PROFESSIONAL UX (not alert!)
     * @param {string} message - Notification message
     * @param {string} type - Type: success, error, info
     */
    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container') || this.createToastContainer();

        const toast = document.createElement('div');
        toast.style.cssText = `
            background: ${type === 'success' ? '#10B981' : type === 'error' ? '#EF4444' : '#3B82F6'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            animation: slideInRight 0.3s ease;
        `;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Create toast container
     * @returns {HTMLElement}
     */
    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        document.body.appendChild(container);
        return container;
    }
}

// Add animation keyframes if not already added
if (!document.getElementById('concierge-animations')) {
    const style = document.createElement('style');
    style.id = 'concierge-animations';
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes fadeOut {
            from {
                opacity: 1;
            }
            to {
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

