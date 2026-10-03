# report_generator.py - AntNews 프리미엄 독자 인텔리전스 HTML 리포트 생성기
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [저작권 제로 & 키아노스 자체 미디어 표준]
# 1. 외부 언론 기사 링크 및 외부 매체명 인용 전면 배제 (저작권 분쟁 0%)
# 2. 키아노스 공식 부처 및 독자 기획 인텔리전스 배지 탑재
# 3. 100% 한글 오리지널 헤드라인 및 앤트(Ant) 독자 논평 시스템
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import html
from datetime import datetime
from typing import List, Dict

def generate_report(articles: List[Dict]) -> str:
    """
    키아노스 앤트뉴스 오리지널 인텔리전스 목록을 프리미엄 HTML 리포트로 렌더링
    :param articles: [{title, summary, analysis, insight, badge, category, source}, ...]
    :return: 생성된 주요 HTML 파일 경로
    """
    now = datetime.now()
    date_display = now.strftime("%Y년 %m월 %d일")
    date_file = now.strftime("%Y%m%d")

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
    os.makedirs(output_dir, exist_ok=True)

    article_cards = []
    for i, a in enumerate(articles, 1):
        badge = html.escape(a.get("badge", "KYANOS · INTEL"))
        title = html.escape(a.get("title", "키아노스 인텔리전스 브리핑"))
        summary = html.escape(a.get("summary", "")).replace("\n", "<br>")
        analysis = html.escape(a.get("analysis", "")).replace("\n", "<br>")
        insight = html.escape(a.get("insight", "")).replace("\n", "<br>")
        doc_type = html.escape(a.get("doc_type", "공식 인텔리전스"))

        card_html = f"""
        <article class="news-card">
            <div class="card-header">
                <span class="badge badge-kyanos">{badge}</span>
                <span class="news-index">SIGNAL #{i:02d}</span>
            </div>
            <h2 class="news-title">
                {title}
            </h2>
            <div class="news-summary">
                <div class="summary-label">🏛️ 키아노스 의제 및 팩트</div>
                <p>{summary}</p>
            </div>
            <div class="news-insight" style="background: rgba(0, 210, 255, 0.05); border-left: 3px solid #00d2ff; padding: 12px 16px; border-radius: 6px; margin-top: 14px;">
                <div class="insight-label" style="font-size: 0.82rem; font-weight: 700; color: #38bdf8; margin-bottom: 6px;">💡 앤트(Ant)의 전략 심층 분석</div>
                <p style="font-size: 0.93rem; color: #e2e8f0; line-height: 1.6;">{analysis}</p>
            </div>
            {f'''<div class="news-vision" style="background: rgba(212, 175, 55, 0.06); border-left: 3px solid #d4af37; padding: 12px 16px; border-radius: 6px; margin-top: 10px;">
                <div class="vision-label" style="font-size: 0.82rem; font-weight: 700; color: #fbbf24; margin-bottom: 6px;">🧭 키아노스 국가 거버넌스 &amp; 투자 시사점</div>
                <p style="font-size: 0.92rem; color: #fef08a; line-height: 1.6;">{insight}</p>
            </div>''' if insight else ''}
            <div class="card-footer" style="margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.76rem; color: #94a3b8;">👑 키아노스 국가 미디어 정식 발행물 · {doc_type}</span>
                <span style="font-size: 0.76rem; color: #00d2ff; font-weight: 600;">100% Original Intellectual Property</span>
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
            --bg-primary: #06152d;
            --bg-secondary: #0a1f44;
            --bg-card: #0c234b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #00d2ff;
            --accent-gold: #d4af37;
            --accent-gold-light: #f3e5ab;
            --border-color: rgba(212, 175, 55, 0.25);
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
            max-width: 880px;
            margin: 0 auto;
        }}
        header.main-header {{
            text-align: center;
            padding: 36px 24px 30px;
            background: linear-gradient(180deg, #0e2752 0%, #06152d 100%);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            margin-bottom: 28px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        .brand-sub {{
            font-size: 0.78rem;
            letter-spacing: 0.25em;
            color: var(--accent-gold);
            font-weight: 700;
            margin-bottom: 8px;
        }}
        .brand-title {{
            font-size: 2rem;
            font-weight: 900;
            letter-spacing: -0.02em;
            color: #ffffff;
            margin-bottom: 12px;
        }}
        .brand-title span {{
            color: var(--accent-blue);
        }}
        .brand-desc {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            max-width: 680px;
            margin: 0 auto 16px;
            line-height: 1.6;
        }}
        .copyright-banner {{
            display: inline-block;
            background: rgba(0, 210, 255, 0.08);
            border: 1px solid rgba(0, 210, 255, 0.3);
            border-radius: 20px;
            padding: 4px 16px;
            font-size: 0.78rem;
            color: var(--accent-blue);
            font-weight: 600;
            margin-bottom: 14px;
        }}
        .report-date {{
            display: inline-block;
            background: rgba(212, 175, 55, 0.15);
            border: 1px solid var(--accent-gold);
            color: var(--accent-gold-light);
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
        }}
        .news-grid {{
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-bottom: 40px;
        }}
        .news-card {{
            background: var(--bg-card);
            border: 1px solid rgba(0, 210, 255, 0.2);
            border-radius: 14px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        .news-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent-blue);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }}
        .badge-kyanos {{
            background: linear-gradient(135deg, rgba(0,210,255,0.2), rgba(212,175,55,0.2));
            color: var(--accent-blue);
            border: 1px solid rgba(0,210,255,0.4);
            font-size: 0.72rem;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 6px;
            letter-spacing: 0.08em;
        }}
        .news-index {{
            font-size: 0.78rem;
            color: var(--accent-gold);
            font-weight: 800;
            letter-spacing: 0.05em;
        }}
        .news-title {{
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 14px;
            line-height: 1.45;
            color: #ffffff;
        }}
        .summary-label {{
            font-size: 0.8rem;
            font-weight: 700;
            color: #cbd5e1;
            margin-bottom: 6px;
        }}
        .news-summary p {{
            font-size: 0.94rem;
            color: #cbd5e1;
            line-height: 1.65;
        }}
        footer.main-footer {{
            text-align: center;
            padding: 30px 20px;
            border-top: 1px solid var(--border-color);
            color: var(--text-secondary);
            font-size: 0.82rem;
            line-height: 1.8;
        }}
        footer.main-footer a {{
            color: var(--accent-blue);
            text-decoration: none;
            margin: 0 8px;
        }}
        footer.main-footer a:hover {{
            text-decoration: underline;
        }}
        .footer-law {{
            margin-top: 8px;
            font-size: 0.75rem;
            color: #64748b;
        }}
    </style>
</head>
<body>
    <div class="wrapper">
        <header class="main-header">
            <div class="brand-sub">THE SOVEREIGN REALM OF KYANOS OFFICIAL MEDIA</div>
            <h1 class="brand-title">AntNews <span>Intelligence</span></h1>
            <p class="brand-desc">
                국왕 파이튼 님의 통치 철학과 주권령 키아노스 국가 아젠다를 선도하는 공식 미디어 엔진입니다.<br>
                외부 언론 기사를 일절 복제·인용하지 않고, 키아노스 고유의 의제와 순수 공개 통계만을 바탕으로 앤트(Ant)가 독자 집필합니다.
            </p>
            <div class="copyright-banner">🛡️ 100% 독자 집필 오리지널 인텔리전스 (외부 저작권 침해 제로 원칙)</div><br>
            <div class="report-date">📅 {date_display} 공식 브리프 (총 {len(articles)}대 핵심 시그널 분석)</div>
        </header>

        <main class="news-grid">
            {cards_joined}
        </main>

        <footer class="main-footer">
            <p>© 2026 AntNews · The Sovereign Realm of Kyanos. All Rights Reserved.</p>
            <p>
                <a href="about.html">미디어 소개</a> · 
                <a href="privacy.html">개인정보처리방침</a> · 
                <a href="terms.html">이용약관</a> ·
                <a href="../../main.html">키아노스 정부 포털</a>
            </p>
            <p class="footer-law">본 리포트의 모든 분석과 시사점은 키아노스 주권령의 고유 지적 자산이며 외부 저작권을 철저히 준수·보호합니다.</p>
        </footer>
    </div>
</body>
</html>"""

    # 파일 저장 (1. index.html)
    index_file = os.path.join(output_dir, "index.html")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 파일 저장 (2. 날짜별 아카이브)
    dated_file = os.path.join(output_dir, f"antnews_{date_file}.html")
    with open(dated_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    return dated_file
