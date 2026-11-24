/**
 * ============================================================================
 * KYANOS ⇋ ERYTHROS — DYNAMIC MODE / PULSE ENGINE (CLIENT CONTROLLER)
 * 단일 플랫폼 내 실시간 상태·모드 전환 엔진 (Lean, Zero-Dependency)
 * - localStorage 영속화 및 다중 탭 실시간 동기화
 * - GPU 가속 Pulse Ripple & 상태 토스트
 * - 전역 CustomEvent ('kyanos:themechange') 발행 (2D 파티클 & 3D 퓨전 배경 연동)
 * - 키보드 단축키: Alt + E
 * ============================================================================
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'kyanos_theme_mode';
  var VALID_MODES = { kyanos: true, erythros: true };
  var THEME_COLORS = {
    kyanos: '#19223c',
    erythros: '#14070d'
  };

  var toastTimer = null;
  var transitionTimer = null;

  function readStoredMode() {
    try {
      var val = localStorage.getItem(STORAGE_KEY);
      if (val && VALID_MODES[val]) return val;
    } catch (e) {}
    return 'kyanos';
  }

  function writeStoredMode(mode) {
    try {
      localStorage.setItem(STORAGE_KEY, mode);
    } catch (e) {}
  }

  function updateThemeColorMeta(mode) {
    var meta = document.querySelector('meta[name="theme-color"]');
    if (!meta) return;
    meta.setAttribute('content', THEME_COLORS[mode] || THEME_COLORS.kyanos);
  }

  function triggerRipple(mode, originEvent) {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }
    var ripple = document.createElement('div');
    ripple.className = 'kyanos-pulse-ripple ' + (mode === 'erythros' ? 'to-erythros' : 'to-kyanos');

    var x = 90;
    var y = window.innerHeight - 44;
    if (originEvent && typeof originEvent.clientX === 'number' && (originEvent.clientX || originEvent.clientY)) {
      x = originEvent.clientX;
      y = originEvent.clientY;
    }
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    document.body.appendChild(ripple);
    setTimeout(function () {
      if (ripple.parentNode) ripple.parentNode.removeChild(ripple);
    }, 720);
  }

  function showToast(mode) {
    var toast = document.getElementById('kyanos-pulse-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'kyanos-pulse-toast';
      toast.className = 'kyanos-pulse-toast';
      toast.setAttribute('role', 'status');
      toast.setAttribute('aria-live', 'polite');
      document.body.appendChild(toast);
    }

    if (mode === 'erythros') {
      toast.className = 'kyanos-pulse-toast mode-erythros';
      toast.innerHTML =
        '<strong>ERYTHROS PULSE ACTIVE</strong>' +
        '태양의 결단과 역동적 실행 모드로 전환되었습니다.';
    } else {
      toast.className = 'kyanos-pulse-toast mode-kyanos';
      toast.innerHTML =
        '<strong>KYANOS MODE ACTIVE</strong>' +
        '심해의 지성과 헌정 질서 모드로 복귀하였습니다.';
    }

    // Force reflow for smooth re-trigger
    void toast.offsetWidth;
    toast.classList.add('visible');

    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toast.classList.remove('visible');
    }, 2600);
  }

  function syncControls(mode) {
    var buttons = document.querySelectorAll('.kyanos-pulse-btn[data-mode]');
    for (var i = 0; i < buttons.length; i++) {
      var btn = buttons[i];
      var isCurrent = btn.getAttribute('data-mode') === mode;
      btn.setAttribute('aria-pressed', isCurrent ? 'true' : 'false');
    }

    var drawerBtn = document.getElementById('drawerPulseToggleBtn');
    var drawerDesc = document.getElementById('drawerPulseDesc');
    if (drawerBtn) {
      drawerBtn.textContent = mode === 'erythros' ? '🔴 ERYTHROS' : '🔵 KYANOS';
      drawerBtn.setAttribute('aria-pressed', mode === 'erythros' ? 'true' : 'false');
    }
    if (drawerDesc) {
      drawerDesc.textContent = mode === 'erythros'
        ? '역동적 실행 · 펄스 활성 중'
        : '심해의 지성 · 헌정 질서 모드';
    }
  }

  function dispatchChange(mode, source) {
    try {
      window.dispatchEvent(new CustomEvent('kyanos:themechange', {
        detail: { mode: mode, source: source || 'api' }
      }));
    } catch (e) {}
  }

  function applyMode(mode, options) {
    var opts = options || {};
    var normalized = VALID_MODES[mode] ? mode : 'kyanos';
    var root = document.documentElement;
    var previous = root.getAttribute('data-theme') === 'erythros' ? 'erythros' : 'kyanos';

    if (opts.animate && previous !== normalized) {
      root.classList.add('kyanos-theme-transitioning');
      if (transitionTimer) clearTimeout(transitionTimer);
      transitionTimer = setTimeout(function () {
        root.classList.remove('kyanos-theme-transitioning');
      }, 620);
    }

    if (normalized === 'erythros') {
      root.setAttribute('data-theme', 'erythros');
    } else {
      root.removeAttribute('data-theme');
    }

    updateThemeColorMeta(normalized);
    if (opts.persist !== false) {
      writeStoredMode(normalized);
    }

    syncControls(normalized);

    if (opts.animate && previous !== normalized) {
      triggerRipple(normalized, opts.originEvent);
      showToast(normalized);
    }

    dispatchChange(normalized, opts.source || 'user');
    return normalized;
  }

  function injectFloatingDock() {
    if (document.getElementById('kyanos-pulse-dock')) return;

    var dock = document.createElement('div');
    dock.id = 'kyanos-pulse-dock';
    dock.className = 'kyanos-pulse-dock notranslate';
    dock.setAttribute('translate', 'no');
    dock.setAttribute('role', 'group');
    dock.setAttribute('aria-label', 'Kyanos Erythros Dynamic Mode Switcher');
    dock.title = '키아노스 ⇋ 에리트로스 상태 전환 (단축키: Alt + E)';

    dock.innerHTML =
      '<button type="button" class="kyanos-pulse-btn" data-mode="kyanos" aria-pressed="true" aria-label="Kyanos 지성 모드">' +
        '<span class="kyanos-pulse-dot" aria-hidden="true"></span>' +
        '<span>KYANOS</span>' +
      '</button>' +
      '<button type="button" class="kyanos-pulse-btn" data-mode="erythros" aria-pressed="false" aria-label="Erythros 실행 펄스 모드">' +
        '<span class="kyanos-pulse-dot" aria-hidden="true"></span>' +
        '<span>ERYTHROS</span>' +
      '</button>';

    dock.addEventListener('click', function (e) {
      var target = e.target.closest('.kyanos-pulse-btn[data-mode]');
      if (!target) return;
      var nextMode = target.getAttribute('data-mode');
      var currentMode = KyanosPulse.getMode();
      // Clicking the already active button gently toggles to the other mode for effortless single-click switching
      if (nextMode === currentMode) {
        nextMode = currentMode === 'kyanos' ? 'erythros' : 'kyanos';
      }
      applyMode(nextMode, { animate: true, persist: true, originEvent: e, source: 'dock' });
    });

    document.body.appendChild(dock);
  }

  function bindMobileDrawerTile() {
    var drawerContent = document.querySelector('#mobileDrawer .drawer-content');
    if (!drawerContent || document.getElementById('drawerPulseCard')) return;

    var card = document.createElement('div');
    card.id = 'drawerPulseCard';
    card.className = 'drawer-pulse-card';
    card.innerHTML =
      '<div class="drawer-pulse-meta">' +
        '<span class="drawer-pulse-title">Dynamic Mode / Pulse</span>' +
        '<span class="drawer-pulse-desc" id="drawerPulseDesc">심해의 지성 · 헌정 질서 모드</span>' +
      '</div>' +
      '<button type="button" class="drawer-pulse-toggle notranslate" translate="no" id="drawerPulseToggleBtn" aria-pressed="false">🔵 KYANOS</button>';

    drawerContent.insertBefore(card, drawerContent.firstChild);

    var toggleBtn = document.getElementById('drawerPulseToggleBtn');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', function (e) {
        KyanosPulse.toggle(e);
      });
    }
  }

  var KyanosPulse = {
    getMode: function () {
      return document.documentElement.getAttribute('data-theme') === 'erythros' ? 'erythros' : 'kyanos';
    },
    setMode: function (mode, originEvent) {
      return applyMode(mode, { animate: true, persist: true, originEvent: originEvent, source: 'api' });
    },
    toggle: function (originEvent) {
      var next = this.getMode() === 'kyanos' ? 'erythros' : 'kyanos';
      return applyMode(next, { animate: true, persist: true, originEvent: originEvent, source: 'toggle' });
    },
    onChange: function (callback) {
      if (typeof callback !== 'function') return;
      window.addEventListener('kyanos:themechange', function (e) {
        callback(e.detail.mode, e.detail);
      });
    }
  };

  window.KyanosPulse = KyanosPulse;

  function init() {
    injectFloatingDock();
    bindMobileDrawerTile();

    var initialMode = readStoredMode();
    applyMode(initialMode, { animate: false, persist: false, source: 'init' });

    // Cross-tab real-time synchronization
    window.addEventListener('storage', function (e) {
      if (e.key === STORAGE_KEY) {
        var syncedMode = VALID_MODES[e.newValue] ? e.newValue : 'kyanos';
        applyMode(syncedMode, { animate: true, persist: false, source: 'storage' });
      }
    });

    // Keyboard shortcut: Alt + E
    window.addEventListener('keydown', function (e) {
      if (e.altKey && !e.ctrlKey && !e.metaKey && (e.key === 'e' || e.key === 'E')) {
        var activeTag = (document.activeElement && document.activeElement.tagName) || '';
        if (activeTag === 'INPUT' || activeTag === 'TEXTAREA') return;
        e.preventDefault();
        KyanosPulse.toggle();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
