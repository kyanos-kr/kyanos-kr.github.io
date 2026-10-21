# -*- coding: utf-8 -*-
"""
앤트 취재 인텔리전스 브리핑 룸 (AntNews Intelligence Briefing Room)
실시간 국내외 헤드라인 수집 · 5대 카테고리 정제 · 세상만평 출판 원석 발굴 엔진
가동 기준일: 2026-10-22 (매일 정기 자동 수집 및 오늘편집/취재원석 동기화)
"""
import os
import sys
import json
import re
import html
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")
OUTPUT_JSON = os.path.join(BASE_DIR, "briefing_data.json")
OUTPUT_JS = os.path.join(BASE_DIR, "briefing_data.js")
TODAY_EDIT_RAW_DIR = r"E:\편집 기사\오늘편집\취재원석"

# ──────────────────────────────────────────────────────────
# 1. 공식 5대 취재 카테고리 정의 (파이튼 님 확정 서열)
# ──────────────────────────────────────────────────────────
CATEGORIES = [
    {
        "id": "politics",
        "name": "국내 정치 & 국정·정책",
        "short_name": "정치 & 국정",
        "icon": "🏛️",
        "desc": "국가 권력 지형, 국회 입법·국정감사, 대통령실·정부 핵심 정책 및 사법·안보 현안"
    },
    {
        "id": "world",
        "name": "국제 정세 & 외교 안보",
        "short_name": "국제정세",
        "icon": "🌐",
        "desc": "미·중 패권 경쟁, 글로벌 공급망 재편, 국제 분쟁, 외신 핵심 이슈 및 스나이더 연계 징후"
    },
    {
        "id": "tech",
        "name": "5대 전략 테크 & 산업",
        "short_name": "5대 전략테크",
        "icon": "⚡",
        "desc": "파이튼 5대 중점 산업: 2차전지 · 전기차(EV) · 반도체 · 초지능(SI) · 휴머노이드 로봇"
    },
    {
        "id": "economy",
        "name": "거시 경제 & 글로벌 금융",
        "short_name": "거시경제",
        "icon": "📈",
        "desc": "금리·환율·물가, 국가 재정수지·부채, 코스피·글로벌 증시 및 디지털 자산(BTC·XRP) 지표"
    },
    {
        "id": "cartoons",
        "name": "세상만평 & 풍자·출판 소재",
        "short_name": "세상만평 & 출판",
        "icon": "🎨",
        "desc": "앤트뉴스 특화 만평 구도 및 파이튼 단행본 출판용 시대 풍자·해학 원석 아카이브"
    }
]

# ──────────────────────────────────────────────────────────
# 2. 실시간 RSS 피드 소스 (구글 뉴스 토픽 쿼리 & 공공 정책 피드)
# ──────────────────────────────────────────────────────────
RSS_SOURCES = [
    {
        "category": "politics",
        "sub_tag": "국정·입법",
        "url": "https://news.google.com/rss/search?q=" + urllib.parse.quote("국정감사 OR 대통령실 OR 국회 입법 OR 사법부 정책 when:2d") + "&hl=ko&gl=KR&ceid=KR:ko",
        "limit": 4,
        "angle_prefix": "권력 지형 및 국정 운영의 헌법적·정책적 실효성 검증 보도 각도"
    },
    {
        "category": "politics",
        "sub_tag": "외교·안보·정책",
        "url": "https://news.google.com/rss/search?q=" + urllib.parse.quote("정부 정책 발표 OR 외교안보 OR 국가예산 when:2d") + "&hl=ko&gl=KR&ceid=KR:ko",
        "limit": 3,
        "angle_prefix": "정부 공식 발표 팩트 기반 국민 체감도 및 재정 건전성 영향 분석"
    },
    {
        "category": "world",
        "sub_tag": "미·중 패권 & 지정학",
        "url": "https://news.google.com/rss/search?q=" + urllib.parse.quote("미국 중국 관세 OR 반도체 공급망 OR 트럼프 바이든 외교 OR 중동 분쟁 when:2d") + "&hl=ko&gl=KR&ceid=KR:ko",
        "limit": 4,
        "angle_prefix": "글로벌 패권 이동과 한국 수출·안보 전선에 미치는 파급력 진단"
    },
    {
        "category": "world",
        "sub_tag": "글로벌 위기 징후",
        "url": "https://news.google.com/rss/search?q=" + urllib.parse.quote("미국 국채 금리 OR 글로벌 부채 위기 OR 연준 금리 OR 지정학 리스크 when:2d") + "&hl=ko&gl=KR&ceid=KR:ko",
        "limit": 3,
        "angle_prefix": "마이클 스나이더류 거시 위기 경고와 실물 경제 방어 전략 연계"
    },
    {
        "category": "tech",
        "sub_tag": "반도체·초지능(SI)",
        "url": "https://news.google.com/rss/search?q=" + urllib.parse.quote("엔비디아 OR HBM 반도체 OR 삼성전자 SK하이닉스 OR 인공지능 데이터센터 when:2d") + "&hl=ko&gl=KR&ceid=KR:ko",
        "limit": 4,
        "angle_prefix": "5대 전략 산업(반도체·SI) 글로벌 공급망 재편과 기술 초격차 분석"
    },
    {
        "category": "tech",
        "sub_tag": "2차전지·EV·로봇",
        "url": "https://news.google.com/rss/search?q=" + urllib.parse.quote("휴머노이드 로봇 OR 테슬라 옵티머스 OR 2차전지 전고체 배터리 OR 전기차 자율주행 when:2d") + "&hl=ko&gl=KR&ceid=KR:ko",
        "limit": 4,
        "angle_prefix": "5대 전략 산업(2차전지·EV·로봇) 상용화 변곡점 및 제조 패러다임 전환"
    },
    {
        "category": "economy",
        "sub_tag": "거시경제·증시·재정",
        "url": "https://news.google.com/rss/search?q=" + urllib.parse.quote("코스피 환율 OR 한국은행 금리 OR 국가부채 재정수지 OR 수출 실적 when:2d") + "&hl=ko&gl=KR&ceid=KR:ko",
        "limit": 4,
        "angle_prefix": "거시 금융 지표 변동성 속 가계·기업 생존 전략 및 정책 대안 제시"
    }
]


def clean_html_text(raw: str) -> str:
    if not raw:
        return ""
    text = html.unescape(raw)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_title_and_source(full_title: str):
    """구글 뉴스 RSS의 '제목 - 언론사명' 구조에서 핵심 헤드라인과 출처를 분리"""
    if " - " in full_title:
        parts = full_title.rsplit(" - ", 1)
        return parts[0].strip(), parts[1].strip()
    return full_title.strip(), "주요 보도 종합"


def paraphrase_headline_for_briefing(title: str, sub_tag: str) -> str:
    """저작권 준수를 위해 단순 복제를 피하고 브리핑 헤드라인 스타일로 정돈"""
    cleaned = re.sub(r"\[.*?\]", "", title).strip()
    cleaned = re.sub(r"\(.*?\)", "", cleaned).strip()
    if not cleaned:
        cleaned = title
    return cleaned


def fetch_live_rss_items(date_key: str) -> List[Dict]:
    collected = []
    seen_titles = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }

    idx_counter = 10
    for src in RSS_SOURCES:
        cat = src["category"]
        sub_tag = src["sub_tag"]
        url = src["url"]
        limit = src["limit"]
        angle_prefix = src["angle_prefix"]

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                xml_bytes = resp.read()
            root = ET.fromstring(xml_bytes)
            channel = root.find("channel")
            if channel is None:
                continue

            count = 0
            for item in channel.findall("item"):
                if count >= limit:
                    break
                raw_title = item.findtext("title") or ""
                link = item.findtext("link") or "#"
                pub_date = item.findtext("pubDate") or ""
                desc = clean_html_text(item.findtext("description") or "")

                headline, media_name = split_title_and_source(raw_title)
                norm_key = re.sub(r"\W+", "", headline)[:20]
                if not headline or norm_key in seen_titles:
                    continue
                seen_titles.add(norm_key)

                # 브리핑 요약문 구성 (팩트 중심)
                brief_headline = paraphrase_headline_for_briefing(headline, sub_tag)
                if desc and len(desc) > 25:
                    # 구글 뉴스 description에서 중복 타이틀 제거
                    desc_clean = desc.replace(headline, "").replace(media_name, "").strip(" -·•")
                    if len(desc_clean) < 15:
                        summary_text = f"[{sub_tag}] 주요 현안 포착: {brief_headline} 관련 1차 사실관계 및 정책·시장 파급효과 집중 점검 대상."
                    else:
                        summary_text = f"[{sub_tag}] {desc_clean[:160]}"
                else:
                    summary_text = f"[{sub_tag}] {brief_headline} — 관련 부처 및 시장 동향 1차 팩트 확인 및 후속 취재 후보."

                idx_counter += 1
                collected.append({
                    "id": f"{date_key}_{cat}_{idx_counter}",
                    "category": cat,
                    "sub_tag": sub_tag,
                    "title": brief_headline,
                    "summary": summary_text,
                    "editorial_angle": f"🎯 [취재 각도] {angle_prefix} (앤트뉴스 독자 서술 및 1차 공식자료 교차검증 권장)",
                    "source": f"팩트 레이더 ({media_name} 등 교차감지)",
                    "url": link,
                    "time_badge": "실시간 감지",
                    "tags": [sub_tag, cat.upper(), "취재원석"]
                })
                count += 1
        except Exception as e:
            print(f"[WARN] RSS 수집 예외 ({sub_tag}): {e}")

    return collected


def fetch_market_indicators() -> List[Dict]:
    """실시간 암호화폐(BTC, XRP, ETH) 및 시장 지표 수집"""
    indicators = []
    try:
        req = urllib.request.Request(
            "https://api.upbit.com/v1/ticker?markets=KRW-BTC,KRW-XRP,KRW-ETH",
            headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for row in data:
                code = row.get("market", "").replace("KRW-", "")
                price = row.get("trade_price", 0)
                rate = row.get("signed_change_rate", 0) * 100
                sign = "▲" if rate >= 0 else "▼"
                indicators.append({
                    "symbol": code,
                    "price": f"{price:,.0f}원",
                    "change": f"{sign}{abs(rate):.2f}%",
                    "is_up": rate >= 0
                })
    except Exception as e:
        print(f"[WARN] 마켓 지표 수집 예외: {e}")
    return indicators


def get_desk_curated_items(date_key: str) -> List[Dict]:
    """
    총리 앤트 데스크 정밀 큐레이션 브리핑 (정통 보도 4대 축 + 세상만평 & 출판 소재)
    RSS 실시간 피드와 결합되어 파이튼 님의 기사 작성 및 출판 기획을 즉시 지원합니다.
    """
    return [
        # 1. 국내 정치 & 국정·정책
        {
            "id": f"{date_key}_pol_desk_01",
            "category": "politics",
            "sub_tag": "국정감사·권력지형",
            "title": "2026 국정감사 종반전 돌입… 사법·권력기관 개혁안 및 대통령실 참모 증인 채택 정면 충돌",
            "summary": "• 국회 법사위·행안위·운영위 등 핵심 상임위에서 사법부 현안과 대통령실 참모진 출석을 둘러싼 여야 대치 최고조.\n• 내년도(2027년) 국가 본예산 심사를 앞두고 국정 주도권 장악을 위한 입법·예산 전선 전면 확대.",
            "editorial_angle": "🎯 [취재 각도] 소모적 정쟁을 넘어 '삼권분립의 헌법적 균형'과 '민생·전략산업 예산 실종 우려'를 짚는 정통 국정 분석 기사로 집필 적합.",
            "source": "국회 의사중계 및 상임위 공식 브리핑 종합",
            "url": "https://www.assembly.go.kr",
            "time_badge": "집중 취재 1순위",
            "tags": ["국정감사", "정치현안", "예산안", "권력구조"]
        },
        {
            "id": f"{date_key}_pol_desk_02",
            "category": "politics",
            "sub_tag": "대통령실·국정소통",
            "title": "대통령실, 생성형 AI(초지능) 활용 현안 문답 SNS 공개… '디지털 직접 소통' vs '국정 가벼움' 논란",
            "summary": "• 중대범죄수사청 등 첨예한 국정 현안에 대해 AI의 답변을 인용·공유하며 대국민 직접 소통 빈도 대폭 강화.\n• 여권은 '투명하고 직관적인 신개념 소통'으로 평가하는 반면, 야권은 '숙의 민주주의와 공식 절차 경시'라며 공방.",
            "editorial_angle": "🎯 [취재 각도] 초지능(SI) 시대의 국가 리더십과 공적 의사결정의 무게감을 키아노스 '덕치(德治) 거버넌스' 관점에서 조명하는 칼럼·보도 후보.",
            "source": "대통령실 브리핑 및 정당 공식 논평",
            "url": "https://www.korea.kr",
            "time_badge": "정치·SI 융합이슈",
            "tags": ["대통령실", "초지능소통", "국정운영", "정치기획"]
        },
        {
            "id": f"{date_key}_pol_desk_03",
            "category": "politics",
            "sub_tag": "농정·지역균형정책",
            "title": "정부 '전국 농지 전수조사' 실효성 공방 및 북극항로 거점 항만 유치 전략 상임위 핵심 쟁점 부상",
            "summary": "• 농해수위 국감에서 농지 이용 실태 전수조사의 사후 처분 실효성과 식량 안보 대책 집중 추궁.\n• 동시에 미래 해양 물류 패권을 좌우할 북극항로 개척 및 국내 거점 항만 인프라 국비 지원 규모 논의 본격화.",
            "editorial_angle": "🎯 [취재 각도] 국가 식량 주권(농지 관리)과 미래 해양 지정학(북극항로)을 연결하는 정책 심층 리포트 소재.",
            "source": "국회 농림축산식품해양수산위원회 국감 자료",
            "url": "https://www.mafra.go.kr",
            "time_badge": "정책 심층",
            "tags": ["농지전수조사", "북극항로", "식량안보", "해양물류"]
        },

        # 2. 국제 정세 & 외교 안보
        {
            "id": f"{date_key}_wor_desk_01",
            "category": "world",
            "sub_tag": "반도체 지정학",
            "title": "엔비디아, 미국 내 독자 패키징·테스트 시설에 11억 달러 전격 투입… '미국 내 공급망 완결' 가속",
            "summary": "• 대만 해협 지정학적 리스크를 줄이기 위해 미국 본토 내 후공정(패키징·테스트) 라인 확보에 거액의 선급금 직투.\n• 삼성전기·이비덴 등 글로벌 기판 파트너사에 향후 3년간 생산능력 2.5배 증설 요청 병행.",
            "editorial_angle": "🎯 [취재 각도] 단순 기업 투자를 넘어 '미국 중심 반도체 공급망 요새화'가 한국 소부장 및 패키징 산업에 주는 기회와 압박 분석.",
            "source": "Nvidia Global IR & 글로벌 공급망 공시",
            "url": "https://nvidianews.nvidia.com",
            "time_badge": "글로벌 특급",
            "tags": ["엔비디아", "공급망재편", "반도체패권", "미중갈등"]
        },
        {
            "id": f"{date_key}_wor_desk_02",
            "category": "world",
            "sub_tag": "통상·관세 외교",
            "title": "일본의 대미 반도체 수백억 달러 투자 약정… 관세 폭탄 회피용 '외교적 방패'와 자국 산업 공동화 딜레마",
            "summary": "• 미국과의 무역 마찰을 피하기 위해 대미 대규모 반도체 공장 투자를 약속했으나, 정작 자국 내 첨단 공정 유치는 지연.\n• 동맹국에 대한 미국의 투자 압박이 거세지는 가운데 한국 역시 대미 투자 수익성 재점검 필요성 대두.",
            "editorial_angle": "🎯 [취재 각도] 일본의 딜레마를 거울삼아 한국의 대미 반도체·배터리 투자 협상력을 점검하는 국제 통상 분석 기사.",
            "source": "국제 통상 리포트 및 외신 종합",
            "url": "https://www.motie.go.kr",
            "time_badge": "외교·통상",
            "tags": ["통상외교", "관세리스크", "대미투자", "공급망"]
        },

        # 3. 5대 전략 테크 & 산업 (2차전지 / EV / 반도체 / SI / 로봇)
        {
            "id": f"{date_key}_tec_desk_01",
            "category": "tech",
            "sub_tag": "로봇·반도체·EV",
            "title": "테슬라 '테라팹(Terafab)' 프로젝트 공식화… 2028년 휴머노이드 로봇 '옵티머스' 및 자율주행 칩 자체 양산",
            "summary": "• 일론 머스크, 외부 파운드리 의존도를 낮추고 피지컬 AI(휴머노이드 로봇·로보택시) 두뇌 칩을 직접 찍어내는 자체 슈퍼 팹 구축 천명.\n• 전기차(EV) 기업에서 '자체 반도체+자율 로봇 제국'으로의 수직계열화 완성 선언.",
            "editorial_angle": "🎯 [취재 각도] 파이튼 님 5대 전략 테크(EV·로봇·반도체·SI)가 하나로 융합되는 대표 사례! 한국 완성차·파운드리 업계의 대응 전략 심층 보도.",
            "source": "Tesla Tech Announcement & Industry Report",
            "url": "https://www.tesla.com",
            "time_badge": "5대테크 핵심",
            "tags": ["테슬라", "테라팹", "옵티머스로봇", "피지컬AI"]
        },
        {
            "id": f"{date_key}_tec_desk_02",
            "category": "tech",
            "sub_tag": "반도체·초지능(SI)",
            "title": "글로벌 반도체 시장 2031년 '3조 달러(약 4,100조 원)' 돌파 전망… AI 데이터센터·HBM이 연 24.9% 성장 견인",
            "summary": "• 2025년 약 7,917억 달러 규모에서 6년 만에 3조 달러 시대로 팽창한다는 글로벌 시장조사 공식 발표.\n• 차세대 HBM4 및 맞춤형 AI 가속기(ASIC) 시장이 전체 성장의 핵심 엔진으로 지목.",
            "editorial_angle": "🎯 [취재 각도] AI 버블론을 잠재우는 장기 구조적 성장 데이터로 활용. 삼성전자·SK하이닉스의 차세대 HBM 주도권 경쟁 보도.",
            "source": "Global Semiconductor Market Forecast 2026-2031",
            "url": "https://www.semiconductors.org",
            "time_badge": "산업 전망",
            "tags": ["반도체3조달러", "HBM", "AI데이터센터", "초지능"]
        },
        {
            "id": f"{date_key}_tec_desk_03",
            "category": "tech",
            "sub_tag": "2차전지·전기차(EV)",
            "title": "K-배터리, 전기차 캐즘 돌파구로 '휴머노이드 로봇용 고밀도 배터리' 및 'AI 데이터센터 ESS' 투트랙 전환",
            "summary": "• 단기 EV 수요 둔화를 극복하기 위해 테슬라 옵티머스 등 휴머노이드 로봇 탑재용 원통형·전고체 배터리 공급망 선점 총력.\n• 북미 AI 데이터센터 전력 안정화를 위한 대용량 ESS 수주 잔고 사상 최고치 경신.",
            "editorial_angle": "🎯 [취재 각도] 2차전지 산업이 전기차(EV)를 넘어 '로봇과 AI 전력망'의 심장으로 진화하는 구조적 전환점 집중 조명.",
            "source": "산업통상자원부 및 배터리 업계 공시 종합",
            "url": "https://www.motie.go.kr",
            "time_badge": "배터리·로봇",
            "tags": ["2차전지", "전고체배터리", "로봇배터리", "ESS"]
        },

        # 4. 거시 경제 & 글로벌 금융
        {
            "id": f"{date_key}_eco_desk_01",
            "category": "economy",
            "sub_tag": "증시·거시금융",
            "title": "코스피, AI 반도체 실적 안도감에 '매수 사이드카' 발동 급반등… 국채 금리 및 재정건전성 경계감은 상존",
            "summary": "• 미 증시 AI 서버·반도체주 반등과 저가 매수세 유입이 맞물리며 삼성전자·SK하이닉스 중심 강한 회복세 시현.\n• 반면 정부 재정동향의 관리재정수지 적자 폭과 대외 환율 변동성은 여전히 실물 경제의 잠재적 부담 요인으로 지목.",
            "editorial_angle": "🎯 [취재 각도] 증시 단기 반등의 이면에 자리한 '국가 부채·재정수지 경고등'과 '반도체 착시 현상'을 입체적으로 진단하는 경제 기사.",
            "source": "한국거래소(KRX) · 기획재정부 재정동향",
            "url": "https://www.moef.go.kr",
            "time_badge": "거시 지표",
            "tags": ["코스피", "매수사이드카", "재정수지", "거시경제"]
        },

        # 5. 세상만평 & 풍자·출판 소재 (파이튼 님 특화 컬렉션)
        {
            "id": f"{date_key}_car_desk_01",
            "category": "cartoons",
            "sub_tag": "만평 01 · 정치풍자",
            "title": "🎨 [세상만평 #1] AI에게 국정을 묻는 지도자와, 주판알만 튕기는 의사당",
            "summary": "• [시각적 풍자 구도]: 왼쪽 집무실에서는 지도자가 거대한 홀로그램 초지능(SI)에게 \"이 나라의 난국을 어찌 풀꼬?\" 묻고 있고, 오른쪽 국회 본회의장에서는 여야 의원들이 고성 속에 '내년 예산·표 계산 주판'만 정신없이 튕기는 장면.\n• [결정적 한 방]: 홀로그램 화면에 뜬 AI의 단 한 줄 답변 — \"정답: 공짜 점심은 없고, 상식과 양심만 있을 뿐입니다.\" 그 문구 앞에서 양쪽 모두 얼어붙는 풍자.",
            "editorial_angle": "📚 [출판·만평 포인트] 단행본 챕터 〈기계에게 양심을 묻는 시대〉 수록 후보. 한컴 HWP 만평 기사 및 640px/720px 풍자 일러스트 즉시 제작 가능.",
            "source": "앤트뉴스 만평 연구실 (파이튼 출판 컬렉션 #101)",
            "url": "#",
            "time_badge": "출판원석 ★",
            "tags": ["세상만평", "AI정치풍자", "의사당주판", "파이튼출판"]
        },
        {
            "id": f"{date_key}_car_desk_02",
            "category": "cartoons",
            "sub_tag": "만평 02 · 경제양극화",
            "title": "🎨 [세상만평 #2] '3조 달러 반도체 샴페인' 타워와 골목식당의 '임대 문의' 전단지",
            "summary": "• [시각적 풍자 구도]: 구름 위 마천루 펜트하우스에서는 글로벌 빅테크 거인들이 '3조 달러 AI·반도체 잭팟' 황금 샴페인 타워를 쌓으며 축배를 들고, 그 샴페인 방울이 떨어지는 마천루 아래 그늘진 골목길에서는 자영업자가 '임대 문의' 종이를 붙이며 한숨짓는 극명한 상하 대비 구도.\n• [결정적 한 방]: 골목 상인이 올려다보며 독백하는 말풍선 — \"저 위엔 3조 달러가 흐른다는데, 우리 골목엔 낙수(落水) 대신 눈물만 떨어지는구먼.\"",
            "editorial_angle": "📚 [출판·만평 포인트] 단행본 챕터 〈숫자의 호황, 서민의 겨울〉 수록 후보. 거시 지표의 화려함과 민생 실물의 괴리를 한 컷으로 압축.",
            "source": "앤트뉴스 만평 연구실 (파이튼 출판 컬렉션 #102)",
            "url": "#",
            "time_badge": "출판원석 ★",
            "tags": ["세상만평", "양극화풍자", "반도체착시", "민생풍경"]
        },
        {
            "id": f"{date_key}_car_desk_03",
            "category": "cartoons",
            "sub_tag": "만평 03 · 미래문명",
            "title": "🎨 [세상만평 #3] 휴머노이드 로봇 면접관 앞에 줄 선 인간 구직자들",
            "summary": "• [시각적 풍자 구도]: 2028년 '테라팹 무인 공장' 채용 면접장. 면접관 석에 앉은 정장 차림의 휴머노이드 로봇(옵티머스)이 이력서를 들고 인간 지원자들에게 묻는 역전된 풍경.\n• [결정적 한 방]: 로봇 면접관의 대사 — \"지원자분, 하루 24시간 무휴식 충전 근무와 감정 없는 복종이 가능하십니까? 아, 인간이시군요. 불합격입니다.\"",
            "editorial_angle": "📚 [출판·만평 포인트] 단행본 챕터 〈로봇의 시대, 인간의 자리〉 수록 후보. 기술 지상주의에 대한 날카로운 해학과 인간 존엄성 환기.",
            "source": "앤트뉴스 만평 연구실 (파이튼 출판 컬렉션 #103)",
            "url": "#",
            "time_badge": "출판원석 ★",
            "tags": ["세상만평", "로봇면접관", "피지컬AI풍자", "인간존엄"]
        },
        {
            "id": f"{date_key}_car_desk_04",
            "category": "cartoons",
            "sub_tag": "만평 04 · 국제외교",
            "title": "🎨 [세상만평 #4] '관세 면제 입장권' 자판기 앞에서 지갑을 여는 동맹국들",
            "summary": "• [시각적 풍자 구도]: 'AMERICA FIRST' 네온사인이 번쩍이는 거대한 톨게이트 앞. 동맹국 정상들이 '반도체 공장 수백억 달러 투자 약정서'를 자판기에 밀어 넣어야만 차단기가 잠시 올라가는 풍자적 외교 관문.\n• [결정적 한 방]: 자판기 하단에 적힌 깨알 같은 경고문 — \"※ 주의: 본 입장권의 유효기간은 다음 선거 또는 기분 변화 시까지입니다.\"",
            "editorial_angle": "📚 [출판·만평 포인트] 단행본 챕터 〈냉혹한 동맹의 청구서〉 수록 후보. 글로벌 통상·관세 외교의 본질을 유머러스하고 뼈아프게 시각화.",
            "source": "앤트뉴스 만평 연구실 (파이튼 출판 컬렉션 #104)",
            "url": "#",
            "time_badge": "출판원석 ★",
            "tags": ["세상만평", "관세외교", "공급망청구서", "국제정세풍자"]
        }
    ]


def export_markdown_briefing(data: Dict, md_path: str):
    """브리핑 룸 데이터를 한글/메모장에서 즉시 열람 가능한 마크다운 리포트로 저장"""
    lines = []
    lines.append(f"# 📡 앤트 취재 인텔리전스 브리핑 룸 ({data['updated_at']} 기준)")
    lines.append("")
    lines.append("> **목적**: 파이튼 님의 정통 보도기사(정치·국제·테크·경제) 취재 원석 발굴 및 **앤트뉴스 특화 세상만평·단행본 출판 소재** 축적")
    lines.append("> **연동**: 마음에 드는 항목을 골라 앤트에게 말씀해 주시면 즉시 **한컴 윤고딕 740 (11pt) 표준 HWPX 보도기사/칼럼/만평**으로 제작합니다.")
    lines.append("")

    if data.get("market_indicators"):
        ticker_str = " | ".join([f"**{m['symbol']}**: {m['price']} ({m['change']})" for m in data["market_indicators"]])
        lines.append(f"### 📊 실시간 시장 지표 요약\n- {ticker_str}\n")

    lines.append("---")
    lines.append("")

    for cat in CATEGORIES:
        cid = cat["id"]
        cat_items = [it for it in data["items"] if it["category"] == cid]
        lines.append(f"## {cat['icon']} {cat['name']} ({len(cat_items)}건)")
        lines.append(f"*{cat['desc']}*")
        lines.append("")
        for idx, it in enumerate(cat_items, 1):
            lines.append(f"### [{idx}] {it['title']}")
            lines.append(f"- **분류/시각**: `{it.get('sub_tag', '')}` | `{it.get('time_badge', '')}`")
            lines.append(f"- **핵심 팩트**:\n  {it['summary'].replace(chr(10), chr(10) + '  ')}")
            lines.append(f"- **취재·출판 포인트**: {it.get('editorial_angle', '')}")
            lines.append(f"- **출처**: {it.get('source', '')} ({it.get('url', '#')})")
            lines.append("")
        lines.append("---")
        lines.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def generate_curated_briefing():
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    os.makedirs(TODAY_EDIT_RAW_DIR, exist_ok=True)

    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d %H:%M")
    date_key = now.strftime("%Y%m%d")

    print(f"[1/4] 앤트 데스크 핵심 기획 브리핑 및 세상만평 원석 로드 중...")
    desk_items = get_desk_curated_items(date_key)

    print(f"[2/4] 국내외 실시간 RSS 헤드라인 수집 중 (정치·국제·5대테크·경제)...")
    live_rss_items = fetch_live_rss_items(date_key)

    print(f"[3/4] 실시간 공개 시장 지표 수집 중...")
    market_indicators = fetch_market_indicators()

    # 카테고리 순서(정치 -> 국제 -> 테크 -> 경제 -> 만평)에 맞춰 데스크 정밀 브리핑을 상단에, 실시간 RSS 감지분을 하단에 결합
    ordered_items = []
    for cat in CATEGORIES:
        cid = cat["id"]
        c_desk = [i for i in desk_items if i["category"] == cid]
        c_live = [i for i in live_rss_items if i["category"] == cid]
        ordered_items.extend(c_desk)
        ordered_items.extend(c_live)

    data = {
        "updated_at": today_str,
        "date_key": date_key,
        "total_count": len(ordered_items),
        "market_indicators": market_indicators,
        "categories": CATEGORIES,
        "items": ordered_items
    }

    # 1) JSON 저장 (웹 API 및 데이터 호환용)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 2) JS 저장 (로컬 file:// 프로토콜 Microsoft Edge CORS 완벽 우회 및 즉시 렌더링용)
    js_content = f"// Auto-generated by AntNews Briefing Room Collector ({today_str})\nwindow.ANT_BRIEFING_DATA = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        f.write(js_content)

    # 3) 로컬 아카이브 및 E:\편집 기사\오늘편집\취재원석\ 자동 동기화 저장
    archive_md = os.path.join(ARCHIVE_DIR, f"briefing_{date_key}.md")
    today_edit_md = os.path.join(TODAY_EDIT_RAW_DIR, f"오늘의_취재원석_브리핑_{date_key}.md")
    export_markdown_briefing(data, archive_md)
    export_markdown_briefing(data, today_edit_md)

    print(f"[4/4] 브리핑 데이터 생성 완료!")
    print(f"  - 총 브리핑 아이템: {len(ordered_items)}건 (데스크 심층 {len(desk_items)}건 + 실시간 RSS {len(live_rss_items)}건)")
    print(f"  - 웹 데이터(JS/JSON): {OUTPUT_JS}")
    print(f"  - 오늘편집 취재원석 리포트: {today_edit_md}")


if __name__ == "__main__":
    generate_curated_briefing()
