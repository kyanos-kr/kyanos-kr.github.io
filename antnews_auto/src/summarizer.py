# summarizer.py - 앤트뉴스 AI 분석·논평 생성 모듈
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 저작권 방침:
#   - 원문을 번역·요약하는 방식 → 폐기
#   - 공식 발표문 핵심 사실 추출 후 앤트뉴스 고유 시각으로
#     완전 재작성(Rewrite) → 독자적 2차 저작물로 보호
#   - "AI 분석", "앤트뉴스 논평" 레이블 명시 → 독자 혼동 방지
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import requests
import json
import time
import re
import os
from typing import List, Dict

OLLAMA_API   = os.environ.get("OLLAMA_API", "http://localhost:11434/api/generate")
MODEL        = "exaone3.5:2.4b"
TIMEOUT      = 45

# ──────────────────────────────────────────────────────────
# 경량 Fallback (Ollama 불가 시 자동 전환)
# ──────────────────────────────────────────────────────────
def _fallback_analysis(article: Dict) -> Dict:
    """Ollama 미응답 시 원문 핵심 사실만 추출한 경량 논평 생성."""
    raw   = article.get("summary", article.get("title", ""))
    clean = re.sub(r"<[^>]+>", "", raw).strip()[:200]
    article["korean_summary"] = (
        f"[앤트뉴스 자동 정리] {article.get('source','')} 공식 발표: "
        f"{clean}"
    )
    article["insight"]  = ""
    article["_fallback"] = True
    return article


# ──────────────────────────────────────────────────────────
# Ollama AI 논평 생성 (완전 재작성)
# ──────────────────────────────────────────────────────────
_PROMPT_TEMPLATE = """
당신은 앤트뉴스(AntNews) 소속 AI 분석 기자입니다.
아래 공식 발표문의 핵심 사실을 바탕으로, 앤트뉴스 고유의 시각과 언어로
완전히 새로운 한국어 논평을 작성하세요.

규칙:
1. 원문을 직접 번역하거나 복사하지 말 것.
2. 핵심 사실(수치, 날짜, 기관명)만 인용하고 나머지는 독자적 문장으로 재작성.
3. "앤트뉴스 분석:", "앤트뉴스 논평:" 형식으로 시작할 것.
4. 한국어 2~3문장 분석 + 1문장 시사점.
5. 출처: {source} | 라이선스: {license}

공식 발표 내용:
제목: {title}
내용: {summary}

응답 형식 (반드시 준수):
앤트뉴스 분석: (핵심 사실 기반 2~3문장 독자적 논평)
시사점: (투자·정책 관점 1문장)
"""

def summarize_article(article: Dict) -> Dict:
    prompt = _PROMPT_TEMPLATE.format(
        title   = article.get("title", ""),
        summary = article.get("summary", "")[:400],
        source  = article.get("source", ""),
        license = article.get("license", "공공저작물"),
    )
    try:
        payload  = {
            "model"  : MODEL,
            "prompt" : prompt,
            "stream" : False,
            "options": {"temperature": 0.4, "num_predict": 350},
        }
        res = requests.post(OLLAMA_API, json=payload, timeout=TIMEOUT)
        res.raise_for_status()
        text = res.json().get("response", "")

        analysis = ""
        insight  = ""
        for line in text.splitlines():
            if line.startswith("앤트뉴스 분석:"):
                analysis = line.replace("앤트뉴스 분석:", "").strip()
            elif line.startswith("시사점:"):
                insight  = line.replace("시사점:", "").strip()

        article["korean_summary"] = analysis or text[:250]
        article["insight"]        = insight
        article["_fallback"]      = False

    except (requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            Exception) as e:
        print(f"  [FALLBACK] Ollama 미응답 → 경량 전환 ({e})")
        return _fallback_analysis(article)

    return article


def summarize_articles(articles: List[Dict]) -> List[Dict]:
    results      = []
    use_fallback = False
    total        = len(articles)

    for i, article in enumerate(articles, 1):
        mode = "(경량)" if use_fallback else "(AI 논평)"
        print(f"  [{i}/{total}] {mode} 분석: {article['title'][:55]}")
        if use_fallback:
            results.append(_fallback_analysis(article))
        else:
            s = summarize_article(article)
            if s.get("_fallback"):
                use_fallback = True
            results.append(s)
            if not use_fallback:
                time.sleep(1)

    ai_cnt = sum(1 for r in results if not r.get("_fallback"))
    fb_cnt = total - ai_cnt
    print(f"  → 완료: AI 논평 {ai_cnt}건 / 경량 정리 {fb_cnt}건")
    return results


if __name__ == "__main__":
    sample = [{
        "title"  : "IMF Raises Global Growth Forecast for 2026",
        "summary": "The IMF revised upward its global GDP growth projection to 3.4% for 2026.",
        "source" : "IMF 공식",
        "license": "공공저작물",
    }]
    out = summarize_articles(sample)
    print(json.dumps(out, indent=2, ensure_ascii=False))
