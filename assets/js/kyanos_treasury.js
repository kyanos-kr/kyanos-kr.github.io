/**
 * ============================================================================
 * KYANOS SOVEREIGN TREASURY & CIVIC PATRON SYSTEM
 * 키아노스 주권국 - 국가 자립 재정 확충 및 시민 후원 시스템
 * 총괄: 앤트 국무총리 | 수석 엔지니어: 탈로스 (티탄)
 * ============================================================================
 */

(function () {
  'use strict';

  // 1. 재정 금고 지갑 및 계좌 정보 (자립형 다채널 수납 인프라)
  const TREASURY_CONFIG = {
    // 키아노스 국가 자립 재정 계좌
    bank: {
      bankName: "국가 자립 재정 금고 (카카오뱅크 / 토스뱅크)",
      accountNumber: "3333-01-XXXXXXX (키아노스 국고)",
      holder: "키아노스 정부 (파이튼)",
      guide: "입금자명에 본인의 시민 등록 번호(예: KYN-XXXXXX)를 입력하시면 즉시 정식 기여자로 영구 등재됩니다."
    },
    // 키아노스 공식 온체인 암호화폐 금고 (XRP / USDT / ETH)
    crypto: {
      xrp: {
        symbol: "XRP",
        network: "XRPL (XRP Ledger)",
        address: "rKyanosSovereignTreasuryVaultXRP1234567890",
        destinationTag: "20261005"
      },
      usdt: {
        symbol: "USDT / USDC",
        network: "Ethereum / Tron / Polygon",
        address: "0x7A9F21b3C91427a1c94B2E9f7A9b06886eD73B4D"
      }
    }
  };

  // 2. 4대 재원 프로그램 상세 정의
  const TREASURY_PROGRAMS = [
    {
      id: "founders_pass",
      badge: "한정 1,000명",
      icon: "👑",
      title: "파운더스 디지털 시민권",
      target: "Founders Civic Pass (골드·사파이어)",
      desc: "키아노스 건국 초기에 동참하는 핵심 시민을 위한 영구 주권 패스입니다. 광고 없이 온전히 유지되는 국가 플랫폼의 영구 수호자가 됩니다.",
      benefits: [
        "디지털 시민증에 'FOUNDER' 골드 엠블럼 영구 각인",
        "앤트뉴스(AntNews) VIP 딥리서치 및 비공개 브리핑 무제한 열람",
        "넥스포럼(NEXFORUM) 글로벌 연례 서밋 VIP 우선 초청권",
        "키아노스 국부 기여 경험치 +2,000 XP 즉시 부여"
      ],
      xpReward: 2000,
      btnText: "파운더스 시민권 신청"
    },
    {
      id: "patron_civilization",
      badge: "문명 보존 기금",
      icon: "🏛️",
      title: "국립 인류문명사연구원 후원",
      target: "Civilization Heritage Fund",
      desc: "동서양 인류 역사 사료의 디지털 복원, 지혜의 옴니포털 아카이빙, AGI 시대 인간 도덕 기준 연구를 후원합니다.",
      benefits: [
        "국립대도서관 고전 원전 대역본 및 전문가 비판 주석 무료 열람",
        "연구원 연례 학술 백서 소장본 제공",
        "디지털 명예 학술위원 뱃지 수여",
        "학술 기여 경험치 +1,000 XP 즉시 부여"
      ],
      xpReward: 1000,
      btnText: "문명사 연구 기금 후원"
    },
    {
      id: "patron_music",
      badge: "문화 예술 진흥",
      icon: "🎵",
      title: "국립음악창작원 문화 후원",
      target: "National Music Creation Fund",
      desc: "파이튼 님의 원작 시와 철학을 바탕으로 AI 오케스트라 명곡 및 현대적 음악을 창작하고 전 세계에 보급하는 예술 기금입니다.",
      benefits: [
        "모든 신곡 무손실(FLAC) 고음질 음원 우선 다운로드",
        "기타/건반 전용 풀스코어 코드 악보집 제공",
        "국립음악실 명예 후원자 헌정 크레딧 등재",
        "예술 기여 경험치 +800 XP 즉시 부여"
      ],
      xpReward: 800,
      btnText: "음악창작원 후원하기"
    },
    {
      id: "patron_antnews",
      badge: "독립 언론 인프라",
      icon: "📰",
      title: "앤트뉴스 AI 인텔리전스 펀드",
      target: "AntNews Sovereign Media Fund",
      desc: "빅테크 광고 의존과 왜곡된 여론을 탈피하고, 24/7 AI 팩트체크 엔진과 객관적 글로벌 정세 리포트를 유지하기 위한 독립 저널리즘 펀드입니다.",
      benefits: [
        "광고 없는 초고속 실시간 뉴스 엔진 무제한 이용",
        "마이클 스나이더 등 글로벌 심층 외신 전용 한국어 번역 리포트",
        "마켓 펄스(Market Pulse) 24/7 금융 경보 알림 연동",
        "언론 자립 기여 경험치 +1,200 XP 즉시 부여"
      ],
      xpReward: 1200,
      btnText: "독립 언론 펀드 후원"
    }
  ];

  class TreasuryManager {
    constructor() {
      this.initModal();
    }

    initModal() {
      document.addEventListener("DOMContentLoaded", () => {
        this.renderGatewayModal();
      });
      if (document.readyState === "interactive" || document.readyState === "complete") {
        this.renderGatewayModal();
      }
    }

    renderGatewayModal() {
      if (document.getElementById("treasuryGatewayModal")) return;

      const modal = document.createElement("div");
      modal.id = "treasuryGatewayModal";
      modal.className = "treasury-gateway-modal";
      modal.innerHTML = `
        <div class="treasury-gateway-card">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.2rem; border-bottom: 1px solid rgba(212, 175, 55, 0.25); padding-bottom: 0.8rem;">
            <div>
              <div style="font-family: 'Cinzel', serif; font-size: 1.25rem; font-weight: 800; color: #ffe066;">
                💎 KYANOS SOVEREIGN TREASURY
              </div>
              <div style="font-size: 0.72rem; color: #a5b4cb; letter-spacing: 0.12em; text-transform: uppercase;">
                키아노스 주권국 자립 재정 확충 센터
              </div>
            </div>
            <button id="treasuryModalClose" style="background:none; border:none; color:#a5b4cb; font-size:1.6rem; cursor:pointer;">&times;</button>
          </div>

          <div id="treasurySelectedProgramInfo" style="background: rgba(0, 210, 255, 0.08); border: 1px solid rgba(0, 210, 255, 0.3); border-radius: 12px; padding: 1rem; margin-bottom: 1.4rem;">
            <div style="font-weight: 700; color: #fff; font-size: 0.95rem; margin-bottom: 4px;" id="treasuryProgramTitle">
              국가 자립 재정 확충 참여
            </div>
            <div style="font-size: 0.8rem; color: #a5b4cb; line-height: 1.5;" id="treasuryProgramDesc">
              시민 여러분의 자발적 기여는 애드센스 등 외부 광고에 의존하지 않는 독립적인 국가 지식 인프라의 토대가 됩니다.
            </div>
          </div>

          <div class="treasury-tabs">
            <button class="treasury-tab-btn active" data-tab="bank">🏛️ 계좌 / 간편 송금</button>
            <button class="treasury-tab-btn" data-tab="crypto">⚡ 암호화폐 (XRP / USDT)</button>
            <button class="treasury-tab-btn" data-tab="pledge">📜 명예 기여 서약</button>
          </div>

          <!-- Tab 1: Bank Transfer -->
          <div class="treasury-tab-content active" id="tab-bank">
            <div style="font-size: 0.82rem; color: #cfd9e8; margin-bottom: 0.8rem; line-height: 1.5;">
              키아노스 국고 전용 계좌로 원하시는 금액을 자율 후원하실 수 있습니다.
            </div>
            <div class="treasury-copy-box">
              <div>
                <div style="font-size: 0.7rem; color: #a5b4cb;">공식 국고 수납 기관</div>
                <div class="treasury-copy-text">${TREASURY_CONFIG.bank.bankName}</div>
                <div class="treasury-copy-text" style="font-size: 1.05rem; font-weight: 700; color: #ffe066; margin-top: 3px;">${TREASURY_CONFIG.bank.accountNumber}</div>
                <div style="font-size: 0.72rem; color: #a5b4cb;">예금주: ${TREASURY_CONFIG.bank.holder}</div>
              </div>
              <button class="treasury-copy-btn" onclick="KyanosTreasury.copyText('${TREASURY_CONFIG.bank.accountNumber}')">계좌 복사</button>
            </div>
            <div style="font-size: 0.75rem; color: #a5b4cb; line-height: 1.5; background: rgba(0,0,0,0.3); padding: 0.8rem; border-radius: 8px;">
              💡 <strong>입금 팁:</strong> ${TREASURY_CONFIG.bank.guide}
            </div>
          </div>

          <!-- Tab 2: Crypto -->
          <div class="treasury-tab-content" id="tab-crypto">
            <div style="font-size: 0.82rem; color: #cfd9e8; margin-bottom: 0.8rem;">
              국경 없는 글로벌 온체인 금고로 즉시 후원하실 수 있습니다.
            </div>
            
            <!-- XRP -->
            <div class="treasury-copy-box" style="margin-bottom: 0.8rem;">
              <div style="flex: 1; overflow: hidden;">
                <div style="font-size: 0.7rem; color: #00d2ff; font-weight: 700;">💎 XRP (리플 레저 공식 금고)</div>
                <div class="treasury-copy-text" style="font-size: 0.8rem;">${TREASURY_CONFIG.crypto.xrp.address}</div>
                <div style="font-size: 0.7rem; color: #ffe066;">데스티네이션 태그: ${TREASURY_CONFIG.crypto.xrp.destinationTag}</div>
              </div>
              <button class="treasury-copy-btn" onclick="KyanosTreasury.copyText('${TREASURY_CONFIG.crypto.xrp.address}')">주소 복사</button>
            </div>

            <!-- USDT -->
            <div class="treasury-copy-box">
              <div style="flex: 1; overflow: hidden;">
                <div style="font-size: 0.7rem; color: #10b981; font-weight: 700;">💵 USDT / USDC (멀티체인 지갑)</div>
                <div class="treasury-copy-text" style="font-size: 0.8rem;">${TREASURY_CONFIG.crypto.usdt.address}</div>
              </div>
              <button class="treasury-copy-btn" onclick="KyanosTreasury.copyText('${TREASURY_CONFIG.crypto.usdt.address}')">주소 복사</button>
            </div>
          </div>

          <!-- Tab 3: Pledge -->
          <div class="treasury-tab-content" id="tab-pledge">
            <div style="font-size: 0.82rem; color: #cfd9e8; margin-bottom: 1rem; line-height: 1.6;">
              금전적 후원 외에도 키아노스의 가치를 주변에 알리고, 덕치 헌법을 실천하는 시민 서약으로도 국가 재정 자립에 동참하실 수 있습니다.
            </div>
            <div style="text-align: center; padding: 1.5rem 0;">
              <button class="civic-btn-primary" style="margin: 0 auto; width: 100%; max-width: 320px;" onclick="KyanosTreasury.completePledge()">
                ✨ 자립 재정 수호 서약 및 경험치 수령
              </button>
            </div>
          </div>

          <div style="margin-top: 1.5rem; text-align: center;">
            <button id="treasuryConfirmBtn" class="treasury-action-btn" style="width: 100%;" onclick="KyanosTreasury.completeContribution()">
              기여 확인 및 디지털 기여 증표 발급 받기
            </button>
          </div>
        </div>
      `;

      document.body.appendChild(modal);

      // Event listeners
      document.getElementById("treasuryModalClose").addEventListener("click", () => this.closeGateway());
      modal.addEventListener("click", (e) => {
        if (e.target === modal) this.closeGateway();
      });

      // Tab switching
      modal.querySelectorAll(".treasury-tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          modal.querySelectorAll(".treasury-tab-btn").forEach(b => b.classList.remove("active"));
          modal.querySelectorAll(".treasury-tab-content").forEach(c => c.classList.remove("active"));
          btn.classList.add("active");
          const target = modal.querySelector(`#tab-${btn.dataset.tab}`);
          if (target) target.classList.add("active");
        });
      });
    }

    openGateway(programId) {
      const modal = document.getElementById("treasuryGatewayModal");
      if (!modal) return;

      const program = TREASURY_PROGRAMS.find(p => p.id === programId) || TREASURY_PROGRAMS[0];
      this.currentProgram = program;

      const titleEl = document.getElementById("treasuryProgramTitle");
      const descEl = document.getElementById("treasuryProgramDesc");
      if (titleEl) titleEl.textContent = `${program.icon} ${program.title} (${program.target})`;
      if (descEl) descEl.textContent = `${program.desc} | 기여 시 +${program.xpReward} XP 및 특별 칭호 부여`;

      modal.classList.add("active");
    }

    closeGateway() {
      const modal = document.getElementById("treasuryGatewayModal");
      if (modal) modal.classList.remove("active");
    }

    copyText(text) {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
          if (window.KyanosCivic) {
            window.KyanosCivic.showToast("복사 완료!", "클립보드에 안전하게 복사되었습니다.", "📋");
          } else {
            alert("복사되었습니다: " + text);
          }
        });
      } else {
        alert("복사 대상: " + text);
      }
    }

    completePledge() {
      if (window.KyanosCivic) {
        window.KyanosCivic.addXp(300, "키아노스 자립 재정 수호 서약");
        window.KyanosCivic.unlockAchievement("treasury_backer");
        window.KyanosCivic.showToast("서약 접수 완료!", "국가 자립 재정을 지지해주신 숭고한 마음에 깊이 감사드립니다.", "💎");
      }
      this.closeGateway();
    }

    completeContribution() {
      const program = this.currentProgram || TREASURY_PROGRAMS[0];
      if (window.KyanosCivic) {
        window.KyanosCivic.addXp(program.xpReward, `[국부 기여] ${program.title}`);
        window.KyanosCivic.unlockAchievement("treasury_backer");
        window.KyanosCivic.showToast(
          "👑 기여 증표 발급 완료!",
          `${program.title} 기여가 기록되었습니다. 키아노스 명예의 전당에 등재됩니다.`,
          "✨"
        );
      }
      this.closeGateway();
    }
  }

  window.KyanosTreasury = new TreasuryManager();
})();
