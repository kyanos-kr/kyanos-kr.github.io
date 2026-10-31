# -*- coding: utf-8 -*-
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
from PIL import Image

# 1. Paths
base_dir = r"D:\DATA CENTER\편집 기사\오늘편집"
topic_folder = os.path.join(base_dir, "음바페 마오쩌둥 발언과 거대 대륙의 옹졸한 민낯")
os.makedirs(topic_folder, exist_ok=True)

cartoon_folder = os.path.join(base_dir, "만평")
os.makedirs(cartoon_folder, exist_ok=True)

raw_img_path = r"C:\Users\태봉\.gemini\antigravity\brain\801259a5-f015-4bb6-b052-4c3e132e88c0\mbappe_political_cartoon_1793282022925.jpg"
target_img_name = "음바페 마오쩌둥 발언과 거대 대륙의 옹졸한 민낯.jpg"
target_img_path = os.path.join(topic_folder, target_img_name)
target_img_cartoon = os.path.join(cartoon_folder, target_img_name)

# Resize to standard width 640px
with Image.open(raw_img_path) as im:
    w, h = im.size
    new_w = 640
    new_h = int(h * (new_w / w))
    im_resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
    im_resized.save(target_img_path, quality=95)
    im_resized.save(target_img_cartoon, quality=95)
    print(f"Saved resized image: {new_w}x{new_h} to {target_img_path}")

# High-res original backup in topic folder
shutil.copy2(raw_img_path, os.path.join(topic_folder, "음바페_시사만평_고해상도_원화.jpg"))

# 2. Generate HWPX
TEMPLATE_PATH = r"D:\DATA CENTER\RPT DB\보도 기사 정보\AI 에이전트 통제 불능 위험\AI 에이전트 통제 불능 위험.hwpx"
output_hwpx_path = os.path.join(topic_folder, "음바페 마오쩌둥 발언과 거대 대륙의 옹졸한 민낯.hwpx")
output_hwpx_cartoon = os.path.join(cartoon_folder, "음바페 마오쩌둥 발언과 거대 대륙의 옹졸한 민낯.hwpx")

temp_dir = os.path.join(topic_folder, "_temp_hwpx_build")
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir, exist_ok=True)

with zipfile.ZipFile(TEMPLATE_PATH, "r") as z:
    z.extractall(temp_dir)

# Update header.xml
hdr_path = os.path.join(temp_dir, "Contents", "header.xml")
tree_hdr = ET.parse(hdr_path)
root_hdr = tree_hdr.getroot()

ns_hh = "http://www.hancom.co.kr/hwpml/2011/head"
ns_hp = "http://www.hancom.co.kr/hwpml/2011/paragraph"
ns_core = "http://www.hancom.co.kr/hwpml/2011/core"
ns_hs = "http://www.hancom.co.kr/hwpml/2011/section"

for ff in root_hdr.iter(f"{{{ns_hh}}}fontface"):
    for font in ff.iter(f"{{{ns_hh}}}font"):
        font.attrib["face"] = "한컴 윤고딕 740"

for p in root_hdr.iter(f"{{{ns_hh}}}paraPr"):
    found_ls = False
    for ls in p.iter(f"{{{ns_hh}}}lineSpacing"):
        ls.attrib["type"] = "PERCENT"
        ls.attrib["value"] = "160"
        found_ls = True
    if not found_ls:
        new_ls = ET.Element(f"{{{ns_hh}}}lineSpacing", {"type": "PERCENT", "value": "160", "unit": "PERCENT"})
        p.append(new_ls)

ET.register_namespace("hh", ns_hh)
ET.register_namespace("hp", ns_hp)
ET.register_namespace("hc", ns_core)
tree_hdr.write(hdr_path, encoding="utf-8", xml_declaration=True)

# Update section0.xml
sec_path = os.path.join(temp_dir, "Contents", "section0.xml")
tree_sec = ET.parse(sec_path)
root_sec = tree_sec.getroot()

first_p = root_sec.find(f"{{{ns_hp}}}p")
sec_pr = None
ctrl = None
if first_p is not None:
    run0 = first_p.find(f"{{{ns_hp}}}run")
    if run0 is not None:
        sec_pr = run0.find(f"{{{ns_hp}}}secPr")
        ctrl = run0.find(f"{{{ns_hp}}}ctrl")

for child in list(root_sec):
    root_sec.remove(child)

p_id_counter = 1000000000

def make_p(paraPrIDRef="0", styleIDRef="0"):
    global p_id_counter
    p = ET.Element(f"{{{ns_hp}}}p", {
        "id": str(p_id_counter),
        "paraPrIDRef": str(paraPrIDRef),
        "styleIDRef": str(styleIDRef),
        "pageBreak": "0",
        "columnBreak": "0",
        "merged": "0"
    })
    p_id_counter += 1
    return p

def make_run(charPrIDRef="9", text=None):
    r = ET.Element(f"{{{ns_hp}}}run", {"charPrIDRef": str(charPrIDRef)})
    if text is not None:
        t = ET.SubElement(r, f"{{{ns_hp}}}t")
        t.text = text
    return r

headline = "음바페 농담 한마디에 발끈한 거대 대륙의 옹졸한 민낯"
sub1 = "마오쩌둥 독재자 평에 中 관영매체·기업 일제히 보복 발작"
sub2 = "14억 대국의 밴댕이 소갈딱지, 자해적 보이콧으로 국격 추락"
byline = "[2026.10.29 | 앤트뉴스 시사만평 = 파이튼 기자]"

paragraphs = [
    "프랑스가 낳은 세계적 축구 슈퍼스타 킬리안 음바페가 최근 현지 방송 인터뷰 도중 던진 가벼운 농담 한마디가 거대한 대륙의 신경을 곤두세웠다. 음바페는 방송에서 과거 역사적 인물을 언급하는 과정에서 마오쩌둥을 향해 특유의 여유로운 표정으로 \"그는 중국의 독재자였다\"는 취지의 우스갯소리를 건넸다. 서구 사회에서는 정치 지도자나 역사적 권력자에 대한 풍자와 해학이 지극히 자연스러운 표현의 자유이자 일상적인 담론의 일부에 불과하지만, 이 한마디는 베이징의 심장부를 강타하며 집단적인 히스테리를 촉발시켰다.",
    "중국 내 반응은 그야말로 이성을 상실한 발작에 가까웠다. 관영 매체들은 앞다투어 \"음바페가 14억 중국 인민의 민족적 자존심과 감정을 심각하게 훼손했다\"며 맹비난을 쏟아냈고, 관제 민족주의에 경도된 네티즌들은 음바페의 소셜미디어로 몰려가 저열한 악플 테러를 자행했다. 분노는 여기서 그치지 않았다. 음바페를 광고 모델로 기용했던 중국 기업들은 위약금을 감수하면서까지 광고 계약을 전격 중단하겠다고 선언했고, 관영 방송과 주요 동영상 플랫폼들은 음바페 소속팀의 경기 생중계 보이콧을 검토하겠다며 으름장을 놓았다. 한 축구선수의 가벼운 농담에 국가 기관과 거대 자본이 총동원되어 졸렬한 앙갚음에 나선 꼴이다.",
    "960만 제곱킬로미터에 달하는 광활한 영토와 14억의 인구, 세계 2위의 경제 대국(G2)을 자처하는 나라의 그릇이 고작 이 정도에 불과한가. 일개 스포츠 스타가 던진 촌철살인의 유머 한마디조차 품어내지 못하고 손바닥만 한 밴댕이 소갈딱지처럼 길길이 날뛰는 모습은 전 세계의 실소를 자아내기에 충분하다. 툭하면 타국의 정당한 비판이나 문화적 표현을 향해 '중국 인민의 감정'이라는 전가의 보도를 휘두르며 경제적 보복을 일삼는 행태는 대국의 품격이 아니라, 골목길에서 떼를 쓰는 미성숙한 불량배의 치졸한 행패와 다름없다.",
    "더욱 기괴한 것은 음바페가 언급한 마오쩌둥의 역사적 실체다. 대약진운동과 문화대혁명이라는 미증유의 광기로 수천만 무고한 인민을 아사(餓死)와 살육으로 몰아넣은 독재자를 '독재자'라 부른 것이 도대체 무슨 죄란 말인가. 역사적 사실을 사실대로 말했을 뿐인데도, 이를 성역화된 우상에 대한 신성모독으로 몰아붙여 세계인의 입을 틀어막으려는 태도는 중국 사회가 여전히 21세기 문명 세계와는 아득히 동떨어진 1인 지배 전체주의의 미망(迷妄) 속에 갇혀 있음을 스스로 자인하는 꼴이다.",
    "자유로운 비판과 유머를 용인하지 못하고, 진실에 대해 집단적 린치와 자해적 보이콧으로 응수하는 사회는 결코 위대한 문명 국가가 될 수 없다. 광고를 끊고 중계를 차단한다고 해서 음바페의 발끝에서 터져 나오는 골 폭풍이 멈추지 않으며, 전 세계인이 공유하는 보편적 상식과 진실이 지워지지도 않는다. 스스로 거대하다고 자부하는 대륙이 실상은 작은 바늘 끝 하나에도 찔려 비명을 지르는 '유리 심장'의 왜소한 집단임을 드러낸 이번 만평 사태는, 전체주의 독재의 껍데기가 얼마나 취약하고 옹졸한지 전 세계에 똑똑히 각인시키고 있다."
]

# P0: Main Headline (charPr 7: 11pt bold)
p0 = make_p("0", "0")
run_sec = ET.SubElement(p0, f"{{{ns_hp}}}run", {"charPrIDRef": "7"})
if sec_pr is not None:
    run_sec.append(sec_pr)
if ctrl is not None:
    run_sec.append(ctrl)
t0 = ET.SubElement(run_sec, f"{{{ns_hp}}}t")
t0.text = headline
root_sec.append(p0)

# Blank line
p_sp1 = make_p("0", "0")
p_sp1.append(make_run("7"))
root_sec.append(p_sp1)

# Subheadline 1 (charPr 7: 11pt bold)
p_sub1 = make_p("0", "0")
p_sub1.append(make_run("7", sub1))
root_sec.append(p_sub1)

# Subheadline 2 (charPr 7: 11pt bold)
p_sub2 = make_p("0", "0")
p_sub2.append(make_run("7", sub2))
root_sec.append(p_sub2)

# Blank line
p_sp2 = make_p("0", "0")
p_sp2.append(make_run("9"))
root_sec.append(p_sp2)

# Body paragraphs
for para_text in paragraphs:
    p_body = make_p("0", "0")
    p_body.append(make_run("9", para_text.strip()))
    root_sec.append(p_body)

    p_empty = make_p("0", "0")
    p_empty.append(make_run("9"))
    root_sec.append(p_empty)

# Byline (paraPr 20: right-aligned, charPr 8: 9.5pt)
p_by = make_p("20", "0")
p_by.append(make_run("8", byline))
root_sec.append(p_by)

# Final blank
p_end = make_p("0", "0")
p_end.append(make_run("9"))
root_sec.append(p_end)

ET.register_namespace("hp", ns_hp)
ET.register_namespace("hs", ns_hs)
ET.register_namespace("hc", ns_core)
tree_sec.write(sec_path, encoding="utf-8", xml_declaration=True)

# Package into HWPX
if os.path.exists(output_hwpx_path):
    os.remove(output_hwpx_path)

with zipfile.ZipFile(output_hwpx_path, "w", zipfile.ZIP_DEFLATED) as z_out:
    for root, dirs, files in os.walk(temp_dir):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, temp_dir)
            z_out.write(full, rel)

shutil.rmtree(temp_dir)
shutil.copy2(output_hwpx_path, output_hwpx_cartoon)

print(f"Successfully created HWPX: {output_hwpx_path}")
print(f"Also mirrored to: {output_hwpx_cartoon}")
