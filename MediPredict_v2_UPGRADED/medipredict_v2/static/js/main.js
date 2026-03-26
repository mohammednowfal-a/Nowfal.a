// ─── Theme Toggle ────────────────────────────────────────────
function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    html.setAttribute('data-theme', isDark ? 'light' : 'dark');
    document.getElementById('themeToggle').textContent = isDark ? '☀️' : '🌙';
    localStorage.setItem('medipredict_theme', isDark ? 'light' : 'dark');
}

// ─── Language Toggle ─────────────────────────────────────────
function toggleLang() {
    const html = document.documentElement;
    const isEn = html.getAttribute('data-lang') === 'en';
    const newLang = isEn ? 'hi' : 'en';
    html.setAttribute('data-lang', newLang);
    document.getElementById('langToggle').textContent = isEn ? '🇮🇳' : '🌐';
    localStorage.setItem('medipredict_lang', newLang);
    applyLanguage(newLang);
}

function applyLanguage(lang) {
    document.querySelectorAll('[data-en]').forEach(el => {
        const text = el.getAttribute(`data-${lang}`);
        if (text) {
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') el.placeholder = text;
            else el.textContent = text;
        }
    });
}

// ─── Mobile Nav ──────────────────────────────────────────────
function toggleMobileNav() {
    document.getElementById('navLinks').classList.toggle('open');
}

// Close mobile nav when clicking outside
document.addEventListener('click', (e) => {
    const nav = document.getElementById('navLinks');
    const hamburger = document.querySelector('.hamburger');
    if (nav && !nav.contains(e.target) && hamburger && !hamburger.contains(e.target)) {
        nav.classList.remove('open');
    }
});

// ─── Loading Screen ──────────────────────────────────────────
function showLoading() {
    const loader = document.getElementById('loaderScreen');
    if (loader) {
        loader.style.display = 'flex';
        setTimeout(() => { loader.style.opacity = '0'; setTimeout(() => loader.style.display = 'none', 400); }, 8000);
    }
}

// Hide loader on page load
window.addEventListener('load', () => {
    const loader = document.getElementById('loaderScreen');
    if (loader) {
        setTimeout(() => {
            loader.style.transition = 'opacity 0.5s';
            loader.style.opacity = '0';
            setTimeout(() => loader.style.display = 'none', 500);
        }, 800);
    }
});

// ─── Scroll Reveal ───────────────────────────────────────────
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1 });

// ─── Animate Count Up ────────────────────────────────────────
function animateCounters() {
    document.querySelectorAll('.stat-num').forEach(el => {
        const text = el.textContent;
        const num = parseInt(text.replace(/\D/g, ''));
        const suffix = text.replace(/[0-9]/g, '');
        if (!num) return;
        let start = 0;
        const step = Math.ceil(num / 60);
        const timer = setInterval(() => {
            start += step;
            if (start >= num) { el.textContent = num + suffix; clearInterval(timer); }
            else el.textContent = start + suffix;
        }, 20);
    });
}

// ─── Animate Result Bars ─────────────────────────────────────
function animateBars() {
    document.querySelectorAll('.match-bar-fill').forEach(bar => {
        const w = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => { bar.style.transition = 'width 1.2s ease'; bar.style.width = w; }, 300);
    });
}

// ─── Bottom Nav Active State ──────────────────────────────────
function setActiveBottomNav() {
    const path = window.location.pathname;
    document.querySelectorAll('.bottom-nav-item').forEach(item => {
        const href = item.getAttribute('href');
        if (href && path === href) item.style.color = 'var(--primary)';
    });
}

// ─── Init ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Restore theme
    const savedTheme = localStorage.getItem('medipredict_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) themeBtn.textContent = savedTheme === 'dark' ? '🌙' : '☀️';

    // Restore language
    const savedLang = localStorage.getItem('medipredict_lang') || 'en';
    document.documentElement.setAttribute('data-lang', savedLang);
    const langBtn = document.getElementById('langToggle');
    if (langBtn) langBtn.textContent = savedLang === 'en' ? '🌐' : '🇮🇳';
    if (savedLang === 'hi') applyLanguage('hi');

    // Animations
    animateCounters();
    animateBars();
    setActiveBottomNav();

    // Scroll reveal
    document.querySelectorAll('.feature-card, .result-card, .about-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });

    // Auto dismiss flash messages
    setTimeout(() => {
        document.querySelectorAll('.flash').forEach(f => {
            f.style.transition = 'opacity 0.5s';
            f.style.opacity = '0';
            setTimeout(() => f.remove(), 500);
        });
    }, 4000);
});
