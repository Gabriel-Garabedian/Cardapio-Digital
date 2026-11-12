/* ═══════════════════════════════════════════════
   DA MASSA — script.js
   Navegação, formulários e mensagens
═══════════════════════════════════════════════ */

'use strict';

// ─── 1. DOM READY ─────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initFlashMessages();
  initPasswordStrength();
  initFormSubmitLoading();
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
        burger.setAttribute('aria-expanded', 'false');
      }
    });
  }
}

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
  btn.setAttribute('aria-label', isText ? 'Mostrar senha' : 'Ocultar senha');
  btn.style.opacity = isText ? '.5' : '.9';
}

// ─── 8. CATEGORY NAV (menu page) ──────────────
window.showCategory = function(slug, btn) {
  // Hide all
  document.querySelectorAll('.cat-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
  // Show target
  const target = document.getElementById('sec-' + slug);
  if (target) {
    target.classList.add('active');
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

// ─── 14. INPUT FOCUS HIGHLIGHT ────────────────
document.querySelectorAll('.form-input').forEach(input => {
  const wrap = input.closest('.input-wrap');
  if (!wrap) return;
  input.addEventListener('focus',  () => wrap.classList.add('focused'));
  input.addEventListener('blur',   () => wrap.classList.remove('focused'));
});

// ─── 17. KEYBOARD SHORTCUT: / to search ───────
document.addEventListener('keydown', e => {
  // Esc closes any open mobile nav
  if (e.key === 'Escape') {
    const links  = document.querySelector('.navbar-links');
    const burger = document.getElementById('navBurger');
    if (links && links.classList.contains('mobile-open')) {
      links.classList.remove('mobile-open');
      if (burger) {
        burger.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
      }
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
  toast.innerHTML = '<span></span><button class="flash-close" aria-label="Fechar aviso" onclick="this.parentElement.remove()">×</button>';
  toast.querySelector('span').textContent = msg;
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
