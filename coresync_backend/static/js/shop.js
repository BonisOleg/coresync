// ====================================================
// CORESYNC SHOP
// Extends DashboardAPI for consistency
// ====================================================

/**
 * Shop API - extends base DashboardAPI class
 * Uses existing patterns from dashboard.js
 */
class CoreSyncShopAPI extends DashboardAPI {
    constructor() {
        super();
        this.productsCache = new Map();
    }

    /**
     * Get all products or filter by category
     * @param {string} category - Category filter or 'all'
     * @returns {Promise<Array>}
     */
    async getProducts(category = 'all') {
        const cacheKey = `products_${category}`;

        // Return cached if available
        if (this.productsCache.has(cacheKey)) {
            return this.productsCache.get(cacheKey);
        }

        try {
            const url = category !== 'all'
                ? `/api/shop/products/?category=${category}`
                : '/api/shop/products/';

            const data = await this.request(url);

            // Cache the results
            this.productsCache.set(cacheKey, data);

            return data;
        } catch (error) {
            console.error('Failed to load products:', error);
            throw error;
        }
    }

    /**
     * Get product categories
     * @returns {Promise<Object>}
     */
    async getCategories() {
        return this.request('/api/shop/products/categories/');
    }

    /**
     * Create pickup order
     * @param {Object} orderData - Order items and notes
     * @returns {Promise<Object>}
     */
    async createOrder(orderData) {
        return this.request('/api/shop/orders/create_order/', {
            method: 'POST',
            body: JSON.stringify(orderData)
        });
    }

    /**
     * Get user's orders
     * @returns {Promise<Array>}
     */
    async getMyOrders() {
        return this.request('/api/shop/orders/');
    }

    /**
     * Cancel order
     * @param {number} orderId - Order ID
     * @returns {Promise<Object>}
     */
    async cancelOrder(orderId) {
        return this.request(`/api/shop/orders/${orderId}/cancel_order/`, {
            method: 'POST'
        });
    }
}

/**
 * Main Shop class
 */
class CoreSyncShop {
    constructor() {
        this.api = new CoreSyncShopAPI();
        this.products = [];
        this.cart = this.loadCart();
        this.currentCategory = 'all';

        this.init();
    }

    /**
     * Initialize shop
     */
    async init() {
        await this.loadProducts();
        this.setupFilters();
        this.updateCartBadge();
        this.setupEventListeners();
    }

    /**
     * Load products from API
     * @param {string} category - Category to filter
     */
    async loadProducts(category = 'all') {
        try {
            this.showLoading();

            const data = await this.api.getProducts(category);
            this.products = data.results || data;

            if (this.products.length === 0) {
                this.showEmptyState();
            } else {
                this.renderProducts();
            }
        } catch (error) {
            console.error('Error loading products:', error);
            this.showError('Failed to load products. Please refresh the page.');
        }
    }

    /**
     * Render products grid
     */
    renderProducts() {
        const grid = document.getElementById('products-grid');
        const loading = document.getElementById('loading');
        const emptyState = document.getElementById('empty-state');

        if (!grid) return;

        loading.style.display = 'none';
        emptyState.style.display = 'none';
        grid.style.display = 'grid';

        grid.innerHTML = this.products.map(product => `
            <div class="product-card" data-product-id="${product.id}">
                <img 
                    src="${product.main_image || '/static/images/placeholder.png'}" 
                    alt="${product.name}"
                    class="product-image"
                    onerror="this.src='/static/images/placeholder.png'"
                >
                <div class="product-info">
                    <h3 class="product-title">${product.name}</h3>
                    <p class="product-description">${product.short_description}</p>
                    <div class="product-pricing">
                        <div>
                            <span class="price-original">$${parseFloat(product.price).toFixed(2)}</span>
                            <span class="price-member">$${parseFloat(product.member_price).toFixed(2)}</span>
                        </div>
                        <div>
                            <span class="badge" style="background: #10B981; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem;">
                                Save ${product.discount_percentage}%
                            </span>
                        </div>
                    </div>
                    ${product.in_stock
                ? `<button 
                            class="btn-primary btn-small" 
                            style="width: 100%;"
                            onclick="shop.addToCart(${product.id}, '${product.name.replace(/'/g, "\\'")}', ${product.member_price}, '${product.main_image || ''}')"
                          >
                            Add to Cart
                          </button>`
                : `<div style="text-align: center; padding: 0.75rem; background: rgba(239, 68, 68, 0.1); border-radius: 4px;">
                            <span style="color: #EF4444;">Out of Stock</span>
                          </div>`
            }
                </div>
            </div>
        `).join('');
    }

    /**
     * Setup category filters
     */
    setupFilters() {
        const filterButtons = document.querySelectorAll('.filter-btn');

        filterButtons.forEach(btn => {
            btn.addEventListener('click', async (e) => {
                // Update active state
                filterButtons.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');

                // Load products
                const category = e.target.dataset.category;
                this.currentCategory = category;
                await this.loadProducts(category);
            });
        });
    }

    /**
     * Add product to cart
     * @param {number} id - Product ID
     * @param {string} name - Product name
     * @param {number} price - Product price
     * @param {string} image - Product image URL
     */
    addToCart(id, name, price, image) {
        const existing = this.cart.find(item => item.id === id);

        if (existing) {
            existing.quantity++;
        } else {
            this.cart.push({
                id,
                name,
                price,
                image,
                quantity: 1
            });
        }

        this.saveCart();
        this.updateCartBadge();
        this.showToast(`${name} added to pickup list!`, 'success');
    }

    /**
     * Load cart from localStorage
     * @returns {Array}
     */
    loadCart() {
        try {
            return JSON.parse(localStorage.getItem('coresync_cart')) || [];
        } catch (e) {
            return [];
        }
    }

    /**
     * Save cart to localStorage
     */
    saveCart() {
        localStorage.setItem('coresync_cart', JSON.stringify(this.cart));
    }

    /**
     * Update cart badge
     */
    updateCartBadge() {
        const badge = document.getElementById('cart-badge');
        if (!badge) return;

        const totalItems = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        badge.textContent = totalItems;
        badge.style.display = totalItems > 0 ? 'flex' : 'none';
    }

    /**
     * Show loading state
     */
    showLoading() {
        const loading = document.getElementById('loading');
        const grid = document.getElementById('products-grid');
        const emptyState = document.getElementById('empty-state');

        if (loading) loading.style.display = 'block';
        if (grid) grid.style.display = 'none';
        if (emptyState) emptyState.style.display = 'none';
    }

    /**
     * Show empty state
     */
    showEmptyState() {
        const loading = document.getElementById('loading');
        const grid = document.getElementById('products-grid');
        const emptyState = document.getElementById('empty-state');

        if (loading) loading.style.display = 'none';
        if (grid) grid.style.display = 'none';
        if (emptyState) emptyState.style.display = 'block';
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        this.showEmptyState();
        const emptyState = document.getElementById('empty-state');
        if (emptyState) {
            emptyState.innerHTML = `
                <p style="color: #EF4444;">${message}</p>
                <button class="btn-secondary" onclick="location.reload()">Retry</button>
            `;
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
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            background: ${type === 'success' ? '#10B981' : type === 'error' ? '#EF4444' : '#3B82F6'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            animation: slideInRight 0.3s ease, fadeOut 0.3s ease 2.7s;
            min-width: 250px;
        `;
        toast.textContent = message;

        container.appendChild(toast);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Create toast container if not exists
     * @returns {HTMLElement}
     */
    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        `;
        document.body.appendChild(container);
        return container;
    }

    /**
     * Setup additional event listeners
     */
    setupEventListeners() {
        // Add any additional listeners here
    }
}

/**
 * Cart page class
 */
class CoreSyncCart {
    constructor() {
        this.api = new CoreSyncShopAPI();
        this.cart = this.loadCart();
        this.init();
    }

    init() {
        this.renderCart();
        this.setupCheckout();
        this.setMinPickupDate();
    }

    loadCart() {
        try {
            return JSON.parse(localStorage.getItem('coresync_cart')) || [];
        } catch (e) {
            return [];
        }
    }

    saveCart() {
        localStorage.setItem('coresync_cart', JSON.stringify(this.cart));
    }

    renderCart() {
        const container = document.getElementById('cart-items-list');
        const emptyCart = document.getElementById('empty-cart');
        const summary = document.getElementById('cart-summary');

        if (!container) return;

        if (this.cart.length === 0) {
            container.style.display = 'none';
            emptyCart.style.display = 'block';
            summary.style.display = 'none';
            return;
        }

        container.style.display = 'block';
        emptyCart.style.display = 'none';
        summary.style.display = 'block';

        container.innerHTML = this.cart.map((item, index) => `
            <div class="cart-item">
                <img 
                    src="${item.image || '/static/images/placeholder.png'}" 
                    alt="${item.name}"
                    class="cart-item-image"
                >
                <div class="cart-item-info">
                    <div class="cart-item-title">${item.name}</div>
                    <div class="cart-item-price">$${parseFloat(item.price).toFixed(2)} each</div>
                    <div class="quantity-controls">
                        <button class="quantity-btn" onclick="cart.decreaseQuantity(${index})">-</button>
                        <span class="quantity-display">${item.quantity}</span>
                        <button class="quantity-btn" onclick="cart.increaseQuantity(${index})">+</button>
                    </div>
                </div>
                <div class="cart-item-actions">
                    <div class="cart-item-price" style="margin-bottom: 1rem;">
                        $${(item.price * item.quantity).toFixed(2)}
                    </div>
                    <button class="remove-btn" onclick="cart.removeItem(${index})">Remove</button>
                </div>
            </div>
        `).join('');

        this.updateSummary();
    }

    increaseQuantity(index) {
        this.cart[index].quantity++;
        this.saveCart();
        this.renderCart();
    }

    decreaseQuantity(index) {
        if (this.cart[index].quantity > 1) {
            this.cart[index].quantity--;
            this.saveCart();
            this.renderCart();
        }
    }

    removeItem(index) {
        this.cart.splice(index, 1);
        this.saveCart();
        this.renderCart();
        this.showToast('Item removed from cart', 'info');
    }

    updateSummary() {
        const subtotal = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const tax = subtotal * 0.08; // 8% tax
        const total = subtotal + tax;

        document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
        document.getElementById('tax').textContent = `$${tax.toFixed(2)}`;
        document.getElementById('total').textContent = `$${total.toFixed(2)}`;
    }

    setMinPickupDate() {
        const dateInput = document.getElementById('pickup-date');
        if (dateInput) {
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            dateInput.min = tomorrow.toISOString().split('T')[0];
        }
    }

    setupCheckout() {
        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', () => this.checkout());
        }
    }

    async checkout() {
        if (this.cart.length === 0) {
            this.showToast('Your cart is empty', 'error');
            return;
        }

        const pickupDate = document.getElementById('pickup-date').value;
        const customerNotes = document.getElementById('customer-notes').value;

        const orderData = {
            items: this.cart.map(item => ({
                product_id: item.id,
                quantity: item.quantity
            })),
            customer_notes: customerNotes,
            pickup_date: pickupDate || null
        };

        try {
            const checkoutBtn = document.getElementById('checkout-btn');
            checkoutBtn.disabled = true;
            checkoutBtn.textContent = 'Processing...';

            const order = await this.api.createOrder(orderData);

            // Clear cart
            this.cart = [];
            this.saveCart();

            this.showToast('Order placed successfully!', 'success');

            setTimeout(() => {
                window.location.href = '/dashboard/';
            }, 2000);

        } catch (error) {
            console.error('Checkout error:', error);
            this.showToast(error.message || 'Failed to place order', 'error');

            const checkoutBtn = document.getElementById('checkout-btn');
            checkoutBtn.disabled = false;
            checkoutBtn.textContent = 'Complete Order';
        }
    }

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

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        document.body.appendChild(container);
        return container;
    }
}

// Add animation keyframes
if (!document.getElementById('shop-animations')) {
    const style = document.createElement('style');
    style.id = 'shop-animations';
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

