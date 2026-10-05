/**
 * ============================================================================
 * KYANOS GLOBAL HYBRID TRANSLATOR & I18N ENGINE
 * 키아노스 주권국 - 글로벌 하이브리드 실시간 다국어 번역 엔진
 * 총괄: 앤트 국무총리 | 수석 엔지니어: 탈로스 (티탄)
 * ============================================================================
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'kyanos_selected_lang';
  const SUPPORTED_LANGS = [
    { code: 'ko', label: 'KR', title: '한국어 (원문)' },
    { code: 'en', label: 'EN', title: 'English' },
    { code: 'ja', label: 'JP', title: '日本語' },
    { code: 'zh-CN', label: 'CN', title: '简体中文' }
  ];

  class KyanosTranslator {
    constructor() {
      this.currentLang = localStorage.getItem(STORAGE_KEY) || 'ko';
      this.initGoogleTranslate();
      this.initUI();
      this.initBrandProtection();
    }

    /**
     * 🛡️ 키아노스(KYANOS) 국가 브랜드 고유명사 보호 및 실시간 자동 교정기
     * 구글 번역기가 'KYANOS'를 오역한 '캬노스'를 원천 방지하고 '키아노스'로 자동 수복함
     */
    initBrandProtection() {
      const protectElements = () => {
        // 로고 및 국가명 관련 셀렉터에 notranslate 및 translate="no" 강제 부여
        const logoSelectors = [
          '.brand-logo', '.brand-text', '.nav-logo-group', '.nav-title-box',
          '.top-brand-emblem', '.emblem-text-group', '.realm-title-area',
          '.national-emblem-badge', '.hero-title', '.badge'
        ];
        
        logoSelectors.forEach(selector => {
          document.querySelectorAll(selector).forEach(el => {
            el.classList.add('notranslate');
            el.setAttribute('translate', 'no');
          });
        });

        // 텍스트 노드 실시간 교정: '캬노스' 오타 발견 즉시 '키아노스'로 복원
        this.healTypoInNode(document.body);
      };

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
          protectElements();
          this.observeDOM();
        });
      } else {
        protectElements();
        this.observeDOM();
      }
    }

    observeDOM() {
      // 구글 번역기가 텍스트를 비동기로 변경할 때 '캬노스' 발생 즉시 감지하여 교정
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === 'characterData') {
            this.healTextNode(mutation.target);
          } else if (mutation.type === 'childList') {
            mutation.addedNodes.forEach(node => {
              this.healTypoInNode(node);
            });
          }
        });
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
      });
    }

    healTypoInNode(rootNode) {
      if (!rootNode) return;
      if (rootNode.nodeType === Node.TEXT_NODE) {
        this.healTextNode(rootNode);
        return;
      }
      
      const walker = document.createTreeWalker(rootNode, NodeFilter.SHOW_TEXT, null, false);
      let currentNode = walker.nextNode();
      while (currentNode) {
        this.healTextNode(currentNode);
        currentNode = walker.nextNode();
      }
    }

    healTextNode(textNode) {
      if (textNode && textNode.nodeValue && textNode.nodeValue.includes('캬노스')) {
        textNode.nodeValue = textNode.nodeValue.replace(/캬노스/g, '키아노스');
      }
    }

    initGoogleTranslate() {
      // 1. Google Translate Init Callback
      window.googleTranslateElementInit = () => {
        /* global google */
        if (typeof google !== 'undefined' && google.translate) {
          new google.translate.TranslateElement({
            pageLanguage: 'ko',
            includedLanguages: 'ko,en,ja,zh-CN,es,fr,de,ru,ar',
            autoDisplay: false
          }, 'google_translate_element');

          // 초기 저장된 언어가 영어나 기타 언어일 경우 자동 적용
          if (this.currentLang && this.currentLang !== 'ko') {
            setTimeout(() => this.applyLanguage(this.currentLang), 600);
          }
        }
      };

      // 2. Hidden Div for Google Translate
      if (!document.getElementById('google_translate_element')) {
        const div = document.createElement('div');
        div.id = 'google_translate_element';
        div.style.display = 'none';
        document.body.appendChild(div);
      }

      // 3. Load Script
      if (!document.getElementById('google-translate-script')) {
        const script = document.createElement('script');
        script.id = 'google-translate-script';
        script.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
        script.async = true;
        document.head.appendChild(script);
      }
    }

    initUI() {
      const render = () => {
        if (document.getElementById('kyanosLangSelector')) return;

        const container = document.createElement('div');
        container.id = 'kyanosLangSelector';
        container.className = 'kyanos-lang-selector-wrap notranslate';
        container.setAttribute('translate', 'no');
        container.setAttribute('aria-label', 'Global Language Switcher');

        let buttonsHtml = '';
        SUPPORTED_LANGS.forEach(l => {
          const isActive = l.code === this.currentLang ? 'active' : '';
          buttonsHtml += `<button class="kyanos-lang-btn ${isActive}" data-lang="${l.code}" title="${l.title}">${l.label}</button>`;
        });

        container.innerHTML = `
          <span class="kyanos-lang-globe" title="키아노스 글로벌 다국어 번역기">🌐</span>
          ${buttonsHtml}
        `;

        // 헤더 내비게이션 바가 있으면 우측 액션 영역에 마운트, 없으면 플로팅
        const nav = document.querySelector('.nav-actions') || document.querySelector('.nav-links') || document.querySelector('header');
        if (nav) {
          nav.insertBefore(container, nav.firstChild);
        } else {
          container.classList.add('floating');
          document.body.appendChild(container);
        }

        // 이벤트 리스너 등록
        container.querySelectorAll('.kyanos-lang-btn').forEach(btn => {
          btn.addEventListener('click', (e) => {
            const lang = e.currentTarget.getAttribute('data-lang');
            this.switchLanguage(lang);
          });
        });
      };

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', render);
      } else {
        render();
      }
    }

    switchLanguage(langCode) {
      this.currentLang = langCode;
      localStorage.setItem(STORAGE_KEY, langCode);

      // UI 버튼 active 갱신
      document.querySelectorAll('.kyanos-lang-btn').forEach(btn => {
        if (btn.getAttribute('data-lang') === langCode) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });

      this.applyLanguage(langCode);
    }

    applyLanguage(langCode) {
      if (langCode === 'ko') {
        // 한국어 원문 복구: 구글 번역 쿠키 및 세션 완전 초기화 후 원본 복원
        this.resetGoogleTranslate();
        return;
      }

      // 구글 번역 셀렉트박스 조작
      const select = document.querySelector('.goog-te-combo');
      if (select) {
        select.value = langCode;
        select.dispatchEvent(new Event('change'));
      } else {
        // 셀렉터가 아직 생성되지 않았을 경우 쿠키 직접 주입 후 리프레시
        document.cookie = `googtrans=/ko/${langCode}; path=/; domain=${window.location.hostname}`;
        document.cookie = `googtrans=/ko/${langCode}; path=/;`;
        window.location.reload();
      }
    }

    resetGoogleTranslate() {
      // 1. 모든 구글 번역 쿠키 완전 삭제 (경로 및 서브도메인 포함)
      const hostname = window.location.hostname;
      const domains = [hostname, '.' + hostname, ''];
      const paths = ['/', window.location.pathname];

      domains.forEach(d => {
        paths.forEach(p => {
          const cookieBase = `googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=${p};`;
          document.cookie = d ? `${cookieBase} domain=${d};` : cookieBase;
        });
      });

      // 2. 로컬 스토리지에 'ko' 명시적 저장
      localStorage.setItem(STORAGE_KEY, 'ko');

      // 3. 상단 구글 번역 iframe 배너 닫기 시도
      try {
        const iframe = document.querySelector('iframe.goog-te-banner-frame');
        if (iframe) {
          const innerDoc = iframe.contentDocument || iframe.contentWindow.document;
          const closeBtn = innerDoc.querySelector('.goog-te-button button');
          if (closeBtn) closeBtn.click();
        }
      } catch (e) {}

      // 4. 셀렉트 박스 ko로 초기화 시도
      const select = document.querySelector('.goog-te-combo');
      if (select) {
        select.value = 'ko';
        select.dispatchEvent(new Event('change'));
      }

      // 5. 구글 번역 잔여 텍스트 오염을 원천 차단하고 순수한 원본을 로드하기 위해 즉각 리로드
      setTimeout(() => {
        window.location.reload();
      }, 50);
    }
  }

  // 인스턴스 초기화
  window.KyanosTranslator = new KyanosTranslator();

})();
