"""
키아노스 영상스튜디오 - AI 숏폼 원클릭 자동 생성 엔진 (Kyanos Shorts Generator)
스마트스토어/뉴스/기획안 텍스트 기반 9:16 쇼츠 자동 인코딩 파이프라인
"""

import os
import sys
import json
import asyncio
import subprocess
import static_ffmpeg
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# FFmpeg 경로 환경변수 등록
static_ffmpeg.add_paths()

WORKSPACE_DIR = Path("d:/안티그래비티파이튼/키아노스_영상스튜디오")
OUTPUT_DIR = WORKSPACE_DIR / "02_숏폼_쇼츠_자료" / "shorts_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def generate_tts(text: str, output_path: str, voice: str = "ko-KR-SunHiNeural"):
    """Edge-TTS를 활용한 고음질 한국어 음성 생성"""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def create_scene_frame(image_path: str, caption_text: str, output_path: str, width: int = 1080, height: int = 1920):
    """9:16 쇼츠 규격 이미지 프레임 생성 (자막 바 및 브랜드 배지 적용)"""
    img = Image.new("RGB", (width, height), (10, 15, 29))
    draw = ImageDraw.Draw(img)
    
    # 1. 메인 이미지 (가운데 배치 또는 블러 배경 위 배치)
    if image_path and os.path.exists(image_path):
        src_img = Image.open(image_path).convert("RGB")
        src_img.thumbnail((width - 80, height // 2))
        x = (width - src_img.width) // 2
        y = 350
        img.paste(src_img, (x, y))
    else:
        # 가상 3D 네온 박스 렌더링
        draw.rounded_rectangle([100, 400, width - 100, height - 600], radius=30, outline=(0, 229, 255), width=6)
        draw.text((width // 2 - 200, 700), "[ KYANOS 3D CORE ]", fill=(0, 229, 255))

    # 2. 상단 브랜드 헤더 (워터마크)
    draw.rectangle([0, 0, width, 140], fill=(5, 8, 18))
    draw.text((60, 50), "👑 KYANOS OFFICIAL | 숏폼 AI", fill=(255, 215, 0))
    
    # 3. 하단 자막 영역 (가독성 높은 자막 박스)
    sub_bg = [60, height - 380, width - 60, height - 180]
    draw.rounded_rectangle(sub_bg, radius=20, fill=(0, 0, 0, 200), outline=(255, 255, 255), width=2)
    
    # 텍스트 그리기 (기본 폰트 폴백)
    draw.text((100, height - 300), caption_text, fill=(255, 255, 255))
    
    img.save(output_path)

def render_shorts_scene(image_frame: str, audio_file: str, output_mp4: str):
    """정적 프레임과 오디오를 결합하여 장면 MP4 생성 (FFmpeg)"""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_frame,
        "-i", audio_file,
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_mp4
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

if __name__ == "__main__":
    print("[Kyanos Shorts Generator] Engine initialized successfully.")
