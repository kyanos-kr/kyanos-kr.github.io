# -*- coding: utf-8 -*-
"""
====================================================================
[키아노스 국립음악창작원] 독자적 AI 음원 생성 엔진 (Kyanos Music Engine)
보안 관할: 키아노스 국제질서유지 보안사령부 (K-SEF) 퀀텀 아이기스 사이버 방위단
기술 표준: Windows & PyTorch CUDA 하드웨어 보호 캡 적용
====================================================================
"""

import os
import sys
import time
import json
from datetime import datetime
import torch
import scipy.io.wavfile
from transformers import AutoProcessor, MusicgenForConditionalGeneration

# -------------------------------------------------------------
# 1. K-SEF 보안 프로토콜 및 시스템 리소스 보호 캡 활성화
# -------------------------------------------------------------
def apply_security_hardware_cap():
    """PC 반응성 보호 및 GPU 과부하 원천 차단"""
    # 윈도우 프로세스 우선순위 보통 이하로 조정
    try:
        import psutil
        p = psutil.Process(os.getpid())
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        print("[보안 방위단] 프로세스 우선순위: '보통 이하(Below Normal)' 격리 완료 (PC 쾌적성 100% 보장)")
    except Exception as e:
        print(f"[보안 알림] 프로세스 우선순위 설정 예외: {e}")

    # GPU VRAM 안전 상한 설정 (전체 6GB 중 60%인 3.6GB 이하로 엄격 제어)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.cuda.set_per_process_memory_fraction(0.60, 0)
        gpu_name = torch.cuda.get_device_name(0)
        print(f"[보안 방위단] GPU 가속 연동: {gpu_name} (VRAM 안전 캡: 최대 3.6GB 강제)")
    else:
        print("[보안 방위단] 안전 CPU 모드로 가동합니다.")
    return device

# -------------------------------------------------------------
# 2. 키아노스 시그니처 음악 스타일 프리셋
# -------------------------------------------------------------
KYANOS_PRESETS = {
    "1": {
        "title": "가을 그리고 차 한잔 (Autumn & Tea Acoustic)",
        "prompt": "Gentle acoustic guitar, warm mellow piano, serene autumn atmosphere, melancholic emotional folk ballad, soft cello harmony, 72 bpm, pristine studio acoustic recording",
        "description": "파이튼 님의 대표 서정시 분위기, 따뜻하고 쓸쓸한 가을 포크 멜로디"
    },
    "2": {
        "title": "키아노스 제국 서사시 (Kyanos Imperial Anthem)",
        "prompt": "Majestic cinematic orchestra, noble brass fanfare, soaring emotional strings, steady dignified timpani, royal imperial dignity, 88 bpm, grand soundtrack",
        "description": "국가적 위엄과 웅장함이 깃든 시네마틱 클래식 오케스트라"
    },
    "3": {
        "title": "서정적 달빛 피아노 (Moonlit Lyric Piano & Cello)",
        "prompt": "Delicate solo grand piano and resonant deep cello, slow lyrical melody, reflective contemplation, peaceful quiet night, classical romance, 65 bpm",
        "description": "사색과 명상, 깊은 밤의 감성을 담아내는 잔잔한 피아노 듀엣"
    },
    "4": {
        "title": "희망찬 새벽의 바람 (Breeze of Dawn Pop Ballad)",
        "prompt": "Uplifting warm acoustic guitar with smooth electric piano, hopeful folk pop, gentle rhythm, bright sunny morning, inspiring melody, 95 bpm",
        "description": "밝고 희망찬 아침의 활력을 불어넣는 따스한 어쿠스틱 팝"
    }
}

# -------------------------------------------------------------
# 3. AI 음원 생성 메인 클래스
# -------------------------------------------------------------
class KyanosMusicEngine:
    def __init__(self, model_name="facebook/musicgen-small"):
        self.device = apply_security_hardware_cap()
        self.model_name = model_name
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.base_dir, "생성_음원")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.processor = None
        self.model = None

    def load_model(self):
        """엔진 모델 로드"""
        if self.model is None:
            print(f"\n[엔진 가동] {self.model_name} 로컬 모델 로딩 중...")
            start_t = time.time()
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.model = MusicgenForConditionalGeneration.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)
            print(f"[엔진 준비 완료] 준비 소요 시간: {time.time() - start_t:.2f}초")

    def generate_music(self, prompt, duration_seconds=15, title_tag="키아노스_선율"):
        """음원 생성 및 안전 저장"""
        self.load_model()
        
        # 1초당 약 50 토큰 연산
        tokens_to_generate = int(duration_seconds * 50)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{title_tag}_{timestamp}.wav"
        output_filepath = os.path.join(self.output_dir, safe_filename)

        print(f"\n=======================================================")
        print(f"🎵 키아노스 국립음악창작원 음원 생성 가동")
        print(f"• 곡 명칭 : {title_tag}")
        print(f"• 프롬프트: \"{prompt}\"")
        print(f"• 목표길이: 약 {duration_seconds}초")
        print(f"=======================================================")
        print("[작곡 및 편곡 연산 진행 중... PC 속도 저하 없이 백그라운드 안전 구동]")

        start_gen = time.time()
        inputs = self.processor(
            text=[prompt],
            padding=True,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            audio_values = self.model.generate(
                **inputs, 
                max_new_tokens=tokens_to_generate, 
                do_sample=True, 
                guidance_scale=3.0
            )

        # 오디오 파형 추출 및 파일 저장
        sampling_rate = self.model.config.audio_encoder.sampling_rate
        audio_data = audio_values[0, 0].cpu().to(torch.float32).numpy()
        scipy.io.wavfile.write(output_filepath, rate=sampling_rate, data=audio_data)

        # 메모리 안전 즉각 반환 (K-SEF 수칙)
        del audio_values
        del inputs
        if self.device == "cuda":
            torch.cuda.empty_cache()

        elapsed = time.time() - start_gen
        actual_duration = len(audio_data) / sampling_rate

        print(f"\n✨ [생성 완료] 성공적으로 작곡되어 키아노스 저장소에 영구 보존되었습니다!")
        print(f"• 저장 파일 : {output_filepath}")
        print(f"• 실제 길이 : {actual_duration:.1f}초 (연산 소요: {elapsed:.1f}초)")
        
        # 메타데이터 기록
        meta = {
            "title": title_tag,
            "filename": safe_filename,
            "prompt": prompt,
            "duration": actual_duration,
            "created_at": datetime.now().isoformat(),
            "sample_rate": sampling_rate
        }
        meta_filepath = os.path.join(self.output_dir, f"{safe_filename}.json")
        with open(meta_filepath, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        return output_filepath

# -------------------------------------------------------------
# 4. 인터랙티브 콘솔 실행기
# -------------------------------------------------------------
def run_interactive():
    print("=" * 60)
    print(" 🎼 키아노스 국립음악창작원 자체 AI 음악 생성기 (v1.0)")
    print(" 최고통수권자: 국왕 파이튼 님 | 관할: 보안사령부 퀀텀 아이기스")
    print("=" * 60)
    
    print("\n[키아노스 스타일 프리셋 선택]")
    for k, v in KYANOS_PRESETS.items():
        print(f" [{k}] {v['title']} - {v['description']}")
    print(" [5] 직접 원하는 프롬프트/가사 분위기 입력")
    print(" [Q] 프로그램 종료")

    choice = input("\n원하시는 번호를 선택해 주십시오 (기본값: 1): ").strip()
    if choice.upper() == 'Q':
        print("프로그램을 안전하게 종료합니다.")
        return

    if choice in KYANOS_PRESETS:
        selected = KYANOS_PRESETS[choice]
        prompt = selected["prompt"]
        title_tag = selected["title"].split(" (")[0]
    elif choice == "5":
        prompt = input("곡의 분위기, 악기, 템포를 영어 또는 한국어로 입력하십시오: ").strip()
        title_tag = input("저장할 곡 명칭을 입력하십시오 (예: 나의_시_01): ").strip() or "키아노스_자작곡"
    else:
        selected = KYANOS_PRESETS["1"]
        prompt = selected["prompt"]
        title_tag = selected["title"].split(" (")[0]

    dur_str = input("생성할 곡 길이(초)를 입력하십시오 (권장: 15~30초, 기본값: 20초): ").strip()
    duration = int(dur_str) if dur_str.isdigit() else 20

    engine = KyanosMusicEngine()
    engine.generate_music(prompt=prompt, duration_seconds=duration, title_tag=title_tag)

if __name__ == "__main__":
    run_interactive()
