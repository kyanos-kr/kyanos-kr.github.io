import re

# 1. main.html 정리
with open('main.html', 'r', encoding='utf-8') as f:
    main_content = f.read()

# 상단 헤더 메뉴의 '자립 재정' 항목 제거
main_content = re.sub(r'\s*<!-- 자립 재정 센터 -->\s*<li><a href="treasury_hub\.html"[^>]*>.*?자립 재정</a></li>', '', main_content)

# 모바일 드로어의 '자립 재정' 항목 제거
main_content = re.sub(r'\s*<li class="drawer-nav-item">\s*<a href="treasury_hub\.html"[^>]*>.*?자립 재정 허브.*?</a>\s*</li>', '', main_content, flags=re.DOTALL)

# 상단 CSS 제거 (kyanos_civic_treasury.css)
main_content = re.sub(r'\s*<link rel="stylesheet" href="assets/css/kyanos_civic_treasury\.css"[^>]*>', '', main_content)

# 하단 스크립트 제거 (kyanos_citizen_xp.js, kyanos_treasury.js)
main_content = re.sub(r'\s*<!-- 키아노스 국민 방문 경험치 & 자립 재정 스크립트 -->\s*<script src="assets/js/kyanos_citizen_xp\.js" defer></script>\s*<script src="assets/js/kyanos_treasury\.js" defer></script>', '', main_content)

with open('main.html', 'w', encoding='utf-8') as f:
    f.write(main_content)
print("main.html cleaned successfully")

# 2. index.html 정리
with open('index.html', 'r', encoding='utf-8') as f:
    index_content = f.read()

# Brand 5 카드를 '경제부 포털'로 교체 (자립재정은 경제부 내부 소관)
old_brand5 = re.compile(r'<!-- Brand 5: KYANOS SOVEREIGN TREASURY -->\s*<a href="treasury_hub\.html".*?</a>', re.DOTALL)
new_brand5 = '''<!-- Brand 5: MINISTRY OF ECONOMY -->
        <a href="gov_economy.html" target="_blank" rel="noopener noreferrer" class="brand-mini-card economy" title="키아노스 경제부 - 국가 자립 재정 & 글로벌 금융·자산 인텔리전스" aria-label="경제부 국가 재정 및 마켓 포털" style="border-color: rgba(255,224,102,0.5);">
          <div class="brand-logo-circle" style="background: radial-gradient(circle, #ffe066 0%, #06152d 70%);">
            <span style="font-size: 1.2rem;" aria-hidden="true">💰</span>
          </div>
          <div class="brand-info">
            <span class="brand-title" style="color: #ffe066;">경제부 포털</span>
            <span class="brand-tag" style="color: #fbeea4;">💎 국가 재정 & 자산 ↗</span>
          </div>
        </a>'''

index_content = old_brand5.sub(new_brand5, index_content)

# 상단 CSS 제거 (kyanos_civic_treasury.css)
index_content = re.sub(r'\s*<link rel="stylesheet" href="assets/css/kyanos_civic_treasury\.css"[^>]*>', '', index_content)

# 하단 스크립트 제거 (kyanos_citizen_xp.js, kyanos_treasury.js)
index_content = re.sub(r'\s*<!-- 키아노스 국민 방문 경험치 & 자립 재정 스크립트 -->\s*<script src="assets/js/kyanos_citizen_xp\.js" defer></script>\s*<script src="assets/js/kyanos_treasury\.js" defer></script>', '', index_content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_content)
print("index.html cleaned successfully")
