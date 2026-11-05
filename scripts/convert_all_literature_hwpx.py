# -*- coding: utf-8 -*-
import os, sys, re, shutil, zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = r'D:\안티그래비티파이튼\키아노스_정부부처\04_교육_문화부\국립인류문명사연구원\01_동양철학_법가_한비자\한비자_법술세_제왕학과_키아노스_덕치.hwpx'
ROOT_DIR = r'F:\03_파이튼_문학_인문_창작서고'

def clean_md_inline(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = text.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def parse_md_to_hwpx_elements(md_path):
    with open(md_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    lines = content.splitlines()
    elements = []
    
    in_table = False
    table_headers = []
    
    for line in lines:
        raw = line.strip()
        if not raw:
            continue
        
        if raw in ['---', '***', '___']:
            continue
            
        if raw.startswith('|') and raw.endswith('|'):
            cells = [clean_md_inline(c) for c in raw.split('|')[1:-1]]
            if all(set(c).issubset({'-', ':', ' '}) for c in cells if c):
                continue
            if not in_table:
                in_table = True
                table_headers = cells
                continue
            else:
                row_parts = []
                for i, c in enumerate(cells):
                    if not c:
                        continue
                    header = table_headers[i] if i < len(table_headers) else f'항목{i+1}'
                    row_parts.append(f'[{header}] {c}')
                elements.append(('p', ' · '.join(row_parts)))
                continue
        else:
            in_table = False
            table_headers = []

        if raw.startswith('# '):
            text = clean_md_inline(raw[2:])
            elements.append(('headline', text))
        elif raw.startswith('## '):
            text = clean_md_inline(raw[3:])
            elements.append(('sub', text))
        elif raw.startswith('### '):
            text = clean_md_inline(raw[4:])
            elements.append(('sub', text))
        elif raw.startswith('#### '):
            text = clean_md_inline(raw[5:])
            elements.append(('sub', text))
        elif raw.startswith('> '):
            text = clean_md_inline(raw[2:])
            if any(k in text for k in ['집필', '원작', '분류', '등록', '일자', '키아노스']):
                elements.append(('byline', text))
            else:
                elements.append(('p', text))
        else:
            if raw.startswith('- ') or raw.startswith('* '):
                raw = '• ' + raw[2:]
            elif re.match(r'^\d+\.\s+', raw):
                raw = re.sub(r'^(\d+\.)\s+', r'\1 ', raw)
            elements.append(('p', clean_md_inline(raw)))
            
    return elements

def convert_md_file_to_hwpx(md_path, hwpx_path):
    elements = parse_md_to_hwpx_elements(md_path)
    if not elements:
        print(f'[WARN] No elements parsed from {md_path}')
        return False

    temp_dir = os.path.join(os.path.dirname(hwpx_path), '_temp_conv_' + os.path.splitext(os.path.basename(hwpx_path))[0])
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(TEMPLATE_PATH, 'r') as z:
        z.extractall(temp_dir)

    sec_path = os.path.join(temp_dir, 'Contents', 'section0.xml')
    tree_sec = ET.parse(sec_path)
    root_sec = tree_sec.getroot()

    for child in list(root_sec):
        root_sec.remove(child)

    ns_hp = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
    ns_hs = 'http://www.hancom.co.kr/hwpml/2011/section'
    ns_hc = 'http://www.hancom.co.kr/hwpml/2011/core'

    def make_p(text, char_pr_id='9', para_pr_id='0'):
        new_p = ET.Element(f'{{{ns_hp}}}p', {'paraPrID': para_pr_id})
        run = ET.SubElement(new_p, f'{{{ns_hp}}}run', {'charPrID': char_pr_id})
        t = ET.SubElement(run, f'{{{ns_hp}}}t')
        t.text = text
        return new_p

    def make_empty_p():
        new_p = ET.Element(f'{{{ns_hp}}}p', {'paraPrID': '0'})
        run = ET.SubElement(new_p, f'{{{ns_hp}}}run', {'charPrID': '9'})
        t = ET.SubElement(run, f'{{{ns_hp}}}t')
        t.text = ''
        return new_p

    for el_type, text in elements:
        if not text:
            continue
        if el_type == 'headline':
            root_sec.append(make_p(text, char_pr_id='7', para_pr_id='0'))
            root_sec.append(make_empty_p())
        elif el_type == 'sub':
            root_sec.append(make_p(text, char_pr_id='7', para_pr_id='0'))
            root_sec.append(make_empty_p())
        elif el_type == 'byline':
            root_sec.append(make_p(text, char_pr_id='8', para_pr_id='20'))
            root_sec.append(make_empty_p())
        else:
            root_sec.append(make_p(text, char_pr_id='9', para_pr_id='0'))
            root_sec.append(make_empty_p())

    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hs', ns_hs)
    ET.register_namespace('hc', ns_hc)
    tree_sec.write(sec_path, encoding='utf-8', xml_declaration=True)

    if os.path.exists(hwpx_path):
        os.remove(hwpx_path)

    with zipfile.ZipFile(hwpx_path, 'w', zipfile.ZIP_DEFLATED) as z_out:
        mime_path = os.path.join(temp_dir, 'mimetype')
        if os.path.exists(mime_path):
            z_out.write(mime_path, 'mimetype', compress_type=zipfile.ZIP_STORED)

        for root_d, dirs, files in os.walk(temp_dir):
            for file in files:
                if file == 'mimetype':
                    continue
                full_f = os.path.join(root_d, file)
                rel_f = os.path.relpath(full_f, temp_dir)
                z_out.write(full_f, rel_f)

    shutil.rmtree(temp_dir, ignore_errors=True)
    return True

readme_map = {
    r'F:\03_파이튼_문학_인문_창작서고\README.md': r'F:\03_파이튼_문학_인문_창작서고\00_키아노스_국가영구불멸서고_총람안내.hwpx',
    r'F:\03_파이튼_문학_인문_창작서고\01_세계문학_불멸의문학선\README.md': r'F:\03_파이튼_문학_인문_창작서고\01_세계문학_불멸의문학선\00_세계문학_불멸의문학선_서고안내.hwpx',
    r'F:\03_파이튼_문학_인문_창작서고\01_세계문학_불멸의문학선\06_이문열_나관중_삼국지연의\README.md': r'F:\03_파이튼_문학_인문_창작서고\01_세계문학_불멸의문학선\06_이문열_나관중_삼국지연의\00_삼국지_처세도덕_인텔리전스_총람안내.hwpx',
    r'F:\03_파이튼_문학_인문_창작서고\01_세계문학_불멸의문학선\08_윌리엄_셰익스피어_4대비극\README.md': r'F:\03_파이튼_문학_인문_창작서고\01_세계문학_불멸의문학선\08_윌리엄_셰익스피어_4대비극\00_셰익스피어_4대비극_영구보존서고_안내.hwpx',
    r'F:\03_파이튼_문학_인문_창작서고\02_역사_사상_철학서고\README.md': r'F:\03_파이튼_문학_인문_창작서고\02_역사_사상_철학서고\00_역사사상철학서고_총람안내.hwpx',
    r'F:\03_파이튼_문학_인문_창작서고\02_역사_사상_철학서고\01_서양_역사사상관\README.md': r'F:\03_파이튼_문학_인문_창작서고\02_역사_사상_철학서고\01_서양_역사사상관\00_서양_역사사상관_안내.hwpx',
    r'F:\03_파이튼_문학_인문_창작서고\02_역사_사상_철학서고\02_동양_역사사상관\README.md': r'F:\03_파이튼_문학_인문_창작서고\02_역사_사상_철학서고\02_동양_역사사상관\00_동양_역사사상관_안내.hwpx',
}

def main():
    md_files = []
    for root, dirs, files in os.walk(ROOT_DIR):
        for f in files:
            if f.lower().endswith('.md'):
                md_files.append(os.path.join(root, f))
    
    print(f'=== Starting batch conversion for {len(md_files)} Markdown files ===')
    success_count = 0
    fail_count = 0
    converted_pairs = []

    for i, md_path in enumerate(md_files, 1):
        hwpx_path = readme_map.get(md_path, os.path.splitext(md_path)[0] + '.hwpx')
        rel_md = os.path.relpath(md_path, ROOT_DIR)
        rel_hwpx = os.path.relpath(hwpx_path, ROOT_DIR)
        try:
            ok = convert_md_file_to_hwpx(md_path, hwpx_path)
            if ok and os.path.exists(hwpx_path) and os.path.getsize(hwpx_path) > 1000:
                size = os.path.getsize(hwpx_path)
                print(f'[{i:02d}/{len(md_files)}] SUCCESS: {rel_hwpx} ({size:,} B)')
                success_count += 1
                converted_pairs.append((md_path, hwpx_path))
            else:
                print(f'[{i:02d}/{len(md_files)}] FAILED: {rel_md}')
                fail_count += 1
        except Exception as e:
            print(f'[{i:02d}/{len(md_files)}] ERROR on {rel_md}: {e}')
            fail_count += 1

    print('=' * 60)
    print(f'Finished: Success={success_count}, Failed={fail_count}, Total={len(md_files)}')

if __name__ == '__main__':
    main()
