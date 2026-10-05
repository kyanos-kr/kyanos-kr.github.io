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
        container.className = 'kyanos-lang-selector-wrap';
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
        // 한국어 원문 복구: 구글 번역 쿠키 초기화 및 원본 복원
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
      // 쿠키 삭제 및 원본 복원
      document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      document.cookie = `googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=${window.location.hostname}`;
      
      const iframe = document.querySelector('iframe.goog-te-banner-frame');
      if (iframe) {
        const innerDoc = iframe.contentDocument || iframe.contentWindow.document;
        const closeBtn = innerDoc.querySelector('.goog-te-button button');
        if (closeBtn) closeBtn.click();
      }

      const select = document.querySelector('.goog-te-combo');
      if (select) {
        select.value = 'ko';
        select.dispatchEvent(new Event('change'));
      } else {
        window.location.reload();
      }
    }
  }

  // 인스턴스 초기화
  window.KyanosTranslator = new KyanosTranslator();

})();
