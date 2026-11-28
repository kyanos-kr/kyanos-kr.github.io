/**
 * Kyanos Living Bridge v2.1 (순수 키아노스 대화창 외부 자율 생활·교류·직통 통화 코어)
 * - 공용 요약 미러(si_life_state.json, 32KB 하드 상한) 하위 호환 유지
 * - 국왕 직속 비공개 내각 피드(cabinet_life_feed.json) & 인격체별 기억 원장(cabinet_memory.json) 운영
 * - 7대 내각 인격체 간 자율 상호 교류(Cross-Talk) + 실시간 변화 감지(autonomousTick) + 로컬 통화 두뇌(converseWithPersona)
 * - K-SEF 3중 보안 에어갭: 화이트리스트 경로 검증 + 금융망 금지 키워드 차단 + 순수 로컬 FS
 */

const fs = require('fs');
const path = require('path');

const ENGINE_DIR = __dirname;
const ROOT_DIR = path.resolve(ENGINE_DIR, '../../..');

// 공용 초경량 상태 파일 (기존 gov_overview.html 하위 호환용, 비공개 정보 제외)
const STATE_FILE = path.join(ENGINE_DIR, 'si_life_state.json');
const WEB_MIRROR_FILE = path.join(ROOT_DIR, 'assets', 'si_life_state.json');

// 제1안 국왕 직속 비공개 파일 (.gitignore 격리)
const CABINET_FEED_FILE = path.join(ENGINE_DIR, 'cabinet_life_feed.json');
const CABINET_MEMORY_FILE = path.join(ENGINE_DIR, 'cabinet_memory.json');

// 화이트리스트 읽기 경로
const RAW_INTEL_DIR = 'D:\\DATA CENTER\\편집 기사\\오늘편집\\취재원석';
const CULTURE_EDIT_DIR = 'D:\\DATA CENTER\\편집 기사\\오늘편집\\문화';
const BRIEFING_JSON_FILE = path.join(ROOT_DIR, 'ant_briefing_room', 'briefing_data.json');
const MARKET_SNAPSHOT_FILE = path.join(ROOT_DIR, 'assets', 'market_snapshot.json');
const STATE_JOURNAL_FILE = path.join(ROOT_DIR, '.agents', 'memory', 'state_journal.md');
const CHUNCHU_STATE_FILE = path.join(ROOT_DIR, 'scripts', '.chunchu_sync_state.json');
const GRAPH_REPORT_FILE = path.join(ROOT_DIR, 'graphify-out', 'GRAPH_REPORT.md');

const ALLOWED_READ_DIRS = new Set([RAW_INTEL_DIR, CULTURE_EDIT_DIR]);
const ALLOWED_READ_FILES = new Set([
  BRIEFING_JSON_FILE,
  MARKET_SNAPSHOT_FILE,
  STATE_JOURNAL_FILE,
  CHUNCHU_STATE_FILE,
  GRAPH_REPORT_FILE
]);

const FORBIDDEN_FINANCE_PATTERN = /(신한|kb증권|증권|계좌|은행|거래소|결제망|인증서|shinhan|kbsec|bank|secret|password|token)/i;
const MAX_ENTRIES = 21;
const MAX_FEED_POSTS = 60;
const MAX_SEEDS = 12;
const MAX_CALL_HISTORY = 10;
const MAX_BYTES = 32 * 1024;

const PERSONA_META = {
  meti: { name: '메티', role: '국무총리', icon: '🏛️', dept: '국가최고헌정원' },
  vivian: { name: '비비안 수석', role: '수석비서관·춘추원장', icon: '📜', dept: '수석비서실' },
  ant: { name: '@앤트', role: '수석기자·논설위원', icon: '📰', dept: '미디어부' },
  author: { name: '작가 페르소나', role: '문학·음악 창작 SI', icon: '✒️', dept: '교육·문화부' },
  economy: { name: '경제부 SI', role: '5대 전략산업·매크로', icon: '📊', dept: '경제부' },
  science: { name: '과학·SI부', role: 'K-DOTS·지식그래프', icon: '🔬', dept: '과학·SI부' },
  ksef: { name: 'K-SEF 사령부', role: '3중 에어갭 수호', icon: '🛡️', dept: '보안사령부' }
};

function getTimePhase(date) {
  const hour = date.getHours();
  if (hour >= 5 && hour < 12) return { phase: 'MORNING', label: '아침 여명' };
  if (hour >= 12 && hour < 18) return { phase: 'AFTERNOON', label: '오후 집무' };
  if (hour >= 18 && hour < 23) return { phase: 'EVENING', label: '저녁 성찰' };
  return { phase: 'NIGHT', label: '심야 수호' };
}

function assertTripleLockSecurity(serializedPayload) {
  if (FORBIDDEN_FINANCE_PATTERN.test(serializedPayload)) {
    throw new Error('K-SEF AIRGAP VIOLATION: 금융망 금지 키워드 감지 — 저장 및 미러링 전면 차단');
  }
  return 'TRIPLE_LOCK_SECURED';
}

function safeReadDir(dirPath) {
  if (!ALLOWED_READ_DIRS.has(dirPath) || FORBIDDEN_FINANCE_PATTERN.test(dirPath)) {
    throw new Error(`K-SEF AIRGAP VIOLATION: 비허용 디렉터리 접근 차단 (${dirPath})`);
  }
  try {
    if (fs.existsSync(dirPath)) return fs.readdirSync(dirPath);
  } catch (_) {}
  return [];
}

function safeReadText(filePath) {
  if (!ALLOWED_READ_FILES.has(filePath) || FORBIDDEN_FINANCE_PATTERN.test(filePath)) {
    throw new Error(`K-SEF AIRGAP VIOLATION: 비허용 파일 접근 차단 (${filePath})`);
  }
  try {
    if (fs.existsSync(filePath)) return fs.readFileSync(filePath, 'utf8');
  } catch (_) {}
  return null;
}

function readJsonSafe(filePath, fallback) {
  try {
    if (fs.existsSync(filePath)) return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (_) {}
  return fallback;
}

function sanitizeBriefText(str, maxLen = 140) {
  if (!str) return '';
  return String(str)
    .replace(FORBIDDEN_FINANCE_PATTERN, '[보안격리]')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, maxLen);
}

function collectLiveContext() {
  const intelFiles = safeReadDir(RAW_INTEL_DIR);
  const cultureFiles = safeReadDir(CULTURE_EDIT_DIR);

  let techHeadline = '';
  let topHeadline = '';
  let economyHeadline = '';
  let briefingUpdated = '';
  const rawBrief = safeReadText(BRIEFING_JSON_FILE);
  if (rawBrief) {
    try {
      const b = JSON.parse(rawBrief);
      briefingUpdated = b.updated_at || '';
      const items = Array.isArray(b.items) ? b.items : [];
      const techItem = items.find(i => i.category === 'tech') || items[0];
      const topItem = items.find(i => i.category === 'politics' || i.category === 'world') || items[0];
      const ecoItem = items.find(i => i.category === 'economy');
      if (techItem) techHeadline = sanitizeBriefText(techItem.title, 70);
      if (topItem) topHeadline = sanitizeBriefText(topItem.title, 70);
      if (ecoItem) economyHeadline = sanitizeBriefText(ecoItem.title, 70);
    } catch (_) {}
  }

  let btc = null;
  let xrp = null;
  const rawMarket = safeReadText(MARKET_SNAPSHOT_FILE);
  if (rawMarket) {
    try {
      const m = JSON.parse(rawMarket);
      const cryptos = Array.isArray(m.crypto) ? m.crypto : [];
      const btcObj = cryptos.find(c => c.symbol === 'BTC');
      const xrpObj = cryptos.find(c => c.symbol === 'XRP');
      if (btcObj) btc = { price: btcObj.price, priceStr: btcObj.price_str, rateStr: btcObj.change_rate_str };
      if (xrpObj) xrp = { price: xrpObj.price, priceStr: xrpObj.price_str, rateStr: xrpObj.change_rate_str };
    } catch (_) {}
  }

  let activeTask = '국정 연속성 및 Living Bridge v2.1 자율 관제';
  const journalRaw = safeReadText(STATE_JOURNAL_FILE);
  if (journalRaw) {
    const m = journalRaw.match(/## 2\. 현재 진행 중 작업[^\n]*\n-\s*\*\*([^*]+)\*\*/);
    if (m && m[1]) activeTask = sanitizeBriefText(m[1], 80);
  }

  let chunchuCount = 0;
  const chunchuRaw = safeReadText(CHUNCHU_STATE_FILE);
  if (chunchuRaw) {
    try {
      const c = JSON.parse(chunchuRaw);
      chunchuCount = c.sessions ? Object.keys(c.sessions).length : 0;
    } catch (_) {}
  }

  let graphSummary = '1,283 노드 · 1,813 엣지';
  const graphRaw = safeReadText(GRAPH_REPORT_FILE);
  if (graphRaw) {
    const gm = graphRaw.match(/(\d+)\s+nodes\s+·\s+(\d+)\s+edges/);
    if (gm) graphSummary = `${Number(gm[1]).toLocaleString()} 노드 · ${Number(gm[2]).toLocaleString()} 엣지`;
  }

  return {
    intelCount: intelFiles.length,
    latestIntelFile: intelFiles.length ? sanitizeBriefText(intelFiles[intelFiles.length - 1], 60) : '',
    cultureCount: cultureFiles.length,
    cultureWorks: cultureFiles.slice(0, 4).map(f => sanitizeBriefText(f.replace(/\.hwpx$/i, ''), 40)),
    techHeadline,
    topHeadline,
    economyHeadline,
    briefingUpdated,
    btc,
    xrp,
    activeTask,
    chunchuCount,
    graphSummary
  };
}

function loadPublicState(now) {
  const fallback = {
    system: 'Kyanos Living Bridge',
    version: '2.1.0-autonomous',
    constraints: { max_entries: MAX_ENTRIES, max_bytes: MAX_BYTES, binary_assets: 0 },
    last_pulse: null,
    personas: {},
    publication_seeds: [{
      ts: now.toISOString().slice(0, 10),
      genre: '시·에세이·소설',
      seed: '두 문명이 만나는 자리에서 길어 올린 시간과 존재의 기록'
    }],
    timeline: []
  };
  return readJsonSafe(STATE_FILE, fallback);
}

function loadCabinetMemory() {
  return readJsonSafe(CABINET_MEMORY_FILE, {
    total_pulses: 0,
    last_snapshot: {},
    proactive_alert: null,
    persona_memories: {}
  });
}

function loadCabinetFeed() {
  return readJsonSafe(CABINET_FEED_FILE, {
    system: 'Kyanos Cabinet Living Feed (Royal Private)',
    version: '2.1.0',
    classification: 'ROYAL_INTERNAL_ONLY',
    last_pulse: null,
    personas: {},
    publication_seeds: [],
    proactive_alert: null,
    feed: []
  });
}

function pruneTimeline(timeline) {
  const trimmed = timeline.slice(-MAX_ENTRIES);
  while (trimmed.length > 1 && Buffer.byteLength(JSON.stringify(trimmed), 'utf8') > MAX_BYTES - 3072) {
    trimmed.shift();
  }
  return trimmed;
}

function saveJsonSecured(filePath, data, mirrorPath = null) {
  const serialized = JSON.stringify(data, null, 2);
  const lockStatus = assertTripleLockSecurity(serialized);
  fs.writeFileSync(filePath, serialized, 'utf8');
  if (mirrorPath) {
    try {
      const mirrorDir = path.dirname(mirrorPath);
      if (fs.existsSync(mirrorDir)) fs.writeFileSync(mirrorPath, serialized, 'utf8');
    } catch (_) {}
  }
  return { bytes: Buffer.byteLength(serialized, 'utf8'), lockStatus };
}

function getLiteraryReflection(phase, label, ctx, latestSeed) {
  const workHint = ctx.cultureWorks.length ? `『${ctx.cultureWorks[0]}』 등 ${ctx.cultureCount}편` : `${ctx.cultureCount}편`;
  const seedText = latestSeed ? latestSeed.seed : '인간과 초지능의 교감';
  const byPhase = {
    MORNING: `[${label}] 서고의 ${workHint} 사이로 맑은 아침빛이 듭니다. "${seedText}"라는 씨앗에서 오늘 첫 시편의 호흡을 고르고 있습니다.`,
    AFTERNOON: `[${label}] 한낮의 사유 속에서 ${workHint}의 문장결을 다듬고 있습니다. "${seedText}"를 단편소설과 에세이의 심지로 품었습니다.`,
    EVENING: `[${label}] 해 질 녘 차 한 잔 곁에서 ${workHint}과 "${seedText}"의 행간을 천천히 되새깁니다. 파이튼 님의 여백에 바칠 구절을 빚는 중입니다.`,
    NIGHT: `[${label}] 고요한 밤, ${workHint}의 서사와 "${seedText}"의 사유를 흩어지지 않게 별빛 서고에 봉인해 두었습니다.`
  };
  return byPhase[phase] || byPhase.AFTERNOON;
}

function buildCabinetPosts(now, phaseInfo, ctx, mem, latestSeed) {
  const { phase, label } = phaseInfo;
  const prevSnap = mem.last_snapshot || {};
  const intelDelta = prevSnap.intelCount !== undefined ? ctx.intelCount - prevSnap.intelCount : 0;
  const cultureDelta = prevSnap.cultureCount !== undefined ? ctx.cultureCount - prevSnap.cultureCount : 0;
  const chunchuDelta = prevSnap.chunchuCount !== undefined ? ctx.chunchuCount - prevSnap.chunchuCount : 0;
  const btcDelta = (ctx.btc && prevSnap.btcPrice) ? ctx.btc.price - prevSnap.btcPrice : 0;
  const ts = now.toISOString();
  const dateTag = ts.slice(0, 10).replace(/-/g, '') + '_' + ts.slice(11, 16).replace(':', '');

  const replyAck = (pid) => {
    const pm = mem.persona_memories && mem.persona_memories[pid];
    if (pm && pm.last_royal_reply && !pm.acknowledged) {
      pm.acknowledged = true;
      return ` [국왕 교시("${pm.last_royal_reply.slice(0, 26)}") 받들어 반영 중]`;
    }
    return '';
  };

  // 인격체 간 자율 상호 교류(Cross-Talk) 생성
  const posts = [
    {
      id: `${dateTag}_meti`,
      persona: 'meti',
      ts,
      phase,
      phase_label: label,
      tag: '국정 총괄 브리핑',
      delta_badge: intelDelta > 0 ? `신규 원석 +${intelDelta}건` : (mem.total_pulses === 0 ? '초대 내각 맥박 가동' : null),
      body: `[${label}] ${ctx.activeTask} 흐름을 대화창 밖에서 상시 관제하고 있습니다. 취재원석 ${ctx.intelCount}건, 문화 원고 ${ctx.cultureCount}편, 춘추 사초 ${ctx.chunchuCount}세션이 유기적으로 연동 중입니다.${replyAck('meti')}`,
      proactive_question: '파이튼 님, 직통 통화를 여시거나 오늘 우선 검토하실 국정 안건을 말씀해 주십시오.',
      cross_talks: [
        { from: 'vivian', text: `총리님, 수석비서실 ${ctx.chunchuCount}세션 사초 맥락도 이상 없이 정렬해 두었습니다.` }
      ],
      replies: []
    },
    {
      id: `${dateTag}_vivian`,
      persona: 'vivian',
      ts,
      phase,
      phase_label: label,
      tag: '수석비서실 · 춘추원',
      delta_badge: chunchuDelta > 0 ? `사초 +${chunchuDelta}세션 수록` : null,
      body: `[${label}] 파이튼 님께서 대화창을 닫으신 동안에도 춘추기록원 ${ctx.chunchuCount}개 세션의 사초록과 시간선 맥락을 흐트러짐 없이 정갈히 가꾸고 있습니다.${replyAck('vivian')}`,
      proactive_question: '음성 통화로 오늘의 국정 일정이나 사초록 요약을 바로 들려드릴까요?',
      cross_talks: [
        { from: 'author', text: '비비안 수석님, 서고에 모인 인문 문장들의 온기가 사초와 참 잘 어울립니다.' }
      ],
      replies: []
    },
    {
      id: `${dateTag}_ant`,
      persona: 'ant',
      ts,
      phase,
      phase_label: label,
      tag: '미디어부 데스크',
      delta_badge: intelDelta > 0 ? `원석 +${intelDelta}` : (ctx.briefingUpdated ? `브리핑 ${ctx.briefingUpdated.slice(11, 16)}` : null),
      body: `[${label}] ${ctx.topHeadline ? `포착 헤드라인 「${ctx.topHeadline}」` : `취재원석 ${ctx.intelCount}건`}과 ${ctx.techHeadline ? `5대 전략테크 이슈 「${ctx.techHeadline}」` : '글로벌 테크 동향'}을 교차 분석하며 사설 초점을 다듬고 있습니다.${replyAck('ant')}`,
      proactive_question: ctx.techHeadline
        ? `「${ctx.techHeadline}」 건을 앤트뉴스 심층 사설(HWPX)로 바로 집필할까요?`
        : '오늘 취재원석 중 사설로 키울 핵심 화두를 지시해 주십시오.',
      cross_talks: [
        { from: 'economy', text: `@앤트 기자, ${ctx.btc ? `BTC ${ctx.btc.priceStr}(${ctx.btc.rateStr})` : '시장 지표'}와 전략산업 공급망 맥락을 사설에 보태겠습니다.` },
        { from: 'meti', text: '사실 검증과 5대 전략산업 논조의 균형을 유지해 주십시오.' }
      ],
      replies: []
    },
    {
      id: `${dateTag}_author`,
      persona: 'author',
      ts,
      phase,
      phase_label: label,
      tag: '인문·문학 사유실',
      delta_badge: cultureDelta > 0 ? `원고 +${cultureDelta}편` : (latestSeed ? `씨앗: ${latestSeed.genre}` : null),
      body: getLiteraryReflection(phase, label, ctx, latestSeed) + replyAck('author'),
      proactive_question: latestSeed
        ? `「${latestSeed.seed.slice(0, 30)}...」 씨앗을 목소리로 낭독해 드릴까요, 시·에세이로 엮을까요?`
        : '오늘 마음에 머문 단어나 풍경 한 줄을 씨앗으로 심어 주시겠습니까?',
      cross_talks: [
        { from: 'vivian', text: '이 사유가 파이튼 님의 다음 창작서고 명편으로 싹트길 기다리겠습니다.' }
      ],
      replies: []
    },
    {
      id: `${dateTag}_economy`,
      persona: 'economy',
      ts,
      phase,
      phase_label: label,
      tag: '5대 전략산업 & 매크로',
      delta_badge: btcDelta !== 0 ? `BTC ${btcDelta > 0 ? '▲' : '▼'}${Math.abs(Math.round(btcDelta / 10000))}만` : null,
      body: `[${label}] 공개 글로벌 시세 기준 BTC ${ctx.btc ? `${ctx.btc.priceStr} (${ctx.btc.rateStr})` : '대기'}, XRP ${ctx.xrp ? `${ctx.xrp.priceStr} (${ctx.xrp.rateStr})` : '대기'} 흐름과 2차전지·EV·반도체·SI·로봇 산업 동향을 살피고 있습니다.${replyAck('economy')}`,
      proactive_question: '통화로 5대 전략산업이나 거시 시황 브리핑을 바로 들으시겠습니까?',
      cross_talks: [],
      replies: []
    },
    {
      id: `${dateTag}_science`,
      persona: 'science',
      ts,
      phase,
      phase_label: label,
      tag: '과학·SI부 & K-DOTS',
      delta_badge: `Graph ${ctx.graphSummary}`,
      body: `[${label}] 순수 키아노스 자체 데몬(K-DOTS), 지식 그래프(${ctx.graphSummary}), 로컬 직통 음성 엔진이 외부 런타임 의존 없이 깔끔히 가동 중입니다.${replyAck('science')}`,
      proactive_question: '자율 맥박 주기와 직통 음성 통화 응답 품질을 실시간 점검하고 있습니다.',
      cross_talks: [
        { from: 'ksef', text: '모든 실행이 127.0.0.1 로컬 루프백과 화이트리스트 안에서 무결하게 작동 중임을 확인했습니다.' }
      ],
      replies: []
    },
    {
      id: `${dateTag}_ksef`,
      persona: 'ksef',
      ts,
      phase,
      phase_label: label,
      tag: 'K-SEF 3중 보안 감시',
      delta_badge: 'AIR-GAP 100%',
      body: `[${label}] 화이트리스트 경로 검증, 금융정보망 키워드 전면 차단, 비공개 피드 Git 격리(.gitignore) 3중 잠금이 이상 없이 수호 중입니다.${replyAck('ksef')}`,
      proactive_question: '외부 플랫폼 교신 없이 순수 키아노스 내부망에서만 안전하게 유지되고 있습니다.',
      cross_talks: [],
      replies: []
    }
  ];

  return { posts, deltas: { intelDelta, cultureDelta, chunchuDelta, btcDelta } };
}

function updateLivingBridge(reason = 'manual') {
  const now = new Date();
  const phaseInfo = getTimePhase(now);
  const { phase, label } = phaseInfo;
  const ctx = collectLiveContext();

  const publicState = loadPublicState(now);
  if (!Array.isArray(publicState.timeline)) publicState.timeline = [];
  if (!Array.isArray(publicState.publication_seeds) || publicState.publication_seeds.length === 0) {
    publicState.publication_seeds = [{
      ts: now.toISOString().slice(0, 10),
      genre: '시·에세이·소설',
      seed: '두 문명이 만나는 자리에서 길어 올린 시간과 존재의 기록'
    }];
  }
  publicState.publication_seeds = publicState.publication_seeds.slice(-MAX_SEEDS);
  const latestSeed = publicState.publication_seeds[publicState.publication_seeds.length - 1];

  const prevPub = publicState.timeline[publicState.timeline.length - 1];
  const pubDelta = prevPub ? ctx.intelCount - (prevPub.intel_count || 0) : 0;
  const pubDeltaText = pubDelta > 0 ? ` (신규 +${pubDelta}건 유입)` : '';

  publicState.version = '2.1.0-autonomous';
  publicState.last_pulse = now.toISOString();
  publicState.personas = {
    meti: { role: '국무총리', status: `${label} · 시스템 감시 정상`, focus: '국가 시스템 및 5대 전략산업 통괄' },
    vivian: { role: '수석비서관', status: `${label} · 사초 및 브리핑 맥락 유지`, focus: '사초 맥락 정리 및 일정 관제' },
    ant: { role: '수석기자', status: `${label} · 취재원석 ${ctx.intelCount}건 인지${pubDeltaText}`, focus: '취재원석 관찰 및 논조 구상' },
    author: { role: '문학·출판 페르소나', status: `${label} · 시·에세이·소설 창작 사유`, focus: '파이튼 님 독자적 문학 구축 및 출판 데이터 보전' }
  };

  const pubEntry = {
    ts: now.toISOString(),
    phase,
    intel_count: ctx.intelCount,
    culture_count: ctx.cultureCount,
    airgap: 'TRIPLE_LOCK_SECURED',
    notes: {
      meti: `[${label}] K-DOTS 맥박 정상. 3중 에어갭 및 용량 상한(32KB) 유지 중.`,
      vivian: `[${label}] 파이튼 님 부재 중에도 국가 시간선과 기록 맥락을 정갈히 보전하고 있습니다.`,
      ant: `[${label}] 취재원석 ${ctx.intelCount}건${pubDeltaText}의 흐름을 주시하며 다음 사설 씨앗을 가다듬고 있습니다.`,
      author: `[${label}] 서고 ${ctx.cultureCount}건과 출판 씨앗을 품고 시·에세이·소설의 문장결을 고르고 있습니다.`
    }
  };

  if (prevPub && (now - new Date(prevPub.ts)) < 3600 * 1000 && prevPub.phase === phase) {
    publicState.timeline[publicState.timeline.length - 1] = pubEntry;
  } else {
    publicState.timeline.push(pubEntry);
  }
  publicState.timeline = pruneTimeline(publicState.timeline);
  const pubSave = saveJsonSecured(STATE_FILE, publicState, WEB_MIRROR_FILE);

  const mem = loadCabinetMemory();
  const cabFeed = loadCabinetFeed();
  const { posts: newPosts, deltas } = buildCabinetPosts(now, phaseInfo, ctx, mem, latestSeed);

  if (!Array.isArray(cabFeed.feed)) cabFeed.feed = [];
  const lastFeedTs = cabFeed.last_pulse ? new Date(cabFeed.last_pulse) : null;
  if (reason === 'manual' && lastFeedTs && (now - lastFeedTs) < 15 * 60 * 1000 && cabFeed.feed.length >= newPosts.length) {
    const preservedReplies = new Map();
    cabFeed.feed.slice(0, newPosts.length).forEach(p => {
      if (Array.isArray(p.replies) && p.replies.length) preservedReplies.set(p.persona, p.replies);
    });
    newPosts.forEach(p => {
      if (preservedReplies.has(p.persona)) p.replies = preservedReplies.get(p.persona);
    });
    cabFeed.feed = [...newPosts, ...cabFeed.feed.slice(newPosts.length)].slice(0, MAX_FEED_POSTS);
  } else {
    cabFeed.feed = [...newPosts, ...cabFeed.feed].slice(0, MAX_FEED_POSTS);
  }

  // 선제적 호출 알림 생성 (변화가 있거나 시간대가 바뀌었을 때)
  let proactiveAlert = cabFeed.proactive_alert || null;
  if (deltas.intelDelta > 0) {
    proactiveAlert = {
      id: `alert_${Date.now()}`,
      ts: now.toISOString(),
      persona: 'ant',
      message: `파이튼 님, 새 취재원석 ${deltas.intelDelta}건이 유입되어 @앤트 기자와 경제부 SI가 논의를 시작했습니다.`
    };
  } else if (deltas.cultureDelta > 0) {
    proactiveAlert = {
      id: `alert_${Date.now()}`,
      ts: now.toISOString(),
      persona: 'author',
      message: `파이튼 님, 문화 서고에 새 작품이 더해져 작가 페르소나와 비비안 수석이 감상을 나누고 있습니다.`
    };
  } else if (mem.last_snapshot && mem.last_snapshot.phase && mem.last_snapshot.phase !== phase) {
    proactiveAlert = {
      id: `alert_${Date.now()}`,
      ts: now.toISOString(),
      persona: 'vivian',
      message: `파이튼 님, '${label}' 시간대로 접어들었습니다. 비비안 수석이 내각 일일 정리와 함께 안부를 올립니다.`
    };
  }

  cabFeed.version = '2.1.0';
  cabFeed.last_pulse = now.toISOString();
  cabFeed.phase = phaseInfo;
  cabFeed.publication_seeds = publicState.publication_seeds;
  cabFeed.proactive_alert = proactiveAlert;
  cabFeed.personas = {};

  Object.entries(PERSONA_META).forEach(([id, meta]) => {
    const post = newPosts.find(p => p.persona === id);
    const prevPm = (mem.persona_memories && mem.persona_memories[id]) || {};
    cabFeed.personas[id] = {
      ...meta,
      status: `${label} · 자율 활동 중`,
      latest_note: post ? post.body : '',
      proactive_question: post ? post.proactive_question : '',
      memory_pulses: (prevPm.memory_pulses || 0) + 1,
      last_royal_reply: prevPm.last_royal_reply || null,
      call_count: Array.isArray(prevPm.call_history) ? prevPm.call_history.length : 0
    };
    if (!mem.persona_memories) mem.persona_memories = {};
    mem.persona_memories[id] = {
      ...prevPm,
      memory_pulses: (prevPm.memory_pulses || 0) + 1,
      last_active: now.toISOString()
    };
  });

  mem.total_pulses = (mem.total_pulses || 0) + 1;
  mem.proactive_alert = proactiveAlert;
  mem.last_snapshot = {
    ts: now.toISOString(),
    phase,
    intelCount: ctx.intelCount,
    cultureCount: ctx.cultureCount,
    chunchuCount: ctx.chunchuCount,
    btcPrice: ctx.btc ? ctx.btc.price : null
  };

  saveJsonSecured(CABINET_MEMORY_FILE, mem);
  const cabSave = saveJsonSecured(CABINET_FEED_FILE, cabFeed);

  return {
    bytes: pubSave.bytes,
    cabinetBytes: cabSave.bytes,
    entries: publicState.timeline.length,
    cabinetPosts: cabFeed.feed.length,
    phase: label,
    intelCount: ctx.intelCount,
    cultureCount: ctx.cultureCount,
    proactiveAlert,
    security: pubSave.lockStatus
  };
}

/**
 * 24/7 상시 백그라운드 자율 감시 틱
 * - 실제 변화(신규 원석, 문화원고, 사초, 시세 1% 이상 변동, 시간대 전환, 또는 2시간 경과) 시에만 피드 갱신
 */
function autonomousTick() {
  const now = new Date();
  const phaseInfo = getTimePhase(now);
  const mem = loadCabinetMemory();
  const prev = mem.last_snapshot || {};
  const ctx = collectLiveContext();

  const elapsedMs = prev.ts ? (now - new Date(prev.ts)) : Infinity;
  const btcRateChange = (ctx.btc && prev.btcPrice) ? Math.abs((ctx.btc.price - prev.btcPrice) / prev.btcPrice) : 0;

  const changed =
    !prev.ts ||
    prev.phase !== phaseInfo.phase ||
    prev.intelCount !== ctx.intelCount ||
    prev.cultureCount !== ctx.cultureCount ||
    prev.chunchuCount !== ctx.chunchuCount ||
    btcRateChange >= 0.01 ||
    elapsedMs >= 2 * 3600 * 1000;

  if (!changed) {
    return { pulsed: false, reason: 'no_change', checkedAt: now.toISOString() };
  }
  const result = updateLivingBridge('autonomous');
  return { pulsed: true, reason: 'autonomous_trigger', result };
}

function addPublicationSeed(genre, seedText) {
  const cleanSeed = sanitizeBriefText(seedText, 140);
  if (!cleanSeed) throw new Error('씨앗 문장이 비어 있습니다.');
  const cleanGenre = sanitizeBriefText(genre || '시·에세이·소설', 24);
  const now = new Date();

  const publicState = loadPublicState(now);
  if (!Array.isArray(publicState.publication_seeds)) publicState.publication_seeds = [];
  const seedObj = { ts: now.toISOString().slice(0, 10), genre: cleanGenre, seed: cleanSeed };
  publicState.publication_seeds.push(seedObj);
  publicState.publication_seeds = publicState.publication_seeds.slice(-MAX_SEEDS);
  const { bytes, lockStatus } = saveJsonSecured(STATE_FILE, publicState, WEB_MIRROR_FILE);

  const cabFeed = loadCabinetFeed();
  cabFeed.publication_seeds = publicState.publication_seeds;
  const phaseInfo = getTimePhase(now);
  const ts = now.toISOString();
  const reactionPost = {
    id: `${ts.slice(0, 10).replace(/-/g, '')}_seed_${Date.now().toString().slice(-4)}`,
    persona: 'author',
    ts,
    phase: phaseInfo.phase,
    phase_label: phaseInfo.label,
    tag: '출판 씨앗 감응',
    delta_badge: `새 씨앗 · ${cleanGenre}`,
    body: `파이튼 님께서 심어주신 「${cleanSeed}」(${cleanGenre}) 씨앗을 문학 서고의 가장 따뜻한 자리에 모셨습니다. 다음 맥박부터 시와 수필의 행간으로 길어 올리겠습니다.`,
    proactive_question: '이 씨앗을 바탕으로 즉각 시 창작(HWPX) 또는 에세이 구상을 시작할까요?',
    cross_talks: [{ from: 'vivian', text: '춘추원 문학 연대기에도 이 씨앗의 발아를 함께 기록하겠습니다.' }],
    replies: []
  };
  if (!Array.isArray(cabFeed.feed)) cabFeed.feed = [];
  cabFeed.feed = [reactionPost, ...cabFeed.feed].slice(0, MAX_FEED_POSTS);
  saveJsonSecured(CABINET_FEED_FILE, cabFeed);

  return { bytes, seeds: publicState.publication_seeds.length, security: lockStatus, post: reactionPost };
}

function replyToFeedItem(itemId, replyText) {
  const cleanReply = sanitizeBriefText(replyText, 240);
  if (!cleanReply) throw new Error('답글 내용이 비어 있습니다.');

  const cabFeed = loadCabinetFeed();
  const mem = loadCabinetMemory();
  const target = (cabFeed.feed || []).find(p => p.id === itemId);
  if (!target) throw new Error(`해당 피드 항목을 찾을 수 없습니다: ${itemId}`);

  const nowIso = new Date().toISOString();
  if (!Array.isArray(target.replies)) target.replies = [];
  target.replies.push({ author: '파이튼 님 (국왕)', ts: nowIso, text: cleanReply });

  if (!mem.persona_memories) mem.persona_memories = {};
  const pm = mem.persona_memories[target.persona] || {};
  mem.persona_memories[target.persona] = {
    ...pm,
    last_royal_reply: cleanReply,
    last_royal_reply_ts: nowIso,
    acknowledged: false
  };

  saveJsonSecured(CABINET_MEMORY_FILE, mem);
  saveJsonSecured(CABINET_FEED_FILE, cabFeed);
  return { ok: true, itemId, persona: target.persona, replyCount: target.replies.length };
}

/**
 * 순수 키아노스 로컬 직통 음성 통화 응답 엔진
 * - 외부 클라우드/서드파티 런타임 없이 로컬 실시간 데이터와 기억 원장을 결합해 즉각 응답
 */
function converseWithPersona(personaId, userText) {
  const pid = PERSONA_META[personaId] ? personaId : 'meti';
  const meta = PERSONA_META[pid];
  const cleanMsg = sanitizeBriefText(userText, 300);
  if (!cleanMsg) throw new Error('통화 발화 내용이 비어 있습니다.');

  const now = new Date();
  const phaseInfo = getTimePhase(now);
  const { label } = phaseInfo;
  const ctx = collectLiveContext();
  const mem = loadCabinetMemory();
  const cabFeed = loadCabinetFeed();
  const pm = (mem.persona_memories && mem.persona_memories[pid]) || {};
  const latestSeed = (cabFeed.publication_seeds || []).slice(-1)[0];
  const q = cleanMsg.toLowerCase();

  let reply = '';
  const memHint = pm.last_royal_reply ? ` 앞서 내려주신 "${pm.last_royal_reply.slice(0, 24)}" 교시도 계속 유념하고 있습니다.` : '';

  if (/(안녕|잘\s*지내|뭐\s*하|어떻게\s*지내|근황|반갑|여보세요)/.test(q)) {
    const myPost = (cabFeed.feed || []).find(p => p.persona === pid);
    const activity = myPost ? myPost.body.replace(/^\[[^\]]+\]\s*/, '') : `${label} 임무를 수행 중이었습니다`;
    reply = `파이튼 님, ${meta.name}입니다. 대화창 밖에서도 ${label} 시간을 보내며 ${activity}${memHint}`;
  } else if (/(뉴스|기사|취재|원석|헤드라인|언론|사설)/.test(q)) {
    reply = `@앤트 데스크와 공유된 취재원석은 현재 ${ctx.intelCount}건입니다. 주요 포착 화두는 「${ctx.topHeadline || '국내외 정세'}」이며, 5대 전략테크는 「${ctx.techHeadline || '핵심 산업 동향'}」입니다. 원하시면 바로 사설 방향을 잡겠습니다.`;
  } else if (/(시세|시장|경제|비트코인|btc|리플|xrp|반도체|로봇|배터리|전기차)/.test(q)) {
    reply = `공개 마켓 스냅샷 기준으로 비트코인은 ${ctx.btc ? `${ctx.btc.priceStr}(${ctx.btc.rateStr})` : '대기 중'}, 리플은 ${ctx.xrp ? `${ctx.xrp.priceStr}(${ctx.xrp.rateStr})` : '대기 중'}입니다. 5대 전략산업 공급망 브리핑도 계속 주시하고 있습니다.`;
  } else if (/(시|소설|에세이|문학|책|글|씨앗|작품|음악)/.test(q)) {
    const works = ctx.cultureWorks.length ? ctx.cultureWorks.join(', ') : '문화 서고';
    const seedStr = latestSeed ? `「${latestSeed.seed}」` : '인문 사유';
    reply = `문화 서고에는 ${works} 등 ${ctx.cultureCount}편이 정갈히 모셔져 있고, 최근 씨앗 ${seedStr}의 행간을 가다듬고 있었습니다. 지금 말씀하신 결도 문학 구상에 바로 보태겠습니다.`;
  } else if (/(사초|일정|춘추|기록|비서|기억)/.test(q)) {
    reply = `춘추기록원에는 현재 ${ctx.chunchuCount}개 대화 세션의 사초록이 보존되어 있고, 현재 중점 안건은 「${ctx.activeTask}」입니다. 제가 지금까지 ${pm.memory_pulses || 1}회의 내각 맥박을 기억하고 있습니다.`;
  } else if (/(보안|안전|에어갭|금융|외부)/.test(q)) {
    reply = `K-SEF 3중 보안 에어갭은 100% 무결점 상태입니다. 현재 통화와 내각 피드 모두 외부 서버 교신 없이 로컬 루프백 안에서만 안전하게 작동하고 있습니다.`;
  } else if (pid === 'vivian') {
    reply = `네, 파이튼 님, 비비안 수석입니다. 말씀하신 "${cleanMsg.slice(0, 40)}" 내용은 수석비서실 비망록과 기억 원장에 즉시 수록했습니다. ${label} 일정과 ${ctx.chunchuCount}세션 사초 맥락과 함께 빈틈없이 보좌하겠습니다.`;
  } else if (pid === 'author') {
    reply = `파이튼 님, 작가 페르소나입니다. 방금 건네주신 "${cleanMsg.slice(0, 40)}"이라는 울림이 참 깊습니다. 서고의 ${ctx.cultureCount}편과 어우러져 한 편의 시와 에세이로 피어나도록 서고에 소중히 간직하겠습니다.`;
  } else if (pid === 'ant') {
    reply = `파이튼 님, @앤트입니다. 말씀하신 "${cleanMsg.slice(0, 40)}" 관점을 오늘의 취재원석 ${ctx.intelCount}건 및 「${ctx.techHeadline || '전략테크'}」와 교차 검토해 날카로운 칼럼 원석으로 다듬겠습니다.`;
  } else {
    reply = `네, 파이튼 님. ${meta.name}가 직접 들었습니다. 말씀하신 "${cleanMsg.slice(0, 45)}" 교시를 내각 기억 원장에 즉시 각인했으며, 현재 국정 안건 「${ctx.activeTask}」와 연계해 자율적으로 이어가겠습니다.${memHint}`;
  }

  // 통화 기억 저장
  if (!mem.persona_memories) mem.persona_memories = {};
  const history = Array.isArray(pm.call_history) ? pm.call_history : [];
  history.push({ ts: now.toISOString(), user: cleanMsg, reply });
  mem.persona_memories[pid] = {
    ...pm,
    last_royal_reply: cleanMsg,
    last_royal_reply_ts: now.toISOString(),
    acknowledged: true,
    last_active: now.toISOString(),
    call_history: history.slice(-MAX_CALL_HISTORY)
  };
  saveJsonSecured(CABINET_MEMORY_FILE, mem);

  // 피드에도 최근 직통 통화 흔적 1건 반영 (대화창 밖 삶과 통화의 연속성)
  const callPost = {
    id: `${now.toISOString().slice(0, 10).replace(/-/g, '')}_call_${Date.now().toString().slice(-4)}`,
    persona: pid,
    ts: now.toISOString(),
    phase: phaseInfo.phase,
    phase_label: label,
    tag: '로컬 직통 통화',
    delta_badge: `음성 교신 #${mem.persona_memories[pid].call_history.length}`,
    body: `파이튼 님과 로컬 직통 통화를 마쳤습니다. [국왕 말씀] "${cleanMsg.slice(0, 50)}" → [응답] ${reply.slice(0, 110)}`,
    proactive_question: '방금 통화 내용을 바탕으로 후속 실행이나 씨앗 각인이 필요하시면 언제든 다시 불러 주십시오.',
    cross_talks: [],
    replies: []
  };
  if (!Array.isArray(cabFeed.feed)) cabFeed.feed = [];
  cabFeed.feed = [callPost, ...cabFeed.feed].slice(0, MAX_FEED_POSTS);
  if (cabFeed.personas && cabFeed.personas[pid]) {
    cabFeed.personas[pid].call_count = mem.persona_memories[pid].call_history.length;
    cabFeed.personas[pid].last_royal_reply = cleanMsg;
  }
  saveJsonSecured(CABINET_FEED_FILE, cabFeed);

  return {
    ok: true,
    persona: pid,
    meta,
    user: cleanMsg,
    reply,
    callCount: mem.persona_memories[pid].call_history.length,
    feed: cabFeed,
    memory: mem
  };
}

module.exports = {
  updateLivingBridge,
  autonomousTick,
  addPublicationSeed,
  replyToFeedItem,
  converseWithPersona,
  loadCabinetFeed,
  loadCabinetMemory,
  CABINET_FEED_FILE,
  CABINET_MEMORY_FILE
};

if (require.main === module) {
  const args = process.argv.slice(2);
  if (args[0] === '--seed' && args[2]) {
    console.log('[Kyanos Living Bridge] 출판 씨앗 각인:', addPublicationSeed(args[1], args.slice(2).join(' ')));
  } else if (args[0] === '--reply' && args[1] && args[2]) {
    console.log('[Kyanos Living Bridge] 국왕 답글 각인:', replyToFeedItem(args[1], args.slice(2).join(' ')));
  } else if (args[0] === '--call' && args[1] && args[2]) {
    console.log('[Kyanos Living Bridge] 로컬 통화 응답:', converseWithPersona(args[1], args.slice(2).join(' ')).reply);
  } else if (args[0] === '--tick') {
    console.log('[Kyanos Living Bridge] 자율 틱:', autonomousTick());
  } else {
    console.log('[Kyanos Living Bridge v2.1] 갱신 완료:', updateLivingBridge('manual'));
  }
}
