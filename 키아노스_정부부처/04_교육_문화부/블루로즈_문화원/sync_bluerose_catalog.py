# -*- coding: utf-8 -*-
"""
키아노스 교육·문화부 — 블루로즈 문화원 자동 카탈로그 동기화 엔진
assets/images/, assets/posters/ 및 문학·헤리티지 자산을 스캔하여
assets/bluerose_catalog.json 을 생성·갱신합니다.
"""
import json
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(r"d:\안티그래비티파이튼")
IMAGES_DIR = ROOT_DIR / "assets" / "images"
PHOTO_DIR = IMAGES_DIR / "bluerose_photo"
POSTERS_DIR = ROOT_DIR / "assets" / "posters"
OUTPUT_JSON = ROOT_DIR / "assets" / "bluerose_catalog.json"

ARTWORK_META = {
    "camus_stranger_plague.jpg": {
        "title": "부조리의 태양과 연대의 등불",
        "category": "세계문학 아트워크",
        "subtitle": "알베르 카뮈 — 이방인 · 페스트",
        "description": "실존의 부조리 속에서도 인간의 존엄과 연대를 포기하지 않는 문학적 성찰을 담은 블루로즈 고전 회화."
    },
    "saint_exupery_little_prince.jpg": {
        "title": "사막의 별빛과 길들여진 장미",
        "category": "세계문학 아트워크",
        "subtitle": "생텍쥐페리 — 어린 왕자",
        "description": "눈에 보이지 않는 본질과 사랑의 책임을 별빛 아래 장미의 은유로 그려낸 서정 아트워크."
    },
    "laozi_tao_te_ching.jpg": {
        "title": "상선약수(上善若水), 고요한 도의 강물",
        "category": "동서양 철학 회화",
        "subtitle": "노자 — 도덕경",
        "description": "물처럼 다투지 않고 만물을 이롭게 하는 덕치(德治)의 근원을 수묵과 빛으로 형상화한 작품."
    },
    "hesse_siddhartha.jpg": {
        "title": "깨달음의 강가에서 듣는 영원의 소리",
        "category": "세계문학 아트워크",
        "subtitle": "헤르만 헤세 — 싯다르타",
        "description": "구도자의 방황 끝에 흐르는 강물 속에서 모든 시간의 합일을 깨닫는 순간을 포착한 작품."
    },
    "poincare_conjecture.jpg": {
        "title": "우주의 위상과 영원의 구(球)",
        "category": "지성·과학 미학",
        "subtitle": "앙리 푸앵카레 — 우주의 형태학",
        "description": "수학적 대칭성과 우주의 기하학적 아름다움을 푸른 심연의 빛으로 시각화한 지성 예술."
    },
    "thomas_more_utopia.jpg": {
        "title": "이상향 유토피아의 항구",
        "category": "동서양 철학 회화",
        "subtitle": "토마스 모어 — 유토피아",
        "description": "정의와 공동선이 살아 숨 쉬는 이상 국가의 항구를 고전적 구도로 그려낸 사유화."
    },
    "maugham_moon_and_sixpence.jpg": {
        "title": "달을 쫓는 영혼의 붓질",
        "category": "세계문학 아트워크",
        "subtitle": "서머싯 몸 — 달과 6펜스",
        "description": "현실의 안락함(6펜스)을 버리고 이상과 예술(달)을 향해 나아가는 순수 예술혼의 초상."
    },
    "daudet_the_stars.jpg": {
        "title": "프로방스 밤하늘의 별들",
        "category": "세계문학 아트워크",
        "subtitle": "알퐁스 도데 — 별",
        "description": "순수한 사랑과 밤하늘의 별빛이 어우러지는 목가적 서정을 담은 감성 일러스트."
    },
    "daudet_the_last_lesson.jpg": {
        "title": "마지막 수업, 칠판 위의 언어",
        "category": "세계문학 아트워크",
        "subtitle": "알퐁스 도데 — 마지막 수업",
        "description": "모국어와 정신의 유산을 끝까지 지켜내려는 스승의 마지막 기록을 담은 역사 문학화."
    },
    "dickens_great_expectations.jpg": {
        "title": "안개 낀 템즈와 위대한 유산",
        "category": "세계문학 아트워크",
        "subtitle": "찰스 디킨스 — 위대한 유산",
        "description": "성장과 회한, 그리고 인간적 성숙으로 나아가는 고전 서사의 극적 장면을 담은 작품."
    },
    "flaubert_madame_bovary.jpg": {
        "title": "창가의 몽상과 고전의 빛",
        "category": "세계문학 아트워크",
        "subtitle": "귀스타브 플로베르 — 보바리 부인",
        "description": "근대 리얼리즘 문학의 정점에서 인간의 욕망과 현실의 간극을 섬세하게 포착한 작품."
    },
    "sartre_nausea.jpg": {
        "title": "실존의 거리, 고독한 사색",
        "category": "동서양 철학 회화",
        "subtitle": "장 폴 사르트르 — 구토",
        "description": "존재가 본질에 앞선다는 실존주의 철학의 고뇌를 짙은 음영으로 표현한 현대 사유화."
    },
    "kyanos_official_poster_kr.png": {
        "title": "키아노스 건국 공식 포스터 (국문판)",
        "category": "국가 상징 포스터",
        "subtitle": "Kyanos Sovereign Nation Official Poster",
        "description": "덕치와 초지능(SI)의 조화를 천명한 키아노스 정부의 공식 국문 상징 포스터."
    },
    "kyanos_official_poster_en.png": {
        "title": "키아노스 건국 공식 포스터 (영문판)",
        "category": "국가 상징 포스터",
        "subtitle": "Kyanos Global Vision Poster",
        "description": "세계 시민과 국제 학술·문화 교류를 향해 키아노스의 비전을 선포하는 영문 공식 포스터."
    },
    "kyanos_official_poster_hybrid.png": {
        "title": "키아노스 하이브리드 비전 포스터",
        "category": "국가 상징 포스터",
        "subtitle": "East-West & SI Harmony Edition",
        "description": "동서양 문명과 미래 초지능의 융합 미학을 담은 하이브리드 에디션 공식 포스터."
    },
    "01_jeongseojin_sunset.jpg": {
        "title": "정서진의 고요한 서해 낙조",
        "category": "파이튼 포토 컬렉션",
        "subtitle": "파이튼 오리지널 포토 · 인천 정서진",
        "description": "광화문의 정서쪽에 자리한 정서진에서 담아낸 서해의 유장한 빛과 여운."
    },
    "02_bomunsa_temple.jpg": {
        "title": "석모도 보문사 천년 고찰의 정취",
        "category": "파이튼 포토 컬렉션",
        "subtitle": "파이튼 오리지널 포토 · 강화 보문사",
        "description": "바다와 산사가 어우러지는 보문사 경내의 고즈넉한 건축미와 사색의 공간."
    },
    "03_heungguksa_autumn.jpg": {
        "title": "흥국사의 깊은 가을 단풍",
        "category": "파이튼 포토 컬렉션",
        "subtitle": "파이튼 오리지널 포토 · 흥국사",
        "description": "가을빛으로 물든 산사의 고요한 처마와 단풍이 빚어내는 한국적 서정."
    },
    "04_ara_sicheon_bridge.jpg": {
        "title": "아라뱃길 시천교의 물빛 풍경",
        "category": "파이튼 포토 컬렉션",
        "subtitle": "파이튼 오리지널 포토 · 경인 아라뱃길",
        "description": "물길을 가로지르는 시천교와 잔잔한 수면이 어우러진 도심 속 쉼표."
    },
    "05_jeonnyuri_hangang.jpg": {
        "title": "전류리포구 가는 길, 한강 하구",
        "category": "파이튼 포토 컬렉션",
        "subtitle": "파이튼 오리지널 포토 · 김포 전류리포구",
        "description": "한강이 서해로 흘러드는 전류리포구 길목에서 포착한 탁 트인 강변의 숨결."
    },
    "06_haengju_hangang.jpg": {
        "title": "행주산성에서 바라본 한강 물줄기",
        "category": "파이튼 포토 컬렉션",
        "subtitle": "파이튼 오리지널 포토 · 행주산성",
        "description": "역사의 숨결이 깃든 행주산성 능선에서 조망한 한강의 장엄한 파노라마."
    },
    "07_gimpo_hangang_sunset.jpg": {
        "title": "김포 한강변의 황금빛 석양",
        "category": "파이튼 포토 컬렉션",
        "subtitle": "파이튼 오리지널 포토 · 김포 한강",
        "description": "강물 위로 부서지는 저녁놀의 온기를 고스란히 담아낸 서정 풍경화."
    },
    "08_aragapmun_reflection.jpg": {
        "title": "아라갑문에서의 회상(回想)",
        "category": "파이튼 포토 컬렉션",
        "subtitle": "파이튼 오리지널 포토 · 아라갑문",
        "description": "수필 《아라갑문에서》의 정서와 맞닿은 강변의 고요한 물빛과 사색."
    },
    "09_haengju_bridge_evening.jpg": {
        "title": "행주대교의 저녁 어스름",
        "category": "파이튼 포토 컬렉션",
        "subtitle": "파이튼 오리지널 포토 · 행주대교",
        "description": "하루를 마감하는 강변의 고요한 여명과 다리 불빛의 조화."
    },
    "10_gwangalli_sea.jpg": {
        "title": "부산 광안리 푸른 바다와 수평선",
        "category": "파이튼 포토 컬렉션",
        "subtitle": "파이튼 오리지널 포토 · 부산 광안리",
        "description": "시원하게 열린 남해 바다의 파도와 수평선이 주는 해방감."
    },
    "11_haeundae_dongbaek.jpg": {
        "title": "해운대 동백섬의 해안 비경",
        "category": "파이튼 포토 컬렉션",
        "subtitle": "파이튼 오리지널 포토 · 해운대 동백섬",
        "description": "동백섬 산책로 너머로 펼쳐지는 바다와 암석 해안의 웅장한 어울림."
    },
    "12_autumn_reeds_hangang.jpg": {
        "title": "방화대교 북단, 은빛 가을 갈대",
        "category": "파이튼 포토 컬렉션",
        "subtitle": "파이튼 오리지널 포토 · 한강 강변",
        "description": "가을 바람에 일렁이는 강변 갈대밭의 서정적인 빛과 그림자."
    }
}

POETRY_SALON = [
    {
        "id": "poem-dawn",
        "title": "병오의 통곡 속 여명",
        "volume": "제2권 《가을 그리고 차 한잔》 제5편",
        "genre": "서정시 · 영웅서사",
        "excerpt": "삭풍에 섞인 전란의 먼지 / 기울어진 처마 끝 강물로 흐르는 굶주린 곡소리...\n장미 가시 돋친 고독의 성소(聖所) / 어둠을 등불 삼아 건너는 비극의 심연\n서늘한 옷자락 끝에 닿는 신의 숨결 / 그것은 가눌 길 없는 사랑의 다른 이름.\n고통의 재를 털어낸 저 뜨거운 이마 위로 / 내일의 눈동자가 눈부시게 열린다.",
        "note": "비탄을 거름 삼아 솟구치는 생명력과 내일을 향한 여명의 빛을 노래한 파이튼 국왕 대표 명시."
    },
    {
        "id": "poem-dream",
        "title": "꿈 (Dream)",
        "volume": "제2권 《가을 그리고 차 한잔》 제2편",
        "genre": "단상시 · 희망",
        "excerpt": "우리는 기다린다.\n세상의 등불을, 세상의 밝음을\n인내하고 기도하며\n저 밝은 내일의 낙원을.",
        "note": "어둠 속에서도 꺼지지 않는 등불과 내일의 낙원을 향한 고요한 기도를 담은 단아한 서정시."
    },
    {
        "id": "poem-trajectory",
        "title": "이 아침의 詩: 환희의 궤적(軌跡)",
        "volume": "제2권 《가을 그리고 차 한잔》 제3편",
        "genre": "답시 · 철학시",
        "excerpt": "그대는 붓으로 고통을 짓이겨 그 속에 영원히 시들지 않는 꽃을 심었소.\n선지자의 거창한 예언이 아니라 그저 '오늘 하루의 달콤한 환희'를 바라는 그대의 마음이야말로,\n가장 인간적이기에 가장 신성(神聖)한 시인의 태도라 할 수 있겠소.\n현재에 깃든 영원의 순간을 노래하노라.",
        "note": "이백의 호방함과 릴케의 사랑이 교차하며 현재의 순간 속에 깃든 영원을 예찬한 작품."
    },
    {
        "id": "poem-forest",
        "title": "사색의 숲에서 길을 묻다 — 행복에 관하여",
        "volume": "제3권 《사색의 숲에서 길을 묻다》 제9편",
        "genre": "인문 수필 · 기행",
        "excerpt": "아침고요 수목원에서 청평사 계곡을 지나 설악 주전골의 가을 단풍까지,\n길고 긴 인생길(旅行) 위에서 우리가 마주하는 것은 결국 '지금 이 순간의 고요한 감사'이다.\n썰물이 지나간 자리에 남는 조개껍데기처럼, 세월의 물결이 씻어낸 자리에 진실한 삶이 빛난다.",
        "note": "대한민국의 산하와 호수를 거닐며 삶의 의미와 행복의 본질을 성찰한 제3권 대표 산문."
    }
]

HERITAGE_TIMELINE = [
    {
        "date": "2026.09",
        "title": "키아노스 건국 및 블루로즈 문화원 헌장 선포",
        "desc": "교육·문화부 산하 5대 핵심 기관 중 예술·문학·국가 상징 미학을 전담하는 블루로즈 문화원 설립."
    },
    {
        "date": "2026.10",
        "title": "Land of Blue Rose & 건국 공식 포스터 3종 아카이빙",
        "desc": "불가능을 기적으로 바꾼 파란 장미의 건국 서사(Land of Blue Rose.hwpx) 및 국·영문 공식 포스터 등재."
    },
    {
        "date": "2026.11.09",
        "title": "파이튼 문학 제1~3권 50편 통합 원고 컴파일",
        "desc": "《파이튼의 팝송 스토리텔링》(26편), 《가을 그리고 차 한잔》(6편), 《사색의 숲에서 길을 묻다》(18편) 총 50편 집대성."
    },
    {
        "date": "2026.11.24",
        "title": "블루로즈 3D 디지털 정원 1.0 개원",
        "desc": "무과금 순수 Three.js + Web Audio API 기반의 3D 파란 장미 성소 및 힐링 사운드 정원 최초 개관."
    },
    {
        "date": "2026.11.28",
        "title": "블루로즈 문화원 2.0 전면 개편 (Sanctuary 2.0)",
        "desc": "3D 조형 파크(시비·오벨리스크), 디지털 미술관(15점), 파이튼 시문학 살롱, 자동 동기화 카탈로그 통합 가동."
    }
]


def build_catalog() -> dict:
    gallery = []
    for folder, prefix in [
        (PHOTO_DIR, "assets/images/bluerose_photo"),
        (IMAGES_DIR, "assets/images"),
        (POSTERS_DIR, "assets/posters"),
    ]:
        if not folder.exists():
            continue
        for p in sorted(folder.iterdir()):
            if p.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            meta = ARTWORK_META.get(p.name, {
                "title": p.stem.replace("_", " ").title(),
                "category": "블루로즈 컬렉션",
                "subtitle": "Kyanos Cultural Archive",
                "description": "블루로즈 문화원 디지털 아카이브에 수록된 공식 시각 예술 작품입니다."
            })
            gallery.append({
                "filename": p.name,
                "src": f"{prefix}/{p.name}",
                "size_kb": round(p.stat().st_size / 1024, 1),
                **meta
            })

    catalog = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "institution": "블루로즈 문화원 (Blue Rose Cultural Arts Foundation)",
        "stats": {
            "gallery_count": len(gallery),
            "poetry_count": len(POETRY_SALON),
            "compiled_manuscripts": 50,
            "heritage_milestones": len(HERITAGE_TIMELINE)
        },
        "gallery": gallery,
        "poetry_salon": POETRY_SALON,
        "heritage_timeline": HERITAGE_TIMELINE
    }
    OUTPUT_JSON.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    return catalog


if __name__ == "__main__":
    result = build_catalog()
    print(f"[OK] bluerose_catalog.json synced: {result['stats']}")
