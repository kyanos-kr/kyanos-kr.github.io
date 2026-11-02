import os
from PIL import Image, ImageDraw, ImageFont

def create_infographic():
    width = 960
    height = 540
    img = Image.new('RGB', (width, height), color='#0b0f19')
    draw = ImageDraw.Draw(img)

    # Gradient background / lines
    for y in range(height):
        r = int(11 + (22 - 11) * (y / height))
        g = int(15 + (28 - 15) * (y / height))
        b = int(25 + (55 - 25) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Grid / tech lines
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=(25, 40, 70, 40))
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=(25, 40, 70, 40))

    # Title box
    draw.rectangle([(50, 40), (910, 120)], fill='#111827', outline='#6366f1', width=2)
    
    font_paths = [
        "C:/Windows/Fonts/malgunbd.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/gulim.ttc"
    ]
    font_title = None
    font_sub = None
    font_box = None
    font_desc = None
    for fp in font_paths:
        if os.path.exists(fp):
            font_title = ImageFont.truetype(fp, 25)
            font_sub = ImageFont.truetype(fp, 15)
            font_box = ImageFont.truetype(fp, 17)
            font_desc = ImageFont.truetype(fp, 13)
            break
    if not font_title:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_box = ImageFont.load_default()
        font_desc = ImageFont.load_default()

    draw.text((70, 52), "[Phaeton SI Odyssey #11] 초지능 에이전틱 군집과 국가 엔진룸 거버넌스", fill='#818cf8', font=font_title)
    draw.text((70, 88), "부처별 책임분담제 · 2중 검수 루프 · 피지컬 실물 경제 생산함수의 자율 오케스트레이션", fill='#cbd5e1', font=font_sub)

    # 4 Core Columns
    boxes = [
        ("① 에이전틱 군집 오케스트라", "부처별 전문 에이전트 분업\nDrafter-Reviewer 2중 검수\n자율 협업 무결점 파이프라인", "#6366f1"),
        ("② 국가 엔진룸 거버넌스", "메티 총리 중앙 지휘관제\n국정운영령 제2026-1102호\n지연 제로 자율 국정 집행", "#3b82f6"),
        ("③ 피지컬 생산함수 융합", "5대 테크(2차전지·EV·반도체)\n초지능 로봇 자율 생산망\n실물 경제 생산성 수렴 대도약", "#10b981"),
        ("④ 지능 주권 & 영구 서고", "국가 중앙 영구 지식 서고 안치\n글로벌 빅테크 종속 탈피\n국가 생산성 무한 확장", "#f59e0b")
    ]

    box_w = 195
    box_h = 320
    start_x = 55
    spacing = 20
    start_y = 150

    for i, (btitle, bdesc, color) in enumerate(boxes):
        bx = start_x + i * (box_w + spacing)
        by = start_y
        draw.rectangle([(bx, by), (bx + box_w, by + box_h)], fill='#1e293b', outline=color, width=2)
        # Header inside box
        draw.rectangle([(bx, by), (bx + box_w, by + 45)], fill=color)
        draw.text((bx + 10, by + 12), btitle, fill='#ffffff', font=font_box)
        # Body text inside box
        draw.text((bx + 14, by + 70), bdesc, fill='#e2e8f0', font=font_desc, spacing=14)
        
        # Bottom badge
        draw.rectangle([(bx + 15, by + box_h - 45), (bx + box_w - 15, by + box_h - 15)], fill='#0f172a', outline='#334155')
        draw.text((bx + 35, by + box_h - 38), "100% 무인 자율", fill='#38bdf8', font=font_desc)

    # Footer
    draw.text((55, 495), "KYANOS SUPER INTELLIGENCE ODYSSEY · CHIEF ORCHESTRATOR METI", fill='#64748b', font=font_desc)
    draw.text((720, 495), "OFFICIAL ANTHOLOGY 2026", fill='#64748b', font=font_desc)

    out_path = r"D:\안티그래비티파이튼\assets\images\si\07_agentic_swarm_si_governance_engine.jpg"
    img.save(out_path, quality=95)
    print("Saved infographic to:", out_path)

if __name__ == '__main__':
    create_infographic()
