import os
import sys
import shutil
import zipfile
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"D:\안티그래비티파이튼"
TODAY_DIR = r"D:\DATA CENTER\편집 기사\오늘편집"
TEMP_DIR = os.path.join(TODAY_DIR, "임시폴더")
TEMPLATE_PATH = r"D:\DATA CENTER\RPT DB\보도 기사 정보\AI 에이전트 통제 불능 위험\AI 에이전트 통제 불능 위험.hwpx"

os.makedirs(TEMP_DIR, exist_ok=True)

# 1. HWPX Creator function
def create_standard_hwpx(output_hwpx_path, headline, sub1, sub2, byline, paragraphs, column_footer=None):
    build_dir = os.path.join(os.path.dirname(output_hwpx_path), '_build_temp')
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    with zipfile.ZipFile(TEMPLATE_PATH, 'r') as z:
        z.extractall(build_dir)

    hdr_path = os.path.join(build_dir, 'Contents', 'header.xml')
    tree_hdr = ET.parse(hdr_path)
    root_hdr = tree_hdr.getroot()

    ns_hh = 'http://www.hancom.co.kr/hwpml/2011/head'
    ns_hp = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
    ns_core = 'http://www.hancom.co.kr/hwpml/2011/core'
    ns_hs = 'http://www.hancom.co.kr/hwpml/2011/section'

    # Ensure 한컴 윤고딕 740
    for ff in root_hdr.iter(f'{{{ns_hh}}}fontface'):
        for font in ff.iter(f'{{{ns_hh}}}font'):
            font.attrib['face'] = '한컴 윤고딕 740'

    # Line spacing 160%
    for p in root_hdr.iter(f'{{{ns_hh}}}paraPr'):
        found_ls = False
        for ls in p.iter(f'{{{ns_hh}}}lineSpacing'):
            ls.attrib['type'] = 'PERCENT'
            ls.attrib['value'] = '160'
            found_ls = True
        if not found_ls:
            new_ls = ET.Element(f'{{{ns_hh}}}lineSpacing', {'type': 'PERCENT', 'value': '160', 'unit': 'PERCENT'})
            p.append(new_ls)

    ET.register_namespace('hh', ns_hh)
    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hc', ns_core)
    tree_hdr.write(hdr_path, encoding='utf-8', xml_declaration=True)

    # Section 0
    sec_path = os.path.join(build_dir, 'Contents', 'section0.xml')
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

    p_id = 1000000000

    def make_p(paraPrIDRef="0", styleIDRef="0"):
        nonlocal p_id
        p = ET.Element(f'{{{ns_hp}}}p', {
            'id': str(p_id),
            'paraPrIDRef': str(paraPrIDRef),
            'styleIDRef': str(styleIDRef),
            'pageBreak': '0',
            'columnBreak': '0',
            'merged': '0'
        })
        p_id += 1
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

    # Sub1 & Sub2 (charPr 7: 11pt, bold)
    p_sub1 = make_p("0", "0")
    p_sub1.append(make_run("7", sub1))
    root_sec.append(p_sub1)

    p_sub2 = make_p("0", "0")
    p_sub2.append(make_run("7", sub2))
    root_sec.append(p_sub2)

    # Blank line
    p_sp2 = make_p("0", "0")
    p_sp2.append(make_run("9"))
    root_sec.append(p_sp2)

    # Body paragraphs (charPr 9: 11pt, normal, separated by blank line)
    preview_paras = []
    for para_text in paragraphs:
        if not para_text.strip():
            continue
        p_b = make_p("0", "0")
        p_b.append(make_run("9", para_text.strip()))
        root_sec.append(p_b)

        p_empty = make_p("0", "0")
        p_empty.append(make_run("9"))
        root_sec.append(p_empty)
        preview_paras.append(para_text.strip())

    # Byline (paraPr 20: right-aligned, charPr 8: 9.5pt)
    p_by = make_p("20", "0")
    p_by.append(make_run("8", byline))
    root_sec.append(p_by)

    # Column footer if any (e.g. 마이클 스나이더 컬럼, 손영일 컬럼)
    if column_footer:
        p_cf = make_p("20", "0")
        p_cf.append(make_run("8", column_footer))
        root_sec.append(p_cf)

    # Final empty line
    p_end = make_p("0", "0")
    p_end.append(make_run("9"))
    root_sec.append(p_end)

    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hs', ns_hs)
    ET.register_namespace('hc', ns_core)
    ET.register_namespace('hh', ns_hh)
    tree_sec.write(sec_path, encoding='utf-8', xml_declaration=True)

    # PrvText.txt
    prv_text_path = os.path.join(build_dir, 'Preview', 'PrvText.txt')
    if os.path.exists(prv_text_path):
        preview_content = f"{headline}\n\n{sub1}\n{sub2}\n\n" + "\n\n".join(preview_paras) + f"\n\n{byline}\n"
        if column_footer:
            preview_content += f"{column_footer}\n"
        with open(prv_text_path, 'w', encoding='utf-8') as pf:
            pf.write(preview_content)

    if os.path.exists(output_hwpx_path):
        os.remove(output_hwpx_path)

    with zipfile.ZipFile(output_hwpx_path, 'w') as zout:
        mimetype_path = os.path.join(build_dir, 'mimetype')
        if os.path.exists(mimetype_path):
            zout.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)
        for r_dir, dirs, files in os.walk(build_dir):
            for file in files:
                full_p = os.path.join(r_dir, file)
                rel_p = os.path.relpath(full_p, build_dir)
                if rel_p == 'mimetype':
                    continue
                zout.write(full_p, rel_p, compress_type=zipfile.ZIP_DEFLATED)

    shutil.rmtree(build_dir)
    print(f"Created HWPX: {output_hwpx_path}")


# 2. Standard 640px Image Generator
def create_article_image(output_path, title_text, category_text, bg_color1, bg_color2, accent_color):
    width = 640
    height = 380
    img = Image.new('RGB', (width, height), color=bg_color1)
    draw = ImageDraw.Draw(img)

    # Vertical gradient
    for y in range(height):
        r = int(bg_color1[0] + (bg_color2[0] - bg_color1[0]) * (y / height))
        g = int(bg_color1[1] + (bg_color2[1] - bg_color1[1]) * (y / height))
        b = int(bg_color1[2] + (bg_color2[2] - bg_color1[2]) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Outer border
    draw.rectangle([(15, 15), (width - 15, height - 15)], outline=accent_color, width=2)
    # Inner subtle line
    draw.rectangle([(22, 22), (width - 22, height - 22)], outline=(255, 255, 255, 40), width=1)

    # Category pill
    draw.rectangle([(40, 40), (220, 75)], fill=accent_color)
    
    font_paths = [
        "C:/Windows/Fonts/malgunbd.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/gulim.ttc"
    ]
    f_cat = None
    f_title = None
    f_sub = None
    f_brand = None
    for fp in font_paths:
        if os.path.exists(fp):
            f_cat = ImageFont.truetype(fp, 15)
            f_title = ImageFont.truetype(fp, 23)
            f_sub = ImageFont.truetype(fp, 14)
            f_brand = ImageFont.truetype(fp, 13)
            break
    if not f_cat:
        f_cat = ImageFont.load_default()
        f_title = ImageFont.load_default()
        f_sub = ImageFont.load_default()
        f_brand = ImageFont.load_default()

    draw.text((55, 48), category_text, fill=(255, 255, 255), font=f_cat)

    # Title text - auto wrapping
    words = title_text.split()
    lines = []
    cur = ""
    for w in words:
        if len(cur + " " + w) > 18:
            lines.append(cur)
            cur = w
        else:
            cur = cur + " " + w if cur else w
    if cur:
        lines.append(cur)

    start_y = 120
    for l in lines[:3]:
        draw.text((45, start_y), l, fill=(255, 255, 255), font=f_title)
        start_y += 38

    # Accent decorative bar
    draw.line([(45, start_y + 15), (145, start_y + 15)], fill=accent_color, width=3)

    # Bottom branding
    draw.text((45, height - 50), "ANT NEWS · KYANOS INTELLIGENCE ARCHIVE", fill=(180, 190, 205), font=f_brand)
    draw.text((width - 150, height - 50), "2026.11.01", fill=(180, 190, 205), font=f_brand)

    img.save(output_path, quality=95)
    print(f"Created 640px image: {output_path}")


# 3. Main Builder Routine
def main():
    print("=== 오늘편집 4대 부문 패키징 및 HWPX 생성 시작 ===")

    # -------------------------------------------------------------
    # 1) 기사: 국제 비상식량 비축 권고 사실 확인 리포트
    # -------------------------------------------------------------
    pkg1_dir = os.path.join(TEMP_DIR, "국제 비상식량 비축 권고 관련 사실 확인")
    os.makedirs(pkg1_dir, exist_ok=True)
    orig1_src = os.path.join(TODAY_DIR, "기사", "국제 비상식량 비축 권고 관련 사실 확인 리포트.hwpx")
    orig1_dst = os.path.join(pkg1_dir, "[원본]국제 비상식량 비축 권고 관련 사실 확인 리포트.hwpx")
    shutil.copy2(orig1_src, orig1_dst)

    img1_dst = os.path.join(pkg1_dir, "국제비상식량비축권고.jpg")
    create_article_image(
        img1_dst,
        "미·EU·일 비상식량 비축 권고 확산과 팩트체크",
        "ANT NEWS 팩트체크",
        (15, 23, 42), (30, 41, 59), (59, 130, 246)
    )

    mod1_dst = os.path.join(pkg1_dir, "[수정본]국제 비상식량 비축 권고 관련 사실 확인 리포트.hwpx")
    paras1 = [
        "최근 온라인과 소셜미디어를 중심으로 미국과 유럽연합(EU), 일본 등 주요국 정부가 국민들에게 비상식량을 대규모로 비축하라는 지침을 내렸다는 주장이 급속히 확산하며 국제사회의 불안감을 증폭시키고 있다. 특히 일부 보수 매체와 온라인 채널을 중심으로 세계 3차 대전 발발이 임박했다는 위기론까지 덧붙여지면서 대중적 동요가 확산하는 양상이다. 이에 앤트뉴스 국제탐사보도국은 각국 정부와 국제기구의 공식 발표를 전수 검증하여 사실관계를 명확히 규명했다.",
        "검증 결과, 일본과 EU 정부가 시민들에게 비상물자 비축을 권고한 것은 객관적 사실로 확인됐다. 일본 정부는 난카이 해구 대지진과 수도권 직하지진, 후지산 분화 등 초대형 자연재해에 대비해 최소 3일치에서 1주일치의 식량과 식수, 생필품을 비축할 것을 공식 지침으로 제시하고 있다. 이는 수십 년간 이어져 온 일본 방재청의 정례적인 재난 대비 정책 강화의 일환이며, 전쟁 임박을 전제로 한 조치가 아니다.",
        "EU 집행위원회 역시 '대비 연합 전략(Preparedness Union Strategy)'을 공식 발표하고, 모든 시민이 국가의 직접 지원 없이 최소 72시간 동안 자급자족할 수 있는 비상 배낭과 물자를 구비할 것을 권고했다. 하디야 라비브 EU 집행위원은 러시아-우크라이나 전쟁 장기화, 에너지 인프라에 대한 사이버 공격, 기후 재난, 팬데믹 등 복합 위기가 동시다발적으로 발생할 경우 행정망이 정상 복구될 때까지 3일간의 골든타임을 확보하는 것이 필수적이라고 설명했다. 즉 전쟁 직전의 공황 상태가 아닌, 현대 국가 위기관리의 핵심인 '사회적 회복력(Resilience)'을 극대화하려는 제도적 조치다.",
        "반면, '미국 정부가 전 국민에게 30일치 비상식량을 비축하라고 공식 명령했다'는 주장은 신뢰할 만한 공식 근거가 전혀 없는 허위 과장 정보로 판명됐다. 미 연방재난관리청(FEMA)과 Ready.gov의 공식 가이드라인은 최소 72시간, 최대 2주 수준의 비상물자 구비를 일관되게 권고하고 있을 뿐이다. 30일치 비축 주장은 전직 사법기관 출신 방송인의 개인적 발언이나 인터넷 콘텐츠가 와전된 것에 불과하며, 국방부(DoD) 차원의 공식 지침도 발표된 바 없다.",
        "결론적으로 주요 선진국들이 비상물자 비축을 강조하는 배경에는 코로나19 팬데믹 당시 목격된 생필품 사재기와 글로벌 물류망 마비, 국지적 분쟁과 기후 위기 등이 얽힌 복합 리스크에 선제 대응하려는 의도가 자리 잡고 있다. 전쟁 공포에 기반한 자극적 선동에 휘둘리기보다는, 현대 사회의 모든 시민이 일상적 위기 극복을 위한 최소한의 자급 역량을 갖추는 합리적 방재 의식이 요구되는 시점이다."
    ]
    create_standard_hwpx(
        mod1_dst,
        "미·EU·일 비상식량 비축 권고 확산… 전쟁 공포와 팩트체크",
        "일본 3일·EU 72시간 자급 공식 권고… '전시 대비' 아닌 복합 재난 회복력 강화",
        "美 '30일치 비축 명령'은 사실무근… 기후 재난·공급망 마비 대비 자급 역량 부각",
        "[2026.11.01 | 앤트뉴스 국제탐사보도국]",
        paras1
    )

    # -------------------------------------------------------------
    # 2) 마이클스나이더: 데이비드 윌커슨이 미국의 미래에 대해 본 8가지
    # -------------------------------------------------------------
    pkg2_dir = os.path.join(TEMP_DIR, "데이비드 윌커슨이 미국의 미래에 대해 본 8가지")
    os.makedirs(pkg2_dir, exist_ok=True)
    orig2_src = os.path.join(TODAY_DIR, "마이클스나이더", "데이비드 윌커슨이 미국의 미래에 대해 본 8가지 .hwpx")
    orig2_dst = os.path.join(pkg2_dir, "[원본]데이비드 윌커슨이 미국의 미래에 대해 본 8가지 .hwpx")
    shutil.copy2(orig2_src, orig2_dst)

    img2_dst = os.path.join(pkg2_dir, "데이비드윌커슨미국미래.jpg")
    create_article_image(
        img2_dst,
        "데이비드 윌커슨의 예언과 미국의 현실",
        "마이클 스나이더 컬럼",
        (45, 10, 15), (75, 20, 25), (225, 29, 72)
    )

    mod2_dst = os.path.join(pkg2_dir, "[수정본]데이비드 윌커슨이 미국의 미래에 대해 본 8가지.hwpx")
    paras2 = [
        "데이비드 윌커슨은 미국의 미래에 대해 보여준 환상에 깊은 감정적 충격을 받았다. 그 후 몇 달 동안 그는 이를 마음속에서 떨쳐내려 했지만 실패했다. 그는 가능한 한 많은 사람들과 이 사실을 나누어야 한다는 것을 알았지만, 그렇게 할 경우 광신자라는 극심한 비판과 조롱을 받게 될 것임을 잘 알고 있었다. 하지만 그 어떤 두려움도 그를 멈추게 하지 못했다. 데이비드 윌커슨은 자신이 겪은 일을 세상과 나눌 용기를 지녔고, 우리는 반세기가 지난 지금도 그가 남긴 준엄한 경고를 되돌아보고 있다.",
        "1963년 출간되어 전 세계 1,500만 부 이상 판매된 베스트셀러 『십자가와 스위치블레이드』로 널리 알려진 윌커슨은 평생을 하나님을 찾고 사람들의 영적·육체적 고통을 돌보는 데 바쳤다. 2011년 79세를 일기로 세상을 떠나기 전, 그는 1973년에 하나님으로부터 미래에 일어날 거대한 환상을 보았다. 1974년 출간된 『비전』에 상세히 기록된 이 예언은 미국과 전 세계에 다가올 다섯 가지 비극적 재앙을 담고 있었으며, 그가 본 여덟 가지 구체적 징조는 오늘날 놀라울 정도로 적나라하게 현실화되었다.",
        "첫째, 그는 유럽에서 시작되어 일본을 거쳐 마침내 미국으로 확산될 심각한 글로벌 경제 붕괴를 예고했다. 1973년 당시 동서로 분단되어 있던 '독일'에서 금융 혼란의 불씨가 당겨질 것이라 지목한 그의 예언은 매우 흥미롭다. 현재 프랑스의 정정 불안과 더불어 유럽 최대 경제국인 독일의 국채 수익률이 요동치고 국책 기간산업이 흔들리는 현실은 그가 본 경제적 혼란의 궤적과 정확히 일치한다.",
        "둘째, 전 세계적 자연재해의 폭증과 미국의 연쇄 대지진이다. 윌커슨은 단순한 단발성 재난이 아니라 지구가 산통을 겪듯 갈수록 빈번하고 강력해지는 기상이변을 목격했다. 2026년 슈퍼 엘니뇨가 촉발한 사상 초유의 기상이변과 더불어, 내가 수년간 경고해 온 캘리포니아의 '빅 원' 및 뉴마드리드 단층의 거대 지진 위험은 결코 가벼운 경고로 치부할 수 없다.",
        "셋째, 전 세계적 기근과 식량 위기다. 기상이변과 지정학적 갈등으로 인해 식량 공급망이 급격히 위축되고 수억 명의 인구가 굶주림에 직면할 것이라는 예언 또한 현실이 되었다. 넷째, 대중문화와 미디어를 통한 도덕적 오염의 범람이다. 한때 상상조차 할 수 없었던 퇴폐적이고 선정적인 콘텐츠가 스마트폰과 스트리밍을 통해 24시간 여과 없이 안방으로 쏟아져 들어오고 있다.",
        "다섯째는 가정 내 반항과 가족 공동체의 해체다. 윌커슨은 청소년들이 부모를 증오하고 가정의 신뢰가 무너지는 비극을 보았다. 오늘날 수많은 결손 가정과 스마트폰 중독 속에서 진정한 대화와 유대를 상실한 가정의 붕괴는 그의 예언 그대로다. 여섯째는 교회의 세속화와 성경적 진리의 훼손이며, 일곱째는 영화와 방송 미디어가 기독교 신앙을 조롱하고 오컬트와 마술을 매력적으로 미화하는 영적 타락이다.",
        "오늘날 우리는 선이 악이라 불리고, 악이 선으로 둔갑하는 철저히 뒤집힌 사회를 살아가고 있다. 50년 전 윌커슨이 눈물로 경고했던 환상들은 더 이상 먼 미래의 상상이 아니다. 그것은 지금 우리 눈앞에서 펼쳐지고 있는 엄연한 현실이다."
    ]
    create_standard_hwpx(
        mod2_dst,
        "데이비드 윌커슨의 예언과 미국의 현실",
        "50년 전 경고한 경제 혼란과 자연재해",
        "가정 붕괴와 도덕적 타락의 현실화",
        "[2026.11.01 | 앤트뉴스 편집국]",
        paras2,
        column_footer="마이클 스나이더 컬럼"
    )

    # -------------------------------------------------------------
    # 3) 손영일컬럼: 30년 후의 인간세상 내다보기 221
    # -------------------------------------------------------------
    pkg3_dir = os.path.join(TEMP_DIR, "30년 후의 인간세상 내다보기 221")
    os.makedirs(pkg3_dir, exist_ok=True)
    orig3_src = os.path.join(TODAY_DIR, "손영일컬럼", "30년 후의 인간세상 내다보기 221 .hwpx")
    orig3_dst = os.path.join(pkg3_dir, "[원본]30년 후의 인간세상 내다보기 221 .hwpx")
    shutil.copy2(orig3_src, orig3_dst)

    img3_dst = os.path.join(pkg3_dir, "30년후인간세상내다보기.jpg")
    create_article_image(
        img3_dst,
        "30년 후의 인간세상 내다보기 221",
        "손영일 컬럼 일요단상",
        (20, 35, 25), (35, 60, 45), (16, 185, 129)
    )

    mod3_dst = os.path.join(pkg3_dir, "[수정본]30년 후의 인간세상 내다보기 221.hwpx")
    paras3 = [
        "제3차 세계대전은 과연 일어날 것인가? 전문가들은 첨단 무기와 핵전력이 고도화될수록 기존 강대국들은 패권을 지키기 위해 세력권을 넓히려 할 것이며, 과거 대전의 피해국들은 새로운 패전의 비극을 피하기 위해 죽기 살기로 맞설 것이라 경고한다. 2050년부터 2056년까지 약 6년 동안 펼쳐질 제3차 세계대전의 가상 시나리오에 따르면, 직접적인 전투와 폭격으로만 1억 5천만 명에서 2억 명이 희생되고 기근과 의료체계 붕괴, 감염병과 인프라 파괴로 인한 총 사망자는 3억 5천만 명에서 5억 명에 달할 것으로 추산된다. 세계 총생산(GDP) 또한 개전 이전 정점 대비 30% 이상 폭락할 것이다.",
        "단순히 공장 몇 개가 파괴되는 것보다 훨씬 치명적인 문제는 전 세계 산업 공급망 전체가 완전히 절단된다는 점이다. 반도체 팹이 멀쩡히 살아남더라도 고순도 희귀금속과 정밀 노광장비가 끊기면 단 하나의 칩도 생산할 수 없다. 자동차 공장이 유지되어도 전장 센서와 반도체, 배터리와 소프트웨어 제어망이 무너지면 완성차의 출하는 불가능하다.",
        "따라서 대전이 종식된 후 각국이 마주할 전후 복구는 과거 1, 2차 대전 이후의 세계화 복원과는 근본적으로 차원을 달리할 것이다. 전략물자에 대한 통제와 국가별 배급제, 외환규제와 자본이동 제한, 핵심 기간산업에 대한 국가 통제와 대규모 공공투자가 불가피하게 강화된다. 자유시장경제를 표방하는 국가라 할지라도 정부는 전력과 식량, 통신과 해운, 반도체와 방위산업 등 사활적 기간산업에 직접 개입하지 않을 수 없을 것이다.",
        "2056년 봄부터 스위스 제네바에서 열릴 종전회의 역시 이러한 냉혹한 현실을 인정하게 될 것이다. 패전국이라 하더라도 미국 본토에는 여전히 방대한 농업과 공업 인프라, 수천 기의 핵탄두가 잔존할 것이며, 유럽 각국 역시 전쟁 관여도와 피해 규모가 상이하다. 승전국에 속할 한국과 일본, 인도와 중동 국가들 또한 핵보유국인 미국을 무력으로 해체하거나 유럽 전체를 군정 하에 두는 것은 현실적으로 불가능함을 명확히 인식할 것이다.",
        "이에 따라 제네바 종전회의의 대원칙은 정권과 핵심 개인에게 전쟁 책임을 묻되, 국가 체제 자체는 보존하고 군사적 재발 방지를 담보하는 동시에 신속한 경제 재건을 추진하는 방향으로 타협점을 찾을 것이다. 이는 관용이라기보다 핵 시대를 살아가는 인류의 불가피한 현실적 선택이다. 핵보유국의 지휘체계가 완전히 와해될 경우 잔존 핵무기와 생화학물질을 통제할 방법이 없으며, 주요국의 경제가 장기 붕괴하면 승전국의 수출 시장과 원자재 공급망마저 공멸하기 때문이다.",
        "2056년 출범할 국제특별재판부는 국가와 국민 전체가 아닌 개인과 특정 군사 조직의 책임을 묻는 원칙을 채택할 것이다. 물론 패전국 지도부가 집중 기소되겠으나, 승전국 측의 불법 행위 역시 형식적으로나마 수사 대상에 오르며 '승자를 위한 재판'이라는 비판을 피해 갈 수 없을 것이다. 이 같은 30년 후의 전망은 문자 그대로 추론과 예견에 불과할지라도, 첨단 문명의 파괴력 앞에서 인류가 나아가야 할 방향을 진지하게 되돌아보게 하는 묵직한 화두다."
    ]
    create_standard_hwpx(
        mod3_dst,
        "30년 후의 인간세상 내다보기 221",
        "2050년대 제3차 세계대전 발발 가정과 문명사적 파괴",
        "글로벌 공급망 붕괴와 종전 후 제네바 체제의 현실적 재편",
        "[2026.11.01 | 앤트뉴스 문화인문학부]",
        paras3,
        column_footer="손 영일 컬럼 일요단상(日曜斷想) 221"
    )

    # -------------------------------------------------------------
    # 4) 문화: 미안하다
    # -------------------------------------------------------------
    pkg4_dir = os.path.join(TEMP_DIR, "미안하다")
    os.makedirs(pkg4_dir, exist_ok=True)
    orig4_src = os.path.join(TODAY_DIR, "문화", "미안하다.hwp")
    orig4_dst = os.path.join(pkg4_dir, "[원본]미안하다.hwp")
    shutil.copy2(orig4_src, orig4_dst)

    img4_dst = os.path.join(pkg4_dir, "미안하다.jpg")
    create_article_image(
        img4_dst,
        "골방의 눈물, 땀이라 우기며 삼킨 미안함",
        "앤트뉴스 문화수필",
        (30, 20, 40), (50, 30, 65), (168, 85, 247)
    )

    mod4_dst = os.path.join(pkg4_dir, "[수정본]미안하다.hwpx")
    paras4 = [
        "한여름 35도가 넘는 폭염 속에서 땀내 진동하는 작은 골방에 틀어박혀 이 글을 쓰고 있다. 혹여 누군가 불쑥 방문을 열고 들어와 내 붉어진 두 눈가에 흐르는 눈물이라도 볼라치면, 한사코 더위 탓에 쏟아지는 땀방울이라 우겨댈 참이다. 그 오랜 세월 가슴 밑바닥에서 남몰래 삼켜온 눈물이 감춰진 나만의 영원한 무덤 속으로 함께 동행하려면, 이 들켜버린 비밀 앞에서 자신이 너무나 초라해질 것만 같아서다.",
        "낡은 스피커에서는 저니(Journey)의 'Open Arms'가 애절하게 흘러나오고 있었다. 가슴속 깊은 곳에서 치받쳐 올라오는 먹먹한 회한이 걷잡을 수 없는 통곡으로 터져 나올까 두려워, 서둘러 이글스의 'Hotel California'로 음악을 바꾸어 버렸다. 보다 이성적으로 마음을 다잡고, 내 영혼의 가장 깊숙한 상처와 마주하여 이 고백을 끝까지 써 내려가기 위함이다. 그러나 찌푸려진 눈가 잔주름 사이로는 이미 주체할 수 없는 굵은 이슬이 쉼 없이 흘러내리고 있다.",
        "살아오면서 뼈저리게 후회하고 평생을 갚아도 모자랄 세 번의 미안한 일이 있다. 첫째는 나를 낳아 길러주신 부모님께 다하지 못한 효도요, 둘째는 험난한 세월을 묵묵히 함께 견뎌준 아내에게 지워준 삶의 무게이며, 마지막은 내 모든 피와 살을 나누어준 자식에게 온전히 다 주지 못한 부정(父情)이다. 세상의 그 어떤 성공과 명예도 가족의 눈물을 닦아주지 못했다면 그것은 부질없는 그림자에 불과함을 이제야 깨닫는다.",
        "누구나 인생의 황혼에 서면 부모와 아내에게 죄송한 마음을 품는다. 하지만 자식의 뒷모습을 바라보며 느끼는 아버지의 미안함은 가슴 한구석을 도려내는 듯한 또 다른 차원의 절규다. 부모에게 받은 사랑을 다 갚지도 못했는데, 내 자식에게는 그 절반의 온기조차 온전히 건네지 못한 채 세월만 흘러가 버렸다는 자책이 가슴을 친다.",
        "골방의 찌는 듯한 더위는 내 영혼의 부끄러움을 태우는 정화의 불길일지도 모른다. 눈물을 땀이라 속이며 써 내려간 이 남자의 참회는, 세상의 모든 아버지들이 가슴속 깊은 무덤 속에 묻어두고 차마 꺼내놓지 못한 가장 정직하고 시린 영혼의 기도다."
    ]
    create_standard_hwpx(
        mod4_dst,
        "골방의 눈물, 땀이라 우기며 삼킨 미안함",
        "35도 폭염의 골방에서 흘린 남자의 가슴 시린 고백",
        "부모와 아내, 그리고 자식에게 바치는 영혼의 참회록",
        "[2026.11.01 | 앤트뉴스 문화인문학부]",
        paras4
    )

    print("=== 오늘편집 4대 부문 패키징 및 HWPX 생성 완료 ===")

if __name__ == '__main__':
    main()
