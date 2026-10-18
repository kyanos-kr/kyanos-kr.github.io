import os
import sys
import json
import re

json_path = r'd:\안티그래비티파이튼\키아노스_정부부처\04_교육_문화부\국립인류문명사연구원\삼국지_지혜색인보\samgukji_raw_data.json'
out_dir = r'd:\안티그래비티파이튼\키아노스_정부부처\04_교육_문화부\국립인류문명사연구원\삼국지_지혜색인보'

with open(json_path, 'r', encoding='utf-8') as f:
    items = json.load(f)

# 정제 함수
def clean_text(t):
    # 특수 이상 한자나 HWP 쓰레기 제거
    lines = t.split('\n')
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        # 제거할 HWP 헤더 잔여물 패턴
        l = re.sub(r'^[捤獥汤捯Bƀ*̀㇄ꭌуՀф€хɀҰҰϼπꘘч˰]+', '', l)
        l = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', l)
        # 이상한 제어 문자 시퀀스 제거
        l = re.sub(r'[䐀耄܀䔀䀄瀀뀀뀀ﰀ쀀᠀¦؀䈀耀爁ကĀ̀䌀䀄逎岬₸]+', '', l)
        if l:
            cleaned_lines.append(l)
    return '\n\n'.join(cleaned_lines)

# 인물 및 주제 태깅 규칙
person_keywords = {
    '조조': ['조조', '맹덕', '아만'],
    '유비': ['유비', '현덕', '선주'],
    '제갈공명': ['제갈공명', '제갈량', '공명', '제갈균', '와룡'],
    '최주평': ['최주평', '수경선생', '사마휘'],
    '사마의': ['사마의', '중달'],
    '관우': ['관우', '운장'],
    '장비': ['장비', '익덕'],
    '동탁': ['동탁'],
    '공융': ['공융'],
    '예형': ['예형'],
    '양수': ['양수'],
    '마량': ['마량', '백미', '마속'],
    '노숙': ['노숙', '자경'],
    '여백사': ['여백사'],
    '진궁': ['진궁'],
    '서서(선복)': ['선복', '서서']
}

theme_keywords = {
    '권력과 정치': ['권력', '정치', '왕조', '혁명', '동탁', '치자', '제거', '성취'],
    '군주의 도와 리더십': ['지도자', '치자', '리더십', '왕업', '대업', '겸양', '인내', '위엄', '덕'],
    '난세의 처세와 인간관계': ['처세', '인간관계', '의리', '義理', '형세', '친구', '벗'],
    '고사와 지혜': ['계륵', '鷄肋', '백미', '白眉', '깨달음', '원호정책', '금주령'],
    '역사관과 인생무상': ['허무주의', '멸망', '근본', '불변', '선비', '희생', '시']
}

processed_items = []
for idx, it in enumerate(items, 1):
    content = clean_text(it.get('content', ''))
    title = it.get('title', f'인용_{idx}')
    cat_folder = it.get('category_folder', '')
    
    # 인물 추출
    matched_persons = []
    for p, kws in person_keywords.items():
        if any(kw in title or kw in content for kw in kws):
            matched_persons.append(p)
    if not matched_persons:
        matched_persons = ['기타 / 삼국지 군상']
        
    # 주제 추출
    matched_themes = []
    for th, kws in theme_keywords.items():
        if any(kw in title or kw in content for kw in kws):
            matched_themes.append(th)
    if not matched_themes:
        matched_themes = ['인문학 일반']
        
    # 핵심 인용구(앞 2~3문장 또는 첫 단락)
    paragraphs = [p for p in content.split('\n\n') if len(p.strip()) > 15]
    core_quote = paragraphs[0] if paragraphs else content[:200]
    
    processed_items.append({
        'id': f'SAMGUK-{idx:03d}',
        'title': title,
        'category_folder': cat_folder,
        'persons': matched_persons,
        'themes': matched_themes,
        'core_quote': core_quote,
        'full_content': content,
        'source_file': it.get('filename', '')
    })

# 1. 마크다운 원문색인총람 생성
md_lines = [
    '# 🏛️ 키아노스 국립 인류문명사연구원\n## 《파이튼 삼국지 지혜 원문색인총람 (Wisdom Index Vault)》\n',
    '> **총재 및 편찬자**: 파이튼 (漠杳 / Python)\n> **기획·색인 편찬**: 국무총리 앤트 (Ant)\n> **보존 원칙**: **원작 작가 평(이문열 평설) 및 역사 인용구의 무훼손 원문 그대로(Verbatim) 영구 보존**\n',
    '---\n',
    '## 📑 [1] 3차원 다면 색인 (Multi-faceted Index)\n',
    '### 1. 주제별 색인 (By Theme)'
]

# 주제별 색인 표
all_themes = sorted(list(set(th for item in processed_items for th in item['themes'])))
for th in all_themes:
    items_in_th = [it for it in processed_items if th in it['themes']]
    md_lines.append(f'- **{th}** ({len(items_in_th)}편): ' + ', '.join([f"[{it['title']}](#{it['id'].lower()})" for it in items_in_th]))

md_lines.append('\n### 2. 주요 인물별 색인 (By Person)')
all_persons = sorted(list(set(p for item in processed_items for p in item['persons'])))
for p in all_persons:
    items_in_p = [it for it in processed_items if p in it['persons']]
    md_lines.append(f'- **{p}** ({len(items_in_p)}편): ' + ', '.join([f"[{it['title']}](#{it['id'].lower()})" for it in items_in_p]))

md_lines.append('\n---\n\n## 📜 [2] 삼국지 지혜 원문 인용 카드 (40선 전재)\n')

for it in processed_items:
    md_lines.append(f"### <a id=\"{it['id'].lower()}\"></a>[{it['id']}] {it['title']}")
    md_lines.append(f"- **분류 주제**: `{'` `'.join(it['themes'])}`")
    md_lines.append(f"- **관련 인물**: `{'` `'.join(it['persons'])}`")
    md_lines.append(f"- **원천 파일**: `{it['source_file']}` (원천 경로: `{it['category_folder']}`)")
    md_lines.append('\n#### 📌 핵심 인용 대목 (원문 발췌)')
    md_lines.append(f"> \"{it['core_quote']}\"\n")
    md_lines.append('#### 📖 원문 전문 (Verbatim)')
    md_lines.append('```text')
    md_lines.append(it['full_content'])
    md_lines.append('```\n')
    md_lines.append('---\n')

md_output_path = os.path.join(out_dir, '삼국지_인문학_원문색인총람.md')
with open(md_output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(md_lines))

print(f'Saved Markdown Index: {md_output_path}')

# 2. 고품격 Edge 웹 뷰어 HTML 생성
html_template = f'''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>키아노스 삼국지 지혜 인용실 (Wisdom Index Vault)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&family=Pretendard:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --accent: #d29922;
      --accent-blue: #58a6ff;
      --text: #c9d1d9;
      --text-muted: #8b949e;
      --text-bright: #f0f6fc;
      --quote-bg: #1f242c;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'Pretendard', sans-serif;
      line-height: 1.6;
      padding: 0;
    }}
    header {{
      background: linear-gradient(180deg, #1c2128 0%, #161b22 100%);
      border-bottom: 2px solid var(--accent);
      padding: 30px 40px;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }}
    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }}
    .header-title h1 {{
      font-family: 'Noto Serif KR', serif;
      color: #f3cf7a;
      font-size: 26px;
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .header-title p {{
      color: var(--text-muted);
      font-size: 14px;
      margin-top: 4px;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      background: rgba(210, 153, 34, 0.15);
      color: var(--accent);
      border: 1px solid var(--accent);
    }}
    .search-bar {{
      display: flex;
      gap: 15px;
      flex-wrap: wrap;
    }}
    .search-input {{
      flex: 1;
      min-width: 280px;
      padding: 12px 18px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: #0d1117;
      color: var(--text-bright);
      font-size: 15px;
      outline: none;
      transition: all 0.2s;
    }}
    .search-input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(210,153,34,0.25);
    }}
    .filter-pills {{
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-top: 10px;
    }}
    .pill {{
      padding: 6px 14px;
      border-radius: 16px;
      font-size: 13px;
      cursor: pointer;
      background: #21262d;
      border: 1px solid var(--border);
      color: var(--text);
      white-space: nowrap;
      transition: all 0.2s;
    }}
    .pill.active, .pill:hover {{
      background: var(--accent);
      color: #000;
      font-weight: 600;
      border-color: var(--accent);
    }}
    main {{
      max-width: 1400px;
      margin: 30px auto;
      padding: 0 30px;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(620px, 1fr));
      gap: 25px;
    }}
    .quote-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.2s, border-color 0.2s;
    }}
    .quote-card:hover {{
      border-color: var(--accent);
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }}
    .card-meta {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}
    .card-id {{
      font-size: 12px;
      font-weight: 700;
      color: var(--accent-blue);
      letter-spacing: 0.5px;
    }}
    .card-tags {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}
    .tag {{
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 10px;
      background: #21262d;
      color: var(--text-muted);
    }}
    .card-title {{
      font-family: 'Noto Serif KR', serif;
      font-size: 20px;
      font-weight: 700;
      color: var(--text-bright);
      margin-bottom: 12px;
    }}
    .card-body {{
      background: var(--quote-bg);
      border-left: 3px solid var(--accent);
      padding: 14px 18px;
      border-radius: 0 8px 8px 0;
      font-size: 14.5px;
      line-height: 1.75;
      color: #e6edf3;
      white-space: pre-wrap;
      max-height: 320px;
      overflow-y: auto;
      margin-bottom: 18px;
    }}
    .card-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid var(--border);
      padding-top: 14px;
      font-size: 12px;
      color: var(--text-muted);
    }}
    .copy-btn {{
      background: #238636;
      color: white;
      border: none;
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      font-size: 12px;
      transition: background 0.2s;
    }}
    .copy-btn:hover {{
      background: #2ea043;
    }}
    .copy-btn.copied {{
      background: #d29922;
      color: #000;
    }}
    @media (max-width: 768px) {{
      main {{ grid-template-columns: 1fr; padding: 0 15px; }}
      header {{ padding: 20px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-top">
      <div class="header-title">
        <h1>🏛️ 키아노스 삼국지 지혜 인용실</h1>
        <p>파이튼(漠杳) 인문학 지혜 서고 | 원문 무훼손 색인 40선 | Microsoft Edge 최적화</p>
      </div>
      <div>
        <span class="badge">소장 자료 {len(processed_items)}편 탑재</span>
      </div>
    </div>
    <div class="search-bar">
      <input type="text" id="searchInput" class="search-input" placeholder="인물(조조, 유비, 공명), 고사(계륵, 백미), 주제(권력, 처세, 리더십) 검색...">
    </div>
    <div class="filter-pills" id="filterPills">
      <div class="pill active" data-filter="all">전체 보기</div>
      <div class="pill" data-filter="조조">조조 (맹덕)</div>
      <div class="pill" data-filter="유비">유비 (현덕)</div>
      <div class="pill" data-filter="제갈공명">제갈공명</div>
      <div class="pill" data-filter="최주평">최주평</div>
      <div class="pill" data-filter="권력과 정치">권력과 정치</div>
      <div class="pill" data-filter="군주의 도와 리더십">리더십과 치자</div>
      <div class="pill" data-filter="난세의 처세와 인간관계">난세 처세</div>
      <div class="pill" data-filter="고사와 지혜">계륵·백미 고사</div>
    </div>
  </header>

  <main id="cardContainer">
'''

for it in processed_items:
    persons_str = ' '.join(it['persons'])
    themes_str = ' '.join(it['themes'])
    escaped_content = it['full_content'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    json_safe_content = json.dumps(it['full_content'])
    
    html_template += f'''
    <div class="quote-card" data-persons="{persons_str}" data-themes="{themes_str}" data-title="{it['title']}" data-content="{it['full_content'][:100]}">
      <div>
        <div class="card-meta">
          <span class="card-id">{it['id']}</span>
          <div class="card-tags">
            {' '.join([f'<span class="tag">{p}</span>' for p in it['persons']])}
            {' '.join([f'<span class="tag">{t}</span>' for t in it['themes']])}
          </div>
        </div>
        <h2 class="card-title">{it['title']}</h2>
        <div class="card-body">{escaped_content}</div>
      </div>
      <div class="card-footer">
        <span>출처: {it['source_file']}</span>
        <button class="copy-btn" onclick='copyToClipboard(this, {json_safe_content})'>원문 복사</button>
      </div>
    </div>
'''

html_template += '''
  </main>

  <script>
    const searchInput = document.getElementById('searchInput');
    const filterPills = document.querySelectorAll('.pill');
    const cards = document.querySelectorAll('.quote-card');

    let currentFilter = 'all';

    function filterCards() {
      const query = searchInput.value.toLowerCase().trim();

      cards.forEach(card => {
        const title = card.getAttribute('data-title').toLowerCase();
        const persons = card.getAttribute('data-persons').toLowerCase();
        const themes = card.getAttribute('data-themes').toLowerCase();
        const body = card.querySelector('.card-body').innerText.toLowerCase();

        const matchesQuery = !query || title.includes(query) || persons.includes(query) || themes.includes(query) || body.includes(query);
        const matchesFilter = currentFilter === 'all' || persons.includes(currentFilter.toLowerCase()) || themes.includes(currentFilter.toLowerCase()) || title.includes(currentFilter.toLowerCase());

        if (matchesQuery && matchesFilter) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    }

    searchInput.addEventListener('input', filterCards);

    filterPills.forEach(pill => {
      pill.addEventListener('click', () => {
        filterPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        currentFilter = pill.getAttribute('data-filter');
        filterCards();
      });
    });

    function copyToClipboard(btn, text) {
      navigator.clipboard.writeText(text).then(() => {
        const originalText = btn.innerText;
        btn.innerText = '복사 완료!';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.innerText = originalText;
          btn.classList.remove('copied');
        }, 1800);
      }).catch(err => {
        alert('복사 실패: ' + err);
      });
    }
  </script>
</body>
</html>
'''

html_output_path = os.path.join(out_dir, '삼국지_지혜인용실.html')
with open(html_output_path, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f'Saved HTML Viewer: {html_output_path}')

# 3. 인터넷 바로가기 (.url) 생성
url_content = f'''[InternetShortcut]
URL=file:///{html_output_path.replace(os.sep, '/')}
IconIndex=0
'''
url_path = os.path.join(out_dir, '키아노스_삼국지_지혜인용실.url')
with open(url_path, 'w', encoding='utf-8') as f:
    f.write(url_content)

print(f'Saved Edge Shortcut: {url_path}')
