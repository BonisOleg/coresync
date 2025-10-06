// ====================================================
// CORESYNC DASHBOARD
// API-First, Lightweight, Production-Ready
// ====================================================

class DashboardAPI {
    constructor() {
        this.baseURL = '/api';
        this.token = localStorage.getItem('auth_token');
    }

    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                ...options,
                headers
            });

            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login/';
                    return null;
                }
                throw new Error(`API Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    async getDashboard() {
        return this.request('/users/profile/dashboard/');
    }

    async getMyBookings() {
        return this.request('/bookings/my-bookings/');
    }

    async cancelBooking(bookingId) {
        return this.request(`/bookings/${bookingId}/cancel/`, { method: 'PUT' });
    }

    async rescheduleBooking(bookingId, data) {
        return this.request(`/bookings/${bookingId}/reschedule/`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async updateProfile(data) {
        return this.request('/users/profile/', {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async getMyMembership() {
        return this.request('/memberships/my-membership/');
    }
}

const api = new DashboardAPI();

// ====================================================
// DASHBOARD OVERVIEW
// ====================================================

class DashboardOverview {
    constructor() {
        this.init();
    }

    async init() {
        await this.loadDashboardData();
    }

    async loadDashboardData() {
        try {
            const data = await api.getDashboard();

            if (!data) return;

            this.renderQuickStats(data.quick_stats || {});
            this.renderNextAppointment(data.next_appointment);
            this.renderRecommendations(data.ai_recommendations || []);
            this.renderRecentServices(data.recent_services || []);

        } catch (error) {
            console.error('Dashboard load error:', error);
        }
    }

    renderQuickStats(stats) {
        const updates = {
            'services-count': stats.services_this_month || 0,
            'total-spent': `$${stats.total_spent || 0}`,
            'days-remaining': stats.membership_days || '-'
        };

        Object.entries(updates).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        });
    }

    renderNextAppointment(appointment) {
        const container = document.getElementById('next-appointment-container');
        if (!container) return;

        if (!appointment) {
            container.innerHTML = `
                <div class="membership-card" style="text-align: center; padding: 3rem;">
                    <p style="color: rgba(255,255,255,0.5); margin-bottom: 1.5rem; font-family: 'Maison_Neue_Book', sans-serif;">
                        No upcoming appointments
                    </p>
                    <a href="/book/" class="membership-cta-btn">Book Your First Service</a>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="membership-card" style="text-align: left; padding: 2rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div>
                        <div class="membership-card-title" style="font-size: 1.2rem; margin-bottom: 0.5rem;">
                            ${appointment.service_name}
                        </div>
                        <div style="font-family: 'Maison_Neue_Mono', monospace; font-size: 0.85rem; color: rgba(255,255,255,0.6);">
                            ${appointment.date} at ${appointment.time}
                        </div>
                    </div>
                </div>
                <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; line-height: 1.8;">
                    ${appointment.room ? `<div>📍 ${appointment.room}</div>` : ''}
                    ${appointment.technician ? `<div>👤 ${appointment.technician}</div>` : ''}
                </div>
                <div style="display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap;">
                    <a href="/dashboard/bookings/#${appointment.id}" class="membership-cta-btn btn-secondary">
                        View Details
                    </a>
                </div>
            </div>
        `;
    }

    renderRecommendations(recommendations) {
        const container = document.getElementById('recommendations-container');
        if (!container) return;

        if (recommendations.length === 0) {
            container.innerHTML = `
                <div class="membership-card" style="grid-column: 1/-1; text-align: center; padding: 2rem;">
                    <p style="color: rgba(255,255,255,0.5); font-family: 'Maison_Neue_Book', sans-serif;">
                        No recommendations yet
                    </p>
                </div>
            `;
            return;
        }

        container.innerHTML = recommendations.map(rec => `
            <div class="membership-card" style="text-align: left;">
                <h4 class="membership-card-title" style="font-size: 1rem; margin-bottom: 1rem;">
                    ${rec.service_name || rec.type}
                </h4>
                <p style="color: rgba(255,255,255,0.7); font-family: 'Maison_Neue_Book', sans-serif; font-size: 0.9rem; margin-bottom: 1rem; line-height: 1.6;">
                    ${rec.reason || rec.message}
                </p>
                ${rec.suggested_date ? `
                    <p style="color: rgba(255,255,255,0.5); font-family: 'Maison_Neue_Mono', monospace; font-size: 0.85rem; margin-bottom: 1rem;">
                        Suggested: ${rec.suggested_date}
                    </p>
                ` : ''}
                <button onclick="window.location.href='/book/'" class="membership-cta-btn" style="width: 100%;">
                    Book Now
                </button>
            </div>
        `).join('');
    }

    renderRecentServices(services) {
        const container = document.getElementById('bookings-preview-container');
        if (!container) return;

        if (!services || services.length === 0) {
            container.innerHTML = `
                <div class="membership-card" style="grid-column: 1/-1; text-align: center; padding: 3rem;">
                    <p style="color: rgba(255,255,255,0.5); font-family: 'Maison_Neue_Book', sans-serif;">
                        No bookings yet
                    </p>
                </div>
            `;
            return;
        }

        container.innerHTML = services.slice(0, 3).map(service => `
            <div class="membership-card" style="text-align: left;">
                <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div class="membership-card-title" style="font-size: 1rem; margin-bottom: 0.5rem;">
                        ${service.service_name || service.service?.name}
                    </div>
                    <div style="font-family: 'Maison_Neue_Mono', monospace; font-size: 0.85rem; color: rgba(255,255,255,0.6);">
                        ${service.service_date || service.date}
                    </div>
                </div>
                <div style="color: rgba(255,255,255,0.6); font-size: 0.9rem; font-family: 'Maison_Neue_Book', sans-serif;">
                    ${service.price_paid ? `<div>💰 $${service.price_paid}</div>` : ''}
                    ${service.rating ? `<div style="margin-top: 0.5rem;">⭐ ${service.rating}/5</div>` : ''}
                </div>
            </div>
        `).join('');
    }
}

// ====================================================
// DASHBOARD BOOKINGS
// ====================================================

class DashboardBookings {
    constructor() {
        this.currentFilter = 'upcoming';
        this.init();
    }

    async init() {
        this.bindFilterEvents();
        await this.loadBookings();
    }

    bindFilterEvents() {
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.currentFilter = e.target.dataset.filter;
                this.updateActiveFilter(e.target);
                this.loadBookings();
            });
        });
    }

    updateActiveFilter(activeBtn) {
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.classList.remove('active');
            btn.style.background = 'transparent';
            btn.style.borderColor = 'rgba(255,255,255,0.3)';
            btn.style.color = '#fff';
        });
        activeBtn.classList.add('active');
        activeBtn.style.background = 'rgba(245,245,220,0.1)';
        activeBtn.style.borderColor = '#F5F5DC';
        activeBtn.style.color = '#F5F5DC';
    }

    async loadBookings() {
        try {
            const data = await api.getMyBookings();
            const bookings = this.currentFilter === 'upcoming' ? data.upcoming : data.past;
            this.renderBookings(bookings);
        } catch (error) {
            console.error('Load bookings error:', error);
        }
    }

    renderBookings(bookings) {
        const container = document.getElementById('all-bookings-container');
        if (!container) return;

        if (!bookings || bookings.length === 0) {
            container.innerHTML = `
                <div class="membership-card" style="grid-column: 1/-1; text-align: center; padding: 4rem;">
                    <p style="color: rgba(255,255,255,0.5); margin-bottom: 2rem; font-family: 'Maison_Neue_Book', sans-serif;">
                        No ${this.currentFilter} bookings
                    </p>
                    <a href="/book/" class="membership-cta-btn">Book a Service</a>
                </div>
            `;
            return;
        }

        container.innerHTML = bookings.map(booking => `
            <div class="membership-card" style="text-align: left;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div>
                        <div class="membership-card-title" style="font-size: 1.2rem; margin-bottom: 0.5rem;">
                            ${booking.service}
                        </div>
                        <div style="font-family: 'Maison_Neue_Mono', monospace; font-size: 0.85rem; color: rgba(255,255,255,0.6);">
                            ${booking.date} at ${booking.start_time}
                        </div>
                    </div>
                    <span style="color: #F5F5DC; font-size: 0.85rem; text-transform: uppercase; font-family: 'Maison_Neue_Mono', monospace;">
                        ${booking.status}
                    </span>
                </div>
                <div style="color: rgba(255,255,255,0.7); font-family: 'Maison_Neue_Book', sans-serif; font-size: 0.9rem; line-height: 1.8;">
                    ${booking.room ? `<div>📍 ${booking.room}</div>` : ''}
                    ${booking.duration ? `<div>⏱️ ${booking.duration} minutes</div>` : ''}
                    ${booking.addons?.length ? `<div>➕ ${booking.addons.join(', ')}</div>` : ''}
                </div>
                ${this.currentFilter === 'upcoming' ? `
                    <div style="display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap;">
                        ${booking.can_cancel ? `
                            <button onclick="dashboard.cancel(${booking.id})" class="membership-cta-btn btn-danger">
                                Cancel
                            </button>
                        ` : ''}
                    </div>
                ` : `
                    <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
                        <button onclick="window.location.href='/book/'" class="membership-cta-btn btn-secondary">
                            Book Again
                        </button>
                    </div>
                `}
            </div>
        `).join('');
    }

    async cancel(bookingId) {
        if (!confirm('Are you sure you want to cancel this booking?')) return;

        try {
            await api.cancelBooking(bookingId);
            await this.loadBookings();
            alert('Booking cancelled successfully');
        } catch (error) {
            alert('Failed to cancel booking');
        }
    }
}

// ====================================================
// INITIALIZE
// ====================================================

let dashboard;

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('next-appointment-container')) {
        new DashboardOverview();
    }

    if (document.getElementById('all-bookings-container')) {
        dashboard = new DashboardBookings();
    }
});

