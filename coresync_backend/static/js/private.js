// Private page specific JavaScript functionality

/**
 * Align privacy item lines for consistent visual appearance
 * Matches the width of the second line to the first line
 */
function alignPrivacyLines() {
    const privacyLines = document.querySelectorAll('.privacy-item-line');
    if (privacyLines.length >= 2) {
        // Reset width of second line first
        privacyLines[1].style.width = 'fit-content';

        // Get width of first line after possible changes
        setTimeout(() => {
            const firstLineWidth = privacyLines[0].offsetWidth;
            // Apply this width to second line
            privacyLines[1].style.width = firstLineWidth + 'px';
        }, 10);
    }
}

// Initialize private page functionality
document.addEventListener('DOMContentLoaded', function () {
    alignPrivacyLines();
});

// Handle window resize
window.addEventListener('resize', function () {
    alignPrivacyLines();
});

