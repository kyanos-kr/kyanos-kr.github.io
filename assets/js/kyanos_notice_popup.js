/**
 * 키아노스 시스템 개편 및 서비스 점검 안내 팝업 스크립트
 * Kyanos System Renovation & Service Update Notice Popup
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'kyanos_hide_renovation_notice';
  const EXPIRE_HOURS = 24;

  // 1. 숨김 여부 체크 (localStorage 확인)
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

  // 2. CSS 자동 인클루드 (없을 경우 보장)
  function ensureCSS() {
    const existing = document.querySelector('link[href*="kyanos_notice_popup.css"]');
    if (!existing) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'assets/css/kyanos_notice_popup.css';
      document.head.appendChild(link);
    }
  }

  // 3. 모달 DOM 생성 및 렌더링
  function createNoticeModal() {
    if (!shouldShowNotice()) return;

    ensureCSS();

    // Backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'kyanos-notice-backdrop';
    backdrop.id = 'kyanosNoticeBackdrop';

    backdrop.innerHTML = `
      <div class="kyanos-notice-modal" role="dialog" aria-modal="true" aria-labelledby="kyanosNoticeTitle">
        <div class="kyanos-notice-header-bar"></div>
        <div class="kyanos-notice-body">
          <div class="kyanos-notice-icon-wrap">
            <span>⚙️</span>
          </div>
          <div>
            <span class="kyanos-notice-tag">NOTICE • OFFICIAL ANNOUNCEMENT</span>
          </div>
          <h2 class="kyanos-notice-title" id="kyanosNoticeTitle">
            시스템 개편 및 서비스 점검 안내
          </h2>
          <p class="kyanos-notice-desc">
            현재 <strong>키아노스(KYANOS)</strong> 공식 포털은 국가 시스템 전면 개편과<br>
            인텔리전스 인프라 고도화 작업이 상시 진행 중에 있습니다.<br>
            이에 따라 일부 서비스 및 메뉴 이용 시 일시적인 연결 지연이나 변동이 발생할 수 있으니 방문객 여러분의 너그러운 양해를 부탁드립니다.
          </p>

          <div class="kyanos-notice-status-box">
            <div class="kyanos-notice-status-item">
              <span class="bullet">✦</span>
              <span><strong>진행 사항:</strong> 각 부처별 시스템 개편 및 데이터베이스 최적화 정비</span>
            </div>
            <div class="kyanos-notice-status-item">
              <span class="bullet">✦</span>
              <span><strong>이용 안내:</strong> 개편 완료 시까지 일부 링크 및 기능이 순차적으로 업데이트됩니다.</span>
            </div>
            <div class="kyanos-notice-status-item">
              <span class="bullet">✦</span>
              <span><strong>목표:</strong> 더욱 품격 있고 신뢰받는 국가 최고 지능형 포털로 도약하겠습니다.</span>
            </div>
          </div>
        </div>

        <div class="kyanos-notice-footer">
          <label class="kyanos-notice-check-label">
            <input type="checkbox" id="kyanosNoticeHideCheck">
            <span>오늘 하루 이 창을 열지 않음</span>
          </label>
          <button type="button" class="kyanos-notice-btn" id="kyanosNoticeCloseBtn">
            <span>확인 및 사이트 입장</span>
            <span>&rarr;</span>
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(backdrop);

    // Fade-in animation trigger
    requestAnimationFrame(() => {
      setTimeout(() => {
        backdrop.classList.add('active');
      }, 50);
    });

    // 닫기 로직
    const closeBtn = backdrop.querySelector('#kyanosNoticeCloseBtn');
    const hideCheck = backdrop.querySelector('#kyanosNoticeHideCheck');

    function closeModal() {
      if (hideCheck && hideCheck.checked) {
        try {
          const expireTime = new Date().getTime() + (EXPIRE_HOURS * 60 * 60 * 1000);
          localStorage.setItem(STORAGE_KEY, expireTime.toString());
        } catch (e) {
          console.warn('LocalStorage access restricted:', e);
        }
      }

      backdrop.classList.remove('active');
      setTimeout(() => {
        backdrop.remove();
      }, 400);
    }

    closeBtn.addEventListener('click', closeModal);

    // 배경 클릭 시 닫기
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        closeModal();
      }
    });

    // ESC 키로 닫기
    window.addEventListener('keydown', function escHandler(e) {
      if (e.key === 'Escape' && document.body.contains(backdrop)) {
        closeModal();
        window.removeEventListener('keydown', escHandler);
      }
    });
  }

  // DOM 로드 완료 후 실행
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createNoticeModal);
  } else {
    createNoticeModal();
  }
})();
