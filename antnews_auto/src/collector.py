# collector.py - 키아노스 내부 미디어 및 저작권 제로(Zero) 공공 데이터 수집 모듈
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [키아노스 미디어 저작권 원천 봉쇄 헌장]
# 1. 외부 상업 언론 및 외부 기사의 무단 전재, 번역, 요약, 링크 전면 배제 (저작권 침해 0%)
# 2. 키아노스 주권령 공식 정부 발표, 부처별 정책 및 프로젝트 진척 사항 중심 편성
# 3. 저작권 보호 대상이 아닌 순수 공개 지표(실시간 마켓 시세, 공공 통계)만 활용
# 4. 모든 인텔리전스 헤드라인과 분석문은 키아노스 앤트뉴스 자체 순수 창작물로 구성
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import requests
from datetime import datetime
from typing import List, Dict
import random

# ──────────────────────────────────────────────────────────
# 1. 키아노스 주권령 정부 공식 내부 의제 및 부처별 브리핑 풀
# ──────────────────────────────────────────────────────────
KYANOS_STATE_DISPATCHES = [
    {
        "category": "키아노스 과학·AGI부",
        "title": "과학·AGI부, 산하 자율로봇·드론 생산기술국(Project TALOS) 가동 본격화",
        "summary": "키아노스 정부 과학·AGI부는 미래 방어 및 산업 자율화를 위해 신설된 '자율로봇·드론 생산기술국(Project TALOS)'의 인프라 구축을 본격화했습니다. Physical AI 기반의 자율 기구와 무인 방어 체계 R&D가 집중 추진됩니다.",
        "source": "키아노스 정부 공식",
        "doc_type": "정부 공식 브리핑",
        "badge": "GOV · TALOS"
    },
    {
        "category": "키아노스 경제부",
        "title": "경제부 EVERMORE 럭셔리 경제국, 글로벌 프라이빗 헤리티지 자산 전략 수립",
        "summary": "경제부 EVERMORE 럭셔리 경제국은 희소성과 영구적 가치를 지닌 프라이빗 멤버십 자산 및 대체 자산 운용 가이드라인을 발표했습니다. 국부펀드(KSWF) 연계 자산 증권화 체계가 단계적으로 고도화됩니다.",
        "source": "키아노스 경제부",
        "doc_type": "정부 공식 브리핑",
        "badge": "GOV · EVERMORE"
    },
    {
        "category": "키아노스 통치 거버넌스",
        "title": "파이튼 국왕의 덕치(德治) 12대 원칙 기반 차세대 AI 자율 거버넌스 모델 정립",
        "summary": "도덕과 양심의 의회를 중심으로 통치자 파이튼의 덕치 철학을 구현하는 키아노스 헌법 가치가 AI 시스템 전반에 투영되고 있습니다. 기술 지상주의를 지양하고 인간 존엄을 최우선하는 지능형 통치 체계가 완성 단계에 접어들었습니다.",
        "source": "키아노스 통치 본부",
        "doc_type": "국가 거버넌스",
        "badge": "GOV · VIRTUE"
    },
    {
        "category": "키아노스 교육·문화부",
        "title": "블루로즈 문화원, 글로벌 지식인 대상 키아노스 건국 가치 및 인문 강좌 개설",
        "summary": "교육·문화부 산하 블루로즈 문화원은 고결함과 도전 정신을 상징하는 파란 장미의 정신을 널리 알리고, 21세기 신문명 담론을 이끌 글로벌 학술 및 문화 교류 프로그램을 공식 가동했습니다.",
        "source": "키아노스 교육문화부",
        "doc_type": "문화 공식 브리핑",
        "badge": "GOV · CULTURE"
    },
    {
        "category": "키아노스 복지부",
        "title": "복지부 AGI시대 인간보호국, 첨단 기술 윤리 및 시민 생애 안전망 강화 발표",
        "summary": "AGI와 자율 기계가 보편화되는 미래 사회에서 시민들의 심리적·물리적 안전을 영구 보장하기 위한 'AGI 인간 보호 헌장' 제정이 복지부 주도로 활발히 진행 중입니다.",
        "source": "키아노스 복지부",
        "doc_type": "복지 공식 브리핑",
        "badge": "GOV · WELFARE"
    }
]

# ──────────────────────────────────────────────────────────
# 2. 글로벌 전략 인텔리전스 핵심 테마 풀 (100% 앤트뉴스 오리지널 기획)
# ──────────────────────────────────────────────────────────
ORIGINAL_STRATEGIC_THEMES = [
    {
        "category": "피지컬 AI & 로보틱스",
        "title": "피지컬 AI와 자율 제조 로보틱스 전환 가속 — 하드웨어 융합 패러다임 분석",
        "summary": "거대언어모델(LLM) 중심의 소프트웨어 인공지능이 센서와 액추에이터를 갖춘 피지컬 AI로 급속히 진화하고 있습니다. 글로벌 제조 및 물류 현장에서 완전 자율 로봇의 실전 배치가 가속화되는 흐름을 심층 짚어봅니다.",
        "source": "앤트뉴스 인텔리전스",
        "doc_type": "자체 기획 분석",
        "badge": "INTELLIGENCE · AI"
    },
    {
        "category": "차세대 에너지 인프라",
        "title": "AI 연산 폭증에 대응하는 무탄소 청정 전력망과 소형원전(SMR)의 지정학",
        "summary": "데이터센터 전력 소모 급증에 따라 청정 기저 부하를 제공하는 초소형 원자로(SMR)와 해양 청정 발전 기술이 미래 국가 경쟁력의 핵심축으로 부상하고 있습니다. 에너지 자립 생태계 구축의 시사점을 다룹니다.",
        "source": "앤트뉴스 인텔리전스",
        "doc_type": "자체 기획 분석",
        "badge": "INTELLIGENCE · ENERGY"
    },
    {
        "category": "디지털 금융 & 대체 자산",
        "title": "기관급 RWA(실물연계자산) 토큰화와 국부펀드 디지털 자산 포트폴리오 진화",
        "summary": "전통 채권, 부동산, 미술품 등 고가치 실물 자산이 블록체인 인프라 위에서 토큰화되는 움직임이 가속화되고 있습니다. 탈중앙 금융과 제도권 자본 시장의 융합 지점을 분석합니다.",
        "source": "앤트뉴스 인텔리전스",
        "doc_type": "자체 기획 분석",
        "badge": "INTELLIGENCE · FINANCE"
    }
]

# ──────────────────────────────────────────────────────────
# 3. 순수 실시간 마켓 지표 (저작권 비대상 공개 시세 데이터)
# ──────────────────────────────────────────────────────────
def fetch_public_market_indicators() -> List[Dict]:
    """저작권 보호 대상이 아닌 공개 금융 지표 수집"""
    results = []
    try:
        r = requests.get(
            "https://api.upbit.com/v1/ticker?markets=KRW-BTC,KRW-ETH,KRW-XRP",
            timeout=8, headers={"Accept": "application/json"}
        )
        if r.status_code == 200:
            for item in r.json():
                market = item.get("market", "")
                coin_name = market.replace("KRW-", "")
                price = item.get("trade_price", 0)
                rate = item.get("signed_change_rate", 0)
                arrow = "▲" if rate >= 0 else "▼"
                results.append({
                    "category": "디지털 자산 지표",
                    "title": f"[공개 시장 지표] {coin_name} 실시간 거래가 {price:,.0f}원 ({arrow}{abs(rate)*100:.2f}%)",
                    "summary": f"키아노스 경제 금융망 실시간 모니터링 데이터. {coin_name} 현재가 {price:,.0f}원, 24시간 변동률 {rate*100:+.2f}%. 순수 공개 시장 통계 지표.",
                    "source": "공개 시장 지표",
                    "doc_type": "공개 금융 데이터",
                    "badge": f"MARKET · {coin_name}"
                })
    except Exception as e:
        print(f"[SKIP] 시장 데이터 수집 예외: {e}")
    return results

# ──────────────────────────────────────────────────────────
# 4. 통합 수집 메인 함수 (외부 기사 인용 0% 보장)
# ──────────────────────────────────────────────────────────
def fetch_rss_feeds() -> List[Dict]:
    """
    외부 언론 기사를 일절 인용하지 않는 키아노스 100% 저작권 안전 미디어 수집 엔진.
    1) 키아노스 정부 내부 공식 발표 (State Official)
    2) 앤트뉴스 오리지널 전략 분석 테마 (Ant Strategic Theme)
    3) 순수 공개 시장 지표 (Public Market Data)
    """
    items = []

    # 1. 키아노스 정부 공식 브리핑 (순환/선별 2~3건)
    today_seed = int(datetime.now().strftime("%Y%m%d"))
    random.seed(today_seed)
    selected_gov = random.sample(KYANOS_STATE_DISPATCHES, min(3, len(KYANOS_STATE_DISPATCHES)))
    items.extend(selected_gov)

    # 2. 앤트뉴스 오리지널 전략 테마 (1~2건)
    selected_themes = random.sample(ORIGINAL_STRATEGIC_THEMES, min(2, len(ORIGINAL_STRATEGIC_THEMES)))
    items.extend(selected_themes)

    # 3. 순수 마켓 지표 (3건)
    market_items = fetch_public_market_indicators()
    items.extend(market_items)

    print(f"\n[OK] 키아노스 내부 미디어 및 공공 지표 총 {len(items)}건 편성 완료 (외부 언론 기사 인용 0%)")
    return items

if __name__ == "__main__":
    data = fetch_rss_feeds()
    for d in data:
        print(f"[{d['badge']}] {d['title']}")
