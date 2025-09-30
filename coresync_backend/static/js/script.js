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

// Progressive Booking Calendar with Dropdown System
class CoreSyncBookingCalendar {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.bookingData = {
            date: '',
            time: '',
            technician: '',
            timePreference: '',
            massageType: '',
            servicePreferences: {
                pressure: '',
                temperature: '',
                music: '',
                aromatherapy: ''
            },
            addons: []
        };
        this.currentDropdown = 0;

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
            <div class="progressive-booking-calendar">
                <!-- Calendar Section -->
                <div class="calendar-section">
                    ${this.renderCalendar()}
                </div>
                
                <!-- Progressive Dropdown Section -->
                <div class="dropdown-section">
                    <div class="booking-options-container">
                        <!-- Always visible base dropdowns -->
                        <div class="base-options">
                            <div class="option-group">
                                <label class="option-label">TRAVELING PERSONS</label>
                                <select id="traveling-persons" class="booking-dropdown">
                                    <option value="">Select number of persons</option>
                                    <option value="1">1 Person</option>
                                    <option value="2">2 Persons</option>
                                    <option value="3">3 Persons</option>
                                    <option value="4">4+ Persons</option>
                                </select>
                            </div>
                            
                            <div class="option-group">
                                <label class="option-label">ACCOMPANYING CHILDREN</label>
                                <select id="accompanying-children" class="booking-dropdown">
                                    <option value="">Age of child</option>
                                    <option value="0-2">0-2 years</option>
                                    <option value="3-5">3-5 years</option>
                                    <option value="6-12">6-12 years</option>
                                    <option value="13-17">13-17 years</option>
                                </select>
                            </div>
                        </div>
                        
                        <!-- Progressive options container -->
                        <div id="progressive-options" class="progressive-options">
                            ${this.renderProgressiveOptions()}
                        </div>
                    </div>
                    
                    <div class="booking-actions">
                        <button id="check-availability-btn" class="check-btn">CHECK</button>
                    </div>
                </div>
            </div>
        `;
    }

    renderCalendar() {
        const today = new Date();
        const userPrivileges = this.getUserPrivileges();

        // Generate calendar grid for current and next month
        const currentMonth = this.generateMonthCalendar(today, userPrivileges);
        const nextMonth = this.generateMonthCalendar(new Date(today.getFullYear(), today.getMonth() + 1), userPrivileges);

        return `
            <div class="calendar-header">
                <h3 class="calendar-title">SELECT YOUR PREFERRED DATE</h3>
            </div>
            <div class="calendar-grid-container">
                <div class="month-calendar">
                    <div class="month-header">${today.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</div>
                    <div class="weekdays">
                        <div class="weekday">MON</div>
                        <div class="weekday">TUE</div>
                        <div class="weekday">WED</div>
                        <div class="weekday">THU</div>
                        <div class="weekday">FRI</div>
                        <div class="weekday">SAT</div>
                        <div class="weekday">SUN</div>
                    </div>
                    <div class="days-grid">
                        ${currentMonth}
                    </div>
                </div>
                
                <div class="month-calendar">
                    <div class="month-header">${new Date(today.getFullYear(), today.getMonth() + 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</div>
                    <div class="weekdays">
                        <div class="weekday">MON</div>
                        <div class="weekday">TUE</div>
                        <div class="weekday">WED</div>
                        <div class="weekday">THU</div>
                        <div class="weekday">FRI</div>
                        <div class="weekday">SAT</div>
                        <div class="weekday">SUN</div>
                    </div>
                    <div class="days-grid">
                        ${nextMonth}
                    </div>
                </div>
            </div>
        `;
    }

    generateMonthCalendar(date, userPrivileges) {
        const year = date.getFullYear();
        const month = date.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startDate = new Date(firstDay);

        // Get Monday of the week containing the first day
        const dayOfWeek = (firstDay.getDay() + 6) % 7; // Convert Sunday=0 to Monday=0
        startDate.setDate(firstDay.getDate() - dayOfWeek);

        const days = [];
        const today = new Date();

        // Generate 6 weeks (42 days)
        for (let i = 0; i < 42; i++) {
            const currentDate = new Date(startDate);
            currentDate.setDate(startDate.getDate() + i);

            const isCurrentMonth = currentDate.getMonth() === month;
            const isToday = currentDate.toDateString() === today.toDateString();
            const canBook = this.canBookDate(currentDate, userPrivileges);
            const isPriorityPeriod = this.isPriorityPeriod(currentDate);
            const isSelected = this.bookingData.date === currentDate.toISOString().split('T')[0];

            let dayClass = 'calendar-day';
            if (!isCurrentMonth) dayClass += ' other-month';
            if (isToday) dayClass += ' today';
            if (canBook && isCurrentMonth) dayClass += ' available';
            if (!canBook && isCurrentMonth) dayClass += ' unavailable';
            if (isPriorityPeriod && !userPrivileges.canBookPrioritySlots) dayClass += ' member-only';
            if (isSelected) dayClass += ' selected';

            days.push(`
                <div class="${dayClass}" 
                     data-date="${currentDate.toISOString().split('T')[0]}"
                     ${canBook && isCurrentMonth ? 'tabindex="0"' : ''}>
                    ${currentDate.getDate()}
                </div>
            `);
        }

        return days.join('');
    }

    renderProgressiveOptions() {
        if (!this.bookingData.date || !this.bookingData.time) {
            return '<div class="no-selection">Select date and time to see more options</div>';
        }

        const options = [];

        // Step 1: Time slots (after date selection)
        if (this.bookingData.date && !this.bookingData.time) {
            options.push(`
                <div class="option-group progressive-option" data-step="1">
                    <label class="option-label">AVAILABLE TIME SLOTS</label>
                    <select id="time-slot" class="booking-dropdown">
                        <option value="">Select time</option>
                        <option value="09:00">9:00 AM</option>
                        <option value="10:00">10:00 AM</option>
                        <option value="11:00">11:00 AM</option>
                        <option value="12:00">12:00 PM</option>
                        <option value="14:00">2:00 PM</option>
                        <option value="15:00">3:00 PM</option>
                        <option value="16:00">4:00 PM</option>
                        <option value="17:00">5:00 PM</option>
                    </select>
                </div>
            `);
        }

        // Step 2: Technician selection (after time selection)
        if (this.bookingData.date && this.bookingData.time && !this.bookingData.technician) {
            options.push(`
                <div class="option-group progressive-option" data-step="2">
                    <label class="option-label">PREFERRED TECHNICIAN</label>
                    <select id="technician-select" class="booking-dropdown">
                        <option value="">Choose your technician</option>
                        <option value="sarah">Sarah Johnson - Facial & Skincare Specialist</option>
                        <option value="michael">Michael Chen - Massage Therapy Expert</option>
                        <option value="emma">Emma Rodriguez - Laser Treatment Professional</option>
                        <option value="david">David Kim - AI Massage Bed Specialist</option>
                        <option value="any">Any Available Technician</option>
                    </select>
                </div>
            `);
        }

        // Step 3: Time preference (after technician selection)
        if (this.bookingData.technician && !this.bookingData.timePreference) {
            options.push(`
                <div class="option-group progressive-option" data-step="3">
                    <label class="option-label">TIME PREFERENCE</label>
                    <select id="time-preference" class="booking-dropdown">
                        <option value="">Select preference</option>
                        <option value="morning">Morning Session (Energizing)</option>
                        <option value="afternoon">Afternoon Session (Balanced)</option>
                        <option value="evening">Evening Session (Relaxing)</option>
                        <option value="flexible">Flexible Timing</option>
                    </select>
                </div>
            `);
        }

        // Step 4: Massage type (after time preference)
        if (this.bookingData.timePreference && !this.bookingData.massageType) {
            options.push(`
                <div class="option-group progressive-option" data-step="4">
                    <label class="option-label">TYPE OF MASSAGE</label>
                    <select id="massage-type" class="booking-dropdown">
                        <option value="">Choose massage type</option>
                        <option value="swedish">Swedish Massage - Classic Relaxation</option>
                        <option value="deep-tissue">Deep Tissue - Therapeutic</option>
                        <option value="hot-stone">Hot Stone - Ultimate Relaxation</option>
                        <option value="ai-massage">AI Massage Bed - High-Tech Experience</option>
                        <option value="couples">Couples Massage - Shared Experience</option>
                        <option value="prenatal">Prenatal Massage - Pregnancy Safe</option>
                    </select>
                </div>
            `);
        }

        // Step 5: Service preferences (after massage type)
        if (this.bookingData.massageType) {
            options.push(`
                <div class="service-preferences progressive-option" data-step="5">
                    <div class="preferences-grid">
                        <div class="option-group">
                            <label class="option-label">PRESSURE LEVEL</label>
                            <select id="pressure-level" class="booking-dropdown">
                                <option value="">Select pressure</option>
                                <option value="light">Light Pressure</option>
                                <option value="medium">Medium Pressure</option>
                                <option value="firm">Firm Pressure</option>
                                <option value="deep">Deep Pressure</option>
                            </select>
                        </div>
                        
                        <div class="option-group">
                            <label class="option-label">ROOM TEMPERATURE</label>
                            <select id="temperature" class="booking-dropdown">
                                <option value="">Select temperature</option>
                                <option value="cool">Cool (68-70°F)</option>
                                <option value="moderate">Moderate (72-74°F)</option>
                                <option value="warm">Warm (76-78°F)</option>
                            </select>
                        </div>
                        
                        <div class="option-group">
                            <label class="option-label">MUSIC PREFERENCE</label>
                            <select id="music-preference" class="booking-dropdown">
                                <option value="">Select music</option>
                                <option value="nature">Nature Sounds</option>
                                <option value="classical">Classical Music</option>
                                <option value="ambient">Ambient/Electronic</option>
                                <option value="meditation">Meditation Music</option>
                                <option value="silence">Peaceful Silence</option>
                            </select>
                        </div>
                        
                        <div class="option-group">
                            <label class="option-label">AROMATHERAPY</label>
                            <select id="aromatherapy" class="booking-dropdown">
                                <option value="">Select scent</option>
                                <option value="lavender">Lavender - Relaxation</option>
                                <option value="eucalyptus">Eucalyptus - Energizing</option>
                                <option value="peppermint">Peppermint - Refreshing</option>
                                <option value="chamomile">Chamomile - Soothing</option>
                                <option value="none">No Aromatherapy</option>
                            </select>
                        </div>
                    </div>
                </div>
            `);
        }

        return options.join('');
    }

    // This method is now integrated into renderCalendar() - removing to avoid duplication

    getUserPrivileges() {
        // In real app, this would come from server/auth
        // For demo, detect from URL params or localStorage
        const urlParams = new URLSearchParams(window.location.search);
        const membershipLevel = urlParams.get('membership') || localStorage.getItem('membershipLevel') || 'none';

        switch (membershipLevel) {
            case 'unlimited':
                return {
                    isMember: true,
                    isVip: true,
                    hasPriorityBooking: true,
                    canBookPrioritySlots: true,
                    maxAdvanceDays: 90
                };
            case 'premium':
                return {
                    isMember: true,
                    isVip: false,
                    hasPriorityBooking: true,
                    canBookPrioritySlots: true,
                    maxAdvanceDays: 60
                };
            case 'base':
                return {
                    isMember: true,
                    isVip: false,
                    hasPriorityBooking: false,
                    canBookPrioritySlots: false,
                    maxAdvanceDays: 30
                };
            default:
                return {
                    isMember: false,
                    isVip: false,
                    hasPriorityBooking: false,
                    canBookPrioritySlots: false,
                    maxAdvanceDays: 3
                };
        }
    }

    isPriorityPeriod(date) {
        // Priority period is anything more than 3 days ahead
        const today = new Date();
        const daysDiff = Math.ceil((date - today) / (1000 * 60 * 60 * 24));
        return daysDiff > 3;
    }

    canBookDate(date, userPrivileges) {
        const today = new Date();
        const daysDiff = Math.ceil((date - today) / (1000 * 60 * 60 * 24));

        // Check max advance days
        if (daysDiff > userPrivileges.maxAdvanceDays) {
            return false;
        }

        // Check priority access
        if (this.isPriorityPeriod(date) && !userPrivileges.canBookPrioritySlots) {
            return false;
        }

        return true;
    }

    // Old step rendering methods removed - now using progressive dropdown system

    bindEvents() {
        // Date selection events
        this.bindDateEvents();

        // Progressive dropdown events
        this.bindProgressiveDropdownEvents();

        // Check availability button
        const checkBtn = document.getElementById('check-availability-btn');
        if (checkBtn) {
            checkBtn.addEventListener('click', () => this.handleBookingSubmission());
        }
    }

    bindDateEvents() {
        // Calendar day selection
        document.querySelectorAll('.calendar-day.available').forEach(day => {
            day.addEventListener('click', (e) => {
                // Remove previous selection
                document.querySelectorAll('.calendar-day.selected').forEach(d =>
                    d.classList.remove('selected'));

                // Add selection to clicked day
                e.target.classList.add('selected');
                this.bookingData.date = e.target.dataset.date;

                // Update progressive options
                this.updateProgressiveOptions();
            });
        });
    }

    bindProgressiveDropdownEvents() {
        // Base dropdowns
        const travelingPersons = document.getElementById('traveling-persons');
        const children = document.getElementById('accompanying-children');

        if (travelingPersons) {
            travelingPersons.addEventListener('change', (e) => {
                this.bookingData.travelingPersons = e.target.value;
            });
        }

        if (children) {
            children.addEventListener('change', (e) => {
                this.bookingData.children = e.target.value;
            });
        }

        // Progressive dropdowns
        this.bindProgressiveDropdown('time-slot', 'time');
        this.bindProgressiveDropdown('technician-select', 'technician');
        this.bindProgressiveDropdown('time-preference', 'timePreference');
        this.bindProgressiveDropdown('massage-type', 'massageType');

        // Service preferences
        this.bindProgressiveDropdown('pressure-level', 'servicePreferences.pressure');
        this.bindProgressiveDropdown('temperature', 'servicePreferences.temperature');
        this.bindProgressiveDropdown('music-preference', 'servicePreferences.music');
        this.bindProgressiveDropdown('aromatherapy', 'servicePreferences.aromatherapy');
    }

    bindProgressiveDropdown(elementId, dataKey) {
        const element = document.getElementById(elementId);
        if (element) {
            element.addEventListener('change', (e) => {
                // Handle nested object keys like 'servicePreferences.pressure'
                if (dataKey.includes('.')) {
                    const [parent, child] = dataKey.split('.');
                    this.bookingData[parent][child] = e.target.value;
                } else {
                    this.bookingData[dataKey] = e.target.value;
                }

                // Add smooth animation
                e.target.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    e.target.style.transform = 'scale(1)';
                }, 200);

                // Update progressive options after selection
                setTimeout(() => {
                    this.updateProgressiveOptions();
                }, 300);
            });
        }
    }

    updateProgressiveOptions() {
        const progressiveContainer = document.getElementById('progressive-options');
        if (progressiveContainer) {
            // Add fade out animation
            progressiveContainer.style.opacity = '0.5';
            progressiveContainer.style.transform = 'translateY(-10px)';

            setTimeout(() => {
                progressiveContainer.innerHTML = this.renderProgressiveOptions();

                // Re-bind events for new elements
                this.bindProgressiveDropdownEvents();

                // Add fade in animation
                progressiveContainer.style.opacity = '1';
                progressiveContainer.style.transform = 'translateY(0)';
            }, 300);
        }
    }

    // Old step navigation methods removed - now using progressive dropdown system

    async submitBooking() {
        // Show loading state
        const nextBtn = document.getElementById('booking-next-btn');
        nextBtn.textContent = 'BOOKING...';
        nextBtn.disabled = true;

        try {
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            // Prepare booking data
            const bookingPayload = {
                service_id: this.getServiceId(this.bookingData.service),
                date: this.bookingData.date,
                start_time: this.convertTo24Hour(this.bookingData.time),
                room_id: 1, // Will be determined by service type
                technician_preference: this.bookingData.technician,
                addons: this.bookingData.addons.map(addon => ({
                    id: this.getAddonId(addon),
                    quantity: 1
                })),
                special_requests: '',
                scene_preferences: {}
            };

            // Make API call
            const response = await fetch('/api/bookings/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(bookingPayload)
            });

            const result = await response.json();

            if (response.ok) {
                // Success
                this.showSuccessMessage(result);
                this.reset();
            } else {
                // Error
                this.showErrorMessage(result.error || 'Booking failed');
            }
        } catch (error) {
            console.error('Booking error:', error);
            this.showErrorMessage('Network error. Please try again.');
        } finally {
            nextBtn.textContent = 'BOOK NOW';
            nextBtn.disabled = false;
        }
    }

    showSuccessMessage(result) {
        const message = `
            <div style="background: rgba(0,255,0,0.1); border: 1px solid #00ff00; color: #00ff00; 
                        padding: 2rem; text-align: center; font-family: 'Maison_Neue_Book', sans-serif;">
                <h3 style="color: #00ff00; margin-bottom: 1rem;">Booking Confirmed!</h3>
                <p>Booking Reference: <strong>${result.booking_reference}</strong></p>
                <p>Date: ${result.date} at ${result.start_time}</p>
                <p>Total: $${result.pricing.final_total}</p>
                <div style="margin-top: 1.5rem;">
                    <button onclick="window.location.reload()" 
                            style="background: #00ff00; color: #000; border: none; padding: 1rem 2rem; 
                                   font-family: 'Maison_Neue_Bold', sans-serif; cursor: pointer;">
                        BOOK ANOTHER SERVICE
                    </button>
                </div>
            </div>
        `;
        this.container.innerHTML = message;
    }

    showErrorMessage(error) {
        alert(`Booking failed: ${error}`);
    }

    getServiceId(serviceName) {
        // Map service names to IDs
        const serviceMap = {
            'AI Massage Therapy': 1,
            'Facial Treatment': 2,
            'Laser Hair Removal': 3,
            'Deep Tissue Massage': 4,
            'Relaxation Package': 5
        };
        return serviceMap[serviceName] || 1;
    }

    getAddonId(addonName) {
        // Map addon names to IDs
        const addonMap = {
            'LED Light Therapy': 1,
            'Aromatherapy': 2,
            'Hot Stone Add-on': 3,
            'Oxygen Treatment': 4
        };
        return addonMap[addonName] || 1;
    }

    convertTo24Hour(time12h) {
        const [time, modifier] = time12h.split(' ');
        let [hours, minutes] = time.split(':');
        if (hours === '12') hours = '00';
        if (modifier === 'PM') hours = parseInt(hours, 10) + 12;
        return `${hours}:${minutes || '00'}`;
    }

    async handleBookingSubmission() {
        // Validate required fields
        if (!this.bookingData.date) {
            this.showMessage('Please select a date', 'error');
            return;
        }

        if (!this.bookingData.time) {
            this.showMessage('Please select a time slot', 'error');
            return;
        }

        const checkBtn = document.getElementById('check-availability-btn');
        checkBtn.textContent = 'PROCESSING...';
        checkBtn.disabled = true;

        try {
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            // Prepare comprehensive booking data
            const bookingPayload = {
                service_id: this.getServiceId(this.bookingData.massageType || 'swedish'),
                date: this.bookingData.date,
                start_time: this.bookingData.time,
                room_id: 1,
                technician_preference: this.bookingData.technician || 'any',
                special_requests: this.generateSpecialRequests(),
                scene_preferences: this.bookingData.servicePreferences || {},
                addons: []
            };

            // Make API call
            const response = await fetch('/api/bookings/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(bookingPayload)
            });

            const result = await response.json();

            if (response.ok) {
                this.showBookingSuccess(result);
            } else {
                this.showMessage(result.error || 'Booking failed', 'error');
            }
        } catch (error) {
            console.error('Booking error:', error);
            this.showMessage('Network error. Please try again.', 'error');
        } finally {
            checkBtn.textContent = 'CHECK';
            checkBtn.disabled = false;
        }
    }

    generateSpecialRequests() {
        const requests = [];
        const prefs = this.bookingData.servicePreferences;

        if (prefs.pressure) requests.push(`Pressure: ${prefs.pressure}`);
        if (prefs.temperature) requests.push(`Temperature: ${prefs.temperature}`);
        if (prefs.music) requests.push(`Music: ${prefs.music}`);
        if (prefs.aromatherapy && prefs.aromatherapy !== 'none') {
            requests.push(`Aromatherapy: ${prefs.aromatherapy}`);
        }
        if (this.bookingData.timePreference) {
            requests.push(`Time preference: ${this.bookingData.timePreference}`);
        }

        return requests.join(', ');
    }

    showBookingSuccess(result) {
        const container = this.container;
        container.innerHTML = `
            <div class="booking-success">
                <div class="success-icon">✅</div>
                <h2 class="success-title">Booking Confirmed!</h2>
                <div class="success-details">
                    <p><strong>Booking Reference:</strong> ${result.booking_reference}</p>
                    <p><strong>Date:</strong> ${new Date(result.date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                    <p><strong>Time:</strong> ${result.start_time} - ${result.end_time}</p>
                    <p><strong>Service:</strong> ${result.service.name}</p>
                    <p><strong>Total:</strong> $${result.pricing.final_total}</p>
                </div>
                <div class="success-actions">
                    <button class="success-btn primary" onclick="window.location.reload()">
                        BOOK ANOTHER SERVICE
                    </button>
                    <button class="success-btn secondary" onclick="window.location.href='/'">
                        RETURN HOME
                    </button>
                </div>
            </div>
        `;
    }

    showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `booking-message ${type}`;
        messageDiv.textContent = message;

        this.container.prepend(messageDiv);

        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }

    getServiceId(serviceType) {
        const serviceMap = {
            'swedish': 1,
            'deep-tissue': 2,
            'hot-stone': 3,
            'ai-massage': 1,
            'couples': 4,
            'prenatal': 5
        };
        return serviceMap[serviceType] || 1;
    }

    reset() {
        this.currentDropdown = 0;
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

// Removed duplicate booking calendar initialization - use dedicated /book/ page
