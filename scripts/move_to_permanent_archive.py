import os
import shutil

# Paths
today_str = "2026-11-04"
topic_folder_name = "2026-11-04_SI_제13호_글로벌테크패권과피지컬SI반도체자립"
clean_topic_name = "글로벌 테크 패권 전쟁과 피지컬 SI 반도체 자립"

temp_dir = os.path.join(r"D:\DATA CENTER\편집 기사\오늘편집\키아노스", topic_folder_name)
f_archive_dir = os.path.join(r"F:\00_키아노스_국가기록보관소\SI_미래전략_보관소", topic_folder_name)
rpt_db_dir = os.path.join(r"D:\DATA CENTER\RPT DB\보도 기사 정보", topic_folder_name)

os.makedirs(f_archive_dir, exist_ok=True)
os.makedirs(rpt_db_dir, exist_ok=True)

# Source files from temp_dir
hwpx_file = f"{topic_folder_name}.hwpx"
jpg_file = f"{topic_folder_name}.jpg"

# Source html
html_src = r"d:\안티그래비티파이튼\키아노스_정부부처\04_교육_문화부\3대_블로그_네트워크\03_초지능_미래오디세이\2026-11-04_SI_제13호_글로벌테크패권과피지컬SI반도체자립.html"

# 1. Ensure F: archive has all components (HWPX, JPG, HTML, README)
shutil.copy2(os.path.join(temp_dir, hwpx_file), f_archive_dir)
shutil.copy2(os.path.join(temp_dir, jpg_file), f_archive_dir)
shutil.copy2(html_src, f_archive_dir)

meta_info = f"""# 초지능 미래 오디세이 제13호 영구보관 기록

- 제목: [Phaeton SI Odyssey #13] 글로벌 테크 패권 전쟁과 피지컬 SI 반도체 자립: 미 대중 첨단기술 통제 속 한국 5대 전략산업의 초격차 생존 방정식
- 발행 일자: {today_str}
- 블로그 URL: https://phaetonktb.blogspot.com/2026/11/phaeton-si-odyssey-13-si-5.html
- 포스트 ID: 6700873189627922908
- 상태: LIVE (발행 완료)
- 서식 규격: 한컴 윤고딕 740, 11pt, 160% 행간 표준 HWPX + 가로 640px JPG 세트
- 보관 일자: {today_str} (Meti 국무총리 전권 영구보관소 이동 완결)
"""
with open(os.path.join(f_archive_dir, "PUBLISH_ARCHIVE_INFO.md"), "w", encoding="utf-8") as f:
    f.write(meta_info)

# 2. Also place full package into D:\DATA CENTER\RPT DB\보도 기사 정보
shutil.copy2(os.path.join(temp_dir, hwpx_file), rpt_db_dir)
shutil.copy2(os.path.join(temp_dir, jpg_file), rpt_db_dir)
shutil.copy2(html_src, rpt_db_dir)
with open(os.path.join(rpt_db_dir, "ARCHIVE_INFO.md"), "w", encoding="utf-8") as f:
    f.write(meta_info)

# 3. Clean up the temporary waiting room in 오늘편집
shutil.rmtree(temp_dir)
print(f"1. Permanent Archive (F:): {f_archive_dir}")
print(f"2. Press DB Archive (RPT DB): {rpt_db_dir}")
print(f"3. Temporary waiting room cleared: {temp_dir}")
