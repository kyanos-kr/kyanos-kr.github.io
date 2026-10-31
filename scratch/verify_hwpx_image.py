import zipfile, os
from PIL import Image

base = r'D:\DATA CENTER\편집 기사\오늘편집'
folders = [
    'PHP 치명적 취약점 PHP2Shell 경보',
    '메타 테슬라 실적 호조에도 AI 투자 부담 주가 급락',
    '북한 권력승계 시나리오 김여정 섭정과 김주애 세습',
    '일론 머스크의 혁신 비전과 제조 주권 철학 분석',
    '일론 머스크 7대 미래 예측과 문명사적 실현 가능성 진단'
]

for f in folders:
    h_path = os.path.join(base, f, f + '.hwpx')
    i_path = os.path.join(base, f, f + '.jpg')
    print("="*40)
    print("Checking:", f)
    with zipfile.ZipFile(h_path, 'r') as z:
        hdr = z.read('Contents/header.xml').decode('utf-8')
        font_ok = '한컴 윤고딕 740' in hdr
        ls_ok = 'value="160"' in hdr
        prv = z.read('Preview/PrvText.txt').decode('utf-8')
        print(f"HWPX - Font OK: {font_ok}, LineSpacing 160 OK: {ls_ok}, PrvText len: {len(prv)}")
    with Image.open(i_path) as im:
        print(f"IMAGE - Size: {im.size}, Format: {im.format}")
