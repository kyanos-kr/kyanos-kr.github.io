import os
import sys
import json
import re

out_dir = r"d:\안티그래비티파이튼\키아노스_정부부처\04_교육_문화부\3대_블로그_네트워크\01_네이버_파이튼의_문학산책\삼국지_지혜색인보"
json_path = os.path.join(out_dir, "samgukji_raw_data.json")

with open(json_path, "r", encoding="utf-8") as f:
    items = json.load(f)

# 인물 키워드
person_keywords = {
    '조조': ['조조', '맹덕', '아만', '단가행'],
    '유비': ['유비', '현덕', '선주', '감 소저', '감부인'],
    '제갈공명': ['제갈공명', '제갈량', '공명', '제갈균', '와룡'],
    '최주평': ['최주평', '수경선생', '사마휘'],
    '사마의': ['사마의', '중달'],
    '관우': ['관우', '운장'],
    '장비': ['장비', '익덕'],
    '조자룡': ['조자룡', '조운'],
    '동탁': ['동탁'],
    '공융': ['공융'],
    '예형': ['예형'],
    '양수': ['양수'],
    '마량': ['마량', '백미', '마속'],
    '노숙': ['노숙', '자경'],
    '여백사': ['여백사'],
    '진궁': ['진궁'],
    '서서(선복)': ['선복', '서서'],
    '원소': ['원소', '元蘇'],
    '손견': ['손견', '孫堅', '손권'],
    '학소': ['학소']
}

# 주제 키워드
theme_keywords = {
    '권력과 정치': ['권력', '정치', '왕조', '혁명', '동탁', '치자', '승계', '황건적', '신정국가', '유언비어', '선동'],
    '군주의 도와 리더십': ['지도자', '치자', '리더십', '왕업', '대업', '겸양', '인내', '위엄', '덕', '관용', '절영지회', '대의', '단가행'],
    '난세의 처세와 인간관계': ['처세', '인간관계', '의리', '義理', '형세', '친구', '벗', '형제애', '영웅호색', '허물'],
    '고사와 지혜': ['계륵', '鷄肋', '백미', '白眉', '깨달음', '원호정책', '금주령', '절영지회', '아부', '阿父'],
    '역사관과 인생무상': ['허무주의', '멸망', '근본', '불변', '선비', '희생', '시', '냇물', '아침이슬', '두강주', '스러진 삶']
}

def clean_text(t):
    lines = t.split('\n')
    cleaned = []
    for line in lines:
        l = line.strip()
        l = re.sub(r'^[捤獥汤捯Bƀ*̀㇄ꭌуՀф€хɀҰҰϼπꘘч˰]+', '', l)
        l = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', l)
        l = re.sub(r'[䐀耄܀䔀䀄瀀뀀뀀ﰀ쀀᠀¦؀䈀耀爁ကĀ̀䌀䀄逎岬₸]+', '', l)
        if l:
            cleaned.append(l)
    return '\n\n'.join(cleaned)

processed_items = []
for idx, it in enumerate(items, 1):
    content = clean_text(it.get('content', ''))
    title = it.get('title', f'인용_{idx}')
    
    # 인물 추출
    matched_persons = it.get('persons', [])
    if not matched_persons:
        for p, kws in person_keywords.items():
            if any(kw in title or kw in content for kw in kws):
                matched_persons.append(p)
    if not matched_persons:
        matched_persons = ['기타 / 삼국지 군상']
        
    # 주제 추출
    matched_themes = it.get('themes', [])
    if not matched_themes:
        for th, kws in theme_keywords.items():
            if any(kw in title or kw in content for kw in kws):
                matched_themes.append(th)
    if not matched_themes:
        matched_themes = ['인문학 일반']
        
    core_quote = it.get('core_quote', '')
    if not core_quote:
        paragraphs = [p for p in content.split('\n\n') if len(p.strip()) > 15]
        core_quote = paragraphs[0] if paragraphs else content[:200]
        
    processed_items.append({
        'id': it.get('id', f'SAMGUK-{idx:03d}'),
        'title': title,
        'volume_no': it.get('volume_no', 99),
        'volume_title': it.get('volume_title', '기타 권차'),
        'volume_sub': it.get('volume_sub', ''),
        'category_folder': it.get('category_folder', ''),
        'persons': matched_persons,
        'themes': matched_themes,
        'core_quote': core_quote,
        'full_content': content,
        'source_file': it.get('filename', '')
    })

# 1. 마크다운 원문색인총람 생성 (평역 10권 순서 체계화)
md_lines = [
    '# 🏛️ 키아노스 국립 인류문명사연구원\n## 《파이튼 삼국지 지혜 원문색인총람 (Wisdom Index Vault)》\n',
    '> **총재 및 편찬자**: 파이튼 (漠杳 / Python)\n> **기획·색인 편찬**: 국무총리 앤트 (Ant)\n> **편찬 규격**: **이문열 평역 삼국지 10권 정규 순서 및 영구 지혜 보관소 체계**\n> **보존 원칙**: **원작 작가 평(이문열 평설) 및 역사 인용구의 무훼손 원문 그대로(Verbatim) 영구 보존**\n',
    '---\n',
    '## 📚 [1] 삼국지 평역 10권별 목차 및 수록 현황 (Volume Index)\n'
]

# 권별 그룹화 목차
vols_order = sorted(list(set(it['volume_no'] for it in processed_items)))
for v in vols_order:
    v_items = [it for it in processed_items if it['volume_no'] == v]
    v_title = v_items[0]['volume_title']
    md_lines.append(f'### 📖 {v_title} ({len(v_items)}편)')
    for it in v_items:
        sub_info = f" - *{it['volume_sub']}*" if it['volume_sub'] else ""
        md_lines.append(f"- **[{it['id']}]** [{it['title']}](#{it['id'].lower()}){sub_info} `{'` `'.join(it['themes'])}`")
    md_lines.append('')

md_lines.append('---\n\n## 📑 [2] 3차원 다면 색인 (Multi-faceted Index)\n')
md_lines.append('### 1. 주제별 색인 (By Theme)')
all_themes = sorted(list(set(th for item in processed_items for th in item['themes'])))
for th in all_themes:
    items_in_th = [it for it in processed_items if th in it['themes']]
    md_lines.append(f'- **{th}** ({len(items_in_th)}편): ' + ', '.join([f"[{it['title']}](#{it['id'].lower()})" for it in items_in_th]))

md_lines.append('\n### 2. 주요 인물별 색인 (By Person)')
all_persons = sorted(list(set(p for item in processed_items for p in item['persons'])))
for p in all_persons:
    items_in_p = [it for it in processed_items if p in it['persons']]
    md_lines.append(f'- **{p}** ({len(items_in_p)}편): ' + ', '.join([f"[{it['title']}](#{it['id'].lower()})" for it in items_in_p]))

md_lines.append(f'\n---\n\n## 📜 [3] 삼국지 지혜 원문 인용 카드 ({len(processed_items)}선 전재)\n')

for it in processed_items:
    md_lines.append(f"### <a id=\"{it['id'].lower()}\"></a>[{it['id']}] {it['title']}")
    md_lines.append(f"- **수록 권차**: **{it['volume_title']}** ({it['volume_sub']})")
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
      --accent-green: #3fb950;
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
      padding: 25px 40px;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }}
    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
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
      scrollbar-width: thin;
    }}
    .pill {{
      padding: 6px 14px;
      border-radius: 20px;
      border: 1px solid var(--border);
      background: #21262d;
      color: var(--text);
      font-size: 13px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s;
    }}
    .pill:hover {{
      border-color: var(--accent);
      color: var(--text-bright);
    }}
    .pill.active {{
      background: var(--accent);
      color: #000;
      font-weight: 600;
      border-color: var(--accent);
    }}
    .vol-nav {{
      display: flex;
      gap: 8px;
      padding: 12px 40px;
      background: #12161c;
      border-bottom: 1px solid var(--border);
      overflow-x: auto;
    }}
    .vol-pill {{
      padding: 5px 12px;
      border-radius: 6px;
      background: #1a202c;
      border: 1px solid #2d3748;
      color: #a0aec0;
      font-size: 12px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s;
    }}
    .vol-pill:hover, .vol-pill.active {{
      background: #2b6cb0;
      color: #fff;
      border-color: #4299e1;
    }}
    main {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 30px 40px;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
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
      transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
    }}
    .quote-card:hover {{
      transform: translateY(-3px);
      border-color: var(--accent);
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }}
    .card-meta {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .card-id {{
      font-family: monospace;
      font-size: 11px;
      color: var(--accent);
      background: rgba(210, 153, 34, 0.1);
      padding: 3px 8px;
      border-radius: 4px;
      border: 1px solid rgba(210, 153, 34, 0.3);
    }}
    .vol-badge {{
      font-size: 11px;
      font-weight: 600;
      color: #63b3ed;
      background: rgba(49, 130, 206, 0.15);
      padding: 3px 8px;
      border-radius: 4px;
      border: 1px solid rgba(49, 130, 206, 0.4);
    }}
    .card-tags {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}
    .tag {{
      font-size: 11px;
      padding: 2px 7px;
      border-radius: 4px;
      background: #21262d;
      color: var(--text-muted);
    }}
    .card-title {{
      font-family: 'Noto Serif KR', serif;
      font-size: 19px;
      font-weight: 700;
      color: var(--text-bright);
      margin-bottom: 14px;
      line-height: 1.4;
    }}
    .card-body {{
      font-size: 14px;
      line-height: 1.7;
      color: #adbac7;
      background: var(--quote-bg);
      border-left: 3px solid var(--accent);
      padding: 14px 16px;
      border-radius: 0 8px 8px 0;
      white-space: pre-wrap;
      max-height: 280px;
      overflow-y: auto;
      margin-bottom: 16px;
    }}
    .card-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 12px;
      border-top: 1px solid var(--border);
      font-size: 12px;
      color: var(--text-muted);
    }}
    .copy-btn {{
      background: #21262d;
      border: 1px solid var(--border);
      color: var(--text);
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
      transition: all 0.2s;
    }}
    .copy-btn:hover {{
      background: var(--accent);
      color: #000;
      border-color: var(--accent);
    }}
    .copy-btn.copied {{
      background: var(--accent-green);
      color: #fff;
      border-color: var(--accent-green);
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-top">
      <div class="header-title">
        <h1>🏛️ 키아노스 삼국지 지혜 인용실 (Wisdom Index Vault)</h1>
        <p>파이튼(Python) 총재 편찬 · 이문열 평역 삼국지 10권 순서 완전 보존 서고 (총 {len(processed_items)}선 완비)</p>
      </div>
      <div>
        <span class="badge">평역 10권 연동 보관소</span>
      </div>
    </div>
    <div class="search-bar">
      <input type="text" id="searchInput" class="search-input" placeholder="인물(조조, 유비, 관우...), 주제, 명구, 고사성어, 권차 검색...">
    </div>
    <div class="filter-pills">
      <button class="pill active" data-filter="all">전체보기 ({len(processed_items)})</button>
      <button class="pill" data-filter="조조">조조</button>
      <button class="pill" data-filter="유비">유비</button>
      <button class="pill" data-filter="관우">관우</button>
      <button class="pill" data-filter="제갈공명">제갈공명</button>
      <button class="pill" data-filter="조자룡">조자룡</button>
      <button class="pill" data-filter="권력과 정치">권력과 정치</button>
      <button class="pill" data-filter="군주의 도와 리더십">군주의 도와 리더십</button>
      <button class="pill" data-filter="난세의 처세와 인간관계">난세의 처세</button>
      <button class="pill" data-filter="고사와 지혜">고사와 지혜</button>
      <button class="pill" data-filter="역사관과 인생무상">역사관과 인생무상</button>
    </div>
  </header>

  <nav class="vol-nav">
    <button class="vol-pill active" data-vol="all">전체 권차</button>
    <button class="vol-pill" data-vol="제1권">1권 도원결의</button>
    <button class="vol-pill" data-vol="제2권">2권 구름처럼 일어나는 영웅들</button>
    <button class="vol-pill" data-vol="제3권">3권 영웅갈등</button>
    <button class="vol-pill" data-vol="제4권">4권 적벽대전</button>
    <button class="vol-pill" data-vol="제5권">5권 삼고초려</button>
    <button class="vol-pill" data-vol="제6권">6권 입촉기록</button>
    <button class="vol-pill" data-vol="제7권">7권 한중 쟁탈전</button>
    <button class="vol-pill" data-vol="제9권">9권 출사표</button>
    <button class="vol-pill" data-vol="특별부록">특별부록</button>
  </nav>

  <main id="cardContainer">
'''

for it in processed_items:
    persons_str = ' '.join(it['persons'])
    themes_str = ' '.join(it['themes'])
    escaped_content = it['full_content'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    json_safe_content = json.dumps(it['full_content'])
    
    html_template += f'''
    <div class="quote-card" data-vol="{it['volume_title']}" data-persons="{persons_str}" data-themes="{themes_str}" data-title="{it['title']}" data-content="{it['full_content'][:100]}">
      <div>
        <div class="card-meta">
          <span class="card-id">{it['id']}</span>
          <span class="vol-badge">{it['volume_title'].split('(')[0]}</span>
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
        <button class="copy-btn" onclick='copyToClipboard(this, {json_safe_content})'>본문 복사</button>
      </div>
    </div>
'''

html_template += '''
  </main>

  <script>
    const searchInput = document.getElementById('searchInput');
    const filterPills = document.querySelectorAll('.pill');
    const volPills = document.querySelectorAll('.vol-pill');
    const cards = document.querySelectorAll('.quote-card');

    let currentFilter = 'all';
    let currentVol = 'all';

    function filterCards() {
      const query = searchInput.value.toLowerCase().trim();

      cards.forEach(card => {
        const title = card.getAttribute('data-title').toLowerCase();
        const persons = card.getAttribute('data-persons').toLowerCase();
        const themes = card.getAttribute('data-themes').toLowerCase();
        const vol = card.getAttribute('data-vol').toLowerCase();
        const body = card.querySelector('.card-body').innerText.toLowerCase();

        const matchesQuery = !query || title.includes(query) || persons.includes(query) || themes.includes(query) || vol.includes(query) || body.includes(query);
        const matchesFilter = currentFilter === 'all' || persons.includes(currentFilter.toLowerCase()) || themes.includes(currentFilter.toLowerCase()) || title.includes(currentFilter.toLowerCase());
        const matchesVol = currentVol === 'all' || vol.includes(currentVol.toLowerCase());

        if (matchesQuery && matchesFilter && matchesVol) {
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

    volPills.forEach(pill => {
      pill.addEventListener('click', () => {
        volPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        currentVol = pill.getAttribute('data-vol');
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
