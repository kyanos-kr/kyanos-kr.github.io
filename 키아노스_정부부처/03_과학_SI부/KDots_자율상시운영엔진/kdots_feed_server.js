/**
 * Kyanos Cabinet Autonomous Mind Server (v3.0)
 * - 127.0.0.1 루프백 전용 바인딩 (외부 네트워크 접근 원천 차단)
 * - 24/7 대화창 외부 상시 자율 사유 루프(autonomousTick, 60초 주기 감시)
 * - 수동적 대화창 없이 국왕 의결(/api/stance) 및 능동 발제 육성(/api/tts) 제공
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const {
  updateLivingBridge,
  autonomousTick,
  addPublicationSeed,
  recordRoyalStance,
  assertTripleLockSecurity,
  loadCabinetFeed,
  loadCabinetMemory,
  CABINET_FEED_FILE
} = require('./kdots_living_bridge');

const HOST = '127.0.0.1';
const PORT = Number(process.env.KYANOS_FEED_PORT || 4780);
const HEARTBEAT_MS = 60 * 1000;
const UI_FILE = path.join(__dirname, 'cabinet_feed_console.html');
const LOG_FILE = path.join(__dirname, 'kdots_feed_server.log');
const TTS_SCRIPT = path.join(__dirname, 'kdots_tts.py');
const VENV_PYTHON = path.resolve(__dirname, '../../../antnews_auto/.venv/Scripts/python.exe');
const MAX_BODY_BYTES = 16 * 1024;

function logServer(msg) {
  const line = `[${new Date().toISOString()}] [CABINET-DAEMON] ${msg}\n`;
  try {
    fs.appendFileSync(LOG_FILE, line, 'utf8');
  } catch (_) {}
}

function sendJson(res, statusCode, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store'
  });
  res.end(body);
}

function readJsonBody(req) {
  return new Promise((resolve, reject) => {
    let raw = '';
    let size = 0;
    req.on('data', chunk => {
      size += chunk.length;
      if (size > MAX_BODY_BYTES) {
        reject(new Error('요청 본문이 허용 크기를 초과했습니다.'));
        req.destroy();
        return;
      }
      raw += chunk.toString('utf8');
    });
    req.on('end', () => {
      try {
        resolve(raw ? JSON.parse(raw) : {});
      } catch (e) {
        reject(new Error('올바른 JSON 형식이 아닙니다.'));
      }
    });
    req.on('error', reject);
  });
}

function synthesizeNeuralTts(persona, text) {
  return new Promise((resolve, reject) => {
    const cleanText = String(text || '').replace(/\*\*/g, '').replace(/\s+/g, ' ').trim().slice(0, 700);
    if (!cleanText) return reject(new Error('음성 변환 문장이 비어 있습니다.'));
    assertTripleLockSecurity(cleanText);
    if (!fs.existsSync(VENV_PYTHON) || !fs.existsSync(TTS_SCRIPT)) {
      return reject(new Error('TTS 실행 환경이 준비되지 않았습니다.'));
    }

    const child = spawn(VENV_PYTHON, [TTS_SCRIPT, String(persona || 'meti')], {
      windowsHide: true
    });
    const chunks = [];
    let errBuf = '';
    const timer = setTimeout(() => {
      child.kill();
      reject(new Error('TTS 생성 시간 초과'));
    }, 15000);

    child.stdout.on('data', d => chunks.push(d));
    child.stderr.on('data', d => { errBuf += d.toString('utf8'); });
    child.on('error', err => {
      clearTimeout(timer);
      reject(err);
    });
    child.on('close', code => {
      clearTimeout(timer);
      if (code !== 0 || chunks.length === 0) {
        return reject(new Error(errBuf || `TTS 종료 코드 ${code}`));
      }
      resolve(Buffer.concat(chunks));
    });
    child.stdin.write(cleanText, 'utf8');
    child.stdin.end();
  });
}

function runDaemonTick() {
  try {
    const res = autonomousTick();
    if (res.pulsed) {
      logServer(`Autonomous deliberation triggered (${res.result.phase}, posts=${res.result.cabinetPosts})`);
    }
  } catch (err) {
    logServer(`Autonomous tick error: ${err.message}`);
  }
}

const server = http.createServer(async (req, res) => {
  const reqPath = (req.url || '/').split('?')[0];

  try {
    if (req.method === 'GET' && (reqPath === '/' || reqPath === '/index.html')) {
      const html = fs.readFileSync(UI_FILE, 'utf8');
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
      res.end(html);
      return;
    }

    if (req.method === 'GET' && reqPath === '/api/health') {
      sendJson(res, 200, {
        ok: true,
        mode: 'ROYAL_INTERNAL_ONLY',
        architecture: 'AUTONOMOUS_OPINION_ENGINE_V3',
        autonomous_daemon: true,
        heartbeat_ms: HEARTBEAT_MS,
        host: HOST,
        port: PORT
      });
      return;
    }

    if (req.method === 'GET' && reqPath === '/api/feed') {
      if (!fs.existsSync(CABINET_FEED_FILE)) updateLivingBridge('autonomous');
      sendJson(res, 200, { ok: true, feed: loadCabinetFeed(), memory: loadCabinetMemory() });
      return;
    }

    if (req.method === 'POST' && reqPath === '/api/pulse') {
      const result = updateLivingBridge('manual');
      sendJson(res, 200, { ok: true, result, feed: loadCabinetFeed(), memory: loadCabinetMemory() });
      return;
    }

    if (req.method === 'POST' && reqPath === '/api/seed') {
      const body = await readJsonBody(req);
      const result = addPublicationSeed(body.genre, body.seed);
      sendJson(res, 200, { ok: true, result, feed: loadCabinetFeed(), memory: loadCabinetMemory() });
      return;
    }

    if (req.method === 'POST' && reqPath === '/api/stance') {
      const body = await readJsonBody(req);
      const result = recordRoyalStance(body.itemId, body.stance, body.note || '');
      sendJson(res, 200, result);
      return;
    }

    if (req.method === 'POST' && reqPath === '/api/tts') {
      const body = await readJsonBody(req);
      const mp3Buffer = await synthesizeNeuralTts(body.persona, body.text);
      res.writeHead(200, {
        'Content-Type': 'audio/mpeg',
        'Content-Length': mp3Buffer.length,
        'Cache-Control': 'no-store'
      });
      res.end(mp3Buffer);
      return;
    }

    sendJson(res, 404, { ok: false, error: 'Not Found' });
  } catch (err) {
    logServer(`ERROR ${req.method} ${reqPath}: ${err.message}`);
    sendJson(res, 400, { ok: false, error: err.message });
  }
});

server.listen(PORT, HOST, () => {
  runDaemonTick();
  setInterval(runDaemonTick, HEARTBEAT_MS);
  logServer(`Autonomous Cabinet Mind Server v3.0 active on http://${HOST}:${PORT}`);
  console.log(`🏛️ 키아노스 자율 내각 능동 발제 서버 가동: http://${HOST}:${PORT}`);
});
