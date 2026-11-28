# -*- coding: utf-8 -*-
"""
Kyanos Pure Neural TTS Streamer (Stage 1: Zero-Overhead Spoken Korean Normalizer)
- Converts written symbols, acronyms, percentages, and parenthetical numbers into
  natural Korean speech without altering facts or meanings (<1ms, zero VRAM).
- Streams MP3 directly to stdout with zero temp-file disk bloat.
"""

import asyncio
import re
import sys
import edge_tts

# 차분하고 품격 있는 내각 보고용 속도·보이스 매핑
VOICE_MAP = {
    "vivian": ("ko-KR-SunHiNeural", "-3%"),
    "meti": ("ko-KR-InJoonNeural", "-5%"),
    "ant": ("ko-KR-InJoonNeural", "+0%"),
    "author": ("ko-KR-HyunsuMultilingualNeural", "-7%"),
    "economy": ("ko-KR-InJoonNeural", "-2%"),
    "science": ("ko-KR-HyunsuMultilingualNeural", "-2%"),
    "ksef": ("ko-KR-HyunsuMultilingualNeural", "-5%"),
}

# 의미 변질 없는 순수 독음 매핑 (긴 토큰 우선 정렬 적용)
ACRONYM_MAP = {
    "K-SEF": "케이세프",
    "K-DOTS": "케이닷츠",
    "Graphify": "그래피파이",
    "HWPX": "한글 문서",
    "VRAM": "브이램",
    "BTC": "비트코인",
    "XRP": "리플",
    "ETH": "이더리움",
    "SOL": "솔라나",
    "GSR": "금 은 교환비율",
    "TSLA": "테슬라",
    "NVDA": "엔비디아",
    "TTS": "음성 합성",
    "STT": "음성 인식",
    "API": "에이피아이",
    "EV": "전기차",
    "AI": "에이아이",
    "SI": "에스아이",
    "UI": "유아이",
    "PC": "피씨",
}

_ACRONYM_RE = re.compile(
    r"(?<![A-Za-z])("
    + "|".join(re.escape(k) for k in sorted(ACRONYM_MAP, key=len, reverse=True))
    + r")(?![A-Za-z])"
)


def _replace_percent(match: re.Match) -> str:
    sign = match.group(1) or ""
    num = match.group(2)
    prefix = "플러스 " if sign == "+" else ("마이너스 " if sign == "-" else "")
    return f"{prefix}{num}퍼센트"


def normalize_for_speech(text: str) -> str:
    """문어체 기호·약어·퍼센트를 사실 왜곡 없이 자연스러운 구어체 호흡으로 정제한다."""
    s = str(text or "")
    s = s.replace("**", "")
    s = s.replace("@앤트", "앤트 기자")
    s = s.replace("127.0.0.1", "로컬 전용망")
    s = s.replace(".gitignore", "깃 이그노어")

    # 괄호·인용 부호 및 말줄임표를 자연스러운 호흡 쉼표로 변환
    s = re.sub(r"[「」『』\[\]]", " ", s)
    s = re.sub(r"\.{2,}|…", ", ", s)
    s = s.replace("·", ", ")
    s = re.sub(r"\(([^()]{1,40})\)", r", \1, ", s)
    s = s.replace("(", ", ").replace(")", ", ")

    # 퍼센트 및 달러 표기 구어체 독음
    s = re.sub(r"([+-])?(\d+(?:,\d{3})*(?:\.\d+)?)\s*%", _replace_percent, s)
    s = re.sub(r"\$\s*([+-])?(\d+(?:,\d{3})*(?:\.\d+)?)", lambda m: f"{'플러스 ' if m.group(1)=='+' else ('마이너스 ' if m.group(1)=='-' else '')}{m.group(2)}달러", s)

    # 약어 독음 매핑
    s = _ACRONYM_RE.sub(lambda m: ACRONYM_MAP[m.group(1)], s)

    # 쉼표·공백 정리
    s = re.sub(r"\s*,\s*(?:,\s*)+", ", ", s)
    s = re.sub(r"^[\s,]+|[\s,]+$", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


async def stream_tts(persona: str, text: str) -> None:
    spoken = normalize_for_speech(text)
    if not spoken:
        return
    voice, rate = VOICE_MAP.get(persona, ("ko-KR-InJoonNeural", "-3%"))
    communicate = edge_tts.Communicate(spoken, voice, rate=rate)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            sys.stdout.buffer.write(chunk["data"])
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    persona_arg = sys.argv[1] if len(sys.argv) > 1 else "meti"
    raw_bytes = sys.stdin.buffer.read()
    text_arg = raw_bytes.decode("utf-8", errors="replace").strip()
    if not text_arg and len(sys.argv) > 2:
        text_arg = " ".join(sys.argv[2:]).strip()
    if not text_arg:
        sys.exit(1)
    asyncio.run(stream_tts(persona_arg, text_arg))
