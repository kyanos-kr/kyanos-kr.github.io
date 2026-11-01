import olefile
import zlib
import struct

def parse_hwp5(path):
    f = olefile.OleFileIO(path)
    dirs = f.listdir()
    body_sections = [d for d in dirs if d[0] == 'BodyText']
    full_text = []

    HWPTAG_PARA_HEADER = 0x32
    HWPTAG_PARA_TEXT = 0x43

    for sec in sorted(body_sections):
        stream = f.openstream(sec)
        data = stream.read()
        try:
            unpacked = zlib.decompress(data, -15)
        except Exception:
            unpacked = data

        offset = 0
        while offset < len(unpacked):
            if offset + 4 > len(unpacked):
                break
            header = struct.unpack('<I', unpacked[offset:offset+4])[0]
            tag_id = header & 0x3FF
            level = (header >> 10) & 0x3FF
            size = (header >> 20) & 0xFFF
            offset += 4

            if size == 0xFFF:
                if offset + 4 > len(unpacked):
                    break
                size = struct.unpack('<I', unpacked[offset:offset+4])[0]
                offset += 4

            record_data = unpacked[offset:offset+size]
            offset += size

            if tag_id == HWPTAG_PARA_TEXT:
                chars = []
                idx = 0
                while idx < len(record_data):
                    code = struct.unpack('<H', record_data[idx:idx+2])[0]
                    idx += 2
                    if code == 10 or code == 13:
                        chars.append('\n')
                    elif code < 32:
                        if code in [4, 5, 6, 7, 8, 9, 19, 20]:
                            pass
                        elif code in [1, 2, 3, 11, 12, 14, 15, 16, 17, 18, 21, 22, 23]:
                            idx += 14
                    else:
                        chars.append(chr(code))
                line = ''.join(chars).strip()
                if line:
                    full_text.append(line)

    return '\n'.join(full_text)

if __name__ == '__main__':
    path = r'D:\DATA CENTER\편집 기사\오늘편집\국내\서산 국립생태공원\탐방기 서산 국립생태공원.hwp'
    res = parse_hwp5(path)
    print("=== EXTRACTED HWP 5.0 ===")
    print(res)
