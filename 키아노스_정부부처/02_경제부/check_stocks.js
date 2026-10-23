const https = require('https');
const fs = require('fs');
const path = require('path');

const codes = [
  { name: 'PKC', code: '001340', sector: '2차전지 전해액/화학', role: '구 백광산업, 전해액 핵심소재(PCl3/PCl5) 국산화' },
  { name: '율촌화학', code: '008730', sector: '2차전지 파우치필름', role: '알루미늄 파우치 필름 국산화 선도 (농심계열)' },
  { name: '대주전자재료', code: '078600', sector: '실리콘 음극재', role: '글로벌 실리콘 음극재 독보적 1위 기술 대장주' },
  { name: '휴림로봇', code: '090710', sector: '지능형/산업용 로봇', role: '제조·서비스 로봇 및 지능형 로봇 생태계' },
  { name: '에코앤드림', code: '101360', sector: '하이니켈 전구체', role: '하이니켈 5세대 전구체 대규모 증설 및 장기공급' },
  { name: '피엔티', code: '137400', sector: '2차전지 코터/장비', role: '롤투롤 전극공정(코터·롤프레스) 글로벌 최강 장비' },
  { name: 'SFA넥셀', code: '222080', sector: '전극공정/전고체 장비', role: '구 씨아이에스(CIS), 롤투롤 및 전고체 장비 기술' },
  { name: '신흥에스이씨', code: '243840', sector: '2차전지 캡/캔 부품', role: '각형·원통형 캡어셈블리 및 CID 안전 부품 대장' },
  { name: '이랜시스', code: '264850', sector: '로봇 감속기/모터', role: '로봇 감속기·감속모터 (삼성 봇핏 부품 수혜)' },
  { name: '나인테크', code: '267320', sector: '스태킹 장비/열전소자', role: '2차전지 라미네이션&스태킹(L&S) 롤투롤 전문' },
  { name: '레이크머티리얼즈', code: '281740', sector: '황화리튬/전구체', role: '전고체 배터리 핵심 황화리튬 및 초고순도 TMA' },
  { name: '제이오', code: '418550', sector: '탄소나노튜브(CNT)', role: '이차전지 양/음극재용 고효율 CNT 도전재 선도' }
];

function fetchStock(item) {
  return new Promise((resolve) => {
    const url = 'https://polling.finance.naver.com/api/realtime/domestic/stock/' + item.code;
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve({ item, data: json.datas ? json.datas[0] : null });
        } catch (e) {
          resolve({ item, error: e.message });
        }
      });
    }).on('error', err => resolve({ item, error: err.message }));
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

(async () => {
  const kospi = await fetchIndex('KOSPI');
  const kosdaq = await fetchIndex('KOSDAQ');
  
  const now = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
  console.log(`\n======================================================`);
  console.log(`🏛️ 키아노스 경제부 | 12대 전략 재원 실시간 시세 점검`);
  console.log(`⏰ 점검 시각: ${now}`);
  if (kospi) console.log(`📊 코스피: ${kospi.closePrice} (${kospi.compareToPreviousClosePrice} / ${kospi.fluctuationsRatio}%)`);
  if (kosdaq) console.log(`📊 코스닥: ${kosdaq.closePrice} (${kosdaq.compareToPreviousClosePrice} / ${kosdaq.fluctuationsRatio}%)`);
  console.log(`======================================================`);
  console.log(
    '종목명'.padEnd(10) +
    '현재가'.padStart(10) +
    '전일비'.padStart(10) +
    '등락률'.padStart(8) +
    '거래량'.padStart(12) +
    '거래대금'.padStart(10)
  );
  console.log('-'.repeat(64));

  for (const it of codes) {
    const res = await fetchStock(it);
    if (res.data) {
      const d = res.data;
      const rateStr = (parseFloat(d.fluctuationsRatio) > 0 ? '+' : '') + d.fluctuationsRatio + '%';
      console.log(
        it.name.padEnd(10) +
        (d.closePrice + '원').padStart(10) +
        (d.compareToPreviousClosePrice + '원').padStart(10) +
        rateStr.padStart(8) +
        (d.accumulatedTradingVolume + '주').padStart(12) +
        d.accumulatedTradingValue.padStart(10)
      );
    }
  }
  console.log(`======================================================\n`);
})();
