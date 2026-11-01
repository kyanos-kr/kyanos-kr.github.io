import olefile
import zlib
import struct

def parse_hwp_paragraphs(filepath):
    f = olefile.OleFileIO(filepath)
    sections = [d for d in f.listdir() if d[0] == 'BodyText']
    full_paragraphs = []

    for sec in sorted(sections):
        raw = f.openstream(sec).read()
        try:
            data = zlib.decompress(raw, -15)
        except Exception:
            data = raw

        offset = 0
        while offset < len(data):
            if offset + 4 > len(data):
                break
            hdr = struct.unpack('<I', data[offset:offset+4])[0]
            tag = hdr & 0x3FF
            size = (hdr >> 20) & 0xFFF
            offset += 4
            if size == 0xFFF:
                if offset + 4 > len(data):
                    break
                size = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
            
            rec = data[offset:offset+size]
            offset += size

            # HWPTAG_PARA_TEXT = 67 (0x43)
            if tag == 67:
                chars = []
                p = 0
                while p < len(rec):
                    code = struct.unpack('<H', rec[p:p+2])[0]
                    p += 2
                    if code == 10:
                        chars.append('\n')
                    elif code == 13:
                        chars.append('\n')
                    elif code in [1, 2, 3, 11, 12, 14, 15, 16, 17, 18, 21, 22, 23]:
                        p += 14  # skip remaining 14 bytes of 16-byte extended control
                    elif code in [4, 5, 6, 7, 8, 9, 19, 20]:
                        if code == 9:
                            chars.append('\t')
                    elif code >= 32:
                        chars.append(chr(code))
                p_text = ''.join(chars).strip()
                if p_text:
                    full_paragraphs.append(p_text)

    return full_paragraphs

if __name__ == '__main__':
    paras = parse_hwp_paragraphs(r'D:\DATA CENTER\편집 기사\오늘편집\국내\서산 국립생태공원\탐방기 서산 국립생태공원.hwp')
    for i, p in enumerate(paras):
        print(f"[{i}] {p}")
