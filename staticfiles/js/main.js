/**
 * PackAndGo - Main JavaScript
 * Animations, interactions, and dynamic features
 */

// ─────────────────────────────────────────────
// LOADING ANIMATION
// ─────────────────────────────────────────────
window.addEventListener('load', () => {
    const loader = document.getElementById('page-loader');
    if (loader) {
        setTimeout(() => {
            loader.style.opacity = '0';
            setTimeout(() => loader.remove(), 500);
        }, 800);
    }
});

// ─────────────────────────────────────────────
// COUNTER ANIMATION
// ─────────────────────────────────────────────
function animateCounter(el) {
    const target = parseInt(el.getAttribute('data-target'));
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;

    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        el.textContent = Math.floor(current).toLocaleString();
    }, 16);
}

// Trigger counters when visible
const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateCounter(entry.target);
            counterObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('[data-target]').forEach(el => counterObserver.observe(el));

// ─────────────────────────────────────────────
// SCROLL ANIMATIONS
// ─────────────────────────────────────────────
const scrollObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate__animated', 'animate__fadeInUp');
            entry.target.style.opacity = '1';
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.scroll-animate').forEach(el => {
    el.style.opacity = '0';
    scrollObserver.observe(el);
});

// ─────────────────────────────────────────────
// PRICE CALCULATOR
// ─────────────────────────────────────────────
const vehicleSelect = document.getElementById('id_vehicle_type');
const distanceInput = document.getElementById('id_distance_km');
const priceDisplay = document.getElementById('price-display');

function updatePrice() {
    const vehicle = vehicleSelect ? vehicleSelect.value : '';
    const distance = distanceInput ? distanceInput.value : 0;

    if (!vehicle || !distance) return;

    fetch(`/api/calculate-price/?vehicle_type=${vehicle}&distance=${distance}`)
        .then(res => res.json())
        .then(data => {
            if (priceDisplay) {
                priceDisplay.textContent = `₹${data.price.toLocaleString()}`;
                priceDisplay.classList.add('price-updated');
                setTimeout(() => priceDisplay.classList.remove('price-updated'), 500);
            }
        })
        .catch(err => console.error('Price calculation error:', err));
}

if (vehicleSelect) vehicleSelect.addEventListener('change', updatePrice);
if (distanceInput) distanceInput.addEventListener('input', updatePrice);

// ─────────────────────────────────────────────
// VEHICLE CARD SELECTION
// ─────────────────────────────────────────────
document.querySelectorAll('.vehicle-card').forEach(card => {
    card.addEventListener('click', () => {
        document.querySelectorAll('.vehicle-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        const vehicleType = card.getAttribute('data-vehicle');
        if (vehicleSelect) {
            vehicleSelect.value = vehicleType;
            vehicleSelect.dispatchEvent(new Event('change'));
        }
    });
});

// ─────────────────────────────────────────────
// SIDEBAR TOGGLE (Mobile)
// ─────────────────────────────────────────────
const sidebarToggle = document.getElementById('sidebar-toggle');
const sidebar = document.getElementById('sidebar');

if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });

    // Close sidebar when clicking outside
    document.addEventListener('click', (e) => {
        if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });
}

// ─────────────────────────────────────────────
// STAR RATING
// ─────────────────────────────────────────────
document.querySelectorAll('.star-rating').forEach(container => {
    const stars = container.querySelectorAll('.star');
    const input = container.querySelector('input[type="hidden"]');

    stars.forEach((star, index) => {
        star.addEventListener('mouseover', () => {
            stars.forEach((s, i) => {
                s.classList.toggle('active', i <= index);
            });
        });

        star.addEventListener('click', () => {
            if (input) input.value = index + 1;
            stars.forEach((s, i) => {
                s.classList.toggle('selected', i <= index);
            });
        });
    });

    container.addEventListener('mouseleave', () => {
        const selected = parseInt(input ? input.value : 0);
        stars.forEach((s, i) => {
            s.classList.toggle('active', i < selected);
        });
    });
});

// ─────────────────────────────────────────────
// NOTIFICATIONS
// ─────────────────────────────────────────────
const notifBell = document.getElementById('notif-bell');
if (notifBell) {
    notifBell.addEventListener('click', () => {
        fetch('/notifications/read/', {
            method: 'GET',
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        }).then(() => {
            const badge = document.getElementById('notif-badge');
            if (badge) badge.style.display = 'none';
        });
    });
}

// ─────────────────────────────────────────────
// CSRF COOKIE HELPER
// ─────────────────────────────────────────────
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ─────────────────────────────────────────────
// AUTO-DISMISS ALERTS
// ─────────────────────────────────────────────
setTimeout(() => {
    document.querySelectorAll('.alert-auto-dismiss').forEach(alert => {
        alert.style.transition = 'opacity 0.5s ease';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
    });
}, 4000);

// ─────────────────────────────────────────────
// TOOLTIP INIT
// ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(el => new bootstrap.Tooltip(el));
});

// ─────────────────────────────────────────────
// SMOOTH SCROLL
// ─────────────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ─────────────────────────────────────────────
// FORM VALIDATION FEEDBACK
// ─────────────────────────────────────────────
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function (e) {
        const btn = form.querySelector('[type="submit"]');
        if (btn && form.checkValidity()) {
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            btn.disabled = true;
        }
    });
});
