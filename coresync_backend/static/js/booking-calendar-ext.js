/**
 * CoreSync Booking Calendar Extensions
 * Extends the CoreSyncBookingCalendar class from script.js
 * Handles: membership status display, level switching
 */

// Global variables
let bookingCalendar = null;
let selectedDates = [];

// ===================================
// MEMBERSHIP STATUS DISPLAY
// ===================================

/**
 * Initialize membership status display
 */
function initializeMembershipStatus() {
    const membership = getCurrentMembershipLevel();
    updateMembershipDisplay(membership);
}

/**
 * Get current membership level from URL or localStorage
 * @returns {string} Membership level: 'none', 'base', 'premium', or 'unlimited'
 */
function getCurrentMembershipLevel() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('membership') || localStorage.getItem('membershipLevel') || 'none';
}

/**
 * Update membership display with status and benefits
 * @param {string} level - Membership level
 */
function updateMembershipDisplay(level) {
    const statusElement = document.getElementById('current-status');
    const benefitsElement = document.getElementById('membership-benefits');

    if (!statusElement || !benefitsElement) return;

    let statusText, statusColor, benefits;

    switch (level) {
        case 'unlimited':
            statusText = 'VIP UNLIMITED MEMBER';
            statusColor = '#F5F5DC';
            benefits = 'Book up to 3 months ahead • Priority access • All services included • VIP treatment';
            break;
        case 'premium':
            statusText = 'PREMIUM MEMBER';
            statusColor = '#F5F5DC';
            benefits = 'Book up to 2 months ahead • Priority booking • 30-40% discount • Free services included';
            break;
        case 'base':
            statusText = 'BASE MEMBER';
            statusColor = '#F5F5DC';
            benefits = 'Book up to 1 month ahead • 25% discount on all services';
            break;
        default:
            statusText = 'NON-MEMBER';
            statusColor = 'rgba(255,255,255,0.7)';
            benefits = 'Book up to 3 days ahead • Full pricing • Join membership for better access';
    }

    statusElement.textContent = statusText;
    statusElement.style.color = statusColor;
    benefitsElement.textContent = benefits;
}

/**
 * Set membership level (demo function)
 * @param {string} level - Membership level to set
 */
function setMembershipLevel(level) {
    localStorage.setItem('membershipLevel', level);
    const url = new URL(window.location);
    url.searchParams.set('membership', level);
    window.history.pushState({}, '', url);

    updateMembershipDisplay(level);

    // Reinitialize calendar with new membership level
    if (bookingCalendar) {
        initializeBookingCalendar();
    }
}

// ===================================
// BOOKING CALENDAR INITIALIZATION
// ===================================

/**
 * Initialize booking calendar
 */
function initializeBookingCalendar() {
    const container = document.getElementById('booking-calendar-container');

    if (!container) return;

    // Clear previous content
    container.innerHTML = '<div class="text-center" style="color: rgba(255,255,255,0.7); font-family: \'Maison_Neue_Book\', sans-serif; padding: 2rem;">Initializing calendar...</div>';

    // Initialize calendar with slight delay to show loading
    setTimeout(() => {
        if (typeof CoreSyncBookingCalendar !== 'undefined') {
            bookingCalendar = new CoreSyncBookingCalendar('booking-calendar-container');
        }
    }, 300);
}

// ===================================
// EXTEND CORESYNCBOOKINGCALENDAR
// ===================================

/**
 * Extend CoreSyncBookingCalendar with membership integration
 * This runs after script.js has loaded the base class
 */
function extendBookingCalendar() {
    if (typeof CoreSyncBookingCalendar === 'undefined') {
        console.warn('CoreSyncBookingCalendar not found. Make sure script.js is loaded first.');
        return;
    }

    // Override getUserPrivileges to integrate with membership system
    const originalGetUserPrivileges = CoreSyncBookingCalendar.prototype.getUserPrivileges;

    CoreSyncBookingCalendar.prototype.getUserPrivileges = function () {
        const membershipLevel = getCurrentMembershipLevel();

        switch (membershipLevel) {
            case 'unlimited':
                return {
                    isMember: true,
                    isVip: true,
                    hasPriorityBooking: true,
                    canBookPrioritySlots: true,
                    maxAdvanceDays: 90,
                    discountPercentage: 100 // All inclusive
                };
            case 'premium':
                return {
                    isMember: true,
                    isVip: false,
                    hasPriorityBooking: true,
                    canBookPrioritySlots: true,
                    maxAdvanceDays: 60,
                    discountPercentage: 35
                };
            case 'base':
                return {
                    isMember: true,
                    isVip: false,
                    hasPriorityBooking: false,
                    canBookPrioritySlots: false,
                    maxAdvanceDays: 30,
                    discountPercentage: 25
                };
            default:
                return {
                    isMember: false,
                    isVip: false,
                    hasPriorityBooking: false,
                    canBookPrioritySlots: false,
                    maxAdvanceDays: 3,
                    discountPercentage: 0
                };
        }
    };
}

// ===================================
// EVENT LISTENERS
// ===================================

document.addEventListener('DOMContentLoaded', function () {
    // Initialize membership status
    initializeMembershipStatus();

    // Extend booking calendar class
    extendBookingCalendar();

    // Initialize booking calendar
    initializeBookingCalendar();

    // Add hover effect to demo buttons
    document.querySelectorAll('.demo-btn').forEach(btn => {
        btn.addEventListener('mouseenter', function () {
            if (!this.classList.contains('demo-btn--vip')) {
                this.style.background = 'rgba(255,255,255,0.1)';
                this.style.borderColor = 'rgba(255,255,255,0.5)';
            }
        });
        btn.addEventListener('mouseleave', function () {
            if (!this.classList.contains('demo-btn--vip')) {
                this.style.background = 'transparent';
                this.style.borderColor = 'rgba(255,255,255,0.3)';
            }
        });
    });

    // Demo membership level buttons (data-membership-level)
    document.querySelectorAll('[data-membership-level]').forEach(btn => {
        btn.addEventListener('click', function () {
            const level = this.dataset.membershipLevel;
            setMembershipLevel(level);
        });
    });
});

// Export functions for global access (backwards compatibility)
window.initializeMembershipStatus = initializeMembershipStatus;
window.getCurrentMembershipLevel = getCurrentMembershipLevel;
window.updateMembershipDisplay = updateMembershipDisplay;
window.setMembershipLevel = setMembershipLevel;
window.initializeBookingCalendar = initializeBookingCalendar;

