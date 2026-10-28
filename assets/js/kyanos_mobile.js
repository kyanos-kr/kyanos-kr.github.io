/**
 * KYANOS SOVEREIGN REALM - MOBILE & PWA CONTROLLER
 * 모바일 반응형 내비게이션 드로어, 바텀 바, 서비스 워커 등록
 */

(function () {
  'use strict';

  // 1. Register PWA Service Worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./sw.js')
        .then((reg) => {
          // Service worker registered silently
        })
        .catch((err) => {
          console.warn('[Kyanos PWA] Registration notice:', err);
        });
    });
  }

  // 2. Initialize Mobile UI Controls on DOM Ready
  document.addEventListener('DOMContentLoaded', () => {
    initMobileDrawer();
    initBottomNav();
  });

  function initMobileDrawer() {
    const toggleBtn = document.getElementById('mobileMenuBtn');
    const drawer = document.getElementById('mobileDrawer');
    const overlay = document.getElementById('mobileDrawerOverlay');
    const closeBtn = document.getElementById('mobileDrawerClose');

    if (!toggleBtn || !drawer || !overlay) return;

    function openDrawer() {
      drawer.classList.add('active');
      overlay.classList.add('active');
      document.body.style.overflow = 'hidden'; // Prevent background scroll
    }

    function closeDrawer() {
      drawer.classList.remove('active');
      overlay.classList.remove('active');
      document.body.style.overflow = '';
    }

    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      openDrawer();
    });

    if (closeBtn) {
      closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeDrawer();
      });
    }

    overlay.addEventListener('click', closeDrawer);

    // Close when clicking any nav link inside drawer
    const drawerLinks = drawer.querySelectorAll('.drawer-nav-item a');
    drawerLinks.forEach((link) => {
      link.addEventListener('click', () => {
        closeDrawer();
      });
    });

    // ESC key support
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && drawer.classList.contains('active')) {
        closeDrawer();
      }
    });
  }

  function initBottomNav() {
    const navItems = document.querySelectorAll('.bottom-nav-item');
    if (!navItems.length) return;

    navItems.forEach((btn) => {
      btn.addEventListener('click', function (e) {
        const action = this.getAttribute('data-action');
        if (action === 'menu') {
          e.preventDefault();
          const toggleBtn = document.getElementById('mobileMenuBtn');
          if (toggleBtn) toggleBtn.click();
        } else if (action === 'top') {
          e.preventDefault();
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
      });
    });
  }
})();
