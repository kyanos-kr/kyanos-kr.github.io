/**
 * ============================================================================
 * KYANOS PASSPORT - UNIFIED AUTH GATEWAY & ZERO TRUST SHIELD (CLIENT ENGINE)
 * 키아노스 통합 로그인 관문 및 4계층 권한 차등화 제어 엔진
 * 통수권자: 국왕 파이튼 | 총괄 지휘: 국무총리 메티
 * 2026-11-20 국정 시행안건 연동
 * ============================================================================
 */

(function () {
  'use strict';

  // 4계층 권한 상수
  const TIERS = {
    TIER_1: { id: 1, name: "국가최고원수", label: "👑 파이튼 님 집무실 (Tier-1 Sovereign)", role: "SOVEREIGN" },
    TIER_2: { id: 2, name: "내각총괄", label: "🏛️ 총리실·수석비서실 (Tier-2 Cabinet)", role: "CABINET" },
    TIER_3: { id: 3, name: "부처실무", label: "🏢 부처 행정관 (Tier-3 Ministry)", role: "MINISTRY" },
    TIER_4: { id: 4, name: "일반시민", label: "🌐 키아노스 시민 (Tier-4 Citizen)", role: "CITIZEN" }
  };

  const STORAGE_KEY = 'kyanos_auth_session';

  const KyanosAuth = {
    currentTier: TIERS.TIER_4,
    currentUser: null,
    isAuthenticated: false,

    init: function () {
      this.loadSession();
      this.injectMarkup();
      this.bindEvents();
      this.attachRouteGuard();
      this.updateUIState();
      console.log("%c👑 [Kyanos Passport] 통합 로그인 관문 및 4계층 권한 엔진 가동 완료 (Current: " + this.currentTier.name + ")", "color:#f59e0b; font-weight:bold; font-size:12px;");
    },

    loadSession: function () {
      try {
        const stored = sessionStorage.getItem(STORAGE_KEY) || localStorage.getItem(STORAGE_KEY);
        if (stored) {
          const data = JSON.parse(stored);
          if (data && data.tier) {
            this.currentTier = data.tier;
            this.currentUser = data.user;
            this.isAuthenticated = true;
          }
        }
      } catch (e) {
        console.warn("[KyanosAuth] 세션 복원 오류:", e);
      }
    },

    saveSession: function (tier, user, persist) {
      this.currentTier = tier;
      this.currentUser = user;
      this.isAuthenticated = true;
      const data = JSON.stringify({ tier: tier, user: user, timestamp: Date.now() });
      if (persist) {
        localStorage.setItem(STORAGE_KEY, data);
      } else {
        sessionStorage.setItem(STORAGE_KEY, data);
      }
      this.updateUIState();
    },

    logout: function () {
      sessionStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(STORAGE_KEY);
      this.currentTier = TIERS.TIER_4;
      this.currentUser = null;
      this.isAuthenticated = false;
      this.updateUIState();
      if (window.KSEFActiveDefense && window.KSEFActiveDefense.showSecurityToast) {
        window.KSEFActiveDefense.showSecurityToast("정상적으로 로그아웃되었습니다.");
      } else {
        alert("키아노스 보안 세션에서 안전하게 로그아웃되었습니다.");
      }
    },

    injectMarkup: function () {
      if (document.getElementById('kyanos-gate-modal-overlay')) return;

      const overlay = document.createElement('div');
      overlay.id = 'kyanos-gate-modal-overlay';
      overlay.className = 'kyanos-gate-modal-overlay';
      overlay.innerHTML = `
        <div class="kyanos-gate-card">
          <button class="kyanos-gate-close-btn" id="kyanosGateCloseBtn" title="닫기">&times;</button>
          
          <div class="kyanos-gate-header">
            <div class="kyanos-gate-emblem">👑</div>
            <h3 class="kyanos-gate-title notranslate" translate="no">KYANOS PASSPORT</h3>
            <p class="kyanos-gate-subtitle">키아노스 통합 로그인 관문 및 주권자 인증 체계</p>
          </div>

          <div class="kyanos-gate-tiers-badge">
            <span class="kyanos-tier-pill">Tier-1 원수실</span>
            <span class="kyanos-tier-pill">Tier-2 내각총괄</span>
            <span class="kyanos-tier-pill">Tier-3 부처실무</span>
            <span class="kyanos-tier-pill active">Tier-4 일반열람</span>
          </div>

          <form class="kyanos-gate-form" id="kyanosGateForm" onsubmit="return false;">
            <div class="kyanos-gate-input-group">
              <label class="kyanos-gate-label" for="kyanosAuthIdentity">식별자 (Identity / ID)</label>
              <input type="text" id="kyanosAuthIdentity" class="kyanos-gate-input" placeholder="성함, 직책 또는 시민 ID 입력" autocomplete="username" required>
            </div>

            <div class="kyanos-gate-input-group">
              <label class="kyanos-gate-label" for="kyanosAuthSecret">보안 패스코드 (Access Key)</label>
              <input type="password" id="kyanosAuthSecret" class="kyanos-gate-input" placeholder="보안 인증 키 입력" autocomplete="current-password" required>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; color:#94a3b8;">
              <label style="display:flex; align-items:center; gap:5px; cursor:pointer;">
                <input type="checkbox" id="kyanosAuthPersist" style="accent-color:#f59e0b;"> 세션 유지 (Remember)
              </label>
              <span style="color:#fde68a; cursor:pointer;" id="kyanosFastPassBtn" title="파이튼 님 간편 검증">[마스터 패스]</span>
            </div>

            <button type="submit" class="kyanos-gate-btn-submit" id="kyanosGateSubmitBtn">관문 인증 및 진입</button>
            <div class="kyanos-gate-status" id="kyanosGateStatus"></div>
          </form>

          <div class="kyanos-gate-footer">
            <p>※ 외부 일반 방문객은 별도 인증 없이 <strong>기본 공개 서고 및 앤트뉴스</strong>를 자유롭게 열람하실 수 있습니다.</p>
            <p style="margin-top:6px;">초청 코드 또는 시민권 사전 등록 신청: <a href="mailto:kyanos.gov@gmail.com?subject=[키아노스 시민권 신청]" target="_blank">사전 등록 문의 ↗</a></p>
          </div>
        </div>
      `;
      document.body.appendChild(overlay);

      // 미완성 구역 차폐 쉴드 모달
      const shield = document.createElement('div');
      shield.id = 'kyanos-shield-modal';
      shield.className = 'kyanos-shield-modal';
      shield.innerHTML = `
        <div style="font-size:2rem; margin-bottom:0.5rem;">🛡️</div>
        <h4 id="kyanosShieldTitle">K-SEF 인가 구역 알림</h4>
        <p id="kyanosShieldMsg">해당 구역은 현재 키아노스 국가 인프라 편제 및 정밀 고도화 공사가 진행 중인 <strong>보안 인가 전용 구역</strong>입니다.</p>
        <div style="display:flex; justify-content:center; gap:10px;">
          <button class="kyanos-shield-modal-close" id="kyanosShieldCloseBtn">확인</button>
          <button class="kyanos-shield-modal-close" id="kyanosShieldLoginBtn" style="border-color:#f59e0b; color:#fde68a;">인증 관문 열기</button>
        </div>
      `;
      document.body.appendChild(shield);
    },

    bindEvents: function () {
      const overlay = document.getElementById('kyanos-gate-modal-overlay');
      const closeBtn = document.getElementById('kyanosGateCloseBtn');
      const form = document.getElementById('kyanosGateForm');
      const fastPassBtn = document.getElementById('kyanosFastPassBtn');
      const shieldModal = document.getElementById('kyanos-shield-modal');
      const shieldCloseBtn = document.getElementById('kyanosShieldCloseBtn');
      const shieldLoginBtn = document.getElementById('kyanosShieldLoginBtn');

      if (closeBtn) {
        closeBtn.addEventListener('click', () => this.closeModal());
      }
      if (overlay) {
        overlay.addEventListener('click', (e) => {
          if (e.target === overlay) this.closeModal();
        });
      }
      if (shieldCloseBtn) {
        shieldCloseBtn.addEventListener('click', () => {
          shieldModal.classList.remove('active');
        });
      }
      if (shieldLoginBtn) {
        shieldLoginBtn.addEventListener('click', () => {
          shieldModal.classList.remove('active');
          this.openModal();
        });
      }

      if (fastPassBtn) {
        fastPassBtn.addEventListener('click', () => {
          document.getElementById('kyanosAuthIdentity').value = '파이튼';
          document.getElementById('kyanosAuthSecret').value = 'kyanos-sovereign-2026';
          document.getElementById('kyanosGateStatus').className = 'kyanos-gate-status success';
          document.getElementById('kyanosGateStatus').innerText = '원수실 마스터 시퀀스가 로드되었습니다. 진입 버튼을 누르십시오.';
        });
      }

      if (form) {
        form.addEventListener('submit', (e) => {
          e.preventDefault();
          this.processAuth();
        });
      }
    },

    openModal: function () {
      const overlay = document.getElementById('kyanos-gate-modal-overlay');
      if (overlay) {
        overlay.classList.add('active');
        const input = document.getElementById('kyanosAuthIdentity');
        if (input) setTimeout(() => input.focus(), 150);
      }
    },

    closeModal: function () {
      const overlay = document.getElementById('kyanos-gate-modal-overlay');
      if (overlay) overlay.classList.remove('active');
    },

    processAuth: function () {
      const identityInput = document.getElementById('kyanosAuthIdentity');
      const secretInput = document.getElementById('kyanosAuthSecret');
      const persistCheck = document.getElementById('kyanosAuthPersist');
      const statusEl = document.getElementById('kyanosGateStatus');

      const id = (identityInput.value || '').trim();
      const secret = (secretInput.value || '').trim();

      statusEl.className = 'kyanos-gate-status';
      statusEl.innerText = '인증 시퀀스 검증 중...';

      setTimeout(() => {
        // 1. 최고통수권자 파이튼 님
        if (id.toLowerCase() === 'python' || id === '파이튼' || secret === 'kyanos-sovereign-2026' || secret === 'python2026') {
          this.saveSession(TIERS.TIER_1, '파이튼', persistCheck.checked);
          statusEl.className = 'kyanos-gate-status success';
          statusEl.innerText = '환영합니다, 파이튼 님. 최고 존엄 세션이 활성화되었습니다.';
          setTimeout(() => {
            this.closeModal();
            if (window.KSEFActiveDefense && window.KSEFActiveDefense.showSecurityToast) {
              window.KSEFActiveDefense.showSecurityToast("👑 파이튼 님 인증 완료: 전 구역 접근 통제 해제");
            }
          }, 800);
          return;
        }

        // 2. 내각 (메티, 비비안)
        if (id === '메티' || id === '비비안' || secret === 'kyanos-cabinet-2026') {
          this.saveSession(TIERS.TIER_2, id || '총리실', persistCheck.checked);
          statusEl.className = 'kyanos-gate-status success';
          statusEl.innerText = `[${id || '내각'}] 집행 권한 세션이 활성화되었습니다.`;
          setTimeout(() => this.closeModal(), 800);
          return;
        }

        // 3. 부처 관리자
        if (secret.startsWith('dept-') || id.includes('장관')) {
          this.saveSession(TIERS.TIER_3, id || '부처관리관', persistCheck.checked);
          statusEl.className = 'kyanos-gate-status success';
          statusEl.innerText = '부처 실무 관리 세션이 인가되었습니다.';
          setTimeout(() => this.closeModal(), 800);
          return;
        }

        // 실패 시
        statusEl.className = 'kyanos-gate-status error';
        statusEl.innerText = '유효하지 않은 보안 키입니다. 인가된 코드를 다시 확인하십시오.';
      }, 350);
    },

    updateUIState: function () {
      // 상단 트리거 버튼 갱신
      let triggerBtn = document.getElementById('kyanosTopAuthTrigger');
      if (!triggerBtn) {
        // 없으면 헤더나 인트로 상단에 부착
        const headerNav = document.querySelector('header nav .nav-links') || document.querySelector('.top-nav');
        if (headerNav) {
          const li = document.createElement('li');
          li.id = 'kyanos-auth-nav-item';
          li.style.display = 'inline-flex';
          li.style.alignItems = 'center';
          li.innerHTML = `<button id="kyanosTopAuthTrigger" class="kyanos-auth-trigger-btn">관문 인증</button>`;
          headerNav.appendChild(li);
          triggerBtn = document.getElementById('kyanosTopAuthTrigger');
        }
      }

      if (triggerBtn) {
        if (this.isAuthenticated) {
          triggerBtn.innerHTML = `<span>${this.currentTier.id === 1 ? '👑' : '🛡️'} ${this.currentUser} (${this.currentTier.name})</span>`;
          triggerBtn.title = "클릭 시 세션 정보 확인 및 로그아웃";
          triggerBtn.onclick = () => {
            if (confirm(`현재 세션: ${this.currentTier.label}\n사용자: ${this.currentUser}\n\n로그아웃하시겠습니까?`)) {
              this.logout();
            }
          };
        } else {
          triggerBtn.innerHTML = `<span>👑 관문 로그인</span>`;
          triggerBtn.title = "키아노스 4계층 권한 로그인 관문 열기";
          triggerBtn.onclick = () => this.openModal();
        }
      }
    },

    // 미완성 구역 및 내부 인프라 링크 인터셉트 가드
    attachRouteGuard: function () {
      document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;

        const href = link.getAttribute('href') || '';
        const title = link.getAttribute('title') || '';
        const text = link.innerText || '';

        // 차폐 대상 패턴 (공사 중이거나 내부 시스템 전용)
        const isRestrictedTarget = (
          href.includes('schedule_manager.html') ||
          href.includes('gov_society.html') ||
          href.includes('gov_welfare.html') ||
          href.includes('gov_international.html') ||
          text.includes('준비중') ||
          title.includes('공사') ||
          href.includes('#under-construction')
        );

        if (isRestrictedTarget) {
          // Tier-1 또는 Tier-2 세션이면 통과
          if (this.isAuthenticated && (this.currentTier.id <= 2)) {
            return; // 통과 허용
          }

          // 미인가 방문객 차단 인터셉트
          e.preventDefault();
          e.stopPropagation();

          const shieldModal = document.getElementById('kyanos-shield-modal');
          const shieldTitle = document.getElementById('kyanosShieldTitle');
          const shieldMsg = document.getElementById('kyanosShieldMsg');

          shieldTitle.innerText = "🛡️ K-SEF 보안 인가 구역 (Restricted)";
          shieldMsg.innerHTML = `해당 구역은 현재 키아노스 내부 인프라 편제 및 정밀 고도화 공사가 진행 중인 <strong>보안 인가 전용 구역</strong>입니다.<br><br>인가된 세션 키를 소지하신 경우 [인증 관문 열기]를 통해 진입하십시오.`;
          shieldModal.classList.add('active');
        }
      }, true);
    }
  };

  window.KyanosAuth = KyanosAuth;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => KyanosAuth.init());
  } else {
    KyanosAuth.init();
  }
})();
