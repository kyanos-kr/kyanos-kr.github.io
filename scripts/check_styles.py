# -*- coding: utf-8 -*-
import sys
import io
import os
import zipfile
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ref_path = r'E:\RPT DB\보도 기사 정보\1마이클스나이더\프랑스 연료 부족 위기에 처함.hwpx'
with zipfile.ZipFile(ref_path, 'r') as z:
    hdr_xml = z.read('Contents/header.xml').decode('utf-8')

root = ET.fromstring(hdr_xml)
print("=== Ref charPr summary ===")
for c in root.iter('{http://www.hancom.co.kr/hwpml/2011/head}charPr'):
    cid = c.attrib.get('id')
    h = c.attrib.get('height')
    fref = list(c.iter('{http://www.hancom.co.kr/hwpml/2011/head}fontRef'))
    f_val = fref[0].attrib if fref else {}
    print(f"charPr {cid}: height={h}, fontRef={f_val.get('hangul')}")

print("=== Ref paraPr summary ===")
for p in root.iter('{http://www.hancom.co.kr/hwpml/2011/head}paraPr'):
    pid = p.attrib.get('id')
    lsp = list(p.iter('{http://www.hancom.co.kr/hwpml/2011/head}lineSpacing'))
    lsp_val = lsp[0].attrib.get('value') if lsp else None
    align = list(p.iter('{http://www.hancom.co.kr/hwpml/2011/head}align'))
    align_val = align[0].attrib.get('horizontal') if align else None
    print(f"paraPr {pid}: align={align_val}, lineSpacing={lsp_val}")
