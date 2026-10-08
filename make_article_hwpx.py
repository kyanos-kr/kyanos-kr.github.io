import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

def build_hwpx(template_hwpx_path, output_hwpx_path, headline, sub1, sub2, paragraphs, byline):
    # Create temp directory
    temp_dir = r'd:\안티그래비티파이튼\temp_hwpx'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Extract template
    with zipfile.ZipFile(template_hwpx_path, 'r') as z:
        z.extractall(temp_dir)
        
    # Read section0.xml to preserve secPr and namespaces
    sec0_path = os.path.join(temp_dir, 'Contents', 'section0.xml')
    tree = ET.parse(sec0_path)
    root = tree.getroot()
    
    # Hancom namespaces
    ns_hp = "http://www.hancom.co.kr/hwpml/2011/paragraph"
    ns_hs = "http://www.hancom.co.kr/hwpml/2011/section"
    
    # Find secPr in original first paragraph
    first_p = root.find(f'{{{ns_hp}}}p')
    sec_pr = None
    if first_p is not None:
        run0 = first_p.find(f'{{{ns_hp}}}run')
        if run0 is not None:
            sec_pr = run0.find(f'{{{ns_hp}}}secPr')
            ctrl = run0.find(f'{{{ns_hp}}}ctrl')
            
    # Clear children of root (hs:sec)
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

    def make_run(charPrIDRef="7", text=None):
        r = ET.Element(f'{{{ns_hp}}}run', {'charPrIDRef': str(charPrIDRef)})
        if text is not None:
            t = ET.SubElement(r, f'{{{ns_hp}}}t')
            t.text = text
        return r

    # P0: Headline
    p0 = make_p("0", "0")
    # Add secPr and ctrl in the first run if available
    run_sec = ET.SubElement(p0, f'{{{ns_hp}}}run', {'charPrIDRef': '7'})
    if sec_pr is not None:
        run_sec.append(sec_pr)
    if ctrl is not None:
        run_sec.append(ctrl)
    # Text run for headline
    p0.append(make_run("7", headline))
    root.append(p0)
    
    # P1: Empty line
    p1 = make_p("0", "0")
    p1.append(make_run("7"))
    root.append(p1)
    
    # P2: Subtitle 1
    p2 = make_p("0", "0")
    p2.append(make_run("7", sub1))
    root.append(p2)
    
    # P3: Subtitle 2
    p3 = make_p("0", "0")
    p3.append(make_run("7", sub2))
    root.append(p3)
    
    # P4: Empty line
    p4 = make_p("0", "0")
    p4.append(make_run("7"))
    root.append(p4)
    
    # Paragraphs with blank line in between
    for para_text in paragraphs:
        p_body = make_p("0", "0")
        p_body.append(make_run("7", para_text))
        root.append(p_body)
        
        # empty line
        p_empty = make_p("0", "0")
        p_empty.append(make_run("7"))
        root.append(p_empty)
        
    # Byline (paraPrIDRef="20" is RIGHT align)
    p_byline = make_p("20", "0")
    p_byline.append(make_run("7", byline))
    root.append(p_byline)
    
    # Final empty line
    p_final = make_p("0", "0")
    p_final.append(make_run("7"))
    root.append(p_final)
    
    # Write back section0.xml
    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hs', ns_hs)
    ET.register_namespace('hc', "http://www.hancom.co.kr/hwpml/2011/core")
    ET.register_namespace('hh', "http://www.hancom.co.kr/hwpml/2011/head")
    ET.register_namespace('hpf', "http://www.hancom.co.kr/schema/2011/hpf")
    tree.write(sec0_path, encoding='utf-8', xml_declaration=True)
    
    # Also update Preview/PrvText.txt if exists
    prv_text_path = os.path.join(temp_dir, 'Preview', 'PrvText.txt')
    if os.path.exists(prv_text_path):
        preview_content = f"{headline}\n\n{sub1}\n{sub2}\n\n" + "\n\n".join(paragraphs) + f"\n\n{byline}\n"
        with open(prv_text_path, 'w', encoding='utf-8') as pf:
            pf.write(preview_content)
            
    # Zip back into hwpx
    # Note: 'mimetype' MUST be the first file and uncompressed in HWPX / OCF standard
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
                
    # Clean up temp
    shutil.rmtree(temp_dir)
    print("HWPX successfully created:", output_hwpx_path)

if __name__ == '__main__':
    template = r'E:\RPT DB\보도 기사 정보\중국산공유기백도어발결\중국산공유기백도어발견.hwpx'
    out = r'd:\안티그래비티파이튼\test_output.hwpx'
    headline = '파라마운트, 워너·CNN 인수… 거대 미디어 공룡 탄생'
    sub1 = '1110억弗 반독점 소송 종결… 154조 원 빅딜 확정'
    sub2 = 'HBO·CBS·DC 결집… 2억 구독자로 넷플릭스 정조준'
    body = [
        "파라마운트-스카이댄스 그룹이 워너브라더스 디스커버리(WBD) 인수를 전격 확정하며 세계 최대 규모의 미디어 제국으로 재탄생했다. 미국 12개 주가 제기했던 반독점 소송이 전격 합의로 종결되면서 총 1,110억 달러(한화 약 154조 원)에 달하는 세기의 초대형 인수합병(M&A) 거래가 최종 궤도에 올랐다. 이번 합병으로 글로벌 보도 부문의 대표 주자인 CNN은 물론 HBO, DC 코믹스, 디스커버리 채널, 지상파 방송 CBS 등 세계 문화·보도 산업을 주도해온 핵심 자산들이 파라마운트 단일 우산 아래 집결하게 됐다.",
        "데이비드 엘리슨 최고경영자(CEO)가 이끄는 파라마운트-스카이댄스 그룹은 이번 합병을 통해 전통적인 레거시 미디어와 최첨단 스트리밍 생태계를 아우르는 압도적인 콘텐츠 포트폴리오를 거머쥐게 됐다. 영화 분야에서는 파라마운트의 간판 프랜차이즈인 '미션 임파서블'과 '탑건'에 워너브라더스의 글로벌 지식재산권(IP)인 '해리포터'와 'DC 유니버스'가 결합한다. 방송 및 드라마 영역 역시 '소프라노스'를 비롯한 명품 콘텐츠를 보유한 HBO 오리지널 시리즈와 CBS의 폭넓은 지상파 네트워크가 한데 묶여 전례 없는 시너지를 예고하고 있다.",
        "특히 글로벌 온라인 동영상 서비스(OTT) 시장에서의 지각변동이 불가피할 전망이다. 통합 법인은 기존의 파라마운트 플러스(Paramount+)와 HBO 맥스(Max)의 플랫폼 및 가입자 기반을 연계하여 단숨에 2억 명 이상의 글로벌 유료 구독 군단을 확보하게 된다. 이는 현재 시장을 양분하고 있는 넷플릭스와 디즈니 플러스를 정조준하는 강력한 대항마가 출현했음을 의미하며, 향후 글로벌 콘텐츠 유통 플랫폼의 세력 판도를 근본적으로 재편할 것으로 관측된다.",
        "이번 빅딜에서 가장 뜨거운 쟁점 중 하나였던 보도 부문 재편과 관련해, 파라마운트는 CNN을 CBS 뉴스와 함께 산하 조직으로 편입하되 저널리즘의 공정성을 담보하기 위한 강력한 장치를 마련하기로 합의했다. 규제 당국 및 주 정부와의 합의안에 따라 양사에는 독립적인 외부 편집위원회가 공식 설치되며, 편집권의 전권을 보장받게 된다. 보도 인력 및 네트워크 운영의 부분적 통합 가능성은 열려 있으나, 상업적 압력이나 모기업의 입김으로부터 취재 현장을 보호하겠다는 취지다. 아울러 디지털 뉴스 서비스인 'CNN 올 액세스(All Access)'를 통합 스트리밍 플랫폼에 연동하는 방안도 유력하게 검토되고 있다.",
        "한편 이번 합병 인가 과정에서는 콘텐츠 생태계 보호를 위한 엄격한 조건들도 부과됐다. 파라마운트-스카이댄스는 독과점에 따른 창작 생태계 위축 우려를 해소하기 위해 향후 5년간 매년 3억 달러 이상, 총 15억 달러(한화 약 2조 원) 규모의 미국 내 영화 제작 투자를 공식 집행해야 한다. 또한 극장 상영 영화를 매년 30편 이상 의무적으로 제작·개봉해야 하며, 미달 시 거액의 벌금이 부과된다. 아울러 파업과 제작비 축소로 타격을 입은 헐리우드 엔터테인먼트 종사자들을 위한 별도의 상생 지원 기금도 조성된다.",
        "업계 전문가들은 이번 거래가 글로벌 콘텐츠 패권 경쟁에서 막강한 규모의 경제를 실현할 것이라는 점에는 동의하면서도, 과거 대형 미디어 합병 사례들이 겪었던 통합 실패의 함정을 경계해야 한다고 지적한다. 막대한 부채 부담과 이질적인 기업 문화 융합, 조직 개편에 따른 구조조정 통증이 수반될 수밖에 없기 때문이다. 나아가 세계적인 영향력을 지닌 CNN의 논조가 거대 자본의 이해관계 속에서 온전히 독립성을 지켜낼 수 있을지에 대한 언론계의 감시와 우려도 여전히 현재진행형이다. 세계 미디어 역사의 새로운 장을 연 이번 1,110억 달러의 결단이 글로벌 문화 패권의 재편을 알리는 승부수가 될지, 혹은 비대한 공룡의 난제로 귀결될지 전 세계 문화·금융 시장의 시선이 집중되고 있다."
    ]
    byline = "앤트뉴스 국제부"
    build_hwpx(template, out, headline, sub1, sub2, body, byline)
