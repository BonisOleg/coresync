/**
 * CoreSync Membership Page Functionality
 * Handles: membership forms, AI widget, WhatsApp integration
 */

// ===================================
// MEMBERSHIP FORM FUNCTIONALITY
// ===================================

function openMembershipForm(planType) {
    const modal = document.getElementById('membership-modal');
    const modalTitle = document.getElementById('modal-title');
    const selectedPlan = document.getElementById('selected-plan');

    // Set plan details
    const planTitles = {
        'base': 'JOIN BASE TIER - $375/month',
        'premium': 'JOIN PREMIUM TIER - $700/month',
        'unlimited': 'JOIN UNLIMITED TIER - $1,650/month'
    };

    modalTitle.textContent = planTitles[planType] || 'JOIN MEMBERSHIP';
    selectedPlan.value = planType;

    modal.style.display = 'block';

    // Prevent body scroll
    document.body.style.overflow = 'hidden';
}

function closeMembershipForm() {
    const modal = document.getElementById('membership-modal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// ===================================
// AI ASSISTANT WIDGET
// ===================================

let aiWidgetVisible = false;

function toggleAIWidget() {
    const widget = document.getElementById('ai-assistant-widget');
    const toggle = document.querySelector('.ai-widget-toggle');

    aiWidgetVisible = !aiWidgetVisible;

    if (aiWidgetVisible) {
        widget.style.display = 'block';
        toggle.style.display = 'none';
    } else {
        widget.style.display = 'none';
        toggle.style.display = 'flex';
    }
}

function sendAIMessage() {
    const input = document.getElementById('ai-input');
    const messages = document.getElementById('ai-messages');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    const userMessage = document.createElement('div');
    userMessage.className = 'ai-message ai-message--user';
    userMessage.innerHTML = `<div class="ai-message-content">${message}</div>`;
    messages.appendChild(userMessage);

    // Clear input
    input.value = '';

    // Simulate AI thinking
    const thinkingMessage = document.createElement('div');
    thinkingMessage.className = 'ai-message ai-message--bot';
    thinkingMessage.innerHTML = `<div class="ai-message-content">Thinking...</div>`;
    messages.appendChild(thinkingMessage);

    // Scroll to bottom
    messages.scrollTop = messages.scrollHeight;

    // Simulate AI response
    setTimeout(() => {
        messages.removeChild(thinkingMessage);

        const response = getAIResponse(message);
        const botMessage = document.createElement('div');
        botMessage.className = 'ai-message ai-message--bot';
        botMessage.innerHTML = `<div class="ai-message-content">${response}</div>`;
        messages.appendChild(botMessage);

        // Show WhatsApp fallback if needed
        if (response.includes('contact our team')) {
            document.getElementById('ai-fallback').classList.remove('d-none');
        }

        messages.scrollTop = messages.scrollHeight;
    }, 1500);
}

function getAIResponse(message) {
    const lowerMessage = message.toLowerCase();

    // Membership questions
    if (lowerMessage.includes('membership') || lowerMessage.includes('plan') || lowerMessage.includes('price')) {
        return `Great question about membership! We have 3 plans:<br><br>
                • <strong>Base Tier ($375/month)</strong>: 25% off all services<br>
                • <strong>Premium Tier ($700/month)</strong>: Free services included<br>
                • <strong>Unlimited ($1,650/month)</strong>: Everything unlimited<br><br>
                Members get priority booking 2-3 months ahead vs 3 days for non-members.`;
    }

    // Service questions
    if (lowerMessage.includes('service') || lowerMessage.includes('massage') || lowerMessage.includes('facial')) {
        return `We offer two main experiences:<br><br>
                • <strong>Mensuite</strong>: Advanced men's spa with AI massage beds<br>
                • <strong>Coresync Private</strong>: Luxury couple's spa with hot tub<br><br>
                Popular services: AI Massage ($200), Precision Facial ($180), Couple's Experience ($400).`;
    }

    // Booking questions
    if (lowerMessage.includes('book') || lowerMessage.includes('appointment') || lowerMessage.includes('schedule')) {
        return `To book your service:<br><br>
                1. Choose your date & time<br>
                2. Select preferred technician<br>
                3. Pick your service type<br>
                4. Add any enhancements<br>
                5. Confirm booking<br><br>
                Members get priority access to better time slots!`;
    }

    // Location/contact questions
    if (lowerMessage.includes('location') || lowerMessage.includes('address') || lowerMessage.includes('contact')) {
        return `We're located at:<br><br>
                <strong>1544 71st Street, Brooklyn, NY 11228</strong><br>
                <strong>551.574.2281</strong><br>
                <strong>info@coresync.life</strong><br><br>
                Hours: 9 AM - 9 PM daily`;
    }

    // Technology questions
    if (lowerMessage.includes('technology') || lowerMessage.includes('ai') || lowerMessage.includes('iot')) {
        return `Our cutting-edge technology includes:<br><br>
                AI Massage Beds with personalized programs<br>
                Smart Mirror with analysis<br>
                IoT scent and lighting control<br>
                Meditation pods with guided sessions<br><br>
                Everything controlled through our mobile app`;
    }

    // Default response with fallback
    return `I'd be happy to help, but I need more specific information. For immediate assistance, please contact our team directly.`;
}

function openWhatsApp() {
    const phone = '+13478995612';
    const message = 'Hi! I need help with CoreSync services and membership.';
    const url = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
    window.open(url, '_blank');
}

// ===================================
// EVENT LISTENERS
// ===================================

document.addEventListener('DOMContentLoaded', function () {
    // Membership form submit
    const membershipForm = document.getElementById('membership-form');
    if (membershipForm) {
        membershipForm.addEventListener('submit', function (e) {
            e.preventDefault();

            // Get form data
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);

            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'PROCESSING...';
            submitBtn.disabled = true;

            // Simulate API call (replace with actual API endpoint)
            setTimeout(() => {
                alert(`Thank you for your interest in ${data.plan.toUpperCase()} membership! We'll contact you soon.`);
                closeMembershipForm();
                this.reset();

                // Reset button
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }

    // Close modal when clicking outside
    window.addEventListener('click', function (event) {
        const modal = document.getElementById('membership-modal');
        if (event.target === modal) {
            closeMembershipForm();
        }
    });

    // AI Widget - Enter key support
    const aiInput = document.getElementById('ai-input');
    if (aiInput) {
        aiInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendAIMessage();
            }
        });
    }

    // Membership form buttons (data-action)
    document.querySelectorAll('[data-action="open-membership"]').forEach(btn => {
        btn.addEventListener('click', function () {
            const plan = this.dataset.plan;
            openMembershipForm(plan);
        });
    });

    // AI Widget toggle (data-action)
    document.querySelectorAll('[data-action="toggle-ai"]').forEach(btn => {
        btn.addEventListener('click', toggleAIWidget);
    });

    // Modal close (data-action)
    document.querySelectorAll('[data-action="close-modal"]').forEach(btn => {
        btn.addEventListener('click', closeMembershipForm);
    });

    // AI send button (data-action)
    document.querySelectorAll('[data-action="send-ai"]').forEach(btn => {
        btn.addEventListener('click', sendAIMessage);
    });

    // WhatsApp button (data-action)
    document.querySelectorAll('[data-action="open-whatsapp"]').forEach(btn => {
        btn.addEventListener('click', openWhatsApp);
    });
});

// Export functions for global access (backwards compatibility)
window.openMembershipForm = openMembershipForm;
window.closeMembershipForm = closeMembershipForm;
window.toggleAIWidget = toggleAIWidget;
window.sendAIMessage = sendAIMessage;
window.openWhatsApp = openWhatsApp;

