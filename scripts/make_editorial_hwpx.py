# -*- coding: utf-8 -*-
"""
Generate Ant Editorial Columns in HWPX format.
Strictly following Python standard specs:
- Font: 한컴 윤고딕 740
- Sizes:
  - Main Headline: 11pt, bold, single line
  - Sub headlines: 11pt, bold
  - Subheads (소제목): 11pt, bold
  - Body: 11pt, normal, blank line between paragraphs
  - Byline: 9.5pt, normal, right-aligned
- Line spacing: 160%
- Destination: D:\DATA CENTER\편집 기사\오늘편집\파이튼컬럼\
"""

import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

def build_editorial_hwpx(output_hwpx_path, headline, sub1, sub2, byline_text, body_elements):
    template_hwpx_path = r'D:\DATA CENTER\편집 기사\오늘편집\손영일컬럼\국민들의 염장을 그만 질러라 206 .hwpx'
    temp_dir = r'D:\안티그래비티파이튼\temp_editorial_build'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(template_hwpx_path, 'r') as z:
        z.extractall(temp_dir)

    # 1. Update header.xml
    hdr_path = os.path.join(temp_dir, 'Contents', 'header.xml')
    tree_hdr = ET.parse(hdr_path)
    root_hdr = tree_hdr.getroot()

    ns_hh = 'http://www.hancom.co.kr/hwpml/2011/head'
    ns_hp = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
    ns_core = 'http://www.hancom.co.kr/hwpml/2011/core'
    ns_hs = 'http://www.hancom.co.kr/hwpml/2011/section'

    # Font: 한컴 윤고딕 740
    for ff in root_hdr.iter(f'{{{ns_hh}}}fontface'):
        for font in ff.iter(f'{{{ns_hh}}}font'):
            font.attrib['face'] = '한컴 윤고딕 740'

    refList = root_hdr.find(f'{{{ns_hh}}}refList')
    cpList = refList.find(f'{{{ns_hh}}}charProperties')
    ppList = refList.find(f'{{{ns_hh}}}paraProperties')

    c_base = cpList.findall(f'{{{ns_hh}}}charPr')[0]
    
    def get_or_create_cp(cid, height, bold=False):
        for c in cpList.findall(f'{{{ns_hh}}}charPr'):
            if c.attrib.get('id') == str(cid):
                c.attrib['height'] = str(height)
                c.attrib['textColor'] = '#000000'
                fontRef = c.find(f'{{{ns_hh}}}fontRef')
                if fontRef is not None:
                    for k in fontRef.attrib:
                        fontRef.attrib[k] = '0'
                b_elem = c.find(f'{{{ns_hh}}}bold')
                if bold and b_elem is None:
                    c.append(ET.Element(f'{{{ns_hh}}}bold'))
                elif not bold and b_elem is not None:
                    c.remove(b_elem)
                return c
        new_c = ET.fromstring(ET.tostring(c_base))
        new_c.attrib['id'] = str(cid)
        new_c.attrib['height'] = str(height)
        new_c.attrib['textColor'] = '#000000'
        fontRef = new_c.find(f'{{{ns_hh}}}fontRef')
        if fontRef is not None:
            for k in fontRef.attrib:
                fontRef.attrib[k] = '0'
        b_elem = new_c.find(f'{{{ns_hh}}}bold')
        if bold and b_elem is None:
            new_c.append(ET.Element(f'{{{ns_hh}}}bold'))
        elif not bold and b_elem is not None:
            new_c.remove(b_elem)
        cpList.append(new_c)
        return new_c

    get_or_create_cp(6, 1100, bold=False)  # 11pt normal (body)
    get_or_create_cp(16, 950, bold=False) # 9.5pt normal (byline)
    get_or_create_cp(17, 1100, bold=True) # 11pt bold (headline, sub, subhead)
    cpList.attrib['itemCnt'] = str(len(list(cpList)))

    # Ensure lineSpacing 160% on all paraPr
    for p in ppList.findall(f'{{{ns_hh}}}paraPr'):
        ls = p.find(f'{{{ns_hh}}}lineSpacing')
        if ls is not None:
            ls.attrib['type'] = 'PERCENT'
            ls.attrib['value'] = '160'
        else:
            new_ls = ET.Element(f'{{{ns_hh}}}lineSpacing', {'type': 'PERCENT', 'value': '160', 'unit': 'PERCENT'})
            p.append(new_ls)

    p20 = None
    for p in ppList.findall(f'{{{ns_hh}}}paraPr'):
        if p.attrib.get('id') == '20':
            p20 = p
            break
    if p20 is not None:
        align = p20.find(f'{{{ns_hh}}}align')
        if align is not None:
            align.attrib['horizontal'] = 'RIGHT'

    ET.register_namespace('hh', ns_hh)
    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hc', ns_core)
    tree_hdr.write(hdr_path, encoding='utf-8', xml_declaration=True)

    # 2. Update section0.xml
    sec_path = os.path.join(temp_dir, 'Contents', 'section0.xml')
    tree_sec = ET.parse(sec_path)
    root_sec = tree_sec.getroot()

    first_p = root_sec.find(f'{{{ns_hp}}}p')
    sec_pr = None
    ctrl = None
    if first_p is not None:
        run0 = first_p.find(f'{{{ns_hp}}}run')
        if run0 is not None:
            sec_pr = run0.find(f'{{{ns_hp}}}secPr')
            ctrl = run0.find(f'{{{ns_hp}}}ctrl')

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

    def make_run(charPrIDRef="6", text=None):
        r = ET.Element(f'{{{ns_hp}}}run', {'charPrIDRef': str(charPrIDRef)})
        if text is not None:
            t = ET.SubElement(r, f'{{{ns_hp}}}t')
            t.text = text
        return r

    # P0: Main Headline (charPr 17: 11pt, bold)
    p0 = make_p("0", "0")
    run_sec = ET.SubElement(p0, f'{{{ns_hp}}}run', {'charPrIDRef': '17'})
    if sec_pr is not None:
        run_sec.append(sec_pr)
    if ctrl is not None:
        run_sec.append(ctrl)
    run_sec.append(ET.Element(f'{{{ns_hp}}}t'))
    run_sec.find(f'{{{ns_hp}}}t').text = headline
    root_sec.append(p0)

    # Empty line
    p_sp1 = make_p("0", "0")
    p_sp1.append(make_run("6"))
    root_sec.append(p_sp1)

    # Sub 1 (charPr 17: 11pt, bold)
    p_sub1 = make_p("0", "0")
    p_sub1.append(make_run("17", sub1))
    root_sec.append(p_sub1)

    # Sub 2 (charPr 17: 11pt, bold)
    p_sub2 = make_p("0", "0")
    p_sub2.append(make_run("17", sub2))
    root_sec.append(p_sub2)

    # Empty line
    p_sp2 = make_p("0", "0")
    p_sp2.append(make_run("6"))
    root_sec.append(p_sp2)

    # Body elements
    preview_paras = []
    for elem_type, text in body_elements:
        if elem_type == 'subhead':
            p_subh = make_p("0", "0")
            p_subh.append(make_run("17", f"■ {text}"))
            root_sec.append(p_subh)

            p_sp = make_p("0", "0")
            p_sp.append(make_run("6"))
            root_sec.append(p_sp)
            preview_paras.append(f"■ {text}")
        elif elem_type == 'p':
            p_b = make_p("0", "0")
            p_b.append(make_run("6", text))
            root_sec.append(p_b)

            p_sp = make_p("0", "0")
            p_sp.append(make_run("6"))
            root_sec.append(p_sp)
            preview_paras.append(text)

    # Byline (paraPr 20: RIGHT, charPr 16: 9.5pt)
    p_by = make_p("20", "0")
    p_by.append(make_run("16", byline_text))
    root_sec.append(p_by)

    p_end = make_p("0", "0")
    p_end.append(make_run("6"))
    root_sec.append(p_end)

    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hs', ns_hs)
    ET.register_namespace('hc', ns_core)
    ET.register_namespace('hh', ns_hh)
    tree_sec.write(sec_path, encoding='utf-8', xml_declaration=True)

    # 3. Preview text
    prv_text_path = os.path.join(temp_dir, 'Preview', 'PrvText.txt')
    if os.path.exists(prv_text_path):
        preview_content = f"{headline}\n\n{sub1}\n{sub2}\n\n" + "\n\n".join(preview_paras) + f"\n\n{byline_text}\n"
        with open(prv_text_path, 'w', encoding='utf-8') as pf:
            pf.write(preview_content)

    # 4. Zip back
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
    print("Editorial HWPX successfully generated:", output_hwpx_path)

if __name__ == '__main__':
    print("Script loaded successfully.")
