import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

def build_hwpx(template_hwpx_path, output_hwpx_path, headline, sub1, sub2, paragraphs, byline):
    temp_dir = r'd:\안티그래비티파이튼\temp_hwpx_elon'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    with zipfile.ZipFile(template_hwpx_path, 'r') as z:
        z.extractall(temp_dir)
        
    sec0_path = os.path.join(temp_dir, 'Contents', 'section0.xml')
    tree = ET.parse(sec0_path)
    root = tree.getroot()
    
    ns_hp = "http://www.hancom.co.kr/hwpml/2011/paragraph"
    ns_hs = "http://www.hancom.co.kr/hwpml/2011/section"
    
    first_p = root.find(f'{{{ns_hp}}}p')
    sec_pr = None
    ctrl = None
    if first_p is not None:
        run0 = first_p.find(f'{{{ns_hp}}}run')
        if run0 is not None:
            sec_pr = run0.find(f'{{{ns_hp}}}secPr')
            ctrl = run0.find(f'{{{ns_hp}}}ctrl')
            
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
    run_sec = ET.SubElement(p0, f'{{{ns_hp}}}run', {'charPrIDRef': '7'})
    if sec_pr is not None:
        run_sec.append(sec_pr)
    if ctrl is not None:
        run_sec.append(ctrl)
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
    
    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hs', ns_hs)
    ET.register_namespace('hc', "http://www.hancom.co.kr/hwpml/2011/core")
    ET.register_namespace('hh', "http://www.hancom.co.kr/hwpml/2011/head")
    ET.register_namespace('hpf', "http://www.hancom.co.kr/schema/2011/hpf")
    tree.write(sec0_path, encoding='utf-8', xml_declaration=True)
    
    prv_text_path = os.path.join(temp_dir, 'Preview', 'PrvText.txt')
    if os.path.exists(prv_text_path):
        preview_content = f"{headline}\n\n{sub1}\n{sub2}\n\n" + "\n\n".join(paragraphs) + f"\n\n{byline}\n"
        with open(prv_text_path, 'w', encoding='utf-8') as pf:
            pf.write(preview_content)
            
    os.makedirs(os.path.dirname(output_hwpx_path), exist_ok=True)
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
    print("HWPX successfully created at:", output_hwpx_path)

if __name__ == '__main__':
    template = r'D:\b\RPT DB\보도 기사 정보\중국산공유기백도어발결\중국산공유기백도어발견.hwpx'
    out = r'D:\b\편집 기사\오늘편집\일론머스크_미래예측7가지_내면의진실과_실현가능성_심층리포트.hwpx'
    
    headline = "머스크가 예고한 7대 미래… 문명적 도약인가 자본의 환상인가"
    sub1 = "AGI·로봇·화성·BCI 등 7대 예측 심층 분석"
    sub2 = "제1원칙 비전 뒤편의 공학적 한계와 경제적 진실"
    
    body = [
        "일론 머스크 테슬라·스페이스X 최고경영자(CEO)가 제시한 미래 문명의 7대 예측이 글로벌 테크 생태계와 금융 시장에 거대한 파장을 일으키고 있다. 노동의 종말과 보편적 고소득(UHI), 인간 지능 총합을 능가하는 초지능(AGI/ASI)의 조기 도래, 3~5년 내 최고 외과의를 능가하는 자율 로봇 수술, 인구보다 많은 100억~200억 대 휴머노이드 보급, 초디플레이션에 의한 저축의 무의미화, 화성 자립 도시를 통한 다행성 인류 문명, 그리고 뉴럴링크를 통한 뇌-컴퓨터 융합이 그 핵심 축이다. 머스크의 미래학은 단순한 공상과학적 상상이 아니라 물리 법칙과 컴퓨팅 지수를 근거로 제시되지만, 그 내면에는 기업가치 부양을 위한 자본주의적 서사와 현실 공학·제도적 장벽이 날카롭게 맞서고 있다.",
        
        "첫째, '10~20년 내 노동의 종말과 일의 선택화' 예측은 테슬라를 단순 전기차 제조사에서 전 세계 노동력을 대체할 궁극의 AI·로보틱스 독점 플랫폼으로 포장하기 위한 핵심 내러티브다. 재화와 서비스의 한계생산비용이 0에 수렴하여 모든 인류가 보편적 고소득(UHI)을 누린다는 장밋빛 전망은 자본주의의 소유 구조를 간과한 측면이 크다. 노동 소멸 시 부의 원천은 AI와 로봇 인프라를 독점한 극소수 테크 과두제(Oligarchy)로 100% 집중된다. 이를 강제 회수해 국민에게 배분할 초국가적 조세 제도나 사회적 합의가 결여된다면, 인류는 풍요가 아닌 전례 없는 부의 양극화와 '잉여 계급'의 소외로 전락할 위험이 크다. 비정형 환경 대응과 윤리적 책무 영역을 감안할 때 20년 내 완전 실현 가능성은 30% 수준에 머문다.",
        
        "둘째, '2029년 인간 총합을 능가하는 초지능(AGI/ASI) 도래' 예측은 xAI의 슈퍼컴퓨터 '콜로서스(Colossus)' 투자 유치 및 막대한 엔비디아 칩셋 확보를 정당화하는 '스케일링 법칙(Scaling Law)'의 산물이다. 특정 수학, 코딩, 데이터 분석 영역에서는 이미 인간의 지성을 압도하는 성과가 나타나고 있어 부분적 실현 가능성은 50%에 이른다. 그러나 거대언어모델(LLM)의 고질적 환각(Hallucination), 고품질 학습 데이터의 고갈, 무엇보다 초지능 데이터센터를 감당할 수 없는 글로벌 전력망과 변압기, 냉각 용수 등 '물리적 인프라의 병목'이 2029년 완전 범용 초지능 출현을 가로막는 절대적 한계선으로 작용하고 있다.",
        
        "셋째, '3~5년 내 인간 최고의 외과 의사를 능가하는 로봇 수술' 예측은 테슬라 옵티머스의 액추에이터 정밀도와 비전 AI를 과시하기 위한 마케팅적 수사에 가깝다. 현재 다빈치 등 수술 로봇은 숙련된 외과의의 손동작을 100% 원격 전달하는 정밀 도구일 뿐, 독자적 판단으로 메스를 대지 않는다. 수술 중 예기치 않은 출혈, 연부 조직(Soft tissue)의 비선형적 변형, 환자별 해부학적 이형성에 대한 직관적 대처는 완전 자율 AI가 수년 내 감당하기 불가능하다. 의료사고 시의 법적 책임(Liability)과 미국 FDA 등 글로벌 규제 당국의 보수적 임상 승인 절차를 고려할 때 3~5년 내 실현 가능성은 15% 미만으로 극히 희박하다.",
        
        "넷째, '인간 인구보다 많은 100억~200억 대 휴머노이드 로봇 시대'는 전기차 수요 정체(캐즘)를 돌파하고 테슬라 시가총액을 수십조 달러로 재평가받기 위한 승부수다. 대당 2만~3만 달러 수준의 보급형 로봇 비전은 장기적 방향성(40% 가능성)을 지니고 있으나 시점은 대폭 지연될 공산이 크다. 현재 2~4시간에 불과한 배터리 지속 시간, 장시간 가동 시 모터 발열 및 감속기 마모, 희토류 공급망 병목, 예측 불가능한 돌발 상황에서의 실시간 동역학 제어 기술이 미완이다. 2030년대 중반까지는 인간을 완전히 대체하기보다, 통제된 스마트 팩토리와 물류 창고에 수십만~수백만 대 수준으로 배치되는 것이 현실적 궤도다.",
        
        "다섯째, '초디플레이션으로 인한 저축 및 은퇴 자금의 무의미화'는 기술 결정론이 낳은 경제학적 착시다. 한계생산비용이 0에 수렴해 공산품과 정보 재화의 가격이 폭락하더라도, 인간의 근원적 욕망이 투사되는 토지, 주거 공간, 청정 에너지, 고성능 연산 자원과 같은 '물리적 희소 자산'은 오히려 천문학적 프리미엄을 형성한다. 화폐가 사라지는 것이 아니라, 로봇과 AI 지분을 소유하지 못한 일반 대중의 실질 구매력이 박탈되는 디스토피아가 전개될 수 있다. 저축이 불필요해지는 것이 아니라 전통적 현금 저축의 효용이 급락하고 실물 자산과 테크 지분의 독점적 보유가 생존의 절대 조건이 될 가능성이 높아 실현 가능성은 20%에 그친다.",
        
        "여섯째, '20~30년 내 100만 명 화성 자립 도시 건설'은 머스크의 가장 순수한 원초적 소명이자 스페이스X 스타십 프로젝트와 스타링크 상장의 거대한 자금 조달 명분이다. 스타십을 통한 무인 화성 착륙과 2030년대 소규모 유인 탐사 기지 건설은 70% 이상의 높은 공학적 실현 가능성을 자랑한다. 그러나 100만 명이 자급자족하는 거대 문명 건설은 차원이 다른 문제다. 지구의 38%에 불과한 저중력으로 인한 골밀도·심혈관계 영구 손상, 대기권 부재로 인한 치명적 우주 방사선, 완전 폐쇄형 인공 생태계(CELSS) 구축의 실패 위험, 테라포밍의 물리적 불가능성을 감안할 때 30년 내 자립 도시 실현 가능성은 25% 미만이다.",
        
        "일곱째, '뉴럴링크 뇌-컴퓨터 인터페이스(BCI)를 통한 초지능과의 공생'은 인간의 정보 입출력 대역폭 한계(초당 수십 바이트)를 돌파해 인류가 AI의 애완동물로 전락하는 것을 막겠다는 철학적 결단이다. 사지 마비 환자의 전자기기 제어, 시각 복원, 척수 손상 극복 등 의료 재활 목적의 기술적 성과는 이미 가시화되어 실현 가능성이 85%에 달한다. 그러나 수천 개 전극을 두개골에 삽입하는 침습적 방식으로는 860억 개 뉴런과 수백조 개 시냅스가 빚어내는 고차원 의식, 기억, 정서, 직관을 해독·동기화할 수 없다. 뇌과학의 근본적 돌파구 없이 AI와의 전뇌 융합이나 디지털 불멸을 단기간에 달성하는 것은 요원하다.",
        
        "결론적으로 일론 머스크의 7대 미래 예측은 '물리학 법칙에 위배되지 않는다면 반드시 현실화된다'는 제1원칙 환원주의와, 불가능한 시한을 내걸어 인재와 천문학적 자본을 빨아들이는 '머스크 타임'의 결합체다. 그의 예언은 100% 적중하지 않더라도, 기술 혁신의 이정표를 앞당기고 전 지구적 산업의 표준을 강제 재편하는 '자기실현적 예언'으로 기능해 왔다. 인류는 머스크가 제시하는 장밋빛 기술 유토피아에 무비판적으로 경도되거나 허황된 사기극으로 치부하는 양극단을 경계해야 한다. 그가 던진 7대 화두의 내면적 자본 논리를 냉철히 꿰뚫어 보면서, 초지능과 피지컬 로봇이 가져올 문명적 지각변동에 대비한 경제·사회적 안전망과 규범 체계를 선제적으로 구축하는 혜안이 절실하다."
    ]
    
    byline = "앤트뉴스 미래기술 심층분석팀"
    
    build_hwpx(template, out, headline, sub1, sub2, body, byline)
