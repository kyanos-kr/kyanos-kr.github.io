# -*- coding: utf-8 -*-
import sys
import io
import re
import zipfile
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

files = [
    r'E:\편집 기사\오늘편집\대규모 긴장 고조가 임박해 이란 군의 경계 태세가 가능한 최고 수준으로 상향 조정되었다.hwpx',
    r'E:\편집 기사\오늘편집\네 노아의방주는 역사적사실.hwpx',
    r'E:\편집 기사\오늘편집\러시아 폐페스트 발병 은폐.hwpx'
]

for p in files:
    print('***********************************************')
    print('FILE:', p)
    with zipfile.ZipFile(p, 'r') as z:
        sec = z.read('Contents/section0.xml').decode('utf-8')
        root = ET.fromstring(sec)
        paragraphs = list(root.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}p'))
        for i, p_elem in enumerate(paragraphs):
            texts = [t.text for t in p_elem.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}t') if t.text]
            line = ''.join(texts).strip()
            # check english words
            words = line.split()
            eng = [w for w in words if re.match(r"^[A-Za-z,'\".-]+$", w)]
            if len(eng) >= 3 and not line.startswith('http'):
                print(f'P{i}: {line}')
