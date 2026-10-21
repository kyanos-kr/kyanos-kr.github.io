# -*- coding: utf-8 -*-
"""
키아노스 제1호 자체 저작권 음원 리마스터링 생성기
주제: 날카로움을 깎아낸 부드러운 음색의 파이프 오르간 & 백파이프 희망 팝 BGM
편성: 기타 제외, 부드러운 웜(Warm) 톤 백파이프와 웅장하고 따뜻한 파이프 오르간, 부드러운 오케스트라 패드, 온화한 드럼
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
    print("[키아노스 국립음악창작원] 부드러운 음색(Warm Tone) 음원 재생성 착수")
    print("=" * 65)
    
    engine = KyanosMusicEngine()
    
    title_tag = "희망찬_새벽의_오르간과_백파이프_부드러운선율"
    # 기타 제외, 멜로우/웜 톤 백파이프, 웅장하고 부드러운 오르간 패드, 날카로움 제거
    prompt = (
        "Mellow warm Scottish bagpipe lyrical melody, rich gentle church pipe organ harmony, "
        "lush smooth orchestral strings pad, soft round acoustic drums, warm bass, "
        "hopeful tranquil morning atmosphere, smooth sweet tone, soothing and uplifting, "
        "no harsh high frequencies, pristine analog warmth studio recording, 100 bpm"
    )
    
    duration_seconds = 22
    
    print(f"\n[파이튼 님 피드백 반영]")
    print(f"• 기타 제외(No guitar)")
    print(f"• 백파이프 연주 유지하되 부드럽고 따뜻한 웜 톤(Mellow & Warm tone)")
    print(f"• 파이프 오르간과 현악 패드의 풍성하고 아늑한 감싸안음")
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
