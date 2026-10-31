# -*- coding: utf-8 -*-
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

base_dir = r"D:\DATA CENTER\편집 기사\오늘편집"
topic_folder = os.path.join(base_dir, "음바페 마오쩌둥 발언과 거대 대륙의 옹졸한 민낯")
cartoon_folder = os.path.join(base_dir, "만평")

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

# Concise editorial commentary reflecting the cartoon nature
paragraphs = [
    "프랑스 축구스타 음바페가 방송에서 던진 \"마오쩌둥은 독재자\"라는 가벼운 농담 한마디에 14억 거대 대륙이 집단 발작을 일으켰다. 관영 매체의 선동, 네티즌의 악플 테러, 기업들의 광고 중단과 경기 중계 보이콧까지, 일개 운동선수의 우스갯소리에 국가 전체가 동원되어 옹졸한 보복을 일삼는 꼴은 960만 ㎢ 대륙의 그릇이 고작 손바닥만 한 밴댕이 소갈딱지임을 스스로 자인할 뿐이다.",
    "수천만 무고한 인민을 죽음으로 몰아넣은 독재자를 사실대로 불렀다고 하여 '국민 감정 훼손'이라며 길길이 날뛰는 사회는 결코 위대한 문명국이 될 수 없다. 유머를 유머로 받지 못하고 진실에 자해적 보이콧으로 맞서는 전체주의의 '유리 심장'이야말로, 오늘날 세계가 마주한 거대 대륙의 가장 치졸하고 우스꽝스러운 민낯이다."
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

# Concise Body paragraphs
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

print("Successfully rebuilt concise cartoon editorial HWPX!")
