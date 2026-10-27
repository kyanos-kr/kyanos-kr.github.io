import os
import sys
import shutil
import zipfile
import xml.etree.ElementTree as ET

TEMPLATE_PATH = r'D:\DATA CENTER\RPT DB\보도 기사 정보\AI 에이전트 통제 불능 위험\AI 에이전트 통제 불능 위험.hwpx'

def create_standard_hwpx(output_hwpx_path, headline, sub1, sub2, byline, paragraphs):
    temp_dir = os.path.join(os.path.dirname(output_hwpx_path), '_temp_hwpx_build')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(TEMPLATE_PATH, 'r') as z:
        z.extractall(temp_dir)

    # 1. Update header.xml to guarantee font and styles
    hdr_path = os.path.join(temp_dir, 'Contents', 'header.xml')
    tree_hdr = ET.parse(hdr_path)
    root_hdr = tree_hdr.getroot()

    ns_hh = 'http://www.hancom.co.kr/hwpml/2011/head'
    ns_hp = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
    ns_core = 'http://www.hancom.co.kr/hwpml/2011/core'
    ns_hs = 'http://www.hancom.co.kr/hwpml/2011/section'

    # Font check: Ensure '한컴 윤고딕 740' is set
    for ff in root_hdr.iter(f'{{{ns_hh}}}fontface'):
        for font in ff.iter(f'{{{ns_hh}}}font'):
            font.attrib['face'] = '한컴 윤고딕 740'

    # Ensure lineSpacing is 160% on all paraPr (including nested switch/case/default)
    for p in root_hdr.iter(f'{{{ns_hh}}}paraPr'):
        found_ls = False
        for ls in p.iter(f'{{{ns_hh}}}lineSpacing'):
            ls.attrib['type'] = 'PERCENT'
            ls.attrib['value'] = '160'
            found_ls = True
        if not found_ls:
            new_ls = ET.Element(f'{{{ns_hh}}}lineSpacing', {'type': 'PERCENT', 'value': '160', 'unit': 'PERCENT'})
            p.append(new_ls)

    # Write header.xml
    ET.register_namespace('hh', ns_hh)
    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hc', ns_core)
    tree_hdr.write(hdr_path, encoding='utf-8', xml_declaration=True)

    # 2. Update section0.xml
    sec_path = os.path.join(temp_dir, 'Contents', 'section0.xml')
    tree_sec = ET.parse(sec_path)
    root_sec = tree_sec.getroot()

    # Preserve secPr and ctrl from original first paragraph
    first_p = root_sec.find(f'{{{ns_hp}}}p')
    sec_pr = None
    ctrl = None
    if first_p is not None:
        run0 = first_p.find(f'{{{ns_hp}}}run')
        if run0 is not None:
            sec_pr = run0.find(f'{{{ns_hp}}}secPr')
            ctrl = run0.find(f'{{{ns_hp}}}ctrl')

    # Clear root children
    for child in list(root_sec):
        root_sec.remove(child)

    p_id_counter = 1000000000

    def make_p(paraPrIDRef="0", styleIDRef="0"):
        nonlocal p_id_counter
        p = ET.Element(f'{{{ns_hp}}}p', {
            'id': str(p_id_counter),
            'paraPrIDRef': str(paraPrIDRef),
            'styleIDRef': str(styleIDRef),
            'pageBreak': '0',
            'columnBreak': '0',
            'merged': '0'
        })
        p_id_counter += 1
        return p

    def make_run(charPrIDRef="9", text=None):
        r = ET.Element(f'{{{ns_hp}}}run', {'charPrIDRef': str(charPrIDRef)})
        if text is not None:
            t = ET.SubElement(r, f'{{{ns_hp}}}t')
            t.text = text
        return r

    # P0: Main Headline (charPr 7: 11pt, bold)
    p0 = make_p("0", "0")
    run_sec = ET.SubElement(p0, f'{{{ns_hp}}}run', {'charPrIDRef': '7'})
    if sec_pr is not None:
        run_sec.append(sec_pr)
    if ctrl is not None:
        run_sec.append(ctrl)
    t0 = ET.SubElement(run_sec, f'{{{ns_hp}}}t')
    t0.text = headline
    root_sec.append(p0)

    # Blank line
    p_sp1 = make_p("0", "0")
    p_sp1.append(make_run("7"))
    root_sec.append(p_sp1)

    # Subheadline 1 (charPr 7: 11pt, bold)
    p_sub1 = make_p("0", "0")
    p_sub1.append(make_run("7", sub1))
    root_sec.append(p_sub1)

    # Subheadline 2 (charPr 7: 11pt, bold)
    p_sub2 = make_p("0", "0")
    p_sub2.append(make_run("7", sub2))
    root_sec.append(p_sub2)

    # Blank line
    p_sp2 = make_p("0", "0")
    p_sp2.append(make_run("9"))
    root_sec.append(p_sp2)

    # Body paragraphs (charPr 9: 11pt, normal)
    preview_paras = []
    for para_text in paragraphs:
        if not para_text.strip():
            continue
        p_body = make_p("0", "0")
        p_body.append(make_run("9", para_text.strip()))
        root_sec.append(p_body)

        # Blank line
        p_empty = make_p("0", "0")
        p_empty.append(make_run("9"))
        root_sec.append(p_empty)
        preview_paras.append(para_text.strip())

    # Byline (paraPr 20: right-aligned, charPr 8: 9.5pt)
    p_by = make_p("20", "0")
    p_by.append(make_run("8", byline))
    root_sec.append(p_by)

    # Final empty line
    p_end = make_p("0", "0")
    p_end.append(make_run("9"))
    root_sec.append(p_end)

    # Write section0.xml
    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hs', ns_hs)
    ET.register_namespace('hc', ns_core)
    ET.register_namespace('hh', ns_hh)
    tree_sec.write(sec_path, encoding='utf-8', xml_declaration=True)

    # Update PrvText.txt
    prv_text_path = os.path.join(temp_dir, 'Preview', 'PrvText.txt')
    if os.path.exists(prv_text_path):
        preview_content = f"{headline}\n\n{sub1}\n{sub2}\n\n" + "\n\n".join(preview_paras) + f"\n\n{byline}\n"
        with open(prv_text_path, 'w', encoding='utf-8') as pf:
            pf.write(preview_content)

    # Zip into target hwpx
    if os.path.exists(output_hwpx_path):
        os.remove(output_hwpx_path)

    with zipfile.ZipFile(output_hwpx_path, 'w') as zout:
        mimetype_path = os.path.join(temp_dir, 'mimetype')
        if os.path.exists(mimetype_path):
            zout.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)
        for root_dir, dirs, files in os.walk(temp_dir):
            for file in files:
                full_p = os.path.join(root_dir, file)
                rel_p = os.path.relpath(full_p, temp_dir)
                if rel_p == 'mimetype':
                    continue
                zout.write(full_p, rel_p, compress_type=zipfile.ZIP_DEFLATED)

    shutil.rmtree(temp_dir)
    print(f"Standard HWPX created: {output_hwpx_path}")
