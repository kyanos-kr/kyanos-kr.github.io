# -*- coding: utf-8 -*-
import sys
import io
import os
import zipfile
import re
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ref_path = r'E:\RPT DB\보도 기사 정보\1마이클스나이더\프랑스 연료 부족 위기에 처함.hwpx'
with zipfile.ZipFile(ref_path, 'r') as z:
    hdr_xml = z.read('Contents/header.xml')

articles = [
    {
        'key': 'fuel',
        'raw_txt': r'd:\안티그래비티파이튼\키아노스_정부부처\07_국제부\스나이더_번역원문\fuel.txt',
        'base_hwpx': r'E:\편집 기사\오늘편집\전 세계 연료 시위 발생.hwpx',
        'out_name': '전 세계 연료 시위 발생_수정본.hwpx',
        'orig_title': '전 세계 연료 시위 발생: 시리아 타이어 소각 도로 차단과 연쇄 소요',
        'main_title': '글로벌 유류 대란, 세계 각국 연쇄 폭동',
        'sub_title1': '시리아 도로 차단과 동남아 배급 혼란',
        'sub_title2': '중남미 방화 시위와 치솟는 생계 위기',
        'date_str': '2026년 9월 17일'
    },
    {
        'key': 'nuclear',
        'raw_txt': r'd:\안티그래비티파이튼\키아노스_정부부처\07_국제부\스나이더_번역원문\nuclear.txt',
        'base_hwpx': r'E:\편집 기사\오늘편집\러시아와의 핵전쟁의 유령이 떠오르다.hwpx',
        'out_name': '러시아와의 핵전쟁의 유령이 떠오르다_수정본.hwpx',
        'orig_title': '러시아와의 핵전쟁의 유령이 떠오르다',
        'main_title': '우크라 장거리 공습, 미러 핵충돌 위기',
        'sub_title1': '모스크바 정유소 타격과 전술핵 위협',
        'sub_title2': '나토 직접 참전 경고와 초단기 전쟁론',
        'date_str': '2026년 9월 21일'
    },
    {
        'key': 'houthi',
        'raw_txt': r'd:\안티그래비티파이튼\키아노스_정부부처\07_국제부\스나이더_번역원문\houthi.txt',
        'base_hwpx': r'E:\편집 기사\오늘편집\후티 소탕전 개시.hwpx',
        'out_name': '후티 소탕전 개시_수정본.hwpx',
        'orig_title': '후티 소탕전 개시: 예멘 통제권 탈환을 위한 10만 병력의 새로운 군사 작전',
        'main_title': '예멘 10만 대군 집결, 후티 전면 소탕전',
        'sub_title1': '사우디 공습 지원과 바브엘만데브 탈환',
        'sub_title2': '미국 표적 정보 제공과 이란 개입 경고',
        'date_str': '2026년 10월 5일'
    },
    {
        'key': 'bioweapon',
        'raw_txt': r'd:\안티그래비티파이튼\키아노스_정부부처\07_국제부\스나이더_번역원문\bioweapon.txt',
        'base_hwpx': r'E:\편집 기사\오늘편집\소련은 공격적 생물무기 프로그램을 보유.hwpx',
        'out_name': '소련은 공격적 생물무기 프로그램을 보유_수정본.hwpx',
        'orig_title': '소련은 공격적 생물무기 프로그램을 보유했고, 흑사병을 무기화했다',
        'main_title': '소련 생물무기 악몽, 유전자 변형 흑사병',
        'sub_title1': '바이오프레파라트 비밀 연구와 독소 결합',
        'sub_title2': '이르쿠츠크 사고 의혹과 항생제 무력화 공포',
        'date_str': '2026년 10월 6일'
    }
]

today_edit_dir = r'E:\편집 기사\오늘편집'

def clean_and_convert(text):
    # 1. Strip promo / advert
    if any(k in text for k in ['마이클 스나이더의 서브스택은', '서브스택은 독자 지원 출판물', '구독자가 되는 것을 고려', 'Substack']):
        return None

    # 2. English translations
    translations = [
        ("288 million people live in Indonesia, and it is very heavily dependent on imported oil.",
         "인도네시아에는 2억 8,800만 명이 거주하고 있으며, 수입 석유에 극도로 의존하고 있다."),
        ("They will never, ever lay down their weapons.",
         "그들은 결코 무기를 내려놓지 않을 것이다."),
        ("So there will be no surrender.",
         "따라서 항복이란 없다."),
        ("The Houthis will fight until they are either wiped out or they are victorious.",
         "후티는 전멸하거나 승리할 때까지 싸울 것이다."),
        ("It appears that this will be the biggest conflict in the entire modern history of Yemen.",
         "이는 예멘 현대사 전체에서 가장 거대한 충돌이 될 것으로 보인다."),
        ("It is being reported that over 100,000 soldiers could be mobilized to battle the Houthis…",
         "후티와 맞서 싸우기 위해 10만 명 이상의 병력이 동원될 수 있다는 보도가 나오고 있다..."),
        ("More than 100,000 Yemeni troops could be mobilized in the offensive, depending on the scale, the officials all said.",
         "작전 규모에 따라 10만 명 이상의 예멘 군이 이번 공세에 동원될 수 있다고 당국자들은 일제히 밝혔다.")
    ]
    for en, ko in translations:
        text = text.replace(en, ko)

    # 3. Honorific to plain (해라체)
    rules = [
        (r'불가피할 가능성이 큽니다\.', '불가피할 가능성이 크다.'),
        (r'불평하고 있습니다\.', '불평하고 있다.'),
        (r'격분하고 있습니다\.', '격분하고 있다.'),
        (r'촉발되었습니다\.', '촉발되었다.'),
        (r'도달했습니다\.', '도달했다.'),
        (r'항의했습니다\.', '항의했다.'),
        (r'경고해왔습니다\.', '경고해 왔다.'),
        (r'초래하기 시작했습니다\.', '초래하기 시작했다.'),
        (r'시작되었습니다\.', '시작되었다.'),
        (r'확산되었습니다\.', '확산되었다.'),
        (r'미쳤습니다\.', '미쳤다.'),
        (r'포함되었습니다\.', '포함되었다.'),
        (r'선포했습니다\.', '선포했다.'),
        (r'일으켰습니다\.', '일으켰다.'),
        (r'취했습니다\.', '취했다.'),
        (r'발표했습니다\.', '발표했다.'),
        (r'기다리세요\.', '기다려 보라.'),
        (r'잡으세요,\s*앞으로\s*험난한\s*여정이\s*될\s*테니까요\.', '꽉 잡아야 한다. 앞으로 험난한 여정이 될 것이기 때문이다.'),
        (r'몰고 있기 때문입니다\.', '몰고 있기 때문이다.'),
        (r'밝혔습니다\.', '밝혔다.'),
        (r'감행했습니다\.\.\.', '감행했다...'),
        (r'자랑스러워했습니다\.\.\.', '자랑스러워했다...'),
        (r'들었습니다\.\.\.', '전해 들었다...'),
        (r'차지합니다\.', '차지한다.'),
        (r'야기합니다\.', '야기한다.'),
        (r'아닙니다\.', '아니다.'),
        (r'만든다는 점입니다\.', '만든다는 점이다.'),
        (r'상상해 보시길 바랍니다\.', '상상해 보라.'),
        (r'침공하기도 했습니다\.', '침공하기도 했다.'),
        (r'어떨까요\?', '어떠하겠는가?'),
        (r'원할 것입니다\.', '원할 것이다.'),
        (r'생각하지 않습니다\.', '생각하지 않는다.'),
        (r'잘 모릅니다\.', '잘 모른다.'),
        (r'예상될 수 있습니다\.', '예상될 수 있다.'),
        (r'엄청날 것입니다\.', '엄청날 것이다.'),
        (r'가능성이 큽니다\.', '가능성이 크다.'),
        (r'위험한 게임을 하고 있습니다\.', '위험한 게임을 하고 있다.'),
        (r'정말 그들이 멈췄으면 좋겠어요\.', '정말이지 그들이 멈추기를 바랄 뿐이다.'),
        (r'촉발될 수 있습니다\.', '촉발될 수 있다.'),
        (r'매우 짧을 것입니다\.', '매우 짧을 것이다.'),
        (r'다가간 적은 없습니다\.', '다가간 적은 없다.'),
        (r'계속 파티를 즐깁니다\.', '계속 파티를 즐긴다.'),
        (r'접어들었습니다\.', '접어들었다.'),
        (r'할 것입니다\.', '할 것이다.'),
        (r'뜻입니다\.', '뜻이다.'),
        (r'정반대입니다\.', '정반대이다.'),
        (r'모든 것을 되찾는 것입니다\.', '모든 것을 되찾는 것이다.'),
        (r'거부되었다\.', '거부되었다.'),
        (r'지원할 것입니다\.\.\.', '지원할 것이다...'),
        (r'것으로 보입니다\.\.\.', '것으로 보인다...'),
        (r'높다고 생각합니다\.', '높다고 생각한다.'),
        (r'치명적일 것이다\.', '치명적일 것이다.'),
        (r'느꼈을 것입니다\.', '느꼈을 것이다.'),
        (r'두고 봐야겠죠\.', '두고 볼 일이다.'),
        (r'분명해졌다\.', '분명해졌다.'),
        (r'다가오고 있습니다\.', '다가오고 있다.'),
        (r'유일한 형태입니다\.', '유일한 형태이다.'),
        (r'상상할 수 없을 것입니다\.', '상상할 수 없을 것이다.'),
        (r'주장하고 있습니다\.', '주장하고 있다.'),
        (r'그 정보가 맞길 바랍니다\.', '그 정보가 맞기를 바란다.'),
        (r'말하고 있습니다\.', '말하고 있다.'),
        (r'막을 수 있을까요\?', '막을 수 있겠는가?'),
        (r'보유하고 있었습니다\.', '보유하고 있었다.'),
        (r'운영되었습니다\.\.\.', '운영되었다...'),
        (r'실험을 하고 있었습니다\.', '실험을 하고 있었다.'),
        (r'페스티스였습니다\.', '페스티스였다.'),
        (r'알고 있습니다\.\.\.', '알고 있다...'),
        (r'만드는 것이었습니다\.', '만드는 것이었다.'),
        (r'유기체입니다\.', '유기체이다.'),
        (r'실험하고 있었습니다\.', '실험하고 있었다.'),
        (r'있었습니다\.', '있었다.'),
        (r'삽입했습니다\.', '삽입했다.'),
        (r'불안감을 주었습니다\.', '불안감을 주었다.'),
        (r'유발합니다\.', '유발한다.'),
        (r'제안했습니다\.', '제안했다.'),
        (r'것이었습니다\.', '것이었다.'),
        (r'있게 되었습니다\.', '있게 되었다.'),
        (r'사망할 것입니다\.', '사망할 것이다.'),
        (r'특별히 주목해 주세요\.', '특별히 주목할 필요가 있다.'),
        (r'방어 수단이기 때문입니다\.', '방어 수단이기 때문이다.'),
        (r'주장했습니다\.\.\.', '주장했다...'),
        (r'이루어졌습니다\.', '이루어졌다.'),
        (r'거의 40년 전 일이에요\.', '거의 40년 전 일이다.'),
        (r'진전을 이루었나요\?', '진전을 이루었는가?'),
        (r'상상했다\.\.\.', '상상했다...'),
        (r'막지 못했습니다\.', '막지 못했다.'),
        (r'멸망했다\.\.\.', '멸망했다...'),
        (r'급증합니다\.', '급증한다.'),
        (r'그렇게 무섭지 않기를 바랍니다\.', '그렇게 참혹하지 않기를 바란다.'),
        (r'최선을 다하고 있습니다\.\.\.', '최선을 다하고 있다...'),
        (r'안심할 것입니다\.', '안심할 것이다.'),
        (r'격리 조치에 들어갔습니다\.', '격리 조치에 들어갔다.'),
        (r'폐쇄되고 격리 조치가 내려졌다는 보고가 있습니다\.\.\.', '폐쇄되고 격리 조치가 내려졌다는 보고가 있다...'),
        (r'실제로 받고 있습니다\.\.\.', '실제로 배포받고 있다...'),
        (r'사실도 알게 되었습니다\.', '사실도 알게 되었다.'),
        (r'왜 그렇게 하겠습니까\?', '왜 그렇게 하겠는가?'),
        (r'취소되었나요\?', '취소되었겠는가?'),
        (r'생각하지 않습니다\.', '생각하지 않는다.'),
        (r'바랄 뿐입니다\.', '바랄 뿐이다.'),
        (r'전파될 수 있습니다\.\.\.', '전파될 수 있다...'),
        (r'다릅니다\.', '다르다.'),
        (r'전파될 수 있습니다\.', '전파될 수 있다.'),
        (r'형태입니다\.', '형태이다.'),
        (r'사망할 것입니다\.', '사망할 것이다.'),
        (r'효과가 없을 수도 있다\.', '효과가 없을 수도 있다.'),
        (r'그럼 어떻게 될지 지켜보자\.', '앞으로 어떻게 될지 지켜보자.'),
        (r'점입니다\.', '점이다.'),
        (r'안전할 것입니다\.', '안전할 것이다.'),
        (r'처할 수 있습니다\.', '처할 수 있다.'),
        (r'저는\s*', '나는 '),
        (r'제가\s*', '내가 '),
        (r'있습니다\.', '있다.'),
        (r'없습니다\.', '없다.'),
        (r'입니다\.', '이다.'),
        (r'됩니다\.', '된다.'),
        (r'않습니다\.', '않는다.'),
        (r'합니다\.', '한다.'),
        (r'였습니다\.', '였다.'),
        (r'이었습니다\.', '이었다.'),
        (r'했습니다\.', '했다.'),
        (r'받았습니다\.', '받았다.'),
        (r'보입니다\.', '보인다.'),
        (r'모릅니다\.', '모른다.')
    ]
    for pattern, repl in rules:
        text = re.sub(pattern, repl, text)

    return text

def create_p(paraPrID, charPrID, text=""):
    p = ET.Element('{http://www.hancom.co.kr/hwpml/2011/paragraph}p', {
        'id': '2147483648',
        'paraPrIDRef': str(paraPrID),
        'styleIDRef': '0',
        'pageBreak': '0',
        'columnBreak': '0',
        'merged': '0'
    })
    run = ET.SubElement(p, '{http://www.hancom.co.kr/hwpml/2011/paragraph}run', {
        'charPrIDRef': str(charPrID)
    })
    if text:
        t = ET.SubElement(run, '{http://www.hancom.co.kr/hwpml/2011/paragraph}t')
        t.text = text
    return p

for art in articles:
    print(f"\n==========================================")
    print(f"Building: {art['out_name']}")

    # 1. Read base zip to preserve image & other metadata
    with zipfile.ZipFile(art['base_hwpx'], 'r') as zin:
        file_map = {item.filename: zin.read(item.filename) for item in zin.infolist()}

    # 2. Use standard reference header (11pt YoonGothic 740, 160% line spacing)
    file_map['Contents/header.xml'] = hdr_xml

    # 3. Read raw txt lines
    with open(art['raw_txt'], 'r', encoding='utf-8') as f:
        raw_lines = [line.strip() for line in f if line.strip()]

    # Skip first line if it was original title
    body_raw = raw_lines[1:] if len(raw_lines) > 1 else raw_lines

    # Filter promo and convert to plain
    cleaned_body = []
    for line in body_raw:
        res = clean_and_convert(line)
        if res is not None:
            cleaned_body.append(res)

    # Find if base hwpx had picture paragraph
    base_tree = ET.fromstring(file_map['Contents/section0.xml'])
    pic_p = None
    orig_secPr = None

    for p in base_tree.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}p'):
        if orig_secPr is None:
            for run in p.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}run'):
                s = run.find('{http://www.hancom.co.kr/hwpml/2011/paragraph}secPr')
                if s is not None:
                    orig_secPr = s
                    break
        if pic_p is None:
            if p.find('.//{http://www.hancom.co.kr/hwpml/2011/paragraph}pic') is not None:
                pic_p = p

    # 4. Construct fresh section0
    ns_sec = 'http://www.hancom.co.kr/hwpml/2011/section'
    new_root = ET.Element(f'{{{ns_sec}}}sec')

    for prefix, uri in [
        ('', 'http://www.hancom.co.kr/hwpml/2011/section'),
        ('hp', 'http://www.hancom.co.kr/hwpml/2011/paragraph'),
        ('hs', 'http://www.hancom.co.kr/hwpml/2011/section'),
        ('hc', 'http://www.hancom.co.kr/hwpml/2011/core'),
        ('ha', 'http://www.hancom.co.kr/hwpml/2011/app'),
        ('hp10', 'http://www.hancom.co.kr/hwpml/2016/paragraph'),
        ('hh', 'http://www.hancom.co.kr/hwpml/2011/head'),
        ('hhs', 'http://www.hancom.co.kr/hwpml/2011/history'),
        ('hm', 'http://www.hancom.co.kr/hwpml/2011/master-page'),
        ('hpf', 'http://www.hancom.co.kr/schema/2011/hpf'),
        ('dc', 'http://purl.org/dc/elements/1.1/'),
        ('opf', 'http://www.idpf.org/2007/opf/'),
        ('ooxmlchart', 'http://www.hancom.co.kr/hwpml/2016/ooxmlchart'),
        ('hwpunitchar', 'http://www.hancom.co.kr/hwpml/2016/HwpUnitChar'),
        ('epub', 'http://www.idpf.org/2007/ops'),
        ('config', 'urn:oasis:names:tc:opendocument:xmlns:config:1.0')
    ]:
        ET.register_namespace(prefix, uri)

    # Header block
    # p0: Main title (charPr=7)
    p0 = create_p(20, 7, art['main_title'])
    if orig_secPr is not None:
        run0 = list(p0.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}run'))[0]
        run0.insert(0, orig_secPr)
    new_root.append(p0)
    new_root.append(create_p(22, 8, ""))
    new_root.append(create_p(22, 8, art['sub_title1']))
    new_root.append(create_p(22, 8, art['sub_title2']))
    new_root.append(create_p(20, 9, ""))
    new_root.append(create_p(20, 10, art['orig_title']))

    # Picture if present
    if pic_p is not None:
        new_root.append(pic_p)

    # Body paragraphs
    for para_text in cleaned_body:
        new_root.append(create_p(22, 8, para_text))

    # Convert XML
    file_map['Contents/section0.xml'] = ET.tostring(new_root, encoding='utf-8', xml_declaration=True)

    # Preview PrvText
    prv_lines = [
        art['main_title'],
        "",
        art['sub_title1'],
        art['sub_title2'],
        "",
        art['orig_title']
    ] + cleaned_body
    file_map['Preview/PrvText.txt'] = '\n'.join(prv_lines).encode('utf-8')

    # Save to E:\편집 기사\오늘편집\
    out_path = os.path.join(today_edit_dir, art['out_name'])
    with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        if 'mimetype' in file_map:
            zout.writestr('mimetype', file_map['mimetype'], compress_type=zipfile.ZIP_STORED)
        for fname, data in file_map.items():
            if fname != 'mimetype':
                zout.writestr(fname, data, compress_type=zipfile.ZIP_DEFLATED)
    print(f"  [Saved] {out_path} ({os.path.getsize(out_path):,} bytes)")

print("\nAll 4 revised articles created in 오늘편집!")
