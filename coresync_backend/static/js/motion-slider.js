/**
 * Motion Slider Component JavaScript
 * Modern cursor-based slider with auto-progress and navigation
 * 
 * Features:
 * - Auto-rotation with configurable duration
 * - Cursor-based navigation with progress ring
 * - Touch/swipe support for mobile
 * - Keyboard navigation (arrows, Home, End)
 * - Dots navigation
 * - Fully accessible (ARIA labels, focus management)
 * 
 * @author CoreSync Development Team
 * @version 1.0.0
 */

(function () {
    'use strict';

    /**
     * Configuration constants
     * @const {number} AUTO_DURATION - Auto-rotation duration in ms
     * @const {number} PROGRESS_DURATION - Progress ring animation duration in ms
     * @const {number} SWIPE_THRESHOLD - Minimum swipe distance in pixels
     */
    const AUTO_DURATION = 5500;
    const PROGRESS_DURATION = 5500;
    const SWIPE_THRESHOLD = 50;

    /**
     * Motion Slider Class
     * @class
     */
    class MotionSlider {
        /**
         * Create a motion slider
         * @param {HTMLElement} element - The slider container element
         */
        constructor(element) {
            this.slider = element;
            this.slides = Array.from(element.querySelectorAll('.motion-slide'));
            this.dots = Array.from(element.querySelectorAll('.motion-dot'));
            this.mobileNavPrev = element.querySelector('.motion-mobile-nav.prev');
            this.mobileNavNext = element.querySelector('.motion-mobile-nav.next');

            // Create custom cursor
            this.customCursor = this.createCustomCursor();
            this.progressBar = this.customCursor.querySelector('.progress-bar');
            this.arrow = this.customCursor.querySelector('.cursor-arrow');

            this.currentIndex = 0;
            this.autoTimer = null;
            this.progressTimer = null;
            this.currentDirection = 1;
            this.isMouseInside = false;
            this.touchStartX = 0;
            this.touchEndX = 0;
            this.isMobile = window.innerWidth <= 768;

            this.init();
        }

        /**
         * Create custom cursor element
         * @returns {HTMLElement} - Custom cursor element
         */
        createCustomCursor() {
            const cursor = document.createElement('div');
            cursor.className = 'motion-custom-cursor';
            cursor.setAttribute('aria-hidden', 'true');
            cursor.innerHTML = `
                <div class="cursor-ring">
                    <svg viewBox="0 0 36 36">
                        <circle class="progress-bg" cx="18" cy="18" r="16"></circle>
                        <circle class="progress-bar" cx="18" cy="18" r="16"></circle>
                    </svg>
                    <span class="cursor-arrow"></span>
                </div>
            `;
            document.body.appendChild(cursor);
            return cursor;
        }

        /**
         * Initialize slider functionality
         */
        init() {
            this.setupAccessibility();
            this.attachEventListeners();
            this.startAutoRotation();
            this.preloadMedia();
        }

        /**
         * Setup ARIA labels and roles for accessibility
         */
        setupAccessibility() {
            this.slider.setAttribute('role', 'region');
            this.slider.setAttribute('aria-label', 'Image slider with amenities');
            this.slider.setAttribute('aria-live', 'polite');

            this.slides.forEach((slide, index) => {
                slide.setAttribute('role', 'group');
                slide.setAttribute('aria-roledescription', 'slide');
                slide.setAttribute('aria-label', `Slide ${index + 1} of ${this.slides.length}`);
            });

            this.dots.forEach((dot, index) => {
                dot.setAttribute('role', 'button');
                dot.setAttribute('aria-label', `Go to slide ${index + 1}`);
                dot.setAttribute('tabindex', '0');
            });

            if (this.progressRing) {
                this.progressRing.setAttribute('role', 'button');
                this.progressRing.setAttribute('aria-label', 'Navigate slider');
                this.progressRing.setAttribute('tabindex', '0');
            }

            if (this.mobileNavPrev) {
                this.mobileNavPrev.setAttribute('aria-label', 'Previous slide');
            }

            if (this.mobileNavNext) {
                this.mobileNavNext.setAttribute('aria-label', 'Next slide');
            }
        }

        /**
         * Attach all event listeners
         */
        attachEventListeners() {
            // Mouse events for cursor tracking (desktop only)
            if (!this.isMobile) {
                this.slider.addEventListener('mousemove', this.handleMouseMove.bind(this));
                this.slider.addEventListener('mouseenter', this.handleMouseEnter.bind(this));
                this.slider.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
                this.slider.addEventListener('click', this.handleSliderClick.bind(this));
            }

            // Touch events for mobile swipe
            this.slider.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
            this.slider.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });

            // Dots navigation
            this.dots.forEach((dot, index) => {
                dot.addEventListener('click', () => this.goToSlide(index));
                dot.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        this.goToSlide(index);
                    }
                });
            });

            // Mobile navigation buttons
            if (this.mobileNavPrev) {
                this.mobileNavPrev.addEventListener('click', () => this.navigate(-1));
            }

            if (this.mobileNavNext) {
                this.mobileNavNext.addEventListener('click', () => this.navigate(1));
            }

            // Keyboard navigation
            this.slider.addEventListener('keydown', this.handleKeyboard.bind(this));

            // Pause on focus for accessibility
            this.slider.addEventListener('focusin', this.stopAutoRotation.bind(this));
            this.slider.addEventListener('focusout', () => {
                if (!this.isMouseInside) {
                    this.startAutoRotation();
                }
            });
        }

        /**
         * Handle mouse movement for cursor tracking
         * @param {MouseEvent} e - Mouse event
         */
        handleMouseMove(e) {
            // Update cursor position
            this.customCursor.style.left = e.clientX + 'px';
            this.customCursor.style.top = e.clientY + 'px';

            // Determine direction based on mouse position
            const rect = this.slider.getBoundingClientRect();
            const halfWidth = rect.width / 2;
            const mouseX = e.clientX - rect.left;
            const isLeftSide = mouseX < halfWidth;

            // Set direction: left side = backward (-1), right side = forward (1)
            const newDirection = isLeftSide ? -1 : 1;

            // Update arrow direction
            if (this.arrow) {
                if (newDirection === -1) {
                    this.arrow.classList.add('left');
                } else {
                    this.arrow.classList.remove('left');
                }
            }

            // Restart progress if direction changed
            if (newDirection !== this.currentDirection) {
                this.currentDirection = newDirection;
                this.startProgressTimer();
            }
        }

        /**
         * Handle mouse enter event
         */
        handleMouseEnter() {
            this.isMouseInside = true;
            this.stopAutoRotation();

            // Show custom cursor (desktop only)
            if (!this.isMobile && this.customCursor) {
                this.customCursor.classList.add('visible');
            }

            this.startProgressTimer();
        }

        /**
         * Handle mouse leave event
         */
        handleMouseLeave() {
            this.isMouseInside = false;

            // Hide custom cursor
            if (this.customCursor) {
                this.customCursor.classList.remove('visible');
            }

            this.stopProgressTimer();
            this.startAutoRotation();
        }

        /**
         * Handle slider click
         */
        handleSliderClick() {
            this.navigate(this.currentDirection);
            // Restart progress timer immediately after click
            this.startProgressTimer();
        }

        /**
         * Handle touch start for swipe gestures
         * @param {TouchEvent} e - Touch event
         */
        handleTouchStart(e) {
            this.touchStartX = e.changedTouches[0].screenX;
        }

        /**
         * Handle touch end for swipe gestures
         * @param {TouchEvent} e - Touch event
         */
        handleTouchEnd(e) {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe();
        }

        /**
         * Process swipe gesture
         */
        handleSwipe() {
            const swipeDistance = this.touchStartX - this.touchEndX;

            if (Math.abs(swipeDistance) > SWIPE_THRESHOLD) {
                if (swipeDistance > 0) {
                    this.navigate(1); // Swipe left - next
                } else {
                    this.navigate(-1); // Swipe right - previous
                }
            }
        }

        /**
         * Handle keyboard navigation
         * @param {KeyboardEvent} e - Keyboard event
         */
        handleKeyboard(e) {
            switch (e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    this.navigate(-1);
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.navigate(1);
                    break;
                case 'Home':
                    e.preventDefault();
                    this.goToSlide(0);
                    break;
                case 'End':
                    e.preventDefault();
                    this.goToSlide(this.slides.length - 1);
                    break;
            }
        }

        /**
         * Navigate to next or previous slide
         * @param {number} direction - Direction to navigate (1 or -1)
         */
        navigate(direction) {
            const newIndex = (this.currentIndex + direction + this.slides.length) % this.slides.length;
            this.goToSlide(newIndex);
        }

        /**
         * Go to specific slide
         * @param {number} index - Target slide index
         */
        goToSlide(index) {
            if (index === this.currentIndex) return;

            // Remove active class from current slide and dot
            this.slides[this.currentIndex].classList.remove('active');
            this.dots[this.currentIndex].classList.remove('active');

            // Update index
            this.currentIndex = index;

            // Add active class to new slide and dot
            this.slides[this.currentIndex].classList.add('active');
            this.dots[this.currentIndex].classList.add('active');

            // Play video if current slide is video
            this.playCurrentVideo();

            // Restart auto-rotation
            this.startAutoRotation();
        }

        /**
         * Start auto-rotation timer
         */
        startAutoRotation() {
            this.stopAutoRotation();

            this.autoTimer = setTimeout(() => {
                this.navigate(1);
            }, AUTO_DURATION);
        }

        /**
         * Stop auto-rotation timer
         */
        stopAutoRotation() {
            if (this.autoTimer) {
                clearTimeout(this.autoTimer);
                this.autoTimer = null;
            }
        }

        /**
         * Start progress ring animation timer
         */
        startProgressTimer() {
            // Clear any existing timer first
            this.stopProgressTimer();

            if (!this.progressBar) return;

            // Force reset animation completely
            this.progressBar.classList.remove('animating');
            this.progressBar.style.animation = 'none';
            this.progressBar.style.strokeDasharray = '0 100';

            // Force reflow to ensure animation restart
            void this.progressBar.offsetWidth;

            // Use setTimeout to ensure clean state before starting
            setTimeout(() => {
                if (!this.isMouseInside) return; // Don't start if mouse left

                // Start CSS animation
                this.progressBar.style.animation = `progressFill ${PROGRESS_DURATION}ms linear forwards`;
                this.progressBar.classList.add('animating');

                // Set timer to navigate when progress completes
                this.progressTimer = setTimeout(() => {
                    if (this.isMouseInside) {
                        this.navigate(this.currentDirection);
                        // Restart progress timer after navigation
                        this.startProgressTimer();
                    }
                }, PROGRESS_DURATION);
            }, 50); // Small delay for clean restart
        }

        /**
         * Stop progress ring animation timer
         */
        stopProgressTimer() {
            if (this.progressTimer) {
                clearTimeout(this.progressTimer);
                this.progressTimer = null;
            }

            if (this.progressBar) {
                this.progressBar.classList.remove('animating');
                this.progressBar.style.animation = 'none';
                this.progressBar.style.strokeDasharray = '0 100';
            }
        }

        /**
         * Play video in current slide if exists
         */
        playCurrentVideo() {
            const currentSlide = this.slides[this.currentIndex];
            const video = currentSlide.querySelector('video');

            // Pause all videos first
            this.slides.forEach(slide => {
                const v = slide.querySelector('video');
                if (v) {
                    v.pause();
                    v.currentTime = 0;
                }
            });

            // Play current video
            if (video) {
                video.play().catch(err => {
                    console.warn('Video autoplay failed:', err);
                });
            }
        }

        /**
         * Preload media for smooth transitions
         */
        preloadMedia() {
            this.slides.forEach(slide => {
                const img = slide.querySelector('img');
                const video = slide.querySelector('video');

                if (img && !img.complete) {
                    const preloadImg = new Image();
                    preloadImg.src = img.src;
                }

                if (video) {
                    video.load();
                }
            });
        }

        /**
         * Destroy slider and clean up
         */
        destroy() {
            this.stopAutoRotation();
            this.stopProgressTimer();

            // Remove custom cursor
            if (this.customCursor && this.customCursor.parentNode) {
                this.customCursor.parentNode.removeChild(this.customCursor);
            }

            // Remove event listeners
            this.slider.removeEventListener('mousemove', this.handleMouseMove);
            this.slider.removeEventListener('mouseenter', this.handleMouseEnter);
            this.slider.removeEventListener('mouseleave', this.handleMouseLeave);
            this.slider.removeEventListener('click', this.handleSliderClick);
            this.slider.removeEventListener('touchstart', this.handleTouchStart);
            this.slider.removeEventListener('touchend', this.handleTouchEnd);
            this.slider.removeEventListener('keydown', this.handleKeyboard);
            this.slider.removeEventListener('focusin', this.stopAutoRotation);
            this.slider.removeEventListener('focusout', this.startAutoRotation);
        }
    }

    /**
     * Initialize all motion sliders on the page
     */
    function initMotionSliders() {
        const sliders = document.querySelectorAll('.motion-slider');

        sliders.forEach(slider => {
            new MotionSlider(slider);
        });
    }

    // Auto-initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMotionSliders);
    } else {
        initMotionSliders();
    }

    // Export for manual initialization if needed
    window.MotionSlider = MotionSlider;
    window.initMotionSliders = initMotionSliders;

})();

