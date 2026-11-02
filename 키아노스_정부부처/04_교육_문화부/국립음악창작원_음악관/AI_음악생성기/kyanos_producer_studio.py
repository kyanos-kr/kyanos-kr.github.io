# -*- coding: utf-8 -*-
"""
====================================================================
[키아노스 국립음악창작원] 하이브리드 AI 프로듀서 스튜디오
Kyanos Hybrid AI Producer Studio (KyanoSound Studio v2.0)
벤치마킹: 포자랩스(POZAlabs) Steal Saturday 하이브리드 음원 제작 모델
보안 관할: 키아노스 국제질서유지 보안사령부 (K-SEF) 퀀텀 아이기스 방위단
====================================================================
"""

import os
import sys
import json
import time
from datetime import datetime

# Windows 콘솔 UTF-8 출력 보장
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 작업 기준 디렉토리
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_ROOT = os.path.dirname(CURRENT_DIR)
CATALOG_PATH = os.path.join(MUSIC_ROOT, "kyanos_tracks_catalog.json")

# 장르 및 사운드 프리셋 아키텍처
GENRE_PRESETS = {
    "1": {
        "name": "Acoustic Folk Ballad (서정 어쿠스틱 포크)",
        "bpm": 72,
        "key": "G Major",
        "instruments": "Acoustic Guitar, Mellow Upright Piano, Soft Cello, Subtle Shaker",
        "prompt_template": "Gentle fingerstyle acoustic guitar, mellow warm piano, emotional cello harmony, 72 bpm, pristine acoustic folk ballad recording, intimate studio reverb"
    },
    "2": {
        "name": "Cinematic Orchestral Rock (웅장한 시네마틱 록)",
        "bpm": 88,
        "key": "D Minor",
        "instruments": "Full Symphonic Orchestra, Distorted Guitars, Heavy Timpani, Epic Horns",
        "prompt_template": "Majestic cinematic orchestra, noble brass fanfare, driving rock drums, epic emotional soaring strings, 88 bpm, high quality movie soundtrack"
    },
    "3": {
        "name": "Classical Elegy / Piano Solo (사색 피아노 에레지)",
        "bpm": 64,
        "key": "C Minor",
        "instruments": "Solo Grand Piano, Deep Resonant Cello, Chamber Strings",
        "prompt_template": "Delicate reflective solo grand piano, resonant melancholy cello solo, slow lyrical tempo, 64 bpm, classical romance, rich acoustic hall acoustics"
    },
    "4": {
        "name": "Midnight Jazz & Blues (미드나잇 재즈 발라드)",
        "bpm": 68,
        "key": "Bb Major",
        "instruments": "Muted Trumpet, Upright Bass, Jazz Rhodes Piano, Soft Brush Drums",
        "prompt_template": "Nocturnal smooth jazz ballad, warm Rhodes piano, muted trumpet solo, walking upright bass, gentle brush snare, 68 bpm, vintage warm club tone"
    },
    "5": {
        "name": "Ambient Neo-Classical (자연 앰비언트 클래식)",
        "bpm": 76,
        "key": "C Major",
        "instruments": "Wooden Flute, Harp, Lush Synthesizer Pads, Wind and Forest Birds Ambience",
        "prompt_template": "Peaceful forest ambience, ethereal harp glissando, wooden acoustic flute, lush warm analog synth pad, 76 bpm, healing meditation neo-classical"
    }
}

def analyze_and_arrange(title, poem_text, genre_key="1"):
    """파이튼 님의 원작 시를 바탕으로 하이브리드 편곡 메타데이터 생성"""
    preset = GENRE_PRESETS.get(genre_key, GENRE_PRESETS["1"])
    
    # 가사 1절 및 후렴 구조 자동 편곡
    lines = [line.strip() for line in poem_text.strip().split("\n") if line.strip()]
    verse_lines = lines[:len(lines)//2] if len(lines) >= 2 else lines
    chorus_lines = lines[len(lines)//2:] if len(lines) >= 2 else lines

    arranged_lyrics = f"[1절]\n" + "\n".join(verse_lines) + "\n\n[후렴]\n" + "\n".join(chorus_lines)
    
    # 코드 진행 추천
    chords_map = {
        "G Major": "Intro: G - D/F# - Em7 - C(add9) / Verse: G - Bm7 - Em7 - C - D7 / Chorus: C - D - Bm7 - Em - Am7 - D7 - G",
        "D Minor": "Intro: Dm - Bb - F - C / Verse: Dm - Am - Bb - F - Gm - C - Dm / Chorus: Bb - C - Dm - F - Bb - C - D",
        "C Minor": "Intro: Cm - Ab - Bb - Eb - Fm - G7 - Cm / Verse: Cm - Fm - Bb - Eb - Ab - Fm - G7 / Chorus: Eb - Bb - Cm - Ab - Eb - Fm7 - Bb7 - Eb",
        "Bb Major": "Intro: Bbmaj7 - Gm7 - Cm7 - F7 / Verse: Bb - Dm7 - Eb - F7 - Gm7 - C7 - Cm7 - F7 / Chorus: Ebmaj7 - F - Dm7 - Gm7 - Cm7 - F7 - Bb",
        "C Major": "Intro: C - G/B - Am - F / Verse: C - Em - F - G - Am - Em - F - G / Chorus: F - G - Em - Am - F - G - C"
    }
    recommended_chords = chords_map.get(preset["key"], "C - G - Am - F")
    
    track_meta = {
        "id": title.lower().replace(" ", "_"),
        "title": title,
        "en_title": f"{title} (KyanoSound Arrangement)",
        "genre": preset["name"],
        "bpm": preset["bpm"],
        "key": preset["key"],
        "instruments": preset["instruments"],
        "chords": recommended_chords,
        "poem": poem_text,
        "lyrics": arranged_lyrics,
        "ai_prompt": preset["prompt_template"],
        "mp3_src": "",
        "has_audio": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return track_meta

def register_to_catalog(track_meta):
    """ArtistKit 카탈로그에 메타데이터 등록"""
    catalog = []
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            catalog = json.load(f)
            
    # 중복 체크
    exists = False
    for i, t in enumerate(catalog):
        if t["title"] == track_meta["title"]:
            catalog[i] = track_meta
            exists = True
            break
    if not exists:
        catalog.append(track_meta)
        
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
        
    print(f"\n[성공] Kyanos ArtistKit 카탈로그에 '{track_meta['title']}' 등록 완료!")
    print(f"• 카탈로그 경로: {CATALOG_PATH}")

def print_banner():
    print("=" * 68)
    print("🎵 [키아노스 국립음악창작원] 하이브리드 AI 프로듀서 스튜디오 v2.0")
    print("   포자랩스(POZAlabs) Steal Saturday 아키텍처 실증 적용 엔진")
    print("=" * 68)

if __name__ == "__main__":
    print_banner()
    print("1. 시그니처 사운드 프리셋:")
    for k, v in GENRE_PRESETS.items():
        print(f"   [{k}] {v['name']} ({v['bpm']} BPM, {v['key']})")
    print("-" * 68)
    
    # 데모 테스트 모드
    demo_title = "키아노스의 푸른 새벽"
    demo_poem = (
        "짙은 어둠을 걷어내는 새벽의 서광,\n"
        "푸른 대지 위에 새로운 희망의 숨결이 차오른다.\n"
        "바람은 평화를 실어 나르고,\n"
        "우리는 더 밝은 내일을 향해 발걸음을 내딛는다."
    )
    print(f"• 예시 분석 곡명: {demo_title}")
    demo_meta = analyze_and_arrange(demo_title, demo_poem, genre_key="1")
    print("\n[AI 오디오 프롬프트 생성 결과]:")
    print(f"  \"{demo_meta['ai_prompt']}\"")
    print("\n[추천 코드 진행]:")
    print(f"  {demo_meta['chords']}")
    print("\n[편곡 보컬 가사]:")
    print(demo_meta['lyrics'])
    print("=" * 68)
    print("스튜디오 엔진이 정상 작동 대기 중입니다.")
