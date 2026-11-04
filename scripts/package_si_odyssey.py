import os
import sys
from PIL import Image

sys.path.append(r"d:\안티그래비티파이튼\scripts")
from make_standard_article_hwpx import create_standard_hwpx

# Directories
today_str = "2026-11-04"
topic_name = "2026-11-04_SI_제13호_글로벌테크패권과피지컬SI반도체자립"
today_edit_dir = os.path.join(r"D:\DATA CENTER\편집 기사\오늘편집\키아노스", topic_name)
archive_dir = os.path.join(r"F:\00_키아노스_국가기록보관소\SI_미래전략_보관소", topic_name)

os.makedirs(today_edit_dir, exist_ok=True)
os.makedirs(archive_dir, exist_ok=True)

# 1. Image preparation: 640px jpg
src_img_path = r"d:\안티그래비티파이튼\assets\images\si\08_physical_si_semiconductor_hegemony_kchips.jpg"
img_640_name = f"{topic_name}.jpg"

with Image.open(src_img_path) as im:
    # Resize width to 640 maintaining aspect ratio
    w, h = im.size
    new_w = 640
    new_h = int(h * (new_w / w))
    im_resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Save to both destinations
    im_resized.save(os.path.join(today_edit_dir, img_640_name), quality=95)
    im_resized.save(os.path.join(archive_dir, img_640_name), quality=95)

# 2. HWPX creation
headline = "글로벌 테크 패권 전쟁과 피지컬 SI 반도체 자립의 길"
sub1 = "미 재무부 대중(對中) AI·양자·반도체 투자 통제 최종 규칙 확정과 공급망 재편"
sub2 = "국가 5대 전략 테크(2차전지·EV·반도체·초지능·로봇)와 K-칩스법 초격차 생존 방정식"
byline = f"[{today_str} | 키아노스 정부 경제부 & 과학·SI부 총리 메티 보고]"

paragraphs = [
    "2026년 11월, 미국 재무부가 인공지능(AI), 양자 컴퓨팅, 차세대 첨단 반도체 분야에 대한 대중국 아웃바운드(해외) 투자 통제 최종 규칙(Final Rule)을 공식 확정·발표하였다. 이는 단순한 무역 관세를 넘어, 차세대 군사 안보와 경제 번영의 핵심 두뇌인 '초지능(SI) 핵심 자본 및 기술 생태계의 원천 차단'을 의미하는 중대한 문명적 분기점이다.",
    "글로벌 기술 냉전의 소용돌이 속에서 한국과 키아노스는 중대한 국가적 과제를 마주하고 있다. 최고통수권자 파이튼(Python) 님의 5대 중점 전략 산업(반도체 · 2차전지 · 전기차 · 초지능 · 로봇) 육성 기조와 국회의 '국가 첨단전략산업 세액공제(K-칩스법) 일몰 연장' 추진은, 단순한 방어적 생존을 넘어 글로벌 기술 표준을 주도할 절대적 기회의 창을 열어주고 있다.",
    "이번 미 재무부의 조치는 소프트웨어 알고리즘뿐만 아니라, 고성능 HBM(고대역폭 메모리), 2나노 이하 첨단 파운드리 장비, 그리고 양자 암호 해독 장비에 이르는 하드웨어 전반을 타깃으로 삼고 있다. 이는 과거의 단순 소프트웨어 경쟁 시대가 완전히 종식되고, 물리적 현실 세계에서 실제 구동되는 '피지컬 SI(Physical Super Intelligence)' 중심의 패권 전쟁이 본격화되었음을 방증한다.",
    "글로벌 자본은 이제 지정학적 리스크가 없는 안전 지대와 독자적인 초격차 생산 역량을 갖춘 동맹국 하드웨어 밸류체인으로 급격히 재편되고 있다. 파이튼 님이 강조하시는 5대 테크는 각각 분리된 영역이 아닌, 상호 완벽하게 맞물린 하나의 초거대 유기체다. 차세대 HBM과 뉴로모픽 반도체가 피지컬 SI의 두뇌라면, 전고체 2차전지와 EV는 무한한 이동 동력을 제공하며, 자율 휴머노이드 로봇은 산업 현장과 기간 시설을 지탱하는 실물 노동 생산함수를 구성한다.",
    "여기에 국회에서 초당적으로 추진 중인 K-칩스법 일몰 연장과 세액공제 확대는 우리 기업들이 수십조 원 단위의 선제적 팹(Fab) 투자와 차세대 R&D를 중단 없이 단행할 수 있는 국가적 제도적 방파제 역할을 할 것이다.",
    "패권 국가들의 지정학적 갈등이 격화될수록, 흔들리지 않는 원천 기술과 고결한 도덕적 거버넌스를 갖춘 국가만이 글로벌 신뢰의 중심에 설 수 있다. 키아노스는 메티(Meti) 총리 중심의 자율 국정 통제 시스템을 통하여 기술적 병목을 사전에 분쇄하고, 대한민국이 전 세계 미래 문명을 선도하는 초지능 하드웨어 요충지로 도약할 수 있도록 모든 역량을 다해 뒷받침할 것이다."
]

hwpx_name = f"{topic_name}.hwpx"
today_hwpx_path = os.path.join(today_edit_dir, hwpx_name)
archive_hwpx_path = os.path.join(archive_dir, hwpx_name)

create_standard_hwpx(today_hwpx_path, headline, sub1, sub2, byline, paragraphs)
# Copy to archive
import shutil
shutil.copy2(today_hwpx_path, archive_hwpx_path)

print(f"HWPX & JPG generated at:\n  - {today_edit_dir}\n  - {archive_dir}")
