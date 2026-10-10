# -*- coding: utf-8 -*-
import sys
import io
import zipfile
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ref_path = r'E:\RPT DB\보도 기사 정보\1마이클스나이더\프랑스 연료 부족 위기에 처함.hwpx'
with zipfile.ZipFile(ref_path, 'r') as z:
    hdr_ref = z.read('Contents/header.xml').decode('utf-8')
    print("Reference header len:", len(hdr_ref))
    
target_path = r'E:\편집 기사\오늘편집\네 노아의방주는 역사적사실.hwpx'
with zipfile.ZipFile(target_path, 'r') as z:
    hdr_target = z.read('Contents/header.xml').decode('utf-8')
    print("Target header len:", len(hdr_target))

# Check fontface in reference header
root = ET.fromstring(hdr_ref)
for ff in root.iter('{http://www.hancom.co.kr/hwpml/2011/head}fontface'):
    fonts = [f.attrib.get('face') for f in ff.iter('{http://www.hancom.co.kr/hwpml/2011/head}font')]
    print("Ref fontface:", ff.attrib.get('lang'), fonts)
    break
