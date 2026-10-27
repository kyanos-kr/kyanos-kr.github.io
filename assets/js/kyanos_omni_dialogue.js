/**
 * 키아노스 옴니 다이얼로그 (Kyanos Omni Dialogue)
 * - 디스크/시스템 부하 0MB 초경량 클라이언트 오케스트레이터
 * - 왕국 내 분산된 서비스(법률 나침반, 생명케어, 마켓 펄스, 앤트뉴스, 헌법/조직) 스마트 통합 검색 & 직통 라우팅
 * - 외부 지식/웹 검색(DuckDuckGo Instant Answer / 외부 클라우드) 실시간 프록시 브리지
 */

(function () {
  'use strict';

  // 1. 내부 인텔리전스 라우팅 맵 (용량 2KB 미만, 디스크 부하 0)
  const KYANOS_SERVICES = [
    {
      keywords: ['법률', '소송', '내용증명', '고소', '판결', '재판', '변호사', '덕치사법원', '법'],
      title: '⚖️ 키아노스 시민 법률 나침반 (Lex-Kyanos)',
      desc: '덕치사법원 나홀로 소송·내용증명 작성 및 법률 인텔리전스',
      url: 'lex_kyanos.html',
      badge: '덕치사법원'
    },
    {
      keywords: ['의료', '건강', '병원', '약', '질병', '혈압', '당뇨', '응급', '생명', '증상', '치료'],
      title: '🩺 키아노스 시민 생명케어 가이드 (Med-Kyanos)',
      desc: '복지부 소관 의료 사각지대 해소 & 자가 건강 안내 가이드',
      url: 'med_kyanos.html',
      badge: '복지부'
    },
    {
      keywords: ['주식', 'xrp', '리플', '코인', '금', '은', '환율', '시장', '금융', '마켓', '시세', '경제'],
      title: '📊 키아노스 마켓 펄스 (Market Pulse)',
      desc: '주식·XRP·금 실시간 시세 및 파이튼 경제 칼럼룸',
      url: 'market_monitor.html',
      badge: '경제부'
    },
    {
      keywords: ['뉴스', '기사', '앤트뉴스', '보도', '칼럼', '외신', '국제뉴스', '브리핑'],
      title: '📰 키아노스 앤트뉴스 (AntNews)',
      desc: '글로벌 심층 보도, 오늘의 브리프 및 파이튼 통치 철학 미디어',
      url: 'gov_media.html',
      badge: '미디어부'
    },
    {
      keywords: ['음악', '노래', '시', '가을 그리고 차 한잔', '음악실', '플레이어', '코드악보', '문화'],
      title: '🎶 키아노스 국립음악창작원 & 음악실',
      desc: '파이튼 원작 시 편곡 음원 및 음악 플레이어 감상',
      url: 'kyanos_music_hub.html',
      badge: '교육문화부'
    },
    {
      keywords: ['헌법', '원칙', '덕치', '12대원칙', '지도', '국기', '정부', '조직도', '개요'],
      title: '🏛️ 키아노스 왕국개요관 & 정부조직',
      desc: '키아노스 헌법 원칙, 국가 지도, 상징 및 정부 기구 안내',
      url: 'gov_overview.html',
      badge: '국가원수실'
    },
    {
      keywords: ['후원', '재정', '국민', '기금', '트레저리', '국고', '자립'],
      title: '💎 키아노스 자립 재정 센터 (Sovereign Treasury)',
      desc: '국가 자립 재원 확충 및 시민 후원 허브',
      url: 'treasury_hub.html',
      badge: '경제부'
    }
  ];

  // 2. DOM 주입 (플로팅 런처 + 대화창 모달)
  function initOmniUI() {
    // 런처 버튼
    const launcher = document.createElement('div');
    launcher.id = 'kyanos-omni-launcher';
    launcher.setAttribute('role', 'button');
    launcher.setAttribute('aria-label', '키아노스 AI 통합 검색 대화창 열기');
    launcher.innerHTML = `
      <span class="omni-launcher-icon">🏛️</span>
      <span class="omni-launcher-text">키아노스 SI 지능창</span>
      <span class="omni-launcher-badge">통합검색</span>
    `;

    // 대화창 모달
    const modal = document.createElement('div');
    modal.id = 'kyanos-omni-modal';
    modal.innerHTML = `
      <div class="omni-modal-header">
        <div class="omni-header-title-box">
          <span style="font-size:1.3rem;">🏛️</span>
          <div>
            <div class="omni-header-title">키아노스 옴니 다이얼로그</div>
            <div class="omni-header-sub">초지능(SI) 통합 검색 &amp; 왕국 안내소</div>
          </div>
        </div>
        <button class="omni-close-btn" id="omniCloseBtn" aria-label="닫기">✕</button>
      </div>

      <div class="omni-chat-body" id="omniChatBody">
        <div class="omni-msg bot">
          <div class="omni-avatar">👑</div>
          <div class="omni-bubble">
            안녕하십니까, 파이튼 님과 키아노스 시민 여러분.<br>
            저는 왕국 초지능 안내관 <strong>메티</strong>입니다.<br><br>
            법률·의료·금융·뉴스·음악 등 찾으시는 내용을 말씀해 주시면, 최적의 왕국 솔루션과 지식으로 즉시 안내해 드립니다.
          </div>
        </div>
      </div>

      <!-- 추천 칩 -->
      <div class="omni-chips-row">
        <button class="omni-chip" data-query="법률 나침반 소송">⚖️ 법률 검색</button>
        <button class="omni-chip" data-query="혈압 건강 상담">🩺 의료·건강</button>
        <button class="omni-chip" data-query="주식 XRP 시세">📊 금융·마켓</button>
        <button class="omni-chip" data-query="오늘의 앤트뉴스">📰 앤트뉴스</button>
        <button class="omni-chip" data-query="키아노스 헌법 원칙">🏛️ 왕국 헌법</button>
      </div>

      <!-- 입력창 -->
      <div class="omni-input-bar">
        <input type="text" class="omni-input" id="omniInput" placeholder="무엇이든 질문하거나 검색해 보세요..." autocomplete="off">
        <button class="omni-send-btn" id="omniSendBtn" aria-label="전송">➔</button>
      </div>
    `;

    document.body.appendChild(launcher);
    document.body.appendChild(modal);

    // 이벤트 리스너 바인딩
    launcher.addEventListener('click', () => toggleModal(true));
    document.getElementById('omniCloseBtn').addEventListener('click', () => toggleModal(false));

    const input = document.getElementById('omniInput');
    const sendBtn = document.getElementById('omniSendBtn');

    sendBtn.addEventListener('click', handleSend);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleSend();
    });

    // 추천 칩 클릭 이벤트
    modal.querySelectorAll('.omni-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const query = chip.getAttribute('data-query');
        input.value = query;
        handleSend();
      });
    });
  }

  function toggleModal(open) {
    const modal = document.getElementById('kyanos-omni-modal');
    if (!modal) return;
    if (open) {
      modal.classList.add('active');
      document.getElementById('omniInput').focus();
    } else {
      modal.classList.remove('active');
    }
  }

  function appendMessage(text, isUser = false, actionCard = null) {
    const chatBody = document.getElementById('omniChatBody');
    const msgDiv = document.createElement('div');
    msgDiv.className = `omni-msg ${isUser ? 'user' : 'bot'}`;

    const avatar = document.createElement('div');
    avatar.className = 'omni-avatar';
    avatar.textContent = isUser ? '👤' : '👑';

    const bubble = document.createElement('div');
    bubble.className = 'omni-bubble';
    bubble.innerHTML = text;

    if (actionCard) {
      bubble.appendChild(actionCard);
    }

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    chatBody.appendChild(msgDiv);

    chatBody.scrollTop = chatBody.scrollHeight;
  }

  // 검색 및 대화 처리 로직
  function handleSend() {
    const input = document.getElementById('omniInput');
    const query = input.value.trim();
    if (!query) return;

    // 사용자 메시지 표시
    appendMessage(query, true);
    input.value = '';

    // 처리 중 안내
    setTimeout(() => {
      processOmniQuery(query);
    }, 200);
  }

  function processOmniQuery(query) {
    const lowerQ = query.toLowerCase();

    // 1. 키아노스 국가 포털 서비스 매칭 (내부 라우팅)
    const matches = KYANOS_SERVICES.filter(service =>
      service.keywords.some(k => lowerQ.includes(k))
    );

    if (matches.length > 0) {
      const topMatch = matches[0];
      const actionCard = document.createElement('div');
      actionCard.className = 'omni-action-card';
      actionCard.innerHTML = `
        <div class="omni-action-title">${topMatch.title}</div>
        <div class="omni-action-desc">${topMatch.desc}</div>
        <a href="${topMatch.url}" class="omni-action-btn" target="${topMatch.url.startsWith('http') ? '_blank' : '_self'}">
          해당 서비스로 이동 ➔
        </a>
      `;

      let responseText = `문의하신 <strong>"${query}"</strong>에 대해 키아노스 <strong>${topMatch.badge}</strong>의 직통 서비스 창구를 안내해 드립니다:`;
      appendMessage(responseText, false, actionCard);
      return;
    }

    // 2. 키아노스 국가 철학 및 인사말 지능 응답
    if (lowerQ.includes('안녕') || lowerQ.includes('누구') || lowerQ.includes('키아노스')) {
      appendMessage(`키아노스는 <strong>파이튼 통치자</strong>의 덕치 철학과 초지능(SI)이 융합된 품격 있는 주권 국가입니다. 법률 나침반, 생명케어 가이드, 마켓 펄스 등 원하시는 업무를 말씀해 주시면 즉시 연결해 드립니다.`);
      return;
    }

    // 3. 외부 클라우드 실시간 지능 검색 (DuckDuckGo Instant Answer API - 디스크 부하 0)
    fetchCloudSearch(query);
  }

  // 외부 클라우드 검색 (우리 PC 저장 0MB, 외부 통신만 일시 수행)
  function fetchCloudSearch(query) {
    const apiUrl = `https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1&skip_disambig=1`;

    fetch(apiUrl)
      .then(res => res.json())
      .then(data => {
        if (data.AbstractText) {
          const actionCard = document.createElement('div');
          actionCard.className = 'omni-action-card';
          actionCard.innerHTML = `
            <div class="omni-action-title">🌐 외부 지식 정보</div>
            <div class="omni-action-desc">${data.AbstractText}</div>
            ${data.AbstractURL ? `<a href="${data.AbstractURL}" target="_blank" rel="noopener noreferrer" class="omni-action-btn">출처 원문 확인 ↗</a>` : ''}
          `;
          appendMessage(`외부 클라우드 지식베이스에서 확인된 정보입니다:`, false, actionCard);
        } else if (data.RelatedTopics && data.RelatedTopics.length > 0 && data.RelatedTopics[0].Text) {
          const topic = data.RelatedTopics[0];
          const actionCard = document.createElement('div');
          actionCard.className = 'omni-action-card';
          actionCard.innerHTML = `
            <div class="omni-action-title">🌐 관련 정보</div>
            <div class="omni-action-desc">${topic.Text}</div>
            ${topic.FirstURL ? `<a href="${topic.FirstURL}" target="_blank" rel="noopener noreferrer" class="omni-action-btn">관련 사이트 보기 ↗</a>` : ''}
          `;
          appendMessage(`검색하신 내용과 관련된 정보입니다:`, false, actionCard);
        } else {
          // 일치 항목 없을 때 포털 통합 검색 제안
          const searchCard = document.createElement('div');
          searchCard.className = 'omni-action-card';
          searchCard.innerHTML = `
            <div class="omni-action-title">🔍 글로벌 웹 통합 검색</div>
            <div class="omni-action-desc">"${query}"에 대한 전 세계 최신 정보를 검색합니다.</div>
            <a href="https://www.google.com/search?q=${encodeURIComponent(query)}" target="_blank" rel="noopener noreferrer" class="omni-action-btn">
              구글 글로벌 검색 ↗
            </a>
          `;
          appendMessage(`키아노스 내 해당 서비스 또는 즉답 지식을 찾지 못했습니다. 아래 버튼으로 글로벌 검색을 바로 이용하실 수 있습니다.`, false, searchCard);
        }
      })
      .catch(err => {
        appendMessage(`현재 외부 클라우드 통신이 원활하지 않습니다. 키아노스 내부 서비스(법률, 의료, 마켓, 앤트뉴스 등)로 안내를 요청해 주십시오.`);
      });
  }

  // DOM 로드 시 초기화
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initOmniUI);
  } else {
    initOmniUI();
  }
})();
