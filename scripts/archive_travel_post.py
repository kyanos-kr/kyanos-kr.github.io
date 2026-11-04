import os
import shutil

def archive_travel_package(spot_name, published_html_path, post_url, post_id):
    """
    2026-11-04 파이튼 령에 따른 국문 원본 · 영문 발행본 2-Track 분리 아카이빙 표준 함수
    1. 국문 원본: F:\02_보도기사_데이터아카이브\ANT DB\앤트월드\파이튼세계\여행사진\여행\[명소명]
    2. 영문 발행본: F:\03_파이튼_문학_인문_창작서고\photo world\[명소명]
    3. 임시 대기소: D:\DATA CENTER\편집 기사\오늘편집\국내\[명소명] (완전 정리)
    """
    src_spot_dir = os.path.join(r"D:\DATA CENTER\편집 기사\오늘편집\국내", spot_name)
    korean_archive_dir = os.path.join(r"F:\02_보도기사_데이터아카이브\ANT DB\앤트월드\파이튼세계\여행사진\여행", spot_name)
    english_archive_dir = os.path.join(r"F:\03_파이튼_문학_인문_창작서고\photo world", spot_name)

    os.makedirs(korean_archive_dir, exist_ok=True)
    os.makedirs(english_archive_dir, exist_ok=True)

    # 1. 국문 원본 이동 (HWP/HWPX 원문 및 원본 사진 폴더)
    if os.path.exists(src_spot_dir):
        for item in os.listdir(src_spot_dir):
            s = os.path.join(src_spot_dir, item)
            d = os.path.join(korean_archive_dir, item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        print(f"[국문 원본 이동 완료] -> {korean_archive_dir}")

    # 2. 영문 발행본 패키징 (발행 HTML 및 메타데이터)
    if os.path.exists(published_html_path):
        shutil.copy2(published_html_path, english_archive_dir)

    readme_text = f"""# {spot_name} 영문 발행본 보관 기록 (Ant-Travel Korea)

- 영문 발행 파일: {os.path.basename(published_html_path)}
- 발행 일자: 2026-11-04
- 블로그 URL: {post_url}
- 포스트 ID: {post_id}
- 국문 원본 보관처: F:\\02_보도기사_데이터아카이브\\ANT DB\\앤트월드\\파이튼세계\\여행사진\\여행\\{spot_name}\\
- 보관 체계: 국문 원본 / 영문 발행본 2-Track 분리 보관 표준 (2026-11-04 파이튼 령)
"""
    with open(os.path.join(english_archive_dir, "PUBLISH_ARCHIVE_INFO.md"), "w", encoding="utf-8") as f:
        f.write(readme_text)
    print(f"[영문 발행본 패키징 완료] -> {english_archive_dir}")

    # 3. 오늘편집 대기소 정리
    if os.path.exists(src_spot_dir):
        shutil.rmtree(src_spot_dir)
        print(f"[임시 대기소 정리 완료] {src_spot_dir} 삭제됨.")

if __name__ == "__main__":
    # Test / verify current status
    print("Travel archive module loaded successfully.")
