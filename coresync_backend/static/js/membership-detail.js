// ====================================================
// CORESYNC MEMBERSHIP DETAIL
// Extends DashboardAPI for consistency
// ====================================================

/**
 * Membership Detail class - extends DashboardAPI
 */
class MembershipDetail extends DashboardAPI {
    constructor() {
        super();
        this.membership = null;
        this.stats = null;
        this.init();
    }

    /**
     * Initialize membership detail page
     */
    async init() {
        await this.loadMembershipData();
        await this.loadUsageStats();
    }

    /**
     * Load membership data
     */
    async loadMembershipData() {
        try {
            const data = await this.request('/api/memberships/my-membership/');
            this.membership = data;
            this.renderMembershipInfo(data);
            this.renderBenefits(data.benefits || this.getDefaultBenefits(data.plan_name));
            this.renderUpgradeOptions(data.upgrade_options || []);
        } catch (error) {
            console.error('Error loading membership:', error);
            this.showError('Failed to load membership data');
        }
    }

    /**
     * Load usage statistics
     */
    async loadUsageStats() {
        try {
            // Try to get stats from service history
            const history = await this.request('/api/services/history/');
            const bookings = history.results || history;

            // Calculate stats from bookings
            const thisMonth = new Date();
            const monthStart = new Date(thisMonth.getFullYear(), thisMonth.getMonth(), 1);

            const monthBookings = bookings.filter(b => new Date(b.booking_date) >= monthStart);

            const stats = {
                services_this_month: monthBookings.length,
                visits_this_month: monthBookings.length,
                total_savings: monthBookings.reduce((sum, b) => {
                    const saved = (b.non_member_price || 0) - (b.final_total || 0);
                    return sum + Math.max(0, saved);
                }, 0)
            };

            this.stats = stats;
            this.renderStats(stats);
        } catch (error) {
            console.error('Error loading stats:', error);
            // Show default stats
            this.renderStats({
                services_this_month: 0,
                visits_this_month: 0,
                total_savings: 0
            });
        }
    }

    /**
     * Render membership info
     * @param {Object} data - Membership data
     */
    renderMembershipInfo(data) {
        const titleEl = document.getElementById('membership-plan-name');
        const statusEl = document.getElementById('membership-status');

        if (titleEl) titleEl.textContent = data.plan_name || 'No Active Membership';
        if (statusEl) {
            statusEl.textContent = data.is_active ? 'Active' : 'Inactive';
            statusEl.style.color = data.is_active ? '#10B981' : '#EF4444';
        }
    }

    /**
     * Render usage statistics
     * @param {Object} stats - Usage stats
     */
    renderStats(stats) {
        const servicesEl = document.getElementById('services-used');
        const savingsEl = document.getElementById('total-savings');
        const visitsEl = document.getElementById('visit-count');

        if (servicesEl) servicesEl.textContent = stats.services_this_month || 0;
        if (savingsEl) savingsEl.textContent = `$${(stats.total_savings || 0).toFixed(0)}`;
        if (visitsEl) visitsEl.textContent = stats.visits_this_month || 0;
    }

    /**
     * Get default benefits based on plan
     * @param {string} planName - Plan name
     * @returns {Array}
     */
    getDefaultBenefits(planName) {
        const benefits = {
            'Mensuite': [
                { icon: '🧖‍♂️', name: 'Men\'s Spa Access', description: 'Full access to Mensuite facilities' },
                { icon: '💆', name: 'Massage Services', description: '30% discount on all massages' },
                { icon: '🛁', name: 'Sauna & Steam', description: 'Unlimited sauna access' },
                { icon: '📅', name: 'Priority Booking', description: 'Book up to 30 days in advance' },
            ],
            'CoreSync Private': [
                { icon: '💑', name: 'Couple\'s Spa Access', description: 'Private rooms for two' },
                { icon: '🌹', name: 'Romantic Packages', description: '30% discount on couple\'s services' },
                { icon: '🍾', name: 'Complimentary Refreshments', description: 'Wine and refreshments included' },
                { icon: '📅', name: 'Priority Booking', description: 'Book up to 30 days in advance' },
            ],
            'Unlimited': [
                { icon: '♾️', name: 'Unlimited Access', description: 'All services included' },
                { icon: '🏠', name: 'IoT Control', description: 'Full control of room environment' },
                { icon: '🎁', name: 'Concierge Service', description: 'Personal concierge requests' },
                { icon: '🛍️', name: 'Shop Discounts', description: 'Exclusive member pricing on all products' },
                { icon: '⭐', name: 'VIP Treatment', description: 'Priority access to all amenities' },
            ]
        };

        return benefits[planName] || [];
    }

    /**
     * Render benefits list
     * @param {Array} benefits - Benefits array
     */
    renderBenefits(benefits) {
        const container = document.getElementById('benefits-list');
        if (!container) return;

        if (benefits.length === 0) {
            container.innerHTML = '<p style="color: rgba(255,255,255,0.5); text-align: center;">No benefits data available.</p>';
            return;
        }

        container.innerHTML = `
            <div style="display: grid; gap: 1rem;">
                ${benefits.map(benefit => `
                    <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
                        <span style="font-size: 1.5rem;">${benefit.icon || '✓'}</span>
                        <div>
                            <div style="font-weight: 600;">${benefit.name}</div>
                            <div style="font-size: 0.875rem; color: rgba(255,255,255,0.7);">${benefit.description}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * Render upgrade options
     * @param {Array} options - Upgrade options
     */
    renderUpgradeOptions(options) {
        const container = document.getElementById('upgrade-options');
        if (!container) return;

        if (options.length === 0) {
            container.innerHTML = '<p style="color: rgba(255,255,255,0.6); text-align: center;">You have the highest tier membership!</p>';
            return;
        }

        container.innerHTML = options.map(option => `
            <div style="background: rgba(255,255,255,0.05); padding: 2rem; border-radius: 8px; margin-bottom: 1rem;">
                <h3>${option.name}</h3>
                <p style="color: rgba(255,255,255,0.7); margin: 1rem 0;">${option.description}</p>
                <div style="font-size: 2rem; color: #B8860B; margin: 1rem 0;">
                    $${parseFloat(option.price).toFixed(0)}/month
                </div>
                <button class="btn-primary" onclick="membershipDetail.upgrade('${option.id}')">
                    Upgrade Now
                </button>
            </div>
        `).join('');
    }

    /**
     * Upgrade membership
     * @param {string} planId - Plan ID
     */
    async upgrade(planId) {
        if (!confirm('Are you sure you want to upgrade your membership?')) return;

        try {
            await this.request('/api/memberships/upgrade/', {
                method: 'POST',
                body: JSON.stringify({ plan_id: planId })
            });
            this.showToast('Upgrade successful! Your new benefits are now active.', 'success');
            setTimeout(() => location.reload(), 2000);
        } catch (error) {
            console.error('Upgrade error:', error);
            this.showToast('Upgrade failed. Please contact support.', 'error');
        }
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        console.error(message);
        this.showToast(message, 'error');
    }

    /**
     * Show toast notification
     * @param {string} message - Message to show
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

// Add animation keyframes
if (!document.getElementById('membership-animations')) {
    const style = document.createElement('style');
    style.id = 'membership-animations';
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

