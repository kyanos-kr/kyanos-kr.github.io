# -*- coding: utf-8 -*-
"""
Kyanos Pure Neural TTS Streamer
- Uses installed edge_tts Korean neural voices with zero temp-file disk bloat.
"""

import asyncio
import sys
import edge_tts

VOICE_MAP = {
    "vivian": ("ko-KR-SunHiNeural", "+0%"),
    "meti": ("ko-KR-InJoonNeural", "-2%"),
    "ant": ("ko-KR-InJoonNeural", "+6%"),
    "author": ("ko-KR-HyunsuMultilingualNeural", "-6%"),
    "economy": ("ko-KR-InJoonNeural", "+2%"),
    "science": ("ko-KR-HyunsuMultilingualNeural", "+3%"),
    "ksef": ("ko-KR-HyunsuMultilingualNeural", "-3%"),
}


async def stream_tts(persona: str, text: str) -> None:
    voice, rate = VOICE_MAP.get(persona, ("ko-KR-InJoonNeural", "+0%"))
    communicate = edge_tts.Communicate(text, voice, rate=rate)
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
