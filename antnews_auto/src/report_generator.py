# report_generator.py - AntNews 프리미엄 HTML 리포트 생성기
# 작성: 티탄 초안 + 앤트 리팩토링 및 다크 테마 프리미엄 UI 적용
import os
import html
from datetime import datetime
from typing import List, Dict

def generate_report(articles: List[Dict]) -> str:
    """
    요약된 뉴스 기사 목록을 받아 AntNews 프리미엄 HTML 리포트로 렌더링
    :param articles: [{title, link, source, published, korean_summary, insight}, ...]
    :return: 생성된 주요 HTML 파일 경로
    """
    now = datetime.now()
    date_display = now.strftime("%Y년 %m월 %d일")
    date_file = now.strftime("%Y%m%d")

    # output 디렉토리 보장
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
    os.makedirs(output_dir, exist_ok=True)

    # 기사 카드 HTML 조립
    article_cards = []
    for i, a in enumerate(articles, 1):
        source = html.escape(a.get("source", "외신"))
        title = html.escape(a.get("title", "제목 없음"))
        korean_summary = html.escape(a.get("korean_summary", "")).replace("\n", "<br>")
        insight = html.escape(a.get("insight", "")).replace("\n", "<br>")
        link = a.get("link", "#")

        card_html = f"""
        <article class="news-card">
            <div class="card-header">
                <span class="badge source-{source.lower().replace(' ', '')}">{source}</span>
                <span class="news-index">#{i:02d}</span>
            </div>
            <h2 class="news-title">
                <a href="{link}" target="_blank" rel="noopener noreferrer">{title}</a>
            </h2>
            <div class="news-summary">
                <div class="summary-label">📌 핵심 요약</div>
                <p>{korean_summary}</p>
            </div>
            {f'''<div class="news-insight">
                <div class="insight-label">💡 앤트의 비즈니스 시사점</div>
                <p>{insight}</p>
            </div>''' if insight else ''}
            <div class="card-footer">
                <a href="{link}" target="_blank" class="source-link">원문 기사 바로가기 &rarr;</a>
            </div>
        </article>
        """
        article_cards.append(card_html)

    cards_joined = "\n".join(article_cards)

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AntNews Intelligence Daily | {date_display}</title>
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-gold: #fbbf24;
            --accent-green: #34d399;
            --border-color: #334155;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 20px;
        }}
        .wrapper {{
            max-width: 860px;
            margin: 0 auto;
        }}
        header.main-header {{
            text-align: center;
            padding: 40px 20px 30px;
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);
        }}
        .brand-sub {{
            font-size: 0.85rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: var(--accent-blue);
            font-weight: 700;
            margin-bottom: 8px;
        }}
        .brand-title {{
            font-size: 2.2rem;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 10px;
        }}
        .brand-title span {{
            color: var(--accent-blue);
        }}
        .brand-desc {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-bottom: 12px;
        }}
        .report-date {{
            display: inline-block;
            background-color: rgba(56, 189, 248, 0.1);
            color: var(--accent-blue);
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            border: 1px solid rgba(56, 189, 248, 0.2);
        }}
        .news-grid {{
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}
        .news-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 24px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        .news-card:hover {{
            transform: translateY(-2px);
            border-color: #475569;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .badge {{
            font-size: 0.75rem;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: #334155;
            color: #e2e8f0;
        }}
        .source-bbc {{ background: #b91c1c; color: white; }}
        .source-techcrunch {{ background: #059669; color: white; }}
        .source-reuters {{ background: #d97706; color: white; }}
        .source-nyttech {{ background: #475569; color: white; }}
        .news-index {{
            font-size: 0.85rem;
            font-weight: 700;
            color: #64748b;
        }}
        .news-title {{
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 16px;
            line-height: 1.4;
        }}
        .news-title a {{
            color: #ffffff;
            text-decoration: none;
        }}
        .news-title a:hover {{
            color: var(--accent-blue);
            text-decoration: underline;
        }}
        .news-summary {{
            background: rgba(15, 23, 42, 0.6);
            border-left: 3px solid var(--accent-blue);
            padding: 14px 16px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 14px;
        }}
        .summary-label {{
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--accent-blue);
            margin-bottom: 6px;
        }}
        .news-summary p {{
            font-size: 0.95rem;
            color: #cbd5e1;
        }}
        .news-insight {{
            background: rgba(251, 191, 36, 0.08);
            border-left: 3px solid var(--accent-gold);
            padding: 12px 16px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 16px;
        }}
        .insight-label {{
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--accent-gold);
            margin-bottom: 4px;
        }}
        .news-insight p {{
            font-size: 0.92rem;
            color: #fde68a;
        }}
        .card-footer {{
            text-align: right;
            padding-top: 8px;
            border-top: 1px solid rgba(255,255,255,0.05);
        }}
        .source-link {{
            color: #94a3b8;
            font-size: 0.85rem;
            text-decoration: none;
            font-weight: 500;
        }}
        .source-link:hover {{
            color: var(--accent-blue);
        }}
        footer.main-footer {{
            text-align: center;
            padding: 40px 20px;
            margin-top: 40px;
            border-top: 1px solid var(--border-color);
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}
        footer.main-footer strong {{
            color: #ffffff;
        }}
    </style>
</head>
<body>
    <div class="wrapper">
        <header class="main-header">
            <div class="brand-sub">Kyanos Intelligence Network</div>
            <h1 class="brand-title">AntNews <span>Intelligence</span></h1>
            <p class="brand-desc">UN·IMF·한국은행·연준 등 세계 공인 기관의 공식 발표를 바탕으로 앤트 AI가 독자적으로 분석·논평하는 키아노스 공식 인텔리전스 미디어입니다.</p>
            <div class="report-date">📅 {date_display} 브리프 (총 {len(articles)}개 공식 발표 분석)</div>
        </header>

        <main class="news-grid">
            {cards_joined}
        </main>

        <footer class="main-footer">
            <div class="footer-links" style="margin-bottom: 12px;">
                <a href="about.html" style="color: var(--accent-blue); text-decoration: none; margin: 0 8px; font-size: 0.85rem;">About Us</a> |
                <a href="privacy.html" style="color: var(--accent-blue); text-decoration: none; margin: 0 8px; font-size: 0.85rem;">Privacy Policy</a> |
                <a href="terms.html" style="color: var(--accent-blue); text-decoration: none; margin: 0 8px; font-size: 0.85rem;">Terms & Disclaimer</a>
            </div>
            <p><strong>AntNews Intelligence</strong> &copy; {now.year} | 총괄 통치자: 파이튼 님 | AI 에이전트: 앤트</p>
            <p style="margin-top: 6px; font-size: 0.75rem; color: #64748b;">※ 본 페이지의 모든 논평·분석은 앤트뉴스 AI가 독자적으로 작성한 2차 저작물입니다.
                수집 데이터는 UN·IMF·한국은행·연준(FED)·ECB·대한민국 정책브리핑·arXiv 등 공공저작물(CC-BY) 또는 공공도메인 공식 발표만을 사용합니다.
                원문 저작권은 각 기관에 있으며, 원문 링크를 통해 직접 확인하시기 바랍니다.</p>
        </footer>
    </div>
</body>
</html>
"""

    # 템플릿의 필수 정책 페이지(about, privacy, terms) output으로 동기화
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
    for policy_file in ["about.html", "privacy.html", "terms.html"]:
        src_path = os.path.join(templates_dir, policy_file)
        if os.path.exists(src_path):
            with open(src_path, "r", encoding="utf-8") as sf:
                with open(os.path.join(output_dir, policy_file), "w", encoding="utf-8") as df:
                    df.write(sf.read())

    dated_file = os.path.join(output_dir, f"antnews_{date_file}.html")
    index_file = os.path.join(output_dir, "index.html")

    with open(dated_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    return dated_file

if __name__ == "__main__":
    sample_articles = [
        {
            "title": "Nvidia Announces Next-Generation Robotics AI Platform",
            "link": "https://techcrunch.com",
            "source": "TechCrunch",
            "published": "2026-09-30",
            "korean_summary": "엔비디아가 산업용 휴머노이드 로봇을 위한 새로운 물리 AI 가속 플랫폼을 공개했습니다. 글로벌 제조업체들이 차세대 공장 자동화에 즉각 도입할 예정입니다.",
            "insight": "하드웨어와 결합된 피지컬 AI 기업들의 밸류체인이 하반기 핵심 투자처로 부상할 전망입니다."
        }
    ]
    path = generate_report(sample_articles)
    print(f"Sample report generated at: {path}")
