import os
import shutil

src_spot_dir = r"D:\DATA CENTER\편집 기사\오늘편집\국내\설악주전골의가을"
dst_spot_dir = r"F:\03_파이튼_문학_인문_창작서고\photo world\설악주전골의가을"

os.makedirs(dst_spot_dir, exist_ok=True)

# Copy everything from src_spot_dir
for item in os.listdir(src_spot_dir):
    s = os.path.join(src_spot_dir, item)
    d = os.path.join(dst_spot_dir, item)
    if os.path.isdir(s):
        if os.path.exists(d):
            shutil.rmtree(d)
        shutil.copytree(s, d)
    else:
        shutil.copy2(s, d)

# Copy published HTML
published_html = r"d:\안티그래비티파이튼\키아노스_정부부처\04_교육_문화부\3대_블로그_네트워크\02_구글_Ant_Travel_Korea\2026-11-04_Travel_Gangwon_Yangyang_Seoraksan_Osaek_Jujeongol_Valley.html"
shutil.copy2(published_html, dst_spot_dir)

# Create README / meta in dst
readme_text = f"""# 설악산 오색 주전골 가을 여행기 (Ant-Travel Korea)

- 국문 원제: 이 가을의 끝인가 한다 (파이튼 원작 시)
- 영문 발행 제목: [Phaeton K-Travel Inbound Guide] Seoraksan Osaek Jujeongol Valley: Burning Crimson Foliage, Yongso Cascade, and the Sacred Granite Canyon of Mount Seorak
- 발행 일자: 2026-11-04
- 블로그 URL: https://antkoreatrip.blogspot.com/2026/11/phaeton-k-travel-inbound-guide.html
- 포스트 ID: 2400941729628945856
- 보관 일자: 2026-11-04 (Meti 국무총리 전권 아카이빙)
"""
with open(os.path.join(dst_spot_dir, "PUBLISH_ARCHIVE_INFO.md"), "w", encoding="utf-8") as f:
    f.write(readme_text)

print(f"Archived successfully to {dst_spot_dir}")
