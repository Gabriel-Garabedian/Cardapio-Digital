/* ═══════════════════════════════════════════════
   DA MASSA — script.js
   Animations, interactions and UX magic
═══════════════════════════════════════════════ */

'use strict';

// ─── 1. DOM READY ─────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initAOS();
  initParticles();
  initFlashMessages();
  initPasswordStrength();
  initPasswordToggle();
  initCategoryNav();
  initFormSubmitLoading();
  initRipple();
  initSauceTags();
});

// ─── 2. NAVBAR ────────────────────────────────
function initNavbar() {
  const navbar  = document.getElementById('navbar');
  const burger  = document.getElementById('navBurger');
  const links   = document.querySelector('.navbar-links');
  if (!navbar) return;

  // Scroll shadow
  const onScroll = () => navbar.classList.toggle('scrolled', window.scrollY > 10);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile burger
  if (burger && links) {
    burger.addEventListener('click', () => {
      const open = links.classList.toggle('mobile-open');
      burger.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', open);
    });
    // Close on outside click
    document.addEventListener('click', e => {
      if (!navbar.contains(e.target)) {
        links.classList.remove('mobile-open');
        burger.classList.remove('open');
      }
    });
  }
}

// ─── 3. AOS (Animate on Scroll) ───────────────
function initAOS() {
  const elements = document.querySelectorAll('[data-aos]');
  if (!elements.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el    = entry.target;
        const delay = parseInt(el.dataset.delay || 0);
        setTimeout(() => el.classList.add('aos-animate'), delay);
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

  elements.forEach(el => observer.observe(el));
}

// ─── 4. PARTICLES (auth page only) ────────────
function initParticles() {
  const container = document.getElementById('particles');
  if (!container) return;

  const COUNT  = 22;
  const frag   = document.createDocumentFragment();
  const shapes = ['✦', '·', '◦', '✧', '⊹'];

  for (let i = 0; i < COUNT; i++) {
    const span = document.createElement('span');
    const size = Math.random() * 14 + 6;
    span.textContent = shapes[Math.floor(Math.random() * shapes.length)];
    Object.assign(span.style, {
      position:  'absolute',
      left:      Math.random() * 100 + '%',
      top:       Math.random() * 100 + '%',
      fontSize:  size + 'px',
      color:     `rgba(201,168,76,${Math.random() * .18 + .04})`,
      animation: `drift ${Math.random() * 14 + 10}s ${Math.random() * 6}s ease-in-out infinite alternate`,
      pointerEvents: 'none',
      userSelect: 'none',
    });
    frag.appendChild(span);
  }
  container.appendChild(frag);

  // Inject drift keyframes once
  if (!document.getElementById('driftStyle')) {
    const style = document.createElement('style');
    style.id = 'driftStyle';
    style.textContent = `
      @keyframes drift {
        0%   { transform: translate(0,0) rotate(0deg); opacity:.15; }
        50%  { opacity:.35; }
        100% { transform: translate(${rand(-40,40)}px, ${rand(-50,50)}px) rotate(${rand(-30,30)}deg); opacity:.1; }
      }`;
    document.head.appendChild(style);
  }
}
const rand = (a, b) => Math.floor(Math.random() * (b - a + 1)) + a;

// ─── 5. FLASH MESSAGES ────────────────────────
function initFlashMessages() {
  const flashes = document.querySelectorAll('[data-flash]');
  flashes.forEach((el, i) => {
    // Staggered entrance
    el.style.animationDelay = `${i * 120}ms`;
    // Auto dismiss after 4.5s
    setTimeout(() => dismissFlash(el), 4500 + i * 200);
  });
}

function dismissFlash(el) {
  el.style.transition = 'opacity .35s, transform .35s';
  el.style.opacity    = '0';
  el.style.transform  = 'translateX(60px)';
  setTimeout(() => el.remove(), 380);
}

// ─── 6. PASSWORD STRENGTH ─────────────────────
function initPasswordStrength() {
  const pwInput  = document.getElementById('regPassword');
  const fill     = document.getElementById('strengthFill');
  const label    = document.getElementById('strengthLabel');
  if (!pwInput || !fill || !label) return;

  pwInput.addEventListener('input', () => {
    const val   = pwInput.value;
    const score = getStrengthScore(val);
    const pct   = [0, 25, 50, 75, 100][score];
    const colors = ['', '#e74c3c', '#e67e22', '#3498db', '#2ecc71'];
    const labels = ['', 'Fraca', 'Regular', 'Boa', 'Forte'];
    fill.style.width      = pct + '%';
    fill.style.background = colors[score] || 'transparent';
    label.textContent     = labels[score] || '';
    label.style.color     = colors[score] || 'transparent';
  });
}

function getStrengthScore(pw) {
  if (!pw) return 0;
  let score = 0;
  if (pw.length >= 6)  score++;
  if (pw.length >= 10) score++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
  if (/[0-9]/.test(pw) && /[^A-Za-z0-9]/.test(pw)) score++;
  return Math.min(score, 4);
}

// ─── 7. PASSWORD TOGGLE ───────────────────────
function togglePassword(btn) {
  const input = btn.closest('.input-wrap').querySelector('input');
  if (!input) return;
  const isText = input.type === 'text';
  input.type   = isText ? 'password' : 'text';
  // Swap icon
  btn.style.opacity = isText ? '.5' : '.9';
}

// ─── 8. CATEGORY NAV (menu page) ──────────────
function initCategoryNav() {
  // Handled by inline showCategory(), but we can also track scroll
  const sections = document.querySelectorAll('.cat-section');
  if (!sections.length) return;

  // Scroll-spy via IntersectionObserver is tricky here because sections are hidden.
  // Category switching is driven by showCategory() directly.
}

window.showCategory = function(slug, btn) {
  // Hide all
  document.querySelectorAll('.cat-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
  // Show target
  const target = document.getElementById('sec-' + slug);
  if (target) {
    target.classList.add('active');
    // Re-run AOS for newly visible items
    target.querySelectorAll('[data-aos]:not(.aos-animate)').forEach((el, i) => {
      const delay = parseInt(el.dataset.delay || i * 60);
      setTimeout(() => el.classList.add('aos-animate'), delay);
    });
  }
  if (btn) btn.classList.add('active');

  // Scroll cat btn into view (horizontal)
  if (btn) btn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
};

// ─── 9. FORM LOADING STATE ────────────────────
function initFormSubmitLoading() {
  const form   = document.getElementById('loginForm');
  const btnTxt = document.querySelector('.btn-text');
  const btnLdr = document.querySelector('.btn-loader');
  if (!form || !btnTxt || !btnLdr) return;

  form.addEventListener('submit', () => {
    btnTxt.classList.add('hidden');
    btnLdr.classList.remove('hidden');
  });
}

// ─── 10. RIPPLE EFFECT ────────────────────────
function initRipple() {
  document.querySelectorAll('.btn-submit, .btn-add-primary, .cat-btn, .auth-tab').forEach(addRipple);
}

function addRipple(el) {
  el.style.position = el.style.position || 'relative';
  el.style.overflow = 'hidden';
  el.addEventListener('click', e => {
    const rect   = el.getBoundingClientRect();
    const size   = Math.max(rect.width, rect.height) * 2;
    const ripple = document.createElement('span');
    Object.assign(ripple.style, {
      position:   'absolute',
      width:      size + 'px',
      height:     size + 'px',
      left:       e.clientX - rect.left - size / 2 + 'px',
      top:        e.clientY - rect.top  - size / 2 + 'px',
      borderRadius: '50%',
      background: 'rgba(255,255,255,.25)',
      pointerEvents: 'none',
      transform:  'scale(0)',
      animation:  'ripple .55s ease-out forwards',
    });
    el.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  });
}

// Inject ripple keyframes
(function() {
  if (document.getElementById('rippleStyle')) return;
  const s = document.createElement('style');
  s.id = 'rippleStyle';
  s.textContent = '@keyframes ripple { to { transform: scale(1); opacity: 0; } }';
  document.head.appendChild(s);
})();

// ─── 11. SAUCE TAGS interactive ───────────────
function initSauceTags() {
  document.querySelectorAll('.sauce-tag').forEach(tag => {
    tag.addEventListener('click', () => {
      // Visual "selected" bounce
      tag.style.transform = 'scale(.93)';
      setTimeout(() => (tag.style.transform = ''), 150);
    });
  });
}

// ─── 12. CHEF ROW HOVER GLOW ──────────────────
document.querySelectorAll('.chef-row').forEach(row => {
  row.addEventListener('mouseenter', () => {
    row.style.transition = 'background .15s, box-shadow .15s';
  });
});

// ─── 13. CARD STAGGER on load ─────────────────
(function staggerCards() {
  const cards = document.querySelectorAll('.menu-card, .stat-card, .chef-section-card');
  cards.forEach((c, i) => {
    if (!c.dataset.delay) c.dataset.delay = String(i * 55);
  });
})();

// ─── 14. INPUT FOCUS HIGHLIGHT ────────────────
document.querySelectorAll('.form-input').forEach(input => {
  const wrap = input.closest('.input-wrap');
  if (!wrap) return;
  input.addEventListener('focus',  () => wrap.classList.add('focused'));
  input.addEventListener('blur',   () => wrap.classList.remove('focused'));
});

// ─── 15. CHEF STATS counter animation ─────────
(function animateCounters() {
  const nums = document.querySelectorAll('.stat-number');
  if (!nums.length) return;
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el  = entry.target;
      const raw = el.textContent.trim();
      const num = parseInt(raw.replace(/\D/g,''));
      if (isNaN(num) || num === 0) return;
      const prefix = raw.startsWith('R$') ? 'R$' : '';
      let start = 0;
      const step = Math.ceil(num / 30);
      const timer = setInterval(() => {
        start = Math.min(start + step, num);
        el.textContent = prefix + start;
        if (start >= num) clearInterval(timer);
      }, 28);
      observer.unobserve(el);
    });
  }, { threshold: .5 });
  nums.forEach(n => observer.observe(n));
})();

// ─── 16. SMOOTH MODAL OPEN (backdrop) ─────────
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.style.transition = 'opacity .2s';
  const origOpen = MutationObserver;
});

// ─── 17. KEYBOARD SHORTCUT: / to search ───────
document.addEventListener('keydown', e => {
  // Esc closes any open mobile nav
  if (e.key === 'Escape') {
    const links  = document.querySelector('.navbar-links');
    const burger = document.getElementById('navBurger');
    if (links && links.classList.contains('mobile-open')) {
      links.classList.remove('mobile-open');
      burger && burger.classList.remove('open');
    }
  }
});

// ─── 18. TOAST helper (used by chef.html inline JS) ───
window.showToast = function(msg, type = 'success') {
  const existing = document.querySelector('.js-toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = `flash flash-${type} js-toast`;
  toast.style.cssText = 'position:fixed;bottom:28px;right:24px;z-index:9999;min-width:240px;';
  toast.innerHTML = `<span>${msg}</span><button class="flash-close" onclick="this.parentElement.remove()">×</button>`;
  document.body.appendChild(toast);
  setTimeout(() => dismissFlash(toast), 3500);
};

// ─── 19. INPUT WRAP focused style ─────────────
(function injectFocusStyle() {
  if (document.getElementById('focusStyle')) return;
  const s = document.createElement('style');
  s.id = 'focusStyle';
  s.textContent = `.input-wrap.focused { outline: none; }
    .input-wrap.focused .input-icon { color: var(--gold) !important; transition: color .2s; }
    .btn-loader.hidden, .btn-text.hidden { display:none !important; }`;
  document.head.appendChild(s);
})();

// ─── 20. MENU CARD click subtle feedback ──────
document.querySelectorAll('.menu-card').forEach(card => {
  card.addEventListener('click', () => {
    card.style.transform = 'scale(.987)';
    setTimeout(() => (card.style.transform = ''), 160);
  });
});
