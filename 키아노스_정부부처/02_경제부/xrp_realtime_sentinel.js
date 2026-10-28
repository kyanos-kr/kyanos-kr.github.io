const https = require('https');

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' } }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve(null);
        }
      });
    }).on('error', () => resolve(null));
  });
}

async function getLiveXRP() {
  const upbitPromise = fetchJson('https://api.upbit.com/v1/ticker?markets=KRW-XRP');
  const binancePromise = fetchJson('https://api.binance.com/api/v3/ticker/24hr?symbol=XRPUSDT');
  const usdKrwPromise = fetchJson('https://polling.finance.naver.com/api/realtime/market/exchange/FX_USDKRW');

  const [upbitData, binanceData, exchangeData] = await Promise.all([upbitPromise, binancePromise, usdKrwPromise]);

  const now = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });

  console.log('========================================================================================');
  console.log(`🏛️ [키아노스 국고 제1호 전략자산] XRP 실시간 24H 인텔리전스 레이더`);
  console.log(`⏰ 감제 시각: ${now} (KST)`);
  console.log('========================================================================================\n');

  if (!upbitData || !upbitData[0]) {
    console.log('❌ 업비트 데이터 수신 지연');
    return;
  }

  const u = upbitData[0];
  const b = binanceData;

  const krwPrice = u.trade_price;
  const krwChangeRate = (u.change_rate * 100 * (u.change === 'FALL' ? -1 : 1)).toFixed(2);
  const krwVolume24h = (u.acc_trade_price_24h / 100000000).toFixed(1); // 억원
  const high52 = u.highest_52_week_price;
  const low52 = u.lowest_52_week_price;

  let usdtPrice = b ? parseFloat(b.lastPrice).toFixed(4) : 'N/A';
  let usdtChange = b ? parseFloat(b.priceChangePercent).toFixed(2) : 'N/A';
  let usdtVol24h = b ? (parseFloat(b.quoteVolume) / 1000000).toFixed(1) : 'N/A';

  // 환율
  let fxRate = 1385.0; // fallback
  if (exchangeData && exchangeData.datas && exchangeData.datas[0]) {
    fxRate = exchangeData.datas[0].closePrice || 1385.0;
  }

  let kimP = 'N/A';
  if (b && fxRate) {
    const globalConverted = parseFloat(b.lastPrice) * fxRate;
    kimP = (((krwPrice - globalConverted) / globalConverted) * 100).toFixed(2);
  }

  console.log(`📍 [국내 원화 마켓 (Upbit)]`);
  console.log(`   - 현재가: ${krwPrice.toLocaleString()} 원 (${krwChangeRate > 0 ? '+' : ''}${krwChangeRate}%)`);
  console.log(`   - 24시간 거래대금: ${krwVolume24h} 억 원`);
  console.log(`   - 당일 고가 / 저가: ${u.high_price.toLocaleString()} 원 / ${u.low_price.toLocaleString()} 원`);
  console.log(`   - 52주 최고 / 최저: ${high52.toLocaleString()} 원 / ${low52.toLocaleString()} 원\n`);

  console.log(`🌐 [글로벌 마켓 (Binance USDT)]`);
  console.log(`   - 현재가: $${usdtPrice} (${usdtChange > 0 ? '+' : ''}${usdtChange}%)`);
  console.log(`   - 24시간 거래대금: $${usdtVol24h} M (백만 달러)`);
  console.log(`   - 김치 프리미엄: ${kimP > 0 ? '+' : ''}${kimP}% (기준환율: ${fxRate}원)\n`);

  console.log(`🛡️ [키아노스 국가 자산 전략 분석]`);
  console.log(`   - 기조: 최고통수권자 파이튼 령에 따른 '24/7 불침번 예의주시 및 국가 전략 비축'`);
  console.log(`   - 기관 레일: ISO 20022 결제망 표준 채택 & RLUSD 스테이블코인 상용화 가속 중`);
  console.log(`   - 사법·제도: 미 SEC 소송 종결 수순 & 현물 ETF(Bitwise/Canary) 등록 모니터링`);
  console.log('========================================================================================\n');
}

getLiveXRP();
