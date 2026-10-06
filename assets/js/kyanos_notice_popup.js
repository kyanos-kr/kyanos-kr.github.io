/**
 * 키아노스 우측 상단 슬림 플로팅 공지 위젯
 * Kyanos Top-Right Floating Notice Widget Script
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'kyanos_hide_top_notice';
  const EXPIRE_HOURS = 24;

  // 1. 표시 여부 판별 (24시간 숨김 체크)
  function shouldShowNotice() {
    try {
      const hideUntil = localStorage.getItem(STORAGE_KEY);
      if (!hideUntil) return true;
      const now = new Date().getTime();
      return now > parseInt(hideUntil, 10);
    } catch (e) {
      return true;
    }
  }

  // 2. CSS 링크 보장
  function ensureCSS() {
    const existing = document.querySelector('link[href*="kyanos_notice_popup.css"]');
    if (!existing) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'assets/css/kyanos_notice_popup.css';
      document.head.appendChild(link);
    }
  }

  // 3. 위젯 렌더링
  function createTopNoticeWidget() {
    if (!shouldShowNotice()) return;

    ensureCSS();

    const widget = document.createElement('aside');
    widget.className = 'kyanos-top-notice-widget';
    widget.id = 'kyanosTopNoticeWidget';
    widget.setAttribute('aria-label', '키아노스 시스템 개편 안내');

    widget.innerHTML = `
      <div class="kyanos-top-notice-bar"></div>
      <div class="kyanos-top-notice-head">
        <div class="kyanos-top-notice-title-group">
          <span class="kyanos-top-notice-icon">⚙️</span>
          <h3 class="kyanos-top-notice-title">시스템 개편 점검 안내</h3>
        </div>
        <button type="button" class="kyanos-top-notice-close-x" id="kyanosTopNoticeCloseX" title="닫기" aria-label="닫기">✕</button>
      </div>

      <div class="kyanos-top-notice-body">
        <p class="kyanos-top-notice-text">
          현재 키아노스 포털은 <strong>시스템 전면 개편 및 DB 인프라 고도화</strong> 작업이 상시 진행 중입니다. 일부 서비스의 이용 변동이 있을 수 있습니다.
        </p>
        <div class="kyanos-top-notice-chips">
          <div class="kyanos-top-notice-chip">
            <span class="chip-dot">✦</span>
            <span><strong>진행:</strong> 각 부처 시스템 개편 & 최적화</span>
          </div>
          <div class="kyanos-top-notice-chip">
            <span class="chip-dot">✦</span>
            <span><strong>안내:</strong> 메뉴 및 기능 순차적 정상화</span>
          </div>
        </div>
      </div>

      <div class="kyanos-top-notice-foot">
        <label class="kyanos-top-notice-check">
          <input type="checkbox" id="kyanosTopNoticeHideCheck">
          <span>오늘 하루 보지 않기</span>
        </label>
        <button type="button" class="kyanos-top-notice-confirm-btn" id="kyanosTopNoticeConfirmBtn">닫기</button>
      </div>
    `;

    document.body.appendChild(widget);

    // Fade-in animation
    requestAnimationFrame(() => {
      setTimeout(() => {
        widget.classList.add('active');
      }, 80);
    });

    // 닫기 로직
    const closeX = widget.querySelector('#kyanosTopNoticeCloseX');
    const confirmBtn = widget.querySelector('#kyanosTopNoticeConfirmBtn');
    const hideCheck = widget.querySelector('#kyanosTopNoticeHideCheck');

    function closeWidget() {
      if (hideCheck && hideCheck.checked) {
        try {
          const expireTime = new Date().getTime() + (EXPIRE_HOURS * 60 * 60 * 1000);
          localStorage.setItem(STORAGE_KEY, expireTime.toString());
        } catch (e) {
          console.warn('LocalStorage access restricted:', e);
        }
      }

      widget.classList.remove('active');
      setTimeout(() => {
        widget.remove();
      }, 350);
    }

    if (closeX) closeX.addEventListener('click', closeWidget);
    if (confirmBtn) confirmBtn.addEventListener('click', closeWidget);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createTopNoticeWidget);
  } else {
    createTopNoticeWidget();
  }
})();
