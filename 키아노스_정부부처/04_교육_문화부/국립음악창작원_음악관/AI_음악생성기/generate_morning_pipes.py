# -*- coding: utf-8 -*-
"""
키아노스 제1호 자체 저작권 음원 생성기 (Windows UTF-8 인코딩 안전 버전)
주제: 희망찬 아침을 여는 파이프 오르간 & 백파이프 테마 팝 BGM
"""

import os
import sys
import time

# 표준 입출력 UTF-8 강제
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

from kyanos_music_engine import KyanosMusicEngine

def main():
    print("=" * 65)
    print("[키아노스 국립음악창작원] 제1호 자체 저작권 BGM 음원 생성 착수")
    print("=" * 65)
    
    engine = KyanosMusicEngine()
    
    # 파이튼 님의 취향: 파이프 오르간, 백파이프 + 희망찬 아침 팝 BGM
    title_tag = "희망찬_새벽의_오르간과_백파이프"
    prompt = (
        "Uplifting morning pop with majestic pipe organ chords and emotional Scottish bagpipe melody, "
        "crisp acoustic guitar rhythm, cheerful tambourine, energetic inspiring drum beat, "
        "hopeful dawn sunrise atmosphere, bright catchy melody, high quality studio production, 110 bpm"
    )
    
    # 숏폼 및 BGM 테스트용 20초 분량 생성 (tokens: 20 * 50 = 1000)
    duration_seconds = 20
    
    print(f"\n[작업 시작] 파이튼 님의 악기 구성(파이프 오르간 + 백파이프) 반영")
    print(f"프롬프트: {prompt}")
    
    output_path = engine.generate_music(
        prompt=prompt,
        duration_seconds=duration_seconds,
        title_tag=title_tag
    )
    
    print("\n" + "=" * 65)
    print(f"[생성 완료] 파일 위치: {output_path}")
    print("=" * 65)

if __name__ == "__main__":
    main()
