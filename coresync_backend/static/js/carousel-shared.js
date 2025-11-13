/**
 * CoreSync Shared Carousel Functionality
 * Used across: membership.html
 * 
 * Provides touch-enabled carousel navigation with responsive design
 */

let currentSlide = 0;
const totalSlides = 5;

/**
 * Update carousel position and button states
 */
function updateCarousel() {
    const track = document.querySelector('.amenities-track');
    const amenityItems = document.querySelectorAll('.amenity-item');

    if (!track || amenityItems.length === 0) return;

    const itemWidth = amenityItems[0].offsetWidth;
    const gap = parseFloat(getComputedStyle(track).gap) || 20;
    const slideWidth = itemWidth + gap;

    // Calculate items to show based on screen size
    let itemsToShow = 4; // Desktop default
    if (window.innerWidth <= 480) {
        itemsToShow = 1;
    } else if (window.innerWidth <= 768) {
        itemsToShow = 2;
    }

    const maxSlide = Math.max(0, totalSlides - itemsToShow);
    currentSlide = Math.min(currentSlide, maxSlide);

    const translateX = -currentSlide * slideWidth;
    track.style.transform = `translateX(${translateX}px)`;

    // Update navigation buttons state
    const prevBtn = document.querySelector('.carousel-prev');
    const nextBtn = document.querySelector('.carousel-next');

    if (prevBtn && nextBtn) {
        prevBtn.style.opacity = currentSlide === 0 ? '0.5' : '1';
        prevBtn.style.pointerEvents = currentSlide === 0 ? 'none' : 'auto';

        nextBtn.style.opacity = currentSlide >= maxSlide ? '0.5' : '1';
        nextBtn.style.pointerEvents = currentSlide >= maxSlide ? 'none' : 'auto';
    }
}

/**
 * Move carousel in specified direction
 * @param {number} direction - -1 for previous, 1 for next
 */
function moveCarousel(direction) {
    const itemsToShow = window.innerWidth <= 480 ? 1 : window.innerWidth <= 768 ? 2 : 4;
    const maxSlide = Math.max(0, totalSlides - itemsToShow);

    currentSlide += direction;
    currentSlide = Math.max(0, Math.min(currentSlide, maxSlide));

    updateCarousel();
}

// Touch/swipe support for mobile
let touchStartX = 0;
let touchEndX = 0;

function handleTouchStart(e) {
    touchStartX = e.changedTouches[0].screenX;
}

function handleTouchEnd(e) {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}

function handleSwipe() {
    const swipeThreshold = 50;
    const swipeDistance = touchStartX - touchEndX;

    if (Math.abs(swipeDistance) > swipeThreshold) {
        if (swipeDistance > 0) {
            // Swipe left - next slide
            moveCarousel(1);
        } else {
            // Swipe right - previous slide
            moveCarousel(-1);
        }
    }
}

/**
 * Initialize carousel functionality
 * Should be called on DOMContentLoaded
 */
function initCarousel() {
    // Initial setup
    setTimeout(() => {
        updateCarousel();
    }, 100);

    // Add touch event listeners for mobile swipe
    const carouselContainer = document.querySelector('.amenities-container');
    if (carouselContainer) {
        carouselContainer.addEventListener('touchstart', handleTouchStart, { passive: true });
        carouselContainer.addEventListener('touchend', handleTouchEnd, { passive: true });
    }

    // Add click listeners to carousel navigation buttons
    document.querySelectorAll('[data-carousel-nav]').forEach(btn => {
        btn.addEventListener('click', function () {
            const direction = parseInt(this.dataset.carouselNav);
            moveCarousel(direction);
        });
    });
}

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', initCarousel);

// Handle window resize
window.addEventListener('resize', updateCarousel);

// Export for global access (backwards compatibility with onclick)
window.moveCarousel = moveCarousel;
window.updateCarousel = updateCarousel;

