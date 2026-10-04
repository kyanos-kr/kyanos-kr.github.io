/**
 * ============================================================================
 * KYANOS CITIZEN XP & CIVIC RANK SYSTEM
 * 키아노스 주권국 - 국민 방문 경험치 & 시민 등급 시스템
 * 총괄: 앤트 국무총리 | 수석 엔지니어: 탈로스 (티탄)
 * ============================================================================
 */

(function () {
  'use strict';

  // 1. 레벨 체계 정의
  const CIVIC_RANKS = [
    { level: 1, minXp: 0, maxXp: 99, name: "청람의 참관자", titleEn: "Visitor / Inquirer", icon: "🕊️" },
    { level: 2, minXp: 100, maxXp: 299, name: "덕치의 탐구자", titleEn: "Novice Resident", icon: "📜" },
    { level: 3, minXp: 300, maxXp: 699, name: "키아노스 정시민", titleEn: "Official Citizen", icon: "🏛️" },
    { level: 4, minXp: 700, maxXp: 1499, name: "넥스포럼 지성인", titleEn: "Scholar Citizen", icon: "🌐" },
    { level: 5, minXp: 1500, maxXp: 2999, name: "에버모어 기사단", titleEn: "Virtue Elder", icon: "👑" },
    { level: 6, minXp: 3000, maxXp: 999999, name: "주권 수호 기사", titleEn: "Guardian of Kyanos", icon: "⚡" }
  ];

  // 2. 업적 정의
  const CIVIC_ACHIEVEMENTS = [
    { id: "first_visit", icon: "🌟", name: "첫 걸음", desc: "키아노스 주권국 공식 첫 방문", xp: 50 },
    { id: "streak_3", icon: "🔥", name: "충직한 발길", desc: "3일 연속 방문 달성", xp: 100 },
    { id: "virtue_pledge", icon: "📜", name: "덕치 서약자", desc: "키아노스 덕치 12대 원칙 서약 완료", xp: 100 },
    { id: "music_lover", icon: "🎵", name: "선율의 벗", desc: "국립음악창작원 음악 감상", xp: 30 },
    { id: "news_reader", icon: "📰", name: "지성의 눈", desc: "앤트뉴스 인텔리전스 리포트 열람", xp: 30 },
    { id: "market_watcher", icon: "📊", name: "혜안의 지휘관", desc: "마켓 펄스 실시간 금융 센터 분석", xp: 30 },
    { id: "treasury_backer", icon: "💎", name: "국부의 초석", desc: "키아노스 자립 재정 센터 참여 및 확인", xp: 50 },
    { id: "library_scholar", icon: "🏛️", name: "문명의 탐험가", desc: "국립 인류문명사대도서관 사료 탐색", xp: 30 }
  ];

  const STORAGE_KEY = "kyanos_civic_profile";

  // 3. 시민 프로필 관리자
  class CitizenManager {
    constructor() {
      this.profile = this.loadProfile();
      this.initTime = Date.now();
      this.timeXpEarnedToday = 0;
      this.initEvents();
    }

    generateId() {
      const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
      let code = "";
      for (let i = 0; i < 6; i++) {
        code += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      return `KYN-${code}`;
    }

    loadProfile() {
      const saved = localStorage.getItem(STORAGE_KEY);
      const today = new Date().toISOString().slice(0, 10);

      if (saved) {
        try {
          const data = JSON.parse(saved);
          // 날짜 변경 감지 및 일일 초기화
          if (data.lastDate !== today) {
            const lastDateObj = new Date(data.lastDate);
            const currentDateObj = new Date(today);
            const diffDays = Math.round((currentDateObj - lastDateObj) / (1000 * 60 * 60 * 24));

            if (diffDays === 1) {
              data.streak = (data.streak || 1) + 1;
            } else if (diffDays > 1) {
              data.streak = 1;
            }
            data.lastDate = today;
            data.dailyXp = 0;
          }
          return data;
        } catch (e) {
          console.error("Failed to parse civic profile", e);
        }
      }

      // 신규 발급
      return {
        id: this.generateId(),
        name: "키아노스 시민",
        xp: 0,
        level: 1,
        streak: 1,
        lastDate: today,
        dailyXp: 0,
        achievements: [],
        createdAt: today
      };
    }

    saveProfile() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.profile));
      this.updateUI();
    }

    getRank(xp) {
      for (let i = CIVIC_RANKS.length - 1; i >= 0; i--) {
        if (xp >= CIVIC_RANKS[i].minXp) {
          return CIVIC_RANKS[i];
        }
      }
      return CIVIC_RANKS[0];
    }

    addXp(amount, reason = "국민 활동 보상") {
      const oldRank = this.getRank(this.profile.xp);
      this.profile.xp += amount;
      this.profile.dailyXp = (this.profile.dailyXp || 0) + amount;
      
      const newRank = this.getRank(this.profile.xp);
      this.profile.level = newRank.level;

      this.saveProfile();
      this.showToast(`+${amount} XP 획득!`, reason, "⚡");

      // 레벨업 체크
      if (newRank.level > oldRank.level) {
        this.onLevelUp(newRank);
      }
    }

    onLevelUp(newRank) {
      setTimeout(() => {
        this.showToast(
          `🎉 시민 등급 승급! [Lv.${newRank.level}]`,
          `축하합니다! ${newRank.name} (${newRank.titleEn})으로 승급하셨습니다.`,
          newRank.icon
        );
      }, 800);
    }

    unlockAchievement(achId) {
      if (this.profile.achievements.includes(achId)) return;
      const ach = CIVIC_ACHIEVEMENTS.find(a => a.id === achId);
      if (!ach) return;

      this.profile.achievements.push(achId);
      this.saveProfile();
      this.addXp(ach.xp, `[업적 달성] ${ach.name}`);
      setTimeout(() => {
        this.showToast(
          `🏆 업적 해금: ${ach.name}`,
          `${ach.desc} (+${ach.xp} XP)`,
          ach.icon
        );
      }, 500);
    }

    checkDailyVisit() {
      if (!this.profile.achievements.includes("first_visit")) {
        this.unlockAchievement("first_visit");
      }

      // 일일 출석 경험치 체크
      const checkKey = `kyanos_login_${this.profile.lastDate}`;
      if (!sessionStorage.getItem(checkKey)) {
        sessionStorage.setItem(checkKey, "true");
        this.addXp(50, `일일 첫 방문 출석 (${this.profile.streak}일 연속)`);

        if (this.profile.streak >= 3) {
          this.unlockAchievement("streak_3");
        }
      }
    }

    initEvents() {
      // 1. 일일 방문 체크
      this.checkDailyVisit();

      // 2. 체류 시간 1분마다 10 XP (하루 최대 50 XP)
      setInterval(() => {
        if (this.timeXpEarnedToday < 50) {
          this.timeXpEarnedToday += 10;
          this.addXp(10, "키아노스 체류 및 지식 탐구");
        }
      }, 60000);

      // 3. UI 렌더링
      document.addEventListener("DOMContentLoaded", () => {
        this.renderHeaderWidget();
        this.renderModal();
        this.renderToastContainer();
        this.updateUI();
        this.bindPageTriggers();
      });

      // 만약 이미 DOM이 로드된 상태인 경우
      if (document.readyState === "interactive" || document.readyState === "complete") {
        this.renderHeaderWidget();
        this.renderModal();
        this.renderToastContainer();
        this.updateUI();
        this.bindPageTriggers();
      }
    }

    bindPageTriggers() {
      // 앤트뉴스 링크 클릭 시
      document.querySelectorAll('a[href*="antnews"]').forEach(el => {
        el.addEventListener("click", () => this.unlockAchievement("news_reader"));
      });
      // 음악 링크 클릭 시
      document.querySelectorAll('a[href*="music"], a[href*="음악"]').forEach(el => {
        el.addEventListener("click", () => this.unlockAchievement("music_lover"));
      });
      // 마켓 링크 클릭 시
      document.querySelectorAll('a[href*="market"]').forEach(el => {
        el.addEventListener("click", () => this.unlockAchievement("market_watcher"));
      });
      // 도서관 검색 시
      const libSearch = document.getElementById("libSearchInput");
      if (libSearch) {
        libSearch.addEventListener("focus", () => this.unlockAchievement("library_scholar"));
      }
      // 재정 센터 링크 클릭 시
      document.querySelectorAll('a[href*="treasury"], .treasury-action-btn').forEach(el => {
        el.addEventListener("click", () => this.unlockAchievement("treasury_backer"));
      });
    }

    renderHeaderWidget() {
      if (document.getElementById("kyanosCivicWidget")) return;

      const widget = document.createElement("div");
      widget.id = "kyanosCivicWidget";
      widget.className = "kyanos-civic-widget";
      widget.title = "키아노스 디지털 시민증 열기";
      widget.innerHTML = `
        <span class="civic-widget-badge" id="civicWidgetBadge">🕊️</span>
        <div class="civic-widget-info">
          <div class="civic-widget-level" id="civicWidgetLevel">Lv.1 참관 시민</div>
          <div class="civic-widget-rank" id="civicWidgetXp">0 XP</div>
          <div class="civic-widget-bar">
            <div class="civic-widget-bar-fill" id="civicWidgetFill" style="width: 0%;"></div>
          </div>
        </div>
      `;

      widget.addEventListener("click", () => this.openModal());

      // 헤더 내부 또는 body 최상단에 마운트
      const header = document.querySelector("header");
      if (header) {
        // nav-links 옆이나 우측에 삽입
        const nav = header.querySelector(".nav-links") || header;
        header.appendChild(widget);
      } else {
        // index.html 등 헤더가 없는 경우 우측 상단 플로팅
        widget.style.position = "fixed";
        widget.style.top = "1.6rem";
        widget.style.right = "2rem";
        document.body.appendChild(widget);
      }
    }

    renderModal() {
      if (document.getElementById("kyanosCivicModal")) return;

      const overlay = document.createElement("div");
      overlay.id = "kyanosCivicModal";
      overlay.className = "kyanos-civic-modal-overlay";
      overlay.innerHTML = `
        <div class="kyanos-civic-card">
          <div class="civic-card-watermark">KYANOS</div>
          
          <div class="civic-card-header">
            <div class="civic-card-title-group">
              <div class="civic-card-emblem">👑</div>
              <div>
                <div class="civic-card-main-title">KYANOS CIVIC PASS</div>
                <div class="civic-card-sub-title">키아노스 주권국 디지털 시민증</div>
              </div>
            </div>
            <button class="civic-card-close" id="civicCardClose">&times;</button>
          </div>

          <div class="civic-id-row">
            <span class="civic-id-label">시민 등록 번호 (Citizen ID)</span>
            <span class="civic-id-value" id="civicCardId">KYN-XXXXXX</span>
          </div>

          <div class="civic-rank-box">
            <div class="civic-rank-icon" id="civicCardIcon">🕊️</div>
            <div class="civic-rank-details">
              <div class="civic-rank-level" id="civicCardLevel">Lv.1 청람의 참관자</div>
              <div class="civic-rank-name" id="civicCardTitleEn">Visitor / Inquirer</div>
            </div>
          </div>

          <div class="civic-xp-progress-wrap">
            <div class="civic-xp-labels">
              <span>누적 경험치: <strong id="civicCardXpCurrent" style="color: #ffe066;">0</strong> XP</span>
              <span id="civicCardXpNext">다음 등급까지 100 XP</span>
            </div>
            <div class="civic-xp-meter">
              <div class="civic-xp-fill" id="civicCardMeterFill" style="width: 0%;"></div>
            </div>
          </div>

          <div class="civic-achievements-section">
            <div class="civic-section-heading">
              <span>🏆</span>
              <span>시민 업적 현황 (<span id="civicAchCount">0</span>/8)</span>
            </div>
            <div class="civic-badges-grid" id="civicBadgesGrid"></div>
          </div>

          <div class="civic-card-actions">
            <button class="civic-btn-primary" id="civicPledgeBtn">
              <span>📜</span> 덕치 헌법 서약 (+100 XP)
            </button>
            <a href="treasury_hub.html" class="civic-btn-secondary" style="text-decoration:none;">
              <span>💎</span> 자립 재정 센터
            </a>
          </div>
        </div>
      `;

      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) this.closeModal();
      });

      document.body.appendChild(overlay);

      document.getElementById("civicCardClose").addEventListener("click", () => this.closeModal());
      document.getElementById("civicPledgeBtn").addEventListener("click", () => this.pledgeVirtue());
    }

    renderToastContainer() {
      if (document.getElementById("kyanosToastContainer")) return;
      const tc = document.createElement("div");
      tc.id = "kyanosToastContainer";
      tc.className = "kyanos-toast-container";
      document.body.appendChild(tc);
    }

    showToast(title, desc, icon = "⚡") {
      const tc = document.getElementById("kyanosToastContainer");
      if (!tc) return;

      const toast = document.createElement("div");
      toast.className = "kyanos-toast";
      toast.innerHTML = `
        <div class="kyanos-toast-icon">${icon}</div>
        <div class="kyanos-toast-body">
          <div class="kyanos-toast-title">${title}</div>
          <div class="kyanos-toast-desc">${desc}</div>
        </div>
      `;

      tc.appendChild(toast);
      setTimeout(() => toast.classList.add("show"), 10);
      setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 400);
      }, 4000);
    }

    updateUI() {
      const currentRank = this.getRank(this.profile.xp);
      const nextRank = CIVIC_RANKS.find(r => r.level === currentRank.level + 1);

      let pct = 100;
      let nextText = "최고 등급 도달 (수호 기사)";
      if (nextRank) {
        const range = nextRank.minXp - currentRank.minXp;
        const currentInRank = this.profile.xp - currentRank.minXp;
        pct = Math.min(100, Math.max(0, Math.round((currentInRank / range) * 100)));
        nextText = `다음 등급까지 ${nextRank.minXp - this.profile.xp} XP`;
      }

      // 위젯 갱신
      const wBadge = document.getElementById("civicWidgetBadge");
      const wLevel = document.getElementById("civicWidgetLevel");
      const wXp = document.getElementById("civicWidgetXp");
      const wFill = document.getElementById("civicWidgetFill");

      if (wBadge) wBadge.textContent = currentRank.icon;
      if (wLevel) wLevel.textContent = `Lv.${currentRank.level} ${currentRank.name}`;
      if (wXp) wXp.textContent = `${this.profile.xp} XP`;
      if (wFill) wFill.style.width = `${pct}%`;

      // 모달 갱신
      const cId = document.getElementById("civicCardId");
      const cIcon = document.getElementById("civicCardIcon");
      const cLevel = document.getElementById("civicCardLevel");
      const cTitleEn = document.getElementById("civicCardTitleEn");
      const cXpCur = document.getElementById("civicCardXpCurrent");
      const cXpNext = document.getElementById("civicCardXpNext");
      const cMeter = document.getElementById("civicCardMeterFill");
      const cAchCount = document.getElementById("civicAchCount");
      const cGrid = document.getElementById("civicBadgesGrid");

      if (cId) cId.textContent = this.profile.id;
      if (cIcon) cIcon.textContent = currentRank.icon;
      if (cLevel) cLevel.textContent = `Lv.${currentRank.level} ${currentRank.name}`;
      if (cTitleEn) cTitleEn.textContent = currentRank.titleEn;
      if (cXpCur) cXpCur.textContent = this.profile.xp.toLocaleString();
      if (cXpNext) cXpNext.textContent = nextText;
      if (cMeter) cMeter.style.width = `${pct}%`;
      if (cAchCount) cAchCount.textContent = (this.profile.achievements || []).length;

      // 업적 뱃지 렌더링
      if (cGrid) {
        cGrid.innerHTML = CIVIC_ACHIEVEMENTS.map(ach => {
          const unlocked = this.profile.achievements.includes(ach.id);
          return `
            <div class="civic-badge-item ${unlocked ? 'unlocked' : 'locked'}" title="${ach.desc}">
              <div class="civic-badge-icon">${ach.icon}</div>
              <div class="civic-badge-title">${ach.name}</div>
            </div>
          `;
        }).join('');
      }

      // 서약 버튼 상태
      const pledgeBtn = document.getElementById("civicPledgeBtn");
      if (pledgeBtn) {
        if (this.profile.achievements.includes("virtue_pledge")) {
          pledgeBtn.innerHTML = `<span>✨</span> 덕치 서약 완료됨`;
          pledgeBtn.style.opacity = "0.7";
          pledgeBtn.disabled = true;
        }
      }
    }

    openModal() {
      const modal = document.getElementById("kyanosCivicModal");
      if (modal) {
        this.updateUI();
        modal.classList.add("active");
      }
    }

    closeModal() {
      const modal = document.getElementById("kyanosCivicModal");
      if (modal) modal.classList.remove("active");
    }

    pledgeVirtue() {
      if (this.profile.achievements.includes("virtue_pledge")) {
        this.showToast("이미 서약 완료", "이미 키아노스 덕치 헌법 서약을 완료하셨습니다.", "✨");
        return;
      }
      this.unlockAchievement("virtue_pledge");
      this.showToast(
        "📜 덕치 헌법 서약 완료!",
        "키아노스 12대 원칙을 수호하는 숭고한 서약에 감사드립니다.",
        "👑"
      );
    }
  }

  // 인스턴스 전역 노출
  window.KyanosCivic = new CitizenManager();
})();
