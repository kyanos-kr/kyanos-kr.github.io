#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파이튼 문학 출판 연계 시스템 (Phaeton Literary Publishing System Engine)
네이버 블로그 『파이튼의 문학산책』 RSS 원고를 수집하여
표준 출판 도서 규격(한컴 2024 윤고딕 740, 신국판/사륙판)으로 자동 조판·컴파일합니다.
"""

import os
import sys
import io
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape
from datetime import datetime

# Windows 콘솔 인코딩 대응
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "출판_원고_보관소")
PLAN_FILE = os.path.join(BASE_DIR, "series_plan.json")

def clean_html(raw_html):
    """HTML 태그 제거 및 텍스트 정제"""
    if not raw_html:
        return ""
    text = unescape(raw_html)
    # 이미지 태그 추출 및 마크다운 변환 또는 분리
    images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', text)
    # 태그 제거
    clean = re.sub(r'<[^>]+>', ' ', text)
    # 공백 정돈
    clean = re.sub(r'[ \t]+', ' ', clean)
    clean = re.sub(r'\n\s*\n+', '\n\n', clean).strip()
    return clean, images

def fetch_naver_posts():
    """네이버 RSS 피드에서 원고 파싱"""
    url = "https://rss.blog.naver.com/invision.xml"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req) as resp:
        content = resp.read()
    
    root = ET.fromstring(content)
    items = root.findall('.//item')
    
    posts = []
    for it in items:
        title = it.find('title').text if it.find('title') is not None else "무제"
        category = it.find('category').text if it.find('category') is not None else "미분류"
        link = it.find('link').text if it.find('link') is not None else ""
        pub_date = it.find('pubDate').text if it.find('pubDate') is not None else ""
        desc = it.find('description').text if it.find('description') is not None else ""
        
        # 카테고리 정규화 (NBSP 제거 등)
        category_clean = category.replace('\xa0', ' ').strip()
        body_text, images = clean_html(desc)
        
        posts.append({
            "title": title.strip(),
            "category": category_clean,
            "link": link.strip(),
            "pub_date": pub_date.strip(),
            "body": body_text,
            "images": images
        })
    return posts

def compile_book(series_info, matching_posts):
    """시리즈 도서 1권을 완성형 출판 원고로 조판"""
    vol = series_info["volume"]
    title = series_info["title"]
    subtitle = series_info["subtitle"]
    genre = series_info["genre"]
    desc = series_info["description"]
    
    # 1. Markdown 출판 원고 작성
    md_lines = []
    md_lines.append(f"# {title}")
    md_lines.append(f"### {subtitle}")
    md_lines.append(f"\n**저자**: 파이튼 (Python)  ")
    md_lines.append(f"**기획·발행**: 키아노스 교육·문화부 국립출판국 / 블루로즈 문화원  ")
    md_lines.append(f"**판형 규격**: 한컴오피스 2024 표준 (한컴 윤고딕 740, 11pt, 줄간격 160%, 신국판)  ")
    md_lines.append(f"**출판 등록 번호**: KYANOS-PUB-VOL{vol:02d}\n")
    md_lines.append("---\n")
    
    # 서문
    md_lines.append("## 🌿 저자의 말 (Preface)\n")
    md_lines.append(f"> \"삶의 굽이마다 스쳐 지나간 수많은 선율과 이야기, 그리고 영혼에 새겨진 사색의 흔적들을 한 권의 책으로 엮어 세상과 나눕니다.\"\n")
    md_lines.append(f"{desc}\n")
    md_lines.append("---\n")
    
    # 목차
    md_lines.append("## 📑 목차 (Table of Contents)\n")
    for idx, p in enumerate(matching_posts, start=1):
        md_lines.append(f"- **제{idx}편**: {p['title']}  *(원문 분류: {p['category']})*")
    md_lines.append("\n---\n")
    
    # 본문
    for idx, p in enumerate(matching_posts, start=1):
        md_lines.append(f"\n# 제{idx}편. {p['title']}\n")
        md_lines.append(f"*수록 출처: 네이버 블로그 『파이튼의 문학산책』 ({p['category']})*  \n")
        
        # 본문 문단
        paragraphs = p['body'].split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if para:
                md_lines.append(f"{para}\n")
        
        md_lines.append("\n---\n")
        
    # 판권지
    md_lines.append("## 🏛️ 판권지 (Colophon)\n")
    md_lines.append(f"- **도서명**: {title} — {subtitle}")
    md_lines.append(f"- **지은이**: 파이튼 (Python)")
    md_lines.append(f"- **발행일**: {datetime.now().strftime('%Y년 %m월 %d일')}")
    md_lines.append(f"- **발행처**: 키아노스 교육·문화부 블루로즈 문화원")
    md_lines.append(f"- **출판 표준**: 한컴 윤고딕 740 (11pt / 160%)")
    md_lines.append(f"- **원문 금고**: 네이버 블로그 『파이튼의 문학산책』 (https://blog.naver.com/invision)")
    
    md_content = "\n".join(md_lines)
    
    # 2. HTML e-Book 판형 생성
    html_content = generate_ebook_html(series_info, matching_posts)
    
    return md_content, html_content

def generate_ebook_html(series_info, matching_posts):
    """책장 넘김 스타일의 프리미엄 HTML 조판"""
    title = series_info["title"]
    subtitle = series_info["subtitle"]
    vol = series_info["volume"]
    
    toc_html = ""
    articles_html = ""
    for idx, p in enumerate(matching_posts, start=1):
        clean_title = p['title'].replace('"', '&quot;')
        toc_html += f'<li><a href="#chap_{idx}"><span>제{idx}편</span> {clean_title}</a></li>'
        
        # 본문 단락
        paras = p['body'].split('\n\n')
        paras_html = "".join([f'<p class="book-p">{unescape(para.strip())}</p>' for para in paras if para.strip()])
        
        articles_html += f'''
        <article id="chap_{idx}" class="book-chapter">
          <div class="chap-badge">CHAPTER {idx:02d} · {p["category"]}</div>
          <h2 class="chap-title">{clean_title}</h2>
          <div class="chap-meta">원문 수록: 네이버 블로그 『파이튼의 문학산책』 · {p["pub_date"]}</div>
          <div class="chap-body">
            {paras_html}
          </div>
        </article>
        '''

    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>{title} — {subtitle}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&family=Nanum+Myeongjo:wght@400;700;800&display=swap');
    :root {{
      --paper: #fcfbfa;
      --ink: #1c1c1e;
      --gold: #b38b40;
      --gold-dark: #8c6d23;
      --border: #e8e2d5;
      --font-body: '한컴 윤고딕 740', 'Nanum Myeongjo', serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #1a1721;
      color: var(--ink);
      font-family: var(--font-body);
      padding: 40px 20px;
      line-height: 1.6;
    }}
    .book-wrapper {{
      max-width: 820px;
      margin: 0 auto;
      background: var(--paper);
      box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(0,0,0,0.1);
      border-radius: 4px;
      padding: 70px 60px;
    }}
    .book-cover {{
      text-align: center;
      padding: 60px 20px;
      border-bottom: 2px solid var(--border);
      margin-bottom: 50px;
    }}
    .vol-tag {{
      display: inline-block;
      font-size: 0.85rem;
      letter-spacing: 0.2em;
      color: var(--gold-dark);
      font-weight: 700;
      margin-bottom: 1.5rem;
      text-transform: uppercase;
    }}
    .book-title {{
      font-size: 2.3rem;
      font-weight: 700;
      color: #111;
      margin-bottom: 0.8rem;
      letter-spacing: -0.02em;
    }}
    .book-subtitle {{
      font-size: 1.15rem;
      color: #555;
      font-style: italic;
      margin-bottom: 2rem;
    }}
    .book-author {{
      font-size: 1.05rem;
      color: #333;
      font-weight: 600;
    }}
    .book-publisher {{
      font-size: 0.85rem;
      color: #777;
      margin-top: 0.5rem;
    }}
    .book-toc {{
      background: #f7f5ef;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 30px;
      margin-bottom: 60px;
    }}
    .toc-title {{
      font-size: 1.2rem;
      color: var(--gold-dark);
      font-weight: 700;
      margin-bottom: 1rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.5rem;
    }}
    .book-toc ul {{ list-style: none; }}
    .book-toc li {{ margin-bottom: 0.6rem; font-size: 0.95rem; }}
    .book-toc a {{ text-decoration: none; color: #2c3e50; display: flex; justify-content: space-between; }}
    .book-toc a:hover {{ color: var(--gold-dark); text-decoration: underline; }}
    .book-chapter {{
      margin-bottom: 70px;
      padding-bottom: 50px;
      border-bottom: 1px dashed var(--border);
    }}
    .chap-badge {{
      font-size: 0.8rem;
      color: var(--gold-dark);
      font-weight: 700;
      letter-spacing: 0.1em;
      margin-bottom: 0.5rem;
    }}
    .chap-title {{
      font-size: 1.6rem;
      color: #111;
      margin-bottom: 0.6rem;
      font-weight: 700;
    }}
    .chap-meta {{
      font-size: 0.82rem;
      color: #888;
      margin-bottom: 2rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid #f0eee8;
    }}
    .book-p {{
      font-size: 11pt;
      line-height: 160%;
      color: #2b2b2b;
      margin-bottom: 1.4rem;
      text-indent: 1em;
      word-break: keep-all;
    }}
    .colophon {{
      background: #fdfcf9;
      border-top: 2px solid #333;
      padding: 30px 20px;
      margin-top: 60px;
      font-size: 0.85rem;
      color: #555;
      line-height: 1.8;
    }}
    @media print {{
      body {{ background: #fff; padding: 0; }}
      .book-wrapper {{ box-shadow: none; padding: 0; max-width: 100%; }}
      .book-chapter {{ page-break-after: always; }}
    }}
  </style>
</head>
<body>
  <div class="book-wrapper">
    <header class="book-cover">
      <span class="vol-tag">Volume {vol:02d} · Literary Collection</span>
      <h1 class="book-title">{title}</h1>
      <p class="book-subtitle">{subtitle}</p>
      <div class="book-author">파이튼 (Python) 著</div>
      <div class="book-publisher">키아노스 교육·문화부 블루로즈 문화원 출판국</div>
    </header>

    <section class="book-toc">
      <h2 class="toc-title">목차 (Table of Contents)</h2>
      <ul>{toc_html}</ul>
    </section>

    <main class="book-content">
      {articles_html}
    </main>

    <footer class="colophon">
      <h3 style="color:#111; margin-bottom:0.5rem;">판권 정보 (Colophon)</h3>
      <p><strong>도서명:</strong> {title} — {subtitle}</p>
      <p><strong>저자:</strong> 파이튼 (Python)</p>
      <p><strong>발행처:</strong> 키아노스 교육·문화부 블루로즈 문화원</p>
      <p><strong>서식 규격:</strong> 한컴 윤고딕 740, 본문 11pt, 줄간격 160% (출판 표준 규격)</p>
      <p><strong>출판 원본 금고:</strong> 네이버 블로그 『파이튼의 문학산책』 (https://blog.naver.com/invision)</p>
    </footer>
  </div>
</body>
</html>
'''
    return html

def main():
    print("=" * 60)
    print("🚀 [키아노스] 파이튼 문학 출판 연계 시스템 가동")
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. 출판 계획 로드
    if not os.path.exists(PLAN_FILE):
        print(f"❌ 설정 파일 누락: {PLAN_FILE}")
        return
        
    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        plan = json.load(f)
        
    # 2. 네이버 RSS 포스트 수집
    print("📡 네이버 블로그 『파이튼의 문학산책』 최신 원고 수집 중...")
    try:
        posts = fetch_naver_posts()
        print(f"✅ 총 {len(posts)}편의 원고를 수집 완료했습니다.")
    except Exception as e:
        print(f"❌ 네이버 원고 수집 실패: {e}")
        return
        
    # 3. 시리즈별 매칭 및 컴파일
    summary_report = []
    for series in plan["series"]:
        vol = series["volume"]
        title = series["title"]
        cats = series["categories"]
        
        # 카테고리 매칭
        matched = [p for p in posts if any(c in p["category"] for c in cats)]
        print(f"\n📖 [제{vol}권] 《{title}》 ➔ 수록 원고: {len(matched)}편")
        
        if not matched:
            print("   (해당 분류의 원고가 아직 없거나 카테고리 미매칭)")
            continue
            
        # 조판 컴파일
        md_text, html_text = compile_book(series, matched)
        
        # 파일 저장
        safe_title = re.sub(r'[\/\\:\*\?"<>\|]', '_', title)
        md_path = os.path.join(OUTPUT_DIR, f"제{vol:02d}권_{safe_title}_출판원고.md")
        html_path = os.path.join(OUTPUT_DIR, f"제{vol:02d}권_{safe_title}_조판미리보기.html")
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_text)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_text)
            
        print(f"   💾 출판 마크다운 저장: {os.path.basename(md_path)}")
        print(f"   🎨 e-Book 조판 미리보기 저장: {os.path.basename(html_path)}")
        
        summary_report.append({
            "volume": vol,
            "title": title,
            "count": len(matched),
            "md_file": os.path.basename(md_path),
            "html_file": os.path.basename(html_path)
        })
        
    # 결과 요약 JSON 저장
    result_path = os.path.join(BASE_DIR, "latest_publish_summary.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump({
            "compiled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_collected": len(posts),
            "books": summary_report
        }, f, ensure_ascii=False, indent=2)
        
    print("\n" + "=" * 60)
    print("✨ 파이튼 문학 출판 연계 조판 완료!")
    print(f"📁 출판 원고 저장소: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
