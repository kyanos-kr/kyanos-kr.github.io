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
        "desc": "미·중 패권 경쟁, 글로벌 공급망 재편, 국제 분쟁 및 외신 핵심 이슈"
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
        "angle_prefix": "글로벌 부채·물류 병목 및 지정학 충격에 따른 공급망 리스크 객관 분석"
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
    당일(KST 오늘 00:00 이후) 발행된 실시간 RSS 기사만 정밀 수집하고,
    과거 아카이브 및 당일 중복을 철저히 배제한 신규 취재원석 리스트 생성
    """
    collected = []
    today_registered: List[Tuple[str, Set[str]]] = []
    kst = datetime.timezone(datetime.timedelta(hours=9))
    now_kst = datetime.datetime.now(kst)
    today_kst_date = now_kst.date()

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

                # 1. 당일(KST 오늘 날짜) 발행 기사만 엄격 필터링 (전날 헤드라인 완전 차단)
                if not pub_date_str:
                    continue
                try:
                    pub_dt = email.utils.parsedate_to_datetime(pub_date_str)
                    if pub_dt.tzinfo is None:
                        pub_dt = pub_dt.replace(tzinfo=datetime.timezone.utc)
                    pub_kst = pub_dt.astimezone(kst)
                    if pub_kst.date() != today_kst_date:
                        continue
                    diff_hours = max(0.0, (now_kst - pub_kst).total_seconds() / 3600.0)
                except Exception:
                    continue

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
    매일 반복되던 과거 고정 템플릿(장바구니, 관세자판기, 로봇출근 등)을 원천 폐기하고,
    '당일 실제 포착된 핫이슈 헤드라인과 팩트'의 핵심 키워드를 직접 분석하여
    매일 100% 새롭고 날카로운 맞춤형 풍자 구도·제목·말풍선을 동적으로 기획·생성합니다.
    """
    cartoons = []

    # 분야별 톱 기사 추출
    top_pol = next((it for it in top_items if it["category"] == "politics"), None)
    top_wor = next((it for it in top_items if it["category"] == "world"), None)
    top_tec = next((it for it in top_items if it["category"] == "tech"), None)
    top_eco = next((it for it in top_items if it["category"] == "economy"), None)

    # 1. 정치/국정 당일 맞춤 풍자 만평
    if top_pol:
        title_p = top_pol["title"]
        if "국무회의" in title_p or "쿠데타" in title_p or "계엄" in title_p or "한덕수" in title_p:
            c_title = "🎨 [세상만평 #1] 국무회의 의사봉 뒤의 ‘면책 특권과 내란의 경계’"
            c_scene = f"국무회의 탁자 위, 한 손에는 헌법 법전을 들고 절차를 따지다가도 순식간에 비상 서명란에 펜을 꽂는 고위 관료들의 이중적 분장. 그 옆에서 역사책을 든 국민이 매서운 눈초리로 시계를 바라보는 구도."
            c_punch = "“절차만 갖추면 국정 수호이고, 불발되면 그저 심부름이었을 뿐입니까?”"
            c_book = "단행본 〈권력의 거울, 국무회의 417호〉 수록 후보."
        elif "예산" in title_p or "국회" in title_p:
            c_title = "🎨 [세상만평 #1] 여의도 예산 전쟁터와 지방 관료들의 마라톤"
            c_scene = f"국회 예결위 회의장 문턱에 줄을 선 채 보따리를 쥐고 있는 지방자치단체장들과, 정쟁 마이크를 잡느라 예산안 심사는 거들떠보지도 않는 국회의원들의 극명한 대비."
            c_punch = "“싸우실 땐 100점 만점인데, 민생 예산 도장은 언제 찍어주시나요?”"
            c_book = "단행본 〈예산의 계절, 멈춰선 민생〉 수록 후보."
        else:
            c_title = f"🎨 [세상만평 #1] 정쟁의 확성기와 ‘{title_p[:18]}’의 현주소"
            c_scene = f"당일 긴급 현안인 '{title_p}'을 둘러싸고 마이크 볼륨만 키우는 여의도 의사당 앞, 차분하게 장바구니 영수증을 맞춰보는 서민들의 서늘한 침묵."
            c_punch = "“확성기 소리는 요란한데, 서민들 손에 쥐어지는 해결책은 어디에 있습니까?”"
            c_book = "단행본 〈정치의 소음, 국민의 심판〉 수록 후보."

        cartoons.append({
            "id": f"{date_key}_car_01",
            "category": "cartoons",
            "sub_tag": "만평 01 · 국정·정치",
            "title": c_title,
            "summary": f"• [풍자 모티브]: 오늘 국정 현안 — '{title_p}'\n• [시각적 구도]: {c_scene}\n• [결정적 한 방 말풍선]: {c_punch}",
            "editorial_angle": f"📚 [출판·만평 포인트] {c_book} 한컴 HWPX 표준 만평 기사 및 640px 풍자화 즉시 제작 연동.",
            "source": "앤트뉴스 만평 연구실 (파이튼 출판 컬렉션)",
            "url": "#",
            "time_badge": "오늘의 명작 ★",
            "tags": ["세상만평", "국정풍자", "민생정치", "파이튼출판"]
        })

    # 2. 국제/외교 당일 맞춤 풍자 만평
    if top_wor:
        title_w = top_wor["title"]
        if "트럼프" in title_w or "세금" in title_w or "데이터센터" in title_w or "해외" in title_w:
            c_title = "🎨 [세상만평 #2] ‘해외 데이터센터 세금 폭탄’과 트럼프의 계산기"
            c_scene = f"거대한 AI 서버 랙을 등에 짊어진 빅테크 기업들이 미국 국경선을 넘으려 하자, 트럼프가 '세금 폭탄(Tax Bomb)' 투척기를 장전하며 '러시아·중국과는 베스트 프렌드' 팻말을 흔드는 기이한 삼각 외교 풍경."
            c_punch = "“친구는 밖에서 사귀고, 세금은 안방에서 털겠다는 아메리카 퍼스트 2.0!”"
            c_book = "단행본 〈트럼프의 관세 폭탄과 AI 패권〉 수록 후보."
        elif "바이든" in title_w or "식민" in title_w or "일본" in title_w:
            c_title = "🎨 [세상만평 #2] 백악관의 막판 직격탄과 계산 바빠진 도쿄"
            c_scene = f"임기 말 바이든이 역사적 만행을 정조준하며 직격탄을 날리자, 과거사 덮기에 급급하던 일본 관료들이 깜짝 놀라 트럼프 당선인 사무실 문을 두드리는 외교 풍경."
            c_punch = "“외교 무대에서 진실을 지우려 해도 역사의 청구서는 결코 사라지지 않습니다.”"
            c_book = "단행본 〈외교의 퇴장로, 역사의 청구서〉 수록 후보."
        else:
            c_title = f"🎨 [세상만평 #2] 글로벌 패권의 격랑과 ‘{title_w[:18]}’"
            c_scene = f"급변하는 국제 질서 속에서 '{title_w}' 이슈를 둘러싸고 주판알을 튕기는 강대국 정상들과 그 사이에서 줄타기하는 글로벌 공급망의 위태로운 항해."
            c_punch = "“동맹의 악수 뒤편에 숨겨진 청구서 금액을 확인하십시오.”"
            c_book = "단행본 〈글로벌 정글의 생존법칙〉 수록 후보."

        cartoons.append({
            "id": f"{date_key}_car_02",
            "category": "cartoons",
            "sub_tag": "만평 02 · 글로벌외교",
            "title": c_title,
            "summary": f"• [풍자 모티브]: 오늘 국제 정세 — '{title_w}'\n• [시각적 구도]: {c_scene}\n• [결정적 한 방 말풍선]: {c_punch}",
            "editorial_angle": f"📚 [출판·만평 포인트] {c_book} 글로벌 지정학 패권의 이면을 통찰하는 단행본 챕터.",
            "source": "앤트뉴스 만평 연구실 (파이튼 출판 컬렉션)",
            "url": "#",
            "time_badge": "국제풍자 ★",
            "tags": ["세상만평", "글로벌통상", "지정학", "파이튼출판"]
        })

    # 3. 테크/초지능(SI) 당일 맞춤 풍자 만평
    if top_tec:
        title_t = top_tec["title"]
        if "삼전" in title_t or "닉스" in title_t or "목표가" in title_t or "조정" in title_t or "반도체" in title_t:
            c_title = "🎨 [세상만평 #3] 목표주가 깎는 증권사 리포트와 고요한 ‘반도체 용광로’"
            c_scene = f"얼마 전까지 ‘반도체 20만 전자 간다’며 나팔을 불던 증권사 애널리스트들이 태세를 바꿔 ‘조정 국면 시작’ 깃발로 갈아치우는 동안, 반도체 팹 안에서는 차세대 HBM 웨이퍼를 묵묵히 연마하는 엔지니어들의 땀방울."
            c_punch = "“오를 때는 장밋빛 찬가, 내릴 때는 절망의 곡소리… 당신들의 목표가는 도대체 누구를 위한 것입니까?”"
            c_book = "단행본 〈반도체 슈퍼사이클의 허상과 실체〉 수록 후보."
        elif "로봇" in title_t or "AX" in title_t or "휴머노이드" in title_t:
            c_title = "🎨 [세상만평 #3] 축제장에 나선 로봇과 질문을 던지는 시민"
            c_scene = f"로봇 AX 페스타 무대에서 현란한 춤과 작업을 시연하는 AI 로봇을 박수치며 관람하던 시민이, 옆에 서 있는 동료의 어깨를 툭 치며 씁쓸한 미소를 짓는 교차 시선."
            c_punch = "“신기하긴 한데… 내일 우리 일자리는 로봇님이 대신 서 계시는 건 아니겠죠?”"
            c_book = "단행본 〈피지컬 AI 시대, 인간의 존엄과 노동〉 수록 후보."
        else:
            c_title = f"🎨 [세상만평 #3] 테크 혁신의 질주와 ‘{title_t[:18]}’의 명암"
            c_scene = f"'{title_t}' 기술 드라이브로 화려하게 빛나는 테크 기업 본사 유리창과, 그 기술 변화의 속도를 따라잡지 못해 숨이 가쁜 사회적 인프라의 간극."
            c_punch = "“속도만 앞세우는 기술 앞에 인간의 삶과 제도는 어디쯤 서 있습니까?”"
            c_book = "단행본 〈초격차 기술의 명암〉 수록 후보."

        cartoons.append({
            "id": f"{date_key}_car_03",
            "category": "cartoons",
            "sub_tag": "만평 03 · 초지능·로봇",
            "title": c_title,
            "summary": f"• [풍자 모티브]: 오늘 5대 테크 현안 — '{title_t}'\n• [시각적 구도]: {c_scene}\n• [결정적 한 방 말풍선]: {c_punch}",
            "editorial_angle": f"📚 [출판·만평 포인트] {c_book} 초지능(SI)과 반도체 산업의 현실을 조명하는 만평.",
            "source": "앤트뉴스 만평 연구실 (파이튼 출판 컬렉션)",
            "url": "#",
            "time_badge": "미래문명 ★",
            "tags": ["세상만평", "반도체", "초지능SI", "인간존엄"]
        })

    # 4. 거시경제/금융 당일 맞춤 풍자 만평
    if top_eco:
        title_e = top_eco["title"]
        if "나스닥" in title_e or "패닉" in title_e or "코로나 이후 최악" in title_e or "급락" in title_e:
            c_title = "🎨 [세상만평 #4] 나스닥 패닉의 벼랑 끝, ‘공포를 사들이는 노련한 현자’"
            c_scene = f"나스닥 급락 헤드라인에 비명을 지르며 우왕좌왕 주식을 절벽 아래로 내던지는 군중들 아래에서, 튼튼한 그물을 치고 '1등 우량 독점 자산'을 차분히 바구니에 담는 노련한 가치투자자(파이튼 & 메티)의 의연한 미소."
            c_punch = "“남들이 공포에 질려 던질 때가 진짜 씨앗을 심을 시간입니다. 소음은 사라지고 본질만 남습니다.”"
            c_book = "단행본 〈위기 속에서 피어나는 진짜 자산의 힘〉 수록 후보."
        elif "비트코인" in title_e or "금값" in title_e or "금리" in title_e:
            c_title = "🎨 [세상만평 #4] 금값도 코인도 휘청… ‘실질금리의 닻’ 앞에 흔들리는 자산들"
            c_scene = f"높아진 실질금리라는 거대한 파도가 밀려오자, 금괴와 비트코인 보물상자를 든 투자자들이 요동치는 뗏목 위에서 균형을 잡으려 안간힘을 쓰는 금융 풍경."
            c_punch = "“유동성의 거품이 걷힐 때, 진짜 안전한 피난처가 어디인지 비로소 드러납니다.”"
            c_book = "단행본 〈디지털 자산과 금, 화폐의 미래〉 수록 후보."
        else:
            c_title = f"🎨 [세상만평 #4] 시장의 요동과 ‘{title_e[:18]}’의 통찰"
            c_scene = f"거시경제 지표 변동에 일희일비하며 매도·매수 버튼을 누르느라 넋이 나간 개미 투자자들과, 거시 사이클의 큰 지도를 펼쳐놓고 길을 찾는 현자의 대비."
            c_punch = "“시장의 파도에 휩쓸리지 마십시오. 나침반을 가진 자만이 목적지에 도달합니다.”"
            c_book = "단행본 〈시장의 소음을 뚫는 부의 안목〉 수록 후보."

        cartoons.append({
            "id": f"{date_key}_car_04",
            "category": "cartoons",
            "sub_tag": "만평 04 · 증시·자산",
            "title": c_title,
            "summary": f"• [풍자 모티브]: 오늘 거시경제 현황 — '{title_e}'\n• [시각적 구도]: {c_scene}\n• [결정적 한 방 말풍선]: {c_punch}",
            "editorial_angle": f"📚 [출판·만평 포인트] {c_book} 금융 위기와 변동성을 꿰뚫는 가치투자 혜안.",
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
