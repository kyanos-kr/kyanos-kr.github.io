import os
import sys
import shutil
import zipfile
from PIL import Image
import xml.etree.ElementTree as ET

TEMPLATE_PATH = r'D:\DATA CENTER\RPT DB\보도 기사 정보\AI 에이전트 통제 불능 위험\AI 에이전트 통제 불능 위험.hwpx'
TARGET_DIR = r'D:\DATA CENTER\편집 기사\오늘편집\임시폴더\백일맞은 스틸미대사 소회'
ORIGIN_DIR = r'D:\DATA CENTER\편집 기사\오늘편집\기사\백일맞은 스틸미대사 소회'

os.makedirs(TARGET_DIR, exist_ok=True)
output_hwpx_path = os.path.join(TARGET_DIR, '백일맞은 스틸미대사 소회.hwpx')
temp_dir = os.path.join(TARGET_DIR, '_temp_hwpx_build')

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir, exist_ok=True)

with zipfile.ZipFile(TEMPLATE_PATH, 'r') as z:
    z.extractall(temp_dir)

# 1. Update header.xml
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

def make_p(paraPrIDRef='0', styleIDRef='0'):
    global p_id_counter
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

headline = '미셸 박 스틸 주한미국대사, 취임 백일 맞아 동맹 현대화와 신뢰 강조'
sub1 = '— 한미동맹의 핵심은 상호 신뢰와 실천… 미래 세대를 위한 안보 환경 구축 천명'
sub2 = '— 조선·배터리·원전 등 전략산업 협력 견인 및 국방비 증액과 특별법 입법 촉구'

paragraphs = [
    '취임 100일을 맞은 미셸 박 스틸(Michelle Park Steel) 주한미국대사가 주한미국대사관 공식 대담 프로그램과 소셜미디어 채널을 통해 그간의 외교 성과를 짚어보고 향후 동맹 발전의 중점 청사진을 제시했다. 스틸 대사는 부임 이후 100일간 숨 가쁘게 전개된 한국 각계 인사들과의 현장 교류를 회고하며, 전통적 안보 결속을 넘어 미래 첨단 산업과 글로벌 공급망을 아우르는 동맹의 포괄적 진화를 역설했다.',
    '스틸 대사는 이번 소회 발표에서 향후 임기 중 완수할 3대 핵심 국정·외교 과제로 △한미동맹의 현대화 △양국 경제적 기회 및 상호 투자 확대 △인도·태평양 역내 복합 위기 대응을 위한 공조 체계 강화를 천명했다. 그는 이러한 과제들이 성공적으로 안착하기 위한 절대적 전제조건으로 "신뢰와 소통"을 꼽으며, "동맹의 진정한 가치는 가장 중대한 위기의 순간에 서로를 의심 없이 믿을 수 있는가에 달려 있다"고 강조했다.',
    '이어 스틸 대사는 "양국은 상호 간에 맺은 합의와 약속을 성실히 이행해야 하며, 민감하고 복잡한 외교 현안일수록 투명하고 책임감 있게 다루어 동맹의 근간인 상호 신뢰를 흔들림 없이 수호해야 한다"고 역설했다. 아울러 동맹의 궁극적 지향점은 한미 양국 국민의 생명과 재산을 안전하게 보호하고, 다음 세대가 희망찬 미래를 자유롭게 설계할 수 있는 항구적 평화 안보 환경을 확립하는 데 있다고 밝혔다.',
    '경제 및 글로벌 공급망 협력 분야에서는 한국 기업들의 적극적인 대미 투자가 양국 경제 모두에 중대한 시너지를 창출하는 상호 호혜적 결실을 맺고 있다고 높이 평가했다. 특히 현재 미국 내에서 국가적 과제로 추진 중인 조선산업 제조 역량 재건 프로젝트와 관련해 "세계 최고 수준의 선박 건조 및 도크 운영 기술력을 보유한 한국 조선업계의 전문성이 결정적 역할을 수행할 수 있다"며, 양국 협력이 미 현지 조선소 경쟁력 제고와 한국 기업의 글로벌 사업 확대를 동시에 견인할 것임을 분명히 했다.',
    '에너지 안보와 첨단 테크 공급망의 핵심 축인 배터리 및 원자력 분야의 협력 확대 역시 중점 과제로 제시됐다. LG에너지솔루션과 삼성SDI 등 한국 대표 기업들의 미국 내 기가팩토리 투자를 대표적 상생 사례로 거론한 스틸 대사는 "에너지 저장 수요 확대가 양국 산업계와 근로자들에게 막대한 경제적 기회를 제공하고 있다"고 분석했다. 또한 원자력 분야에서도 미국의 독보적인 원자로 설계·기초기술 역량과 한국의 탁월한 기자재 제작·시공 능력이 결합될 경우 글로벌 원전 르네상스를 선도할 최상의 조합이 될 것이라며, 차세대 소형모듈원자로(SMR) 상용화 공조에 큰 기대감을 표명했다.',
    '한편 스틸 대사는 동맹의 질적 도약을 뒷받침하기 위한 한국 측의 책임 있는 역할과 제도적 지원의 중요성도 피력했다. 한국 기업들의 대규모 대미 투자가 예측 가능한 제도적 안정성 속에서 연속성을 확보하기 위해 국회 차원의 대미 투자 특별법 제정 등 입법적 뒷받침이 긴요함을 강조하는 한편, 한국 내 진출한 미국 기업들이 차별 없는 환경에서 공정하게 경쟁할 수 있는 시장 여건 조성을 당부했다. 아울러 한국이 GDP 대비 국방비를 3.5% 수준까지 단계적으로 현실화하겠다는 중장기 안보 약속을 차질 없이 추진함으로써, 한반도를 넘어 인도·태평양의 평화와 안정을 함께 견인하는 주도적 글로벌 안보 파트너로 확고히 자리매김해 줄 것을 촉구했다.'
]

byline = '앤트뉴스 보도국 종합브리핑룸'

# Headline
p0 = make_p('0', '0')
run_sec = ET.SubElement(p0, f'{{{ns_hp}}}run', {'charPrIDRef': '7'})
if sec_pr is not None:
    run_sec.append(sec_pr)
if ctrl is not None:
    run_sec.append(ctrl)
t0 = ET.SubElement(run_sec, f'{{{ns_hp}}}t')
t0.text = headline
root_sec.append(p0)

# Blank
p_sp1 = make_p('0', '0')
p_sp1.append(make_run('7'))
root_sec.append(p_sp1)

# Sub 1
p_sub1 = make_p('0', '0')
p_sub1.append(make_run('7', sub1))
root_sec.append(p_sub1)

# Sub 2
p_sub2 = make_p('0', '0')
p_sub2.append(make_run('7', sub2))
root_sec.append(p_sub2)

# Blank
p_sp2 = make_p('0', '0')
p_sp2.append(make_run('9'))
root_sec.append(p_sp2)

# Body
preview_paras = []
for para_text in paragraphs:
    p_body = make_p('0', '0')
    p_body.append(make_run('9', para_text.strip()))
    root_sec.append(p_body)
    
    p_empty = make_p('0', '0')
    p_empty.append(make_run('9'))
    root_sec.append(p_empty)
    preview_paras.append(para_text.strip())

# Byline
p_by = make_p('20', '0')
p_by.append(make_run('8', byline))
root_sec.append(p_by)

# End blank
p_end = make_p('0', '0')
p_end.append(make_run('9'))
root_sec.append(p_end)

ET.register_namespace('hp', ns_hp)
ET.register_namespace('hs', ns_hs)
ET.register_namespace('hc', ns_core)
ET.register_namespace('hh', ns_hh)
tree_sec.write(sec_path, encoding='utf-8', xml_declaration=True)

# PrvText
prv_text_path = os.path.join(temp_dir, 'Preview', 'PrvText.txt')
if os.path.exists(prv_text_path):
    preview_content = f'{headline}\n\n{sub1}\n{sub2}\n\n' + '\n\n'.join(preview_paras) + f'\n\n{byline}\n'
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
print('Successfully created HWPX:', output_hwpx_path)

# Image Packaging: 1:1 package
src_img_path = os.path.join(ORIGIN_DIR, '페북캡처.jpg')
tgt_img_path = os.path.join(TARGET_DIR, '백일맞은 스틸미대사 소회.jpg')
shutil.copy2(src_img_path, tgt_img_path)
print('Copied and matched image:', tgt_img_path)

# Origin folder backup under TARGET_DIR
raw_backup_dir = os.path.join(TARGET_DIR, '원본_백일맞은 스틸미대사 소회')
os.makedirs(raw_backup_dir, exist_ok=True)
for fname in os.listdir(ORIGIN_DIR):
    s = os.path.join(ORIGIN_DIR, fname)
    d = os.path.join(raw_backup_dir, fname)
    if os.path.isfile(s):
        shutil.copy2(s, d)
print('Archived raw origin files into:', raw_backup_dir)

# Clean up origin folder in 오늘편집>기사
shutil.rmtree(ORIGIN_DIR)
print('Cleaned up origin folder from 오늘편집>기사')
