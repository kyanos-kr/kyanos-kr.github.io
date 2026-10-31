import zipfile, os, sys
import xml.etree.ElementTree as ET

files = [
    '긴급 사이버 위협 분석 보고서.hwpx',
    '메타 테슬라 실적 발표 주식 급락.hwpx',
    '북한 권력승계 시나리오 분석 리포트.hwpx',
    '일론 머스크의 혁신적 비전과 핵심 철학 종합 분석.hwpx',
    '핵심 총괄 평가 매트릭스.hwpx'
]

base_dir = r'D:\DATA CENTER\편집 기사\오늘편집'
dump_dir = r'd:\안티그래비티파이튼\scratch\hwpx_dump'
os.makedirs(dump_dir, exist_ok=True)

hp_tag = '{http://www.hancom.co.kr/hwpml/2011/paragraph}'

for f in files:
    path = os.path.join(base_dir, f)
    with zipfile.ZipFile(path, 'r') as z:
        sec = z.read('Contents/section0.xml')
        root = ET.fromstring(sec)
        paras = []
        for p in root.iter(f'{hp_tag}p'):
            p_text = ''.join(t.text for t in p.iter(f'{hp_tag}t') if t.text)
            if p_text.strip():
                paras.append(p_text.strip())
        out_name = os.path.splitext(f)[0] + '_full.txt'
        out_path = os.path.join(dump_dir, out_name)
        with open(out_path, 'w', encoding='utf-8') as out:
            out.write('\n\n'.join(paras))
        print(f'Done {f}: {len(paras)} paragraphs, saved to {out_name}')
