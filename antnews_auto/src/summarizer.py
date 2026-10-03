# summarizer.py - 앤트뉴스 오리지널 인텔리전스 및 키아노스 전략 논평 생성기
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [저작권 제로 & 독자 창작 방침]
# - 외부 언론 기사 인용, 전재, 번역 완전 배제 (침해 가능성 0%)
# - 키아노스 주권령 통치 철학(파이튼 국왕의 덕치 원칙) 및 전략 비전 기반
# - 앤트(Ant) AI의 100% 독자 집필 2차 창작 논평 및 비즈니스 시사점 도출
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import requests
import json
import time
import os
from typing import List, Dict

OLLAMA_API = os.environ.get("OLLAMA_API", "http://localhost:11434/api/generate")
MODEL      = "exaone3.5:2.4b"
TIMEOUT    = 35

# ──────────────────────────────────────────────────────────
# 1. Ollama AI 오리지널 전략 분석 프롬프트
# ──────────────────────────────────────────────────────────
_PROMPT_TEMPLATE = """
당신은 키아노스 주권령 공식 미디어 '앤트뉴스(AntNews)'의 전략 분석 총괄(앤트)입니다.
아래의 키아노스 국가 의제 및 시장 지표를 바탕으로, 국왕 파이튼 님의 통치 철학과 미래 산업 비전에 맞춘 독자적인 분석 논평을 작성하십시오.

의제 주제: {title}
기본 내용: {summary}
영역: {category}

규칙:
1. 외부 언론 기사체나 외신 인용 표현을 절대 쓰지 마십시오.
2. 키아노스 자체의 주권적 시각과 미래 국가 전략 관점에서 100% 새로운 한국어 문장으로 작성하십시오.
3. 응답은 반드시 아래 2개 항목으로만 답변하십시오:

앤트뉴스 분석: (키아노스 관점의 독자적 심층 논평 2~3문장)
시사점: (국가 거버넌스 및 투자·비즈니스 관점의 1문장 인사이트)
"""

def _fallback_analysis(item: Dict) -> Dict:
    """Ollama 오프라인 시 키아노스 고유의 표준 논평 적용 (외부 텍스트 인용 0%)"""
    category = item.get("category", "키아노스 인텔리전스")
    title = item.get("title", "")
    summary = item.get("summary", "")

    if "로봇" in title or "TALOS" in title:
        analysis = "피지컬 AI와 자율 로보틱스는 키아노스의 물리적 방어선과 첨단 무인 산업을 지탱하는 핵심 코어입니다. 과학·AGI부 중심의 기술 내재화를 통해 외부 의존 없는 완전 자립 생산 생태계를 완성해 나갑니다."
        insight = "하드웨어와 AI 코어가 일체화된 자주 생산 역량은 21세기 주권 국가의 가장 강력한 방패이자 성장 동력이 됩니다."
    elif "경제" in title or "EVERMORE" in title:
        analysis = "불확실한 글로벌 금융 질서 속에서 영구 불변의 헤리티지 가치를 지닌 희소 실물 자산의 중요성이 배가되고 있습니다. 키아노스 국부펀드와 연계된 프라이빗 경제망은 지속 가능한 가치 보존의 표본을 제시합니다."
        insight = "단순 소비재를 넘어 헤리티지 자산군을 조기에 선점하고 제도화하는 것이 장기적 자본 주권의 핵심입니다."
    elif "지표" in title or "공개 시장" in title:
        analysis = f"시장 실시간 데이터는 탈중앙 자산과 제도권 자본의 상호작용을 투명하게 드러냅니다. {summary} 변동성에 흔들리지 않는 장기적 가치 평가 체계 유지가 요구됩니다."
        insight = "단기 시세 등락에 매몰되지 않고 글로벌 유동성 축의 거시적 이동 경로를 추적하는 혜안이 필수적입니다."
    else:
        analysis = f"키아노스 통치 본부는 덕치 원칙과 기술 고도화의 균형을 바탕으로 미래 국가 시스템의 새로운 표준을 구축하고 있습니다. {summary}"
        insight = "인간 존엄과 고도화된 AI 거버넌스의 융합이야말로 차세대 주권 국가가 지향해야 할 본질입니다."

    item["analysis"] = analysis
    item["insight"]  = insight
    item["_fallback"] = True
    return item

def generate_original_commentary(item: Dict) -> Dict:
    """Ollama AI를 활용한 독자적 오리지널 논평 집필"""
    prompt = _PROMPT_TEMPLATE.format(
        title    = item.get("title", ""),
        summary  = item.get("summary", ""),
        category = item.get("category", "")
    )

    try:
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.35, "num_predict": 300},
        }
        res = requests.post(OLLAMA_API, json=payload, timeout=TIMEOUT)
        res.raise_for_status()
        text = res.json().get("response", "")

        analysis = ""
        insight = ""
        for line in text.splitlines():
            line_str = line.strip()
            if line_str.startswith("앤트뉴스 분석:"):
                analysis = line_str.replace("앤트뉴스 분석:", "").strip()
            elif line_str.startswith("시사점:"):
                insight = line_str.replace("시사점:", "").strip()

        item["analysis"] = analysis if analysis else text.strip()[:200]
        item["insight"]  = insight if insight else "키아노스 국가 철학 기반의 전략적 리더십이 요구되는 시점입니다."
        item["_fallback"] = False

    except Exception as e:
        print(f"  [Notice] Ollama AI 미응답({e}) → 키아노스 표준 인텔리전스 전환")
        return _fallback_analysis(item)

    return item

def summarize_articles(articles: List[Dict]) -> List[Dict]:
    """
    모든 편성 아이템을 100% 독자 작성 인텔리전스로 변환
    """
    results = []
    use_fallback = False
    total = len(articles)

    for i, item in enumerate(articles, 1):
        mode = "(표준)" if use_fallback else "(AI 논평)"
        print(f"  [{i}/{total}] {mode} 인텔리전스 집필: {item['title'][:45]}")
        if use_fallback:
            results.append(_fallback_analysis(item))
        else:
            s = generate_original_commentary(item)
            if s.get("_fallback"):
                use_fallback = True
            results.append(s)
            if not use_fallback:
                time.sleep(0.5)

    ai_cnt = sum(1 for r in results if not r.get("_fallback"))
    fb_cnt = total - ai_cnt
    print(f"  → 집필 완료: AI 오리지널 논평 {ai_cnt}건 / 표준 인텔리전스 {fb_cnt}건")
    return results

if __name__ == "__main__":
    test_item = [{
        "category": "과학·AGI부",
        "title": "과학·AGI부, 산하 자율로봇·드론 생산기술국(Project TALOS) 가동 본격화",
        "summary": "Project TALOS의 무인 생산 기지 구축이 착수되었습니다.",
        "badge": "GOV · TALOS"
    }]
    out = summarize_articles(test_item)
    print("분석:", out[0]["analysis"])
    print("시사점:", out[0]["insight"])
