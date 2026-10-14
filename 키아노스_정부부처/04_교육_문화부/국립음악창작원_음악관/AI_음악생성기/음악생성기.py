import os
import sys
import time
import torch
import scipy.io.wavfile
from transformers import AutoProcessor, MusicgenForConditionalGeneration

# 1. 윈도우 프로세스 우선순위를 낮춰 일상 작업 및 키아노스 운영에 지장을 주지 않음
try:
    import psutil
    p = psutil.Process(os.getpid())
    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    print("[시스템] 프로세스 우선순위를 '보통 이하(Below Normal)'로 설정하여 PC 반응성을 보호합니다.")
except Exception as e:
    print(f"[알림] 우선순위 설정 건너뜀: {e}")

# 2. GPU VRAM 할당량 60% 제한 (6GB 중 약 3.6GB 이하로 엄격 제어)
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cuda":
    torch.cuda.set_per_process_memory_fraction(0.60, 0)
    print(f"[시스템] GPU 활성화: {torch.cuda.get_device_name(0)}")
    print("[시스템] VRAM 사용 한도: 최대 3.6GB로 안전 캡 설정 완료")
else:
    print("[시스템] CPU 모드로 동작합니다.")

output_dir = r"d:\안티그래비티파이튼\music_ai\outputs"
os.makedirs(output_dir, exist_ok=True)

# 3. 모델 로드 (가장 가볍고 품질이 검증된 facebook/musicgen-small)
model_name = "facebook/musicgen-small"
print(f"\n[모델 로딩] {model_name} 로딩 중...")
start_time = time.time()

processor = AutoProcessor.from_pretrained(model_name)
model = MusicgenForConditionalGeneration.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
).to(device)

print(f"[모델 로딩 완료] 소요 시간: {time.time() - start_time:.2f}초")

# 4. 키아노스 감성의 테스트 음악 프롬프트
prompt = "Gentle acoustic guitar and warm cello duet, calm autumn melody, melancholic, peaceful folk ballad, 72 bpm, high quality studio recording"
print(f"\n[음악 생성 프롬프트]: \"{prompt}\"")
print("[음악 생성 중...] 약 15초 분량의 테스트 음원을 생성합니다. PC 속도 저하 없이 백그라운드에서 진행됩니다.")

inputs = processor(
    text=[prompt],
    padding=True,
    return_tensors="pt",
).to(device)

# 15초 분량 생성 (MusicGen 토큰 기준 750 tokens ≈ 15초)
audio_values = model.generate(**inputs, max_new_tokens=750, do_sample=True, guidance_scale=3.0)

# 5. 오디오 저장
sampling_rate = model.config.audio_encoder.sampling_rate
audio_data = audio_values[0, 0].cpu().to(torch.float32).numpy()

output_wav = os.path.join(output_dir, "test_autumn_acoustic.wav")
scipy.io.wavfile.write(output_wav, rate=sampling_rate, data=audio_data)

# GPU 메모리 즉시 반환
if device == "cuda":
    del audio_values
    del inputs
    torch.cuda.empty_cache()

print(f"\n[생성 완료!] 음원 파일 저장 완료:")
print(f"-> {output_wav}")
print(f"-> 샘플링 레이트: {sampling_rate} Hz, 길이: {len(audio_data)/sampling_rate:.1f}초")
