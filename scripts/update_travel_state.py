import os

p = r"d:\안티그래비티파이튼\키아노스_정부부처\04_교육_문화부\3대_블로그_네트워크\02_구글_Ant_Travel_Korea\travel_upload_state.yaml"
with open(p, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    "last_uploaded_date: 2026-11-03",
    "last_uploaded_date: 2026-11-04"
)
text = text.replace(
    "last_uploaded_spot: 2026-11-03_Travel_Gangwon_Chuncheon_Obongsan_Cheongpyeongsa_Temple.html",
    "last_uploaded_spot: 2026-11-04_Travel_Gangwon_Yangyang_Seoraksan_Osaek_Jujeongol_Valley.html"
)

new_entry = """  - date: 2026-11-04
    spot: 2026-11-04_Travel_Gangwon_Yangyang_Seoraksan_Osaek_Jujeongol_Valley.html
    post_id: "2400941729628945856"
    url: "https://antkoreatrip.blogspot.com/2026/11/phaeton-k-travel-inbound-guide.html"
"""

if "2026-11-04_Travel_Gangwon_Yangyang_Seoraksan_Osaek_Jujeongol_Valley.html" not in text:
    text = text.strip() + "\n" + new_entry

with open(p, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS")
