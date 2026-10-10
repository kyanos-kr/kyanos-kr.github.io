# -*- coding: utf-8 -*-
import sys
import io
import os
import zipfile
import shutil
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ref_path = r'E:\RPT DB\보도 기사 정보\1마이클스나이더\프랑스 연료 부족 위기에 처함.hwpx'
with zipfile.ZipFile(ref_path, 'r') as z:
    hdr_xml = z.read('Contents/header.xml')

# The 3 articles in chronological order
articles = [
    {
        'src': r'E:\편집 기사\오늘편집\대규모 긴장 고조가 임박해 이란 군의 경계 태세가 가능한 최고 수준으로 상향 조정되었다.hwpx',
        'out_name': '대규모 긴장 고조가 임박해 이란 군의 경계 태세가 가능한 최고 수준으로 상향 조정되었다.hwpx',
        'main_title': '중동 전면전 초읽기, 이란 최고 경계령',
        'sub_title1': '미사일 보복 위협과 호르무즈 전운 고조',
        'sub_title2': '글로벌 유가 폭등과 대규모 에너지 위기',
        'remove_tail': False,
        'translations': {
            "He said that given the country’s current circumstances and recent attacks against it, remaining in the NPT offers Iran nothing but harm.":
            "그는 국가의 현재 상황과 최근 자국에 가해진 공격들을 고려할 때 NPT에 잔류하는 것은 이란에 해악만 가져다줄 뿐이라고 말했다.",
            "Once they have withdrawn from that treaty, they would be free to start testing nuclear weapons.":
            "이란이 조약에서 탈퇴하게 되면, 아무런 제약 없이 핵무기 실험을 시작할 수 있게 될 것이다."
        }
    },
    {
        'src': r'E:\편집 기사\오늘편집\네 노아의방주는 역사적사실.hwpx',
        'out_name': '네 노아의방주는 역사적사실.hwpx',
        'main_title': '노아의 방주 안식처와 역사적 실체 규명',
        'sub_title1': '터키 두루피나르 지층서 지하 탐사 진행',
        'sub_title2': '정밀 시추와 현대 과학으로 입증되는 역사',
        'remove_tail': True,
        'translations': {}
    },
    {
        'src': r'E:\편집 기사\오늘편집\러시아 폐페스트 발병 은폐.hwpx',
        'out_name': '러시아 폐페스트 발병 은폐.hwpx',
        'main_title': '러시아 폐페스트 의혹과 전염병 공포',
        'sub_title1': '연구소 조교 사망과 병원 5곳 전격 봉쇄',
        'sub_title2': '치사율 100% 위험과 푸틴 당국의 은폐 의혹',
        'remove_tail': False,
        'translations': {}
    }
]

dest_dir = r'E:\RPT DB\보도 기사 정보\1마이클스나이더'

for art in articles:
    print(f"Processing: {os.path.basename(art['src'])}")
    out_path = os.path.join(dest_dir, art['out_name'])
    
    with zipfile.ZipFile(art['src'], 'r') as zin:
        file_map = {}
        for item in zin.infolist():
            file_map[item.filename] = zin.read(item.filename)
            
    # Update header.xml with the standard reference header (contains YoonGothic 740, 11pt, 160% line spacing)
    file_map['Contents/header.xml'] = hdr_xml
    
    # Process section0.xml
    sec_xml = file_map['Contents/section0.xml'].decode('utf-8')
    root = ET.fromstring(sec_xml)
    
    # Register namespaces
    ns = {
        'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
        'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
        'hc': 'http://www.hancom.co.kr/hwpml/2011/core'
    }
    for prefix, uri in [
        ('', 'http://www.hancom.co.kr/hwpml/2011/section'),
        ('hp', 'http://www.hancom.co.kr/hwpml/2011/paragraph'),
        ('hs', 'http://www.hancom.co.kr/hwpml/2011/section'),
        ('hc', 'http://www.hancom.co.kr/hwpml/2011/core'),
        ('ha', 'http://www.hancom.co.kr/hwpml/2011/app'),
        ('hp10', 'http://www.hancom.co.kr/hwpml/2016/paragraph'),
        ('hh', 'http://www.hancom.co.kr/hwpml/2011/head'),
        ('hhs', 'http://www.hancom.co.kr/hwpml/2011/history'),
        ('hm', 'http://www.hancom.co.kr/hwpml/2011/master-page'),
        ('hpf', 'http://www.hancom.co.kr/schema/2011/hpf'),
        ('dc', 'http://purl.org/dc/elements/1.1/'),
        ('opf', 'http://www.idpf.org/2007/opf/'),
        ('ooxmlchart', 'http://www.hancom.co.kr/hwpml/2016/ooxmlchart'),
        ('hwpunitchar', 'http://www.hancom.co.kr/hwpml/2016/HwpUnitChar'),
        ('epub', 'http://www.idpf.org/2007/ops'),
        ('config', 'urn:oasis:names:tc:opendocument:xmlns:config:1.0')
    ]:
        ET.register_namespace(prefix, uri)

    p_list = list(root.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}p'))
    
    # Check if tail needs removal
    if art['remove_tail']:
        for p_elem in list(p_list):
            texts = ''.join([t.text for t in p_elem.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}t') if t.text])
            if '앤트뉴스의 논평 컬럼으로 재작성' in texts or '사실과 역사적 사실을 확인 후' in texts:
                root.remove(p_elem)
                print("  Removed editor note tail paragraph.")

    # Apply translations
    if art['translations']:
        for p_elem in root.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}p'):
            for t_elem in p_elem.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}t'):
                if t_elem.text:
                    for src_en, tgt_ko in art['translations'].items():
                        if src_en in t_elem.text:
                            t_elem.text = t_elem.text.replace(src_en, tgt_ko)
                            print(f"  Translated: {src_en[:30]}... -> {tgt_ko[:30]}...")

    # Refresh p_list
    p_list = list(root.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}p'))

    # Check if headline structure already exists (like in Russia article)
    # P0: Main title, P2, P3: Sub titles, P5: Original article title
    # Let's inspect the start of p_list
    first_texts = [''.join([t.text for t in p.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}t') if t.text]).strip() for p in p_list[:5]]
    
    # Structure of standard Snyder hwpx:
    # P0 (paraPr=20): Main Headline [charPr=7]
    # P1 (paraPr=22): Empty [charPr=8]
    # P2 (paraPr=22): Sub Headline 1 [charPr=8]
    # P3 (paraPr=22): Sub Headline 2 [charPr=8]
    # P4 (paraPr=20): Empty [charPr=9]
    # P5 (paraPr=20): Original Article Title [charPr=10]
    
    # Function to create a standard paragraph
    def create_p(paraPrID, charPrID, text=""):
        p = ET.Element('{http://www.hancom.co.kr/hwpml/2011/paragraph}p', {
            'id': '2147483648',
            'paraPrIDRef': str(paraPrID),
            'styleIDRef': '0',
            'pageBreak': '0',
            'columnBreak': '0',
            'merged': '0'
        })
        run = ET.SubElement(p, '{http://www.hancom.co.kr/hwpml/2011/paragraph}run', {
            'charPrIDRef': str(charPrID)
        })
        if text:
            t = ET.SubElement(run, '{http://www.hancom.co.kr/hwpml/2011/paragraph}t')
            t.text = text
        return p

    if '러시아 폐페스트' in art['out_name']:
        # Russia already has some titles at P0, P2. Let's replace the header block cleanly.
        # Find where the author/date or body begins
        body_idx = 0
        for i, p in enumerate(p_list):
            txt = ''.join([t.text for t in p.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}t') if t.text]).strip()
            if '마이클 스나이더' in txt or '16시간 전' in txt or p.find('.//{http://www.hancom.co.kr/hwpml/2011/paragraph}pic') is not None:
                body_idx = i
                break
        # Remove paragraphs before body_idx
        for p in p_list[:body_idx]:
            root.remove(p)
        orig_title = "러시아 폐페스트 발병 은폐: 28세 과학자 급사 후 확산 의혹과 통제"
    else:
        # P0 is the original title, P1 is author, P2 is date, P3 is pic
        orig_title = first_texts[0]
        # Remove original title paragraph P0
        root.remove(p_list[0])

    # Now insert standard headlines at the beginning
    new_head_paras = [
        create_p(20, 7, art['main_title']),
        create_p(22, 8, ""),
        create_p(22, 8, art['sub_title1']),
        create_p(22, 8, art['sub_title2']),
        create_p(20, 9, ""),
        create_p(20, 10, orig_title)
    ]
    
    # We need to preserve secPr in the first paragraph of section0
    # In section0, P0 normally carries secPr. Let's make sure secPr is in new_head_paras[0].
    # Check if original first paragraph had secPr
    orig_secPr = None
    for run in p_list[0].iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}run'):
        secPr = run.find('{http://www.hancom.co.kr/hwpml/2011/paragraph}secPr')
        if secPr is not None:
            orig_secPr = secPr
            break
            
    if orig_secPr is not None:
        run0 = list(new_head_paras[0].iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}run'))[0]
        run0.insert(0, orig_secPr)
        
    for idx, new_p in enumerate(new_head_paras):
        root.insert(idx, new_p)

    # Now update all runs across the entire section to use YoonGothic 740 standard charPr & paraPr
    # Specifically, set body paragraphs to charPr=8 (11pt YoonGothic) and paraPr=22 or 21 (160% line spacing)
    for p in root.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}p'):
        # Keep our newly created header paras as they are
        if p in new_head_paras:
            continue
        # For other paragraphs:
        # If it has a pic, keep paraPr=21
        has_pic = p.find('.//{http://www.hancom.co.kr/hwpml/2011/paragraph}pic') is not None
        if has_pic:
            p.set('paraPrIDRef', '21')
            for run in p.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}run'):
                if run.find('{http://www.hancom.co.kr/hwpml/2011/paragraph}pic') is not None:
                    run.set('charPrIDRef', '11')
                else:
                    run.set('charPrIDRef', '8')
        else:
            p.set('paraPrIDRef', '22')
            for run in p.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}run'):
                run.set('charPrIDRef', '8')

    # Convert XML back to string
    new_sec_xml = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    file_map['Contents/section0.xml'] = new_sec_xml
    
    # Also update Preview/PrvText.txt
    prv_lines = [
        art['main_title'],
        "",
        art['sub_title1'],
        art['sub_title2'],
        "",
        orig_title
    ]
    # Extract rest of text for PrvText
    for p in root.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}p'):
        if p not in new_head_paras:
            t_str = ''.join([t.text for t in p.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}t') if t.text]).strip()
            if t_str:
                prv_lines.append(t_str)
    file_map['Preview/PrvText.txt'] = '\n'.join(prv_lines).encode('utf-8')

    # Write out the new zip file
    with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        # Note: mimetype must be first and uncompressed in HWPX/ODF standards
        if 'mimetype' in file_map:
            zout.writestr('mimetype', file_map['mimetype'], compress_type=zipfile.ZIP_STORED)
        for fname, data in file_map.items():
            if fname != 'mimetype':
                zout.writestr(fname, data, compress_type=zipfile.ZIP_DEFLATED)

    print(f"  Successfully created: {out_path}")
    print(f"  Size: {os.path.getsize(out_path)} bytes\n")
