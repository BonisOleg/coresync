// ====================================================
// CORESYNC SERVICE DETAIL
// Extends DashboardAPI for consistency
// ====================================================

/**
 * Service Detail class - extends DashboardAPI
 */
class ServiceDetail extends DashboardAPI {
    constructor(serviceSlug) {
        super();
        this.serviceSlug = serviceSlug;
        this.service = null;
        this.addons = [];
        this.selectedAddons = [];
        this.init();
    }

    /**
     * Initialize service detail page
     */
    async init() {
        await this.loadServiceDetails();
        await this.loadAddons();
        this.setupBookingButton();
        this.setupAddonSelection();
    }

    /**
     * Load service details
     */
    async loadServiceDetails() {
        try {
            const service = await this.request(`/api/services/${this.serviceSlug}/`);
            this.service = service;
            this.renderPricing(service);
        } catch (error) {
            console.error('Error loading service:', error);
            this.showToast('Failed to load service details', 'error');
        }
    }

    /**
     * Load available add-ons for this service
     */
    async loadAddons() {
        try {
            // Try to get add-ons from service data first
            if (this.service && this.service.available_addons) {
                this.addons = this.service.available_addons;
                this.renderAddons(this.addons);
                return;
            }

            // Fallback: load from API
            const response = await this.request(`/api/services/addons/?service=${this.serviceSlug}`);
            this.addons = response.results || response;
            this.renderAddons(this.addons);
        } catch (error) {
            console.error('Error loading addons:', error);
            // Don't show error - add-ons are optional
        }
    }

    /**
     * Render pricing tiers
     * @param {Object} service - Service data
     */
    renderPricing(service) {
        const container = document.getElementById('pricing-tiers');
        if (!container) return;

        const hasUnlimited = service.category === 'unlimited';

        container.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem;">
                <!-- Non-Member Price -->
                <div style="background: rgba(255,255,255,0.05); padding: 2rem; border-radius: 8px; text-align: center;">
                    <h3 style="margin-bottom: 1rem; color: rgba(255,255,255,0.7);">Non-Member</h3>
                    <div style="font-size: 3rem; font-weight: bold; color: #fff; margin-bottom: 0.5rem;">
                        $${parseFloat(service.non_member_price || service.price || 0).toFixed(0)}
                    </div>
                    <p style="color: rgba(255,255,255,0.6); font-size: 0.875rem;">per visit</p>
                </div>
                
                <!-- Member Price -->
                <div style="background: linear-gradient(135deg, rgba(184,134,11,0.2), rgba(184,134,11,0.1)); padding: 2rem; border-radius: 8px; text-align: center; border: 2px solid #B8860B;">
                    <h3 style="margin-bottom: 1rem; color: #B8860B; font-weight: bold;">Member Price</h3>
                    <div style="font-size: 3rem; font-weight: bold; color: #B8860B; margin-bottom: 0.5rem;">
                        $${parseFloat(service.member_price || 0).toFixed(0)}
                    </div>
                    <p style="color: rgba(255,255,255,0.6); font-size: 0.875rem;">per visit</p>
                    ${service.non_member_price && service.member_price ? `
                        <div style="margin-top: 1rem; padding: 0.5rem; background: rgba(16,185,129,0.2); border-radius: 4px;">
                            <span style="color: #10B981; font-weight: bold;">
                                Save $${(parseFloat(service.non_member_price) - parseFloat(service.member_price)).toFixed(0)}
                            </span>
                        </div>
                    ` : ''}
                </div>
                
                ${hasUnlimited ? `
                    <!-- Unlimited Members -->
                    <div style="background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.1)); padding: 2rem; border-radius: 8px; text-align: center; border: 2px solid #10B981;">
                        <h3 style="margin-bottom: 1rem; color: #10B981; font-weight: bold;">Unlimited Members</h3>
                        <div style="font-size: 2.5rem; font-weight: bold; color: #10B981; margin-bottom: 0.5rem;">
                            Included
                        </div>
                        <p style="color: rgba(255,255,255,0.6); font-size: 0.875rem;">unlimited access</p>
                        <div style="margin-top: 1rem; padding: 0.5rem; background: rgba(16,185,129,0.2); border-radius: 4px;">
                            <span style="color: #10B981; font-weight: bold;">Best Value</span>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Render available add-ons
     * @param {Array} addons - Add-ons list
     */
    renderAddons(addons) {
        const container = document.getElementById('service-addons');
        if (!container || addons.length === 0) {
            if (container) container.style.display = 'none';
            return;
        }

        container.innerHTML = `
            <h3 style="margin-bottom: 1.5rem;">Enhance Your Experience</h3>
            <div class="addons-list" style="display: grid; gap: 1rem;">
                ${addons.map(addon => `
                    <label style="display: flex; align-items: center; gap: 1rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px; cursor: pointer; transition: all 0.3s ease;">
                        <input 
                            type="checkbox" 
                            value="${addon.id}"
                            data-price="${addon.price}"
                            data-name="${addon.name}"
                            onchange="serviceDetail.toggleAddon(${addon.id}, ${addon.price}, '${addon.name.replace(/'/g, "\\'")}')"
                            style="width: 20px; height: 20px; cursor: pointer;"
                        >
                        <div style="flex: 1;">
                            <div style="font-weight: 600;">${addon.name}</div>
                            <div style="font-size: 0.875rem; color: rgba(255,255,255,0.7); margin-top: 0.25rem;">
                                ${addon.description || ''}
                            </div>
                        </div>
                        <div style="font-weight: bold; color: #B8860B;">
                            +$${parseFloat(addon.price).toFixed(0)}
                        </div>
                    </label>
                `).join('')}
            </div>
            <div class="addon-total" style="margin-top: 1.5rem; padding: 1rem; background: rgba(184,134,11,0.1); border-radius: 8px; text-align: center;">
                <span style="color: rgba(255,255,255,0.7);">Add-ons Total: </span>
                <span style="font-size: 1.5rem; font-weight: bold; color: #B8860B;">$<span id="addons-total">0.00</span></span>
            </div>
        `;
    }

    /**
     * Toggle add-on selection
     * @param {number} addonId - Add-on ID
     * @param {number} price - Add-on price
     * @param {string} name - Add-on name
     */
    toggleAddon(addonId, price, name) {
        const checkbox = document.querySelector(`input[value="${addonId}"]`);

        if (checkbox.checked) {
            this.selectedAddons.push({ id: addonId, price, name });
            this.showToast(`${name} added`, 'success');
        } else {
            this.selectedAddons = this.selectedAddons.filter(a => a.id !== addonId);
            this.showToast(`${name} removed`, 'info');
        }

        this.updateAddonsTotal();
    }

    /**
     * Update add-ons total
     */
    updateAddonsTotal() {
        const total = this.selectedAddons.reduce((sum, addon) => sum + parseFloat(addon.price), 0);
        const totalElement = document.getElementById('addons-total');
        if (totalElement) {
            totalElement.textContent = total.toFixed(2);
        }
    }

    /**
     * Setup booking button
     */
    setupBookingButton() {
        const bookBtn = document.getElementById('quick-book-btn');
        if (bookBtn) {
            bookBtn.addEventListener('click', () => {
                // Build booking URL with pre-selected service and add-ons
                const addonIds = this.selectedAddons.map(a => a.id).join(',');
                const url = `/book/?service=${this.serviceSlug}${addonIds ? '&addons=' + addonIds : ''}`;
                window.location.href = url;
            });
        }
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
if (!document.getElementById('service-detail-animations')) {
    const style = document.createElement('style');
    style.id = 'service-detail-animations';
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

