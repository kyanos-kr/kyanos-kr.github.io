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
      keywords: ['보이스', 'voice', '음성', '받아쓰기', '입력', 'f9', '마이크', '위스퍼'],
      title: '🎙️ 키아노스 보이스 (KyanosFlow v1.0)',
      desc: 'PC 전용 무제한 로컬 음성 받아쓰기 (F9 누르고 말하기 → 손 떼면 자동 입력)',
      url: 'kyanos_voice_guide.html',
      badge: '소프트웨어연구원'
    },
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
    // 런처 그룹 컨테이너
    const hub = document.createElement('div');
    hub.className = 'kyanos-floating-hub';

    // 1) 키아노스 보이스 런처 버튼
    const voiceLauncher = document.createElement('div');
    voiceLauncher.id = 'kyanos-voice-launcher';
    voiceLauncher.setAttribute('role', 'button');
    voiceLauncher.setAttribute('aria-label', '키아노스 보이스 대화창 열기');
    voiceLauncher.innerHTML = `
      <span class="voice-launcher-icon">🎙️</span>
      <span class="voice-launcher-text">키아노스 보이스</span>
      <span class="voice-launcher-badge">실시간 음성</span>
    `;

    // 2) 키아노스 SI 지능창 런처 버튼
    const omniLauncher = document.createElement('div');
    omniLauncher.id = 'kyanos-omni-launcher';
    omniLauncher.setAttribute('role', 'button');
    omniLauncher.setAttribute('aria-label', '키아노스 AI 통합 검색 대화창 열기');
    omniLauncher.innerHTML = `
      <span class="omni-launcher-icon">🏛️</span>
      <span class="omni-launcher-text">키아노스 SI 지능창</span>
      <span class="omni-launcher-badge">통합검색</span>
    `;

    hub.appendChild(voiceLauncher);
    hub.appendChild(omniLauncher);

    // 키아노스 보이스 인터랙티브 창 모달
    const voiceModal = document.createElement('div');
    voiceModal.id = 'kyanos-voice-modal';
    voiceModal.innerHTML = `
      <div class="voice-modal-header">
        <div class="voice-modal-title">
          <span>🎙️ 키아노스 보이스 창</span>
          <span style="font-size:0.75rem; color:#92400e; font-weight:600;">(Kyanos Voice)</span>
        </div>
        <button class="voice-close-btn" id="voiceCloseBtn" aria-label="닫기">✕</button>
      </div>

      <!-- 상단 모드 전환 탭 -->
      <div class="voice-nav-tabs">
        <button class="voice-nav-tab active" id="tabVoiceLive">🎙️ 실시간 보이스 말하기</button>
        <button class="voice-nav-tab" id="tabVoiceGuide">💡 PC 전체 F9 사용법</button>
      </div>

      <div class="voice-modal-body">
        <!-- 1) 실시간 보이스 말하기 뷰 -->
        <div class="voice-view-panel active" id="panelVoiceLive">
          <div class="voice-live-mic-box">
            <button class="voice-mic-main-btn" id="voiceMicMainBtn" title="마이크 클릭하여 말하기 시작" type="button">
              <span class="mic-icon">🎙️</span>
              <span class="mic-wave"></span>
            </button>
            <div class="voice-mic-status" id="voiceMicStatus">
              마이크를 누르고 말씀해 보세요
            </div>
            <div class="voice-mic-substatus" id="voiceMicSubstatus">
              (한국어 음성을 실시간으로 정확하게 글자로 적어드립니다)
            </div>
          </div>

          <div class="voice-result-box">
            <div class="voice-result-header">
              <span>📝 실시간 인식 텍스트</span>
              <span class="voice-char-count" id="voiceCharCount">0자</span>
            </div>
            <textarea class="voice-result-textarea" id="voiceResultArea" placeholder="마이크를 누르고 말씀하시면 여기에 실시간으로 글자가 작성됩니다..."></textarea>
          </div>

          <div class="voice-action-toolbar">
            <button class="voice-action-btn copy" id="voiceCopyBtn" type="button" title="클립보드에 복사">
              📋 전체 복사
            </button>
            <button class="voice-action-btn send-omni" id="voiceSendOmniBtn" type="button" title="키아노스 SI 지능창으로 전송">
              🏛️ SI 지능창에 질문
            </button>
            <button class="voice-action-btn clear" id="voiceClearBtn" type="button" title="지우기">
              🧹 지우기
            </button>
          </div>
          <div class="voice-toast-msg" id="voiceToastMsg"></div>
        </div>

        <!-- 2) PC 전체 F9 사용법 뷰 -->
        <div class="voice-view-panel" id="panelVoiceGuide">
          <div class="voice-step-card">
            <div class="voice-step-num">STEP 1</div>
            <div class="voice-step-text">글 쓸 곳 커서 클릭 (한글, 메모장, 카톡 등)</div>
          </div>
          <div class="voice-step-card highlight">
            <div class="voice-step-num" style="color:#1d4ed8;">STEP 2 (핵심)</div>
            <div class="voice-step-text">
              <span class="voice-key-badge">F9</span> 키를 <strong>누른 채로</strong> 말씀하세요
            </div>
          </div>
          <div class="voice-step-card">
            <div class="voice-step-num">STEP 3</div>
            <div class="voice-step-text">
              말씀 후 <span class="voice-key-badge">F9</span> 키에서 손 떼면 <strong>자동 타이핑!</strong>
            </div>
          </div>
          <div class="voice-traffic-lights">
            <span>🔵 파랑: 대기</span>
            <span>🔴 빨강: 녹음 중</span>
            <span>🟠 주황: 입력 중</span>
          </div>
          <div style="font-size:0.76rem; color:#78350f; line-height:1.4;">
            • 말하던 중 취소: <strong>[Esc]</strong> 키<br>
            • 단축키 변경/설정: 우측 하단 마이크 트레이 <strong>우클릭</strong>
          </div>
          <a href="kyanos_voice_guide.html" target="_blank" class="voice-full-link-btn">
            공식 전체 가이드 열기 ↗
          </a>
        </div>
      </div>
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
            법률·의료·금융·뉴스·음악 및 <strong>키아노스 보이스</strong> 등 찾으시는 내용을 말씀해 주시면, 최적의 왕국 솔루션과 지식으로 즉시 안내해 드립니다.
          </div>
        </div>
      </div>

      <!-- 추천 칩 -->
      <div class="omni-chips-row">
        <button class="omni-chip" style="background:rgba(254,240,138,0.25); border-color:#eab308; color:#fde047; font-weight:700;" data-query="키아노스 보이스 사용법">🎙️ 키아노스 보이스</button>
        <button class="omni-chip" data-query="법률 나침반 소송">⚖️ 법률 검색</button>
        <button class="omni-chip" data-query="혈압 건강 상담">🩺 의료·건강</button>
        <button class="omni-chip" data-query="주식 XRP 시세">📊 금융·마켓</button>
        <button class="omni-chip" data-query="오늘의 앤트뉴스">📰 앤트뉴스</button>
        <button class="omni-chip" data-query="키아노스 헌법 원칙">🏛️ 왕국 헌법</button>
      </div>

      <!-- 입력창 -->
      <div class="omni-input-bar">
        <input type="text" class="omni-input" id="omniInput" placeholder="무엇이든 질문하거나 검색해 보세요..." autocomplete="off">
        <button class="omni-mic-btn" id="omniMicBtn" title="음성으로 질문하기" aria-label="음성 마이크" type="button">🎙️</button>
        <button class="omni-send-btn" id="omniSendBtn" aria-label="전송" type="button">➔</button>
      </div>
    `;

    document.body.appendChild(hub);
    document.body.appendChild(voiceModal);
    document.body.appendChild(modal);

    // 이벤트 리스너 바인딩
    voiceLauncher.addEventListener('click', () => {
      toggleModal(false);
      toggleVoiceModal(true);
    });
    document.getElementById('voiceCloseBtn').addEventListener('click', () => toggleVoiceModal(false));

    omniLauncher.addEventListener('click', () => {
      toggleVoiceModal(false);
      toggleModal(true);
    });
    document.getElementById('omniCloseBtn').addEventListener('click', () => toggleModal(false));

    // 보이스 모달 탭 전환 이벤트
    const tabVoiceLive = document.getElementById('tabVoiceLive');
    const tabVoiceGuide = document.getElementById('tabVoiceGuide');
    const panelVoiceLive = document.getElementById('panelVoiceLive');
    const panelVoiceGuide = document.getElementById('panelVoiceGuide');

    tabVoiceLive.addEventListener('click', () => {
      tabVoiceLive.classList.add('active');
      tabVoiceGuide.classList.remove('active');
      panelVoiceLive.classList.add('active');
      panelVoiceGuide.classList.remove('active');
    });

    tabVoiceGuide.addEventListener('click', () => {
      tabVoiceGuide.classList.add('active');
      tabVoiceLive.classList.remove('active');
      panelVoiceGuide.classList.add('active');
      panelVoiceLive.classList.remove('active');
    });

    // 실시간 음성인식(Web Speech API) 초기화
    setupSpeechRecognition();

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

  // 실시간 음성 인식(Web Speech API) 엔진
  function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const micBtn = document.getElementById('voiceMicMainBtn');
    const micStatus = document.getElementById('voiceMicStatus');
    const micSubstatus = document.getElementById('voiceMicSubstatus');
    const resultArea = document.getElementById('voiceResultArea');
    const charCount = document.getElementById('voiceCharCount');
    const copyBtn = document.getElementById('voiceCopyBtn');
    const clearBtn = document.getElementById('voiceClearBtn');
    const sendOmniBtn = document.getElementById('voiceSendOmniBtn');
    const toastMsg = document.getElementById('voiceToastMsg');
    const omniMicBtn = document.getElementById('omniMicBtn');
    const omniInput = document.getElementById('omniInput');

    function showToast(msg) {
      if (!toastMsg) return;
      toastMsg.textContent = msg;
      toastMsg.classList.add('show');
      setTimeout(() => toastMsg.classList.remove('show'), 2500);
    }

    function updateCharCount() {
      if (charCount && resultArea) {
        charCount.textContent = `${resultArea.value.length}자`;
      }
    }

    if (resultArea) {
      resultArea.addEventListener('input', updateCharCount);
    }

    if (clearBtn && resultArea) {
      clearBtn.addEventListener('click', () => {
        resultArea.value = '';
        updateCharCount();
        showToast('텍스트가 지워졌습니다.');
      });
    }

    if (copyBtn && resultArea) {
      copyBtn.addEventListener('click', () => {
        if (!resultArea.value.trim()) {
          showToast('복사할 내용이 없습니다.');
          return;
        }
        navigator.clipboard.writeText(resultArea.value).then(() => {
          showToast('📋 복사 완료! 한글/메모장에 Ctrl+V 하세요.');
        }).catch(() => {
          resultArea.select();
          document.execCommand('copy');
          showToast('📋 복사되었습니다.');
        });
      });
    }

    if (sendOmniBtn && resultArea) {
      sendOmniBtn.addEventListener('click', () => {
        const text = resultArea.value.trim();
        if (!text) {
          showToast('전송할 음성 텍스트가 없습니다.');
          return;
        }
        toggleVoiceModal(false);
        toggleModal(true);
        if (omniInput) {
          omniInput.value = text;
          handleSend();
        }
      });
    }

    if (!SpeechRecognition) {
      if (micStatus) {
        micStatus.textContent = '현재 브라우저가 음성 인식을 지원하지 않습니다.';
      }
      if (micSubstatus) {
        micSubstatus.textContent = 'Microsoft Edge 또는 Chrome 브라우저에서 이용해 주십시오.';
      }
      if (micBtn) {
        micBtn.disabled = true;
        micBtn.style.opacity = '0.5';
      }
      if (omniMicBtn) {
        omniMicBtn.style.display = 'none';
      }
      return;
    }

    // 보이스 모달 전용 음성 인식기
    const recognition = new SpeechRecognition();
    recognition.lang = 'ko-KR';
    recognition.interimResults = true;
    recognition.continuous = true;

    let isRecording = false;
    let hasError = false;
    let baseTranscript = '';

    function startRecognitionWithPermission() {
      if (!isRecording) {
        hasError = false;
        baseTranscript = resultArea.value ? resultArea.value + (resultArea.value.endsWith(' ') || resultArea.value.endsWith('\n') ? '' : ' ') : '';
        try {
          recognition.start();
        } catch (e) {
          console.warn('Recognition start error:', e);
        }
      }
    }

    micBtn.addEventListener('click', () => {
      if (isRecording) {
        recognition.stop();
        return;
      }

      hasError = false;
      // Edge 브라우저 마이크 장치 및 권한 사전 정밀 점검
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        micStatus.style.color = '#1d4ed8';
        micStatus.textContent = '🎙️ 마이크 연결 및 권한 확인 중...';
        micSubstatus.textContent = '브라우저 상단에 "마이크 허용" 창이 뜨면 [허용]을 눌러주세요.';

        navigator.mediaDevices.getUserMedia({ audio: true })
          .then((stream) => {
            // 권한 및 마이크 장치 확인 성공 시 스트림 해제 후 recognition 시작
            stream.getTracks().forEach(track => track.stop());
            startRecognitionWithPermission();
          })
          .catch((err) => {
            console.warn('getUserMedia error:', err);
            hasError = true;
            isRecording = false;
            micBtn.classList.remove('recording');
            micStatus.style.color = '#dc2626';

            if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
              micStatus.textContent = '🔌 연결된 마이크 장치가 감지되지 않습니다.';
              micSubstatus.innerHTML = '현재 PC에 마이크(이어폰·헤드셋·무선마이크)가 꽂혀 있지 않습니다. <strong>마이크 연결 후 다시 눌러주세요!</strong>';
            } else if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
              micStatus.textContent = '🔒 마이크 접근 권한이 차단되어 있습니다.';
              micSubstatus.innerHTML = 'Edge 주소창 좌측 <strong>[자물쇠🔒]</strong> 클릭 ➔ <strong>[마이크: 허용]</strong>으로 설정해 주세요.';
            } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
              micStatus.textContent = '⚠️ 마이크가 다른 프로그램에서 사용 중입니다.';
              micSubstatus.textContent = '다른 녹음 앱이나 통화 프로그램을 종료한 후 다시 시도해 주세요.';
            } else {
              // 기타 예외 시에는 음성인식 직접 시도
              hasError = false;
              startRecognitionWithPermission();
            }
          });
      } else {
        startRecognitionWithPermission();
      }
    });

    recognition.onstart = () => {
      hasError = false;
      isRecording = true;
      micBtn.classList.add('recording');
      micStatus.textContent = '🔴 듣고 있습니다... 편하게 말씀하세요!';
      micStatus.style.color = '#dc2626';
      micSubstatus.textContent = '말씀이 끝나면 마이크 버튼을 다시 눌러 완료하세요.';
    };

    recognition.onresult = (event) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          final += event.results[i][0].transcript;
        } else {
          interim += event.results[i][0].transcript;
        }
      }

      if (final) {
        baseTranscript += final + ' ';
      }

      resultArea.value = baseTranscript + interim;
      resultArea.scrollTop = resultArea.scrollHeight;
      updateCharCount();
    };

    recognition.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
      hasError = true;
      isRecording = false;
      micBtn.classList.remove('recording');
      micStatus.style.color = '#dc2626';

      if (event.error === 'not-allowed') {
        micStatus.textContent = '🔒 마이크 접근 권한이 필요합니다.';
        micSubstatus.innerHTML = 'Edge 브라우저 주소창 좌측 <strong>[자물쇠🔒]</strong> 클릭 ➔ <strong>[마이크: 허용]</strong>으로 설정해 주세요.';
      } else if (event.error === 'no-speech') {
        micStatus.textContent = '소리가 감지되지 않았습니다.';
        micSubstatus.textContent = '마이크에 가까이 대고 조금 더 큰 목소리로 말씀해 보세요.';
      } else if (event.error === 'audio-capture') {
        micStatus.textContent = '🔌 마이크 입력 장치를 찾을 수 없습니다.';
        micSubstatus.innerHTML = 'PC에 마이크(이어폰·헤드셋·무선마이크)가 연결되어 있는지 확인해 주세요.';
      } else if (event.error === 'network') {
        micStatus.textContent = '음성 변환 네트워크 일시 지연';
        micSubstatus.textContent = '잠시 후 다시 마이크 버튼을 눌러 시도해 주세요.';
      } else {
        micStatus.textContent = `음성 안내 (${event.error})`;
        micSubstatus.textContent = '마이크 연결 상태를 확인하신 후 다시 눌러보세요.';
      }
    };

    recognition.onend = () => {
      isRecording = false;
      micBtn.classList.remove('recording');
      if (!hasError) {
        micStatus.textContent = '마이크를 누르고 말씀해 보세요';
        micStatus.style.color = '#78350f';
        micSubstatus.textContent = '말씀하신 내용이 아래 텍스트 창에 완성되었습니다.';
      }
    };

    // 옴니 다이얼로그 전용 인라인 음성 검색
    if (omniMicBtn && omniInput) {
      const omniRecognition = new SpeechRecognition();
      omniRecognition.lang = 'ko-KR';
      omniRecognition.interimResults = true;
      omniRecognition.continuous = false;
      let isOmniRec = false;

      omniMicBtn.addEventListener('click', () => {
        if (isOmniRec) {
          omniRecognition.stop();
        } else {
          try {
            omniRecognition.start();
          } catch (e) {
            console.warn(e);
          }
        }
      });

      omniRecognition.onstart = () => {
        isOmniRec = true;
        omniMicBtn.classList.add('recording');
        omniMicBtn.textContent = '🔴';
        omniInput.placeholder = '말씀하세요... (음성 듣는 중)';
      };

      omniRecognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
        omniInput.value = transcript;
      };

      omniRecognition.onerror = () => {
        isOmniRec = false;
        omniMicBtn.classList.remove('recording');
        omniMicBtn.textContent = '🎙️';
        omniInput.placeholder = '무엇이든 질문하거나 검색해 보세요...';
      };

      omniRecognition.onend = () => {
        isOmniRec = false;
        omniMicBtn.classList.remove('recording');
        omniMicBtn.textContent = '🎙️';
        omniInput.placeholder = '무엇이든 질문하거나 검색해 보세요...';
        if (omniInput.value.trim()) {
          handleSend();
        }
      };
    }
  }

  function toggleVoiceModal(open) {
    const modal = document.getElementById('kyanos-voice-modal');
    if (!modal) return;
    if (open) {
      modal.classList.add('active');
    } else {
      modal.classList.remove('active');
    }
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
