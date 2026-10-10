# -*- coding: utf-8 -*-
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import glob
import zipfile
import xml.etree.ElementTree as ET

source_dir = r"E:\편집 기사\오늘편집"
dest_dir = r"E:\RPT DB\보도 기사 정보\1마이클스나이더"

files = glob.glob(os.path.join(source_dir, "*.hwpx"))
print(f"Found {len(files)} files in {source_dir}")
for f in files:
    print(" -", os.path.basename(f))
