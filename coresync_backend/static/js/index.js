// Index page specific JavaScript functionality

// Add click handler for service cards
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('click', function () {
            const link = this.getAttribute('data-link');
            if (link) {
                window.location.href = link;
            }
        });
    });
});
