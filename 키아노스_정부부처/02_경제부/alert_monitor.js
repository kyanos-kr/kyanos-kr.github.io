const https = require('https');
const fs = require('fs');
const path = require('path');

// 12대 재원 종목 및 당일 매수 타이밍 감시 기준선 (Trigger Strategy)
const WATCH_TARGETS = [
  {
    name: '대주전자재료',
    code: '078600',
    bought: true,
    boughtPrice: 92700,
    role: '실리콘 음극재 독보적 1위 대장주',
    strategy: '기체결(92,700원 완료) - 94,000원 돌파 안착 시 추가 확대 검토'
  },
  {
    name: '피엔티',
    code: '137400',
    bought: false,
    role: '롤투롤 전극공정(코터·롤프레스) 최강자',
    triggerLow: 27000,
    triggerHigh: 27200,
    desc: '27,000원 심리적 바닥 지지 확인 및 27,200원 상향 돌파 시 1차 분할 매수 적기'
  },
  {
    name: '이랜시스',
    code: '264850',
    bought: false,
    role: '로봇 감속기·모터 핵심 부품',
    triggerLow: 4950,
    triggerHigh: 5020,
    desc: '5,000원 라운드피겨 탈환 및 5,020원 이상 안착 시 로봇 대장주 분할 매수'
  },
  {
    name: '레이크머티리얼즈',
    code: '281740',
    bought: false,
    role: '전고체 배터리 황화리튬 및 초고순도 TMA',
    triggerLow: 10730,
    triggerHigh: 10950,
    desc: '10,700~10,800원 바닥 지지 후 10,950원 돌파 시 전고체 소재 분할 매수'
  },
  {
    name: '에코앤드림',
    code: '101360',
    bought: false,
    role: '하이니켈 5세대 전구체 주도주 (폭락장 독보적 역주행)',
    triggerLow: 10300,
    triggerHigh: 10550,
    desc: '당일 주도주 눌림목 지지 후 10,550원 재탈환 시 모멘텀 추세 추종 분할 매수'
  },
  {
    name: '율촌화학',
    code: '008730',
    bought: false,
    role: '2차전지 알루미늄 파우치필름 국산화',
    triggerLow: 12850,
    triggerHigh: 13050,
    desc: '12,850원 바닥 확인 후 13,000원선 회복 안착 시 분할 매수'
  },
  {
    name: '신흥에스이씨',
    code: '243840',
    bought: false,
    role: '각형/원통형 캡어셈블리 및 캔 부품',
    triggerLow: 5560,
    triggerHigh: 5680,
    desc: '5,600원 지지선 방어 및 5,680원 상향 턴어라운드 시 분할 매수'
  },
  {
    name: 'PKC',
    code: '001340',
    bought: false,
    role: '전해액 핵심소재(PCl3/5) 국산화 (구 백광산업)',
    triggerLow: 4750,
    triggerHigh: 4830,
    desc: '4,750원 바닥 방어 후 시가(4,835원) 수준 회복 시 매수'
  },
  {
    name: '휴림로봇',
    code: '090710',
    bought: false,
    role: '산업용·협동·지능형 로봇 플랫폼',
    triggerLow: 4800,
    triggerHigh: 4950,
    desc: '4,800원 전저점 지지 후 4,950원 돌파 시 분할 매수'
  },
  {
    name: 'SFA넥셀',
    code: '222080',
    bought: false,
    role: '전극공정 및 전고체 장비 (구 씨아이에스)',
    triggerLow: 7230,
    triggerHigh: 7350,
    desc: '7,230원 저점 지지 후 7,350원 회복 시 분할 매수'
  },
  {
    name: '제이오',
    code: '418550',
    bought: false,
    role: '탄소나노튜브(CNT) 도전재 독보적 생산 기술',
    triggerLow: 4250,
    triggerHigh: 4320,
    desc: '4,250원 저점 방어 후 4,320원 회복 시 분할 매수'
  },
  {
    name: '나인테크',
    code: '267320',
    bought: false,
    role: '2차전지 라미네이션&스태킹(L&S) 롤투롤',
    triggerLow: 2400,
    triggerHigh: 2440,
    desc: '2,400원 지지 확인 후 2,440원 돌파 시 분할 매수'
  }
];

function fetchStock(code) {
  return new Promise((resolve) => {
    const url = 'https://polling.finance.naver.com/api/realtime/domestic/stock/' + code;
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json.datas ? json.datas[0] : null);
        } catch (e) {
          resolve(null);
        }
      });
    }).on('error', () => resolve(null));
  });
}

function fetchIndex(code) {
  return new Promise((resolve) => {
    const url = 'https://polling.finance.naver.com/api/realtime/domestic/index/' + code;
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json.datas ? json.datas[0] : null);
        } catch (e) {
          resolve(null);
        }
      });
    }).on('error', () => resolve(null));
  });
}

const logFile = path.join(__dirname, '매수경보_발령로그.txt');

function logAlert(msg) {
  const time = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
  const entry = `[${time}] ${msg}\n`;
  fs.appendFileSync(logFile, entry, 'utf8');
}

async function runCheck() {
  const kospi = await fetchIndex('KOSPI');
  const kosdaq = await fetchIndex('KOSDAQ');
  const now = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });

  console.log(`\n================================================================`);
  console.log(`🚨 키아노스 경제부 | 12대 핵심 재원 매수 타이밍 실시간 경보 감시`);
  console.log(`⏰ 감시 시각: ${now}`);
  if (kospi) console.log(`📊 코스피: ${kospi.closePrice} (${kospi.fluctuationsRatio}%) | 코스닥: ${kosdaq?.closePrice} (${kosdaq?.fluctuationsRatio}%)`);
  console.log(`================================================================`);

  const alerts = [];
  const watchlist = [];

  for (const it of WATCH_TARGETS) {
    const d = await fetchStock(it.code);
    if (!d) continue;

    const price = parseInt(d.closePriceRaw);
    const low = parseInt(d.lowPriceRaw);
    const high = parseInt(d.highPriceRaw);
    const open = parseInt(d.openPriceRaw);

    if (it.bought) {
      // 이미 매수한 대주전자재료
      const diffFromBought = price - it.boughtPrice;
      const profitRate = ((diffFromBought / it.boughtPrice) * 100).toFixed(2);
      console.log(`📌 [보유종목] ${it.name} | 매수가: ${it.boughtPrice.toLocaleString()}원 | 현재가: ${price.toLocaleString()}원 (${profitRate}%) | 상태: ${diffFromBought >= 0 ? '수익/보합권 방어 중' : '조정 대응 중'}`);
      continue;
    }

    // 매수 타이밍 조건 판정
    // 1) 당일 저점 지지 후 반등 목표가(triggerHigh) 이상 돌파 안착 시 -> 🚨 강력 매수 경보
    // 2) 당일 최저점 부근(triggerLow)에서 하방 경직성 확보 시 -> ⚠️ 바닥권 분할 매수 관심 경보
    let status = '관망(Watch)';
    let isAlert = false;
    let alertMsg = '';

    if (price >= it.triggerHigh) {
      status = '🚨 [매수 타이밍 발령]';
      isAlert = true;
      alertMsg = `🚨 [매수 타이밍 발령] ${it.name}(${it.code}) 현재가 ${price.toLocaleString()}원 (기준선 ${it.triggerHigh.toLocaleString()}원 돌파) ➔ ${it.desc}`;
      alerts.push(alertMsg);
      logAlert(alertMsg);
    } else if (price <= it.triggerLow * 1.01 && price >= it.triggerLow) {
      status = '⚠️ [바닥 지지 분할 매수권]';
      isAlert = true;
      alertMsg = `⚠️ [바닥 지지선 도달] ${it.name}(${it.code}) 현재가 ${price.toLocaleString()}원 (당일 저점 ${low.toLocaleString()}원 부근 지지) ➔ ${it.desc}`;
      alerts.push(alertMsg);
      logAlert(alertMsg);
    }

    watchlist.push({
      name: it.name,
      code: it.code,
      price: price.toLocaleString() + '원',
      rate: d.fluctuationsRatio + '%',
      low: low.toLocaleString() + '원',
      trigger: it.triggerHigh.toLocaleString() + '원',
      status: status
    });
  }

  console.log('\n--- 11대 미체결 재원 매수 타이밍 감시 현황 ---');
  console.log(
    '종목명'.padEnd(10) +
    '현재가'.padStart(10) +
    '등락률'.padStart(8) +
    '당일저가'.padStart(10) +
    '매수돌파기준'.padStart(12) +
    '   판정상태'
  );
  console.log('-'.repeat(70));
  for (const w of watchlist) {
    console.log(
      w.name.padEnd(10) +
      w.price.padStart(10) +
      w.rate.padStart(8) +
      w.low.padStart(10) +
      w.trigger.padStart(12) +
      '   ' + w.status
    );
  }

  if (alerts.length > 0) {
    console.log(`\n🔔 [금일 즉시 유효 매수 경보 목록]`);
    alerts.forEach(a => console.log('  ' + a));
  } else {
    console.log(`\n⏳ 현재 기준선을 돌파한 신규 매수 타이밍 종목 없음 (바닥 다지기 관망 유지)`);
  }
  console.log(`================================================================\n`);
}

// 1회 실행 또는 연속 실행
const isOnce = process.argv.includes('--once');

if (isOnce) {
  runCheck();
} else {
  runCheck();
  // 30초마다 갱신
  setInterval(runCheck, 30000);
}
