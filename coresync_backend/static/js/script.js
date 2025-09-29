document.addEventListener('DOMContentLoaded', () => {
    const serviceCards = document.querySelectorAll('.service-card'),
        burgerMenu = document.getElementById('burger-menu'),
        navMenu = document.getElementById('nav-menu'),
        header = document.querySelector('.header'),
        heroImage = document.querySelector('.hero-image'),
        footerBtn = document.querySelector('.footer-btn');

    document.querySelectorAll('.service-btn').forEach(btn => btn.addEventListener('click', function () {
        this.style.transform = 'scale(0.98)';
        setTimeout(() => this.style.transform = 'scale(1)', 150);
    }));

    if (footerBtn) footerBtn.addEventListener('click', function () {
        this.style.transform = 'translateY(-2px) scale(1.02)';
        setTimeout(() => this.style.transform = 'translateY(-2px) scale(1)', 150);
    });

    if (heroImage) window.addEventListener('scroll', () => heroImage.style.transform = `translateY(${pageYOffset * -.5}px)`);

    serviceCards.forEach(card => {
        card.addEventListener('mouseenter', () => card.style.transform = 'translateY(-8px)');
        card.addEventListener('mouseleave', () => card.style.transform = 'translateY(0)');
        card.addEventListener('click', function () {
            const link = this.getAttribute('data-link');
            if (link) {
                this.style.opacity = '.7';
                location.href = link;
            }
        });
    });

    if (burgerMenu && navMenu) {
        burgerMenu.addEventListener('click', () => {
            // Only activate navigation on desktop
            if (window.innerWidth <= 1024) {
                burgerMenu.classList.toggle('active');
                return;
            }

            const isMenuOpen = burgerMenu.classList.contains('active');

            if (isMenuOpen) {
                // Close menu
                burgerMenu.classList.remove('active');
                navMenu.classList.remove('active');
                header.classList.remove('menu-open');
            } else {
                // Open menu
                burgerMenu.classList.add('active');
                header.classList.add('menu-open');

                // Slight delay for logo animation to start first
                setTimeout(() => {
                    navMenu.classList.add('active');
                }, 200);
            }
        });

        // Navigation buttons functionality
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const link = this.getAttribute('data-link');
                if (link) {
                    // Add gentle fade out animation
                    navMenu.style.transition = 'opacity 0.8s ease';
                    navMenu.style.opacity = '0';

                    // Close menu with animation
                    setTimeout(() => {
                        burgerMenu.classList.remove('active');
                        navMenu.classList.remove('active');
                        header.classList.remove('menu-open');
                        navMenu.style.transition = '';
                        navMenu.style.opacity = '';
                    }, 400);

                    // Navigate after animation
                    setTimeout(() => {
                        window.location.href = link;
                    }, 800);
                }
            });
        });
    }

    if (header) window.addEventListener('scroll', () => header.style.background = scrollY > 100 ? 'rgba(0,0,0,.95)' : 'rgba(0,0,0,.9)');

    document.querySelectorAll('img').forEach(img => img.addEventListener('error', () => console.warn('Image failed to load:', img.src)));

    if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
        document.body.style.cursor = 'pointer';
        const fix = () => document.documentElement.style.setProperty('--vh', `${innerHeight * .01}px`);
        fix();
        addEventListener('resize', fix);
        addEventListener('orientationchange', () => setTimeout(fix, 500));
    }
});

window.addEventListener('load', () => ['/static/images/Hiro_converted.png', '/static/images/private.png', '/static/images/private1.png', '/static/images/menssuite.png', '/static/images/menssuite1.png', '/static/images/menu.png'].forEach(url => { const img = new Image(); img.src = url; }));

// ===================================
// NEW BOOKING CALENDAR FUNCTIONALITY
// ===================================

// Booking Calendar Class (Safe, no conflicts with existing code)
class CoreSyncBookingCalendar {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.currentStep = 1;
        this.maxSteps = 6;  // ЗБІЛЬШЕНО: окремо дата та час
        this.bookingData = {
            date: '',
            time: '',
            technician: '',
            service: '',
            addons: []
        };

        if (this.container) {
            this.init();
        }
    }

    init() {
        this.render();
        this.bindEvents();
    }

    render() {
        this.container.innerHTML = `
            <div class="booking-calendar-wrapper" style="max-width: 800px; margin: 0 auto;">
                <!-- Step Indicator -->
                <div class="booking-steps" style="display: flex; justify-content: center; margin-bottom: 3rem;">
                    ${Array.from({ length: this.maxSteps }, (_, i) => `
                        <div class="booking-step-indicator ${i + 1 === this.currentStep ? 'active' : ''}" 
                             style="width: 40px; height: 40px; border-radius: 50%; background: ${i + 1 <= this.currentStep ? '#B8860B' : 'rgba(255,255,255,0.2)'}; 
                                    color: ${i + 1 <= this.currentStep ? '#000' : '#fff'}; display: flex; align-items: center; justify-content: center; 
                                    margin: 0 1rem; font-family: 'Maison_Neue_Bold', sans-serif; font-weight: bold;">
                            ${i + 1}
                        </div>
                    `).join('')}
                </div>
                
                <!-- Step Content -->
                <div class="booking-step-content" id="step-content">
                    ${this.renderCurrentStep()}
                </div>
                
                <!-- Navigation Buttons -->
                <div class="booking-nav" style="display: flex; justify-content: space-between; margin-top: 3rem;">
                    <button id="booking-prev-btn" class="booking-nav-btn" 
                            style="background: transparent; border: 1px solid #fff; color: #fff; padding: 1rem 2rem; 
                                   font-family: 'Maison_Neue_Bold', sans-serif; cursor: pointer; 
                                   ${this.currentStep === 1 ? 'opacity: 0.5; pointer-events: none;' : ''}"
                            ${this.currentStep === 1 ? 'disabled' : ''}>
                        PREVIOUS
                    </button>
                    <button id="booking-next-btn" class="booking-nav-btn"
                            style="background: #B8860B; border: none; color: #000; padding: 1rem 2rem; 
                                   font-family: 'Maison_Neue_Bold', sans-serif; cursor: pointer;">
                        ${this.currentStep === this.maxSteps ? 'BOOK NOW' : 'NEXT'}
                    </button>
                </div>
            </div>
        `;
    }

    renderCurrentStep() {
        switch (this.currentStep) {
            case 1:
                return this.renderDateStep();
            case 2:
                return this.renderTimeStep();
            case 3:
                return this.renderTechnicianStep();
            case 4:
                return this.renderServiceStep();
            case 5:
                return this.renderAddonsStep();
            case 6:
                return this.renderConfirmationStep();
            default:
                return '<div>Invalid step</div>';
        }
    }

    renderDateStep() {
        const today = new Date();
        const dates = [];

        // Generate next 14 days
        for (let i = 0; i < 14; i++) {
            const date = new Date(today);
            date.setDate(today.getDate() + i);
            dates.push(date);
        }

        return `
            <h3 style="color: #B8860B; font-family: 'Maison_Neue_Bold', sans-serif; text-align: center; margin-bottom: 2rem;">
                SELECT DATE
            </h3>
            <div class="date-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                ${dates.map(date => `
                    <button class="date-option" data-date="${date.toISOString().split('T')[0]}"
                            style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); 
                                   color: #fff; padding: 1rem; text-align: center; cursor: pointer; 
                                   font-family: 'Maison_Neue_Book', sans-serif;">
                        <div style="font-size: 0.8rem; opacity: 0.8;">${date.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                        <div style="font-weight: bold;">${date.getDate()}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">${date.toLocaleDateString('en-US', { month: 'short' })}</div>
                    </button>
                `).join('')}
            </div>
        `;
    }

    renderTimeStep() {
        return `
            <h3 style="color: #B8860B; font-family: 'Maison_Neue_Bold', sans-serif; text-align: center; margin-bottom: 2rem;">
                SELECT TIME
            </h3>
            <div class="time-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 1rem;">
                ${['9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM', '8:00 PM'].map(time => `
                    <button class="time-option" data-time="${time}"
                            style="background: rgba(184,134,11,0.1); border: 1px solid #B8860B; 
                                   color: #B8860B; padding: 1rem 0.5rem; text-align: center; cursor: pointer; 
                                   font-family: 'Maison_Neue_Book', sans-serif; font-size: 0.9rem; transition: all 0.3s ease;">
                        ${time}
                    </button>
                `).join('')}
            </div>
            <div style="margin-top: 2rem; text-align: center; color: rgba(255,255,255,0.7); font-family: 'Maison_Neue_Book', sans-serif; font-size: 0.9rem;">
                Selected date: <span style="color: #B8860B; font-weight: bold;">${this.bookingData.date || 'Please select a date first'}</span>
            </div>
        `;
    }

    renderTechnicianStep() {
        const technicians = [
            { name: 'Sarah Johnson', specialty: 'Facial & Skincare', experience: '5 years' },
            { name: 'Michael Chen', specialty: 'Massage Therapy', experience: '8 years' },
            { name: 'Emma Rodriguez', specialty: 'Laser Treatment', experience: '3 years' },
            { name: 'David Kim', specialty: 'AI Massage Bed', experience: '2 years' }
        ];

        return `
            <h3 style="color: #B8860B; font-family: 'Maison_Neue_Bold', sans-serif; text-align: center; margin-bottom: 2rem;">
                SELECT TECHNICIAN
            </h3>
            <div class="technician-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
                ${technicians.map(tech => `
                    <button class="technician-option" data-technician="${tech.name}"
                            style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); 
                                   color: #fff; padding: 1.5rem; text-align: center; cursor: pointer; 
                                   font-family: 'Maison_Neue_Book', sans-serif;">
                        <div style="font-family: 'Maison_Neue_Bold', sans-serif; font-size: 1.1rem; margin-bottom: 0.5rem;">
                            ${tech.name}
                        </div>
                        <div style="color: #B8860B; font-size: 0.9rem; margin-bottom: 0.3rem;">
                            ${tech.specialty}
                        </div>
                        <div style="opacity: 0.7; font-size: 0.8rem;">
                            ${tech.experience} experience
                        </div>
                    </button>
                `).join('')}
            </div>
        `;
    }

    renderServiceStep() {
        const services = [
            { name: 'AI Massage Therapy', duration: '60 min', price: '$200' },
            { name: 'Facial Treatment', duration: '45 min', price: '$180' },
            { name: 'Laser Hair Removal', duration: '30 min', price: '$150' },
            { name: 'Deep Tissue Massage', duration: '75 min', price: '$240' },
            { name: 'Relaxation Package', duration: '90 min', price: '$300' }
        ];

        return `
            <h3 style="color: #B8860B; font-family: 'Maison_Neue_Bold', sans-serif; text-align: center; margin-bottom: 2rem;">
                SELECT SERVICE
            </h3>
            <div class="service-grid" style="display: grid; gap: 1rem;">
                ${services.map(service => `
                    <button class="service-option" data-service="${service.name}"
                            style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); 
                                   color: #fff; padding: 1.5rem; text-align: left; cursor: pointer; 
                                   font-family: 'Maison_Neue_Book', sans-serif; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-family: 'Maison_Neue_Bold', sans-serif; font-size: 1.1rem; margin-bottom: 0.3rem;">
                                ${service.name}
                            </div>
                            <div style="opacity: 0.7; font-size: 0.9rem;">
                                ${service.duration}
                            </div>
                        </div>
                        <div style="color: #B8860B; font-family: 'Maison_Neue_Bold', sans-serif; font-size: 1.2rem;">
                            ${service.price}
                        </div>
                    </button>
                `).join('')}
            </div>
        `;
    }

    renderAddonsStep() {
        const addons = [
            { name: 'LED Light Therapy', price: '$50' },
            { name: 'Aromatherapy', price: '$25' },
            { name: 'Hot Stone Add-on', price: '$40' },
            { name: 'Oxygen Treatment', price: '$60' }
        ];

        return `
            <h3 style="color: #B8860B; font-family: 'Maison_Neue_Bold', sans-serif; text-align: center; margin-bottom: 2rem;">
                SELECT ADD-ONS (OPTIONAL)
            </h3>
            <div class="addon-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                ${addons.map(addon => `
                    <label class="addon-option" 
                           style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); 
                                  color: #fff; padding: 1.5rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center;
                                  font-family: 'Maison_Neue_Book', sans-serif;">
                        <div>
                            <input type="checkbox" name="addons" value="${addon.name}" 
                                   style="margin-right: 1rem; transform: scale(1.2);">
                            <span>${addon.name}</span>
                        </div>
                        <span style="color: #B8860B; font-family: 'Maison_Neue_Bold', sans-serif;">
                            ${addon.price}
                        </span>
                    </label>
                `).join('')}
            </div>
            <div style="margin-top: 2rem; text-align: center;">
                <button style="background: transparent; border: 1px solid rgba(255,255,255,0.3); color: #fff; 
                               padding: 0.8rem 1.5rem; font-family: 'Maison_Neue_Book', sans-serif; cursor: pointer;"
                        onclick="document.querySelectorAll('input[name=addons]').forEach(cb => cb.checked = false)">
                    SKIP ADD-ONS
                </button>
            </div>
        `;
    }

    renderConfirmationStep() {
        return `
            <h3 style="color: #B8860B; font-family: 'Maison_Neue_Bold', sans-serif; text-align: center; margin-bottom: 2rem;">
                CONFIRM YOUR BOOKING
            </h3>
            <div class="booking-summary" style="background: rgba(255,255,255,0.05); padding: 2rem; border: 1px solid rgba(255,255,255,0.2);">
                <div class="summary-item" style="display: flex; justify-content: space-between; padding: 0.8rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <span style="color: rgba(255,255,255,0.8);">Date & Time:</span>
                    <span style="color: #fff; font-family: 'Maison_Neue_Bold', sans-serif;">${this.bookingData.date} at ${this.bookingData.time}</span>
                </div>
                <div class="summary-item" style="display: flex; justify-content: space-between; padding: 0.8rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <span style="color: rgba(255,255,255,0.8);">Technician:</span>
                    <span style="color: #fff; font-family: 'Maison_Neue_Bold', sans-serif;">${this.bookingData.technician}</span>
                </div>
                <div class="summary-item" style="display: flex; justify-content: space-between; padding: 0.8rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <span style="color: rgba(255,255,255,0.8);">Service:</span>
                    <span style="color: #fff; font-family: 'Maison_Neue_Bold', sans-serif;">${this.bookingData.service}</span>
                </div>
                ${this.bookingData.addons.length > 0 ? `
                    <div class="summary-item" style="display: flex; justify-content: space-between; padding: 0.8rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <span style="color: rgba(255,255,255,0.8);">Add-ons:</span>
                        <span style="color: #B8860B; font-family: 'Maison_Neue_Bold', sans-serif;">${this.bookingData.addons.join(', ')}</span>
                    </div>
                ` : ''}
            </div>
        `;
    }

    bindEvents() {
        // Navigation buttons
        const prevBtn = document.getElementById('booking-prev-btn');
        const nextBtn = document.getElementById('booking-next-btn');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previousStep());
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextStep());
        }

        // Step-specific events
        this.bindStepEvents();
    }

    bindStepEvents() {
        // Date selection
        document.querySelectorAll('.date-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.date-option').forEach(b => b.style.background = 'rgba(255,255,255,0.1)');
                e.target.style.background = 'rgba(184,134,11,0.3)';
                this.bookingData.date = e.target.dataset.date;
            });
        });

        // Time selection
        document.querySelectorAll('.time-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.time-option').forEach(b => {
                    b.style.background = 'rgba(184,134,11,0.1)';
                    b.style.color = '#B8860B';
                });
                e.target.style.background = '#B8860B';
                e.target.style.color = '#000';
                this.bookingData.time = e.target.dataset.time;
            });
        });

        // Technician selection
        document.querySelectorAll('.technician-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.technician-option').forEach(b => b.style.background = 'rgba(255,255,255,0.05)');
                e.currentTarget.style.background = 'rgba(184,134,11,0.2)';
                this.bookingData.technician = e.currentTarget.dataset.technician;
            });
        });

        // Service selection
        document.querySelectorAll('.service-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.service-option').forEach(b => b.style.background = 'rgba(255,255,255,0.05)');
                e.currentTarget.style.background = 'rgba(184,134,11,0.2)';
                this.bookingData.service = e.currentTarget.dataset.service;
            });
        });

        // Addon selection
        document.querySelectorAll('input[name="addons"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                const checkedAddons = Array.from(document.querySelectorAll('input[name="addons"]:checked'))
                    .map(cb => cb.value);
                this.bookingData.addons = checkedAddons;
            });
        });
    }

    nextStep() {
        if (this.currentStep < this.maxSteps) {
            if (this.validateCurrentStep()) {
                this.currentStep++;
                this.render();
                this.bindEvents();
            } else {
                alert('Please make a selection before proceeding.');
            }
        } else {
            // Final booking submission
            this.submitBooking();
        }
    }

    previousStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.render();
            this.bindEvents();
        }
    }

    validateCurrentStep() {
        switch (this.currentStep) {
            case 1:
                return this.bookingData.date;
            case 2:
                return this.bookingData.time;
            case 3:
                return this.bookingData.technician;
            case 4:
                return this.bookingData.service;
            case 5:
                return true; // Add-ons are optional
            case 6:
                return true; // Confirmation step
            default:
                return false;
        }
    }

    submitBooking() {
        // Show loading state
        document.getElementById('booking-next-btn').textContent = 'BOOKING...';

        // Simulate API call
        setTimeout(() => {
            alert(`Booking confirmed! ${JSON.stringify(this.bookingData, null, 2)}`);
            // Reset calendar or redirect to confirmation page
            this.reset();
        }, 2000);
    }

    reset() {
        this.currentStep = 1;
        this.bookingData = {
            date: '',
            time: '',
            technician: '',
            service: '',
            addons: []
        };
        this.render();
        this.bindEvents();
    }
}

// Initialize booking calendar when DOM is ready (safe, no conflicts)
document.addEventListener('DOMContentLoaded', function () {
    // Only initialize if element exists (won't conflict with existing code)
    if (document.getElementById('membership-booking-calendar')) {
        // Show booking calendar section when needed
        window.showBookingCalendar = function () {
            const section = document.getElementById('membership-booking-calendar');
            if (section) {
                section.style.display = 'block';
                section.scrollIntoView({ behavior: 'smooth' });

                // Initialize calendar
                window.bookingCalendar = new CoreSyncBookingCalendar('membership-booking-calendar');
            }
        };
    }
});
