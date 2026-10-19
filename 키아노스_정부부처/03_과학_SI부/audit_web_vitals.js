/**
 * ============================================================================
 * KYANOS REALM - WEB VITALS & QUALITY AUDIT WATCHDOG
 * 키아노스 주권국 과학·SI부 & 덕치사법원 - 공식 웹 성능/품질 정기 감사 엔진
 * 총괄: 앤트 국무총리 | 수석 엔지니어: 탈로스 (티탄)
 * ============================================================================
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const TARGET_URLS = [
  { name: '공식 인트로 포털 (Intro)', url: 'https://kyanos-kr.github.io/' },
  { name: '공식 메인 포털 (Main)', url: 'https://kyanos-kr.github.io/main.html' },
  { name: '마켓 펄스 금융 센터 (Market)', url: 'https://kyanos-kr.github.io/market_monitor.html' },
  { name: '미디어부 & 앤트뉴스 (Media)', url: 'https://kyanos-kr.github.io/gov_media.html' }
];

const TARGET_SCORE = 90;
const REPORT_DIR = path.join(__dirname, 'audit_reports');

if (!fs.existsSync(REPORT_DIR)) {
  fs.mkdirSync(REPORT_DIR, { recursive: true });
}

console.log('👑 ============================================================');
console.log('   키아노스 주권국 웹 성능 & 품질 정기 감사 시스템 가동');
console.log('   목표 기준치: 성능 / 접근성 / 모범사례 / SEO 각각 90+ 점수 유지');
console.log('============================================================\n');

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
process.env.CHROME_PATH = chromePath;

const summary = [];

TARGET_URLS.forEach((target, index) => {
  console.log(`[${index + 1}/${TARGET_URLS.length}] 점검 대상: ${target.name} (${target.url})`);
  const safeName = target.name.replace(/[^a-zA-Z0-9가-힣]/g, '_');
  const reportPath = path.join(REPORT_DIR, `report_${safeName}.json`);

  try {
    const cmd = `npx.cmd lighthouse "${target.url}" --output=json --output-path="${reportPath}" --chrome-flags="--headless --no-sandbox" --preset=desktop --only-categories=performance,accessibility,best-practices,seo --quiet`;
    execSync(cmd, { stdio: 'ignore' });

    if (fs.existsSync(reportPath)) {
      const data = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
      const scores = {
        perf: Math.round(data.categories.performance.score * 100),
        a11y: Math.round(data.categories.accessibility.score * 100),
        bp: Math.round(data.categories['best-practices'].score * 100),
        seo: Math.round(data.categories.seo.score * 100)
      };

      const isPass = scores.perf >= TARGET_SCORE && scores.a11y >= TARGET_SCORE && scores.bp >= TARGET_SCORE && scores.seo >= TARGET_SCORE;
      
      console.log(`   - 성능(Perf): ${scores.perf}점 ${scores.perf >= TARGET_SCORE ? '✅' : '⚠️'}`);
      console.log(`   - 접근성(A11y): ${scores.a11y}점 ${scores.a11y >= TARGET_SCORE ? '✅' : '⚠️'}`);
      console.log(`   - 모범사례(BP): ${scores.bp}점 ${scores.bp >= TARGET_SCORE ? '✅' : '⚠️'}`);
      console.log(`   - 검색(SEO): ${scores.seo}점 ${scores.seo >= TARGET_SCORE ? '✅' : '⚠️'}`);
      console.log(`   -> 종합 판정: ${isPass ? '🟢 최상위 합격 (PASS)' : '🔴 보완 필요 (ATTENTION)'}\n`);

      summary.push({
        target: target.name,
        url: target.url,
        scores,
        isPass
      });
    }
  } catch (err) {
    console.error(`   ❌ 감사 실행 중 오류 발생: ${err.message}\n`);
    summary.push({
      target: target.name,
      url: target.url,
      error: err.message,
      isPass: false
    });
  }
});

// 감사 요약 보고서 파일 생성
const timestamp = new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '');
let markdownReport = `# 키아노스 웹 성능·품질 정기 감사 보고서\n\n`;
markdownReport += `- **감사 일시**: ${timestamp}\n`;
markdownReport += `- **감사 주관**: 국무총리 앤트 & 과학·SI부 기술감사국\n`;
markdownReport += `- **합격 기준**: 각 부문 ${TARGET_SCORE}점 이상\n\n`;
markdownReport += `| 점검 대상 페이지 | 성능(Perf) | 접근성(A11y) | 모범사례(BP) | SEO | 판정 |\n`;
markdownReport += `| :--- | :---: | :---: | :---: | :---: | :---: |\n`;

summary.forEach(s => {
  if (s.scores) {
    markdownReport += `| [${s.target}](${s.url}) | ${s.scores.perf}점 | ${s.scores.a11y}점 | ${s.scores.bp}점 | ${s.scores.seo}점 | ${s.isPass ? '🟢 PASS' : '⚠️ CHECK'} |\n`;
  } else {
    markdownReport += `| [${s.target}](${s.url}) | - | - | - | - | ❌ FAIL |\n`;
  }
});

fs.writeFileSync(path.join(REPORT_DIR, 'LATEST_AUDIT_SUMMARY.md'), markdownReport, 'utf8');
console.log('🎉 전체 감사가 완료되었습니다. 요약 리포트: audit_reports/LATEST_AUDIT_SUMMARY.md\n');
