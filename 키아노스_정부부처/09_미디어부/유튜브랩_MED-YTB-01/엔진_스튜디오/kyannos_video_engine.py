# -*- coding: utf-8 -*-
"""
키아노스 정부 09_미디어부 유튜브 미디어 랩 (MED-YTB-01)
숏폼/롱폼 영상 자동 생성 엔진 코어 (Kyannos Video Producer Core v1.0)
- Edge-TTS(한국어 프리미엄 음성) 기반 나레이션 음성 생성
- static_ffmpeg 기반 무손실 9:16 (숏폼 1080x1920) 및 16:9 (롱폼 1920x1080) 비디오 합성
- 무제한 무료 로컬 렌더링 파이프라인
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts
import static_ffmpeg

# FFmpeg 경로 자동 등록
static_ffmpeg.add_paths()

class KyannosVideoProducer:
    def __init__(self, output_dir: str = None):
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(__file__).resolve().parent / "생성_산출물"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 기본 한국어 보이스 (ko-KR-SunHiNeural: 또렷하고 신뢰감 있는 뉴스/해설 톤)
        self.default_voice = "ko-KR-SunHiNeural"
        self.male_voice = "ko-KR-InJoonNeural"

    async def generate_narration(self, text: str, output_audio_path: str, voice: str = None) -> str:
        """Edge-TTS를 이용한 무제한 무료 음성 생성"""
        chosen_voice = voice or self.default_voice
        communicate = edge_tts.Communicate(text, chosen_voice, rate="+5%", pitch="+0Hz")
        await communicate.save(output_audio_path)
        return output_audio_path

    def get_audio_duration(self, audio_path: str) -> float:
        """FFmpeg를 통해 오디오 재생 시간(초) 정확히 측정"""
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())

    def create_card_slide(self, title: str, subtitle: str, body_lines: list, output_image_path: str, is_short: bool = True):
        """고품질 타이포그래피 슬라이드 카드 이미지 자동 생성 (숏폼 1080x1920 / 롱폼 1920x1080)"""
        width, height = (1080, 1920) if is_short else (1920, 1080)
        
        # 딥 네이비 & 다크 블루그레이 그라데이션 베이스
        img = Image.new("RGB", (width, height), color=(15, 23, 42)) # Slate 900
        draw = ImageDraw.Draw(img)

        # 상단 액센트 바
        draw.rectangle([0, 0, width, 12], fill=(59, 130, 246)) # Blue 500

        # 기본 폰트 로드 (Windows 맑은 고딕 기본 탑재 활용)
        font_path = "C:/Windows/Fonts/malgunbd.ttf"
        reg_font_path = "C:/Windows/Fonts/malgun.ttf"

        try:
            title_font = ImageFont.truetype(font_path, 60 if is_short else 54)
            sub_font = ImageFont.truetype(font_path, 36 if is_short else 30)
            body_font = ImageFont.truetype(reg_font_path, 40 if is_short else 36)
            brand_font = ImageFont.truetype(font_path, 28)
        except Exception:
            title_font = sub_font = body_font = brand_font = ImageFont.load_default()

        # 브랜드 뱃지
        brand_text = "KYANNOS MEDIA LAB · MED-YTB-01"
        draw.text((80, 80 if is_short else 60), brand_text, fill=(148, 163, 184), font=brand_font)

        # 타이틀 및 서브타이틀
        y_cursor = 240 if is_short else 160
        draw.text((80, y_cursor), title, fill=(255, 255, 255), font=title_font)
        y_cursor += 90
        
        if subtitle:
            draw.text((80, y_cursor), subtitle, fill=(96, 165, 250), font=sub_font) # Blue 400
            y_cursor += 70

        # 구분선
        y_cursor += 20
        draw.line([(80, y_cursor), (width - 80, y_cursor)], fill=(51, 65, 85), width=2)
        y_cursor += 60

        # 본문 핵심 요약 라인 렌더링
        for line in body_lines:
            draw.text((80, y_cursor), f"• {line}", fill=(226, 232, 240), font=body_font)
            y_cursor += 70

        img.save(output_image_path)
        return output_image_path

    def render_video(self, image_path: str, audio_path: str, output_video_path: str, duration: float):
        """이미지와 오디오를 합성하여 고화질 MP4 영상 렌더링"""
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(image_path),
            "-i", str(audio_path),
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
            "-t", str(duration),
            "-shortest",
            str(output_video_path)
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return output_video_path

    async def build_single_clip(self, title: str, subtitle: str, body_lines: list, narration_script: str, filename_prefix: str, is_short: bool = True):
        """원클릭 완전 자동 클립 생성 파이프라인"""
        audio_file = self.output_dir / f"{filename_prefix}_audio.mp3"
        image_file = self.output_dir / f"{filename_prefix}_card.png"
        video_file = self.output_dir / f"{filename_prefix}.mp4"

        # 1. 음성 합성
        await self.generate_narration(narration_script, str(audio_file))
        duration = self.get_audio_duration(str(audio_file)) + 0.5

        # 2. 카드 비주얼 생성
        self.create_card_slide(title, subtitle, body_lines, str(image_file), is_short=is_short)

        # 3. 비디오 렌더링
        self.render_video(str(image_file), str(audio_file), str(video_file), duration)
        return str(video_file)

if __name__ == "__main__":
    producer = KyannosVideoProducer()
    test_title = "키아노스 SI 미디어 랩 개통"
    test_sub = "무제한 무료 숏폼·롱폼 영상 자동 생성 엔진"
    test_body = [
        "Microsoft Edge TTS 기반 초고음질 음성 합성",
        "static_ffmpeg 기반 무손실 1080p 로컬 렌더링",
        "경제·기사·칼럼 원클릭 숏폼 자산화 파이프라인"
    ]
    test_script = (
        "키아노스 정부 미디어부 유튜브 랩의 숏폼 영상 자동 생성 엔진이 성공적으로 가동되었습니다. "
        "이제 외부 유료 구독 없이도, 우리 자체 시스템 내에서 고품질 브리핑 영상과 릴스를 무제한으로 제작할 수 있습니다."
    )
    asyncio.run(producer.build_single_clip(test_title, test_sub, test_body, test_script, "테스트_쇼츠_01", is_short=True))
    print("Video production successful!")
