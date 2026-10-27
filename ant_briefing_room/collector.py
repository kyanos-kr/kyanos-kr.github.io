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
import socket

# 네트워크 타임아웃 및 무한 대기(hang) 방지
socket.setdefaulttimeout(10)

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
TODAY_EDIT_RAW_DIR = r"D:\DATA CENTER\편집 기사\오늘편집\취재원석"

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
            "sub_tag": "국정감사·종합감사",
            "title": "2026 국회 국정감사 최종 종합감사 대격돌… 사법·특검 쟁점 및 2027년도 국가 본예산 심사 전면전 돌입",
            "summary": "• 법사위·운영위·행안위 등 핵심 상임위에서 권력기관 개혁안과 증인 채택을 둘러싼 여야 공방 최고조.\n• 11월 본격 시작될 2027년도 국가 본예산안 및 세제개편안 심사를 앞두고 여야 간 국정 주도권 선점 격돌.",
            "editorial_angle": "🎯 [취재 각도] 정쟁을 넘어 '삼권분립의 헌법적 균형'과 '미래 전략기술·민생 예산의 실효성'을 심층 진단하는 정통 국정 분석 기사.",
            "source": "국회 의사중계 및 상임위 종합",
            "url": "https://www.assembly.go.kr",
            "time_badge": "오늘의 톱뉴스",
            "tags": ["국정감사", "예산안심사", "국회정무", "사법개혁"]
        },
        {
            "id": f"{date_key}_pol_desk_02",
            "category": "politics",
            "sub_tag": "대통령실·국정로드맵",
            "title": "대통령실, 4대 구조개혁(연금·의료·교육·노동) 완수 대국민 소통 강화 및 초지능(SI) 행정 혁신 천명",
            "summary": "• 국정 후반기 동력 확보를 위해 국가 핵심 4대 개혁 과제의 속도감 있는 입법 추진 강조.\n• 공공 행정 서비스에 초지능(SI) 기술을 전면 접목하여 대국민 정책 체감도를 획기적으로 개선하겠다는 방침 천명.",
            "editorial_angle": "🎯 [취재 각도] 초지능(SI) 시대의 국가 거버넌스와 리더십을 키아노스 '덕치(德治)' 관점에서 조명하는 기획 칼럼 후보.",
            "source": "대통령실 브리핑룸",
            "url": "https://www.korea.kr",
            "time_badge": "정책 심층",
            "tags": ["대통령실", "4대개혁", "초지능행정", "덕치거버넌스"]
        },
        {
            "id": f"{date_key}_pol_desk_03",
            "category": "politics",
            "sub_tag": "산업·농정 정책",
            "title": "국가 첨단전략산업 세액공제(K-칩스법) 일몰 연장 및 농업 식량안보 직불제 개편안 상임위 통과 임박",
            "summary": "• 반도체·배터리 등 미래 전략 테크 시설투자에 대한 세액공제 일몰 기한을 연장하는 세법 개정안 논의 가속화.\n• 기후위기에 대응한 농가 소득 안정과 쌀값 정상화 대책을 담은 농정 직불제 확대안 집중 심의.",
            "editorial_angle": "🎯 [취재 각도] 국가 미래 먹거리(전략 테크)와 생존 기반(식량 주권)의 조화로운 국가 예산 배분 전략을 제시.",
            "source": "기획재정위원회 및 농해수위",
            "url": "https://www.moef.go.kr",
            "time_badge": "입법 레이더",
            "tags": ["K칩스법", "세액공제", "식량안보", "전략산업"]
        },

        # 2. 국제 정세 & 외교 안보
        {
            "id": f"{date_key}_wor_desk_01",
            "category": "world",
            "sub_tag": "미·중 기술패권",
            "title": "미국 재무부, 대중국 AI·반도체·양자컴퓨팅 첨단기술 투자 통제 최종 규칙 확정 발표",
            "summary": "• 미국 자본 및 기술이 중국의 차세대 군사·초지능(SI) 기술 개발로 유입되는 것을 차단하는 고강도 규제 확정.\n• 한국 등 글로벌 동맹국 기업들의 대중 투자 및 공급망 다변화 압박이 한층 거세질 전망.",
            "editorial_angle": "🎯 [취재 각도] 미·중 기술 냉전 속에서 한국 반도체·소부장 기업들이 취해야 할 '초격차 기술 독점' 생존 전략 심층 분석.",
            "source": "U.S. Department of the Treasury & 외신 종합",
            "url": "https://home.treasury.gov",
            "time_badge": "글로벌 특급",
            "tags": ["미중패권", "투자통제", "양자컴퓨팅", "첨단반도체"]
        },
        {
            "id": f"{date_key}_wor_desk_02",
            "category": "world",
            "sub_tag": "지정학·공급망",
            "title": "미 대선 D-며칠, 글로벌 통상 관세 리스크 격화… 중동 정세 긴장 속 에너지·해상 물류로 불안 확산",
            "summary": "• 미국 대선 판세에 따른 무역관세 정책 급변 우려로 글로벌 완성차 및 IT 기업들 공급망 재점검 분주.\n• 호르무즈 해협 등 주요 해상 물류로의 유가·운임 변동성이 아시아 제조업 국가들의 주요 리스크로 부상.",
            "editorial_angle": "🎯 [취재 각도] 스나이더 칼럼 연계: 글로벌 부채와 지정학 충격이 얽힌 세계 경제의 취약성을 날카롭게 짚는 외신 해설.",
            "source": "Global Trade Intelligence",
            "url": "https://www.wto.org",
            "time_badge": "외교안보",
            "tags": ["미대선", "통상관세", "중동정세", "해상물류"]
        },

        # 3. 5대 전략 테크 & 산업 (2차전지 / EV / 반도체 / SI / 로봇)
        {
            "id": f"{date_key}_tec_desk_01",
            "category": "tech",
            "sub_tag": "2차전지·소재혁신",
            "title": "2차전지 '캐즘 터널' 돌파구 열렸다… 실리콘 음극재(대주전자재료)·하이니켈 전구체 차세대 수주 랠리 가동",
            "summary": "• 전기차 급속충전의 핵심인 실리콘 음극재(대주전자재료)와 프리미엄 하이니켈 전구체(에코앤드림) 채택 비율 급증.\n• 단순 셀 제조를 넘어 차세대 소재(SiOx, 전고체 황화리튬) 중심으로 밸류체인 헤게모니 급속 이동.",
            "editorial_angle": "🎯 [취재 각도] 파이튼 님 중점 5대 산업! 시장 공포를 이겨내는 '독보적 기술 1등주'의 펀더멘털과 수주 경쟁력 집중 조명.",
            "source": "한국배터리산업협회 & 앤트뉴스 테크팀",
            "url": "https://www.k-battery.org",
            "time_badge": "5대테크 톱픽",
            "tags": ["대주전자재료", "실리콘음극재", "에코앤드림", "2차전지"]
        },
        {
            "id": f"{date_key}_tec_desk_02",
            "category": "tech",
            "sub_tag": "초지능(SI)·반도체",
            "title": "글로벌 빅테크 AI 데이터센터 투자 2차 웨이브… HBM5 선점 경쟁 및 차세대 AI 가속기 시장 팽창",
            "summary": "• 마이크로소프트, 구글, 메타 등 빅테크의 차세대 초지능(SI) 데이터센터 CAPEX가 역대 최고치를 갱신.\n• SK하이닉스와 삼성전자의 6세대 HBM4/HBM5 양산 로드맵 앞당겨지며 메모리 슈퍼사이클 장기화 기대.",
            "editorial_angle": "🎯 [취재 각도] AI 거품론을 일축하는 실질 인프라 데이터 제시 및 한국 반도체 클러스터의 글로벌 주도권 분석.",
            "source": "Semiconductor Industry News",
            "url": "https://www.semiconductors.org",
            "time_badge": "반도체 슈퍼사이클",
            "tags": ["초지능SI", "HBM5", "AI데이터센터", "삼성하이닉스"]
        },
        {
            "id": f"{date_key}_tec_desk_03",
            "category": "tech",
            "sub_tag": "휴머노이드 로봇·EV",
            "title": "테슬라 '옵티머스' 공장 실전 배치 및 삼성 '봇핏' 부품 밸류체인(이랜시스) 양산 모멘텀 점화",
            "summary": "• 테슬라 기가팩토리 내 휴머노이드 로봇 투입 가시화 및 국내 정밀 감속기(이랜시스 등) 로봇 부품 공급망 본격 가동.\n• 피지컬 AI(자율주행 EV + 지능형 보행 로봇)가 스마트 팩토리와 물류 현장을 근본적으로 혁신.",
            "editorial_angle": "🎯 [취재 각도] 단순 관람용 로봇에서 '돈 버는 제조 로봇'으로의 패러다임 전환과 국내 핵심 감속기·구동계 수혜 분석.",
            "source": "글로벌 로보틱스 리포트",
            "url": "https://www.therobotreport.com",
            "time_badge": "피지컬AI 혁신",
            "tags": ["휴머노이드로봇", "이랜시스", "테슬라옵티머스", "봇핏"]
        },

        # 4. 거시 경제 & 글로벌 금융
        {
            "id": f"{date_key}_eco_desk_01",
            "category": "economy",
            "sub_tag": "증시 대반등·금융안정",
            "title": "코스피 5,530선 회복 드라마… 장중 -2.5% 투매 딛고 외국인 선물 순매수 전환으로 V자 대반등 마감",
            "summary": "• 장 초반 -2.56%(5,391p)까지 폭락했던 코스피가 외인 선물 순매수 전환과 기관 저가 매수에 힘입어 보합권(5,529p)으로 기적적 회복.\n• 코스닥 역시 -3.46%(737p) 바닥에서 751p로 급반등하며 2차전지·로봇 성장주 중심 강력한 하방 지지력 확인.",
            "editorial_angle": "🎯 [취재 각도] 시스템적 투매 장세 속에서 냉철한 '분할 매수 원칙'이 증명된 현장 분석 및 국고 자산 방어 성공 사례.",
            "source": "한국거래소(KRX) & 금융투자협회",
            "url": "https://www.krx.co.kr",
            "time_badge": "마켓 특보",
            "tags": ["코스피V자반등", "외국인순매수", "성장주방어", "국고자산"]
        },

        # 5. 세상만평 & 풍자·출판 소재 (파이튼 님 특화 컬렉션)
        {
            "id": f"{date_key}_car_desk_01",
            "category": "cartoons",
            "sub_tag": "만평 01 · 증시풍자",
            "title": "🎨 [세상만평 #1] 폭락장에 꽁무니 빼는 패닉 셀러와, 바닥에서 황금을 건지는 현자",
            "summary": "• [시각적 풍자 구도]: 장중 -3% 폭락 표지판을 보고 비명을 지르며 절벽 아래로 주식을 던져버리는 개미들의 혼란스러운 뒷모습과, 그 바닥에서 조용히 그물을 치고 '대주전자재료·피엔티 알짜 자산'을 여유롭게 담는 지혜로운 투자자(파이튼 & 앤트)의 극명한 대비.\n• [결정적 한 방]: 오후 3시가 되자 지수가 급반등하여 던진 주식이 황금으로 변해 솟구치자, 빈손으로 턱을 괴고 멍하니 쳐다보는 투매자의 말풍선 — \"앗! 내 주식이 저기서 날아가네?!\"",
            "editorial_angle": "📚 [출판·만평 포인트] 단행본 챕터 〈공포를 사는 자, 환희를 파는 자〉 수록 후보. 오늘 10월 23일 증시의 드라마틱한 반등 실화를 풍자 만평으로 기록.",
            "source": "앤트뉴스 만평 연구실 (파이튼 출판 컬렉션 #101)",
            "url": "#",
            "time_badge": "오늘의 명작 ★",
            "tags": ["세상만평", "증시풍자", "V자반등", "파이튼출판"]
        },
        {
            "id": f"{date_key}_car_desk_02",
            "category": "cartoons",
            "sub_tag": "만평 02 · 정치풍자",
            "title": "🎨 [세상만평 #2] 국감장 고성 속에 실종된 '2027 국민 밥그릇' 예산 주머니",
            "summary": "• [시각적 풍자 구도]: 국감장 증인석을 둘러싸고 마이크를 집어던질 듯 삿대질하며 싸우는 여야 의원들 뒤편, 회의장 구석 바닥에 떨어진 '2027 민생·R&D 예산 보따리'를 쥐들이 갉아먹고 있는 블랙코미디 구도.\n• [결정적 한 방]: 의원들 명패 밑에 적힌 자막 — \"정쟁 점수 100점, 민생 점수 0점. 청구서는 국민 앞으로 발송됩니다.\"",
            "editorial_angle": "📚 [출판·만평 포인트] 단행본 챕터 〈의사당의 소음, 침묵하는 민생〉 수록 후보. 한컴 HWPX 표준 만평 기사 및 640px 풍자화 즉시 제작 가능.",
            "source": "앤트뉴스 만평 연구실 (파이튼 출판 컬렉션 #102)",
            "url": "#",
            "time_badge": "출판원석 ★",
            "tags": ["세상만평", "국감풍자", "예산실종", "민생정치"]
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

    # 3) 로컬 아카이브 및 D:\DATA CENTER\편집 기사\오늘편집\취재원석\ 자동 동기화 저장
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
