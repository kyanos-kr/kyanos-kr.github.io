import os
import sys
import shutil
import zipfile
import subprocess
import xml.etree.ElementTree as ET

TEMPLATE_PATH = r'D:\DATA CENTER\RPT DB\보도 기사 정보\AI 에이전트 통제 불능 위험\AI 에이전트 통제 불능 위험.hwpx'
BASE_DIR = r'D:\DATA CENTER\편집 기사\오늘편집\손영일컬럼'

columns_data = [
    {
        'raw_file': '국민들의 염장을 그만 질러라 206 .hwpx',
        'clean_title': '국민들의 염장을 그만 질러라 206',
        'headline': '국민들의 염장을 그만 질러라 206',
        'sub1': '고위 공직자들의 무책임한 언행과 서민 상처',
        'sub2': '진정한 공복(公僕)의 도리와 국민 공감의 무게',
        'byline': '-손 영일 컬럼 일요단상(日曜斷想)』 206',
        'color_top': (25, 30, 45),
        'color_btm': (10, 15, 25),
        'color_acc': (220, 70, 70),
        'category': '손영일 컬럼 | 일요단상 206'
    },
    {
        'raw_file': '그대야말로 진정한 대장부 204 .hwpx',
        'clean_title': '그대야말로 진정한 대장부 204',
        'headline': '그대야말로 진정한 대장부 204',
        'sub1': '어떤 풍파에도 꺾이지 않는 줏대 있는 삶',
        'sub2': '삼포(三抛)를 버리고 삼회(三懷)를 품는 선비정신',
        'byline': '-손 영일 컬럼 일요단상(日曜斷想)』 204',
        'color_top': (20, 35, 45),
        'color_btm': (8, 18, 25),
        'color_acc': (40, 180, 220),
        'category': '손영일 컬럼 | 일요단상 204'
    },
    {
        'raw_file': '긍정적 마인드를 가져야할 이유 651.hwpx',
        'clean_title': '긍정적 마인드를 가져야할 이유 651',
        'headline': '긍정적 마인드를 가져야할 이유 651',
        'sub1': '심은 대로 거두는 샐리의 법칙과 나비효과',
        'sub2': '사소한 선행과 긍정 에너지가 바꾸는 세상',
        'byline': '손 영일 컬럼창몽지상강론(創夢紙上講론)』651',
        'color_top': (20, 40, 30),
        'color_btm': (8, 20, 15),
        'color_acc': (60, 200, 120),
        'category': '손영일 컬럼 | 창몽지상강론 651'
    },
    {
        'raw_file': '외상이라면 소도 잡아먹는다 644.hwpx',
        'clean_title': '외상이라면 소도 잡아먹는다 644',
        'headline': '외상이라면 소도 잡아먹는다 644',
        'sub1': '상업신용의 발전사와 신용카드의 유혹',
        'sub2': '공짜라는 그물에 갇히는 인간의 탐욕 경계',
        'byline': '-손 영일 컬럼 『창몽지상강론(創夢紙上講론)』 644',
        'color_top': (35, 30, 20),
        'color_btm': (20, 15, 8),
        'color_acc': (230, 160, 40),
        'category': '손영일 컬럼 | 창몽지상강론 644'
    },
    {
        'raw_file': '충분히 있을 법한 가짜 뉴스들 649.hwpx',
        'clean_title': '충분히 있을 법한 가짜 뉴스들 649',
        'headline': '충분히 있을 법한 가짜 뉴스들 649',
        'sub1': 'AI 딥페이크와 SNS 시대 탈진실(Post-Truth)의 덫',
        'sub2': '확증편향을 뚫고 과학적·합리적 진실을 찾는 지혜',
        'byline': '-손 영일 컬럼『창몽지상강론(創夢紙上講론)』649',
        'color_top': (35, 20, 35),
        'color_btm': (18, 10, 20),
        'color_acc': (200, 90, 230),
        'category': '손영일 컬럼 | 창몽지상강론 649'
    },
    {
        'raw_file': '하루빨리 갑중의 최고갑이 되자205.hwpx',
        'clean_title': '하루빨리 갑중의 최고갑이 되자 205',
        'headline': '하루빨리 갑(甲)중의 최고갑이 되자 205',
        'sub1': '이스라엘 민족사와 유대교 성립의 냉엄한 교훈',
        'sub2': '환상에서 벗어나 국가적 자강과 실력을 기르는 길',
        'byline': '-손 영일 컬럼 『일요단상(日曜斷想)』 205',
        'color_top': (30, 25, 45),
        'color_btm': (12, 10, 25),
        'color_acc': (255, 120, 60),
        'category': '손영일 컬럼 | 일요단상 205'
    }
]

def extract_body_paragraphs(hwpx_path):
    with zipfile.ZipFile(hwpx_path, 'r') as z:
        sec0 = z.read('Contents/section0.xml').decode('utf-8')
        root = ET.fromstring(sec0)
        paras = []
        for p in root.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}p'):
            t = ''.join([elem.text for elem in p.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}t') if elem.text]).strip()
            if t:
                paras.append(t)
        return paras[1:-1]

def create_column_hwpx(output_hwpx_path, headline, byline, paragraphs):
    temp_dir = os.path.join(os.path.dirname(output_hwpx_path), '_temp_hwpx_build')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(TEMPLATE_PATH, 'r') as z:
        z.extractall(temp_dir)

    hdr_path = os.path.join(temp_dir, 'Contents', 'header.xml')
    tree_hdr = ET.parse(hdr_path)
    root_hdr = tree_hdr.getroot()

    ns_hh = 'http://www.hancom.co.kr/hwpml/2011/head'
    ns_hp = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
    ns_core = 'http://www.hancom.co.kr/hwpml/2011/core'
    ns_hs = 'http://www.hancom.co.kr/hwpml/2011/section'

    for ff in root_hdr.iter(f'{{{ns_hh}}}fontface'):
        for font in ff.iter(f'{{{ns_hh}}}font'):
            font.attrib['face'] = '한컴 윤고딕 740'

    for p in root_hdr.iter(f'{{{ns_hh}}}paraPr'):
        ls = p.find(f'{{{ns_hh}}}lineSpacing')
        if ls is not None:
            ls.attrib['type'] = 'PERCENT'
            ls.attrib['value'] = '160'
        else:
            new_ls = ET.Element(f'{{{ns_hh}}}lineSpacing', {'type': 'PERCENT', 'value': '160', 'unit': 'PERCENT'})
            p.append(new_ls)

    ET.register_namespace('hh', ns_hh)
    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hc', ns_core)
    tree_hdr.write(hdr_path, encoding='utf-8', xml_declaration=True)

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

    def make_p(paraPrIDRef='0', styleIDRef='0'):
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

    def make_run(charPrIDRef='9', text=None):
        r = ET.Element(f'{{{ns_hp}}}run', {'charPrIDRef': str(charPrIDRef)})
        if text is not None:
            t = ET.SubElement(r, f'{{{ns_hp}}}t')
            t.text = text
        return r

    # P0: Headline (charPr 7: 11pt, bold)
    p0 = make_p('0', '0')
    run_sec = ET.SubElement(p0, f'{{{ns_hp}}}run', {'charPrIDRef': '7'})
    if sec_pr is not None:
        run_sec.append(sec_pr)
    if ctrl is not None:
        run_sec.append(ctrl)
    t0 = ET.SubElement(run_sec, f'{{{ns_hp}}}t')
    t0.text = headline
    root_sec.append(p0)

    # Empty line
    p_sp1 = make_p('0', '0')
    p_sp1.append(make_run('9'))
    root_sec.append(p_sp1)

    # Body paragraphs
    preview_paras = []
    for para_text in paragraphs:
        if not para_text.strip():
            continue
        p_body = make_p('0', '0')
        p_body.append(make_run('9', para_text.strip()))
        root_sec.append(p_body)

        # Empty line
        p_empty = make_p('0', '0')
        p_empty.append(make_run('9'))
        root_sec.append(p_empty)
        preview_paras.append(para_text.strip())

    # Byline (paraPr 20: right-aligned, charPr 8: 9.5pt)
    p_by = make_p('20', '0')
    p_by.append(make_run('8', byline))
    root_sec.append(p_by)

    # Final empty line
    p_end = make_p('0', '0')
    p_end.append(make_run('9'))
    root_sec.append(p_end)

    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hs', ns_hs)
    ET.register_namespace('hc', ns_core)
    ET.register_namespace('hh', ns_hh)
    tree_sec.write(sec_path, encoding='utf-8', xml_declaration=True)

    prv_text_path = os.path.join(temp_dir, 'Preview', 'PrvText.txt')
    if os.path.exists(prv_text_path):
        preview_content = f'{headline}\n\n' + '\n\n'.join(preview_paras) + f'\n\n{byline}\n'
        with open(prv_text_path, 'w', encoding='utf-8') as pf:
            pf.write(preview_content)

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
    print(f'Done HWPX: {output_hwpx_path}')

def render_image(dest_jpg, cat, title, sub1, sub2, top, btm, acc):
    safe_title = title.replace('"', '`"')
    safe_sub = (sub1 + '`r`n' + sub2).replace('"', '`"')
    safe_cat = cat.replace('"', '`"')
    ps_file = os.path.join(BASE_DIR, '_render_script.ps1')
    
    ps_lines = [
        'Add-Type -AssemblyName System.Drawing',
        '$width = 640',
        '$height = 360',
        '$bmp = New-Object System.Drawing.Bitmap($width, $height)',
        '$g = [System.Drawing.Graphics]::FromImage($bmp)',
        '$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias',
        '$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit',
        f'$cTop = [System.Drawing.Color]::FromArgb({top[0]}, {top[1]}, {top[2]})',
        f'$cBottom = [System.Drawing.Color]::FromArgb({btm[0]}, {btm[1]}, {btm[2]})',
        f'$cAccent = [System.Drawing.Color]::FromArgb({acc[0]}, {acc[1]}, {acc[2]})',
        '$rect = New-Object System.Drawing.Rectangle(0, 0, $width, $height)',
        '$brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush($rect, $cTop, $cBottom, [System.Drawing.Drawing2D.LinearGradientMode]::ForwardDiagonal)',
        '$g.FillRectangle($brush, $rect)',
        '$brush.Dispose()',
        '$penGrid = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(20, 255, 255, 255), 1)',
        'for ($x = 40; $x -lt $width; $x += 60) { $g.DrawLine($penGrid, $x, 0, $x, $height) }',
        'for ($y = 40; $y -lt $height; $y += 60) { $g.DrawLine($penGrid, 0, $y, $width, $y) }',
        '$penGrid.Dispose()',
        '$barBrush = New-Object System.Drawing.SolidBrush($cAccent)',
        '$g.FillRectangle($barBrush, 36, 32, 6, 24)',
        '$barBrush.Dispose()',
        '$fontCat = New-Object System.Drawing.Font("Malgun Gothic", 11, [System.Drawing.FontStyle]::Bold)',
        '$fontTitle = New-Object System.Drawing.Font("Malgun Gothic", 17, [System.Drawing.FontStyle]::Bold)',
        '$fontSub = New-Object System.Drawing.Font("Malgun Gothic", 10, [System.Drawing.FontStyle]::Regular)',
        '$fontBrand = New-Object System.Drawing.Font("Malgun Gothic", 9, [System.Drawing.FontStyle]::Bold)',
        '$brushCat = New-Object System.Drawing.SolidBrush($cAccent)',
        f'$g.DrawString("{safe_cat}", $fontCat, $brushCat, 50, 34)',
        '$brushCat.Dispose()',
        '$brushBrand = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(180, 255, 255, 255))',
        '$g.DrawString("KYANOS ANTNEWS COLUMN", $fontBrand, $brushBrand, 430, 36)',
        '$brushBrand.Dispose()',
        '$brushTitle = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)',
        '$titleRect = New-Object System.Drawing.RectangleF(36, 85, 568, 115)',
        '$formatTitle = New-Object System.Drawing.StringFormat',
        f'$g.DrawString("{safe_title}", $fontTitle, $brushTitle, $titleRect, $formatTitle)',
        '$brushTitle.Dispose()',
        '$brushSub = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(215, 225, 235))',
        '$subRect = New-Object System.Drawing.RectangleF(36, 215, 568, 75)',
        f'$g.DrawString("{safe_sub}", $fontSub, $brushSub, $subRect, $formatTitle)',
        '$brushSub.Dispose()',
        '$penLine = New-Object System.Drawing.Pen($cAccent, 3)',
        '$g.DrawLine($penLine, 36, 305, 604, 305)',
        '$penLine.Dispose()',
        '$brushFoot = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(160, 180, 200))',
        '$g.DrawString("2026.10.25 - ANTNEWS EDITORIAL SUITE", $fontBrand, $brushFoot, 36, 320)',
        '$g.DrawString("STANDARD 640PX IMAGE", $fontBrand, $brushFoot, 470, 320)',
        '$brushFoot.Dispose()',
        '$fontCat.Dispose()',
        '$fontTitle.Dispose()',
        '$fontSub.Dispose()',
        '$fontBrand.Dispose()',
        '$g.Dispose()',
        f'$dest = "{dest_jpg}"',
        '$dir = [System.IO.Path]::GetDirectoryName($dest)',
        'if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }',
        '$bmp.Save($dest, [System.Drawing.Imaging.ImageFormat]::Jpeg)',
        '$bmp.Dispose()',
        'Write-Host "SUCCESS: $dest"'
    ]

    with open(ps_file, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(ps_lines))
    
    ret = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_file], capture_output=True, text=True)
    if os.path.exists(ps_file):
        os.remove(ps_file)
    print(f'Rendered JPG: {dest_jpg} (ret={ret.returncode})')

def main():
    for col in columns_data:
        raw_hwpx_path = os.path.join(BASE_DIR, col['raw_file'])
        clean_title = col['clean_title']
        target_folder = os.path.join(BASE_DIR, clean_title)
        os.makedirs(target_folder, exist_ok=True)

        dest_hwpx = os.path.join(target_folder, clean_title + '.hwpx')
        dest_jpg = os.path.join(target_folder, clean_title + '.jpg')

        body_paras = extract_body_paragraphs(raw_hwpx_path)
        create_column_hwpx(dest_hwpx, col['headline'], col['byline'], body_paras)
        render_image(dest_jpg, col['category'], col['headline'], col['sub1'], col['sub2'],
                     col['color_top'], col['color_btm'], col['color_acc'])

        # Delete the raw unorganized file outside the folder
        if os.path.exists(raw_hwpx_path):
            os.remove(raw_hwpx_path)
            print(f'Cleaned up raw unorganized file: {raw_hwpx_path}')

        print(f'Successfully completed: {clean_title}\n')

    print('All 6 column packages successfully built and organized!')

if __name__ == '__main__':
    main()
