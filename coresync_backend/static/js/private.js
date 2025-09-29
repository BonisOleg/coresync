// Private page specific JavaScript functionality

function alignPrivacyLines() {
    const privacyLines = document.querySelectorAll('.privacy-item-line');
    if (privacyLines.length >= 2) {
        // Спочатку скидаємо ширину другого рядка
        privacyLines[1].style.width = 'fit-content';

        // Отримуємо ширину першого рядка після можливих змін
        setTimeout(() => {
            const firstLineWidth = privacyLines[0].offsetWidth;
            // Застосовуємо цю ширину до другого рядка
            privacyLines[1].style.width = firstLineWidth + 'px';
        }, 10);
    }
}

// Amenities Carousel functionality
let currentSlide = 0;
const totalSlides = 5;

function updateCarousel() {
    const track = document.querySelector('.amenities-track');
    const itemWidth = document.querySelector('.amenity-item').offsetWidth;
    const gap = parseFloat(getComputedStyle(track).gap);
    const slideWidth = itemWidth + gap;

    // Calculate how many items are visible
    const containerWidth = document.querySelector('.amenities-container').offsetWidth;
    const visibleItems = Math.floor(containerWidth / slideWidth);

    // Adjust for responsive design
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

    // Update navigation buttons visibility
    const prevBtn = document.querySelector('.carousel-prev');
    const nextBtn = document.querySelector('.carousel-next');

    if (prevBtn && nextBtn) {
        prevBtn.style.opacity = currentSlide === 0 ? '0.5' : '1';
        prevBtn.style.pointerEvents = currentSlide === 0 ? 'none' : 'auto';

        nextBtn.style.opacity = currentSlide >= maxSlide ? '0.5' : '1';
        nextBtn.style.pointerEvents = currentSlide >= maxSlide ? 'none' : 'auto';
    }
}

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

// Initialize private page functionality
document.addEventListener('DOMContentLoaded', function () {
    alignPrivacyLines();
    updateCarousel();

    // Add touch event listeners for mobile swipe
    const carouselContainer = document.querySelector('.amenities-container');
    if (carouselContainer) {
        carouselContainer.addEventListener('touchstart', handleTouchStart, { passive: true });
        carouselContainer.addEventListener('touchend', handleTouchEnd, { passive: true });
    }
});

// Handle window resize
window.addEventListener('resize', function () {
    alignPrivacyLines();
    updateCarousel();
});

// Export functions for global access (if needed for inline onclick handlers)
window.moveCarousel = moveCarousel;
