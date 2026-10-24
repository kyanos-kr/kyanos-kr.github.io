import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

def build_hwpx_perfect(template_hwpx, output_hwpx, headline, sub1, sub2, paragraphs, byline):
    temp_dir = r'd:\안티그래비티파이튼\temp_hwpx_builder'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    # 1. Extract template
    with zipfile.ZipFile(template_hwpx, 'r') as z:
        z.extractall(temp_dir)
        
    sec0_path = os.path.join(temp_dir, 'Contents', 'section0.xml')
    tree = ET.parse(sec0_path)
    root = tree.getroot()
    
    ns_hp = "http://www.hancom.co.kr/hwpml/2011/paragraph"
    ns_hs = "http://www.hancom.co.kr/hwpml/2011/section"
    ns_hc = "http://www.hancom.co.kr/hwpml/2011/core"
    ns_hh = "http://www.hancom.co.kr/hwpml/2011/head"
    ns_hpf = "http://www.hancom.co.kr/schema/2011/hpf"
    
    # Extract secPr and ctrl from the original section0.xml
    first_p = root.find(f'{{{ns_hp}}}p')
    sec_pr = None
    ctrl = None
    if first_p is not None:
        run0 = first_p.find(f'{{{ns_hp}}}run')
        if run0 is not None:
            sec_pr = run0.find(f'{{{ns_hp}}}secPr')
            ctrl = run0.find(f'{{{ns_hp}}}ctrl')
            
    # Clear existing paragraphs in root (hs:sec)
    for child in list(root):
        root.remove(child)
        
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

    # P0: Headline (charPr="17" -> 11pt Bold, Hancom YoonGothic 740)
    p0 = make_p("0", "0")
    run_sec = ET.SubElement(p0, f'{{{ns_hp}}}run', {'charPrIDRef': '17'})
    if sec_pr is not None:
        run_sec.append(sec_pr)
    if ctrl is not None:
        run_sec.append(ctrl)
    p0.append(make_run("17", headline))
    root.append(p0)
    
    # P1: Empty line
    p1 = make_p("0", "0")
    p1.append(make_run("6"))
    root.append(p1)
    
    # P2: Subtitle 1 (11pt Bold)
    p2 = make_p("0", "0")
    p2.append(make_run("17", sub1))
    root.append(p2)
    
    # P3: Subtitle 2 (11pt Bold)
    p3 = make_p("0", "0")
    p3.append(make_run("17", sub2))
    root.append(p3)
    
    # P4: Empty line
    p4 = make_p("0", "0")
    p4.append(make_run("6"))
    root.append(p4)
    
    # Body Paragraphs with 1 blank line between paragraphs
    # charPr="6" -> 11pt Normal, Hancom YoonGothic 740, lineSpacing=160% (paraPr="0")
    for para in paragraphs:
        p_body = make_p("0", "0")
        p_body.append(make_run("6", para))
        root.append(p_body)
        
        p_blank = make_p("0", "0")
        p_blank.append(make_run("6"))
        root.append(p_blank)
        
    # Byline (paraPr="20" -> Right Align, charPr="16" -> 9.5pt Normal)
    p_byline = make_p("20", "0")
    p_byline.append(make_run("16", byline))
    root.append(p_byline)
    
    # Final blank line
    p_final = make_p("0", "0")
    p_final.append(make_run("6"))
    root.append(p_final)
    
    # Save section0.xml
    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hs', ns_hs)
    ET.register_namespace('hc', ns_hc)
    ET.register_namespace('hh', ns_hh)
    ET.register_namespace('hpf', ns_hpf)
    tree.write(sec0_path, encoding='utf-8', xml_declaration=True)
    
    # Update Preview/PrvText.txt
    prv_text_path = os.path.join(temp_dir, 'Preview', 'PrvText.txt')
    if os.path.exists(prv_text_path):
        preview_text = f"{headline}\n\n{sub1}\n{sub2}\n\n" + "\n\n".join(paragraphs) + f"\n\n{byline}\n"
        with open(prv_text_path, 'w', encoding='utf-8') as pf:
            pf.write(preview_text)
            
    # Repackage to HWPX (OCF standard: mimetype stored uncompressed first)
    with zipfile.ZipFile(output_hwpx, 'w') as zout:
        mimetype_path = os.path.join(temp_dir, 'mimetype')
        if os.path.exists(mimetype_path):
            zout.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)
        for r_dir, dirs, files in os.walk(temp_dir):
            for file in files:
                full_path = os.path.join(r_dir, file)
                rel_path = os.path.relpath(full_path, temp_dir)
                if rel_path == 'mimetype':
                    continue
                zout.write(full_path, rel_path, compress_type=zipfile.ZIP_DEFLATED)
                
    shutil.rmtree(temp_dir)
    print("HWPX successfully created:", output_hwpx)

if __name__ == '__main__':
    template = r'D:\b\편집 기사\오늘편집\파이튼컬럼\재판의 정당성과 피고인의 방어권 보장.hwpx'
    out_file = r'D:\b\편집 기사\오늘편집\오세훈_서울시장_항소심_무죄_판결_보도기사.hwpx'
    
    headline = "오세훈 서울시장, '여론조사 대납 의혹' 항소심 무죄 선고"
    sub1 = "서울고법 '핵심 증인 진술 번복·신빙성 결여… 범죄 증명 부족'"
    sub2 = "1심 징역형 유죄 뒤집혀… 시장직 상실 위기 벗고 시정 안정성 확보"
    
    paragraphs = [
        "오세훈 서울시장이 정치자금법 위반 혐의로 기소된 이른바 '여론조사 비용 대납 의혹' 사건 항소심에서 무죄를 선고받았다. 서울고등법원 형사7부는 1심 재판부의 벌금 1,000만 원 및 추징금 선고를 파기하고 오 시장에게 무죄를 선고했다. 이에 따라 선출직 공직자 기준 벌금 100만 원 이상의 형이 확정될 경우 시장직을 상실하게 되는 사법적 리스크에서 완전히 벗어나게 되었으며, 함께 기소된 전 서울시 정무부시장과 후원자 역시 전원 무죄 판결을 받았다.",
        "이번 재판의 쟁점은 지난 2021년 4월 서울시장 보궐선거 과정에서 정치브로커 명태균 씨 측에 여론조사를 직접 의뢰하고, 그에 따른 비용을 후원자 김한정 씨가 대신 지급하도록 공모·지시했는지 여부였다. 1심 재판부는 명 씨 등의 진술과 관련 정황을 근거로 유죄를 인정해 벌금형을 선고했으나, 항소심 재판부의 법리적 판단은 정반대였다.",
        "항소심 재판부는 공소사실을 뒷받침하는 핵심 직접 증거인 명태균 씨의 진술 신빙성에 치명적인 결함이 있다고 판단했다. 재판부는 판결문에서 핵심 증인의 진술이 수사 과정과 법정 증언을 거치며 일관되지 못하고 번복되었을 뿐 아니라, 객관적인 물적 증거나 통화 내역 등과 배치되는 정황이 다수 발견되었다고 지적했다. 증인의 진술이 과장되거나 사실관계와 어긋나는 상황에서 이를 유죄의 단초로 삼을 수 없다는 판단이다.",
        "특히 재판부는 오세훈 시장이 구체적으로 특정 여론조사를 지시하거나 대납을 요청했다고 볼 만한 객관적 증거가 합리적 의심을 배제할 정도로 엄격히 입증되지 않았다고 판시했다. 형사재판의 대원칙인 '의심스러울 때는 피고인의 이익으로(In dubio pro reo)'라는 법리가 철저히 준용된 결과다. 심증이나 정치적 의혹 제기만으로는 국가 형벌권을 발동할 수 없으며, 엄격한 증명 책임을 검찰이 다하지 못했다는 점을 분명히 한 결정이다.",
        "무죄 선고 직후 오세훈 시장은 법원의 현명하고 정의로운 판단에 경의를 표하며, 그동안 시정을 신뢰하고 성원해 준 서울시민과 국민 여러분께 머리 숙여 감사를 드린다고 입장을 밝혔다. 아울러 이유 여하를 막론하고 재판 과정으로 인해 시민들께 심려를 끼쳐드린 점에 대해 송구스럽게 생각하며, 앞으로 더욱 무거운 책임감과 신중한 자세로 시정에 매진하겠다고 강조했다.",
        "법조계와 정치권에서는 이번 판결로 서울시 주요 핵심 현안과 역점 사업들이 사법적 불확실성을 털어내고 강력한 추진 동력을 얻게 될 것으로 내다보고 있다. 선출직 단체장의 거취를 둘러싼 정쟁과 불안정성이 조기에 해소되면서 행정의 연속성과 예측 가능성이 한층 공고해질 전망이다. 다만 검찰의 대법원 상고 여부가 변수로 남아 있으나, 사실심인 2심에서 핵심 증언의 신빙성이 완전히 탄핵당한 만큼 법리 판단 중심의 상고심에서도 결과가 뒤집힐 가능성은 희박하다는 것이 중론이다."
    ]
    
    byline = "[2026.10.23 | 앤트뉴스 국내]"
    
    build_hwpx_perfect(template, out_file, headline, sub1, sub2, paragraphs, byline)
