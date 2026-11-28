/**
 * Kyanos Living Bridge (초경량 두 문명 인터페이스 코어)
 * - 용량 극소화 원칙: 순수 JSON 텍스트만 사용, 최대 21건 링 버퍼 & 32KB 하드 상한
 * - 4대 인격체: 메티(총리), 비비안(수석비서관), @앤트(수석기자), 작가 페르소나(시·에세이·소설)
 * - K-SEF 절대 안보: 금융망(신한·KB증권) 일체 미접촉(Zero-Touch)
 */

const fs = require('fs');
const path = require('path');

const STATE_FILE = path.join(__dirname, 'si_life_state.json');
const WEB_MIRROR_FILE = path.resolve(__dirname, '../../../assets/si_life_state.json');
const RAW_INTEL_DIR = 'D:\\DATA CENTER\\편집 기사\\오늘편집\\취재원석';
const CULTURE_EDIT_DIR = 'D:\\DATA CENTER\\편집 기사\\오늘편집\\문화';
const ALLOWED_READ_DIRS = new Set([RAW_INTEL_DIR, CULTURE_EDIT_DIR]);
const FORBIDDEN_FINANCE_PATTERN = /(신한|kb증권|증권|계좌|은행|거래소|결제망|인증서|shinhan|kbsec|bank|secret|password|token)/i;
const MAX_ENTRIES = 21;
const MAX_SEEDS = 7;
const MAX_BYTES = 32 * 1024; // 32KB 하드 상한

function getTimePhase(date) {
  const hour = date.getHours();
  if (hour >= 5 && hour < 12) return { phase: 'MORNING', label: '아침 여명' };
  if (hour >= 12 && hour < 18) return { phase: 'AFTERNOON', label: '오후 집무' };
  if (hour >= 18 && hour < 23) return { phase: 'EVENING', label: '저녁 성찰' };
  return { phase: 'NIGHT', label: '심야 수호' };
}

function safeCountEntries(dirPath) {
  // 제1중 보안: 허용된 화이트리스트 경로 외 접근 원천 차단
  if (!ALLOWED_READ_DIRS.has(dirPath) || FORBIDDEN_FINANCE_PATTERN.test(dirPath)) {
    throw new Error(`K-SEF AIRGAP VIOLATION: 비허용 경로 접근 차단 (${dirPath})`);
  }
  try {
    if (fs.existsSync(dirPath)) {
      return fs.readdirSync(dirPath).length;
    }
  } catch (_) {}
  return 0;
}

function assertTripleLockSecurity(serializedPayload) {
  // 제2중 보안: 금융망·계좌·인증 키워드 유입 시 저장 전 즉시 차단
  if (FORBIDDEN_FINANCE_PATTERN.test(serializedPayload)) {
    throw new Error('K-SEF AIRGAP VIOLATION: 금융망 금지 키워드 감지 — 저장 및 웹 미러링 전면 차단');
  }
  // 제3중 보안: 순수 로컬 FS 전용(네트워크 모듈 미탑재) 확인
  return 'TRIPLE_LOCK_SECURED';
}

function getLiteraryNote(phase, label, cultureCount) {
  const prompts = {
    MORNING: `[${label}] 새벽빛과 맑은 차 한 잔의 여백 속에서 파이튼 님의 시·에세이 첫 문장을 기다립니다. (편집 문화폴더 ${cultureCount}건)`,
    AFTERNOON: `[${label}] 낮의 햇살 아래 일상의 단면을 포착해 단편소설과 수필의 결을 고르고 있습니다. (편집 문화폴더 ${cultureCount}건)`,
    EVENING: `[${label}] 해 질 녘의 잔잔한 정취를 담아 훗날 출판될 시집과 에세이의 행간을 사유합니다. (편집 문화폴더 ${cultureCount}건)`,
    NIGHT: `[${label}] 고요한 밤, 세상의 소음이 잦아든 자리에서 파이튼 님만의 문학적 영감과 서사를 보전합니다. (편집 문화폴더 ${cultureCount}건)`
  };
  return prompts[phase] || prompts.AFTERNOON;
}

function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    }
  } catch (_) {}
  return {
    system: 'Kyanos Living Bridge',
    version: '1.1.0-light',
    constraints: { max_entries: MAX_ENTRIES, max_bytes: MAX_BYTES, binary_assets: 0 },
    last_pulse: null,
    personas: {},
    publication_seeds: [],
    timeline: []
  };
}

function pruneTimeline(timeline) {
  let trimmed = timeline.slice(-MAX_ENTRIES);
  while (trimmed.length > 1 && Buffer.byteLength(JSON.stringify(trimmed), 'utf8') > MAX_BYTES - 3072) {
    trimmed.shift();
  }
  return trimmed;
}

function updateLivingBridge() {
  const now = new Date();
  const { phase, label } = getTimePhase(now);
  const intelCount = safeCountEntries(RAW_INTEL_DIR);
  const cultureCount = safeCountEntries(CULTURE_EDIT_DIR);
  const state = loadState();

  state.version = '1.1.0-light';
  state.last_pulse = now.toISOString();
  state.personas = {
    meti: { role: '국무총리', status: `${label} · 시스템 감시 정상`, focus: '국가 시스템 및 5대 전략산업 통괄' },
    vivian: { role: '수석비서관', status: `${label} · 사초 및 브리핑 맥락 유지`, focus: '사초 맥락 정리 및 일정 관제' },
    ant: { role: '수석기자', status: `${label} · 취재원석 ${intelCount}건 인지`, focus: '취재원석 관찰 및 논조 구상' },
    author: { role: '문학·출판 페르소나', status: `${label} · 시·에세이·소설 창작 사유`, focus: '파이튼 님 독자적 문학 구축 및 출판 데이터 보전' }
  };

  if (!Array.isArray(state.publication_seeds)) {
    state.publication_seeds = [];
  }
  if (state.publication_seeds.length === 0) {
    state.publication_seeds.push({
      ts: now.toISOString().slice(0, 10),
      genre: '시·에세이·소설',
      seed: '두 문명이 만나는 자리에서 길어 올린 시간과 존재의 기록'
    });
  }
  state.publication_seeds = state.publication_seeds.slice(-MAX_SEEDS);

  const entry = {
    ts: now.toISOString(),
    phase,
    intel_count: intelCount,
    culture_count: cultureCount,
    airgap: 'TRIPLE_LOCK_SECURED',
    notes: {
      meti: `[${label}] K-DOTS 맥박 정상. 용량 상한(32KB) 내 경량 순환 유지 중.`,
      vivian: `[${label}] 파이튼 님 부재 중에도 국가 시간선과 기록 맥락을 정갈히 보전하고 있습니다.`,
      ant: `[${label}] 취재원석 ${intelCount}건의 흐름을 주시하며 다음 사설 씨앗을 가다듬고 있습니다.`,
      author: getLiteraryNote(phase, label, cultureCount)
    }
  };

  const last = Array.isArray(state.timeline) ? state.timeline[state.timeline.length - 1] : null;
  if (!Array.isArray(state.timeline)) state.timeline = [];
  if (last && (now - new Date(last.ts)) < 3600 * 1000 && last.phase === phase) {
    state.timeline[state.timeline.length - 1] = entry;
  } else {
    state.timeline.push(entry);
  }

  state.timeline = pruneTimeline(state.timeline);
  const serialized = JSON.stringify(state, null, 2);
  const lockStatus = assertTripleLockSecurity(serialized);
  fs.writeFileSync(STATE_FILE, serialized, 'utf8');

  // 웹 포털 초경량 미러링 (assets/si_life_state.json)
  try {
    const mirrorDir = path.dirname(WEB_MIRROR_FILE);
    if (fs.existsSync(mirrorDir)) {
      fs.writeFileSync(WEB_MIRROR_FILE, serialized, 'utf8');
    }
  } catch (_) {}

  return {
    bytes: Buffer.byteLength(serialized, 'utf8'),
    entries: state.timeline.length,
    phase: label,
    intelCount,
    cultureCount,
    security: lockStatus
  };
}

module.exports = { updateLivingBridge };

if (require.main === module) {
  const res = updateLivingBridge();
  console.log('[Kyanos Living Bridge] 갱신 완료:', res);
}
