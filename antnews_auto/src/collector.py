# collector.py - 저작권 안전 공식 소스 전용 뉴스 수집 모듈
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 저작권 방침:
#   ✅ 사용 가능: 정부·공공기관·국제기구 공식 RSS/API (공개 허용)
#   ✅ 사용 가능: CC0·CC-BY 라이선스 공개 뉴스
#   ✅ 사용 가능: 각 기관이 배포 목적으로 공표한 보도자료·공식 발표문
#   ❌ 제거됨: TechCrunch, NYT, BBC 등 상업 미디어 RSS (재게재 불허)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import feedparser
import requests
from typing import List, Dict
import time

# ──────────────────────────────────────────────────────────
# 1. 공식 허용 RSS 피드 목록 (저작권 프리 / 공공 도메인)
# ──────────────────────────────────────────────────────────
OFFICIAL_RSS_FEEDS = [
    # ── 국제기구 ──
    {
        "url": "https://news.un.org/feed/subscribe/en/news/topic/economic-development/feed/rss.xml",
        "name": "UN 경제개발", "count": 2, "license": "CC-BY"
    },
    {
        "url": "https://www.who.int/en/news/rss",   # 307 리다이렉트 수정
        "name": "WHO 공식", "count": 2, "license": "공공저작물"
    },
    {
        "url": "https://www.imf.org/en/News/rss",
        "name": "IMF 공식", "count": 2, "license": "공공저작물"
    },
    {
        "url": "https://www.bis.org/rss/press.rss",  # ECB 404 → BIS(국제결제은행) 대체
        "name": "BIS 국제결제은행", "count": 2, "license": "공공저작물"
    },
    # ── 미국 연방정부 공공도메인 ──
    {
        "url": "https://www.federalreserve.gov/feeds/press_all.xml",
        "name": "미 연준(FED)", "count": 2, "license": "US Gov 공공도메인"
    },
    {
        "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=&dateb=&owner=include&count=5&search_text=&output=atom",
        "name": "SEC 공시", "count": 2, "license": "US Gov 공공도메인"
    },
    # ── 한국 공식 기관 ──
    {
        "url": "https://www.korea.kr/rss/news.do",   # 200 OK 확인
        "name": "대한민국 정책브리핑", "count": 3, "license": "공공저작물(CC-BY)"
    },
    {
        "url": "https://www.bok.or.kr/portal/cmmn/rss/selectRssInfo.do?rssType=P",  # rssType=E→P 수정
        "name": "한국은행 공식", "count": 2, "license": "공공저작물"
    },
    # ── 학술 오픈 액세스 ──
    {
        "url": "https://rss.arxiv.org/rss/cs.AI",    # 200 OK 확인
        "name": "arXiv AI 논문", "count": 2, "license": "오픈 액세스"
    },
    {
        "url": "https://rss.arxiv.org/rss/econ.GN",  # econ→econ.GN (General Economics)
        "name": "arXiv 경제학 논문", "count": 2, "license": "오픈 액세스"
    },
    # ── 세계은행 ──
    {
        "url": "https://feeds.worldbank.org/worldbank/all",
        "name": "세계은행(World Bank)", "count": 2, "license": "CC-BY"
    },
]


# ──────────────────────────────────────────────────────────
# 2. 공개 API 기반 데이터 수집
#    (API Key 불필요 / 공개 엔드포인트)
# ──────────────────────────────────────────────────────────
def fetch_public_api_data() -> List[Dict]:
    """공개 API 에서 경제·금융 공식 데이터를 수집합니다."""
    results = []

    # ── 업비트 마켓 현황 (API Key 불필요) ──
    try:
        r = requests.get(
            "https://api.upbit.com/v1/ticker?markets=KRW-BTC,KRW-ETH,KRW-XRP",
            timeout=10, headers={"Accept": "application/json"}
        )
        if r.status_code == 200:
            for item in r.json():
                market = item.get("market", "")
                price = item.get("trade_price", 0)
                rate = item.get("signed_change_rate", 0)
                arrow = "▲" if rate >= 0 else "▼"
                results.append({
                    "title": f"[업비트] {market} 현재가 {price:,.0f}원 {arrow}{abs(rate)*100:.2f}%",
                    "link": "https://upbit.com",
                    "summary": f"업비트 공식 API 실시간 데이터. {market}: {price:,.0f}원, 변동률 {rate*100:+.2f}%",
                    "published": "",
                    "source": "업비트 공식 API",
                    "license": "공개 API"
                })
        print(f"[OK] 업비트 API: {len(r.json())}건 수집")
    except Exception as e:
        print(f"[SKIP] 업비트 API: {e}")

    return results


# ──────────────────────────────────────────────────────────
# 3. RSS 피드 수집 메인 함수
# ──────────────────────────────────────────────────────────
def fetch_rss_feeds() -> List[Dict]:
    """
    공식 허용 RSS 소스와 공개 API 에서 뉴스·데이터 수집.
    ※ 상업 미디어 RSS 완전 제거 – 저작권 안전 보장.
    """
    result = []

    # 1) 공식 RSS 수집
    for feed in OFFICIAL_RSS_FEEDS:
        try:
            feed_data = feedparser.parse(feed["url"])
            count = 0
            for entry in feed_data.entries[:feed["count"]]:
                result.append({
                    "title":     entry.get("title", ""),
                    "link":      entry.get("link", ""),
                    "summary":   entry.get("summary", entry.get("description", ""))[:300],
                    "published": entry.get("published", ""),
                    "source":    feed["name"],
                    "license":   feed.get("license", "공공저작물"),
                })
                count += 1
            print(f"[OK] {feed['name']}: {count}건 수집 ({feed.get('license','?')})")
            time.sleep(0.3)  # 서버 부하 방지
        except Exception as e:
            print(f"[SKIP] {feed['name']}: {e}")

    # 2) 공개 API 데이터 추가
    api_data = fetch_public_api_data()
    result.extend(api_data)

    print(f"\n  → 총 {len(result)}건 수집 완료 (전체 저작권 안전 소스)")
    return result


if __name__ == "__main__":
    news = fetch_rss_feeds()
    for a in news:
        print(f"  [{a['source']}|{a['license']}] {a['title'][:60]}")
