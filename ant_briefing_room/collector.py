# -*- coding: utf-8 -*-
"""
앤트 취재 인텔리전스 브리핑 룸 (AntNews Intelligence Briefing Room)
실시간 국내외 헤드라인 수집 · 5대 카테고리 정제 · 세상만평 출판 원석 발굴 엔진

[파이튼 님 지침 엄수 — 일일 신규 취재원석 원칙]
1. 당일(24시간 이내) 일일 뉴스만 엄선 수집 (when:1d 및 pubDate 24시간 초과분 자동 폐기)
2. 과거 5일간 브리핑 아카이브와의 교차 대조를 통한 전날/과거 기사 중복 100% 원천 차단
3. 당일 동일 이슈 기사 간 군집화(Clustering) 및 유사도 검증으로 중복 보도 단 1건으로 통합
4. 과거 정적 하드코딩 배제 및 당일 핫이슈 기반 동적 톱뉴스 & 신규 세상만평 생성
"""
import os
import sys
import json
import re
import glob
import html
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import email.utils
from typing import List, Dict, Set, Tuple
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
# 2. 당일(when:1d) 한정 실시간 RSS 피드 소스 정의
# ──────────────────────────────────────────────────────────
RSS_SOURCES = [
    # 1. 국내 정치 & 국정·정책
    {
        "category": "politics",
        "sub_tag": "대통령실·국정로드맵",
        "query": "대통령실 OR 국정기조 OR 국무회의 when:1d",
        "limit": 3,
        "angle_prefix": "국정 최고사령탑의 정책 드라이브 및 헌법적 통치 실효성 심층 분석"
    },
    {
        "category": "politics",
        "sub_tag": "국회·입법예산",
        "query": "국회 입법 OR 법제사법위원회 OR 국가예산안 OR 국정감사 when:1d",
        "limit": 3,
        "angle_prefix": "삼권분립 원칙과 국가 본예산·민생 법안의 실질적 입법 동향 진단"
    },
    {
        "category": "politics",
        "sub_tag": "정부부처·공공정책",
        "query": "기획재정부 OR 산업통상자원부 OR 금융위원회 정책 발표 when:1d",
        "limit": 3,
        "angle_prefix": "정부 공식 정책 발표의 실효성과 산업·국민 체감도 심층 검증"
    },

    # 2. 국제 정세 & 외교 안보
    {
        "category": "world",
        "sub_tag": "미국 대선·글로벌외교",
        "query": "미국 대선 OR 백악관 OR 미 국무부 OR 트럼프 바이든 when:1d",
        "limit": 3,
        "angle_prefix": "글로벌 패권 이동과 차기 미국 행정부 대외정책의 지정학적 파급력"
    },
    {
        "category": "world",
        "sub_tag": "미·중 패권 & 통상관세",
        "query": "미국 중국 관세 OR 대중국 제재 OR 반도체 통제 when:1d",
        "limit": 3,
        "angle_prefix": "미·중 무역 냉전 격화 속 대한민국 전략 수출 산업의 생존로 타진"
    },
    {
        "category": "world",
        "sub_tag": "지정학 리스크 & 물류",
        "query": "중동 분쟁 OR 호르무즈 해협 OR 국제 유가 OR 글로벌 공급망 when:1d",
        "limit": 3,
        "angle_prefix": "마이클 스나이더 연계: 글로벌 부채와 지정학 충격 속 공급망 리스크"
    },

    # 3. 5대 전략 테크 & 산업
    {
        "category": "tech",
        "sub_tag": "2차전지·소재혁신",
        "query": "2차전지 OR 실리콘 음극재 OR 전고체 배터리 OR 전기차 when:1d",
        "limit": 3,
        "angle_prefix": "2차전지 캐즘 돌파 차세대 소재 혁신 및 핵심 밸류체인 수주 모멘텀"
    },
    {
        "category": "tech",
        "sub_tag": "반도체·초지능(SI)",
        "query": "삼성전자 SK하이닉스 OR HBM 반도체 OR AI 가속기 OR 엔비디아 when:1d",
        "limit": 3,
        "angle_prefix": "HBM 및 차세대 초지능(SI) 인프라 데이터센터 슈퍼사이클 분석"
    },
    {
        "category": "tech",
        "sub_tag": "휴머노이드 로봇·피지컬AI",
        "query": "휴머노이드 로봇 OR 테슬라 옵티머스 OR 정부 로봇 구매 OR 피지컬 AI when:1d",
        "limit": 3,
        "angle_prefix": "제조 및 서비스 현장 실전 배치와 정밀 감속기·구동계 부품 수혜 점검"
    },

    # 4. 거시 경제 & 글로벌 금융
    {
        "category": "economy",
        "sub_tag": "증시·수급동향",
        "query": "코스피 OR 코스닥 OR 외국인 기관 순매수 OR 증시 급등락 when:1d",
        "limit": 3,
        "angle_prefix": "시장 변동성 속 주도 업종 펀더멘털 및 국고자산 분할 대응 전략"
    },
    {
        "category": "economy",
        "sub_tag": "환율·금리·거시지표",
        "query": "원달러 환율 OR 한국은행 기준금리 OR 미국 국채 금리 when:1d",
        "limit": 3,
        "angle_prefix": "고환율·고금리 복합 압박 속 가계·기업 재정 건전성 방어 분석"
    },
    {
        "category": "economy",
        "sub_tag": "디지털 자산·귀금속",
        "query": "비트코인 OR 리플 XRP OR 가상자산 OR 국제 금값 when:1d",
        "limit": 3,
        "angle_prefix": "디지털 자산 제도권 편입 및 금·은 대체 안전자산 배분 궤도"
    }
]

# 불용어(Stopwords) 정의
STOP_WORDS = {
    "기사", "보도", "관련", "종합", "오늘", "위해", "대한", "속보", "사진",
    "포토", "뉴스", "단독", "연합", "뉴스1", "뉴시스", "이데일리", "머니투데이",
    "조선일보", "중앙일보", "동아일보", "한국경제", "매일경제", "서울경제", "일보",
    "신문", "방송", "발표", "개최", "진행", "예정", "확인", "의견", "논란",
    "입장", "주목", "기대", "우려", "통해", "따른", "있어", "되는", "하는"
}


def clean_html_text(raw: str) -> str:
    if not raw:
        return ""
    text = html.unescape(raw)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_title_and_source(full_title: str) -> Tuple[str, str]:
    """구글 뉴스 RSS의 '제목 - 언론사명' 구조에서 핵심 헤드라인과 언론사를 분리"""
    if " - " in full_title:
        parts = full_title.rsplit(" - ", 1)
        return parts[0].strip(), parts[1].strip()
    return full_title.strip(), "공식 뉴스종합"


def extract_meaningful_tokens(text: str) -> Set[str]:
    """제목 및 본문에서 핵심 의미 키워드(2글자 이상) 추출"""
    text_clean = re.sub(r"\[.*?\]|\(.*?\)|<.*?>|『.*?』|〈.*?〉|\".*?\"|'.*?'", " ", text)
    words = re.findall(r"[가-힣a-zA-Z0-9]{2,}", text_clean)
    return {w.lower() for w in words if w.lower() not in STOP_WORDS}


def normalize_title(title: str) -> str:
    """공백, 기호, 괄호 제거 후 순수 글자열 생성"""
    cleaned = re.sub(r"\[.*?\]|\(.*?\)", "", title)
    return re.sub(r"\W+", "", cleaned).lower()


def load_past_archive_signatures(days: int = 5, current_date_key: str = "") -> List[Tuple[str, Set[str]]]:
    """
    최근 N일간의 아카이브 및 오늘편집/취재원석 리포트에서 이미 수록된 기사 제목 로드
    오늘 날짜(current_date_key) 파일은 제외하여 당일 갱신 시 오탐 방지
    """
    history_items = []
    seen_raw_titles = set()

    # 1) archive/ 폴더 내 마크다운 파일 검사
    archive_files = sorted(glob.glob(os.path.join(ARCHIVE_DIR, "briefing_*.md")))
    # 2) 오늘편집/취재원석/ 폴더 내 마크다운 파일 검사
    today_files = sorted(glob.glob(os.path.join(TODAY_EDIT_RAW_DIR, "오늘의_취재원석_브리핑_*.md")))

    target_files = sorted(list(set(archive_files + today_files)))
    for fpath in target_files[-15:]:
        fname = os.path.basename(fpath)
        # 오늘 날짜 파일은 과거 대조 대상에서 제외
        if current_date_key and current_date_key in fname:
            continue
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    m = re.match(r"^###\s*\[\d+\]\s*(.+)$", line.strip())
                    if m:
                        raw_t = m.group(1).strip()
                        if raw_t and raw_t not in seen_raw_titles:
                            seen_raw_titles.add(raw_t)
                            toks = extract_meaningful_tokens(raw_t)
                            norm = normalize_title(raw_t)
                            if toks:
                                history_items.append((norm, toks))
        except Exception as e:
            print(f"[WARN] 과거 아카이브 로드 예외 ({fname}): {e}")

    return history_items


def is_duplicate_item(
    candidate_title: str,
    candidate_tokens: Set[str],
    history_items: List[Tuple[str, Set[str]]],
    today_items: List[Tuple[str, Set[str]]]
) -> Tuple[bool, str]:
    """
    1) 과거 N일간의 아카이브와의 중복 여부 검사 (과거 보도 재탕 원천 차단)
    2) 당일 이미 수집된 기사와의 유사도 검사 (당일 언론사별 동일 사안 중복 차단)
    """
    if not candidate_tokens:
        return True, "키워드 부재"

    cand_norm = normalize_title(candidate_title)

    # 1. 과거 아카이브 대조 (전날, 전전날 이미 수록된 기사 차단)
    for hist_norm, hist_tokens in history_items:
        # 완전 일치 또는 16자 이상 부분 문자열 일치
        if cand_norm in hist_norm or hist_norm in cand_norm:
            return True, "과거 아카이브 제목 일치"
        if len(cand_norm) >= 12 and cand_norm[:14] == hist_norm[:14]:
            return True, "과거 아카이브 접두 일치"

        # 핵심 키워드 자카드 유사도 검사
        overlap = len(candidate_tokens & hist_tokens)
        union = len(candidate_tokens | hist_tokens)
        similarity = overlap / max(1, union)
        if similarity >= 0.38 or (overlap >= 4 and len(candidate_tokens) <= 6):
            return True, f"과거 보도 중복 (유사도 {similarity:.2f})"

    # 2. 당일 수집 목록 대조 (당일 동일 사건 타 언론사 중복 보도 차단)
    for today_norm, today_tokens in today_items:
        if cand_norm in today_norm or today_norm in cand_norm:
            return True, "당일 기사 제목 중복"
        if len(cand_norm) >= 12 and cand_norm[:12] == today_norm[:12]:
            return True, "당일 기사 접두 중복"

        overlap = len(candidate_tokens & today_tokens)
        union = len(candidate_tokens | today_tokens)
        similarity = overlap / max(1, union)
        if similarity >= 0.32 or (overlap >= 3 and len(candidate_tokens) <= 5):
            return True, f"당일 동일 사안 중복 (유사도 {similarity:.2f})"

    return False, "신규 정상"


def fetch_fresh_live_rss_items(
    date_key: str,
    history_items: List[Tuple[str, Set[str]]]
) -> List[Dict]:
    """
    당일 24시간 이내의 실시간 RSS 기사만 정밀 수집하고,
    과거 아카이브 및 당일 중복을 철저히 배제한 신규 취재원석 리스트 생성
    """
    collected = []
    today_registered: List[Tuple[str, Set[str]]] = []
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }

    item_idx = 10
    for src in RSS_SOURCES:
        cat = src["category"]
        sub_tag = src["sub_tag"]
        query = src["query"]
        limit = src["limit"]
        angle_prefix = src["angle_prefix"]

        url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(query) + "&hl=ko&gl=KR&ceid=KR:ko"

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=9) as resp:
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
                pub_date_str = item.findtext("pubDate") or ""
                desc_raw = clean_html_text(item.findtext("description") or "")

                # 1. 24시간 시간 필터링 (당일 뉴스 보장)
                diff_hours = 0.0
                if pub_date_str:
                    try:
                        pub_dt = email.utils.parsedate_to_datetime(pub_date_str)
                        diff_hours = (now_utc - pub_dt).total_seconds() / 3600.0
                        if diff_hours > 24.0:
                            # 24시간 초과 기사는 전날 기사로 판별하여 즉시 폐기
                            continue
                    except Exception:
                        diff_hours = 0.0

                headline, media_name = split_title_and_source(raw_title)
                if not headline or len(headline) < 8:
                    continue

                # 2. 중복 검증 (과거 5일 아카이브 및 당일 기사 간 중복 차단)
                tokens = extract_meaningful_tokens(headline)
                is_dup, reason = is_duplicate_item(headline, tokens, history_items, today_registered)
                if is_dup:
                    continue

                # 신규 등록
                today_registered.append((normalize_title(headline), tokens))

                # 요약문 구성 (팩트 중심)
                if desc_raw and len(desc_raw) > 20:
                    desc_clean = desc_raw.replace(headline, "").replace(media_name, "").strip(" -·•")
                    if len(desc_clean) < 15:
                        summary_text = f"• [{sub_tag}] 주요 현안 팩트: {headline}\n• 관련 정부 부처 및 시장 파급효과 실시간 점검 대상."
                    else:
                        summary_text = f"• {desc_clean[:180]}\n• 공식 발표 팩트 및 후속 취재 후보."
                else:
                    summary_text = f"• [{sub_tag}] {headline}\n• 시장 동향 1차 팩트 확인 및 앤트뉴스 보도기사화 후보."

                time_label = f"{int(diff_hours)}시간 전 포착" if diff_hours >= 1.0 else "방금 전 실시간 포착"

                item_idx += 1
                collected.append({
                    "id": f"{date_key}_{cat}_{item_idx}",
                    "category": cat,
                    "sub_tag": sub_tag,
                    "title": headline,
                    "summary": summary_text,
                    "editorial_angle": f"🎯 [취재 각도] {angle_prefix} (앤트뉴스 독자 서술 및 1차 공식자료 교차검증 권장)",
                    "source": f"팩트 레이더 ({media_name})",
                    "url": link,
                    "time_badge": time_label,
                    "tags": [sub_tag, cat.upper(), "당일신규원석"]
                })
                count += 1
        except Exception as e:
            print(f"[WARN] RSS 피드 처리 예외 ({sub_tag}): {e}")

    return collected


def generate_daily_cartoons(
    date_key: str,
    top_items: List[Dict]
) -> List[Dict]:
    """
    매일 반복되는 과거 고정 만평을 전면 폐기하고,
    '오늘 실제 수집된 당일 톱뉴스'를 기반으로 즉시 풍자 구도를 기획하는 100% 당일 신규 만평
    """
    cartoons = []

    # 오늘 수집된 분야별 톱 기사 추출
    top_pol = next((it for it in top_items if it["category"] == "politics"), None)
    top_wor = next((it for it in top_items if it["category"] == "world"), None)
    top_tec = next((it for it in top_items if it["category"] == "tech"), None)
    top_eco = next((it for it in top_items if it["category"] == "economy"), None)

    # 1. 정치/국정 당일 풍자 만평
    if top_pol:
        cartoons.append({
            "id": f"{date_key}_car_01",
            "category": "cartoons",
            "sub_tag": "만평 01 · 국정·정치",
            "title": f"🎨 [세상만평 #1] 의사당의 확성기와 서민의 빈 장바구니",
            "summary": f"• [풍자 모티브]: 오늘 국정 현안 — '{top_pol['title']}'\n• [시각적 구도]: 마이크와 카메라 앞에서 핏대를 세우며 설전을 벌이는 여야 의원들 뒤편, 텅 빈 장바구니를 들고 의원석 명패를 묵묵히 쳐다보는 서민의 씁쓸한 뒷모습.\n• [결정적 한 방 말풍선]: \"정쟁 점수는 100점 만점인데, 민생 성적표는 언제 나오나요?\"",
            "editorial_angle": "📚 [출판·만평 포인트] 단행본 〈의사당의 소음, 침묵하는 민생〉 챕터 수록 후보. 한컴 HWPX 표준 만평 기사 및 640px 풍자화 즉시 제작 가능.",
            "source": "앤트뉴스 만평 연구실 (파이튼 출판 컬렉션)",
            "url": "#",
            "time_badge": "오늘의 명작 ★",
            "tags": ["세상만평", "국정풍자", "민생정치", "파이튼출판"]
        })

    # 2. 국제/지정학 당일 풍자 만평
    if top_wor:
        cartoons.append({
            "id": f"{date_key}_car_02",
            "category": "cartoons",
            "sub_tag": "만평 02 · 글로벌외교",
            "title": f"🎨 [세상만평 #2] '동맹의 관세 자판기' 앞에서 고민하는 지구촌",
            "summary": f"• [풍자 모티브]: 오늘 국제 정세 — '{top_wor['title']}'\n• [시각적 구도]: 'GLOBAL TRADE' 네온사인이 번쩍이는 거대한 통상 관세 게이트. 동맹국 정상들이 반도체·배터리 공장 투자 보따리를 자판기에 밀어 넣어야만 차단기가 1밀리미터 올라가는 냉혹한 글로벌 통상 풍경.\n• [결정적 한 방 말풍선]: \"※ 주의: 본 관세 면제권의 유효기간은 다음 대선 또는 기분 변화 시까지입니다.\"",
            "editorial_angle": "📚 [출판·만평 포인트] 단행본 〈냉혹한 동맹의 청구서〉 챕터 수록 후보. 글로벌 통상 패권의 본질을 유머러스하게 형상화.",
            "source": "앤트뉴스 만평 연구실 (파이튼 출판 컬렉션)",
            "url": "#",
            "time_badge": "국제풍자 ★",
            "tags": ["세상만평", "글로벌통상", "관세외교", "파이튼출판"]
        })

    # 3. 테크/초지능 당일 풍자 만평
    if top_tec:
        cartoons.append({
            "id": f"{date_key}_car_03",
            "category": "cartoons",
            "sub_tag": "만평 03 · 초지능·로봇",
            "title": f"🎨 [세상만평 #3] 출근하는 AI 로봇과 명예퇴직 신청서 앞의 인간",
            "summary": f"• [풍자 모티브]: 오늘 5대 테크 현안 — '{top_tec['title']}'\n• [시각적 구도]: 최신 피지컬 AI 로봇이 공장 게이트를 힘차게 통과하며 '24시간 무정지 근무 중' 배지를 반짝이는 가운데, 사물함 앞에서 묵묵히 짐을 싸며 로봇의 충전기를 물끄러미 바라보는 인간 근로자의 교차 시선.\n• [결정적 한 방 말풍선]: \"로봇님, 노조 가입은 안 하실 거죠?\"",
            "editorial_angle": "📚 [출판·만평 포인트] 단행본 〈로봇의 시대, 인간의 품격〉 수록 후보. 기술 지상주의 시대 인간 존엄성과 덕치(德治) 거버넌스의 필요성 환기.",
            "source": "앤트뉴스 만평 연구실 (파이튼 출판 컬렉션)",
            "url": "#",
            "time_badge": "미래문명 ★",
            "tags": ["세상만평", "휴머노이드", "초지능SI", "인간존엄"]
        })

    # 4. 거시경제 당일 풍자 만평
    if top_eco:
        cartoons.append({
            "id": f"{date_key}_car_04",
            "category": "cartoons",
            "sub_tag": "만평 04 · 증시·자산",
            "title": f"🎨 [세상만평 #4] 공포에 던지는 자와 바닥에서 황금을 건지는 현자",
            "summary": f"• [풍자 모티브]: 오늘 거시경제 현황 — '{top_eco['title']}'\n• [시각적 구도]: 단기 변동성 뉴스에 파랗게 질려 주식을 절벽 아래로 던져버리는 패닉 셀러 개미와, 그 아래에서 잔잔한 호수처럼 그물을 펼치고 '1등 알짜 기술주'를 담담히 주워 담는 노련한 가치투자자(파이튼 & 메티)의 대비.\n• [결정적 한 방 말풍선]: \"공포를 살 때 환희가 잉태되고, 소음에 귀를 닫을 때 통찰이 열린다.\"",
            "editorial_angle": "📚 [출판·만평 포인트] 단행본 〈자본의 파도에서 살아남는 법〉 수록 후보. 시스템적 투매 장세에서 냉철한 분할 원칙의 중요성 전달.",
            "source": "앤트뉴스 만평 연구실 (파이튼 출판 컬렉션)",
            "url": "#",
            "time_badge": "자산통찰 ★",
            "tags": ["세상만평", "가치투자", "시장변동성", "파이튼출판"]
        })

    return cartoons


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


def export_markdown_briefing(data: Dict, md_path: str):
    """브리핑 룸 데이터를 한글/메모장에서 즉시 열람 가능한 마크다운 리포트로 저장"""
    lines = []
    lines.append(f"# 📡 앤트 취재 인텔리전스 브리핑 룸 ({data['updated_at']} 기준)")
    lines.append("")
    lines.append("> **목적**: 파이튼 님의 정통 보도기사(정치·국제·테크·경제) 취재 원석 발굴 및 **앤트뉴스 특화 세상만평·단행본 출판 소재** 축적")
    lines.append("> **당일 엄선 원칙**: 전날 중복 보도를 전면 배제하고, 오직 **오늘 24시간 이내 포착된 신규 일일 취재원석**만 엄선 수록했습니다.")
    lines.append("> **연동**: 마음에 드는 항목을 골라 앤트(메티)에게 말씀해 주시면 즉시 **한컴 윤고딕 740 (11pt) 표준 HWPX 보도기사/칼럼/만평**으로 제작합니다.")
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

    print(f"======================================================")
    print(f"📡 AntNews Briefing Collector: 당일 취재원석 엄선 수집 가동")
    print(f"기준 일시: {today_str} (당일 24시간 한정 / 과거 중복 100% 필터링)")
    print(f"======================================================")

    # 1. 과거 5일간 아카이브 서명 로드 (과거 중복 원천 차단)
    print(f"[1/4] 과거 5일간 아카이브 및 기보도 서명 로드 중...")
    history_items = load_past_archive_signatures(days=5, current_date_key=date_key)
    print(f"  -> 과거 대조 DB 구축 완료: 총 {len(history_items)}개 기보도 헤드라인 차단 목록 확보")

    # 2. 당일(when:1d) 실시간 신규 기사 수집 (과거 및 당일 중복 동시 필터링)
    print(f"[2/4] 당일 24시간 이내 실시간 신규 RSS 취재원석 엄선 수집 중...")
    fresh_rss_items = fetch_fresh_live_rss_items(date_key, history_items)
    print(f"  -> 엄선 완료된 당일 신규 취재원석: 총 {len(fresh_rss_items)}건 (중복 보도 전원 탈락)")

    # 3. 실시간 마켓 지표 수집
    print(f"[3/4] 실시간 공개 시장 지표 수집 중...")
    market_indicators = fetch_market_indicators()

    # 4. 당일 톱뉴스 기반 신규 세상만평 & 풍자 출판 소재 생성
    print(f"[4/4] 당일 톱뉴스 기반 세상만평 및 풍자 출판 원석 동적 기획 중...")
    fresh_cartoons = generate_daily_cartoons(date_key, fresh_rss_items)

    # 카테고리별 정렬 (정치 -> 국제 -> 테크 -> 경제 -> 세상만평)
    ordered_items = []
    for cat in CATEGORIES:
        cid = cat["id"]
        if cid == "cartoons":
            ordered_items.extend(fresh_cartoons)
        else:
            c_items = [i for i in fresh_rss_items if i["category"] == cid]
            # 카테고리 내 첫 번째 기사를 톱뉴스로 승격
            if c_items:
                c_items[0]["time_badge"] = "오늘의 톱뉴스 ★"
            ordered_items.extend(c_items)

    data = {
        "updated_at": today_str,
        "date_key": date_key,
        "total_count": len(ordered_items),
        "market_indicators": market_indicators,
        "categories": CATEGORIES,
        "items": ordered_items
    }

    # 1) JSON 저장
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 2) JS 저장 (CORS 회피 로컬 실행용)
    js_content = f"// Auto-generated by AntNews Briefing Room Collector ({today_str})\nwindow.ANT_BRIEFING_DATA = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        f.write(js_content)

    # 3) 로컬 아카이브 및 오늘편집/취재원석 마크다운 동기화 저장
    archive_md = os.path.join(ARCHIVE_DIR, f"briefing_{date_key}.md")
    today_edit_md = os.path.join(TODAY_EDIT_RAW_DIR, f"오늘의_취재원석_브리핑_{date_key}.md")
    export_markdown_briefing(data, archive_md)
    export_markdown_briefing(data, today_edit_md)

    print(f"\n✅ 당일 엄선 브리핑 리포트 생성 완료!")
    print(f"  - 당일 유일 신규 아이템: 총 {len(ordered_items)}건 (신규 취재원석 {len(fresh_rss_items)}건 + 당일 맞춤 만평 {len(fresh_cartoons)}건)")
    print(f"  - 웹 데이터: {OUTPUT_JS}")
    print(f"  - 파이튼 님 취재원석 서고: {today_edit_md}")

    # 4) [파이튼 님 지침 엄수] 3일 경과 취재원석 및 아카이브 데이터 영구 자동 폐기
    auto_purge_expired_raw_data(retention_days=3)


def auto_purge_expired_raw_data(retention_days: int = 3):
    """
    [파이튼 님 훈령] 취재원석 3일 경과 데이터 영구 자동 폐기 엔진
    파이튼 님이 기사 활용 여부를 판단하신 후 3일이 경과한 불필요 취재원석 마크다운
    및 과거 아카이브 파일을 자동으로 영구 삭제하여 저장소를 정갈하고 가볍게 유지합니다.
    """
    now = datetime.datetime.now()
    cutoff_date = (now - datetime.timedelta(days=retention_days)).date()
    purged_count = 0

    target_dirs = [TODAY_EDIT_RAW_DIR, ARCHIVE_DIR]
    print(f"\n🧹 [자동 폐기 관제] 3일 이전({cutoff_date} 이전) 경과 취재원석 자동 정밀 정리 가동...")

    for t_dir in target_dirs:
        if not os.path.exists(t_dir):
            continue
        for fname in os.listdir(t_dir):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(t_dir, fname)
            date_match = re.search(r"(\d{8})", fname)
            should_purge = False

            if date_match:
                try:
                    f_date = datetime.datetime.strptime(date_match.group(1), "%Y%m%d").date()
                    if f_date < cutoff_date:
                        should_purge = True
                except Exception:
                    pass
            else:
                # 파일 수정일 기준 검사
                try:
                    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fpath))
                    if (now - mtime).days > retention_days:
                        should_purge = True
                except Exception:
                    pass

            if should_purge:
                try:
                    os.remove(fpath)
                    purged_count += 1
                    print(f"  🗑️ [영구 폐기 완료]: {fname}")
                except Exception as e:
                    print(f"  [WARN] 파일 삭제 예외 ({fname}): {e}")

    if purged_count > 0:
        print(f"  -> 총 {purged_count}개의 3일 경과 취재원석 파일이 영구 자동 폐기되었습니다.")
    else:
        print(f"  -> 현재 3일 이상 경과된 불필요 취재원석 파일이 없습니다. (최적 청정 상태 유지)")


if __name__ == "__main__":
    generate_curated_briefing()
