// ===================================
// NAVIGATION & UI INTERACTION
// ===================================

document.addEventListener('DOMContentLoaded', function () {
    const burgerMenu = document.getElementById('burger-menu');
    const navMenu = document.getElementById('nav-menu');
    const header = document.querySelector('.header');
    const footerBtn = document.querySelector('.footer-btn');
    const heroImage = document.querySelector('.hero-image');

    document.querySelectorAll('.service-btn').forEach(btn => btn.addEventListener('click', function () {
        this.style.transform = 'scale(0.98)';
        setTimeout(() => this.style.transform = 'scale(1)', 150);
    }));

    if (footerBtn) footerBtn.addEventListener('click', function () {
        this.style.transform = 'translateY(-2px) scale(1.02)';
        setTimeout(() => this.style.transform = 'translateY(-2px) scale(1)', 150);
    });

    if (heroImage) window.addEventListener('scroll', () => heroImage.style.transform = `translateY(${pageYOffset * -.5}px)`);

    document.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('click', function () {
            const link = this.getAttribute('data-link');
            if (link) window.location.href = link;
        });
    });

    // Burger menu toggle with smooth animation
    if (burgerMenu && navMenu) {
        burgerMenu.addEventListener('click', function () {
            const isActive = this.classList.contains('active');

            if (!isActive) {
                // Open menu with logo animation first
                this.classList.add('active');
                header.classList.add('menu-open');

                // Slight delay for logo animation to start first
                setTimeout(() => {
                    navMenu.classList.add('active');
                }, 200);
            } else {
                // Close menu immediately
                this.classList.remove('active');
                navMenu.classList.remove('active');
                header.classList.remove('menu-open');
            }
        });

        // Navigation button handlers with smooth transition
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const link = this.getAttribute('data-link');
                if (link) {
                    // Fade out menu
                    navMenu.style.opacity = '0';

                    // Close menu with animation
                    setTimeout(() => {
                        burgerMenu.classList.remove('active');
                        navMenu.classList.remove('active');
                        header.classList.remove('menu-open');
                        navMenu.style.opacity = '1';
                    }, 400);

                    // Navigate after animation
                    setTimeout(() => {
                        window.location.href = link;
                    }, 800);
                }
            });
        });
    }

    // iOS viewport height fix for dynamic vh units
    if (typeof CSS !== 'undefined' && CSS.supports('height', '100dvh')) {
        document.documentElement.style.setProperty('--vh', '1dvh');
    } else {
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
        this.selectedDates = [];  // Array for date range selection
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
                        <button id="check-availability-btn" class="check-btn">CHECK AVAILABILITY</button>
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
        today.setHours(0, 0, 0, 0);

        for (let i = 0; i < 42; i++) {
            const currentDate = new Date(startDate);
            currentDate.setDate(startDate.getDate() + i);

            const isCurrentMonth = currentDate.getMonth() === month;
            const dateStr = currentDate.toISOString().split('T')[0];
            const canBook = this.canUserBookDate(currentDate, userPrivileges);
            const isPriorityPeriod = this.isPriorityPeriod(currentDate);
            const isToday = currentDate.getTime() === today.getTime();
            const isSelected = this.selectedDates.includes(dateStr);

            let dayClass = 'calendar-day';
            if (!isCurrentMonth) dayClass += ' other-month';
            if (isToday) dayClass += ' today';
            if (canBook && isCurrentMonth) dayClass += ' available';
            if (!canBook && isCurrentMonth) dayClass += ' unavailable';
            if (isPriorityPeriod && !userPrivileges.canBookPrioritySlots) dayClass += ' member-only';
            if (isSelected) dayClass += ' selected';

            days.push(`
                <div class="${dayClass}" data-date="${dateStr}">
                    ${currentDate.getDate()}
                </div>
            `);
        }

        return days.join('');
    }

    renderProgressiveOptions() {
        // ВИПРАВЛЕНО: Показуємо повідомлення тільки якщо немає дати
        if (!this.bookingData.date) {
            return '<div class="no-selection">📅 Please select a date from the calendar to see available time slots</div>';
        }

        const options = [];

        // Step 1: Time slots (показується одразу після вибору дати)
        if (this.bookingData.date && !this.bookingData.time) {
            const availableSlots = this.getAvailableTimeSlots();
            options.push(`
                <div class="option-group progressive-option" data-step="1">
                    <label class="option-label">⏰ AVAILABLE TIME SLOTS</label>
                    <select id="time-slot" class="booking-dropdown">
                        <option value="">Select time</option>
                        ${availableSlots.map(slot => `<option value="${slot.value}">${slot.label}</option>`).join('')}
                    </select>
                    <p class="option-hint">Selected: ${this.formatDate(this.bookingData.date)}</p>
                </div>
            `);
        }

        // Step 2: Technician selection (after time selection)
        if (this.bookingData.date && this.bookingData.time && !this.bookingData.technician) {
            options.push(`
                <div class="option-group progressive-option" data-step="2">
                    <label class="option-label">👤 PREFERRED TECHNICIAN</label>
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
                    <label class="option-label">🕐 SESSION PREFERENCE</label>
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
                    <label class="option-label">💆 TYPE OF MASSAGE</label>
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
                                <option value="moderate">Moderate (71-73°F)</option>
                                <option value="warm">Warm (74-76°F)</option>
                            </select>
                        </div>
                        
                        <div class="option-group">
                            <label class="option-label">MUSIC PREFERENCE</label>
                            <select id="music" class="booking-dropdown">
                                <option value="">Select music</option>
                                <option value="nature">Nature Sounds</option>
                                <option value="classical">Classical Music</option>
                                <option value="ambient">Ambient/Meditation</option>
                                <option value="silence">Silence/No Music</option>
                            </select>
                        </div>
                        
                        <div class="option-group">
                            <label class="option-label">AROMATHERAPY</label>
                            <select id="aromatherapy" class="booking-dropdown">
                                <option value="">Select scent</option>
                                <option value="lavender">Lavender (Calming)</option>
                                <option value="eucalyptus">Eucalyptus (Refreshing)</option>
                                <option value="peppermint">Peppermint (Energizing)</option>
                                <option value="none">No Aromatherapy</option>
                            </select>
                        </div>
                    </div>
                </div>
            `);
        }

        return options.join('') || '<div class="no-selection">Complete selections to continue</div>';
    }

    // Генерація доступних слотів часу
    getAvailableTimeSlots() {
        const slots = [
            { value: '09:00', label: '9:00 AM - Morning Start' },
            { value: '10:00', label: '10:00 AM - Mid Morning' },
            { value: '11:00', label: '11:00 AM - Late Morning' },
            { value: '12:00', label: '12:00 PM - Noon' },
            { value: '13:00', label: '1:00 PM - Early Afternoon' },
            { value: '14:00', label: '2:00 PM - Afternoon' },
            { value: '15:00', label: '3:00 PM - Mid Afternoon' },
            { value: '16:00', label: '4:00 PM - Late Afternoon' },
            { value: '17:00', label: '5:00 PM - Early Evening' },
            { value: '18:00', label: '6:00 PM - Evening' },
        ];

        // TODO: В майбутньому можна додати API запит для перевірки доступності
        return slots;
    }

    // Форматування дати
    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    getUserPrivileges() {
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

    canUserBookDate(date, userPrivileges) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const targetDate = new Date(date);
        targetDate.setHours(0, 0, 0, 0);

        // Can't book past dates
        if (targetDate < today) {
            return false;
        }

        const daysInAdvance = Math.floor((targetDate - today) / (1000 * 60 * 60 * 24));

        // Check if within allowed booking window
        if (daysInAdvance > userPrivileges.maxAdvanceDays) {
            return false;
        }

        // Check priority access
        if (this.isPriorityPeriod(date) && !userPrivileges.canBookPrioritySlots) {
            return false;
        }

        return true;
    }

    isPriorityPeriod(date) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const targetDate = new Date(date);
        targetDate.setHours(0, 0, 0, 0);
        const daysInAdvance = Math.floor((targetDate - today) / (1000 * 60 * 60 * 24));

        // Priority period is 30+ days in advance
        return daysInAdvance >= 30;
    }

    bindEvents() {
        this.bindDateEvents();
        this.bindProgressiveDropdownEvents();

        const checkBtn = document.getElementById('check-availability-btn');
        if (checkBtn) {
            checkBtn.addEventListener('click', () => this.handleBookingSubmission());
        }
    }

    bindDateEvents() {
        // Calendar day selection with range support
        document.querySelectorAll('.calendar-day.available').forEach(day => {
            day.addEventListener('click', (e) => {
                const clickedDate = e.target.dataset.date;

                // If no dates selected or clicking same date, start fresh
                if (this.selectedDates.length === 0 || this.selectedDates.includes(clickedDate)) {
                    this.selectedDates = [clickedDate];
                    this.bookingData.date = clickedDate;
                }
                // If one date selected, create range
                else if (this.selectedDates.length === 1) {
                    const startDate = new Date(this.selectedDates[0]);
                    const endDate = new Date(clickedDate);

                    // Ensure start < end
                    if (startDate > endDate) {
                        [this.selectedDates[0], clickedDate] = [clickedDate, this.selectedDates[0]];
                    }

                    // Build range
                    this.selectedDates = this.getDateRange(this.selectedDates[0], clickedDate);
                    this.bookingData.date = this.selectedDates[0];  // Use first date as booking date
                }
                // If already a range, start over
                else {
                    this.selectedDates = [clickedDate];
                    this.bookingData.date = clickedDate;
                }

                // Update visual selection
                this.updateDateSelection();

                // Update progressive options
                this.updateProgressiveOptions();
            });
        });
    }

    getDateRange(start, end) {
        const dates = [];
        const startDate = new Date(start);
        const endDate = new Date(end);

        for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
            dates.push(new Date(d).toISOString().split('T')[0]);
        }

        return dates;
    }

    updateDateSelection() {
        // Remove all selection classes
        document.querySelectorAll('.calendar-day').forEach(day => {
            day.classList.remove('selected', 'in-range', 'range-start', 'range-end');
        });

        // Apply selection classes
        if (this.selectedDates.length > 0) {
            this.selectedDates.forEach((date, index) => {
                const dayElement = document.querySelector(`.calendar-day[data-date="${date}"]`);
                if (dayElement) {
                    if (this.selectedDates.length === 1) {
                        dayElement.classList.add('selected');
                    } else {
                        dayElement.classList.add('in-range');
                        if (index === 0) dayElement.classList.add('range-start');
                        if (index === this.selectedDates.length - 1) dayElement.classList.add('range-end');
                    }
                }
            });
        }
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
        this.bindProgressiveDropdown('music', 'servicePreferences.music');
        this.bindProgressiveDropdown('aromatherapy', 'servicePreferences.aromatherapy');
    }

    bindProgressiveDropdown(elementId, dataPath) {
        const element = document.getElementById(elementId);
        if (element) {
            element.addEventListener('change', (e) => {
                // Handle nested properties
                if (dataPath.includes('.')) {
                    const [parent, child] = dataPath.split('.');
                    this.bookingData[parent][child] = e.target.value;
                } else {
                    this.bookingData[dataPath] = e.target.value;
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
        if (!progressiveContainer) return;

        // Fade out
        progressiveContainer.style.opacity = '0.5';
        progressiveContainer.style.transform = 'translateY(-10px)';

        setTimeout(() => {
            progressiveContainer.innerHTML = this.renderProgressiveOptions();

            // Re-bind events for new elements
            this.bindProgressiveDropdownEvents();

            // Fade in
            progressiveContainer.style.opacity = '1';
            progressiveContainer.style.transform = 'translateY(0)';
        }, 300);
    }

    async handleBookingSubmission() {
        // Validate data
        if (!this.validateBookingData()) {
            return;
        }

        // Show loading state
        const checkBtn = document.getElementById('check-availability-btn');
        checkBtn.disabled = true;
        checkBtn.textContent = 'CHECKING...';

        try {
            // Prepare booking data
            const bookingPayload = {
                service_id: this.getServiceId(this.bookingData.service),
                date: this.bookingData.date,
                start_time: this.convertTo24Hour(this.bookingData.time),
                room_id: 1, // Will be determined by service type
                technician_preference: this.bookingData.technician,
                addons: this.bookingData.addons.map(addon => ({
                    addon_id: this.getAddonId(addon),
                    quantity: 1
                })),
                notes: this.generateSpecialRequests()
            };

            // Call API
            const response = await fetch('/api/bookings/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(bookingPayload)
            });

            const result = await response.json();

            if (response.ok) {
                // Show success
                this.showSuccessScreen(result);
            } else {
                // Show error
                this.showMessage(result.error || 'Booking failed. Please try again.', 'error');
                checkBtn.disabled = false;
                checkBtn.textContent = 'CHECK AVAILABILITY';
            }

        } catch (error) {
            console.error('Booking error:', error);
            this.showMessage('An error occurred. Please try again.', 'error');
            checkBtn.disabled = false;
            checkBtn.textContent = 'CHECK AVAILABILITY';
        }
    }

    showSuccessScreen(result) {
        this.container.innerHTML = `
            <div class="booking-success" style="background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px;
                        padding: 2rem; text-align: center; font-family: 'Maison_Neue_Book', sans-serif;">
                <h3 style="color: #00ff00; margin-bottom: 1rem;">Booking Confirmed!</h3>
                <p>Booking Reference: <strong>${result.booking_reference}</strong></p>
                <p>Date: ${result.date} at ${result.start_time}</p>
                <p>Total: $${result.pricing.final_total}</p>
                <div style="margin-top: 1.5rem;">
                    <button onclick="window.location.reload()" 
                        style="background: #F5F5DC; color: #000; border: none; padding: 1rem 2rem; 
                        border-radius: 4px; cursor: pointer; font-family: 'Maison_Neue_Bold', sans-serif;">
                        BOOK ANOTHER
                    </button>
                </div>
            </div>
        `;
    }

    showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `booking-message ${type}`;
        messageDiv.textContent = message;

        const container = document.querySelector('.booking-options-container');
        container.insertBefore(messageDiv, container.firstChild);

        setTimeout(() => {
            messageDiv.style.opacity = '0';
            setTimeout(() => messageDiv.remove(), 300);
        }, 5000);
    }

    getServiceId(serviceName) {
        const serviceMap = {
            'swedish': 1,
            'deep-tissue': 2,
            'hot-stone': 3,
            'ai-massage': 4,
            'couples': 5,
            'prenatal': 6
        };
        return serviceMap[serviceName] || 1;
    }

    getAddonId(addonName) {
        const addonMap = {
            'aromatherapy': 1,
            'hot-stone': 2,
            'deep-tissue': 3
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

    validateBookingData() {
        if (!this.bookingData.date) {
            this.showMessage('Please select a date', 'error');
            return false;
        }

        if (!this.bookingData.time) {
            this.showMessage('Please select a time slot', 'error');
            return false;
        }

        return true;
    }

    async submitBooking() {
        if (!this.validateBookingData()) {
            return;
        }

        try {
            const bookingPayload = {
                service_id: this.getServiceId(this.bookingData.massageType || 'swedish'),
                date: this.bookingData.date,
                start_time: this.bookingData.time,
                room_id: 1,
                technician_preference: this.bookingData.technician || 'any',
                special_requests: this.generateSpecialRequests(),
                traveling_persons: this.bookingData.travelingPersons || '1',
                children: this.bookingData.children || 'none'
            };

            const response = await fetch('/api/bookings/availability/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(bookingPayload)
            });

            const result = await response.json();

            if (result.available) {
                this.showSuccessMessage(result);
            } else {
                this.showMessage('Selected time slot is not available. Please choose another time.', 'error');
            }

        } catch (error) {
            console.error('Error:', error);
            this.showMessage('An error occurred. Please try again.', 'error');
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
            requests.push(`Session: ${this.bookingData.timePreference}`);
        }

        return requests.join('; ');
    }

    showSuccessMessage(data) {
        this.showMessage(`✓ Time slot available! Booking confirmed for ${data.date} at ${data.time}`, 'success');
    }
}

// Auto-initialize on page load if calendar container exists
document.addEventListener('DOMContentLoaded', () => {
    const calendarContainer = document.getElementById('booking-calendar-container');
    if (calendarContainer && typeof CoreSyncBookingCalendar !== 'undefined') {
        // Check if not already initialized
        if (!calendarContainer.querySelector('.progressive-booking-calendar')) {
            new CoreSyncBookingCalendar('booking-calendar-container');
        }
    }
});
