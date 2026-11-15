# -*- coding: utf-8 -*-
"""
키아노스 정부 09_미디어부 유튜브 미디어 랩 (MED-YTB-01)
오픈소스 기반 실사 모션 숏폼 자동 생성 엔진 v3.0 (Kyannos Real-Motion Engine v3.0)

[v3.0 핵심 진화 내역]
1. Natural Voice Studio (초자연적 아나운서 음성 마스터링):
   - 3세대 다국어 신경망 보이스(`ko-KR-HyunsuMultilingualNeural` / `ko-KR-SunHiNeural`) 탑재
   - FFmpeg 스튜디오 오디오 마스터링 체인(따뜻함 EQ + 치찰음 억제 + 성우 컴프레서 + EBU R128 라우드니스 정규화)으로 기계음 완전 제거
2. Real-Time Word-Boundary Karaoke Subtitles (0.01초 단위 단어 하이라이트 자막):
   - Edge-TTS WordBoundary 타임스탬프를 실시간 추출하여, 추가 VRAM 소모 없이 발화하는 어절마다 골드(#FBBF24) 하이라이트가 살아 움직이는 ASS 벡터 자막 자동 생성
3. Cinematic XFade Transitions (부드러운 씬 전환 트랜지션):
   - 단순 컷 편집을 넘어 0.4초 시네마틱 디졸브(xfade)로 실사 장면들을 유려하게 연결
4. Open-Source B-Roll Fetcher (yt-dlp) + 실사 모션 무결성 검증기 + RTX 3050 (h264_nvenc) 가속
5. D: 드라이브(GitHub 연동 엔진룸) 빌드 ➔ F: 드라이브(혜민각 영구 서고) 최종 완성본 자동 이관
"""

import os
import wave
import shutil
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import edge_tts
import static_ffmpeg
import yt_dlp

# FFmpeg 실행 경로 자동 등록
static_ffmpeg.add_paths()


class KyannosRealShortsEngineV3:
    def __init__(self, workspace_dir: Optional[str] = None):
        self.base_dir = Path(workspace_dir) if workspace_dir else Path(__file__).resolve().parent
        self.broll_cache_dir = self.base_dir / "broll_cache"
        self.output_dir = self.base_dir / "생성_산출물"
        self.broll_cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 3세대 자연스러운 한국어 신경망 보이스
        self.male_natural_voice = "ko-KR-HyunsuMultilingualNeural"
        self.female_natural_voice = "ko-KR-SunHiNeural"
        self.male_news_voice = "ko-KR-InJoonNeural"
        self.use_nvenc = self._detect_nvenc()

    def _detect_nvenc(self) -> bool:
        """NVIDIA RTX 3050 h264_nvenc 하드웨어 가속 가용 여부 자동 감지"""
        try:
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "testsrc=duration=0.2:size=320x240:rate=30",
                "-c:v", "h264_nvenc", "-f", "null", "-"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            return res.returncode == 0
        except Exception:
            return False

    def get_korean_font(self, size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
        candidates = [
            "C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf",
            "C:/Windows/Fonts/NanumGothicBold.ttf" if bold else "C:/Windows/Fonts/NanumGothic.ttf",
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def fetch_real_broll(self, scene_id: str, query_or_url: str) -> Path:
        """오픈소스 yt-dlp 엔진을 통해 실제 카메라로 촬영된 풀-모션 실사 비디오 클립 조달"""
        existing = list(self.broll_cache_dir.glob(f"{scene_id}_raw.*"))
        valid_exts = {".mp4", ".webm", ".mkv", ".mov"}
        for p in existing:
            if p.suffix.lower() in valid_exts and p.stat().st_size > 100_000:
                return p

        out_tmpl = str(self.broll_cache_dir / f"{scene_id}_raw.%(ext)s")
        target = query_or_url if query_or_url.startswith("http") else f"ytsearch1:{query_or_url}"

        ydl_opts = {
            "format": "bestvideo[height<=1080][ext=mp4]/best[height<=1080][ext=mp4]/best",
            "outtmpl": out_tmpl,
            "quiet": True,
            "noplaylist": True,
            "overwrites": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([target])

        downloaded = [
            p for p in self.broll_cache_dir.glob(f"{scene_id}_raw.*")
            if p.suffix.lower() in valid_exts
        ]
        if not downloaded:
            raise FileNotFoundError(f"실사 B-Roll 비디오 다운로드 실패: {query_or_url}")
        return downloaded[0]

    def verify_real_motion(self, video_path: Path) -> float:
        """픽셀 변화량(Motion Delta)으로 정지 슬라이드가 아닌 진짜 실사 동영상인지 검증"""
        f1 = self.broll_cache_dir / f"_verify_{video_path.stem}_1.jpg"
        f2 = self.broll_cache_dir / f"_verify_{video_path.stem}_2.jpg"
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-ss", "00:00:01.0", "-i", str(video_path), "-frames:v", "1", str(f1)],
                check=True, capture_output=True
            )
            subprocess.run(
                ["ffmpeg", "-y", "-ss", "00:00:03.0", "-i", str(video_path), "-frames:v", "1", str(f2)],
                check=True, capture_output=True
            )
            arr1 = np.asarray(Image.open(f1).convert("RGB").resize((320, 180)), dtype=np.float32)
            arr2 = np.asarray(Image.open(f2).convert("RGB").resize((320, 180)), dtype=np.float32)
            return float(np.mean(np.abs(arr1 - arr2)))
        finally:
            for tmp in (f1, f2):
                if tmp.exists():
                    tmp.unlink()

    async def generate_natural_narration(
        self,
        text: str,
        raw_mp3: Path,
        mastered_wav: Path,
        voice: Optional[str] = None,
        rate: str = "-4%",
        pitch: str = "-1Hz",
    ) -> Tuple[float, List[Dict]]:
        """
        [v3.0 Natural Voice Studio]
        1. Edge-TTS 스트리밍으로 오디오 및 0.01초 단위 어절 타임스탬프(WordBoundary) 동시 추출
        2. 방송국 스튜디오 보이스 마스터링 체인 적용 (기계적 날카로움 제거 + 따뜻한 중저음 보강)
        """
        chosen_voice = voice or self.male_natural_voice
        communicate = edge_tts.Communicate(
            text, chosen_voice, rate=rate, pitch=pitch, boundary="WordBoundary"
        )

        word_events = []
        audio_bytes = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes.extend(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start_sec = chunk["offset"] / 10_000_000.0
                dur_sec = chunk["duration"] / 10_000_000.0
                word_events.append({
                    "text": chunk["text"],
                    "start": start_sec,
                    "end": start_sec + dur_sec,
                    "dur": dur_sec,
                })

        raw_mp3.write_bytes(bytes(audio_bytes))

        # 방송국 성우 마이크 마스터링 체인 (따뜻한 바디감 + 치찰음 억제 + 부드러운 컴프레션 + 라우드니스 정규화)
        audio_filter = (
            "highpass=f=85,"
            "equalizer=f=220:width_type=o:width=1.2:g=2.5,"
            "equalizer=f=3200:width_type=o:width=1.5:g=1.8,"
            "equalizer=f=7000:width_type=o:width=1.2:g=-1.8,"
            "acompressor=threshold=-18dB:ratio=2.5:attack=15:release=180,"
            "loudnorm=I=-16:TP=-1.5:LRA=11"
        )
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(raw_mp3),
                "-af", audio_filter, "-ar", "44100", "-ac", "1", str(mastered_wav)
            ],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        duration = self.get_media_duration(mastered_wav)
        return duration, word_events

    def get_media_duration(self, media_path: Path) -> float:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(media_path)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())

    def _format_ass_time(self, seconds: float) -> str:
        seconds = max(0.0, seconds)
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int(round((seconds - int(seconds)) * 100))
        if cs >= 100:
            cs = 99
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    def create_dynamic_karaoke_ass(
        self,
        word_events: List[Dict],
        scene_title: str,
        scene_dur: float,
        out_ass: Path,
        words_per_line: int = 4,
    ):
        """
        [v3.0 Word-Boundary 실시간 하이라이트 ASS 자막 생성기]
        - 아나운서가 발화하는 어절만 실시간으로 황금빛(#FBBF24)으로 빛나는 유튜브 최신 숏폼 스타일
        """
        header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SceneTitle,Malgun Gothic,42,&H0064D2FF,&H0064D2FF,&H000A0F1D,&H90000000,-1,0,0,0,100,100,1,0,1,3,1,2,60,60,360,1
Style: KaraokeMain,Malgun Gothic,58,&H00FFFFFF,&H00FFFFFF,&H00070B14,&HA0000000,-1,0,0,0,100,100,0,0,1,4,2,2,70,70,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        # 상단 씬 타이틀 (부드러운 페이드 인/아웃)
        t_start = self._format_ass_time(0.15)
        t_end = self._format_ass_time(max(0.5, scene_dur - 0.25))
        events.append(
            f"Dialogue: 0,{t_start},{t_end},SceneTitle,,0,0,0,,{{\\fad(250,250)}}{scene_title}"
        )

        if word_events:
            # 4어절 단위로 묶어 한 번에 한 구절씩 표시하되, 현재 읽는 어절을 골드(#24BFFB BGR)로 실시간 강조
            chunks = [
                word_events[i:i + words_per_line]
                for i in range(0, len(word_events), words_per_line)
            ]
            for c_idx, chunk in enumerate(chunks):
                chunk_end = (
                    chunks[c_idx + 1][0]["start"]
                    if c_idx + 1 < len(chunks)
                    else min(scene_dur - 0.1, chunk[-1]["end"] + 0.35)
                )
                for active_idx, active_word in enumerate(chunk):
                    w_start = active_word["start"]
                    w_end = (
                        chunk[active_idx + 1]["start"]
                        if active_idx + 1 < len(chunk)
                        else chunk_end
                    )
                    if w_end <= w_start:
                        w_end = w_start + 0.15

                    styled_words = []
                    for j, w in enumerate(chunk):
                        if j == active_idx:
                            # 활성 어절: 앰버 골드 (#FBBF24 -> ASS BGR: &H0024BFFB&) + 약간 확대 느낌
                            styled_words.append(f"{{\\c&H0024BFFB&}}{w['text']}{{\\c&H00FFFFFF&}}")
                        else:
                            styled_words.append(w["text"])

                    line_text = " ".join(styled_words)
                    events.append(
                        f"Dialogue: 1,{self._format_ass_time(w_start)},{self._format_ass_time(w_end)},KaraokeMain,,0,0,0,,{line_text}"
                    )

        out_ass.write_text(header + "\n".join(events) + "\n", encoding="utf-8-sig")

    def create_brand_frame_png(self, brand_badge: str, out_png: Path, w: int = 1080, h: int = 1920):
        """상/하단 시네마틱 비네팅 + 상단 브랜드 배지 + 하단 골드 포인트 바 투명 프레임"""
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        for y in range(250):
            alpha = int(145 * (1 - y / 250))
            draw.line([(0, y), (w, y)], fill=(7, 11, 20, alpha))
        for y in range(h - 560, h):
            progress = (y - (h - 560)) / 560
            alpha = int(215 * (progress ** 1.3))
            draw.line([(0, y), (w, y)], fill=(7, 11, 20, alpha))

        brand_font = self.get_korean_font(26, bold=True)
        bbox = draw.textbbox((0, 0), brand_badge, font=brand_font)
        tw = bbox[2] - bbox[0]
        px = (w - tw) // 2
        draw.rounded_rectangle(
            [px - 28, 74, px + tw + 28, 128],
            radius=27, fill=(10, 15, 29, 175), outline=(245, 158, 11, 195), width=2
        )
        draw.text((px, 86), brand_badge, fill=(251, 191, 36, 255), font=brand_font)

        # 하단 골드 디바이더
        draw.line([(w // 2 - 70, h - 430), (w // 2 + 70, h - 430)], fill=(245, 158, 11, 230), width=4)
        overlay.save(out_png)

    def generate_ambient_bgm(self, duration: float, out_wav: Path):
        """따뜻하고 품격 있는 시네마틱 앰비언트 배경음악 자체 합성"""
        sample_rate = 44100
        total_samples = int((duration + 1.5) * sample_rate)
        t = np.linspace(0, duration + 1.5, total_samples, endpoint=False)

        freqs = [174.61, 220.00, 261.63, 329.63, 392.00]
        signal = np.zeros_like(t)
        for idx, f in enumerate(freqs):
            lfo = 0.7 + 0.3 * np.sin(2 * np.pi * (0.12 + idx * 0.03) * t)
            signal += (0.2 / len(freqs)) * lfo * np.sin(2 * np.pi * f * t)

        fade_len = min(int(1.5 * sample_rate), total_samples // 4)
        if fade_len > 0:
            signal[:fade_len] *= np.linspace(0, 1, fade_len)
            signal[-fade_len:] *= np.linspace(1, 0, fade_len)

        pcm = np.clip(signal * 32767, -32768, 32767).astype(np.int16)
        with wave.open(str(out_wav), "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm.tobytes())

    def render_scene_v3(
        self,
        raw_video_path: Path,
        frame_png_path: Path,
        ass_filename: str,
        mastered_wav_path: Path,
        out_clip_path: Path,
        duration: float,
        start_offset: float = 1.0,
    ):
        """실사 비디오 + 브랜드 프레임 + 실시간 단어 하이라이트 ASS 자막 + 마스터링 음성 합성"""
        filter_complex = (
            f"[0:v]scale=-2:1920:flags=lanczos,crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,"
            f"fps=30,eq=contrast=1.05:saturation=1.10,format=yuv420p[bg];"
            f"[bg][1:v]overlay=0:0,ass={ass_filename}[v]"
        )
        vcodec_args = (
            ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "19", "-b:v", "6M"]
            if self.use_nvenc
            else ["-c:v", "libx264", "-preset", "fast", "-crf", "19"]
        )
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1", "-ss", f"{start_offset:.2f}", "-i", str(raw_video_path),
            "-loop", "1", "-i", str(frame_png_path),
            "-i", str(mastered_wav_path),
            "-filter_complex", filter_complex,
            "-map", "[v]", "-map", "2:a",
            *vcodec_args,
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-t", f"{duration:.2f}",
            str(out_clip_path)
        ]
        subprocess.run(cmd, cwd=str(self.output_dir), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def concat_with_xfade(self, clip_paths: List[Path], clip_durations: List[float], out_merged: Path, xfade_dur: float = 0.4):
        """[v3.0 시네마틱 XFade 트랜지션] 씬과 씬 사이를 0.4초 부드러운 디졸브로 연결"""
        if len(clip_paths) == 1:
            shutil.copy2(clip_paths[0], out_merged)
            return

        inputs = []
        for cp in clip_paths:
            inputs.extend(["-i", str(cp)])

        v_filters = []
        a_filters = []
        offset = clip_durations[0] - xfade_dur

        # 1번째 전환
        v_filters.append(f"[0:v][1:v]xfade=transition=fade:duration={xfade_dur}:offset={offset:.3f}[vx1]")
        a_filters.append(f"[0:a][1:a]acrossfade=d={xfade_dur}[ax1]")

        # 이후 연속 전환
        for i in range(2, len(clip_paths)):
            offset += clip_durations[i - 1] - xfade_dur
            v_filters.append(f"[vx{i-1}][{i}:v]xfade=transition=fade:duration={xfade_dur}:offset={offset:.3f}[vx{i}]")
            a_filters.append(f"[ax{i-1}][{i}:a]acrossfade=d={xfade_dur}[ax{i}]")

        last_idx = len(clip_paths) - 1
        filter_complex = ";".join(v_filters + a_filters)
        vcodec_args = (
            ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "19", "-b:v", "6M"]
            if self.use_nvenc
            else ["-c:v", "libx264", "-preset", "fast", "-crf", "19"]
        )

        cmd = [
            "ffmpeg", "-y", *inputs,
            "-filter_complex", filter_complex,
            "-map", f"[vx{last_idx}]", "-map", f"[ax{last_idx}]",
            *vcodec_args, "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            str(out_merged)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    async def build_real_shorts_v3(
        self,
        project_name: str,
        brand_badge: str,
        scenes: List[Dict],
        voice: Optional[str] = None,
        archive_targets: Optional[List[Path]] = None,
    ) -> Dict:
        """v3.0 전체 파이프라인 실행: 실사 확보 -> 모션 검증 -> 스튜디오 보이스 마스터링 -> 실시간 단어 자막 -> XFade 합성 -> F: 서고 이관"""
        frame_png = self.output_dir / f"{project_name}_temp_frame.png"
        self.create_brand_frame_png(brand_badge, frame_png)

        clip_paths = []
        clip_durations = []
        motion_scores = {}

        for idx, s in enumerate(scenes, start=1):
            sid = s.get("id", f"scene{idx}")
            raw_video = self.fetch_real_broll(sid, s["broll_source"])
            motion_score = self.verify_real_motion(raw_video)
            motion_scores[sid] = round(motion_score, 2)

            raw_mp3 = self.output_dir / f"{project_name}_{sid}_temp.mp3"
            mastered_wav = self.output_dir / f"{project_name}_{sid}_temp_master.wav"
            ass_file = self.output_dir / f"{project_name}_{sid}_temp.ass"
            clip_path = self.output_dir / f"{project_name}_{sid}_temp_clip.mp4"

            print(f"[{sid}] 1. Natural Voice Studio 음성 합성 & WordBoundary 추출 중...")
            audio_dur, word_events = await self.generate_natural_narration(
                s["narration"], raw_mp3, mastered_wav, voice=s.get("voice") or voice
            )
            scene_dur = audio_dur + 0.75

            print(f"[{sid}] 2. 단어별 실시간 하이라이트 ASS 자막 생성 중 ({len(word_events)} 어절)...")
            self.create_dynamic_karaoke_ass(word_events, s["title"], scene_dur, ass_file)

            print(f"[{sid}] 3. RTX 3050 ({'h264_nvenc' if self.use_nvenc else 'libx264'}) 실사 + 자막 렌더링 중...")
            self.render_scene_v3(
                raw_video, frame_png, ass_file.name, mastered_wav, clip_path,
                duration=scene_dur, start_offset=float(s.get("start_offset", 1.5))
            )
            clip_paths.append(clip_path)
            clip_durations.append(scene_dur)

        print("[FINAL] 시네마틱 XFade 씬 전환 및 BGM 마스터 믹싱 중...")
        merged_xfade = self.output_dir / f"{project_name}_temp_xfade.mp4"
        self.concat_with_xfade(clip_paths, clip_durations, merged_xfade, xfade_dur=0.4)

        total_dur = self.get_media_duration(merged_xfade)
        bgm_wav = self.output_dir / f"{project_name}_temp_bgm.wav"
        self.generate_ambient_bgm(total_dur, bgm_wav)

        final_mp4 = self.output_dir / f"{project_name}.mp4"
        vcodec_final = (
            ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "19", "-b:v", "6M"]
            if self.use_nvenc
            else ["-c:v", "libx264", "-preset", "fast", "-crf", "19"]
        )
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(merged_xfade), "-i", str(bgm_wav),
                "-filter_complex", "[0:a]volume=1.0[a0];[1:a]volume=0.16[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                "-map", "0:v", "-map", "[aout]",
                *vcodec_final, "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                str(final_mp4)
            ],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # 임시 작업 파일 즉시 소각
        for tmp in self.output_dir.glob(f"{project_name}_*_temp*"):
            if tmp.exists():
                tmp.unlink()
        for tmp in [frame_png, merged_xfade, bgm_wav]:
            if tmp.exists():
                tmp.unlink()

        copied_paths = []
        if archive_targets:
            for target_path in archive_targets:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(final_mp4, target_path)
                copied_paths.append(str(target_path))

        size_mb = final_mp4.stat().st_size / (1024 * 1024)
        return {
            "version": "v3.0",
            "voice": voice or self.male_natural_voice,
            "engine_output": str(final_mp4),
            "archived_to": copied_paths,
            "duration_sec": round(total_dur, 2),
            "size_mb": round(size_mb, 2),
            "nvenc_accelerated": self.use_nvenc,
            "motion_delta_scores": motion_scores,
        }


if __name__ == "__main__":
    engine = KyannosRealShortsEngineV3()
    AUTUMN_SCENES = [
        {
            "id": "scene1",
            "broll_source": "https://www.youtube.com/watch?v=rDgFaUVXBqY",
            "start_offset": 2.0,
            "narration": "붉은 단풍이 바람을 타고 살랑이는 계절, 키아노스에도 깊고 고요한 가을이 찾아왔습니다.",
            "title": "붉은 단풍이 춤추는 계절",
        },
        {
            "id": "scene2",
            "broll_source": "https://www.youtube.com/watch?v=SHOKEp4NEUg",
            "start_offset": 3.0,
            "narration": "어지러운 세상의 소음을 잠시 내려놓고, 붉게 물든 단풍 숲길을 걸으며 삶의 본질을 돌아보는 시간.",
            "title": "붉게 물든 단풍 숲길 위에서",
        },
        {
            "id": "tea_steam",
            "broll_source": "https://www.youtube.com/watch?v=eD53pvv0fFE",
            "start_offset": 1.0,
            "narration": "하얀 김이 피어오르는 따뜻한 차 한 잔의 온기 속에서, 우리는 내일을 살아갈 고요한 지혜를 얻습니다.",
            "title": "따뜻한 차 한 잔의 온기",
        },
        {
            "id": "scene4",
            "broll_source": "https://www.youtube.com/watch?v=a0CpEqt45tQ",
            "start_offset": 4.0,
            "narration": "음지에서 묵묵히 쌓아온 헌신이 양지의 찬란한 빛으로 피어나는 곳. 여기는, 키아노스의 가을입니다.",
            "title": "음지에서 일하고 양지를 지향하다",
        },
    ]

    f_archive_dir = Path(r"F:\혜민각\04_국정 기록·언론\미디어부_멀티미디어랩\01_영상제작_원본및렌더링\20261115_키아노스_가을_테스트숏츠")
    archive_list = [
        f_archive_dir / "kyanos_autumn_shorts_2026.mp4",
        f_archive_dir / "kyanos_autumn_shorts_2026_REAL_MOTION.mp4",
    ]

    result = asyncio.run(
        engine.build_real_shorts_v3(
            project_name="kyanos_autumn_shorts_2026",
            brand_badge="KYANOS  ·  REAL MOTION v3.0",
            scenes=AUTUMN_SCENES,
            voice="ko-KR-HyunsuMultilingualNeural",
            archive_targets=archive_list,
        )
    )
    print("REAL MOTION v3.0 COMPLETE:", result)
